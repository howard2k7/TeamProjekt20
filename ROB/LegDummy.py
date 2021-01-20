class LegDummy:

    def __init__(self, id, id1, id2, id3, legPosition):
        self.id = id
        self.id1 = id1
        self.id2 = id2
        self.id3 = id3
        self.legPosition = legPosition

    def getlastPosition(self):
        return self.legPosition

    def setFootPosPoints(self, pos):
        self.legPosition = pos