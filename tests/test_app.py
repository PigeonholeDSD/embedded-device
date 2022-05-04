import pytest
from app import app
import json
import os

@pytest.fixture
def client():
    app.config['TESTING'] = True
    client = app.test_client()
    ctx = app.app_context()
    ctx.push()
    yield client
    ctx.pop()

def test_root_head(client):
    res = client.head('/')
    assert res.status_code == 200

def test_root_get(client):
    res = client.get('/')
    resp_body = {
        'id': '12abed34-a70a-43a2-ba0e-ff9c288a147d',
        'battery': 100,
        'charging': True,
        'prediction': '',
    }
    assert res.get_json() == resp_body

def test_timestamp(client):
    valid_ts = ['1650375337']
    invalid_ts = ['1650375337.8234', '0', '1650375337abc']
    valid_keys = ['6bce5953a9506d6c14f2522fd6228afbee394da3']
    invalid_keys = ['6bce5953a9506d6c14f2522fd6228afbee394da379273', '6bce#953a950@d6c14f2(22fd62\x278a\x89bee394da37927\x00', '', '\n\n\n']
    for ts in valid_ts:
        for key in valid_keys:
            res = client.get('/ticket?ts=' + ts + ':' + key)
            assert res.status_code == 200
    for ts in invalid_ts:
        for key in invalid_keys:
            res = client.get('/ticket?ts=' + ts + ':' + key)
            assert res.status_code == 400
    for ts in valid_ts:
        for key in invalid_keys:
            res = client.get('/ticket?ts=' + ts + ':' + key)
            assert res.status_code == 400
    for ts in invalid_ts:
        for key in valid_keys:
            res = client.get('/ticket?ts=' + ts + ':' + key)
            assert res.status_code == 400

def test_model_get(client):
    test_string = 'dsd2022'
    f = open('model', 'w')
    f.write(test_string)
    f.close()
    res = client.get('/model')
    assert res.data == test_string.encode()
    assert res.status_code == 200
    os.remove('model')
    res = client.get('/model')
    assert res.status_code == 404

def test_calibration_pending_get(client):
    resp_body = [
            {
                "name": "walk",
                "duration": 20,
                "display": "walk",
                "desc": "Please walk on a firm and level ground"
            },
            {
                "name": "upstairs",
                "duration": 10,
                "display": "go upstairs",
                "desc": "Please go upstairs"
            }
        ]
    res = client.get('/calibration/pending')
    assert res.status_code == 200
    assert res.get_json() == resp_body

def test_calibration_get(client):
    f = open("calibration/walk.csv", "w")
    f.close()
    res = client.get('/calibration')
    assert res.status_code == 200
    os.remove("calibration/walk.csv")
    res = client.get('/calibration')
    assert res.status_code == 404

def test_calibration_delete(client):
    res = client.delete('/calibration')
    assert res.status_code == 200