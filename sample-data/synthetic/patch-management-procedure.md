# Patch Management Procedure (Synthetic)

> Synthetic document created for the SentinelBrief demo corpus. It contains no
> real or sensitive information.

## Purpose

This procedure describes how security updates and patches are identified,
tested, and deployed so that known vulnerabilities are remediated within
predictable timeframes.

## Scope

The procedure covers operating systems, applications, libraries, container
images, and network device firmware across all environments.

## Asset inventory

Effective patching depends on a current inventory. Each asset must record its
owner, environment, software versions, and exposure (internet-facing or
internal). Assets missing from the inventory cannot be assumed to be patched.

## Identifying patches

* Subscribe to vendor advisories and trusted vulnerability feeds.
* Review newly published vulnerabilities at least weekly.
* Use vulnerability scanning to detect missing patches and misconfigurations.

## Risk-based prioritisation

Patches are prioritised by severity and exposure, not by release date alone.

* **Critical.** Actively exploited, or critical severity on an internet-facing
  system. Patch within 72 hours.
* **High.** High severity, or critical severity on internal systems. Patch within
  7 days.
* **Medium.** Patch within 30 days.
* **Low.** Patch during routine maintenance.

## Testing

Where feasible, apply patches first to a test or staging environment to confirm
they do not break functionality. Emergency patches for actively exploited
vulnerabilities may bypass full testing when the risk of waiting is greater than
the risk of disruption; record this decision.

## Deployment

* Schedule patch windows and notify affected owners in advance.
* Deploy in waves, starting with lower-risk systems where possible.
* Keep a rollback plan and a recent backup before patching critical systems.

## Verification

After deployment, confirm that patches installed successfully and that the
related vulnerability no longer appears in scans. Update the asset inventory with
the new versions.

## Exceptions

If a system cannot be patched within its deadline, document the reason, apply
compensating controls (such as isolation or tighter monitoring), and set a review
date. Exceptions for internet-facing systems require security team approval.
