import copy
import math
import time
import numpy as np

from mincom import MinCom
from HexaplotSender import HexaplotSender
from LegDummy import LegDummy
from COM.Robhost import Host


class Robot:
    def __init__(self, testMode):

        self.testMode = testMode  # Flag für Testmodus (Hexaplotter verwenden?)

        self.legs = ()

        # Kommunikationsobjekt erzeugen
        self.host = Host()

        if self.testMode:
            # hexaplotter
            #self.hs = HexaplotSender()
            # Testkommunikationsobjekt erzeugen
            # self.mc = MinCom()
            # sechs Beinobjekte mit entsprechenden Joint IDs erzeugen
            legs = (LegDummy(1, False, 1, 3, 5), LegDummy(2, False, 2, 4, 6),
                    LegDummy(3, False, 8, 10, 12), LegDummy(4, False, 14, 16, 18),
                    LegDummy(5, False, 13, 15, 17), LegDummy(6, False, 7, 9, 11))
            # leg(nummer int 1-6, bool True(real leg), int idAlpha, int idBeta, int idGamma)  -> siehe Klasse LegDummy
        else:
            ...
            # TODO echte legs zuweisen

        self.extremeZ = 0.03  # Extrempunkt maxZ
        self.moveDiameter = 0.25  # Durchmesser vom Arbeitsbereich nach X
        #  self.coordPoints = coordPoints  # wird durch realDynCoorNumber abgelöst
        #  self.coordPoints = 510
        self.cycleTime = 0.05  # Durchlaufzeit einer Iteration in Sekunden
        self.oneStepTime = 1.0  # Durchlaufzeit einer ganzen Bewegung durch die Trajektorienliste
        self.coordPoints = math.floor(self.oneStepTime/self.cycleTime)
        self.traj = self.createTraj()  # wird bei aktuell funktionierender Methode verwendet
        print(self.traj)

        self.trajAIndex = 0  # Schwingungsanfangsindex
        self.trajBIndex = math.floor(len(self.traj)/2)  # Stemmungsanfangsindex

        # Roboter Parameter
        self.velocity = 1.0  # Geschwindigkeit (0.0 0.5 1.0)
        self.degree = 0  # Grad der Bewegung/Trajektorie in Radiant (für Bewegungsänderung)

        self.cachedCommands = []  # Kommandos cachen zur späteren Überprüfung (degree [0], velocity [1])

        # sechs Startpunkte für Beine erzeugen
        self.legsStartPos = self.createLegStartPos()

        # Trajektorienliste mit Trajektorienpunkten erzeugen

        # self.traj = [(0.0, 0.0, 0.0, 1.0), (-0.5, 0.0, 0.0, 1.0), (-1.0, 0.0, 0.0, 1.0), (-0.5, 0.0, 0.5, 1.0),
        #             (0.0, 0.0, 1.0, 1.0),  (0.5, 0.0, 0.5, 1.0),  (1.0, 0.0, 0.0, 1.0), (0.5, 0.0, 0.0, 1.0)]
        # "1" hinzugefuegt und Startkoordinate geaendert für Trajekt.mitte
        # Startkoordinate (Index 0) muss Mitte sein -> 1. Tupel von createTraj
        # wird durch funktionierender Methode abgelöst

    def createTraj(self):
        if self.coordPoints >= 4:
            traj = []
            for i in range(math.ceil(self.coordPoints / 4)):
                x = (-i / (math.ceil(self.coordPoints / 4) - 1)) * (self.moveDiameter / 2)
                traj += [(x, 0.0, 0.0, 1.0), ]
            print("\nErste Koordinate: \t\t\t\t\t\t\t\t" + str(traj[0]) + " \t(aus Zeile 73)")
            print("Koordinate zwischen Stemm- und Schwingphase: \t" + str(
                traj[-1]) + " \t(aus Zeile 74)")  # dient zu Testzwecken -> zeigt Uebergang
            if ((self.coordPoints % 4) == 0) or ((self.coordPoints % 4) == 3):
                for i in range(1, math.ceil(self.coordPoints / 4) + 2):
                    x = -self.moveDiameter / 2 + (i / (math.ceil(self.coordPoints / 4) + 1)) * (self.moveDiameter / 2)
                    z = (-self.extremeZ / math.pow(self.moveDiameter / 2, 2)) * math.pow(x, 2) + self.extremeZ
                    traj += [(x, 0.0, z, 1.0), ]
            elif (self.coordPoints % 4) == 1:
                for i in range(1, math.ceil(self.coordPoints / 4)):
                    x = -self.moveDiameter / 2 + (i / (math.ceil(self.coordPoints / 4) - 1)) * (self.moveDiameter / 2)
                    z = (-self.extremeZ / math.pow(self.moveDiameter / 2, 2)) * math.pow(x, 2) + self.extremeZ
                    traj += [(x, 0.0, z, 1.0), ]
            elif (self.coordPoints % 4) == 2:
                for i in range(1, math.ceil(self.coordPoints / 4) + 1):
                    x = -self.moveDiameter / 2 + (i / math.ceil(self.coordPoints / 4)) * (self.moveDiameter / 2)
                    z = (-self.extremeZ / math.pow(self.moveDiameter / 2, 2)) * math.pow(x, 2) + self.extremeZ
                    traj += [(x, 0.0, z, 1.0), ]
            print("Koordinate am hoechsten Punkt: \t\t\t\t\t" + str(traj[-1]) + " \t(aus Zeile 90)")
            for i in range(1, math.ceil(self.coordPoints / 4) + 1):
                x = (i / math.ceil(self.coordPoints / 4)) * (self.moveDiameter / 2)
                z = (-self.extremeZ / math.pow(self.moveDiameter / 2, 2)) * math.pow(x, 2) + self.extremeZ
                traj += [(x, 0.0, z, 1.0), ]
            print("Koordinate zwischen Schwing- und Stemmphase: \t" + str(traj[-1]) + " \t(aus Zeile 95)")
            for i in range(1, math.floor(self.coordPoints / 4)):
                x = self.moveDiameter / 2 - (i / (math.floor(self.coordPoints / 4) - 1)) * (self.moveDiameter / 2)
                traj += [(x, 0.0, 0.0, 1.0), ]
            del traj[-1]
            print("Letzte Koordinate: \t\t\t\t\t\t\t\t" + str(traj[-1]) + " (aus Zeile 100)\n")
            print("Laenge von traj: \t\t\t\t" + str(
                len(traj)) + " (aus Zeile 101)\nGeforderte Koordinatenanzahl: \t" + str(
                self.coordPoints) + " (aus Zeile 101)\n")  # dient zu Testzwecken
            return traj
        else:
            print("Fehler: Anzahl der Koordinaten liegt unter 4")
            return

    def createLegStartPos(self):  # evt. Liste direkt erstellen mit gemessenen Werten
        # Position in Metern!
        xB = 0.000  # TODO Offset vom Hauptkörper des Roboters in x Richtung
        yB = 0.000  # TODO Offset vom Hauptkörper des Roboters in y Richtung
        startZ = 0.100
        allLegPos = ((1.000,  -1.000, -1.000),
                     (1.000,   1.000, -1.000),
                     (0.000,   1.000, -1.000),
                     (-1.000,  1.000, -1.000),
                     (-1.000, -1.000, -1.000),
                     (0.000,  -1.000, -1.000))
        for (x, y, z) in allLegPos:
            x *= xB
            y *= yB
            z += startZ
        return allLegPos

    def iterate(self):
        while 1:
            tStart = time.perf_counter()

            self.getNewCommands()  # Kommunikationsobjekt abfragen
            # wenn neue Kommandos dann ggf. (Richtungsänderung, Höhenverstellung, Geschwindigkeitsreduzierung/erhöhung)
            # -> Hoehenverstellung ueber self.moveRadius bzw. self.moveRadiusDenominator
            # Trajektorie aendern wenn ein Bein in der Startposition

            if self.cachedCommands:
                if self.velocity != self.cachedCommands[0]:
                    self.velocity = self.cachedCommands[0]
                    print("Velocity: " + str(self.velocity))
                    if self.velocity == 0.0:  # Breche Iterationsdurchlauf ab, wenn keine Geschwindigkeit
                        print("Roboter steht!")
                        return
                """if self.extremeZ != self.cachedCommands[2]:
                    self.extremeZ *= self.cachedCommands[2]"""
                # Überprüfe, ob aktuelle Leg Position in der Mitte der Trajektorie liegt,um Trajektorie um Z zu rotieren
                if self.cachedCommands[1] != self.degree and (self.trajAIndex == 0 or self.trajBIndex == 0):
                    self.degree = self.cachedCommands[1]
                    print("Rot. Degree: " + str(self.degree))
                    tmpTraj = list(copy.deepcopy(self.traj))
                    for i in range(len(self.traj)):
                        # "1" ist schon im Vektor: tmpTraj[i] += (1,)
                        # print("RotMatrix: " + str(self.rotMatrixZ()))
                        tmpTraj[i] = self.createRotatedVector(tmpTraj[i], self.degree)
                        # np.round(np.array,digits) falls gerundet werden soll, sonst raw
                        self.traj[i] = tuple(copy.deepcopy(tmpTraj[i]))  # "1" bleibt im Vektor
                        #  print("Trajektorie: " + str(self.traj[i][:-1]))  # zeige Traj. ohne "1"

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
            for i, val in enumerate(self.legs):  # 6 neue Koordinaten in Liste speichern
                if (i % 2) == 0:
                    aPosition = tuple(np.add(val.getFootPosition(), legATraj))
                    allCurrentPositions.append(aPosition)
                else:
                    bPosition = tuple(np.add(val.getFootPosition(), legBTraj))
                    allCurrentPositions.append(bPosition)

            # Punkte zur Ausführung an die
            # Beinobjekte übergeben
            # print(allCurrentPositions)
            if self.testMode:
                ...
                #self.hs.send_points(allCurrentPositions)  # sende an plotter
            elif self.legs[0][1] and self.legs[1][1] and self.legs[2][1] and self.legs[3][1] and self.legs[4][1] and self.legs[5][1]:
                # while not posReached:
                # self.legs[0].setFootPosPoints(allCurrentPositions[0])  # real bei True
                # self.legs[1].setFootPosPoints(allCurrentPositions[1])
                # self.legs[2].setFootPosPoints(allCurrentPositions[2])  # Leg Gruppe hat Methode setFoot..
                # self.legs[3].setFootPosPoints(allCurrentPositions[3])
                # self.legs[4].setFootPosPoints(allCurrentPositions[4])
                # self.legs[5].setFootPosPoints(allCurrentPositions[5])
                # if allLegs posReached: posReached = True
                pass
            else:
                print("FEHLER: Beine sind in unterschiedlichen Zustaenden!!! -> return")
                return

            self.trajAIndex += 1
            self.trajBIndex += 1

            tEnd = time.perf_counter()
            periodLength = tEnd - tStart
            print("periodLength: " + str(periodLength) + " (aus Zeile 198)")  # dient zu Testzwecken
            time.sleep(self.cycleTime - periodLength)  #TODO velocity zwischenpunkte

    def getNewCommands(self):  # erhalte neue Kommandos (mincom)
        """        commands = self.mc.getData()
        # Überprüfe, ob neue Kommandos vorhanden
        if commands != 0:
            commands = list(map(float, self.mc.getData()))  # konvertiere zu int Objekten
        elif self.cachedCommands == commands or commands == 0:  # keine neuen Kommandos
            return
        print(commands)
        # Übernehme neue Kommandos in Robot Klasse Parameter
        #self.degree = commands[0]
        #self.velocity = commands[1]
        self.cachedCommands = commands"""
        commands = self.host.lastPressed  # list[velocity(0.0 bis 1.0)],[degree(rad)]
        if self.cachedCommands == commands or commands == 0 or not type(float) == commands:  # keine neuen Kommandos oder ungültig
            return
        #  print(commands)
        self.cachedCommands = commands

    def createRotatedVector(self, vector, degree):  # erstellt rotierten Vektor um z Achse um Grad degree
        rotationMatrix = np.array([(math.cos(degree), -math.sin(degree), 0, 0),
                                  (math.sin(degree), math.cos(degree), 0, 0),
                                  (0, 0, 1, 0),
                                  (0, 0, 0, 1)])
        rotatedVector = rotationMatrix.dot(vector)
        return rotatedVector


if __name__ == "__main__":
    rb = Robot(True)
    rb.iterate()

