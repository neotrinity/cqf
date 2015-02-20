__author__ = 'vamshi'
import numpy
from math import log


class SimpleDiscounter:
    def __init__(self, tenor, discounts):
        self.noOfPeriods = len(tenor)
        self.discounts = discounts
        self.tenor = tenor
        self.rates = numpy.array([-1.0*log(discounts[i])/tenor[i] for i in xrange(self.noOfPeriods)])

    def discountFactor(self, time):
        discount, t = 1.0, 0.0
        for i in xrange(0, self.noOfPeriods):
            if time <= self.tenor[i]:
                return discount+(time-t)*(self.discounts[i]-discount)/(self.tenor[i]-t)
            discount = self.discounts[i]
            t = self.tenor[i]
        return self.discounts[self.noOfPeriods-1]


