import heapq
import time
from dataclasses import dataclass

class Node:
    def __init__(self, level, value, weight, bound):
        self.level = level
        self.value = value
        self.weight = weight
        self.bound = bound

    def __lt__(self, other):
        return self.bound > other.bound  # max-heap

@dataclass
class BnBResult:
    best_value: int
    total_nodes: int
    max_queue_size: int
    duration: float
    timeout: bool

# Bound usando fração real dos itens restantes
def compute_bound_linear(node, items, W, n):
    if node.weight >= W:
        return 0    
    result = node.value
    j = node.level
    total_weight = node.weight

    while j < n and total_weight + items[j][0] <= W:
        total_weight += items[j][0]
        result += items[j][1]
        j += 1

    if j < n and items[j][0] > 0:
        result += (W - total_weight) * (items[j][1] / items[j][0])
    return result

# Bound constante baseado só no próximo item
def compute_bound_constant(node, items, W, n):
    if node.weight >= W:
        return 0
    if node.level >= n:
        return node.value
    best_ratio = items[node.level][1] / items[node.level][0]
    return node.value + (W - node.weight) * best_ratio

# Função genérica que aceita qualquer função de bound
def bnb_knapsack(items, W, bound_func, timeout_seconds=1800):
    items = sorted(items, key=lambda x: x[1] / x[0], reverse=True)
    n = len(items)
    start_time = time.time()

    root = Node(level=0, value=0, weight=0, bound=0.0)
    root.bound = bound_func(root, items, W, n)

    queue = []
    heapq.heappush(queue, root)

    best_value = 0
    total_nodes = 1
    max_queue_size = 1

    while queue:
        elapsed = time.time() - start_time
        if elapsed >= timeout_seconds:
            return BnBResult(best_value, total_nodes, max_queue_size, elapsed, True)

        node = heapq.heappop(queue)

        if node.bound <= best_value or node.level >= n:
            continue

        i = node.level
        w_next = node.weight + items[i][0]
        v_next = node.value + items[i][1]

        if w_next <= W and v_next > best_value:
            best_value = v_next

        # Com item i
        child_with = Node(i + 1, v_next, w_next, 0.0)
        child_with.bound = bound_func(child_with, items, W, n)
        if child_with.bound > best_value:
            heapq.heappush(queue, child_with)
            total_nodes += 1

        # Sem item i
        child_without = Node(i + 1, node.value, node.weight, 0.0)
        child_without.bound = bound_func(child_without, items, W, n)
        if child_without.bound > best_value:
            heapq.heappush(queue, child_without)
            total_nodes += 1

        max_queue_size = max(max_queue_size, len(queue))

    duration = time.time() - start_time
    return BnBResult(best_value, total_nodes, max_queue_size, duration, False)

#Chamando a função de forma + elegante
def bnb_knapsack_linear(items, W, timeout_seconds=1800):
    return bnb_knapsack(items, W, compute_bound_linear, timeout_seconds)

def bnb_knapsack_constant(items, W, timeout_seconds=1800):
    return bnb_knapsack(items, W, compute_bound_constant, timeout_seconds)
