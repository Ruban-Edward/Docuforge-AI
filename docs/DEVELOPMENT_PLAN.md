# DocuForge AI — Development Plan

> **Platform:** AI-powered documentation standardisation platform
>
> **Stack:** React + TypeScript + Vite + Tailwind + shadcn/ui · Python + FastAPI + Pydantic + SQLAlchemy + Alembic · PostgreSQL · LLM API · python-docx + PyMuPDF + LibreOffice headless · Docker + Docker Compose

---

## Phase 1: Project Foundation, Backend Setup, Database, Authentication, and Template Management

### Objectives

- Establish the entire monorepo project structure and development environment.
- Define, implement, and migrate the full initial database schema (all 14 models).
- Implement JWT-based authentication with token refresh and logout.
- Implement role-based access control (RBAC) as a reusable dependency.
- Implement full CRUD APIs for users, departments, templates, template versions, and template sections.
- Implement admin statistics and audit log endpoints.
- Build the foundational React frontend with authentication, layout, and all management UIs.
- Write foundational backend tests to validate core behaviour.

### Features Delivered

- Secure login and logout with JWT access + refresh tokens.
- Role-based access enforcement across all API endpoints.
- Full user management (create, edit, assign roles, deactivate).
- Department management (create, edit, list).
- Template management with version control and section ordering.
- Admin dashboard stub with system statistics and audit log.
- Responsive application shell (sidebar, header, protected routes).

### Implementation Tasks

#### Backend Tasks

1. Initialise FastAPI project with a modular package structure (`app/api/`, `app/services/`, `app/models/`, `app/schemas/`, `app/core/`, `app/db/`).
2. Configure Pydantic `BaseSettings` to load all configuration from environment variables (`.env`).
3. Configure SQLAlchemy async engine and session factory using `asyncpg`.
4. Implement all 14 database models with SQLAlchemy ORM (users, roles, departments, permissions, templates, template versions, template sections, documents, document versions, document sections, ai_processing_jobs, ai_usage_records, audit_logs, review_records).
5. Create a single Alembic migration covering the full initial schema, including indexes and foreign keys.
6. Write a database seeder to insert system roles (Admin, Manager, Editor, Viewer) and default permissions on first run.
7. Implement JWT authentication: `POST /auth/login` (issue access + refresh tokens), `POST /auth/refresh`, `POST /auth/logout` (blacklist token), `PUT /auth/change-password`.
8. Implement RBAC via a FastAPI dependency (`require_roles`, `require_permissions`) injected into route handlers.
9. Implement users CRUD API (`GET/POST /users`, `GET/PUT/DELETE /users/{id}`, `PUT /users/{id}/roles`) with RBAC enforcement.
10. Implement departments CRUD API (`GET/POST /departments`, `GET/PUT/DELETE /departments/{id}`).
11. Implement templates CRUD API (`GET/POST /templates`, `GET/PUT/DELETE /templates/{id}`).
12. Implement template versions CRUD API (`GET/POST /templates/{id}/versions`, `GET/PUT /templates/{id}/versions/{ver_id}`, `POST /templates/{id}/versions/{ver_id}/publish`).
13. Implement template sections CRUD API (`GET/POST /templates/{id}/versions/{ver_id}/sections`, `GET/PUT/DELETE .../sections/{sec_id}`, `PUT .../sections/reorder`).
14. Implement admin endpoints: `GET /admin/stats`, `GET /admin/audit-log` (paginated, filterable).
15. Set up structured JSON logging (`structlog` or `loguru`) with request ID middleware.
16. Implement custom exception handlers returning consistent JSON error envelopes.
17. Configure CORS with an allowlist from environment variables.

#### Frontend Tasks

1. Initialise React + TypeScript project with Vite (`npm create vite`).
2. Configure Tailwind CSS and install shadcn/ui; set up the base component library.
3. Set up React Router v6 with a root layout and nested route definitions.
4. Implement an Axios instance with request interceptors (attach Bearer token) and response interceptors (silent access-token refresh on 401).
5. Implement an Auth Context/Store (React Context + `useReducer`) managing user identity, tokens, and login/logout actions.
6. Implement the Login page with form validation (`react-hook-form` + `zod`), error display, and redirect on success.
7. Implement a `<ProtectedRoute>` wrapper that redirects unauthenticated users to `/login` and enforces role visibility.
8. Implement the main application layout: collapsible sidebar with navigation links, top header with user menu and notifications stub.
9. Implement the Dashboard skeleton page with placeholder statistic cards.
10. Implement Template Management pages: template list (table with search/filter/pagination), create template modal, template edit page, template version list, and a drag-and-drop section editor (reorder sections, add/edit/delete sections).
11. Implement User Management pages: user list table, create user drawer, edit user page, role assignment multi-select.
12. Implement Department Management page: list, create, and edit departments.
13. Implement Application Settings stub page (placeholder for Phase 5 admin features).
14. Implement a global toast notification system and a confirmation dialog component.

