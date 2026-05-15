from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

import pandas as pd
import requests

from .series import SeriesDefinition


class BCBClientError(RuntimeError):
    pass


@dataclass
class BCBClient:
    timeout: tuple[int, int] = (10, 30)

    def __post_init__(self) -> None:
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "taxa-selic/2.0"})

    def fetch(self, definition: SeriesDefinition, start: date, end: date) -> pd.DataFrame:
        if definition.source == "sgs":
            return self._fetch_sgs(definition, start, end)
        if definition.source == "ptax":
            return self._fetch_ptax(definition, start, end)
        raise BCBClientError(f"Fonte não suportada: {definition.source}")

    def _fetch_sgs(self, definition: SeriesDefinition, start: date, end: date) -> pd.DataFrame:
        url = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{definition.sgs_code}/dados"
        frames: list[pd.DataFrame] = []
        window_start = start

        while window_start <= end:
            window_end = min(window_start + timedelta(days=3650), end)
            params = {
                "formato": "json",
                "dataInicial": window_start.strftime("%d/%m/%Y"),
                "dataFinal": window_end.strftime("%d/%m/%Y"),
            }
            payload = self._request_json(url, params=params)
            frame = pd.DataFrame(payload)
            if not frame.empty:
                frame = frame.rename(columns={"data": "date", "valor": "value"}).copy()
                frame = frame.assign(
                    date=pd.to_datetime(frame["date"], format="%d/%m/%Y", errors="coerce"),
                    value=pd.to_numeric(frame["value"], errors="coerce"),
                )
                frames.append(frame)
            window_start = window_end + timedelta(days=1)

        if not frames:
            return self._empty_frame()
        return self._normalize_frame(pd.concat(frames, ignore_index=True))

    def _fetch_ptax(self, definition: SeriesDefinition, start: date, end: date) -> pd.DataFrame:
        if definition.ptax_symbol == "USD":
            function = (
                "CotacaoDolarPeriodo"
                f"(dataInicial='{start.strftime('%m-%d-%Y')}',"
                f"dataFinalCotacao='{end.strftime('%m-%d-%Y')}')"
            )
        else:
            function = (
                "CotacaoMoedaPeriodo"
                f"(moeda='{definition.ptax_symbol}',"
                f"dataInicial='{start.strftime('%m-%d-%Y')}',"
                f"dataFinalCotacao='{end.strftime('%m-%d-%Y')}')"
            )
        url = f"https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/{function}"
        payload = self._request_json(url, params={"$format": "json", "$top": 100000})
        frame = pd.DataFrame(payload.get("value", []))
        if frame.empty:
            return self._empty_frame()
        frame = frame.copy()
        if "cotacaoVenda" in frame:
            value_series = pd.to_numeric(frame["cotacaoVenda"], errors="coerce")
        else:
            value_series = pd.to_numeric(frame.get("paridadeVenda"), errors="coerce")
        frame = frame.assign(
            date=pd.to_datetime(frame["dataHoraCotacao"], errors="coerce").dt.normalize(),
            value=value_series,
        )
        frame = frame[["date", "value"]]
        return self._normalize_frame(frame)

    def _request_json(self, url: str, params: dict | None = None) -> dict | list:
        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
        except requests.Timeout as exc:
            raise BCBClientError(f"Timeout ao consultar {url}") from exc
        except requests.RequestException as exc:
            raise BCBClientError(f"Erro ao consultar {url}: {exc}") from exc
        try:
            return response.json()
        except ValueError as exc:
            raise BCBClientError(f"Resposta inválida do Banco Central em {url}") from exc

    @staticmethod
    def _empty_frame() -> pd.DataFrame:
        return pd.DataFrame(columns=["date", "value"])

    @staticmethod
    def _normalize_frame(frame: pd.DataFrame) -> pd.DataFrame:
        normalized = frame.dropna(subset=["date", "value"]).copy()
        normalized = normalized.assign(
            date=pd.to_datetime(normalized["date"], errors="coerce").dt.normalize(),
            value=pd.to_numeric(normalized["value"], errors="coerce"),
        )
        normalized = normalized.dropna(subset=["value"])
        normalized = normalized.drop_duplicates(subset=["date"], keep="last")
        normalized = normalized.sort_values("date").reset_index(drop=True)
        return normalized