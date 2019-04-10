from krpsim_error import *
from pathlib import Path
import argparse
import sys
import errno
import os

class Config_structure():
    
    def __init__(self):
        self.stock = {}
        self.process = {}
        self.optimize = []

class Process():
    
    def __init__(self):
        self.name = ""
        self.duration = 0
        self.input = {}
        self.output = {}
        self.cycle_ending = 0

class Env():
    
    def __init__(self, conf):
        self.cycle = 0
        self.conf = conf
        self.active_process = []
    
    def add_output(self, process):
        for stock, quant in process.output.items():
            self.conf.stock[stock] += quant
    
    def update_cycle(self, new_cycle):
        self.cycle = new_cycle
        for process in self.active_process:
            if process.cycle_ending <= new_cycle:
                self.add_output(process)
                del process
    
    def process(self, name):
        new_process = Process()
        ref_process = self.conf.process[name]
        for stock, quant in ref_process.input.items():
            self.conf.stock[stock] -= quant
            if self.conf.stock[stock] < 0:
                raise KRPError("Algorithm Error at cycle {} on process '{}': it's impossible to use more stock than available".format(self.cycle, name))
        new_process.output = ref_process.output
        new_process.cycle_ending = self.cycle + ref_process.duration
        self.active_process.append(new_process)

class Setting():

    def __init__(self):
        self.stock = {}
        self.process = {}
        self.actions = []
        self.get_arguments(sys.argv[1:])

    def get_arguments(self, args=None):

        parser = argparse.ArgumentParser(description='krpsim_verif program.')
        parser.add_argument('config_file', type=argparse.FileType('r'))
        parser.add_argument('trace_file', type=argparse.FileType('r'))
        args = parser.parse_args()

        self.check_config_file(args.config_file)
        self.check_trace_file(args.trace_file)

    def check_config_file(self, config_file):
        line = self.save_stock(config_file)
        if line == None:
            raise ErrorInput("Process Error: No process declarated")
        line = self.save_process(config_file, line)
        if line == None:
            raise ErrorInput("Process Error: Process bad declaration")
        self.verif_optimize(line)

    def save_stock(self, config_file):
        line = config_file.readline()
        while line:
            instr = line.split('#')[0]
            if instr != "":
                instr = instr.split(':')
                if len(instr) != 2:
                    return line
                label = instr[0]
                try:
                    quant = int(instr[1])
                except:
                    raise ErrorInput("Stock Error: Quantity should be a valid integer")
                self.stock[label] = quant
            line = config_file.readline()
        return 

    def save_process(self, config_file, line):
        while line:
            instr = line.split('#')[0]
            if instr != "":
                tmp_instr = instr.split('):(')
                if len(tmp_instr) != 2:
                    tmp_instr = instr.split(')::')
                    if len(tmp_instr) != 2:
                        return line
                process = self.split_instr(tmp_instr)
                self.process[process.name] = process
            line = config_file.readline()
        return "\n"

    def split_instr(self, instr):
        p = Process()
        left = instr[0].split(':(')
        if len(left) < 2:
            raise ErrorInput("Process Error: any Process need resources or name")
        right = instr[1].split('):')
        p.name = left[0]
        for inputs in left[1].split(';'):
            single_input = inputs.split(':')
            if len(single_input) != 2:
                raise ErrorInput("Process Error: bad declaration of a Process")
            input_name = single_input[0]
            try:
                quantity = int(single_input[1])
            except:
                raise ErrorInput("Process Error: Quantity must be a valid integer")
            p.input[input_name] = quantity

        if len(right) == 1:
            try:
                delay = int(right[0])
                p.duration = delay
                return p
            except:
                raise ErrorInput("Process Error: Delay must be a valid integer")

        for outputs in right[0].split(';'):
            single_output = outputs.split(':')
            if len(single_output) != 2:
                raise ErrorInput("Process Error: bad declaration of a Process")
            output_name = single_output[0]
            try:
                quantity = int(single_output[1])
            except:
                raise ErrorInput("Process Error: Quantity must be a valid integer")
            try:
                delay = int(right[1])
                p.duration = delay
            except:
                raise ErrorInput("Process Error: Delay must be a valid integer")
            p.output[output_name] = quantity
            if output_name not in self.stock.keys():
                self.stock[output_name] = 0

        return p

    def verif_optimize(self, line):
        line = line.split(':')
        if len(line) != 2:
            raise ErrorInput("Config file Error: Config file is unvalid")
        if line[0] != "optimize":
            raise ErrorInput("Config file Error: Config file is unvalid")


    def check_trace_file(self, trace_file):
        line = trace_file.readline()
        while line:
            self.actions.append(line[:-1])
            line = trace_file.readline()
