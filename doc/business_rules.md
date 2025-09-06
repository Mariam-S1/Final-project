# Business Rules & KPI Definitions

This document defines how key metrics are calculated and how fields are interpreted.

---

## Revenue & Orders
- **Revenue**: 
  - Formula: `SUM(order_items.quantity * order_items.price)` OR 
    `SUM(invoice_lines.quantity * invoice_lines.unit_price)`
  - Use `invoice_lines` for finalized billing data.

- **Average Order Value (AOV)**:
  - Formula: `Total Revenue / Total Number of Orders`

- **Customer Lifetime Value (CLV)**:
  - Formula: `SUM(revenue per customer across all orders)`

- **Order Statuses**:
  - `pending`, `paid`, `shipped`, `cancelled`

---

## Invoices & Payments
- **Invoice Statuses**:
  - `unpaid`: Invoice created but not paid.
  - `paid`: Fully settled.
  - `cancelled`: Voided invoice.

- **Aging Invoices**:
  - Group unpaid invoices by `due_date` buckets (0-30 days, 31-60 days, etc.).

- **Partial Payment**:
  - Calculated via `payment_allocations.amount` < `invoices.total_amount`.

---

## Inventory
- **Stock Health**:
  - If `qty_on_hand` < `reorder_point`, product is low stock.

- **Stock Movements**:
  - Positive `change_qty`: Purchase or stock adjustment.
  - Negative `change_qty`: Sale or consumption.

---

## Leads & Customers
- **Lead Scoring**:
  - Field: `leads.score`, set by ML model or `lead_score_tool`.

- **Inactive Customers**:
  - Customers with no `orders.created_at` in the last 6 months.

---

## General Conventions
- All IDs are integers with `AUTOINCREMENT`.
- All dates stored as ISO strings: `YYYY-MM-DD` or `YYYY-MM-DD HH:MM:SS`.
- Foreign keys are strictly enforced.