#### Infrastructure Tasks

1. Create `docker-compose.yml` defining services: `backend` (FastAPI + Uvicorn), `frontend` (Vite dev server), `db` (PostgreSQL 16), `nginx` (reverse proxy for frontend).
2. Write `Dockerfile` stubs for backend and frontend (dev mode with hot-reload volumes).
3. Create `.env.example` files for both `backend/` and `frontend/` documenting all required variables.
4. Add a comprehensive `.gitignore` covering Python, Node, Docker, and IDE artefacts.

### Dependencies

- No prior phase required. This is the project origin.
- Requires: PostgreSQL 16+, Python 3.11+, Node.js 20+, Docker Desktop or Docker Engine.

### Expected Deliverables

- Fully runnable local development environment via `docker compose up`.
- Complete database schema applied via Alembic (`alembic upgrade head`).
- Working JWT authentication flow (login → access token → refresh → logout).
- All CRUD REST APIs for users, departments, templates, versions, and sections.
- React frontend with login, protected routing, layout, and all management UIs functional against the live API.
- Foundational backend test suite (`pytest`) covering auth, RBAC, and template endpoints.
- `.env.example` and project-level `README.md` with setup instructions.

### Acceptance Criteria

1. `docker compose up` starts all services without errors; frontend is accessible at `http://localhost:5173` and API at `http://localhost:8000`.
2. `POST /auth/login` with valid credentials returns a 200 with `access_token` and `refresh_token`.
3. Accessing any protected endpoint without a token returns 401; with an insufficient-role token returns 403.
4. Full CRUD lifecycle (create → read → update → delete) passes for templates, template versions, sections, users, and departments.
5. The section reorder endpoint correctly persists the new `order_index` values.
6. `alembic upgrade head` applies all migrations cleanly on a fresh database.
7. All seeded system roles are present in the database after first run.
8. All backend unit tests pass (`pytest -q` exits 0).
9. The React frontend login flow works end-to-end: submit credentials → receive token → see dashboard → sidebar navigation works → logout clears session.
10. The template section editor allows adding, editing, reordering (drag-and-drop), and deleting sections with changes persisted to the API.

### Estimated Effort

**2–3 weeks** for a solo developer.

---

## Phase 2: Document Upload, Content Extraction, AI Integration, and Structured Information Extraction

### Objectives

- Implement a secure file upload endpoint with strict MIME type and size validation.
- Implement pluggable text extractors for DOCX, PDF, Markdown, and plain text.
- Design and implement a provider-independent AI abstraction layer.
- Implement a concrete LLM provider (OpenAI or equivalent) using structured JSON output mode.
- Validate all AI responses against Pydantic schemas before persistence.
- Implement background AI processing job tracking and status polling.
- Implement a paste-content (raw text) ingestion endpoint as an alternative to file upload.

### Features Delivered

- Drag-and-drop or browse file upload supporting DOCX, PDF, MD, and TXT.
- Paste-text content ingestion via text area.
- Real-time processing status page with a progress indicator and polling.
- Preview of AI-extracted section content before proceeding to mapping.

### Implementation Tasks

#### Backend Tasks

