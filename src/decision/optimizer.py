from src.ingestion.analytics import (
    calculate_campaign_metrics,
    aggregate_campaigns,
)
from src.ingestion.synthetic_stream import generate_dataset
from src.diagnostic.agent import diagnose_all_campaigns


# =========================================================
# Decision thresholds
# =========================================================

SCALE_ROAS_THRESHOLD = 4.0
SCALE_MARGIN_THRESHOLD = 40.0
SCALE_INVENTORY_THRESHOLD = 300

REDUCE_ROAS_THRESHOLD = 2.5
REDUCE_MARGIN_THRESHOLD = 20.0
REDUCE_INVENTORY_THRESHOLD = 100

CRITICAL_INVENTORY_THRESHOLD = 25


# =========================================================
# Opportunity Score
# =========================================================

def calculate_opportunity_score(campaign):
    """
    Calculate a 0-100 score representing how attractive
    a campaign is for additional advertising budget.
    """

    # -----------------------------------------------------
    # Advertising efficiency score
    # -----------------------------------------------------

    roas_score = min(
        campaign["roas"] / 6.0,
        1.0
    )

    # -----------------------------------------------------
    # Profitability score
    # -----------------------------------------------------

    margin_score = min(
        campaign["margin_percentage"] / 60.0,
        1.0
    )

    # -----------------------------------------------------
    # Inventory score
    # -----------------------------------------------------

    inventory = campaign["inventory"]

    if inventory <= CRITICAL_INVENTORY_THRESHOLD:
        inventory_score = 0.0

    elif inventory < REDUCE_INVENTORY_THRESHOLD:
        inventory_score = 0.25

    elif inventory < SCALE_INVENTORY_THRESHOLD:
        inventory_score = 0.60

    else:
        inventory_score = 1.0

    # -----------------------------------------------------
    # Conversion score
    # -----------------------------------------------------

    conversion_score = min(
        campaign["conversion_rate"] / 8.0,
        1.0
    )

    # -----------------------------------------------------
    # Profit score
    # -----------------------------------------------------

    profit_score = 1.0 if campaign["ad_profit"] > 0 else 0.0

    # -----------------------------------------------------
    # Weighted opportunity score
    # -----------------------------------------------------

    score = (
        roas_score * 0.30
        + margin_score * 0.25
        + inventory_score * 0.20
        + conversion_score * 0.15
        + profit_score * 0.10
    )

    return round(
        score * 100,
        2
    )


# =========================================================
# Determine action
# =========================================================

def determine_action(campaign, diagnosis):
    """
    Decide what action should be taken for a campaign.
    """

    roas = campaign["roas"]
    margin = campaign["margin_percentage"]
    inventory = campaign["inventory"]
    ad_profit = campaign["ad_profit"]

    severity = diagnosis["severity"]

    # -----------------------------------------------------
    # Critical inventory
    # -----------------------------------------------------

    if inventory <= CRITICAL_INVENTORY_THRESHOLD:

        return "PAUSE"

    # -----------------------------------------------------
    # Critical diagnostic issue
    # -----------------------------------------------------

    if severity == "CRITICAL":

        return "PAUSE"

    # -----------------------------------------------------
    # High severity performance problem
    # -----------------------------------------------------

    if severity == "HIGH":

        return "REDUCE"

    # -----------------------------------------------------
    # Clearly unprofitable campaign
    # -----------------------------------------------------

    if ad_profit < 0:

        return "REDUCE"

    # -----------------------------------------------------
    # Poor ROAS
    # -----------------------------------------------------

    if roas < REDUCE_ROAS_THRESHOLD:

        return "REDUCE"

    # -----------------------------------------------------
    # Low-margin product
    # -----------------------------------------------------

    if margin < REDUCE_MARGIN_THRESHOLD:

        return "REDUCE"

    # -----------------------------------------------------
    # Strong scaling opportunity
    # -----------------------------------------------------

    if (
        roas >= SCALE_ROAS_THRESHOLD
        and margin >= SCALE_MARGIN_THRESHOLD
        and inventory >= SCALE_INVENTORY_THRESHOLD
        and ad_profit > 0
    ):

        return "SCALE"

    # -----------------------------------------------------
    # Otherwise maintain
    # -----------------------------------------------------

    return "MAINTAIN"


