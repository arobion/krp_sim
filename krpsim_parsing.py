from krpsim_error import *

class Transaction:

    def __init__(self, name="", input={}, output={}, duration=0):
        self.name = name
        self.input = input
        self.output = output
        self.duration = duration

    def string(self):
        return "{} {} {}".format(self.input, self.output, self.duration)

def parse_config_file(config_file, krp):

    line = save_stock(config_file, krp)
    if line ==None:
        raise ErrorInput("Process Error: No process declarated")
    line = save_process(config_file, line, krp)
    if line == None:
        raise ErrorInput("Process Error: Process bad declaration")
    verif_optimize(line, config_file, krp)


#    krp.initial_place_tokens["euro"] = 10
#    krp.initial_place_tokens["materiel"] = 0
#    krp.initial_place_tokens["produit"] = 0
#    krp.initial_place_tokens["client_content"] = 0
#
#        # transactions
#    krp.transactions["achat_meteriel"] = Transaction("achat_meteriel", {"euro": 8}, {"materiel": 1}, 10)
#    krp.transactions["realisation_produit"] = Transaction("realisation_produit", {"materiel": 1}, {"produit": 1}, 20)
#    krp.transactions["livraison"] = Transaction("livraison", {"produit": 1}, {"client_content": 1}, 30)
        # optimize
#    krp.optimize = "client_content"


def verif_optimize(line, config_file, krp):
    line = line.split(':(')
    if len(line) != 2:
        raise ErrorInput("Config file Error: Config file is unvalid")
    if line[0] != "optimize":
        raise ErrorInput("Config file Error: Config file is unvalid")
    if line[1][-2:] != ")\n":
        raise ErrorInput("Config file Error: optimize is unvalid")
    line[1] = line[1][:-2]
    to_opt = line[1].split(';')
    for elem in to_opt:
        krp.optimize.append(elem)

def save_stock(config_file, krp):
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
            krp.initial_place_tokens[label] = quant
        line = config_file.readline()
    return  

def save_process(config_file, line, krp):
    while line:
        instr = line.split('#')[0]
        if instr != "":
            tmp_instr = instr.split('):(')
            if len(tmp_instr) != 2:
                tmp_instr = instr.split(')::')
                if len(tmp_instr) != 2:
                    return line
            transaction = split_instr(tmp_instr, krp)
            krp.transactions[transaction.name] = transaction
        line = config_file.readline()
    return "\n"

def split_instr(instr, krp):
    t = Transaction("", {}, {}, 0)
    left = instr[0].split(':(')
    if len(left) < 2:
        raise ErrorInput("Process Error: any Process need resources or name")
    right = instr[1].split('):')
    t.name = left[0]
    for inputs in left[1].split(';'):
        single_input = inputs.split(':')
        if len(single_input) != 2:
            raise ErrorInput("Process Error: bad declaration of a Process")
        input_name = single_input[0]
        try:
            quantity = int(single_input[1])
        except:
            raise ErrorInput("Process Error: Quantity must be a valid integer")
        t.input[input_name] = quantity

    if len(right) == 1:
        try:
            delay = int(right[0])
            t.duration = delay
            return t
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
        t.output[output_name] = quantity
        if output_name not in krp.initial_place_tokens.keys():
            krp.initial_place_tokens[output_name] = 0

    try:
        delay = int(right[1])
        t.duration = delay
    except:
        raise ErrorInput("Process Error: Delay must be a valid integer")
    return t
