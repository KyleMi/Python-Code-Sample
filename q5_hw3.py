import time
import numpy as np
import matplotlib.pyplot as plt

def readFile(filename):
    lines = []
    with open(filename, "r") as f:
        for line in f:
            lines.append(line)
    print(lines[0])
    return lines

def avgIntensity(lineArray):
    return np.average(lineArray)

def symmetry(lineArray):
    matrix = np.split(lineArray, 16)
    matrixUD = np.flipud(matrix)
    # return np.linalg.norm(matrix - matrixUD)/lineArray.size
    return np.linalg.norm(matrix - matrixUD)

def plot2D(lines):

    for line in lines:
        
        lineArray = np.array([float(element) for element in line.split()])

        if int(lineArray[0]) == 1:
            
            plt.plot(avgIntensity(lineArray[1:]), symmetry(lineArray[1:]), marker='o', color='b')
            
        if int(lineArray[0]) == 5:
            
            plt.plot(avgIntensity(lineArray[1:]), symmetry(lineArray[1:]), marker='x', color='r')
    plt.show()



def feature(lines):
    feature = []
    target = []
    for line in lines:
        lineArray = np.array([float(element) for element in line.split()])
        if int(lineArray[0]) == 1:
            feature.append(np.array([avgIntensity(lineArray[1:]), symmetry(lineArray[1:]), 1]))
            target.append(np.array([1]))

        if int(lineArray[0]) == 5:
            feature.append(np.array([avgIntensity(lineArray[1:]), symmetry(lineArray[1:]), 1]))
            target.append(np.array([-1]))
    return np.array(feature), np.array(target)

def least_squares_gradient_descent(x, y, max_iter=1000, step_size=0.00001, tol=1e-3):
    x_dim = x.shape[1]
    weight = np.zeros((x_dim, 1))
    obj_val = []
    N=len(x)

    for i in range(max_iter):
        sum = 0
        for idx in range(len(x)):
            x_n = x[idx]
            y_n = y[idx]
            exponent = y_n * np.dot(weight.T, x_n)
            denominator = 1 + np.exp(exponent)
            sum += x_n * y_n/denominator
        graduate = -sum / N
        # update weight and iterate step by step,move to v_t=-g_t direction
        weight -= step_size * graduate.reshape(x_dim, 1)
        obj_val.append(errorMeasure(x, y, weight))
    # return final weight
    return weight, obj_val

def errorMeasure(feature, target, weight):
    error = 0
    for idx in range(len(feature)):
        xn = feature[idx]
        yn = target[idx]
        error += np.log(1 + np.exp(-yn * np.dot(weight.T, xn)))
    return error / len(feature)

def thirdPolyFeatureConverter(lines):
    feature = []
    target = []
    for line in lines:
        lineArray = np.array([float(element) for element in line.split()])
        if int(lineArray[0]) == 1:
            f0, f1, f2 = 1, avgIntensity(lineArray[1:]), symmetry(lineArray[1:])
            feature.append(np.array([f0, f1, f2, f1**2, f1*f2, f2**2, f1**3, f1**2 * f2, f1 * f2**2, f2**3]))
            target.append(np.array([1]))

        if int(lineArray[0]) == 5:
            f0, f1, f2 = 1, avgIntensity(lineArray[1:]), symmetry(lineArray[1:])
            feature.append(np.array([f0, f1, f2, f1**2, f1*f2, f2**2, f1**3, f1**2 * f2, f1 * f2**2, f2**3]))
            target.append(np.array([-1]))
    return np.array(feature), np.array(target)

def p5b():
    Lines = readFile("ZipDigits.train")
    featureTrain, targetTrain = feature(Lines)

    weight, obj_val = least_squares_gd(featureTrain, targetTrain, 1000, 0.1)
    err = errorMeasure(featureTrain, targetTrain, weight)

    xs = np.linspace(-1, 1, 20, endpoint=True)
    ys = [-(weight[0]*x + weight[2])/weight[1] for x in xs]

    plt.figure()
    plot2D(trainLines)
    plt.plot(xs, ys)
    plt.xlabel("Average grayscale")
    plt.xlabel("Symmetry Difference")
    plt.title("Training Data -- Error: " + str(err) + "\nWeight vector" + str(weight.reshape(1,3)))
    # plt.suptitle("Weight vector" + str(weight))

    # plt.figure()
    # plt.plot(range(len(obj_val)), obj_val)

    testLines = readFile("ZipDigits.test")
    featureTest, targetTest = featureConverter(testLines)

    err = errorMeasure(featureTest, targetTest, weight)

    xs = np.linspace(-1, 1, 20, endpoint=True)
    ys = [-(weight[0]*x + weight[2])/weight[1] for x in xs]

    plt.figure()
    plot2D(testLines)
    plt.plot(xs, ys)
    plt.xlabel("Average grayscale")
    plt.ylabel("Symmetry Difference")
    plt.title("Test Data -- Error: " + str(err) + "\nWeight vector" + str(weight.reshape(1,3)))

    plt.show()

def q5c():
    trainLines = readFile("ZipDigits.train")
    featureTrain, targetTrain = thirdPolyFeatureConverter(trainLines)

    weight, obj_val = least_squares_gd(featureTrain, targetTrain, 1000, 1)
    print ("Weight vector: " + str(weight.reshape(1, 10)))
    err = errorMeasure(featureTrain, targetTrain, weight)
    print ("Train Error: " + str(err))

    testLines = readFile("ZipDigits.test")
    featureTest, targetTest = thirdPolyFeatureConverter(testLines)

    err = errorMeasure(featureTest, targetTest, weight)
    print ("Test Error: " + str(err))


if __name__ == '__main__':
    # rd=readFile("ZipDigits.test")
    # plot2D(rd)
    p5b()
    # q5c()
