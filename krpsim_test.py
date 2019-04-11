import random
import copy
from krpsim_marking import Marking
from heapq import heappop, heappush
import time
import sys

def simulate_transaction(krp, sim, transition):
    for place_name, quantity in transition.input.items():
        sim.place_tokens[place_name] -= quantity
    for place_name, quantity in transition.output.items():
        sim.place_tokens[place_name] += quantity

def get_next_optimize(sim):
    possible_return = []
    for place_name, quantity in sim.place_tokens.items():
        if quantity < 0:
            possible_return.append(place_name)
    if len(possible_return) == 0:
        return None
    return (possible_return[0]) # NOT RANDOM
#    return (possible_return[random.randint(0,len(possible_return) - 1)]) # RANDOM

def get_local_maximum(krp, marking, possible_actions, current_optimize):
    """
    How to detect local maximum ? 
    l'idee est de tester chaque action separement en regardant le resultat final en terme de cycle et de quantite ?
    donc 1ere idee simple : on relance la create_one_unit_action_2 pour chacune des actions, et on regarde en combien de cycles elle a cree combien de ce que l'on cherche a optimize
    """
    if len(possible_actions) == 1:
        return possible_actions[0]
    else:
        save = None
        save_value = 0
        for elem in possible_actions:
            list_actions, sim = create_one_unit_action_2(krp, current_optimize, forced_action=elem)
            if save_value < sim.place_tokens[current_optimize]:
                save_value = sim.place_tokens[current_optimize]
                save = elem
        return save


def create_one_unit_action_2(krp, optimize, forced_action=None):
    """
        1) list optimize reworked
        2) lister toutes les actions possibles
        3) choose randomly one
        4) simuler cette action sur les places du graph
        5) define new optimize by a (random?)negative place value
        6) relaunch
        7) repeat until optimize = void

        Rework sur le calcul des quantitees.
        il va falloir simuler chaque actions, pour prendre en compte si une autre action doit etre faite.
        donc on a notre point de depart avec la liste des places
        chaque ation ajoutee a la liste, va modifier cette liste :
        do flan va faire : - 10 jaune d'oeuf, - 4 lait, + 5 flan
        etc etc pour chaque action
        donc ensuite pour realiser un flan il va falloir que l'on optimize l'un des negatifs, par exemple jaune d'oeuf. ## NOTION DE CHOIX AU HASARD OU ALORS DANS L'ORDRE ?? 
        donc l'action separation oeuf => -1 oeuf, + 1 jaune d'oeuf, + 1 blanc d'oeuf
        repeat while oeuf is negatif
        total : - 10 oeuf, -4 lait, +10 be + 5 flan
        il manque les oeuf:
        buy oeuf : -100 euros (9 900 en realitees) + 90 oeuf - 4 lait + 10 be + 5 flan
        buy lait : -100 euros (9 800 en realitee) + 90 oeuf + 1996 lait + 10 be + 5 flan
        donc au total avec les 4 actions on fait:
        10 000 euros => 9 800 euros, 90 oeufs, 1996 lait, 10 be, 5 flan

        About greedy find ( recherche de maximum local a chaque fois ).
        l'idee est de ne plus avoir un choix random, mais un choix determine qui serait le meilleur possible parmis tout les choix disponibles.
        donc on va faire une fonction : get_local_maximum qui va renvoyer la meilleure selection.
        more in get_local_maximum's docstring
    """
    # list_actions = []
    dict_actions = {}
    current_optimize = optimize
    simulated_marking = copy.deepcopy(krp.initial_marking)
    while current_optimize:
        possible_actions = krp.places_outputs[current_optimize] # step 2)
        if forced_action in possible_actions:
            selection = forced_action
        else:
            selection = get_local_maximum(krp, simulated_marking, possible_actions, current_optimize) # OPTIMIZED
            # selection = possible_actions[random.randint(0,len(possible_actions) - 1)] # step 3) # RANDOM
            # selection = possible_actions[0] # NOT RANDOM
        current_optimize = None
        simulate_transaction(krp, simulated_marking, selection)
        current_optimize = get_next_optimize(simulated_marking)

        if selection in dict_actions:
            dict_actions[selection] += 1
        else:
            dict_actions[selection] = 1

    return dict_actions, simulated_marking

