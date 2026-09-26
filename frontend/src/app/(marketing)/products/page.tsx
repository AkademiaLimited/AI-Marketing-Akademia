import Link from "next/link";
import { apiFetch } from "@/lib/api";
import { getProductBySlug, getProductByName } from "../_lib/marketing-config";
import type { Product } from "@/types";

export const dynamic = 'force-dynamic';

export default async function ProductsOverviewPage() {
  let products: Product[] = [];
  try {
    products = await apiFetch<Product[]>("/products");
  } catch {
    products = [];
  }

  const published = products.filter((p) => p.published);

  return (
    <>
      <section className="hero hero-left" style={{ paddingBottom: 0 }}>
        <div className="wrap">
           <h1>Six practical AI tools. From one team.</h1>
        </div>
      </section>

      <section>
        <div className="wrap">
          <div className="products-grid">
            {published.length === 0 && (
              <div className="pcard full" style={{ gridColumn: '1 / -1' }}>
                <div className="pcard-body">
                  <h3>No products published yet</h3>
                  <p className="desc">Check back soon for our latest AI tools.</p>
                </div>
              </div>
            )}
            {published.map((p) => {
              const m = getProductBySlug(p.slug) || getProductByName(p.name);
              const SvgComponent = m?.visual;
              const accent = m?.accent || '#050038';
              const tint = m?.tint || '#F5F5F7';
              const dark = m?.dark || '#000000';
              const desc = p.description || m?.description || '';

              return (
                <div key={p.id} className="pcard full" style={{ '--accent': accent, '--accent-tint': tint, '--accent-dark': dark } as React.CSSProperties}>
                  <div className="pcard-visual">
                    {SvgComponent}
                  </div>
                  <div className="pcard-body">
                    <h3>{p.name}</h3>
                    <p className="desc">{desc}</p>
                    <div className="meta-row">
                      <div>
                        <div className="k">Problem it solves</div>
                        {p.problem}
                      </div>
                    </div>
                    <div className="meta-row">
                      <div>
                        <div className="k">Who it&apos;s for</div>
                        {p.target}
                      </div>
                    </div>
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
