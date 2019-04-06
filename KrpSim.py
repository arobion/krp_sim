from krpsim_coverability import brute_force
from krpsim_graph import KrpsimGraph
from krpsim_setting import Setting
from krpsim_marking import Marking
from krpsim_fusions import SerialFusion, PreFusion, LateralTransitionsFusionOne, LateralTransitionsFusionTwo, LateralPlacesFusion


def main():
    setting = Setting()
    krpsim = KrpsimGraph(setting)
#    print(krpsim)

    print(krpsim.initial_marking)
    print("")

    sf = SerialFusion(krpsim)
    pf = PreFusion(krpsim)
    ltf1 = LateralTransitionsFusionOne(krpsim)
    ltf2 = LateralTransitionsFusionTwo(krpsim)
    lpf = LateralPlacesFusion(krpsim)

    while True:
        if sf.detect():
            continue
        if pf.detect():
            continue
        if ltf1.detect():
            continue
        if ltf2.detect():
            continue
        if lpf.detect():
            continue
        break

    print(krpsim)

    krpsim.initial_marking = Marking(0, krpsim.initial_place_tokens.copy(), [], krpsim.transitions)
    brute_force(krpsim)

if __name__ == "__main__":
    main()
