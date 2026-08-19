# Digital Twin: source index and evidence boundaries

Use authoritative sources for definitions, standards, security, and evaluation. Treat vendor descriptions and practitioner reports as implementation evidence or hypotheses, not independent proof of fidelity, safety, or business outcome.

## Core sources

| Source | Use | Boundary |
|---|---|---|
| NISTIR 8356, Security and Trust Considerations for Digital Twin Technology | Definitions, abstract entities, synchronization, trust, security, authorization | Technical report, not a universal normative definition |
| NIST Digital Twins for Advanced Manufacturing | System-of-systems, lifecycle, VVUQ, testbeds, digital thread, reference architectures | Manufacturing scope; transfer to software is adaptation |
| ISO 23247 | Manufacturing digital-twin framework | Manufacturing scope; do not claim software-factory conformance |
| ISO/IEC 30173 | Digital-twin concepts and terminology | Standard terminology; inspect current edition before quoting |
| DTDL | Machine-readable models, interfaces, relationships, telemetry, semantic types | Runtime support is service-specific; test portability |
| IDTA AAS / IEC 63278 | Standardized industrial asset representation | Industrial semantics; not a complete agent/software ontology |
| OPC UA | Information models, services, PubSub, security, history, companion specs | Interoperability mechanism, not domain governance |
| FMI 3.0 | Model exchange, co-simulation, scheduled execution | Simulation interface, not semantic validity or twin identity |
| W3C PROV, RDF, JSON-LD, SHACL | Provenance, semantic graph, JSON representation, validation | Building blocks; adoption still requires domain vocabulary |
| NASA-STD-7009 and ASME VVUQ | Model/simulation credibility, V&V, uncertainty | Thresholds remain intended-use and risk dependent |
| NIST AI RMF, SSDF, Privacy Framework, SP 800-207/800-61 | Governance, software security, privacy, zero trust, incident response | Adjacent control frameworks; map controls honestly |
| OWASP agent security | Excessive agency, tool authorization, prompt-injection defenses | Guidance, not a certification or complete safety case |
| Kimmel et al., Digital Twins for Software Engineering Processes | Direct conceptual bridge to DevOps/software-process twins | Research vision; no proof of complete production deployment |
| SEI TwinOps | Model-based engineering + DevOps + twin/testbench pattern | Cyber-physical engineering; software transfer is partial |
| Facebook/Meta cyber-cyber twins | Running software as a twin subject | Specific published work, not universal factory evidence |
| SWE-bench family, service emulators, traffic mirrors | Agent environments and scenario components | Snapshots/emulators/mirrors are not automatically live twins |

## Claims discipline

Use `direct evidence`, `adaptation`, `vendor claim`, `inference`, or `open question` labels. Preserve source URL, title, revision/date, access date, relevant scope, and limitation. Do not turn a standard into efficacy evidence, an architecture into a production result, an emulator into a twin, or a confidence score into authority.

## URLs

- https://csrc.nist.gov/pubs/ir/8356/final
- https://www.nist.gov/programs-projects/digital-twins-advanced-manufacturing
- https://www.iso.org/standard/75066.html
- https://www.iso.org/standard/81442.html
- https://azure.github.io/opendigitaltwins-dtdl/DTDL/v4/DTDL.v4.html
- https://industrialdigitaltwin.org/en/content-hub/aasspecifications
- https://reference.opcfoundation.org/
- https://www.fmi-standard.org/docs/3.0/
- https://www.w3.org/TR/prov-o/
- https://www.w3.org/TR/rdf11-concepts/
- https://www.w3.org/TR/json-ld11/
- https://www.w3.org/TR/shacl/
- https://arxiv.org/html/2510.05768v1
- https://www.sei.cmu.edu/publications/annual-reviews/2020-year-in-review/year_in_review_article.cfm?customel_datapageid_315013=315536
