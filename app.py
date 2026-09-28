"""Run with: streamlit run app.py"""

import json

import pandas as pd
import streamlit as st

from model import allocate, compare_decisions, source


st.set_page_config(page_title="Local vs global", layout="centered")
st.title("Local vs global")

example = st.segmented_control(
    "Example",
    ["Split stock", "Buy ahead", "Who decides"],
    default="Split stock",
    label_visibility="collapsed",
)

if example == "Split stock":
    supply = st.slider("Supply", 0.0, 16.0, 10.0, 0.5)
    priority = st.slider("Weight on A", 0.2, 5.0, 3.0, 0.1)
    floor = st.slider("B minimum", 0.0, 8.0, 5.0, 0.5)

    result = allocate(supply, priority, floor)
    system, local = result["system"], result["local"]

    left, right = st.columns(2)
    with left:
        st.subheader("Global")
        st.metric("A", f"{system['a']:.1f}")
        st.metric("B", f"{system['b']:.1f}")
        st.metric("Score", f"{system['score']:.1f}")
    with right:
        st.subheader("B floor")
        st.metric("A", f"{local['a']:.1f}")
        st.metric("B", f"{local['b']:.1f}")
        st.metric("Score", f"{local['score']:.1f}")

    chart = pd.DataFrame(
        {"A": [system["a"], local["a"]], "B": [system["b"], local["b"]]},
        index=["Global", "B floor"],
    )
    st.bar_chart(chart, stack=True)

    if result["binding"]:
        st.caption(f"+{local['b'] - system['b']:.1f} to B · score +{local['score'] - system['score']:.1f}")
    else:
        st.caption("Same split")

elif example == "Buy ahead":
    probability = st.slider("Disruption %", 0, 100, 50, 5, key="disruption")
    shortage_cost = st.slider("Shortage cost", 0.0, 10.0, 4.0, 0.5)

    sourcing = source(probability, shortage_cost)
    today, future = sourcing["today"], sourcing["long_term"]

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Today")
        st.metric("Local", f"{today['local_order']:.2f}")
        st.metric("Cost", f"{today['expected_total']:.2f}")
    with c2:
        st.subheader("Future-aware")
        st.metric("Local", f"{future['local_order']:.2f}")
        st.metric("Cost", f"{future['expected_total']:.2f}")

    orders = pd.DataFrame(
        {
            "Local": [today["local_order"], future["local_order"]],
            "Distant": [today["distant_order"], future["distant_order"]],
        },
        index=["Today", "Future-aware"],
    )
    st.bar_chart(orders, stack=True)

    if future["local_order"] <= 0:
        st.caption("Both buy distant")

elif example == "Who decides":
    weight = st.slider("Weight on A", 0.2, 5.0, 3.0, 0.1, key="decision_weight")
    min_b = st.slider("B minimum", 0.0, 8.0, 5.0, 0.5, key="decision_floor")
    simulated = compare_decisions(weight, min_b, seed=42, trials=100)

    rows = []
    for rule in simulated["agents"]:
        rows.append({"Rule": rule["name"], "Score": rule["score"]})
    for style in simulated["humans"]:
        rows.append({"Rule": style["name"], "Score": style["mean_score"]})
    summary = pd.DataFrame(rows).sort_values("Score")
    st.bar_chart(summary.set_index("Rule")["Score"])

with st.expander("Notes"):
    if "notes" not in st.session_state:
        st.session_state.notes = []
    observation = st.text_area("Note", label_visibility="collapsed", placeholder="Note", key="observation")
    evidence = st.text_input("Evidence", label_visibility="collapsed", placeholder="Evidence", key="evidence")
    if st.button("Add", key="add_note"):
        if observation.strip():
            st.session_state.notes.append(
                {"observation": observation.strip(), "evidence_to_seek": evidence.strip()}
            )
    if st.session_state.notes:
        st.dataframe(pd.DataFrame(st.session_state.notes), hide_index=True, width="stretch")
        st.download_button(
            "JSON",
            json.dumps(st.session_state.notes, indent=2),
            file_name="local-global-notes.json",
            mime="application/json",
        )
