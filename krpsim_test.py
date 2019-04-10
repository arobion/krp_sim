import random
import copy
from krpsim_marking import Marking
from heapq import heappop, heappush

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
#    return (possible_return[random.randint(0,len(possible_return) - 1)])


def create_one_unit_action_2(krp, optimize):
    """
        1) list optimize reworked
        2) lister toutes les actions possibles
        3) choose randomly one
        4) simuler cette action sur les places du graph
        5) define new optimize by a (random?)negative place value
        6) relaunch
        7) repeat until optimize = void
    """
    optimize_list = [optimize]
    list_actions = []
    current_optimize = optimize_list[0]
    simulated_marking = copy.deepcopy(krp.initial_marking)
    while current_optimize:
        possible_actions = krp.places_outputs[current_optimize] # step 2)
#    selection = list_actions[random.randint(0,len(list_actions) - 1)] # step 3)
        selection = possible_actions[0] # not random
        current_optimize = None
        simulate_transaction(krp, simulated_marking, selection) # to do
        current_optimize = get_next_optimize(simulated_marking) # to do
        list_actions.insert(0, selection)

#    print(simulated_marking)
#    print(list_actions)



    return list_actions
def create_one_unit_action(krp, optimize):
    """
    1) recherche `optimize`
    2) lister toutes les actions possibles pour creer cet optimize
    3) choose randomly one
    4) save the action
    5) add all the places inputs of the action in optimize
    6) relaunch with new `optimize`
    7) repeat until all ressource needed are present


    BREAK WHEN OPTIMIZE = empty ??
    optimize va se presneter sous la forme d'une liste qu'on va pop/remplir au fur et a mesure
    Remarques :
    R1) ajouter l'element dans les optimize que si il n'est pas present dans les places
#    R2) ajouter l'element dans les optimize que si il est creable

    A propos du calcul des quantitees.
    il faut trouver le facteur limitant, c'est a dire qu'est ce qui va bloquer une unite de production. dans cet example c'est le four, car non creable, et utilise par "do flan"... humm cela semble etre une mauvaise idee pour do boite puisque une boite necessitera l'utilisation du four par plusieurs process differents.
    sinon pour les quantitees, on regarde combien il en faut pour une input, combien l'action en produit, et on ajoute autant de fois que necessaire l'action dans la liste des actions a effectuer


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


    gerer le cas des fours :
    """
    optimize_list = [optimize]
    list_actions = []

    while len(optimize_list) != 0: # step 6 and 7

        current_optimize = optimize_list.pop(0) # step 1)
        possible_actions = krp.places_outputs[current_optimize] # step 2)
#    selection = list_actions[random.randint(0,len(list_actions) - 1)] # step 3)
        selection = possible_actions[0] # not random
    
#        print(selection, current_optimize)
        for elem in list_actions:
            if current_optimize in elem.input:
                nb_necessary = elem.input[current_optimize]
                nb_created = selection.output[current_optimize]
                print(nb_necessary, nb_created, selection, current_optimize, list_actions, elem)
#                while (nb_necessary > 0):
#                    list_actions.insert(0, selection)
#                    nb_necessary -= nb_created

#                print(elem, current_optimize, selection)

        if selection not in list_actions:
            list_actions.insert(0, selection) # step 4
        for elem in selection.input:
            if krp.initial_place_tokens[elem] == 0: # R1
                print('ici')
                optimize_list.append(elem) # step 5
    return list_actions


def concatenate(krp, list_actions):
    """
    Objectif : remettre toutes les actions dans l'ordre
    lancer les actions des que possibles en meme temps
    sommer le gain et le cout en cycle
    retourner un score ?? 
    1) parcourir la liste des actions. des qu'une action est lancable, la passer dans la "ordered list" et la remove de la list actions
    2) quand on a parcouru toute la liste, fire each transaction in ordered list
    3) resourdre la premiere transition
    3) repeter jusqu'a avoir viday la list_actions
    


    IL MANQUE la geston des cycles, et le classement des transtion par cycle de fin
    """
    ordered_list = []
    current_cycle = krp.initial_marking.cycle
    while (len(list_actions)):
        index = 0
        len_tot = len(list_actions)
        while index < len_tot:
            if is_firable(krp, list_actions[index]):
                fire_transition(krp, list_actions[index], current_cycle)
                del list_actions[index]
                len_tot -= 1
                continue
            index += 1
        current_cycle = resolve_nearest_transitions(krp, current_cycle)
    krp.initial_marking.cycle = current_cycle

    

def is_firable(krp, transition):
    for place_name, required_value in transition.input.items():
        if krp.initial_marking.place_tokens[place_name] < required_value:
            return False
    return True

def fire_transition(krp, transition, current_cycle):
    ending = transition.duration + current_cycle
    heappush(krp.initial_marking.transition_tokens, (ending, transition.name)) # transition
    for place_name, required_value in transition.input.items():
        krp.initial_marking.place_tokens[place_name] -= required_value

def resolve_nearest_transitions(krp, current_cycle):
    if len(krp.initial_marking.transition_tokens) == 0:
        return current_cycle
    transition = heappop(krp.initial_marking.transition_tokens)
    for place_name, required_value in krp.transitions[transition[1]].output.items():
        krp.initial_marking.place_tokens[place_name] += required_value
    print("{}:{}".format(transition[0] - krp.transitions[transition[1]].duration, transition[1]))
    return transition[0]
    

def poc(krp):

#    optimize_list = [krp.optimize[0]]
    while (krp.initial_marking.cycle < krp.delay):
        list_actions = create_one_unit_action_2(krp, "euro")
        concatenate(krp, list_actions)
#    concatenate(krp, list_actions) # il manque la gestion des cycles
#    list_actions = create_one_unit_action_2(krp, "flan") # il manque la gestion des quantite

#    print("\n")
#    for elem in list_actions:
#        print(elem)
#    print("\n")
    
#    print(krp.initial_marking)