# =========================================================
# Budget recommendation
# =========================================================

def calculate_budget_change(action, spend):
    """
    Calculate a suggested percentage change in budget.
    """

    if action == "SCALE":
        return round(spend * 0.25, 2)

    if action == "REDUCE":
        return round(spend * -0.20, 2)

    if action == "PAUSE":
        return round(spend * -1.00, 2)

    return 0.0


# =========================================================
# Build decisions
# =========================================================

def generate_decisions(dataset):
    """
    Generate decisions for every campaign.
    """

    daily_metrics = calculate_campaign_metrics(
        dataset
    )

    campaign_metrics = aggregate_campaigns(
        daily_metrics
    )

    diagnoses = diagnose_all_campaigns(
        dataset
    )

    diagnosis_lookup = {
        diagnosis["campaign_id"]: diagnosis
        for diagnosis in diagnoses
    }

    decisions = []

    for campaign in campaign_metrics:

        campaign_id = campaign["campaign_id"]

        diagnosis = diagnosis_lookup[
            campaign_id
        ]

        opportunity_score = (
            calculate_opportunity_score(
                campaign
            )
        )

        action = determine_action(
            campaign,
            diagnosis
        )

        budget_change = calculate_budget_change(
            action,
            campaign["spend"]
        )

        decisions.append(
            {
                "campaign_id": campaign_id,
                "platform": campaign["platform"],
                "sku": campaign["sku"],

                "action": action,

                "opportunity_score": opportunity_score,

                "current_spend": round(
                    campaign["spend"],
                    2
                ),

                "recommended_budget_change": budget_change,

                "recommended_spend": round(
                    campaign["spend"]
                    + budget_change,
                    2
                ),

                "roas": campaign["roas"],

                "margin_percentage": campaign[
                    "margin_percentage"
                ],

                "ad_profit": campaign[
                    "ad_profit"
                ],

                "inventory": campaign[
                    "inventory"
                ],

                "inventory_health": campaign[
                    "inventory_health"
                ],

                "diagnostic_severity": diagnosis[
                    "severity"
                ],

                "primary_drivers": diagnosis[
                    "primary_drivers"
                ],
            }
        )

    # Highest opportunity first
    decisions.sort(
        key=lambda x: x["opportunity_score"],
        reverse=True
    )

    return decisions


# =========================================================
# Test Decision Engine
# =========================================================

if __name__ == "__main__":

    dataset = generate_dataset()

    decisions = generate_decisions(
        dataset
    )

    print("\n")
    print("=" * 70)
    print("                 ATHENA DECISION ENGINE")
    print("=" * 70)

    for decision in decisions:

        print("\n")

        print(
            f"Campaign: "
            f"{decision['campaign_id']}"
        )

        print(
            f"Platform: "
            f"{decision['platform']}"
        )

        print(
            f"SKU: "
            f"{decision['sku']}"
        )

        print(
            f"Opportunity Score: "
            f"{decision['opportunity_score']}/100"
        )

        print(
            f"Action: "
            f"{decision['action']}"
        )

        print(
            f"Current Spend: "
            f"₹{decision['current_spend']:,.2f}"
        )

        print(
            f"Recommended Budget Change: "
            f"₹{decision['recommended_budget_change']:,.2f}"
        )

        print(
            f"Recommended Spend: "
            f"₹{decision['recommended_spend']:,.2f}"
        )

        print(
            f"ROAS: "
            f"{decision['roas']}"
        )

        print(
            f"Margin: "
            f"{decision['margin_percentage']}%"
        )

        print(
            f"Ad Profit: "
            f"₹{decision['ad_profit']:,.2f}"
        )

        print(
            f"Inventory: "
            f"{decision['inventory']} units"
        )

        print(
            f"Inventory Health: "
            f"{decision['inventory_health']}"
        )

        print(
            f"Diagnostic Severity: "
            f"{decision['diagnostic_severity']}"
        )

        print(
            f"Primary Drivers: "
            f"{', '.join(decision['primary_drivers'])}"
        )

        print("-" * 70)