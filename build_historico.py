from taxa_selic.bcb import BCBClient
from taxa_selic.service import EconomicDataService
from taxa_selic.storage import SeriesStorage


def main() -> None:
    service = EconomicDataService(client=BCBClient(), storage=SeriesStorage())
    for slug in ["selic-diaria", "meta-selic", "cdi", "ipca", "igpm", "dolar-ptax", "euro-ptax"]:
        payload = service.update_series(slug)
        print(
            f"✅ {payload['series']['title']}: "
            f"{payload['stored_rows']} linhas armazenadas"
        )
    service.export_legacy_selic()


if __name__ == "__main__":
    main()