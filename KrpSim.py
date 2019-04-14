from krpsim_bruteforce import bruteforce
from krpsim_graph import KrpsimGraph
from krpsim_setting import Setting
from krpsim_marking import Marking
from krpsim_test import poc, print_dico
import copy


def solve(krpsim):
    # run brute force
    bruteforce_result = bruteforce(copy.deepcopy(krpsim))
    if not bruteforce_result.is_timeout:
        print(bruteforce_result.out)
        print(bruteforce_result)
        return

    # run poc
    best_score, best_marking, best_random_set, best_out = poc(copy.deepcopy(krpsim))

    # compare results
    if (bruteforce_result[1].initial_marking.place_tokens[krpsim.optimize[0]] >
            best_score):
        print(bruteforce_result.out)
    else:
        print("{}".format(best_out[0]))
        # print_dico(best_random_set)
        print(best_marking)


def main():
    setting = Setting()
    krpsim = KrpsimGraph(setting)
    solve(krpsim)

if __name__ == "__main__":
    main()


