import numpy
import math
import time
cimport numpy

from libc.math cimport sqrt, exp

DTYPE = numpy.double
ctypedef numpy.double_t DTYPE_t


cdef inline double d_min(double a, double b): return a if a <= b else b


cdef class Pricer2:
    cdef object hjmModel
    cdef int noOfIntervals
    cdef double principal, maturity
    cdef object random_state
    cdef numpy.ndarray grid, initialCurve, delta, drift, sigmaHat

    def __init__(self, hjmModel, principal, maturity):
        self.hjmModel = hjmModel
        self.principal = principal
        self.maturity = maturity
        self.random_state = numpy.random.RandomState()
        self.noOfIntervals = 0

    cdef configure(self):
        self.buildGrid()
        self.initialCurve = self.hjmModel.computeInitialCurve(self.grid)
        self.sigmaHat = self.hjmModel.computeSigmaHat(self.grid)
        self.noOfIntervals = self.grid.size
        self.delta = numpy.zeros(self.noOfIntervals, dtype=DTYPE)
        cdef DTYPE_t t = 0.0
        cdef long i
        for i in range(self.noOfIntervals):
            self.delta[i] = (self.grid[i] - t)
            t = self.grid[i]
        self.drift = numpy.zeros(self.noOfIntervals, dtype=DTYPE)


    cdef buildGrid(self):
        cdef double d = self.getDelta()
        cdef int gridSize = int(math.ceil(self.maturity / d))
        cdef numpy.ndarray[DTYPE_t] g = numpy.array([(i + 1) * d for i in range(gridSize)], dtype=DTYPE)
        self.grid = g


    cdef double getDelta(self):
        return 0.083333

    def price(self, long noOfSimulations):
        self.configure()
        cdef double tot, value
        cdef list simulations = []
        cdef long i
        tot = 0.0
        #print "config done"
        #start_time = time.time()
        for i in range(noOfSimulations):
            #if i % 100 == 0:
            #    print i, time.time() - start_time
            value = self.presentValue()
            tot += value
            simulations.append((i, tot / (i + 1)))
        return (tot / noOfSimulations, simulations)

    cdef double presentValue(self):
        raise NotImplementedError

    cdef int updateDrift(self, long i, numpy.ndarray[DTYPE_t] forwardCurve):
        cdef numpy.ndarray[DTYPE_t, ndim=3] sigmaHat = self.sigmaHat
        cdef long numberOfFactors = self.hjmModel.numberOfFactors
        cdef numpy.ndarray[DTYPE_t] delta = self.delta
        cdef numpy.ndarray[DTYPE_t] drift = self.drift

        cdef numpy.ndarray[DTYPE_t] a = numpy.zeros(numberOfFactors, dtype=DTYPE)
        cdef double bPrevious, bNext
        cdef long j, k, z
        bPrevious = 0.0
        cdef DTYPE_t value
        z = self.noOfIntervals - i - 1
        for j in range(z):
            bNext = 0.0
            for k in range(numberOfFactors):
                value = sigmaHat[k, i, j] * d_min(1.0, forwardCurve[j]) * delta[(i + j)]
                a[k] = a[k] + value
                bNext = bNext + (a[k] * a[k])
            drift[j] = ((bNext - bPrevious) / (2.0 * delta[i + j]))
            bPrevious = bNext
        return 0


cdef class ZCBPricer(Pricer2):
    def __init__(self, hjmModel, principal, maturity):
        super(ZCBPricer, self).__init__(hjmModel, principal, maturity)


    cdef double presentValue(self):
        cdef double discount = 1.0
        cdef double discountedPayoff = 0.0

        cdef long x 
        #cdef numpy.ndarray[DTYPE_t] forwardCurve = numpy.array([self.initialCurve[x] for x in range(self.noOfIntervals)],
        #                                                        dtype=DTYPE)
        cdef numpy.ndarray[DTYPE_t] forwardCurve = numpy.copy(self.initialCurve)
        cdef double lowerlimit = 0.0
        cdef numpy.ndarray[DTYPE_t] delta = self.delta
        cdef long numberOfFactors = self.hjmModel.numberOfFactors
        cdef numpy.ndarray[DTYPE_t, ndim=3] sigmaHat = self.sigmaHat
        normal = self.random_state.normal
        cdef numpy.ndarray[DTYPE_t] drift = self.drift
        cdef numpy.ndarray[DTYPE_t] grid = self.grid
        cdef long i, j, k, z
        cdef double tot, shortRate, norm
        cdef DTYPE_t value
        for i in range(self.noOfIntervals):
            shortRate = forwardCurve[0]
            discount = discount*(exp(-1.0 * shortRate * delta[i]))
            self.updateDrift(i, forwardCurve)
            z = self.noOfIntervals - i - 1
            for j in range(z):
                tot = 0.0
                for k in range(numberOfFactors):
                    norm = normal()
                    tot = tot + (sigmaHat[k, i, j] * d_min(1.0, forwardCurve[j]) * norm)
                value = (forwardCurve[(j + 1)] + drift[j] * delta[i] + tot * sqrt(delta[i]))
                forwardCurve[j] = value
            discountedPayoff = discountedPayoff + (discount * self.cashflow(shortRate, lowerlimit, grid[i]))
            lowerlimit = grid[i]
        return discountedPayoff


    cdef double cashflow(self, double shortRate, double lowerLimit, double upperLimit):
        if lowerLimit < self.maturity and self.maturity <= upperLimit:
            return self.principal
        return 0.0

cdef class CapPricer(Pricer2):
    cdef double fixedRate, tenor

    def __init__(self, hjmModel, principal, maturity, fixedRate, tenor):
        super(CapPricer, self).__init__(hjmModel, principal, maturity)
        self.fixedRate = fixedRate
        self.tenor = tenor


    cdef double presentValue(self):
        cdef double discount = 1.0
        cdef double discountedPayoff = 0.0
        cdef numpy.ndarray[DTYPE_t] forwardCurve = numpy.copy(self.initialCurve)
        cdef long i, j, k
        cdef double shortRate, payoff, fhat, sum

        for i in xrange(self.noOfIntervals):
            shortRate = forwardCurve[0]
            self.updateDrift(i, forwardCurve)
            for j in xrange(self.noOfIntervals - i - 1):
                sum = 0.0
                for k in xrange(self.hjmModel.numberOfFactors):
                    sum += self.sigmaHat[k,i,j] * min(1.0, forwardCurve[j]) * self.random_state.normal()
                forwardCurve[j] = (forwardCurve[(j + 1)] + self.drift[j] * self.delta[i] + sum * sqrt(self.delta[i]))
            fHat = (exp(shortRate * self.delta[i]) - 1.0) / self.delta[i]
            payoff = 0.0
            if fHat > self.fixedRate:
                payoff = (fHat - self.fixedRate) * exp(-shortRate * self.delta[i]) * self.principal
            discountedPayoff += discount * payoff
            discount *= exp(-shortRate * self.delta[i])
        return discountedPayoff

    cdef double getDelta(self):
        return self.tenor






