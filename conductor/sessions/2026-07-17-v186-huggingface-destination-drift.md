# v186 Hugging Face destination drift

## Scope

Refresh the read-only public destination metadata monitor on merged `main` `dfd9e18`.

## Evidence

Run [29584493383](https://github.com/edithatogo/reimbursement-atlas/actions/runs/29584493383)
reached both configured public endpoints. The dataset passed with `license=other`; the Space
reported `license=mit` and `sdk=gradio` instead of the governed `apache-2.0` and `static` values.
The monitor recorded `mutation_performed=false` and synchronized issue #320.

## Boundary

No Hugging Face metadata or content was changed. Reconciliation remains gated by licence,
evidence, research and publication approval.
