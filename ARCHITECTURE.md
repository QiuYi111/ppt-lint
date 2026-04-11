# Architecture Guide: Pragmatic DDD

**Target**: Maintainable, testable software that doesn't drown in complexity.
**Principle**: Physical isolation is better than convention.

## The Three-Layer Standard

Do not use complex Hexagonal/Onion terminology if it confuses the team. Use this simple structure:

TODO: sync with guide

```text
Project/
├── api/                  # [Contract Layer]
│   └── proto/            # The source of truth for the outside world
│
├── cmd/                  # [Boot Layer]
│   └── server/main.go    # The ONLY place that knows how to wire everything
│
├── internal/             # [Private Code]
│   ├── domain/           # [Core Domain]
│   │   ├── entity.go     # Pure Business Logic
│   │   └── repo_iface.go # Interfaces for what domain needs (NOT implementation)
│   │
│   └── infrastructure/   # [Infrastructure & Adapter]
│       ├── persistence/  # Database implementations of repo_iface
│       └── rpc/          # gRPC/HTTP Handlers
```

## The Iron Rules of Dependency

1. **Domain is King**: `internal/domain` cannot import `infrastructure`, `cmd`, or third-party drivers (NO SQL, NO HTTP).
2. **Infrastructure Serves Domain**: `internal/infrastructure` imports `internal/domain`.
3. **Main Wires All**: `cmd/main.go` imports both `domain` and `infrastructure` to inject dependencies.

## Workflow Example

**Goal**: Add a "User Login" feature.

1. **Domain**: Define `User` struct in `domain/user.go`. Define `UserRepository` interface in `domain/user_repo.go`.
   - *Note*: No database code here. Just `Save(u User) error`.
2. **Infrastructure**: Implement `PostgresUserRepo` in `infrastructure/persistence/user_repo.go`.
   - *Note*: This file imports `gorm` or `sqlx` AND `domain`.
3. **Main**: In `cmd/main.go`:
   ```go
   repo := persistence.NewPostgresUserRepo(db) // Infra
   service := domain.NewUserService(repo)      // Domain
   server.Run(service)
   ```
