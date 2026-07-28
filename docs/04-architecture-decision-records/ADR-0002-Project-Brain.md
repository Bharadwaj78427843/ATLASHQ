# ADR-0002: Project Brain as Primary Architectural Object

**Status:** Accepted  
**Date:** 2026-07-28  
**Owner:** Principal Architect  
**Reviewers:** CTO, Distinguished Engineer, Principal Database Architect

---

## Context

Every AI engineering tool today is centered on the output artifact: a diff, a file, a chat message. This architecture produces stateless interactions — each session starts from scratch, ignoring prior decisions and accumulated knowledge. The result is repeated discovery, inconsistent decisions, and generated work that ignores prior constraints.

Atlas's core thesis is that judgment, not generation, is the bottleneck. This requires the system to be centered on the model of the project, not on the output.

## Decision

**Atlas Brain is the primary architectural object.** All platforms read from and write to it:
- Atlas Studio is a view over it
- Atlas Agents reason against it
- Atlas Runtime feeds outcomes back to it
- Atlas Cloud provides the infrastructure within which it operates
- Atlas Governance constrains what can be written to it and by whom

The Project Brain is a governed, temporal, evidence-backed model of the software project, composed of: Project Understanding, Context Engine, Knowledge Graph, Decision Graph, Engineering Memory, Institutional Memory, Relationship Engine, and Cognition Engine.

## Alternatives Considered

| Alternative | Rejection Rationale |
|---|---|
| Conversation-history-centered | Conversations do not model project structure or preserve rationale across sessions; linear not relational |
| File-index-centered (traditional RAG) | No typed relationships; no decision provenance; no temporal model; treats chunks as independent |
| Code-AST-centered | Code is one artifact; Atlas must reason across requirements, data, operations, and organizational context |

## Trade-offs Accepted

- Project Brain construction takes engineering effort; V1 is not instantly useful from day one
- Brain schema changes are migrations, not refactors — they must be planned carefully
- Complexity in retrieval: multiple access methods (graph, vector, temporal) rather than one

## Consequences

- The canonical data model for Atlas is a property graph, not a document store or relational schema
- All agent recommendations must be grounded in Brain evidence
- Studio writes to Brain only through the Memory Interface; never direct

## Reconsideration Condition

If, at 6 months post-GA, less than 30% of active users engage with the Project Brain beyond initial ingestion (i.e., they bypass it for stateless generation), the fundamental model of what users want must be re-examined.

## References

- [ATLAS_CONSTITUTION.md](../00-company/ATLAS_CONSTITUTION.md) — Chapter 17: Project Brain Philosophy
- [PRODUCT_VISION.md](../01-product/PRODUCT_VISION.md) — Section 11: Project Brain
- [ADR-0001](ADR-0001-AEOS.md) — Atlas as AEOS
- [Sprint 1 — Reference Architecture](../03-sprints/Sprint-1/01-atlas-reference-architecture/README.md) — §5: Project Brain Architecture
