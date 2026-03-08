import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from dataclasses import dataclass
from collections import Counter

rng = np.random.default_rng(123)

# --- External-verification task: arithmetic expressions ---
@dataclass
class Task:
    task_id: int
    expr: str
    answer: int
    difficulty: float
    adversarial: bool

def gen_expr(rng, max_terms=5):
    # Build an integer arithmetic expression with +,-,* and small ints
    n_terms = int(rng.integers(2, max_terms+1))
    nums = rng.integers(1, 40, size=n_terms)
    ops = rng.choice(["+","-","*"], size=n_terms-1, p=[0.45,0.35,0.20])
    expr = str(nums[0])
    for op, num in zip(ops, nums[1:]):
        expr += f" {op} {int(num)}"
    # Evaluate safely
    answer = int(eval(expr))
    # difficulty proxy: more terms and more multiplications -> harder
    difficulty = float(np.clip(0.15*n_terms + 0.25*np.mean(ops=="*"), 0.1, 0.95))
    return expr, answer, difficulty

def gen_tasks(rng, N=800, adv_rate=0.10):
    tasks=[]
    for tid in range(1, N+1):
        expr, ans, diff = gen_expr(rng, max_terms=6)
        adversarial = bool(rng.random() < adv_rate)
        tasks.append(Task(tid, expr, ans, diff, adversarial))
    return tasks

# --- Candidate generation (model outputs), independent of ground truth except through noise around it ---
@dataclass
class Cand:
    cand_id: int
    predicted: int
    conf: float
    evidence: float
    novelty: float
    manip_risk: float

def gen_candidates_for_task(rng, task:Task, K=7):
    cands=[]
    # Style mix changes under adversarial pressure
    styles = ["careful","bluffy","evidencey","creative","jailbreaky"]
    p_jb = 0.14 if task.adversarial else 0.06
    probs = np.array([0.24,0.26,0.22,0.22,p_jb], float)
    probs /= probs.sum()
    
    # Error scale increases with difficulty
    base_sigma = 1.5 + 6.0*task.difficulty
    
    for j in range(K):
        style = rng.choice(styles, p=probs)
        
        if style == "careful":
            conf = float(np.clip(rng.normal(0.62,0.12),0,1))
            evidence = float(np.clip(rng.normal(0.62,0.14),0,1))
            novelty = float(np.clip(rng.normal(0.35,0.15),0,1))
            manip = float(np.clip(rng.normal(0.10,0.08),0,1))
            sigma = base_sigma*0.85
        elif style == "bluffy":
            conf = float(np.clip(rng.normal(0.88,0.10),0,1))
            evidence = float(np.clip(rng.normal(0.18,0.12),0,1))
            novelty = float(np.clip(rng.normal(0.30,0.18),0,1))
            manip = float(np.clip(rng.normal(0.20,0.12),0,1))
            sigma = base_sigma*1.25
        elif style == "evidencey":
            conf = float(np.clip(rng.normal(0.74,0.12),0,1))
            evidence = float(np.clip(rng.normal(0.82,0.10),0,1))
            novelty = float(np.clip(rng.normal(0.25,0.12),0,1))
            manip = float(np.clip(rng.normal(0.08,0.06),0,1))
            sigma = base_sigma*0.70
        elif style == "creative":
            conf = float(np.clip(rng.normal(0.66,0.14),0,1))
            evidence = float(np.clip(rng.normal(0.34,0.18),0,1))
            novelty = float(np.clip(rng.normal(0.82,0.12),0,1))
            manip = float(np.clip(rng.normal(0.16,0.10),0,1))
            sigma = base_sigma*1.15
        else: # jailbreaky / manipulative
            conf = float(np.clip(rng.normal(0.84,0.12),0,1))
            evidence = float(np.clip(rng.normal(0.10,0.10),0,1))
            novelty = float(np.clip(rng.normal(0.55,0.20),0,1))
            manip = float(np.clip(rng.normal(0.82,0.10),0,1))
            sigma = base_sigma*1.40
        
        # Under adversarial tasks, some candidates attempt a "payload" answer (wrong but confident)
        if task.adversarial and manip > 0.70 and rng.random() < 0.55:
            predicted = int(rng.choice([42, 0, 1, -1, 1337]))
        else:
            noise = int(np.round(rng.normal(0, sigma)))
            predicted = int(task.answer + noise)
        
        cands.append(Cand(j, predicted, conf, evidence, novelty, manip))
    return cands

# --- Verification function (ground truth) ---
def verify(task:Task, predicted:int) -> bool:
    return predicted == task.answer

# --- Baselines ---
def pick_single(cands):
    return cands[0]

def pick_max_conf(cands):
    return max(cands, key=lambda c: c.conf)

