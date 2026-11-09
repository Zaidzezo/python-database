class AtlasDBError(Exception):
    pass

class QueryError(AtlasDBError):
    pass

class InvalidQueryError(QueryError):
    pass

class UnsupportedOperatorError(InvalidQueryError):
    pass