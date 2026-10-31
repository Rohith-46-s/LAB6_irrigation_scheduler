import pytest
from irrigation_scheduler import should_irrigate, water_volume, schedule

# --- Tests for should_irrigate ---
def test_should_irrigate_high_moisture():
    # Covers moisture >= 60
    assert should_irrigate(65, 0, "seedling") is False

def test_should_irrigate_heavy_rain():
    # Covers rain_mm >= 10
    assert should_irrigate(40, 12, "seedling") is False

def test_should_irrigate_seedling_low_moisture():
    # Covers stage == "seedling" and moisture < 45 (True)
    assert should_irrigate(40, 2, "seedling") is True

def test_should_irrigate_seedling_high_moisture():
    # Covers stage == "seedling" and moisture < 45 (False)
    assert should_irrigate(50, 2, "seedling") is False

def test_should_irrigate_flowering_stages():
    # Covers stage == "flowering" (moisture < 55 True and False)
    assert should_irrigate(50, 2, "flowering") is True
    assert should_irrigate(58, 2, "flowering") is False

def test_should_irrigate_moderate_rain_other_stage():
    # Covers rain_mm >= 5 in default stage
    assert should_irrigate(30, 7, "mature") is False

def test_should_irrigate_default_stage_moisture():
    # Covers default stage fallback return moisture < 40 (True and False)
    assert should_irrigate(35, 2, "mature") is True
    assert should_irrigate(45, 2, "mature") is False


# --- Tests for water_volume ---
def test_water_volume_invalid_area():
    # Covers area_m2 <= 0 raising ValueError
    with pytest.raises(ValueError, match="invalid area"):
        water_volume(0, "seedling", 25)
    with pytest.raises(ValueError):
        water_volume(-5, "seedling", 25)

def test_water_volume_stages_and_temps():
    # Covers seedling stage + normal temp
    assert water_volume(10, "seedling", 20) == 20.0
    
    # Covers flowering stage + high temp (> 35)
    # litres = 5 * 1.5 = 7.5, area 10 -> 75.0
    assert water_volume(10, "flowering", 40) == 75.0
    
    # Covers other stage + low temp (< 10)
    # litres = 4 * 0.5 = 2.0, area 10 -> 20.0
    assert water_volume(10, "mature", 5) == 20.0


# --- Tests for schedule ---
def test_schedule_execution():
    zones = [
        ("Zone1", 10, 30, 0, "seedling", 20),   # Should irrigate (need: 20)
        ("Zone2", 10, 70, 0, "seedling", 20),   # Should skip (high moisture)
        ("Zone3", 50, 30, 0, "seedling", 20)    # Exceeds budget, triggers break
    ]
    # Initial budget = 30. Zone1 takes 20, leaving 10. Zone3 needs 100 (exceeds budget 10 -> break)
    result = schedule(zones, budget=30)
    assert result == ["Zone1"]

def test_schedule_empty_zones():
    assert schedule([], budget=100) == []