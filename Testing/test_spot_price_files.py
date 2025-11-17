import sys
import types

import pandas as pd
import pytest

sys.modules.setdefault(
    "flexoffer_logic", types.SimpleNamespace(set_time_resolution=lambda *_, **__: None)
)

from config import config
from database import dataManager


def test_missing_spot_price_files_fail_fast(monkeypatch, tmp_path):
    monkeypatch.setattr(config, "DATA_FILEPATH", str(tmp_path))
    monkeypatch.setattr(config, "TIME_RESOLUTION", 3600)
    dataManager.load_and_prepare_prices.cache_clear()

    with pytest.raises(FileNotFoundError):
        dataManager.loadSpotPriceData()

    with pytest.raises(FileNotFoundError):
        dataManager.load_and_prepare_prices(pd.Timestamp("2024-01-01"), 1, config.TIME_RESOLUTION)
