# Security Policy

## Reporting a Security Vulnerability

Atlas takes security seriously. If you discover a security vulnerability, **do not open a public GitHub issue.**

### Responsible Disclosure Process

1. **Email:** security@atlashq.com (placeholder — configure before launch)
2. **Subject line:** `[SECURITY] Brief description`
3. **Include:**
   - Affected component (which platform/service/module)
   - Severity assessment (Critical / High / Medium / Low)
   - Reproduction steps
   - Potential impact
   - Suggested mitigation if known

### Response Timeline

| Severity | Initial Response | Resolution Target |
|---|---|---|
| Critical | 24 hours | 72 hours |
| High | 48 hours | 7 days |
| Medium | 5 business days | 30 days |
| Low | 10 business days | 90 days |

---

## Security Architecture

Atlas is designed with security-first principles. The full threat model is documented in:

- [Security & Trust Architecture](docs/03-sprints/Sprint-1/08-security-and-trust-architecture/README.md)
- [Atlas Constitution — Chapter 6: Security](docs/00-company/ATLAS_CONSTITUTION.md)

### Key Security Properties

| Property | Implementation |
|---|---|
| Multi-tenant isolation | Each tenant's Project Brain is strictly isolated; cross-tenant data access is impossible by design |
| Zero long-lived agent secrets | Secrets & Credentials Broker issues just-in-time, scoped, auto-expiring credentials |
| Audit Trail | Every consequential action is cryptographically logged; tampering is detectable |
| Retrieved content as untrusted data | Content from ingested documents, code, and tickets is always treated as untrusted; never as instructions |
| No autonomous production access in V1 | All agents are Stage 1 (Advisory); no agent autonomously modifies production systems |
| Policy-based authorization | Every tool invocation is checked against the Policy Engine before execution |

---

## Supported Versions

| Version | Security Support |
|---|---|
| V1 (current design) | Active |

---

## Hall of Fame

We will publicly acknowledge responsible disclosure contributors here. Thank you for keeping Atlas and its users safe.
