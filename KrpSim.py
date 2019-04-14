from krpsim_bruteforce import bruteforce
from krpsim_graph import KrpsimGraph
from krpsim_setting import Setting
from krpsim_marking import Marking
from krpsim_test import poc, print_dico
import copy


def solve(krpsim):
    bruteforce_result = bruteforce(copy.deepcopy(krpsim))
    best_score, best_marking, best_random_set, best_out = poc(krpsim)

    # Comparison with brute force approach
    if (bruteforce_result[1].initial_marking.place_tokens[krpsim.optimize[0]] >
            best_score):
        print(brute_force_result[2])
    else:
        print("{}".format(best_out[0]))
        print_dico(best_random_set)
        print(best_marking)


def main():
    setting = Setting()
    krpsim = KrpsimGraph(setting)
    krpsim.initial_marking = Marking(0, krpsim.initial_place_tokens.copy(), [], krpsim.transitions)
    solve(krpsim)

if __name__ == "__main__":
    main()


