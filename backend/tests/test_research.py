import pytest
from sqlalchemy import select

from app.models.email import Email
from app.models.lead import Lead
from app.models.product import Product


@pytest.fixture
async def research_lead(db_session):
    product = Product(
        id="research-product",
        name="AI Pod",
        slug="research-pod",
        description="Task management and reporting for teams.",
        problem="Scattered operational work",
        target="Operations teams",
        features=[],
        benefits=[],
        capabilities=[],
    )
    lead = Lead(
        id="research-lead",
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
async def test_research_creates_qualified_email_draft(db_session, research_lead, monkeypatch):
    async def mock_call_groq_json(prompt, system_prompt, **kwargs):
        assert "Example Foods" in prompt
        assert "Operational visibility" in prompt
        return {
            "qualification_score": 0.88,
            "qualification_reason": "The website describes a growing operations team with manual reporting needs.",
            "subject": "A clearer view of operations at Example Foods",
            "body": "Hi Jane,\n\nAI Pod could help your team simplify reporting.\n\nBest,\nAI Marketer",
        }

    monkeypatch.setattr("app.services.research.call_groq_json", mock_call_groq_json)

    from app.services.research import research_lead_and_draft_email

    result = await research_lead_and_draft_email(
        db_session,
        research_lead.id,
        website_text="Example Foods is growing. Operational visibility is difficult.",
    )

    assert result["qualification_score"] == 0.88
    assert result["email_status"] == "draft"

    lead_result = await db_session.execute(select(Lead).where(Lead.id == research_lead.id))
    assert lead_result.scalar_one().status == "qualified"

    email_result = await db_session.execute(select(Email).where(Email.id == result["email_id"]))
    email = email_result.scalar_one()
    assert email.subject == "A clearer view of operations at Example Foods"
    assert email.status == "draft"


@pytest.mark.anyio
async def test_research_rejects_local_websites(db_session, research_lead):
    research_lead.website = "http://127.0.0.1:8000/private"
    await db_session.commit()

    from app.services.research import research_lead_and_draft_email

    with pytest.raises(ValueError, match="Local websites are not allowed"):
        await research_lead_and_draft_email(db_session, research_lead.id)