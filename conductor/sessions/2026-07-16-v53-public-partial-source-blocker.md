# v53 public partial-source blocker

## Finding

The final handoff correctly classified source acquisition as `partial`, but the public status
manifest only exposed licence, evidence, research-publication and OSF blockers.

## Implemented

- Read final-handoff JSONL in the public status generator.
- Expose stable `source_acquisition` blocker metadata when source ingestion is partial.
- Add a contract test and retain the evidence path to the handoff task records.
- Record the change in the HANDOFF-018 Conductor backlog.
