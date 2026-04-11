# Implementation Guide

How to apply the **Neural-Grid Framework** to your project.

## 1. Directory Structure

Adopt the "Standard Layout" to enforce separation of concerns.

```text
Project/
├── api/                  # [Contract] Protobufs / OpenAI Specs
├── cmd/                  # [Entrypoint] Main applications
├── docs/                 # [Documentation] Requirements, Plans, Wikis, Reports
│   ├── requirements/     # PRDs and feature specs
│   ├── plan/             # Phased implementation checklists
│   ├── wikis/            # Core architectural documentation
│   └── reports/          # Bug reports and implementation summaries
├── internal/             # [Private] Logic hidden from external import
│   ├── domain/           # [Core] Pure Business Logic (No deps)
│   └── infrastructure/   # [Infra] DB, HTTP, RPC implementations
├── tests/                # [Verification] E2E / BDD Tests
├── scripts/              # [Automation] Helper scripts
├── 3rdParty/          # [Dependencies] Git submodules for external repos
├── Makefile              # [Interface] The Command Center
├── docker-compose.yml    # [Environment] Infrastructure as Code
└── CLAUDE.md             # [AI] Custom instructions & agent workflows
```

## 2. Step-by-Step Adoption

### Step 1: The "AI Collaboration Foundation"

Copy `templates/CLAUDE.md` to your root.

- **Why**: Establishes the operational boundaries, tool constraints, and context for agentic AIs (like Claude Code) before development starts.
- **Action**: Replace the placeholders inside the file based on your specific project requirements:
  - `<DOMAIN_EXPERT>`: e.g., "Web3 Security Expert" or "React Frontend Specialist".
  - `<TECH_STACK>`: Keep an up-to-date list of your project's core technologies.
- **Directory synergy**: Remember to store your Project Requirements in `docs/requirements/` and stage plans in `docs/plan/` so the Agent can correctly parse them.

### Step 2: The "Law"

Copy `templates/CONTRIBUTING.md` to your root.

- **Why**: Sets the expectations for the team immediately.
- **Action**: Edit the specific language/tool names but keep the *Principles* intact.

### Step 3: The "Interface"

Copy `templates/Makefile` to your root.

- **Why**: Unifies how everyone interacts with the project.
- **Action**: Fill in the `init`, `test`, `lint` commands for your specific stack (Go, Python, TypeScript).

### Step 4: The "Gatekeeper"

Copy `templates/.pre-commit-config.yaml` to your root.

- **Why**: Prevents bad code from entering Git.
- **Action**: Run `make init` (which should run `pre-commit install`).

### Step 5: The "Architecture"

Refactor one module to follow strict DDD.

1. Move logic to `internal/domain`.
2. Remove **ALL** imports in `domain` that point to databases or HTTP frameworks.
3. Define interfaces in `domain` for what it needs (e.g., `UserRepository`).
4. Implement those interfaces in `internal/infrastructure`.

## 3. The "Golden Path" Workflow

Enforce this loop for every feature:

1. **Contract**: Change API definition first.
2. **Generate**: Run `make proto` / `make gen`.
3. **Test**: Write a failing test.
4. **Code**: Implement logic.
5. **Verify**: Run `make verify`.
