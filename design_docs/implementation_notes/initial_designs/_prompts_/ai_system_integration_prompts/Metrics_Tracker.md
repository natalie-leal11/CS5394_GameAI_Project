FINAL — MetricsTracker Attributes (Aligned with Current Implementation)
🔹 1. Run-Level (VALID)

These are fully supported:

run_seed

run_start_time

run_elapsed_time

rooms_cleared

biomes_cleared (can derive from room index ranges)

total_deaths

total_damage_taken

total_damage_dealt

total_healing_received

total_healing_wasted (only if you track overheal vs cap)

total_rewards_collected

total_upgrades_selected (only safe-room upgrades)


🔹 2. Player State (VALID)

hp_percent_current

hp_absolute_current

low_hp_events_count (easy: HP < 30%)

near_death_events_count (HP < 15%)

revive_used_count (ONLY Biome 4 boss → player revive NOT present → keep as 0 or remove)

🔹 3. Room Lifecycle (VALID)

current_room_index

current_biome_index

room_start_time

room_end_time

room_clear_time

room_active_flag

🔹 4. Room Health Metrics (VALID)

hp_percent_start_room

hp_percent_end_room

hp_lost_in_room

hp_gained_in_room

max_hp_during_room

min_hp_during_room

🔹 5. Combat Metrics (VALID)

damage_taken_in_room

damage_dealt_in_room

damage_taken_rate

damage_dealt_rate

hits_taken_count

hits_given_count

kill_count_room

kill_count_total

🔹 6. Enemy Interaction (PARTIAL — simplify)

Keep only what is realistically trackable:

enemy_types_in_room

enemy_composition_id (derive from spawn_specs)

damage_taken_by_enemy_type

kills_by_enemy_type



🔹 7. Encounter Context (VALID)

room_type

enemies_spawned_count

elite_enemies_count

ambush_flag

spawn_pattern_type (spread / triangle / ambush / single)

spawn_delay_profile (0, 0.4, 0.8 etc)



🔹 8. Hazard Metrics (VALID)

hazard_tiles_count

time_in_hazard_tiles

damage_from_hazards

hazard_type_distribution (lava vs slow)

🔹 9. Player Behavior (PARTIAL)

Keep simple:

movement_distance

idle_time

dash_count

time_near_enemies

time_far_from_enemies


🔹 10. Room Outcome (IMPORTANT — KEEP)

These are critical for AI Director later:

room_result
→ enum:

clean_clear

damaged_clear

near_death

death

clean_clear_flag

heavy_damage_flag

near_death_flag

death_flag

death_room_index

death_biome_index

🔹 11. Rewards (SIMPLIFIED — MATCH GAME)
✅ Keep:

reward_dropped_flag

reward_collected_flag

reward_type (heal orb only for now)

reward_value (% heal)

time_to_collect_reward

reward_missed_flag



🔹 12. Healing Metrics (VALID)

healing_orb_collected_count

healing_amount_collected

healing_wasted



🔹 13. Upgrade Metrics (IMPORTANT — KEEP)

upgrade_options_count (Biome 3/4 only)

upgrade_selected_type (health / speed / attack / defense)

upgrade_selected_id

upgrade_power_value

upgrade_skipped_flag

🔹 14. Trend Metrics (KEEP — but simple)

last_3_rooms_hp_loss

last_3_rooms_clear_time

last_3_rooms_result

recent_death_flag

recent_struggle_flag

recent_dominating_flag

🔹 15. Derived Signals (SIMPLIFY)

struggling_rooms_count

dominating_rooms_count

spike_damage_events


🔹 16. Biome-Level Metrics (VALID)

biome_start_time

biome_end_time

biome_clear_time

biome_damage_taken

biome_deaths

🔹 17. History Storage (KEEP)

room_history

biome_history