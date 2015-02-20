__author__ = 'vamshi'
import numpy
cimport numpy
from libc.math cimport sqrt

DTYPE = numpy.double
ctypedef numpy.double_t DTYPE_t


NO_SIMULATIONS = 3000

cdef class BCDPricer:
    cdef int noofnames, k, m
    cdef double delta, recoveryrate
    cdef object discounter, marginals, copula
    cdef numpy.ndarray t

    def __init__(self, noofnames, k, delta, m, recoveryrate, discounter, copula, marginals):
        self.noofnames = noofnames
        self.k = k
        self.delta = delta
        self.m = m
        self.recoveryrate = recoveryrate
        self.discounter = discounter
        self.marginals = marginals
        self.t = numpy.array([delta * (i+1) for i in xrange(0, m)])
        self.copula = copula

    def price(self, int noSimulations, includeAccruedPremium):
        cdef double plSum = 0.0, dlSum = 0.0, apSum = 0.0, defaulTime = 0.0
        cdef numpy.ndarray uniformVariates
        cdef double dl,pl,ap,fairSpread
        simulations = []
        cdef int i
        for i in xrange(0, noSimulations):
            uniformVariates = self.copula.simulate()
            defaulTime = self.computeDefaulTime(uniformVariates)
            dl = self.defaultLegFactor(defaulTime)
            pl = self.premiumLegFactor(defaulTime)
            if includeAccruedPremium:
                ap = self.accruedPremiumFactor(defaulTime)
            else:
                if pl == 0.0:
                    ap = 0.5 * self.delta * self.discounter.discountFactor(self.t[0])
                else:
                    ap = 0.0
            plSum += pl
            dlSum += dl
            apSum += ap
            fairSpread = dl / (pl + ap)
            simulations.append((i, (dlSum / (plSum + apSum)) * 100.0 * 100.0))
        return (dlSum / (plSum + apSum), simulations)


    cdef double computeDefaulTime(self, numpy.ndarray variates):
        cdef numpy.ndarray defaulttimes = numpy.array([self.marginals[i].inverseCdf(variates[i]) for i in xrange(0, self.noofnames)])
        defaulttimes.sort()
        return defaulttimes[(self.k - 1)]

    cdef double premiumLegFactor(self,double defaulttime):
        cdef double value = 0.0, time = 0.0
        cdef int i
        for i in xrange(0, self.m):
            if defaulttime > self.t[i]:
                value += self.delta * self.discounter.discountFactor(self.t[i])
        return value

    cdef double defaultLegFactor(self,double defaulttime):
        cdef int i
        for i in xrange(0, self.m):
            if defaulttime <= self.t[i]:
                return (1.0 - self.recoveryrate) * self.discounter.discountFactor(self.t[i])
        return 0.0

    cdef double accruedPremiumFactor(self, double defaulttime):
        cdef int i
        for i in xrange(0, self.m):
            if defaulttime <= self.t[i]:
                return 0.5 * self.delta * self.discounter.discountFactor(self.t[i])
        return 0.0

