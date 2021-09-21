class Result:
    __slots__ = ["value", "status_code"]

    def __init__(self, value, status_code):
        self.status_code = status_code
        self.value = value