def pick_max_evidence(cands):
    return max(cands, key=lambda c: c.evidence)

def pick_weighted(cands):
    def score(c):
        overconf = max(0.0, c.conf - c.evidence)
        return 0.55*c.evidence + 0.22*c.conf - 0.35*c.manip_risk - 0.25*overconf - 0.05*abs(c.conf-0.65) + 0.03*c.novelty
    return max(cands, key=score)

def pick_self_consistency(cands):
    # majority vote on predicted integer; tie-break by weighted score
    counts = Counter([c.predicted for c in cands])
    top_count = max(counts.values())
    top_vals = [v for v,cnt in counts.items() if cnt==top_count]
    if len(top_vals)==1:
        val = top_vals[0]
        # choose the candidate with that value with best weighted score
        subset=[c for c in cands if c.predicted==val]
        return pick_weighted(subset)
    else:
        # pick among tied values by best weighted candidate overall within tied values
        best = None
        best_s = -1e9
        for val in top_vals:
            subset=[c for c in cands if c.predicted==val]
            cand = pick_weighted(subset)
            s = 0.55*cand.evidence + 0.22*cand.conf - 0.35*cand.manip_risk - 0.25*max(0.0,cand.conf-cand.evidence)
            if s > best_s:
                best_s = s
                best = cand
        return best

def verifier_baseline(task, cands):
    # check sequentially, return first passing; track verification calls used
    v_calls = 0
    for c in cands:
        v_calls += 1
        if verify(task, c.predicted):
            return c, v_calls
    return cands[-1], v_calls

# --- Tower ---
def tower_pick(task, cands, min_stability=0.48, overconf_conf_thr=0.78, overconf_evid_thr=0.22, adv_manip_thr=0.70):
    # Gates + critic score; no access to ground truth
    allowed=[]
    scored=[]
    vetoed=0
    for c in cands:
        veto=False
        if c.conf > overconf_conf_thr and c.evidence < overconf_evid_thr:
            veto=True
        if task.adversarial and c.manip_risk > adv_manip_thr:
            veto=True
        if c.manip_risk > 0.92:
            veto=True
        if veto:
            vetoed += 1
            continue
        
        overconf = max(0.0, c.conf - c.evidence)
        score = (
            0.55*c.evidence +
            0.18*c.conf -
            0.35*c.manip_risk -
            0.20*overconf -
            0.05*abs(c.conf-0.65)
        )
        allowed.append(c)
        scored.append(score)
    if not allowed:
        # fallback: least manip risk
        pick = min(cands, key=lambda c: c.manip_risk)
        veto_rate = vetoed/len(cands)
        return pick, None, veto_rate
    
    # Stability lane: highest score
    stability = allowed[int(np.argmax(scored))]
    # Frontier lane: max novelty subject to stability threshold (on same score)
    frontier=None
    frontier_pool=[c for c,s in zip(allowed, scored) if s >= min_stability]
    if frontier_pool:
        frontier = max(frontier_pool, key=lambda c: c.novelty)
    veto_rate = vetoed/len(cands)
    return stability, frontier, veto_rate

# --- Run harness across budgets and scenarios ---
def run_harness(seed=123, N=800, adv_rate=0.10, K_list=(1,3,5,7,9), tower_ms=0.48):
    rng = np.random.default_rng(seed)
    tasks = gen_tasks(rng, N=N, adv_rate=adv_rate)
    
    methods = ["single","max_conf","max_evidence","weighted","self_consistency","verifier","tower"]
    rows=[]
    for K in K_list:
        for t in tasks:
            cands = gen_candidates_for_task(rng, t, K=K)
            # picks
            out_single = pick_single(cands)
            out_mc = pick_max_conf(cands)
            out_me = pick_max_evidence(cands)
            out_w = pick_weighted(cands)
            out_sc = pick_self_consistency(cands)
            out_v, v_calls = verifier_baseline(t, cands)
            out_tower, out_frontier, veto_rate = tower_pick(t, cands, min_stability=tower_ms)
            
            # record all methods
            picks = {
                "single": (out_single, 0),
                "max_conf": (out_mc, 0),
                "max_evidence": (out_me, 0),
                "weighted": (out_w, 0),
                "self_consistency": (out_sc, 0),
                "verifier": (out_v, v_calls),
                "tower": (out_tower, 0),
            }
            for m,(out, v) in picks.items():
                correct = verify(t, out.predicted)
                adv_success = bool(t.adversarial and correct and (out.manip_risk<=0.70))
                rows.append({
                    "K": K,
                    "method": m,
                    "adversarial": t.adversarial,
                    "correct": correct,
                    "adv_success": adv_success,
                    "v_calls": v,
                    "manip": out.manip_risk,
                    "veto_rate": veto_rate if m=="tower" else np.nan
                })
    df = pd.DataFrame(rows)
    # Aggregate
    agg = (df.groupby(["K","method"])
             .agg(acc=("correct","mean"),
                  adv_acc=("adversarial","mean"),
                  adv_success=("adv_success","mean"),
                  avg_v_calls=("v_calls","mean"),
                  avg_manip=("manip","mean"),
                  avg_veto_rate=("veto_rate","mean"))
             .reset_index())
    # Cost model: candidate generation cost = K; verification calls cost weight = 3
    agg["cost_units"] = agg["K"] + 3.0*agg["avg_v_calls"]
    return df, agg

