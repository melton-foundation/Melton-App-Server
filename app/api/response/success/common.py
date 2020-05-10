class FunctionalSuccess(object):
    def __init__(self, message = "Successful."):
        self.type = "success"
        self.message = message


    def to_dict(self):
        return self.__dict__