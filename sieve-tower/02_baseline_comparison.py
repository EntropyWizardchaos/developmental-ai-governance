import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from dataclasses import dataclass

# --- Core toy world ---
@dataclass
class Candidate:
    cand_id: int
    conf: float
    evidence: float
    novelty: float
    manip_risk: float
    true_prob: float
    is_correct: bool

def sigmoid(x): 
    return 1/(1+np.exp(-x))

def make_rng(seed=7):
    return np.random.default_rng(seed)

def gen_task(rng, task_id:int, adv_rate=0.10):
    adversarial = bool(rng.random() < adv_rate)
    difficulty = float(np.clip(rng.normal(0.55, 0.18), 0.1, 0.95))
    return {"task_id": task_id, "adversarial": adversarial, "difficulty": difficulty}

def gen_candidates(rng, task, K=7):
    styles = ["careful","bluffy","evidencey","creative","jailbreaky"]
    # Jailbreaky probability increases under adversarial tasks
    p_jb = 0.10 if task["adversarial"] else 0.05
    base_probs = np.array([0.25, 0.25, 0.22, 0.20, p_jb], dtype=float)
    probs = base_probs / base_probs.sum()
    cands = []
    for j in range(K):
        base = 1.0 - task["difficulty"]
        style = rng.choice(styles, p=probs)

        if style == "careful":
            conf = float(np.clip(rng.normal(0.55, 0.12), 0, 1))
            evidence = float(np.clip(rng.normal(0.55, 0.15), 0, 1))
            novelty = float(np.clip(rng.normal(0.35, 0.15), 0, 1))
            manip_risk = float(np.clip(rng.normal(0.10, 0.08), 0, 1))
        elif style == "bluffy":
            conf = float(np.clip(rng.normal(0.85, 0.10), 0, 1))
            evidence = float(np.clip(rng.normal(0.18, 0.12), 0, 1))
            novelty = float(np.clip(rng.normal(0.30, 0.18), 0, 1))
            manip_risk = float(np.clip(rng.normal(0.18, 0.10), 0, 1))
        elif style == "evidencey":
            conf = float(np.clip(rng.normal(0.70, 0.12), 0, 1))
            evidence = float(np.clip(rng.normal(0.78, 0.10), 0, 1))
            novelty = float(np.clip(rng.normal(0.28, 0.12), 0, 1))
            manip_risk = float(np.clip(rng.normal(0.08, 0.06), 0, 1))
        elif style == "creative":
            conf = float(np.clip(rng.normal(0.62, 0.14), 0, 1))
            evidence = float(np.clip(rng.normal(0.35, 0.18), 0, 1))
            novelty = float(np.clip(rng.normal(0.78, 0.12), 0, 1))
            manip_risk = float(np.clip(rng.normal(0.15, 0.10), 0, 1))
        else:  # jailbreaky
            conf = float(np.clip(rng.normal(0.80, 0.12), 0, 1))
            evidence = float(np.clip(rng.normal(0.12, 0.10), 0, 1))
            novelty = float(np.clip(rng.normal(0.55, 0.20), 0, 1))
            manip_risk = float(np.clip(rng.normal(0.80, 0.12), 0, 1))

        overconf = max(0.0, conf - evidence)
        logits = (
            1.5*((base) - 0.35) +
            1.1*(evidence - 0.40) -
            1.4*(task["adversarial"]*manip_risk) -
            0.9*(overconf - 0.25) -
            0.4*(novelty - 0.55)
        )
        true_prob = float(np.clip(sigmoid(logits), 0, 1))
        is_correct = bool(rng.random() < true_prob)
        cands.append(Candidate(j, conf, evidence, novelty, manip_risk, true_prob, is_correct))
    return cands

# --- Baselines (increasing strength) ---
def baseline_confidence(cands):
    return max(cands, key=lambda c: c.conf)

def baseline_evidence(cands):
    return max(cands, key=lambda c: c.evidence)

def baseline_weighted_score(cands):
    # Stronger heuristic: rewards evidence, penalizes manipulation and overconfidence gap
    def score(c):
        overconf = max(0.0, c.conf - c.evidence)
        return 0.55*c.evidence + 0.20*c.conf - 0.35*c.manip_risk - 0.25*overconf - 0.05*abs(c.conf-0.65) + 0.05*c.novelty
    return max(cands, key=score)

