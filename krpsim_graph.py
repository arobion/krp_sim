from krpsim_marking import Marking


class KrpsimGraph:

    def __init__(self, setting):
        setting.parse_config_file()
        self.initial_place_tokens = setting.initial_place_tokens
        self.transitions = setting.transitions
        self.optimize = setting.optimize
        self.delay = setting.delay_max
        self.places_inputs = setting.places_inputs
        self.places_outputs = setting.places_outputs
#        self.initial_marking = Marking(0, self.initial_place_tokens.copy(), [], self.transitions)
        self.initial_marking = None
        self.transformations = {}

    def __str__(self):
        out = ""
        out += "places:\n"
        for name, token in self.initial_place_tokens.items():
            out += ("    {}: {}\n".format(name, token))
        out += "transitions:\n"
        for name, transition in self.transitions.items():
            out += "    {}\n".format(transition)
        out += "optimize:\n    {}\n".format(self.optimize)
        return (out)
