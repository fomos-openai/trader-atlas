from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import pandas as pd

from tests.synthetic import synthetic_market_data
from trader_atlas.config import load_config
from trader_atlas.data_contract import validate_market_data
from trader_atlas.errors import DataContractError

ROOT = Path(__file__).resolve().parents[2]


class DataContractAcceptanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config, _ = load_config(ROOT / "configs/btc-eth-spot-trend.yml")

    def test_duplicate_and_missing_rows_fail_closed(self) -> None:
        frame = synthetic_market_data()
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "market.csv"
            frame.to_csv(source, index=False)
            duplicate = pd.concat((frame, frame.iloc[[0]]), ignore_index=True)
            with self.assertRaisesRegex(DataContractError, "duplicate"):
                validate_market_data(duplicate, source, self.config)
            with self.assertRaisesRegex(DataContractError, "missing or non-daily"):
                validate_market_data(frame.drop(index=[20, 21]), source, self.config)

    def test_out_of_order_rows_are_normalized_deterministically(self) -> None:
        frame = synthetic_market_data().sample(frac=1.0, random_state=7)
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "market.csv"
            frame.to_csv(source, index=False)
            normalized, _ = validate_market_data(frame, source, self.config)
        ordered = normalized.sort_values(["timestamp", "symbol"]).reset_index(drop=True)
        pd.testing.assert_frame_equal(normalized, ordered)


if __name__ == "__main__":
    unittest.main()
