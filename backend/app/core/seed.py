import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal, Base, engine
from app.models.product import Product
from app.models.email import Email
from app.models.automation import Automation
from app.models.content import Content
from app.models.user import User
from app.models.lead import Lead
from app.models.campaign import Campaign
from app.models.generated_content import GeneratedContent
from app.models.publish_log import PublishLog
from app.core.auth import hash_password


PRODUCTS = [
    {
        "id": str(uuid.uuid4()),
        "name": "AI Pod",
        "slug": "pod",
        "published": True,
        "problem": "Work is scattered across tools and pulling together an honest picture of progress takes hours every week.",
        "target": "Best for: Teams and departments who need one shared view of what's being worked on, without chasing status updates.",
        "description": "A task management and reporting system with AI built in.",
        "features": [],
        "benefits": [],
        "capabilities": [
            {"icon": "pod", "title": "Task management", "body": "Shared boards keep every task, owner and deadline visible in one place."},
            {"icon": "report", "title": "Reporting", "body": "Progress is turned into clear reports automatically, no manual compiling."},
            {"icon": "chat", "title": "AI chat", "body": "Ask AI Pod a direct question about your team's work and get a plain answer."},
        ],
        "category": "business",
        "price": "Custom",
        "image_url": "",
    },
    {
        "id": str(uuid.uuid4()),
        "name": "AI Recruiter",
        "slug": "recruiter",
        "published": True,
        "problem": "HR teams post a job, then spend hours manually reading applications to work out who is actually worth a call.",
        "target": "Best for: HR teams and recruiters who need to match open roles with suitable candidates faster, without losing quality.",
        "description": "An AI-powered recruiting and HR platform.",
        "features": [],
        "benefits": [],
        "capabilities": [
            {"icon": "jobs", "title": "Job matching", "body": "Open roles are connected with relevant candidate information automatically."},
            {"icon": "match", "title": "Candidate insight", "body": "See why a candidate fits a role, not just that they applied."},
            {"icon": "recruiter", "title": "HR workflow", "body": "Built around how HR teams actually review and shortlist people."},
        ],
        "category": "business",
        "price": "$299/mo",
        "image_url": "",
    },
    {
        "id": str(uuid.uuid4()),
        "name": "AI Dojo",
        "slug": "dojo",
        "published": True,
        "problem": "Working with AI often feels flat and impersonal, hidden behind a plain text box.",
        "target": "Best for: Anyone who wants a more engaging, personalised way to interact with AI — for training, support, or simply exploring.",
        "description": "Interactive AI avatars for a more personal experience.",
        "features": [],
        "benefits": [],
        "capabilities": [
            {"icon": "avatar", "title": "AI avatars", "body": "Choose an avatar and interact with it directly, in real time."},
            {"icon": "spark", "title": "Personalised", "body": "Each interaction adapts to you, not a generic script."},
            {"icon": "chat", "title": "Engaging by design", "body": "Built to be more memorable than a plain chat window."},
        ],
        "category": "general",
        "price": "$199/mo",
        "image_url": "",
    },
    {
        "id": str(uuid.uuid4()),
        "name": "AI World",
        "slug": "world",
        "published": True,
        "problem": "Experiencing a place before you visit — or without being able to travel at all — is usually limited to photos and video.",
        "target": "Best for: Travellers planning a trip, tourism organisations and anyone curious about exploring Japan virtually.",
        "description": "A virtual world built around Japan.",
        "features": [],
        "benefits": [],
        "capabilities": [
            {"icon": "map", "title": "Explore Japan", "body": "Move through a virtual representation of Japan's places and culture."},
            {"icon": "guide", "title": "Guided tours", "body": "Supports guided, tour-style experiences, not just free roaming."},
            {"icon": "world", "title": "Tourism-ready", "body": "Built to support real tourism and travel-preparation use cases."},
        ],
        "category": "general",
        "price": "$99/mo",
        "image_url": "",
    },
]


