from src.ingestion.schema import AdvertisingData


ad = AdvertisingData(
    campaign_id="C001",
    platform="Meta",
    sku="SKU001",
    date="2026-10-07",
    spend=5000,
    impressions=100000,
    clicks=4000,
    conversions=200
)

print(ad)