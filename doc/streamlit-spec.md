# Local / Global — Streamlit baseline specification

Status: v1 baseline for the Python visualization. This is a research instrument, not an empirical result.

## Purpose and audience
A non-specialist can change one assumption, see how allocations or costs move, and capture a question for follow-up research. The tone is curious, not a verdict for or against central planning, local authority, human decisions, or future AI agents.

## Run surface
- Python 3.10+; install `requirements.txt`; run `streamlit run app.py`.
- Three tabs; native Streamlit widgets and charts; no account, API key, database, or external data.
- Notes are session-only and exportable to JSON. The app must say they are not durable without download.

## Experiment 1: share scarce stock
- Both A and B need 8 units; available supply adjustable from 0 to 16.
- Weight on A adjustable 0.2 to 5; B weight fixed at 1. B's requested floor adjustable 0 to 8.
- Score = weight × (8−A)^2 / 2 + (8−B)^2 / 2. A+B=supply, 0≤A,B≤8.
- First rule minimizes score; second minimizes subject to B's attainable floor (capped to supply).
- Show A/B received, A/B unmet, score and a side-by-side allocation plot; say when floor binds and who gives up units. Explicitly label this as a chosen modeled score, not welfare or fairness.
- Default: 10 supply, A weight 3, B floor 5 => central A/B = 6.5/3.5, score 13.5; B-floor = 5/5, score 18.
- Edges: nonbinding floor leaves both allocations identical; supply 0 and 16 retain feasibility; impossible floor is visibly capped.

## Experiment 2: buy now, depend later
- Buy 10 today. Local purchases cost one extra per unit; a distant supplier is cheaper today.
- Local order y in [0,10] changes *assumed* future local capacity to 2+0.6y. In a distant disruption, distant capacity is 4; next period needs 10.
- Adjustable disruption probability 0–100% and cost of a missing future unit 0–10.
- Today-only choice y=0; future-aware choice minimizes y + p×cost×max(0, 6−(2+0.6y)). Display orders, expected shortage, and expected modeled cost for both.
- Default: today-only expected cost 8, future-aware local order 20/3 and modeled cost 20/3; probability 0 implies y=0.
- State that the capacity response is a hypothesis to investigate, not evidence.

## Experiment 3: fictional styles versus fixed rules
- Fixed supply 10; each market needs 8. Adjustable A weight, B floor, 10–500 trials per fictional style, and random seed.
- Fictional styles: self-interested favors A; gain-seeking favors higher-weighted market (equal weights split); systematic aims at minimum score; empathetic aims for equal shortages. Each run adds an independent uniform perturbation in [-1.5,+1.5], then clamps A's share to [2,8].
- Deterministic rules on identical inputs: minimum weighted score, minimum score subject to B floor, A-first. No stochastic noise for these rules.
- Show means, observed min/max of scores, allocation and shortage for each style/rule; plot the comparison. The same invented score is applied to all. Identical seed/inputs reproduce identical results.
- Explicitly call these fictional styles and deterministic rules, *not* real human behavioral evidence, LLMs, or actual deployed agents. Score ordering has meaning only under the chosen objective.

## Research notebook and interpretation
- Each visitor can write an observation plus evidence to seek, add it to the current session, and download notes as JSON. An empty observation does not create a note.
- Every tab supplies a question leading to interviews, records, or alternative assumptions, not a preordained conclusion.
- No result may claim actual causal, ethical, or policy superiority based on synthetic numbers.

## Verification baseline
- Pure model tests cover default values, nonbinding/infeasible floors, conservation, zero disruption, fixed-rule benchmark alignment, reproducible noisy runs, and equal-weight gain-seeking neutrality.
- App interaction tests cover initial rendering, each tab's critical result, changed assumptions and edge captions, the notebook's empty-input guard and download output.
- Launch test verifies a running Streamlit server and real browser interaction: switch all tabs, move at least one slider, and add/download a note without runtime errors.
