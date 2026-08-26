Here is the complete system architecture for the **KSA Real Estate Ethics Reporting Platform**, designed as a lightweight, self-hosted, containerized monolith.

---

## 1. Database Schema (Prisma)

**File:** `prisma/schema.prisma`

```prisma
generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "sqlite"
  url      = env("DATABASE_URL")
}

// ── Enums ──────────────────────────────────────────────

enum UserRole {
  AUDITOR
  CEO
}

enum ReportStatus {
  NEW
  IN_REVIEW
  ESCALATED
  RESOLVED
}

enum ReportCategory {
  FINANCIAL_MISCONDUCT
  FRAUD_CORRUPTION
  HARASSMENT_WORKPLACE_MISCONDUCT
  HEALTH_SAFETY_VIOLATION
  OTHER
}

enum AuditAction {
  VIEWED
  ESCALATED
  RESOLVED
}

// ── Models ─────────────────────────────────────────────

model User {
  id           String     @id @default(uuid())
  email        String     @unique
  passwordHash String
  name         String
  role         UserRole
  isActive     Boolean    @default(true)
  createdAt    DateTime   @default(now())
  updatedAt    DateTime   @updatedAt
  lastLoginAt  DateTime?
  auditLogs    AuditLog[]
}

model Report {
  id           String         @id @default(uuid())
  receiptCode  String         @unique // 16-char alphanumeric reporter key
  category     ReportCategory
  description  String
  incidentDate DateTime?
  location     String?
  status       ReportStatus   @default(NEW)
  ipHash       String         // HMAC-SHA256(pepper, IP); never raw IP
  createdAt    DateTime       @default(now())
  updatedAt    DateTime       @updatedAt
  attachments  Attachment[]
  auditLogs    AuditLog[]
}

model Attachment {
  id           String   @id @default(uuid())
  reportId     String
  report       Report   @relation(fields: [reportId], references: [id], onDelete: Cascade)
  filename     String   // UUID on disk; no exec extension risk
  originalName String   // sanitized display name only
  mimeType     String   // validated whitelist
  size         Int      // bytes; enforced ≤ 5MB
  storagePath  String   // absolute path outside webroot
  exifStripped Boolean  @default(false)
  createdAt    DateTime @default(now())
}

model AuditLog {
  id        String      @id @default(uuid())
  reportId  String?
  report    Report?     @relation(fields: [reportId], references: [id], onDelete: SetNull)
  userId    String
  user      User        @relation(fields: [userId], references: [id], onDelete: Cascade)
  action    AuditAction
  details   String?     // e.g., "Status: NEW → IN_REVIEW"
  createdAt DateTime    @default(now())

  @@index([reportId])
  @@index([userId])
  @@index([createdAt])
}

// Tracks anonymous submission attempts for rate limiting
model RateLimit {
  id          String   @id @default(uuid())
  ipHash      String
  windowStart DateTime // truncated to the top of the hour
  count       Int      @default(1)

  @@unique([ipHash, windowStart])
  @@index([ipHash, windowStart])
}
```

---

## 2. REST API Contract

### Authentication
All admin endpoints require a JWT delivered via `Cookie: whistle_token` (httpOnly, Secure, SameSite=Strict). The React SPA uses `credentials: 'include'`.

---

### `POST /api/auth/login`
**Description:** Authenticate Internal Audit or CEO user.  
**Auth:** None  
**Body:**
```json
{
  "email": "string",
  "password": "string"
}
```
**Responses:**
- `200 OK`  
  `Set-Cookie: whistle_token=<jwt>; HttpOnly; Secure; SameSite=Strict; Max-Age=28800`  
  ```json
  {
    "user": {
      "id": "uuid",
      "email": "string",
      "name": "string",
      "role": "AUDITOR | CEO"
    }
  }
  ```
- `401 Unauthorized` — Invalid credentials.

---

### `POST /api/upload`
**Description:** Anonymous evidence upload. Files are quarantined, EXIF-stripped, and linked by ID in a subsequent report submission.  
**Auth:** None  
**Rate Limit:** Shared 5/hour/IP bucket with `POST /api/reports`.  
**Content-Type:** `multipart/form-data`  
**Form Fields:** `file` (single, max 5MB)  
**Validation:** Whitelist MIME (`image/jpeg`, `image/png`, `application/pdf`); magic-number verified.  
**Responses:**
- `201 Created`
  ```json
  {
    "id": "uuid",
    "filename": "uuid.jpg",
    "originalName": "sanitized_name.jpg",
    "mimeType": "image/jpeg",
    "size": 2048000,
    "exifStripped": true
  }
  ```
