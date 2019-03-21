from krpsim_transaction import Transaction

"""
unmarked = find_unmarked
for place in unmarked_place:


"""
def detect_pre_fusion(krp):
    unmarked_places = find_unmarked_places(krp)
    return False
















#################################################################
###################  SERIAL FUSION PART #########################
#################################################################

def detect_serial_fusion(krp):
    unmarked_places = find_unmarked_places(krp)
    for place in unmarked_places:
        if place not in krp.places_inputs.keys() or place not in krp.places_outputs.keys():
            continue
#        print(len(krp.places_inputs[place][0].input)," AND AND", len(krp.places_outputs[place][0].output))
        if len(krp.places_inputs[place]) == 1 and len(krp.places_outputs[place]) == 1:
            if len(krp.places_inputs[place][0].input) == 1 and len(krp.places_outputs[place][0].output) == 1:
                if check_transaction_inputs(krp, krp.places_outputs[place][0]):
                    proceed_serial_fusion(krp, place, krp.places_outputs[place][0], krp.places_inputs[place][0])
                    return True
    return False

def find_unmarked_places(krp):
    ret = []
    for k, v in krp.initial_place_tokens.items():
        if v == 0:
            ret.append(k)
    return ret

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
