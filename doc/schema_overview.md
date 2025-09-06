
# ERP Database Schema Overview (v2)

This ERP database powers the Router, Sales, Finance, Inventory, and Analytics agents.  
It tracks customers, orders, invoices, payments, inventory, suppliers, and ML metadata.

---

## 🔗 Key Relationships (Entity-Relationship Overview)
- **Customers → Orders → Order Items**: Sales orders link to customers and products.
- **Invoices → Payments**: Invoices are linked to payments via allocations.
- **Products → Stock/Movements → Suppliers**: Inventory changes tracked per product.
- **Ledger Entries/Lines**: Full double-entry accounting system.
- **Conversations/Messages**: Persistent chat memory for Router/Agents.
- **Documents/Model Registry**: Source files for RAG and ML models.

---

## 1. Router / Orchestration
| Table          | Purpose | Key Columns |
|----------------|---------|-------------|
| **approvals** | Track approvals for risky actions. | `id`, `module`, `payload_json`, `status`, `requested_by`, `decided_by`, `created_at`, `decided_at` |
| **tool_calls** | Log every tool invocation. | `agent`, `tool_name`, `input_json`, `output_json`, `created_at` |
| **conversations** | Conversation threads. | `id`, `user_id`, `started_at` |
| **messages** | Messages in a conversation. | `id`, `conversation_id`, `sender`, `content`, `created_at` |

---

## 2. Sales & CRM
| Table            | Purpose | Key Columns |
|------------------|---------|-------------|
| **customers** | Customer master. | `id`, `name`, `email`, `phone`, `created_at` |
| **customer_kv** | Key-value memory per customer. | `customer_id`, `key`, `value` |
| **leads** | Leads with ML scoring. | `id`, `customer_name`, `contact_email`, `message`, `score`, `status`, `created_at` |
| **products** | Product catalog. | `id`, `sku`, `name`, `price`, `description` |
| **orders** | Sales order header. | `id`, `customer_id`, `total`, `status`, `created_at` |
| **order_items** | Order detail lines. | `order_id`, `product_id`, `quantity`, `price` |
| **tickets** | Support tickets. | `customer_id`, `subject`, `body`, `status`, `created_at` |

---

## 3. Finance
| Table              | Purpose | Key Columns |
|--------------------|---------|-------------|
| **invoices** | Customer invoices. | `id`, `customer_id`, `invoice_number`, `issue_date`, `due_date`, `total_amount`, `status` |
| **invoice_lines** | Invoice line details. | `invoice_id`, `description`, `quantity`, `unit_price` |
| **invoice_orders** | Link invoices to orders. | `invoice_id`, `order_id` |
| **payments** | Payments received. | `id`, `customer_id`, `amount`, `method`, `received_at` |
| **payment_allocations** | Map payments to invoices. | `payment_id`, `invoice_id`, `amount` |
| **chart_of_accounts** | Accounts list. | `account`, `description` |
| **ledger_entries** | Journal entries. | `id`, `entry_date`, `created_at` |
| **ledger_lines** | Double-entry lines. | `entry_id`, `account`, `debit`, `credit` |

---

## 4. Inventory & Supply Chain
| Table                | Purpose | Key Columns |
|----------------------|---------|-------------|
| **stock** | Current stock per product. | `product_id`, `qty_on_hand`, `reorder_point` |
| **stock_movements** | Stock movement audit. | `product_id`, `change_qty`, `reason`, `ref_id`, `created_at` |
| **suppliers** | Supplier master. | `id`, `name`, `email`, `phone` |
| **supplier_products** | Map suppliers to products. | `supplier_id`, `product_id` |

---

## 5. RAG / ML Ops
| Table              | Purpose | Key Columns |
|--------------------|---------|-------------|
| **documents** | Source files for RAG. | `module`, `path`, `tags`, `created_at` |
| **model_registry** | Track ML models. | `name`, `version`, `path`, `created_at` |
| **ml_features_cache** | Cache of ML features. | `entity_type`, `entity_id`, `feature_json` |

---

## 6. Users
| Table     | Purpose | Key Columns |
|-----------|---------|-------------|
| **users** | System users. | `id`, `name`, `email`, `role`, `created_at` |

---

### Notes:
- All dates are ISO strings (YYYY-MM-DD).  
- `status` fields are enums: e.g., `pending`, `paid`, `cancelled`.  
- All IDs are `INTEGER PRIMARY KEY AUTOINCREMENT`.  
- Foreign keys are enforced.  
- This schema is designed for **Agentic ERP** workflows: Sales, Finance, Inventory, and RAG.