# def concatenate(krp, list_actions):
#     """
#     Objectif : remettre toutes les actions dans l'ordre
#     lancer les actions des que possibles en meme temps
#     sommer le gain et le cout en cycle
#     retourner un score ?? 
#     1) parcourir la liste des actions. des qu'une action est lancable, la passer dans la "ordered list" et la remove de la list actions
#     2) quand on a parcouru toute la liste, fire each transaction in ordered list
#     3) resourdre la premiere transition
#     4) repeter jusqu'a avoir viday la list_actions
    
#     """
#     ordered_list = []
#     current_cycle = krp.initial_marking.cycle
#     while (len(list_actions)):
#         index = 0
#         len_tot = len(list_actions)
#         while index < len_tot:
#             if is_firable(krp, list_actions[index]):
#                 fire_transition(krp, list_actions[index], current_cycle)
#                 del list_actions[index]
#                 len_tot -= 1
#                 continue
#             index += 1
#         current_cycle = resolve_nearest_transitions(krp, current_cycle)
#     krp.initial_marking.cycle = current_cycle
    
# def is_firable(krp, transition):
#     for place_name, required_value in transition.input.items():
#         if krp.initial_marking.place_tokens[place_name] < required_value:
#             return False
#     return True

# def fire_transition(krp, transition, current_cycle):
#     ending = transition.duration + current_cycle
#     heappush(krp.initial_marking.transition_tokens, (ending, transition.name)) # transition
#     for place_name, required_value in transition.input.items():
#         krp.initial_marking.place_tokens[place_name] -= required_value

    

def concatenate_dict(krp, dict_actions):
    current_cycle = krp.initial_marking.cycle
    while (len(dict_actions)):
        delete = []
        for transition, times in dict_actions.items():
            if is_fireable(krp, transition, 1):
                if is_fireable(krp, transition, times):
                    fire_transition(krp, transition, current_cycle, times)
                    delete.append(transition)
                else:
                    fireable_times = get_firable_times(krp, transition, times)
                    fire_transition(krp, transition, current_cycle, fireable_times)
                    dict_actions[transition] -= fireable_times
        for transition in delete:
            del dict_actions[transition]
        current_cycle = resolve_nearest_transitions(krp, current_cycle)
        # print_dict_actions(dict_actions)
        # print(krp.initial_marking.place_tokens)
    krp.initial_marking.cycle = current_cycle

def get_firable_times(krp, transition, times):
    for fireable_times in range(times, 1):
        if is_firable(krp, transition, fireable_times):
            return fireable_times
    return 1
    

def is_fireable(krp, transition, times):
    for place_name, required_value in transition.input.items():
        if krp.initial_marking.place_tokens[place_name] < required_value * times:
            return False
    return True


def fire_transition(krp, transition, current_cycle, times):
    ending = transition.duration + current_cycle
    heappush(krp.initial_marking.transition_tokens, (ending, transition.name, times))
    for place_name, required_value in transition.input.items():
        krp.initial_marking.place_tokens[place_name] -= required_value * times


def resolve_nearest_transitions(krp, current_cycle):
    # print(krp.initial_marking.transition_tokens)
    # print(krp.initial_marking.place_tokens)
    if len(krp.initial_marking.transition_tokens) == 0:
        return current_cycle
    cycle = krp.initial_marking.transition_tokens[0][0]
    while len(krp.initial_marking.transition_tokens) != 0 and krp.initial_marking.transition_tokens[0][0] == cycle:
        transition = heappop(krp.initial_marking.transition_tokens)
        for place_name, required_value in krp.transitions[transition[1]].output.items():
            krp.initial_marking.place_tokens[place_name] += required_value * transition[2]
        for i in range(0, transition[2]):
            print("{}:{}".format(transition[0] - krp.transitions[transition[1]].duration, transition[1]))
    # print(krp.initial_marking.transition_tokens)
    # print(krp.initial_marking.place_tokens)
    return transition[0]


def poc(krp):
    total_time = time.time()
    create_time = 0
    concat_time = 0

#    optimize_list = [krp.optimize[0]]
    while (krp.initial_marking.cycle < krp.delay):
        start = time.time()
        dict_actions, sim = create_one_unit_action_2(krp, krp.optimize[0])
        create_time += time.time() - start
        start = time.time()
        concatenate_dict(krp, dict_actions)
        concat_time += time.time() - start

    # print("total time: ", time.time()-total_time)
    # print("create time:", create_time)
    # print("concat time:", concat_time)
    # print(krp.initial_marking)


def print_dict_actions(dict_actions):
    print("")
    for key, value in dict_actions.items():
        print(key.name, value)
