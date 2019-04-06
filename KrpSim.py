from krpsim_coverability import brute_force
from krpsim_graph import KrpsimGraph
from krpsim_setting import Setting
from krpsim_marking import Marking


def main():
    setting = Setting()
    krpsim = KrpsimGraph(setting)
    print(krpsim)

    krpsim.initial_marking = Marking(0, krpsim.initial_place_tokens.copy(), [], krpsim.transitions)
    brute_force(krpsim)

if __name__ == "__main__":
    main()
