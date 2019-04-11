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



def update_dico(action, dico, optimize):
    if optimize not in dico.keys():
        dico[optimize] = {action: 1}
    elif action not in dico[optimize].keys():
        dico[optimize][action] = 1
    else:
        dico[optimize][action] += 1

def get_random_action(random_set, possible_actions, current_optimize):
    if len(possible_actions) == 1:
        return possible_actions[0]

    if random_set:
        tot = 0
        for act, nb in random_set[current_optimize].items():
            tot += nb
        threshold = 0
        rand = random.randint(0, tot)
        for action, perc in random_set[current_optimize].items():
            threshold += perc
            if rand < threshold:
                for elem in possible_actions:
                    if elem.name == action:
                        return elem
    else:
        return (possible_actions[random.randint(0,len(possible_actions) - 1)])

def create_one_unit_action_2(krp, optimize, forced_action=None, dico={}, random_set=None):
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
#            selection = get_local_maximum(krp, simulated_marking, possible_actions, current_optimize) # OPTIMIZED
            selection = get_random_action(random_set, possible_actions, current_optimize)
#             selection = possible_actions[random.randint(0,len(possible_actions) - 1)] # step 3) # RANDOM
            # selection = possible_actions[0] # NOT RANDOM
        if len(possible_actions) > 1:
            update_dico(selection, dico, current_optimize)
        current_optimize = None
#        print(selection)
        simulate_transaction(krp, simulated_marking, selection)
        current_optimize = get_next_optimize(simulated_marking)

        if selection in dict_actions:
            dict_actions[selection] += 1
        else:
            dict_actions[selection] = 1

    return dict_actions, simulated_marking
    

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
    if len(krp.initial_marking.transition_tokens) == 0:
        return current_cycle
    cycle = krp.initial_marking.transition_tokens[0][0]
    while len(krp.initial_marking.transition_tokens) != 0 and krp.initial_marking.transition_tokens[0][0] == cycle:
        transition = heappop(krp.initial_marking.transition_tokens)
        for place_name, required_value in krp.transitions[transition[1]].output.items():
            krp.initial_marking.place_tokens[place_name] += required_value * transition[2]
#        for i in range(0, transition[2]):
#            print("{}:{}".format(transition[0] - krp.transitions[transition[1]].duration, transition[1]))
    return transition[0]

def print_dico(dico):
    for opt, stats in dico.items():
        print(opt)
        tot = 0
        for act, nb in stats.items():
            tot += nb
        for act, nb in stats.items():
            print("    {} : {:.0f} %".format(act.name, (nb / tot) * 100))

def poc(krp):
    # total_time = time.time()
    # create_time = 0
    # concat_time = 0

    # optimize_list = [krp.optimize[0]]
    dico = {}
    random_set = None
#    random_set = {'euro' : {'vente_flan' : 4, 'vente_tarte_pomme' : 38, 'vente_boite' : 53, 'vente_tarte_citron': 6},
#                  'oeuf' : {'buy_oeuf' : 51, 'reunion_oeuf': 49},
#                  'blanc_oeuf' : {'do_pate_sablee' : 51, 'separation_oeuf': 49} }
    iterations = 5;
    nb_agents = 5;
    best_marking = None 
    best_score = 0
    best_random = {}
    for i in range(0, iterations):
        dico = {}
        while (krp.initial_marking.cycle < krp.delay):
#        start = time.time()
            dict_actions, sim = create_one_unit_action_2(krp, krp.optimize[0], dico=dico, random_set=random_set)
#        create_time += time.time() - start
#        start = time.time()
            concatenate_dict(krp, dict_actions)
#        concat_time += time.time() - start
        if krp.initial_marking.place_tokens[krp.optimize[0]] > best_score:
            best_score = krp.initial_marking.place_tokens[krp.optimize[0]]
            best_marking = copy.deepcopy(krp.initial_marking)
            best_random_set = dico
        krp.initial_marking = Marking(0, krp.initial_place_tokens.copy(), [], krp.transitions)
    print_dico(best_random_set)
    print(best_marking)

    # print("total time: ", time.time()-total_time)
    # print("create time:", create_time)
    # print("concat time:", concat_time)
#    print_dico(dico)
#    print(krp.initial_marking)


def print_dict_actions(dict_actions):
    print("")
    for key, value in dict_actions.items():
        print(key.name, value)
