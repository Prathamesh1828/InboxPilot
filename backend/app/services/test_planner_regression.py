import pytest
from app.services.planner import EmailPlanner
from app.schemas.action_plan import ActionType

def test_planner_meeting_regression():
    planner = EmailPlanner()
    
    plan = planner.create_plan(
        category="MEETING",
        classification_reasoning="The email contains an explicit meeting request with a time.",
        subject="Project Discussion",
        body="Please schedule a client meeting tomorrow at 11:00 AM to discuss the project.",
    )
    
    assert plan.action == ActionType.CREATE_CALENDAR_EVENT
    assert plan.parameters.start_time is not None
    assert plan.risk_level == "MEDIUM"
    assert plan.requires_approval is True
