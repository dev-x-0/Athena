from src.ingestion.analytics import (
    calculate_campaign_metrics,
    aggregate_campaigns,
)
from src.ingestion.synthetic_stream import generate_dataset


# =========================================================
# Diagnostic thresholds
# =========================================================

ROAS_DROP_THRESHOLD = 0.20
CONVERSION_DROP_THRESHOLD = 0.20
CPA_INCREASE_THRESHOLD = 0.20

LOW_ROAS_THRESHOLD = 2.0
LOW_MARGIN_THRESHOLD = 20.0

LOW_INVENTORY_THRESHOLD = 100
CRITICAL_INVENTORY_THRESHOLD = 25


# =========================================================
# Helper functions
# =========================================================

def percentage_change(current, baseline):
    """
    Calculate percentage change from baseline to current.
    """

    if baseline == 0:
        return 0.0

    return (current - baseline) / baseline


def average(values):
    """
    Calculate a simple average.
    """

    if not values:
        return 0.0

    return sum(values) / len(values)


# =========================================================
# Calculate historical baselines
# =========================================================

def calculate_baselines(daily_metrics):
    """
    Calculate historical average performance for each campaign.
    """

    campaign_history = {}

    for row in daily_metrics:

        campaign_id = row["campaign_id"]

        if campaign_id not in campaign_history:
            campaign_history[campaign_id] = {
                "roas": [],
                "conversion_rate": [],
                "cpa": [],
            }

        campaign_history[campaign_id]["roas"].append(
            row["roas"]
        )

        campaign_history[campaign_id]["conversion_rate"].append(
            row["conversion_rate"]
        )

        campaign_history[campaign_id]["cpa"].append(
            row["cpa"]
        )

    baselines = {}

    for campaign_id, history in campaign_history.items():

        baselines[campaign_id] = {
            "roas": average(history["roas"]),
            "conversion_rate": average(
                history["conversion_rate"]
            ),
            "cpa": average(history["cpa"]),
        }

    return baselines


# =========================================================
# Diagnose a single campaign
# =========================================================