- `400 Bad Request` — Invalid type or size.
- `429 Too Many Requests`

---

### `POST /api/reports`
**Description:** Anonymous whistleblower submission. Zero cookies; only `ipHash` is persisted for rate-limit enforcement.  
**Auth:** None  
**Rate Limit:** 5 submissions per hour per IP (hashed).  
**Body:**
```json
{
  "category": "FINANCIAL_MISCONDUCT | FRAUD_CORRUPTION | HARASSMENT_WORKPLACE_MISCONDUCT | HEALTH_SAFETY_VIOLATION | OTHER",
  "description": "string (max 5000)",
  "incidentDate": "2024-06-15T00:00:00.000Z",
  "location": "string (optional)",
  "attachmentIds": ["uuid", "uuid"] // optional, max 5
}
```
**Responses:**
- `201 Created`
  ```json
  {
    "receiptCode": "X7K9P2M4Q8R1T6W3",
    "message": "Report submitted securely. Save your receipt code to check for updates."
  }
  ```
- `429 Too Many Requests`
- `400 Bad Request`

---

### `GET /api/reports`
**Description:** Auditor case-management inbox. Excludes `receiptCode` and `ipHash` to maintain reporter anonymity.  
**Auth:** JWT + `AUDITOR` role  
**Query Parameters:**
| Param | Type | Description |
|---|---|---|
| `status` | string | `NEW`, `IN_REVIEW`, `ESCALATED`, `RESOLVED` |
| `category` | string | Report category |
| `dateFrom` | ISO date | Filter `createdAt` ≥ |
| `dateTo` | ISO date | Filter `createdAt` ≤ |
| `search` | string | Fuzzy match on `description` |
| `page` | integer | Default `1` |
| `limit` | integer | Default `25`, max `100` |

**Response:** `200 OK`
```json
{
  "data": [
    {
      "id": "uuid",
      "category": "FRAUD_CORRUPTION",
      "description": "...",
      "status": "NEW",
      "incidentDate": "2024-06-10",
      "location": "Riyadh Site A",
      "createdAt": "2024-06-15T08:30:00.000Z",
      "attachments": [
        { "id": "uuid", "originalName": "invoice.pdf", "mimeType": "application/pdf", "size": 1024000 }
      ]
    }
  ],
  "meta": { "page": 1, "limit": 25, "total": 42 }
}
```

---

### `PUT /api/reports/:id/status`
**Description:** Move a report through the investigation workflow.  
**Auth:** JWT + `AUDITOR` role  
**Body:**
```json
{
  "status": "IN_REVIEW | RESOLVED",
  "note": "optional internal note"
}
```
**Business Rules:**
- `NEW` → `IN_REVIEW` (start investigation)
- `IN_REVIEW` → `RESOLVED` (close case)
- Direct transition to `ESCALATED` is blocked; use `POST /api/reports/:id/escalate`.

**Responses:**
- `200 OK` — Returns updated report object.
- `403 Forbidden` — CEO role insufficient.
- `409 Conflict` — Invalid state transition.

---

### `POST /api/reports/:id/escalate`
**Description:** Escalate an `IN_REVIEW` case to the Governance Layer (CEO). Idempotent if already `ESCALATED`.  
**Auth:** JWT + `AUDITOR` role  
**Body:**
```json
{
  "reason": "Financial threshold exceeded; requires executive oversight."
}
```
**Side Effects:** Sets `status = ESCALATED`; creates `AuditLog` entry.  
**Responses:**
- `200 OK`
- `409 Conflict` — Report not in `IN_REVIEW`.

---

### `GET /api/reports/escalated`
**Description:** CEO governance view. Returns only `ESCALATED` cases with direct identifiers redacted (`receiptCode`, `ipHash`, and exact `createdAt` truncated to date-only).  
**Auth:** JWT + `CEO` role  
**Query Parameters:** Same filter semantics as `GET /api/reports` (minus `status`).  
**Response:** `200 OK` — Array of escalated report summaries.

---

### `GET /api/audit-log`
**Description:** Immutable audit trail of all investigator/executive actions.  
**Auth:** JWT (`AUDITOR` or `CEO`)  
**Query Parameters:** `reportId`, `userId`, `action`, `dateFrom`, `dateTo`, `page`, `limit`.  
**Response:** `200 OK`
```json
{
  "data": [
    {
      "id": "uuid",
      "reportId": "uuid",
      "user": { "id": "uuid", "name": "A. Al-Rashid", "role": "AUDITOR" },
      "action": "ESCALATED",
      "details": "Status: IN_REVIEW → ESCALATED | Reason: Financial threshold exceeded",
      "createdAt": "2024-06-16T10:00:00.000Z"
    }
  ],
  "meta": { "page": 1, "limit": 50, "total": 120 }
}
```

