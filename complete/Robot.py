import copy
import math
import time
import numpy as np
import sys

from HexaplotSender import HexaplotSender
from LegDummy import LegDummy
from Robhost import Host


from LegFF import Leg


class Robot:
    # Roboter statische Parameter
    moveZMax = 0.092  # max. Höhe vom Arbeitsbereich nach Z
    moveXMax = 0.042  # max. Durchmesser vom Arbeitsbereich nach X

    def __init__(self, testMode=False):
        self.testMode = testMode  # Flag für Testmodus (Hexaplotter, DummyLegs)
        z = 0.15
        x = 0.169
        y = 0.089
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
            # self.legs = [LegDummy(1, 1, 3, 5)]
        else:
            # Kommunikationsobjekt erzeugen
            if len(sys.argv) > 1:  # or ==3
                # TCP/UDP + Port als Argumente übergeben
                self.host = Host(str(sys.argv[1]), str(sys.argv[2]))
            else:
                self.host = Host()
            # sechs reale Beinobjekte mit entsprechenden Joint IDs erzeugen
            #self.legs = [Leg(1, 1, 3, 5, False, True, False), Leg(2, 2, 4, 6, False, False, True),
                         #Leg(3, 8, 10, 12, False, True, False), Leg(4, 14, 16, 18, False, True, False),
                         #Leg(5, 13, 15, 17, False, False, True), Leg(6, 7, 9, 11, False, False, True)]

            self.legs = [Leg(1, 3, 14, 15, False, True, False)]

        #  Wähle Startpunkte für jedes Bein
        self.legStartPositions = [[x, -y, -z, 1], [x, y, -z, 1], [0, x + 0.02, -z, 1],
                                  [-x, y, -z, 1], [-x, -y, -z, 1], [0, -x - 0.02, -z, 1]]

        self.cycleTime = 0.05  # Durchlaufzeit einer Iteration in Sekunden
        self.coordPoints = 20  # Anzahl Punkte die der Roboter ablaufen soll

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

        # Setze Beine in die Anfangsposition (Stemmungsposition, Schwingungsposition)
        self.moveLegsToStartPosition()

        self.middleXZIndex = 0
        self.stopPointDuration = 1  # Anzahl der Iterationen die beim ersten Stemmpunkt abwarten soll (Haltepunkt)

        # statische Trajektorienliste mit Trajektorienpunkten erzeugen
        self.traj = self.createTraj(Robot.moveZMax)
        self.currentTraj = copy.copy(self.traj)  # Aktuelle abgelaufene Trajektorie

        self.trajAIndex = -1  # Schwingungsanfangsindex
        self.trajBIndex = math.floor(len(self.currentTraj) / 2) - 1  # Stemmungsanfangsindex

        time.sleep(1)

        self.iterate()

    def moveLegsToStartPosition(self):
        newPos = []
        for i in range(len(self.legs)):
            tmp = copy.copy(self.legStartPositions[i])
            if (i % 2) == 0:  # Schwingbeine um z verschieben
                tmp[2] += Robot.moveZMax
            newPos.append(tmp)
            self.legs[i].setFootPosPoints(tmp, 0)
        if self.testMode:  # Startposition an Hexaplotter senden
            self.hs.send_points(newPos)

    def createTraj(self, newZ):
        trajectory = []
        xPoints = int(self.coordPoints / 2) + 1
        xzPoints = int(self.coordPoints / 2) - 1
        self.middleXZIndex = math.ceil(xzPoints / 2)
        # Erstelle Trajektorien für die Schwingphase
        if len(self.cachedCommands) == 0 or \
                self.cachedCommands[2] != 1:
            for i in range(1, xzPoints + 1):
                x = -Robot.moveXMax / 2 + i * (Robot.moveXMax / (xzPoints + 1))
                z = -(newZ * x ** 2 * 4) / (Robot.moveXMax ** 2) + newZ
                trajectory.append([x, 0.0, z, 1])
        else:  # Erstelle Trajektorie für drittes Hindernis
            for i in range(1, int(xzPoints / 3) + 1):
                z = i * ((Robot.moveZMax - (Robot.moveXMax / 2)) / int(xzPoints / 3))
                trajectory.append([-Robot.moveXMax / 2, 0, z, 1])
            for i in range(1, int(xzPoints / 3) + 1):
                x = -Robot.moveXMax / 2 + i * (Robot.moveXMax / ((xzPoints / 3) + 1))
                z = math.sqrt((Robot.moveXMax / 2) ** 2 - x ** 2) + Robot.moveZMax - Robot.moveXMax / 2
                trajectory.append([x, 0, z, 1])
            for i in range(0, int(xzPoints / 3)):
                z = Robot.moveZMax - (Robot.moveXMax / 2) - i * ((
                        Robot.moveZMax - (Robot.moveXMax / 2)) / (xzPoints / 3))
                trajectory.append([Robot.moveXMax / 2, 0, z, 1])
        # Erstelle Trajektorien für die Stemmphase
        for i in range(0, xPoints):
            x = Robot.moveXMax / 2 - i * (Robot.moveXMax / (xPoints - 1))
            if i == 0:  # Haltepunkt für die Stemmphase
                for j in range(self.stopPointDuration):
                    trajectory.append([x, 0.0, 0.0, 1])
            trajectory.append([x, 0.0, 0.0, 1])
        print(trajectory)
        """else:
            zPoints = 5
            xPoints = 6
            self.middleXZIndex = 9
            z = []
            x = []
            for i in range(zPoints):
                z.append(Robot.moveXMax / 2 - i * (Robot.moveXMax / (zPoints - 1)))
            for i in range(xPoints):
                x.append(Robot.moveXMax / 2 - i * (Robot.moveXMax / (xPoints - 1)))

            for i in z:
                trajectory.append([-Robot.moveXMax / 2, 0, i, 1])
            for i in x:
                trajectory.append([i, 0, Robot.moveZMax, 1])
            for i in reversed(z):
                trajectory.append([Robot.moveXMax / 2, 0, i, 1])
            for i in reversed(x):
                trajectory.append([i, 0, 0, 1])
            print(trajectory)"""

        return trajectory

    def iterate(self):
        while True:
            tStart = time.perf_counter()

            self.getNewCommands()  # Kommunikationsobjekt abfragen
            # wenn neue Kommandos dann ggf. (Richtungsänderung, Höhenverstellung, Geschwindigkeitsreduzierung/erhöhung)

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
                    # print("Height: " + str(self.currentZ))
                # Überprüfe, ob aktuelle Leg Position in der Mitte der Trajektorie liegt,um Trajektorie um Z zu rotieren
                if (self.cachedCommands[1] != self.degree) and (
                        (self.trajAIndex == (self.middleXZIndex - 1) or self.trajBIndex == (self.middleXZIndex - 1))):
                    self.degree = self.cachedCommands[1]
                    self.rotateTraj(self.degree)
                    """print(
                        "Aktuelle Trajektorie mit neuer Richtung bei Grad: " + str(self.degree) + str(self.currentTraj))"""
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

            # Überprüfe ob die berechnete Zeit für eine Bewegung abgelaufen ist
            if self.testMode or self.legs[0].getTimefinished() <= time.time(): #and
                                 #self.legs[1].getTimefinished() <= time.time() and
                                 #self.legs[2].getTimefinished() <= time.time() and
                                 #self.legs[3].getTimefinished() <= time.time() and
                                 #self.legs[4].getTimefinished() <= time.time() and
                                 #self.legs[5].getTimefinished() <= time.time()):
                legATraj = self.currentTraj[self.trajAIndex + 1]
                legBTraj = self.currentTraj[self.trajBIndex + 1]
                # print(legATraj)
                # print(legBTraj)

                # Punkte zur Ausführung an die
                # Beinobjekte übergeben
                points = []  # tmp Liste für Hexaplotter
                for i in range(len(self.legs)):
                    if (i % 2) != 0:
                        # Überprüft ob nächster Punkt = Haltepunkt, falls ja dann überspringe Punkt
                        if self.moveToPos(i, legATraj) != (self.moveToPos(0, self.currentTraj[self.trajAIndex])):
                            self.legs[i].setFootPosPoints(self.moveToPos(i, legATraj), self.velocity)
                            points.append(self.moveToPos(i, legATraj))
                    else:
                        if self.moveToPos(i, legBTraj) != (self.moveToPos(0, self.currentTraj[self.trajBIndex])):
                            self.legs[i].setFootPosPoints(self.moveToPos(i, legBTraj), self.velocity)
                            points.append(self.moveToPos(i, legBTraj))
                if self.testMode:
                    self.hs.send_points(points)
                # Stemmtrajektorienpunkt an die Orte
                # der drei stemmenden Beine verschieben
                # Schwingtrajektorienpunkt an die Orte
                # der drei schwingenden Beine verschieben
                self.trajAIndex += 1
                self.trajBIndex += 1

            tEnd = time.perf_counter()
            periodLength = tEnd - tStart
            # print("periodLength: " + str(periodLength))

            # Warte Taktzeit ab...
            time.sleep(self.cycleTime - periodLength)

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
        #print(commands)

    def rotateTraj(self, degree):  # erstellt rotierten Vektor um z Achse um Grad degree
        self.currentTraj = []  # Aktuelle Trajektorie leeren
        if not degree == 0:  # Umrechnung für Controller
            degree = (360 * math.pi / 180) - degree
        rotationMatrix = np.array([(math.cos(degree), -math.sin(degree), 0, 0),
                                   (math.sin(degree), math.cos(degree), 0, 0),
                                   (0, 0, 1, 0),
                                   (0, 0, 0, 1)])
        for i in range(len(self.traj)):
            self.currentTraj.append(list(rotationMatrix.dot(self.traj[i])))


if __name__ == "__main__":
    rb = Robot(False)
