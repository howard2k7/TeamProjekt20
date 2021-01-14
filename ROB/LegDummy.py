class LegDummy:

    def __init__(self, id, legPosition, id1, id2, id3):
        self.id = id
        self.legPosition = legPosition
        self.id1 = id1
        self.id2 = id2
        self.id3 = id3

    def getFootPosition(self):
        return self.legPosition

    def setFootPos(self, pos):
        self.legPosition = pos