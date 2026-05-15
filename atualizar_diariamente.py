from taxa_selic.charts import build_series_figure
from taxa_selic.service import EconomicDataService
from taxa_selic.storage import SeriesStorage
from taxa_selic.bcb import BCBClient


def main() -> None:
    service = EconomicDataService(client=BCBClient(), storage=SeriesStorage())
    updates = service.update_all()
    service.export_legacy_selic()

    selic = service.get_series("selic-diaria")
    frame = service.storage.load("selic-diaria")
    figure = build_series_figure(service.get_definition("selic-diaria"), frame)
    figure.write_html("grafico_selic_periodos.html")

    print(f"✅ Atualização concluída para {len(updates)} séries")
    if selic["latest"]:
        print(
            "📌 Último valor Selic: "
            f"{selic['latest']['value']} em {selic['latest']['date']}"
        )


if __name__ == "__main__":
    main()