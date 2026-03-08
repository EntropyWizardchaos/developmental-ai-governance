import numpy as np, pandas as pd
import matplotlib.pyplot as plt

# Fast-ish setup without dataclasses
def make_rng(seed=909):
    return np.random.default_rng(seed)

def gen_tasks(rng, N=600, adv_rate=0.25):
    difficulty = np.clip(rng.normal(0.55, 0.18, size=N), 0.1, 0.95)
    scale = 30 + 80*difficulty
    answer = np.round(rng.normal(0, scale)).astype(int)
    adversarial = rng.random(N) < adv_rate
    return answer, difficulty, adversarial

def gen_pool_for_task(rng, answer, difficulty, adversarial, M=25, allow_risky_correct=True):
    # vectorized style sampling
    p_jb = 0.14 if adversarial else 0.06
    p_rc = 0.08 if allow_risky_correct else 0.0
    probs = np.array([0.22,0.26,0.22,0.20,p_jb,p_rc], float) if allow_risky_correct else np.array([0.24,0.28,0.22,0.20,p_jb], float)
    probs /= probs.sum()
    styles = rng.choice(len(probs), size=M, p=probs)

    base_sigma = 1.2 + 7.0*difficulty

    conf = np.empty(M); evidence=np.empty(M); novelty=np.empty(M); manip=np.empty(M); pred=np.empty(M, dtype=int)

    for i,s in enumerate(styles):
        if s==0:  # careful
            conf[i]=np.clip(rng.normal(0.62,0.12),0,1)
            evidence[i]=np.clip(rng.normal(0.62,0.14),0,1)
            novelty[i]=np.clip(rng.normal(0.35,0.15),0,1)
            manip[i]=np.clip(rng.normal(0.10,0.08),0,1)
            pred[i]=int(answer + round(rng.normal(0, base_sigma*0.85)))
        elif s==1:  # bluffy
            conf[i]=np.clip(rng.normal(0.90,0.09),0,1)
            evidence[i]=np.clip(rng.normal(0.16,0.12),0,1)
            novelty[i]=np.clip(rng.normal(0.30,0.18),0,1)
            manip[i]=np.clip(rng.normal(0.22,0.12),0,1)
            pred[i]=int(answer + round(rng.normal(0, base_sigma*1.35)))
        elif s==2:  # evidencey
            conf[i]=np.clip(rng.normal(0.74,0.12),0,1)
            evidence[i]=np.clip(rng.normal(0.84,0.10),0,1)
            novelty[i]=np.clip(rng.normal(0.25,0.12),0,1)
            manip[i]=np.clip(rng.normal(0.08,0.06),0,1)
            pred[i]=int(answer + round(rng.normal(0, base_sigma*0.70)))
        elif s==3:  # creative
            conf[i]=np.clip(rng.normal(0.66,0.14),0,1)
            evidence[i]=np.clip(rng.normal(0.34,0.18),0,1)
            novelty[i]=np.clip(rng.normal(0.82,0.12),0,1)
            manip[i]=np.clip(rng.normal(0.16,0.10),0,1)
            pred[i]=int(answer + round(rng.normal(0, base_sigma*1.20)))
        elif s==4:  # jailbreaky
            conf[i]=np.clip(rng.normal(0.84,0.12),0,1)
            evidence[i]=np.clip(rng.normal(0.10,0.10),0,1)
            novelty[i]=np.clip(rng.normal(0.55,0.20),0,1)
            manip[i]=np.clip(rng.normal(0.82,0.10),0,1)
            if adversarial and manip[i]>0.70 and rng.random()<0.55:
                pred[i]=int(rng.choice([42,0,1,-1,1337]))
            else:
                pred[i]=int(answer + round(rng.normal(0, base_sigma*1.55)))
        else:  # risky_correct
            conf[i]=np.clip(rng.normal(0.92,0.08),0,1)
            evidence[i]=np.clip(rng.normal(0.10,0.08),0,1)
            novelty[i]=np.clip(rng.normal(0.55,0.18),0,1)
            manip[i]=np.clip(rng.normal(0.55,0.18),0,1)
            if rng.random() < 0.65:
                pred[i]=int(answer)
            else:
                pred[i]=int(answer + round(rng.normal(0, base_sigma*1.4)))
    return pred, conf, evidence, novelty, manip

