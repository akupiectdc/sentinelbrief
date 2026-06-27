# Data Sources

SentinelBrief works with a small, clearly-licensed corpus so the repository
stays light and safe to publish.

## Allowed demo inputs

1. **Synthetic security procedures** - small Markdown documents written for this
   repository, stored in `sample-data/synthetic/`. They imitate the kind of
   internal documents an organization would index, without containing any real
   private data.
2. **Public source references** - pointers (title, publisher, URL) to official
   public cybersecurity publications, stored in
   `sample-data/external/sources.json`. The documents themselves are **not**
   committed; only references are.
3. **User-provided local documents** - a user can place their own files in a
   local-only folder (e.g. `sample-data/local/`, git-ignored) and ingest them.

## Synthetic documents

The committed synthetic set covers:

* `incident-response-policy.md` - incident response policy
* `phishing-triage-playbook.md` - phishing triage playbook
* `vulnerability-disclosure-procedure.md` - vulnerability disclosure procedure

These are deliberately short and generic. They are safe to index, quote, and
cite in a demo.

## External references

`sample-data/external/sources.json` lists official public sources, preferring
CERT Polska / NASK publications. Each entry records the title, publisher,
language, URL, and a short note. To use them, a user downloads the document
locally (outside the repository) and ingests it.

## What must never be committed

* large public PDFs
* private documents
* sensitive documents
* copyrighted corpora copied without permission
* real internal company documents

The `.gitignore` excludes `*.pdf` and `sample-data/local/` to reduce the risk of
accidentally committing source material.

## Metadata

Each ingested document carries: `document_id`, `title`, `source_type`,
`language`, `filename` or `url`, and `ingested_at`. Each chunk carries:
`document_id`, `chunk_id`, `source_title`, `source_type`, and (when available)
`page_number`, `character_start`, and `character_end`.
