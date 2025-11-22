# API Endpoints Documentation

Base URL: `/api/v1`

All endpoints (except authentication) require authentication via JWT (JSON Web Token). Include the access token in the Authorization header:
```
Authorization: Bearer <your_access_token_here>
```

---

## Authentication Endpoints

### 1. Register User
**Endpoint:** `POST /api/v1/auth/register/`  
**Authentication:** Not required

**Request Payload:**
```json
{
  "email": "user@example.com",
  "password": "password123",
  "password_confirm": "password123",
  "user_type": "customer",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Response (201 Created):**
```json
{
  "message": "User registered successfully",
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzA0MDY3ODAwLCJpYXQiOjE3MDQwNjY5MDAsImp0aSI6IjEyMzQ1Njc4IiwidXNlcl9pZCI6MX0.xyz123",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTcwNDE1MzMwMCwiaWF0IjoxNzA0MDY2OTAwLCJqdGkiOiI4NzY1NDMyMSIsInVzZXJfaWQiOjF9.abc456",
    "user": {
      "id": 1,
      "email": "user@example.com",
      "user_type": "customer"
    }
  }
}
```

**Error Response (400 Bad Request):**
```json
{
  "email": ["This field is required."],
  "password": ["This field is required."],
  "password_confirm": ["Passwords do not match"]
}
```

---

### 2. Login User
**Endpoint:** `POST /api/v1/auth/login/`  
**Authentication:** Not required

**Request Payload:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response (200 OK):**
```json
{
  "message": "Login successful",
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzA0MDY3ODAwLCJpYXQiOjE3MDQwNjY5MDAsImp0aSI6IjEyMzQ1Njc4IiwidXNlcl9pZCI6MX0.xyz123",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTcwNDE1MzMwMCwiaWF0IjoxNzA0MDY2OTAwLCJqdGkiOiI4NzY1NDMyMSIsInVzZXJfaWQiOjF9.abc456",
    "user": {
      "id": 1,
      "email": "user@example.com",
      "user_type": "customer"
    }
  }
}
```

**Error Response (400 Bad Request):**
```json
{
  "non_field_errors": ["Invalid credentials"]
}
```

---

### 3. Refresh Token
**Endpoint:** `POST /api/v1/auth/refresh/`  
**Authentication:** Not required

**Request Payload:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTcwNDE1MzMwMCwiaWF0IjoxNzA0MDY2OTAwLCJqdGkiOiI4NzY1NDMyMSIsInVzZXJfaWQiOjF9.abc456"
}
```

**Response (200 OK):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzA0MDY3ODAwLCJpYXQiOjE3MDQwNjY5MDAsImp0aSI6IjEyMzQ1Njc4IiwidXNlcl9pZCI6MX0.xyz123"
}
```

**Error Response (401 Unauthorized):**
```json
{
  "detail": "Token is invalid or expired",
  "code": "token_not_valid"
}
```

**Note:** When refresh token rotation is enabled (default), a new refresh token is also returned in the response. The old refresh token becomes invalid after use.

---

### 4. Get User Profile
**Endpoint:** `GET /api/v1/auth/profile/`  
**Authentication:** Required

**Response (200 OK):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "user_type": "customer",
  "date_joined": "2024-01-01T00:00:00Z"
}
```

---

### 5. Update User Profile
**Endpoint:** `PUT /api/v1/auth/profile/` or `PATCH /api/v1/auth/profile/`  
**Authentication:** Required

**Request Payload (PATCH - partial update):**
```json
{
  "email": "newemail@example.com",
  "first_name": "Jane",
  "last_name": "Smith"
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "email": "newemail@example.com",
  "username": "newemail@example.com",
  "first_name": "Jane",
  "last_name": "Smith",
  "user_type": "customer",
  "date_joined": "2024-01-01T00:00:00Z"
}
```

**Error Response (400 Bad Request):**
```json
{
  "email": ["This email is already in use."]
}
```

**Note:** When updating email, the username is automatically synced to match the new email address.

---

### 6. Change Password
**Endpoint:** `POST /api/v1/auth/change-password/`  
**Authentication:** Required

**Request Payload:**
```json
{
  "old_password": "oldpassword123",
  "new_password": "newpassword123",
  "new_password_confirm": "newpassword123"
}
```

