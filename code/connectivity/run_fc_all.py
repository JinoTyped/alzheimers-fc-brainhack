import os
from fc_utilities import first_level
DERIV = os.path.expanduser("~/derivatives/adni/fmriprep/25.2.4")
BIDS  = os.path.expanduser("~/adni/bids")
for s in sorted(os.listdir(BIDS)):
    if s.startswith("sub-"):
        first_level(DERIV, s[4:], bids_root=BIDS)
