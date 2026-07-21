# Role-Based Access Control (RBAC)

## The Problem

All authenticated users are not equal. In a medical education platform:

| Role | Can view courses | Can create courses | Can manage users | Can see analytics |
|---|---|---|---|---|
| Student | ✅ | ❌ | ❌ | ❌ |
| Instructor | ✅ | ✅ | ❌ | ❌ |
| Admin | ✅ | ✅ | ✅ | ✅ |

We need to protect each endpoint based on who is calling it.

## The RBAC Pattern

```
Request + Token
    │
    ▼
Authenticate → "This is arun"
    │
    ▼
Authorize → "Is arun allowed to do this?"
    │
    ▼
Process or Reject
```

Authentication and authorization are two **separate** checks, done in sequence.

## Implementing Roles

### Step 1: Add role to the user model

The user table gets a `role` field:
```
users:
├── id
├── username
├── hashed_password
├── role: str    ← "student" | "instructor" | "admin"
└── ...
```

### Step 2: Create a role-checker dependency

```
require_role("instructor")
    └── Gets current user (from auth dependency)
    └── Checks user.role
    └── If wrong → 403 Forbidden
    └── If correct → pass through
```

### Step 3: Apply to routes

```
POST /courses
    └── Depends(require_role("instructor"))

DELETE /users/{id}
    └── Depends(require_role("admin"))

GET /courses
    └── Depends(require_role("student"))
    └── (Students can only see their own courses)
```

## The Dependency Chain (Complete)

```
Route
    └── Depends(require_role("instructor"))
            └── Depends(get_current_active_user)
                    └── Depends(get_current_user)
                            └── Depends(oauth2_scheme)
```

Each dependency adds a check. If any fails, the request is rejected before the route runs.

## Role Hierarchy

A simple improvement: roles can inherit permissions.

```
admin    → can do everything
instructor → can do everything a student can + create content
student  → can only view and submit
```

Implement this as:

```
ROLE_HIERARCHY = {
    "admin": 3,
    "instructor": 2,
    "student": 1
}

def require_minimum_role(min_role):
    def checker(user = Depends(get_current_user)):
        if ROLE_HIERARCHY[user.role] < ROLE_HIERARCHY[min_role]:
            raise HTTPException(403)
        return user
    return checker
```

## Permission vs Role

As systems grow, roles become too coarse. You may need **permissions**:

```
User has role: "instructor"

Permissions:
├── course:create  ✅
├── course:edit    ✅
├── course:delete  ❌  (only admins)
├── user:view      ✅
└── user:delete    ❌
```

FastAPI supports this via **OAuth2 scopes** — the token includes a list of granted scopes, and the endpoint checks them.

## Key Systems Insight

The auth system pattern is **always a pipeline**:

```
Token → Decode → Identify → Fetch User → Check Role → Allow/Deny
```

Each step can fail independently. Each failure returns a different status:
- Missing/invalid token → 401 Unauthorized
- Valid token but wrong role → 403 Forbidden
- Valid token, valid role → 200 Success

This separation lets you debug auth issues quickly: "Which step failed?"
