import numpy as np
import matplotlib.pyplot as plt
from sympy import *
import csv


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

def example():

    pp = [34.0, 35.0, 35.0, 36.0, 34.0, 34.0, 35.0, 
    33.0, 37.0, 35.0, 36.0, 35.0, 34.0, 35.0, 36.0, 
    35.0, 34.0, 36.0, 34.0, 39.0, 34.0, 34.0, 35.0, 
    34.0, 35.0, 34.0, 35.0, 34.0, 34.0, 34.0, 34.0, 
    34.0, 35.0, 35.0, 34.0, 34.0, 34.0, 37.0, 36.0, 
    34.0, 35.0, 36.0, 34.0, 36.0, 34.0, 35.0, 36.0, 
    36.0, 35.0, 35.0]

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

    plt.plot(range(len(measurements)), measurements, label = 'Measurements')
    plt.plot(range(len(predictions)), np.array(predictions), label = 'Kalman Filter Prediction')
    plt.legend()
    plt.show()


    use = predictions[len(predictions)-1]
    print(use)

    return use


class Locating():
    
    def __init__(self):

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

        self.distance_one = 2.9
        self.distance_two = 12.7366
        self.distance_three = 16.0334
        self.distance_four = 7.1925

    
        # distance_one = 0
        # distance_two = 0
        # distance_three = 0
        # distance_four = 0
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
        

        print(self.ans)

        if self.ans[0] > 0 and self.ans[0] < 17 and self.ans[1] > -0.2 and self.ans[1] < 8 and self.ans[2] > 0 and self.ans[2] < 3:
            self.table.append(self.ans)

    
if __name__ == '__main__':

    example()
    loc = Locating()
    loc.lets_get_data()
    