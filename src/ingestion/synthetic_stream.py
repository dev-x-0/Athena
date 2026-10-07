from datetime import date, timedelta
import random

from .schema import (
    AdvertisingData,
    SalesData,
    ProductData,
    InventoryData,
)


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

RANDOM_SEED = 42
DAYS = 14

random.seed(RANDOM_SEED)


# ---------------------------------------------------------
# Products
# ---------------------------------------------------------

PRODUCTS = [
    {
        "sku": "SKU001",
        "product_name": "Smart Bottle",
        "selling_price": 1500.0,
        "cost_price": 675.0,
        "initial_inventory": 900,
    },
    {
        "sku": "SKU002",
        "product_name": "Wireless Earbuds",
        "selling_price": 3000.0,
        "cost_price": 1200.0,
        "initial_inventory": 1200,
    },
    {
        "sku": "SKU003",
        "product_name": "Travel Backpack",
        "selling_price": 2500.0,
        "cost_price": 2200.0,
        "initial_inventory": 500,
    },
    {
        "sku": "SKU004",
        "product_name": "Fitness Band",
        "selling_price": 2000.0,
        "cost_price": 900.0,
        "initial_inventory": 700,
    },
]


CAMPAIGNS = [
    {
        "campaign_id": "C001",
        "platform": "Meta",
        "sku": "SKU001",
        "base_spend": 9000,
        "ctr": 0.045,
        "conversion_rate": 0.055,
    },
    {
        "campaign_id": "C002",
        "platform": "Google",
        "sku": "SKU002",
        "base_spend": 12000,
        "ctr": 0.060,
        "conversion_rate": 0.070,
    },
    {
        "campaign_id": "C003",
        "platform": "TikTok",
        "sku": "SKU003",
        "base_spend": 10000,
        "ctr": 0.050,
        "conversion_rate": 0.045,
    },
    {
        "campaign_id": "C004",
        "platform": "Meta",
        "sku": "SKU004",
        "base_spend": 8000,
        "ctr": 0.040,
        "conversion_rate": 0.050,
    },
]


# ---------------------------------------------------------
# Product generation
# ---------------------------------------------------------

def generate_products():
    products = []

    for product in PRODUCTS:
        products.append(
            ProductData(
                sku=product["sku"],
                product_name=product["product_name"],
                selling_price=product["selling_price"],
                cost_price=product["cost_price"],
            )
        )

    return products


# ---------------------------------------------------------
# Inventory generation
# ---------------------------------------------------------

def generate_inventory():
    inventory = []

    for product in PRODUCTS:
        inventory.append(
            InventoryData(
                sku=product["sku"],
                available_units=product["initial_inventory"],
            )
        )

    return inventory


# ---------------------------------------------------------
# Advertising data generation
# ---------------------------------------------------------

def generate_advertising_data(days=DAYS):
    advertising_data = []

    start_date = date.today() - timedelta(days=days - 1)

    for day_number in range(days):

        current_date = start_date + timedelta(days=day_number)

        for campaign in CAMPAIGNS:

            # Normal daily variation
            spend = campaign["base_spend"] * random.uniform(0.90, 1.10)

            ctr = campaign["ctr"] * random.uniform(0.90, 1.10)

            conversion_rate = (
                campaign["conversion_rate"]
                * random.uniform(0.90, 1.10)
            )

            # -------------------------------------------------
            # Scenario 1:
            # C003 experiences a performance crash
            # during the final 4 days.
            # -------------------------------------------------

            if (
                campaign["campaign_id"] == "C003"
                and day_number >= days - 4
            ):
                ctr *= 0.80
                conversion_rate *= 0.65

            # -------------------------------------------------
            # Calculate impressions / clicks / conversions
            # -------------------------------------------------

            estimated_cpc = random.uniform(8, 14)

            clicks = max(
                1,
                int(spend / estimated_cpc)
            )

            impressions = max(
                clicks,
                int(clicks / ctr)
            )

            conversions = max(
                0,
                int(clicks * conversion_rate)
            )

            advertising_data.append(
                AdvertisingData(
                    campaign_id=campaign["campaign_id"],
                    platform=campaign["platform"],
                    sku=campaign["sku"],
                    date=current_date,
                    spend=round(spend, 2),
                    impressions=impressions,
                    clicks=clicks,
                    conversions=conversions,
                )
            )

    return advertising_data


# ---------------------------------------------------------
# Sales data generation
# ---------------------------------------------------------

def generate_sales_data(advertising_data, products):
    sales_data = []

    product_lookup = {
        product.sku: product
        for product in products
    }

    order_counter = 1

    for ad in advertising_data:

        product = product_lookup[ad.sku]

        # Base conversion from advertising
        units_sold = ad.conversions

        # Small amount of organic / additional sales
        organic_sales = random.randint(2, 10)

        units_sold += organic_sales

        revenue = units_sold * product.selling_price

        sales_data.append(
            SalesData(
                order_id=f"ORD{order_counter:05d}",
                sku=ad.sku,
                date=ad.date,
                units_sold=units_sold,
                revenue=round(revenue, 2),
            )
        )

        order_counter += 1

    return sales_data


# ---------------------------------------------------------
# Inventory calculation
# ---------------------------------------------------------

def calculate_inventory(products, sales_data):
    inventory = []

    total_sales = {}

    for sale in sales_data:
        total_sales[sale.sku] = (
            total_sales.get(sale.sku, 0)
            + sale.units_sold
        )

    for product in products:

        remaining_inventory = (
            PRODUCTS[
                next(
                    i
                    for i, p in enumerate(PRODUCTS)
                    if p["sku"] == product.sku
                )
            ]["initial_inventory"]
            - total_sales.get(product.sku, 0)
        )

        # Intentionally create an inventory-risk scenario
        if product.sku == "SKU003":
            remaining_inventory = min(
                remaining_inventory,
                70
            )

        remaining_inventory = max(
            0,
            remaining_inventory
        )

        inventory.append(
            InventoryData(
                sku=product.sku,
                available_units=remaining_inventory,
            )
        )

    return inventory


# ---------------------------------------------------------
# Main synthetic stream
# ---------------------------------------------------------

def generate_dataset(days=DAYS):
    products = generate_products()

    advertising_data = generate_advertising_data(days)

    sales_data = generate_sales_data(
        advertising_data,
        products
    )

    inventory = calculate_inventory(
        products,
        sales_data
    )

    return {
        "advertising": advertising_data,
        "sales": sales_data,
        "products": products,
        "inventory": inventory,
    }


# ---------------------------------------------------------
# Quick test
# ---------------------------------------------------------

if __name__ == "__main__":

    dataset = generate_dataset()

    print("\n=== ATHENA SYNTHETIC DATA ===\n")

    print(
        f"Advertising records: "
        f"{len(dataset['advertising'])}"
    )

    print(
        f"Sales records: "
        f"{len(dataset['sales'])}"
    )

    print(
        f"Products: "
        f"{len(dataset['products'])}"
    )

    print(
        f"Inventory records: "
        f"{len(dataset['inventory'])}"
    )

    print("\n=== SAMPLE ADVERTISING RECORD ===\n")
    print(dataset["advertising"][0])

    print("\n=== PRODUCTS ===\n")

    for product in dataset["products"]:
        print(product)

    print("\n=== INVENTORY ===\n")

    for item in dataset["inventory"]:
        print(item)