def diagnose_campaign(campaign, baseline):
    """
    Identify anomalies and likely causes for a campaign.
    """

    findings = []
    severity = "NORMAL"

    current_roas = campaign["roas"]
    current_conversion_rate = campaign["conversion_rate"]
    current_cpa = campaign["cpa"]

    baseline_roas = baseline["roas"]
    baseline_conversion_rate = baseline[
        "conversion_rate"
    ]
    baseline_cpa = baseline["cpa"]

    # -----------------------------------------------------
    # ROAS analysis
    # -----------------------------------------------------

    roas_change = percentage_change(
        current_roas,
        baseline_roas
    )

    if roas_change <= -ROAS_DROP_THRESHOLD:

        findings.append(
            {
                "type": "ROAS_DROP",
                "severity": "HIGH",
                "message": (
                    f"ROAS dropped by "
                    f"{abs(roas_change) * 100:.1f}% "
                    f"from its historical baseline."
                ),
                "impact": abs(roas_change),
            }
        )

        severity = "HIGH"

    # -----------------------------------------------------
    # Conversion rate analysis
    # -----------------------------------------------------

    conversion_change = percentage_change(
        current_conversion_rate,
        baseline_conversion_rate
    )

    if conversion_change <= -CONVERSION_DROP_THRESHOLD:

        findings.append(
            {
                "type": "CONVERSION_DROP",
                "severity": "HIGH",
                "message": (
                    f"Conversion rate dropped by "
                    f"{abs(conversion_change) * 100:.1f}%."
                ),
                "impact": abs(conversion_change),
            }
        )

        severity = "HIGH"

    # -----------------------------------------------------
    # CPA analysis
    # -----------------------------------------------------

    if baseline_cpa > 0:

        cpa_change = percentage_change(
            current_cpa,
            baseline_cpa
        )

        if cpa_change >= CPA_INCREASE_THRESHOLD:

            findings.append(
                {
                    "type": "CPA_INCREASE",
                    "severity": "MEDIUM",
                    "message": (
                        f"CPA increased by "
                        f"{cpa_change * 100:.1f}%."
                    ),
                    "impact": cpa_change,
                }
            )

            if severity == "NORMAL":
                severity = "MEDIUM"

    # -----------------------------------------------------
    # Profitability analysis
    # -----------------------------------------------------

    if campaign["roas"] < LOW_ROAS_THRESHOLD:

        findings.append(
            {
                "type": "LOW_ROAS",
                "severity": "HIGH",
                "message": (
                    f"ROAS is only "
                    f"{campaign['roas']:.2f}, "
                    f"below the minimum target."
                ),
                "impact": (
                    LOW_ROAS_THRESHOLD
                    - campaign["roas"]
                ),
            }
        )

        severity = "HIGH"

    # -----------------------------------------------------
    # Margin analysis
    # -----------------------------------------------------

    if campaign["margin_percentage"] < LOW_MARGIN_THRESHOLD:

        findings.append(
            {
                "type": "LOW_MARGIN",
                "severity": "MEDIUM",
                "message": (
                    f"Product margin is only "
                    f"{campaign['margin_percentage']:.1f}%."
                ),
                "impact": (
                    LOW_MARGIN_THRESHOLD
                    - campaign["margin_percentage"]
                ),
            }
        )

        if severity == "NORMAL":
            severity = "MEDIUM"

    # -----------------------------------------------------
    # Inventory analysis
    # -----------------------------------------------------

    inventory = campaign["inventory"]

    if inventory <= CRITICAL_INVENTORY_THRESHOLD:

        findings.append(
            {
                "type": "CRITICAL_INVENTORY",
                "severity": "CRITICAL",
                "message": (
                    f"Inventory is critically low "
                    f"at only {inventory} units."
                ),
                "impact": (
                    CRITICAL_INVENTORY_THRESHOLD
                    - inventory
                ),
            }
        )

        severity = "CRITICAL"

    elif inventory <= LOW_INVENTORY_THRESHOLD:

        findings.append(
            {
                "type": "LOW_INVENTORY",
                "severity": "HIGH",
                "message": (
                    f"Inventory is low at "
                    f"{inventory} units."
                ),
                "impact": (
                    LOW_INVENTORY_THRESHOLD
                    - inventory
                ),
            }
        )

        if severity != "CRITICAL":
            severity = "HIGH"

    # -----------------------------------------------------
    # Rank findings
    # -----------------------------------------------------

    findings.sort(
        key=lambda item: item["impact"],
        reverse=True
    )

    # -----------------------------------------------------
    # Determine primary drivers
    # -----------------------------------------------------

    primary_drivers = []

    for finding in findings[:3]:

        primary_drivers.append(
            finding["type"]
        )

    # -----------------------------------------------------
    # Final diagnosis
    # -----------------------------------------------------

    if not findings:

        summary = (
            "Campaign performance is within "
            "normal operating ranges."
        )

    else:

        summary = (
            f"{len(findings)} performance issue(s) "
            f"detected. Primary drivers: "
            f"{', '.join(primary_drivers)}."
        )

    return {
        "campaign_id": campaign["campaign_id"],
        "platform": campaign["platform"],
        "sku": campaign["sku"],

        "severity": severity,

        "summary": summary,

        "primary_drivers": primary_drivers,

        "findings": findings,

        "current_metrics": {
            "roas": campaign["roas"],
            "conversion_rate": campaign[
                "conversion_rate"
            ],
            "cpa": campaign["cpa"],
            "margin_percentage": campaign[
                "margin_percentage"
            ],
            "inventory": campaign["inventory"],
            "ad_profit": campaign["ad_profit"],
        },

        "baseline_metrics": {
            "roas": round(
                baseline["roas"],
                2
            ),
            "conversion_rate": round(
                baseline["conversion_rate"],
                2
            ),
            "cpa": round(
                baseline["cpa"],
                2
            ),
        },
    }


# =========================================================
# Diagnose all campaigns
# =========================================================

def diagnose_all_campaigns(dataset):
    """
    Run the diagnostic engine across every campaign.
    """

    daily_metrics = calculate_campaign_metrics(
        dataset
    )

    campaign_metrics = aggregate_campaigns(
        daily_metrics
    )

    baselines = calculate_baselines(
        daily_metrics
    )

    diagnoses = []

    for campaign in campaign_metrics:

        campaign_id = campaign["campaign_id"]

        baseline = baselines[campaign_id]

        diagnosis = diagnose_campaign(
            campaign,
            baseline
        )

        diagnoses.append(diagnosis)

    return diagnoses


# =========================================================
# Test diagnostic engine
# =========================================================

if __name__ == "__main__":

    dataset = generate_dataset()

    diagnoses = diagnose_all_campaigns(
        dataset
    )

    print("\n")
    print("=" * 60)
    print("             ATHENA DIAGNOSTIC ENGINE")
    print("=" * 60)

    for diagnosis in diagnoses:

        print("\n")
        print(
            f"Campaign: "
            f"{diagnosis['campaign_id']}"
        )

        print(
            f"Platform: "
            f"{diagnosis['platform']}"
        )

        print(
            f"SKU: "
            f"{diagnosis['sku']}"
        )

        print(
            f"Severity: "
            f"{diagnosis['severity']}"
        )

        print(
            f"\nDiagnosis:"
        )

        print(
            diagnosis["summary"]
        )

        print(
            "\nPrimary Drivers:"
        )

        for driver in diagnosis[
            "primary_drivers"
        ]:

            print(
                f"  - {driver}"
            )

        print(
            "\nFindings:"
        )

        for finding in diagnosis["findings"]:

            print(
                f"  [{finding['severity']}] "
                f"{finding['message']}"
            )

        print("\n" + "-" * 60)