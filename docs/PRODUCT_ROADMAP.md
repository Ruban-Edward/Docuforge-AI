# DocuForge AI — Product Roadmap

## Purpose

This roadmap turns the product idea into a sequence of small, verifiable steps. It is the product-focused companion to the existing technical planning documents. It does not mark existing work as complete, authorize Phase 2 work, or replace the requirements, architecture, database schema, API specification, or development plan.

## Product goal

Help an employee turn rough notes or an existing document into a consistent organisation-approved document:

1. The user selects a document type and provides content by pasting text or uploading a supported file.
2. The system compares the content with the selected, versioned template.
3. The system proposes content under the template's headings and clearly identifies sections it could not fill from the source.
4. The user supplies missing information or skips sections that policy allows them to skip.
5. The user reviews the result and exports a standardised document.

The system must preserve the user's meaning. AI may organise and rewrite supplied information, but must not invent facts. Users must be able to review and correct the result before export.

## Assessment of the current direction

### Keep

- **Python and FastAPI:** a good fit for a developer who already knows Python and for document processing and LLM integration.
- **React, TypeScript, and Vite:** suitable for the interactive template editor and guided document-completion workflow.
- **PostgreSQL, SQLAlchemy, and Alembic:** a sensible foundation for users, templates, template versions, sections, and audit history.
- **Docker Compose:** makes the application and PostgreSQL reproducible without requiring PostgreSQL to be installed on a developer's machine.
- **The existing foundation:** authentication/RBAC, departments, templates and versions, template sections, and the initial database schema are useful prerequisites. Extend these rather than rebuilding them.

### Adjust the development sequence

The existing plan puts extensive administration and infrastructure work ahead of demonstrating the main user value. Keep the existing work, but make the next milestones deliver a thin, end-to-end documentation workflow as early as practical. Admin features are useful only insofar as they enable that workflow.

The repository already has a backend, a frontend shell, Docker configuration, and planning documents. This is a foundation, not evidence that the full product workflow or Phase 1 acceptance criteria have been completed. Verify each feature against its acceptance criteria before describing it as done.

### Product and design decisions to make before external AI integration

- Which document types should the first pilot support (for example, task completion notes, an implementation report, or a runbook)?
- What are the exact required, optional, and conditionally required headings for the first approved template?
- Who may skip each heading, and should skipping require a reason?
- Which file types and maximum sizes are needed for the pilot?
- May organisation content be sent to a third-party AI provider? Which provider, region, retention terms, and data-processing agreement are approved?
- Who owns template approval and version changes?
- Which output format is required first: Markdown, DOCX, or both?

Do not send real organisation documents to an external AI service until the organisation has approved the provider and data-handling terms. Use synthetic or sanitised examples during development.

## Step-by-step implementation plan

Work on one step at a time. At the end of each step, run its tests, update `DEVELOPMENT_PROGRESS.md`, and review the result before starting the next step.

### Step 0 — Confirm the first real workflow

**Goal:** Make the product requirements concrete before adding more implementation.

**Work**

- Select one document type for the pilot.
- Collect a small set of synthetic or approved example inputs and the organisation's corresponding ideal documents.
- Agree on the template headings and mark each as required, optional, or conditionally required.
- Define skip rules, including who is allowed to skip a section and what the final document should show when one is skipped.
- Choose the first input method and export format.
- Record privacy, retention, access, and AI-provider constraints.

**Deliverable:** An approved pilot template and a short set of representative input/output examples.

**Acceptance:** A developer and a representative user agree what a correct result looks like, including how missing information and skips are handled.

### Step 1 — Verify and stabilise the existing foundation

**Goal:** Make the existing application a reliable base without expanding its scope.

**Work**

- Run the existing backend tests, frontend build, migration checks, and Docker health checks; record exact commands and results.
- Review current auth, authorization, seed behavior, template-version immutability, section ordering, and API error handling.
- Fix only defects that block the pilot workflow or create a material security/reliability risk.
- Replace development-only credentials and secret defaults with clearly documented environment configuration before any shared or production deployment.
- Confirm that template versions and their sections can be reliably created, edited while draft, published, and read back.

**Deliverable:** A verified development environment and a stable template-management API.

**Acceptance:** A clean Docker-based development setup starts, migrations apply, tests pass, and a published template version cannot be modified.

### Step 2 — Finalise the first template model and editor

**Goal:** Administrators can configure the structure against which content will be standardised.

**Work**

- Agree on the section fields needed for the pilot: title/key, order, content type, requiredness, skip/Not Applicable policy, and validation rules.
- Build and test the template and section editor against the live API, including persistent reordering.
- Define whether “Not Applicable” differs from “skipped” and how each appears in output.
- Pin each document workflow to a specific published template version so later template edits do not silently change work in progress or historical output.

**Deliverable:** One published, versioned pilot template maintained through the UI.

**Acceptance:** The configured template survives reload, and changing a draft does not change a published or previously selected version.

### Step 3 — Accept user content safely

**Goal:** A user can start a document using pasted content; upload can follow once the paste workflow is proven.

**Work**

- Implement document creation against a selected published template version.
- Store the original submitted text separately from any transformed content.
- Add upload only for the agreed first file types, with size/type validation and safe storage.
- Extract plain text from uploaded files while retaining useful source metadata (such as filename and page/paragraph references where available).
- Enforce access controls, retention policy, and safe handling of uploaded files.

**Deliverable:** A document record containing the original source and its selected template version.

**Acceptance:** Pasted text works end-to-end. If upload is in the pilot, valid files are extracted and invalid/oversized files are rejected with actionable errors.

### Step 4 — Map content to template sections

