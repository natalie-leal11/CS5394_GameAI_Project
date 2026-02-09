## Software Requirements Specification
## Adaptive Dungeon Desgin with an AI Director

**Group Members:** Natalie Cristina Leal Blanco, Maham Asif

## 1. Introduction

### 1.1 Purpose
The purpose of this document is to define the functional and non-functional requirements for the *Adaptive Dungeon Design with an AI Director* game system. This document serves as a formal agreement between stakeholders and developers, detailing system behavior, contraints, interfaces, and performance expectations.

The Software Requirements Specification (SRS) is intended to guide the design. implementation, and evaluation of a procedurally generated dungeon-crawling game in which a high-level AI Director dynamically adjusts difficulty, pacing and encounter structure based on player performance. The document provides sufficient detail to allow developers to implement the system without requiring additional design clarification. 

### 1.2 Document Conventions
The following conventions are used throughout this document:

- "**Shall**" indicates a mandatory requiremnet. 
- "**Should**" indicates a recommended but non-mandatory requirement.
- "**May**" indicates an optional feature.
- Functional requiremnts are labeled using the format **R<section>.<number?>** (e.g., R4.2).
- Priorities are classified as: 
    - **Essential** - Required for core functionality.
    - **Optional** - Enhances gameplay but not required 
    - **Stretch** - Future or experimental features. 

### 1.3 Intended Audience and Reading Suggestions
This document is intended for the following audiences:
- Developers and Designers: Responsible for implementing gameplay systems, AI logic, and procedural generation. 
- Testers/Evaluators: Responsible for validation that requirements are met. 
- Instructors/Reviewers: Resposible for assessing project completeness and design rigor. 

Suggested reading order:
- All readers should begin with **Section 1: Introduction**. 
- Developers and Designers should read **Sections 2, 3, 4, and 5**.
- Testers adn reviewers should focus on **Sections 4 and 5**.

### 1.4 Product Scope
*Adaptive Dungeon Design with an AI Director* is a single-player, top-down, 2D dungeon crawler with roguelike elements. Each game session consits of a fixed-length dungeon run composed of procedurally generated rooms. Rather than relying on complex enemyintelligence, the game derives challenge from adaptive encounter design and pacing. 

A centralized AI Director system monitors player performance metrics such as health, deaths, and progression speed, and dynamically adjusts enemy encounters, ambush frequency, and resource availablity. Reinforcement learning is used exclusively during offline developement to tune system parameters; no learning occurs during gameplay.

The scope of this project includes:
- Procedural dungeon generation with controlled variation.
- Deterministic AI Director behavior during gameplay.
Combat-focused gameplay with simple, aggressive enemies.
- Clear win and loss conditions per run. 

Multi-player, long-term progression systems, and real-time machine learning are explicitly outside the scope of this project.

### 1.5 References
1. “IEEE Guide for Software Requirements Specifications.” IEEE Std 830-1984 , 1984, p. 1.
EBSCOhost , DOI: h ttps://doi.org/10.1109/IEEESTD.1984.119205
2. Slither: A Game of Strategy - Software Requirements Specification
3. Adaptive Dungeon Design with an AI Director - Project Description

### 1.6 Definitions, Acronyms, and Abbreviations
- **AI Director:** A high-level control system that dynamically adjusts dungeon difficulty and pacing based on player performance.
- **Procedural Generation:** Algorithmic generation of game content using predefined rules and random seeds. 
- **Roguelike:** A game structure characterized by randomized runs, permadeath, and replayability.
- **Reinforcement Learning (RL):** A machine learning technique used offline to optimized numerical parameters.
- **Encounter:** Any combat or high-pressure gameplay situation within a dungeon room. 

## 2. Overall Description

### 2.1 Product Perspective
The Adaptive Dungeon Design system is a standalone, single-player game application. The system is composed of multiple interacting subsystems including dungeon generation, enemy behavior, player control, and an AI Director responsible for adaptive difficulty and pacing.

