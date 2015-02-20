__author__ = 'vamshi'
import os
import numpy
from distribution import StepwiseHazardDistribution


DEFAULT_TENOR = [0.5, 1.0, 2.0, 3.0, 5.0, 7.0, 10.0]
DEFAULT_ALPHA = [0.016832, 0.020203, 0.021950, 0.030838, 0.028126, 0.032054, 0.030386]

ENTITIES = {
    "AAL.L": "ANGLO AMERICAN",
    "ABF.L": "ASSOCIAT BRIT FOODS",
    "ABG.L": "AFRICAN BARR GOLD",
    "ADM.L": "ADMIRAL GROUP",
    "AGK.L": "AGGREKO",
    "AMEC.L": "AMEC",
    "ANTO.L": "ANTOFAGASTA",
    "ARM.L": "ARM HOLDINGS",
    "ATST.L": "ALLIANCE TRUST",
    "AU.L": "AUTONOMY CORP",
    "AV.L": "AVIVA",
    "AZN.L": "ASTRAZENECA",
    "BA.L": "BAE SYSTEMS",
    "BARC.L": "BARCLAYS",
    "BATS.L": "BRIT AMER TOBACCO",
    "BAY.L": "BRITISH AIRWAYS",
    "BG.L": "BG GROUP",
    "BLND.L": "BRIT LAND CO REIT",
    "BLT.L": "BHP BILLITON",
    "BNZL.L": "BUNZL",
    "BP.L": "BP",
    "BRBY.L": "BURBERRY GROUP",
    "BSY.L": "B SKY B GROUP",
    "BT-A.L": "BT GROUP",
    "CCL.L": "CARNIVAL",
    "CNA.L": "CENTRICA",
    "CNE.L": "CAIRN ENERGY",
    "COB.L": "COBHAM",
    "CPG.L": "COMPASS GROUP",
    "CPI.L": "CAPITA GRP",
    "CSCG.L": "CAP SHOP CENTRES",
    "DGE.L": "DIAGEO",
    "ESSR.L": "ESSAR ENERGY",
    "FRES.L": "FRESNILLO",
    "GFS.L": "G4S"}


class Entity(object):
    def __init__(self, name, ticker, sector=''):
        self.name = name
        self.ticker = ticker
        self.sector = sector
        self.survivalDistribution = None

    def priceData(self):
        datafilepath = os.path.join(os.path.dirname(__file__), os.pardir, "data/bcd-data/price" + self.ticker + ".csv")
        return numpy.genfromtxt(datafilepath, dtype=float)

    def calibrate(self):
        if self.survivalDistribution is not None:
            return

        datafilepath = os.path.join(os.path.dirname(__file__), os.pardir, "data/bcd-data/survival" + self.ticker + ".csv")
        try:
            tenor_alpha = numpy.genfromtxt(datafilepath, dtype=float, delimiter=",")
            self.survivalDistribution = StepwiseHazardDistribution(tenor_alpha[:, 0], tenor_alpha[:, 1])
        except IOError:
            self.survivalDistribution = StepwiseHazardDistribution(DEFAULT_TENOR, DEFAULT_ALPHA)

    def getGraphData(self):
        return {
            'label': self.ticker,
            'data': [(i*0.1, self.survivalDistribution.Q(i*0.1)) for i in range(100)]
            }



