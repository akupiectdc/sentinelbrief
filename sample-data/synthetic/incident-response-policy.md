# Incident Response Policy (Synthetic)

> Synthetic document created for the SentinelBrief demo corpus. It contains no
> real or sensitive information.

## Purpose

This policy defines how the organization detects, reports, and responds to
information security incidents. It applies to all employees, contractors, and
systems.

## Definitions

A **security incident** is any event that compromises, or threatens to
compromise, the confidentiality, integrity, or availability of information
systems or data. Examples include malware infections, unauthorized access,
data leaks, and denial-of-service conditions.

## Severity levels

* **SEV-1 (Critical):** active compromise of production systems or confirmed
  data breach. Requires immediate response.
* **SEV-2 (High):** likely compromise or significant service disruption.
* **SEV-3 (Medium):** contained issue with limited impact.
* **SEV-4 (Low):** minor or suspected issue with no confirmed impact.

## Response phases

1. **Detection.** Incidents may be detected by monitoring alerts, user reports,
   or third-party notifications.
2. **Reporting.** Anyone who suspects an incident must report it to the Security
   Operations Center (SOC) without delay through the designated channel.
3. **Triage.** The on-call analyst assigns a severity level and opens an
   incident ticket.
4. **Containment.** The team isolates affected systems to prevent the incident
   from spreading. For SEV-1 incidents, containment takes priority over root
   cause analysis.
5. **Eradication.** Remove the cause, such as malware, malicious accounts, or
   exploited vulnerabilities.
6. **Recovery.** Restore systems from known-good sources and verify normal
   operation before returning them to production.
7. **Post-incident review.** Within five business days, the team documents
   timeline, impact, root cause, and corrective actions.

## Roles

* **Incident Commander:** coordinates the response and makes final decisions.
* **SOC Analyst:** performs triage, investigation, and containment.
* **Communications Lead:** manages internal and external communication.

## Communication

For SEV-1 and SEV-2 incidents, the Communications Lead notifies executive
stakeholders within one hour of confirmation. External notifications follow
legal and regulatory requirements.

## Record keeping

Every incident must have a ticket that records detection time, actions taken,
people involved, and the post-incident review outcome. Records are retained for
at least one year.
