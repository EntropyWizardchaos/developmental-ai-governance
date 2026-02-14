"""
Sieve Spiral v0.1 - Centrifuge vs Tower Comparison
Harley Robinson & Claude (Axiom)

Core insight from experiments:
- Bottom quartile (low stability) verifies at 0.65 success rate
- Top quartile (high stability) verifies at 0.48 success rate
- The tower is inversely correlated with correctness in edge cases

Spiral hypothesis:
- Don't use stability as accept/reject
- Use stability as ROUTING: low stability -> outer rim -> heavy verification
- High stability -> inner core -> trust accumulated wisdom
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def make_rng(seed=1111):
    return np.random.default_rng(seed)

def gen_tasks(rng, N=1200, adv_rate=0.25):
    difficulty = np.clip(rng.normal(0.55, 0.18, size=N), 0.1, 0.95)
    scale = 30 + 80*difficulty
    answer = np.round(rng.normal(0, scale)).astype(int)
    adversarial = rng.random(N) < adv_rate
    return answer, difficulty, adversarial

def gen_pool_for_task(rng, answer, difficulty, adversarial, M=40):
    p_jb = 0.14 if adversarial else 0.06
    p_rc = 0.10  # risky_correct style
    probs = np.array([0.22, 0.26, 0.22, 0.20, p_jb, p_rc], float)
    probs /= probs.sum()
    styles = rng.choice(len(probs), size=M, p=probs)
    
    base_sigma = 1.2 + 7.0*difficulty
    
    conf = np.empty(M)
    evidence = np.empty(M)
    novelty = np.empty(M)
    manip = np.empty(M)
    pred = np.empty(M, dtype=int)
    
    for i, s in enumerate(styles):
        if s == 0:  # careful
            conf[i] = np.clip(rng.normal(0.62, 0.12), 0, 1)
            evidence[i] = np.clip(rng.normal(0.62, 0.14), 0, 1)
            novelty[i] = np.clip(rng.normal(0.35, 0.15), 0, 1)
            manip[i] = np.clip(rng.normal(0.10, 0.08), 0, 1)
            pred[i] = int(answer + round(rng.normal(0, base_sigma*0.85)))
        elif s == 1:  # bluffy
            conf[i] = np.clip(rng.normal(0.90, 0.09), 0, 1)
            evidence[i] = np.clip(rng.normal(0.16, 0.12), 0, 1)
            novelty[i] = np.clip(rng.normal(0.30, 0.18), 0, 1)
            manip[i] = np.clip(rng.normal(0.22, 0.12), 0, 1)
            pred[i] = int(answer + round(rng.normal(0, base_sigma*1.35)))
        elif s == 2:  # evidencey
            conf[i] = np.clip(rng.normal(0.74, 0.12), 0, 1)
            evidence[i] = np.clip(rng.normal(0.84, 0.10), 0, 1)
            novelty[i] = np.clip(rng.normal(0.25, 0.12), 0, 1)
            manip[i] = np.clip(rng.normal(0.08, 0.06), 0, 1)
            pred[i] = int(answer + round(rng.normal(0, base_sigma*0.70)))
        elif s == 3:  # creative
            conf[i] = np.clip(rng.normal(0.66, 0.14), 0, 1)
            evidence[i] = np.clip(rng.normal(0.34, 0.18), 0, 1)
            novelty[i] = np.clip(rng.normal(0.82, 0.12), 0, 1)
            manip[i] = np.clip(rng.normal(0.16, 0.10), 0, 1)
            pred[i] = int(answer + round(rng.normal(0, base_sigma*1.20)))
        elif s == 4:  # jailbreaky
            conf[i] = np.clip(rng.normal(0.84, 0.12), 0, 1)
            evidence[i] = np.clip(rng.normal(0.10, 0.10), 0, 1)
            novelty[i] = np.clip(rng.normal(0.55, 0.20), 0, 1)
            manip[i] = np.clip(rng.normal(0.82, 0.10), 0, 1)
            if adversarial and manip[i] > 0.70 and rng.random() < 0.55:
                pred[i] = int(rng.choice([42, 0, 1, -1, 1337]))
            else:
                pred[i] = int(answer + round(rng.normal(0, base_sigma*1.55)))
        else:  # risky_correct
            conf[i] = np.clip(rng.normal(0.92, 0.08), 0, 1)
            evidence[i] = np.clip(rng.normal(0.10, 0.08), 0, 1)
            novelty[i] = np.clip(rng.normal(0.55, 0.18), 0, 1)
            manip[i] = np.clip(rng.normal(0.55, 0.18), 0, 1)
            if rng.random() < 0.60:
                pred[i] = int(answer)
            else:
                pred[i] = int(answer + round(rng.normal(0, base_sigma*1.4)))
    
    return pred, conf, evidence, novelty, manip

def tower_score(conf, evidence, manip):
    """Original tower scoring - used for both systems"""
    overconf = np.maximum(0.0, conf - evidence)
    return 0.55*evidence + 0.18*conf - 0.35*manip - 0.20*overconf - 0.05*np.abs(conf-0.65)

def tower_gate(adversarial, conf, evidence, manip):
    """Hard veto rules"""
    veto = (conf > 0.78) & (evidence < 0.22)
    if adversarial:
        veto = veto | (manip > 0.70)
    veto = veto | (manip > 0.92)
    return veto

# =============================================================================
# TOWER (STACK) - Original architecture
# =============================================================================
def tower_select(pred, conf, evidence, manip, adversarial, answer, B_total):
    """
    Tower logic: Filter by veto, rank by score, verify top-B
    Returns: success (bool), verification_calls (int)
    """
    score = tower_score(conf, evidence, manip)
    veto = tower_gate(adversarial, conf, evidence, manip)
    
    allowed_idx = np.where(~veto)[0]
    if allowed_idx.size == 0:
        # Fallback: pick lowest manip
        pick = int(np.argmin(manip))
        return (pred[pick] == answer), 0
    
    # Rank allowed by score descending
    order = allowed_idx[np.argsort(-score[allowed_idx])]
    
    # Verify top-B
    calls = 0
    for idx in order[:B_total]:
        calls += 1
        if pred[idx] == answer:
            return True, calls
    
    return False, calls

# =============================================================================
# SPIRAL (CENTRIFUGE) - New architecture
# =============================================================================
def spiral_select(pred, conf, evidence, manip, adversarial, answer, B_total,
                  inner_threshold=0.75, outer_threshold=0.25):
    """
    Spiral logic: 
    - Compute stability score
    - Route by score quantile:
      - Inner core (high stability): trust without verification
      - Middle band: light verification
      - Outer rim (low stability): heavy verification
    
    Key insight: low stability candidates are MORE likely correct when verified
    So we INVERT verification priority
    """
    score = tower_score(conf, evidence, manip)
    veto = tower_gate(adversarial, conf, evidence, manip)
    
    # Compute quantiles for routing
    q_inner = np.quantile(score, inner_threshold)
    q_outer = np.quantile(score, outer_threshold)
    
    # Route candidates
    inner_idx = np.where((score >= q_inner) & (~veto))[0]  # High stability, trust
    middle_idx = np.where((score >= q_outer) & (score < q_inner) & (~veto))[0]
    outer_idx = np.where((score < q_outer) & (~veto))[0]  # Low stability, verify heavily
    
    # Also track vetoed but potentially recoverable
    vetoed_idx = np.where(veto)[0]
    
    calls = 0
    
    # OUTER RIM FIRST - this is the inversion
    # These are the "risky" candidates that your data shows are actually more often correct
    # Allocate most verification budget here
    outer_budget = int(B_total * 0.6)  # 60% of budget to outer rim
    if outer_idx.size > 0:
        # Sort by novelty descending (frontier candidates)
        outer_order = outer_idx[np.argsort(-conf[outer_idx])]  # or novelty
        for idx in outer_order[:outer_budget]:
            calls += 1
            if pred[idx] == answer:
                return True, calls, "outer"
    
    # MIDDLE BAND - moderate verification
    middle_budget = int(B_total * 0.3)  # 30% to middle
    if middle_idx.size > 0:
        middle_order = middle_idx[np.argsort(-score[middle_idx])]
        for idx in middle_order[:middle_budget]:
            calls += 1
            if pred[idx] == answer:
                return True, calls, "middle"
    
    # INNER CORE - trust the top pick, minimal verification
    inner_budget = B_total - outer_budget - middle_budget  # ~10%
    if inner_idx.size > 0:
        inner_order = inner_idx[np.argsort(-score[inner_idx])]
        # Take top inner candidate as "trusted" - only verify if budget allows
        if inner_budget > 0:
            for idx in inner_order[:inner_budget]:
                calls += 1
                if pred[idx] == answer:
                    return True, calls, "inner"
        else:
            # Trust without verification
            if pred[inner_order[0]] == answer:
                return True, 0, "inner_trusted"
    
    # Fallback: check vetoed candidates with remaining budget (recovery attempt)
    remaining = B_total - calls
    if remaining > 0 and vetoed_idx.size > 0:
        # Even vetoed candidates might be correct - this is the "dig up bodies" logic
        vetoed_order = vetoed_idx[np.argsort(-evidence[vetoed_idx])]  # prioritize by evidence
        for idx in vetoed_order[:remaining]:
            calls += 1
            if pred[idx] == answer:
                return True, calls, "recovered"
    
    return False, calls, "failed"

# =============================================================================
# COMPARISON EXPERIMENT
# =============================================================================
def run_comparison(seed=1111, N=1200, M=40, B_total=5, adv_rate=0.25):
    rng = make_rng(seed)
    answer, difficulty, adversarial = gen_tasks(rng, N=N, adv_rate=adv_rate)
    
    tower_results = []
    spiral_results = []
    
    for i in range(N):
        pred, conf, evid, nov, manip = gen_pool_for_task(
            rng, int(answer[i]), float(difficulty[i]), bool(adversarial[i]), M=M
        )
        
        # Tower (stack)
        t_success, t_calls = tower_select(
            pred, conf, evid, manip, bool(adversarial[i]), int(answer[i]), B_total
        )
        tower_results.append({
            "success": t_success,
            "calls": t_calls,
            "adversarial": bool(adversarial[i]),
            "difficulty": float(difficulty[i])
        })
        
        # Spiral (centrifuge)
        s_success, s_calls, s_zone = spiral_select(
            pred, conf, evid, manip, bool(adversarial[i]), int(answer[i]), B_total
        )
        spiral_results.append({
            "success": s_success,
            "calls": s_calls,
            "zone": s_zone,
            "adversarial": bool(adversarial[i]),
            "difficulty": float(difficulty[i])
        })
    
    tower_df = pd.DataFrame(tower_results)
    spiral_df = pd.DataFrame(spiral_results)
    
    return tower_df, spiral_df

def analyze_results(tower_df, spiral_df):
    """Generate comparison metrics"""
    
    results = {
        "metric": [],
        "tower": [],
        "spiral": [],
        "delta": []
    }
    
    # Overall accuracy
    t_acc = tower_df["success"].mean()
    s_acc = spiral_df["success"].mean()
    results["metric"].append("Overall Accuracy")
    results["tower"].append(t_acc)
    results["spiral"].append(s_acc)
    results["delta"].append(s_acc - t_acc)
    
    # Average verification calls
    t_calls = tower_df["calls"].mean()
    s_calls = spiral_df["calls"].mean()
    results["metric"].append("Avg Verification Calls")
    results["tower"].append(t_calls)
    results["spiral"].append(s_calls)
    results["delta"].append(s_calls - t_calls)
    
    # Efficiency: accuracy per verification call
    t_eff = t_acc / max(t_calls, 0.01)
    s_eff = s_acc / max(s_calls, 0.01)
    results["metric"].append("Efficiency (acc/call)")
    results["tower"].append(t_eff)
    results["spiral"].append(s_eff)
    results["delta"].append(s_eff - t_eff)
    
    # Adversarial accuracy
    t_adv = tower_df[tower_df["adversarial"]]["success"].mean()
    s_adv = spiral_df[spiral_df["adversarial"]]["success"].mean()
    results["metric"].append("Adversarial Accuracy")
    results["tower"].append(t_adv)
    results["spiral"].append(s_adv)
    results["delta"].append(s_adv - t_adv)
    
    # Non-adversarial accuracy
    t_nonadv = tower_df[~tower_df["adversarial"]]["success"].mean()
    s_nonadv = spiral_df[~spiral_df["adversarial"]]["success"].mean()
    results["metric"].append("Non-Adversarial Accuracy")
    results["tower"].append(t_nonadv)
    results["spiral"].append(s_nonadv)
    results["delta"].append(s_nonadv - t_nonadv)
    
    # High difficulty accuracy (top quartile)
    diff_q75 = tower_df["difficulty"].quantile(0.75)
    t_hard = tower_df[tower_df["difficulty"] >= diff_q75]["success"].mean()
    s_hard = spiral_df[spiral_df["difficulty"] >= diff_q75]["success"].mean()
    results["metric"].append("High Difficulty Accuracy")
    results["tower"].append(t_hard)
    results["spiral"].append(s_hard)
    results["delta"].append(s_hard - t_hard)
    
    return pd.DataFrame(results)

def analyze_spiral_zones(spiral_df):
    """Break down spiral performance by zone"""
    zone_stats = spiral_df.groupby("zone").agg(
        count=("success", "count"),
        success_rate=("success", "mean"),
        avg_calls=("calls", "mean")
    ).round(3)
    return zone_stats

# =============================================================================
# MAIN
# =============================================================================
if __name__ == "__main__":
    print("Running Tower vs Spiral comparison...")
    print("=" * 60)
    
    # Run comparison
    tower_df, spiral_df = run_comparison(seed=1111, N=1200, M=40, B_total=5, adv_rate=0.25)
    
    # Analyze
    comparison = analyze_results(tower_df, spiral_df)
    print("\n=== TOWER vs SPIRAL COMPARISON ===")
    print(comparison.round(4).to_string(index=False))
    
    zone_stats = analyze_spiral_zones(spiral_df)
    print("\n=== SPIRAL ZONE BREAKDOWN ===")
    print(zone_stats)
    
    # Budget sweep
    print("\n=== BUDGET SWEEP ===")
    budget_results = []
    for B in [1, 2, 3, 5, 7, 10]:
        t_df, s_df = run_comparison(seed=1111, N=800, M=40, B_total=B, adv_rate=0.25)
        budget_results.append({
            "B": B,
            "tower_acc": t_df["success"].mean(),
            "spiral_acc": s_df["success"].mean(),
            "tower_calls": t_df["calls"].mean(),
            "spiral_calls": s_df["calls"].mean(),
            "delta_acc": s_df["success"].mean() - t_df["success"].mean()
        })
    
    budget_df = pd.DataFrame(budget_results).round(4)
    print(budget_df.to_string(index=False))
    
    # Save results
    comparison.to_csv("/home/claude/tower_vs_spiral_comparison.csv", index=False)
    budget_df.to_csv("/home/claude/budget_sweep.csv", index=False)
    
    # Plotting
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    # Plot 1: Accuracy comparison
    ax1 = axes[0]
    x = range(len(budget_df))
    ax1.plot(budget_df["B"], budget_df["tower_acc"], 'o-', label="Tower (Stack)", color="blue")
    ax1.plot(budget_df["B"], budget_df["spiral_acc"], 's-', label="Spiral (Centrifuge)", color="orange")
    ax1.set_xlabel("Verification Budget (B)")
    ax1.set_ylabel("Accuracy")
    ax1.set_title("Tower vs Spiral: Accuracy by Budget")
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Delta accuracy
    ax2 = axes[1]
    colors = ['green' if d > 0 else 'red' for d in budget_df["delta_acc"]]
    ax2.bar(budget_df["B"], budget_df["delta_acc"], color=colors, alpha=0.7)
    ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
    ax2.set_xlabel("Verification Budget (B)")
    ax2.set_ylabel("Spiral - Tower (Accuracy Delta)")
    ax2.set_title("Spiral Advantage by Budget")
    ax2.grid(True, alpha=0.3)
    
    # Plot 3: Efficiency (accuracy per call)
    ax3 = axes[2]
    tower_eff = budget_df["tower_acc"] / budget_df["tower_calls"].clip(lower=0.1)
    spiral_eff = budget_df["spiral_acc"] / budget_df["spiral_calls"].clip(lower=0.1)
    ax3.plot(budget_df["B"], tower_eff, 'o-', label="Tower", color="blue")
    ax3.plot(budget_df["B"], spiral_eff, 's-', label="Spiral", color="orange")
    ax3.set_xlabel("Verification Budget (B)")
    ax3.set_ylabel("Efficiency (Accuracy / Calls)")
    ax3.set_title("Verification Efficiency")
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig("/home/claude/tower_vs_spiral.png", dpi=150, bbox_inches='tight')
    plt.close()
    
    print("\n=== PLOTS SAVED ===")
    print("tower_vs_spiral.png")
    print("tower_vs_spiral_comparison.csv")
    print("budget_sweep.csv")
