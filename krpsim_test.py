import random

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
    """
    optimize_list = [optimize]
    list_actions = []

    while len(optimize_list) != 0: # step 6 and 7

        current_optimize = optimize_list.pop(0) # step 1)
        possible_actions = krp.places_outputs[current_optimize] # step 2)
#    selection = list_actions[random.randint(0,len(list_actions) - 1)] # step 3)
        selection = possible_actions[0] # not random
    
        list_actions.insert(0, selection) # step 4
        for elem in selection.input:
            if krp.initial_place_tokens[elem] == 0: # R1
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
    


    ILO MANQUE la geston des cycles, et le classement des transtion par cycle de fin
    """
    ordered_list = []
    while (len(list_actions)):
        index = 0
        len_tot = len(list_actions)
        while index < len_tot:
            if is_firable(krp, list_actions[index]):
                fire_transition(krp, list_actions[index])
                del list_actions[index]
                len_tot -= 1
                continue
            index += 1
        resolve_nearest_transitions(krp)

    

def is_firable(krp, transition):
    for place_name, required_value in transition.input.items():
        if krp.initial_marking.place_tokens[place_name] < required_value:
            return False
    return True

def fire_transition(krp, transition):
    krp.initial_marking.transition_tokens.append(transition) # transition
    for place_name, required_value in transition.input.items():
        krp.initial_marking.place_tokens[place_name] -= required_value

def resolve_nearest_transitions(krp):
    if len(krp.initial_marking.transition_tokens) == 0:
        return False
    transition = krp.initial_marking.transition_tokens.pop()
    for place_name, required_value in transition.output.items():
        krp.initial_marking.place_tokens[place_name] += required_value
    

def poc(krp):

#    optimize_list = [krp.optimize[0]]
    list_actions = create_one_unit_action(krp, "flan") # il manque la gestion des quantite

    for elem in list_actions:
        print(elem)
    print("\n")
    
    concatenate(krp, list_actions) # il manque la gestion des cycles
    print(krp.initial_marking)


