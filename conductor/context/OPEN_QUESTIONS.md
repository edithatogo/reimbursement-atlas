# Open questions

## Source and licensing

1. Should the legacy MBS XML adapter remain fixture-only now that XML distribution is discontinued?
2. Which CMS CLFS public file should be used for first live-source validation?
3. What exact licence language governs redistribution of generated derived fields for MBS, PBS, CMS, NHS and other first-wave sources?
4. How much CPT/HCPCS descriptor text can be stored in a public dataset without requiring additional licensing?
5. Which generated artefacts are safe for Hugging Face publication versus local-only cache?

## Data model

1. Should `ScheduleItemRecord.payment_amount` represent schedule fee, benefit, allowed amount, tariff, price limit or another value via a structured `amount_type` field?
2. Should bundled facility/professional decomposition become a separate table?
3. Should restrictions be normalised into their own records before ontology mapping?
4. Do source-version records need snapshot checksums even for manually downloaded local-only files?

## Analyses

1. Which policy analysis should become the first real demonstrator: genomics/pathology diffusion, cognitive/procedural ratio, transparency index or price-opacity score?
2. What basket of genomic/pathology tests is clinically defensible and globally mappable?
3. What minimum review process is needed before a crosswalk candidate can be used in a policy output?

## Interfaces

1. Should the API remain local-only until authentication and licence gates exist?
2. Which MCP server library should be used once the read-only tool contract is stable?
3. Should the dashboard read static CSVs only, or query the local API when available?
