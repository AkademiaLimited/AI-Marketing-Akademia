# Ocoya vs AI Marketing Akademia: Competitive Analysis

## Executive Summary

**Ocoya** is a mature, fully-operational social media management platform with 20+ real API integrations. **AI Marketing Akademia** is an early-stage MVP with simulated publishing but stronger B2B lead research capabilities.

| Metric | Ocoya | Akademia |
|--------|-------|----------|
| Stage | Production/Mature | MVP/Early |
| Social platforms | 20+ real integrations | 0 (simulated) |
| AI content generation | Yes | Yes |
| AI lead research | No | Yes (LangGraph) |
| B2B lead management | No | Yes (dedicated module) |
| Email automation | No | Yes (draft + approval) |
| Website scraping | No | Yes (lead research) |
| Pricing | $29–$199/month | Not launched |
| Team size | Unknown (est. 50+) | 1 developer |

---

## What Ocoya Does

### Core Features
1. **20+ Social Platform Publishing** — Facebook, Instagram, X/Twitter, LinkedIn, Pinterest, Bluesky, Threads, YouTube, TikTok, and 12+ more (Discord, Slack, Twitch, WordPress, etc.)
2. **AI Content Generation** — Captions (37 languages), images, video, carousels
3. **Smart Scheduling** — Auto-best-time posting across networks from one calendar
4. **Brand Identity** — Learns brand voice/colors/fonts, applies to every post
5. **Design Studio** — In-house visual editor
6. **Campaigns** — Multi-post campaign planning
7. **Social Inbox** — Manage DMs, comments, mentions across all platforms
8. **Workflows** — Visual automation rules
9. **Analytics** — Performance tracking
10. **MCP & API** — AI assistants can operate the platform end-to-end

### Publishing Flow (Ocoya)
```
Describe brand → Describe post → AI generates caption + visuals →
Review/approve → Publish to ALL platforms simultaneously
```

### Integrations (20+)
| Category | Platforms |
|----------|-----------|
| Social | Facebook, Instagram, X, LinkedIn, Pinterest, Bluesky, Threads, YouTube, TikTok, Mastodon |
| Messaging | Telegram, Slack, Discord |
| Publishing | WordPress, Tumblr, DEV.to, Dribbble |
| E-commerce | WooCommerce |
| Other | Google Business, Kick, Twitch, Whop |

### Pricing
| Plan | Price | Users | Profiles | Credits |
|------|-------|-------|----------|---------|
| Starter | $29/mo | 1 | 5 | 300 |
| Team | $79/mo | 5 | 20 | 1,500 |
| Agency | $199/mo | 20 | 100 | 5,000 |

---

## What AI Marketing Akademia Does

### Core Features
1. **B2B Lead Management** — Full lead pipeline (new → contacted → responded → meeting → customer)
2. **AI Lead Research** — LangGraph workflow: fetch lead's website, qualify fit, draft personalized email
3. **AI Content Generation** — Groq generates platform-specific social copy
4. **Email Workflow** — Draft → Approve/Reject → Send (simulated currently)
5. **Product Management** — 4 AI products with marketing trigger
6. **Campaign Tracking** — Funnel metrics (found → contacted → ... → customer)
7. **Automation Metadata** — Record automation runs and results
8. **Workflow Auditing** — Full append-only activity log

### Publishing Flow (Akademia — Current)
```
Publish product → AI generates captions → Select channels →
SIMULATED publish (fake URLs stored in publish_logs)
```

### What's Missing vs Ocoya
| Ocoya Feature | Akademia Status | Effort to Build |
|--------------|-----------------|-----------------|
| Real social API integrations | **MISSING** (simulated) | Medium-High |
| AI image/video generation | **MISSING** | High |
| Visual design studio | **MISSING** | High |
| Social inbox (DMs/comments) | **MISSING** | High |
| Analytics dashboard | **MISSING** | Medium |
| Brand identity management | **MISSING** | Medium |
| MCP/API for AI assistants | **MISSING** | Medium |
| 37-language translation | **MISSING** | Low |

### What Akademia Has That Ocoya Lacks
| Feature | Akademia | Ocoya |
|---------|----------|-------|
| B2B lead management | ✅ Full pipeline | ❌ |
| AI lead research (website scraping) | ✅ LangGraph workflow | ❌ |
| Personalized email drafting | ✅ Per-lead AI drafts | ❌ |
| Lead qualification scoring | ✅ 0-1 fit score | ❌ |
| Contact form → lead pipeline | ✅ | ❌ |
| Product-specific AI workflows | ✅ | ❌ |

---

## Competitive Positioning

### Where Akademia Wins
1. **B2B lead research** — Ocoya has no lead management at all
2. **Personalized email outreach** — AI drafts per-lead emails referencing their company
3. **Website analysis** — AI reads lead's website to understand their business
4. **Niche focus** — AI marketing tools (Pod, Recruiter, Dojo, World) vs generic social media

### Where Ocoya Wins
1. **Real publishing** — Actual posts on 20+ platforms
2. **Maturity** — Production-ready with paying customers
3. **Visual generation** — Images, video, carousels
4. **Brand management** — Consistent voice across all content
5. **Team collaboration** — Multi-user, team plans

---

## Gap Analysis: What Akademia Needs to Match Ocoya

### Essential (Required for Production)
| Feature | Current | Needed | Effort |
|---------|---------|--------|--------|
| Social API integrations | Simulated | 3-5 platform APIs | Medium |
| Email delivery provider | Drafts only | Resend/SendGrid integration | Low |
| Blog/news public page | Missing | `/blog` or `/news` route | Low |
| Analytics dashboard | Basic counts | Conversion tracking, ROI | Medium |
| Real lead discovery | Synthetic only | Search API (Google/Bing) | Medium |

### Differentiating (What Makes Us Unique)
| Feature | Current | Why It Matters |
|---------|---------|----------------|
| LangGraph lead research | Implemented | Deep, personalized AI research |
| Per-lead email drafting | Implemented | Personal, not templated |
| Product marketing pipeline | Implemented | Connects products to leads |
| Workflow audit trail | Implemented | Full traceability for compliance |

---

## Go-to-Market Strategy

### Positioning Statement
> "AI Marketing Akademia automates B2B lead research and personalized outreach with AI, while Ocoya automates social media content and publishing."

### Target Customer
- B2B SaaS companies
- Small agency teams (5-20 people)
- Companies selling AI products

### Price Point
- Below Ocoya's $29 starter (or bundle with their existing product suite)

### Key Message
> "Don't just post content — intelligently research, qualify, and convert real B2B leads with AI."
