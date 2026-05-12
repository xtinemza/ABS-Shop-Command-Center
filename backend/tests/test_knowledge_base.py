"""
Tests for knowledge_base.py — vehicle lookup, spec formatting, price context.
Run with: pytest backend/tests/ -v
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from knowledge_base import find_vehicle, vehicle_context, VEHICLES


class TestFindVehicle:
    def test_exact_make_model_match(self):
        result = find_vehicle("Toyota Camry")
        assert result is not None
        assert "name" in result or len(result) > 0

    def test_case_insensitive(self):
        lower = find_vehicle("toyota camry")
        upper = find_vehicle("TOYOTA CAMRY")
        assert lower is not None
        assert upper is not None

    def test_unknown_vehicle_returns_none(self):
        result = find_vehicle("Zaphod Beeblebrox 3000")
        assert result is None

    def test_empty_query_returns_none(self):
        result = find_vehicle("")
        assert result is None

    def test_vehicles_dict_not_empty(self):
        assert len(VEHICLES) > 0


class TestVehicleContext:
    def test_returns_string(self):
        vehicle = find_vehicle("Toyota Camry")
        if vehicle:
            ctx = vehicle_context(vehicle)
            assert isinstance(ctx, str)
            assert len(ctx) > 0

    def test_empty_dict_returns_string(self):
        ctx = vehicle_context({})
        assert isinstance(ctx, str)

    def test_context_contains_oil_spec(self):
        vehicle = find_vehicle("Toyota Camry")
        if vehicle and "oil" in vehicle:
            ctx = vehicle_context(vehicle)
            assert vehicle["oil"] in ctx
