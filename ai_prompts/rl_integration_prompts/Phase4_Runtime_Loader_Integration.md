PHASE 4 — Runtime Loader Integration

Goal
Load tuned difficulty parameters at game start and expose them read-only.

Create or modify narrowly:

src/game/ai/difficulty_params_loader.py
src/game/main.py
existing AI Director / Player Model initialization points if needed

Requirements

1. Load config/difficulty_params.json once at startup
2. Validate the file against the parameter schema
3. Expose the loaded object as read-only runtime configuration
4. Pass parameters into AI Director and Player Model constructors
5. Do not allow mutation during gameplay
6. Preserve existing gameplay systems that are outside AI scope

Important rules

- No learning loop
- No gradient updates
- No runtime write-back to config
- No random parameter edits
- Same loaded file + same seed + same input sequence must remain deterministic

STOP AFTER IMPLEMENTATION
