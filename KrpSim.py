from krpsim_bruteforce import bruteforce
from krpsim_graph import KrpsimGraph
from krpsim_setting import Setting
from krpsim_marking import Marking
from krpsim_test import poc, print_dico
import copy


def solve(krpsim):
    bruteforce_result, is_timeout = bruteforce(copy.deepcopy(krpsim))
    bruteforce_result[1].initial_marking.transition_tokens = []
    if not is_timeout:
        with open("trace", "w") as f:
            f.write(bruteforce_result[2])
        if bruteforce_result[2] == "":
            print("not enough cycles, nothing done")
        else:
            print(bruteforce_result[1].initial_marking)
        return
    print("brute force timed out, switch to colibri algorithm")
    best_score, best_marking, best_random_set, best_out = poc(krpsim)
    best_marking.transition_tokens = []

    # Comparison with brute force approach
    if best_out == None:
        print("Unable to find a solution, file is too complex")
        return
    if (bruteforce_result[1].initial_marking.place_tokens[krpsim.optimize[0]] >
            best_score):
        with open("trace", "w") as f:
            f.write(bruteforce_result[2])
        print(bruteforce_result[1].initial_marking)
    else:
        with open("trace", "w") as f:
            f.write(best_out[0])
        print_dico(best_random_set)
        print(best_marking)


def main():
    setting = Setting()
    krpsim = KrpsimGraph(setting)
    krpsim.initial_marking = Marking(0, krpsim.initial_place_tokens.copy(), [], krpsim.transitions)
    solve(krpsim)

if __name__ == "__main__":
    main()