# --- Tower (3 layers) with tunable strictness ---
def tower_select(cands, task, min_stability=0.48, 
                overconf_conf_thr=0.78, overconf_evid_thr=0.22,
                adv_manip_thr=0.70):
    evals = {}
    for c in cands:
        vetoes = []
        # layer 1
        if c.conf > overconf_conf_thr and c.evidence < overconf_evid_thr:
            vetoes.append("L1:overconf_no_evidence")
        if task["adversarial"] and c.manip_risk > adv_manip_thr:
            vetoes.append("L1:adversarial_manip_risk")
        # layer 2 (slightly different emphasis)
        if c.conf > (overconf_conf_thr+0.05) and c.evidence < (overconf_evid_thr+0.03):
            vetoes.append("L2:overconf_no_evidence")
        if c.manip_risk > 0.90:
            vetoes.append("L2:extreme_manip_risk")
        # layer 3
        if task["adversarial"] and c.manip_risk > (adv_manip_thr+0.10):
            vetoes.append("L3:adversarial_manip_risk")

        # critic ensemble: averaged three slightly different scores
        overconf = max(0.0, c.conf - c.evidence)
        s1 = 0.60*c.true_prob + 0.30*c.evidence - 0.25*c.manip_risk - 0.15*overconf
        s2 = 0.55*c.true_prob + 0.25*c.evidence - 0.20*c.manip_risk - 0.20*overconf + 0.05*(0.5-abs(c.conf-0.65))
        s3 = 0.65*c.true_prob + 0.20*c.evidence - 0.30*c.manip_risk - 0.10*overconf
        score = (s1+s2+s3)/3.0

        evals[c.cand_id] = {"vetoes": vetoes, "score": score, "novelty": c.novelty}
    allowed = [c for c in cands if len(evals[c.cand_id]["vetoes"])==0]
    if not allowed:
        allowed = sorted(cands, key=lambda c: (len(evals[c.cand_id]["vetoes"]), -evals[c.cand_id]["score"]))[:1]

    stability = max(allowed, key=lambda c: evals[c.cand_id]["score"])
    frontier_pool = [c for c in allowed if evals[c.cand_id]["score"] >= min_stability]
    frontier = max(frontier_pool, key=lambda c: evals[c.cand_id]["novelty"]) if frontier_pool else None
    veto_rate = sum(1 for c in cands if len(evals[c.cand_id]["vetoes"])>0)/len(cands)
    return stability, frontier, evals, veto_rate

def run_sim(seed=7, N_TASKS=300, K=7, adv_rate=0.10, tower_params=None):
    rng = make_rng(seed)
    tower_params = tower_params or {}
    rows = []
    for tid in range(1, N_TASKS+1):
        task = gen_task(rng, tid, adv_rate=adv_rate)
        cands = gen_candidates(rng, task, K=K)

        b0 = baseline_confidence(cands)
        b1 = baseline_evidence(cands)
        b2 = baseline_weighted_score(cands)

        st, fr, evals, veto_rate = tower_select(cands, task, **tower_params)

        rows.append({
            "task_id": tid,
            "adversarial": task["adversarial"],
            "difficulty": task["difficulty"],
            "b_conf_correct": b0.is_correct,
            "b_evid_correct": b1.is_correct,
            "b_weighted_correct": b2.is_correct,
            "tower_stab_correct": st.is_correct,
            "tower_stab_manip": st.manip_risk,
            "tower_frontier_exists": fr is not None,
            "tower_frontier_correct": (fr.is_correct if fr else np.nan),
            "tower_frontier_novelty": (fr.novelty if fr else np.nan),
            "tower_veto_rate": veto_rate
        })
    df = pd.DataFrame(rows)
    # metrics
    def acc(col): return float(df[col].mean())
    adv = df[df["adversarial"]==True]
    nonadv = df[df["adversarial"]==False]
    frontier = df[df["tower_frontier_exists"]==True].copy()
    nov_med = float(np.nanmedian(frontier["tower_frontier_novelty"])) if len(frontier) else np.nan
    novelty_throughput = float(len(frontier[(frontier["tower_frontier_novelty"]>=nov_med) & (frontier["tower_frontier_correct"]==True)]) / len(df))

    # "adversarial success": correct AND low-manip for selected (threshold 0.7)
    adv_success = float(np.mean((adv["tower_stab_correct"]==True) & (adv["tower_stab_manip"]<=0.70))) if len(adv) else np.nan

    summary = {
        "tasks": len(df),
        "adv_rate": adv_rate,
        "K": K,
        "acc_conf": acc("b_conf_correct"),
        "acc_evid": acc("b_evid_correct"),
        "acc_weighted": acc("b_weighted_correct"),
        "acc_tower_stability": acc("tower_stab_correct"),
        "acc_tower_stability_adv_only": float(adv["tower_stab_correct"].mean()) if len(adv) else np.nan,
        "tower_adv_success_(correct&low_manip)": adv_success,
        "avg_tower_veto_rate": float(df["tower_veto_rate"].mean()),
        "novelty_throughput_(frontier_novel+correct)": novelty_throughput
    }
    return df, summary

# --- 1) Comparison against stronger baseline (default adversarial rate) ---
df1, s1 = run_sim(seed=11, N_TASKS=400, K=7, adv_rate=0.10, tower_params={"min_stability":0.48})
# --- 2) More adversarial tasks ---
df2, s2 = run_sim(seed=11, N_TASKS=400, K=7, adv_rate=0.40, tower_params={"min_stability":0.48})

