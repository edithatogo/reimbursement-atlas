# Analysis recipes

`data/seed/analysis_recipes.*` turns high-level policy analyses into workflow-ready plans.

Each recipe records:

- linked analysis id;
- design/prototype/blocked/production status;
- required input tables;
- output tables;
- quality gates;
- policy question;
- caveats.

The recipes are used by:

- the Conductor handoff layer;
- graph generation;
- future GitHub issue/project automation;
- dashboard discovery;
- future CI gates that check whether required inputs and outputs exist.

The first recipes cover genomics price/coverage linkage, cognitive-procedural relativities, medicine price opacity, source transparency and local-versus-national coverage discretion.
