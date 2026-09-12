from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers import auth, campaigns, contact, dashboard, emails, leads, products, automations, content, workflows
from app.core.config import settings

app = FastAPI(title="Akademia AI Marketing System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])
app.include_router(leads.router, prefix="/api/leads", tags=["leads"])
app.include_router(campaigns.router, prefix="/api/campaigns", tags=["campaigns"])
app.include_router(products.router, prefix="/api/products", tags=["products"])
app.include_router(contact.router, prefix="/api/contact", tags=["contact"])
app.include_router(emails.router, prefix="/api/emails", tags=["emails"])
app.include_router(automations.router, prefix="/api/automations", tags=["automations"])
app.include_router(content.router, prefix="/api/content", tags=["content"])
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(workflows.router, prefix="/api/workflows", tags=["workflows"])


@app.get("/health")
def health():
    return {"status": "ok"}
