"""Run with: streamlit run app.py"""

import json

import pandas as pd
import streamlit as st

from model import allocate, compare_decisions, source


st.set_page_config(page_title="Local / Global | Question laboratory", page_icon="⚖️", layout="wide")
st.title("Local / Global")
st.caption("A small question laboratory about who decides, who bears shortages, and what an 'optimal' score leaves out.")
st.info("Synthetic examples, not real supply-chain data. Change a rule, watch what moves, and note what evidence would test it.")

allocation_tab, sourcing_tab, decisions_tab = st.tabs(
    ["1 · Share scarce stock", "2 · Buy now, depend later", "3 · Compare decision rules"]
)

with allocation_tab:
    st.subheader("Who gets ten units when both places need eight?")
    st.write("The central rule minimizes a weighted shortage score. The local rule asks that B receive at least a chosen minimum. Neither score nor floor is a fact of nature.")
    a1, a2, a3 = st.columns(3)
    with a1:
        supply = st.slider("Units available", 0.0, 16.0, 10.0, 0.5)
    with a2:
        priority = st.slider("Weight on A's shortage", 0.2, 5.0, 3.0, 0.1)
    with a3:
        floor = st.slider("B's requested minimum", 0.0, 8.0, 5.0, 0.5)
    result = allocate(supply, priority, floor)
    system, local = result["system"], result["local"]
    plans = pd.DataFrame([
        {"Rule": "Lowest weighted score", "A receives": system["a"], "B receives": system["b"],
         "A unmet": system["shortage_a"], "B unmet": system["shortage_b"], "Modeled loss": system["score"]},
        {"Rule": "B minimum", "A receives": local["a"], "B receives": local["b"],
         "A unmet": local["shortage_a"], "B unmet": local["shortage_b"], "Modeled loss": local["score"]},
    ])
    st.write(f"**Central:** A {system['a']:.1f} / B {system['b']:.1f} (loss {system['score']:.1f}) · **B minimum:** A {local['a']:.1f} / B {local['b']:.1f} (loss {local['score']:.1f})")
    st.bar_chart(plans.set_index("Rule")[["A receives", "B receives"]], stack=True)
    st.dataframe(plans, hide_index=True, width="stretch")
    if result["binding"]:
        st.write(f"Meeting B's minimum moves **{local['b'] - system['b']:.1f} units** from A to B; the weighted loss rises by **{local['score'] - system['score']:.1f}**. B benefits under this measure while A receives less.")
    else:
        st.write("B's minimum does not change this allocation. Try a higher floor or different priority weight.")
    if floor > supply:
        st.caption("B's requested minimum exceeds all available stock; this model caps the attainable floor at available stock.")
    with st.expander("How is 'loss' defined?"):
        st.write("Loss = weight on A × (8 − A received)² / 2 + (8 − B received)² / 2. The central rule chooses the feasible split with the smallest value; the other rule also tries to meet B's floor. This invented score says nothing about fairness, legitimacy, or real-world welfare.")
    st.caption("Research prompt: Who chooses the weight and who can enforce the floor? Which costs are absent from the score?")

with sourcing_tab:
    st.subheader("Could today's cheaper order weaken tomorrow's option?")
    st.write("In this invented two-period model, ordering locally costs one extra unit per item today but builds future local capacity. If the distant supplier is disrupted tomorrow, it can deliver only four units.")
    b1, b2 = st.columns(2)
    with b1:
        probability = st.slider("Chance of distant disruption (%)", 0, 100, 50, 5, key="disruption")
    with b2:
        shortage_cost = st.slider("Cost of one future missing unit", 0.0, 10.0, 4.0, 0.5)
    sourcing = source(probability, shortage_cost)
    today, future = sourcing["today"], sourcing["long_term"]
    comparison = pd.DataFrame([
        {"Rule": "Today-only buyer", "Local order": today["local_order"],
         "Distant order": today["distant_order"], "Expected future shortage": today["expected_shortage"],
         "Expected modeled cost": today["expected_total"]},
        {"Rule": "Future-aware buyer", "Local order": future["local_order"],
         "Distant order": future["distant_order"], "Expected future shortage": future["expected_shortage"],
         "Expected modeled cost": future["expected_total"]},
    ])
    st.bar_chart(comparison.set_index("Rule")[["Local order", "Distant order"]], stack=True)
    st.dataframe(comparison, hide_index=True, width="stretch")
    if future["local_order"] > 0:
        st.write(f"The future-aware rule buys **{future['local_order']:.2f} locally**, paying more today but reducing expected modeled cost from **{today['expected_total']:.2f}** to **{future['expected_total']:.2f}**.")
    else:
        st.write("Under these settings, both rules buy distantly. A low disruption risk or low shortage cost can make the local-capacity effect too small to change the choice.")
    with st.expander("What is assumed?"):
        st.write("Today: buy 10 units; each local unit costs 1 extra. Tomorrow: local capacity = 2 + 0.6 × today's local order. Disrupted distant capacity = 4. Expected modeled cost = today's extra cost + disruption probability × shortage cost × max(0, 6 − local capacity). This capacity response is a hypothesis, not measured evidence.")
    st.caption("Research prompt: Does a supplier actually expand capacity with repeat orders? What contractual or policy options change the result?")

