from exceptions import InvalidQueryError, UnsupportedOperatorError

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

def apply_operator(operator, operand, stored):
    operators = {
        "$gt": lambda a, b: a > b,
        "$gte": lambda a, b: a >= b,
        "$lt": lambda a, b: a < b,
        "$lte": lambda a, b: a <= b,
    }

    if operator not in operators:
        raise UnsupportedOperatorError(f"Unsupported operator: {operator}")
    if type(operand) not in (int, float, str):
        raise InvalidQueryError(f"Operand must be a number or string, got {type(operand)}")
    if type(stored) not in (int, float, str):
        return False
    if type(operand) == str and type(stored) == str:
        return operators[operator](stored, operand)
    elif type(operand) in (int, float) and type(stored) in (int, float):
        return operators[operator](stored, operand)
    return False