from bcd.entity import ENTITIES, Entity
from bcd.calibration import GaussianCalibrator
from bcd.discounter import SimpleDiscounter
from bcd.bcdpricer import BCDPricer
from numpy import array, arange
from math import ceil
from datetime import datetime
import matplotlib.pyplot as plt

def getNoOfPeriods(delta, maturityDate, effectiveDate):
     return int(ceil((maturityDate - effectiveDate).days / (365 * delta)))

entities = ["AAL.L", "AGK.L", "ATST.L", "BA.L", "BAY.L"]
delta = 0.5
includeAccruedPremium = True
seniorities = [1, 2, 3]
recoveryRates = arange(0.1, 0.9, 0.1)
noOfSimulations = 1000

mdate = datetime.strptime("20/09/2015", "%d/%m/%Y")
edate = datetime.strptime("20/06/2010", "%d/%m/%Y")

marginals = []
ent_objs = []
for t in entities:
    e = Entity(ENTITIES[t],t)
    e.calibrate()
    ent_objs.append(e)
    marginals.append(e.survivalDistribution)

calib = GaussianCalibrator()
pd = array([e.priceData() for e in ent_objs])
cop = calib.calibrate(pd)

noOfNames = len(entities)
noOfPeriods = getNoOfPeriods(delta, mdate, edate)
discounter = SimpleDiscounter([0.5, 1.0, 2.0, 3.0, 4.0, 5.0], [0.9932727, 0.9858018, 0.9627129, 0.9285788, 0.8891939, 0.8474275])


fsas = []
for k in seniorities:
    fss = []
    for rr in recoveryRates:
        pricer = BCDPricer(noOfNames, k, delta, noOfPeriods, rr, discounter, cop, marginals)
        price, sims = pricer.price(noOfSimulations, includeAccruedPremium)
        fss.append(price)
    fsas.append(fss)

plt.plot(recoveryRates, fsas[0], 'bo', label="Seniority-1")
plt.plot(recoveryRates, fsas[1], 'ro', label="Seniority-2")
plt.plot(recoveryRates, fsas[2], 'go', label="Seniority-3")
plt.title("Gaussian")
plt.xlabel("Recovery rate")
plt.ylabel("Fair Spread")
plt.legend()
plt.show()

