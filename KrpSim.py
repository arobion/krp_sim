from krpsim_coverability import brute_force
from krpsim_solver import solver
from krpsim_graph import KrpsimGraph

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





def detect_serial_fusion(krp):
    unmarked_places = find_unmarked_places(krp)
    for place in unmarked_places:
        if place not in krp.places_inputs.keys() or place not in krp.places_outputs.keys():
            continue
        if len(krp.places_inputs[place]) == 1 and len(krp.places_outputs[place]) == 1:
            if check_transaction_inputs(krp, krp.places_outputs[place][0]):
                print("serial_fusion:", place, krp.places_outputs[place][0].name, krp.places_inputs[place][0].name)


def main():
    krpsim = KrpsimGraph()
    print(krpsim)

    print(krpsim.initial_marking)
    print("")
    detect_serial_fusion(krpsim)

#    brute_force(krpsim)

if __name__ == "__main__":
    main()
