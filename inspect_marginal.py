import inspect
import marginal

methods = [
    (marginal.UniversalRuntime, "before_action"),
    (marginal.UniversalRuntime, "after_action"),
    (marginal.UniversalRuntime, "fail_action"),
    (marginal.UniversalRuntime, "record_outcome"),
    (marginal.DiminishingReturnDetector, "evaluate"),
    (marginal.DiminishingReturnDetector, "observe"),
    (marginal.AgentAction, "to_core_action"),
]

for cls, method_name in methods:
    method = getattr(cls, method_name)

    print("\n" + "=" * 60)
    print(f"{cls.__name__}.{method_name}")
    print("=" * 60)

    print(inspect.getdoc(method) or "No docstring available.")

    try:
        print("\nImplementation:")
        print(inspect.getsource(method))
    except (OSError, TypeError) as error:
        print("Source unavailable:", error)