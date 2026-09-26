# Content Distribution Map

## How Content Flows Through the System

### The Complete Journey

```
[Admin creates product or adds lead]
              │
              ▼
[AI generates content]
  - Groq writes social captions
  - Groq writes email drafts
  - Groq qualifies leads
              │
              ▼
[Content stored in database]
  - generated_content table (captions, hashtags)
  - emails table (drafts)
  - leads table (status, reasoning)
              │
              ▼
[Admin reviews and approves]
  - Approve email draft → triggers email send
  - Publish product → triggers social posting
              │
              ▼
[Platform APIs publish content]
  - Instagram Graph API
  - LinkedIn UGC API
  - Twitter API v2
  - Email provider (Resend/SendGrid/Mailgun)
              │
              ▼
[Real people see the content]
  - Instagram followers
  - LinkedIn network
  - Twitter followers
  - Email recipients
              │
              ▼
[They visit aiakademia.com]
  - Browse products
  - Fill contact form
              │
              ▼
[Lead enters the system]
  - Status: new
  - Admin is notified
  - AI researches the lead
  - Personalized email is drafted
  - Admin approves → email is sent
  - Lead responds → meeting → customer
```

## Where Each Content Type Lands

### Social Media Posts

| Platform | API Used | Content Type | Where It Lands | Who Sees It |
|----------|---------|-------------|---------------|-------------|
| Instagram | Graph API | Image post with caption + hashtags | Business/Creator account feed | Followers + explore page |
| LinkedIn | UGC API | Text + image post | Company page feed | Company connections + network |
| Twitter/X | API v2 | Tweet with text + optional image | Timeline | Followers + timeline |

**Consumer:** Real people browsing social platforms who match the target audience for the product.

**How the API helps:**
- Instagram Graph API: Creates media container, then publishes it. Requires a Facebook App, Business/Creator Instagram account, and Page Access Token.
- LinkedIn UGC API: Creates a post on the company page. Requires a LinkedIn App and company page admin access.
- Twitter API v2: Creates a tweet. Requires a Twitter Developer App and Bearer Token.

### Email Outreach

| Provider | API Used | Content Type | Where It Lands | Who Sees It |
|----------|---------|-------------|---------------|-------------|
| Resend | POST /emails | Personalized outreach email | Recipient inbox | The B2B lead |
| SendGrid | POST /v3/mail/send | Personalized outreach email | Recipient inbox | The B2B lead |
| Mailgun | POST /v3/messages | Personalized outreach email | Recipient inbox | The B2B lead |
| SMTP | smtplib | Personalized outreach email | Recipient inbox | The B2B lead |

**Consumer:** The specific B2B lead — a real person at a real company who receives a personalized email referencing their company's specific situation.

**How the API helps:**
- Handles actual email delivery (currently the system only saves drafts)
- Provides delivery confirmation, open tracking, click tracking
- Handles retries for failed deliveries
- Manages bounce and complaint rates

### Website Content (Blog/News)

| Content Type | Where It's Stored | Where It Lands | Who Sees It |
|-------------|------------------|---------------|-------------|
| Blog posts | content table | /blog or /news page (needs to be built) | Website visitors |
| News items | content table | /blog or /news page (needs to be built) | Website visitors |
| Product pages | products table | /products and /products/{slug} | All website visitors |

**Consumer:** Potential customers browsing the website who are researching AI tools before contacting sales.

### Product Pages (Already Working)

**Where it lands:** `/products` (list) and `/products/{slug}` (detail)
**Who sees it:** Anyone visiting aiakademia.com
**Content source:** Manual admin entry via the Products page in the admin dashboard

## Platform API Requirements

### Social Media APIs

| Platform | What You Need | Cost | Effort |
|----------|--------------|------|--------|
| Instagram | Facebook App, Business/Creator account, Page Access Token | Free | Medium |
| LinkedIn | LinkedIn App, Company Page admin, OAuth token | Free | Medium |
| Twitter | Twitter Developer App, API Key + Secret, Bearer Token | Free (limited) | Low |

### Email APIs

| Provider | What You Need | Cost | Effort |
|----------|--------------|------|--------|
| Resend | API key from resend.com | Free tier + paid | Low |
| SendGrid | API key from sendgrid.com | Free tier + paid | Low |
| Mailgun | API key from mailgun.com | Free tier + paid | Low |
| SMTP | Server credentials | Varies | Low |

## The Gap: What's Missing

| Feature | Current State | What's Needed |
|---------|--------------|---------------|
| Social publishing | Simulated (fake URLs) | Real API calls to Instagram/LinkedIn/Twitter |
| Email sending | Drafts only | Real email provider integration |
| Blog/news page | Missing public route | New frontend page rendering content table |
| Lead discovery | Synthetic only | Real search API (Google/Bing) |
| Engagement tracking | None | Webhook handlers for opens/clicks/likes |

## The Key File

The single point where fake publishing happens is:
`backend/app/tasks/content.py` → `_publish_to_platform()` function (line 122)

Replace:
```python
post_url = f"https://{platform}.com/p/{uuid.uuid4().hex[:12]}"
```

With real API calls to each platform. Everything else in the pipeline is already built.