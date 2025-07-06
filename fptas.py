from dataclasses import dataclass
import time
import math

@dataclass
class ApproxDPResult:
    best_value: int
    duration: float
    timeout: bool

#Com lista
def knapsack_fptas_list(items, W, epsilon=0.5, timeout_seconds=1800):
    start = time.time()
    n = len(items)
    if n == 0:
        return ApproxDPResult(0, 0.0, False)

    vmax = max((v for _, v in items), default=0)
    if vmax == 0:
        return ApproxDPResult(0, 0.0, False)

    mu = (epsilon * vmax) / n
    scaled_items = [(w, max(1, math.floor(v / mu)), v) for w, v in items]
    V_scaled_total = sum(v_scaled for _, v_scaled, _ in scaled_items)

    dp = [(math.inf, 0) for _ in range(V_scaled_total + 1)]
    dp[0] = (0, 0)

    for w, v_scaled, v_orig in scaled_items:
        elapsed = time.time() - start
        if elapsed >= timeout_seconds:
            best_value_on_timeout = max(
                original_val for weight, original_val in dp if weight <= W
            )
            return ApproxDPResult(best_value_on_timeout, elapsed, True)

        for v in range(V_scaled_total, v_scaled - 1, -1):
            prev_weight, prev_orig_val = dp[v - v_scaled]
            new_weight = prev_weight + w
            new_value = prev_orig_val + v_orig
            if new_weight < dp[v][0]:
                dp[v] = (new_weight, new_value)

    best_value = max(original_val for weight, original_val in dp if weight <= W)
    duration = time.time() - start
    return ApproxDPResult(best_value, duration, False)

#Com dicionário
def knapsack_fptas_dict(items, W, epsilon=0.5, timeout_seconds=1800):
    start = time.time()
    n = len(items)
    if n == 0:
        return ApproxDPResult(0, 0.0, False)

    vmax = max((v for _, v in items), default=0)
    if vmax == 0:
        return ApproxDPResult(0, 0.0, False)

    mu = (epsilon * vmax) / n
    scaled_items = [(w, max(1, math.floor(v / mu)), v) for w, v in items]

    dp = {0: (0, 0)}

    for w, v_scaled, v_orig in scaled_items:
        elapsed = time.time() - start
        if elapsed >= timeout_seconds:
            best_value_on_timeout = max(
                original_val for weight, original_val in dp.values() if weight <= W
            )
            return ApproxDPResult(best_value_on_timeout, elapsed, True)

        new_dp = dp.copy()
        for v, (prev_weight, prev_orig_val) in dp.items():
            new_v = v + v_scaled
            new_weight = prev_weight + w
            new_value = prev_orig_val + v_orig

            if new_v not in new_dp or new_weight < new_dp[new_v][0]:
                new_dp[new_v] = (new_weight, new_value)
        dp = new_dp

    best_value = max(
        original_val for weight, original_val in dp.values() if weight <= W
    )
    duration = time.time() - start
    return ApproxDPResult(best_value, duration, False)

#Escolher a versão usada
def knapsack_fptas(items, W, epsilon=0.5, timeout_seconds=1800, use_dict=True):
    if use_dict:
        return knapsack_fptas_dict(items, W, epsilon, timeout_seconds)
    else:
        return knapsack_fptas_list(items, W, epsilon, timeout_seconds)
