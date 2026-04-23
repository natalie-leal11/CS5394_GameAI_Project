# PHASE 3 — Provide AI Director Data Access

Ensure the overlay can read AI system values.

Add getters if they do not exist.

## AIDirector

Add method:

get_debug_state()

Return dictionary:

```
{
    "difficulty": self.difficulty_modifier,
    "enemy_adjustment": self.enemy_adjustment,
    "reinforcement_chance": self.reinforcement_chance
}
```

## PlayerModel

Add method:

get_state()

Return one of:

STRUGGLING
STABLE
DOMINATING

## DebugOverlay.draw() access

Inside DebugOverlay.draw() access data like:

```
director = self.game_scene.ai_director
player_model = self.game_scene.player_model
room_controller = self.game_scene._room_controller
seed = self.game_scene.seed
```

Overlay must fail gracefully if any object is missing.

## STOP AFTER IMPLEMENTATION
