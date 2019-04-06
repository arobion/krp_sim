class Transaction():

    def __init__(self, name="", input={}, output={}, duration=0):
        self.name = name
        self.input = input
        self.output = output
        self.duration = duration

    def __add__(self, other):
        for elem in other.input.keys():
            if elem not in self.input:
                self.input[elem] = other.input[elem]
            else:
                self.input[elem] += other.input[elem]
        for elem in other.output.keys():
            if elem not in self.output:
                self.output[elem] = other.output[elem]
            else:
                self.output[elem] += other.output[elem]

    def __str__(self):
        return "{}: {} {} {}".format(self.name, self.input, self.output, self.duration)

    #  def __repr__(self):
    #     return "transaction({} {} {})".format(self.input, self.output, self.duration)