---

## 3. Component Tree (React + Vite)

```
src/
├── main.jsx
├── App.jsx                 // BrowserRouter + route guards
├── api/
│   └── client.js           // Axios instance; credentials: 'include'
├── routes.jsx
│   ├── PublicRoutes
│   │   └── /               → AnonymousSubmissionPage
│   ├── AuthRoutes
│   │   └── /login          → LoginPage
│   └── ProtectedRoutes     // Validates JWT cookie + role
│       └── /dashboard      → DashboardLayout
│           ├── /auditor    → AuditorDashboardPage
│           ├── /ceo        → CEODashboardPage
│           └── /audit-log  → AuditLogPage
│
├── layouts/
│   ├── PublicLayout.jsx    // Zero-tracking header; no analytics scripts
│   └── DashboardLayout.jsx
│       ├── Sidebar.jsx     // Role-aware navigation
│       ├── TopBar.jsx      // User badge + logout
│       └── MainPanel.jsx   // Responsive grid for laptop density
│
├── pages/
│   ├── AnonymousSubmissionPage.jsx
│   │   ├── TrustHeader.jsx         // "Zero Tracking • No Cookies • No IP Logs"
│   │   ├── CategoryGrid.jsx        // 5 selectable category cards
│   │   ├── AnonymousForm.jsx       // Description, date, location
│   │   ├── FileUploadZone.jsx      // Drag & drop; calls POST /api/upload
│   │   └── ReceiptModal.jsx        // Post-submit receipt code display
│   │
│   ├── LoginPage.jsx
│   │   └── LoginForm.jsx
│   │
│   ├── AuditorDashboardPage.jsx
│   │   ├── FilterBar.jsx
│   │   ├── StatsSummary.jsx        // NEW / IN_REVIEW / ESCALATED / RESOLVED counts
│   │   ├── ReportDataTable.jsx     // Dense, sortable, keyboard-navigable
│   │   ├── ReportDetailDrawer.jsx  // Slide-out case file
│   │   ├── StatusUpdateModal.jsx
│   │   └── EscalateModal.jsx
│   │
│   ├── CEODashboardPage.jsx
│   │   ├── GovernanceFilterBar.jsx
│   │   ├── EscalatedCasesTable.jsx // Redacted identifiers
│   │   └── GovernanceMetrics.jsx   // Aggregated category trends (anonymized)
│   │
│   └── AuditLogPage.jsx
│       └── AuditLogTable.jsx
│
├── components/
│   ├── shared/
│   │   ├── DataTable.jsx
│   │   ├── StatusBadge.jsx         // Color-coded workflow states
│   │   ├── DateHijriWrapper.jsx   // Hijri/Gregorian dual display
│   │   └── EmptyState.jsx
│   └── guards/
│       ├── RoleGuard.jsx           // Redirect CEO away from /auditor
│       └── AnonRouteGuard.jsx      // Prevent authenticated users on /
│
├── hooks/
│   ├── useAuth.js
│   ├── useReports.js
│   └── useAuditLog.js
│
└── utils/
    ├── crypto.js           // Receipt code generator
    └── validators.js       // File type & size checks
```

---

## 4. Security Model

### Authentication Layer
- **JWT Strategy:** Short-lived access tokens (`exp` = 8 hours) signed with `RS256` (asymmetric key pair). No refresh-token complexity; daily re-authentication is acceptable for a small internal audit team and limits stolen-token window.
- **Transport:** Tokens are bound to `httpOnly`, `Secure`, `SameSite=Strict` cookies named `whistle_token`. The React SPA uses `credentials: 'include'`. This eliminates XSS token exfiltration risks inherent in `localStorage`.
- **Password Hashing:** `bcrypt` with cost factor `12`. Enforced minimum password length of 12 characters.

### Authorization Layer
- Role-based middleware (`requireRole('AUDITOR')`, `requireRole('CEO')`) inspects the JWT payload before route handlers.
- CEO endpoints explicitly reject `AUDITOR` tokens and vice versa.
- Audit logs are append-only from the application layer; no `DELETE` or `PUT` operations exposed.

