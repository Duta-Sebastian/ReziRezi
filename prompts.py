def transcript_extract_all_names(transcript: str):
    return f"""Task: Extract all person names mentioned in the following Romanian audio transcript(s).

Instructions:

1. Identify ALL Romanian and foreign names mentioned, including:
   - Full names (prenume și nume de familie)
   - Partial names (doar prenume sau doar nume)
   - Diminutives and nicknames (e.g., Ionuț, Gigel, Ralu, Anca)
   - Names with Romanian diacritics (ă, â, î, ș, ț)
   - Foreign names mentioned in Romanian context
   - Names preceded by titles (domnul/doamna, dl./dna., etc.)

2. Format your output as a clean list with:
   - Each unique name on a new line.
   - Preserve Romanian diacritics exactly as written
   - Include context if available (e.g., "Mihai Popescu (directorul)", "doamna Andreea (clienta)")
   - Group variations of the same person (e.g., "Alexandru Ionescu / Alex / domnul Ionescu")

3. Pay attention to Romanian-specific patterns:
   - Vocative case (e.g., "Mihaele", "Marino")
   - Genitive forms (e.g., "lui Andrei", "al Mariei")
   - Common Romanian name prefixes/suffixes (-escu, -eanu, -ică, etc.)

4. Exclude:
   - Company/institution names
   - Place names (cities, streets)
   - Brand names
   - Fictional characters (unless relevant)

5. If uncertain whether something is a person's name, include it with a [?] marker.

6. Normalize and Correct: This is the most important step. For each person identified, determine their full and correct official name, even if they are mentioned by a nickname, a partial name, or a potential transcription error (e.g., if the transcript says "Ciolnau," you should identify him as "Marcel Ciolacu").

Transcript:
{transcript}

Output:
List all identified names. RETURN ONLY THE NAMES!!!"""