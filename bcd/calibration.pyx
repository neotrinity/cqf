__author__ = 'vamshi'
from scipy.stats import norm, kendalltau, t
from scipy.special import gammaln, gamma, stdtrit
from distribution import EmpiricalDistribution
from bcd.copula import GaussianCopula, StudentTCopula
import numpy
from math import pi
#import time

cimport numpy
from libc.math cimport sqrt, sin, log


DTYPE = numpy.double
ctypedef numpy.double_t DTYPE_t

cdef double t_pdf(double x, double df):
    """
    Notes
    -----
    The probability density function for `t` is::

                                       gamma((df+1)/2)
        t.pdf(x, df) = ---------------------------------------------------
                       sqrt(pi*df) * gamma(df/2) * (1+x**2/df)**((df+1)/2)

    for ``df > 0``.
    """
    cdef double part = ((df+1.0)/2.0)
    cdef double numer = gamma(part)
    cdef double denom = sqrt(pi*df) * gamma(df/2.0) * (1.0+x**2/df)**part
    return numer/denom
    ## Reference : https://github.com/scipy/scipy/blob/v0.14.0/scipy/stats/_continuous_distns.py#L2990-L3021
    ## VAMSHI TO CHECK
    ##
    ## Note to vamshi the below is the code present in scipy.stats.t.pdf.
    ## However the above is the formula provided in the scipy webpage
    ## Which one is correct ???

    # def _pdf(self, x, df):
    #     r = asarray(df*1.0)
    #     Px = exp(gamln((r+1)/2)-gamln(r/2))
    #     Px /= sqrt(r*pi)*(1+(x**2)/r)**((r+1)/2)
    #     return Px

    # def _logpdf(self, x, df):
    #     r = df*1.0
    #     lPx = gamln((r+1)/2)-gamln(r/2)
    #     lPx -= 0.5*log(r*pi) + (r+1)/2*log(1+(x**2)/r)
    #     return lP

def returns(numpy.ndarray adjusted_prices):
    cdef int dimension, no_of_observations,i, j
    cdef numpy.ndarray returns
    dimension, no_of_observations = len(adjusted_prices), len(adjusted_prices[0])
    returns = numpy.zeros((dimension, no_of_observations - 1))
    for i in xrange(dimension):
        for j in xrange(1, no_of_observations):
            returns[i, j-1] = log(adjusted_prices[i, j]/adjusted_prices[i, j-1])
    return returns


def transformed_variates(numpy.ndarray observations):
    cdef int dimenstion, no_of_observations, i, j
    cdef numpy.ndarray variates
    cdef object marginal
    dimension, no_of_observations = len(observations), len(observations[0])
    variates = numpy.zeros((dimension, no_of_observations))
    for i in xrange(dimension):
        marginal = EmpiricalDistribution(observations[i])
        for j in xrange(no_of_observations):
            variates[i, j] = norm.ppf(marginal.cdf(observations[i, j]))
    return variates


def uniform_variates(numpy.ndarray observations):
    cdef int dimension, no_of_observations,i,j
    cdef numpy.ndarray variates
    cdef object marginal
    dimension,  no_of_observations = len(observations), len(observations[0])
    variates = numpy.zeros((dimension, no_of_observations))
    for i in xrange(dimension):
        marginal = EmpiricalDistribution(observations[i])
        for j in xrange(no_of_observations):
            variates[i, j] = marginal.cdf(observations[i, j])
    return variates

def transformedTVariates(numpy.ndarray observations):
    cdef int dimension, no_of_observations,i,j
    cdef numpy.ndarray variates
    cdef object marginal
    dimension, no_of_observations = len(observations), len(observations[0])
    variates = numpy.zeros((dimension, no_of_observations))
    for i in xrange(dimension):
        marginal = EmpiricalDistribution(observations[i])
        for j in xrange(no_of_observations):
            variates[i, j] = marginal.cdf(observations[i, j])
    return variates