1. Implement `POST /documents/upload` endpoint: validate MIME type against an allowlist (`application/vnd.openxmlformats-officedocument.wordprocessingml.document`, `application/pdf`, `text/markdown`, `text/plain`), reject disallowed types with 422, store file with a UUID filename to a configured storage directory, create a `documents` DB record.
2. Implement `DocxProcessor` using `python-docx` to extract full text and heading-structured content from `.docx` files.
3. Implement `PdfProcessor` using `PyMuPDF` (`fitz`) to extract text page by page, with basic heading heuristics.
4. Implement `MarkdownProcessor` to parse Markdown headings and body content.
5. Implement `TxtProcessor` for plain-text ingestion with paragraph segmentation.
6. Implement `ProcessorFactory` selecting the correct processor by MIME type.
7. Implement `BaseAIProvider` abstract class defining the `extract(text, template_schema) -> AIExtractionResult` interface.
8. Implement a concrete `OpenAIProvider` (or equivalent LLM provider) calling the chat completions API in JSON mode with a structured prompt derived from the target template's section keys.
9. Implement `ProviderFactory` selecting the active provider from application configuration.
10. Define `AIExtractionResult` and per-section Pydantic schemas for AI response validation; raise `AIResponseValidationError` on schema mismatch.
11. Implement `AIProcessingService` orchestrating the full pipeline: extract text → preprocess/truncate → submit to AI provider → validate response → persist extracted sections to `ai_processing_jobs` and `document_sections` staging tables.
12. Implement `ai_processing_jobs` CRUD: create job on upload, update status (`pending` → `processing` → `completed` / `failed`), store error detail on failure.
13. Implement `ai_usage_records` tracking: record model, prompt tokens, completion tokens, estimated cost per AI call.
14. Implement `GET /documents/{doc_id}/processing-status` for status polling.
15. Implement `GET /documents/{doc_id}/extraction-result` returning raw AI-extracted sections for preview.
16. Implement `POST /documents/paste` accepting `{ content: str, template_id: UUID }` and triggering the same processing pipeline.

#### Frontend Tasks

1. Implement the Upload / Paste Content page with a file dropzone (`react-dropzone`) supporting drag-and-drop and click-to-browse.
2. Implement client-side file type validation (extension + MIME sniffing) with inline error messages.
3. Implement a template selector dropdown on the upload page (fetched from `GET /templates`).
4. Implement a paste-text tab with a `<textarea>` showing live character count.
5. Implement the Processing Status page with an auto-polling hook (every 2 s via `setInterval`) hitting `GET /documents/{doc_id}/processing-status`, rendering a progress stepper (Uploaded → Extracting → AI Processing → Complete).
6. Implement the Extraction Result Preview page displaying AI-extracted sections in a read-only structured view before the user proceeds to the mapping/validation step.

### Dependencies

- Phase 1 must be complete: database schema, document model, authenticated API, and template management must all be in place.
- LLM API credentials (e.g., `OPENAI_API_KEY`) must be available in the environment.

### Expected Deliverables

- Working file upload endpoint with MIME validation and UUID-based storage.
- All four file processors implemented and independently testable.
- AI abstraction layer with at least one concrete provider.
- Full async processing pipeline from upload to persisted AI extraction result.
- Frontend upload/paste UI and processing status page.
- Unit tests for each processor and AI provider mock.

### Acceptance Criteria

1. Uploading a `.docx`, `.pdf`, `.md`, and `.txt` file each triggers processing and reaches `completed` status.
2. Uploading a file with a disallowed MIME type (e.g., `.exe`) returns a 422 with a clear error message.
3. After successful processing, `GET /documents/{doc_id}/extraction-result` returns structured section content.
4. `POST /documents/paste` with valid text triggers the same pipeline and reaches `completed` status.
5. `ai_usage_records` contains a record with token counts for each AI call made.
6. A malformed AI response (simulated in tests) is caught by Pydantic validation and results in a `failed` job status with an error message persisted to the DB.
7. The frontend polling hook stops and transitions to the result preview page when status is `completed`.
8. All processor unit tests pass with sample fixture files.

### Estimated Effort

**2–3 weeks** for a solo developer.

---

## Phase 3: Heading Mapping, Missing Section Detection, and Interactive Validation

### Objectives

- Implement a Python service that maps AI-extracted content keys to canonical template section records using `section_key` matching.
- Detect which mandatory template sections have no mapped content.
- Present an interactive frontend workflow for users to review, fill in missing sections, or skip optional ones.
- Enforce the business rule that mandatory sections cannot be skipped.
- Provide a pre-generation validation endpoint to gate document generation.

### Features Delivered

- Automatic mapping of AI-extracted content to the target template's sections.
- Clear visual indication of section status: Complete, Missing (Mandatory), or Optional.
- Inline text editor for users to provide content for missing mandatory sections.
- Skip option (with reason) for optional sections.
- Validation summary and progress indicator before proceeding to generation.

### Implementation Tasks

#### Backend Tasks

