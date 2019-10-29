from heapq import heappop, heappush
import time


def is_better(m1, m2, optimize):
    if m1.cycle == 0 and m2.cycle == 0:
        return False

    if m1.place_tokens[optimize] > m2.place_tokens[optimize]:
        return True
    if m1.place_tokens[optimize] == m2.place_tokens[optimize]:
        if m1.cycle < m2.cycle:
            return True
    return False


def is_visited(now, visited):
    tup = (tuple(now.place_tokens.items()), tuple(now.transition_tokens))
    if tup in visited:
        return True
    return False


def bruteforce(krpsim):
    optimize = krpsim.optimize[0]
    queue = []
    visited = set()
    best = krpsim.initial_marking
    heappush(queue, (krpsim.initial_marking.cycle, krpsim.initial_marking))
    start_time = time.time()
    while queue:
        now = heappop(queue)[1]

        if now.cycle > krpsim.delay:
            break

        if is_better(now, best, optimize):
            best = now

        if is_visited(now, visited):
            continue

        tup = (tuple(now.place_tokens.items()), tuple(now.transition_tokens))
        visited.add(tup)

        nexts = now.get_nexts(start_time)

        for next_one in nexts:
            heappush(queue, (next_one.cycle, next_one))
            next_one.prev = now

    krpsim.initial_marking = best
    if time.time() - start_time > 3:
        best.is_timeout = True
    return (None, krpsim, best.out), best.is_timeout
