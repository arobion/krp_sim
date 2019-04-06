from krpsim_coverability import brute_force
from krpsim_graph import KrpsimGraph
from krpsim_setting import Setting
from krpsim_marking import Marking
from krpsim_fusions import detect_serial_fusion, detect_pre_fusion, detect_lateral_transaction_fusion_1, detect_lateral_transaction_fusion_2, detect_lateral_places_fusion


def main():
    setting = Setting()
    krpsim = KrpsimGraph(setting)
#    print(krpsim)

    print(krpsim.initial_marking)
    print("")

    while True:
        print('REDUCTION')
        if detect_serial_fusion(krpsim):
            continue
        if detect_pre_fusion(krpsim):
            continue
        if detect_lateral_transaction_fusion_1(krpsim):
            continue
        if detect_lateral_transaction_fusion_2(krpsim):
            continue
        if detect_lateral_places_fusion(krpsim):
            continue

        break

    print(krpsim)

    krpsim.initial_marking = Marking(0, krpsim.initial_place_tokens.copy(), [], krpsim.transactions)
    brute_force(krpsim)

if __name__ == "__main__":
    main()