1. Implement `SectionMappingService`: for each AI-extracted key, look up a matching `template_section` record by `section_key` for the document's target `template_version_id`; create `document_sections` records for all matched sections.
2. Implement missing section detection: compare the set of populated `document_sections` against all sections in the template version; classify each unmatched section as `mandatory` or `optional` based on `is_required` flag.
3. Implement `GET /documents/{doc_id}/sections` returning all sections with their current status and content.
4. Implement `GET /documents/{doc_id}/sections/missing` returning only sections with no mapped content, annotated with `is_required`.
5. Implement `PUT /documents/{doc_id}/sections/{section_id}` allowing users to supply or update section content (creates or updates the `document_section` record).
6. Implement `PUT /documents/{doc_id}/sections/{section_id}/skip` with a `reason` body field, setting `status = skipped`; return 400 if the section is mandatory.
7. Implement `POST /documents/{doc_id}/sections/validate` running pre-generation checks: all mandatory sections must have `status = complete`; return a structured list of violations if any exist.
8. Enforce the business rule server-side: a `PUT .../skip` on a mandatory section always returns 400 regardless of frontend state.

#### Frontend Tasks

1. Implement the Missing Sections Review page, fetching from `GET /documents/{doc_id}/sections`.
2. Render each section as a card displaying: section title, AI-extracted content (read-only preview in a styled block), and a status badge (`Complete` / `Missing – Required` / `Optional`).
3. For missing mandatory sections: render an inline rich-text or plain-text editor pre-populated with any partial AI content; content is auto-saved on blur via `PUT .../sections/{id}`.
4. For optional sections: render an editor and a "Skip" button that opens a small popover asking for a skip reason before confirming.
5. Implement a fixed validation summary sidebar or bottom bar showing the count of remaining required sections and a "Proceed to Generation" button (disabled until all mandatory sections are complete).
6. Implement a real-time section completion progress bar (e.g., "7 / 10 sections complete").

### Dependencies

- Phase 2 must be complete: AI extraction pipeline must produce structured extraction results stored in the database.
- Template section `section_key` values and `is_required` flags must be correctly seeded during template authoring (Phase 1).

### Expected Deliverables

- `SectionMappingService` with unit tests covering exact match, partial match, and no-match scenarios.
- All six section-related API endpoints implemented and tested (including RBAC enforcement).
- Pre-generation validation endpoint with integration tests.
- Frontend missing sections review page wired to the live API.
- Business rule test: `PUT .../skip` on a mandatory section returns 400.

### Acceptance Criteria

1. After AI extraction completes, `GET /documents/{doc_id}/sections` returns all template sections annotated with mapping status.
2. `GET /documents/{doc_id}/sections/missing` returns only sections with no AI-extracted content.
3. Submitting content via `PUT /documents/{doc_id}/sections/{section_id}` updates the section status to `complete`.
4. `PUT /documents/{doc_id}/sections/{section_id}/skip` succeeds (200) for optional sections and returns 400 for mandatory ones.
5. `POST /documents/{doc_id}/sections/validate` returns 200 with no violations when all mandatory sections are complete, and returns a non-empty violations list when any mandatory section is missing.
6. The frontend "Proceed to Generation" button is disabled while any mandatory section is incomplete and enables as soon as the last mandatory section is filled.
7. Skipping a mandatory section from the frontend is blocked (UI disables the skip option) and also blocked at the API level.

### Estimated Effort

**1–2 weeks** for a solo developer.

---

## Phase 4: DOCX Generation, PDF Export, Document Preview, and Editing

### Objectives

- Implement python-docx–based DOCX generation that populates an official template file while preserving its styles, headers, footers, and page numbering.
- Implement LibreOffice headless PDF conversion as a subprocess call.
- Implement Markdown export rendered from document sections.
- Implement document versioning: each generation event creates a new immutable `document_version` record.
- Implement in-browser document preview rendered section by section.
- Implement post-generation section editing and re-generation workflow.

### Features Delivered

- One-click document generation producing a styled DOCX.
- Download DOCX, PDF, and Markdown exports from the preview page.
- In-browser structured document preview with per-section editing.
- Version history panel listing all generated versions with individual download options.

### Implementation Tasks

#### Backend Tasks

