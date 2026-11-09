def validate_query(query):
    if not isinstance(query, dict):
        raise TypeError("Query must be a dictionary.")

def match_query(document, query):
    for key, value in query.items():
        if key not in document:
            return False
        if document[key] != value:
            return False
    return True