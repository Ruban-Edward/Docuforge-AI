# DocuForge AI — API Specification

> **Version:** 1.0.0  
> **Base URL:** `https://api.docuforge.ai/api/v1`  
> **Protocol:** HTTPS only  
> **Data Format:** JSON (unless otherwise noted for file uploads/downloads)  
> **Auth:** JWT Bearer tokens

---

## Table of Contents

1. [Overview](#overview)
2. [Standard Response Envelope](#standard-response-envelope)
3. [Authentication Header](#authentication-header)
4. [Pagination](#pagination)
5. [Error Code Catalogue](#error-code-catalogue)
6. [User Roles & Permissions](#user-roles--permissions)
7. [Endpoint Groups](#endpoint-groups)
   - [1. Authentication](#1-authentication-apiv1auth)
   - [2. Users](#2-users-apiv1users)
   - [3. Departments](#3-departments-apiv1departments)
   - [4. Templates](#4-templates-apiv1templates)
   - [5. Template Sections](#5-template-sections)
   - [6. Documents](#6-documents-apiv1documents)
   - [7. File Upload](#7-file-upload)
   - [8. AI Processing](#8-ai-processing)
   - [9. Section Mapping & Missing Sections](#9-section-mapping--missing-sections)
   - [10. Document Generation](#10-document-generation)
   - [11. Document Export](#11-document-export)
   - [12. Document Versions](#12-document-versions)
   - [13. Document Reviews](#13-document-reviews)
   - [14. Admin](#14-admin-apiv1admin)

---

## Overview

DocuForge AI is an AI-powered documentation standardisation platform. It allows organisations to upload raw documents, process them against predefined templates using AI extraction, fill in missing sections, generate polished standardised documents, and manage review workflows — all through a RESTful API.

**Technology Stack:**
- Backend: Python + FastAPI
- Auth: JWT (access + refresh token pair)
- All endpoints prefixed with `/api/v1/`

---

## Standard Response Envelope

All API responses are wrapped in a standard envelope:

**Success:**
```json
{
  "success": true,
  "data": { },
  "message": "Optional human-readable message",
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 100,
    "pages": 5
  }
}
```

> `pagination` is only present on list endpoints. `message` is optional.

**Error:**
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Human-readable error message",
    "details": [
      {
        "field": "email",
        "message": "Invalid email format"
      }
    ]
  }
}
```

> `details` is optional and contains field-level validation errors when applicable.

---

## Authentication Header

All authenticated endpoints require the following HTTP header:

```
Authorization: Bearer <access_token>
```

The access token is a short-lived JWT (default: 15 minutes). Use the refresh token endpoint to obtain a new access token without re-authenticating.

---

## Pagination

List endpoints support the following query parameters:

| Parameter | Type | Default | Description |
|---|---|---|---|
| `page` | integer | `1` | Page number (1-indexed) |
| `per_page` | integer | `20` | Items per page (max 100) |
| `sort_by` | string | `created_at` | Field to sort by |
| `sort_dir` | string | `desc` | Sort direction: `asc` or `desc` |

Example: `GET /api/v1/documents?page=2&per_page=10&sort_by=title&sort_dir=asc`

---

## Error Code Catalogue

The following error codes are used across the API and appear in the `error.code` field of error responses:

| Code | HTTP Status | Description |
|---|---|---|
| `INVALID_CREDENTIALS` | 401 | Email/password combination is incorrect |
| `TOKEN_EXPIRED` | 401 | The JWT access or refresh token has expired |
| `TOKEN_INVALID` | 401 | The token is malformed or signature is invalid |
| `TOKEN_REVOKED` | 401 | The refresh token has been revoked (logged out) |
| `NOT_AUTHENTICATED` | 401 | No token provided in Authorization header |
| `FORBIDDEN` | 403 | Authenticated but insufficient role/ownership |
| `USER_NOT_FOUND` | 404 | User with given ID does not exist |
| `USER_INACTIVE` | 403 | User account has been deactivated |
| `USER_ALREADY_EXISTS` | 409 | Email is already registered |
| `DEPARTMENT_NOT_FOUND` | 404 | Department with given ID does not exist |
| `TEMPLATE_NOT_FOUND` | 404 | Template with given ID does not exist |
| `TEMPLATE_VERSION_NOT_FOUND` | 404 | Template version with given ID does not exist |
| `TEMPLATE_VERSION_NOT_PUBLISHED` | 422 | Cannot use an unpublished template version |
| `SECTION_NOT_FOUND` | 404 | Section with given ID does not exist |
| `SECTION_MANDATORY_SKIPPED` | 422 | Attempted to skip a mandatory section |
| `DOCUMENT_NOT_FOUND` | 404 | Document with given ID does not exist |
| `DOCUMENT_ALREADY_GENERATED` | 409 | Document generation already completed for this version |
| `DOCUMENT_VERSION_NOT_FOUND` | 404 | Document version with given ID does not exist |
| `INVALID_FILE_TYPE` | 422 | Uploaded file MIME type is not supported |
| `FILE_TOO_LARGE` | 413 | Uploaded file exceeds the 20 MB limit |
| `FILE_UPLOAD_FAILED` | 500 | File could not be saved to storage |
| `AI_PROCESSING_FAILED` | 502 | AI provider returned an error or timed out |
| `AI_JOB_NOT_FOUND` | 404 | Processing job ID does not exist |
| `GENERATION_FAILED` | 500 | Document generation encountered an internal error |
| `REVIEW_NOT_FOUND` | 404 | Review record with given ID does not exist |
| `INVALID_REVIEW_DECISION` | 422 | Review decision must be `approve`, `reject`, or `request_changes` |
| `VALIDATION_ERROR` | 422 | Request body or query parameter validation failed |
| `RESET_TOKEN_INVALID` | 400 | Password reset token is invalid or has expired |
| `WRONG_CURRENT_PASSWORD` | 400 | Provided current password does not match |
| `INTERNAL_SERVER_ERROR` | 500 | Unexpected server-side error |

---

## User Roles & Permissions

Roles are hierarchical — higher roles inherit all permissions of lower roles.

| Role | Level | Description |
|---|---|---|
| `developer` | 1 | Can create and manage own documents |
| `manager` | 2 | Developer permissions + review documents, view team documents |
| `admin` | 3 | Manager permissions + manage users, departments, templates |
| `super_admin` | 4 | Full access including system configuration |

> **Role shorthand used in this document:**  
> - `Any authenticated` = any valid JWT, regardless of role  
> - `developer+` = developer, manager, admin, or super_admin  
> - `manager+` = manager, admin, or super_admin  
> - `admin+` = admin or super_admin

---

## Endpoint Groups

---

## 1. Authentication (`/api/v1/auth`)

---

#### `POST /api/v1/auth/login`
**Purpose:** Authenticate a user with email and password, returning a JWT access token and refresh token.  
**Auth Required:** No  
**Required Role:** N/A  

**Request:**
```json
{
  "email": "alice@example.com",
  "password": "S3cur3P@ssword!"
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "dGhpcyBpcyBhIHJlZnJlc2ggdG9rZW4...",
    "token_type": "bearer",
    "expires_in": 900,
    "user": {
      "id": "usr_01HXZ4N3M5KQRP8VWTJG2D6YB",
      "email": "alice@example.com",
      "full_name": "Alice Johnson",
      "role": "developer",
      "department_id": "dept_01HXZ4N3M5KQRP8VWTJG2D6YB",
      "is_active": true
    }
  },
  "message": "Login successful"
}
```

**Errors:**  
- `400` – missing required fields  
- `401` – `INVALID_CREDENTIALS` — wrong email or password  
- `403` – `USER_INACTIVE` — account has been deactivated  
- `422` – unprocessable entity (malformed JSON)  

---

#### `POST /api/v1/auth/refresh`
**Purpose:** Exchange a valid refresh token for a new access token and rotate the refresh token.  
**Auth Required:** No  
**Required Role:** N/A  

**Request:**
```json
{
  "refresh_token": "dGhpcyBpcyBhIHJlZnJlc2ggdG9rZW4..."
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "bmV3UmVmcmVzaFRva2Vu...",
    "token_type": "bearer",
    "expires_in": 900
  }
}
```

**Errors:**  
- `400` – missing `refresh_token` field  
- `401` – `TOKEN_EXPIRED` / `TOKEN_INVALID` / `TOKEN_REVOKED`  
- `422` – unprocessable entity  

---

#### `POST /api/v1/auth/logout`
**Purpose:** Revoke the current refresh token, effectively ending the user's session.  
**Auth Required:** Yes  
**Required Role:** Any authenticated  

**Request:**
```json
{
  "refresh_token": "dGhpcyBpcyBhIHJlZnJlc2ggdG9rZW4..."
}
```

**Response (200):**
```json
{
  "success": true,
  "data": null,
  "message": "Logged out successfully"
}
```

**Errors:**  
- `401` – `NOT_AUTHENTICATED` — missing or invalid access token  
- `422` – unprocessable entity  

---

#### `GET /api/v1/auth/me`
**Purpose:** Retrieve the profile of the currently authenticated user.  
**Auth Required:** Yes  
**Required Role:** Any authenticated  

**Request:** _(no body)_

**Response (200):**
```json
{
  "success": true,
  "data": {
    "id": "usr_01HXZ4N3M5KQRP8VWTJG2D6YB",
    "email": "alice@example.com",
    "full_name": "Alice Johnson",
    "role": "developer",
    "department": {
      "id": "dept_01HXZ4N3M5KQRP8VWTJG2D6YB",
      "name": "Engineering"
    },
    "is_active": true,
    "created_at": "2024-01-15T09:00:00Z",
    "last_login_at": "2024-06-01T08:30:00Z"
  }
}
```

**Errors:**  
- `401` – `NOT_AUTHENTICATED` / `TOKEN_EXPIRED` / `TOKEN_INVALID`  

---

#### `POST /api/v1/auth/change-password`
**Purpose:** Change the authenticated user's own password by verifying the current password first.  
**Auth Required:** Yes  
**Required Role:** Any authenticated  

**Request:**
```json
{
  "current_password": "OldP@ssword123",
  "new_password": "NewS3cur3P@ss!",
  "confirm_password": "NewS3cur3P@ss!"
}
```

**Response (200):**
```json
{
  "success": true,
  "data": null,
  "message": "Password changed successfully"
}
```

**Errors:**  
- `400` – `WRONG_CURRENT_PASSWORD` — current password is incorrect  
- `401` – `NOT_AUTHENTICATED`  
- `422` – `new_password` and `confirm_password` do not match, or password does not meet complexity requirements  

---

#### `POST /api/v1/auth/forgot-password`
**Purpose:** Initiate a password reset flow by generating a reset token for the given email (MVP: token is logged server-side; email sending is a future enhancement).  
**Auth Required:** No  
**Required Role:** N/A  

**Request:**
```json
{
  "email": "alice@example.com"
}
```

**Response (200):**
```json
{
  "success": true,
  "data": null,
  "message": "If this email is registered, a password reset link has been sent"
}
```

> **Note:** Always returns 200 regardless of whether the email exists, to prevent user enumeration. In MVP mode, the reset token is written to the application log.

**Errors:**  
- `422` – invalid email format  

---

#### `POST /api/v1/auth/reset-password`
**Purpose:** Reset a user's password using a valid password reset token.  
**Auth Required:** No  
**Required Role:** N/A  

**Request:**
```json
{
  "token": "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4",
  "new_password": "NewS3cur3P@ss!",
  "confirm_password": "NewS3cur3P@ss!"
}
```

**Response (200):**
```json
{
  "success": true,
  "data": null,
  "message": "Password has been reset successfully. Please log in with your new password."
}
```

**Errors:**  
- `400` – `RESET_TOKEN_INVALID` — token is expired, already used, or not found  
- `422` – passwords do not match or do not meet complexity requirements  

---

## 2. Users (`/api/v1/users`)

> All write operations require `admin+`. Read operations on other users' data also require `admin+`.

---

#### `GET /api/v1/users`
**Purpose:** Retrieve a paginated, filterable list of all registered users.  
**Auth Required:** Yes  
**Required Role:** admin+  

**Query Parameters:**

| Parameter | Type | Description |
|---|---|---|
| `role` | string | Filter by role: `developer`, `manager`, `admin`, `super_admin` |
| `department_id` | string | Filter by department ID |
| `is_active` | boolean | Filter by active status (`true` / `false`) |
| `search` | string | Search by name or email (partial match) |
| `page` | integer | Page number |
| `per_page` | integer | Items per page |

**Request:** _(no body; query params only)_

**Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": "usr_01HXZ4N3M5KQRP8VWTJG2D6YB",
      "email": "alice@example.com",
      "full_name": "Alice Johnson",
      "role": "developer",
      "department": {
        "id": "dept_01HXZ4N3M5KQRP8VWTJG2D6YB",
        "name": "Engineering"
      },
      "is_active": true,
      "created_at": "2024-01-15T09:00:00Z",
      "last_login_at": "2024-06-01T08:30:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 85,
    "pages": 5
  }
}
```

**Errors:**  
- `401` – not authenticated  
- `403` – forbidden (insufficient role)  

---

#### `POST /api/v1/users`
**Purpose:** Create a new user account with a specified role and department.  
**Auth Required:** Yes  
**Required Role:** admin+  

**Request:**
```json
{
  "email": "bob@example.com",
  "full_name": "Bob Smith",
  "password": "TempP@ssword123!",
  "role": "developer",
  "department_id": "dept_01HXZ4N3M5KQRP8VWTJG2D6YB"
}
```

**Response (201):**
```json
{
  "success": true,
  "data": {
    "id": "usr_02IYA5O4N6LRSQ9WUKHJ3E7ZC",
    "email": "bob@example.com",
    "full_name": "Bob Smith",
    "role": "developer",
    "department": {
      "id": "dept_01HXZ4N3M5KQRP8VWTJG2D6YB",
      "name": "Engineering"
    },
    "is_active": true,
    "created_at": "2024-06-01T10:00:00Z"
  },
  "message": "User created successfully"
}
```

**Errors:**  
- `400` – validation error  
- `401` – not authenticated  
- `403` – forbidden  
- `404` – `DEPARTMENT_NOT_FOUND`  
- `409` – `USER_ALREADY_EXISTS`  
- `422` – unprocessable entity  

---

#### `GET /api/v1/users/{user_id}`
**Purpose:** Retrieve full profile details for a specific user by ID.  
**Auth Required:** Yes  
**Required Role:** admin+  

**Request:** _(no body)_

**Response (200):**
```json
{
  "success": true,
  "data": {
    "id": "usr_01HXZ4N3M5KQRP8VWTJG2D6YB",
    "email": "alice@example.com",
    "full_name": "Alice Johnson",
    "role": "developer",
    "department": {
      "id": "dept_01HXZ4N3M5KQRP8VWTJG2D6YB",
      "name": "Engineering"
    },
    "is_active": true,
    "created_at": "2024-01-15T09:00:00Z",
    "updated_at": "2024-05-20T14:22:00Z",
    "last_login_at": "2024-06-01T08:30:00Z",
    "document_count": 12
  }
}
```

**Errors:**  
- `401` – not authenticated  
- `403` – forbidden  
- `404` – `USER_NOT_FOUND`  

---

#### `PUT /api/v1/users/{user_id}`
**Purpose:** Update profile details (name, department) for a specific user.  
**Auth Required:** Yes  
**Required Role:** admin+  

**Request:**
```json
{
  "full_name": "Alice M. Johnson",
  "department_id": "dept_02IYA5O4N6LRSQ9WUKHJ3E7ZC"
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "id": "usr_01HXZ4N3M5KQRP8VWTJG2D6YB",
    "email": "alice@example.com",
    "full_name": "Alice M. Johnson",
    "role": "developer",
    "department": {
      "id": "dept_02IYA5O4N6LRSQ9WUKHJ3E7ZC",
      "name": "Product"
    },
    "is_active": true,
    "updated_at": "2024-06-01T11:00:00Z"
  },
  "message": "User updated successfully"
}
```

**Errors:**  
- `400` – validation error  
- `401` – not authenticated  
- `403` – forbidden  
- `404` – `USER_NOT_FOUND` / `DEPARTMENT_NOT_FOUND`  
- `422` – unprocessable entity  

---

#### `DELETE /api/v1/users/{user_id}`
**Purpose:** Soft-delete a user account (marks as inactive; data is retained).  
**Auth Required:** Yes  
**Required Role:** admin+  

**Request:** _(no body)_

**Response (200):**
```json
{
  "success": true,
  "data": null,
  "message": "User deleted successfully"
}
```

**Errors:**  
- `401` – not authenticated  
- `403` – forbidden  
- `404` – `USER_NOT_FOUND`  

---

#### `PUT /api/v1/users/{user_id}/activate`
**Purpose:** Reactivate a previously deactivated user account.  
**Auth Required:** Yes  
**Required Role:** admin+  

**Request:** _(no body)_

**Response (200):**
```json
{
  "success": true,
  "data": {
    "id": "usr_01HXZ4N3M5KQRP8VWTJG2D6YB",
    "is_active": true,
    "updated_at": "2024-06-01T12:00:00Z"
  },
  "message": "User activated successfully"
}
```

**Errors:**  
- `401` – not authenticated  
- `403` – forbidden  
- `404` – `USER_NOT_FOUND`  

---

#### `PUT /api/v1/users/{user_id}/deactivate`
**Purpose:** Deactivate a user account, preventing login without deleting data.  
**Auth Required:** Yes  
**Required Role:** admin+  

**Request:** _(no body)_

**Response (200):**
```json
{
  "success": true,
  "data": {
    "id": "usr_01HXZ4N3M5KQRP8VWTJG2D6YB",
    "is_active": false,
    "updated_at": "2024-06-01T12:30:00Z"
  },
  "message": "User deactivated successfully"
}
```

**Errors:**  
- `401` – not authenticated  
- `403` – forbidden  
- `404` – `USER_NOT_FOUND`  

---

#### `PUT /api/v1/users/{user_id}/role`
**Purpose:** Change the assigned role of a user.  
**Auth Required:** Yes  
**Required Role:** admin+  

**Request:**
```json
{
  "role": "manager"
}
```

> Valid values: `developer`, `manager`, `admin`, `super_admin`. Only `super_admin` can assign/modify `super_admin` role.

**Response (200):**
```json
{
  "success": true,
  "data": {
    "id": "usr_01HXZ4N3M5KQRP8VWTJG2D6YB",
    "email": "alice@example.com",
    "role": "manager",
    "updated_at": "2024-06-01T13:00:00Z"
  },
  "message": "User role updated successfully"
}
```

**Errors:**  
- `400` – invalid role value  
- `401` – not authenticated  
- `403` – forbidden (e.g. admin trying to assign super_admin)  
- `404` – `USER_NOT_FOUND`  
- `422` – unprocessable entity  

---

## 3. Departments (`/api/v1/departments`)

> Read operations: any authenticated user. Write operations: admin+.

---

#### `GET /api/v1/departments`
**Purpose:** Retrieve a list of all departments in the organisation.  
**Auth Required:** Yes  
**Required Role:** Any authenticated  

**Query Parameters:**

| Parameter | Type | Description |
|---|---|---|
| `is_active` | boolean | Filter by active status |
| `search` | string | Search by name |

**Request:** _(no body)_

**Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": "dept_01HXZ4N3M5KQRP8VWTJG2D6YB",
      "name": "Engineering",
      "description": "Software development and infrastructure",
      "is_active": true,
      "member_count": 23,
      "created_at": "2024-01-01T00:00:00Z"
    },
    {
      "id": "dept_02IYA5O4N6LRSQ9WUKHJ3E7ZC",
      "name": "Product",
      "description": "Product management and design",
      "is_active": true,
      "member_count": 10,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 8,
    "pages": 1
  }
}
```

**Errors:**  
- `401` – not authenticated  

---

#### `POST /api/v1/departments`
**Purpose:** Create a new department.  
**Auth Required:** Yes  
**Required Role:** admin+  

**Request:**
```json
{
  "name": "Legal",
  "description": "Legal and compliance team"
}
```

**Response (201):**
```json
{
  "success": true,
  "data": {
    "id": "dept_03JZB6P5O7MSTR0XVLIJ4F8AD",
    "name": "Legal",
    "description": "Legal and compliance team",
    "is_active": true,
    "member_count": 0,
    "created_at": "2024-06-01T14:00:00Z"
  },
  "message": "Department created successfully"
}
```

**Errors:**  
- `400` – validation error  
- `401` – not authenticated  
- `403` – forbidden  
- `409` – department name already exists  
- `422` – unprocessable entity  

---

#### `GET /api/v1/departments/{dept_id}`
**Purpose:** Retrieve details for a specific department by ID.  
**Auth Required:** Yes  
**Required Role:** Any authenticated  

**Request:** _(no body)_

**Response (200):**
```json
{
  "success": true,
  "data": {
    "id": "dept_01HXZ4N3M5KQRP8VWTJG2D6YB",
    "name": "Engineering",
    "description": "Software development and infrastructure",
    "is_active": true,
    "member_count": 23,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-03-15T09:00:00Z"
  }
}
```

**Errors:**  
- `401` – not authenticated  
- `404` – `DEPARTMENT_NOT_FOUND`  

---

#### `PUT /api/v1/departments/{dept_id}`
**Purpose:** Update the name or description of an existing department.  
**Auth Required:** Yes  
**Required Role:** admin+  

**Request:**
```json
{
  "name": "Engineering & Infrastructure",
  "description": "Software engineering, DevOps, and infrastructure"
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "id": "dept_01HXZ4N3M5KQRP8VWTJG2D6YB",
    "name": "Engineering & Infrastructure",
    "description": "Software engineering, DevOps, and infrastructure",
    "is_active": true,
    "updated_at": "2024-06-01T15:00:00Z"
  },
  "message": "Department updated successfully"
}
```

**Errors:**  
- `400` – validation error  
- `401` – not authenticated  
- `403` – forbidden  
- `404` – `DEPARTMENT_NOT_FOUND`  
- `422` – unprocessable entity  

---

#### `DELETE /api/v1/departments/{dept_id}`
**Purpose:** Soft-delete a department (marks as inactive; existing users are not removed).  
**Auth Required:** Yes  
**Required Role:** admin+  

**Request:** _(no body)_

**Response (200):**
```json
{
  "success": true,
  "data": null,
  "message": "Department deleted successfully"
}
```

**Errors:**  
- `401` – not authenticated  
- `403` – forbidden  
- `404` – `DEPARTMENT_NOT_FOUND`  

---

## 4. Templates (`/api/v1/templates`)

> Read operations: any authenticated user. Write operations: admin+.

---

#### `GET /api/v1/templates`
**Purpose:** Retrieve a paginated list of document templates (active only by default).  
**Auth Required:** Yes  
**Required Role:** Any authenticated  

**Query Parameters:**

| Parameter | Type | Description |
|---|---|---|
| `is_active` | boolean | Default `true`. Pass `false` to include inactive (admin+ only) |
| `search` | string | Search by name or description |
| `category` | string | Filter by template category |

**Request:** _(no body)_

**Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": "tmpl_01HXZ4N3M5KQRP8VWTJG2D6YB",
      "name": "Technical Design Document",
      "description": "Standard TDD template for engineering teams",
      "category": "engineering",
      "is_active": true,
      "current_version": {
        "id": "tver_01HXZ4N3M5KQRP8VWTJG2D6YB",
        "version_number": "1.2.0",
        "is_published": true
      },
      "created_at": "2024-02-01T00:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 15,
    "pages": 1
  }
}
```

**Errors:**  
- `401` – not authenticated  

---

#### `POST /api/v1/templates`
**Purpose:** Create a new document template with metadata.  
**Auth Required:** Yes  
**Required Role:** admin+  

**Request:**
```json
{
  "name": "Project Proposal",
  "description": "Standard project proposal template for all departments",
  "category": "management",
  "is_active": true
}
```

**Response (201):**
```json
{
  "success": true,
  "data": {
    "id": "tmpl_02IYA5O4N6LRSQ9WUKHJ3E7ZC",
    "name": "Project Proposal",
    "description": "Standard project proposal template for all departments",
    "category": "management",
    "is_active": true,
    "current_version": null,
    "created_at": "2024-06-01T16:00:00Z"
  },
  "message": "Template created successfully"
}
```

**Errors:**  
- `400` – validation error  
- `401` – not authenticated  
- `403` – forbidden  
- `422` – unprocessable entity  

---

#### `GET /api/v1/templates/{template_id}`
**Purpose:** Retrieve full metadata and current published version for a specific template.  
**Auth Required:** Yes  
**Required Role:** Any authenticated  

**Request:** _(no body)_

**Response (200):**
```json
{
  "success": true,
  "data": {
    "id": "tmpl_01HXZ4N3M5KQRP8VWTJG2D6YB",
    "name": "Technical Design Document",
    "description": "Standard TDD template for engineering teams",
    "category": "engineering",
    "is_active": true,
    "current_version": {
      "id": "tver_01HXZ4N3M5KQRP8VWTJG2D6YB",
      "version_number": "1.2.0",
      "is_published": true,
      "published_at": "2024-05-10T10:00:00Z",
      "file_url": "https://storage.docuforge.ai/templates/tmpl_01.../v1.2.0/template.docx",
      "section_count": 8
    },
    "version_count": 4,
    "created_at": "2024-02-01T00:00:00Z",
    "updated_at": "2024-05-10T10:00:00Z"
  }
}
```

**Errors:**  
- `401` – not authenticated  
- `404` – `TEMPLATE_NOT_FOUND`  

---

#### `PUT /api/v1/templates/{template_id}`
**Purpose:** Update the metadata (name, description, category, active status) of a template.  
**Auth Required:** Yes  
**Required Role:** admin+  

**Request:**
```json
{
  "name": "Technical Design Document v2",
  "description": "Updated TDD template with new compliance sections",
  "category": "engineering",
  "is_active": true
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "id": "tmpl_01HXZ4N3M5KQRP8VWTJG2D6YB",
    "name": "Technical Design Document v2",
    "description": "Updated TDD template with new compliance sections",
    "category": "engineering",
    "is_active": true,
    "updated_at": "2024-06-01T17:00:00Z"
  },
  "message": "Template updated successfully"
}
```

**Errors:**  
- `400` – validation error  
- `401` – not authenticated  
- `403` – forbidden  
- `404` – `TEMPLATE_NOT_FOUND`  
- `422` – unprocessable entity  

---

#### `DELETE /api/v1/templates/{template_id}`
**Purpose:** Soft-delete a template, making it unavailable for new documents.  
**Auth Required:** Yes  
**Required Role:** admin+  

**Request:** _(no body)_

**Response (200):**
```json
{
  "success": true,
  "data": null,
  "message": "Template deleted successfully"
}
```

**Errors:**  
- `401` – not authenticated  
- `403` – forbidden  
- `404` – `TEMPLATE_NOT_FOUND`  

---

#### `GET /api/v1/templates/{template_id}/versions`
**Purpose:** List all versions of a template, including unpublished drafts.  
**Auth Required:** Yes  
**Required Role:** Any authenticated  

**Request:** _(no body)_

**Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": "tver_01HXZ4N3M5KQRP8VWTJG2D6YB",
      "version_number": "1.2.0",
      "changelog": "Added security considerations section",
      "is_published": true,
      "published_at": "2024-05-10T10:00:00Z",
      "created_by": {
        "id": "usr_01HXZ4N3M5KQRP8VWTJG2D6YB",
        "full_name": "Alice Johnson"
      },
      "created_at": "2024-05-08T09:00:00Z"
    },
    {
      "id": "tver_00GWY3M2L4JPQO7VSJHI1C5XA",
      "version_number": "1.1.0",
      "changelog": "Initial stable version",
      "is_published": true,
      "published_at": "2024-03-01T10:00:00Z",
      "created_by": {
        "id": "usr_01HXZ4N3M5KQRP8VWTJG2D6YB",
        "full_name": "Alice Johnson"
      },
      "created_at": "2024-02-28T09:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 4,
    "pages": 1
  }
}
```

**Errors:**  
- `401` – not authenticated  
- `404` – `TEMPLATE_NOT_FOUND`  

---

#### `POST /api/v1/templates/{template_id}/versions`
**Purpose:** Create a new draft version of a template.  
**Auth Required:** Yes  
**Required Role:** admin+  

**Request:**
```json
{
  "version_number": "1.3.0",
  "changelog": "Added GDPR compliance section and updated introduction"
}
```

**Response (201):**
```json
{
  "success": true,
  "data": {
    "id": "tver_02IYA5O4N6LRSQ9WUKHJ3E7ZC",
    "version_number": "1.3.0",
    "changelog": "Added GDPR compliance section and updated introduction",
    "is_published": false,
    "published_at": null,
    "created_at": "2024-06-01T18:00:00Z"
  },
  "message": "Template version created successfully"
}
```

**Errors:**  
- `400` – validation error  
- `401` – not authenticated  
- `403` – forbidden  
- `404` – `TEMPLATE_NOT_FOUND`  
- `409` – version number already exists for this template  
- `422` – unprocessable entity  

---

#### `GET /api/v1/templates/{template_id}/versions/{version_id}`
**Purpose:** Retrieve full details of a specific template version, including all its sections.  
**Auth Required:** Yes  
**Required Role:** Any authenticated  

**Request:** _(no body)_

**Response (200):**
```json
{
  "success": true,
  "data": {
    "id": "tver_01HXZ4N3M5KQRP8VWTJG2D6YB",
    "template_id": "tmpl_01HXZ4N3M5KQRP8VWTJG2D6YB",
    "version_number": "1.2.0",
    "changelog": "Added security considerations section",
    "is_published": true,
    "published_at": "2024-05-10T10:00:00Z",
    "file_url": "https://storage.docuforge.ai/templates/tmpl_01.../v1.2.0/template.docx",
    "sections": [
      {
        "id": "sect_01HXZ4N3M5KQRP8VWTJG2D6YB",
        "title": "Executive Summary",
        "description": "Brief overview of the technical design",
        "is_mandatory": true,
        "display_order": 1
      }
    ],
    "created_at": "2024-05-08T09:00:00Z"
  }
}
```

**Errors:**  
- `401` – not authenticated  
- `404` – `TEMPLATE_NOT_FOUND` / `TEMPLATE_VERSION_NOT_FOUND`  

---

#### `PUT /api/v1/templates/{template_id}/versions/{version_id}/publish`
**Purpose:** Publish a draft template version, making it the active version for document processing.  
**Auth Required:** Yes  
**Required Role:** admin+  

**Request:** _(no body)_

**Response (200):**
```json
{
  "success": true,
  "data": {
    "id": "tver_02IYA5O4N6LRSQ9WUKHJ3E7ZC",
    "version_number": "1.3.0",
    "is_published": true,
    "published_at": "2024-06-01T19:00:00Z"
  },
  "message": "Template version published successfully"
}
```

**Errors:**  
- `401` – not authenticated  
- `403` – forbidden  
- `404` – `TEMPLATE_NOT_FOUND` / `TEMPLATE_VERSION_NOT_FOUND`  
- `409` – version is already published  

---

#### `POST /api/v1/templates/{template_id}/versions/{version_id}/upload-file`
**Purpose:** Upload a DOCX template file for a specific template version (multipart/form-data).  
**Auth Required:** Yes  
**Required Role:** admin+  

**Request:** `Content-Type: multipart/form-data`

| Field | Type | Description |
|---|---|---|
| `file` | file | DOCX file (max 20 MB) |

**Response (200):**
```json
{
  "success": true,
  "data": {
    "version_id": "tver_02IYA5O4N6LRSQ9WUKHJ3E7ZC",
    "file_url": "https://storage.docuforge.ai/templates/tmpl_02.../v1.3.0/template.docx",
    "file_size_bytes": 204800,
    "uploaded_at": "2024-06-01T19:30:00Z"
  },
  "message": "Template file uploaded successfully"
}
```

**Errors:**  
- `400` – no file provided  
- `401` – not authenticated  
- `403` – forbidden  
- `404` – `TEMPLATE_NOT_FOUND` / `TEMPLATE_VERSION_NOT_FOUND`  
- `413` – `FILE_TOO_LARGE`  
- `422` – `INVALID_FILE_TYPE` (only DOCX accepted)  
- `500` – `FILE_UPLOAD_FAILED`  

---

## 5. Template Sections

**Base path:** `/api/v1/templates/{template_id}/versions/{version_id}/sections`

> Write operations require admin+. Read operations require any authenticated user.

---

#### `GET /api/v1/templates/{template_id}/versions/{version_id}/sections`
**Purpose:** List all sections belonging to a template version, ordered by `display_order`.  
**Auth Required:** Yes  
**Required Role:** Any authenticated  

**Request:** _(no body)_

**Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": "sect_01HXZ4N3M5KQRP8VWTJG2D6YB",
      "title": "Executive Summary",
      "description": "Brief overview of the technical design",
      "guidance": "Provide a 2-3 paragraph summary of the system architecture",
      "is_mandatory": true,
      "display_order": 1,
      "created_at": "2024-05-08T09:00:00Z"
    },
    {
      "id": "sect_02IYA5O4N6LRSQ9WUKHJ3E7ZC",
      "title": "Architecture Overview",
      "description": "High-level system architecture description",
      "guidance": "Include component diagram description and key design decisions",
      "is_mandatory": true,
      "display_order": 2,
      "created_at": "2024-05-08T09:05:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 50,
    "total": 8,
    "pages": 1
  }
}
```

**Errors:**  
- `401` – not authenticated  
- `404` – `TEMPLATE_NOT_FOUND` / `TEMPLATE_VERSION_NOT_FOUND`  

---

#### `POST /api/v1/templates/{template_id}/versions/{version_id}/sections`
**Purpose:** Add a new section to a template version.  
**Auth Required:** Yes  
**Required Role:** admin+  

**Request:**
```json
{
  "title": "Security Considerations",
  "description": "Security architecture and threat model",
  "guidance": "Document authentication, authorisation, encryption standards used",
  "is_mandatory": false,
  "display_order": 7
}
```

**Response (201):**
```json
{
  "success": true,
  "data": {
    "id": "sect_03JZB6P5O7MSTR0XVLIJ4F8AD",
    "title": "Security Considerations",
    "description": "Security architecture and threat model",
    "guidance": "Document authentication, authorisation, encryption standards used",
    "is_mandatory": false,
    "display_order": 7,
    "created_at": "2024-06-01T20:00:00Z"
  },
  "message": "Section created successfully"
}
```

**Errors:**  
- `400` – validation error  
- `401` – not authenticated  
- `403` – forbidden  
- `404` – `TEMPLATE_NOT_FOUND` / `TEMPLATE_VERSION_NOT_FOUND`  
- `422` – unprocessable entity  

---

#### `GET /api/v1/templates/{template_id}/versions/{version_id}/sections/{section_id}`
**Purpose:** Retrieve details for a specific section within a template version.  
**Auth Required:** Yes  
**Required Role:** Any authenticated  

**Request:** _(no body)_

**Response (200):**
```json
{
  "success": true,
  "data": {
    "id": "sect_01HXZ4N3M5KQRP8VWTJG2D6YB",
    "template_version_id": "tver_01HXZ4N3M5KQRP8VWTJG2D6YB",
    "title": "Executive Summary",
    "description": "Brief overview of the technical design",
    "guidance": "Provide a 2-3 paragraph summary of the system architecture",
    "is_mandatory": true,
    "display_order": 1,
    "created_at": "2024-05-08T09:00:00Z",
    "updated_at": "2024-05-08T09:00:00Z"
  }
}
```

**Errors:**  
- `401` – not authenticated  
- `404` – `TEMPLATE_NOT_FOUND` / `TEMPLATE_VERSION_NOT_FOUND` / `SECTION_NOT_FOUND`  

---

#### `PUT /api/v1/templates/{template_id}/versions/{version_id}/sections/{section_id}`
**Purpose:** Update the content or properties of an existing template section.  
**Auth Required:** Yes  
**Required Role:** admin+  

**Request:**
```json
{
  "title": "Executive Summary",
  "description": "High-level overview of the design",
  "guidance": "Provide a concise 2-3 paragraph summary",
  "is_mandatory": true,
  "display_order": 1
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "id": "sect_01HXZ4N3M5KQRP8VWTJG2D6YB",
    "title": "Executive Summary",
    "description": "High-level overview of the design",
    "guidance": "Provide a concise 2-3 paragraph summary",
    "is_mandatory": true,
    "display_order": 1,
    "updated_at": "2024-06-01T20:30:00Z"
  },
  "message": "Section updated successfully"
}
```

**Errors:**  
- `400` – validation error  
- `401` – not authenticated  
- `403` – forbidden  
- `404` – `SECTION_NOT_FOUND`  
- `422` – unprocessable entity  

---

#### `DELETE /api/v1/templates/{template_id}/versions/{version_id}/sections/{section_id}`
**Purpose:** Permanently remove a section from a template version.  
**Auth Required:** Yes  
**Required Role:** admin+  

**Request:** _(no body)_

**Response (200):**
```json
{
  "success": true,
  "data": null,
  "message": "Section deleted successfully"
}
```

**Errors:**  
- `401` – not authenticated  
- `403` – forbidden  
- `404` – `SECTION_NOT_FOUND`  

---

#### `PUT /api/v1/templates/{template_id}/versions/{version_id}/sections/reorder`
**Purpose:** Reorder multiple sections in a template version in a single atomic operation.  
**Auth Required:** Yes  
**Required Role:** admin+  

**Request:**
```json
{
  "sections": [
    { "section_id": "sect_01HXZ4N3M5KQRP8VWTJG2D6YB", "display_order": 1 },
    { "section_id": "sect_02IYA5O4N6LRSQ9WUKHJ3E7ZC", "display_order": 2 },
    { "section_id": "sect_03JZB6P5O7MSTR0XVLIJ4F8AD", "display_order": 3 }
  ]
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "updated_count": 3
  },
  "message": "Sections reordered successfully"
}
```

**Errors:**  
- `400` – validation error (e.g. duplicate display_order values)  
- `401` – not authenticated  
- `403` – forbidden  
- `404` – `SECTION_NOT_FOUND` (one or more section IDs invalid)  
- `422` – unprocessable entity  

---

## 6. Documents (`/api/v1/documents`)

---

#### `GET /api/v1/documents`
**Purpose:** List documents — developers see only their own; managers and admin+ see all documents. Supports pagination and filters.  
**Auth Required:** Yes  
**Required Role:** Any authenticated  

**Query Parameters:**

| Parameter | Type | Description |
|---|---|---|
| `status` | string | Filter by status: `draft`, `processing`, `review`, `completed`, `failed` |
| `template_id` | string | Filter by template ID |
| `date_from` | date | Filter documents created on or after (ISO 8601 date) |
| `date_to` | date | Filter documents created on or before (ISO 8601 date) |
| `owner_id` | string | Filter by owner user ID (admin+ only) |
| `search` | string | Search by title |

**Request:** _(no body)_

**Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": "doc_01HXZ4N3M5KQRP8VWTJG2D6YB",
      "title": "Payment Gateway TDD",
      "status": "draft",
      "source_type": "upload",
      "template": {
        "id": "tmpl_01HXZ4N3M5KQRP8VWTJG2D6YB",
        "name": "Technical Design Document"
      },
      "owner": {
        "id": "usr_01HXZ4N3M5KQRP8VWTJG2D6YB",
        "full_name": "Alice Johnson"
      },
      "created_at": "2024-06-01T10:00:00Z",
      "updated_at": "2024-06-01T10:30:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 42,
    "pages": 3
  }
}
```

**Errors:**  
- `401` – not authenticated  

---

#### `POST /api/v1/documents`
**Purpose:** Create a new document record linked to a template.  
**Auth Required:** Yes  
**Required Role:** Any authenticated  

**Request:**
```json
{
  "title": "Payment Gateway TDD",
  "template_id": "tmpl_01HXZ4N3M5KQRP8VWTJG2D6YB",
  "source_type": "upload"
}
```

> `source_type` values: `upload` (file upload), `paste` (pasted text).

**Response (201):**
```json
{
  "success": true,
  "data": {
    "id": "doc_01HXZ4N3M5KQRP8VWTJG2D6YB",
    "title": "Payment Gateway TDD",
    "status": "draft",
    "source_type": "upload",
    "template": {
      "id": "tmpl_01HXZ4N3M5KQRP8VWTJG2D6YB",
      "name": "Technical Design Document",
      "current_version_id": "tver_01HXZ4N3M5KQRP8VWTJG2D6YB"
    },
    "owner": {
      "id": "usr_01HXZ4N3M5KQRP8VWTJG2D6YB",
      "full_name": "Alice Johnson"
    },
    "created_at": "2024-06-01T10:00:00Z"
  },
  "message": "Document created successfully"
}
```

**Errors:**  
- `400` – validation error  
- `401` – not authenticated  
- `404` – `TEMPLATE_NOT_FOUND`  
- `422` – `TEMPLATE_VERSION_NOT_PUBLISHED` / unprocessable entity  

---

#### `GET /api/v1/documents/{doc_id}`
**Purpose:** Retrieve full details of a specific document including status and metadata.  
**Auth Required:** Yes  
**Required Role:** Any authenticated (owner or admin+)  

**Request:** _(no body)_

**Response (200):**
```json
{
  "success": true,
  "data": {
    "id": "doc_01HXZ4N3M5KQRP8VWTJG2D6YB",
    "title": "Payment Gateway TDD",
    "status": "processing",
    "source_type": "upload",
    "template": {
      "id": "tmpl_01HXZ4N3M5KQRP8VWTJG2D6YB",
      "name": "Technical Design Document",
      "version_id": "tver_01HXZ4N3M5KQRP8VWTJG2D6YB",
      "version_number": "1.2.0"
    },
    "owner": {
      "id": "usr_01HXZ4N3M5KQRP8VWTJG2D6YB",
      "full_name": "Alice Johnson"
    },
    "upload": {
      "upload_id": "upl_01HXZ4N3M5KQRP8VWTJG2D6YB",
      "original_filename": "rough_tdd.docx",
      "file_size_bytes": 102400,
      "uploaded_at": "2024-06-01T10:05:00Z"
    },
    "latest_job_id": "job_01HXZ4N3M5KQRP8VWTJG2D6YB",
    "version_count": 1,
    "created_at": "2024-06-01T10:00:00Z",
    "updated_at": "2024-06-01T10:30:00Z"
  }
}
```

**Errors:**  
- `401` – not authenticated  
- `403` – forbidden (not owner, not admin+)  
- `404` – `DOCUMENT_NOT_FOUND`  

---

#### `PUT /api/v1/documents/{doc_id}`
**Purpose:** Update document metadata such as the title.  
**Auth Required:** Yes  
**Required Role:** Any authenticated (owner or admin+)  

**Request:**
```json
{
  "title": "Payment Gateway TDD v2"
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "id": "doc_01HXZ4N3M5KQRP8VWTJG2D6YB",
    "title": "Payment Gateway TDD v2",
    "updated_at": "2024-06-01T11:00:00Z"
  },
  "message": "Document updated successfully"
}
```

**Errors:**  
- `400` – validation error  
- `401` – not authenticated  
- `403` – forbidden  
- `404` – `DOCUMENT_NOT_FOUND`  
- `422` – unprocessable entity  

---

#### `DELETE /api/v1/documents/{doc_id}`
**Purpose:** Soft-delete a document (owner can delete own documents; admin+ can delete any).  
**Auth Required:** Yes  
**Required Role:** Any authenticated (owner or admin+)  

**Request:** _(no body)_

**Response (200):**
```json
{
  "success": true,
  "data": null,
  "message": "Document deleted successfully"
}
```

**Errors:**  
- `401` – not authenticated  
- `403` – forbidden  
- `404` – `DOCUMENT_NOT_FOUND`  

---

## 7. File Upload

---

#### `POST /api/v1/documents/{doc_id}/upload`
**Purpose:** Upload a source file (DOCX, PDF, MD, or TXT) for AI processing; returns an upload record and a preview of extracted text.  
**Auth Required:** Yes  
**Required Role:** Any authenticated (owner or admin+)  

**Request:** `Content-Type: multipart/form-data`

| Field | Type | Description |
|---|---|---|
| `file` | file | Source file: DOCX, PDF, MD, or TXT. Max 20 MB. |

> Server validates MIME type server-side: `application/vnd.openxmlformats-officedocument.wordprocessingml.document`, `application/pdf`, `text/markdown`, `text/plain`.

**Response (200):**
```json
{
  "success": true,
  "data": {
    "upload_id": "upl_01HXZ4N3M5KQRP8VWTJG2D6YB",
    "document_id": "doc_01HXZ4N3M5KQRP8VWTJG2D6YB",
    "original_filename": "rough_tdd.docx",
    "file_size_bytes": 102400,
    "mime_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "extracted_text_preview": "This document describes the payment gateway integration architecture...",
    "extracted_text_char_count": 15420,
    "uploaded_at": "2024-06-01T10:05:00Z"
  },
  "message": "File uploaded and text extracted successfully"
}
```

**Errors:**  
- `400` – no file provided  
- `401` – not authenticated  
- `403` – forbidden  
- `404` – `DOCUMENT_NOT_FOUND`  
- `413` – `FILE_TOO_LARGE` — file exceeds 20 MB  
- `422` – `INVALID_FILE_TYPE` — unsupported MIME type  
- `500` – `FILE_UPLOAD_FAILED`  

---

#### `POST /api/v1/documents/{doc_id}/paste`
**Purpose:** Submit raw plain-text content for a document instead of uploading a file.  
**Auth Required:** Yes  
**Required Role:** Any authenticated (owner or admin+)  

**Request:**
```json
{
  "content": "This is the raw text content of my document...\n\nSection 1: Overview\nThis system processes payments via...",
  "content_format": "plain_text"
}
```

> `content_format` values: `plain_text`, `markdown`.

**Response (200):**
```json
{
  "success": true,
  "data": {
    "upload_id": "upl_02IYA5O4N6LRSQ9WUKHJ3E7ZC",
    "document_id": "doc_01HXZ4N3M5KQRP8VWTJG2D6YB",
    "char_count": 3240,
    "content_format": "plain_text",
    "created_at": "2024-06-01T10:10:00Z"
  },
  "message": "Content submitted successfully"
}
```

**Errors:**  
- `400` – missing or empty `content` field  
- `401` – not authenticated  
- `403` – forbidden  
- `404` – `DOCUMENT_NOT_FOUND`  
- `413` – content exceeds maximum allowed size  
- `422` – unprocessable entity  

---

## 8. AI Processing

---

#### `POST /api/v1/documents/{doc_id}/process`
**Purpose:** Trigger an AI processing job to extract structured content from the uploaded source against a specified template version.  
**Auth Required:** Yes  
**Required Role:** Any authenticated (owner or admin+)  

**Request:**
```json
{
  "template_version_id": "tver_01HXZ4N3M5KQRP8VWTJG2D6YB"
}
```

> MVP: processing runs synchronously; response may include results inline. Future: async job is queued, poll status endpoint.

**Response (202):**
```json
{
  "success": true,
  "data": {
    "job_id": "job_01HXZ4N3M5KQRP8VWTJG2D6YB",
    "document_id": "doc_01HXZ4N3M5KQRP8VWTJG2D6YB",
    "template_version_id": "tver_01HXZ4N3M5KQRP8VWTJG2D6YB",
    "status": "queued",
    "created_at": "2024-06-01T10:15:00Z"
  },
  "message": "AI processing job started"
}
```

**Errors:**  
- `400` – no source content uploaded for this document  
- `401` – not authenticated  
- `403` – forbidden  
- `404` – `DOCUMENT_NOT_FOUND` / `TEMPLATE_VERSION_NOT_FOUND`  
- `422` – `TEMPLATE_VERSION_NOT_PUBLISHED`  
- `409` – a processing job is already in progress for this document  

---

#### `GET /api/v1/documents/{doc_id}/process/{job_id}/status`
**Purpose:** Poll the status of an AI processing job and retrieve the result summary when complete.  
**Auth Required:** Yes  
**Required Role:** Any authenticated (owner or admin+)  

**Request:** _(no body)_

**Response (200):**
```json
{
  "success": true,
  "data": {
    "job_id": "job_01HXZ4N3M5KQRP8VWTJG2D6YB",
    "document_id": "doc_01HXZ4N3M5KQRP8VWTJG2D6YB",
    "status": "completed",
    "progress_percent": 100,
    "started_at": "2024-06-01T10:15:05Z",
    "completed_at": "2024-06-01T10:15:42Z",
    "duration_seconds": 37,
    "sections_extracted": 6,
    "sections_missing": 2,
    "ai_tokens_used": 4821,
    "error_message": null
  }
}
```

> `status` values: `queued`, `processing`, `completed`, `failed`.

**Errors:**  
- `401` – not authenticated  
- `403` – forbidden  
- `404` – `DOCUMENT_NOT_FOUND` / `AI_JOB_NOT_FOUND`  

---

#### `GET /api/v1/documents/{doc_id}/process/{job_id}/extraction`
**Purpose:** Retrieve the full validated AI extraction result as structured JSON once the job is complete.  
**Auth Required:** Yes  
**Required Role:** Any authenticated (owner or admin+)  

**Request:** _(no body)_

**Response (200):**
```json
{
  "success": true,
  "data": {
    "job_id": "job_01HXZ4N3M5KQRP8VWTJG2D6YB",
    "document_id": "doc_01HXZ4N3M5KQRP8VWTJG2D6YB",
    "template_version_id": "tver_01HXZ4N3M5KQRP8VWTJG2D6YB",
    "extraction": {
      "sections": [
        {
          "section_id": "sect_01HXZ4N3M5KQRP8VWTJG2D6YB",
          "title": "Executive Summary",
          "extracted_content": "This document describes the architecture for a PCI-DSS compliant payment gateway...",
          "confidence_score": 0.94,
          "status": "extracted"
        },
        {
          "section_id": "sect_03JZB6P5O7MSTR0XVLIJ4F8AD",
          "title": "Security Considerations",
          "extracted_content": null,
          "confidence_score": null,
          "status": "missing"
        }
      ]
    },
    "completed_at": "2024-06-01T10:15:42Z"
  }
}
```

**Errors:**  
- `400` – job not yet completed  
- `401` – not authenticated  
- `403` – forbidden  
- `404` – `DOCUMENT_NOT_FOUND` / `AI_JOB_NOT_FOUND`  
- `422` – `AI_PROCESSING_FAILED` — job ended in failed state  

---

## 9. Section Mapping & Missing Sections

**Base path:** `/api/v1/documents/{doc_id}/sections`

---

#### `GET /api/v1/documents/{doc_id}/sections`
**Purpose:** Retrieve all document sections for the current template version, including AI-extracted content and status for each.  
**Auth Required:** Yes  
**Required Role:** Any authenticated (owner or admin+)  

**Request:** _(no body)_

**Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "section_id": "sect_01HXZ4N3M5KQRP8VWTJG2D6YB",
      "title": "Executive Summary",
      "is_mandatory": true,
      "display_order": 1,
      "status": "extracted",
      "content": "This document describes the architecture for a PCI-DSS compliant payment gateway...",
      "user_edited": false,
      "confidence_score": 0.94,
      "skipped_reason": null
    },
    {
      "section_id": "sect_03JZB6P5O7MSTR0XVLIJ4F8AD",
      "title": "Security Considerations",
      "is_mandatory": false,
      "display_order": 7,
      "status": "missing",
      "content": null,
      "user_edited": false,
      "confidence_score": null,
      "skipped_reason": null
    }
  ]
}
```

> `status` values: `extracted`, `missing`, `skipped`, `user_provided`.

**Errors:**  
- `401` – not authenticated  
- `403` – forbidden  
- `404` – `DOCUMENT_NOT_FOUND`  

---

#### `GET /api/v1/documents/{doc_id}/sections/missing`
**Purpose:** Retrieve only the mandatory sections that have not yet been filled in or skipped.  
**Auth Required:** Yes  
**Required Role:** Any authenticated (owner or admin+)  

**Request:** _(no body)_

**Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "section_id": "sect_02IYA5O4N6LRSQ9WUKHJ3E7ZC",
      "title": "Architecture Overview",
      "is_mandatory": true,
      "display_order": 2,
      "guidance": "Include component diagram description and key design decisions",
      "status": "missing"
    }
  ]
}
```

**Errors:**  
- `401` – not authenticated  
- `403` – forbidden  
- `404` – `DOCUMENT_NOT_FOUND`  

---

#### `PUT /api/v1/documents/{doc_id}/sections/{section_id}`
**Purpose:** Update the content of a specific section — either providing missing content or editing AI-extracted content.  
**Auth Required:** Yes  
**Required Role:** Any authenticated (owner or admin+)  

**Request:**
```json
{
  "content": "The system uses a microservices architecture with an API gateway fronting three core services: Auth, Payment, and Notification. Each service communicates via gRPC internally..."
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "section_id": "sect_02IYA5O4N6LRSQ9WUKHJ3E7ZC",
    "title": "Architecture Overview",
    "status": "user_provided",
    "content": "The system uses a microservices architecture with an API gateway fronting three core services: Auth, Payment, and Notification. Each service communicates via gRPC internally...",
    "user_edited": true,
    "updated_at": "2024-06-01T11:30:00Z"
  },
  "message": "Section updated successfully"
}
```

**Errors:**  
- `400` – empty content  
- `401` – not authenticated  
- `403` – forbidden  
- `404` – `DOCUMENT_NOT_FOUND` / `SECTION_NOT_FOUND`  
- `422` – unprocessable entity  

---

#### `PUT /api/v1/documents/{doc_id}/sections/{section_id}/skip`
**Purpose:** Mark an optional section as intentionally skipped, with a reason.  
**Auth Required:** Yes  
**Required Role:** Any authenticated (owner or admin+)  

**Request:**
```json
{
  "reason": "Not applicable for this internal tooling project"
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "section_id": "sect_03JZB6P5O7MSTR0XVLIJ4F8AD",
    "title": "Security Considerations",
    "status": "skipped",
    "skipped_reason": "Not applicable for this internal tooling project",
    "updated_at": "2024-06-01T11:35:00Z"
  },
  "message": "Section skipped"
}
```

**Errors:**  
- `400` – missing `reason`  
- `401` – not authenticated  
- `403` – forbidden  
- `404` – `DOCUMENT_NOT_FOUND` / `SECTION_NOT_FOUND`  
- `422` – `SECTION_MANDATORY_SKIPPED` — cannot skip a mandatory section  

---

#### `POST /api/v1/documents/{doc_id}/sections/validate`
**Purpose:** Validate that all mandatory sections are complete; returns a list of remaining issues before generation can proceed.  
**Auth Required:** Yes  
**Required Role:** Any authenticated (owner or admin+)  

**Request:** _(no body)_

**Response (200):**
```json
{
  "success": true,
  "data": {
    "is_valid": false,
    "issues": [
      {
        "section_id": "sect_02IYA5O4N6LRSQ9WUKHJ3E7ZC",
        "title": "Architecture Overview",
        "issue": "Mandatory section has no content"
      }
    ],
    "total_sections": 8,
    "complete_sections": 7,
    "missing_mandatory_count": 1
  },
  "message": "Validation failed: 1 mandatory section incomplete"
}
```

> When `is_valid` is `true`, the document is ready for generation. `issues` will be an empty array.

**Errors:**  
- `401` – not authenticated  
- `403` – forbidden  
- `404` – `DOCUMENT_NOT_FOUND`  

---

## 10. Document Generation

---

#### `POST /api/v1/documents/{doc_id}/generate`
**Purpose:** Trigger standardised document generation from the completed sections, creating a new document version.  
**Auth Required:** Yes  
**Required Role:** Any authenticated (owner or admin+)  

**Request:** _(no body)_

**Response (202):**
```json
{
  "success": true,
  "data": {
    "version_id": "dver_01HXZ4N3M5KQRP8VWTJG2D6YB",
    "document_id": "doc_01HXZ4N3M5KQRP8VWTJG2D6YB",
    "status": "generating",
    "version_number": 2,
    "started_at": "2024-06-01T12:00:00Z"
  },
  "message": "Document generation started"
}
```

**Errors:**  
- `401` – not authenticated  
- `403` – forbidden  
- `404` – `DOCUMENT_NOT_FOUND`  
- `409` – `DOCUMENT_ALREADY_GENERATED` — this exact section set already has a generated version  
- `422` – mandatory sections are still incomplete (run validation first)  
- `500` – `GENERATION_FAILED`  

---

#### `GET /api/v1/documents/{doc_id}/generate/{version_id}/status`
**Purpose:** Poll the status of a document generation job.  
**Auth Required:** Yes  
**Required Role:** Any authenticated (owner or admin+)  

**Request:** _(no body)_

**Response (200):**
```json
{
  "success": true,
  "data": {
    "version_id": "dver_01HXZ4N3M5KQRP8VWTJG2D6YB",
    "document_id": "doc_01HXZ4N3M5KQRP8VWTJG2D6YB",
    "status": "completed",
    "version_number": 2,
    "started_at": "2024-06-01T12:00:00Z",
    "completed_at": "2024-06-01T12:00:18Z",
    "exports_available": ["docx", "pdf", "markdown"],
    "error_message": null
  }
}
```

> `status` values: `generating`, `completed`, `failed`.

**Errors:**  
- `401` – not authenticated  
- `403` – forbidden  
- `404` – `DOCUMENT_NOT_FOUND` / `DOCUMENT_VERSION_NOT_FOUND`  

---

## 11. Document Export

**Base path:** `/api/v1/documents/{doc_id}/versions/{version_id}/export`

---

#### `GET /api/v1/documents/{doc_id}/versions/{version_id}/export/docx`
**Purpose:** Stream the generated DOCX file for download.  
**Auth Required:** Yes  
**Required Role:** Any authenticated (owner or admin+)  

**Request:** _(no body)_

**Response (200):**
```
Content-Type: application/vnd.openxmlformats-officedocument.wordprocessingml.document
Content-Disposition: attachment; filename="payment-gateway-tdd-v2.docx"
[Binary DOCX file stream]
```

**Errors:**  
- `401` – not authenticated  
- `403` – forbidden  
- `404` – `DOCUMENT_NOT_FOUND` / `DOCUMENT_VERSION_NOT_FOUND`  
- `422` – document generation not yet completed  

---

#### `GET /api/v1/documents/{doc_id}/versions/{version_id}/export/pdf`
**Purpose:** Stream a PDF export of the generated document (triggers LibreOffice DOCX→PDF conversion if not cached, then streams).  
**Auth Required:** Yes  
**Required Role:** Any authenticated (owner or admin+)  

**Request:** _(no body)_

**Response (200):**
```
Content-Type: application/pdf
Content-Disposition: attachment; filename="payment-gateway-tdd-v2.pdf"
[Binary PDF file stream]
```

> PDF conversion is performed by LibreOffice on the server. The result is cached so subsequent requests are served immediately.

**Errors:**  
- `401` – not authenticated  
- `403` – forbidden  
- `404` – `DOCUMENT_NOT_FOUND` / `DOCUMENT_VERSION_NOT_FOUND`  
- `422` – document generation not yet completed  
- `500` – `GENERATION_FAILED` — LibreOffice conversion error  

---

#### `GET /api/v1/documents/{doc_id}/versions/{version_id}/export/markdown`
**Purpose:** Stream a Markdown-formatted export of the generated document.  
**Auth Required:** Yes  
**Required Role:** Any authenticated (owner or admin+)  

**Request:** _(no body)_

**Response (200):**
```
Content-Type: text/markdown; charset=utf-8
Content-Disposition: attachment; filename="payment-gateway-tdd-v2.md"
[Markdown text stream]
```

**Errors:**  
- `401` – not authenticated  
- `403` – forbidden  
- `404` – `DOCUMENT_NOT_FOUND` / `DOCUMENT_VERSION_NOT_FOUND`  
- `422` – document generation not yet completed  

---

## 12. Document Versions

**Base path:** `/api/v1/documents/{doc_id}/versions`

---

#### `GET /api/v1/documents/{doc_id}/versions`
**Purpose:** List all generated versions of a document, including generation status and the template version used.  
**Auth Required:** Yes  
**Required Role:** Any authenticated (owner or admin+)  

**Request:** _(no body)_

**Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": "dver_01HXZ4N3M5KQRP8VWTJG2D6YB",
      "version_number": 1,
      "status": "completed",
      "is_current": false,
      "template_version": {
        "id": "tver_00GWY3M2L4JPQO7VSJHI1C5XA",
        "version_number": "1.1.0"
      },
      "created_at": "2024-05-20T09:00:00Z",
      "completed_at": "2024-05-20T09:00:15Z"
    },
    {
      "id": "dver_02IYA5O4N6LRSQ9WUKHJ3E7ZC",
      "version_number": 2,
      "status": "completed",
      "is_current": true,
      "template_version": {
        "id": "tver_01HXZ4N3M5KQRP8VWTJG2D6YB",
        "version_number": "1.2.0"
      },
      "created_at": "2024-06-01T12:00:00Z",
      "completed_at": "2024-06-01T12:00:18Z"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 2,
    "pages": 1
  }
}
```

**Errors:**  
- `401` – not authenticated  
- `403` – forbidden  
- `404` – `DOCUMENT_NOT_FOUND`  

---

#### `GET /api/v1/documents/{doc_id}/versions/{version_id}`
**Purpose:** Retrieve full details of a specific document version.  
**Auth Required:** Yes  
**Required Role:** Any authenticated (owner or admin+)  

**Request:** _(no body)_

**Response (200):**
```json
{
  "success": true,
  "data": {
    "id": "dver_02IYA5O4N6LRSQ9WUKHJ3E7ZC",
    "document_id": "doc_01HXZ4N3M5KQRP8VWTJG2D6YB",
    "version_number": 2,
    "status": "completed",
    "is_current": true,
    "template_version": {
      "id": "tver_01HXZ4N3M5KQRP8VWTJG2D6YB",
      "version_number": "1.2.0"
    },
    "section_snapshot": [
      {
        "section_id": "sect_01HXZ4N3M5KQRP8VWTJG2D6YB",
        "title": "Executive Summary",
        "content": "This document describes...",
        "status": "extracted"
      }
    ],
    "exports": {
      "docx_url": "/api/v1/documents/doc_01.../versions/dver_02.../export/docx",
      "pdf_url": "/api/v1/documents/doc_01.../versions/dver_02.../export/pdf",
      "markdown_url": "/api/v1/documents/doc_01.../versions/dver_02.../export/markdown"
    },
    "created_at": "2024-06-01T12:00:00Z",
    "completed_at": "2024-06-01T12:00:18Z"
  }
}
```

**Errors:**  
- `401` – not authenticated  
- `403` – forbidden  
- `404` – `DOCUMENT_NOT_FOUND` / `DOCUMENT_VERSION_NOT_FOUND`  

---

#### `PUT /api/v1/documents/{doc_id}/versions/{version_id}/restore`
**Purpose:** Restore a previous document version as the current working state by creating a new version (N+1) as a copy.  
**Auth Required:** Yes  
**Required Role:** Any authenticated (owner or admin+)  

**Request:** _(no body; optionally provide a note)_
```json
{
  "restore_note": "Reverting to v1 as v2 had incorrect architecture description"
}
```

**Response (201):**
```json
{
  "success": true,
  "data": {
    "new_version_id": "dver_03JZB6P5O7MSTR0XVLIJ4F8AD",
    "new_version_number": 3,
    "restored_from_version_id": "dver_01HXZ4N3M5KQRP8VWTJG2D6YB",
    "restored_from_version_number": 1,
    "status": "completed",
    "is_current": true,
    "created_at": "2024-06-01T13:00:00Z"
  },
  "message": "Version restored successfully as version 3"
}
```

**Errors:**  
- `401` – not authenticated  
- `403` – forbidden  
- `404` – `DOCUMENT_NOT_FOUND` / `DOCUMENT_VERSION_NOT_FOUND`  
- `422` – cannot restore a version that is already current  

---

## 13. Document Reviews

---

#### `GET /api/v1/documents/{doc_id}/reviews`
**Purpose:** List all review records for a specific document.  
**Auth Required:** Yes  
**Required Role:** Any authenticated (owner or manager+)  

**Request:** _(no body)_

**Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": "rev_01HXZ4N3M5KQRP8VWTJG2D6YB",
      "document_id": "doc_01HXZ4N3M5KQRP8VWTJG2D6YB",
      "document_version_id": "dver_02IYA5O4N6LRSQ9WUKHJ3E7ZC",
      "status": "pending",
      "submitted_by": {
        "id": "usr_01HXZ4N3M5KQRP8VWTJG2D6YB",
        "full_name": "Alice Johnson"
      },
      "reviewer": {
        "id": "usr_02IYA5O4N6LRSQ9WUKHJ3E7ZC",
        "full_name": "Bob Smith"
      },
      "decision": null,
      "comments": null,
      "submitted_at": "2024-06-01T14:00:00Z",
      "reviewed_at": null
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 1,
    "pages": 1
  }
}
```

**Errors:**  
- `401` – not authenticated  
- `403` – forbidden  
- `404` – `DOCUMENT_NOT_FOUND`  

---

#### `POST /api/v1/documents/{doc_id}/reviews`
**Purpose:** Submit a completed document version for review and assign a reviewer.  
**Auth Required:** Yes  
**Required Role:** Any authenticated (owner or admin+)  

**Request:**
```json
{
  "document_version_id": "dver_02IYA5O4N6LRSQ9WUKHJ3E7ZC",
  "reviewer_id": "usr_02IYA5O4N6LRSQ9WUKHJ3E7ZC",
  "notes": "Please review section 3 especially — incorporated the feedback from last sprint"
}
```

**Response (201):**
```json
{
  "success": true,
  "data": {
    "id": "rev_01HXZ4N3M5KQRP8VWTJG2D6YB",
    "document_id": "doc_01HXZ4N3M5KQRP8VWTJG2D6YB",
    "document_version_id": "dver_02IYA5O4N6LRSQ9WUKHJ3E7ZC",
    "status": "pending",
    "reviewer": {
      "id": "usr_02IYA5O4N6LRSQ9WUKHJ3E7ZC",
      "full_name": "Bob Smith"
    },
    "submitted_at": "2024-06-01T14:00:00Z"
  },
  "message": "Document submitted for review"
}
```

**Errors:**  
- `400` – validation error  
- `401` – not authenticated  
- `403` – forbidden  
- `404` – `DOCUMENT_NOT_FOUND` / `DOCUMENT_VERSION_NOT_FOUND` / `USER_NOT_FOUND` (reviewer)  
- `422` – document version not yet generated / reviewer must have manager+ role  
- `409` – a pending review already exists for this document version  

---

#### `PUT /api/v1/documents/{doc_id}/reviews/{review_id}`
**Purpose:** Submit a review decision (approve, reject, or request changes) with optional comments.  
**Auth Required:** Yes  
**Required Role:** manager+  

**Request:**
```json
{
  "decision": "request_changes",
  "comments": "The architecture diagram description is insufficient. Please expand section 2 with component interaction details and latency expectations."
}
```

> `decision` values: `approve`, `reject`, `request_changes`.

**Response (200):**
```json
{
  "success": true,
  "data": {
    "id": "rev_01HXZ4N3M5KQRP8VWTJG2D6YB",
    "document_id": "doc_01HXZ4N3M5KQRP8VWTJG2D6YB",
    "status": "changes_requested",
    "decision": "request_changes",
    "comments": "The architecture diagram description is insufficient...",
    "reviewed_by": {
      "id": "usr_02IYA5O4N6LRSQ9WUKHJ3E7ZC",
      "full_name": "Bob Smith"
    },
    "reviewed_at": "2024-06-01T16:00:00Z"
  },
  "message": "Review submitted"
}
```

**Errors:**  
- `400` – missing `decision`  
- `401` – not authenticated  
- `403` – forbidden (not the assigned reviewer, or insufficient role)  
- `404` – `DOCUMENT_NOT_FOUND` / `REVIEW_NOT_FOUND`  
- `422` – `INVALID_REVIEW_DECISION` / review already completed  

---

#### `GET /api/v1/reviews/pending`
**Purpose:** Retrieve all documents currently pending review that are assigned to the authenticated user.  
**Auth Required:** Yes  
**Required Role:** manager+  

**Query Parameters:**

| Parameter | Type | Description |
|---|---|---|
| `department_id` | string | Filter by document owner's department |
| `date_from` | date | Filter reviews submitted on or after |
| `date_to` | date | Filter reviews submitted on or before |

**Request:** _(no body)_

**Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": "rev_01HXZ4N3M5KQRP8VWTJG2D6YB",
      "document": {
        "id": "doc_01HXZ4N3M5KQRP8VWTJG2D6YB",
        "title": "Payment Gateway TDD",
        "owner": {
          "id": "usr_01HXZ4N3M5KQRP8VWTJG2D6YB",
          "full_name": "Alice Johnson"
        }
      },
      "document_version_id": "dver_02IYA5O4N6LRSQ9WUKHJ3E7ZC",
      "version_number": 2,
      "submitted_at": "2024-06-01T14:00:00Z",
      "notes": "Please review section 3 especially..."
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 3,
    "pages": 1
  }
}
```

**Errors:**  
- `401` – not authenticated  
- `403` – forbidden (developer role cannot access)  

---

## 14. Admin (`/api/v1/admin`)

> All endpoints in this group require `admin+` role.

---

#### `GET /api/v1/admin/stats`
**Purpose:** Retrieve high-level system statistics for the admin dashboard.  
**Auth Required:** Yes  
**Required Role:** admin+  

**Request:** _(no body)_

**Response (200):**
```json
{
  "success": true,
  "data": {
    "users": {
      "total": 142,
      "active": 138,
      "by_role": {
        "developer": 110,
        "manager": 20,
        "admin": 10,
        "super_admin": 2
      }
    },
    "documents": {
      "total": 1024,
      "by_status": {
        "draft": 45,
        "processing": 3,
        "review": 12,
        "completed": 950,
        "failed": 14
      },
      "created_today": 8
    },
    "templates": {
      "total": 15,
      "active": 12
    },
    "ai_usage": {
      "tokens_used_today": 142830,
      "jobs_run_today": 24,
      "average_job_duration_seconds": 32
    }
  }
}
```

**Errors:**  
- `401` – not authenticated  
- `403` – forbidden  

---

#### `GET /api/v1/admin/ai-usage`
**Purpose:** Retrieve paginated AI usage records for cost tracking and auditing.  
**Auth Required:** Yes  
**Required Role:** admin+  

**Query Parameters:**

| Parameter | Type | Description |
|---|---|---|
| `date_from` | date | Filter records from this date (ISO 8601) |
| `date_to` | date | Filter records up to this date (ISO 8601) |
| `user_id` | string | Filter by user who triggered the job |
| `model` | string | Filter by AI model used |

**Request:** _(no body)_

**Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": "usage_01HXZ4N3M5KQRP8VWTJG2D6YB",
      "job_id": "job_01HXZ4N3M5KQRP8VWTJG2D6YB",
      "document_id": "doc_01HXZ4N3M5KQRP8VWTJG2D6YB",
      "user": {
        "id": "usr_01HXZ4N3M5KQRP8VWTJG2D6YB",
        "full_name": "Alice Johnson"
      },
      "ai_model": "gemini-1.5-pro",
      "prompt_tokens": 2341,
      "completion_tokens": 2480,
      "total_tokens": 4821,
      "duration_seconds": 37,
      "created_at": "2024-06-01T10:15:42Z"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 240,
    "pages": 12
  }
}
```

**Errors:**  
- `401` – not authenticated  
- `403` – forbidden  

---

#### `GET /api/v1/admin/audit-log`
**Purpose:** Retrieve a paginated audit trail of system events for compliance and debugging.  
**Auth Required:** Yes  
**Required Role:** admin+  

**Query Parameters:**

| Parameter | Type | Description |
|---|---|---|
| `user_id` | string | Filter by acting user |
| `event_type` | string | Filter by event type (e.g. `user.login`, `document.deleted`, `template.published`) |
| `date_from` | date | Filter events from this date |
| `date_to` | date | Filter events up to this date |
| `resource_type` | string | Filter by resource type: `user`, `document`, `template`, `review` |
| `resource_id` | string | Filter by specific resource ID |

**Request:** _(no body)_

**Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": "audit_01HXZ4N3M5KQRP8VWTJG2D6YB",
      "event_type": "document.deleted",
      "actor": {
        "id": "usr_02IYA5O4N6LRSQ9WUKHJ3E7ZC",
        "full_name": "Bob Smith",
        "role": "admin"
      },
      "resource_type": "document",
      "resource_id": "doc_03JZB6P5O7MSTR0XVLIJ4F8AD",
      "metadata": {
        "document_title": "Old Project Plan",
        "reason": "Outdated document"
      },
      "ip_address": "192.168.1.42",
      "user_agent": "Mozilla/5.0...",
      "created_at": "2024-06-01T09:45:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 5230,
    "pages": 262
  }
}
```

