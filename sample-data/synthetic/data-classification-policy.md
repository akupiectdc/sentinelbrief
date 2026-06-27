# Data Classification Policy (Synthetic)

> Synthetic document created for the SentinelBrief demo corpus. It contains no
> real or sensitive information.

## Purpose

This policy defines how information is classified and handled so that protection
matches the sensitivity of the data. Consistent classification lets staff make
quick, correct decisions about storing, sharing, and disposing of information.

## Classification levels

* **Public.** Information approved for release to anyone. Disclosure causes no
  harm. Examples: published reports, marketing material.
* **Internal.** Day-to-day information intended for staff. Limited harm if
  exposed. Examples: internal procedures, project plans.
* **Confidential.** Sensitive information restricted to those with a need to
  know. Disclosure causes meaningful harm. Examples: customer records,
  contracts, security findings.
* **Restricted.** The most sensitive information, tightly controlled. Disclosure
  causes severe harm. Examples: credentials, encryption keys, regulated personal
  data.

## Labelling

Documents and datasets must carry their classification in the title, header, or
metadata. When information of mixed sensitivity is combined, the result takes the
highest classification present.

## Handling requirements

* **Storage.** Confidential and Restricted data must be stored only in approved
  systems with access controls. Restricted data must be encrypted at rest.
* **Transmission.** Confidential and Restricted data must be encrypted in transit.
  Never send Restricted data over unencrypted channels or to personal accounts.
* **Access.** Grant access on a need-to-know basis. Review access when a person
  changes role and revoke it promptly when they leave.
* **Sharing externally.** Sharing Confidential or Restricted data outside the
  organisation requires owner approval and an agreement covering its protection.

## Retention and disposal

Keep information only as long as it is needed for business or legal reasons. When
disposing of Confidential or Restricted data, use secure deletion for digital
media and shredding for paper. Record the disposal of Restricted data.

## Roles

* **Data owners** assign classification and approve access.
* **Data custodians** operate the systems that store the data and apply controls.
* **All staff** are responsible for handling information according to its label.

## Exceptions

Any exception to this policy must be documented, time-limited, and approved by the
data owner together with the security team.