**Response (200 OK):**
```json
{
  "message": "Password changed successfully"
}
```

**Error Response (400 Bad Request):**
```json
{
  "old_password": ["Old password is incorrect"]
}
```

or

```json
{
  "new_password": ["New passwords do not match"]
}
```

---

## Product Management Endpoints

### 7. List Products
**Endpoint:** `GET /api/v1/products/`  
**Authentication:** Required

**Query Parameters:**
- `search` (optional): Search in product name and description
- `category` (optional): Filter by category ID
- `page` (optional): Page number for pagination
- `page_size` (optional): Number of items per page (default: 20, max: 100)

**Example:** `GET /api/v1/products/?search=laptop&category=1&page=1`

**Response (200 OK):**
```json
{
  "count": 50,
  "next": "http://example.com/api/v1/products/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Laptop",
      "slug": "laptop",
      "description": "High-performance laptop",
      "category": {
        "id": 1,
        "name": "Electronics",
        "slug": "electronics",
        "description": "Electronic devices"
      },
      "category_id": 1,
      "price": "999.99",
      "stock_quantity": 50,
      "image": "http://example.com/media/products/laptop.jpg",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

---

### 8. Create Product
**Endpoint:** `POST /api/v1/products/`  
**Authentication:** Required (Admin only)

**Request Payload:**
```json
{
  "name": "Laptop",
  "description": "High-performance laptop",
  "category_id": 1,
  "price": "999.99",
  "stock_quantity": 50,
  "image": null
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "name": "Laptop",
  "slug": "laptop",
  "description": "High-performance laptop",
  "category": {
    "id": 1,
    "name": "Electronics",
    "slug": "electronics",
    "description": "Electronic devices"
  },
  "category_id": 1,
  "price": "999.99",
  "stock_quantity": 50,
  "image": null,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

**Error Response (403 Forbidden):**
```json
{
  "detail": "Only admins can create products"
}
```

---

### 9. Get Product Detail
**Endpoint:** `GET /api/v1/products/<id>/`  
**Authentication:** Required

**Response (200 OK):**
```json
{
  "id": 1,
  "name": "Laptop",
  "slug": "laptop",
  "description": "High-performance laptop",
  "category": {
    "id": 1,
    "name": "Electronics",
    "slug": "electronics",
    "description": "Electronic devices"
  },
  "category_id": 1,
  "price": "999.99",
  "stock_quantity": 50,
  "image": "http://example.com/media/products/laptop.jpg",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

**Error Response (404 Not Found):**
```json
{
  "detail": "Not found."
}
```

---

### 10. Update Product
**Endpoint:** `PUT /api/v1/products/<id>/` or `PATCH /api/v1/products/<id>/`  
**Authentication:** Required (Admin only)

**Request Payload (PATCH - partial update):**
```json
{
  "price": "899.99",
  "stock_quantity": 45
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "name": "Laptop",
  "slug": "laptop",
  "description": "High-performance laptop",
  "category": {
    "id": 1,
    "name": "Electronics",
    "slug": "electronics",
    "description": "Electronic devices"
  },
  "category_id": 1,
  "price": "899.99",
  "stock_quantity": 45,
  "image": null,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

**Error Response (403 Forbidden):**
```json
{
  "detail": "Only admins can update products"
}
```

---

### 11. Delete Product
**Endpoint:** `DELETE /api/v1/products/<id>/`  
**Authentication:** Required (Admin only)

**Response (200 OK):**
```json
{
  "message": "Product deleted successfully"
}
```

**Error Response (403 Forbidden):**
```json
{
  "detail": "Only admins can delete products"
}
```

---

## Category Management Endpoints

### 12. List Categories
**Endpoint:** `GET /api/v1/categories/`  
**Authentication:** Required

**Query Parameters:**
- `page` (optional): Page number for pagination
- `page_size` (optional): Number of items per page (default: 20, max: 100)

**Response (200 OK):**
```json
{
  "count": 10,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Electronics",
      "slug": "electronics",
      "description": "Electronic devices"
    }
  ]
}
```

---

### 13. Create Category
**Endpoint:** `POST /api/v1/categories/`  
**Authentication:** Required (Admin only)

**Request Payload:**
```json
{
  "name": "Electronics",
  "description": "Electronic devices"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "name": "Electronics",
  "slug": "electronics",
  "description": "Electronic devices"
}
```

**Error Response (403 Forbidden):**
```json
{
  "detail": "Only admins can create categories"
}
```

---

### 14. Get Category Detail
**Endpoint:** `GET /api/v1/categories/<id>/`  
**Authentication:** Required

**Response (200 OK):**
```json
{
  "id": 1,
  "name": "Electronics",
  "slug": "electronics",
  "description": "Electronic devices"
}
```

---

### 15. Update Category
**Endpoint:** `PUT /api/v1/categories/<id>/` or `PATCH /api/v1/categories/<id>/`  
**Authentication:** Required (Admin only)

**Request Payload (PATCH - partial update):**
```json
{
  "description": "Updated description for electronic devices"
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "name": "Electronics",
  "slug": "electronics",
  "description": "Updated description for electronic devices"
}
```

---

### 16. Delete Category
**Endpoint:** `DELETE /api/v1/categories/<id>/`  
**Authentication:** Required (Admin only)

**Response (200 OK):**
```json
{
  "message": "Category deleted successfully"
}
```

---

## Order Management Endpoints

### 17. List Orders
**Endpoint:** `GET /api/v1/orders/`  
**Authentication:** Required

**Note:** 
- Customers see only their own orders
- Admins see all orders

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "order_number": "ORD-1704067200",
    "customer": 1,
    "customer_email": "user@example.com",
    "total_amount": "1999.98",
    "status": "pending",
    "shipping_address": "123 Main St, City, State, ZIP",
    "billing_address": "123 Main St, City, State, ZIP",
    "items": [
      {
        "id": 1,
        "product": {
          "id": 1,
          "name": "Laptop",
          "slug": "laptop",
          "description": "High-performance laptop",
          "category": {
            "id": 1,
            "name": "Electronics",
            "slug": "electronics",
            "description": "Electronic devices"
          },
          "price": "999.99",
          "stock_quantity": 48,
          "image": null,
          "created_at": "2024-01-01T00:00:00Z",
          "updated_at": "2024-01-01T00:00:00Z"
        },
        "quantity": 2,
        "price": "999.99",
        "subtotal": "1999.98",
        "created_at": "2024-01-01T00:00:00Z"
      }
    ],
    "stripe_payment_intent_id": "pi_1234567890",
    "client_secret": "pi_1234567890_secret_xyz",
    "crm_sync_status": "success",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
]
```

---

### 18. Create Order
**Endpoint:** `POST /api/v1/orders/`  
**Authentication:** Required

**Request Payload:**
```json
{
  "shipping_address": "123 Main St, City, State, ZIP",
  "billing_address": "123 Main St, City, State, ZIP",
  "items": [
    {
      "product_id": 1,
      "quantity": 2
    },
    {
      "product_id": 2,
      "quantity": 1
    }
  ]
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "order_number": "ORD-1704067200",
  "customer": 1,
  "customer_email": "user@example.com",
  "total_amount": "1999.98",
  "status": "pending",
  "shipping_address": "123 Main St, City, State, ZIP",
  "billing_address": "123 Main St, City, State, ZIP",
  "items": [
    {
      "id": 1,
      "product": {
        "id": 1,
        "name": "Laptop",
        "slug": "laptop",
        "description": "High-performance laptop",
        "category": {
          "id": 1,
          "name": "Electronics",
          "slug": "electronics",
          "description": "Electronic devices"
        },
        "price": "999.99",
        "stock_quantity": 48,
        "image": null,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
      },
      "quantity": 2,
      "price": "999.99",
      "subtotal": "1999.98",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "stripe_payment_intent_id": null,
  "client_secret": null,
  "crm_sync_status": null,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

**Error Response (400 Bad Request):**
```json
{
  "items": [
    {
      "product_id": ["Product not found or inactive"]
    }
  ],
  "non_field_errors": ["Insufficient stock"]
}
```

---

### 19. Get Order Detail
**Endpoint:** `GET /api/v1/orders/<id>/`  
**Authentication:** Required

**Note:** 
- Customers can only access their own orders
- Admins can access any order

**Response (200 OK):**
```json
{
  "id": 1,
  "order_number": "ORD-1704067200",
  "customer": 1,
  "customer_email": "user@example.com",
  "total_amount": "1999.98",
  "status": "pending",
  "shipping_address": "123 Main St, City, State, ZIP",
  "billing_address": "123 Main St, City, State, ZIP",
  "items": [
    {
      "id": 1,
      "product": {
        "id": 1,
        "name": "Laptop",
        "slug": "laptop",
        "description": "High-performance laptop",
        "category": {
          "id": 1,
          "name": "Electronics",
          "slug": "electronics",
          "description": "Electronic devices"
        },
        "price": "999.99",
        "stock_quantity": 48,
        "image": null,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
      },
      "quantity": 2,
      "price": "999.99",
      "subtotal": "1999.98",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "stripe_payment_intent_id": "pi_1234567890",
  "client_secret": "pi_1234567890_secret_xyz",
  "crm_sync_status": "success",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

**Error Response (403 Forbidden):**
```json
{
  "detail": "You do not have permission to access this order."
}
```

---

### 20. Update Order
**Endpoint:** `PUT /api/v1/orders/<id>/` or `PATCH /api/v1/orders/<id>/`  
**Authentication:** Required

**Note:** 
- Customers can only update pending orders
- Admins can update any order

**Request Payload (PATCH - partial update):**
```json
{
  "status": "processing",
  "shipping_address": "456 New St, City, State, ZIP"
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "order_number": "ORD-1704067200",
  "customer": 1,
  "customer_email": "user@example.com",
  "total_amount": "1999.98",
  "status": "processing",
  "shipping_address": "456 New St, City, State, ZIP",
  "billing_address": "123 Main St, City, State, ZIP",
  "items": [...],
  "stripe_payment_intent_id": "pi_1234567890",
  "client_secret": "pi_1234567890_secret_xyz",
  "crm_sync_status": "success",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

**Error Response (400 Bad Request):**
```json
{
  "error": "Only pending orders can be updated"
}
```

---

### 21. Delete Order
**Endpoint:** `DELETE /api/v1/orders/<id>/`  
**Authentication:** Required

**Note:** 
- Customers can only delete pending orders
- Admins can delete any order

**Response (200 OK):**
```json
{
  "message": "Order deleted successfully"
}
```

**Error Response (400 Bad Request):**
```json
{
  "error": "Only pending orders can be deleted"
}
```

---

## Payment Endpoints

### 22. Create Payment Intent
**Endpoint:** `POST /api/v1/orders/<order_id>/create-payment/`  
**Authentication:** Required

**Note:** 
- Only pending orders can initiate payment
- Customers can only create payment for their own orders
- Admins can create payment for any order

**Response (200 OK):**
```json
{
  "client_secret": "pi_1234567890_secret_xyz",
  "payment_intent_id": "pi_1234567890"
}
```

**Error Response (400 Bad Request):**
```json
{
  "error": "Only pending orders can initiate payment"
}
```

**Error Response (403 Forbidden):**
```json
{
  "detail": "You do not have permission to access this order."
}
```

---

### 23. Confirm Payment
**Endpoint:** `POST /api/v1/orders/<order_id>/confirm-payment/`  
**Authentication:** Required

**Note:** 
- Customers can only confirm payment for their own orders
- Admins can confirm payment for any order
- If payment succeeds, order status is updated to "completed" and synced to CRM

**Response (200 OK):**
```json
{
  "message": "Payment confirmed successfully",
  "order": {
    "id": 1,
    "order_number": "ORD-1704067200",
    "customer": 1,
    "customer_email": "user@example.com",
    "total_amount": "1999.98",
    "status": "completed",
    "shipping_address": "123 Main St, City, State, ZIP",
    "billing_address": "123 Main St, City, State, ZIP",
    "items": [...],
    "stripe_payment_intent_id": "pi_1234567890",
    "client_secret": "pi_1234567890_secret_xyz",
    "crm_sync_status": "success",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
}
```

**Error Response (400 Bad Request):**
```json
{
  "error": "Payment intent not found for this order"
}
```

or

```json
{
  "error": "Payment requires a payment method",
  "client_secret": "pi_1234567890_secret_xyz"
}
```

---

### 24. Stripe Webhook
**Endpoint:** `POST /api/v1/webhooks/stripe/`  
**Authentication:** Not required (uses Stripe signature verification)

**Note:** This endpoint is called by Stripe to notify about payment events. It handles:
- `payment_intent.succeeded` - Updates order status to "completed" and syncs to CRM
- `payment_intent.payment_failed` - Updates order status to "cancelled" if pending
- `payment_intent.canceled` - Updates order status to "cancelled" if pending

**Request Headers:**
```
Stripe-Signature: t=1234567890,v1=signature_hash
```

**Request Body:** (Raw Stripe webhook payload)

**Response (200 OK):**
```json
{
  "status": "success"
}
```

**Error Response (400 Bad Request):**
```json
{
  "error": "Invalid payload"
}
```

or

```json
{
  "error": "Invalid signature"
}
```

---

## Cart Management Endpoints

### 26. Get Cart
**Endpoint:** `GET /api/v1/cart/`  
**Authentication:** Required

**Response (200 OK):**
```json
{
  "id": 1,
  "items": [
    {
      "id": 1,
      "product": {
        "id": 1,
        "name": "Laptop",
        "slug": "laptop",
        "description": "High-performance laptop",
        "category": {
          "id": 1,
          "name": "Electronics",
          "slug": "electronics",
          "description": "Electronic devices"
        },
        "price": "999.99",
        "stock_quantity": 50,
        "image": null,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
      },
      "quantity": 2,
      "price": "999.99",
      "subtotal": "1999.98",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total_amount": "1999.98",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

---

### 27. Add Item to Cart
**Endpoint:** `POST /api/v1/cart/`  
**Authentication:** Required

**Request Payload:**
```json
{
  "product_id": 1,
  "quantity": 2
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "product": {
    "id": 1,
    "name": "Laptop",
    "slug": "laptop",
    "description": "High-performance laptop",
    "category": {
      "id": 1,
      "name": "Electronics",
      "slug": "electronics",
      "description": "Electronic devices"
    },
    "price": "999.99",
    "stock_quantity": 48,
    "image": null,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  },
  "quantity": 2,
  "price": "999.99",
  "subtotal": "1999.98",
  "created_at": "2024-01-01T00:00:00Z"
}
```

**Error Response (400 Bad Request):**
```json
{
  "product_id": ["Product not found or inactive"]
}
```

or

```json
{
  "non_field_errors": ["Insufficient stock"]
}
```

**Note:** If the product already exists in the cart, the quantity will be updated by adding the new quantity to the existing quantity.

---

### 28. Clear Cart
**Endpoint:** `DELETE /api/v1/cart/`  
**Authentication:** Required

**Response (200 OK):**
```json
{
  "message": "Cart cleared successfully"
}
```

---

### 29. Update Cart Item
**Endpoint:** `PUT /api/v1/cart/items/<id>/` or `PATCH /api/v1/cart/items/<id>/`  
**Authentication:** Required

**Request Payload:**
```json
{
  "quantity": 3
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "product": {
    "id": 1,
    "name": "Laptop",
    "slug": "laptop",
    "description": "High-performance laptop",
    "category": {
      "id": 1,
      "name": "Electronics",
      "slug": "electronics",
      "description": "Electronic devices"
    },
    "price": "999.99",
    "stock_quantity": 47,
    "image": null,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  },
  "quantity": 3,
  "price": "999.99",
  "subtotal": "2999.97",
  "created_at": "2024-01-01T00:00:00Z"
}
```

**Error Response (400 Bad Request):**
```json
{
  "quantity": ["This field is required."]
}
```

or

```json
{
  "quantity": ["Quantity must be at least 1."]
}
```

or

```json
{
  "error": "Insufficient stock"
}
```

**Error Response (404 Not Found):**
```json
{
  "detail": "Not found."
}
```

---

### 30. Remove Cart Item
**Endpoint:** `DELETE /api/v1/cart/items/<id>/`  
**Authentication:** Required

**Response (200 OK):**
```json
{
  "message": "Cart item removed successfully"
}
```

**Error Response (404 Not Found):**
```json
{
  "detail": "Not found."
}
```

---

### 31. Cart Checkout
**Endpoint:** `POST /api/v1/cart/checkout/`  
**Authentication:** Required

**Request Payload:**
```json
{
  "shipping_address": "123 Main St, City, State, ZIP",
  "billing_address": "123 Main St, City, State, ZIP",
  "clear_cart": true
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "order_number": "ORD-1704067200",
  "customer": 1,
  "customer_email": "user@example.com",
  "total_amount": "1999.98",
  "status": "pending",
  "shipping_address": "123 Main St, City, State, ZIP",
  "billing_address": "123 Main St, City, State, ZIP",
  "items": [
    {
      "id": 1,
      "product": {
        "id": 1,
        "name": "Laptop",
        "slug": "laptop",
        "description": "High-performance laptop",
        "category": {
          "id": 1,
          "name": "Electronics",
          "slug": "electronics",
          "description": "Electronic devices"
        },
        "price": "999.99",
        "stock_quantity": 48,
        "image": null,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
      },
      "quantity": 2,
      "price": "999.99",
      "subtotal": "1999.98",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "stripe_payment_intent_id": null,
  "client_secret": null,
  "crm_sync_status": null,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

**Error Response (400 Bad Request):**
```json
{
  "error": "Cart is empty"
}
```

or

```json
{
  "error": "Insufficient stock for Laptop"
}
```

**Note:** 
- Creates an order from all items in the cart
- Updates product stock quantities
- Optionally clears the cart after checkout (default: true)
- If any product has insufficient stock, the order creation is rolled back

---

## Reports Endpoints

### 32. Reports Summary
**Endpoint:** `GET /api/v1/reports/summary/`  
**Authentication:** Required (Admin only)

**Response (200 OK):**
```json
{
  "total_orders": 150,
  "total_revenue": 125000.50,
  "paid_orders": 120,
  "pending_orders": 30
}
```

**Error Response (403 Forbidden):**
```json
{
  "error": "Only admins can access reports"
}
```

---

## Order Status Values

- `pending` - Order created but payment not initiated
- `processing` - Order is being processed
- `completed` - Payment successful and order completed
- `cancelled` - Order cancelled

---

## User Types

- `customer` - Regular customer user
- `admin` - Administrator user with full access

---

## JWT Token Information

### Token Types

- **Access Token**: Used to authenticate API requests. Short-lived for security.
- **Refresh Token**: Used to obtain new access tokens when the current one expires. Longer-lived.

### Token Lifetimes

- **Access Token**: 15 minutes
- **Refresh Token**: 1 day

### Using Tokens

1. **Initial Authentication**: After registering or logging in, you receive both `access_token` and `refresh_token`.
2. **Making API Requests**: Include the access token in the Authorization header:
   ```
   Authorization: Bearer <access_token>
   ```
3. **Token Expiration**: When the access token expires (after 15 minutes), you'll receive a `401 Unauthorized` response.
4. **Refreshing Tokens**: Use the refresh token endpoint to get a new access token:
   - Send a POST request to `/api/v1/auth/refresh/` with the `refresh_token` in the request body.
   - You'll receive a new `access_token` (and optionally a new `refresh_token` if rotation is enabled).
5. **Token Rotation**: By default, refresh tokens are rotated. After using a refresh token, it becomes invalid and you must use the new refresh token for subsequent refreshes.

### Token Expiration Handling

When an access token expires:
- The API will return a `401 Unauthorized` response with error details.
- Use the refresh token to obtain a new access token without requiring the user to log in again.
- If the refresh token is also expired, the user must log in again to obtain new tokens.

---

## Pagination

Most list endpoints support pagination with the following query parameters:
- `page` - Page number (default: 1)
- `page_size` - Items per page (default: 20, max: 100)

Pagination response format:
```json
{
  "count": 100,
  "next": "http://example.com/api/v1/endpoint/?page=2",
  "previous": null,
  "results": [...]
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "field_name": ["Error message"],
  "non_field_errors": ["General error message"]
}
```

### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden
```json
{
  "detail": "You do not have permission to perform this action."
}
```

### 404 Not Found
```json
{
  "detail": "Not found."
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal server error"
}
```


