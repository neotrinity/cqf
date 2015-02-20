__author__ = 'vamshi'

import numpy
import os
from hjm.hjmcalibrator import HJMCalibrator
from hjm.pricer import ZCBPricer, CapPricer


DELTA = 0.08333333333333333


class HJMPricer(object):
    def __init__(self, principal, product, maturity, interestRate, frequency, noOfFactors, noOfSimulations):
        self.principal = principal
        self.product = product
        self.maturity = maturity
        self.interestRate = interestRate / 100.0
        self.frequency = frequency
        self.noOfFactors = noOfFactors
        self.noOfSimulations = noOfSimulations
        self.forwardRateData = None

    def getHjmPrice(self):
        hjmModel = self.calibrate()
        pricer = None
        if self.product == "CAP":
            pricer = CapPricer(hjmModel, self.principal, self.maturity, self.interestRate, self.frequency)
        if self.product == "ZCB":
            pricer = ZCBPricer(hjmModel, self.principal, self.maturity)
        return pricer.price(self.noOfSimulations), hjmModel.getPCAData()

    def loadData(self):
        datafilepath = os.path.join(os.path.dirname(__file__), os.pardir, "data/hjm-data/forwardRates.csv")
        return numpy.genfromtxt(datafilepath, dtype=float, delimiter=",")

    def calibrate(self):
        if self.forwardRateData is None:
            self.forwardRateData = self.loadData()
        return HJMCalibrator().calibrate(self.forwardRateData, self.noOfFactors)



