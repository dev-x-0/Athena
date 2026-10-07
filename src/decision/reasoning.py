import os
import json

from src.ingestion.synthetic_stream import generate_dataset
from src.decision.optimizer import generate_decisions
from src.execution.executor import execute_decisions
from src.execution.feedback import run_feedback_loop


# =========================================================
# Build Reasoning Context
# =========================================================

def build_reasoning_context(
    decision,
    execution_result,
    feedback
):
    """
    Convert Athena's structured decision data into a
    compact context that an LLM can reason about.
    """

    return {
        "campaign": decision["campaign_id"],
        "platform": decision["platform"],
        "sku": decision["sku"],

        "action": decision["action"],

        "opportunity_score": decision[
            "opportunity_score"
        ],

        "current_spend": decision[
            "current_spend"
        ],

        "recommended_spend": decision[
            "recommended_spend"
        ],

        "roas": decision["roas"],

        "margin_percentage": decision[
            "margin_percentage"
        ],

        "ad_profit": decision[
            "ad_profit"
        ],

        "inventory": decision[
            "inventory"
        ],

        "inventory_health": decision[
            "inventory_health"
        ],

        "diagnostic_severity": decision[
            "diagnostic_severity"
        ],

        "primary_drivers": decision[
            "primary_drivers"
        ],

        "execution_status": execution_result[
            "status"
        ],

        "feedback_outcome": feedback[
            "outcome"
        ],

        "learning_signal": feedback[
            "learning_signal"
        ],
    }


# =========================================================
# Rule-Based Reasoning Fallback
# =========================================================

def generate_reasoning(context):
    """
    Generate an explanation without requiring an external
    LLM API.

    This acts as a reliable fallback for the hackathon demo.
    """

    action = context["action"]

    campaign = context["campaign"]

    roas = context["roas"]

    margin = context["margin_percentage"]

    inventory = context["inventory"]

    severity = context["diagnostic_severity"]

    drivers = context["primary_drivers"]

    if action == "PAUSE":

        explanation = (
            f"Athena recommends pausing {campaign} because "
            f"the campaign presents a significant performance "
            f"or inventory risk. "
        )

    elif action == "REDUCE":

        explanation = (
            f"Athena recommends reducing spend on {campaign} "
            f"because current performance does not justify "
            f"maintaining the existing budget. "
        )

    elif action == "SCALE":

        explanation = (
            f"Athena recommends scaling {campaign} because "
            f"the campaign shows strong economic potential "
            f"for additional advertising spend. "
        )

    else:

        explanation = (
            f"Athena recommends maintaining {campaign} "
            f"because its current performance does not "
            f"justify a significant budget change. "
        )

    explanation += (
        f"Current ROAS is {roas}, margin is "
        f"{margin}%, and available inventory is "
        f"{inventory} units. "
    )

    if severity != "NORMAL":

        explanation += (
            f"The diagnostic system classified the campaign "
            f"as {severity} severity. "
        )

    if drivers:

        explanation += (
            "Key drivers: "
            + ", ".join(drivers)
            + "."
        )

    return explanation


# =========================================================
# Optional LLM Reasoning
# =========================================================

def generate_llm_reasoning(context):
    """
    Attempt to generate reasoning using an LLM.

    If no API key is configured, Athena automatically
    falls back to deterministic reasoning.
    """

    api_key = os.getenv(
        "OPENAI_API_KEY"
    )

    if not api_key:

        return generate_reasoning(
            context
        )

    # -----------------------------------------------------
    # Keep the actual LLM integration optional.
    # -----------------------------------------------------

    try:

        from openai import OpenAI

        client = OpenAI(
            api_key=api_key
        )

        prompt = f"""
You are Athena, an autonomous D2C advertising
intelligence system.

Explain the following optimization decision
clearly and concisely.

Campaign:
{json.dumps(context, indent=2)}

Explain:
1. What Athena decided.
2. Why Athena made the decision.
3. The most important business factors.
4. What should be monitored next.

Do not invent data.
Use only the supplied information.
"""

        response = client.responses.create(
            model="gpt-5",
            input=prompt
        )

        return response.output_text

    except Exception:

        return generate_reasoning(
            context
        )


# =========================================================
# Generate Reasoning For All Decisions
# =========================================================

def generate_all_reasoning(
    decisions,
    execution_results,
    feedback_results
):
    """
    Generate explanations for every campaign decision.
    """

    execution_lookup = {
        result["campaign_id"]: result
        for result in execution_results
    }

    feedback_lookup = {
        result["campaign_id"]: result
              
        for result in feedback_results
    }

    reasoning_results = []

    for decision in decisions:

        campaign_id = decision[
            "campaign_id"
        ]

        execution_result = (
            execution_lookup[
                campaign_id
            ]
        )

        feedback = (
            feedback_lookup[
                campaign_id
            ]
        )

        context = build_reasoning_context(
            decision,
            execution_result,
            feedback
        )

        explanation = generate_llm_reasoning(
            context
        )

        reasoning_results.append(
            {
                "campaign_id": campaign_id,
                "action": decision["action"],
                "explanation": explanation,
            }
        )

    return reasoning_results


# =========================================================
# Test Athena Reasoning
# =========================================================

if __name__ == "__main__":

    dataset = generate_dataset()

    # Decision
    decisions = generate_decisions(
        dataset
    )

    # Execution
    execution_results = execute_decisions(
        decisions
    )

    # Feedback
    feedback_results = run_feedback_loop(
        decisions,
        execution_results
    )

    # Reasoning
    reasoning_results = generate_all_reasoning(
        decisions,
        execution_results,
        feedback_results
    )

    print("\n")
    print("=" * 70)
    print("                  ATHENA AI REASONING")
    print("=" * 70)

    for result in reasoning_results:

        print("\n")

        print(
            f"Campaign: "
            f"{result['campaign_id']}"
        )

        print(
            f"Action: "
            f"{result['action']}"
        )

        print(
            f"Reasoning:\n"
            f"{result['explanation']}"
        )

        print("-" * 70)