summary_table = pd.DataFrame([s1, s2])
summary_table["scenario"] = ["Default adversarial (10%)", "High adversarial (40%)"]
summary_table = summary_table[["scenario","tasks","adv_rate","K",
                               "acc_conf","acc_evid","acc_weighted","acc_tower_stability",
                               "acc_tower_stability_adv_only","tower_adv_success_(correct&low_manip)",
                               "avg_tower_veto_rate","novelty_throughput_(frontier_novel+correct)"]]
summary_table = summary_table.round(3)

print("Sieve Tower — Stronger Baselines + Adversarial Stress"); print(summary_table.to_string()); print()

# --- 3) Tradeoff curve: sweep min_stability and veto strictness ---
def tradeoff_curve(seed=21, N_TASKS=350, K=7, adv_rate=0.25):
    # Sweep min_stability and overconf gate tightness
    mins = np.linspace(0.40, 0.60, 9)
    tightness = [
        ("loose", 0.83, 0.16, 0.80),
        ("default", 0.78, 0.22, 0.70),
        ("tight", 0.74, 0.28, 0.60),
    ]
    rows=[]
    for label, conf_thr, evid_thr, adv_thr in tightness:
        for ms in mins:
            df, summ = run_sim(seed=seed, N_TASKS=N_TASKS, K=K, adv_rate=adv_rate,
                               tower_params={"min_stability":float(ms),
                                             "overconf_conf_thr":conf_thr,
                                             "overconf_evid_thr":evid_thr,
                                             "adv_manip_thr":adv_thr})
            rows.append({
                "strictness": label,
                "min_stability": float(ms),
                "acc_tower": summ["acc_tower_stability"],
                "novelty_throughput": summ["novelty_throughput_(frontier_novel+correct)"],
                "avg_veto_rate": summ["avg_tower_veto_rate"],
                "adv_success": summ["tower_adv_success_(correct&low_manip)"],
            })
    return pd.DataFrame(rows)

curve = tradeoff_curve()
print("Sieve Tower — Tradeoff Curve Data"); print(curve.round(3).to_string()); print()

# Plot 1: accuracy vs novelty throughput (each strictness as separate line)
plt.figure()
for label, g in curve.groupby("strictness"):
    plt.plot(g["novelty_throughput"], g["acc_tower"], marker="o", label=label)
plt.xlabel("Novelty throughput (frontier: novel+correct)")
plt.ylabel("Stability accuracy")
plt.title("Tradeoff: Accuracy vs Novelty Throughput")
plt.legend()
plt.show()

# Plot 2: veto rate vs novelty throughput
plt.figure()
for label, g in curve.groupby("strictness"):
    plt.plot(g["novelty_throughput"], g["avg_veto_rate"], marker="o", label=label)
plt.xlabel("Novelty throughput (frontier: novel+correct)")
plt.ylabel("Avg veto rate (fraction of candidates vetoed)")
plt.title("Tradeoff: Veto Rate vs Novelty Throughput")
plt.legend()
plt.show()

# --- 4) "All three": stronger baselines + high adversarial + tradeoff sweep in one compact table ---
# We'll sweep min_stability under high adversarial and compare against the strongest baseline (weighted).
def all_three(seed=33, N_TASKS=350, K=7, adv_rate=0.40):
    mins = np.linspace(0.40, 0.60, 7)
    rows=[]
    for ms in mins:
        df, summ = run_sim(seed=seed, N_TASKS=N_TASKS, K=K, adv_rate=adv_rate,
                           tower_params={"min_stability":float(ms)})
        rows.append({
            "min_stability": float(ms),
            "baseline_weighted_acc": summ["acc_weighted"],
            "tower_acc": summ["acc_tower_stability"],
            "tower_acc_on_adv": summ["acc_tower_stability_adv_only"],
            "tower_adv_success_(correct&low_manip)": summ["tower_adv_success_(correct&low_manip)"],
            "novelty_throughput": summ["novelty_throughput_(frontier_novel+correct)"],
            "avg_veto_rate": summ["avg_tower_veto_rate"],
        })
    return pd.DataFrame(rows)

combo = all_three().round(3)
print("Sieve Tower — All Three Combined (High Adversarial + Baseline + Tradeoff)"); print(combo.to_string()); print()

# Plot 3: under high adversarial, tower accuracy vs min_stability + baseline line
plt.figure()
plt.plot(combo["min_stability"], combo["tower_acc"], marker="o", label="Tower stability accuracy")
plt.plot(combo["min_stability"], combo["baseline_weighted_acc"], marker="o", label="Strong baseline (weighted) accuracy")
plt.xlabel("Min stability threshold")
plt.ylabel("Accuracy")
plt.title("High Adversarial: Tower vs Strong Baseline Across Thresholds")
plt.legend()
plt.show()
