__author__ = 'vamshi'
import numpy
import math


M = 1.0

class HJMModel(object):

    def __init__(self, tau, initialRates, sigma):
        self.tau = tau
        self.initialRates = initialRates
        self.sigma = sigma
        self.numberOfFactors = sigma.shape[0]


    def zcbPrice(self, maturity):
        sum = 0.0
        t = 0.0
        for i in xrange(self.tau.size):
            if self.tau[i] <= maturity:
                sum += (self.tau[i] - t) * self.initialRates[i]
                t = self.tau[i]
        return math.exp(-sum)

    def getPCAData(self):
        data = []
        for k in xrange(self.numberOfFactors):
            li = [] 
            for j in xrange(self.initialRates.size):
                li.append((self.tau[j], self.sigma[k][j]))
            d = {
                    'label': 'PCA-%s' % k,
                    'data': li,
                }
            data.append(d)
        return data

    def computeInitialCurve(self, grid):
        return numpy.array([self.interpolateIntialRate(grid[i]) for i in xrange(grid.size)])


    def computeSigmaHat(self, grid):
        m = grid.size
        values = numpy.zeros([self.numberOfFactors, m, m])
        for k in xrange(self.numberOfFactors):
            t = 0.0
            for i in xrange(m):
                for j in xrange(m - i):
                    values[k][i][j] = self.interpolateSigma(k, grid[i + j] - t)
                t = grid[i]

        return values

    def interpolateIntialRate(self, t):
        return self.interpolate2(self.initialRates, t)

    def interpolateSigma(self, k, t):
        return self.interpolate2(self.sigma[k], t)


    def interpolate(self, values, t):
        lowerLimit = 0.0;
        for i in xrange(self.tau.size):
            if (lowerLimit <=t and t< self.tau[i]):
                return values[i]
        return values[self.tau.size-1]


    def interpolate2(self, values, t):
        if t <= self.tau[0]:
            return values[0]
        for i in xrange(1, self.tau.size):
            if t <= self.tau[i]:
                return values[i - 1] + (t - self.tau[i - 1]) * (values[i] - values[i - 1]) / (self.tau[i] - self.tau[i - 1])
        return values[(self.tau.size - 1)]