The AI Director operates as a meta-system layered above core gameplay systems. It does not directly control enemy behavior, but instead influences encounter design by adjusting spawn timing, enemy quantity, encounter intensity, and resource availability. Enemy AI remains deterministic and localized to individual rooms. 

### 2.2 Product Functions
The system supports a single user class:
- **Player:** A suer controlling a single character navigating procedurally generated dungeon runs. The player is assumed to have basic familiarity with action games but no prior knowledge of the AI Director system. 

The system is designed to adapt dynamically to a wide range of player skill levels through the AI Director's monitoring and adjustment mechanisms. 

### 2.4 Operating Environment 
The game shall operate in the following environment:
- Platform: Personal computer (PC)
- Operating System: Windows, MacOS (minimum requirement)
- Input Devices: Keyboard and mouse
- Display: 2D top-down rendering
- Rumtime Environment: Game engine capable of real-time input and rendering

## 3. External Interface Requirements

### 3.1 User Interfaces
The system shall provide a set of user interfaces that allow the player to interact with the game, receive feedback, and understand game state. All interfaces shall be visually consistent with a 2D top-down dungeon crawler perspective.

#### 3.1.1 Main Menu Interface
The Main Menu interface shall allow the player to: 
- Start a new run 
- Exit the game
**Requirements**
- R3.1.1 The system shall display a main menu upon game launch. 
- R3.1.2 The system shall allow the player to start a new game from the main manu.
- R3.1.3 The system shall allow the player to exit the application from the main menu.

#### 3.1.2 In-Game Heads-Up Display (HUD)
The HUD shall provide realt-ime feedback to the player during gameplay. 

Display elements include: 
- Player health 
- Current rooom or progression indicator
- Active combat state indicators

**Requirements**
- R3.2.1 The system shall display the player's current health at all time during gameplay.
- R3.2.2 The system shall visually indicate when the player is engaged in combat. 
- R3.2.3 The HUD shall update in real time without noticeable delay.

#### 3.1.3 Dungeon Room Interface
Each dungeon room shall present: 
- Environmental visuals
- Enemies and hazards
- Entry and exit points

Rooms may vary visually depending on dungeon theme and room type.

**Requirements**
- R3.3.1 The system shall visually distinguish different room types (combat, ambush, safe).
- R3.3.2 The system shall prevent progression to the next room until required conditions are met. 
- R3.3.3 The system shall visually indicate room completion.

#### 3.1.4 End-of-Run Interface
Upon completion or failure of a dungeon run, the system shall present and end-of-run screen.

**Requirements**
- R3.4.1 The system shall display a victory screen upon defeating the funal boss.
- R3.4.2 The system hall display a defeat screen when player health reaches zero.
- R3.4.3 The system shall allow the player to return to the main menu from teh end-of-run screen.

### 3.2 Hardware Interfaces
The system shall support standard PC input devices.

**Requirements**
- R3.5.1 The system shall support keyboard input for movement and actions.
- R3.5.2 The system shall support mouse input for directoinal attacks (if applicable).
- R3.5.3 Gamepad support is optional and not required for core functionality.

### 3.3 Software Interfaces
The system consits of several internal subsystems that communicate through well-defined interfaces. 

#### 3.3.1 AI Director Interface
The AI Director shall interface with:
- Player state tracking systems
- Dungeon generation system
- Enemy spawn manager

**Requirements**
- R3.6.1 The AI Director shall receive player performance data at regular intervals.
- R3.6.2 The AI Director shall output deterministic difficulty adjustment decisions.
- R3.6.3 The AI Director shall not directly control individual enemy AI.

#### 3.3.2 Reinforcement Learning Parameter Interface
Offline-trained parameters shall be loaded at runtime.

**Requirements**
- R3.7.1 The system shall load pre-trained parameter values at game start.
- R3.7.2 The system shall not modify learned parameters during gameplay.

#### 3.3.3 Operational Narrative System Interface
If enabled, a narraitve system may generate textual flavor events. 

**Requirements**
- R3.8.1 Narrative output shall be triggered only by deterministic game events.
- R3.8.2 Narrative systems shall not affect gameplay logic or difficulty.

