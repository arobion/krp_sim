from heapq import heappop, heappush
import time


class Marking:

    def __init__(
            self, cycle, place_tokens, transition_tokens,
            transitions, processed_cycle=0, out=""):
        self.cycle = cycle
        self.place_tokens = place_tokens
        self.transition_tokens = transition_tokens
        self.transitions = transitions
        self.transition_keys = list(transitions)
        self.prev = None
        self.processed_cycle = processed_cycle
        self.nexts = []
        self.start_time = 0
        self.timeout = 3
        self.out = out
        self.is_timeout = False

    def __lt__(self, other):
        return (self.processed_cycle > other.processed_cycle)

    def __str__(self):
        ret = ""
        ret += "cycle:{}\n".format(self.cycle)
        ret += "place_tokens:{}\n".format(self.place_tokens)
        ret += "transition_tokens:{}\n".format(self.transition_tokens)
        return (ret)

    def simulate_transition(self, name):
        transition = self.transitions[name]
        for key, val in transition.output.items():
            self.processed_state[key] += val

    def get_nexts(self, start_time):
        self.start_time = start_time
        self.get_transition_combinations(self, 0)
        return self.nexts

    def get_transition_combinations(self, current, index):
        # stop if timeout
        if time.time() > self.start_time + self.timeout:
            self.is_timeout = True
            return

        # stop when run through all transition
        # then finish the nearest transition
        if index >= len(self.transition_keys):
            if current.finish_nearest_transition():
                self.nexts.append(current)
            return

        # 0 for this transition
        next = Marking(
            self.cycle,
            current.place_tokens.copy(),
            current.transition_tokens.copy(),
            self.transitions,
            self.processed_cycle,
            current.out)
        self.get_transition_combinations(next, index + 1)

        # more than 0 for this transition
        transition = self.transitions[self.transition_keys[index]]
        times = 1
        while self.can_do_transition(current, transition, times):
            next = self.create_new_marking(current, transition, times)
            self.get_transition_combinations(next, index + 1)
            times += 1

    def can_do_transition(self, current, transition, times):
        for place_name, required_value in transition.input.items():
            if current.place_tokens[place_name] < required_value * times:
                return False
        return True

    def create_new_marking(self, current, transition, times):
        next = Marking(
            self.cycle,
            current.place_tokens.copy(),
            current.transition_tokens.copy(),
            self.transitions,
            self.processed_cycle,
            current.out)

        # update place_tokens
        for place_name, used_value in transition.input.items():
            next.place_tokens[place_name] -= used_value * times

        # update transition_tokens
        ending = next.cycle + next.transitions[transition.name].duration
        heappush(next.transition_tokens, (ending, transition.name, times))
        if ending > next.processed_cycle:
            next.processed_cycle = ending
        for t in range(0, times):
            next.out += "{}:{}\n".format(next.cycle, transition.name)
        return next

    def finish_nearest_transition(self):
        if len(self.transition_tokens) == 0:
            return False

        #  Update cycle
        self.cycle = self.transition_tokens[0][0]

        #  Update place_tokens
        nearest = heappop(self.transition_tokens)
        for place_name, added_value in (
                self.transitions[nearest[1]].output.items()):
            self.place_tokens[place_name] += added_value * nearest[2]

        return True