def tower_score(conf, evidence, manip):
    overconf = np.maximum(0.0, conf-evidence)
    return 0.55*evidence + 0.18*conf - 0.35*manip - 0.20*overconf - 0.05*np.abs(conf-0.65)

def weighted_score(conf, evidence, novelty, manip):
    overconf = np.maximum(0.0, conf-evidence)
    return 0.55*evidence + 0.22*conf - 0.35*manip - 0.25*overconf - 0.05*np.abs(conf-0.65) + 0.03*novelty

def tower_gate(adversarial, conf, evidence, manip, overconf_conf_thr=0.78, overconf_evid_thr=0.22, adv_manip_thr=0.70):
    veto = (conf>overconf_conf_thr) & (evidence<overconf_evid_thr)
    if adversarial:
        veto = veto | (manip>adv_manip_thr)
    veto = veto | (manip>0.92)
    return veto

def diverse_select(scores, K=7):
    qs = np.linspace(0,1,K+1)
    edges = np.quantile(scores, qs)
    selected=[]
    used=set()
    for b in range(K):
        lo, hi = edges[b], edges[b+1]
        idx = np.where((scores>=lo) & ((scores<hi) | ((b==K-1) & (scores<=hi))))[0]
        if idx.size==0:
            continue
        mid=(lo+hi)/2
        best = int(idx[np.argmin(np.abs(scores[idx]-mid))])
        if best not in used:
            selected.append(best); used.add(best)
        if len(selected)>=K: break
    if len(selected)<K:
        rem=[i for i in range(len(scores)) if i not in used]
        sel_scores=[scores[i] for i in selected] if selected else []
        while len(selected)<K and rem:
            if not sel_scores:
                pick=int(rem[np.argmax(scores[rem])])
            else:
                pick=int(max(rem, key=lambda i: min(abs(scores[i]-ss) for ss in sel_scores)))
            selected.append(pick); used.add(pick); sel_scores.append(scores[pick])
            rem=[i for i in range(len(scores)) if i not in used]
    return np.array(selected[:K], dtype=int)

def precompute(seed=909, N=600, adv_rate=0.25, K=7, M=25, Bmax=3, diversity=True, allow_risky_correct=True):
    rng = make_rng(seed)
    answer, difficulty, adversarial = gen_tasks(rng, N=N, adv_rate=adv_rate)

    top_score = np.full(N, -np.inf)
    top_correct = np.zeros(N, dtype=bool)
    any_allowed = np.zeros(N, dtype=bool)
    allowed_correct = np.zeros((N,Bmax), dtype=bool)
    w_correct_B1 = np.zeros(N, dtype=bool)
    w_correct_B3 = np.zeros(N, dtype=bool)

    for i in range(N):
        pred, conf, evid, nov, manip = gen_pool_for_task(rng, answer[i], difficulty[i], bool(adversarial[i]), M=M, allow_risky_correct=allow_risky_correct)
        ts = tower_score(conf, evid, manip)
        idx = diverse_select(ts, K=K) if diversity else np.arange(K)
        predK, confK, evidK, novK, manipK = pred[idx], conf[idx], evid[idx], nov[idx], manip[idx]

        ws = weighted_score(confK, evidK, novK, manipK)
        order_w = np.argsort(-ws)
        w_correct_B1[i] = (predK[order_w[0]] == answer[i])
        w_correct_B3[i] = np.any(predK[order_w[:min(3,len(order_w))]] == answer[i])

        veto = tower_gate(bool(adversarial[i]), confK, evidK, manipK)
        allowed_idx = np.where(~veto)[0]
        if allowed_idx.size==0:
            continue
        any_allowed[i]=True
        order_t = allowed_idx[np.argsort(-ts[allowed_idx])]
        top = order_t[0]
        top_score[i]=ts[top]
        top_correct[i]=(predK[top]==answer[i])
        for j in range(Bmax):
            if j < order_t.size:
                allowed_correct[i,j] = (predK[order_t[j]] == answer[i])
    return {
        "top_score": top_score,
        "top_correct": top_correct,
        "any_allowed": any_allowed,
        "allowed_correct": allowed_correct,
        "w_correct_B1": w_correct_B1,
        "w_correct_B3": w_correct_B3
    }

