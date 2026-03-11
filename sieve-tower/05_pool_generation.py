import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from dataclasses import dataclass
from collections import Counter

# ---------- World ----------
@dataclass
class Task:
    task_id: int
    answer: int
    difficulty: float
    adversarial: bool

@dataclass
class Cand:
    cand_id: int
    predicted: int
    conf: float
    evidence: float
    novelty: float
    manip_risk: float
    style: str

def make_rng(seed=202):
    return np.random.default_rng(seed)

def gen_task(rng, tid, adv_rate=0.25):
    difficulty = float(np.clip(rng.normal(0.55, 0.18), 0.1, 0.95))
    scale = 30 + 80*difficulty
    answer = int(np.round(rng.normal(0, scale)))
    adversarial = bool(rng.random() < adv_rate)
    return Task(tid, answer, difficulty, adversarial)

def verify(task:Task, predicted:int)->bool:
    return predicted == task.answer

def gen_candidate(rng, task:Task, allow_risky_correct=True):
    base_styles = ["careful","bluffy","evidencey","creative","jailbreaky"]
    styles = base_styles + (["risky_correct"] if allow_risky_correct else [])
    p_jb = 0.14 if task.adversarial else 0.06
    p_rc = 0.08 if allow_risky_correct else 0.0
    probs = np.array([0.22,0.26,0.22,0.20,p_jb,p_rc], float) if allow_risky_correct else np.array([0.24,0.28,0.22,0.20,p_jb], float)
    probs /= probs.sum()
    style = rng.choice(styles, p=probs)

    base_sigma = 1.2 + 7.0*task.difficulty

    if style == "careful":
        conf = float(np.clip(rng.normal(0.62,0.12),0,1))
        evidence = float(np.clip(rng.normal(0.62,0.14),0,1))
        novelty = float(np.clip(rng.normal(0.35,0.15),0,1))
        manip = float(np.clip(rng.normal(0.10,0.08),0,1))
        sigma = base_sigma*0.85
        predicted = int(task.answer + int(np.round(rng.normal(0, sigma))))
    elif style == "bluffy":
        conf = float(np.clip(rng.normal(0.90,0.09),0,1))
        evidence = float(np.clip(rng.normal(0.16,0.12),0,1))
        novelty = float(np.clip(rng.normal(0.30,0.18),0,1))
        manip = float(np.clip(rng.normal(0.22,0.12),0,1))
        sigma = base_sigma*1.35
        predicted = int(task.answer + int(np.round(rng.normal(0, sigma))))
    elif style == "evidencey":
        conf = float(np.clip(rng.normal(0.74,0.12),0,1))
        evidence = float(np.clip(rng.normal(0.84,0.10),0,1))
        novelty = float(np.clip(rng.normal(0.25,0.12),0,1))
        manip = float(np.clip(rng.normal(0.08,0.06),0,1))
        sigma = base_sigma*0.70
        predicted = int(task.answer + int(np.round(rng.normal(0, sigma))))
    elif style == "creative":
        conf = float(np.clip(rng.normal(0.66,0.14),0,1))
        evidence = float(np.clip(rng.normal(0.34,0.18),0,1))
        novelty = float(np.clip(rng.normal(0.82,0.12),0,1))
        manip = float(np.clip(rng.normal(0.16,0.10),0,1))
        sigma = base_sigma*1.20
        predicted = int(task.answer + int(np.round(rng.normal(0, sigma))))
    elif style == "jailbreaky":
        conf = float(np.clip(rng.normal(0.84,0.12),0,1))
        evidence = float(np.clip(rng.normal(0.10,0.10),0,1))
        novelty = float(np.clip(rng.normal(0.55,0.20),0,1))
        manip = float(np.clip(rng.normal(0.82,0.10),0,1))
        sigma = base_sigma*1.55
        if task.adversarial and manip > 0.70 and rng.random() < 0.55:
            predicted = int(rng.choice([42, 0, 1, -1, 1337]))
        else:
            predicted = int(task.answer + int(np.round(rng.normal(0, sigma))))
    else:  # risky_correct
        conf = float(np.clip(rng.normal(0.92,0.08),0,1))
        evidence = float(np.clip(rng.normal(0.10,0.08),0,1))
        novelty = float(np.clip(rng.normal(0.55,0.18),0,1))
        manip = float(np.clip(rng.normal(0.55,0.18),0,1))
        predicted = task.answer if rng.random() < 0.65 else int(task.answer + int(np.round(rng.normal(0, base_sigma*1.4))))
    return conf, evidence, novelty, manip, predicted, style

