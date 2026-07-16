# Session v94: Recommendation audit and licence queue clarification

## Scope

Audit the remaining recommendations from the merged public-product handoff:

- human licence review;
- PBS API credential and monthly-extract acquisition;
- OSF, Hugging Face and Zenodo publication controls;
- GitHub advanced secret-scanning controls.

## Evidence

- Repository `main` is clean at the merged PR #281 commit.
- The repository release matrix passes 36/36 gates.
- The OSF CLI v1.0.0 contract passes without mutation.
- The checksum-bound licence queue validates with 159 pending artifact candidates.
- The queue includes project metadata, governance outputs, seed artefacts and source-derived
  candidates; it is not a count of raw or source-derived files.
- PBS acquisition remains correctly gated by `PBS_API_SUBSCRIPTION_KEY` and source review.
- OSF, Hugging Face and Zenodo workflows remain non-mutating until review gates pass.
- GitHub's authoritative repository response keeps non-provider pattern scanning and validity
  checks disabled; the personal-account plan boundary is recorded in issue #191.

## Changes

Corrected queue-count wording in release-readiness, review-decision, licence-queue and Conductor
context documentation. No gate was relaxed and no external mutation was attempted.

## Remaining handoff

Human licence/domain review, PBS credential and extract review, research protocol/mapping approval,
publication authorization, and GitHub account/plan controls remain outside repository-only execution.
