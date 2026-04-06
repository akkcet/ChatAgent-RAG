
class Tool:
    def __init__(self, name, description, fn):
        self.name = name
        self.description = description
        self.fn = fn

    def run(self, *args, **kwargs):
        return self.fn(*args, **kwargs)
