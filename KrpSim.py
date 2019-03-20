import heapq
import argparse
from krpsim_parsing import parse_config_file
from krpsim_solver import solver


class KrpSim:

    def __init__(self):
        self.delay = 0
        self.initial_place_tokens = {}
        self.transactions = {}
        self.optimize = []
        self.parse()
        self.initial_marking = Marking(0, self.initial_place_tokens.copy(), [], self.transactions)

    def parse(self):
        # places
        parser = argparse.ArgumentParser(description='KrpSim program')
        parser.add_argument('config_file', type=argparse.FileType('r'))
        parser.add_argument('delay_max', type=int)
        args = parser.parse_args()
        parse_config_file(args.config_file, self)

    def find_to_optimize(self, to_opt):
        return self.initial_place_tokens[to_opt]



    def print(self):
        print("places:")
        for name, token in self.initial_place_tokens.items():
            print("    {}: {}".format(name, token))
        print("transactions:")
        for name, transaction in self.transactions.items():
            print("    {}: {}".format(name, transaction))
        print("optimize:\n    {}".format(self.optimize))



class Marking:

    def __init__(self, cycle, place_tokens, transaction_tokens, transactions):
        self.cycle = cycle
        self.place_tokens = place_tokens
        self.transaction_tokens = transaction_tokens
        self.transactions = transactions
        self.prev = None
    
    def __lt__(self, other):

        return self.processed_cycle > other.processed_cycle

    def process_tokens(self):
#        self.processed_state = self.place_tokens.copy()
        biggest_cycle = 0
        for elem in self.transaction_tokens:
            if elem[0] > biggest_cycle:
                biggest_cycle = elem[0]
#            self.simulate_transaction(elem[1])
        self.processed_cycle = biggest_cycle + self.cycle

    def simulate_transaction(self, name):
        transaction = self.transactions[name]
        for key, val in transaction.output.items():
            self.processed_state[key] += val


    def print(self):
        print("cycle:", self.cycle)
        print("place_tokens:", self.place_tokens)
        print("transaction_tokens:", self.transaction_tokens)

    def get_nexts(self):
        nexts = []
        self.wait_nearest_transaction(nexts)
        self.fire_each_transaction(nexts)
        return (nexts)
    
    def wait_nearest_transaction(self, nexts):
        if len(self.transaction_tokens) == 0:
            return
        next = Marking(self.cycle, self.place_tokens.copy(), self.transaction_tokens.copy(), self.transactions)

    #update cycle
        next.cycle = next.transaction_tokens[0][0]

        # update place_tokens
        while len(next.transaction_tokens) > 0 and next.transaction_tokens[0][0] == next.cycle:
            nearest = heapq.heappop(next.transaction_tokens)
            for place_name, added_value in self.transactions[nearest[1]].output.items():
                next.place_tokens[place_name] += added_value

        nexts.append(next)

    def fire_each_transaction(self, nexts):
        for transaction_name, transaction in self.transactions.items():
            enabled = True

            for place_name, required_value in transaction.input.items():
                if self.place_tokens[place_name] < required_value:
                    enabled = False
                    break

            if enabled:
                next = Marking(self.cycle, self.place_tokens.copy(), self.transaction_tokens.copy(), self.transactions)

                # update place_tokens
                for place_name, used_value in transaction.input.items():
                    next.place_tokens[place_name] -= used_value

                # update transaction_tokens
                ending = next.cycle + next.transactions[transaction_name].duration
                heapq.heappush(next.transaction_tokens, (ending, transaction_name))
                
                nexts.append(next)

    """
    def handle_infinite(self):
        handle the omega here
    """


def try_transaction(krpsim, current):
    nexts = current.get_nexts()
    if current.place_tokens['armoire'] == 1:
        krpsim.count_arm += 1
    for transaction in nexts:
#        transaction.print()
#        print()
        krpsim.count += 1
        try_transaction(krpsim, transaction)


def is_better(m1, m2, optimize):
    if m1.cycle == 0 and m2.cycle == 0:
        return False

    if m1.place_tokens[optimize] > m2.place_tokens[optimize]:
        return True
    if m1.place_tokens[optimize] == m2.place_tokens[optimize]:
        if m1.cycle < m2.cycle:
            return True
    return False

def main():
    krpsim = KrpSim()
    krpsim.print()
    print("")
    
    krpsim.initial_marking.print()
    print("")
    
#    solver(krpsim)
#    krpsim.count = 0
#    krpsim.count_arm = 0
#    nexts = krpsim.initial_marking.get_nexts()
#    for transaction in nexts:
##        transaction.print()
#        krpsim.count += 1
#        try_transaction(krpsim, transaction)
#    print(krpsim.count, krpsim.count_arm)
#    while len(nexts) != 0:
#        nexts[0].print()
#        print("")
#        nexts = nexts[0].get_nexts()


    """
    def is_visited:
        if found in visited 
            return True
        return False
    
    def compare_marking(m1, m2):
        return 
    
    queue = []
    visited = []
    
    best = initial
    queue.append(initial)
    
    while len(queue) > 0:
        now = queue.pop()
    
        if is_visited:
            label as old
            continue
        
        best.compare(now)
        if now is better
            best = now
    
        visited.append(now)
    
        nexts = now.get_nexts()
        if len(nexts) == 0:
            label as dead-end
    
        for next in nexts:
            if next.is_infinite():
                next.handle_infinite()
            else
                queue.append(next)
            next.prev = now
    """

    queue = []
    visited_place = []
    visited_transaction = []
    best = krpsim.initial_marking
    heapq.heappush(queue, (krpsim.initial_marking.cycle, krpsim.initial_marking))
    while queue:
        pop = heapq.heappop(queue)
        now = pop[1]

#        if now is in visited:
        if is_better(now, best, "armoire"):
            best = now

        if is_visited(now, visited_place, visited_transaction):
            continue
        visited_place.append(now.place_tokens)
        visited_transaction.append(now.transaction_tokens)


        nexts = now.get_nexts()
        
        for next_one in nexts:
            next_one.process_tokens()

            heapq.heappush(queue, (next_one.cycle, next_one))
            next_one.prev = now
   
    while best:
        best.print()
        best = best.prev
    
def is_visited(now, visited_place, visited_transaction):
    if now.place_tokens in visited_place:
        if now.transaction_tokens in visited_transaction:
            return True
    return False

if __name__ == "__main__":
    main()
