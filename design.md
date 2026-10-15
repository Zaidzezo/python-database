# AtlasDB — Initial Design

## 1. Overview

AtlasDB is a single-node document database built from scratch in Python. Its purpose is to explore how database engines work internally, including document management, persistent storage, query processing, indexing, and data reliability.

The initial goal is to build a functional database that supports basic CRUD operations and preserves data across program restarts.

## 2. Document Model

A document is a collection of key-value pairs. Each document has a unique identifier (`_id`) and can contain the following value types:

- Integer
- Float
- String
- Boolean
- Null
- Array
- Object
- Nested objects

Documents use a JSON-compatible data model.

Example document:

```json
{
  "_id": "generated-uuid",
  "name": "Ali",
  "age": 16,
  "active": true,
  "programs": [1, 2, 3],
  "metadata": {
    "level": "beginner"
  }
}
```

The `_id` field uniquely identifies each document.

## 3. Document Identifiers

AtlasDB will generate document identifiers automatically using UUIDs.

Requirements:

- Callers cannot choose document IDs when inserting documents.
- Callers cannot change a document's ID through an update.
- Every stored document must have a unique ID.
- If an ID collision occurs, AtlasDB must generate another ID rather than overwrite an existing document.

## 4. CRUD Operations

AtlasDB will support the following basic operations.

### Insert

Create and store a new document.

AtlasDB generates its ID and ensures that it does not replace an existing document.

### Retrieve

Retrieve a document using its ID.

If the requested document does not exist, the operation will raise an appropriate exception.

### Update

Modify an existing document's fields.

- The document's ID cannot be changed.
- If the target document does not exist, the operation will raise an exception.
- The update must not unintentionally modify unrelated fields.

The exact semantics of full updates versus partial updates will be defined during implementation.

### Delete

Remove an existing document from the database.

The behavior of deletion when the requested document does not exist will be specified during implementation.

## 5. Querying

The initial version will support basic document operations.

The supported query conditions and filtering syntax have not yet been defined. These will be decided before implementing the query functionality.

## 6. Persistent Storage

AtlasDB must persist documents on disk.

Requirements:

- Data must survive normal program shutdown and restart.
- Data must remain available after the machine restarts.
- The database must handle file and storage errors.
- The storage mechanism must be designed and implemented as part of AtlasDB rather than delegated to an existing database engine.

## 7. Atomicity and Data Integrity

AtlasDB should protect stored data against incomplete writes.

If a write is interrupted by a power failure, recovery should leave the database in a consistent state rather than expose partially written or corrupted documents.

For an update, the intended behavior is that the database retains either the previous complete state or the new complete state, not a partially applied update.

The storage and recovery mechanisms needed to achieve this guarantee will be investigated and implemented during development.

## 8. Error Handling

AtlasDB will use Python exceptions to communicate errors to callers.

Exceptions should identify the actual problem rather than provide only a generic failure message.

Potential error cases include:

- Requested document not found.
- Invalid document data.
- Invalid operation or input.
- Storage read or write failure.
- ID collision.

The exception types and exact behavior for each case will be defined during implementation.

## 9. Initial Scope

The initial version focuses on:

- A single database process on one machine.
- JSON-compatible documents.
- Automatically generated UUID identifiers.
- Basic CRUD operations.
- Persistent storage.
- Explicit error handling.
- Automated tests for correctness and edge cases.

Distributed storage, replication, advanced transaction support, and production-grade performance are outside the initial scope.

## 10. Development Principles

- Implement the database engine from scratch.
- Understand the reasoning behind each design decision.
- Prioritize correctness and data integrity before performance.
- Test normal behavior, invalid inputs, and failure cases.
- Measure performance before introducing optimizations.
- Document design changes and their reasons.

## 11. Project Status

This document describes the intended behavior of AtlasDB's initial version. It does not claim that these features have already been implemented.

The design may evolve as implementation and testing reveal limitations or new requirements.
