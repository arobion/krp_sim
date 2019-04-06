from krpsim_transaction import Transaction

#################################################################
###################  LATERAL FUSION PART ########################
#################################################################


def detect_lateral_transaction_fusion_1(krp):
    S_list = find_same_input_transactions(krp)
    for S in S_list:
        rule_2 = True
        rule_1 = set()
        rule_4 = set()
        for transaction in S:
            for elem in transaction.output.keys():
                if len(krp.places_outputs[elem]) != 1:
                    rule_2 = False
                if elem in krp.places_inputs:
                    rule_1.add(tuple(krp.places_inputs[elem]))
                else:
                    rule_1.add(False)
                rule_4.add(krp.initial_place_tokens[elem])
        if rule_2 is True and len(rule_1) == 1 and len(rule_4) == 1:
            # print('DETECTED_1')
            proceed_lateral_transaction_fusion_1(krp, S)
            return True
    return False

"""
fusion all the t in S in Tf
remove all the t in S from krp.transaction
add tf in transaction
remove
"""


def proceed_lateral_transaction_fusion_1(krp, S):
    duration = 0
    name = ""
    tf = Transaction(name="", input={}, output={}, duration=0)
    for transaction in S:
        if transaction.duration > duration:
            duration = transaction.duration
        if name == "":
            name = transaction.name
        else:
            name += "+" + transaction.name
        merge_transaction(krp, tf, transaction)
        remove_transaction(krp, tf, transaction)

    tf.name = name
    tf.duration = duration
    krp.transactions[tf.name] = tf


def remove_transaction(krp, tf, transaction):
    krp.transactions.pop(transaction.name)
    for elem in transaction.input:
        krp.places_inputs[elem].pop(krp.places_inputs[elem].index(transaction))
        if tf not in krp.places_inputs[elem]:
            krp.places_inputs[elem].append(tf)
    for elem in transaction.output:
        krp.places_outputs[elem].pop(krp.places_outputs[elem].index(transaction))
        krp.places_outputs[elem].append(tf)


def merge_transaction(krp, tf, transaction):
    nb = 1
    for elem in transaction.output:
        for inputs in krp.places_inputs[elem][0].input:
            if inputs == elem:
                nb = krp.places_inputs[elem][0].input[inputs]
    for i in range(0, nb):
        tf + transaction


def detect_lateral_transaction_fusion_2(krp):
    P_list = find_same_input_places(krp)
    for P in P_list:
        rule_2 = True
        rule_3 = True
        S = []
        rule_4 = set()
        for place in P:
            if place not in krp.places_inputs:
                rule_2 = False
                continue
            if len(krp.places_inputs[place]) != 1:
                rule_2 = False
            else:
                if len(krp.places_inputs[place][0].input.keys()) != 1:
                    rule_3 = False
                else:
                    S.append(krp.places_inputs[place][0])
                    rule_4.add(krp.initial_place_tokens[place])

        if rule_2 is True and rule_3 is True and len(rule_4) == 1:
            print('DETECTED_2')
#            proceed_lateral_transaction_fusion_2(krp, S)
#            return True


def detect_lateral_places_fusion(krp):
    P_list = find_same_input_places(krp)
    for P in P_list:
        rule_2 = True
        rule_3 = True
        rule_3_store = set()
        rule_4 = set()
        rule_4.add(0)
        for place in P:
            if len(krp.places_outputs[place]) != 1:
                rule_2 = False
            if place not in krp.places_inputs:
                rule_3 = False
            else:
                rule_3_store.add(tuple(krp.places_inputs[place]))
                if len(krp.places_inputs[place]) != 1:
                    rule_3 = False
            rule_4.add(krp.initial_place_tokens[place])
        if rule_2 is True and rule_3 is True and len(rule_4) == 1 and len(rule_3_store) == 1:
            # print('DETECTED_3')
            proceed_lateral_places_fusion(krp, P)
            return True

    return False

"""
fusion all the places in P in pf
add pf in initial_place_tokens
update the input transaction
update the output transaction
remove all te places in krp.initial_place_tokens
remove
"""


def proceed_lateral_places_fusion(krp, P):
    pf = ""
    for place in P:
        if pf == "":
            pf = place
        else:
            pf += "+" + place
        krp.initial_place_tokens.pop(place)
    krp.initial_place_tokens[pf] = 0

    for place in P:
        update_place(krp, place, pf)


