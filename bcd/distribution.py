__author__ = 'vamshi'
import math
from numpy import zeros

class Distribution(object):
    def cdf(self, x):
        raise NotImplementedError()

    def F(self, t):
        return self.cdf(t)

    def Q(self, t):
        return 1.0-self.cdf(t)

    def inverseCdf(self, u):
        raise NotImplementedError()


class EmpiricalDistribution(Distribution):
    def __init__(self, observations):
        self.sorted_observations = sorted(observations)

    def cdf(self, x):
        value = 0.0
        for o in self.sorted_observations:
            if o > x:
                break
            value += 1.0
        return (value-0.5)/len(self.sorted_observations)

    def inverseCdf(self, u):
        raise NotImplementedError("Not supported yet.")


class StepwiseHazardDistribution(Distribution):
    def __init__(self, tenor, alpha):
        self.no_of_periods = len(tenor)
        self.tenor = tenor
        self.alpha = alpha
        self.upper = zeros(self.no_of_periods)
        self.upper[0] = self.alpha[0] * self.tenor[0]
        for i in xrange(1, self.no_of_periods):
            self.upper[i] = self.upper[i-1]+self.alpha[i] * (self.tenor[i] - self.tenor[i-1])

    def cdf(self, x):
        t = 0.0
        y = 0.0
        for i in xrange(self.no_of_periods):
            if x <= self.tenor[i]:
                return 1.0 - math.exp(-(y + self.alpha[i] * (x - t)))
            t = self.tenor[i]
            y = self.upper[i]
        return 1.0 - math.exp(-(y + self.alpha[self.noOfPeriods-1] * (x - t)))

    def inverseCdf(self, u):
        if u < 0.0 or 1.0 < u:
            raise ValueError("Arguments to inverseCdf must be between 0.0 and 1.0")
        if u == 0.0:
            return 0.0
        s = -math.log(1.0-u)
        t = 0.0
        y = 0.0
        for i in xrange(self.no_of_periods):
            if s <= self.upper[i]:
                return (s-y)/self.alpha[i]+t
            t = self.tenor[i]
            y = self.upper[i]
        return (s-y)/self.alpha[self.no_of_periods-1]+t



