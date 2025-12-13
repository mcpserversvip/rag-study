# Proposal: Add Database Indexes

## Goal
Optimize database query performance by adding missing indexes for foreign keys and frequently searched columns.

## Context
The current `ddl.sql` defines the table structure but lacks eligible indexes on foreign keys and search fields. As the dataset grows, queries filtering by date, name, or status will become slow. 

Explicitly defining indexes ensures predictable performance and allows for optimization based on query patterns.

## Plan
1.  Analyze each table for potential search patterns.
2.  Add indexes for:
    -   Foreign keys (consistent explicit indexing).
    -   Common search fields (e.g., `name`, `phone`, `date` fields, `status` fields).
3.  Update `db/ddl.sql` with `CREATE INDEX` statements or inline index definitions.
