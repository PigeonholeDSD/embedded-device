import json
import time
import os.path
import threading
import subprocess
import cali

_task = threading.Thread()
_stop = threading.Event()
result = ''


def predict(predict_entrypoint: list) -> None:
    global result
    print('Starting collecting')
    proc_data = subprocess.Popen(
        ['/usr/bin/env', 'python3', 'collect.py'],
        cwd='db',
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        bufsize=0,
    )
    print('Starting predicting')
    proc_algo = subprocess.Popen(
        [*predict_entrypoint, os.path.abspath('model')],
        cwd='algo',
        stdin=proc_data.stdout,
        stdout=subprocess.PIPE,
        bufsize=0,
    )
    assert proc_algo.stdout # make mypy happy
    for line in proc_algo.stdout:
        result = line.decode().strip()
        if _stop.is_set():
            _stop.clear()
            break
    print('Stopping predicting')
    while proc_algo.poll() is None:
        proc_algo.terminate()
        time.sleep(0.5)
        proc_algo.kill()
    print('Stopping collecting')
    while proc_data.poll() is None:
        proc_data.terminate()
        time.sleep(0.5)
        proc_data.kill()


def start() -> bool:
    global _task
    if not os.path.exists('model'):
        return False
    if cali.running:
        return False
    stop()
    with open('model.json', 'r') as f:
        predict_entrypoint = json.load(f)['entrypoint']['predict']
    predict_entrypoint = list(map(
        lambda x: x.replace(
            '$ALGO', os.path.join(
                os.path.split(os.path.abspath(__file__))[0], 
                'algo'
            )
        ), 
        predict_entrypoint
    ))
    _task = threading.Thread(target=predict, args=[predict_entrypoint])
    _task.start()
    return True

def stop() -> None:
    global _task, _stop
    if _task and _task.is_alive():
        _stop.set()
        while _task and _task.is_alive():
            time.sleep(0.1)
