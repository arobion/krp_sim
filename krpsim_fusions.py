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


def find_unmarked_places(krp):
    ret = []
    for k, v in krp.initial_place_tokens.items():
        if v == 0:
            ret.append(k)
    return ret


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
