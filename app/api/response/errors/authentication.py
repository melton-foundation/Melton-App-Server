from response.errors.common import FunctionalError

class ProfileDoesNotExist(FunctionalError):
    def __init__(self, email=None):
        super().__init__("Profile does not exist", 101)
        if email is not None:
            self.details = {"email": email}