def update_place(krp, place, pf):
    transaction_input = krp.places_inputs[place][0]
    transaction_input.input.pop(place)
    transaction_input.input[pf] = 1
    if place in krp.places_inputs:
        krp.places_inputs.pop(place)
    if pf not in krp.places_inputs:
        krp.places_inputs[pf] = [transaction_input]

    transaction_output = krp.places_outputs[place][0]
    transaction_output.output.pop(place)
    transaction_output.output[pf] = 1
    if place in krp.places_outputs:
        krp.places_outputs.pop(place)
    if pf not in krp.places_outputs:
        krp.places_outputs[pf] = [transaction_output]


#################################################################
###################  SERIAL FUSION PART #########################
#################################################################


def detect_serial_fusion(krp):
    for place, value in krp.initial_place_tokens.items():
        # rule 1: place p is unmarked in the initial marking
        if value != 0:
            continue

        # rule 3: place p is disconnected from all other transitions
        # first check if there is place(s) in places_inputs and places_output
        # then check if the len is 1 or not
        if (place not in krp.places_inputs or
                place not in krp.places_outputs or
                len(krp.places_inputs[place]) != 1 or
                len(krp.places_outputs[place]) != 1):
            continue

        # rule 2:
        # 1) place p is the unique output place of t1
        # 2) place p is the unique input place of t2
        t1 = krp.places_outputs[place][0]
        t2 = krp.places_inputs[place][0]
        if len(t1.output) != 1 or len(t2.input) != 1:
            continue

        proceed_serial_fusion(krp, place, t1, t2)
        return True

    return False


def check_transaction_inputs(krp, transaction):
    for place_name in transaction.input.keys():
        if len(krp.places_inputs[place_name]) != 1:
            return False
    return True


def update_places(krp, place, t1, t2, tf):
    krp.initial_place_tokens.pop(place)
    krp.places_inputs.pop(place)
    krp.places_outputs.pop(place)
    for key, val in krp.places_inputs.items():
        if val[0] == t1:
            krp.places_inputs[key][0] = tf
    for key, val in krp.places_outputs.items():
        if val[0] == t2:
            krp.places_outputs[key][0] = tf


def proceed_serial_fusion(krp, place, t1, t2):
    duration = t1.duration + t2.duration
    name = t1.name + "+" + t2.name
    inputs = t1.input
    outputs = t2.output
    tf = Transaction(name=name, input=inputs, output=outputs, duration=duration)
    krp.transactions[tf.name] = tf
    krp.transformations[tf] = [t1, t2]
    krp.transactions.pop(t1.name)
    krp.transactions.pop(t2.name)

    update_places(krp, place, t1, t2, tf)

#################################################################
#####################  PRE FUSION PART ##########################
#################################################################


def detect_pre_fusion(krp):
    unmarked_places = find_unmarked_places(krp)
    return False

















#################################################################
###################  FINDING ITEMS PART #########################
#################################################################

def find_same_input_places(krp):
    ret = []
    for elem_1 in krp.initial_place_tokens.keys():
        sub_ret = set()
        for elem_2 in krp.initial_place_tokens.keys():
            if elem_1 != elem_2:
                if elem_1 in krp.places_outputs and elem_2 in krp.places_outputs:
                    if krp.places_outputs[elem_1] == krp.places_outputs[elem_2]:
                        sub_ret.add(elem_1)
                        sub_ret.add(elem_2)
        if sub_ret not in ret and len(sub_ret) != 0:
            ret.append(sub_ret)
    return ret
                
def find_unmarked_places(krp):
    ret = []
    for k, v in krp.initial_place_tokens.items():
        if v == 0:
            ret.append(k)
    return ret

def find_same_input_transactions(krp):
    ret = []
    for elem_1 in krp.transactions.values():
        sub_ret = set()
        for elem_2 in krp.transactions.values():
            if elem_1 != elem_2:
                if elem_1.input.keys() == elem_2.input.keys():
                    sub_ret.add(elem_1)
                    sub_ret.add(elem_2)
        if sub_ret not in ret and len(sub_ret) != 0:
            ret.append(sub_ret)
    return ret

