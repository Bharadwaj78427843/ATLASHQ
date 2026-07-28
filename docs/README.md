# Atlas Documentation

Welcome to the Atlas engineering documentation. This directory is the canonical home for all engineering knowledge about Atlas.

---

## Directory Structure

| Directory | Contents |
|---|---|
| [`00-company/`](00-company/) | Company Bible, Constitution, founding principles |
| [`01-product/`](01-product/) | Product Vision, Product Map, strategy, and capability model |
| [`02-research/`](02-research/) | Engineering research reports (AERR series) |
| [`03-sprints/`](03-sprints/) | Sprint-by-sprint engineering packages (Sprint 0, 1, 2...) |
| [`04-architecture-decision-records/`](04-architecture-decision-records/) | All architectural decisions with rationale |
| [`05-glossary/`](05-glossary/) | Canonical terminology, domain model, engineering lexicon |
| [`diagrams/`](diagrams/) | Architecture diagrams, flowcharts, and visual references |

---

## Source of Truth

Three documents are the immutable source of truth for all downstream engineering work:

1. **[ATLAS_CONSTITUTION.md](00-company/ATLAS_CONSTITUTION.md)** — The Company Bible
2. **[PRODUCT_VISION.md](01-product/PRODUCT_VISION.md)** — What Atlas is building toward
3. **[PRODUCT_MAP.md](01-product/PRODUCT_MAP.md)** — How the product is structured

> [!IMPORTANT]
> Every engineering decision, feature requirement, and architectural choice must be traceable back to one of these three documents. No downstream document may contradict them.

---

## Documentation Principles

1. **Evidence-first** — Claims cite sources; uncertainty is explicit
2. **Living documents** — Updated as the project evolves; stale knowledge is flagged
3. **Decision-recording** — Every significant choice is recorded with rationale and alternatives
4. **Version-controlled** — All changes tracked via Git with meaningful commit messages
