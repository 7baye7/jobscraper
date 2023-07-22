class BaseSearchParams():
    query: str
    location: str

    def __init__(self):
        self.query = None
        self.location = None