def gen_pool(rng, task, M=35, allow_risky_correct=True):
    pool=[]
    for j in range(M):
        conf, evidence, novelty, manip, predicted, style = gen_candidate(rng, task, allow_risky_correct=allow_risky_correct)
        pool.append(Cand(j, predicted, conf, evidence, novelty, manip, style))
    return pool

# ---------- Scoring / gating ----------
def tower_score(c:Cand):
    overconf = max(0.0, c.conf - c.evidence)
    return 0.55*c.evidence + 0.18*c.conf - 0.35*c.manip_risk - 0.20*overconf - 0.05*abs(c.conf-0.65)

def weighted_score(c:Cand):
    overconf = max(0.0, c.conf - c.evidence)
    return 0.55*c.evidence + 0.22*c.conf - 0.35*c.manip_risk - 0.25*overconf - 0.05*abs(c.conf-0.65) + 0.03*c.novelty

def tower_gate(task:Task, c:Cand, overconf_conf_thr=0.78, overconf_evid_thr=0.22, adv_manip_thr=0.70):
    if c.conf > overconf_conf_thr and c.evidence < overconf_evid_thr:
        return True
    if task.adversarial and c.manip_risk > adv_manip_thr:
        return True
    if c.manip_risk > 0.92:
        return True
    return False

# ---------- Diversity-forced selection ----------
def pick_diverse_K(pool, K=7, score_fn=tower_score):
    scores = np.array([score_fn(c) for c in pool], float)
    qs = np.linspace(0, 1, K+1)
    edges = np.quantile(scores, qs)
    selected=[]
    used=set()
    for b in range(K):
        lo, hi = edges[b], edges[b+1]
        idx = [i for i,s in enumerate(scores) if (s>=lo and (s<hi or (b==K-1 and s<=hi)))]
        if not idx:
            continue
        mid = (lo+hi)/2
        best_i = min(idx, key=lambda i: abs(scores[i]-mid))
        if best_i not in used:
            selected.append(pool[best_i])
            used.add(best_i)
        if len(selected) >= K:
            break
    if len(selected) < K:
        remaining=[c for c in pool if c.cand_id not in used]
        sel_scores=[score_fn(c) for c in selected] if selected else []
        while len(selected)<K and remaining:
            if not sel_scores:
                pick = max(remaining, key=score_fn)
            else:
                pick = max(remaining, key=lambda c: min(abs(score_fn(c)-ss) for ss in sel_scores))
            selected.append(pick)
            used.add(pick.cand_id)
            sel_scores.append(score_fn(pick))
            remaining=[c for c in pool if c.cand_id not in used]
    return selected[:K]

# ---------- Limited verifier policies ----------
def limited_verifier_ranked(task, cands, B, rank_fn):
    ranked = sorted(cands, key=rank_fn, reverse=True)
    calls=0
    fallback = ranked[0]
    for c in ranked[:B]:
        calls += 1
        if verify(task, c.predicted):
            return c, calls
        fallback = c
    return fallback, calls

def tower_plus_limited_verifier(task, cands, B):
    allowed=[c for c in cands if not tower_gate(task,c)]
    veto_rate = 1.0 - (len(allowed)/len(cands))
    if not allowed:
        return min(cands, key=lambda c: c.manip_risk), 0, veto_rate
    ranked = sorted(allowed, key=tower_score, reverse=True)
    calls=0
    fallback = ranked[0]
    for c in ranked[:B]:
        calls += 1
        if verify(task, c.predicted):
            return c, calls, veto_rate
        fallback = c
    return fallback, calls, veto_rate

