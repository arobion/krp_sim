from heapq import heappop, heappush

class Marking:

    def __init__(self, cycle, place_tokens, transaction_tokens, transactions, processed_cycle=0):
        self.cycle = cycle
        self.place_tokens = place_tokens
        self.transaction_tokens = transaction_tokens
        self.transactions = transactions
        self.prev = None
        self.processed_cycle = processed_cycle
    
    def __lt__(self, other):
        return (self.processed_cycle > other.processed_cycle)

    def __str__(self):
        ret = ""
        ret += "cycle:{}\n".format(self.cycle)
        ret += "place_tokens:{}\n".format(self.place_tokens)
        ret += "transaction_tokens:{}\n".format(self.transaction_tokens)
        return (ret)

    def simulate_transaction(self, name):
        transaction = self.transactions[name]
        for key, val in transaction.output.items():
            self.processed_state[key] += val

    def get_nexts(self):
        nexts = []
        self.wait_nearest_transaction(nexts)
        self.fire_each_transaction(nexts)
        return (nexts)
    
    def wait_nearest_transaction(self, nexts):
        if len(self.transaction_tokens) == 0:
            return
        next = Marking(self.cycle, self.place_tokens.copy(), self.transaction_tokens.copy(), self.transactions, self.processed_cycle)

        #  Update cycle
        next.cycle = next.transaction_tokens[0][0]

        #  Update place_tokens
        while len(next.transaction_tokens) > 0 and next.transaction_tokens[0][0] == next.cycle:
            nearest = heappop(next.transaction_tokens)
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

            if not enabled:
                continue
            next = Marking(self.cycle, self.place_tokens.copy(), self.transaction_tokens.copy(), self.transactions, self.processed_cycle)

            # update place_tokens
            for place_name, used_value in transaction.input.items():
                next.place_tokens[place_name] -= used_value

            # update transaction_tokens
            ending = next.cycle + next.transactions[transaction_name].duration
            heappush(next.transaction_tokens, (ending, transaction_name))
            if ending > next.processed_cycle:
                next.processed_cycle = ending
            
            nexts.append(next)