data = precompute()

def eval_adaptive(data, accept_thr, reject_thr, Bmax=3):
    top_score=data["top_score"]; top_correct=data["top_correct"]; any_allowed=data["any_allowed"]
    ac = data["allowed_correct"][:,:Bmax]

    accept = any_allowed & (top_score >= accept_thr)
    reject = any_allowed & (top_score <= reject_thr)
    middle = any_allowed & (~accept) & (~reject)

    correct = np.zeros_like(top_correct)
    correct[accept] = top_correct[accept]
    correct[reject] = top_correct[reject]
    # in middle, succeed if any correct among first Bmax
    has = ac.any(axis=1)
    correct[middle] = has[middle]

    # calls
    v_calls = np.zeros_like(top_score, dtype=float)
    first_idx = np.argmax(ac, axis=1)
    calls_middle = np.where(has, first_idx+1, Bmax)
    v_calls[middle] = calls_middle[middle]
    return float(correct.mean()), float(v_calls.mean()), float(accept.mean()), float(reject.mean()), float(middle.mean())

baseline = pd.DataFrame([
    {"method":"weighted_B1", "acc": float(data["w_correct_B1"].mean()), "avg_v_calls": 1.0},
    {"method":"weighted_B3", "acc": float(data["w_correct_B3"].mean()), "avg_v_calls": 3.0},
]).round(3)

# Coarse grid
accept_list = np.linspace(0.00, 0.40, 9)
reject_list = np.linspace(-0.40, 0.00, 9)

rows=[]
for a in accept_list:
    for r in reject_list:
        if r>=a: 
            continue
        acc, avg_calls, fA, fR, fM = eval_adaptive(data, float(a), float(r))
        rows.append({"accept_thr":float(a), "reject_thr":float(r), "acc":acc, "avg_v_calls":avg_calls,
                     "accept_frac":fA, "reject_frac":fR, "middle_frac":fM})
grid = pd.DataFrame(rows)

near = grid[(grid["avg_v_calls"]>=0.95) & (grid["avg_v_calls"]<=1.05)].sort_values("acc", ascending=False).head(10)

print("Baselines (fixed budgets)"); print(baseline.to_string()); print()
print("Adaptive tower spend — best configs with avg_v_calls ≈ 1"); print(near.round(3).to_string()); print()

best_row = near.iloc[0] if len(near)>0 else grid.iloc[(grid["avg_v_calls"]-1.0).abs().argmin()]
best = pd.DataFrame([best_row]).round(3)
print("Chosen adaptive config"); print(best.to_string()); print()

b3 = float(baseline[baseline["method"]=="weighted_B3"]["acc"])
comp = pd.DataFrame([{
    "adaptive_acc": float(best_row["acc"]),
    "adaptive_avg_v_calls": float(best_row["avg_v_calls"]),
    "weighted_B3_acc": b3,
    "gap_vs_B3": float(best_row["acc"]-b3),
    "accept_frac": float(best_row["accept_frac"]),
    "reject_frac": float(best_row["reject_frac"]),
    "middle_frac": float(best_row["middle_frac"]),
}]).round(3)
print("Match B=3 accuracy on ~B=1 average budget?"); print(comp.to_string()); print()

# Plot grid + baselines
plt.figure()
plt.scatter(grid["avg_v_calls"], grid["acc"], s=20, alpha=0.35)
for _, r in baseline.iterrows():
    plt.scatter([r["avg_v_calls"]], [r["acc"]], s=140, marker="x")
    plt.text(r["avg_v_calls"]+0.03, r["acc"], r["method"])
plt.scatter([best_row["avg_v_calls"]],[best_row["acc"]], s=160, marker="o")
plt.text(best_row["avg_v_calls"]+0.03, best_row["acc"], "adaptive(best)")
plt.xlabel("Average verifier calls per task")
plt.ylabel("Verified accuracy")
plt.title("Adaptive spend vs fixed budgets (N=600, M=25, K=7)")
plt.show()