with decisions_tab:
    st.subheader("What changes when decision rules differ?")
    st.write("Four **fictional human-style rules** make slightly noisy choices; three **deterministic rules** make fixed choices. All receive 10 units to split between A and B, each needing 8, and are judged with the same weighted shortage score.")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        weight = st.slider("A's score weight", 0.2, 5.0, 3.0, 0.1, key="decision_weight")
    with c2:
        min_b = st.slider("B's minimum", 0.0, 8.0, 5.0, 0.5, key="decision_floor")
    with c3:
        trials = st.slider("Trials per style", 10, 500, 100, 10)
    with c4:
        seed = st.number_input("Random seed", min_value=0, max_value=1_000_000, value=42, step=1)
    simulated = compare_decisions(weight, min_b, seed, trials)
    rows = []
    for style in simulated["humans"]:
        rows.append({"Decision rule": style["name"] + " (fictional)", "A receives": style["average_a"],
                     "B receives": style["average_b"], "A unmet": style["shortage_a"],
                     "B unmet": style["shortage_b"], "Mean modeled loss": style["mean_score"],
                     "Lowest run": style["min_score"], "Highest run": style["max_score"]})
    for rule in simulated["agents"]:
        rows.append({"Decision rule": rule["name"], "A receives": rule["a"],
                     "B receives": rule["b"], "A unmet": rule["shortage_a"],
                     "B unmet": rule["shortage_b"], "Mean modeled loss": rule["score"],
                     "Lowest run": rule["score"], "Highest run": rule["score"]})
    scores = pd.DataFrame(rows)
    st.bar_chart(scores.set_index("Decision rule")["Mean modeled loss"])
    st.dataframe(scores, hide_index=True, width="stretch")
    st.caption(f"Lowest attainable score under these inputs: {simulated['benchmark']:.2f}. A lower score only wins under this chosen formula; ranges are min/max of seeded runs, not confidence intervals.")
    with st.expander("Inspect the seven decision rules"):
        for item in simulated["humans"] + simulated["agents"]:
            st.write(f"**{item['name']}** — {item['description']}")
        st.write("Fictional styles aim at different splits and get independent uniform noise of ±1.5 units each run. Rule-based decisions are fixed, not LLMs or deployed AI agents. Seed and trial count make the example reproducible; these runs cannot establish how people behave.")
    st.caption("Research prompt: Would actual decision-makers recognize these motives? Which benchmark would each stakeholder accept or reject?")

st.divider()
st.subheader("Research notebook")
st.write("Record a surprising result and the evidence you would seek. Notes stay in this browser session until you download them; they are not saved to a server.")
if "notes" not in st.session_state:
    st.session_state.notes = []
observation = st.text_area("Observation or counterexample", placeholder="What changed when I adjusted a weight or floor?", key="observation")
evidence = st.text_input("Evidence to look for", placeholder="Interview, contract, procurement records, operational data…", key="evidence")
if st.button("Add note", key="add_note"):
    if observation.strip():
        st.session_state.notes.append({"observation": observation.strip(), "evidence_to_seek": evidence.strip()})
        st.success("Added to this session's notebook. Download to keep it.")
    else:
        st.warning("Write an observation first.")
if st.session_state.notes:
    st.dataframe(pd.DataFrame(st.session_state.notes), hide_index=True, width="stretch")
    st.download_button("Download notes as JSON", json.dumps(st.session_state.notes, indent=2),
                       file_name="local-global-notes.json", mime="application/json")

st.caption("Scope: synthetic quantities and simplified objectives. This is a tool for forming questions, not evidence that centralized planning, local control, or AI agents succeed or fail in practice.")
