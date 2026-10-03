import sys
sys.path.insert(0,'/workspace')
from calc import add
if add(3,2)!=5 or add(-3,2)!=-1:
    raise SystemExit(1)
print('Independent regression checks passed')
