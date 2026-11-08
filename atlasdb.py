from collection import Collection

class AtlasDB:
    def __init__(self):
        self._collections = {}

    def collection(self, name):
        if not isinstance(name, str):
            raise TypeError("Collection name must be a string")
        if not name or name != name.strip():
            raise ValueError("Collection name cannot be empty or contain leading/trailing whitespace")

        if name not in self._collections:
            self._collections[name] = Collection(name)

        return self._collections[name]