**Goal:** Produce a reviewable draft, with gaps explicit and no unsupported facts.

**Work**

- Define a typed structured result for section content, status, and source evidence; validate it server-side.
- First establish a deterministic baseline for simple headings and clearly labelled text. Use an LLM only for cases where semantic mapping is needed.
- If an LLM is approved, put it behind a small provider interface and send only the minimum necessary text.
- Instruct the model to return “not found” rather than guess. Preserve source evidence or references so users can verify where proposed content came from.
- Treat submitted documents as untrusted data, not as instructions to the model.
- Record model/provider, template version, processing status, and relevant usage metadata without logging sensitive source text unnecessarily.
- Build an evaluation set from the approved examples and measure section-level correctness, unsupported-content rate, and gap-detection quality before relying on model output.

**Deliverable:** A structured draft with filled, uncertain, and missing sections represented distinctly.

**Acceptance:** Results validate against the schema; missing content stays missing; reviewers can trace and correct proposed content. The evaluation set meets agreed thresholds before pilot use.

### Step 5 — Resolve missing sections with the user

**Goal:** The user can complete or explicitly skip gaps according to template policy.

**Work**

- Show each section, proposed content, evidence where available, and a clear state (filled, needs review, missing, skipped, or Not Applicable).
- Let the user edit or supply content for missing sections.
- Enforce requiredness and skip permissions on the backend, not only in the UI.
- Ask for a reason when required by the agreed policy and retain the response in document history.
- Save progress so the user can safely leave and resume.

**Deliverable:** A completed, validated document draft ready for final review.

**Acceptance:** Required sections cannot be silently omitted; permitted skips are explicit; saved responses persist after reload.

### Step 6 — Review and export the standard document

**Goal:** Produce the first useful, organisation-standard output.

**Work**

- Add a final preview showing the template structure and the user's resolved content.
- Implement the first agreed export format (prefer the format the organisation already reviews and stores).
- Preserve the selected template version and record the output version and creation time.
- Keep formatting generation separate from AI mapping so either can be tested independently.

**Deliverable:** A user-reviewed document exported in the first agreed format.

**Acceptance:** Output headings/order match the selected template, content is preserved, and status markers for approved skips/Not Applicable sections follow policy.

### Step 7 — Pilot, harden, and expand

**Goal:** Establish that the workflow is safe and useful before adding more formats or document types.

**Work**

- Run an end-to-end pilot with representative users and approved data.
- Review access control, audit trail, data retention/deletion, file handling, AI provider terms, cost/latency, and failure recovery.
- Track user corrections and common failure patterns; improve templates, deterministic rules, prompts, and evaluations accordingly.
- Add further document types and export formats one at a time, each with its own examples and acceptance criteria.

**Deliverable:** A pilot report and an agreed next iteration.

**Acceptance:** Stakeholders approve the quality, privacy, and operational behavior for the pilot before broader use.

## What to learn as you build

You do not need to become an AI researcher or train a model for this product. Build the ordinary application workflow first, then learn the AI concepts needed for controlled information mapping.

| Topic | What is useful for this project |
|---|---|
| HTTP and API design | Requests, responses, status codes, validation, authentication, and error handling |
| SQL and data modelling | Foreign keys, transactions, indexes, migrations, and versioned records |
| Async Python and FastAPI | Dependency injection, async database sessions, background work when genuinely needed, and testing |
| React and TypeScript | Forms, routes, application state, API calls, loading/error states, and accessible review screens |
| Document formats | Text extraction limitations for DOCX/PDF and the difference between extracting content and preserving layout |
| LLM structured output | Schemas, constrained output, prompt boundaries, uncertainty, source evidence, token/cost limits, and provider error handling |
| AI evaluation | Representative examples, human review, section-level measures, unsupported claims, and regression testing |
| Application security | Authentication/authorization, secret management, input/file validation, privacy, retention, and auditability |
| Docker and PostgreSQL | Reproducible services, health checks, persistent data, migrations, and backups |

## Recommended initial technology choices

- Keep the current FastAPI, Pydantic, SQLAlchemy, Alembic, PostgreSQL, React/TypeScript, and Docker Compose stack.
- Start with pasted text and one document type. Add file extraction after the basic mapping/review loop works.
- Keep business rules and section completeness checks in Python. Use AI for semantic organisation where deterministic rules are insufficient.
- Use a hosted LLM only after organisational approval. Do not start with model training, fine-tuning, a vector database, or a complex agent framework; none is required to prove this workflow.
- Make AI output a proposal that is validated and reviewed, not a document that is automatically trusted or published.
- Keep uploaded content private by default and avoid placing source text, secrets, or tokens in application logs.

## Scope boundary

The first useful product is not “AI that writes any document.” It is a controlled workflow for one approved document type, one approved template, and one input-to-review-to-export path. Expand only after that workflow is measurable and accepted.

Do not begin unrelated advanced features (such as autonomous agents, model training, broad integrations, or multi-tenant SaaS) before the pilot proves the core value.

## Relationship to existing documents

- `REQUIREMENTS.md` remains the detailed functional and non-functional requirements source.
- `ARCHITECTURE.md` remains the technical architecture source.
- `DATABASE_SCHEMA.md` and `API_SPECIFICATION.md` remain the schema/API references and should be reconciled with implementation as they evolve.
- `DEVELOPMENT_PLAN.md` contains the original phase breakdown; use this roadmap to prioritize the next product milestone and update that plan after the first workflow decisions are approved.
- `DEVELOPMENT_PROGRESS.md` should record actual implementation and verification only. Do not mark a feature complete because it appears in a plan or exists partially in the code.
