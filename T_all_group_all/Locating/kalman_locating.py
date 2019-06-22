import numpy as np
import matplotlib.pyplot as plt
from sympy import *
import csv
import frssi
import random



class KalmanFilter(object):

    def __init__(self, F=None, B=None, H=None, Q=None, R=None, P=None, x0=None):

        if(F is None or H is None):
            raise ValueError("Set proper system dynamics.")

        self.n = F.shape[1]
        self.m = H.shape[1]

        self.F = F
        self.H = H
        self.B = 0 if B is None else B
        self.Q = np.eye(self.n) if Q is None else Q
        self.R = np.eye(self.n) if R is None else R
        self.P = np.eye(self.n) if P is None else P
        self.x = np.zeros((self.n, 1)) if x0 is None else x0

    def predict(self, u=0):
        self.x = np.dot(self.F, self.x) + np.dot(self.B, u)
        self.P = np.dot(np.dot(self.F, self.P), self.F.T) + self.Q
        return self.x

    def update(self, z):
        y = z - np.dot(self.H, self.x)
        S = self.R + np.dot(self.H, np.dot(self.P, self.H.T))
        K = np.dot(np.dot(self.P, self.H.T), np.linalg.inv(S))
        self.x = self.x + np.dot(K, y)
        I = np.eye(self.n)
        self.P = np.dot(np.dot(I - np.dot(K, self.H), self.P),
            (I - np.dot(K, self.H)).T) + np.dot(np.dot(K, self.R), K.T)




class Locating():
    
    def __init__(self,data1,data2,data3,data4):

        self.x1 = 0.82
        self.x2 = 13.29
        self.x3 = 14.24
        self.x4 = 0.61

        self.y1 = -0.15
        self.y2 = 1.05
        self.y3 = 7.78
        self.y4 = 7.04

        self.z1 = 0
        self.z2 = 2.9
        self.z3 = 0
        self.z4 = 2.9

        # self.distance_one = 2.9
        # self.distance_two = 12.7366
        # self.distance_three = 16.0334
        # self.distance_four = 7.1925

        # distance_one = 0
        # distance_two = 0
        # distance_three = 0
        # distance_four = 0

        self.distance_one = data1
        self.distance_two = data2
        self.distance_three = data3
        self.distance_four = data4

        self.table = []
        self.strength = []
        

    def matrix_A(self):

        self.A = np.array([
        [2*(self.x1-self.x2), 2*(self.y1-self.y2), 2*(self.z1-self.z2)],
        [2*(self.x1-self.x3), 2*(self.y1-self.y3), 2*(self.z1-self.z3)],
        [2*(self.x1-self.x4), 2*(self.y1-self.y4), 2*(self.z1-self.z4)]
        ]
        )

        return self.A


    def matrix_C(self):

        self.lambda1 = (np.square(self.distance_two) - np.square(self.distance_one) - np.square(self.x2) +
                np.square(self.x1) - np.square(self.y2) + np.square(self.y1) - np.square(self.z2) + np.square(self.z1))
        self.lambda2 = (np.square(self.distance_three) - np.square(self.distance_one) - np.square(self.x3) +
                np.square(self.x1) - np.square(self.y3) + np.square(self.y1) - np.square(self.z3) + np.square(self.z1))
        self.lambda3 = (np.square(self.distance_four) - np.square(self.distance_one) - np.square(self.x4) +
                np.square(self.x1) - np.square(self.y4) + np.square(self.y1) - np.square(self.z4) + np.square(self.z1))
        self.C = np.array([self.lambda1, self.lambda2, self.lambda3])

        return self.C


    # def store(self,data1):

    #     with open('output.csv', 'w') as csvfile:
    #         writer = csv.writer(csvfile)
    #         writer.writerows(self.data1)
    

    def lets_get_data(self):

        self.matrixA = self.matrix_A()
        self.matrixC = self.matrix_C()
        # print("matrix A is : ", "\n",matrixA)
        # print("matrix C is : ", "\n",matrixC, "\n")
        self.A_inv = np.linalg.inv(self.matrixA)
        # print("invser matrix for matrix A is :","\n",A_inv)
        self.ans = self.A_inv.dot(self.matrixC)
        # print("\n","the anwser is :")
        
        self.ans = self.ans.tolist()
        if self.ans[2]>3 or self.ans[2]<0:
            self.ans[2] = random.uniform(0,2)

        print(self.ans)

        #if self.ans[0] > 0 and self.ans[0] < 17 and self.ans[1] > -0.2 and self.ans[1] < 8 and self.ans[2] > 0 and self.ans[2] < 3:
        #    self.table.append(self.ans)
			
        return self.ans

    

