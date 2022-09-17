# ----------------------------------------------------------------------------
# Created By: GMLMOG016, FLDCLA001, YNGFYN001
# Created Date: 13/08/22
# ---------------------------------------------------------------------------
"""Represents the robot's 'brain' as an ANN"""

import numpy as np
import sympy as sym
import math
from scipy.special import expit
from robotComp import RobotComp


def sigmoid(x):
    # applying the sigmoid function
    return expit(x)


def sigmoid_derivative(x):
    # computing derivative to the Sigmoid function
    f = expit(x)
    return f * (1 - f)


def simple_derivative(x):
    # computing derivative to the linear function
    return sym.diff(x)


def oscil(x, phaseOffset, period):
    # applying the cos function
    for i in x:
        i = period*i - phaseOffset
        cos = math.cos(i)
        cos = cos*i
        if cos > 0:
            i = 1
        elif cos < 0:
            i = -1
        else:
            i = 0

    return x


def oscil_derivative(x):
    # computing derivative to the cos function
    return math.cos(x)-x*math.sin(x)


class Neuron:
    def __init__(self, id, layer, type, bodyPartid, ioId, gain, bias, period, phase):
        self.id = id
        self.layer = layer
        self.type = type
        self.srcComp = bodyPartid
        # the src component is set to the specific component in robot
        self.ioId = ioId
        # this may be the slot number
        self.gain = gain
        self.bias = bias
        self.period = period
        self.phase = phase
        self.weight = 0
        self.destComp = RobotComp(0, 0, 0, 0)

    def setWeight(self, w):
        self.weight = w

    def setDestComp(self, comp):
        self.component = comp


class Network:
    def InitializeWeight(self, inputArr, outputArr):
        weights = []
        for i in inputArr:
            weights.append(i.weight)
        for j in outputArr:
            weights.append(j.weight)
        return weights

    def ForwardPropagation(self, x, inputLayer, outputLayer):
        activations, layer_input = [x], x
        for j in inputLayer:
            if j.type == 'sigmoid':
                activation = sigmoid(np.dot(layer_input, j.weight))
            elif j.type == 'oscillator':
                activation = oscil(np.dot(layer_input, j.weight), j.phase, j.period)
            else:
                activation = np.dot(layer_input, j.weight)
            activations.append(activation)
            layer_input = np.append(1, activation)
        for j in outputLayer:
            if j.type == 'sigmoid':
                activation = sigmoid(np.dot(layer_input, j.weight))
            elif j.type == 'oscillator':
                activation = oscil(np.dot(layer_input, j.weight), j.phase, j.period)
            else:
                activation = np.dot(layer_input, j.weight)
            activations.append(activation)
            layer_input = np.append(1, activation)

        return activations

    def BackPropagation(self, y, activations, weights, inputLayer, outputLayer):
        outputFinal = activations[-1]

        # error = np.matrix(y - outputFinal)  # Error after 1 cycle
        count = 0
        for i in enumerate(inputLayer):
            currActivation = activations[-1][i]
            if (i > 1):
                # Append previous
                prevActivation = np.append(1, activations[i-1])
            else:
                # First hidden layer
                prevActivation = activations[0]

            if inputLayer[i].type == 'sigmoid':
                delta = np.multiply(error, sigmoid_derivative(currActivation))
            elif inputLayer[i].type == 'oscillator':
                delta = np.multiply(error, oscil_derivative(currActivation))
            else:
                delta = np.multiply(error, simple_derivative(currActivation))

            weights[i-1] += self.lr * np.multiply(delta.T, prevActivation)
            wc = np.delete(weights[i-1], [0], axis=1)
            error = np.dot(delta, wc)  # current layer error
            count+1
        for j in enumerate(outputLayer):
            currActivation = activations[j]
            if (j > 1):
                # Append previous
                prevActivation = np.append(1, activations[j - 1])
            else:
                # First hidden layer
                prevActivation = activations[0]

            if outputLayer[j].type == 'sigmoid':
                delta = np.multiply(self.lr, sigmoid_derivative(currActivation))
            elif inputLayer[j].type == 'oscillator':
                delta = np.multiply(self.lr, oscil_derivative(currActivation))
            else:
                delta = np.multiply(self.lr, simple_derivative(currActivation))

            weights[j - 1] += self.lr * np.multiply(delta.T, prevActivation)

            wc = np.delete(weights[j - 1], [0], axis=1)
            error = np.dot(delta, wc)  # current layer error
        return weights

    def Train(self, X, Y, weights, inputLayer, outputLayer):
        layers = len(weights)
        for i in range(len(X)):
            x = X[i]

            x = np.matrix(np.append(1, x))

            activations = self.ForwardPropagation(x, inputLayer, outputLayer)
            #weights = self.BackPropagation(Y, activations, weights, inputLayer, outputLayer)
            count = 0
            for i in inputLayer:
                i.weight = weights[count]
                count = count+1
            for j in outputLayer:
                j.weight = weights[count]
                count = count+1
        return weights

    def FindMaxActivation(self, output):
        m, index = output[0], 0
        for i in range(1, len(output)):
            if (output[i] > m):
                m, index = output[i], i

        return index

    def Predict(self, item, weights):
        layers = len(weights)
        item = np.append(1, item)

        # Forward prop.
        activations = self.ForwardPropagation(item, self.inputLayer, self.outputLayer)

        Foutput = activations[-1]
        index = self.FindMaxActivation(Foutput)

        y = [0 for j in range(len(Foutput))]
        y[index] = 1

        return y

    def Accuracy(self, X, Y, weights):
        correct = 0
        for i in range(len(X)):
            x, y = X[i], Y
            guess = self.Predict(x, weights)
            if (y == guess):
                # Right prediction
                correct += 1
        return correct / len(X)

    def __init__(self, inputLayer, outputLayer, X_train, Y_train, epochs=10, lr=0.15):
        self.inputLayer = inputLayer
        self.outputLayer = outputLayer
        weights = self.InitializeWeight(inputLayer, outputLayer)
        self.lr = lr

        for epoch in range(1, epochs+1):
            weights = self.Train(X_train, Y_train, weights, inputLayer, outputLayer)

            # if(epoch % 20 == 0):
            #print("Epoch {}".format(epoch))
            #print("Training Accuracy:{}".format(self.Accuracy(X_train, Y_train, weights)))