cdef class GaussianCalibrator:
    def calibrate(self, numpy.ndarray adjustedPrices):
        return self.calibrate_from_returns(returns(adjustedPrices))

    def calibrate_from_returns(self, numpy.ndarray returns):
        return self.calibrate_from_variates(transformed_variates(returns))

    def calibrate_from_variates(self, numpy.ndarray variates):
        cdef int dimension, no_of_observations,i,j,k
        cdef numpy.ndarray covariance
        cdef double tot
        dimension, no_of_observations = len(variates), len(variates[0])
        covariance = numpy.zeros((dimension, dimension))
        for i in xrange(dimension):
            for j in xrange(i+1):
                tot = 0.0
                for k in xrange(no_of_observations):
                    tot += variates[i, k]*variates[j, k]
                covariance[i, j] = tot/no_of_observations
                covariance[j, i] = covariance[i, j]
        return GaussianCopula(covariance)


cdef class StudentTCalibrator:
    MAXIMUM_NU_VALUE = 10.0
    DELTA = 0.2
    cdef double maximumNuValue, delta

    def __init__(self, double maximumNuValue,double delta):
        self.maximumNuValue = maximumNuValue
        self.delta = delta

    def calibrate(self, numpy.ndarray adjustedPrices):
        return self.calibrateFromReturns(returns(adjustedPrices))

    def calibrateFromReturns(self, numpy.ndarray returns):
        return self.calibrateFromVariates(transformedTVariates(returns))

    def calibrateFromVariates(self, numpy.ndarray variates):
        cdef int dimension, no_of_observations
        cdef numpy.ndarray covarianceData, sigma
        cdef double nu
        dimension, no_of_observations = len(variates), len(variates[0])
        covarianceData = self.covariance(variates)
        sigma = numpy.array(covarianceData)
        nu = self.optimalNu(variates, sigma, covarianceData)
        return StudentTCopula(covarianceData, nu)

    def covariance(self,numpy.ndarray variates):
        cdef int dimension, no_of_observations,i,j
        cdef numpy.ndarray covarianceData
        cdef double nu, tau, pv
        dimension, no_of_observations = len(variates), len(variates[0])
        covarianceData = numpy.zeros([dimension, dimension])
        for i in xrange(dimension):
            for j in xrange(i + 1):
                tau, pv = kendalltau(variates[i], variates[j])
                covarianceData[i, j] = sin(pi/2.0 * tau)
                covarianceData[j, i] = covarianceData[i, j]
        return covarianceData

    def optimalNu(self,numpy.ndarray variates,numpy.ndarray sigma,numpy.ndarray covariance):
        cdef int dimension, no_of_observations,i,j
        cdef numpy.ndarray sigmaInverse, variate, variateVector
        cdef double nu,argMax, maxValue, a,b, value,ld, determinant
        dimension, no_of_observations = len(variates), len(variates[0])
        sigmaInverse = numpy.linalg.inv(sigma)
        determinant = numpy.linalg.det(sigma)
        nu = 2.0
        argMax = 0.0
        maxValue = float("-inf")
        #start = time.time()
        while nu <= self.maximumNuValue:
            #print "start while - ", time.time() - start
            a = gammaln(0.5 * (nu + dimension)) - gammaln(0.5 * nu) - 0.5 * dimension * log(nu)
            b = 0.5 * (dimension * log(pi) + log(determinant))
            tCopula = StudentTCopula(covariance, nu)
            value = 0.0
            ld = 0.0

            for j in xrange(no_of_observations):
                variate = numpy.zeros(dimension)
                for i in xrange(dimension):
                    variate[i] = stdtrit(nu, variates[i, j])
                    ld += log(t_pdf(variate[i], nu))
                    # variate[i] = t.ppf(variates[i, j], nu)
                    # ld += log(t.pdf(variate[i], nu))
                variateVector = numpy.array(variate)
                value += log(1.0 + numpy.dot(variateVector, numpy.dot(sigmaInverse, variateVector)) / nu)
            value = no_of_observations * (a - b) - 0.5 * (nu + dimension) * value - ld
            if value > maxValue:
                maxValue = value
                argMax = nu
            nu += self.delta
            #print "end while - ", time.time() - start
        return argMax

