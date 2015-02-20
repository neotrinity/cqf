import math
import numpy
from scipy.stats import norm, kendalltau, t
from scipy.special import gammaln, gamma

from distribution import EmpiricalDistribution
from copula import GaussianCopula, StudentTCopula



def returns(adjusted_prices):
    dimension, no_of_observations = adjusted_prices.shape
    returns = numpy.zeros((dimension, no_of_observations - 1))
    for i in xrange(dimension):
        for j in xrange(1, no_of_observations):
            returns[i, j-1] = math.log(adjusted_prices[i, j]/adjusted_prices[i, j-1])
    return returns


def transformed_variates(observations):
    dimension, no_of_observations = observations.shape
    variates = numpy.zeros((dimension, no_of_observations))
    for i in xrange(dimension):
        marginal = EmpiricalDistribution(observations[i])
        for j in xrange(no_of_observations):
            variates[i, j] = norm.ppf(marginal.cdf(observations[i, j]))
    return variates


def uniform_variates(observations):
    dimension,  no_of_observations = observations.shape
    variates = numpy.zeros((dimension, no_of_observations))
    for i in xrange(dimension):
        marginal = EmpiricalDistribution(observations[i])
        for j in xrange(no_of_observations):
            variates[i, j] = marginal.cdf(observations[i, j])
    return variates

def transformedTVariates(observations):
    dimension, noOfObservations = observations.shape
    variates = numpy.zeros((dimension, noOfObservations))
    for i in xrange(dimension):
        marginal = EmpiricalDistribution(observations[i])
        for j in xrange(noOfObservations):
            variates[i, j] = marginal.cdf(observations[i, j])
    return variates

class GaussianCalibrator(object):

    def calibrate(self, adjustedPrices):
        return self.calibrate_from_returns(returns(adjustedPrices))

    def calibrate_from_returns(self, returns):
        return self.calibrate_from_variates(transformed_variates(returns))

    def calibrate_from_variates(self, variates):
        dimension, no_of_observations = variates.shape
        covariance = numpy.zeros((dimension, dimension))
        for i in xrange(dimension):
            for j in xrange(i+1):
                tot = 0.0
                for k in xrange(no_of_observations):
                    tot += variates[i, k]*variates[j, k]
                covariance[i, j] = tot/no_of_observations
                covariance[j, i] = covariance[i, j]
        return GaussianCopula(covariance)


class StudentTCalibrator(object):
    MAXIMUM_NU_VALUE = 10.0
    DELTA = 0.2

    def __init__(self, maximumNuValue, delta):
        self.maximumNuValue = maximumNuValue
        self.delta = delta

    def calibrate(self, adjustedPrices):
        return self.calibrateFromReturns(returns(adjustedPrices))

    def calibrateFromReturns(self, returns):
        return self.calibrateFromVariates(transformedTVariates(returns))

    def calibrateFromVariates(self, variates):
        dimension, noOfObservations = variates.shape
        covarianceData = self.covariance(variates)
        sigma = numpy.array(covarianceData)
        nu = self.optimalNu(variates, sigma, covarianceData)
        return StudentTCopula(covarianceData, nu)

    def covariance(self, variates):
        dimension, noOfObservations = variates.shape
        covarianceData = numpy.zeros([dimension, dimension])
        for i in xrange(dimension):
            for j in xrange(i + 1):
                tau, pv = kendalltau(variates[i], variates[j])
                covarianceData[i, j] = math.sin(math.pi/2.0 * tau)
                covarianceData[j, i] = covarianceData[i, j]
        return covarianceData

    def optimalNu(self, variates, sigma, covariance):
        dimension, noOfObservations = variates.shape
        sigmaInverse = numpy.linalg.inv(sigma)
        determinant = numpy.linalg.det(sigma)
        nu = 2.0
        argMax = 0.0
        maxValue = float("-inf")
        while nu <= self.maximumNuValue:
            a = gammaln(0.5 * (nu + dimension)) - gammaln(0.5 * nu) - 0.5 * dimension * math.log(nu)
            b = 0.5 * (dimension * math.log(math.pi) + math.log(determinant))
            tCopula = StudentTCopula(covariance, nu)
            value = 0.0
            ld = 0.0
            for j in xrange(noOfObservations):
                variate = numpy.zeros(dimension)
                for i in xrange(dimension):
                    variate[i] = t.ppf(variates[i, j], nu)
                    ld += math.log(t.pdf(variate[i], nu))
                variateVector = numpy.array(variate)
                value += math.log(1.0 + numpy.dot(variateVector, numpy.dot(sigmaInverse, variateVector)) / nu)
            value = noOfObservations * (a - b) - 0.5 * (nu + dimension) * value - ld
            if value > maxValue:
                maxValue = value
                argMax = nu
            nu += self.delta
        return argMax

    # def logLikelihood(self, variate, sigma, nu):
    #     dimension = variate.size
    #     tVariate = numpy.array([variate[i] for i in xrange(dimension)])
    #     observation = numpy.array([tVariate[i] for i in xrange(dimension)])
    #     variateVector = numpy.array(observation)
    #     sigmaInverse = numpy.linalg.inv(sigma)
    #     determinant = numpy.linalg.det(sigma)
    #     a = 0.0
    #     b = 0.0
    #     value = math.log(gamma(0.5 * (nu + dimension)) / gamma(0.5 * nu)) - dimension * math.log(gamma(0.5 * (nu + 1.0)) / gamma(0.5 * nu)) - 0.5 * math.log(determinant)
    #     a = math.log(1.0 + numpy.dot(variateVector, numpy.dot(sigmaInverse, variateVector)) / nu)
    #     b = 0.0
    #     for i in xrange(dimension):
    #         b += math.log(1.0 + tVariate[i] * tVariate[i] / nu)
    #     value += 0.5 * ((nu + 1.0) * b - (nu + dimension) * a)
    #     return value
