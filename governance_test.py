
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
    treasury = Treasury(
        BudgetLimits(
            max_tokens=1000,
            max_usd=0.50,
            max_risk=0.5,
        ),
        policy=build_policy("balanced"),
        mode="shadow",
    )

    runtime = UniversalRuntime(
        treasury,
        engine="bughunter",
        session_id="demo-session",
        task_id="calculator-bug-001",
        capabilities=AgentCapabilities(),
    )

    action = AgentAction(
        action_id="action-002",
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

    decision = runtime.before_action(action)

    print("Action approved:", decision.allowed)
    print("Directive:", decision.directive)

    if decision.allowed:
        # Demo only: no tests are actually run here.
        runtime.after_action(
            action.action_id,
            actual_cost=Cost(
                tokens=100,
                usd=0.01,
                risk=0.1,
            ),
        )
        print("Action lifecycle completed.")
    else:
        print("Action not approved; no execution performed.")

    print("Pending actions:", runtime.pending_action_ids())


if __name__ == "__main__":
    main()
