import time
import os.path
import threading
import subprocess
import cali

_task = ''
_stop = threading.Event()
result = ''


def predict() -> None:
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
        ['/usr/bin/env', 'python3', 'predict.py', os.path.abspath('model')],
        cwd='algo',
        stdin=proc_data.stdout,
        stdout=subprocess.PIPE,
        bufsize=0,
    )
    for line in proc_algo.stdout:
        result = line.decode().strip()
        print(result)
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


def start() -> None:
    global _task
    if cali.running:
        return
    stop()
    _task = threading.Thread(target=predict)
    _task.start()


def stop() -> None:
    global _task, _stop
    if _task and _task.is_alive():
        _stop.set()
        while _task and _task.is_alive():
            time.sleep(0.1)
