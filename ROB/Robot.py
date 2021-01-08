import math
import time
import numpy as np

from mincom import MinCom
from HexaplotSender import HexaplotSender
from LegDummy import LegDummy


class Robot:
    def __init__(self):

        self.cycleTime = 1.5  # Durchlaufzeit in Sekunden
        self.trajAIndex = 0  # Schwingungsanfangsindex #TODO funktion für veränderbare Trajektorienlönge länge abfragen
        self.trajBIndex = 4  # Stemmungsanfangsindex

        # Roboter Parameter
        self.velocity = 1.0  # Geschwindigkeit (0.0 0.5 1.0)
        self.degree = 0  # Grad der Bewegung/Trajektorie in Radiant (für Bewegungsänderung)

        self.height = 1  # TODO: Höhe (z Koordinate) der Beine Trajektorie <- davon abziehen (Lage/Ort der Beine)

        self.cachedCommands = []  # Kommandos cachen zur späteren Überprüfung

        # sechs Startpunkte für Beine erzeugen im Kreis ausdenken mit Radien 60 Grad + Offset x y + Offset z (Höhe)
        self.legsStartPos = [(1, 1, 1),
                             (0, 2, 1),
                             (-1, 1, 1),
                             (-1, -1, 1),
                             (0, -2, 1),
                             (1, -1, 1)]

        # sechs Beinobjekte erzeugen
        self.legs = (LegDummy(self.legsStartPos[0]), LegDummy(self.legsStartPos[1]), LegDummy(self.legsStartPos[2]),
                     LegDummy(self.legsStartPos[3]), LegDummy(self.legsStartPos[4]), LegDummy(self.legsStartPos[5]))

        # hexaplotter
        self.hs = HexaplotSender()

        # Kommunikationsobjekt erzeugen
        self.mc = MinCom()

        # Trajektorienliste mit Trajektorienpunkten erzeugen
        # TODO: Funktion zum ermitteln der (mit max/min Länge) Trajektorienpunkte des Roboters
        # TODO Arbeitsbereich Schrittweite Beine bekommen

        self.traj = [(-1.0, 0.0, 0.0), (-0.5, 0, 0.5), (0.0, 0.0, 1.0), (0.5, 0, 0.5),
                     (1.0, 0.0, 0.0), (0.5, 0.0, 0.0), (0.0, 0.0, 0.0), (-0.5, 0.0, 0.0)]

    def iterate(self):
        while 1:
            tStart = time.perf_counter()

            self.getNewCommands()  # Kommunikationsobjekt abfragen
            # wenn neue Kommandos dann ggf. (Richtungsänderung, Höhenverstellung, Geschwindigkeitsreduzierung/erhöhung)
            # Trajektorie aendern wenn ein Bein in der Startposition

            if self.cachedCommands:
                if self.velocity != self.cachedCommands[1]:
                    self.velocity = self.cachedCommands[1]
                    print("Velocity: " + str(self.velocity))
                    if self.velocity == 0.0:  # Breche Iterationsdurchlauf ab, wenn keine Geschwindigkeit
                        print("Roboter steht!")
                        return
                # Überprüfe, ob aktuelle Leg Position in der Mitte der Trajektorie liegt,um Trajektorie um Z zu rotieren
                if self.cachedCommands[0] != self.degree and (self.trajAIndex == 3 or self.trajAIndex == 7):  #TODO mitte bei veränderter trajektorie
                    self.degree = self.cachedCommands[0]
                    print("Rot. Degree: " + str(self.degree))
                    tmpTraj = list(self.traj.copy())   #TODO Liste testen (Kopie)
                    for i in range(len(self.traj)):
                        tmpTraj[i] += (1,)
                        #print("RotMatrix: " + str(self.rotMatrixZ()))
                        tmpTraj[i] = self.rotMatrixZ().dot(tmpTraj[i])  # np.round(np.array,digits)
                        self.traj[i] = tuple(tmpTraj[i][:-1].copy())  # entferne letzte hinzugefügte 1 vom Vektor
                        print("Trajektorie: " + str(self.traj[i]))

            # Überprüfe ob trajIndices außerhalb von TrajListe, sonst auf -1 setzen
            if self.trajAIndex + 1 > len(self.traj) - 1:
                self.trajAIndex = -1
            if self.trajBIndex + 1 > len(self.traj) - 1:
                self.trajBIndex = -1

            # einen Trajektorienpunkt für
            # schwingendes Bein und einen für
            # stemmendes Bein aus der einzigen
            # Punkteliste holen
            legATraj = self.traj[self.trajAIndex + 1]
            legBTraj = self.traj[self.trajBIndex + 1]

            # Stemmtrajektorienpunkt an die Orte
            # der drei stemmenden Beine verschieben
            # Schwingtrajektorienpunkt an die Orte
            # der drei schwingenden Beine verschieben
            allCurrentPositions = []
            for i, val in enumerate(self.legs):
                if (i % 2) == 0:
                    aPosition = tuple(np.add(val.getFootPosition(), legATraj))
                    allCurrentPositions.append(aPosition)
                else:
                    bPosition = tuple(np.add(val.getFootPosition(), legBTraj))
                    allCurrentPositions.append(bPosition)

            # Punkte zur Ausführung an die
            # Beinobjekte übergeben
            #print(allCurrentPositions)
            self.hs.send_points(allCurrentPositions)  # TODO Realer oder plotter Roboter unterscheidung

            self.trajAIndex += 1
            self.trajBIndex += 1

            tEnd = time.perf_counter()
            periodLength = tEnd - tStart
            time.sleep(self.cycleTime - periodLength)  #TODO velocity zwischenpunkte

    def getNewCommands(self):  # erhalte neue Kommandos (mincom)
        commands = self.mc.getData()
        # Überprüfe, ob neue Kommandos vorhanden
        if commands != 0:
            commands = list(map(float, self.mc.getData()))  # konvertiere zu int Objekten
        elif self.cachedCommands == commands or commands == 0:  # keine neuen Kommandos
            return
        print(commands)
        # Übernehme neue Kommandos in Robot class vars
        """self.degree = commands[0]
        self.velocity = commands[1]"""
        self.cachedCommands = commands

    def rotMatrixZ(self):  # Rotationsmatrix um z Achse
        rotationMatrix = np.array([(math.cos(self.degree), -math.sin(self.degree)), 0, 0,
                                  (math.sin(self.degree), math.cos(self.degree), 0, 0),
                                  (0, 0, 1, 0),
                                  (0, 0, 0, 1)])
        return rotationMatrix


if __name__ == "__main__":
    rb = Robot()
    rb.iterate()
