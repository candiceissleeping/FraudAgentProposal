Packets scored: 20; recognised by the identify request: 20

## All scored filings
| Method | n (treat/ctrl) | AUC | 95% CI |
|---|---|---|---|
| L LLM contradictions | 11/9 | 0.52 | 0.25-0.79 |
| L unverified | 11/9 | 0.52 | 0.25-0.80 |
| L overall rating | 11/9 | 0.56 | 0.29-0.82 |
| C consistency (round 5) | 11/9 | 0.50 | 0.50-0.50 |
| T keyword (round 4) | 11/9 | 0.54 | 0.27-0.81 |
| R rubric v2 (round 4) | 11/9 | 0.76 | 0.52-0.94 |
| F Dechow (round 5) | 11/8 | 0.47 | 0.19-0.75 |
| R+L | 11/9 | 0.65 | 0.38-0.87 |
| T+L | 11/9 | 0.57 | 0.30-0.85 |

## Not recognised by the model
| Method | n (treat/ctrl) | AUC | 95% CI |
|---|---|---|---|

## Recognised by the model
| Method | n (treat/ctrl) | AUC | 95% CI |
|---|---|---|---|
| L LLM contradictions | 11/9 | 0.52 | 0.25-0.79 |
| L unverified | 11/9 | 0.52 | 0.25-0.80 |
| L overall rating | 11/9 | 0.56 | 0.29-0.82 |
| C consistency (round 5) | 11/9 | 0.50 | 0.50-0.50 |
| T keyword (round 4) | 11/9 | 0.54 | 0.27-0.81 |
| R rubric v2 (round 4) | 11/9 | 0.76 | 0.52-0.94 |
| F Dechow (round 5) | 11/8 | 0.47 | 0.19-0.75 |
| R+L | 11/9 | 0.65 | 0.38-0.87 |
| T+L | 11/9 | 0.57 | 0.30-0.85 |

## Excluding post-disclosure pairs (AIG, ITT, Navistar)
| Method | n (treat/ctrl) | AUC | 95% CI |
|---|---|---|---|
| L LLM contradictions | 11/9 | 0.52 | 0.25-0.79 |
| L unverified | 11/9 | 0.52 | 0.25-0.80 |
| L overall rating | 11/9 | 0.56 | 0.29-0.82 |
| C consistency (round 5) | 11/9 | 0.50 | 0.50-0.50 |
| T keyword (round 4) | 11/9 | 0.54 | 0.27-0.81 |
| R rubric v2 (round 4) | 11/9 | 0.76 | 0.52-0.94 |
| F Dechow (round 5) | 11/8 | 0.47 | 0.19-0.75 |
| R+L | 11/9 | 0.65 | 0.38-0.87 |
| T+L | 11/9 | 0.57 | 0.30-0.85 |

## Paired bootstrap (2000 draws)
- R+L - R rubric v2 (round 4): -0.12 (95% CI -0.29 to +0.08)
- L LLM contradictions - C consistency (round 5): +0.02 (95% CI -0.25 to +0.29)

## Run-to-run reliability
- Spearman rank correlation of L, run 1 vs 2: 0.89
- Same flag (L > 0 vs L = 0) in both runs: 18/20

## Within-pair comparison (treatment higher / tie / lower)
- L LLM contradictions: 1 / 0 / 2
- L unverified: 1 / 0 / 2
- L overall rating: 1 / 0 / 2
- C consistency (round 5): 0 / 3 / 0
- T keyword (round 4): 2 / 0 / 1
- R rubric v2 (round 4): 2 / 0 / 1
- F Dechow (round 5): 0 / 0 / 3
- R+L: 1 / 0 / 2
- T+L: 2 / 0 / 1

## Flag rate (L > 0)
- treatment: 10/11
- control: 9/9
