# AI Handoff: Change `Admin.id` from `int` to `UUID` + add Fleet UI

Use this prompt verbatim (or paste the contents of this file to another AI agent).

---

## Task

Change the `admins` table primary key from `Integer` to `UUID`, and add a Fleet management UI to the CLAP-OPS frontend.

## Scope

Two workstreams:

1. **Backend**: change `Admin.id` from `int` to `UUID` (including migrations + the JWT `sub` claim).
2. **Frontend**: add a fleet management UI (list, create, membership management) to `CLAP-OPS-UI`.

## Projects

- Backend: `/home/lucknt/NCI/FYP/CLAP-OPS-Service` (FastAPI + SQLAlchemy + Postgres)
- Frontend: `/home/lucknt/NCI/FYP/CLAP-OPS-UI` (Vite + React + TS)

## Current state

### Backend schema

| Table | `id` / PK type | Notes |
|---|---|---|
| `admins` | `Integer` | **only table with int PK** |
| `fleets` | `UUID` | `server_default=func.gen_random_uuid()` |
| `operators` | `UUID` | FK → `fleets.id` |
| `vehicles` | `UUID` | FK → `fleets.id` |
| `fleet_memberships` | composite PK `(admin_id, fleet_id)` | `admin_id` is `Integer` FK → `admins.id` |

Migration chain: `c7c432f1cc30_initial_admin` → `aee42470c99f_add_vehicles_table` → `7c542b0abc0b_add_operators_table` → `46174fc83a2e_add_fleets_and_fleet_access`

### Backend routes (all require `Authorization: Bearer <token>` from `POST /api/v1/auth/login`)

| Method | Path | Auth requirement |
|---|---|---|
| `POST` | `/api/v1/fleets` | superadmin only |
| `GET` | `/api/v1/fleets` | superadmin only |
| `PUT` | `/api/v1/fleets/{fleet_id}/memberships/{admin_id}` | superadmin only |
| `POST` | `/api/v1/auth/login` | none |
| `GET` | `/api/v1/auth/me` | any admin |
| `POST` | `/api/v1/auth/logout` | any admin |

Fleet-scoped routes need the `X-Fleet-ID` header (UUID) plus `require_fleet_role("MANAGER")` or `require_fleet_role("MEMBER")`.

### Request/response schemas

- **`FleetCreate`**: `name` (required, 1–100), `description` (optional, max 255)
- **`FleetMembershipCreate`**: `role` (required, must be exactly `MANAGER` or `MEMBER`)
- **`FleetResponse`**: `id` (UUID), `name`, `description` (optional), `created_at`
- **`FleetList`**: `{ fleets: [FleetResponse, ...] }`
- **`FleetMembershipResponse`**: `id` (UUID), `name`, `role`

### Key backend code details

- `get_current_admin` in `api/v1/dependencies.py` does `int(payload["sub"])` — must become `UUID(payload["sub"])`
- `create_access_token` in `services/auth/jwt.py` does `create_access_token(user.id)` — must become `create_access_token(str(user.id))`
- `FleetService.set_membership` signature is `set_membership(fleet_id: UUID, admin_id: int, role: str)` — must become `admin_id: UUID`
- `AuthService` takes `user_model: Any` and does `create_access_token(user.id)` — must become `create_access_token(str(user.id))`
- `FleetMembership` model: `admin_id: Mapped[int] = mapped_column(ForeignKey("admins.id", ondelete="CASCADE"), primary_key=True)` — must become `Mapped[UUID]`
- `create_admin.py` already passes `admin.id` through to `FleetMembership(admin_id=...)` — no change needed there

## Workstream 1: Backend changes

### A. Models

Update `database/models/admin.py`:

```python
from uuid import UUID

from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import func

class Admin(Base):
    __tablename__ = "admins"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )
    ...
```

### B. JWT

In `services/auth/jwt.py`:

```python
def create_access_token(admin_id: UUID) -> str:
    ...
    payload = {
        "sub": str(admin_id),
        ...
    }
```

