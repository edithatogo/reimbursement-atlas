# Conductor Session: v170 Current-Main External Preflights

Date: 2026-07-17
Commit: `70fbee23fa98204e0424dadc0502cf56a44ac14f`

## Scope

Refresh non-mutating evidence for OSF discovery, Zenodo readiness, Hugging Face destination
metadata, credentialed source health, and GitHub security-settings visibility after PR #420
merged to `main`.

## Evidence

- OSF workflow `29572723985`: success; pinned `osf-cli-go v1.0.0`, 28 accessible project records,
  private `Reimbursement Atlas` project `q8cnx`; provisioning, registration, upload and publication
  skipped.
- Zenodo workflow `29572723927`: success; `validated_non_depositing`, no DOI, no mutation.
- Hugging Face workflow `29572723939`: failed closed; dataset `other` aligned, Space `mit`/`gradio`
  drifted from governed `apache-2.0`/`static`; no mutation.
- Source-health workflow `29572724022`: success; zero operational blockers, six licence-review
  targets, 14,867 PBS records schema-validated, raw payloads untracked.
- GitHub security workflow `29572723999`: success; report status `blocked_permissions`;
  security-analysis fields were omitted by the workflow token, so no settings conclusion was inferred.

## Outcome

Repository-owned gates remain green and no external readiness flag is promoted. The remaining work
requires licence decisions, human research review, an available local PBS key, HF Space reconciliation,
OSF/Zenodo publication approval, or a token with security-analysis read scope.
