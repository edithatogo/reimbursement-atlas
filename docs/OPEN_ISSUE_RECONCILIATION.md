# Open issue reconciliation

This register records the 2026-08-26 audit of every GitHub issue that was open at
the start of the reconciliation. Issue closure is evidence-bound and does not
silently convert candidate metadata into acquired data or a validated parser.

## Completed from existing source evidence

| Issue | Decision | Evidence |
|---|---|---|
| #21 | Close as implemented. | The real MBS XML release is checksum-bound as `5834d849743a3eab2b8c03e826a5ed6a488a6f65cf4c4148da3ec227e5007805`; its reviewed bundle parses 6,045 rows, passes source validation, excludes raw bytes, and has a checksum-bound owner licence decision for the validation report. |

## Dataset-candidate metadata onboarding

Issues #94 through #108 are closed only as **metadata onboarding**. The canonical
candidate records already identify the source, jurisdiction, access mode,
priority, URL, licence gate, parser state and next step. The generated assessment
adds explicit source-registry linkage and a fail-closed acquisition state.

| Issue | Candidate | Registry state | Acquisition/parser state |
|---|---|---|---|
| #94 | CMS Medicare Coverage Database downloads | Linked to `us_cms_mcd`. | Not acquired; parser planned. |
| #95 | CMS Hospital Price Transparency MRFs | Candidate record only. | Not acquired; parser planned. |
| #96 | Transparency in Coverage MRFs | Candidate record only. | Not acquired; parser planned. |
| #97 | CMS Open Payments | Candidate record only. | Not acquired; parser planned. |
| #98 | OECD Health Statistics | Linked to `oecd_health_stats`. | Not acquired; parser planned. |
| #99 | WHO Global Health Expenditure Database | Context linkage to `who_gho`. | Not acquired; parser planned. |
| #100 | World Bank WDI health indicators | Candidate record only. | Not acquired; parser planned. |
| #101 | SUS SIGTAP | Linked to `br_sigtap`. | Not acquired; parser planned. |
| #102 | FONASA arancel and PAD | Candidate record only. | Not acquired; parser planned. |
| #103 | CUPS procedure codes | Candidate record only. | Not acquired; parser planned. |
| #104 | HIRA/NHI resources | Linked to `kr_hira`. | Not acquired; parser planned. |
| #105 | NHSO/UCS resources | Candidate record only. | Not acquired; parser planned. |
| #106 | Singapore MOH benchmarks | Linked to `sg_fee_benchmarks`. | Not acquired; parser planned. |
| #107 | AIHW contextual tables | Linked to `au_aihw_mbs_pbs_stats`. | Not acquired; parser planned. |
| #108 | IHME GBD | Candidate record only; licensing/API review retained. | Not acquired; parser planned. |

The machine-readable source is
`data/derived/dataset_candidates/dataset_candidate_assessments.jsonl`. Future
payload acquisition must create separate source-version, source-file, contract,
rights and provenance evidence before any promotion claim.

## Remain open

| Issue | Current state | Closure condition |
|---|---|---|
| #255 | Acquired breadth: 341 historical MBS snapshots are replay-eligible, two removed official TXT targets are `upstream_unavailable`, 1,048/1,049 PBS PDFs and all 655 discovered post-2007 structured packages are signature-validated in ignored storage, and governed provenance is published. | Obtain the missing December 1987 bytes from the publisher or an authorised byte-preserving source; obtain written permission or an open licence before raw PBS redistribution; investigate pre-2007 machine-readable releases only if broader structured parity is required. |
| #362 | Monitored external compatibility dependency, not a release blocker. | Upgrade only when the Astro checker peer range supports TypeScript 7 and all package, build and browser gates pass. |

No paper, preprint, broad evidence, source-completeness or redistribution claim is
created by this reconciliation.
