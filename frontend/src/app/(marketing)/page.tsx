import Link from "next/link";
import { apiFetch } from "@/lib/api";
import type { Product } from "@/types";
import { PRODUCTS, getProductBySlug, getProductByName } from "./_lib/marketing-config";

export default async function HomePage() {
  let apiProducts: Product[] = [];
  try {
    apiProducts = await apiFetch<Product[]>("/products");
  } catch {
    apiProducts = [];
  }

  const publishedProducts = apiProducts.filter((p) => p.published);

  return (
    <>
      <section className="hero hero-left">
        <div className="wrap">
           <h1>Six practical AI products. One place to find the right one.</h1>
          <div className="hero-cta">
            <Link href="/products" className="btn btn-primary btn-lg">Get started free</Link>
            <Link href="/contact" className="btn btn-secondary btn-lg">Book a demo</Link>
          </div>
          <div className="dock">
            {PRODUCTS.map((p) => (
              <Link key={p.slug} href={`/products/${p.slug}`} className="dock-tile" style={{ '--tile-accent': p.accent, '--tile-tint': p.tint } as React.CSSProperties}>
                <div className="dock-icon">{p.icon}</div>
                <div className="t-name">{p.name}</div>
                <div className="t-go">Learn more</div>
              </Link>
            ))}
          </div>
        </div>
      </section>

      <section className="section-tight">
        <div className="wrap">
          <div className="sec-head"><h2>Why AI Marketer</h2></div>
          <div className="why-grid">
            <div className="why-item">
              <div className="num">01</div>
              <h3>Six products, one place to start</h3>
              <p>You don&apos;t need to evaluate ten different AI vendors. We represent six practical tools and can point you to the one that actually fits.</p>
            </div>
            <div className="why-item">
              <div className="num">02</div>
              <h3>Plain explanations, not sales pitches</h3>
              <p>Ask what a product does and we&apos;ll tell you clearly including when it isn&apos;t the right fit for what you need.</p>
            </div>
            <div className="why-item">
              <div className="num">03</div>
              <h3>A real team on the other end</h3>
              <p>Contact goes to people who know these products, not an automated queue.</p>
            </div>
          </div>
        </div>
      </section>

      <section className="band">
        <div className="wrap">
          <div className="sec-head">
            <h2>Our products</h2>
            <p>Four tools, four different jobs. See what each one actually does.</p>
          </div>
          <div className="products-grid">
            {publishedProducts.length === 0 && (
              <div className="pcard full" style={{ gridColumn: '1 / -1' }}>
                <div className="pcard-body">
                  <h3>No products published yet</h3>
                  <p className="desc">Check back soon for our latest AI tools.</p>
                </div>
              </div>
            )}
            {publishedProducts.map((p) => {
              const m = getProductBySlug(p.slug) || getProductByName(p.name);
              const SvgComponent = m?.visual;
              const accent = m?.accent || '#050038';
              const tint = m?.tint || '#F5F5F7';
              const dark = m?.dark || '#000000';
              const desc = p.description || m?.description || '';

              return (
                <div key={p.id || p.slug} className="pcard" style={{ '--accent': accent, '--accent-tint': tint, '--accent-dark': dark } as React.CSSProperties}>
                  <div className="pcard-visual">
                    {SvgComponent}
                  </div>
                  <div className="pcard-body">
                    <h3>{p.name}</h3>
                    <p className="desc">{desc}</p>
                    <Link href={`/products/${p.slug}`} className="learn">Learn more</Link>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </section>
    </>
  );
}
