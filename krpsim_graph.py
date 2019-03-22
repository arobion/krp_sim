from krpsim_marking import Marking

class KrpsimGraph:

    def __init__(self, setting):
        setting.parse_config_file()
        self.initial_place_tokens = setting.initial_place_tokens
        self.transactions = setting.transactions
        self.optimize = setting.optimize
        self.delay = setting.delay_max
        self.places_inputs = setting.places_inputs
        self.places_outputs = setting.places_outputs
        self.initial_marking = Marking(0, self.initial_place_tokens.copy(), [], self.transactions)
        self.transformations = {}

    def __str__(self):
        out = ""
        out += "places:\n"
        for name, token in self.initial_place_tokens.items():
            out += ("    {}: {}\n".format(name, token))
        out += "transactions:\n"
        for name, transaction in self.transactions.items():
            out += "    {}\n".format(transaction)
        out += "optimize:\n    {}\n".format(self.optimize)
        return (out)
