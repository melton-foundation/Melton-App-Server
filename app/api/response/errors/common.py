from rest_framework import status

class FunctionalError(object):
    def __init__(self, message = "Some error has occured.", error_code = None):
        self.type = "failure"
        self.message = message
        self.errorCode = error_code

    def to_dict(self):
        return self.__dict__



def _form_bad_request_response(errors):
    response_status = status.HTTP_400_BAD_REQUEST
    errors["type"] = "failure"
    return errors, response_status