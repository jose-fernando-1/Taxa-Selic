from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date


@dataclass(frozen=True)
class SeriesDefinition:
    key: str
    slug: str
    title: str
    source: str
    frequency: str
    unit: str
    default_start: date
    sgs_code: int | None = None
    ptax_symbol: str | None = None
    description: str = ""

    def to_dict(self) -> dict:
        payload = asdict(self)
        payload["default_start"] = self.default_start.isoformat()
        return payload


SERIES_CATALOG: dict[str, SeriesDefinition] = {
    "selic_diaria": SeriesDefinition(
        key="selic_diaria",
        slug="selic-diaria",
        title="Selic diária",
        source="sgs",
        frequency="daily",
        unit="% a.d.",
        default_start=date(1986, 6, 4),
        sgs_code=11,
        description="Taxa Selic efetiva diária via SGS.",
    ),
    "meta_selic": SeriesDefinition(
        key="meta_selic",
        slug="meta-selic",
        title="Meta Selic",
        source="sgs",
        frequency="daily",
        unit="% a.a.",
        default_start=date(1999, 3, 5),
        sgs_code=432,
        description="Meta da taxa Selic definida pelo Copom.",
    ),
    "cdi": SeriesDefinition(
        key="cdi",
        slug="cdi",
        title="CDI",
        source="sgs",
        frequency="daily",
        unit="% a.d.",
        default_start=date(1986, 1, 2),
        sgs_code=12,
        description="Taxa DI diária via SGS.",
    ),
    "ipca": SeriesDefinition(
        key="ipca",
        slug="ipca",
        title="IPCA",
        source="sgs",
        frequency="monthly",
        unit="% a.m.",
        default_start=date(1980, 1, 1),
        sgs_code=433,
        description="Índice Nacional de Preços ao Consumidor Amplo.",
    ),
    "igpm": SeriesDefinition(
        key="igpm",
        slug="igpm",
        title="IGP-M",
        source="sgs",
        frequency="monthly",
        unit="% a.m.",
        default_start=date(1989, 6, 1),
        sgs_code=189,
        description="Índice Geral de Preços do Mercado.",
    ),
    "dolar_ptax": SeriesDefinition(
        key="dolar_ptax",
        slug="dolar-ptax",
        title="Dólar PTAX",
        source="ptax",
        frequency="daily",
        unit="BRL",
        default_start=date(1994, 7, 1),
        ptax_symbol="USD",
        description="Cotação oficial PTAX de venda do dólar.",
    ),
    "euro_ptax": SeriesDefinition(
        key="euro_ptax",
        slug="euro-ptax",
        title="Euro PTAX",
        source="ptax",
        frequency="daily",
        unit="BRL",
        default_start=date(1999, 1, 4),
        ptax_symbol="EUR",
        description="Cotação oficial PTAX de venda do euro.",
    ),
}

SERIES_BY_SLUG = {definition.slug: definition for definition in SERIES_CATALOG.values()}