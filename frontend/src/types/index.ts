export interface Product {
  id: string;
  name: string;
  slug: string;
  published: boolean;
  problem: string;
  target: string;
  description: string;
  features: string[];
  benefits: string[];
  capabilities: Array<{
    icon: string;
    title: string;
    body: string;
  }>;
  category: string;
  price: string;
  image_url: string;
  marketing_status: string;
  marketing_result: string;
}

export type LeadStatus =
  | "new" | "contacted" | "responded" | "needs-followup"
  | "meeting" | "customer" | "lost";

export interface Lead {
  id: string;
  company: string;
  website: string;
  industry: string;
  location: string;
  contact: string;
  email: string;
  product_id: string;
  status: LeadStatus;
  problem: string;
  reasoning: string;
  last_contact: string;
}

export type CampaignStatus = "running" | "paused" | "completed";

export interface Campaign {
  id: string;
  name: string;
  product_id: string;
  target: string;
  status: CampaignStatus;
  found: number;
  contacted: number;
  responded: number;
  interested: number;
  meetings: number;
  customers: number;
}

export interface Email {
  id: string;
  lead_name: string;
  product_name: string;
  status: string;
  subject: string;
  body: string;
}

export interface Automation {
  id: string;
  name: string;
  status: string;
  last_run: string;
  result: string;
}

export interface MarketingActivity {
  id: string;
  workflow_run_id: string;
  lead_id: string;
  email_id: string;
  activity_type: string;
  channel: string;
  source_url: string;
  status: string;
  provider_message_id: string;
  details: string;
  error: string;
  created_at: string;
}

export interface Content {
  id: string;
  type: string;
  title: string;
  status: string;
  date: string;
  excerpt: string;
  image_url: string;
  tag: string;
}
