from response.success.common import FunctionalSuccess


class ItemBought(FunctionalSuccess):
    def __init__(self, user, item):
        super().__init__("Successfully bought.")
        self.details = {"availablePoints": user.profile.points}