EMAILS = [
    {
        "id": "E-501",
        "lead_name": "Kampala FreshFoods Ltd",
        "product_name": "AI Recruiter",
        "status": "sent",
        "subject": "Clearing the hiring backlog at Kampala FreshFoods, Grace",
        "body": "Hi Grace,\n\nI noticed 4 of your open roles have stayed unfilled for a while — usually a sign that manual CV screening is the bottleneck, not a lack of applicants.\n\nAI Recruiter automatically screens and ranks candidates against the role, so you only spend time on the shortlist, not the pile.\n\nWorth a 15-minute chat this week?\n\nBest,\nAI Pod Team",
    },
    {
        "id": "E-502",
        "lead_name": "Nile Logistics Group",
        "product_name": "AI Port",
        "status": "responded",
        "subject": "One shared view across all 3 Nile Logistics hubs",
        "body": "Hi Samuel,\n\nSaw your team is stuck compiling fleet and delivery data by hand across three hubs every week.\n\nAI Port gives every hub a shared task board and turns their combined progress into an automatic report, so head office isn't rebuilding the picture from scratch.\n\nHappy to show you a sample report built from data like yours — interested?\n\nBest,\nAI Pod Team",
    },
    {
        "id": "E-503",
        "lead_name": "Highland People Solutions",
        "product_name": "AI Recruiter",
        "status": "pending",
        "subject": "Faster shortlists for Highland People Solutions",
        "body": "Hi Dr. Yusuf,\n\nA few client reviews mention slow turnaround on candidate shortlists — usually a sign of manual screening at scale.\n\nAI Recruiter screens and ranks every applicant automatically, so your recruiters go straight to the strongest candidates.\n\nWould you be open to a quick call to see it in action?\n\nBest,\nAI Pod Team",
    },
]


AUTOMATIONS = [
    {
        "id": "A1",
        "name": "Lead Discovery — Logistics & Retail Ops EA",
        "status": "running",
        "last_run": "12 min ago",
        "result": "Found 6 new companies, 4 passed duplicate check.",
    },
    {
        "id": "A2",
        "name": "Lead Analysis",
        "status": "running",
        "last_run": "3 min ago",
        "result": "Analysed 4 leads, matched product for all 4.",
    },
    {
        "id": "A3",
        "name": "Follow-up Reminder Check",
        "status": "stopped",
        "last_run": "Today, 07:00",
        "result": "Flagged 3 leads with no response after 5 days.",
    },
]


CONTENT = [
    {
        "id": "B1",
        "type": "blog_post",
        "title": "How AI Recruiter cut screening time by 70% for a 3-person hiring team",
        "status": "published",
        "date": "Aug 12, 2026",
        "excerpt": "A short look at how one small team changed their hiring workflow.",
        "image_url": "",
        "tag": "Product update",
    },
    {
        "id": "N1",
        "type": "news_post",
        "title": "AI Pod passes 500 businesses served across East Africa",
        "status": "published",
        "date": "Aug 18, 2026",
        "excerpt": "More than 500 organisations now use AI Pod for task tracking and reporting.",
        "image_url": "",
        "tag": "Company news",
    },
    {
        "id": "Q1",
        "type": "daily_quote",
        "title": "The best time to find a customer was yesterday. The second best is with AI Pod.",
        "status": "published",
        "date": "Today",
        "excerpt": "",
        "image_url": "",
        "tag": "Quote",
    },
]


LEADS = [
    {
        "company": "Kampala FreshFoods Ltd",
        "website": "https://freshfoods.co.ug",
        "industry": "Food & Beverage",
        "location": "Kampala, Uganda",
        "contact": "Grace Wabwire",
        "email": "grace@freshfoods.co.ug",
        "product_slug": "pod",
        "status": "new",
        "problem": "Manual inventory tracking across 3 warehouses",
        "reasoning": "Kampala FreshFoods operates 3 distribution centers and is likely struggling with visibility into inventory levels and demand forecasting.",
        "last_contact": "12 min ago",
    },
    {
        "company": "Nile Logistics Group",
        "website": "https://nilelogistics.com",
        "industry": "Logistics",
        "location": "Kampala, Uganda",
        "contact": "Samuel Okello",
        "email": "samuel@nilelogistics.com",
        "product_slug": "pod",
        "status": "contacted",
        "problem": "Siloed progress data across 3 hubs",
        "reasoning": "Nile Logistics has 3 hubs with manual reporting, causing delays in operational visibility for head office.",
        "last_contact": "3 days ago",
    },
    {
        "company": "Highland People Solutions",
        "website": "https://highlandpeople.co.ke",
        "industry": "HR & Recruitment",
        "location": "Nairobi, Kenya",
        "contact": "Dr. Yusuf Hassan",
        "email": "yusuf@highlandpeople.co.ke",
        "product_slug": "recruiter",
        "status": "responded",
        "problem": "Slow candidate shortlists",
        "reasoning": "Highland People Solutions is experiencing slow turnaround on candidate shortlists due to manual screening at scale.",
        "last_contact": "1 hour ago",
    },
]