## 4. System Features (Functional Requirements)

### 4.1 Procedural Dungeon Generation
**Description**
The system shall generate a dungeon composed of a fixed number of rooms per run. Procedural generation introduces varation while preserving a consistent difficulty curve. 

**Priority:** Essential

**Functional Requirements**
-R4.1.1 The system shall generate exactly 30 rooms per dungeon run.
- R4.1.2 the system shall include predefined miilestone rooms (start, rest, final boss).
- R4.1.3 The system shall use a procedural seed to vary room order, encounter type, and visual theme. 
- R4.1.4 The system shall preserve overall progression length regardless of branching paths.

### 4.2 AI Director Monitoring System
**Description**
The AI Director monitors player performance to inform difficulty adjustments.

**Priority:** Essential

**Functional Requirements**
- R4.2.1 The AI Director shall track player health through the run.
- R4.2.2 The AI Director shall track player deaths per run. 
- R4.2.3 The AI Director shall track player progression speed.
- R4.2.4 The AI Director shall track recent combat outcomes.

### 4.3 Dynamic Difficulty Adjustment 
**Description**
The AI Director dynamically adjusts dungeon encounters based on monitored data.

**Priority:** Essential

**Functional Requirements**
- R4.3.1 The AI Director shall determine enemy spawn timing. 
- R4.3.2 The AI Director shall determine the number of enemies per encounter.
- R4.3.3 The AI Director shall adjust enemy group composition.
- R4.3.4 The AI Director shall adjust ambush frequency. 
- R4.3.5 The AI Director shall adjust healing item and safe room availablity.
- R4.3.6 Difficulty adjustments shall remain within predefined bounds.

### 4.4 Enemy Behavior System
**Description**
Enemies are intetionally simple and aggressive, remaining confined to individual rooms.

**Priority:** Essential

**Functional Requirements**
- R4.4.1 Enemies shall not patrol or move between rooms
- R4.4.2 Enemies shall engage the player immediately upon combat start.
- R4.4.3 The system shall support multiple enemy types including melee, fast, heavy, and elite variants.
- R4.4.4 A final boss encounter shall appear at the end of each dungeon run. 

### 4.5 Player Character Mechanics
**Description**
the player character shall support combat and movement mechanics.

**Priority:** Essential

**Functional Requirements**
- R4.5.1 The player shall have a short-range attack.
- R4.5.2 The player shall have a long-range attack.
- R4.5.3 The player shall be able to dash or jump.
- R4.5.4 The player shall be able to block or parry attacks.
- R4.5.5 The system shall intitalize player base health to 100.

### 4.6 Game Ending Conditions
**Description**
Each dungeon run ends in either victory or defeat.

**Priority:** Essential

**Functional Requirements**
- R4.6.1 The system shall end the run when the final boss is defeated.
- R4.6.2 The system shall end the run when teh player health reaches zero. 
- R4.6.3 Upon run completion, the system shall reset game state for a new run.

## 5. Non-Functional Requirements 

### 5.1 Performance Requirements
- The system shall maintain a stable frame rate during gameplay.
- AI Director decisions shall not introduce noticeable delay.

### 5.2 Reliability and Robustness
- The system shall handle extended gameplay sessions without failure.
- Difficulty adjustments shall not cause inwinnable scenarior.

### 5.3 Usability
- The game shall be playable without prior instruction.
- Visual feedback shall clearly communicate game state changes.

### 5.4 Maintainability
- New enemy types and dungeon themes shall be addable with minimal system changes.
- AI Director parameters shall be adjustable without code restructuring.

## 6. Design and Implementation Constraints
- Reinforcement learning shall be used only offline.
- The AI Director shall remain deterministic during gameplay.
- The system shall operate within the constraints of a semester-long development timeline. 

## 7. Optional Enhacements
- Event-based narrative text generation
- Additional dungeon themes
- Expanded enemy variety

## 8. Appendices
- Enemy Type Definitions
- Room Type Definitions
- Player Stat Tables