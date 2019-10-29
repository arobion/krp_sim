from krpsim_error import InputError
from krpsim_transition import Transition
import argparse


class Setting():

    def __init__(self):
        self.config_file = None
        self.delay_max = 0
        self.initial_place_tokens = {}
        self.transitions = {}
        self.places_outputs = {}
        self.places_inputs = {}
        self.optimize = []

    def get_args(self):
        parser = argparse.ArgumentParser(description='KrpSim program')
        parser.add_argument('config_file', type=str)
        parser.add_argument('delay_max', type=int)
        args = parser.parse_args()
        self.config_file = args.config_file
        self.delay_max = args.delay_max

    def parse_config_file(self):
        self.get_args()
        with open(self.config_file, 'r') as config_file:
            step = "stock"
            for line in config_file.readlines():
                line = line.split('#')[0]
                if line == "":
                    continue

                line_type = self.get_line_type(line)
                if line_type == "process" and step == "stock":
                    step = "process"
                if line_type == "optimize" and step == "process":
                    step = "optimize"
                if line_type != step:
                    raise InputError("Invalid configuration file")

                if line_type == "stock":
                    self.parse_stock(line)
                elif line_type == "process":
                    self.parse_process(line)
                elif line_type == "optimize":
                    step = "end"
                    self.parse_optimize(line)

    def get_line_type(self, line):
        test_stock = line.split(':')
        if len(test_stock) == 2:
            if test_stock[0] == "optimize":
                return ("optimize")
            return ("stock")
        return ("process")

    def parse_stock(self, line):
        instr = line.split(':')
        if len(instr) != 2:
            raise InputError("Stock Error: Invalid stock format")
        label = instr[0]
        if not label:
            raise InputError("Stock Error: Invalid stock name format")
        try:
            quant = int(instr[1])
        except Exception:
            raise InputError("Stock Error: Quantity should be a valid integer")
        self.initial_place_tokens[label] = quant

    def parse_process(self, line):
        tmp_instr = line.split('):(')
        if len(tmp_instr) != 2:
            tmp_instr = line.split(')::')
            if len(tmp_instr) != 2:
                raise InputError("Invalid configuration file")
            else:
                pass
        else:
            transition = self.parse_transition(tmp_instr)
            self.transitions[transition.name] = transition

    def parse_transition_inputs(self,
                                transition, inputs):
        for entry in inputs.split(';'):
            entry_split = entry.split(':')
            if len(entry_split) != 2:
                raise InputError("Process Error: bad declaration of a Process")
            input_name = entry_split[0]
            input_value = entry_split[1]
            try:
                quantity = int(input_value)
            except Exception:
                raise InputError("Process Error: "
                                 "Quantity must be a valid integer")
            transition.input[input_name] = quantity
            if input_name not in self.places_inputs.keys():
                self.places_inputs[input_name] = []
            self.places_inputs[input_name].append(transition)

    def parse_transition_outputs(self, transition, outputs):
        for entry in outputs.split(';'):
            entry_split = entry.split(':')
            if len(entry_split) != 2:
                raise InputError("Process Error: bad declaration of a Process")
            output_name = entry_split[0]
            output_value = entry_split[1]
            try:
                quantity = int(output_value)
            except Exception:
                raise InputError("Process Error: "
                                 "Quantity must be a valid integer")
            transition.output[output_name] = quantity
            if output_name not in self.initial_place_tokens.keys():
                self.initial_place_tokens[output_name] = 0
            if output_name not in self.places_outputs.keys():
                self.places_outputs[output_name] = []
            self.places_outputs[output_name].append(transition)

    def parse_transition(self, instr):
        transition = Transition("", {}, {}, 0)
        name_inputs = instr[0].split(':(')
        if len(name_inputs) < 2:
            raise InputError("Process Error: any "
                             "Process need resources or name")
        name = name_inputs[0]
        inputs = name_inputs[1]

        transition.name = name
        self.parse_transition_inputs(transition, inputs)
        outputs_delay = instr[1].split('):')
        if len(outputs_delay) == 1:
            try:
                delay = int(outputs_delay[0])
                transition.duration = delay
                return transition
            except Exception:
                raise InputError("Process Error: Delay "
                                 "must be a valid integer")

        if len(outputs_delay) != 2:
            raise InputError("Process Error : Bad process declaration")

        outputs = outputs_delay[0]
        delay = outputs_delay[1]
        self.parse_transition_outputs(transition, outputs)
        try:
            delay = int(delay)
            transition.duration = delay
        except Exception:
            raise InputError("Process Error: Delay must be a valid integer")
        return transition

    def parse_optimize(self, line):
        line = line.strip().split(':(')
        if len(line) != 2:
            raise InputError("Optimize Error : Invalid optimize format")
        if line[0] != "optimize":
            raise InputError("Optimize Error : Invalid optimize name format")
        if line[1][-1:] != ")":
            raise InputError("Optimize Error : optimize is unvalid")
        optimize_entries = line[1][:-1]
        to_optimize = optimize_entries.split(';')
        for elem in to_optimize:
            self.optimize.append(elem)
