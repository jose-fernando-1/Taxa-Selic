from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

import pandas as pd

from .bcb import BCBClient
from .charts import build_series_figure, figure_as_dict
from .series import SERIES_BY_SLUG, SERIES_CATALOG, SeriesDefinition
from .storage import SeriesStorage


@dataclass
class EconomicDataService:
    client: BCBClient
    storage: SeriesStorage

    def list_series(self) -> list[dict]:
        items = []
        for definition in SERIES_CATALOG.values():
            current = self.storage.load(definition.slug)
            latest = None
            if not current.empty:
                last_row = current.iloc[-1]
                latest = {
                    "date": pd.Timestamp(last_row["date"]).date().isoformat(),
                    "value": float(last_row["value"]),
                }
            items.append({**definition.to_dict(), "latest": latest})
        return items

    def update_all(self) -> list[dict]:
        return [self.update_series(definition.slug) for definition in SERIES_CATALOG.values()]

    def update_series(self, slug: str, start: date | None = None, end: date | None = None) -> dict:
        definition = self.get_definition(slug)
        existing = self.storage.load(slug)
        end = end or date.today()
        if start is None:
            if existing.empty:
                start = definition.default_start
            else:
                overlap_days = 45 if definition.frequency == "monthly" else 10
                start = (existing["date"].max().date() - timedelta(days=overlap_days))
                if start < definition.default_start:
                    start = definition.default_start
        fetched = self.client.fetch(definition, start, end)
        combined = self.storage.upsert(slug, fetched)
        return {
            "series": definition.to_dict(),
            "fetched_rows": int(len(fetched.index)),
            "stored_rows": int(len(combined.index)),
            "range": {
                "start": start.isoformat(),
                "end": end.isoformat(),
            },
        }

    def get_series(self, slug: str, start: date | None = None, end: date | None = None) -> dict:
        definition = self.get_definition(slug)
        frame = self.storage.load(slug)
        if frame.empty:
            self.update_series(slug)
            frame = self.storage.load(slug)
        if start is not None:
            frame = frame[frame["date"] >= pd.Timestamp(start)]
        if end is not None:
            frame = frame[frame["date"] <= pd.Timestamp(end)]
        frame = frame.sort_values("date")
        records = [
            {
                "date": pd.Timestamp(row.date).date().isoformat(),
                "value": float(row.value),
            }
            for row in frame.itertuples(index=False)
        ]
        latest = records[-1] if records else None
        return {
            "series": definition.to_dict(),
            "records": records,
            "latest": latest,
            "count": len(records),
        }

    def get_chart(self, slug: str, start: date | None = None, end: date | None = None) -> dict:
        payload = self.get_series(slug, start=start, end=end)
        frame = pd.DataFrame(payload["records"])
        if frame.empty:
            frame = pd.DataFrame(columns=["date", "value"])
        else:
            frame["date"] = pd.to_datetime(frame["date"])
            frame["value"] = pd.to_numeric(frame["value"], errors="coerce")
        figure = build_series_figure(self.get_definition(slug), frame)
        return {
            "series": payload["series"],
            "figure": figure_as_dict(figure),
        }

    def export_legacy_selic(self) -> None:
        frame = self.storage.load("selic-diaria")
        if frame.empty:
            return
        writable = frame.copy()
        writable["data"] = writable["date"].dt.strftime("%Y-%m-%d")
        writable["valor"] = writable["value"]
        writable[["data", "valor"]].to_csv(
            self.storage.base_dir.parent.parent / "selic_efetiva.csv",
            index=False,
        )
        recent = frame.tail(20).copy()
        recent["data"] = recent["date"].dt.strftime("%d/%m/%Y")
        recent["valor"] = recent["value"].map(lambda value: f"{value:.6f}".replace(".", ","))
        recent[["data", "valor"]].to_csv(
            self.storage.base_dir.parent.parent / "selic_recente.csv",
            index=False,
            sep=";",
        )

    @staticmethod
    def get_definition(slug: str) -> SeriesDefinition:
        definition = SERIES_BY_SLUG.get(slug)
        if definition is None:
            raise KeyError(f"Série desconhecida: {slug}")
        return definition