1. Implement `DocxGenerator`: open the template DOCX file associated with the `template_version`, iterate over `document_sections` in `order_index` order, populate section heading and body paragraphs using `python-docx` while preserving existing styles, headers, footers, and page number fields; save the output DOCX to the storage directory.
2. Implement `PdfExporter`: invoke LibreOffice headless (`soffice --headless --convert-to pdf`) as a managed subprocess with a configurable timeout; capture stderr for error reporting.
3. Implement `MarkdownExporter`: render document sections as Markdown using heading levels derived from `section_level` and body content.
4. Implement `POST /documents/{doc_id}/generate`: create a `document_version` record (storing `template_version_id` immutably at the moment of generation), trigger `DocxGenerator` (and queue `PdfExporter`), return `{ version_id }`.
5. Implement export streaming endpoints: `GET /documents/{doc_id}/versions/{version_id}/export/docx`, `.../export/pdf`, `.../export/markdown`; stream files using `FileResponse`.
6. Ensure `template_version_id` on `document_version` is never updated after creation (server-side enforcement).
7. Implement `GET /documents/{doc_id}/versions` listing all versions with metadata (created_at, status, template_version label).
8. Implement `GET /documents/{doc_id}/versions/{version_id}` returning version detail including all section content at time of generation.
9. Implement draft section editing endpoints: `PUT /documents/{doc_id}/sections/{section_id}` (update content in draft state), `POST /documents/{doc_id}/regenerate` (creates a new version from updated draft sections).

#### Frontend Tasks

1. Implement the generation trigger: a "Generate Document" button on the validation complete page, posting to `POST /documents/{doc_id}/generate` and navigating to the generation status page.
2. Implement a generation status indicator (spinner / progress steps) polling `GET /documents/{doc_id}/processing-status` until generation is `complete`.
3. Implement the Document Preview page: render the generated document content section by section in a styled, paginated view.
4. Implement per-section inline edit mode: clicking "Edit" on a section opens an in-place editor; saving auto-persists via the draft edit endpoint.
5. Implement export buttons: "Download DOCX", "Download PDF", "Download Markdown" — each triggering the corresponding streaming endpoint.
6. Implement the Version History panel (sidebar or expandable drawer) listing all versions with timestamps and per-version download buttons.

#### Infrastructure Tasks

1. Add `libreoffice-headless` (or `libreoffice`) to the backend Docker image.
2. Ensure the storage volume is writable by the backend container user.

### Dependencies

- Phase 3 must be complete: pre-generation validation endpoint must pass before generation is triggered.
- The official DOCX template file must be uploaded/associated with each template version (can be managed via admin UI from Phase 1).
- LibreOffice must be available in the backend runtime environment.

### Expected Deliverables

- `DocxGenerator`, `PdfExporter`, and `MarkdownExporter` implementations with unit tests (using fixture template files).
- All generation, versioning, and export API endpoints.
- Frontend document preview, section edit, export, and version history UI.
- Integration test: full lifecycle from generation trigger to file download.

### Acceptance Criteria

1. `POST /documents/{doc_id}/generate` creates a `document_version` record and produces a valid DOCX file on disk.
2. The generated DOCX preserves the template's styles, headers, footers, and page numbers (manual verification against a reference template).
3. `GET .../export/pdf` returns a valid PDF (non-zero bytes, correct Content-Type).
4. `GET .../export/markdown` returns well-formed Markdown with correct heading hierarchy.
5. `template_version_id` on `document_version` matches the template version active at generation time and cannot be changed by any subsequent API call.
6. Editing a section in draft and calling `POST /documents/{doc_id}/regenerate` creates a new version with the updated content.
7. The Version History panel lists all previous versions; downloading an older version returns that version's files (not the latest).
8. LibreOffice conversion completes within the configured timeout; a timeout triggers a `failed` version status with an error message.

### Estimated Effort

**2–3 weeks** for a solo developer.

---

## Phase 5: Document History, Versioning, Administration, Review Workflows

### Objectives

- Implement full document version browsing with side-by-side section diff comparison.
- Implement version restore (clone a past version as a new draft).
- Implement a review and approval workflow (submit → pending review → approve / reject / request changes).
- Implement the admin dashboard with real system statistics.
- Implement AI usage monitoring with charts and filterable tables.
- Implement full audit log browsing with filtering.

### Features Delivered

- Complete document version history with visual diff comparison.
- One-click restore of any past version.
- Submit-for-review flow with email notification stub and status tracking.
- Manager review page: approve, reject, or request changes with comments.
- Admin dashboard: user count, document count, AI call count, token usage.
- AI usage analytics table with date-range filtering and usage charts.
- Audit log table with actor, action, resource, and timestamp filters.

