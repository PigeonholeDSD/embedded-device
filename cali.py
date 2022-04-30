import time
import threading
import subprocess
import predict

running = False


def _collect(motion: str, duration: int) -> None:
    global running
    running = True
    predict.stop()
    print(f'Starting calibrating {motion}')
    f = open(f'calibration/{motion}.csv', 'w')
    proc = subprocess.Popen(
        ['/usr/bin/env', 'python3', 'collect.py'],
        cwd='db',
        stdin=subprocess.DEVNULL,
        stdout=f,
    )
    time.sleep(duration)
    print(f'Stopping calibrating {motion}')
    while proc.poll() is None:
        proc.terminate()
        time.sleep(0.5)
        proc.kill()
    running = False
    predict.start()


def collect(motion: str, duration: int) -> bool:
    if running:
        return False
    threading.Thread(
        target=_collect,
        args=(motion, duration)
    ).start()
    return True
