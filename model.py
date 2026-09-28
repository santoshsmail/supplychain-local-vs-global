"""Small synthetic models for exploring local and system-wide decisions.

These are illustrative rules, not empirical estimates or deployed AI behavior.
"""

import random
from statistics import mean


def allocate(supply=10.0, priority=3.0, floor=5.0):
    """Split available units between A and B, each needing eight."""
    supply = max(0.0, min(16.0, float(supply)))
    weight = max(0.1, float(priority))
    floor = max(0.0, min(8.0, float(floor)))
    low = max(0.0, supply - 8.0)
    high = min(8.0, supply)
    optimum = (weight * 8.0 - 8.0 + supply) / (weight + 1.0)
    system_a = max(low, min(high, optimum))
    local_a = max(low, min(system_a, supply - min(floor, supply)))

    def plan(a):
        b = supply - a
        return {
            "a": a, "b": b, "shortage_a": 8.0 - a,
            "shortage_b": 8.0 - b,
            "score": weight * (8.0 - a) ** 2 / 2 + (8.0 - b) ** 2 / 2,
        }

    return {
        "system": plan(system_a), "local": plan(local_a), "supply": supply,
        "priority": weight, "floor": floor, "binding": system_a - local_a > 1e-8,
    }


def source(probability=50.0, shortage_cost=4.0):
    """Compare today's purchasing cost with an invented future-capacity effect."""
    p = max(0.0, min(100.0, float(probability))) / 100.0
    cost = max(0.0, float(shortage_cost))

    def plan(local_order):
        capacity = 2.0 + 0.6 * local_order
        shortage = max(0.0, 10.0 - 4.0 - capacity)
        return {
            "local_order": local_order, "distant_order": 10.0 - local_order,
            "capacity": capacity, "shortage": shortage,
            "today_extra_cost": local_order, "expected_shortage": p * shortage,
            "expected_total": local_order + p * cost * shortage,
        }

    # Linear on either side of the point where the shortage reaches zero.
    options = [plan(y) for y in (0.0, 10.0, 20.0 / 3.0)]
    return {
        "today": options[0], "long_term": min(options, key=lambda x: x["expected_total"]),
        "probability": p, "shortage_cost": cost,
    }


def compare_decisions(priority=3.0, floor=5.0, seed=42, trials=100):
    """Score fictional noisy styles and fixed rules on the exact same inputs."""
    base = allocate(priority=priority, floor=floor)
    weight = base["priority"]
    rng = random.Random(int(seed))
    trials = max(1, min(1000, int(trials)))

    def decision(a):
        a = max(2.0, min(8.0, a))
        b = 10.0 - a
        return {
            "a": a, "b": b, "shortage_a": 8.0 - a, "shortage_b": 8.0 - b,
            "score": weight * (8.0 - a) ** 2 / 2 + (8.0 - b) ** 2 / 2,
        }

    targets = (
        ("Self-interested", 8.0, "Favors A, the imagined decision-maker's community."),
        ("Gain-seeking", 8.0 if weight > 1 else 2.0 if weight < 1 else 5.0,
         "Favors whichever community has the higher score weight."),
        ("Systematic", base["system"]["a"], "Aims for the lowest weighted score."),
        ("Empathetic", 5.0, "Aims to leave equal shortages in A and B."),
    )
    humans = []
    for name, target, description in targets:
        runs = [decision(target + rng.uniform(-1.5, 1.5)) for _ in range(trials)]
        humans.append({
            "name": name, "description": description, "scores": [r["score"] for r in runs],
            "average_a": mean(r["a"] for r in runs),
            "average_b": mean(r["b"] for r in runs),
            "shortage_a": mean(r["shortage_a"] for r in runs),
            "shortage_b": mean(r["shortage_b"] for r in runs),
            "mean_score": mean(r["score"] for r in runs),
            "min_score": min(r["score"] for r in runs),
            "max_score": max(r["score"] for r in runs),
        })
    agents = [
        {"name": "Central-score rule", "description": "Minimizes weighted shortage score.",
         **decision(base["system"]["a"])},
        {"name": "B-minimum rule", "description": "Minimizes the score while meeting B's floor.",
         **decision(base["local"]["a"])},
        {"name": "A-first rule", "description": "Fills A before sending the remainder to B.",
         **decision(8.0)},
    ]
    return {"humans": humans, "agents": agents, "benchmark": base["system"]["score"]}
