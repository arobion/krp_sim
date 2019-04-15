import random
import copy
from krpsim_marking import Marking
from heapq import heappop, heappush
from concurrent.futures import ProcessPoolExecutor, as_completed


def simulate_transition(krp, sim, transition, ghost):
    for place_name, quantity in transition.input.items():
        sim.place_tokens[place_name] -= quantity
    for place_name, quantity in transition.output.items():
        sim.place_tokens[place_name] += quantity

    for place_name, quantity in transition.input.items():
        if place_name in transition.output.keys():
            if sim.place_tokens[place_name] >= 0:
                if quantity == transition.output[place_name]:
                    if krp.initial_marking.place_tokens[place_name] < quantity:
                        ghost.append([place_name, sim.place_tokens[place_name] - quantity])
#                        print(place_name, sim.place_tokens[place_name], transition)
#                        print(sim)


def get_next_optimize(sim, ghost, krp):
    possible_return = []
    for place_name, quantity in sim.place_tokens.items():
        if quantity < 0:
            possible_return.append(place_name)
    if len(possible_return) == 0:
        if len(ghost) == 0:
            return None
        else:
            elem = ghost.pop(0)
            diff = krp.initial_marking.place_tokens[elem[0]] + elem[1]
            if diff < 0:
                sim.place_tokens[elem[0]] = diff
                return elem[0]
            return None
    return (possible_return[random.randint(0, len(possible_return) - 1)])


def update_dico(krp, action, dico, optimize):
    for elem in krp.transitions.values():
        if action.name == elem.name:
            action = elem
            break 
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
            if elem.output[current_optimize] > elem.input[current_optimize]:
                return False
    return True


def drop_unvalid_actions(possible_actions, krp, sim, list_actions, optimize):
    index = 0
    total_len = len(possible_actions)

    # check if the action is possitive
    while index < total_len:
        elem = possible_actions[index]
        if optimize in elem.input.keys():
            if (elem.output[optimize] - elem.input[optimize] <= 0):
                possible_actions.pop(index)
                total_len -= 1
                continue
        index += 1

    index = 0
    total_len = len(possible_actions)

    # check if the actions is firable
    while index < total_len:
        elem = possible_actions[index]
        if optimize in elem.input.keys():
            if requirements_marking(elem, sim, list_actions, optimize) is False:
                possible_actions.pop(index)
                total_len -= 1
                continue
        index += 1

#    for elem in possible_actions:
#        print(elem)
#    print("\n")


def requirements_marking(transition, sim, list_actions, optimize):
    total_to_add = 0
    for elem in list_actions:
        if optimize in elem.input.keys():
            total_to_add += elem.input[optimize]
    for place, value in transition.input.items():
        if sim.place_tokens[place] + total_to_add - value < 0:
#            print(transition)
            return False
    return True


def create_one_unit_action_2(krp, optimize, dico={}, random_set=None):

    list_actions = []
    current_optimize = optimize
    ghost_optimizes = []
    simulated_marking = copy.deepcopy(krp.initial_marking)

    while current_optimize:
        if current_optimize not in krp.places_outputs:
            return None, None

        possible_actions = copy.deepcopy(krp.places_outputs[current_optimize])
        drop_unvalid_actions(possible_actions, krp, simulated_marking, list_actions, current_optimize)
#        if len(possible_actions) == 0: # checked in positive_actions
#            return None, None

        # check dead loop
        if no_positive_actions(possible_actions, current_optimize) is True:
            return None, None

        selection = get_random_action(
            random_set, possible_actions, current_optimize)

        # check if the action is possitive
#        if current_optimize in selection.input.keys():
#            if (selection.output[current_optimize] -
#                    selection.input[current_optimize]) <= 0:
#                continue

        # check if the actions is firable
#        if current_optimize in selection.input.keys():
#            if requirements_marking(selection, simulated_marking, list_actions, current_optimize) is False:
#                continue

        # update true random
        if len(possible_actions) > 1:
            update_dico(krp, selection, dico, current_optimize)

        simulate_transition(krp, simulated_marking, selection, ghost_optimizes)
        current_optimize = get_next_optimize(simulated_marking, ghost_optimizes, krp)

        list_actions.insert(0, selection)

    return list_actions, simulated_marking


def concatenate_dict(krp, list_actions, out):
    current_cycle = krp.initial_marking.cycle
    while (len(list_actions)):
        index = 0
        total_len = len(list_actions)
        while index < total_len:
            if is_fireable(krp, list_actions[index], 1):
                fire_transition(
                    krp, list_actions[index], current_cycle, 1, out)
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
        if (krp.initial_marking.place_tokens[place_name] <
                required_value * times):
            return False
    return True


def fire_transition(krp, transition, current_cycle, times, out):
    ending = transition.duration + current_cycle
    heappush(krp.initial_marking.transition_tokens,
             (ending, transition.name, times))
    for place_name, required_value in transition.input.items():
        krp.initial_marking.place_tokens[place_name] -= required_value * times
    for i in range(0, times):
        out[0] = out[0] + "{}:{}\n".format(current_cycle, transition.name)


def resolve_nearest_transitions(krp, current_cycle):
    if len(krp.initial_marking.transition_tokens) == 0:
        return current_cycle
    cycle = krp.initial_marking.transition_tokens[0][0]
    while (len(krp.initial_marking.transition_tokens) != 0 and
            krp.initial_marking.transition_tokens[0][0] == cycle):
        transition = heappop(krp.initial_marking.transition_tokens)
        for place_name, required_value in krp.transitions[
                transition[1]].output.items():
            krp.initial_marking.place_tokens[place_name] += (
                    required_value * transition[2])
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
        dict_actions, sim = create_one_unit_action_2(
                krp, krp.optimize[0], dico=dico, random_set=random_set)
        if dict_actions is None:
            break
#        for elem in dict_actions:
#            print(elem)
#        print("")
#        print(sim)

        concatenate_dict(krp, dict_actions, out)
    return tuple((dico, krp, out))


def poc(krp):
    dico = {}
    random_set = None

    iterations = 5
    nb_agents = 12

    best_marking = None
    best_score = 0
    best_random_set = None
    best_out = None

    for i in range(0, iterations):
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

            if (res.result()[1].initial_marking.place_tokens[krp.optimize[0]] >
                    best_score):
                best_score = res.result()[1].initial_marking.place_tokens[
                        krp.optimize[0]]
                best_marking = copy.deepcopy(res.result()[1].initial_marking)
                best_random_set = res.result()[0]
                best_out = res.result()[2]
            krp.initial_marking = Marking(
                    0, krp.initial_place_tokens.copy(), [], krp.transitions)

    return best_score, best_marking, best_random_set, best_out
