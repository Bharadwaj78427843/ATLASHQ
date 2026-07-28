# Atlas — AI Engineering Operating System

> **"Understand before generating. Reason before recommending. Teach before automating."**

---

## What Is Atlas?

Atlas is an **AI Engineering Operating System (AEOS)** — a persistent system that maintains a governed, evidence-linked model of a software project and uses that model through multi-role engineering reasoning to guide, generate, verify, teach, and remember engineering work across the full software lifecycle.

Atlas is **not** another chatbot. It is **not** another coding assistant. It is **not** another NotebookLM. Atlas is the place where intent, architecture, code, data, delivery, operations, and knowledge are understood **together**.

---

## Core Architecture

```
Atlas
├── Atlas Brain         — Persistent reasoning and memory substrate (Project Brain)
├── Atlas Studio        — Human-facing workspace across the full lifecycle
├── Atlas Agents        — Engineering Organization: 14 specialized reasoning roles
├── Atlas Runtime       — Sandboxed execution, verification, and deployment
├── Atlas Cloud         — Multi-tenant platform services (identity, integrations, billing)
└── Atlas Governance    — Cross-cutting policy, trust, audit, and compliance
```

---

## Repository Structure

```
atlas/
├── docs/               — All engineering documentation (architecture, sprints, ADRs, glossary)
├── prompts/            — System, agent, and template prompts
├── apps/               — User-facing applications (web, admin, desktop, mobile, docs)
├── services/           — Backend microservices
├── packages/           — Shared libraries and SDKs
├── agents/             — Agent role definitions and configurations
├── infrastructure/     — Docker, Kubernetes, Terraform, cloud configs
├── integrations/       — Connectors to external systems
├── data/               — Schemas, seeds, and sample data
├── tests/              — Unit, integration, E2E, performance, and security tests
├── scripts/            — Build, deployment, and utility scripts
├── tools/              — Developer tools and CLI
├── assets/             — Logos, icons, images, and presentations
└── experiments/        — Prototypes, research, and playground
```

---

## Getting Started

> **Documentation-first.** Atlas Version 1 is currently in the design phase. Engineering implementation follows the design.

1. Read the [Atlas Constitution](docs/00-company/ATLAS_CONSTITUTION.md) — the Company Bible
2. Read the [Product Vision](docs/01-product/PRODUCT_VISION.md) — what Atlas is building toward
3. Read the [Product Map](docs/01-product/PRODUCT_MAP.md) — how the product is structured
4. Review the [Sprint 1 Engineering Package](docs/03-sprints/Sprint-1/) — the current design work

---

## Design Principles

| Principle | Meaning |
|---|---|
| Ground before you generate | No artifact is produced without checking it against the Project Brain |
| Explain every consequential recommendation | An answer without reasoning is incomplete |
| Scale rigor to consequence | A config change and a payments migration are not the same ceremony |
| Prefer a surfaced gap to a plausible guess | When context is insufficient, ask — don't assume |
| Preserve reasoning as durably as code | A decision without rationale is technical debt |
| Automation earns its authority | Every autonomy expansion requires a verified track record |

---

## Mission

> Help every software team — from a solo founder to a global enterprise — understand what they are building, make better decisions, ship more reliable software, and never lose engineering knowledge again.

---

## Version

**Current:** Design Phase — Sprint 1  
**License:** See [LICENSE](LICENSE)  
**Contributing:** See [CONTRIBUTING.md](CONTRIBUTING.md)  
**Security:** See [SECURITY.md](SECURITY.md)