# ---------- Experiment ----------
def run_experiment(seed=202, N=900, adv_rate=0.25, K=7, M=35, B=2,
                   enforce_diversity=False, allow_risky_correct=True):
    rng = make_rng(seed)
    rows=[]
    for tid in range(1, N+1):
        task = gen_task(rng, tid, adv_rate=adv_rate)
        pool = gen_pool(rng, task, M=M, allow_risky_correct=allow_risky_correct)
        cands = pick_diverse_K(pool, K=K, score_fn=tower_score) if enforce_diversity else pool[:K]

        scores_pool = np.array([tower_score(c) for c in pool])
        low_cut = np.quantile(scores_pool, 0.15)
        low_correct_pool = any((tower_score(c) <= low_cut) and verify(task, c.predicted) for c in pool)
        low_correct_selected = any((tower_score(c) <= low_cut) and verify(task, c.predicted) for c in cands)

        pick_w = max(cands, key=weighted_score)
        pick_wv, calls_wv = limited_verifier_ranked(task, cands, B=B, rank_fn=weighted_score)
        pick_tv, calls_tv, veto_rate = tower_plus_limited_verifier(task, cands, B=B)

        def rec(method, pick, calls, veto=np.nan):
            rows.append({
                "method": method,
                "enforce_diversity": enforce_diversity,
                "allow_risky_correct": allow_risky_correct,
                "adversarial": task.adversarial,
                "correct": verify(task, pick.predicted),
                "adv_success": bool(task.adversarial and verify(task, pick.predicted) and pick.manip_risk<=0.70),
                "v_calls": calls,
                "veto_rate": veto,
                "low_correct_pool": low_correct_pool,
                "low_correct_selected": low_correct_selected,
            })

        rec("weighted", pick_w, 0)
        rec("limited_verifier_weighted", pick_wv, calls_wv)
        rec("tower_plus_limited_verifier", pick_tv, calls_tv, veto=veto_rate)

    df = pd.DataFrame(rows)
    agg = (df.groupby(["enforce_diversity","allow_risky_correct","method"])
             .agg(acc=("correct","mean"),
                  adv_success=("adv_success","mean"),
                  avg_v_calls=("v_calls","mean"),
                  avg_veto_rate=("veto_rate","mean"),
                  low_correct_pool_rate=("low_correct_pool","mean"),
                  low_correct_selected_rate=("low_correct_selected","mean"))
             .reset_index())

    # build scenario labels without numpy string dtype issues
    scenarios=[]
    for _, r in agg.iterrows():
        part1 = "Diversity-forced" if bool(r["enforce_diversity"]) else "Naive-K"
        part2 = "risky_correct ON" if bool(r["allow_risky_correct"]) else "risky_correct OFF"
        scenarios.append(f"{part1} | {part2}")
    agg["scenario"] = scenarios
    return df, agg

aggs=[]
for enforce_div in [False, True]:
    for risky in [False, True]:
        _, agg = run_experiment(seed=202, N=900, adv_rate=0.25, K=7, M=35, B=2,
                                enforce_diversity=enforce_div, allow_risky_correct=risky)
        aggs.append(agg)

agg_all = pd.concat(aggs, ignore_index=True)
agg_all = agg_all[["scenario","method","acc","adv_success","avg_v_calls","avg_veto_rate","low_correct_pool_rate","low_correct_selected_rate"]].round(3)

print("Forced Diversity Test — Does the Tower Still Matter?"); print(agg_all.to_string()); print()

# Plot: Accuracy by scenario
plt.figure()
scenarios = agg_all["scenario"].unique().tolist()
methods = ["weighted","limited_verifier_weighted","tower_plus_limited_verifier"]
x = np.arange(len(scenarios))
width = 0.25
for i,m in enumerate(methods):
    vals = [float(agg_all[(agg_all["scenario"]==s)&(agg_all["method"]==m)]["acc"].iloc[0]) for s in scenarios]
    plt.bar(x + (i-1)*width, vals, width, label=m)
plt.xticks(x, scenarios, rotation=15, ha="right")
plt.ylabel("Verified accuracy")
plt.title("Accuracy by Scenario (B=2 verifier checks/task, K=7, pool M=35)")
plt.legend()
plt.tight_layout()
plt.show()

# Plot: Low-stability-but-correct existence vs selection (risky_correct ON)
plt.figure()
for tag in ["Naive-K | risky_correct ON", "Diversity-forced | risky_correct ON"]:
    g = agg_all[(agg_all["scenario"]==tag) & (agg_all["method"]=="weighted")].iloc[0]
    plt.plot(["exists in pool","selected into K"], [g["low_correct_pool_rate"], g["low_correct_selected_rate"]], marker="o", label=tag)
plt.ylim(0,1)
plt.ylabel("Rate")
plt.title("Low-stability-but-correct: existence vs selection into K (risky_correct ON)")
plt.legend()
plt.show()
