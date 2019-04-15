from krpsim_transition import Transition

'''
Contain:
- SerialFusion
- PreFusion
- LateralTransitionsFusionOne
- LateralTransitionsFusionTwo
- LateralPlacesFusion
'''


class SerialFusion:

    def __init__(self, krp):
        self.krp = krp

    def detect(self):
        for place, value in self.krp.initial_place_tokens.items():

            # rule 1: place p is unmarked in the initial marking
            if value != 0:
                continue

            # rule 3: place p is disconnected from all other transitions
            # first check if there is place(s) in places_inputs and places_output
            # then check if the len is 1 or not
            if (place not in self.krp.places_inputs or
                    place not in self.krp.places_outputs or
                    len(self.krp.places_inputs[place]) != 1 or
                    len(self.krp.places_outputs[place]) != 1):
                continue

            # rule 2:
            # 1) place p is the unique output place of t1
            # 2) place p is the unique input place of t2
            t1 = self.krp.places_outputs[place][0]
            t2 = self.krp.places_inputs[place][0]
            if len(t1.output) != 1 or len(t2.input) != 1:
                continue

            self.proceed(place, t1, t2)
            return True

        return False

    def proceed(self, place, t1, t2):
        duration = t1.duration + t2.duration
        name = t1.name + "+" + t2.name
        inputs = t1.input
        outputs = t2.output
        tf = Transition(name=name, input=inputs, output=outputs, duration=duration)
        self.krp.transitions[tf.name] = tf
        self.krp.transformations[tf] = [t1, t2]
        self.krp.transitions.pop(t1.name)
        self.krp.transitions.pop(t2.name)

        self.update_places(place, t1, t2, tf)

    def update_places(self, place, t1, t2, tf):
        self.krp.initial_place_tokens.pop(place)
        self.krp.places_inputs.pop(place)
        self.krp.places_outputs.pop(place)
        for key, val in self.krp.places_inputs.items():
            if val[0] == t1:
                self.krp.places_inputs[key][0] = tf
        for key, val in self.krp.places_outputs.items():
            if val[0] == t2:
                self.krp.places_outputs[key][0] = tf


class PreFusion:

    def __init__(self, krp):
        self.krp = krp

    def detect(self):
        unmarked_places = find_unmarked_places(self.krp)
        return False
        print("Doing prefusion")


class LateralTransitionsFusionOne:
    def __init__(self, krp):
        self.krp = krp

    def detect(self):
        S_list = find_same_input_transitions(self.krp)
        for S in S_list:
            rule_2 = True
            rule_1 = set()
            rule_4 = set()
            for transition in S:
                for elem in transition.output.keys():
                    if len(self.krp.places_outputs[elem]) != 1:
                        rule_2 = False
                    if elem in self.krp.places_inputs:
                        rule_1.add(tuple(self.krp.places_inputs[elem]))
                    else:
                        rule_1.add(False)
                    rule_4.add(self.krp.initial_place_tokens[elem])
            if rule_2 is True and len(rule_1) == 1 and len(rule_4) == 1:
                print('doing lateral transitions fusion 1')
                self.proceed(S)
                return True
        return False

    """
    fusion all the t in S in Tf
    remove all the t in S from krp.transition
    add tf in transition
    remove
    """

    def proceed(self, S):
        duration = 0
        name = ""
        tf = Transition(name="", input={}, output={}, duration=0)
        for transition in S:
            if transition.duration > duration:
                duration = transition.duration
            if name == "":
                name = transition.name
            else:
                name += "+" + transition.name
            self.merge_transition(tf, transition)
            self.remove_transition(tf, transition)

        tf.name = name
        tf.duration = duration
        self.krp.transitions[tf.name] = tf

    def remove_transition(self, tf, transition):
        self.krp.transitions.pop(transition.name)
        for elem in transition.input:
            self.krp.places_inputs[elem].pop(self.krp.places_inputs[elem].index(transition))
            if tf not in self.krp.places_inputs[elem]:
                self.krp.places_inputs[elem].append(tf)
        for elem in transition.output:
            self.krp.places_outputs[elem].pop(self.krp.places_outputs[elem].index(transition))
            self.krp.places_outputs[elem].append(tf)

    def merge_transition(self, tf, transition):
        nb = 1
        for elem in transition.output:
            for inputs in self.krp.places_inputs[elem][0].input:
                if inputs == elem:
                    nb = self.krp.places_inputs[elem][0].input[inputs]
        for i in range(0, nb):
            tf + transition


