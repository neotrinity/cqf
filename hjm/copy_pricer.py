import numpy
import math


class Pricer(object):
    def __init__(self, hjmModel, grid):
        self.hjmModel = hjmModel
        self.random_state = numpy.random.RandomState()
        self.grid = grid
        self.initialCurve = self.hjmModel.computeInitialCurve(self.grid)
        self.sigmaHat = self.hjmModel.computeSigmaHat(self.grid)
        self.noOfIntervals = self.grid.size
        self.delta = numpy.zeros(self.noOfIntervals)
        t = 0.0
        for i in xrange(self.noOfIntervals):
            self.delta[i] = (self.grid[i] - t)
            t = self.grid[i]
        self.drift = numpy.zeros(self.noOfIntervals)
        self.forwardCurve = numpy.zeros(self.noOfIntervals)


    def price(self, product, noOfSimulations):
        tot = 0.0
        simulations = []
        for i in xrange(noOfSimulations):
            value = self.presentValue(product)
            tot += value
            simulations.append((i, tot / (i + 1)))
        return (tot / noOfSimulations, simulations)


    def presentValue(self, product):
        discount = 1.0
        discountedPayoff = product.initialCashflow()
        for i in xrange(self.noOfIntervals):
            self.forwardCurve[i] = self.initialCurve[i]

        lowerLimit = 0.0
        for i in xrange(self.noOfIntervals):
            shortRate = self.forwardCurve[0]
            discount *= math.exp(-1.0*shortRate * self.delta[i])
            self.updateDrift(i)
            for j in xrange(self.noOfIntervals - i - 1):
                tot = 0.0
                for k in xrange(self.hjmModel.numberOfFactors):
                    tot += self.sigmaHat[k][i][j] * self.random_state.normal(loc=0.0, scale=1.0)

                self.forwardCurve[j] = (self.forwardCurve[j + 1] + self.drift[j] * self.delta[i] + tot * math.sqrt(self.delta[i]))

            discountedPayoff += discount * product.cashflow(shortRate, lowerLimit, self.grid[i])
            lowerLimit = self.grid[i]

        return discountedPayoff

    def updateDrift(self, i):
        a = numpy.zeros(self.hjmModel.numberOfFactors)
        bPrevious = 0.0
        for j in xrange(self.noOfIntervals - i - 1):
            bNext = 0.0
            for k in xrange(self.hjmModel.numberOfFactors):
                a[k] += self.sigmaHat[k][i][j] * self.delta[i + j]
                bNext += a[k] * a[k]
            self.drift[j] = ((bNext - bPrevious) / (2.0 * self.delta[i + j]))
            bPrevious = bNext


class Product(object):
    def __init__(self, maturity):
        self.maturity = maturity

    def initialCashflow(self):
        return 0.0

    def cashflow(self, shortRate, lowerLimit, upperLimit):
        raise NotImplementedError


class ZCB(Product):
    def __init__(self, principal, maturity):
        super(ZCB, self).__init__(maturity)
        self.principal = principal

    def cashflow(self, shortRate, lowerLimit, upperLimit):
        if (lowerLimit < self.maturity) and (self.maturity <= upperLimit):
            return self.principal
        return 0.0


class Cap(Product):

    def __init__(self, principal, maturity, fixedRate, delta):
        super(Cap, self).__init__(maturity)
        self.principal = principal
        self.fixedRate = fixedRate
        self.delta = delta
        self.noOfPayments = int(math.ceil(maturity/delta))
        self.tenor = numpy.array([(i+1)*delta for i in xrange(self.noOfPayments)])

    def cashflow(self, floatingRate, lowerLimit, upperLimit):
        for i in xrange(self.noOfPayments):
            if lowerLimit < self.tenor[i] and self.tenor[i]<= upperLimit and floatingRate > self.fixedRate:
                return (floatingRate-self.fixedRate)*self.delta*self.principal
        return 0.0


