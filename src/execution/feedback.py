from src.ingestion.synthetic_stream import generate_dataset
from src.decision.optimizer import generate_decisions
from src.execution.executor import execute_decisions


# =========================================================
# Feedback Evaluation
# =========================================================

def evaluate_feedback(decision, execution_result):
    """
    Evaluate the expected outcome of an executed decision.

    In a real system, this would compare future campaign
    performance against the performance before the action.
    """

    action = decision["action"]

    if execution_result["status"] == "FAILED":

        return {
            "campaign_id": decision["campaign_id"],
            "action": action,
            "outcome": "FAILED",
            "learning_signal": -1,
            "message": "Execution failed."
        }

    if action == "SCALE":

        return {
            "campaign_id": decision["campaign_id"],
            "action": action,
            "outcome": "PENDING",
            "learning_signal": 0,
            "message": (
                "Campaign scaled. "
                "Future performance should be monitored."
            )
        }

    if action == "REDUCE":

        return {
            "campaign_id": decision["campaign_id"],
            "action": action,
            "outcome": "PENDING",
            "learning_signal": 0,
            "message": (
                "Campaign budget reduced. "
                "Future efficiency should be monitored."
            )
        }

    if action == "PAUSE":

        return {
            "campaign_id": decision["campaign_id"],
            "action": action,
            "outcome": "PROTECTIVE_ACTION",
            "learning_signal": 1,
            "message": (
                "Campaign paused to prevent further "
                "potential losses."
            )
        }

    return {
        "campaign_id": decision["campaign_id"],
        "action": action,
        "outcome": "STABLE",
        "learning_signal": 0,
        "message": (
            "Campaign maintained. "
            "Performance remains under observation."
        )
    }


# =========================================================
# Run Feedback Loop
# =========================================================

def run_feedback_loop(decisions, execution_results):
    """
    Connect decisions with their execution results
    and generate learning signals.
    """

    execution_lookup = {
        result["campaign_id"]: result
        for result in execution_results
    }

    feedback = []

    for decision in decisions:

        execution_result = execution_lookup[
            decision["campaign_id"]
        ]

        evaluation = evaluate_feedback(
            decision,
            execution_result
        )

        feedback.append(
            evaluation
        )

    return feedback


# =========================================================
# Test Feedback System
# =========================================================

if __name__ == "__main__":

    dataset = generate_dataset()

    # Generate optimization decisions
    decisions = generate_decisions(
        dataset
    )

    # Execute decisions
    execution_results = execute_decisions(
        decisions
    )

    # Evaluate outcomes
    feedback = run_feedback_loop(
        decisions,
        execution_results
    )

    print("\n")
    print("=" * 70)
    print("                  ATHENA FEEDBACK LOOP")
    print("=" * 70)

    for result in feedback:

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
            f"Outcome: "
            f"{result['outcome']}"
        )

        print(
            f"Learning Signal: "
            f"{result['learning_signal']}"
        )

        print(
            f"Message: "
            f"{result['message']}"
        )

        print("-" * 70)