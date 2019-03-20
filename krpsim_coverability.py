from heapq import heappop, heappush

def is_better(m1, m2, optimize):
    if m1.cycle == 0 and m2.cycle == 0:
        return False

    if m1.place_tokens[optimize] > m2.place_tokens[optimize]:
        return True
    if m1.place_tokens[optimize] == m2.place_tokens[optimize]:
        if m1.cycle < m2.cycle:
            return True
    return False

def is_visited(now, visited_place, visited_transaction):
    if tuple(now.place_tokens.items()) in visited_place:
        if tuple(now.transaction_tokens) in visited_transaction:
            return True
    return False

def brute_force(krpsim):
    optimize = "marelle"
    queue = []
    visited_place = set()
    visited_transaction = set()
    best = krpsim.initial_marking
    heappush(queue, (krpsim.initial_marking.cycle, krpsim.initial_marking))
    while queue:
        now = heappop(queue)[1]

        if is_better(now, best, optimize):
            best = now
            if best.place_tokens[optimize] == 1:
                break

        if is_visited(now, visited_place, visited_transaction):
            continue

        visited_place.add(tuple(now.place_tokens.items()))
        visited_transaction.add(tuple(now.transaction_tokens))


        nexts = now.get_nexts()
        
        for next_one in nexts:
            next_one.process_tokens()

            heappush(queue, (next_one.cycle, next_one))
            next_one.prev = now
   
    while best:
        print(best)
        best = best.prev
