#!/bin/bash          
extTXT=.TXT
extCSV=.csv
for ticker in AAL.L ABF.L ABG.L ADM.L AGK.L AMEC.L ANTO.L ARM.L ATST.L AU.L AV.L AZN.L BA.L BARC.L BATS.L BAY.L BG.L BLND.L BLT.L BNZL.L BP.L BRBY.L BSY.L BT-A.L CCL.L CNA.L CNE.L COB.L CPG.L CPI.L CSCG.L DGE.L EMG.L ENRC.L ESSR.L EXPN.L FRES.L GFS.L GKN.L GSK.L HMSO.L HSBA.L IAP.L IHG.L III.L IMT.L INVP.L IPR.L ISAT.L ISYS.L
do
  echo "working on $ticker"
  cut -f5 -d" " "$ticker$extTXT" > temp.csv
  tail -n1006 temp.csv > "price$ticker$extCSV"
done