### Implementation Tasks

#### Backend Tasks

1. Implement `GET /documents/{doc_id}/versions` with full metadata (already scaffolded in Phase 4; expand to include section-level snapshots for diff support).
2. Implement `GET /documents/{doc_id}/versions/{version_id}` returning all section content at time of that generation.
3. Implement `PUT /documents/{doc_id}/versions/{version_id}/restore`: copy the section content of the specified version into a new draft, creating a new `document_version` record with `status = draft`.
4. Implement `POST /documents/{doc_id}/reviews`: submit document for review, create a `review_records` entry, assign a reviewer (passed in body or auto-assigned by department), update document status to `pending_review`.
5. Implement `GET /reviews/pending` (Manager+ role): list all documents with `pending_review` status assigned to the requesting user.
6. Implement `PUT /documents/{doc_id}/reviews/{review_id}`: accept `{ decision: approved | rejected | changes_requested, comment: str }`; update document status accordingly; write an audit log entry.
7. Update document status FSM: `draft → pending_review → approved | rejected | changes_requested → draft (on revision) → pending_review`.
8. Implement `GET /admin/stats` returning: total users (by role), total documents (by status), total AI calls (last 30 d), total tokens consumed, storage used (MB).
9. Implement `GET /admin/ai-usage` with pagination, date-range filter (`from`, `to`), and optional `user_id` filter.
10. Implement `GET /admin/audit-log` with pagination and filters: `actor_id`, `action`, `resource_type`, `from`, `to`.

#### Frontend Tasks

1. Implement the Document History page: timeline view of all versions with status badges, creation timestamps, and "Restore" and "Compare" actions per version.
2. Implement the Version Comparison view: side-by-side section diff using a lightweight diff library (e.g., `diff-match-patch`), highlighting added/removed text in each section.
3. Implement the Submit for Review button (shown to Editors on approved draft documents); display a reviewer assignment dialog.
4. Implement the Review Pending status banner on the document preview page.
5. Implement the Manager Review page: table of pending reviews with document title, submitter, submitted date; expand a row to approve/reject/request changes with a comment field.
6. Implement the Admin Dashboard page: stat cards (users, documents, AI calls, tokens), a sparkline chart for daily AI usage, quick links to AI usage and audit log tables.
7. Implement the AI Usage table: paginated, sortable, with a date-range picker filter and a bar chart of daily token consumption.
8. Implement the Audit Log table: paginated, with actor, action, resource type, and date range filters; export to CSV button.

### Dependencies

- Phase 4 must be complete: document versioning infrastructure must exist.
- Review workflow requires at least two user roles (Editor and Manager) which are seeded in Phase 1.

### Expected Deliverables

- Version restore and comparison endpoints with integration tests.
- Full review workflow API with FSM status transitions tested.
- Admin stats, AI usage, and audit log endpoints with integration tests.
- Frontend version history, comparison, review, admin dashboard, AI usage, and audit log pages.

### Acceptance Criteria

1. `PUT /documents/{doc_id}/versions/{version_id}/restore` creates a new draft version whose section content exactly matches the restored version.
2. `POST /documents/{doc_id}/reviews` transitions document status to `pending_review` and creates a review record.
3. `PUT .../reviews/{review_id}` with `approved` transitions status to `approved` and writes an audit log entry.
4. `PUT .../reviews/{review_id}` with `rejected` transitions status to `rejected` and writes an audit log entry.
5. `GET /reviews/pending` returns only documents assigned to the requesting reviewer (Manager+ role); returns 403 for Editors.
6. `GET /admin/stats` returns correct counts matching the actual database state (verified by integration test with known fixtures).
7. `GET /admin/ai-usage` correctly filters results when `from` and `to` query parameters are supplied.
8. `GET /admin/audit-log` returns only entries matching the requested `actor_id` and `action` filters.
9. The version comparison view correctly highlights changed content between two versions (manual verification).
10. The Manager review page shows the approve/reject action and the resulting status change is reflected in the document list.

### Estimated Effort

**2–3 weeks** for a solo developer.

---

## Phase 6: Testing, Security Verification, Docker, and Deployment Preparation

### Objectives

