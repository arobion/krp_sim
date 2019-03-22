from krpsim_coverability import brute_force
from krpsim_graph import KrpsimGraph
from krpsim_setting import Setting
from krpsim_fusions import detect_serial_fusion, detect_pre_fusion

def main():
    setting = Setting()
    krpsim = KrpsimGraph(setting)
    print(krpsim)

    print(krpsim.initial_marking)
    print("")

    while True:
        if detect_serial_fusion(krpsim):
            continue
        if detect_pre_fusion(krpsim):
            continue
            
        break

    brute_force(krpsim)

if __name__ == "__main__":
    main()
