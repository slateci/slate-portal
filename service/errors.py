class BadRequestError(Exception):
    status_code = 400
    message = 'Bad Request'

    def __init__(self, message=None, status_code=None, payload=None):
        if message is not None:
            self.message = message
        if status_code is not None:
            self.status_code = status_code

        self.payload = payload

    def to_dict(self):
        ret = dict(self.payload or ())
        ret['message'] = self.message

        return ret


class InternalServerError(Exception):
    status_code = 500
    message = 'Internal Server Error'

    def __init__(self, message=None, status_code=None, payload=None):
        if message is not None:
            self.message = message
        if status_code is not None:
            self.status_code = status_code

        self.payload = payload

    def to_dict(self):
        ret = dict(self.payload or ())
        ret['message'] = self.message

        return ret


class UnauthorizedError(Exception):
    status_code = 401
    message = 'Not Authorized'

    def __init__(self, message=None, status_code=None, payload=None):
        Exception.__init__(self)
        if message is not None:
            self.message = message
        if status_code is not None:
            self.status_code = status_code

        self.payload = payload

    def to_dict(self):
        ret = dict(self.payload or ())
        ret['message'] = self.message

        return ret


class ForbiddenError(Exception):
    status_code = 403
    message = 'Permission Denied'

    def __init__(self, message=None, status_code=None, payload=None):
        Exception.__init__(self)
        if message is not None:
            self.message = message
        if status_code is not None:
            self.status_code = status_code

        self.payload = payload

    def to_dict(self):
        ret = dict(self.payload or ())
        ret['message'] = self.message

        return ret
