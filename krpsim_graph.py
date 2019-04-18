from krpsim_fusions import SerialFusion, PreFusion
from krpsim_fusions import LateralTransitionsFusionOne
from krpsim_fusions import LateralTransitionsFusionTwo, LateralPlacesFusion


class KrpsimGraph:

    def __init__(self, setting):
        setting.parse_config_file()
        self.initial_place_tokens = setting.initial_place_tokens
        self.transitions = setting.transitions
        self.optimize = setting.optimize
        self.delay = setting.delay_max
        self.places_inputs = setting.places_inputs
        self.places_outputs = setting.places_outputs
        self.initial_marking = None
        self.transformations = {}
        self.check_coherency()
        # self.reduce()

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

    def check_coherency(self):

        # check there are ressources
        ressources = []
        empty_ressources = True
        for name, token in self.initial_place_tokens.items():
            if token != 0:
                empty_ressources = False
            if token < 0:
                raise Exception("Negative ressource declared")
            ressources.append(name)
        if empty_ressources:
            raise Exception("No ressources declared")

        # check transitions are ok
        full_ressources = ['time']
        for name, transition in self.transitions.items():
            if name == "":
                raise Exception("Empty name for transition")
        for name, transition in self.transitions.items():
            for k, v in transition.output.items():
                if v < 0:
                    raise Exception("Negative output ressource for transition")
                full_ressources.append(k)
        for name, transition in self.transitions.items():
            for k, v in transition.input.items():
                if v < 0:
                    raise Exception("Negative input ressource for transition")
                if k not in ressources and k not in full_ressources:
                    raise Exception("Transition can't find input ressource")

        # check optimize
        if len(self.optimize) == 0:
            raise Exception("Optimize missing")
        for elem in self.optimize:
            if elem not in full_ressources:
                raise Exception("Ressource to optimize not in transitions")
