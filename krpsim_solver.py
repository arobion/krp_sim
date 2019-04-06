import heapq


def solver(krp):
    path = {}
    list_places = {}
    get_ind_path(krp, krp.optimize[0], path, list_places)
    calc_cost(krp, path)
    print("\nFINAL PATH = ")
    for elem in path:
        print(elem.name)


def get_ind_path(krp, node, path, lst):
    if is_not_producible(krp, node): # do the function 
        return
    else:
        childs = get_childs(krp, node) # recupere les transitions qui creent la node
        rand = 0
#        print(childs[0].name, path)
        path.insert(0, childs[rand])
        for key, val in childs[rand].input.items():
            for i in range(0, val):
                get_ind_path(krp, key, path, lst)


def is_not_producible(krp, node):
    for key, val in krp.transitions.items():
        if node in val.output.keys():
            return False
    return True


def get_childs(krp, node):
    ret = []
    for key, val in krp.transitions.items():
        if node in val.output.keys():
            ret.append(val)
    return ret


def calc_cost(krp, path):
    full_lst = get_empty_list(krp.initial_place_tokens)
    for elem in path:
        for place, nb in elem.input.items():
            if is_not_producible(krp, place) is True:
                full_lst[place] += nb
    nb = how_many(full_lst, krp.initial_place_tokens.copy())
    print(nb)
    simulate(krp, path, nb)


def get_empty_list(places):
    new = places.copy()
    for k in new.keys():
        new[k] = 0
    return new


def how_many(need, initial):
    nb = 0
    while True:
        for k, v in need.items():
            initial[k] -= v
            if initial[k] < 0:
                return nb
        nb += 1


def simulate(krp, path, nb):
    return
#    tot = path * nb
#    places = kpr.initial_place_tokens.copy()
#    cycle = 0
#    while tot:
#        to_pop = []
#        for i in range(0, len(tot)):
#            if is_doable(elem, places):
#                fire_transition(elem, places)
#                to_pop.append(i)
#        for ind in to_pop:
