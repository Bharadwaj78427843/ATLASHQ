# Architecture Decision Records

This directory contains the canonical record of all significant architectural decisions made for Atlas.

---

## ADR Index

| ADR | Title | Status | Date |
|---|---|---|---|
| [ADR-0001](ADR-0001-AEOS.md) | Atlas as an AI Engineering Operating System | Accepted | 2026-07-28 |
| [ADR-0002](ADR-0002-Project-Brain.md) | Project Brain as Primary Architectural Object | Accepted | 2026-07-28 |
| [ADR-0003](ADR-0003-Engineering-Intelligence-Core.md) | Engineering Intelligence Core — Brain + Cognition Loop | Accepted | 2026-07-28 |
| [ADR-0004](ADR-0004-Microsoft-Agent-Framework.md) | Microsoft Agent Framework as Orchestration Substrate | Proposed | 2026-07-28 |
| [ADR-0005](ADR-0005-RAGFlow.md) | RAGFlow for Document-Heavy Retrieval Scenarios | Proposed | 2026-07-28 |
| [ADR-0006](ADR-0006-Knowledge-Graph.md) | Knowledge Graph Database Technology Selection | Proposed | 2026-07-28 |
| [ADR-0007](ADR-0007-Trust-Governance.md) | Governance as Cross-Cutting Layer | Accepted | 2026-07-28 |
| [ADR-0008](ADR-0008-Model-Router.md) | OpenRouter for Model Provider Agnosticism | Accepted | 2026-07-28 |

---

## ADR Format

Every ADR must include:

```markdown
# ADR-XXXX: [Title]

**Status:** Proposed | Accepted | Deprecated | Superseded by ADR-XXXX

**Context:** What situation or problem prompted this decision?

**Decision:** What was decided?

**Alternatives Considered:** At least one alternative and why it was rejected.

**Trade-offs Accepted:** What is deliberately given up?

**Consequences:** What becomes easier or harder as a result?

**Reconsideration Condition:** What change would make this worth revisiting?

**References:** Links to related ADRs, Sprint documents, or Constitution sections.
```

---

## Status Definitions

| Status | Meaning |
|---|---|
| Proposed | Under review; not yet binding |
| Accepted | In effect; all downstream work must comply |
| Deprecated | No longer recommended; not yet superseded |
| Superseded | Replaced by a newer ADR; retained as historical evidence |