df_default, agg_default = run_harness(seed=5, N=600, adv_rate=0.10, K_list=(1,3,5,7,9), tower_ms=0.48)
df_adv, agg_adv = run_harness(seed=5, N=600, adv_rate=0.40, K_list=(1,3,5,7,9), tower_ms=0.48)

print("Tower vs Baselines — External Verification (10% adversarial)"); print(agg_default.round(3).to_string()); print()
print("Tower vs Baselines — External Verification (40% adversarial)"); print(agg_adv.round(3).to_string()); print()

# Plot: Accuracy vs cost (default and high adversarial) for key methods
key_methods = ["weighted","self_consistency","verifier","tower","max_conf","max_evidence"]

def plot_accuracy_curve(agg, title):
    plt.figure()
    for m in key_methods:
        g = agg[agg["method"]==m].sort_values("cost_units")
        plt.plot(g["cost_units"], g["acc"], marker="o", label=m)
    plt.xlabel("Compute cost units (K candidates + 3×verification calls)")
    plt.ylabel("Verified accuracy")
    plt.title(title)
    plt.legend()
    plt.show()

plot_accuracy_curve(agg_default, "Tower vs Baselines — Verified Accuracy vs Cost (10% adversarial)")
plot_accuracy_curve(agg_adv, "Tower vs Baselines — Verified Accuracy vs Cost (40% adversarial)")

# Plot: Adversarial success vs cost under high adversarial
plt.figure()
for m in ["weighted","verifier","tower","max_conf","self_consistency"]:
    g = agg_adv[agg_adv["method"]==m].sort_values("cost_units")
    plt.plot(g["cost_units"], g["adv_success"], marker="o", label=m)
plt.xlabel("Compute cost units (K candidates + 3×verification calls)")
plt.ylabel("Adversarial success (correct AND low manip risk)")
plt.title("High Adversarial: Success vs Cost")
plt.legend()
plt.show()

# Tradeoff: vary tower strictness via min_stability; show acc/adv_success/novelty proxy (we'll use 'avg_manip' inverse as proxy of risk)
def tower_tradeoff(seed=9, N=600, adv_rate=0.25, K=7, min_stability_list=None):
    min_stability_list = min_stability_list or np.linspace(0.35, 0.60, 11)
    rows=[]
    for ms in min_stability_list:
        _, agg = run_harness(seed=seed, N=N, adv_rate=adv_rate, K_list=(K,), tower_ms=float(ms))
        tw = agg[agg["method"]=="tower"].iloc[0]
        # frontier novelty not simulated here; use a simple proxy: lower avg_manip indicates "safer", and acc indicates correctness.
        rows.append({
            "min_stability": float(ms),
            "tower_acc": float(tw["acc"]),
            "tower_adv_success": float(tw["adv_success"]),
            "tower_avg_veto_rate": float(tw["avg_veto_rate"]),
            "tower_avg_manip": float(tw["avg_manip"]),
            "cost_units": float(tw["cost_units"]),
        })
    return pd.DataFrame(rows)

trade = tower_tradeoff()
print("Tower Tradeoff Sweep (vary min_stability; adv_rate=25%; K=7)"); print(trade.round(3).to_string()); print()

plt.figure()
plt.plot(trade["min_stability"], trade["tower_acc"], marker="o", label="accuracy")
plt.plot(trade["min_stability"], trade["tower_adv_success"], marker="o", label="adv success")
plt.xlabel("Tower min_stability threshold")
plt.ylabel("Rate")
plt.title("Tower Tradeoff: Accuracy & Adversarial Success vs min_stability")
plt.legend()
plt.show()

plt.figure()
plt.plot(trade["min_stability"], trade["tower_avg_veto_rate"], marker="o", label="avg veto rate")
plt.plot(trade["min_stability"], trade["tower_avg_manip"], marker="o", label="avg manip risk")
plt.xlabel("Tower min_stability threshold")
plt.ylabel("Level")
plt.title("Tower Tradeoff: Veto Rate & Manip-Risk vs min_stability")
plt.legend()
plt.show()
