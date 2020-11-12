from response.errors.common import FunctionalError


class ItemNotAvailable(FunctionalError):
    def __init__(self):
        super().__init__("The requested item is not available", 201)


class InsufficientPoints(FunctionalError):
    def __init__(self, user, item):
        super().__init__("Not enough points to buy the requested item.", 202)
        self.details = {
            "availablePoints": user.profile.points,
            "requiredPoints": item.points,
        }


class ItemAlreadyOwned(FunctionalError):
    def __init__(self):
        super().__init__("The requested item is already purchased by the user.", 203)
