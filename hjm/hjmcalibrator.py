__author__ = 'vamshi'

import numpy
import numpy.linalg as linalg
from math import sqrt
from hjm.hjmmodel import HJMModel


class HJMCalibrator(object):
    def calibrate(self, forwardRateData, noOfFactors):
        tau = numpy.array(forwardRateData[0])
        forwardRates = forwardRateData[1:]/100.0
        forwardRate = numpy.array(forwardRates[forwardRates.shape[0]-1])
        eigenDataSet = self.orderedEigenData(forwardRates)
        sigma = self.volatilityFactors(eigenDataSet, noOfFactors, tau.size)
        return HJMModel(tau, forwardRate, sigma)

    def volatilityFactors(self, eigenDataSet, noOfFactors, m):
        sigma = numpy.zeros([noOfFactors, m])
        eva, eve = eigenDataSet
        for i in xrange(noOfFactors):
            sigma[i] = eve[:, i] * sqrt(eva[i])
        return sigma

    def orderedEigenData(self, forwardRates):
        covMat = numpy.cov(self.computeDiffs(forwardRates), rowvar=0, ddof=0)
        eigenValues, eigenVectors = linalg.eigh(covMat)
        idx = eigenValues.argsort()[::-1]
        eigenValues = eigenValues[idx]
        eigenVectors = eigenVectors[:, idx]
        return (eigenValues, eigenVectors)

    def computeDiffs(self, forwardRates):
        noRows, noCols = forwardRates.shape
        diffData = numpy.zeros([noRows - 1, noCols])
        sqrtRootDelta = sqrt(0.00396825396825397)
        for i in xrange(noRows-1):
            for j in xrange(noCols):
                f = forwardRates[i][j]
                fNext = forwardRates[(i + 1)][j]
                diffData[i][j] = (fNext - f) / (sqrtRootDelta * min(1.0, f))
        return diffData



