# Phishing Triage Playbook (Synthetic)

> Synthetic document created for the SentinelBrief demo corpus. It contains no
> real or sensitive information.

## Purpose

This playbook describes how to triage a reported phishing email quickly and
consistently.

## When a phishing email is reported

1. **Acknowledge the report.** Confirm receipt with the reporter and thank them.
   Encouraging reporting is more valuable than punishing mistakes.
2. **Preserve evidence.** Keep the original email, including full headers. Do not
   forward it in a way that strips headers; submit it as an attachment or through
   the reporting button.
3. **Do not click.** Analysts must never click links or open attachments on a
   normal workstation. Use an isolated analysis environment.

## Initial assessment

Check the following signals:

* **Sender:** mismatched display name and address, look-alike domains, or
  external sender posing as an internal colleague.
* **Links:** hover to reveal the true destination; watch for URL shorteners and
  domains that imitate trusted brands.
* **Attachments:** unexpected documents, especially those requesting macros to be
  enabled.
* **Urgency and pretext:** pressure to act fast, payment requests, or credential
  prompts.

## Classification

* **Confirmed phishing:** proceed to containment.
* **Spam / nuisance:** no further action beyond filtering.
* **Legitimate:** release to the user and document the false positive.

## Containment for confirmed phishing

1. Search the mail system for other copies and quarantine them.
2. Block the sender address, sender domain, and any malicious URLs or hashes.
3. If any user interacted with the email, check for credential entry or malware
   execution.

## If credentials were entered

1. Reset the affected user's password immediately.
2. Revoke active sessions and tokens.
3. Review account activity for signs of misuse.
4. Enable or verify multi-factor authentication.

## Escalation

If the phishing campaign is widespread, targets executives, or leads to a
confirmed compromise, escalate to the incident response process and open a
SEV-2 (or higher) incident.

## After action

Record indicators of compromise, update mail filters, and share a short
awareness note with staff when a campaign was notable.
