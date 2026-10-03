1. Never mock a core feature. If something is stubbed, name it "stub_" and list it in README under "Limitations".
2. Every backend module gets pytest tests.
3. All geometry is in millimeters.
4. Every metric we report must be reproducible via a script in /eval and written to /eval/results/*.csv.
5. UI strings go through an i18n dictionary (en, ur).
6. No auth, payments, or databases beyond ChromaDB.
