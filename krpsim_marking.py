from heapq import heappop, heappush


class Marking:

    def __init__(self, cycle, place_tokens, transition_tokens, transitions, processed_cycle=0):
        self.cycle = cycle
        self.place_tokens = place_tokens
        self.transition_tokens = transition_tokens
        self.transitions = transitions
        self.prev = None
        self.processed_cycle = processed_cycle

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

    def get_nexts(self):
        nexts = []
        self.wait_nearest_transition(nexts)
        self.fire_each_transition(nexts)
        return (nexts)

    def wait_nearest_transition(self, nexts):
        if len(self.transition_tokens) == 0:
            return
        next = Marking(self.cycle, self.place_tokens.copy(), self.transition_tokens.copy(), self.transitions, self.processed_cycle)

        #  Update cycle
        next.cycle = next.transition_tokens[0][0]

        #  Update place_tokens
        while len(next.transition_tokens) > 0 and next.transition_tokens[0][0] == next.cycle:
            nearest = heappop(next.transition_tokens)
            for place_name, added_value in self.transitions[nearest[1]].output.items():
                next.place_tokens[place_name] += added_value
        nexts.append(next)

    def fire_each_transition(self, nexts):
        for transition_name, transition in self.transitions.items():
            enabled = True

            for place_name, required_value in transition.input.items():
                if self.place_tokens[place_name] < required_value:
                    enabled = False
                    break

            if not enabled:
                continue
            next = Marking(self.cycle, self.place_tokens.copy(), self.transition_tokens.copy(), self.transitions, self.processed_cycle)

            # update place_tokens
            for place_name, used_value in transition.input.items():
                next.place_tokens[place_name] -= used_value

            # update transition_tokens
            ending = next.cycle + next.transitions[transition_name].duration
            heappush(next.transition_tokens, (ending, transition_name))
            if ending > next.processed_cycle:
                next.processed_cycle = ending

            nexts.append(next)