In `dependencies.py`:

```python
admin_id = UUID(payload["sub"])
```

### C. Fleet service

In `services/fleet_service.py`:

```python
def set_membership(
    self,
    fleet_id: UUID,
    admin_id: UUID,
    role: str,
) -> FleetMembership:
```

### D. Migration

Create a new migration revision that:
1. Drops the `admin_id` foreign key on `fleet_memberships`
2. Alters `admins.id` from `Integer` to `UUID` (with `server_default=gen_random_uuid()`)
3. Alters `fleet_memberships.admin_id` from `Integer` to `UUID`
4. Re-adds the `admin_id` foreign key on `fleet_memberships`

The migration must be **tested against a real Postgres database** before relying on it.

### E. Tests

Update `tests/unit/services/test_operator_service.py` and any other tests that reference `Admin.id` / `admin_id` as integers.

## Workstream 2: Frontend changes

### A. Add a `features/fleets/` module

Create the following files:
- `src/features/fleets/fleets.api.ts` — `useFleetApi()` hook
- `src/features/fleets/fleets.types.ts` — types
- `src/features/fleets/FleetListPage.tsx` — list + create fleet
- `src/features/fleets/FleetDetailPage.tsx` — show fleet + memberships
- `src/features/fleets/FleetForm.tsx` — create/edit form
- `src/features/fleets/FleetMembershipPage.tsx` — add/remove members with role

### B. `fleets.api.ts`

```ts
import { useAuth } from '../../lib/useAuth'
import { apiRequest } from '../../lib/api'
import type { Fleet, FleetCreateInput, FleetMembershipInput } from './fleets.types'

export function useFleetApi() {
  const { accessToken, selectedFleetId } = useAuth()

  return {
    list: async () => {
      if (!accessToken) throw new Error('A fleet request requires an access token')
      return apiRequest<FleetListResponse>('/fleets', { accessToken })
    },
    create: async (fleet: FleetCreateInput) => {
      if (!accessToken) throw new Error('A fleet request requires an access token')
      return apiRequest<Fleet>('/fleets', {
        method: 'POST',
        accessToken,
        body: JSON.stringify(fleet),
      })
    },
  }
}
```

### C. `fleets.types.ts`

```ts
export type FleetRole = 'MANAGER' | 'MEMBER'

export interface Fleet {
  id: string
  name: string
  description?: string | null
  created_at: string
}

export interface FleetCreateInput {
  name: string
  description?: string | null
}

export interface FleetMembershipInput {
  role: FleetRole
}

export interface FleetListResponse {
  fleets: Fleet[]
}
```

### D. `apiRequest` behavior

`lib/api.ts` already supports `method`, `body`, and `accessToken` — reuse it as-is. The `PUT /fleets/{fleet_id}/memberships/{admin_id}` route needs `Authorization: Bearer` + `X-Fleet-ID` headers.

### E. Navigation

Check `App.tsx` / `AppLayout.tsx` for the existing routing pattern and add fleet routes following it.

### F. Permissions

The backend requires **superadmin** for fleet create/list/membership. The frontend currently has `PermissionGate` and `RequireAuth` components in `components/`. Check `lib/permissions.ts` — it currently only handles `MANAGER`/`MEMBER` fleet roles, not superadmin. Add a superadmin check so the UI doesn't expose fleet management to regular admins.

### G. Styling

Check `index.css` for existing patterns (the app uses a `.login-page` / `.login-card` / `.form-error` pattern). Follow the existing visual style.

## Notes

- Backend runs with `uv run clap-ops-service` in `/home/lucknt/NCI/FYP/CLAP-OPS-Service`
- Frontend runs with `npm` commands in `/home/lucknt/NCI/FYP/CLAP-OPS-UI`
- The frontend currently has no fleet UI and `selectedFleetId` in `vehicle.api.ts` has no source — the fleet selector you add should populate it
- Do not modify existing working code unless directly required by the changes above