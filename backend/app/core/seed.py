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
from app.models.brand import BrandProfile
from app.models.workflow import WorkflowRun, MarketingActivity
from app.core.auth import hash_password


PRODUCTS = [
    {
        "id": str(uuid.uuid4()),
        "name": "AI AVATAR AKADEMIA",
        "slug": "avatar",
        "published": True,
        "problem": "Remote communication lacks human presence — avatars, interpreters, and meeting tools feel robotic and disconnected.",
        "target": "Best for: Enterprises and educators who need lifelike 3D avatars for interviews, training, translation, and virtual meetings.",
        "description": "A 3D AI avatar platform bridging Japan and Uganda. Talk to lifelike avatar guides for culture, business etiquette, and Luganda phrases, run live video meetings with real-time speech translation and lip-synced avatar interpreters, or launch an AI-powered interview and recruiter mode — all with your own custom-built avatar characters.",
        "features": ["3D avatar guides", "Real-time speech translation", "Lip-synced avatars", "AI interviewer mode", "Custom avatar characters"],
        "benefits": ["Reduce staffing costs for 24/7 interaction", "Consistent quality for every user", "Multi-language support without hiring", "Full session logging and compliance-ready records"],
        "capabilities": [
            {"icon": "avatar", "title": "AI Candidate Interviewer", "body": "Automate round-one technical and behavioral screening with a voice agent that asks follow-ups, evaluates competence, and generates an assessment report."},
            {"icon": "translate", "title": "Meeting translation", "body": "Real-time conversation translation for cross-language meetings and collaboration."},
            {"icon": "chat", "title": "AI Medical Assistant", "body": "Handles patient intake, caregiver support, and consultation routing, with multi-language translation and secure record storage."},
        ],
        "category": "ai-avatars",
        "price": "Custom",
        "image_url": "https://ai-pod.net/images/image%20copy%2017.png",
    },
    {
        "id": str(uuid.uuid4()),
        "name": "VIRTUAL WORLD",
        "slug": "world",
        "published": True,
        "problem": "Remote work feels isolating — scheduled video calls and chat tabs fragment collaboration and kill spontaneity.",
        "target": "Best for: Distributed teams and event organizers who want spontaneous, in-person-like collaboration in a virtual space.",
        "description": "A persistent virtual office and event space built on the WorkAdventure engine. Teams and attendees move around as characters in a 2D map, bumping into colleagues, joining spontaneous video calls, and collaborating the way they would in a real shared space — no scheduled meeting links required.",
        "features": ["Persistent virtual office", "2D character navigation", "Spontaneous video calls", "WorkAdventure engine", "No scheduled meeting links"],
        "benefits": ["Recreate spontaneous office interactions", "Reduce meeting overload", "Natural proximity-based communication", "Immersive team presence"],
        "capabilities": [
            {"icon": "world", "title": "Virtual office", "body": "A persistent space where teams work and meet as avatars on a 2D map."},
            {"icon": "map", "title": "Event spaces", "body": "Host conferences, meetups, and workshops with spatial audio and proximity chat."},
            {"icon": "chat", "title": "Seamless collaboration", "body": "Bump into colleagues to start conversations — no calendar invites needed."},
        ],
        "category": "virtual-worlds",
        "price": "$99/mo",
        "image_url": "https://ai-pod.net/images/image%20copy%2018.png",
    },
    {
        "id": str(uuid.uuid4()),
        "name": "AIPOD",
        "slug": "pod",
        "published": True,
        "problem": "Work is scattered across tools and pulling together an honest picture of progress takes hours every week.",
        "target": "Best for: Teams and departments who need one shared view of what's being worked on, without chasing status updates.",
        "description": "An AI-powered daily reporting dashboard. Teams log in to submit and review structured daily reports, with account registration and secure sign-in built for organizations that need a consistent, automated pulse on daily work.",
        "features": ["Daily reporting dashboard", "Team status boards", "Auto-generated reports", "AI chat queries", "Secure sign-in"],
        "benefits": ["Eliminate manual status compilation", "Shared real-time view of all work", "Instant AI-powered insights", "Enterprise-grade security"],
        "capabilities": [
            {"icon": "pod", "title": "Task management", "body": "Shared boards keep every task, owner and deadline visible in one place."},
            {"icon": "report", "title": "Reporting", "body": "Progress is turned into clear reports automatically, no manual compiling."},
            {"icon": "chat", "title": "AI chat", "body": "Ask AIPOD a direct question about your team's work and get a plain answer."},
        ],
        "category": "business",
        "price": "Custom",
        "image_url": "https://ai-pod.net/images/image%20copy%2019.png",
    },
    {
        "id": str(uuid.uuid4()),
        "name": "UgaJapa Translation",
        "slug": "translation",
        "published": True,
        "problem": "Teams lose nuance and speed when translating across languages — especially African and Asian language pairs that standard APIs struggle with.",
        "target": "Best for: Global teams using Mattermost who need accurate, affordable, and resilient translation with billing transparency.",
        "description": "A global translation API and dashboard purpose-built for Mattermost plugins, combining a neural translation engine, a voice engine for speech-to-text and subtitles, a 197-language global engine, text-to-speech, and a resilient always-on fallback bot — with per-user API keys, quality scoring, and usage-based billing.",
        "features": ["197-language support", "Neural translation engine", "Speech-to-text & subtitles", "Text-to-speech", "Per-user API keys", "Quality scoring", "Usage-based billing"],
        "benefits": ["Optimized for African & Asian languages", "Always-on fallback for reliability", "Transparent usage-based pricing", "Enterprise-grade quality metadata"],
        "capabilities": [
            {"icon": "globe", "title": "UgaJapa Neural Engine", "body": "AI-powered translation optimised for African languages, Japanese, and complex language pairs."},
            {"icon": "voice", "title": "UgaJapa Voice Engine", "body": "Speech-to-text for voice messages, audio files, and video subtitle generation."},
            {"icon": "world", "title": "UgaJapa Global Engine", "body": "Worldwide text translation across 197 languages with enterprise-grade quality."},
            {"icon": "bot", "title": "UgaJapa Bot", "body": "Resilient on-platform fallback engine — always available, no external dependency."},
        ],
        "category": "translation",
        "price": "$49/mo",
        "image_url": "https://ai-pod.net/images/image%20copy%2020.png",
    },
    {
        "id": str(uuid.uuid4()),
        "name": "AI DOJO",
        "slug": "dojo",
        "published": True,
        "problem": "Language learning apps feel flat — text-based drills never prepare you for real conversations.",
        "target": "Best for: Language learners who want to practice real-world conversations with AI, get instant feedback, and track progress with gamification.",
        "description": "An immersive Japanese language role-play trainer. Learners practice real-time voice conversations with AI characters across 8+ realistic scenario domains — restaurants, travel, business, healthcare, shopping, school life — with instant feedback, XP, and streak tracking to keep learners coming back.",
        "features": ["30+ languages", "100+ scenarios", "Real-time voice chat", "Instant AI feedback", "XP & streak tracking", "Cultural context"],
        "benefits": ["Practice real conversations, not textbooks", "Learn anytime, no scheduling", "Get pronunciation and grammar feedback", "Gamified progress keeps you engaged"],
        "capabilities": [
            {"icon": "avatar", "title": "Realistic AI Partners", "body": "Talk with AI characters that understand context and respond naturally."},
            {"icon": "map", "title": "Immersive Scenarios", "body": "Practice in real-world situations that mirror daily life — restaurants, travel, business, healthcare, shopping, school life."},
            {"icon": "spark", "title": "Instant Feedback", "body": "Get AI feedback on your pronunciation, grammar, and fluency in real time."},
            {"icon": "chart", "title": "Progress Tracking", "body": "Earn XP, build streaks, and watch your skills improve over time."},
        ],
        "category": "education",
        "price": "$199/mo",
        "image_url": "https://ai-pod.net/images/image%20copy%2021.png",
    },
    {
        "id": str(uuid.uuid4()),
        "name": "AI RECRUITER",
        "slug": "recruiter",
        "published": True,
        "problem": "HR teams post a job, then spend hours manually reading applications to work out who is actually worth a call.",
        "target": "Best for: HR teams and recruiters who need to match open roles with suitable candidates faster, without losing quality.",
        "description": "An enterprise-grade AI recruitment operating system. Automates candidate screening, interview scheduling, and shortlisting, giving hiring teams a faster, more consistent way to evaluate talent at scale.",
        "features": ["AI candidate screening", "Interview scheduling", "Automated shortlisting", "Consistent evaluation", "Talent matching at scale"],
        "benefits": ["Slash time-to-hire", "Consistent candidate evaluation", "Scale screening without adding HR headcount", "Reduce unconscious bias in initial screening"],
        "capabilities": [
            {"icon": "jobs", "title": "Job matching", "body": "Open roles are connected with relevant candidate information automatically."},
            {"icon": "match", "title": "Candidate insight", "body": "See why a candidate fits a role, not just that they applied."},
            {"icon": "recruiter", "title": "HR workflow", "body": "Built around how HR teams actually review and shortlist people."},
        ],
        "category": "business",
        "price": "$299/mo",
        "image_url": "https://ai-pod.net/images/image%20copy%2017.png",
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
        "product_name": "AIPOD",
        "status": "sent",
        "subject": "One shared view across all 3 Nile Logistics hubs",
        "body": "Hi Samuel,\n\nSaw your team is stuck compiling fleet and delivery data by hand across three hubs every week.\n\nAIPOD gives every hub a shared task board and turns their combined progress into an automatic report, so head office isn't rebuilding the picture from scratch.\n\nHappy to show you a sample report built from data like yours — interested?\n\nBest,\nAI Pod Team",
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
        "title": "AIPOD passes 500 businesses served across East Africa",
        "status": "published",
        "date": "Aug 18, 2026",
        "excerpt": "More than 500 organisations now use AIPOD for task tracking and reporting.",
        "image_url": "",
        "tag": "Company news",
    },
    {
        "id": "Q1",
        "type": "daily_quote",
        "title": "The best time to find a customer was yesterday. The second best is with AIPOD.",
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
    admin_password = "Admin@1234"
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


async def seed_brands(db: AsyncSession) -> None:
    brand_id = "brand-default-akademia"
    result = await db.execute(select(BrandProfile).where(BrandProfile.id == brand_id))
    if not result.scalar_one_or_none():
        db.add(
            BrandProfile(
                id=brand_id,
                name="Akademia Default",
                user_id="admin@akademia.local",
                is_active=True,
                tone_keywords="professional, approachable, clear",
                voice_description="Brand Voice: Professional yet approachable AI marketing tone.\nValue Proposition: AI-powered marketing automation that delivers results.\nTarget Audience: Businesses looking to scale their marketing with AI.\nKey Messages: Efficiency, accuracy, and consistency in every automated interaction.",
                primary_color="#1F6F5C",
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
            await seed_brands(db)
        await seed_brands(db)

    asyncio.run(main())



