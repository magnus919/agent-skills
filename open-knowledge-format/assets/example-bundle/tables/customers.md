---
type: BigQuery Table
title: Customers
description: One row per customer account.
tags: [sales, customer-data]
timestamp: 2026-06-18T00:00:00Z
---

# Schema

| Column | Type | Description |
|--------|------|-------------|
| `customer_id` | STRING | Unique customer identifier. |
| `name` | STRING | Customer display name. |
| `email` | STRING | Customer email address. |
| `created_at` | TIMESTAMP | Account creation timestamp. |

# Relationships

Each customer has zero or more [orders](/tables/orders.md), linked by `customer_id`.
