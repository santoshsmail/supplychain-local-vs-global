# Local / Global — question laboratory

A small **Python Streamlit** visualization for exploring tensions between aggregate scoring and local decision rights. All numbers and decision styles are synthetic. The app asks research questions; it does not conclude that one governance style is better.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate             # Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
streamlit run app.py
```

Open the local URL printed by Streamlit, usually `http://localhost:8501`.

## Test

```bash
python -m unittest discover -s tests -p 'test_*.py' -v
```

The tests cover model defaults/edges and Streamlit interactions. The [baseline specification](doc/streamlit-spec.md) defines the intended behavior.

## Explore

1. **Share scarce stock:** vary supply, A's weight, and B's minimum; compare allocations and unmet need.
2. **Buy now, depend later:** vary disruption chance and shortage cost; compare today-only and future-aware purchases under an assumed capacity response.
3. **Compare decision rules:** seeded repeated runs for four fictional styles versus three deterministic rules on identical inputs.
4. **Research notebook:** add observations and evidence to seek; download JSON before ending the session. No server-side persistence.

A lower modeled loss is only lower under the explicitly chosen formula. These toy rules do not describe actual people's motives, real supplier behavior, or deployed AI agents. Neither the outcomes nor the simulations are empirical evidence.
