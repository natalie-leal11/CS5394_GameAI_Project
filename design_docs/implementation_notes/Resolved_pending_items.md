Cleaned and reorganized project structure, improved documentation, and updated README to reflect final system architecture.

Key changes:

- Reorganized repository structure:
  - Introduced artifacts/ for generated outputs (models, datasets, training logs)
  - Cleaned and structured design_docs into:
    - test_validation/
    - srs_verification/
    - class_diagram_verification/
    - implementation_notes/
  - Organized AI prompt systems into clear, modular folders

- Removed redundancy:
  - Eliminated duplicate parameter discussion files
  - Consolidated overlapping DOCS and Implemented_Game_Description content
  - Cleaned outdated planning/backlog artifacts

- Documentation improvements:
  - Added comprehensive testing audit and coverage mapping
  - Updated class diagram to match implemented architecture
  - Organized RL implementation and demo documentation

- AI / system organization:
  - Finalized AI Director, seed generation, and RL prompt packs
  - Created structured prompt phases and integration packs
  - Added debug overlay prompt pack

- Testing:
  - Added integration tests for:
    - checkpoint respawn system
    - safe room upgrade behavior
    - seeded encounter specifications
  - Improved test coverage across core gameplay and AI systems

- README update:
  - Added project overview (AI Director, RL, seed system)
  - Documented key systems and architecture
  - Clarified project structure
  - Simplified logging and determinism section

- General cleanup:
  - Organized logs and training outputs
  - Improved naming consistency across folders

No gameplay functionality changes were introduced in this commit.