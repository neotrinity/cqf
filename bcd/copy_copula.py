import numpy
from scipy.stats import norm, chi2, t
import math
# https://julien.danjou.info/blog/2013/guide-python-static-class-abstract-methods
# Maybe i should try this later


class Copula(object):

    #dimension=0

    def density(self, u):
        raise NotImplementedError()

    def _simulate(self, n):
        samples = numpy.zeros((n, self.dimension))
        for i in xrange(n):
            samples[i] = self.simulate()
        return samples

    def simulate(self):
        raise NotImplementedError() # Dont know how this is going to work


class GaussianCopula(Copula):

    def __init__(self, covariance):
        self.covariance = covariance
        self.random_state = numpy.random.RandomState()
        self.dimension = self.covariance[0].size
        self.cholesky_factor = numpy.linalg.cholesky(self.covariance)

    def display_parameters(self):
        sigma = self.covariance
        print(sigma)


    def simulate(self):
        # z = numpy.zeros(self.dimension)
        # for i in xrange(self.dimension):
        #     z[i] = self.random_state.normal(loc=0.0, scale=1.0)
        z = self.random_state.normal(loc=0.0, scale=1.0, size=(self.dimension, ))
        x = numpy.dot(self.cholesky_factor, z)
        for i in xrange(self.dimension):
            x[i] = norm.cdf(x[i], loc=0.0, scale=1.0)
        return x


class StudentTCopula(Copula):

    def __init__(self, covariance, nu):
        self.covariance = covariance
        self.dimension = self.covariance[0].size
        self.cholesky_factor = numpy.linalg.cholesky(self.covariance)
        self.sigma = numpy.array(covariance)
        self.sigmaInverse = numpy.linalg.inv(self.sigma)
        self.determinant = numpy.linalg.det(self.sigma)
        self.nu = nu


    def simulate(self):
        z = norm.rvs(loc=0.0, scale=1.0, size=self.dimension)
        x = numpy.dot(self.cholesky_factor, z)
        s = chi2.rvs(self.nu, size=1)[0]
        for i in xrange(self.dimension):
            x[i] = t(self.nu).cdf(x[i] * math.sqrt(self.nu / s))
        return x


