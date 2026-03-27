# MASTER PROMPT — Preliminary RL Integration
# STRICT REQUIREMENT-BOUND PROMPT SYSTEM

You are integrating a PRELIMINARY reinforcement learning support layer into an
existing 2D top-down dungeon game.

You MUST strictly follow the Software Requirements Specification (SRS).
You MUST preserve the existing src code architecture unless a phase explicitly
permits adding a new file or a narrow integration hook.
You MUST NOT add online learning.
You MUST NOT let RL modify gameplay during a run.
You MUST generate phase-based prompts only.

This is a graded academic project.

---

# OFFICIAL SOURCE OF TRUTH

All implementation must align with:

- AI_Dungeon_SRS.pdf
- Existing src code already present in the repository
- Existing AI integration prompt packs already used for Seed Variation,
  Player Model, and AI Director

If any ambiguity exists:
1. The SRS has final authority.
2. Existing src systems that are outside RL scope must remain unchanged.

---

# RL SCOPE (MANDATORY)

RL is OFFLINE ONLY.

RL may tune numerical parameters used by the AI Director system, such as:
- enemy count multipliers
- elite probability bias
- ambush probability bias
- reinforcement probability
- healing bias
- state classification thresholds

RL must NOT:
- alter dungeon structure
- alter room count
- alter biome boundaries
- alter hazard caps
- alter boss phase logic
- alter base player stats
- execute during gameplay
- mutate parameters at runtime

Runtime gameplay must remain deterministic.

---

# ARCHITECTURE REQUIREMENT

Use additive, modular files only.

Recommended structure:

src/
└── game/
    ├── ai/
    │   ├── difficulty_params.py
    │   └── difficulty_params_loader.py
    ├── rl/
    │   ├── dataset_export.py
    │   ├── offline_tuning_spec.py
    │   └── reward_eval.py
    └── logger.py

tools/
└── rl/
    ├── export_run_dataset.py
    ├── evaluate_candidate_params.py
    └── write_tuned_params.py

config/
└── difficulty_params.json

Do not collapse this into one monolithic file.

---

# IMPLEMENTATION CONTRACT

The preliminary RL integration must do the following:

1. Define a read-only runtime difficulty parameter schema
2. Load tuned parameters from config at game start
3. Keep logging isolated from gameplay logic
4. Export offline-ready run data for later RL tuning
5. Provide a deterministic reward evaluation utility
6. Never run learning or parameter updates during gameplay

Stop after each phase if instructed.

---

# EXECUTION ORDER

Run the following phases sequentially:

Phase1_Runtime_Params_Contract.md
Phase2_Offline_Logging_and_Dataset_Export.md
Phase3_Reward_Evaluation_Utilities.md
Phase4_Runtime_Loader_Integration.md
Phase5_Guardrails_and_Verification.md
