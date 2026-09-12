import pytest
from sqlalchemy import select

from app.models.workflow import MarketingActivity, WorkflowRun
from app.models.lead import Lead
from app.models.product import Product
from app.services.tracking import create_workflow_run, finish_workflow_run, record_activity


@pytest.fixture
async def tracking_lead(db_session):
    product = Product(
        id="tracking-product",
        name="AI Pod",
        slug="tracking-pod",
        description="Task management and reporting for teams.",
        problem="Scattered operational work",
        target="Operations teams",
        features=[],
        benefits=[],
        capabilities=[],
    )
    lead = Lead(
        id="tracking-lead",
        company="Example Foods",
        website="https://example.com",
        industry="Food and beverage",
        contact="Jane Doe",
        email="jane@example.com",
        product_id=product.id,
        problem="Manual reporting",
    )
    db_session.add_all([product, lead])
    await db_session.commit()
    return lead


@pytest.mark.anyio
async def test_tracking_records_run_and_activity(db_session):
    run = await create_workflow_run(db_session, "test_workflow", "lead-1")
    activity = await record_activity(
        db_session,
        run.id,
        "website_researched",
        lead_id="lead-1",
        source_url="https://example.com",
        details="Collected website text.",
    )
    await finish_workflow_run(db_session, run, status="completed")

    stored_run = await db_session.get(WorkflowRun, run.id)
    stored_activity = await db_session.get(MarketingActivity, activity.id)
    assert stored_run is not None
    assert stored_run.status == "completed"
    assert stored_run.finished_at
    assert stored_activity is not None
    assert stored_activity.source_url == "https://example.com"


@pytest.mark.anyio
async def test_research_run_returns_tracking_id_and_events(db_session, tracking_lead, monkeypatch):
    async def mock_call_groq_json(prompt, system_prompt, **kwargs):
        return {
            "qualification_score": 0.88,
            "qualification_reason": "Evidence supports a fit.",
            "subject": "A useful idea for Example Foods",
            "body": "Draft message",
        }

    monkeypatch.setattr("app.services.research.call_groq_json", mock_call_groq_json)

    from app.services.research import research_lead_and_draft_email

    result = await research_lead_and_draft_email(
        db_session,
        tracking_lead.id,
        website_text="Example Foods has a reporting challenge.",
    )

    run = await db_session.get(WorkflowRun, result["workflow_run_id"])
    activities = await db_session.execute(
        select(MarketingActivity).where(
            MarketingActivity.workflow_run_id == result["workflow_run_id"]
        )
    )
    activity_types = {activity.activity_type for activity in activities.scalars()}
    assert run is not None
    assert run.status == "completed"
    assert activity_types == {
        "website_researched",
        "lead_qualified",
        "email_draft_created",
    }


@pytest.mark.anyio
async def test_failed_research_run_records_cause(db_session, tracking_lead):
    tracking_lead.website = "http://127.0.0.1:8000/private"
    await db_session.commit()

    from app.services.research import research_lead_and_draft_email

    with pytest.raises(ValueError, match="Local websites are not allowed"):
        await research_lead_and_draft_email(db_session, tracking_lead.id)

    run_result = await db_session.execute(
        select(WorkflowRun).where(WorkflowRun.lead_id == tracking_lead.id)
    )
    run = run_result.scalar_one()
    activity_result = await db_session.execute(
        select(MarketingActivity).where(MarketingActivity.workflow_run_id == run.id)
    )
    failures = activity_result.scalars().all()
    assert run.status == "failed"
    assert "Local websites are not allowed" in run.error
    failure_types = {activity.activity_type for activity in failures}
    assert "research_website_failed" in failure_types
    assert "workflow_failed" in failure_types
    assert all(activity.status == "failed" for activity in failures)
    assert all("Local websites are not allowed" in activity.error for activity in failures)