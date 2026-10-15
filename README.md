# AtlasDB

AtlasDB is a document database engine built from scratch in Python as a learning project to explore how database systems work internally.

The goal is to understand and implement the fundamental mechanisms behind a database, including document management, query processing, persistent storage, indexing, and data recovery.

## Goals

- Implement basic document operations: insert, retrieve, update, and delete.
- Support querying documents using field-based conditions.
- Persist data across program restarts.
- Design and implement storage mechanisms rather than relying on an existing database engine.
- Explore indexing and efficient data retrieval.
- Investigate reliability, consistency, and crash recovery.
- Build a test suite and benchmarks to evaluate correctness and performance.

## Design Principles

- **Built from scratch:** Implement the core database mechanisms independently.
- **Understandability:** Favor designs whose behavior and trade-offs can be explained clearly.
- **Correctness first:** Prioritize predictable behavior and data integrity before optimization.
- **Measured improvement:** Use tests and benchmarks to guide performance decisions.

## Project Status

AtlasDB is in its initial development stage. The design and implementation are evolving as the project progresses.

The goals described here are planned capabilities, not a statement that these features are already implemented.

## Scope

AtlasDB initially targets a single process running on one machine. Distributed storage, replication, and production-grade transaction guarantees are outside the initial scope.

## Learning Objectives

This project is an opportunity to study:

- Data structures and query execution
- File I/O and on-disk data organization
- Storage-engine design
- Indexing and algorithmic complexity
- Error handling, testing, and recovery
- Performance measurement and engineering trade-offs

## License

To be determined.