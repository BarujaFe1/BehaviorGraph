from app.services.analytics import build_activation_funnel, load_demo_summary


def test_demo_summary_shape():
    summary = load_demo_summary()
    assert summary["product"] == "BehaviorGraph"
    assert "users" in summary
    assert "activation_rate" in summary


def test_activation_funnel_has_steps():
    funnel = build_activation_funnel()
    assert funnel["funnel"] == "activation"
    assert len(funnel["steps"]) >= 3
