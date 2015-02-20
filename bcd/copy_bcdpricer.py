import numpy


NO_SIMULATIONS = 3000


class BCDPricer(object):
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

    def price(self, noSimulations, includeAccruedPremium):
        sum_, plSum, dlSum, apSum, defaulTime = 0.0, 0.0, 0.0, 0.0, 0.0
        simulations = []
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


    def computeDefaulTime(self, variates):
        defaulttimes = numpy.array([self.marginals[i].inverseCdf(variates[i]) for i in xrange(0, self.noofnames)])
        defaulttimes.sort()
        return defaulttimes[(self.k - 1)]

    def premiumLegFactor(self, defaulttime):
        value, time = 0.0, 0.0
        for i in xrange(0, self.m):
            if defaulttime > self.t[i]:
                value += self.delta * self.discounter.discountFactor(self.t[i])
        return value

    def defaultLegFactor(self, defaulttime):
        for i in xrange(0, self.m):
            if defaulttime <= self.t[i]:
                return (1.0 - self.recoveryrate) * self.discounter.discountFactor(self.t[i])
        return 0.0

    def accruedPremiumFactor(self, defaulttime):
        for i in xrange(0, self.m):
            if defaulttime <= self.t[i]:
                return 0.5 * self.delta * self.discounter.discountFactor(self.t[i])
        return 0.0

