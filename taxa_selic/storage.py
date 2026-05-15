from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd


@dataclass
class SeriesStorage:
    base_dir: Path | None = None

    def __post_init__(self) -> None:
        if self.base_dir is None:
            self.base_dir = Path(__file__).resolve().parents[1] / "data" / "series"
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def path_for(self, slug: str) -> Path:
        return self.base_dir / f"{slug}.csv"

    def load(self, slug: str) -> pd.DataFrame:
        path = self.path_for(slug)
        if not path.exists():
            return pd.DataFrame(columns=["date", "value"])
        frame = pd.read_csv(path)
        if frame.empty:
            return pd.DataFrame(columns=["date", "value"])
        frame = frame.assign(
            date=pd.to_datetime(frame["date"], errors="coerce"),
            value=pd.to_numeric(frame["value"], errors="coerce"),
        )
        frame = frame.dropna(subset=["date", "value"])
        frame = frame.drop_duplicates(subset=["date"], keep="last")
        return frame.sort_values("date").reset_index(drop=True)

    def upsert(self, slug: str, frame: pd.DataFrame) -> pd.DataFrame:
        current = self.load(slug)
        sources = [item for item in [current, frame] if not item.empty]
        if not sources:
            combined = pd.DataFrame(columns=["date", "value"])
        else:
            combined = pd.concat(sources, ignore_index=True)
        combined = combined.assign(
            date=pd.to_datetime(combined.get("date"), errors="coerce"),
            value=pd.to_numeric(combined.get("value"), errors="coerce"),
        )
        combined = combined.dropna(subset=["date", "value"])
        combined = combined.drop_duplicates(subset=["date"], keep="last")
        combined = combined.sort_values("date").reset_index(drop=True)
        writable = combined.copy()
        writable = writable.assign(date=writable["date"].dt.strftime("%Y-%m-%d"))
        writable.to_csv(self.path_for(slug), index=False)
        return combined