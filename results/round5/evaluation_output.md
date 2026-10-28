
## All 72 filings
| Method | n (treat/ctrl) | AUC | 95% CI |
|---|---|---|---|
| T keyword | 36/36 | 0.56 | 0.42-0.69 |
| M Beneish | 31/32 | 0.61 | 0.47-0.75 |
| F Dechow | 32/33 | 0.57 | 0.43-0.70 |
| C consistency | 36/36 | 0.53 | 0.46-0.59 |
| C program-only | 36/36 | 0.55 | 0.42-0.69 |
| R rubric v2 | 36/36 | 0.66 | 0.53-0.78 |
| T+F | 36/36 | 0.58 | 0.44-0.71 |
| T+F+C | 36/36 | 0.59 | 0.45-0.72 |
| R+F+C | 36/36 | 0.65 | 0.52-0.78 |

## Excluding post-disclosure pairs (AIG, ITT, Navistar)
| Method | n (treat/ctrl) | AUC | 95% CI |
|---|---|---|---|
| T keyword | 33/33 | 0.52 | 0.39-0.67 |
| M Beneish | 29/30 | 0.61 | 0.46-0.76 |
| F Dechow | 30/31 | 0.58 | 0.44-0.72 |
| C consistency | 33/33 | 0.53 | 0.46-0.60 |
| C program-only | 33/33 | 0.53 | 0.39-0.67 |
| R rubric v2 | 33/33 | 0.62 | 0.49-0.76 |
| T+F | 33/33 | 0.56 | 0.41-0.70 |
| T+F+C | 33/33 | 0.57 | 0.43-0.72 |
| R+F+C | 33/33 | 0.63 | 0.49-0.77 |

## Excluding financial-industry pairs
| Method | n (treat/ctrl) | AUC | 95% CI |
|---|---|---|---|
| T keyword | 33/33 | 0.56 | 0.42-0.70 |
| M Beneish | 31/32 | 0.61 | 0.47-0.75 |
| F Dechow | 32/33 | 0.57 | 0.43-0.70 |
| C consistency | 33/33 | 0.53 | 0.46-0.60 |
| C program-only | 33/33 | 0.54 | 0.40-0.68 |
| R rubric v2 | 33/33 | 0.68 | 0.54-0.80 |
| T+F | 33/33 | 0.59 | 0.46-0.72 |
| T+F+C | 33/33 | 0.60 | 0.46-0.73 |
| R+F+C | 33/33 | 0.67 | 0.54-0.80 |

## H3: AUC gain over the keyword method (paired bootstrap, 2000 draws)
- T+F - T: +0.02 (95% CI -0.07 to +0.12)
- T+F+C - T: +0.04 (95% CI -0.06 to +0.13)

## Within-pair comparison (treatment higher / tie / lower / not computable)
- T keyword: 20 / 2 / 14 / 0
- M Beneish: 19 / 0 / 11 / 6
- F Dechow: 17 / 0 / 15 / 4
- C consistency: 4 / 30 / 2 / 0
- C program-only: 20 / 1 / 15 / 0
- R rubric v2: 23 / 4 / 9 / 0
- T+F: 23 / 0 / 13 / 0
- T+F+C: 23 / 0 / 13 / 0
- R+F+C: 23 / 0 / 13 / 0

## Threshold flags (share of treatment flagged = hit rate; share of control flagged = false alarm)
- M Beneish > -1.78: treatment 3/31, control 0/32
- F Dechow > 1.0: treatment 23/32, control 16/33
- C consistency > 0.0: treatment 4/36, control 2/36
