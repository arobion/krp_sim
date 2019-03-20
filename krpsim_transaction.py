class Transaction():

    def __init__(self, name="", input={}, output={}, duration=0):
        self.name = name
        self.input = input
        self.output = output
        self.duration = duration

    def __str__(self):
        return "{} {} {}".format(self.input, self.output, self.duration)

    #  def __repr__(self):
    #     return "transaction({} {} {})".format(self.input, self.output, self.duration)