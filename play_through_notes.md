Small Notes on game play-through:

* There will be significantly more logs than run notes. Some runs were simply blind play-throughs. 

General Notes to apply later:
- No story screen between main menu and start room.
- We should fix main menu button area. When I click quit it takes me to settings, when I click settings it takes me to controls.
- Esc only quits game, it does not pause.
- Maybe we could add player attack limits later on, to prevent spam attacks.
- Possible system circumstance: I work on a mac, so not sure whether long and short range are both working, the mouse only does one click (do not see two type of attacks, only one which I assume to be short)

First Run: 
- No fountain asset on safe room. 
- Unsure on whether parry and block are working, could be user error.
    - No overlaying assets happening and damage always applied.
    - We could make specifc test case just to ensure that parry and block work.
- Game over works - simple game over message overlay.


Second Run - Detailed Notes about room sequences:
- First room - Start room.
- Second room - Combat room.
- Third room - Combat room.
- Fourth room - Ambush room.
- Fifth room - Safe room (when picking up health upgrade, it goes over 1000)
- Sixth Room - Elite Room
- Seventh Room - Combat Room
- Eighth Room - Mini Boss Room (picked up health upgrade, replenished up to 1000).

- Ninth Room - Combat Room
- Tenth Room - Combat Room
- Eleventh Room - Ambush Room
- Twelfth Room - Safe Room (picked up health upgrade, replenished up to 1000).
- Thirteenth Room - combat room (picked up health upgrade, replenished up to 1000).
- Fourteenth Room - Elite Room
- Fifteenth Room - Elite Room 
- Sixteenth Room - Mini Boss Room (summoning after deathworked).

- Seventeenth Room - Elite Room
- Eighteenth Room - Combat Room (with ranged enemies, their running away keeps the game instereing in my opinion. Picked up health upgrade, replenished below 1000.)
- Nineteenth Room - Ambush Room
- Twentieth Room - Combat Room
- Twenty First Room - Safe Room (picked up health upgrade, it goes over 1000).
- Twenty Second Room - Elite Room
- Twenty Third Room - Combat Room
- Twenty Fourth Room - Mini Boss Room (summoning right before deathworked).

- Twenty Fifth Room - Combat Room 
- Twenthy Sixth Room - Ambush Room
- Twenty Seventh room - Elite Room
- Twenty Eigth Room - Ambush Room
- Twenty Ninth Room - Safe Room (health was low, upgrade went up by 300. Two upgrades)
- Thirtieth Room - Final Boss (summoning worked, died so no victory screen).

Third Run:
- Heavy enemy does not move beyond specific box. Very limited movement, don't remember if this is how we coded it. Please confirm. 
- Possible user error: with the uncertainty of long range attack and block working, range enemies are much harder to deal with especially in larger quantities as I have to individually run behind each to attack in short range. If you have done a completed run-through and can do long range, test whether it is a more level match. 
    - Please confirm whether this is my specifc system, or an overall implementation error in the game.

Fourth Run:
- Made it all the way to final boss. Died on second phase of final boss


After Runs: 
- As of seed controlled variation, I think the 3 variants might be too small a number, as the game starts to feel repetitive after playing for a while. Might think to expand later on
    - Checked to ensure BEGINNER_TEST_MODE = False
    - If you complete multiple runs, let me know whether you think the same. 
- After reviewing some AI Logs, from later runs, there does seem to be some contradiction between the player status and the actual play. For example, in later rooms, I ended in near death consistently, while the log still listed the status as dominating/stable. 