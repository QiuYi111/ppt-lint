# Contributing to {Project Name}

> **"Pragmatic > Dogmatic. Automation > Manual. Consensus > Command."**

Welcome to the team. This document is not a suggestion; it is the **Law** of this repository. We rely on strict process enforcement to maintain velocity and quality.

## 1. Core Principles

1.  **Environment as Code**: "It works on my machine" is an invalid defense. If it doesn't work in Docker/CI, it doesn't work.
2.  **Contract First**: No backend code is written until the API definition (Protobuf/OpenAPI) is reviewed and merged.
3.  **Strict DDD**:
    -   `internal/domain` depends on NOTHING.
    -   `internal/infrastructure` depends on `domain`.
4.  **TDD & BDD**:
    -   **Pure Logic?** TDD. Write `thing_test.go` before `thing.go`.
    -   **Feature Flow?** BDD. Write Integration Tests before wiring `main.go`.
5.  **Observability**: No `print` statements. Use structured logs with searchable keys.
6.  **AI-First Collaboration**: We leverage AI agents (e.g., Claude Code) governed by `CLAUDE.md`. Humans define the architecture and requirements, Agents assist in the execution. Always ensure AI context is up-to-date.

---

## 2. Development Interface

We do not memorize commands. We use `make`.

| Command | Purpose |
| :--- | :--- |
| `make init` | **Start Here**. Installs tools and hooks. |
| `make up` | Starts the *entire* infrastructure in Docker. |
| `make down` | Tears down infrastructure and cleans volumes. |
| `make proto` | **Generates** code from contracts. |
| `make test` | Runs Unit + Integration tests. |
| `make lint` | Runs linters and static checks. |
| `make verify` | **The Gatekeeper**. Runs everything. Run this before push. |

---

## 3. The Workflow (The "Golden Path")

When you pick up a ticket, follow this **exact** sequence:

### Phase 0: AI Context Assembly
1.  **Sync Framework**: Ensure `CLAUDE.md` is correctly configured in your project root.
2.  **Generate Index**: Run `/sc:index-repo` (or equivalent) so the AI has the latest `project_index`.
3.  **Feed Requirements**: Provide the Agent with the relevant `docs/requirements/` and `docs/plan/` files.

### Phase 1: Contract
1.  **Modify Contract**: Edit API definition.
2.  **Gen**: Run `make proto`.
3.  **Commit**: "feat(api): add new endpoint".

### Phase 2: Domain (TDD)
1.  **Define**: Create/Update `internal/domain/entity.go`.
2.  **Test**: Create `internal/domain/entity_test.go`.
3.  **Cycle**: Red -> Green -> Refactor.
    -   *Constraint*: Domain code **cannot** import `infrastructure` or external libs.

### Phase 3: Infrastructure (BDD)
1.  **Implement**: Write `internal/infrastructure/handler.go`.
2.  **Verify**: Write integration test.
    -   *Requirement*: Test **must** hit the real database in Docker.

### Phase 4: Submission
1.  **Local Gate**: Run `make verify`.
2.  **Commit**: Conventional Commits (e.g., `feat(user): implement login`).
3.  **Push**: CI will run `make verify` again.

---

## 4. Coding Standards

-   **Formatting**: Enforced via hook.
-   **Linting**: Zero-tolerance policy.
-   **Errors**: Return semantic errors, not generic strings.
