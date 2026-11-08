# DocuForge AI — Requirements Document

> **Document Status:** Draft v1.0  
> **Last Updated:** 2026-11-08  
> **Audience:** Engineering, Product, Stakeholders

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Business Problem](#2-business-problem)
3. [Objectives](#3-objectives)
4. [Functional Requirements](#4-functional-requirements)
5. [Non-Functional Requirements](#5-non-functional-requirements)
6. [User Roles](#6-user-roles)
7. [Business Rules](#7-business-rules)
8. [MVP Scope](#8-mvp-scope)
9. [Out of Scope (MVP)](#9-out-of-scope-mvp)
10. [Future Enhancements](#10-future-enhancements)
11. [Assumptions](#11-assumptions)
12. [Open Questions](#12-open-questions)

---

## 1. Project Overview

**DocuForge AI** is an AI-powered organisational documentation standardisation and generation platform. It is designed for software engineering teams and technical organisations that need to produce, maintain, and audit professional documentation consistently and efficiently.

The platform enables developers and technical authors to submit raw, unstructured technical content — either by pasting text directly or uploading source documents (DOCX, PDF, Markdown, or plain text) — and uses a large language model (LLM) to intelligently extract relevant information, map it to predefined organisational documentation templates, identify gaps in coverage, interactively prompt the user to fill those gaps, and finally render a polished, standards-compliant document that can be exported as DOCX, PDF, or Markdown.

### Core Value Proposition

| Pain Point | DocuForge AI Solution |
|---|---|
| Inconsistent documentation structure across teams | Enforces organisational templates with mandatory/optional section rules |
| Time wasted reformatting and restructuring docs | AI automatically maps content to the correct template headings |
| Missing sections discovered only after review cycles | Proactively identifies and prompts for missing information at generation time |
| No audit trail for documentation changes | Versioned document history with immutable original content preservation |
| Difficulty verifying compliance to standards | Templates are version-pinned; every document references its source template version |

### Technology Stack

| Layer | Technology |
|---|---|
| **Frontend** | React, TypeScript, Vite, Tailwind CSS, shadcn/ui |
| **Backend** | Python, FastAPI, Pydantic, SQLAlchemy, Alembic |
| **Database** | PostgreSQL |
| **AI / LLM** | External LLM API with structured JSON output mode |
| **Document Processing** | python-docx (DOCX generation), PyMuPDF (PDF reading/generation) |
| **Infrastructure** | Docker, Docker Compose |

---

## 2. Business Problem

### 2.1 Current State

Software development teams produce a wide variety of technical artefacts throughout the software lifecycle: architecture decision records, API specifications, runbooks, incident post-mortems, onboarding guides, project charters, and more. In the absence of a centralised documentation standard, the following problems are endemic:

1. **Inconsistent Structure and Style** — Every developer or team writes documentation in their own format. Some use Google Docs, some write Markdown in a repository, some submit Word documents. Even within the same team, documents covering the same type of artefact may bear no structural resemblance to one another.

2. **No Organisational Standard** — There is no single source of truth defining what a valid piece of organisational documentation looks like. Without a canonical template, there is nothing to validate against, making compliance checks impossible.

3. **Formatting and Reformatting Overhead** — When documentation is submitted for review or for archival, significant manual effort is expended by the author (or reviewer) to reformat it to match expectations. This is unproductive work that does not add informational value.

4. **Missing Information Discovered Late** — Critical sections (e.g., security considerations, rollback procedures, stakeholder sign-off) are frequently absent and are only identified during a formal review cycle, creating rework loops that delay delivery.

5. **Compliance and Auditability Challenges** — In regulated or audit-sensitive environments, proving that documentation was produced to a given standard at a given time is difficult when documents exist as scattered files with no version tracking.

6. **Knowledge Silos** — Institutional knowledge exists in informal notes, chat messages, emails, and meeting transcripts, but is never transformed into formal documentation, contributing to bus-factor risk.

### 2.2 Impact

The combined effect of the above is:

- Increased time-to-delivery due to documentation rework.
- Lower documentation quality and coverage over time.
- Elevated risk of non-compliance during audits.
- Higher onboarding friction for new team members who cannot rely on consistent documentation.
- Loss of institutional knowledge when team members leave.

---

## 3. Objectives

### 3.1 Primary Objectives

1. **Standardise Documentation** — Enforce organisational documentation templates across all teams and document types so that every generated document adheres to a defined structure.

2. **Reduce Manual Effort** — Minimise the time developers spend structuring, formatting, and reformatting documentation by automating information extraction and template mapping via AI.

3. **Eliminate Missing Section Errors** — Proactively identify sections required by a template that are not covered by the submitted content, and interactively collect the missing information from the user before document generation.

4. **Enable Auditability** — Maintain a complete, immutable record of every document submission, extraction, user prompt response, generated output, and version history so that the full lineage of any document can be reconstructed.

5. **Provide Template Governance** — Give administrators control over the definition, versioning, and lifecycle of documentation templates, so that standards can evolve without breaking historical records.

### 3.2 Secondary Objectives

6. **Accelerate Onboarding** — Reduce the learning curve for producing compliant documentation by guiding developers through the process interactively rather than expecting familiarity with standards up front.

7. **Support Multiple Export Formats** — Satisfy the diverse downstream consumption needs of documentation (editorial review in DOCX, archival in PDF, repository storage in Markdown).

8. **Provide Role-Based Access Control** — Ensure that the right people have the right level of access to documents, templates, and administrative functions.

9. **Track AI Usage** — Log AI consumption (tokens, model, latency) to support cost tracking, debugging, and future optimisation.

10. **Lay the Foundation for Advanced Features** — Design the architecture to support future capabilities such as team collaboration, approval workflows, and integration with third-party tools, without requiring a rewrite.

---

## 4. Functional Requirements

### 4.1 Authentication and Authorisation

| ID | Requirement |
|---|---|
| FR-AUTH-01 | The system MUST provide a registration flow for new users with email and password. |
| FR-AUTH-02 | The system MUST support email/password login and issue a JWT access token with a configurable expiry. |
| FR-AUTH-03 | The system MUST support JWT refresh tokens to maintain sessions without requiring repeated logins. |
| FR-AUTH-04 | The system MUST enforce role-based access control (RBAC) on all API endpoints and UI routes. |
| FR-AUTH-05 | The system MUST provide a secure password reset flow via email link. |
| FR-AUTH-06 | The system MUST lock an account after a configurable number of consecutive failed login attempts. |
| FR-AUTH-07 | All authenticated API requests MUST include the JWT in the `Authorization: Bearer` header. |

### 4.2 Document Input — Upload

| ID | Requirement |
|---|---|
| FR-UPLOAD-01 | Users MUST be able to upload source documents in DOCX, PDF, Markdown (`.md`), and plain text (`.txt`) formats. |
| FR-UPLOAD-02 | The system MUST enforce a configurable maximum file size limit per upload (default: 20 MB). |
| FR-UPLOAD-03 | The system MUST validate the MIME type and file extension of uploaded files and reject unsupported formats with a clear error message. |
| FR-UPLOAD-04 | Uploaded files MUST be stored securely server-side and must NOT be executed or interpreted as instructions. |
| FR-UPLOAD-05 | The system MUST preserve the original uploaded file in its unmodified form for the lifetime of the associated document record. |
| FR-UPLOAD-06 | Multiple source files SHOULD be supportable for a single document generation request (e.g., a spec file and a runbook combined). |

### 4.3 Document Input — Paste Content

| ID | Requirement |
|---|---|
| FR-PASTE-01 | Users MUST be able to paste raw unstructured text content directly into a text editor in the UI as an alternative to uploading a file. |
| FR-PASTE-02 | The paste editor MUST support plain text input with a configurable maximum character limit (default: 100,000 characters). |
| FR-PASTE-03 | The system MUST preserve the exact pasted content as the original submission for audit purposes. |
| FR-PASTE-04 | Pasted content MUST be treated as untrusted data and MUST NOT be used as instructions to the AI system (see Business Rules BR-07). |

### 4.4 Multi-Format Content Extraction

| ID | Requirement |
|---|---|
| FR-EXTRACT-01 | The system MUST extract plain text from DOCX files using `python-docx`, preserving paragraph structure. |
| FR-EXTRACT-02 | The system MUST extract plain text from PDF files using `PyMuPDF`, preserving page-level structure where possible. |
| FR-EXTRACT-03 | The system MUST handle Markdown files by stripping formatting syntax to yield clean text suitable for AI processing. |
| FR-EXTRACT-04 | The system MUST handle plain text files directly without transformation. |
| FR-EXTRACT-05 | Extraction failures (e.g., password-protected PDFs, corrupted files) MUST result in a user-visible error message and no processing of the file. |
| FR-EXTRACT-06 | Extracted text MUST be logged alongside the submission record for auditability. |

### 4.5 AI-Based Information Extraction

| ID | Requirement |
|---|---|
| FR-AI-01 | The system MUST send extracted content to an LLM API with structured JSON output mode enabled, requesting extraction of information relevant to the headings of the selected template. |
| FR-AI-02 | The LLM prompt MUST include the template heading definitions and any heading-level instructions as context. |
| FR-AI-03 | The LLM MUST be instructed, in the system prompt, to extract information only from the provided content and to respond with `null` for any section for which no relevant content exists. |
| FR-AI-04 | The system MUST NOT instruct the LLM to generate, invent, or assume information that is not present in the submitted content. |
| FR-AI-05 | The structured JSON response from the LLM MUST be validated against a Pydantic schema before any further processing occurs. |
| FR-AI-06 | AI extraction failures (invalid JSON, schema validation error, API timeout) MUST be caught, logged, and surfaced to the user with a friendly error message. |
| FR-AI-07 | The system MUST log the LLM model used, prompt token count, completion token count, and latency for every AI call. |
| FR-AI-08 | The system MUST support configuration of the LLM API base URL, model name, and API key via environment variables, without code changes. |

### 4.6 Template Heading Mapping

| ID | Requirement |
|---|---|
| FR-MAP-01 | After AI extraction, the system MUST map each extracted value to the corresponding template heading using the structured JSON response keys. |
| FR-MAP-02 | Sections where the LLM returned `null` MUST be flagged as "not found in source content". |
| FR-MAP-03 | The mapping result MUST distinguish between: (a) content successfully extracted, (b) mandatory section with no extracted content, and (c) optional section with no extracted content. |
| FR-MAP-04 | The mapping result MUST be persisted to the database before the user prompt phase begins. |

### 4.7 Mandatory and Optional Section Rules

| ID | Requirement |
|---|---|
| FR-SECTION-01 | Each template heading MUST be marked as either `mandatory` or `optional` by the template author. |
| FR-SECTION-02 | The system MUST prevent document generation if any mandatory section has no content (extracted or user-provided). |
| FR-SECTION-03 | For optional sections with no extracted content, the system MUST ask the user whether they wish to skip the section or provide content manually. |
| FR-SECTION-04 | Skipping an optional section MUST be an explicit user action recorded in the submission log. |

### 4.8 Missing Section Identification and Interactive Prompting

| ID | Requirement |
|---|---|
| FR-PROMPT-01 | After extraction and mapping, the system MUST present the user with an interactive review screen listing all sections, their extracted content (or empty state), and their mandatory/optional status. |
| FR-PROMPT-02 | For each section with no extracted content, the system MUST display a prompt asking the user to provide the missing information or confirm skipping (for optional sections). |
| FR-PROMPT-03 | The user MUST be able to edit any AI-extracted content before proceeding to document generation. |
| FR-PROMPT-04 | The interactive prompting interface MUST clearly indicate which sections are mandatory (and therefore cannot be skipped). |
| FR-PROMPT-05 | User-provided or user-edited content MUST be stored separately from AI-extracted content in the submission record so the provenance of each section's content is traceable. |
| FR-PROMPT-06 | The system MUST NOT proceed to document generation until all mandatory sections have content. |

### 4.9 Content Standardisation

| ID | Requirement |
|---|---|
| FR-STD-01 | The system MUST apply template-defined formatting rules (e.g., heading styles, terminology) consistently across all generated documents. |
| FR-STD-02 | The system SHOULD use the LLM to lightly rewrite extracted and user-provided content into a consistent, professional tone, governed by a style instruction defined in the template. |
| FR-STD-03 | Standardisation rewrites MUST be clearly distinguished from raw extraction in the audit log (i.e., the pre- and post-standardisation content must both be stored). |

### 4.10 Document Generation

| ID | Requirement |
|---|---|
| FR-GEN-01 | The system MUST generate output documents by populating a DOCX template file with the finalised section content using `python-docx`. |
| FR-GEN-02 | DOCX templates MUST use bookmark or placeholder markers (e.g., `{{SECTION_HEADING}}`) that the system replaces with section content. |
| FR-GEN-03 | Generated DOCX files MUST include a metadata footer or cover page referencing the document version and the template version used. |
| FR-GEN-04 | PDF export MUST be derived from the generated DOCX (or rendered independently using PyMuPDF). |
| FR-GEN-05 | Markdown export MUST render each section as a heading-and-body block conforming to the template heading hierarchy. |
| FR-GEN-06 | Document generation MUST be an asynchronous background operation with a status indicator in the UI. |
| FR-GEN-07 | Generated documents MUST be stored server-side and accessible for download at any time within their version history. |

### 4.11 Preview and In-Browser Editing

| ID | Requirement |
|---|---|
| FR-PREVIEW-01 | The system MUST provide an in-browser preview of the generated document before final export, rendering section headings and content in a styled, readable format. |
| FR-PREVIEW-02 | Users MUST be able to make inline edits to any section in the preview and trigger a document re-generation (which creates a new version — it does NOT overwrite the existing version). |
| FR-PREVIEW-03 | The preview MUST visually differentiate sections populated by AI extraction, sections populated by user input, and sections that were skipped. |

### 4.12 Export

| ID | Requirement |
|---|---|
| FR-EXPORT-01 | Users MUST be able to download the generated document in DOCX format. |
| FR-EXPORT-02 | Users MUST be able to download the generated document in PDF format. |
| FR-EXPORT-03 | Users MUST be able to download the generated document in Markdown format. |
| FR-EXPORT-04 | Export operations MUST be logged with the user identity, timestamp, and format. |

### 4.13 Document History and Versioning

| ID | Requirement |
|---|---|
| FR-VERSION-01 | The system MUST maintain a full version history for every document, where each version is an immutable snapshot. |
| FR-VERSION-02 | Each version MUST record: version number, creation timestamp, the user who created it, the template version used, the original source content reference, and all section content (AI-extracted, user-provided, and final). |
| FR-VERSION-03 | Users MUST be able to view and download any previous version of a document. |
| FR-VERSION-04 | Re-generation of a document from edited content MUST always produce a new version number; existing versions MUST NOT be modified. |
| FR-VERSION-05 | The system MUST display a diff-style comparison between any two versions of the same document. |

### 4.14 Template Management

| ID | Requirement |
|---|---|
| FR-TMPL-01 | Authorised users (Admin and above) MUST be able to create new documentation templates through the UI. |
| FR-TMPL-02 | Each template MUST define: a name, description, document type category, one or more ordered sections with heading name, heading description, mandatory/optional flag, and optional style instructions. |
| FR-TMPL-03 | Authorised users MUST be able to edit existing templates (which creates a new template version — existing template versions are immutable once published). |
| FR-TMPL-04 | Authorised users MUST be able to archive (soft-delete) templates, preventing their use in new submissions while preserving historical records. |
| FR-TMPL-05 | Authorised users MUST be able to associate a DOCX template file with each template version for DOCX generation. |
| FR-TMPL-06 | Templates MUST be assignable to specific teams or organisation-wide. |
| FR-TMPL-07 | The system MUST display all available templates in a browsable, searchable library for users when starting a new document. |

### 4.15 Template Versioning

| ID | Requirement |
|---|---|
| FR-TMPLV-01 | Every published template MUST have an immutable version record once it has been used to generate at least one document. |
| FR-TMPLV-02 | Template edits MUST create a new draft version that must be explicitly published by an authorised user. |
| FR-TMPLV-03 | Documents MUST reference the specific template version used to generate them, and that reference MUST remain valid even if the template is later updated or archived. |
| FR-TMPLV-04 | The system MUST display the template version history in the template management UI. |

### 4.16 Role-Based Access Control

| ID | Requirement |
|---|---|
| FR-RBAC-01 | The system MUST enforce the four roles defined in Section 6 at the API level (not only the UI). |
| FR-RBAC-02 | Resource-level permissions MUST ensure that users can only view documents they own or that have been explicitly shared with them (unless they are an Admin or above). |
| FR-RBAC-03 | Template management (create, edit, publish, archive) MUST be restricted to Admin roles and above. |
| FR-RBAC-04 | User management (create, deactivate, change roles) MUST be restricted to Admin roles and above. |
| FR-RBAC-05 | Super Admin capabilities (system configuration, all data access) MUST be restricted to the Super Admin role. |

### 4.17 Admin Panel

| ID | Requirement |
|---|---|
| FR-ADMIN-01 | The system MUST provide an admin panel accessible only to Admin and Super Admin roles. |
| FR-ADMIN-02 | The admin panel MUST support user management: list users, invite users, deactivate users, change user roles. |
| FR-ADMIN-03 | The admin panel MUST provide system-level configuration options (e.g., max file size, session timeout, AI model selection). |
| FR-ADMIN-04 | The admin panel MUST display an overview of recent processing activity (submissions, generations, errors). |

### 4.18 Processing Logs

| ID | Requirement |
|---|---|
| FR-LOG-01 | The system MUST log every significant processing event: submission received, extraction started/completed/failed, AI call started/completed/failed, user prompt responses, generation started/completed/failed, export event. |
| FR-LOG-02 | Logs MUST be queryable by document ID, user ID, template ID, event type, and date range. |
| FR-LOG-03 | Logs MUST include a timestamp (UTC), actor (user or system), event type, and outcome (success/failure). |
| FR-LOG-04 | Logs MUST be retained for a minimum configurable period (default: 2 years). |
| FR-LOG-05 | Log records MUST be append-only; they MUST NOT be editable or deletable by any user including Super Admins (through the application). |

### 4.19 AI Usage Tracking

| ID | Requirement |
|---|---|
| FR-AITRACK-01 | Every LLM API call MUST be recorded with: document ID, submission ID, timestamp, model name, prompt token count, completion token count, total token count, latency (ms), and success/failure status. |
| FR-AITRACK-02 | The admin panel MUST display aggregate AI usage statistics: total tokens used (by period, by model, by user, by team). |
| FR-AITRACK-03 | The system MUST support configurable token usage alerts (e.g., notify Super Admin if daily usage exceeds a threshold). |

---

## 5. Non-Functional Requirements

### 5.1 Performance

| ID | Requirement |
|---|---|
| NFR-PERF-01 | The API MUST respond to non-AI-dependent requests (authentication, template retrieval, document history) within **500 ms** at p95 under normal load. |
| NFR-PERF-02 | AI extraction and document generation (asynchronous) MUST complete within **60 seconds** for documents up to 20 MB under normal load. |
| NFR-PERF-03 | The frontend initial load (LCP) MUST be under **3 seconds** on a standard broadband connection. |
| NFR-PERF-04 | The system MUST support at least **50 concurrent users** in the MVP without degradation beyond the above thresholds. |

### 5.2 Scalability

| ID | Requirement |
|---|---|
| NFR-SCALE-01 | The backend MUST be stateless (no in-memory session state) so that multiple instances can be run behind a load balancer. |
| NFR-SCALE-02 | Background processing (AI calls, document generation) MUST use an async task queue (e.g., Celery or FastAPI background tasks) to prevent blocking the API. |
| NFR-SCALE-03 | The database schema MUST be designed to support horizontal read scaling via read replicas without schema changes. |
| NFR-SCALE-04 | File storage MUST be abstracted behind a configurable storage interface to allow migration from local disk to object storage (e.g., S3-compatible) without code changes. |

### 5.3 Security

| ID | Requirement |
|---|---|
| NFR-SEC-01 | All data in transit MUST be encrypted using TLS 1.2 or higher. |
| NFR-SEC-02 | Passwords MUST be hashed using bcrypt with a minimum cost factor of 12. |
| NFR-SEC-03 | JWT secrets MUST be stored as environment variables and MUST NOT be committed to source control. |
| NFR-SEC-04 | Uploaded files MUST be stored outside the web root and served via signed URLs or authenticated endpoints — never at a guessable public URL. |
| NFR-SEC-05 | The system MUST implement input validation on all API endpoints; any request failing validation MUST be rejected with HTTP 422. |
| NFR-SEC-06 | The LLM prompt construction MUST separate the system instruction layer from the user-data layer to prevent prompt injection from document content. |
| NFR-SEC-07 | Database queries MUST use parameterised statements (enforced by SQLAlchemy ORM) to prevent SQL injection. |
| NFR-SEC-08 | CORS policy MUST be explicitly configured to allow only the application's own frontend origin. |
| NFR-SEC-09 | API rate limiting MUST be applied to all endpoints, with stricter limits on authentication and AI-triggering endpoints. |

### 5.4 Reliability

| ID | Requirement |
|---|---|
| NFR-REL-01 | The system MUST target **99.5% uptime** (excluding planned maintenance windows). |
| NFR-REL-02 | The system MUST gracefully handle LLM API unavailability: queue or retry failed AI requests and notify the user, rather than losing the submission. |
| NFR-REL-03 | The database MUST have automated daily backups with a minimum 30-day retention. |
| NFR-REL-04 | Health check endpoints MUST be available for liveness and readiness probes to support container orchestration. |

### 5.5 Maintainability

| ID | Requirement |
|---|---|
| NFR-MAINT-01 | Backend code MUST be organised following a clean layered architecture: routers → services → repositories → models. |
| NFR-MAINT-02 | All database schema changes MUST be managed through Alembic migrations; there MUST be no ad-hoc schema modifications. |
| NFR-MAINT-03 | Environment-specific configuration MUST be externalised to environment variables or a `.env` file; no configuration values MUST be hardcoded. |
| NFR-MAINT-04 | The codebase MUST have a minimum of 70% unit test coverage on backend service and business logic layers. |
| NFR-MAINT-05 | API contracts MUST be documented via auto-generated OpenAPI/Swagger docs available at `/docs` in development and staging environments. |
| NFR-MAINT-06 | Docker Compose MUST bring up the full development environment (backend, frontend, database) with a single `docker compose up` command. |

### 5.6 Auditability

| ID | Requirement |
|---|---|
| NFR-AUDIT-01 | Every state-changing operation MUST be recorded in the processing log with actor identity and timestamp. |
| NFR-AUDIT-02 | The original submitted content and every intermediate processing artefact (extracted text, AI JSON response, user edits, final content) MUST be stored and linked to the document version. |
| NFR-AUDIT-03 | It MUST be possible, given a document version ID, to fully reconstruct the exact processing steps, inputs, and outputs that produced it. |

### 5.7 Compliance Considerations

| ID | Requirement |
|---|---|
| NFR-COMP-01 | The system MUST support data residency configuration (storage location) to allow deployment in a jurisdiction-specific environment. |
| NFR-COMP-02 | The system MUST support user data deletion requests (right to erasure) at the application level, subject to audit log retention requirements. |
| NFR-COMP-03 | Sensitive configuration (API keys, DB credentials) MUST be managed as secrets and MUST NOT appear in application logs. |

---

## 6. User Roles

### 6.1 Role Overview

| Role | Description |
|---|---|
| **Super Admin** | Full system access including system configuration, all organisational data, and user management. Typically one or two people (platform owners / DevOps). |
| **Admin** | Manages templates, users (up to and including Manager level), and has visibility of all documents within their scope. |
| **Manager / Team Lead** | Can manage templates assigned to their team, view all documents within their team, and assign document tasks to Developers. |
| **Developer / Standard User** | Submits documents, views their own documents (and explicitly shared ones), and uses templates available to them. |

### 6.2 Role Permission Matrix

| Permission | Super Admin | Admin | Manager | Developer |
|---|:---:|:---:|:---:|:---:|
| Submit documents (upload / paste) | ✅ | ✅ | ✅ | ✅ |
| View own documents | ✅ | ✅ | ✅ | ✅ |
| Edit / re-generate own documents | ✅ | ✅ | ✅ | ✅ |
| Export documents (DOCX / PDF / MD) | ✅ | ✅ | ✅ | ✅ |
| View all documents (org-wide) | ✅ | ✅ | ❌ | ❌ |
| View all documents (team-scoped) | ✅ | ✅ | ✅ | ❌ |
| Create templates | ✅ | ✅ | ❌ | ❌ |
| Edit / publish templates | ✅ | ✅ | ❌ | ❌ |
| Archive templates | ✅ | ✅ | ❌ | ❌ |
| Manage team-scoped templates | ✅ | ✅ | ✅ | ❌ |
| View processing logs (own) | ✅ | ✅ | ✅ | ✅ |
| View processing logs (org-wide) | ✅ | ✅ | ❌ | ❌ |
| Invite users | ✅ | ✅ | ❌ | ❌ |
| Deactivate users | ✅ | ✅ | ❌ | ❌ |
| Change user roles (up to Admin) | ✅ | ✅ | ❌ | ❌ |
| Change user roles (Super Admin) | ✅ | ❌ | ❌ | ❌ |
| View AI usage statistics | ✅ | ✅ | ❌ | ❌ |
| System configuration | ✅ | ❌ | ❌ | ❌ |
| Access admin panel | ✅ | ✅ | ❌ | ❌ |

---

## 7. Business Rules

The following rules are non-negotiable constraints governing system behaviour. They must be respected in design, implementation, and testing.

| ID | Rule |
|---|---|
| **BR-01** | **Template headings are never hardcoded.** All section headings, their order, mandatory/optional status, and style instructions MUST be defined in the database via the template management system. No section structure may be embedded in application code. |
| **BR-02** | **AI must not fabricate information.** The LLM MUST be explicitly instructed, via system prompt, to return `null` for any section for which the submitted content provides no relevant information. The system MUST NOT accept or forward a non-null LLM response for a section unless the content can be traced to the submitted input. |
| **BR-03** | **Uploaded content is untrusted data, not instructions.** Document content submitted by users (uploaded files or pasted text) MUST be treated exclusively as data for extraction. It MUST be provided to the LLM as a user-data message (not as system-level instruction), and the system MUST implement prompt injection safeguards to prevent document content from influencing LLM behaviour beyond extraction. |
| **BR-04** | **Documents must reference the exact template version used.** Every generated document version MUST store the template version ID (not just the template ID). If the template is subsequently updated, the document record MUST still correctly reference the template version that was active at the time of generation. |
| **BR-05** | **Mandatory sections cannot be skipped.** If a template section is marked mandatory and no content has been provided (by AI extraction or by the user), the system MUST block document generation and prompt the user to provide the missing content. There is no override or bypass for this rule, even for Admin users. |
| **BR-06** | **Optional section skipping must be explicit and logged.** When a user chooses to skip an optional section that has no extracted content, that decision MUST be recorded as a named user action (with user ID and timestamp) in the submission log. It MUST NOT be inferred silently from an empty field. |
| **BR-07** | **AI output must be validated by Pydantic before use.** No LLM API response may be used in the processing pipeline without first passing validation against a Pydantic model that matches the expected structured output schema. Any response failing validation MUST be treated as an AI processing error. |
| **BR-08** | **Original submitted content must be preserved immutably.** The raw content submitted by the user (extracted text from upload or pasted text) MUST be stored in the database without modification for the full retention period. No processing step may alter or delete this record. |
| **BR-09** | **Document re-generation must produce a new version, never overwrite.** Any action that changes the content of a document (user edits, re-generation from updated content) MUST result in a new document version being created. No existing version record or its associated artefacts may be modified or deleted by the application. |
| **BR-10** | **Template versions are immutable once published.** Once a template version has been published and used to generate at least one document, its section definitions, mandatory/optional flags, and style instructions become immutable. Any change to a template MUST result in the creation of a new draft version that must be separately published. |
| **BR-11** | **Section content provenance must be traceable.** For every section of every document version, the system MUST record whether the content originated from (a) AI extraction, (b) user manual input, (c) user edit of AI-extracted content, or (d) a combination. This provenance label MUST be stored and viewable in the audit log. |
| **BR-12** | **No sensitive data in logs.** Processing logs and AI usage logs MUST NOT contain the full text of submitted documents, generated document content, LLM prompts, or LLM responses. Logs MUST reference these artefacts by ID only. The artefacts themselves are stored separately in the database. |
| **BR-13** | **API keys and secrets must not be logged.** LLM API keys, database credentials, JWT secrets, and any other secret values MUST NOT appear in any log output, error message, stack trace, or API response under any circumstances. |
| **BR-14** | **Template sections define the LLM extraction schema.** The JSON schema passed to the LLM for structured output MUST be derived programmatically from the active template's section definitions at the time of the AI call. The schema MUST NOT be maintained as a static file or string in the codebase. |
| **BR-15** | **Role assignment is controlled by role hierarchy.** A user may only assign a role to another user at a level strictly below their own. An Admin may assign roles up to and including Admin. Only a Super Admin may assign the Super Admin role. No user may change their own role. |
| **BR-16** | **File type validation must occur server-side.** Client-side file type checks (e.g., browser `accept` attribute) are a UX convenience only. The authoritative file type validation MUST occur on the backend by inspecting file content (magic bytes), not solely by trusting the file extension or the MIME type declared by the client. |
| **BR-17** | **Archived templates cannot be used for new submissions.** Once a template is archived, it MUST NOT be selectable for new document submissions. Documents previously generated against an archived template MUST continue to display correctly, referencing the archived template version. |
| **BR-18** | **Document generation is atomic.** A document generation job either completes fully (all sections populated, DOCX/PDF/Markdown files produced and stored, version record committed) or it fails entirely and the system reverts to the pre-generation state. Partial generation results MUST NOT be presented as a completed document. |
| **BR-19** | **AI usage is tracked per document version.** Every AI API call made as part of a document submission pipeline MUST be linked to the specific document submission and version record, allowing the full AI cost of producing any document version to be calculated. |
| **BR-20** | **Style rewrites are auditable.** If the AI performs a standardisation rewrite of section content (e.g., improving tone or phrasing), both the pre-rewrite content and the post-rewrite content MUST be stored. Users MUST be able to revert to the pre-rewrite version of any section. |

---

## 8. MVP Scope

The MVP delivers the core value proposition: a working end-to-end pipeline from content submission to standardised document generation, for a small set of templates and a single team.

### 8.1 Included in MVP

- [x] Email/password authentication with JWT (access + refresh tokens)
- [x] Single user role set: Super Admin + Developer (simplified RBAC; full 4-role RBAC is post-MVP)
- [x] Document submission via paste (plain text only in MVP)
- [x] Document submission via upload (DOCX and PDF; Markdown and TXT are post-MVP)
- [x] Text extraction from DOCX (python-docx) and PDF (PyMuPDF)
- [x] Template management UI: create, view, and publish templates with sections
- [x] LLM-based extraction using structured JSON output against a template
- [x] Pydantic validation of LLM responses
- [x] Interactive missing-section prompting UI
- [x] Mandatory section enforcement (block generation if mandatory sections are empty)
- [x] Optional section skip with confirmation
- [x] DOCX document generation using python-docx template population
- [x] PDF export (derived from DOCX)
- [x] Document version history (view and download past versions)
- [x] Processing log (per-document audit trail of events)
- [x] AI usage logging (model, tokens, latency per call)
- [x] Basic admin panel: user list, invite user, deactivate user
- [x] Docker Compose development environment

### 8.2 MVP Quality Bar

- Backend test coverage ≥ 70% on service and repository layers.
- All API endpoints documented via OpenAPI.
- Alembic migrations for all database schema changes.
- No hardcoded template data in application code.
- All Business Rules BR-01 through BR-20 enforced.

---

## 9. Out of Scope (MVP)

The following features are explicitly excluded from the MVP to maintain focus and delivery velocity. They are captured here to prevent scope creep and to signal that they are planned for later phases.

| Feature | Notes |
|---|---|
| Full 4-role RBAC (Manager role) | MVP uses Super Admin + Developer only |
| Markdown and plain text file upload | PDF and DOCX only in MVP |
| Multiple source files per submission | Single file or single paste per submission in MVP |
| In-browser document preview with WYSIWYG editing | Simple section-by-section form editing in MVP |
| Version diff comparison UI | Version history list and download only in MVP |
| Team / group management | No team assignment in MVP |
| Template assignment to teams | Templates are organisation-wide in MVP |
| Approval / sign-off workflow | No multi-step approval in MVP |
| Markdown export | DOCX and PDF only in MVP |
| AI-powered style standardisation rewrite | Extraction only; no tone rewriting in MVP |
| AI usage alerts and thresholds | Logging only in MVP; no alerting |
| Password reset via email | Manual reset by Super Admin in MVP |
| Account lockout after failed logins | Post-MVP |
| SSO / OAuth (Google, Microsoft) | Email/password only in MVP |
| Webhooks and third-party integrations | None in MVP |
| Analytics dashboard | Admin panel shows basic usage only in MVP |
| Multi-language support | English only in MVP |
| Object storage (S3/GCS) for file storage | Local disk storage in MVP (abstracted interface) |
| Read replica / horizontal DB scaling | Single database instance in MVP |

---

## 10. Future Enhancements

The following are longer-term roadmap items envisioned beyond the MVP. They are listed to inform architectural decisions made now (e.g., stateless API design, storage abstraction) that will make these features achievable without major rework.

### 10.1 Collaboration and Workflow

- **Multi-user document collaboration** — Allow multiple users to contribute to a document simultaneously or in a structured handoff model.
- **Approval and sign-off workflow** — Define configurable multi-step approval chains where named roles must review and digitally sign off on a document before it can be published or exported.
- **Document commenting and annotation** — Allow reviewers to leave inline comments on specific sections.
- **Task assignment** — Managers assign document creation tasks to Developers with due dates.

### 10.2 Integrations

- **Slack integration** — Send notifications to Slack channels on document completion, missed deadlines, or approval requests.
- **Jira integration** — Link document generation tasks to Jira tickets; auto-create Jira subtasks for missing documentation.
- **Confluence export** — Push generated documents directly to a Confluence space.
- **GitHub / GitLab** — Commit Markdown exports directly to a repository branch as part of a documentation-as-code workflow.
- **Webhook support** — Allow organisations to register webhook endpoints that receive events (document generated, version published, approval completed).

### 10.3 AI and Intelligence

- **AI confidence scoring** — Report a per-section confidence score indicating how well the extracted content matches the section intent.
- **Suggested similar documents** — Use vector similarity to recommend existing documents as reference material when a new submission is received.
- **Fine-tuning consideration** — Evaluate the feasibility of fine-tuning a model on organisation-specific documentation patterns (requires careful data governance).
- **Multi-LLM provider support** — Allow configuration of alternate LLM providers (e.g., Anthropic, Azure OpenAI, local Ollama instance) per template or organisation setting.
- **Retrieval-Augmented Generation (RAG)** — Allow templates to reference a knowledge base (e.g., existing approved documents) so the LLM can fill sections with more contextually accurate content.

### 10.4 Analytics and Reporting

- **Analytics dashboard** — Visual reports on documentation volume, template usage, average completion time, most frequently missing sections, AI cost trends.
- **Compliance report** — Exportable report listing all documents of a given type generated within a date range, their template version, and their current status.
- **Developer productivity metrics** — Track time-to-generate (from submission to completed document) per user/team.

### 10.5 Platform and Scale

- **Multi-language support** — UI localisation and AI extraction for non-English source documents.
- **Multi-tenancy** — Isolate data between multiple organisations on a single deployment (SaaS model).
- **Object storage migration** — Formal support for S3-compatible storage for files and generated documents.
- **Custom branding** — Allow organisations to configure logos, colour schemes, and document header/footer branding.
- **Mobile-responsive UI improvements** — Optimise the submission and review flow for use on tablets and mobile devices.
- **Scheduled document reviews** — Flag documents for periodic review (e.g., "this runbook is due for review in 90 days") and notify owners.

---

## 11. Assumptions

The following are assumed to be true for the purposes of this requirements document. If any assumption changes, the affected requirements should be revisited.

| ID | Assumption |
|---|---|
| **A-01** | A single AI/LLM provider will be used at MVP launch. The specific provider will be decided before development begins (see OQ-01). |
| **A-02** | The LLM provider supports a **structured JSON output mode** (function calling or response format constraint) that can be driven by a programmatically generated schema. |
| **A-03** | The platform will be deployed internally within the organisation's infrastructure (on-premises or private cloud) for MVP, not as a public SaaS offering. |
| **A-04** | All submitted content and generated documentation will be in **English** for the MVP. |
| **A-05** | Users will access the platform via a modern desktop web browser (Chrome, Firefox, Edge, Safari — latest two versions). No native mobile app is required for MVP. |
| **A-06** | The organisation has an existing email infrastructure (SMTP server or email relay) available for transactional emails (invitations, password resets in post-MVP). |
| **A-07** | The initial set of documentation templates will be authored by an Admin or Super Admin prior to onboarding Developers. The platform does not ship with pre-built templates. |
| **A-08** | A PostgreSQL instance (version 14 or higher) is available for deployment. |
| **A-09** | Docker and Docker Compose are available on the host machine used for development and deployment. |
| **A-10** | The LLM API is accessible from the backend service's network environment (no network proxy blocking required, or the proxy is pre-configured). |
| **A-11** | Document content submitted by users does not require end-to-end encryption at rest beyond the standard database and file system encryption provided by the deployment environment. (If this changes, field-level encryption may need to be added.) |
| **A-12** | DOCX template files for document generation will be authored externally (e.g., in Microsoft Word) and uploaded by an Admin. The platform does not include a DOCX template editor. |

---

## 12. Open Questions

The following items require a decision or input from stakeholders before or during implementation. Each item is assigned a priority to guide resolution order.

| ID | Question | Priority | Owner |
|---|---|---|---|
| **OQ-01** | Which LLM provider and model will be used? (e.g., OpenAI GPT-4o, Anthropic Claude 3.5, Google Gemini 1.5 Pro, Azure OpenAI). This affects the structured output schema design and API client implementation. | 🔴 High | Product / CTO |
| **OQ-02** | What are the **data residency requirements**? Must document content (uploaded files, generated documents) remain within a specific geographic region or jurisdiction? This affects cloud provider and storage region selection. | 🔴 High | Legal / Compliance |
| **OQ-03** | What is the **expected initial user count** and projected growth rate? This affects database sizing, task queue configuration, and LLM rate limit planning. | 🔴 High | Product |
| **OQ-04** | Should the LLM API key be **organisation-wide** (managed by the platform), or should individual users / teams provide their own API keys? The former is simpler; the latter supports cost allocation per team. | 🟡 Medium | Finance / Product |
| **OQ-05** | What **document types** will be supported at MVP launch? (e.g., architecture decision records, runbooks, incident post-mortems, project charters). This determines which templates need to be created before launch. | 🔴 High | Product / Tech Lead |
| **OQ-06** | Is there an **approval / sign-off workflow** required at MVP (e.g., a Manager must approve before a document is marked final)? This was excluded from MVP scope but should be confirmed. | 🟡 Medium | Product |
| **OQ-07** | What is the **document retention policy**? How long should submitted content, generated documents, and processing logs be retained? Are there regulatory requirements governing this? | 🟡 Medium | Legal / Compliance |
| **OQ-08** | Should the system support **SSO (Single Sign-On)** at MVP or is email/password sufficient for the initial launch period? (Affects auth complexity significantly.) | 🟡 Medium | IT / Security |
| **OQ-09** | Are there **branding assets** (logo, colour palette, typography) to be incorporated into the frontend UI and generated document headers/footers? | 🟢 Low | Design / Marketing |
| **OQ-10** | What is the **maximum expected document size** (in pages / words / MB) that users will typically submit? This informs LLM context window planning and chunking strategy for large documents. | 🟡 Medium | Tech Lead |
| **OQ-11** | Should the **DOCX template** that the system uses for generation be managed entirely by Admins, or should Managers also be able to upload DOCX template files for their team-specific templates? | 🟢 Low | Product |
| **OQ-12** | Is there a requirement to **watermark** generated documents (e.g., "DRAFT" or "CONFIDENTIAL") based on document status? | 🟢 Low | Product / Legal |
| **OQ-13** | What is the preferred **deployment environment** at MVP: bare-metal Docker Compose, managed Kubernetes (EKS/GKE/AKS), or a PaaS (e.g., Render, Railway, Fly.io)? This affects the infrastructure configuration included in the repository. | 🔴 High | DevOps / CTO |
| **OQ-14** | Is there an existing **identity provider or user directory** (e.g., Active Directory, Okta, Google Workspace) that the platform should eventually integrate with for user provisioning? | 🟡 Medium | IT |
| **OQ-15** | Should documents be shareable via a **public or authenticated link** (e.g., for external stakeholders who don't have a platform account)? | 🟢 Low | Product |

---

*End of Requirements Document — DocuForge AI v1.0*
