from __future__ import annotations

from pathlib import Path


EXPECTED_TOP_LEVEL_ENTRIES = [
    "core/",
    "strategies/",
    "config/",
    "data/",
    "backtest/",
    "main.py",
    "paper_trader.py",
    "requirements.txt",
]

EXPECTED_MODULE_NAMES = [
    "clob_client.py",
    "kelly_engine.py",
    "risk_manager.py",
    "trade_logger.py",
    "backtester.py",
    "market_scanner.py",
    "storage.py",
    "noaa_client.py",
    "edge_calculator.py",
    "scanner.py",
    "signal_engine.py",
    "odds_client.py",
    "comparator.py",
    "settings.py",
    "kill_switches.py",
    "trades.db",
    "runner.py",
]


def test_prd_lists_the_documented_mvp_python_layout() -> None:
    prd_text = Path("docs/prd.md").read_text()

    for expected_entry in EXPECTED_TOP_LEVEL_ENTRIES:
        assert expected_entry in prd_text

    for expected_module_name in EXPECTED_MODULE_NAMES:
        assert expected_module_name in prd_text


def test_layout_keeps_weather_modules_inside_strategy_boundary() -> None:
    prd_text = Path("docs/prd.md").read_text()
    weather_module_names = ["noaa_client.py", "edge_calculator.py", "scanner.py"]

    assert "strategies/" in prd_text
    assert "weather/" in prd_text
    assert len(weather_module_names) == 3
    assert all(path in prd_text for path in weather_module_names)
