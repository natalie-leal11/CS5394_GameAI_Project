Open and execute the repo file
DebugOverlay_MasterPrompt.md
exactly as written. Do not modify the document.

CRITICAL CONTEXT

This prompt pack implements a lightweight AI debugging overlay for the game.
The overlay must display runtime information from the AI Director system but
must not modify gameplay behavior.

MANDATORY RULES

1. The overlay must never modify gameplay logic.
2. The overlay must only read data from existing systems.
3. The overlay must be toggleable using the F3 key.
4. The overlay must render after all gameplay drawing.
5. The overlay must be safe if AI systems are temporarily unavailable.

EXECUTION ORDER

Run the following phases sequentially:

Phase1_DebugOverlay_System.md
Phase2_GameScene_Integration.md
Phase3_AIDirector_DataAccess.md

Stop after each phase if instructed.