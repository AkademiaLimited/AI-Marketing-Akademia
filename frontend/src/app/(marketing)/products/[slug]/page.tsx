import { apiFetch } from "@/lib/api";
import Link from "next/link";
import { notFound } from "next/navigation";
import { getProductBySlug, getProductByName } from "../../_lib/marketing-config";
import type { Product } from "@/types";

export default async function ProductDetailPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  let product: Product | null = null;
  try {
    product = await apiFetch<Product>(`/products/${slug}`);
  } catch {
    notFound();
  }

  if (!product) {
    notFound();
  }

  const m = getProductBySlug(product.slug) || getProductByName(product.name);
  const tint = m?.tint || '#F5F5F7';
  const dark = m?.dark || '#000000';
  const visual = m?.visual;
  const gallery = m?.gallery;
  const imageUrl = m?.image_url || product.image_url;
  const websiteUrl = m?.website_url || product.website_url;
  const showGallery = ['dojo', 'world', 'avatar', 'translation'].includes(product.slug);

  return (
    <>
      <section className="pd-hero">
        <div className="wrap">
          <div className="pd-hero-grid">
            <div>
           <h1>{product.name}</h1>
               <p className="pd-tagline">{product.description}</p>
               <p className="pd-desc">{product.problem}</p>
               {websiteUrl && (
                 <a href={websiteUrl} target="_blank" rel="noopener noreferrer" className="learn">Visit product site →</a>
               )}
               <div className="hero-cta">
                <Link href="/contact" className="btn btn-primary btn-lg">Get started free</Link>
                <Link href="/contact" className="btn btn-secondary btn-lg">Book a demo</Link>
              </div>
            </div>
            <div className="pd-visual" style={{ background: tint }}>
              {visual}
            </div>
          </div>
          {imageUrl && (
            <div className="mt-8">
              <img src={imageUrl} alt={product.name} className="w-full rounded-lg" loading="lazy" />
            </div>
          )}
        </div>
      </section>

      {showGallery && gallery && (
        <section className="section-tight">
          <div className="wrap">
            <div className="gallery-grid">
              {gallery.map((item, i) => (
                <div key={i} className="gallery-tile" style={{ background: tint }}>
                  {item}
                </div>
              ))}
            </div>
          </div>
        </section>
      )}

      {product.capabilities && product.capabilities.length > 0 && (
        <section className="section-tight">
          <div className="wrap">
            <div className="sec-head">
              <h2>Capabilities</h2>
            </div>
            <div className="cap-grid">
              {product.capabilities.map((cap, i) => (
                <div key={i} className="cap-card" style={{ '--accent-tint': tint, '--accent-dark': dark } as React.CSSProperties}>
                  <div className="ic">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M12 2v4M12 18v4M4.9 4.9l2.8 2.8M16.3 16.3l2.8 2.8M2 12h4M18 12h4M4.9 19.1l2.8-2.8M16.3 7.7l2.8-2.8" />
                      <circle cx="12" cy="12" r="3" />
                    </svg>
                  </div>
                  <h4>{cap.title}</h4>
                  <p>{cap.body}</p>
                </div>
              ))}
            </div>
          </div>
        </section>
      )}

      <section className="section-tight">
        <div className="wrap">
          <div className="who-row">
            <div>
              <h3>The problem</h3>
              <p>{product.problem}</p>
            </div>
            <div>
              <h3>Who it&apos;s for</h3>
              <p>{product.target}</p>
            </div>
          </div>
        </div>
      </section>

      <section>
        <div className="wrap">
          <div className="cta-band">
            <div>
              <h3>Want to talk about {product.name}?</h3>
              <p>Tell us what you&apos;re trying to solve and we&apos;ll point you in the right direction.</p>
            </div>
            <Link href="/contact" className="btn btn-primary btn-lg">Contact us</Link>
          </div>
        </div>
      </section>
    </>
  );
}
