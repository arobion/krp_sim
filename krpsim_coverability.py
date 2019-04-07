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


def is_visited(now, visited_place, visited_transition):
    if tuple(now.place_tokens.items()) in visited_place:
        if tuple(now.transition_tokens) in visited_transition:
            return True
    return False


def brute_force(krpsim):
    optimize = krpsim.optimize[0]
    queue = []
    visited_place = set()
    visited_transition = set()
    best = krpsim.initial_marking
    heappush(queue, (krpsim.initial_marking.cycle, krpsim.initial_marking))
    while queue:
        now = heappop(queue)[1]

        if now.cycle > krpsim.delay:
            break

        if is_better(now, best, optimize):
            best = now

        if is_visited(now, visited_place, visited_transition):
            continue

        # use this to set a limit
        # if now.place_tokens[optimize] == 1:
        #     break

        visited_place.add(tuple(now.place_tokens.items()))
        visited_transition.add(tuple(now.transition_tokens))

        nexts = now.get_nexts()

        for next_one in nexts:
            heappush(queue, (next_one.cycle, next_one))
            next_one.prev = now
        
    print_best(best)


def print_best(best):
    if best.prev:
        print_best(best.prev)
    print(best)