class LateralTransitionsFusionTwo:

    def __init__(self, krp):
        self.krp = krp

    def detect(self):
        P_list = find_same_input_places(self.krp)
        for P in P_list:
            rule_2 = True
            rule_3 = True
            S = []
            rule_4 = set()
            for place in P:
                if place not in self.krp.places_inputs:
                    rule_2 = False
                    continue
                if len(self.krp.places_inputs[place]) != 1:
                    rule_2 = False
                else:
                    if len(self.krp.places_inputs[place][0].input.keys()) != 1:
                        rule_3 = False
                    else:
                        S.append(self.krp.places_inputs[place][0])
                        rule_4.add(self.krp.initial_place_tokens[place])

            if rule_2 is True and rule_3 is True and len(rule_4) == 1:
                print("doing lateral transitions fusion 2")
                # proceed_lateral_transition_fusion_2(krp, S)
                return True


class LateralPlacesFusion:

    def __init__(self, krp):
        self.krp = krp

    def detect(self):
        P_list = find_same_input_places(self.krp)
        for P in P_list:
            rule_2 = True
            rule_3 = True
            rule_3_store = set()
            rule_4 = set()
            rule_4.add(0)
            for place in P:
                if len(self.krp.places_outputs[place]) != 1:
                    rule_2 = False
                if place not in self.krp.places_inputs:
                    rule_3 = False
                else:
                    rule_3_store.add(tuple(self.krp.places_inputs[place]))
                    if len(self.krp.places_inputs[place]) != 1:
                        rule_3 = False
                rule_4.add(self.krp.initial_place_tokens[place])
            if rule_2 is True and rule_3 is True and len(rule_4) == 1 and len(rule_3_store) == 1:
                print('doing lateral places fusion')
                self.proceed(P)
                return True
        return False

    """
    fusion all the places in P in pf
    add pf in initial_place_tokens
    update the input transition
    update the output transition
    remove all te places in krp.initial_place_tokens
    remove
    """

    def proceed(self, P):
        pf = ""
        for place in P:
            if pf == "":
                pf = place
            else:
                pf += "+" + place
            self.krp.initial_place_tokens.pop(place)
        self.krp.initial_place_tokens[pf] = 0

        for place in P:
            self.update_place(place, pf)

    def update_place(self, place, pf):
        transition_input = self.krp.places_inputs[place][0]
        transition_input.input.pop(place)
        transition_input.input[pf] = 1
        if place in self.krp.places_inputs:
            self.krp.places_inputs.pop(place)
        if pf not in self.krp.places_inputs:
            self.krp.places_inputs[pf] = [transition_input]

        transition_output = self.krp.places_outputs[place][0]
        transition_output.output.pop(place)
        transition_output.output[pf] = 1
        if place in self.krp.places_outputs:
            self.krp.places_outputs.pop(place)
        if pf not in self.krp.places_outputs:
            self.krp.places_outputs[pf] = [transition_output]


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


def find_same_input_transitions(krp):
    ret = []
    for elem_1 in krp.transitions.values():
        sub_ret = set()
        for elem_2 in krp.transitions.values():
            if elem_1 != elem_2:
                if elem_1.input.keys() == elem_2.input.keys():
                    sub_ret.add(elem_1)
                    sub_ret.add(elem_2)
        if sub_ret not in ret and len(sub_ret) != 0:
            ret.append(sub_ret)
    return ret
