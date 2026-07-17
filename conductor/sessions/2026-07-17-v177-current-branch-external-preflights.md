# Conductor session: v177 current-branch external preflights

Date: 2026-07-17
Validated commit: `5833b35`

## Results

| Monitor | Run | Result | Mutation |
| --- | --- | --- | --- |
| Hugging Face destination | [29577724648](https://github.com/edithatogo/reimbursement-atlas/actions/runs/29577724648) | fail closed | none; Space remains `mit`/`gradio` instead of governed `apache-2.0`/`static` |
| OSF protocol/report workflow | [29577726446](https://github.com/edithatogo/reimbursement-atlas/actions/runs/29577726446) | pass | none; registration and publication not requested |
| Zenodo preflight | [29577728066](https://github.com/edithatogo/reimbursement-atlas/actions/runs/29577728066) | pass | none; no DOI or deposit |
| GitHub security settings | [29577729670](https://github.com/edithatogo/reimbursement-atlas/actions/runs/29577729670) | blocked permissions | none; token cannot read security-analysis settings |
| Source health | [29577731251](https://github.com/edithatogo/reimbursement-atlas/actions/runs/29577731251) | pass | none; six licence-review targets and zero operational blockers |

## Boundary

This refresh is operational evidence only. It does not approve licences, research protocols,
policy claims, OSF registration, HF publication, Zenodo deposit or GitHub security settings.
All corresponding readiness gates remain fail-closed.
