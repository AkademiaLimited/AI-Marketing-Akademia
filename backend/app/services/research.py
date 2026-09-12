from html.parser import HTMLParser
import uuid
from typing import Any, TypedDict
from urllib.parse import urlparse

import httpx
from langgraph.graph import END, START, StateGraph
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.groq_client import call_groq_json
from app.models.email import Email
from app.models.lead import Lead
from app.models.product import Product
from app.services.tracking import create_workflow_run, finish_workflow_run, record_activity


class WebsiteTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._ignored_depth = 0
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style", "noscript", "svg"}:
            self._ignored_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "noscript", "svg"} and self._ignored_depth:
            self._ignored_depth -= 1

    def handle_data(self, data: str) -> None:
        if not self._ignored_depth:
            text = " ".join(data.split())
            if text:
                self.parts.append(text)


def _validate_website_url(website: str) -> str:
    parsed = urlparse(website)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("Lead website must be a valid http or https URL")
    if parsed.hostname in {"localhost", "127.0.0.1", "0.0.0.0", "::1"}:
        raise ValueError("Local websites are not allowed")
    return website


async def fetch_website_text(website: str) -> str:
    url = _validate_website_url(website)
    async with httpx.AsyncClient(
        timeout=10.0,
        follow_redirects=True,
        headers={"User-Agent": "AI-Marketer-Research/1.0"},
    ) as client:
        response = await client.get(url)
        response.raise_for_status()

    parser = WebsiteTextParser()
    parser.feed(response.text)
    return " ".join(parser.parts)[:12000]


RESEARCH_SYSTEM_PROMPT = """
You are a careful B2B marketing researcher. Use only the supplied lead and
website text. Do not invent facts, contacts, prices, or claims. Return only
valid JSON in this exact format:
{
  "qualification_score": 0.0,
  "qualification_reason": "short evidence-based explanation",
  "subject": "email subject",
  "body": "professional email draft"
}
The qualification score must be between 0.0 and 1.0. The email is a draft
only and must not claim that an email was sent.
"""


class ResearchState(TypedDict, total=False):
    lead_id: str
    workflow_run_id: str
    website_text: str | None
    lead: Lead
    product: Product
    research_text: str
    qualification_score: float
    qualification_reason: str
    subject: str
    body: str
    email_id: str
    result: dict[str, Any]


