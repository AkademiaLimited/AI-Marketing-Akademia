export interface MarketingProduct {
  slug: string;
  name: string;
  accent: string;
  tint: string;
  dark: string;
  icon: React.ReactNode;
  visual: React.ReactNode;
  description: string;
  image_url?: string;
  website_url?: string;
  gallery?: React.ReactNode[];
  capabilities?: Array<{ icon: React.ReactNode; title: string; body: string }>;
}

export const PRODUCTS: MarketingProduct[] = [
  {
    slug: 'avatar',
    name: 'AI AVATAR AKADEMIA',
    accent: '#1F6F5C',
    tint: '#A7F3F0',
    dark: '#0C4A42',
    description: 'A 3D AI avatar platform bridging Japan and Uganda. Talk to lifelike avatar guides for culture, business etiquette, and Luganda phrases, run live video meetings with real-time speech translation and lip-synced avatar interpreters, or launch an AI-powered interview and recruiter mode.',
    image_url: 'https://ai-pod.net/images/image%20copy%2017.png',
    website_url: 'https://ai-avatar.akademia.co.jp',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <rect x="3" y="3" width="7" height="9" rx="1.5" />
        <rect x="14" y="3" width="7" height="5" rx="1.5" />
        <rect x="14" y="12" width="7" height="9" rx="1.5" />
        <rect x="3" y="16" width="7" height="5" rx="1.5" />
      </svg>
    ),
    visual: (
      <svg viewBox="0 0 200 140" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
        <rect x="20" y="20" width="60" height="45" rx="6" />
        <rect x="90" y="20" width="90" height="20" rx="4" />
        <rect x="90" y="48" width="70" height="17" rx="4" />
        <rect x="20" y="75" width="160" height="45" rx="6" />
        <line x1="40" y1="95" x2="120" y2="95" />
        <line x1="40" y1="105" x2="90" y2="105" />
        <circle cx="150" cy="100" r="12" />
        <path d="M146 100l3 3 5-6" />
      </svg>
    ),
  },
  {
    slug: 'pod',
    name: 'AIPOD',
    accent: '#4262FF',
    tint: '#E8EAFF',
    dark: '#1a2e99',
    description: 'An AI-powered daily reporting dashboard. Teams log in to submit and review structured daily reports, with account registration and secure sign-in built for organizations that need a consistent, automated pulse on daily work.',
    image_url: 'https://ai-pod.net/images/image%20copy%2019.png',
    website_url: 'https://ai-daily-report.akademia.co.jp/',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <rect x="3" y="3" width="7" height="9" rx="1.5" />
        <rect x="14" y="3" width="7" height="5" rx="1.5" />
        <rect x="14" y="12" width="7" height="9" rx="1.5" />
        <rect x="3" y="16" width="7" height="5" rx="1.5" />
      </svg>
    ),
    visual: (
      <svg viewBox="0 0 200 140" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
        <rect x="20" y="20" width="60" height="45" rx="6" />
        <rect x="90" y="20" width="90" height="20" rx="4" />
        <rect x="90" y="48" width="70" height="17" rx="4" />
        <rect x="20" y="75" width="160" height="45" rx="6" />
        <line x1="40" y1="95" x2="120" y2="95" />
        <line x1="40" y1="105" x2="90" y2="105" />
        <circle cx="150" cy="100" r="12" />
        <path d="M146 100l3 3 5-6" />
      </svg>
    ),
  },
  {
    slug: 'world',
    name: 'VIRTUAL WORLD',
    accent: '#8B5CF6',
    tint: '#EDE9FE',
    dark: '#5B21B6',
    description: 'A persistent virtual office and event space built on the WorkAdventure engine. Teams and attendees move around as characters in a 2D map, bumping into colleagues, joining spontaneous video calls, and collaborating the way they would in a real shared space — no scheduled meeting links required.',
    image_url: 'https://ai-pod.net/images/image%20copy%2018.png',
    website_url: 'https://vf.akademia.co.jp/',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="12" cy="12" r="10" />
        <path d="M2 12h20M12 2a15 15 0 014 10 15 15 0 01-4 10 15 15 0 01-4-10A15 15 0 0112 2z" />
      </svg>
    ),
    visual: (
      <svg viewBox="0 0 200 140" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="80" cy="70" r="45" />
        <path d="M35 70h90M80 25a40 40 0 015 50 40 40 0 01-5 50" />
        <path d="M50 45c10-5 25-8 40-5M50 95c10 5 25 8 40 5" />
        <rect x="120" y="30" width="60" height="80" rx="8" />
        <path d="M135 55h30M135 70h20M135 85h25" />
        <circle cx="40" cy="40" r="6" />
        <path d="M36 40l3 3 5-6" />
      </svg>
    ),
    gallery: [
      <svg key="g1" viewBox="0 0 120 120" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <rect x="10" y="30" width="100" height="80" rx="8" />
        <path d="M30 70h20M30 85h35M75 60h10M75 75h25" />
      </svg>,
      <svg key="g2" viewBox="0 0 120 120" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="60" cy="60" r="35" />
        <path d="M45 60l10 10 20-25" />
      </svg>,
      <svg key="g3" viewBox="0 0 120 120" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <rect x="15" y="25" width="90" height="70" rx="8" />
        <path d="M30 50h25M30 65h40M30 80h15" />
      </svg>,
      <svg key="g4" viewBox="0 0 120 120" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M60 20l40 60H20z" />
        <circle cx="60" cy="70" r="8" />
      </svg>,
    ],
  },
  {
    slug: 'translation',
    name: 'UgaJapa Translation',
    accent: '#EC4899',
    tint: '#FCE7F3',
    dark: '#9D1A5B',
    description: 'A global translation API and dashboard purpose-built for Mattermost plugins, combining a neural translation engine, a voice engine for speech-to-text and subtitles, a 197-language global engine, text-to-speech, and a resilient always-on fallback bot — with per-user API keys, quality scoring, and usage-based billing.',
    image_url: 'https://ai-pod.net/images/image%20copy%2020.png',
    website_url: 'https://uj-tc-api.akademia.co.jp/',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <g transform="rotate(-15 12 12)">
          <circle cx="12" cy="12" r="8" />
        </g>
        <g transform="rotate(25 12 12)">
          <path d="M9 15l3-3 3 3" />
        </g>
        <path d="M2 12h20M12 2a15 15 0 014 10 15 15 0 01-4 10 15 15 0 01-4-10A15 15 0 0112 2z" />
      </svg>
    ),
    visual: (
      <svg viewBox="0 0 200 140" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
        <g transform="translate(30, 25)">
          <rect x="0" y="0" width="140" height="100" rx="10" />
          <path d="M20 30h100M20 50h100M20 70h70M20 90h80" />
          <circle cx="140" cy="45" r="14" />
          <path d="M133 45l7 7 14-14" />
        </g>
      </svg>
    ),
    capabilities: [
      { icon: <svg viewBox="0 0 24 24"><path d="M12 2l9 21H3z" /></svg>, title: 'Neural translation', body: 'Optimised for African languages, Japanese, and complex language pairs.' },
      { icon: <svg viewBox="0 0 24 24"><path d="M12 1a11 11 0 0110 17.9V12l-3-3" /></svg>, title: 'Voice engine', body: 'Speech-to-text, subtitles, and text-to-speech in 197 languages.' },
      { icon: <svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10" /><path d="M12 2v10l8 4" /></svg>, title: 'Global engine', body: 'Always-on fallback bot with per-user API keys and usage-based billing.' },
    ],
  },
  {
    slug: 'dojo',
    name: 'AI DOJO',
    accent: '#FFD02F',
    tint: '#FEF3C7',
    dark: '#92400E',
    description: 'An immersive Japanese language role-play trainer. Learners practice real-time voice conversations with AI characters across 8+ realistic scenario domains — restaurants, travel, business, healthcare, shopping, school life — with instant feedback, XP, and streak tracking to keep learners coming back.',
    image_url: 'https://ai-pod.net/images/image%20copy%2021.png',
    website_url: 'https://ai-dojo-opal.vercel.app/',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M12 2v4M12 18v4M4.9 4.9l2.8 2.8M16.3 16.3l2.8 2.8M2 12h4M18 12h4M4.9 19.1l2.8-2.8M16.3 7.7l2.8-2.8" />
        <circle cx="12" cy="12" r="4" />
      </svg>
    ),
    visual: (
      <svg viewBox="0 0 200 140" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
        <rect x="30" y="20" width="140" height="100" rx="10" />
        <circle cx="80" cy="60" r="16" />
        <path d="M64 90c1.2-4 4-6 7.5-6s6.3 2 7.5 6" />
        <circle cx="140" cy="60" r="16" />
        <path d="M124 90c1.2-4 4-6 7.5-6s6.3 2 7.5 6" />
        <rect x="70" y="100" width="60" height="10" rx="3" />
      </svg>
    ),
    gallery: [
      <svg key="g1" viewBox="0 0 120 120" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <rect x="10" y="10" width="100" height="100" rx="12" />
        <circle cx="45" cy="50" r="14" />
        <path d="M31 85c1.2-3 4-5 7.5-5s6.3 2 7.5 5" />
        <circle cx="85" cy="50" r="14" />
        <path d="M71 85c1.2-3 4-5 7.5-5s6.3 2 7.5 5" />
      </svg>,
      <svg key="g2" viewBox="0 0 120 120" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <rect x="10" y="25" width="100" height="85" rx="10" />
        <circle cx="40" cy="55" r="12" />
        <path d="M28 85c1-2.5 3.5-4 6.5-4s5.5 1.5 6.5 4" />
        <rect x="65" y="40" width="35" height="8" rx="2" />
        <rect x="65" y="56" width="25" height="6" rx="2" />
        <rect x="65" y="70" width="30" height="6" rx="2" />
      </svg>,
      <svg key="g3" viewBox="0 0 120 120" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="60" cy="60" r="40" />
        <path d="M40 60l15 15 25-30" />
      </svg>,
    ],
  },
  {
    slug: 'recruiter',
    name: 'AI RECRUITER',
    accent: '#10B981',
    tint: '#D1FAE5',
    dark: '#065F46',
    description: 'An enterprise-grade AI recruitment operating system. Automates candidate screening, interview scheduling, and shortlisting, giving hiring teams a faster, more consistent way to evaluate talent at scale.',
    image_url: 'https://ai-pod.net/images/image%20copy%2017.png',
    website_url: 'https://ai-recruiter.akademia.co.jp',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="12" cy="8" r="4" />
        <path d="M4 20c1.2-4 4-6 7.5-6s6.3 2 7.5 6" />
      </svg>
    ),
    visual: (
      <svg viewBox="0 0 200 140" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="70" cy="50" r="22" />
        <path d="M34 120c1.2-4 4-6 7.5-6s6.3 2 7.5 6" />
        <rect x="110" y="30" width="70" height="16" rx="4" />
        <rect x="110" y="54" width="50" height="12" rx="4" />
        <rect x="110" y="74" width="60" height="12" rx="4" />
        <rect x="40" y="100" width="120" height="28" rx="6" />
        <line x1="55" y1="114" x2="100" y2="114" />
      </svg>
    ),
  },
];

