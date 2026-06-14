class process:
    def __init__(self, pid, pmax, allocation):
        self.pid = pid
        self.pmax = pmax
        self.allocation = allocation
        self.is_finished = bool(False)

    @property
    def need(self):
        return [self.pmax[i] - self.allocation[i] for i in range(len(self.pmax))]
        
