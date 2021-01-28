import copy
import math
import time
import numpy as np
import sys

from mincom import MinCom
from HexaplotSender import HexaplotSender
from LegDummy import LegDummy
from COM.Robhost import Host


# from LegServo.LegFF import Leg


class Robot:
    # Roboter statische Parameter
    moveZMax = 0.03  # max. Höhe vom Arbeitsbereich nach Z
    moveXMax = 0.06  # max. Durchmesser vom Arbeitsbereich nach X

    def __init__(self, testMode=False):

        self.testMode = testMode  # Flag für Testmodus (Hexaplotter, DummyLegs)

        if self.testMode:
            self.host = Host()
            # hexaplotter
            self.hs = HexaplotSender()
            # Testkommunikationsobjekt erzeugen
            # self.mc = MinCom()
            # sechs Beinobjekte mit entsprechenden Joint IDs erzeugen
            self.legs = [LegDummy(1, 1, 3, 5), LegDummy(2, 2, 4, 6),
                         LegDummy(3, 8, 10, 12), LegDummy(4, 14, 16, 18),
                         LegDummy(5, 13, 15, 17), LegDummy(6, 7, 9, 11)]
            #self.legs = [LegDummy(1, 1, 3, 5)]
        else:
            # Kommunikationsobjekt erzeugen
            if len(sys.argv) > 1:  # or ==3
                self.host = Host(str(sys.argv[1]), str(sys.argv[2]))
            else:
                self.host = Host()
            # sechs reale Beinobjekte mit entsprechenden Joint IDs erzeugen
            # self.legs = [Leg(1, 1, 3, 5), Leg(2, 2, 4, 6),
            # Leg(3, 8, 10, 12), Leg(4, 14, 16, 18),
            # Leg(5, 13, 15, 17), Leg(6, 7, 9, 11)]
            self.legs = [Leg(1, 3, 14, 15)]

        self.legStartPositions = [[0.186, -0.0315, -0.012, 1], [0.15, 0.08, -0.08, 1], [0, 0.18, -0.08, 1],
                                  [-0.15, 0.08, -0.08, 1], [-0.15, -0.08, -0.08, 1], [0, -0.18, -0.08, 1]]

        self.cycleTime = 0.05  # Durchlaufzeit einer Iteration in Sekunden
        self.oneStepTime = 1.0  # Durchlaufzeit einer ganzen Bewegung durch die Trajektorienliste
        self.coordPoints = math.floor(self.oneStepTime / self.cycleTime)
        #  self.coordPoints = 510 manuell Anzahl Punkte, die Roboter laufen soll, setzten für Testzwecke

        # Roboter veränderbare Parameter
        self.velocity = 0.0  # Geschwindigkeit (0.0 0.5 1.0)
        self.degree = 0  # Grad der Bewegung/Trajektorie in Radiant (für Bewegungsänderung)
        self.currentZ = Robot.moveZMax
        # self.currentX = 0

        self.cachedCommands = []  # Kommandos cachen zur späteren Überprüfung (degree [0], velocity [1], maxZ [2])

        if self.testMode:
            startPoints = []
            for i in range(len(self.legs)):
                startPoints.append(self.legStartPositions[i])
            self.hs.send_points(startPoints)
            time.sleep(2)

        time.sleep(1)
        # Setze Beine in die Anfangsposition (Stemmungsposition, Schwingungsposition)
        self.moveLegsToStartPosition()

        self.middleXZIndex = 0
        self.stopPointDuration = 1  # Anzahl der Iterationen die beim ersten Stemmpunkt abwarten soll (Haltepunkt)
        # Trajektorienliste mit Trajektorienpunkten erzeugen
        self.traj = self.createTraj(Robot.moveZMax)
        self.currentTraj = copy.copy(self.traj)

        print("Folgende Trajektorie wird angefahren: " + str(self.traj))
        # print("Trajektorienlänge: " + str(len(self.traj)))

        self.trajAIndex = -1  # Schwingungsanfangsindex
        self.trajBIndex = math.floor(len(self.currentTraj) / 2) - 1  # Stemmungsanfangsindex

        time.sleep(1)

        self.iterate()

    def moveLegsToStartPosition(self):
        newPos = []
        for i in range(len(self.legs)):
            tmp = copy.copy(self.legStartPositions[i])
            if (i % 2) == 0:  # [0, 0, 0, 1]
                tmp[0] += (Robot.moveXMax / 2)
            else:
                tmp[0] -= (Robot.moveXMax / 2)
            self.legs[i].setFootPosPoints(tmp)
            newPos.append(tmp)
        if self.testMode:
            self.hs.send_points(newPos)

    def createTraj(self, maxZ):
        trajectory = []
        if self.coordPoints % 4 != 0:
            raise ValueError("illegal Coordpoints")
        xPoints = int(self.coordPoints / 2) + 1
        xzPoints = int(self.coordPoints / 2) - 1
        self.middleXZIndex = math.ceil(xzPoints / 2)
        # print(self.middleXZIndex)
        # xMax/2 = 0.03 m
        # zMax = 0.03 m

        # Erstelle Punkte auf der mit x,z Koordinaten (Schwingphase)
        for i in range(1, xzPoints + 1):
            x = -Robot.moveXMax / 2 + i * (Robot.moveXMax / (xzPoints + 1))
            z = -maxZ / math.pow(Robot.moveXMax / 2, 2) * x ** 2 + maxZ
            trajectory.append([x, 0.0, z, 1])
        # Erstelle Punkte die auf x Achse liegen (Stemmphase)
        for i in range(0, xPoints):
            x = Robot.moveXMax / 2 - i * (Robot.moveXMax / (xPoints - 1))
            if i == 0:  # Haltepunkt für die Stemmphase
                for j in range(self.stopPointDuration):
                    trajectory.append([x, 0.0, 0.0, 1])
            trajectory.append([x, 0.0, 0.0, 1])
        # print("Folgende Trajektorie wurde erstellt: " + str(trajectory))
        return trajectory

    def iterate(self):
        while True:
            tStart = time.perf_counter()

            self.getNewCommands()  # Kommunikationsobjekt abfragen
            # wenn neue Kommandos dann ggf. (Richtungsänderung, Höhenverstellung, Geschwindigkeitsreduzierung/erhöhung)
            # -> Hoehenverstellung ueber self.extremeZ
            # Trajektorie aendern wenn ein Bein in der Startposition

            if self.cachedCommands:
                if self.velocity != self.cachedCommands[0]:
                    self.velocity = self.cachedCommands[0]
                    # print("Velocity: " + str(self.velocity))
                if self.velocity == 0.0:  # Breche Iterationsdurchlauf ab, wenn keine Geschwindigkeit
                    # print("Roboter steht!")
                    continue
                if self.currentZ != (self.cachedCommands[2] * Robot.moveZMax):
                    self.currentZ = self.cachedCommands[2] * Robot.moveZMax
                    self.traj = self.createTraj(self.currentZ)
                    self.currentTraj = copy.copy(self.traj)
                    if self.degree != 0:
                        self.rotateTraj(self.degree)
                    print("Aktuelle Trajektorie mit neuer Höhe bei: " + str(self.currentZ) + str(self.currentTraj))
                    # print("Height: " + str(self.currentZ))
                # Überprüfe, ob aktuelle Leg Position in der Mitte der Trajektorie liegt,um Trajektorie um Z zu rotieren
                if (self.cachedCommands[1] != self.degree) and (
                        (self.trajAIndex == (self.middleXZIndex - 1) or self.trajBIndex == (self.middleXZIndex - 1))):
                    self.degree = self.cachedCommands[1]
                    self.rotateTraj(self.degree)
                    print(
                        "Aktuelle Trajektorie mit neuer Richtung bei Grad: " + str(self.degree) + str(self.currentTraj))
            else:  # Keine Kommandos. Warte auf Kommandos...
                continue

            # Überprüfe ob trajIndices außerhalb von TrajListe, sonst auf -1 setzen
            if self.trajAIndex + 1 > len(self.traj) - 1:
                self.trajAIndex = -1
            if self.trajBIndex + 1 > len(self.traj) - 1:
                self.trajBIndex = -1

            # einen Trajektorienpunkt für
            # schwingendes Bein und einen für
            # stemmendes Bein aus der einzigen
            # Punkteliste holen
            legATraj = self.currentTraj[self.trajAIndex + 1]
            legBTraj = self.currentTraj[self.trajBIndex + 1]
            # print(legATraj)
            # print(legBTraj)

            # Stemmtrajektorienpunkt an die Orte
            # der drei stemmenden Beine verschieben
            # Schwingtrajektorienpunkt an die Orte
            # der drei schwingenden Beine verschieben
            allCurrentPositions = []
            for i in range(len(self.legs)):
                if (i % 2) != 0:
                    allCurrentPositions.append(self.moveToPos(i, legATraj))
                else:
                    allCurrentPositions.append(self.moveToPos(i, legBTraj))
            # Punkte zur Ausführung an die
            # Beinobjekte übergeben
            # print(allCurrentPositions)
            if self.testMode:
                self.hs.send_points(allCurrentPositions)  # sende an plotter
            else:
                # for i, val in self.legs:   #  TODO bei 6 Beinen Index durch i ersetzten
                if allCurrentPositions[0] != (self.moveToPos(0, self.currentTraj[self.trajAIndex])):
                    self.legs[0].setFootPosPoints(allCurrentPositions[0], self.velocity)
            #print(allCurrentPositions[0] == (self.moveToPos(0, self.currentTraj[self.trajBIndex])))
            #print("Move to: " + str(allCurrentPositions[0]))
            #print("Current Trajectory Point: " + str((self.moveToPos(0, self.currentTraj[self.trajBIndex]))))
            self.trajAIndex += 1
            self.trajBIndex += 1

            tEnd = time.perf_counter()
            periodLength = tEnd - tStart
            #  print("periodLength: " + str(periodLength) + " (aus Zeile 198)")  # dient zu Testzwecken
            #  print("Iterate Durchlauf vorbei.")
            time.sleep((self.cycleTime - periodLength) / self.velocity)

    def moveToPos(self, legIndex, traj):
        moveToPos = []
        for i in range(len(traj) - 1):
            moveToPos.append(self.legStartPositions[legIndex][i] + traj[i])
        moveToPos.append(1.0)
        return moveToPos

    def getNewCommands(self):  # erhalte neue Kommandos
        if self.testMode:
            #  print("Trying to get new Commands")
            commands = self.host.lastPressed
            # commands = self.mc.getData()
        else:
            commands = self.host.lastPressed  # list[velocity(0.0 bis 1.0)],[degree(rad)],[maxZ(0.0 bis 1.0)]
        if self.cachedCommands == commands or commands == 0 or (
                any(isinstance(x, str) for x in commands)):  # keine neuen Kommandos oder ungültig
            return
        self.cachedCommands = commands
        print(commands)

    def rotateTraj(self, degree):  # erstellt rotierten Vektor um z Achse um Grad degree
        self.currentTraj = []
        rotationMatrix = np.array([(math.cos(degree), -math.sin(degree), 0, 0),
                                   (math.sin(degree), math.cos(degree), 0, 0),
                                   (0, 0, 1, 0),
                                   (0, 0, 0, 1)])
        for i in range(len(self.traj)):
            self.currentTraj.append(list(rotationMatrix.dot(self.traj[i])))


if __name__ == "__main__":
    rb = Robot(True)
