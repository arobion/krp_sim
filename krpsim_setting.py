from krpsim_error import InputError
from krpsim_transaction import Transaction
import argparse


class Setting():

    def __init__(self):
        self.config_file = None
        self.delay_max = 0
        self.initial_place_tokens = {}
        self.transactions = {}
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
        label = instr[0]
        try:
            quant = int(instr[1])
        except:
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
            transaction = self.parse_transaction(tmp_instr)
            self.transactions[transaction.name] = transaction

    def parse_transaction_inputs(self, transaction, inputs):
        for entry in inputs.split(';'):
            entry_split = entry.split(':')
            if len(entry_split) != 2:
                raise InputError("Process Error: bad declaration of a Process")
            input_name = entry_split[0]
            input_value = entry_split[1]
            try:
                quantity = int(input_value)
            except:
                raise InputError("Process Error: Quantity must be a valid integer")
            transaction.input[input_name] = quantity

    def parse_transaction_outputs(self, transaction, outputs):
        for entry in outputs.split(';'):
            entry_split = entry.split(':')
            if len(entry_split) != 2:
                raise InputError("Process Error: bad declaration of a Process")
            output_name = entry_split[0]
            output_value = entry_split[1]
            try:
                quantity = int(output_value)
            except:
                raise InputError("Process Error: Quantity must be a valid integer")
            transaction.output[output_name] = quantity
            if output_name not in self.initial_place_tokens.keys():
                self.initial_place_tokens[output_name] = 0


    def parse_transaction(self, instr):
        transaction = Transaction("", {}, {}, 0)
        name_inputs = instr[0].split(':(')
        if len(name_inputs) < 2:
            raise InputError("Process Error: any Process need resources or name")
        name = name_inputs[0]
        inputs = name_inputs[1]

        transaction.name = name
        self.parse_transaction_inputs(transaction, inputs)
        outputs_delay = instr[1].split('):')
        if len(outputs_delay) == 1:
            try:
                delay = int(outputs_delay[0])
                transaction.duration = delay
                return transaction
            except:
                raise InputError("Process Error: Delay must be a valid integer")

        if len(outputs_delay) != 2:
            raise InputError("Process Error : Bad process declaration")
        
        outputs = outputs_delay[0]
        delay = outputs_delay[1]
        self.parse_transaction_outputs(transaction, outputs)
        try:
            delay = int(delay)
            transaction.duration = delay
        except:
            raise InputError("Process Error: Delay must be a valid integer")
        return transaction

    def parse_optimize(self, line):
        line = line.split(':(')
        if len(line) != 2:
            raise InputError("Config file Error: Config file is unvalid")
        if line[0] != "optimize":
            raise InputError("Config file Error: Config file is unvalid")
        if line[1][-2:] != ")\n":
            raise InputError("Config file Error: optimize is unvalid")
        optimize_entries = line[1][:-2]
        to_optimize = optimize_entries.split(';')
        for elem in to_optimize:
            self.optimize.append(elem)