- Write comprehensive unit and integration tests for all backend services and API endpoints.
- Write frontend component and integration tests for critical user flows.
- Perform a security review covering auth, file handling, CORS, and rate limiting.
- Finalise production Docker configuration with multi-stage builds.
- Prepare complete deployment documentation.

### Features Delivered

- Full automated test suite (backend + frontend) runnable in CI.
- Production-grade Docker images with minimal attack surface.
- Health check endpoints for orchestration readiness probes.
- Rate limiting on sensitive endpoints.
- Complete `README.md` and deployment guide.

### Implementation Tasks

#### Backend Tasks

1. Configure `pytest` with fixtures: test database (PostgreSQL test instance or SQLite for unit tests), `AsyncClient` via `httpx`, factory fixtures for users, templates, and documents.
2. Write unit tests for `AuthService` (login, refresh, logout, password change, JWT expiry).
3. Write unit tests for `TemplateService` (CRUD, version publishing, section reorder).
4. Write unit tests for `DocumentService` (upload, status transitions).
5. Write unit tests for `AIProcessingService` (mocked AI provider, validation failure path).
6. Write unit tests for `SectionMappingService` (exact match, partial match, no-match).
7. Write unit tests for `DocxGenerator`, `PdfExporter`, and `MarkdownExporter` (using fixture template files).
8. Write unit tests for all four file processors (`DocxProcessor`, `PdfProcessor`, `MarkdownProcessor`, `TxtProcessor`).
9. Write a mock `MockAIProvider` and unit tests for the `ProviderFactory`.
10. Write integration tests for all API endpoint groups (auth, users, departments, templates, documents, sections, generation, export, reviews, admin), asserting status codes, response shapes, and DB state changes.
11. Write integration tests verifying RBAC enforcement on every protected endpoint (test with each role: Admin, Manager, Editor, Viewer, and unauthenticated).
12. Write integration tests for file upload validation: each disallowed MIME type must return 422.
13. Write integration test for mandatory section enforcement: `PUT .../skip` on a mandatory section returns 400.
14. Write integration test for template version immutability: attempt to change `template_version_id` on an existing document version returns an error.
15. Security — verify JWT: test that expired access tokens are rejected; test that refresh tokens cannot be used as access tokens; test that invalidated (logged-out) tokens are rejected.
16. Security — verify bcrypt: assert that stored password hashes use a minimum of 12 rounds.
17. Security — verify CORS: assert that requests from non-allowlisted origins receive a 400/403.
18. Security — verify file storage: assert that uploaded files are stored outside the web root and are not directly accessible via HTTP.
19. Implement token-bucket rate limiting (`slowapi` or equivalent) on `POST /auth/login`, `POST /documents/upload`, and `POST /documents/paste`; write tests asserting 429 on limit breach.

#### Frontend Tasks

1. Configure Vitest and React Testing Library; set up `msw` (Mock Service Worker) for API mocking.
2. Write component tests for: `LoginForm` (validation, submit, error display), `FileDropzone` (file type rejection, accepted file display), `SectionReviewCard` (status badge rendering, skip button disabled for mandatory sections).
3. Write integration tests for critical user flows using React Testing Library: login flow (submit → token stored → redirect to dashboard), upload flow (drop file → navigate to status page → poll until complete), section review flow (fill missing section → proceed button enables).

#### Infrastructure Tasks

1. Write a production multi-stage `Dockerfile` for the backend: builder stage (install dependencies), runtime stage (slim Python image, non-root user, no dev dependencies).
2. Write a production multi-stage `Dockerfile` for the frontend: builder stage (`npm run build`), runtime stage (`nginx:alpine` serving the `dist/` directory).
3. Write `docker-compose.prod.yml` with: production backend and frontend images, PostgreSQL with a persistent named volume, nginx reverse proxy with TLS termination stub, no source-code bind mounts.
4. Implement `GET /health` (liveness) and `GET /ready` (readiness, checks DB connectivity) endpoints on the backend.
5. Write `.env.example` with every required variable documented inline, including type, default value, and security notes.
6. Update `README.md` with: prerequisites, local dev setup, running tests, production deployment steps, environment variable reference, and architecture diagram (ASCII or Mermaid).

### Dependencies

- All Phases 1–5 must be complete.
- A CI pipeline (GitHub Actions or equivalent) is recommended to gate merges on the full test suite.

### Expected Deliverables

