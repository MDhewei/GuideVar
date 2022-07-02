import os
import subprocess as sb
import sys

if len(sys.argv)==1:
    print('GuideVar docker container!\n\t- GuideVar-on is to predict the on-target efficiency of sgRNAs for Cas9 variants\n\t- GuideVar-off is to predict the off-target effects of sgRNAs for Cas9 variants')
    sys.exit(1)

if sys.argv[1]=='GuideVar-on':
    sb.call(["/opt/conda/bin/python", "/GuideVar/GuideVar-on.py"]+ sys.argv[2:])
elif sys.argv[1]=='GuideVar-off':
    sb.call(["/opt/conda/bin/python", "/GuideVar/GuideVar-off.py"]+ sys.argv[2:])
else:
    print('GuideVar docker container!\n\t- GuideVar-on is to predict the on-target efficiency of sgRNAs for Cas9 variants\n\t- GuideVar-off is to predict the off-target effects of sgRNAs for Cas9 variants')
    
    
