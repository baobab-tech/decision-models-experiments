# Data governance for decision models

Status as of 2026-09-30, from vendor privacy policies, terms, DPAs, trust pages and docs. Not legal advice.

## Summary matrix

"n/d" = not documented publicly as of 2026-09-30. Evidence and links are in each model doc's Data governance section.

| Deployment option | Self-host | Fine-tune | EU processing | Trains on your data | Retention / ZDR | DPA | Certifications |
|---|---|---|---|---|---|---|---|
| [Jev (TypeSafe AI), TypeSafe API](models/jev.md#data-governance) | No (closed weights) | No | No; US (AWS, Modal), EU SCCs for transfers | No (privacy policy) | Default period n/d; ZDR for enterprise via sales | Yes, public | SOC 2 Type II |
| [Liquid AI d1, Liquid API](models/liquid-d1.md#data-governance) | No | No | No; US-hosted | Permitted by privacy policy and terms | Kept "as long as necessary"; inputs usable "in perpetuity"; ZDR n/d | Referenced, not public | n/d (trust center access-gated) |
| [Liquid AI d1, Vercel AI Gateway](models/liquid-d1.md#data-governance) | No | No | No; `liquid/d1` has no EU `inferenceRegion` | Vercel: no. Liquid: gateway reports no no-training agreement | Vercel keeps no prompts; no ZDR provider for d1 | Vercel DPA only (not Liquid) | Vercel: SOC 2 Type 2, ISO 27001. Liquid: n/d |
| [GLiNER2.5-Decide (Fastino), hosted API](models/gliner-decide.md#data-governance) | n/a | Yes, hosted training jobs | No; US (AWS), all subprocessors US | Yes by default; enterprise opt-out; own task-model training always | Indefinite by default; `store: false` or team ZDR | No ("do not offer a DPA") | SOC 2 Type II and ISO 27001 in progress (audit expected Nov 2026) |
| [GLiNER2.5-Decide (Fastino), self-hosted](models/gliner-decide.md#data-governance) | Yes (Apache-2.0) | Yes, full or LoRA | Yes, on your EU infra | No | Your control | Not needed (no processor) | Your infra's |
| [Open-weight Jev reproductions, self-hosted](models/open-reproductions.md#data-governance) | Yes (Apache-2.0 for the AutoTrust and Mapika repos checked) | Yes | Yes, on your EU infra | No | Your control | Not needed | Your infra's |
| [Open-weight Jev reproductions, HF Inference Endpoints / HF Jobs](models/open-reproductions.md#data-governance) | Managed (your weights, HF compute) | Yes, via HF Jobs | Endpoints: AWS `eu-west-1` only. Jobs: region n/d | Endpoints do not store payloads; training statement n/d | Endpoint logs 30 days | GDPR DPA via Enterprise plan | SOC 2 Type 2 |
| [Kev](models/kev.md#data-governance) | Yes (Apache-2.0) | Yes, LoRA + head, local or Modal | Yes, on your EU infra; HF Space region n/d | No | Your control; HF Space n/d | Not needed (Modal: your contract) | Your infra's |
| [CLM-8B](models/clm-8b.md#data-governance) | Yes (Apache-2.0) | Yes, heads only | Yes, on your EU infra | No | Your control | Not needed | Your infra's |
| [AnyJev](models/anyjev.md#data-governance) | Yes (Apache-2.0; base-model licence applies) | No weight updates; calibration and heads fit locally | Yes, on your EU infra | No | Your control; exported artifacts can contain labelled states | Not needed | Your infra's |
| [Bonsai-Llama-Jev](models/bonsai-llama-jev.md#data-governance) | Yes (MIT code; weights licence n/d) | n/d; can serve another GGUF | Yes, on your EU infra | No | Your control | Not needed | Your infra's |
| [Together AI Tev1](models/tev1.md#data-governance) | Yes (public weights; licence being finalized) | Yes (MIT recipe; Together fine-tuning) | Together dedicated endpoints in EU (via sales), or local weights | No, without opt-in | ZDR off by default; enable in org settings | SCCs; DPA unverified | SOC 2 Type II |
| [meraGPT Decider 1](models/decider-1.md#data-governance) | No | n/d | n/d; may process in the US | No | Request text in memory only; billing records kept | No DPA; SCCs | n/d |
| [Upstage Solar Decide](models/solar-decide.md#data-governance) | On-prem for Solar Decide n/d | n/d | n/d; US subprocessors | Paid: no. Free tier: may be used | Sync n/d; async 30 days; ZDR endpoint via OpenRouter | No DPA; Korea PIPA | SOC 2, HIPAA, ISO 27001/27701 (unverified) |
| [Respan Span-01](models/span-01.md#data-governance) | Platform on-prem/VPC; Span-01 n/d | n/d | "On request" (unverified) | n/d | Account lifetime; enterprise custom; no ZDR | On request (unverified) | SOC 2 Type II, HIPAA, ISO 27001 (platform-wide) |
| [OpenAI Decisions API](models/openai-decisions-api.md#data-governance) | No | n/d | n/d for Decisions (GPT-6 Luna: yes, +10%) | No (general API terms) | Abuse logs up to 30 days; not ZDR-eligible | Yes (general API DPA) | SOC 2 Type 2 (unverified) |

## Choosing for sensitive data

1. **EU personal data, or data that must not leave your control.** Self-host GLiNER2.5-Decide or an Apache-2.0 open model on your own or EU-hosted infrastructure. No vendor processes the data, so no DPA or transfer mechanism is needed for the model itself.
2. **Managed hosting for open weights in the EU.** HF Inference Endpoints in AWS `eu-west-1` with EU storage region (Team/Enterprise) and an Enterprise-plan DPA. Confirm HF Jobs placement with Hugging Face before fine-tuning on personal data there; the Jobs region is not documented.
3. **API-only models (Jev, d1).** All process in the US. Before sending personal data:
   - sign the vendor's DPA and confirm the transfer mechanism (TypeSafe publishes one with EU SCCs; Liquid's is not public);
   - confirm retention in writing (Jev: request enterprise ZDR; d1: no ZDR documented);
   - confirm training use (Jev: no; Liquid's policy permits it and asks users not to submit personal data).
4. **Through Vercel AI Gateway.** Gateway-side ZDR, no-training, and `inferenceRegion` controls only act on providers that support them. `liquid/d1` supports none of the three as of 2026-09-30; a request that sets ZDR or an EU region should fail rather than route (unverified for d1).
5. **Fastino hosted API.** Set `store: false` or team ZDR and opt out of platform training (enterprise). No DPA is offered, and prompts may reach upstream providers (OpenAI, Anthropic are listed subprocessors), so avoid personal data until a DPA exists.
6. **Non-personal, non-confidential data.** Any option works; pick on accuracy, latency and cost.

Re-check each vendor's pages before relying on this table; several documents (Liquid terms 2024-09-23, Liquid privacy 2025-07-14) predate the decision-model launches.
