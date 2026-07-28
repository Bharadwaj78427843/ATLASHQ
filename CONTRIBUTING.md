# Contributing to Atlas

Thank you for your interest in contributing to Atlas — the AI Engineering Operating System.

---

## Before You Contribute

Read these documents first:

1. **[Atlas Constitution](docs/00-company/ATLAS_CONSTITUTION.md)** — the Company Bible. Non-negotiable.
2. **[Product Vision](docs/01-product/PRODUCT_VISION.md)** — what we are building toward.
3. **[Product Map](docs/01-product/PRODUCT_MAP.md)** — how the product is structured.
4. **[Engineering Standards](docs/03-sprints/Sprint-1/13-engineering-standards/README.md)** — how we write code.

---

## Design-First Principle

> **No code without a design. No design without a decision. No decision without evidence.**

Atlas follows the `Understand → Reason → Design → Validate → Document → Implement` sequence.

Before writing a single line of implementation code:

1. Understand which **Platform** and **Module** owns the capability (Product Map §11.2 Decision Tree)
2. Create or reference an **Architecture Decision Record** (ADR) in `docs/04-architecture-decision-records/`
3. Update the relevant **Sprint document** in `docs/03-sprints/`
4. Get the design reviewed before opening a PR

---

## Development Workflow

### 1. Find or Create an Issue

All work starts with a GitHub issue. Use the appropriate template in `.github/ISSUE_TEMPLATE/`.

### 2. Branch Naming

```
feat/<platform>/<short-description>
fix/<platform>/<short-description>
design/<document-name>
docs/<section>/<short-description>
```

Examples:
- `feat/brain/knowledge-graph-ingestion`
- `fix/agents/orchestrator-timeout`
- `design/database-schema-v1`
- `docs/sprint-1/system-architecture`

### 3. Commit Message Format

Atlas uses [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

Types: `feat`, `fix`, `docs`, `design`, `refactor`, `test`, `chore`

Scopes match platform or package names: `brain`, `studio`, `agents`, `runtime`, `cloud`, `governance`

### 4. Pull Request Requirements

Before opening a PR, verify:

- [ ] All acceptance criteria from the relevant PRD section are met
- [ ] Tests written and passing (unit, integration where applicable)
- [ ] Security Engineer review completed if touching trust-sensitive paths
- [ ] Documentation updated (Documentation Hub entry or README)
- [ ] Audit Trail impact documented
- [ ] No secrets or credentials committed
- [ ] `.editorconfig` standards followed

### 5. Code Review

Every PR requires review from:
- At least **one member** of the owning platform team
- The **Security Engineer role** for any auth, data access, or agent permission changes
- The **Principal Architect** for any changes to inter-platform contracts

---

## Key Constraints

| Constraint | Why |
|---|---|
| No direct production writes in V1 | All agents operate at Stage 1 (Advisory); all system effects require human approval |
| No plaintext secrets in the repository | Secrets are managed by the Secrets & Credentials Broker |
| All agent actions must be logged to the Audit Trail | Irrevocable audit record is required before any autonomy expansion |
| Every recommendation must cite a provenance source | Ungrounded generation is what Atlas exists to prevent |

---

## Code of Conduct

All contributors must follow our [Code of Conduct](CODE_OF_CONDUCT.md).

---

## Questions?

Open a GitHub Discussion. Do not DM maintainers directly.
