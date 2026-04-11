# Manifesto

> "Pragmatic > Dogmatic. Automation > Manual. Consensus > Command."

This framework is not just a collection of tools; it is a **discipline**. It is distilled from high-performance engineering teams to solve the problem of "Chaos in Growth."

## 1. The Core Philosophy

### 1.1 Environment as Code

"It works on my machine" is an invalid defense. It is not an explanation; it is a confession of failure.

- **The Law:** If it requires more than `make init` to start developing, it is broken.
- **The Tool:** Docker Compose & Dev Containers are not optional.

### 1.2 Contract First (Schema-Driven)

We do not write code to "see if it works." We agree on the interface, then we fulfill the contract.

- **The Law:** No backend code is written until the API definition (Protobuf/OpenAPI) is reviewed and merged.
- **The Benefit:** Frontend and Backend work in parallel. Tests are generated from the contract.

### 1.3 Strict Isolation (Pragmatic DDD)

Code structure must prevent "Spaghetti Dependencies" by physical design, not just convention.

- **The Law:** `Domain` logic depends on **NOTHING**. It is pure, testable, and immortal.
- **The Law:** `Infrastructure` (Database, HTTP) depends on `Domain`. Never the other way around.

### 1.4 The "Golden Path" Workflow

Creativity belongs in the solution, not the process. The process should be boring and automatic.

1. **Define**: Update Contract (Proto/Swagger).
2. **Test**: Write the failure case (TDD/BDD).
3. **Implement**: Make it green.
4. **Verify**: Run the local gatekeeper.

## 2. The Quality Standards

### 2.1 Observability

Logs are for machines, not humans.

- **Banned:** `print`, `console.log`
- **Required:** Structured Logging (JSON) with searchable keys.

### 2.2 Testing

Coverage allows refactoring. Without tests, code is "Legacy" the moment it is written.

- **Unit Tests**: For pure domain logic (TDD).
- **Integration Tests**: For infrastructure wiring (BDD).

### 2.3 The Gatekeeper

The CI/CD pipeline is the ultimate authority.

- **Pre-commit**: Blocks low-level garbage (linting, formatting).
- **CI**: Blocks logical failures.
- **Rule**: If CI is red, the branch does not exist.
