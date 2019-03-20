from krpsim_parsing import Setting
from krpsim_marking import Marking

class KrpsimGraph:

    def __init__(self):
        self.delay = 0
        self.initial_place_tokens = {}
        self.transactions = {}
        self.optimize = []
        self.setting = None
        self.get_setting()
        self.initial_marking = Marking(0, self.initial_place_tokens.copy(), [], self.transactions)

    def get_setting(self):
        self.setting = Setting(self)

    def __str__(self):
        out = ""
        out += "places:\n"
        for name, token in self.initial_place_tokens.items():
            out += ("    {}: {}\n".format(name, token))
        out += "transactions:\n"
        for name, transaction in self.transactions.items():
            out += "    {}: {}\n".format(name, transaction)
        out += "optimize:\n    {}\n".format(self.optimize)
        return (out)