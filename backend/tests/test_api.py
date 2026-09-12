import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_health(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.anyio
async def test_products_crud(client: AsyncClient):
    payload = {
        "id": "prod-1",
        "name": "Test Product",
        "slug": "test-product",
        "published": False,
        "problem": "Test problem",
        "target": "Test target",
        "description": "Test description",
        "features": ["Feature 1"],
        "benefits": ["Benefit 1"],
    }
    response = await client.post("/api/products/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["slug"] == "test-product"
    assert data["published"] is False

    response = await client.get("/api/products/test-product")
    assert response.status_code == 200
    assert response.json()["name"] == "Test Product"

    response = await client.get("/api/products/")
    assert response.status_code == 200
    assert len(response.json()) == 1

    response = await client.patch("/api/products/test-product", json={"published": True})
    assert response.status_code == 200
    assert response.json()["published"] is True


@pytest.mark.anyio
async def test_leads_crud(client: AsyncClient):
    product_payload = {
        "id": "prod-lead",
        "name": "Lead Product",
        "slug": "lead-product",
        "published": True,
        "problem": "P",
        "target": "T",
        "description": "D",
        "features": [],
        "benefits": [],
    }
    await client.post("/api/products/", json=product_payload)

    payload = {
        "id": "lead-1",
        "company": "Acme Corp",
        "website": "https://acme.com",
        "industry": "Tech",
        "location": "NYC",
        "contact": "John Doe",
        "email": "john@acme.com",
        "product_id": "prod-lead",
        "status": "new",
        "problem": "Needs AI",
        "reasoning": "High fit",
        "last_contact": "",
    }
    response = await client.post("/api/leads/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["company"] == "Acme Corp"
    assert data["status"] == "new"

    response = await client.get("/api/leads/")
    assert response.status_code == 200
    assert len(response.json()) == 1

    response = await client.get("/api/leads/lead-1")
    assert response.status_code == 200
    assert response.json()["email"] == "john@acme.com"

    response = await client.patch("/api/leads/lead-1/status", json={"status": "contacted"})
    assert response.status_code == 200
    assert response.json()["status"] == "contacted"


@pytest.mark.anyio
async def test_campaigns_crud(client: AsyncClient):
    product_payload = {
        "id": "prod-camp",
        "name": "Campaign Product",
        "slug": "campaign-product",
        "published": True,
        "problem": "P",
        "target": "T",
        "description": "D",
        "features": [],
        "benefits": [],
    }
    await client.post("/api/products/", json=product_payload)

    payload = {
        "id": "camp-1",
        "name": "Test Campaign",
        "product_id": "prod-camp",
        "target": "Startups",
        "status": "running",
        "found": 100,
        "contacted": 50,
        "responded": 20,
        "interested": 10,
        "meetings": 5,
        "customers": 2,
    }
    response = await client.post("/api/campaigns/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Campaign"
    assert data["found"] == 100

    response = await client.get("/api/campaigns/")
    assert response.status_code == 200
    assert len(response.json()) == 1


@pytest.mark.anyio
async def test_dashboard_summary(client: AsyncClient):
    response = await client.get("/api/dashboard/summary")
    assert response.status_code == 200
    data = response.json()
    assert "new" in data
    assert "contacted" in data
    assert "responded" in data
    assert "meetings" in data
    assert "customers" in data
    assert "lost" in data


@pytest.mark.anyio
async def test_contact_endpoint(client: AsyncClient):
    product_payload = {
        "id": "prod-contact",
        "name": "Contact Product",
        "slug": "contact-product",
        "published": True,
        "problem": "P",
        "target": "T",
        "description": "D",
        "features": [],
        "benefits": [],
    }
    await client.post("/api/products/", json=product_payload)

    payload = {
        "name": "Jane Doe",
        "email": "jane@example.com",
        "company": "Example Inc",
        "message": "Interested in your product",
        "product_slug": "contact-product",
    }
    response = await client.post("/api/contact/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["company"] == "Example Inc"
    assert data["contact"] == "Jane Doe"
    assert data["status"] == "new"


@pytest.mark.anyio
async def test_emails_crud(client: AsyncClient):
    payload = {
        "id": "email-1",
        "lead_name": "Acme Corp",
        "product_name": "AI Pod",
        "status": "draft",
        "subject": "Hello",
        "body": "Body text",
    }
    response = await client.post("/api/emails/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["subject"] == "Hello"
    assert data["status"] == "draft"

    response = await client.get("/api/emails/")
    assert response.status_code == 200
    assert len(response.json()) == 1

    response = await client.get("/api/emails/email-1")
    assert response.status_code == 200
    assert response.json()["body"] == "Body text"


@pytest.mark.anyio
async def test_automations_crud(client: AsyncClient):
    payload = {
        "id": "auto-1",
        "name": "Test Automation",
        "status": "running",
        "last_run": "Just now",
        "result": "OK",
    }
    response = await client.post("/api/automations/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Automation"
    assert data["status"] == "running"

    response = await client.get("/api/automations/")
    assert response.status_code == 200
    assert len(response.json()) == 1

    response = await client.get("/api/automations/auto-1")
    assert response.status_code == 200
    assert response.json()["result"] == "OK"

    response = await client.patch("/api/automations/auto-1", json={"status": "stopped"})
    assert response.status_code == 200
    assert response.json()["status"] == "stopped"


@pytest.mark.anyio
async def test_content_crud(client: AsyncClient):
    payload = {
        "id": "content-1",
        "type": "blog_post",
        "title": "Test Blog",
        "status": "published",
        "date": "Aug 12, 2026",
        "excerpt": "Excerpt text",
        "image_url": "",
        "tag": "Product update",
    }
    response = await client.post("/api/content/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Blog"
    assert data["status"] == "published"

    response = await client.get("/api/content/")
    assert response.status_code == 200
    assert len(response.json()) == 1

    response = await client.get("/api/content/content-1")
    assert response.status_code == 200
    assert response.json()["excerpt"] == "Excerpt text"

    response = await client.patch("/api/content/content-1", json={"status": "draft"})
    assert response.status_code == 200
    assert response.json()["status"] == "draft"


@pytest.mark.anyio
async def test_auth_register_and_login(client: AsyncClient):
    payload = {
        "email": "admin@example.com",
        "name": "Admin User",
        "password": "StrongPass1",
    }
    response = await client.post("/api/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "admin@example.com"
    assert "id" in data

    response = await client.post("/api/auth/login", data={"username": "admin@example.com", "password": "StrongPass1"})
    assert response.status_code == 200
    token = response.json()
    assert token["token_type"] == "bearer"
    assert "access_token" in token

    response = await client.get("/api/auth/me", headers={"Authorization": f"Bearer {token['access_token']}"})
    assert response.status_code == 200
    assert response.json()["email"] == "admin@example.com"


@pytest.mark.anyio
async def test_auth_login_wrong_password(client: AsyncClient):
    response = await client.post("/api/auth/login", data={"username": "admin@example.com", "password": "wrong"})
    assert response.status_code == 400
