from collections import defaultdict

from .synthetic_stream import generate_dataset


# ---------------------------------------------------------
# Metric calculation helpers
# ---------------------------------------------------------

def calculate_roas(revenue, spend):
    """Return Revenue / Ad Spend."""
    if spend <= 0:
        return 0.0

    return revenue / spend


def calculate_ctr(clicks, impressions):
    """Return Click Through Rate."""
    if impressions <= 0:
        return 0.0

    return clicks / impressions


def calculate_conversion_rate(conversions, clicks):
    """Return Conversion Rate."""
    if clicks <= 0:
        return 0.0

    return conversions / clicks


def calculate_cpa(spend, conversions):
    """Return Cost Per Acquisition."""
    if conversions <= 0:
        return 0.0

    return spend / conversions


def calculate_margin_percentage(selling_price, cost_price):
    """Return product margin as a percentage."""
    if selling_price <= 0:
        return 0.0

    return (selling_price - cost_price) / selling_price


def calculate_gross_profit(revenue, margin_percentage):
    """Return gross profit before advertising costs."""
    return revenue * margin_percentage


def calculate_ad_profit(gross_profit, ad_spend):
    """Return profit after advertising spend."""
    return gross_profit - ad_spend


# ---------------------------------------------------------
# Main analytics engine
# ---------------------------------------------------------

def calculate_campaign_metrics(dataset):
    """
    Combine advertising, sales, product and inventory data
    and calculate business metrics for every campaign.
    """

    advertising_data = dataset["advertising"]
    sales_data = dataset["sales"]
    products = dataset["products"]
    inventory = dataset["inventory"]

    # -----------------------------------------------------
    # Create lookup tables
    # -----------------------------------------------------

    product_lookup = {
        product.sku: product
        for product in products
    }

    inventory_lookup = {
        item.sku: item.available_units
        for item in inventory
    }

    # -----------------------------------------------------
    # Aggregate sales by SKU and date
    # -----------------------------------------------------

    sales_lookup = defaultdict(
        lambda: {
            "units_sold": 0,
            "revenue": 0.0,
        }
    )

    for sale in sales_data:

        key = (sale.sku, sale.date)

        sales_lookup[key]["units_sold"] += sale.units_sold
        sales_lookup[key]["revenue"] += sale.revenue

    # -----------------------------------------------------
    # Calculate metrics
    # -----------------------------------------------------

    results = []

    for ad in advertising_data:

        product = product_lookup.get(ad.sku)

        if product is None:
            continue

        sales = sales_lookup[
            (ad.sku, ad.date)
        ]

        revenue = sales["revenue"]
        units_sold = sales["units_sold"]

        margin_percentage = calculate_margin_percentage(
            product.selling_price,
            product.cost_price
        )

        gross_profit = calculate_gross_profit(
            revenue,
            margin_percentage
        )

        ad_profit = calculate_ad_profit(
            gross_profit,
            ad.spend
        )

        roas = calculate_roas(
            revenue,
            ad.spend
        )

        ctr = calculate_ctr(
            ad.clicks,
            ad.impressions
        )

        conversion_rate = calculate_conversion_rate(
            ad.conversions,
            ad.clicks
        )

        cpa = calculate_cpa(
            ad.spend,
            ad.conversions
        )

        inventory_units = inventory_lookup.get(
            ad.sku,
            0
        )

        # -------------------------------------------------
        # Inventory health
        # -------------------------------------------------

        if inventory_units <= 25:
            inventory_health = "CRITICAL"

        elif inventory_units <= 100:
            inventory_health = "LOW"

        elif inventory_units <= 300:
            inventory_health = "MEDIUM"

        else:
            inventory_health = "HEALTHY"

        # -------------------------------------------------
        # Store unified result
        # -------------------------------------------------

        results.append(
            {
                "campaign_id": ad.campaign_id,
                "platform": ad.platform,
                "sku": ad.sku,
                "date": ad.date,

                "spend": round(ad.spend, 2),
                "impressions": ad.impressions,
                "clicks": ad.clicks,
                "conversions": ad.conversions,

                "revenue": round(revenue, 2),
                "units_sold": units_sold,

                "selling_price": product.selling_price,
                "cost_price": product.cost_price,

                "margin_percentage": round(
                    margin_percentage * 100,
                    2
                ),

                "gross_profit": round(
                    gross_profit,
                    2
                ),

                "ad_profit": round(
                    ad_profit,
                    2
                ),

                "roas": round(
                    roas,
                    2
                ),

                "ctr": round(
                    ctr * 100,
                    2
                ),

                "conversion_rate": round(
                    conversion_rate * 100,
                    2
                ),

                "cpa": round(
                    cpa,
                    2
                ),

                "inventory": inventory_units,

                "inventory_health": inventory_health,
            }
        )

    return results


