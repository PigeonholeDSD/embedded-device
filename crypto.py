
import os.path
import hashlib
from flask import current_app
from nacl.encoding import HexEncoder
from nacl.signing import SigningKey, VerifyKey
import error


def device_key() -> SigningKey:
    try:
        if 'DEVICE_KEY' in current_app.config:
            return current_app.config['DEVICE_KEY']
    except RuntimeError:
        pass
    try:
        with open('device.key', 'rb') as f:
            return SigningKey(f.read())
    except:
        print('fatal: Error loading DEVICE_KEY')
        exit(2)


def ca_key() -> VerifyKey:
    try:
        if 'CA_KEY' in current_app.config:
            return current_app.config['CA_KEY']
    except RuntimeError:
        pass
    try:
        with open('ca.pub', 'rb') as f:
            return VerifyKey(f.read())
    except:
        print('fatal: Error loading CA_KEY')
        exit(2)


def device_cert() -> str:
    try:
        if 'DEVICE_CERT' in current_app.config:
            return current_app.config['DEVICE_CERT']
    except RuntimeError:
        pass
    try:
        with open('device.crt', 'r') as f:
            return f.read().strip()
    except:
        print('fatal: Error loading DEVICE_CERT')
        exit(2)


def sign(data: str) -> str:
    return device_key().sign(data.encode(), encoder=HexEncoder).signature.decode()


def verify(data: str, sig: str) -> bool:
    try:
        ca_key().verify(data.encode(), HexEncoder().decode(sig))
        return True
    except:
        return False


def hash_file(file: str) -> str:
    h = hashlib.sha256()
    with open(file, 'rb') as f:
        while True:
            chunk = f.read(h.block_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def sign_file(file: str) -> str:
    return sign(hash_file(file))+':'+device_cert()


def sign_ticket(ts: str) -> str:
    return ts+':'+sign(ts)+':'+device_cert()


def check_file(file: str, sig: str) -> None:
    try:
        ca_key().verify(hash_file(file).encode(), HexEncoder().decode(sig))
    except:
        raise error.SignatureError('Invalid signature for model file')
