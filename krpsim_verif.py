from krpsim_tool_verif import Setting, Config_structure, Env
from krpsim_error import ErrorOutput, CustomError


def get_action(action):
    tab = action.split(':')
    if len(tab) != 2:
        raise ErrorOutput("KRP Error: Bad output from the KRP_SIM trace")
    try:
        cycle = int(tab[0])
    except Exception:
        raise ErrorOutput("KRP Error: Cycle should be a valid integer")
    return cycle, tab[1]


def main():
    setting = Setting()
    config = Config_structure()
    config.stock = setting.stock
    config.process = setting.process

    env = Env(config)
    try:
        for action in setting.actions:
            cycle, name = get_action(action)
            if cycle < env.cycle:
                raise ErrorOutput("Cycle problem in tracefile ({} < {})".format(cycle, env.cycle))
            env.update_cycle(cycle)
            env.process(name)
        print("VERIFICATION OK")
    except CustomError as err:
        print(err)


if __name__ == "__main__":
    main()
