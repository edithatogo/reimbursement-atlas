# Conductor session: OSF private project provisioning

Date: 2026-07-15

The authenticated OSF discovery run confirmed that no accessible project had the exact
title `Reimbursement Atlas`. This session adds a token-gated, idempotent workflow mode
that searches first and creates one private project only when absent. The workflow
uploads sanitized project metadata for the maintainer to verify before setting the
repository `OSF_PROJECT_ID` variable.

This is infrastructure setup, not publication or registration. The existing OSF
publication job remains fail-closed because the generated sync manifest contains no
human-approved rows and the evidence, licence and research-review gates remain open.
