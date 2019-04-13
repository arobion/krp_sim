from krpsim_coverability import brute_force
from krpsim_graph import KrpsimGraph
from krpsim_setting import Setting
from krpsim_marking import Marking
from krpsim_test import poc


def main():
    setting = Setting()
    krpsim = KrpsimGraph(setting)

    # print(krpsim)
    # krpsim.reduce();

    krpsim.initial_marking = Marking(0, krpsim.initial_place_tokens.copy(), [], krpsim.transitions)

    #brute_force(krpsim)
    # print(type(krpsim.optimize[0]))
    poc(krpsim)

if __name__ == "__main__":
    main()
