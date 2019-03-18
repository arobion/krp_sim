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
            print("    {}: {}".format(name, transaction.string()))
        print("optimize:\n    {}".format(self.optimize))



class Marking:

    def __init__(self, cycle, place_tokens, transaction_tokens, transactions):
        self.cycle = cycle
        self.place_tokens = place_tokens
        self.transaction_tokens = transaction_tokens
        self.transactions = transactions
    
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
        nearest = heapq.heappop(next.transaction_tokens)

        # update cycle
        next.cycle = nearest[1]

        # update place_tokens
        for place_name, added_value in self.transactions[nearest[0]].output.items():
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
                heapq.heappush(next.transaction_tokens, (transaction_name, ending))
                
                nexts.append(next)


def main():
    krpsim = KrpSim()
    krpsim.print()
    print("")
    
    krpsim.initial_marking.print()
    print("")
    
    solver(krpsim)
#    nexts = krpsim.initial_marking.get_nexts()
#    while len(nexts) != 0:
#        nexts[0].print()
#        print("")
#        nexts = nexts[0].get_nexts()

if __name__ == "__main__":
    main()
