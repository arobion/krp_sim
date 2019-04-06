from krpsim_marking import Marking
from krpsim_fusions import SerialFusion, PreFusion, LateralTransitionsFusionOne, LateralTransitionsFusionTwo, LateralPlacesFusion


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
        self.reduce()

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

    def reduce(self):
        sf = SerialFusion(self)
        pf = PreFusion(self)
        ltf1 = LateralTransitionsFusionOne(self)
        ltf2 = LateralTransitionsFusionTwo(self)
        lpf = LateralPlacesFusion(self)

        while True:
            if sf.detect():
                continue
            if pf.detect():
                continue
            if ltf1.detect():
                continue
            if ltf2.detect():
                continue
            if lpf.detect():
                continue
            break
