from flask import jsonify

class DSDException(Exception):
    pass

class APISyntaxError(DSDException):
    @staticmethod
    def handler(e):
        return jsonify({
            'error': str(e),
        }), 400


class SignatureError(DSDException):
    @staticmethod
    def handler(e):
        return jsonify({
            'error': str(e),
        }), 400