# ---------------------------------------------------------
# Campaign-level aggregation
# ---------------------------------------------------------

def aggregate_campaigns(metrics):
    """
    Combine daily metrics into one summary for each campaign.
    """

    campaigns = defaultdict(
        lambda: {
            "platform": "",
            "sku": "",

            "spend": 0.0,
            "revenue": 0.0,
            "impressions": 0,
            "clicks": 0,
            "conversions": 0,
            "units_sold": 0,

            "gross_profit": 0.0,
            "ad_profit": 0.0,

            "inventory": 0,
            "margin_percentage": 0.0,
        }
    )

    for row in metrics:

        campaign_id = row["campaign_id"]

        campaign = campaigns[campaign_id]

        campaign["platform"] = row["platform"]
        campaign["sku"] = row["sku"]

        campaign["spend"] += row["spend"]
        campaign["revenue"] += row["revenue"]

        campaign["impressions"] += row["impressions"]
        campaign["clicks"] += row["clicks"]
        campaign["conversions"] += row["conversions"]

        campaign["units_sold"] += row["units_sold"]

        campaign["gross_profit"] += row["gross_profit"]
        campaign["ad_profit"] += row["ad_profit"]

        campaign["inventory"] = row["inventory"]

        campaign["margin_percentage"] = (
            row["margin_percentage"]
        )

    # -----------------------------------------------------
    # Calculate final campaign metrics
    # -----------------------------------------------------

    results = []

    for campaign_id, campaign in campaigns.items():

        spend = campaign["spend"]
        revenue = campaign["revenue"]
        clicks = campaign["clicks"]
        impressions = campaign["impressions"]
        conversions = campaign["conversions"]

        results.append(
            {
                "campaign_id": campaign_id,
                "platform": campaign["platform"],
                "sku": campaign["sku"],

                "spend": round(spend, 2),
                "revenue": round(revenue, 2),

                "impressions": impressions,
                "clicks": clicks,
                "conversions": conversions,

                "units_sold": campaign["units_sold"],

                "margin_percentage": campaign[
                    "margin_percentage"
                ],

                "gross_profit": round(
                    campaign["gross_profit"],
                    2
                ),

                "ad_profit": round(
                    campaign["ad_profit"],
                    2
                ),

                "roas": round(
                    calculate_roas(
                        revenue,
                        spend
                    ),
                    2
                ),

                "ctr": round(
                    calculate_ctr(
                        clicks,
                        impressions
                    ) * 100,
                    2
                ),

                "conversion_rate": round(
                    calculate_conversion_rate(
                        conversions,
                        clicks
                    ) * 100,
                    2
                ),

                "cpa": round(
                    calculate_cpa(
                        spend,
                        conversions
                    ),
                    2
                ),

                "inventory": campaign["inventory"],

                "inventory_health": (
                    "CRITICAL"
                    if campaign["inventory"] <= 25
                    else "LOW"
                    if campaign["inventory"] <= 100
                    else "MEDIUM"
                    if campaign["inventory"] <= 300
                    else "HEALTHY"
                ),
            }
        )

    return results


# ---------------------------------------------------------
# Test the analytics engine
# ---------------------------------------------------------

if __name__ == "__main__":

    dataset = generate_dataset()

    daily_metrics = calculate_campaign_metrics(
        dataset
    )

    campaign_metrics = aggregate_campaigns(
        daily_metrics
    )

    print("\n========================================")
    print("       ATHENA ANALYTICS ENGINE")
    print("========================================\n")

    for campaign in campaign_metrics:

        print(
            f"Campaign: {campaign['campaign_id']}"
        )

        print(
            f"Platform: {campaign['platform']}"
        )

        print(
            f"SKU: {campaign['sku']}"
        )

        print(
            f"Spend: ₹{campaign['spend']:,.2f}"
        )

        print(
            f"Revenue: ₹{campaign['revenue']:,.2f}"
        )

        print(
            f"ROAS: {campaign['roas']}"
        )

        print(
            f"CTR: {campaign['ctr']}%"
        )

        print(
            f"Conversion Rate: "
            f"{campaign['conversion_rate']}%"
        )

        print(
            f"CPA: ₹{campaign['cpa']:,.2f}"
        )

        print(
            f"Margin: "
            f"{campaign['margin_percentage']}%"
        )

        print(
            f"Gross Profit: "
            f"₹{campaign['gross_profit']:,.2f}"
        )

        print(
            f"Ad Profit: "
            f"₹{campaign['ad_profit']:,.2f}"
        )

        print(
            f"Inventory: "
            f"{campaign['inventory']} units"
        )

        print(
            f"Inventory Health: "
            f"{campaign['inventory_health']}"
        )

        print("----------------------------------------")