**Errors:**  
- `401` – not authenticated  
- `403` – forbidden  

---

#### `GET /api/v1/admin/health`
**Purpose:** Check the health and connectivity status of all system components.  
**Auth Required:** Yes  
**Required Role:** admin+  

**Request:** _(no body)_

**Response (200):**
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "timestamp": "2024-06-01T14:00:00Z",
    "version": "1.0.0",
    "components": {
      "database": {
        "status": "healthy",
        "response_time_ms": 4,
        "details": "PostgreSQL 15.2 — connection pool: 8/20 active"
      },
      "storage": {
        "status": "healthy",
        "response_time_ms": 12,
        "details": "S3-compatible storage — available"
      },
      "ai_provider": {
        "status": "healthy",
        "response_time_ms": 180,
        "details": "Gemini API — reachable, quota remaining: 85%"
      },
      "libreoffice": {
        "status": "healthy",
        "details": "LibreOffice 7.6 — available for PDF conversion"
      }
    }
  }
}
```

> When any component is degraded or unreachable, its `status` will be `degraded` or `unhealthy` and the top-level `status` will reflect the worst state. HTTP 200 is still returned so monitoring systems can parse the body; a separate `GET /api/v1/health` (unauthenticated, lightweight) is recommended for uptime monitors.

**Errors:**  
- `401` – not authenticated  
- `403` – forbidden  

---

*End of DocuForge AI API Specification v1.0.0*
