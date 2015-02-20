__author__ = 'twisa'


from bcd.entity import ENTITIES, Entity
from bcd.calibration import GaussianCalibrator, StudentTCalibrator
from bcd.discounter import SimpleDiscounter
from bcd.bcdpricer import BCDPricer
from numpy import array, arange
from math import ceil
from datetime import datetime

def get_no_of_periods(delta, maturityDate, effectiveDate):
     return int(ceil((maturityDate - effectiveDate).days / (365 * delta)))


def get_calibrator(copula_type):
    calib = None
    if copula_type == 'gaussian':
        calib = GaussianCalibrator()
    else:
        # student t VAMSHI TO CHECK
        calib = StudentTCalibrator(10.0, 0.25)
    return calib


def get_bcd(entities, copula_type, seniority, delta, is_premium_accrued, \
    effective_date, maturity_date, recovery_rate, no_of_simulations):
    # What is basis used for . Is it unused ?
    marginals = []
    ent_objs = []
    pca = []
    for t in entities:
        e = Entity(ENTITIES[t],t)
        e.calibrate()
        ent_objs.append(e)
        marginals.append(e.survivalDistribution)
        pca.append(e.getGraphData())

    calib = get_calibrator(copula_type)

    pd = array([e.priceData() for e in ent_objs])
    cop = calib.calibrate(pd)

    print marginals
    no_of_names = len(entities)
    no_of_periods = get_no_of_periods(delta, maturity_date, effective_date)
    discounter = SimpleDiscounter([0.5, 1.0, 2.0, 3.0, 4.0, 5.0], [0.9932727, 0.9858018, 0.9627129, 0.9285788, 0.8891939, 0.8474275])

    ## need to handle for multiple senorities
    pricer = BCDPricer(no_of_names, seniority, delta, no_of_periods, recovery_rate, discounter, cop, marginals)
    price, sims = pricer.price(no_of_simulations, is_premium_accrued)
    return (price*100.0*100.0, sims, pca)