CAMPAIGNS = [
    {
        "name": "Kampala FreshFoods Expansion",
        "product_slug": "pod",
        "target": "Logistics & Retail",
        "status": "running",
        "found": 12,
        "contacted": 8,
        "responded": 5,
        "interested": 3,
        "meetings": 1,
        "customers": 0,
    },
    {
        "name": "Nile Logistics Q3 Outreach",
        "product_slug": "pod",
        "target": "3PL & Supply Chain",
        "status": "completed",
        "found": 24,
        "contacted": 24,
        "responded": 18,
        "interested": 7,
        "meetings": 5,
        "customers": 2,
    },
]


async def seed_products(db: AsyncSession) -> None:
    for product_data in PRODUCTS:
        result = await db.execute(select(Product).where(Product.slug == product_data["slug"]))
        existing = result.scalar_one_or_none()
        if existing:
            for key, value in product_data.items():
                if key == "id":
                    continue
                setattr(existing, key, value)
        else:
            product = Product(**product_data)
            db.add(product)
    await db.commit()


async def seed_emails(db: AsyncSession) -> None:
    for email_data in EMAILS:
        result = await db.execute(select(Email).where(Email.id == email_data["id"]))
        existing = result.scalar_one_or_none()
        if existing:
            for key, value in email_data.items():
                setattr(existing, key, value)
        else:
            email = Email(**email_data)
            db.add(email)
    await db.commit()


async def seed_automations(db: AsyncSession) -> None:
    for automation_data in AUTOMATIONS:
        result = await db.execute(select(Automation).where(Automation.id == automation_data["id"]))
        existing = result.scalar_one_or_none()
        if existing:
            for key, value in automation_data.items():
                setattr(existing, key, value)
        else:
            automation = Automation(**automation_data)
            db.add(automation)
    await db.commit()


async def seed_content(db: AsyncSession) -> None:
    for content_data in CONTENT:
        result = await db.execute(select(Content).where(Content.id == content_data["id"]))
        existing = result.scalar_one_or_none()
        if existing:
            for key, value in content_data.items():
                setattr(existing, key, value)
        else:
            content = Content(**content_data)
            db.add(content)
    await db.commit()


async def seed_leads(db: AsyncSession) -> None:
    for lead_data in LEADS:
        product_result = await db.execute(
            select(Product).where(Product.slug == lead_data.pop("product_slug"))
        )
        product = product_result.scalar_one_or_none()
        if not product:
            continue

        lead_data["id"] = str(uuid.uuid4())
        lead_data["product_id"] = product.id

        result = await db.execute(select(Lead).where(Lead.email == lead_data["email"]))
        existing = result.scalar_one_or_none()
        if existing:
            for key, value in lead_data.items():
                setattr(existing, key, value)
        else:
            lead = Lead(**lead_data)
            db.add(lead)
    await db.commit()


async def seed_campaigns(db: AsyncSession) -> None:
    for campaign_data in CAMPAIGNS:
        product_slug = campaign_data.pop("product_slug")
        product_result = await db.execute(
            select(Product).where(Product.slug == product_slug)
        )
        product = product_result.scalar_one_or_none()
        if not product:
            continue

        campaign_data["id"] = str(uuid.uuid4())
        campaign_data["product_id"] = product.id

        result = await db.execute(
            select(Campaign).where(Campaign.name == campaign_data["name"])
        )
        existing = result.scalar_one_or_none()
        if existing:
            for key, value in campaign_data.items():
                setattr(existing, key, value)
        else:
            campaign = Campaign(**campaign_data)
            db.add(campaign)
    await db.commit()


async def seed_users(db: AsyncSession) -> None:
    admin_email = "admin@akademia.local"
    admin_password = "admin123"
    result = await db.execute(select(User).where(User.id == admin_email))
    if not result.scalar_one_or_none():
        db.add(
            User(
                id=admin_email,
                email=admin_email,
                name="Admin",
                hashed_password=hash_password(admin_password),
                is_active=True,
                is_superuser=True,
            )
        )
    await db.commit()


if __name__ == "__main__":
    import asyncio
    from sqlalchemy import text

    async def main() -> None:
        async with engine.begin() as conn:
            await conn.execute(text("DROP SCHEMA public CASCADE"))
            await conn.execute(text("CREATE SCHEMA public"))
            await conn.run_sync(Base.metadata.create_all)
        async with AsyncSessionLocal() as db:
            await seed_products(db)
            await seed_leads(db)
            await seed_campaigns(db)
            await seed_emails(db)
            await seed_automations(db)
            await seed_content(db)
            await seed_users(db)

    asyncio.run(main())