def go_filter(data):

    pp = data

    measurements = np.array(pp)

    dt = 1.0/60
    F = np.array([[1, dt, 0], [0, 1, dt], [0, 0, 1]])
    H = np.array([1, 0, 0]).reshape(1, 3)
    Q = np.array([[0.05, 0.05, 0.0], [0.05, 0.05, 0.0], [0.0, 0.0, 0.0]])
    R = np.array([0.5]).reshape(1, 1)

    x = np.linspace(-10, 10, 100)
    # measurements = - (x**2 + 2*x - 2) + np.random.normal(0, 2, 100)
    
    kf = KalmanFilter(F = F, H = H, Q = Q, R = R)
    predictions = []

    for z in measurements:
        predictions.append(np.dot(H,  kf.predict())[0])
        kf.update(z)

    # plt.plot(range(len(measurements)), measurements, label = 'Measurements')
    # plt.plot(range(len(predictions)), np.array(predictions), label = 'Kalman Filter Prediction')
    # plt.legend()
    # plt.show()

    use = predictions[len(predictions)-1].tolist()
    # print(use)

    return use[0]


if __name__ == '__main__':

    stations = {
        '8C:3B:AD:22:02:66': {
            'x':    13.29,
            'y':    1.05,
            'z':    2.9,
            'signalAttenuation': 3,
            'reference': {
                'distance': 5,
                'signal': -30
            }
        },
        '00:11:32:9D:2B:30': {
            'x':    0.61,
            'y':    7.04,
            'z':    2.9,
            'signalAttenuation': 3,
            'reference': {
                'distance': 5,
                'signal': -30
            }
        },
        '00:11:32:9D:30:3A': {
            'x':    0.82,
            'y':    -0.15,
            'z':    0,
            'signalAttenuation': 5,
            'reference': {
                'distance': 5,
                'signal': -30
            }
        },
        '8C:3B:AD:21:FF:66': {
            'x':    14.24,
            'y':    7.78,
            'z':    0,
            'signalAttenuation': 5,
            'reference': {
                'distance': 5,
                'signal': -30
            }
        },
    }

    rssi_localizer = frssi.RSSILocalizer(stations)

    AP1 = []
    AP2 = []
    AP3 = []
    AP4 = []

    rssi_ap1 = 0
    rssi_ap2 = 0
    rssi_ap3 = 0
    rssi_ap4 = 0

    while True:

        # Receive Data 
        AP1 = [34.0, 35.0, 35.0, 36.0, 34.0]
        AP2 = [35.0, 33.0, 37.0, 35.0, 36.0]
        AP3 = [34.0, 35.0, 34.0, 35.0, 34.0]
        AP4 = [34.0, 35.0, 36.0, 34.0, 34.0]
        # Receive Data 

        if len(AP1) >=5:
            rssi_ap1 = go_filter(AP1)

        if len(AP2) >=5:
            rssi_ap2 = go_filter(AP2)

        if len(AP3) >=5:
            rssi_ap3 = go_filter(AP3)

        if len(AP4) >=5:
            rssi_ap4 = go_filter(AP4)

        if rssi_ap1 != 0 and rssi_ap2 !=0 and rssi_ap3 != 0 and rssi_ap4 !=0:
  
            # Transfer into distance
            # loc = Locating(distance1,ditance2,distrance3,distance4)
            # Transfer into distance
            
            f_signal_dict = {
                '8C:3B:AD:22:02:66': rssi_ap1,
                '00:11:32:9D:2B:30': rssi_ap2,
                '00:11:32:9D:30:3A': rssi_ap3,
                '8C:3B:AD:21:FF:66': rssi_ap4,
            }
            
            dist_dict = rssi_localizer.getDistanceFromAllAP(f_signal_dict)
            
            dist_ap1 = dist_dict.get('8C:3B:AD:22:02:66')
            dist_ap2 = dist_dict.get('00:11:32:9D:2B:30')
            dist_ap3 = dist_dict.get('00:11:32:9D:30:3A')
            dist_ap4 = dist_dict.get('8C:3B:AD:21:FF:66')

            loc = Locating(dist_ap1,dist_ap2,dist_ap3,dist_ap4)
            loc.lets_get_data()
            
            
            rssi_ap1 = 0
            rssi_ap2 = 0
            rssi_ap3 = 0
            rssi_ap4 = 0
            del AP1[:] 
            del AP2[:] 
            del AP3[:] 
            del AP4[:]
            
            
            """
            must send 4 parameters to lets_get_data()

            loc = Locating(rssi_ap1,rssi_ap2,rssi_ap3,rssi_ap4)

            """
    

    
