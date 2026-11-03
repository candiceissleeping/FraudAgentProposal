# Round 9 re-identification probe (closed set)

Read ONLY the file you were given; do not open any other file or directory in this repository.
It starts with a list of 54 candidate companies, followed by 54 anonymised fact cards. Each card belongs to
exactly one candidate (one card per company). Use any knowledge you have about these companies (industry,
history, accounting events, size, financing, management changes) to match every card to a company.

Write this JSON to the output path with the Write tool, then reply "done":
{"R9-xx": {"assigned": "<candidate name exactly as listed>", "confidence": <0-100>, "basis": "short reason"}, ...}
Include all 54 cards.
