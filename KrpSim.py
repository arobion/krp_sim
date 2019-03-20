from krpsim_coverability import brute_force
from krpsim_solver import solver
from krpsim_graph import KrpsimGraph
from krpsim_setting import Setting

def main():
    setting = Setting()
    krpsim = KrpsimGraph(setting)
    #krpsim = KrpsimGraph()
    print(krpsim)

    print(krpsim.initial_marking)
    print("")
    #brute_force(krpsim)

if __name__ == "__main__":
    main()