class Pricer2(object):
    def __init__(self, hjmModel, principal, maturity):
        self.hjmModel = hjmModel
        self.principal = principal
        self.maturity = maturity
        self.random_state = numpy.random.RandomState()
        self.grid = None
        self.sigmaHat = None
        self.noOfIntervals = 0
        self.initialCurve = None
        self.delta = None
        self.drift = None


    def configure(self):
        self.buildGrid()
        self.initialCurve = self.hjmModel.computeInitialCurve(self.grid)
        self.sigmaHat = self.hjmModel.computeSigmaHat(self.grid)
        self.noOfIntervals = self.grid.size
        self.delta = numpy.zeros(self.noOfIntervals)
        t = 0.0
        for i in xrange(self.noOfIntervals):
            self.delta[i] = (self.grid[i] - t)
            t = self.grid[i]
        self.drift = numpy.zeros(self.noOfIntervals)


    def buildGrid(self):
        d = self.getDelta()
        gridSize = int(math.ceil(self.maturity / d))
        self.grid = numpy.array([(i + 1) * d for i in xrange(gridSize)])


    def getDelta(self):
        return 0.083333

    def price(self, noOfSimulations):
        self.configure()
        tot = 0.0
        simulations = []
        for i in xrange(noOfSimulations):
            value = self.presentValue()
            tot += value
            simulations.append((i, tot / (i + 1)))
        return (tot / noOfSimulations, simulations)

    def presentValue(self):
        raise NotImplementedError

    def updateDrift(self, i, forwardCurve):
        noOfIntervals = self.noOfIntervals
        sigmaHat = self.sigmaHat
        numberOfFactors = self.hjmModel.numberOfFactors
        delta = self.delta
        drift = self.drift

        a = numpy.zeros(numberOfFactors)
        bPrevious = 0.0
        for j in xrange(noOfIntervals - i - 1):
            bNext = 0.0
            for k in xrange(numberOfFactors):
                a[k] += sigmaHat[k][i][j] * min(1.0, forwardCurve[j]) * delta[(i + j)]
                bNext += a[k] * a[k]
            drift[j] = ((bNext - bPrevious) / (2.0 * delta[i + j]))
            bPrevious = bNext


class ZCBPricer(Pricer2):

    def __init__(self, hjmModel, principal, maturity):
        super(ZCBPricer, self).__init__(hjmModel, principal, maturity)


    def presentValue(self):
        discount = 1.0
        discountedPayoff = 0.0
        forwardCurve = numpy.array([self.initialCurve[i] for i in xrange(self.noOfIntervals)])
        lowerlimit = 0
        ## trying for speedup
        noOfIntervals = self.noOfIntervals
        delta = self.delta
        updateDrift = self.updateDrift
        numberOfFactors = self.hjmModel.numberOfFactors
        sigmaHat = self.sigmaHat
        normal = self.random_state.normal
        sqrt = math.sqrt
        drift = self.drift
        grid = self.grid
        cashflow = self.cashflow

        for i in xrange(noOfIntervals):
            shortRate = forwardCurve[0]
            discount *= math.exp(-shortRate * delta[i])
            updateDrift(i, forwardCurve)
            for j in xrange(noOfIntervals - i - 1):
                tot = 0.0
                for k in xrange(numberOfFactors):
                    tot += sigmaHat[k][i][j] * min(1.0, forwardCurve[j]) * normal()

                forwardCurve[j] = (forwardCurve[(j + 1)] + drift[j] * delta[i] + tot * sqrt(delta[i]))

            discountedPayoff += discount * cashflow(shortRate, lowerlimit, grid[i])
            lowerlimit = grid[i]
        return discountedPayoff


    def cashflow(self, shortRate, lowerLimit, upperLimit):
        if lowerLimit < self.maturity and self.maturity <= upperLimit:
            return self.principal
        return 0.0

class CapPricer(Pricer2):

    def __init__(self, hjmModel, principal, maturity, fixedRate, tenor):
        super(CapPricer, self).__init__(hjmModel, principal, maturity)
        self.fixedRate = fixedRate
        self.tenor = tenor


    def presentValue(self):
        discount = 1.0
        discountedPayoff = 0.0
        forwardCurve = numpy.array([self.initialCurve[i] for i in xrange(self.noOfIntervals)])
        for i in xrange(self.noOfIntervals):
            shortRate = forwardCurve[0]
            self.updateDrift(i, forwardCurve)
            for j in xrange(self.noOfIntervals - i - 1):
                sum = 0.0
                for k in xrange(self.hjmModel.numberOfFactors):
                    sum += self.sigmaHat[k][i][j] * min(1.0, forwardCurve[j]) * self.random_state.normal()

                forwardCurve[j] = (forwardCurve[(j + 1)] + self.drift[j] * self.delta[i] + sum * math.sqrt(self.delta[i]))

            fHat = (math.exp(shortRate * self.delta[i]) - 1.0) / self.delta[i]
            payoff = 0.0
            if fHat > self.fixedRate:
                payoff = (fHat - self.fixedRate) * math.exp(-shortRate * self.delta[i]) * self.principal
            discountedPayoff += discount * payoff
            discount *= math.exp(-shortRate * self.delta[i])
        return discountedPayoff

    def getDelta(self):
        return self.tenor