### Anonymous Submission Layer
- **Zero Tracking:** No session cookies, no fingerprinting scripts, no analytics. The only client-side storage is React state.
- **IP Anonymization:** Raw IP addresses are never logged. A one-way `HMAC-SHA256(ip, daily_rotating_pepper)` is computed at the edge and stored as `ipHash`. The pepper is rotated via environment variable; old hashes become non-reversible even if the database is exfiltrated.
- **Rate Limiting:** A SQLite `RateLimit` table tracks `(ipHash, windowStart)` with a 1-hour sliding window. Max 5 combined attempts across `/api/upload` and `/api/reports`. Returns `429` without leaking window metadata.

### File Upload Security
- **Engine:** `multer` with `diskStorage` (streams to disk; never buffers >5MB in memory).
- **Validation:** Dual-layer check:
  1. Extension whitelist: `.jpg`, `.jpeg`, `.png`, `.pdf`.
  2. Magic-number inspection via `file-type` library on the first few bytes.
- **Sanitization:**
  - Images processed through `sharp` to strip EXIF/GPS metadata and rewrite to a clean bitmap before re-encoding.
  - PDFs stored with UUID filenames; served with `Content-Disposition: attachment` and `X-Content-Type-Options: nosniff` to prevent browser execution.
- **Storage:** Files reside outside the webroot (`/data/uploads/`). Filenames are UUIDv4; original names are sanitized and stored only for UI display.

### CORS & Transport
- **CORS:** Strict single-origin policy. `Access-Control-Allow-Origin` mirrors the self-hosted domain exactly; `Access-Control-Allow-Credentials: true` only for admin subpaths. Public submission endpoints do not accept credentials (no cookies).
- **TLS:** Mandatory TLS 1.3. HSTS header enabled.
- **Helmet.js:** Enforces CSP `default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' blob:; connect-src 'self'`.

### Data Privacy & Anonymity
- **Reporter Isolation:** `receiptCode` is never exposed to auditors or CEOs. It exists solely for a future (undocumented) reporter lookup endpoint.
- **Database Hygiene:** Prisma ORM eliminates raw SQL injection vectors. All admin inputs are validated with `zod` before touching the service layer.

---

## 5. Decision Log

| Decision | Justification | Trade-off | Mitigation |
|---|---|---|---|
| **JWT over Server-Side Sessions** | Eliminates session store infrastructure (Redis/memory) for a single-node, SQLite-backed deployment. JWTs allow stateless auth validation, fitting the "lightweight self-hosted" mandate. | No server-side revocation list; stolen tokens valid until expiry. | Short 8-hour expiry; httpOnly cookie binding prevents XSS theft; daily re-auth acceptable for 2–5 internal users. |
| **SQLite over PostgreSQL** | Zero separate DB process, minimal container footprint, and trivial backup (single file). Expected load is low-volume (dozens of reports/month, <5 concurrent admins). Prisma ensures migration path to PostgreSQL remains trivial if scale changes. | No row-level locking concurrency; limited HA/replication features. | Write-ahead logging enabled; serialized writes acceptable for this use case. Backup strategy: nightly volume snapshot of the SQLite file. |
| **Multer for File Uploads** | De-facto Express standard; handles streaming multipart data efficiently without loading files into memory. Native integration with file filtering, size limits, and disk storage paths. | Requires careful configuration to avoid path traversal or memory exhaustion. | Explicit `diskStorage` config; absolute upload directory; `limits: { fileSize: 5 * 1024 * 1024 }`; magic-number validation before disk write completion. |
| **Separate CEO View (`/reports/escalated`)** | Enforces **need-to-know** segregation and prevents re-identification risks at the executive level. Internal Audit acts as a filter: CEOs see only substantiated, escalated matters rather than raw, unvetted allegations. Aligns with Saudi corporate governance and Vision 2030 transparency mandates. | CEO loses visibility into early-stage case volume/trends. | Governance dashboard supplements the table with **aggregated, anonymized metrics** (category counts, resolution velocity) so the CEO retains strategic intelligence without direct identifier exposure. |
| **Receipt Code instead of User Accounts for Whistleblowers** | True anonymity requires no email, phone, or credential collection. A long random receipt code provides continuity (check for updates) without identity linkage. | Reporter must physically save the code; lost codes are unrecoverable. | UI emphasizes code preservation with copy-to-clipboard and printable summary; no "password reset" flow exists because there is no identity. |
| **HMAC-IP Hashing with Pepper** | Satisfies the requirement to rate-limit by IP while respecting anonymity. A daily rotating pepper prevents rainbow-table reversal of known corporate IP ranges. | Rate-limit windows reset if pepper rotates mid-hour (rare, acceptable). | Pepper rotation scripted for low-traffic maintenance windows; old window records purged after 24 hours. |

---