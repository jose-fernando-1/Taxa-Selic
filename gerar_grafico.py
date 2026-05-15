from taxa_selic.bcb import BCBClient
from taxa_selic.charts import build_series_figure
from taxa_selic.service import EconomicDataService
from taxa_selic.storage import SeriesStorage


def main() -> None:
    service = EconomicDataService(client=BCBClient(), storage=SeriesStorage())
    service.update_series("selic-diaria")
    frame = service.storage.load("selic-diaria")
    figure = build_series_figure(service.get_definition("selic-diaria"), frame)
    figure.write_html("grafico_selic_periodos.html")
    print("✅ Gráfico da Selic gerado em grafico_selic_periodos.html")


if __name__ == "__main__":
    main()
