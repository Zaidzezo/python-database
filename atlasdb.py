import uuid
import copy
import math


class AtlasDB:
    def __init__(self):
        self._documents = {}

    def _is_json_compatible(self, value):
        if value is None or isinstance(value, (str, bool, int)):
            return True

        if isinstance(value, float):
            return math.isfinite(value)

        if isinstance(value, list):
            return all(
                self._is_json_compatible(item)
                for item in value
            )

        if isinstance(value, dict):
            return all(
                isinstance(key, str)
                and self._is_json_compatible(item)
                for key, item in value.items()
            )

        return False

    def insert_document(self, document):
        if type(document) is not dict:
            raise TypeError("document should be a dictionary")

        if "_id" in document:
            raise ValueError("document should not contain '_id' field")

        if not self._is_json_compatible(document):
            raise TypeError(
                "document must contain only JSON-compatible values"
            )

        duplicate = copy.deepcopy(document)

        _id = uuid.uuid4()

        while str(_id) in self._documents:
            _id = uuid.uuid4()

        duplicate["_id"] = str(_id)
        self._documents[str(_id)] = duplicate

        return str(_id)

    def retrieve_document(self, _id):
        if not isinstance(_id, str):
            raise TypeError("Document _id must be a string")
        if not _id:
            raise ValueError("Document _id cannot be empty")
        if _id not in self._documents:
            raise KeyError(f"Document with _id '{_id}' not found")
        return copy.deepcopy(self._documents[_id])