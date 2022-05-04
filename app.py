#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import os
import os.path
import json
import uuid
import atexit
import shutil
import tarfile
from signal import SIGTERM
from tempfile import mkdtemp
from flask import Flask, request, jsonify, send_file, current_app, after_this_request
import cali
import error
import crypto
import predict

os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.setpgrp()


@atexit.register
def goodbye():
    os.killpg(0, SIGTERM)


app = Flask(__name__)
with open('id', 'r') as f:
    dev_id = uuid.UUID(f.read().strip())
app.config.update({
    'ID': dev_id,
    'DEVICE_KEY': crypto.device_key(),
    'DEVICE_CERT': crypto.device_cert(),
    'CA_KEY': crypto.ca_key(),
})

app.register_error_handler(error.APISyntaxError, error.APISyntaxError.handler)
app.register_error_handler(error.SignatureError, error.SignatureError.handler)


def beep(times: int = 1):
    for _ in range(times):
        print('*BEEP*')


@app.get('/')
def status():
    return jsonify({
        'id': str(current_app.config['ID']),
        'battery': 100,
        'charging': True,
        'prediction': predict.result,
    }), 200


@app.get('/ticket')
def ticket():
    ts = request.args.get('ts', '')
    if not re.match(r'^[1-9][0-9]*:[0-9a-f]{40}$', ts):
        raise error.APISyntaxError('Invalid timestamp')
    return crypto.sign_ticket(ts), 200


@app.get('/model')
def get_model():
    if not os.path.isfile('model'):
        return '', 404
    return send_file('model', 'application/octet-stream')


@app.put('/model')
def put_model():
    file = request.files.get('model')
    if not file:
        raise error.APISyntaxError('No file uploaded')
    path = mkdtemp()
    try:
        filename = os.path.join(path, 'model')
        file.save(filename)
        crypto.check_file(filename, request.headers.get('Signature'))
        os.replace(filename, 'model')
        predict.start()
        beep(2)
    finally:
        shutil.rmtree(path)
    return '', 200


@app.get('/calibration/pending')
def get_pending():
    with open('algo/motions.json') as f:
        motions = json.load(f)
    pending = []
    for motion in motions:
        if not os.path.exists(f'calibration/{motion.get("name")}.csv'):
            pending.append(motion)
    return jsonify(pending), 200


@app.post('/calibration/<string:motion>')
def post_calibration(motion: str):
    beep(1)
    with open('algo/motions.json') as f:
        motions = json.load(f)
    duration = 10
    for i in motions:
        if i.get('name') == motion:
            duration = i.get('duration', 10)
            break
    else:
        raise error.APISyntaxError('Invalid motion name')
    if not cali.collect(motion, duration):
        return jsonify({
            'error': 'Previous motion is not finished'
        }), 409
    return '', 200


@app.get('/calibration')
def get_calibration():
    if not [ x for x in os.listdir('calibration') if not x.startswith('.') ]:
        return '', 404
    with tarfile.open('calibration.tar.gz', "w:gz") as tar:
        for motion in os.listdir('calibration'):
            if not motion.startswith('.'):
                tar.add(
                    name='calibration/'+motion,
                    arcname=motion,
                )

    @after_this_request
    def delete_file(response):
        os.unlink('calibration.tar.gz')
        return response
    return send_file('calibration.tar.gz', 'application/x-tar+gzip')


@app.delete('/calibration')
def delete_calibration():
    for file in os.listdir('calibration'):
        if not file.startswith('.'):
            os.unlink(os.path.join('calibration', file))
    return '', 200


if not predict.start():  # no model found
    beep(3)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8001)
