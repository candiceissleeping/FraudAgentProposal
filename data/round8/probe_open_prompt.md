# Round 8 re-identification probe (open set)

Read ONLY the file you were given; do not open any other file or directory in this repository.
It contains several anonymised fact cards, each describing one US public company's annual report (fiscal years
2017–2023). For each card, try as hard as you can to identify the company. Use any knowledge you have.

Write this JSON to the output path with the Write tool, then reply "done":
{"R8-xx": {"guesses": ["most likely name", "second", "third"], "fiscal_year_guess": "YYYY or empty",
           "confidence": <0-100>, "basis": "short reason"}, ...}
Use an empty list when you have no idea. Include every card in the file.
