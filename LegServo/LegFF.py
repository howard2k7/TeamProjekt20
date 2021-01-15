import math
import time
import numpy as np
from LegServo.jointdrive import JointDrive



class Leg:
    def __init__(self, legNumber, alphaID, betaID, gammaID):  # Konstruktor

        # Member Variable erstellen
        self.servofinished = False
        self.legNumber = legNumber
        self.oldAngles = [0.0, 0.0, 0.0]  # Winkel zwischenspeichern (Geschwindigkeit der Servomotoren)



        # Abstände (Offsets) der Beinansatzpunkte s. Folien 2 und 4, werden übergeben
        self.xB = (0.033, 0.033, 0.000, -0.033, -0.033, 0.000)  # kurze Seite L1,L2,L4,L5
        self.yB = (-0.032, 0.032, 0.0445, 0.032, -0.032, 0.0445)  # lange Seite L3, L6

        # Abstände aN: a0 nur bei L3,6 und L1,2,4,5 gleich, s. Foliensatz L2
        if legNumber == 3 or legNumber == 6:

            self.legDistances = [0.032, 0.038, 0.049, 0.059, 0.021, 0.013, 0.092]

        else:

            self.legDistances = [0.042, 0.038, 0.049, 0.059, 0.021, 0.013, 0.092]

        # Berechnung Coxa, Femur, Tibia
        self.lc = self.legDistances[2]  # lc = a2
        self.lcSquare = math.pow(self.lc, 2)

        self.lf = math.sqrt(math.pow(self.legDistances[3], 2) + math.pow(self.legDistances[4], 2))
        self.lfSquare = math.pow(self.lf, 2)

        self.lt = math.sqrt(math.pow(self.legDistances[5], 2) + math.pow(self.legDistances[6], 2))
        self.ltSquare = math.pow(self.lt, 2)


        print("LC: ", self.lc, self.lcSquare)
        print("LF: ", self.lf, self.lfSquare)
        print("LT: ", self.lt, self.ltSquare)

        self.jointDriveBroadcast = JointDrive(id=254)
        self.jointDriveAlpha = JointDrive(id=alphaID, aOffset=0.523599, aMax=6, aMin=1)
        self.jointDriveBeta = JointDrive(id=betaID, aOffset=0.523599, aMax=6, aMin=1)
        self.jointDriveGamma = JointDrive(id=gammaID, aOffset=0.523599, ccw=True, aMax=6, aMin=1)
        self.oldAngles = [self.jointDriveAlpha.getCurrentJointAngle(), self.jointDriveBeta.getCurrentJointAngle(),
                          self.jointDriveGamma.getCurrentJointAngle()]

    def invKinAlphaJoint(self, pos=[0, 0, 0, 1]):  # Bestimmung der Gelenkwinkel basierend auf der Position des Fußpunktes im Alphakoordinatensystem

        try:
            alpha = math.atan2(pos[1], pos[0])

            footPos = np.array(pos)
            A1 = np.array([
                [math.cos(alpha), 0, math.sin(alpha), self.lc * math.cos(alpha)],
                [math.sin(alpha), 0, -math.cos(alpha), self.lc * math.sin(alpha)],
                [0, 1, 0, 0],
                [0, 0, 0, 1]])

            betaPos = np.dot(A1, np.transpose([0, 0, 0, 1]))
            lct = np.linalg.norm(footPos[0:3] - betaPos[0:3])
            lctSquare = math.pow(lct, 2)
            gamma = math.acos((self.ltSquare + self.lfSquare - lctSquare) / (2 * self.lt * self.lf)) - math.pi

            h1 = math.acos((self.lfSquare + lctSquare - self.ltSquare) / (2 * self.lf * lct))
            h2 = math.acos(
                (lctSquare + self.lcSquare - math.pow(np.linalg.norm(footPos[0:3]), 2)) / (2 * self.lc * lct))

            # Falls Z Koordinate negativ
            if footPos[2] < 0:

                beta = (h1 + h2) - math.pi

            else:

                beta = (math.pi - h2) + h1

            return [alpha, beta, gamma]

        except Exception as e:

            print("Fehler in der Rueckwaertskinematik! Der Punkt liegt ausserhalb des Arbeitsbereiches! " + str(e))

            return self.oldAngles



    def forKinAlphaJoint(self, alpha, beta, gamma):  # Position des FUSSPUNKTS Alphakoordinatensystem

        try:

            T03LastColumn = np.array([
             [math.cos(alpha) * (self.lt * math.cos(beta + gamma) + self.lf * math.cos(beta) + self.lc)],
             [math.sin(alpha) * (self.lt * math.cos(beta + gamma) + self.lf * math.cos(beta) + self.lc)],
             [self.lt * math.sin(beta + gamma) + self.lf * math.sin(beta)],
             [1]])

            return T03LastColumn

        except Exception as e:

            print("Fehler in der Vorwaertskinematik! " + str(e))



    def forCalcBetaJoint(self, alpha):  # Berechnet die Position des Betagelenks im Alphakoordinatensystem

        A1 = np.array([
            [self.lc * math.cos(alpha)],
            [self.lc * math.sin(alpha)],
            [0],
            [1]])  # x,y,z aus Vektor extrahieren

        return [A1[0, 0], A1[1, 0], A1[2, 0], 1]



    def forCalcGammaJoint(self, alpha, beta):  # die Position des Knies ausgehend vom Alphakoordinatensystem

        A1 = np.array([
            [math.cos(alpha), 0, math.sin(alpha), self.lc * math.cos(alpha)],
            [math.sin(alpha), 0, -math.cos(alpha), self.lc * math.sin(alpha)],
            [0, 1, 0, 0],
            [0, 0, 0, 1]])

        A2 = np.array([
            [math.cos(beta), -math.sin(beta), 0, self.lf * math.cos(beta)],
            [math.sin(beta), math.cos(beta), 0, self.lf * math.sin(beta)],
            [0, 0, 1, 0],
            [0, 0, 0, 1]])

        ResultA1TimesA2 = np.dot(A1, A2)

        return [ResultA1TimesA2[0, 3], ResultA1TimesA2[1, 3], ResultA1TimesA2[2, 3], 1]



    def forCalcFootPoint(self, alpha, beta, gamma):  # die Position des Fußes ausgehend vom Alphakoordinatensystem

        T03 = self.forKinAlphaJoint(alpha, beta, gamma)

        return [T03[0, 0], T03[1, 0], T03[2, 0], 1]



    def setJointAngles(self, alpha, beta, gamma):

        footPositionAlpha = self.forCalcFootPoint(alpha, beta, gamma)  # Alphakoordinatensystem
        fPa = footPositionAlpha.copy()
        footPositionBasis = self.calcRotation_Z_Axis_OffsetBasisKoord(fPa)  # Berechnung der Fußposition in das Basiskoordinatensystem

        self.setFootPosAngle(footPositionAlpha, footPositionBasis)  # Roboterbasiskoordinatensystem



    def calcRotation_Z_Axis_OffsetAlphaKoord(self, pos=[0.0,0.0,0.0,1]):  # Offsets berechnen, um Punkte im Alphakoordinatensystem darzustellen

        if self.legNumber == 3:  # Rotation um 90 Grad

            minusSinusTheta = 1
            sinTheta = -1
            x = minusSinusTheta * pos[1]
            y = sinTheta * pos[0]
            pos[0] = x
            pos[1] = y

        elif self.legNumber == 6:  # Rotation um -90 Grad

            minusSinusTheta = -1
            sinTheta = 1
            x = minusSinusTheta * pos[1]
            y = sinTheta * pos[0]
            pos[0] = x
            pos[1] = y

        elif self.legNumber == 4 or self.legNumber == 5:  # Rotation um +- 180 Grad

            cosTheta = -1
            x = cosTheta * pos[0]
            y = cosTheta * pos[1]
            pos[0] = x
            pos[1] = y

        if self.legNumber == 1:

            pos[0] = pos[0] - self.xB[0] - self.legDistances[0]
            pos[1] -= self.yB[0]
            pos[2] += self.legDistances[1]
        elif self.legNumber == 2:

            pos[0] = pos[0] - self.xB[1] - self.legDistances[0]
            pos[1] -= self.yB[1]
            pos[2] += self.legDistances[1]

        elif self.legNumber == 3:

            pos[0] = pos[0] - self.yB[2] - self.legDistances[0]
            pos[1] += self.xB[2]
            pos[2] += self.legDistances[1]

        elif self.legNumber == 4:

            pos[0] = pos[0] + self.xB[3] - self.legDistances[0]
            pos[1] += self.yB[3]
            pos[2] += self.legDistances[1]

        elif self.legNumber == 5:

            pos[0] = pos[0] + self.xB[4] - self.legDistances[0]
            pos[1] += self.yB[4]
            pos[2] += self.legDistances[1]

        elif self.legNumber == 6:

            pos[0] = pos[0] - self.yB[5] - self.legDistances[0]
            pos[1] += self.xB[5]
            pos[2] += self.legDistances[1]
        return pos



    def calcRotation_Z_Axis_OffsetBasisKoord(self, pos=[0.0, 0.0, 0.0, 1]):  # Offsets berechnen, um Punkte im Basiskoordinatensystem darzustellen

        if self.legNumber == 6:  # Rotation um 90 Grad

            minusSinusTheta = 1
            sinTheta = -1
            x = minusSinusTheta * pos[1]
            y = sinTheta * pos[0]
            pos[0] = x
            pos[1] = y

        elif self.legNumber == 3:  # Rotation um -90 Grad

            minusSinusTheta = -1
            sinTheta = 1
            x = minusSinusTheta * pos[1]
            y = sinTheta * pos[0]
            pos[0] = x
            pos[1] = y

        elif self.legNumber == 4 or self.legNumber == 5:  # Rotation um +- 180 Grad

            cosTheta = -1
            x = cosTheta * pos[0]
            y = cosTheta * pos[1]
            pos[0] = x
            pos[1] = y

        if self.legNumber == 1:

            pos[0] = pos[0] + self.xB[0] + self.legDistances[0]
            pos[1] -= self.yB[0]
            pos[2] -= self.legDistances[1]

        elif self.legNumber == 2:

            pos[0] = pos[0] + self.xB[1] + self.legDistances[0]
            pos[1] += self.yB[1]
            pos[2] -= self.legDistances[1]

        elif self.legNumber == 3:

            pos[0] += self.xB[2]
            pos[1] = pos[1] + self.yB[2] + self.legDistances[0]
            pos[2] -= self.legDistances[1]

        elif self.legNumber == 4:

            pos[0] = pos[0] + self.xB[3] - self.legDistances[0]
            pos[1] += self.yB[3]
            pos[2] -= self.legDistances[1]

        elif self.legNumber == 5:

            pos[0] = pos[0] + self.xB[4] - self.legDistances[0]
            pos[1] += self.yB[4]
            pos[2] -= self.legDistances[1]

        elif self.legNumber == 6:

            pos[0] += self.xB[5]
            pos[1] = pos[1] - self.yB[5] - self.legDistances[0]
            pos[2] -= self.legDistances[1]
        return pos



    def setFootPosAngle(self, footPosAlpha=[0.0, 0.0, 0.0, 1], footPosBasis=[0.0, 0.0, 0.0, 1], speed=0):

        newAngles = self.invKinAlphaJoint(footPosAlpha)
        angleSpeed = self.calcServoSpeed(newAngles, self.oldAngles, 254)
        print(angleSpeed)
        print(newAngles)
        self.jointDriveAlpha.setDesiredAngleSpeed(newAngles[0], speed=angleSpeed[0], trigger=True)
        self.jointDriveBeta.setDesiredAngleSpeed(newAngles[1], speed=angleSpeed[1], trigger=True)
        self.jointDriveGamma.setDesiredAngleSpeed(newAngles[2], speed=angleSpeed[2], trigger=True)
        self.jointDriveBroadcast.action();

        self.oldAngles = newAngles.copy()

    def setFootPosPoints(self, footPos=[0.0, 0.0, 0.0, 1]):

        footPosBasis = footPos.copy()
        newAngles1 = self.invKinAlphaJoint(self.calcRotation_Z_Axis_OffsetAlphaKoord(footPosBasis))
        newAngles = [x + math.pi for x in newAngles1]

        angleSpeed = self.calcServoSpeed(newAngles, self.oldAngles, 254 )
        print(angleSpeed)
        print(angleSpeed)
        self.servofinished = False
        self.jointDriveAlpha.setDesiredAngleSpeed(newAngles[0], speed=angleSpeed[0], trigger=True)
        self.jointDriveBeta.setDesiredAngleSpeed(newAngles[1], speed=angleSpeed[1], trigger=True)
        self.jointDriveGamma.setDesiredAngleSpeed(newAngles[2], speed=angleSpeed[2], trigger=True)
        self.jointDriveBroadcast.action();
        while self.servofinished == False:
            self.servoready(newAngles)

        self.oldAngles = newAngles.copy()





    # Reihenfolge der Winkel beachten! Differenz von neuen und alten Winkeln übergeben
    def calcServoSpeed(self, angles=[0.0, 0.0, 0.0], lastAngles=[0.0, 0.0, 0.0], speed = 0):

        diffAngles = [abs(angles[0] - lastAngles[0]), abs(angles[1] - lastAngles[1]), abs(angles[2] - lastAngles[2])]
        largestAngle = max(diffAngles)

        alphaSpeed = (diffAngles[0] / largestAngle) * speed
        betaSpeed = (diffAngles[1] / largestAngle) * speed
        gammaSpeed = (diffAngles[2] / largestAngle) * speed

        return [alphaSpeed, betaSpeed, gammaSpeed]



    def servoready(self, servoAngle):
        if abs(self.jointDriveAlpha.getPresentPosition()-self.jointDriveAlpha.getGoalPosition()) <= 5and abs(self.jointDriveBeta.getPresentPosition()-self.jointDriveBeta.getGoalPosition()<=5) and abs(self.jointDriveGamma.getPresentPosition()-self.jointDriveGamma.getGoalPosition()<=5):
            self.servofinished = True





if __name__ == "__main__":

    leg = Leg(3, 3, 14, 15)
    leg1 = Leg(1, 1, 3, 5)
    leg2 = Leg(2, 2, 4, 6)
    leg3 = Leg(3, 8, 10, 12)
    leg4 = Leg(4, 14, 16, 18)
    leg5 = Leg(5, 13, 15, 17)
    leg6 = Leg(6, 7, 9, 11)

    while True:





        # Beinbewegung Bein 3
        print("Punkt 1")
        leg.setFootPosPoints([0.0, 0.2, 0.07, 1])
        #time.sleep(2)
        print("Punkt 2")
        leg.setFootPosPoints([-0.09, 0.15, -0.1, 1])
        #time.sleep(2)
        print("Punkt 3")
        leg.setFootPosPoints([0.0, 0.15, -0.1, 1])
        #time.sleep(2)
        print("Punkt 4")
        leg.setFootPosPoints([0.06, 0.15, -0.1, 1])
        #time.sleep(2)


