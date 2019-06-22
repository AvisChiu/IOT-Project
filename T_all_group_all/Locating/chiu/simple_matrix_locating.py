import numpy as np
from sympy import *
import csv
# from sympy.abc import *

# 4 APs
# x1 = 0.82
# x2 = 13.29
# x3 = 14.24
# x4 = 0.61

# y1 = -0.15
# y2 = 1.05
# y3 = 7.78
# y4 = 7.04

# z1 = 0
# z2 = 2.9
# z3 = 0
# z4 = 2.9


# distance_one = 2.9
# distance_two = 12.7366
# distance_three = 16.0334
# distance_four = 7.1925


def matrix_A():

    A = np.array([
        [2*(x1-x2), 2*(y1-y2), 2*(z1-z2)],
        [2*(x1-x3), 2*(y1-y3), 2*(z1-z3)],
        [2*(x1-x4), 2*(y1-y4), 2*(z1-z4)]
    ]
    )

    return A


def matrix_C():

    lambda1 = (np.square(distance_two) - np.square(distance_one) - np.square(x2) +
               np.square(x1) - np.square(y2) + np.square(y1) - np.square(z2) + np.square(z1))
    lambda2 = (np.square(distance_three) - np.square(distance_one) - np.square(x3) +
               np.square(x1) - np.square(y3) + np.square(y1) - np.square(z3) + np.square(z1))
    lambda3 = (np.square(distance_four) - np.square(distance_one) - np.square(x4) +
               np.square(x1) - np.square(y4) + np.square(y1) - np.square(z4) + np.square(z1))
    C = np.array([lambda1, lambda2, lambda3])

    return C


def store(data1):

    with open('output.csv', 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(data1)
    

def lets_create_data(strength):

    matrixA = matrix_A()
    matrixC = matrix_C()
    # print("matrix A is : ", "\n",matrixA)
    # print("matrix C is : ", "\n",matrixC, "\n")
    A_inv = np.linalg.inv(matrixA)
    # print("invser matrix for matrix A is :","\n",A_inv)
    ans = A_inv.dot(matrixC)
    # print("\n","the anwser is :")
    
    ans = ans.tolist()
    ans.append(strength)

    print(ans)

    if ans[0] > 0 and ans[0] < 17 and ans[1] > -0.2 and ans[1] < 8 and ans[2] > 0 and ans[2] < 3:
        table.append(ans)
    

    # print(table)


    

if __name__ == "__main__":

    x1 = 0.82
    x2 = 13.29
    x3 = 14.24
    x4 = 0.61

    y1 = -0.15
    y2 = 1.05
    y3 = 7.78
    y4 = 7.04

    z1 = 0
    z2 = 2.9
    z3 = 0
    z4 = 2.9

    distance_one = 2.9
    distance_two = 12.7366
    distance_three = 16.0334
    distance_four = 7.1925

    
    # distance_one = 0
    # distance_two = 0
    # distance_three = 0
    # distance_four = 0

    table = []
    strength = []



    lets_create_data([0,0,0,0])

    # for i in range(0,90):
    #     ii = i/5
    #     distance_one = ii
    #     for j in range(0,90):
    #         jj = j/5
    #         distance_two = jj
    #         for m in range(0,90):
    #             mm = m/5
    #             distance_three = mm
    #             for n in range(0,90):
    #                 nn = n/5
    #                 distance_four = nn
    #                 lets_create_data([ii,jj,mm,nn])
                    
    # store(table)
