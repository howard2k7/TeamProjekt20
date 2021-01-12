import copy
import math
import time
import numpy as np

from mincom import MinCom
from HexaplotSender import HexaplotSender
from LegDummy import LegDummy


class Robot:
    def __init__(self, testMode):

        self.testMode = testMode  # Flag für Testmodus (Hexaplotter verwenden?)

        self.cycleTime = 1.5  # Durchlaufzeit in Sekunden
        self.trajAIndex = 0  # Schwingungsanfangsindex
        self.trajBIndex = math.floor(len(self.traj)/2)  # Stemmungsanfangsindex

        # Roboter Parameter
        self.velocity = 0.0  # Geschwindigkeit (0.0 0.5 1.0)
        self.degree = 0  # Grad der Bewegung/Trajektorie in Radiant (für Bewegungsänderung)
        self.height = 1  # TODO: Höhe (z Koordinate) der Beine Trajektorie <- davon abziehen (Lage/Ort der Beine)

        self.move_maxHeight = 0.00  # TODO Max Auslenkung Höhe messen in z
        self.move_maxLength = 0.00  # TODO Max Auslenkung Länge/Durchmesser in y Richtung

        self.cachedCommands = []  # Kommandos cachen zur späteren Überprüfung (degree [0], velocity [1])

        # sechs Startpunkte für Beine erzeugen
        self.legsStartPos = self.createLegStartPos()

        # sechs Beinobjekte mit entsprechenden Joint IDs erzeugen
        self.legs = (Leg(1, False, 1, 3, 5), Leg(2, False, 2, 4, 6),
                     Leg(3, False, 8, 10, 12), Leg(4, False, 14, 16, 18),
                     Leg(5, False, 13, 15, 17), Leg(6, False, 7, 9, 11))
                    # leg(nummer int 1-6, bool True(real leg), int idAlpha, int idBeta, int idGamma)  -> Klasse anpassen oder von Leg-Gruppe importieren

        self.traj = []

        if self.testMode or not (self.legs[0][1] and self.legs[1][1] and self.legs[2][1] and self.legs[3][1] and self.legs[4][1] and self.legs[5][1]):
            # Test Trajektorie erstellen
            self.traj = [(0.0, 0.0, 0.0, 1.0), (-0.5, 0.0, 0.0, 1.0), (-1.0, 0.0, 0.0, 1.0), (-0.5, 0.0, 0.5, 1.0),
                         (0.0, 0.0, 1.0, 1.0), (0.5, 0.0, 0.5, 1.0), (1.0, 0.0, 0.0, 1.0), (0.5, 0.0, 0.0, 1.0)]
            # hexaplotter
            self.hs = HexaplotSender()
            # Kommunikationsobjekt erzeugen
            self.mc = MinCom()

        # Trajektorienliste mit Trajektorienpunkten erzeugen

        self.traj = self.createTraj()
        # TODO Funktion zum ermitteln der (mit max/min Länge) Trajektorienpunkte des Roboters
        # TODO Arbeitsbereich Schrittweite Beine bekommen

        # "1" hinzugefuegt und Startkoordinate geaendert für Trajekt.mitte
        # Startkoordinate (Index 0) muss Mitte sein -> 1. Tupel von createTraj
        # wird durch funktionierender Methode abgelöst

        # self.traj = createTraj()  # wird bei funktionierender Methode verwendet
        self.tempStaticCoorNumber = 50  # wird durch realDynCoorNumber abgelöst
        # self.realDynCoorNumber = Todo NEW: dynamisch berechnen

        self.moveRadius = 0.05
        self.moveDiameter = 0.1

    def createTraj(self):
        traj = []  # Todo NEW: x und z noch nicht richtig
        for i in range(math.floor(self.tempStaticCoorNumber / 4)):  # floor = abrunden, ceil =aufrunden
            x = -i / self.moveRadius  # [0; -radius] x von 0 bis -radius zusammenbasteln
            traj += [(x, 0.0, 0.0, 1.0), ]
        for i in range(math.floor(self.tempStaticCoorNumber / 4)):
            x = i  # (-radius; 0] x von -radius bis 0 zusammenbasteln
            z = self.getZfromX(x)  # (0; +maxHeight] z von 0 bis +maxHeight zusammenbasteln
            traj += [(x, 0.0, z, 1.0), ]
        for i in range(math.floor(self.tempStaticCoorNumber / 4)):
            x = i  # (0; +radius] x von 0 bis +radius zusammenbasteln
            z = self.getZfromX(x)  # (maxHeight; 0] z von +maxHeight bis 0 zusammenbasteln
            traj += [(x, 0.0, z, 1.0), ]
        for i in range(math.floor(self.tempStaticCoorNumber / 4)):
            x = self.moveRadius - i / self.moveRadius  # (+radius; 0) x von +radius bis 0 zusammenbasteln
            traj += [(x, 0.0, 0.0, 1.0), ]
        return traj

    def getZfromX(self, x):
        z = 2 * math.pow(x, 2) + self.moveRadius
        return z  # Todo NEW: Koeffizient 2 sorgt nicht für Schnittpunkte (-self.moveRadius,0) und (self.moveRadius,0)

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
            # Trajektorie aendern wenn ein Bein in der Startposition

            if self.cachedCommands:  # Kommandos liegen vor
                if self.velocity != self.cachedCommands[1]:
                    self.velocity = self.cachedCommands[1]
                    print("Velocity: " + str(self.velocity))
                    if self.velocity == 0.0:  # Breche Iterationsdurchlauf ab, wenn keine Geschwindigkeit
                        print("Roboter steht!")
                        return
                # Überprüfe, ob aktuelle Leg Position in der Mitte der Trajektorie liegt,um Trajektorie um Z zu rotieren
                if self.cachedCommands[0] != self.degree and (self.trajAIndex == 0 or self.trajBIndex == 0):
                    self.degree = self.cachedCommands[0]
                    print("Rot. Degree: " + str(self.degree))
                    tmpTraj = list(copy.deepcopy(self.traj))
                    for i in range(len(self.traj)):
                        # "1" ist schon im Vektor: tmpTraj[i] += (1,)
                        # print("RotMatrix: " + str(self.rotMatrixZ()))
                        tmpTraj[i] = self.createRotatedVector(tmpTraj[i], self.degree)
                        # np.round(np.array,digits) falls gerundet werden soll, sonst raw
                        self.traj[i] = tuple(tmpTraj[i].copy())  # "1" bleibt im Vektor
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
                    # TODO move Leg to aPosition
                    aPosition = tuple(np.add(val.getFootPosition(), legATraj))
                    allCurrentPositions.append(aPosition)
                else:
                    # TODO move Leg to bPosition
                    bPosition = tuple(np.add(val.getFootPosition(), legBTraj))
                    allCurrentPositions.append(bPosition)

            # Punkte zur Ausführung an die
            # Beinobjekte übergeben
            # print(allCurrentPositions)
            if self.testMode:
                self.hs.send_points(allCurrentPositions)  # sende an plotter
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
            time.sleep(self.cycleTime - periodLength)  #TODO velocity zwischenpunkte

    def getNewCommands(self):  # erhalte neue Kommandos (mincom)
        commands = self.mc.getData()
        # Überprüfe, ob neue Kommandos vorhanden
        if commands != 0:
            commands = list(map(float, self.mc.getData()))  # konvertiere zu int Objekten
        elif self.cachedCommands == commands or commands == 0:  # keine neuen Kommandos
            return
        print(commands)
        # Übernehme neue Kommandos in Robot Klasse Parameter
        """self.degree = commands[0]
        self.velocity = commands[1]"""
        self.cachedCommands = commands

    def createRotatedVector(self, vector, degree):  # erstellt rotierten Vektor um z Achse um Grad degree
        rotationMatrix = np.array([(math.cos(degree), -math.sin(degree)), 0, 0,
                                  (math.sin(degree), math.cos(degree), 0, 0),
                                  (0, 0, 1, 0),
                                  (0, 0, 0, 1)])
        rotatedVector = rotationMatrix.dot(vector)
        return rotatedVector


if __name__ == "__main__":
    rb = Robot(True)
    rb.iterate()