- Complete backend test suite (`pytest`) with ≥80% line coverage on service and API layers.
- Frontend test suite (`vitest`) covering login, upload, and section review flows.
- Production-ready Docker images for backend and frontend.
- `docker-compose.prod.yml` usable for a simple single-host production deployment.
- Security review checklist completed with all items passing.
- Updated `README.md` and a `DEPLOYMENT.md` guide.

### Acceptance Criteria

1. `pytest --cov=app --cov-report=term-missing` exits 0 with ≥80% coverage on service and API modules.
2. All RBAC enforcement integration tests pass for every endpoint and every role combination.
3. File upload integration test: at least five disallowed MIME types each return 422.
4. `PUT .../sections/{id}/skip` on a mandatory section returns 400 in the integration test.
5. Expired JWT access token returns 401; a logged-out refresh token returns 401.
6. `POST /auth/login` after 10 rapid attempts returns 429 (rate limited).
7. `npm run test` (Vitest) exits 0 with all component and integration tests passing.
8. `docker compose -f docker-compose.prod.yml up --build` starts all services without errors.
9. `GET /health` returns 200; `GET /ready` returns 200 when the database is reachable and 503 when it is not.
10. The production backend image runs as a non-root user (`whoami` inside the container is not `root`).

### Estimated Effort

**2–3 weeks** for a solo developer.

---

## Development Phase Summary

| Phase | Description | Key Deliverables | Est. Effort |
|-------|-------------|-----------------|-------------|
| 1 | Foundation + Auth + Templates | Working auth, full CRUD APIs, template management UI | 2–3 weeks |
| 2 | Upload + Extraction + AI | Document upload, file processors, AI integration | 2–3 weeks |
| 3 | Mapping + Missing Sections | Section mapping service, interactive review UI | 1–2 weeks |
| 4 | Generation + Export + Preview | DOCX/PDF/MD generation, preview, version history | 2–3 weeks |
| 5 | History + Reviews + Admin | Version compare, review workflow, admin dashboard | 2–3 weeks |
| 6 | Testing + Security + Docker | Full test suite, security hardening, production Docker | 2–3 weeks |

**Total estimated duration:** 11–17 weeks for a solo developer working full-time.

---

## Phase 1 Quick Start Checklist

1. Create the top-level monorepo directory structure: `backend/`, `frontend/`, `docker/`, `docs/`.
2. Create the `frontend/` project by running `npm create vite@latest frontend -- --template react-ts` from the project root.
3. Create the `backend/` project: initialise a Python virtual environment (`python -m venv .venv`), install FastAPI, Uvicorn, SQLAlchemy, Alembic, Pydantic, asyncpg, python-jose, passlib, and pytest.
4. Create `docker-compose.yml` at the project root defining `backend`, `frontend`, `db` (postgres:16), and `nginx` services.
5. Create `backend/.env.example` and `frontend/.env.example` documenting all required environment variables.
6. Create the FastAPI application package structure inside `backend/app/`: `__init__.py`, `main.py`, `core/`, `api/`, `services/`, `models/`, `schemas/`, `db/`.
7. Configure `app/core/config.py` using Pydantic `BaseSettings` to load `DATABASE_URL`, `SECRET_KEY`, `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`, and `CORS_ORIGINS` from the environment.
8. Configure SQLAlchemy async engine in `app/db/session.py` using `create_async_engine` with the `DATABASE_URL` setting.
9. Implement the 14 SQLAlchemy ORM model files in `app/models/`, establishing all relationships and constraints.
10. Initialise Alembic (`alembic init alembic`), configure `env.py` to import all models and use the async engine, then generate and apply the initial migration (`alembic revision --autogenerate -m "initial schema"` → `alembic upgrade head`).
11. Write the database seeder (`app/db/seed.py`) to insert system roles (Admin, Manager, Editor, Viewer) and run it via a CLI command or startup hook.
12. Implement JWT auth endpoints in `app/api/v1/auth.py` (`/login`, `/refresh`, `/logout`, `/change-password`) using `python-jose` and `passlib`.
13. Implement the RBAC dependency (`app/core/security.py`) as a FastAPI `Depends` callable that validates the token and checks the user's role against an allowed-roles list.
14. Implement the users, departments, templates, template versions, and template sections CRUD routers in `app/api/v1/`, registering them on the FastAPI app in `main.py`.
15. Configure Tailwind CSS and shadcn/ui in the `frontend/` project, set up React Router with the root layout and `/login` route, and implement the Axios instance with token-refresh interceptors.
