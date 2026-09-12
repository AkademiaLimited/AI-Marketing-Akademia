import pytest
from sqlalchemy import select

from app.models.email import Email


@pytest.mark.anyio
async def test_email_review_changes_only_drafts(db_session):
    email = Email(
        id="review-email",
        lead_name="Example Foods",
        product_name="AI Pod",
        status="draft",
        subject="A better way to report",
        body="Draft body",
    )
    db_session.add(email)
    await db_session.commit()

    from app.api.routers.emails import _review_email

    reviewed = await _review_email("review-email", "approved", db_session)
    assert reviewed.status == "approved"

    result = await db_session.execute(select(Email).where(Email.id == "review-email"))
    assert result.scalar_one().status == "approved"

    with pytest.raises(Exception, match="Only draft emails can be reviewed"):
        await _review_email("review-email", "rejected", db_session)