def build_research_email_graph(db: AsyncSession):
    async def load_context(state: ResearchState) -> ResearchState:
        try:
            lead_result = await db.execute(select(Lead).where(Lead.id == state["lead_id"]))
            lead = lead_result.scalar_one_or_none()
            if not lead:
                raise ValueError("Lead not found")

            product_result = await db.execute(select(Product).where(Product.id == lead.product_id))
            product = product_result.scalar_one_or_none()
            if not product:
                raise ValueError("Lead product not found")

            return {"lead": lead, "product": product}
        except Exception as exc:
            await record_activity(
                db,
                state["workflow_run_id"],
                "load_context_failed",
                lead_id=state["lead_id"],
                status="failed",
                error=str(exc),
            )
            raise

    async def research_website(state: ResearchState) -> ResearchState:
        try:
            text = state.get("website_text")
            if text is None:
                text = await fetch_website_text(state["lead"].website)
            if not text:
                raise ValueError("The lead website did not contain readable text")
            await record_activity(
                db,
                state["workflow_run_id"],
                "website_researched",
                lead_id=state["lead"].id,
                source_url=state["lead"].website,
                details=f"Collected {len(text)} characters of readable website text.",
            )
            return {"research_text": text}
        except Exception as exc:
            await record_activity(
                db,
                state["workflow_run_id"],
                "research_website_failed",
                lead_id=state["lead"].id,
                source_url=state["lead"].website,
                status="failed",
                error=str(exc),
            )
            raise

    async def qualify_and_draft(state: ResearchState) -> ResearchState:
        lead = state["lead"]
        product = state["product"]
        try:
            result = await call_groq_json(
                f"Lead company: {lead.company}\n"
                f"Contact: {lead.contact}\n"
                f"Industry: {lead.industry}\n"
                f"Existing problem hypothesis: {lead.problem}\n"
                f"Product: {product.name}\n"
                f"Product description: {product.description}\n\n"
                f"Website text:\n{state['research_text']}",
                system_prompt=RESEARCH_SYSTEM_PROMPT,
            )
            score = float(result.get("qualification_score", 0))
            score = max(0.0, min(1.0, score))
            await record_activity(
                db,
                state["workflow_run_id"],
                "lead_qualified",
                lead_id=lead.id,
                status="qualified" if score >= 0.7 else "review",
                details=result.get("qualification_reason", ""),
            )
            return {
                "qualification_score": score,
                "qualification_reason": result.get("qualification_reason", ""),
                "subject": result.get("subject", ""),
                "body": result.get("body", ""),
            }
        except Exception as exc:
            await record_activity(
                db,
                state["workflow_run_id"],
                "ai_qualification_failed",
                lead_id=lead.id,
                status="failed",
                error=str(exc),
            )
            raise

    async def persist_draft(state: ResearchState) -> ResearchState:
        lead = state["lead"]
        product = state["product"]
        try:
            lead.reasoning = state["qualification_reason"]
            if state["qualification_score"] >= 0.7:
                lead.status = "qualified"

            email = Email(
                id=str(uuid.uuid4()),
                lead_name=lead.company,
                product_name=product.name,
                status="draft",
                subject=state["subject"],
                body=state["body"],
            )
            db.add(email)
            await db.commit()
            await db.refresh(email)
            await record_activity(
                db,
                state["workflow_run_id"],
                "email_draft_created",
                lead_id=lead.id,
                email_id=email.id,
                channel="email",
                status="draft",
                details="Draft created; no message was sent.",
            )

            return {
                "email_id": email.id,
                "result": {
                    "lead_id": lead.id,
                    "company": lead.company,
                    "website": lead.website,
                    "qualification_score": state["qualification_score"],
                    "qualification_reason": lead.reasoning,
                    "email_id": email.id,
                    "email_status": email.status,
                    "subject": email.subject,
                    "body": email.body,
                },
            }
        except Exception as exc:
            await record_activity(
                db,
                state["workflow_run_id"],
                "email_draft_persistence_failed",
                lead_id=lead.id,
                channel="email",
                status="failed",
                error=str(exc),
            )
            raise

    graph = StateGraph(ResearchState)
    graph.add_node("load_context", load_context)
    graph.add_node("research_website", research_website)
    graph.add_node("qualify_and_draft", qualify_and_draft)
    graph.add_node("persist_draft", persist_draft)
    graph.add_edge(START, "load_context")
    graph.add_edge("load_context", "research_website")
    graph.add_edge("research_website", "qualify_and_draft")
    graph.add_edge("qualify_and_draft", "persist_draft")
    graph.add_edge("persist_draft", END)
    return graph.compile()


async def research_lead_and_draft_email(
    db: AsyncSession,
    lead_id: str,
    *,
    website_text: str | None = None,
) -> dict[str, Any]:
    run = await create_workflow_run(db, "research_email_draft", lead_id)
    try:
        final_state = await build_research_email_graph(db).ainvoke(
            {
                "lead_id": lead_id,
                "website_text": website_text,
                "workflow_run_id": run.id,
            }
        )
        await finish_workflow_run(db, run, status="completed")
        result = final_state["result"]
        result["workflow_run_id"] = run.id
        return result
    except Exception as exc:
        await record_activity(
            db,
            run.id,
            "workflow_failed",
            lead_id=lead_id,
            status="failed",
            details="Research and draft workflow stopped before completion.",
            error=str(exc),
        )
        await finish_workflow_run(db, run, status="failed", error=str(exc))
        raise