export function getProductBySlug(slug: string): MarketingProduct | undefined {
  return PRODUCTS.find(p => p.slug === slug);
}

export function getProductByName(name: string): MarketingProduct | undefined {
  return PRODUCTS.find(p => p.name === name || p.name.replace('AI ', '') === name.replace('AI ', ''));
}

export function matchProduct(apiProduct: { name: string; slug: string }): MarketingProduct | undefined {
  return getProductBySlug(apiProduct.slug) || getProductByName(apiProduct.name);
}

export const NEWS_POSTS = [
  {
    id: 'n1',
    tag: 'Product update',
    date: 'Aug 18, 2026',
    title: 'AIPOD passes 500 businesses served across East Africa',
    excerpt: 'We marked a quiet milestone this week: more than 500 organisations are now using AIPOD to track tasks and generate reports. Most of them found us through referrals, which says less about us and more about how painful scattered spreadsheets still are.',
    image: 'https://picsum.photos/seed/ai-pod-500/480/320',
  },
  {
    id: 'n2',
    tag: 'Announcement',
    date: 'Aug 12, 2026',
    title: 'VIRTUAL WORLD launching to public beta next quarter',
    excerpt: 'After six months of closed testing with schools and travel groups, VIRTUAL WORLD is ready for a broader audience. The beta will open in October with expanded city tours and new language exercises.',
    image: 'https://picsum.photos/seed/ai-world-beta/480/320',
  },
  {
    id: 'n3',
    tag: 'Product update',
    date: 'Aug 3, 2026',
    title: 'AI RECRUITER now supports custom evaluation criteria',
    excerpt: 'The latest update to AI RECRUITER lets teams define their own scoring rubrics so the ranking engine matches what matters to them, not a generic industry benchmark.',
    image: 'https://picsum.photos/seed/ai-recruiter-criteria/480/320',
  },
  {
    id: 'n4',
    tag: 'Company news',
    date: 'Jul 22, 2026',
    title: 'Hiring our first sales and customer success lead in Nairobi',
    excerpt: 'We are growing the team that helps organisations pick the right product. The new hire will run demos, onboarding and follow-up support for the AI Marketer portfolio across East Africa.',
    image: 'https://picsum.photos/seed/ai-marketer-hire/480/320',
  },
];
