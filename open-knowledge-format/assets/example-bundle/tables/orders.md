---
type: BigQuery Table
title: Orders
description: One row per completed customer order.
tags: [sales, orders]
timestamp: 2026-06-18T00:00:00Z
---

# Schema

| Column | Type | Description |
|--------|------|-------------|
| `order_id` | STRING | Globally unique order identifier. |
| `customer_id` | STRING | Foreign key to [customers](/tables/customers.md). |
| `total_usd` | NUMERIC | Order total in US dollars. |
| `placed_at` | TIMESTAMP | When the customer submitted the order. |

Part of the [sales dataset](/datasets/sales.md).
