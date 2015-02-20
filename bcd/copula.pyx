#__author__ = 'vamshi'
from scipy.stats import norm, chi2, t
from scipy.special import stdtr, ndtr
import numpy
cimport numpy
from numpy.random import standard_normal, chisquare
from libc.math cimport sqrt

DTYPE = numpy.double
ctypedef numpy.double_t DTYPE_t


cdef class GaussianCopula:
    cdef object random_state
    cdef int dimension
    cdef public numpy.ndarray covariance
    cdef numpy.ndarray cholesky_factor

    def __init__(self, numpy.ndarray covariance):
        self.covariance = covariance
        self.random_state = numpy.random.RandomState()
        self.dimension = len(self.covariance[0])
        self.cholesky_factor = numpy.linalg.cholesky(self.covariance)

    def simulate(self):
        cdef numpy.ndarray z = self.random_state.normal(loc=0.0, scale=1.0, size=(self.dimension, ))
        cdef numpy.ndarray x = numpy.dot(self.cholesky_factor, z)
        cdef int i
        for i in xrange(self.dimension):
            ## VAMSHI TO CHECK
            ## https://github.com/scipy/scipy/blob/v0.14.0/scipy/stats/_continuous_distns.py#L105-L106
            ## https://github.com/scipy/scipy/blob/v0.14.0/scipy/stats/_continuous_distns.py#L155-L156
            ## https://github.com/scipy/scipy/blob/v0.14.0/scipy/stats/_distn_infrastructure.py#L443-L444
            # x[i] = norm.cdf(x[i], loc=0.0, scale=1.0)
            # possibly a great speed up to check
            x[i] = ndtr(x[i])
        return x


cdef class StudentTCopula:
    cdef int dimension
    cdef public numpy.ndarray covariance
    cdef numpy.ndarray cholesky_factor, sigma, sigmaInverse
    cdef double determinant, nu

    def __init__(self, numpy.ndarray covariance,double nu):
        self.covariance = covariance
        self.dimension = self.covariance[0].size
        self.cholesky_factor = numpy.linalg.cholesky(self.covariance)
        self.sigma = numpy.array(covariance)
        self.sigmaInverse = numpy.linalg.inv(self.sigma)
        self.determinant = numpy.linalg.det(self.sigma)
        self.nu = nu

    def simulate(self):
        #cdef numpy.ndarray z = norm.rvs(loc=0.0, scale=1.0, size=self.dimension)
        # reference : https://github.com/scipy/scipy/blob/v0.14.0/scipy/stats/_continuous_distns.py#L146-L147
        # Not a great speed up
        # VAMSHI TO CHECK
        cdef numpy.ndarray z = standard_normal(self.dimension)
        cdef numpy.ndarray x = numpy.dot(self.cholesky_factor, z)
        #cdef double s = chi2.rvs(self.nu, size=1)[0]
        # reference http://docs.scipy.org/doc/numpy/reference/generated/numpy.random.chisquare.html
        # https://github.com/scipy/scipy/blob/v0.14.0/scipy/stats/_continuous_distns.py#L779-L780
        # NOTE : by default a scalar is returned which is what we want
        # VAMSHI TO CHECK
        cdef double s = chisquare(self.nu)
        cdef int i
        for i in xrange(self.dimension):
            #x[i] = t(self.nu).cdf(x[i] * sqrt(self.nu / s))
            # reference code https://github.com/scipy/scipy/blob/v0.14.0/scipy/stats/_continuous_distns.py#L3024
            # # very very great speed up
            # VAMSHI TO CHECK
            x[i] = stdtr(self.nu, x[i] * sqrt(self.nu / s))
        return x


