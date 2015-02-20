from bcd.entity import ENTITIES, Entity
from bcd.calibration import GaussianCalibrator, StudentTCalibrator
from bcd.discounter import SimpleDiscounter
from bcd.bcdpricer import BCDPricer


import numpy
#from pylab import *
import datetime as dt
import math

# print ENTITIES
e1 = Entity("CCL","AAL.L","Sector")
e2 = Entity("BP","AGK.L","Sector2")
e3 = Entity("CCL","ATST.L","Sector")
e4 = Entity("BP","BA.L","Sector2")
e5 = Entity("BP","BAY.L","Sector2")
#
e1.calibrate()
e2.calibrate()
e3.calibrate()
e4.calibrate()
e5.calibrate()
#
# g = GaussianCalibrator()
st = StudentTCalibrator(10, 0.25)
#
e1pd = e1.priceData()
e2pd = e2.priceData()
e3pd = e3.priceData()
e4pd = e4.priceData()
e5pd = e5.priceData()
#
#
# print e1pd.shape, e2pd.shape
#
pd = numpy.array([e1pd, e2pd, e3pd, e4pd, e5pd])
#
#
# gc = g.calibrate(pd)
stc = st.calibrate(pd)
#print stc.covariance
# #print gc.covariance
# print gc.cholesky_factor
#
# x = [0.1*i for i in range(1, 100)]
# y = [e2.survivalDistribution.Q(i * 0.1) for i in range(1,100)]
# plot(x,y)
# ylim(0,1)
# show()
#
#
includeAccruedPremium = True
k = 1
deltas = [0.08333333, 0.25, 0.5, 1.0]
delta = deltas[1]
noOfSimulations = 10000
recoveryrate = 0.4
noOfNames = 5
#
matdate = dt.date(2015, 9, 20)
effdate = dt.date(2010, 6, 20)
#
def getNoOfPeriods(delta, maturityDate, effectiveDate):
     return int(math.ceil((maturityDate - effectiveDate).days / (365 * delta)))
#
noOfPeriods = getNoOfPeriods(delta, matdate, effdate)
# print noOfPeriods
#
discounter = SimpleDiscounter([0.5, 1.0, 2.0, 3.0, 4.0, 5.0], [0.9932727, 0.9858018, 0.9627129, 0.9285788, 0.8891939, 0.8474275])
# print discounter.discountFactor()
marginals = []
marginals.append(e1.survivalDistribution)
marginals.append(e2.survivalDistribution)
marginals.append(e3.survivalDistribution)
marginals.append(e4.survivalDistribution)
marginals.append(e5.survivalDistribution)
#
pricer = BCDPricer(noOfNames, k, delta, noOfPeriods, recoveryrate, discounter, stc, marginals)
price, sims = pricer.price(noOfSimulations, includeAccruedPremium)
print price * 100.0 * 100.0


#from hjm.hjmpricer import *
#hjmp = HJMPricer(1.0, "CAP", 1.0, 0.4, 0.25, 3, 5000)
#(price, sims), pca = hjmp.getHjmPrice()
#print price


