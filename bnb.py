import heapq

class Node:
    def __init__(self, level, value, weight, bound):
        self.level = level
        self.value = value
        self.weight = weight
        self.bound = bound

    def __lt__(self, other):
        return self.bound > other.bound  # bound maior → mais prioridade (heap max)

def compute_bound(node, items, W, n):
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

def bnb_knapsack(items, W):
    # Ordena por valor/peso decrescente
    items = sorted(items, key=lambda x: x[1]/x[0], reverse=True)
    n = len(items)

    root = Node(level=0, value=0, weight=0, bound=0.0)
    root.bound = compute_bound(root, items, W, n)

    queue = []
    heapq.heappush(queue, root)

    best_value = 0

    total_nodes = 1
    max_queue_size = 1

    while queue:
        node = heapq.heappop(queue)

        if node.bound <= best_value or node.level >= n:
            continue

        i = node.level
        w_next = node.weight + items[i][0]
        v_next = node.value + items[i][1]

        if w_next <= W and v_next > best_value:
            best_value = v_next

        #Filho com item
        child_with = Node(i + 1, v_next, w_next, 0.0)
        child_with.bound = compute_bound(child_with, items, W, n)
        if child_with.bound > best_value:
            heapq.heappush(queue, child_with)
            total_nodes += 1

        #Filho sem item
        child_without = Node(i + 1, node.value, node.weight, 0.0)
        child_without.bound = compute_bound(child_without, items, W, n)
        if child_without.bound > best_value:
            heapq.heappush(queue, child_without)
            total_nodes += 1

        max_queue_size = max(max_queue_size, len(queue))
    return best_value, total_nodes, max_queue_size