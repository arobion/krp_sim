import heapq


class KrpSim:

    def __init__(self):
        self.delay = 0
        self.initial_place_tokens = {}
        self.transactions = {}
        self.optimize = ""
        self.parse()
        self.initial_marking = Marking(0, self.initial_place_tokens.copy(), [], self.transactions)

    def parse(self):
        # places
        self.initial_place_tokens["euro"] = 10
        self.initial_place_tokens["materiel"] = 0
        self.initial_place_tokens["produit"] = 0
        self.initial_place_tokens["client_content"] = 0
        # transactions
        self.transactions["achat_meteriel"] = Transaction({"euro": 8}, {"materiel": 1}, 10)
        self.transactions["realisation_produit"] = Transaction({"materiel": 1}, {"produit": 1}, 20)
        self.transactions["livraison"] = Transaction({"produit": 1}, {"client_content": 1}, 30)
        # optimize
        self.optimize = "client_content"

    def print(self):
        print("places:")
        for name, token in self.initial_place_tokens.items():
            print("    {}: {}".format(name, token))
        print("transactions:")
        for name, transaction in self.transactions.items():
            print("    {}: {}".format(name, transaction.string()))
        print("optimize:\n    {}".format(self.optimize))


class Transaction:

    def __init__(self, input={}, output={}, duration=0):
        self.input = input
        self.output = output
        self.duration = duration

    def string(self):
        return "{} {} {}".format(self.input, self.output, self.duration)
    

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


krpsim = KrpSim()
krpsim.print()
print("")

krpsim.initial_marking.print()
print("")

nexts = krpsim.initial_marking.get_nexts()
while len(nexts) != 0:
    nexts[0].print()
    print("")
    nexts = nexts[0].get_nexts()
