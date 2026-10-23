from marginal import (
    AgentAction,
    BudgetLimits,
    Cost,
    Treasury,
    UniversalRuntime,
    AgentCapabilities,
    build_policy,
)


def main():
    # 1. Create a budget
    treasury = Treasury(
        BudgetLimits(
            max_tokens=1000,
            max_usd=0.50,
            max_risk=0.5,
        ),
        policy=build_policy("balanced"),
        mode="shadow",
    )

    # 2. Connect BugHunter to MARGINAL
    runtime = UniversalRuntime(
        treasury,
        engine="bughunter",
        session_id="demo-session",
        task_id="calculator-bug-001",
        capabilities=AgentCapabilities(),
    )

    # 3. Describe a proposed test-running action
    action = AgentAction(
        action_id="action-001",
        name="run_calculator_tests",
        kind="verification",
        estimated_cost=Cost(
            tokens=100,
            usd=0.01,
            risk=0.1,
        ),
        expected_gain=0.8,
        current_success_probability=0.9,
        is_verification=True,
        state_hash="calculator-state-001",
        phase="verification",
    )

    # 4. Ask MARGINAL to evaluate the action
    decision = runtime.before_action(action)

    print("BugHunter AI — MARGINAL Governance Test")
    print("-" * 45)
    print("Action:", decision.action_id)
    print("Allowed:", decision.allowed)
    print("Directive:", decision.directive)
    print("Reason:", decision.reason)
    print("Reason code:", decision.reason_code)
    print("Mode:", decision.mode)

    # Shadow mode is for observing decisions.
    # Do not execute the action in this demo.


if __name__ == "__main__":
    main()