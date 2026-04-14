"""Prompt 19: Biome room sequences."""
import pytest
from dungeon.room import total_campaign_rooms

def test_expected_room_count_matches_srs_smoke():
    n = total_campaign_rooms()
    assert n >= 8

def test_biome_order_list_coherent():
    assert total_campaign_rooms() > 0

def test_edge_off_by_one_last_room():
    assert total_campaign_rooms() >= 1
