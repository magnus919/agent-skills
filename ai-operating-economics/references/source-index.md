# Source Index and Evidence Boundaries

This index records the research basis for the skill. Access dates and versions should be refreshed when a decision depends on a time-sensitive provider capability. These sources inform method and guardrails; they do not establish universal ROI.

## Workflow outcome and measurement

| Source | Evidence type | Supports | Does not support |
|---|---|---|---|
| [Brynjolfsson, Li, and Raymond, Generative AI at Work](https://www.nber.org/papers/w31161) | Independent working paper, revised 2023 | In one customer-support deployment, AI assistance increased resolved issues per hour by about 14% on average, with much larger gains for novice/lower-skilled workers and minimal gains for experienced/high-skilled workers; the paper also examines quality, sentiment, retention, adherence, and learning | General enterprise ROI, current agentic-system performance, or universal productivity claims |
| [NBER digest summary](https://www.nber.org/digest/20236/measuring-productivity-impact-generative-ai) | Independent study summary | Plain-language description of the measured deployment and heterogeneous effects | A substitute for the working paper when methodological detail matters |
| [METR, Uplift Update](https://metr.org/blog/2026-02-24-uplift-update/) | Independent measurement research | Selection effects, task-selection bias, concurrent-agent accounting, and why an attractive developer-speed estimate may not support a strong causal claim | A general estimate of enterprise AI productivity |
| [METR, AI Usage Survey](https://metr.org/blog/2026-05-11-ai-usage-survey/) | Independent survey research | The distinction between speed and value, plus caveats on self-reported uplift and counterfactual estimation | Audited financial ROI or causal productivity evidence |
| [Noy and Zhang, Experimental Evidence on the Productivity Effects of Generative Artificial Intelligence](https://economics.mit.edu/sites/default/files/inline-files/Noy_Zhang_1.pdf) | Randomized experiment manuscript | Short writing-task effects on completion time, blinded quality, performer heterogeneity, task composition, and the limits of inferring durable workplace value | Firm-level ROI, long-term skill development, or generalization to organization-specific work |
| [OECD Employment Outlook 2023: AI, job quality and inclusiveness](https://www.oecd.org/en/publications/oecd-employment-outlook-2023_08785bba-en/full-report/artificial-intelligence-job-quality-and-inclusiveness_a713d0ad.html) | Independent policy research | Worker, management, working-condition, skill, productivity, wage, employment, and transition dimensions that should accompany a narrow productivity measure | A universal prediction of AI's labor-market impact or a substitute for local worker evidence |
| [OECD case studies of AI implementation](https://www.oecd.org/content/dam/oecd/en/publications/reports/2023/03/the-impact-of-ai-on-the-workplace-evidence-from-oecd-case-studies-of-ai-implementation_b4c2c6ee/2247ce58-en.pdf) | Independent case research | Heterogeneity across worker profiles, sectors, countries, task composition, skill requirements, and job quality | A causal benchmark for a specific organization |

## Cost and usage

| Source | Evidence type | Supports | Does not support |
|---|---|---|---|
| [FinOps for AI overview](https://www.finops.org/wg/finops-for-ai-overview/) | Primary foundation guidance | Extending FinOps practices to volatile model pricing, token meters, GPU scarcity, allocation, quotas, tagging, and outcome alignment | Proof that any organization has realized savings |
| [How to Build a Generative AI Cost and Usage Tracker](https://www.finops.org/wg/how-to-build-a-generative-ai-cost-and-usage-tracker/) | Primary foundation guidance | Token attribution levels, centralized or common interfaces, shared-throughput allocation, and the need to account for more than inference | A universal architecture or exact savings formula |
| [GenAI FinOps: How Token Pricing Really Works](https://www.finops.org/wg/genai-finops-how-token-pricing-really-works/) | Primary foundation guidance | The warning that advertised token prices do not describe complete application TCO | A measured cross-provider cost comparison |
| [Token Economics: The Atomic Unit of AI Value](https://www.finops.org/insights/token-economics-the-atomic-unit-of-ai-value/) | Primary foundation insight | Tokens are computation units and require contextual interpretation | Tokens as a direct measure of business value |

## Benefits realization and cost estimation

| Source | Evidence type | Supports | Does not support |
|---|---|---|---|
| [UK Digital and Data Benefits Framework](https://www.gov.uk/government/publications/digital-and-data-benefits-framework/digital-and-data-benefits-framework) | Government guidance | Distinguishing benefits, disbenefits, measures, owners, baselines, dependencies, and realization tracking in a digital business case | A universal accounting treatment or proof that a forecast benefit will be realized |
| [UK Magenta Book evaluation guidance](https://www.gov.uk/government/publications/the-magenta-book/magenta-book-central-government-guidance-on-evaluation-html) | Government evaluation guidance | Evaluation planning, theory of change, counterfactual reasoning, monitoring, and proportionate evidence design | A replacement for domain-specific statistical or financial expertise |
| [FinOps Open Cost and Usage Specification (FOCUS)](https://focus.finops.org/focus-specification/) | Primary specification | A common structure for normalizing billing data and supporting reconciliation, allocation, chargeback, budgeting, and forecasting | Complete TCO, causal ROI, labor cost, or the correct local allocation policy |
| [GAO Cost Estimating and Assessment Guide](https://www.gao.gov/products/gao-20-195g) | Government cost-estimation guidance | Lifecycle cost categories, documented assumptions, uncertainty, sensitivity, independent review, and updating estimates as evidence changes | An AI-specific cost model or a guarantee of estimate accuracy |

## Governance and worker impact

| Source | Evidence type | Supports | Does not support |
|---|---|---|---|
| [NIST AI RMF: Generative AI Profile](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf) | Primary voluntary framework | Generative-AI-specific risk considerations, testing and evaluation, monitoring, incident response, human oversight, and lifecycle controls | Certification, compliance, safety proof, or realized value |
| [ISO/IEC 42001](https://www.iso.org/standard/42001) | International standard description | The AI management-system idea: objectives, responsibilities, performance evaluation, corrective action, and continual improvement | Certification or conformance without an authorized audit and the applicable standard |
| [ILO, Generative AI and Jobs](https://webapps.ilo.org/static/english/intserv/working-papers/wp096/index.html) | Independent policy research | Job quantity and quality, autonomy, work organization, and worker voice as dimensions beyond productivity | A prediction of the impact on a particular employer or occupation |

## Telemetry and controls

| Source | Evidence type | Supports | Does not support |
|---|---|---|---|
| [OpenTelemetry GenAI observability](https://opentelemetry.io/blog/2026/genai-observability/) | Primary technical guidance | Agent, model-call, tool-execution, model/version, duration, and token telemetry; prompt and tool content should not be captured by default when sensitive | Complete production observability or a guarantee of privacy |
| [OpenTelemetry GenAI attributes](https://opentelemetry.io/docs/specs/semconv/registry/attributes/gen-ai/) | Primary technical specification | Portable provider, model, operation, token, and agent attributes, with version/movement caveats | Stable interoperability across every implementation without version pinning |
| [NIST AI RMF Core](https://airc.nist.gov/airmf-resources/airmf/5-sec-core/) | Primary voluntary framework | Govern, map, measure, and manage lifecycle structure; inventory, roles, monitoring, incident response, recovery, and deactivation expectations | Certification, safety proof, or legal compliance |
| [NIST Generative AI Profile](https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence) | Primary voluntary framework | Generative-AI-specific risk-management considerations to supplement AI RMF 1.0 | A complete implementation design or outcome guarantee |
| [AWS Bedrock prompt routing](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-routing.html) | Vendor documentation | An example of provider-side quality/cost routing and its documented limitations | Independent savings or quality superiority |
| [Microsoft Foundry cost management](https://learn.microsoft.com/en-us/azure/ai-foundry/foundry-models/how-to/manage-costs) | Vendor documentation | An example of estimation, representative test traffic, cost grouping, budgets, alerts, and dependent-resource TCO | Hard spend stops, universal controls, or independent ROI |

## Research-use rules

- Preserve the source URL, access date, evidence type, scope, and caveat with every retained claim.
- Treat working papers as research evidence, not peer-reviewed consensus unless the source says otherwise.
- Treat vendor documentation as capability evidence only.
- Treat vendor surveys and case studies as reported claims, not causal outcomes.
- Do not copy copyrighted source text into public skill content; paraphrase and link.
- Re-verify provider capabilities and moving OpenTelemetry conventions before using them as implementation requirements.
