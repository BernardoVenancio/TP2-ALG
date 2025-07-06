from dataclasses import dataclass
import time

@dataclass
class ApproxResult:
    best_value: int
    duration: float
    timeout: bool

def knapsack_2approx(items, W, timeout_seconds=1800):
    start = time.time()

    # Melhor item que cabe sozinho
    best_item_value = max((v for w, v in items if w <= W), default=0)

    # Ordena por valor/peso
    items_sorted = sorted(items, key=lambda x: x[1] / x[0], reverse=True)

    total_weight = 0
    greedy_value = 0

    for w, v in items_sorted:
        elapsed = time.time() - start
        if elapsed >= timeout_seconds:
            # Em caso de timeout, retorna o que conseguiu até aqui
            return ApproxResult(max(best_item_value, greedy_value), elapsed, True)

        if total_weight + w <= W:
            total_weight += w
            greedy_value += v
        else:
            break

    duration = time.time() - start
    return ApproxResult(max(best_item_value, greedy_value), duration, False)
