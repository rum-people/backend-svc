class BasePostsHarvester:
    def get_posts(self, days: int, quantity: int=-1) -> list:
        raise NotImplementedError('This method must be implemented in the derived class.')

    def get_name(self):
        raise NotImplementedError('This method must be implemented in the derived class.')