# Mini Order & Payment System

## Project Overview

- **Backend**: Django + DRF
- **Frontend**: React
- **Database**: PostgreSQL or MySQL
- **Payment Integration**: Stripe or Razorpay Sandbox
- **External API Integration**: CRM Sync
- **Features**: Basic e-commerce workflow, ERP-style reporting
- **Deployment**: Nginx + Gunicorn

## System Requirements

### User Types

There are only two user categories:

#### 1. Admin (via Django Admin Panel only)
- Adds/Edits/Deletes products
- Can view orders in admin panel
- **Note**: No admin UI is needed in React.

#### 2. Customer (React Frontend)
- Register & login
- View product list
- Create order
- Make payment (Stripe/Razorpay sandbox)
- See payment result
- CRM sync result shown after payment

## Database

**Minimal: 3 Tables use**

Database choice: PostgreSQL or MySQL.

## Required API Endpoints

### Authentication
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`

### Products
- `GET /api/v1/products/` → customers fetch products
  - Must use optimized queries (select_related/pagination)

### Orders
- `POST /api/v1/orders/` → create order
- `POST /api/v1/orders/{id}/create-payment/` → initiate Stripe/Razorpay payment
- `POST /api/v1/orders/{id}/confirm-payment/` → verify & mark paid

### CRM Sync (Backend Internal Logic)

After payment confirmation, backend must send order details to an external CRM API, such as:
- `https://dummyjson.com/posts/add`

### Reports
- `GET /api/v1/reports/summary/`
- **Returns**:
  - `total_orders`
  - `total_revenue`
  - `paid_orders`
  - `pending_orders`

## Payment Integration

You must integrate either Stripe or Razorpay Sandbox.

## CRM API Integration

After successful payment:
- Backend must call a dummy CRM API, e.g.:
  ```
  POST https://dummyjson.com/posts/add
  {
    "order_id": <id>,
    "amount": <amount>,
    "customer_email": <email>
  }
  ```
- **Update**: `crm_sync_status = success / failed`
- This demonstrates third-party API integration.

## ERP-Style Summary Reporting

**Endpoint**: `GET /api/v1/reports/summary/`

**Response should include**:
- `total_orders`
- `total_revenue`
- `number of paid orders`
- `number of pending orders`

This demonstrates aggregation and reporting logic, no UI needed.

## Frontend Requirements (React)

### Required Pages

#### 1. Login / Registration Page
- JWT stored in localStorage
- Protected routes implemented

#### 2. Product List
- Fetch `/api/v1/products/`
- Show name + price
- "Buy Now" action

#### 3. Create Order + Payment Flow
1. Customer selects product
2. React calls `/api/v1/orders/`
3. Backend returns order_id
4. React calls `/api/v1/orders/{id}/create-payment/`
5. Stripe checkout or Razorpay popup
6. On success → call `/api/v1/orders/{id}/confirm-payment/`
7. Show success message + CRM sync status

#### 4. Reports Page
- Call `/api/v1/reports/summary/`
- Display numbers (simple UI)

**Note**: No admin frontend needed.

## Deployment Requirement

Candidate must provide a deployment-ready setup using:
- **Nginx + Gunicorn**

Include in repository:

1. **nginx.conf**
   - Reverse proxy
   - Serve static files
   - Proxy pass to Gunicorn

2. **gunicorn.service**
   - Systemd service configuration

3. **Notes on environment variables**

4. **Instructions to run the project in production mode**

**Note**: You do NOT need to deploy it to a server, but configuration MUST be included.

## Deliverables

Submit a GitHub repository containing:

### Backend
- Django project
- Environment variable template
- Nginx config
- Gunicorn service file

### Frontend
- React project
- `.env.example` with API base URL

### Documentation
- README explaining setup
- Stripe/Razorpay sandbox setup instructions
- CRM API endpoint used
- How to run backend & frontend
- How to test payment flow



