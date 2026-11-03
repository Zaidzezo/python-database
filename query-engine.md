# AtlasDB — Query Engine Design

## 1. Objective
Implement a Python-compatible query engine for retrieving documents from named collections. Priorities are correctness, predictable behavior, modularity, and extensibility. No custom query language or parser will be implemented.

## 2. Database Architecture
AtlasDB will support multiple named collections. Each collection owns an independent document store.

```python
db = AtlasDB()
users = db.collection("users")
products = db.collection("products")
```

Requesting an existing collection returns the same instance. Collection names must be non-empty strings without leading or trailing whitespace.

**Responsibilities:**
- `AtlasDB`: manages the collection registry.
- `Collection`: owns documents and implements CRUD operations.
- `Query engine`: validates and evaluates queries.
- `Exceptions`: provides database-specific errors.

Existing CRUD methods move from `AtlasDB` to `Collection`, retaining their names:
- `insert_document(document)`
- `retrieve_document(_id)`
- `update_document(_id, updates)`
- `delete_document(_id)`

The new method is `find(query)`. Existing CRUD tests must be migrated without losing their behavioral guarantees. No compatibility facade will be maintained.

UUID-based `_id` generation remains unchanged. IDs cannot be supplied or modified by callers.

## 3. Query Representation
Queries use native Python dictionaries and lists. The public interface is:

```python
users.find(query)
```

**Equality:**
```python
users.find({"name": "Zaid"})
```

**Comparison operators:**

| Operator | Meaning |
|---|---|
| `$gt` | Greater than |
| `$lt` | Less than |
| `$gte` | Greater than or equal |
| `$lte` | Less than or equal |

```python
users.find({"age": {"$gt": 20}})
```

Multiple operators on one field use AND semantics:
```python
users.find({"age": {"$gte": 18, "$lt": 30}})
```

**Implicit AND:** Multiple ordinary field conditions must all match.
```python
users.find({"name": "Zaid", "age": {"$gt": 20}})
```

**OR:** Alternatives use `$or` with a list of query dictionaries.
```python
users.find({
    "$or": [
        {"name": "Zaid"},
        {"name": "Sara"}
    ]
})
```

AND and OR can be combined. Nested `$or` expressions are supported. An explicit `$and` is deferred. Python dictionaries cannot preserve duplicate keys, and uppercase `OR` is not valid Python syntax.

## 4. Matching Rules
- Queries initially target top-level fields.
- Nested dictionaries and lists support exact structural equality; nested-path queries are deferred.
- Multiple conditions at the same level use AND.
- At least one `$or` branch must match.
- Missing fields are non-matches, not errors.
- `None` matches an explicitly null field, not a missing field.
- Integers and floats compare numerically.
- Booleans are distinct from numbers.
- Strings support lexicographical comparisons.
- Incompatible stored values during ordered comparisons are non-matches.
- Invalid comparison operands are query errors.
- An empty query `{}` matches every document.

## 5. Return Contract
`find()` returns a Python list of complete matching document dictionaries.
- Return all matching documents in encounter order.
- Return `[]` when nothing matches.
- Return complete documents, not only queried fields.
- Return deep copies so callers cannot mutate stored documents through results.

## 6. Error Handling
AtlasDB will define this exception hierarchy:

```text
AtlasDBError
└── QueryError
    └── InvalidQueryError
        └── UnsupportedOperatorError
```

| Situation | Behavior |
|---|---|
| Query is not a dictionary | `TypeError` |
| Malformed query | `InvalidQueryError` |
| Unsupported operator | `UnsupportedOperatorError` |
| Invalid comparison operand | `InvalidQueryError` |
| Missing field | Non-match |
| Incompatible stored value | Non-match |
| No matching documents | Empty list |

Unsupported operators must never be silently ignored. Validate the entire query before scanning documents, including when the collection is empty.

## 7. Execution Architecture
The initial implementation uses a linear scan:
1. Validate the query argument type.
2. Validate its structure and operators.
3. Evaluate each document.
4. Apply comparison and logical conditions.
5. Collect matching documents.
6. Deep-copy and return results.

Validation and document matching must be separate responsibilities. Indexes and query optimization are deferred.

## 8. Module Organization
```text
atlasdb.py       → AtlasDB
collection.py    → Collection
query.py         → Query validation and execution
exceptions.py    → Custom exceptions
```
Avoid circular imports.

## 9. Testing Requirements
Tests must cover:
- Collection creation, reuse, and isolation.
- Existing CRUD behavior after refactoring.
- Equality and all four comparison operators.
- Numeric, boolean, string, null, and nested-value semantics.
- Missing fields and incompatible stored values.
- Implicit AND, `$or`, combined conditions, and nested `$or`.
- Empty queries and empty results.
- Complete results, ordering, and deep-copy isolation.
- Invalid query types, structures, operands, and operators.
- Validation of malformed queries against empty collections.

All existing CRUD regression tests must continue passing.

## 10. Deferred Features
Nested-path queries, `$and`, `$ne`, `$in`, `$nin`, `$exists`, sorting, pagination, projection, aggregation, full-text search, indexing, persistent storage, transactions, replication, and distributed execution.
