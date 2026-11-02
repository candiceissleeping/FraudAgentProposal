"""Round 10: ten more small companies with SEC-confirmed misstated 10-Ks (config/round10_cases.json).

Same pipeline and design as round 9 (round9.py): automatic controls, L0' (fixed extraction, unredacted) and
L3c (round-8 rule v3.1) packets, one fresh agent per packet. See results/round10/protocol.md.

  python -m experiment.edgar_risk.round10 controls | build | agent-files --level L0|L3c --out DIR
"""
from . import round9

round9.CASES = "config/round10_cases.json"
round9.DATA = "data/round10"
round9.OUT = "results/round10"
round9.AAER = "data/round9/aaer_index_2017_2026.json"
round9.SEED = 10
round9.REQUIRE_PRIOR = False

if __name__ == "__main__":
    round9.main()
