"use client";

import { useState, Suspense } from "react";
import { useSearchParams } from "next/navigation";

function ContactForm() {
  const searchParams = useSearchParams();
  const preset = searchParams.get('preset');

  const [showConfirm, setShowConfirm] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [product, setProduct] = useState(() => preset || "General Enquiry");
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError(null);
    setSubmitting(true);

    const form = e.currentTarget;
    const data = new FormData(form);
    const body = {
      name: data.get("name") as string,
      email: data.get("email") as string,
      company: data.get("company") as string,
      message: data.get("message") as string,
      product_slug: product === "General Enquiry" ? undefined : product.toLowerCase().replace("ai ", ""),
    };

    try {
      const res = await fetch("/api/contact", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });

      if (!res.ok) {
        const text = await res.text();
        throw new Error(`Something went wrong: ${text}`);
      }

      setShowConfirm(true);
      form.reset();
      setTimeout(() => {
        setShowConfirm(false);
      }, 5000);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <>
      <div className={`confirm ${showConfirm ? 'show' : ''}`}>
        <h3>Message sent</h3>
        <p>Thank you, someone from AI Marketer will get back to you shortly.</p>
      </div>

      {error && (
        <div className="confirm show" style={{ background: '#FFEBEE', borderColor: '#EF9A9A' }}>
          <h3 style={{ color: '#C62828' }}>Error</h3>
          <p style={{ color: '#B71C1C' }}>{error}</p>
        </div>
      )}

      <form onSubmit={handleSubmit}>
        <div className="field-row">
          <div className="field">
            <label htmlFor="name">Name</label>
            <input id="name" type="text" name="name" required placeholder="Your name" />
          </div>
          <div className="field">
            <label htmlFor="email">Email</label>
            <input id="email" type="email" name="email" required placeholder="you@company.com" />
          </div>
        </div>
        <div className="field-row">
          <div className="field">
            <label htmlFor="company">Company <span style={{ color: 'var(--ink-muted)', fontWeight: 400 }}>(if applicable)</span></label>
            <input id="company" type="text" name="company" placeholder="Company name" />
          </div>
          <div className="field">
            <label htmlFor="product">Product</label>
            <select id="product" value={product} onChange={(e) => setProduct(e.target.value)} name="product">
              {['AI Pod', 'AI Recruiter', 'AI Dojo', 'AI World', 'General Enquiry'].map(o => (
                <option key={o} value={o}>{o}</option>
              ))}
            </select>
          </div>
        </div>
        <div className="field">
          <label htmlFor="message">Message</label>
          <textarea id="message" name="message" rows={6} required placeholder="Tell us a bit about what you need..."></textarea>
        </div>
        <button type="submit" className="btn btn-primary btn-lg" disabled={submitting}>
          {submitting ? 'Sending...' : 'Send message'}
        </button>
      </form>
    </>
  );
}

export default function ContactPage() {
  return (
    <>
      <section className="hero hero-left" style={{ paddingBottom: 0 }}>
        <div className="wrap">
          <h1>Tell us what you&apos;re trying to solve.</h1>
        </div>
      </section>

      <section className="section-tight">
        <div className="wrap">
          <div className="contact-grid">
            <div>
              <Suspense fallback={<div>Loading form...</div>}>
                <ContactForm />
              </Suspense>
            </div>

            <div className="contact-info">
              <h3>Other ways to reach us</h3>
              <div className="ci-row">
                <div className="lab">Email</div>
                <div>gen@akademia.co.jp</div>
              </div>
              <div className="ci-row">
                <div className="lab">Phone</div>
                <div>+81 90-57563969</div>
              </div>
              <div className="ci-row">
                <div className="lab">Hours</div>
                <div>Mon–Fri, 9:00–17:00 EAT</div>
              </div>
              <div className="ci-row">
                <div className="lab">Products</div>
                <div>AI Pod · AI Recruiter · AI Dojo · AI World</div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </>
  );
}
