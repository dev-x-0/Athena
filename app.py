from collections import defaultdict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.ingestion.synthetic_stream import (
    generate_dataset,
)

from src.ingestion.analytics import (
    calculate_campaign_metrics,
    aggregate_campaigns,
)

from src.diagnostic.agent import (
    diagnose_all_campaigns,
)

from src.decision.optimizer import (
    generate_decisions,
)

from src.execution.executor import (
    execute_decisions,
)

from src.execution.feedback import (
    run_feedback_loop,
)

from src.decision.reasoning import (
    generate_all_reasoning,
)


# =========================================================
# FASTAPI APP
# =========================================================

app = FastAPI(
    title="Athena API",
    description="Autonomous D2C Advertising Intelligence Engine",
    version="1.0.0",
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# ATHENA PIPELINE
# =========================================================

def run_athena():

    dataset = generate_dataset()

    # -----------------------------------------------------
    # Analytics
    # -----------------------------------------------------

    daily_metrics = calculate_campaign_metrics(
        dataset
    )

    campaigns = aggregate_campaigns(
        daily_metrics
    )

    # -----------------------------------------------------
    # Diagnostics
    # -----------------------------------------------------

    diagnoses = diagnose_all_campaigns(
        dataset
    )

    # -----------------------------------------------------
    # Decisions
    # -----------------------------------------------------

    decisions = generate_decisions(
        dataset
    )

    # -----------------------------------------------------
    # Execution
    # -----------------------------------------------------

    execution_results = execute_decisions(
        decisions
    )

    # -----------------------------------------------------
    # Feedback
    # -----------------------------------------------------

    feedback_results = run_feedback_loop(
        decisions,
        execution_results,
    )

    # -----------------------------------------------------
    # AI reasoning
    # -----------------------------------------------------

    reasoning_results = generate_all_reasoning(
        decisions,
        execution_results,
        feedback_results,
    )

    return {
        "dataset": dataset,
        "daily_metrics": daily_metrics,
        "campaigns": campaigns,
        "diagnoses": diagnoses,
        "decisions": decisions,
        "execution": execution_results,
        "feedback": feedback_results,
        "reasoning": reasoning_results,
    }


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/")
def root():

    return {
        "status": "online",
        "service": "Athena API",
    }


# =========================================================
# FULL DASHBOARD DATA
# =========================================================

@app.get("/api/dashboard")
def dashboard():

    result = run_athena()

    dataset = result["dataset"]
    campaigns = result["campaigns"]
    diagnoses = result["diagnoses"]
    decisions = result["decisions"]
    execution = result["execution"]
    feedback = result["feedback"]
    reasoning = result["reasoning"]
    daily_metrics = result["daily_metrics"]

    # -----------------------------------------------------
    # Campaign lookup
    # -----------------------------------------------------

    decision_lookup = {
        item["campaign_id"]: item
        for item in decisions
    }

    diagnosis_lookup = {
        item["campaign_id"]: item
        for item in diagnoses
    }

    reasoning_lookup = {
        item["campaign_id"]: item
        for item in reasoning
    }

    execution_lookup = {
        item["campaign_id"]: item
        for item in execution
    }

    # -----------------------------------------------------
    # Campaigns for frontend
    # -----------------------------------------------------

    frontend_campaigns = []

    for campaign in campaigns:

        campaign_id = campaign[
            "campaign_id"
        ]

        decision = decision_lookup.get(
            campaign_id,
            {}
        )

        frontend_campaigns.append(
            {
                "id": campaign_id,

                "name": campaign_id,

                "platform": campaign[
                    "platform"
                ],

                "sku": campaign[
                    "sku"
                ],

                "spend": campaign[
                    "spend"
                ],

                "revenue": campaign[
                    "revenue"
                ],

                "roas": campaign[
                    "roas"
                ],

                "conv": campaign[
                    "conversions"
                ],

                "status": decision.get(
                    "action",
                    "MAINTAIN"
                ),

                "opportunity_score": decision.get(
                    "opportunity_score",
                    0
                ),

                "margin_percentage": campaign[
                    "margin_percentage"
                ],

                "inventory": campaign[
                    "inventory"
                ],

                "ad_profit": campaign[
                    "ad_profit"
                ],
            }
        )

    # -----------------------------------------------------
    # Product summaries
    # -----------------------------------------------------

    product_lookup = {
        product.sku: product
        for product in dataset["products"]
    }

    inventory_lookup = {
        item.sku: item.available_units
        for item in dataset["inventory"]
    }

    product_metrics = defaultdict(
        lambda: {
            "spend": 0.0,
            "revenue": 0.0,
            "conversions": 0,
        }
    )

    for row in daily_metrics:

        sku = row["sku"]

        product_metrics[sku][
            "spend"
        ] += row["spend"]

        product_metrics[sku][
            "revenue"
        ] += row["revenue"]

        product_metrics[sku][
            "conversions"
        ] += row["conversions"]

    frontend_products = []

    for sku, product in product_lookup.items():

        metrics = product_metrics[sku]

        margin = (
            (
                product.selling_price
                - product.cost_price
            )
            / product.selling_price
            * 100
            if product.selling_price > 0
            else 0
        )

        spend = metrics["spend"]
        revenue = metrics["revenue"]

        roas = (
            revenue / spend
            if spend > 0
            else 0
        )

        inventory = inventory_lookup.get(
            sku,
            0
        )

        if inventory <= 25:
            status = "Critical"

        elif inventory <= 100:
            status = "Low stock"

        elif margin < 20:
            status = "Low margin"

        else:
            status = "Healthy"

        frontend_products.append(
            [
                sku,
                product.product_name,
                f"{margin:.1f}%",
                str(inventory),
                f"₹{spend / 1000:.1f}K",
                f"₹{revenue / 1000:.1f}K",
                f"{roas:.2f}x",
                status,
            ]
        )

    # -----------------------------------------------------
    # Findings
    # -----------------------------------------------------

    findings = []

    for diagnosis in diagnoses:

        campaign_id = diagnosis[
            "campaign_id"
        ]

        decision = decision_lookup.get(
            campaign_id,
            {}
        )

        for finding in diagnosis[
            "findings"
        ]:

            finding_type = finding[
                "type"
            ]

            severity = finding[
                "severity"
            ]

            if severity == "CRITICAL":
                ui_type = "critical"

            elif severity == "HIGH":
                ui_type = "warning"

            elif finding_type == "LOW_MARGIN":
                ui_type = "warning"

            else:
                ui_type = "observation"

            findings.append(
                {
                    "type": ui_type,

                    "title": (
                        f"{campaign_id}: "
                        f"{finding_type.replace('_', ' ').title()}"
                    ),

                    "body": finding[
                        "message"
                    ],

                    "metric": (
                        f"ROAS "
                        f"{diagnosis['current_metrics']['roas']:.2f}x · "
                        f"Inventory "
                        f"{diagnosis['current_metrics']['inventory']}"
                    ),

                    "action": decision.get(
                        "action",
                        "Review"
                    ),
                }
            )

    # -----------------------------------------------------
    # Performance trend
    # -----------------------------------------------------

    trend_data = defaultdict(
        lambda: {
            "spend": 0.0,
            "revenue": 0.0,
        }
    )

    for row in daily_metrics:

        date = row["date"]

        trend_data[date][
            "spend"
        ] += row["spend"]

        trend_data[date][
            "revenue"
        ] += row["revenue"]

    trend = []

    for date in sorted(
        trend_data.keys()
    ):

        trend.append(
            {
                "d": date.strftime(
                    "%b %d"
                ),

                "spend": round(
                    trend_data[date]["spend"],
                    2
                ),

                "revenue": round(
                    trend_data[date]["revenue"],
                    2
                ),
            }
        )

    # -----------------------------------------------------
    # Summary KPIs
    # -----------------------------------------------------

    total_spend = sum(
        campaign["spend"]
        for campaign in campaigns
    )

    total_revenue = sum(
        campaign["revenue"]
        for campaign in campaigns
    )

    total_profit = sum(
        campaign["ad_profit"]
        for campaign in campaigns
    )

    overall_roas = (
        total_revenue / total_spend
        if total_spend > 0
        else 0
    )

    # -----------------------------------------------------
    # Final response
    # -----------------------------------------------------

    return {
        "summary": {
            "ad_spend": round(
                total_spend,
                2
            ),

            "revenue": round(
                total_revenue,
                2
            ),

            "roas": round(
                overall_roas,
                2
            ),

            "contribution": round(
                total_profit,
                2
            ),

            "campaign_count": len(
                campaigns
            ),
        },

        "campaigns": frontend_campaigns,

        "products": frontend_products,

        "findings": findings,

        "trend": trend,

        "decisions": decisions,

        "execution": execution,

        "feedback": feedback,

        "reasoning": reasoning,
    }


# =========================================================
# INDIVIDUAL ENDPOINTS
# =========================================================

@app.get("/api/campaigns")
def campaigns():

    return dashboard()["campaigns"]


@app.get("/api/products")
def products():

    return dashboard()["products"]


@app.get("/api/insights")
def insights():

    return dashboard()["findings"]


@app.get("/api/health")
def health():

    return {
        "status": "healthy",
        "engine": "Athena",
    }