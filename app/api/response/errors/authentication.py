from response.errors.common import FunctionalError

class UserNotRegistered(FunctionalError):
    def __init__(self, email=None):
        super().__init__("User is not registered", 101)
        if email is not None:
            self.details = {"email": email}

class ProfileDoesNotExist(FunctionalError):
    def __init__(self, email=None):
        super().__init__("Profile does not exist", 102)
        if email is not None:
            self.details = {"email": email}


class AccountNotApproved(FunctionalError):
    def __init__(self, email=None):
        super().__init__("Your registration is Pending", 103)
        if email is not None:
            self.details = {"email": email}

class InvalidAppleUser(FunctionalError):
    def __init__(self, email=None, apple_id=None):
        super().__init__("Invalid Apple account", 104)
        self.details = {"email": email, "appleId": apple_id}