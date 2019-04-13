import random
import copy
from krpsim_marking import Marking
from heapq import heappop, heappush
from concurrent.futures import ProcessPoolExecutor, as_completed


def simulate_transition(krp, sim, transition):
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
    # return (possible_return[0]) # NOT RANDOM
    return (possible_return[random.randint(0, len(possible_return) - 1)])  # RANDOM


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
        rand = random.randint(0, tot - 1)
        for action, perc in random_set[current_optimize].items():
            threshold += perc
            if rand < threshold:
                return action
    else:
        return (possible_actions[random.randint(0, len(possible_actions) - 1)])


def no_positive_actions(possible_actions, current_optimize):
    for elem in possible_actions:
        if current_optimize not in elem.input.keys():
            return False
        else:
            if elem.output[current_optimize] - elem.input[current_optimize] > 0:
                return False
    return True


def requirements_marking(transition, sim, optimize):
    for place, value in transition.input.items():
        if sim.place_tokens[place] - value < 0 and optimize == place:
            return False
    return True


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
    list_actions = []
    current_optimize = optimize
    simulated_marking = copy.deepcopy(krp.initial_marking)

    while current_optimize:
        if current_optimize not in krp.places_outputs:
            return None, None

        possible_actions = krp.places_outputs[current_optimize]  # step 2)

        if no_positive_actions(possible_actions, current_optimize) is True:  # Check dead looop
            return None, None

        if forced_action in possible_actions:
            selection = forced_action
        else:
            selection = get_random_action(random_set, possible_actions, current_optimize)

        if current_optimize in selection.input.keys():
            if selection.output[current_optimize] - selection.input[current_optimize] <= 0:  # check the action is positive
                continue

        if len(possible_actions) > 1:
            update_dico(selection, dico, current_optimize)  # update true random
        if requirements_marking(selection, simulated_marking, current_optimize) is False:
            continue
        simulate_transition(krp, simulated_marking, selection)
        current_optimize = get_next_optimize(simulated_marking)

        list_actions.insert(0, selection)

    return list_actions, simulated_marking


def concatenate_dict(krp, list_actions, out):
    current_cycle = krp.initial_marking.cycle
    while (len(list_actions)):
        index = 0
        total_len = len(list_actions)
        while index < total_len:
            if is_fireable(krp, list_actions[index], 1):
                fire_transition(krp, list_actions[index], current_cycle, 1, out)
                del list_actions[index]
                total_len -= 1
                continue
            index += 1
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


def fire_transition(krp, transition, current_cycle, times, out):
    ending = transition.duration + current_cycle
    heappush(krp.initial_marking.transition_tokens, (ending, transition.name, times))
    for place_name, required_value in transition.input.items():
        krp.initial_marking.place_tokens[place_name] -= required_value * times
    for i in range(0, times):
        out[0] = out[0] + "{}:{}\n".format(current_cycle, transition.name)


def resolve_nearest_transitions(krp, current_cycle):
    if len(krp.initial_marking.transition_tokens) == 0:
        return current_cycle
    cycle = krp.initial_marking.transition_tokens[0][0]
    while len(krp.initial_marking.transition_tokens) != 0 and krp.initial_marking.transition_tokens[0][0] == cycle:
        transition = heappop(krp.initial_marking.transition_tokens)
        for place_name, required_value in krp.transitions[transition[1]].output.items():
            krp.initial_marking.place_tokens[place_name] += required_value * transition[2]
    return transition[0]


def print_dico(dico):
    if dico:
        for opt, stats in dico.items():
            print(opt)
            tot = 0
            for act, nb in stats.items():
                tot += nb
            for act, nb in stats.items():
                print("    {} : {:.0f} %".format(act.name, (nb / tot) * 100))


def run_one_agent(krp, dico, random_set):
    out = [""]
    while krp.initial_marking.cycle < krp.delay:
        dict_actions, sim = create_one_unit_action_2(krp, krp.optimize[0], dico=dico, random_set=random_set)
        if dict_actions is None:
            break

        concatenate_dict(krp, dict_actions, out)
    return tuple((dico, krp, out))

from krpsim_coverability import brute_force

def poc(krp):
    # optimize_list = [krp.optimize[0]]
    dico = {}
    random_set = None

    iterations = 1
    nb_agents = 1
    best_marking = None 
    best_score = 0
    best_random_set = None
    brute_force_result = brute_force(copy.deepcopy(krp))
    for i in range(0, iterations):
        #print('oo')
        random_set = best_random_set
        futures = []
        with ProcessPoolExecutor(max_workers=nb_agents) as pool:
            for i in range(0, nb_agents):
                dico = {}
                fut = pool.submit(run_one_agent, krp, dico, random_set)
                futures.append(fut)
        results = []
        for res in as_completed(futures):
            if res.result() is None:
                continue
            results.append(res.result())

            if res.result()[1].initial_marking.place_tokens[krp.optimize[0]] > best_score:
                best_score = res.result()[1].initial_marking.place_tokens[krp.optimize[0]]
                best_marking = copy.deepcopy(res.result()[1].initial_marking)
                best_random_set = res.result()[0]
                best_out = res.result()[2]
            krp.initial_marking = Marking(0, krp.initial_place_tokens.copy(), [], krp.transitions)

    # Comparison with brute force approach
    
    if brute_force_result[1].initial_marking.place_tokens[krp.optimize[0]] > best_score:
        print(brute_force_result[2])
    else:
        print("{}".format(best_out[0]))
        print_dico(best_random_set)
        print(best_marking)
