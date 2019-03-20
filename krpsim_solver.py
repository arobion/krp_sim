class Node():

    def __init__(self):
        self.childs = {}


class Bchain():

    def __init__(self):
        self.root = None


def solver(krp):
    search = 'armoire'
    stockq = []

    for key, val in krp.transactions.items():
        if search in val.output.keys():
            for elem, nb in val.input.items():
                stockq.append({elem: nb})
    print(stockq)
