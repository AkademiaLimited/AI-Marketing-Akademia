"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";

function NavLinks({ onNavigate }: { onNavigate: () => void }) {
  const pathname = usePathname();
  
  const isActive = (path: string) => {
    if (path === '/' && pathname === '/') return true;
    if (path !== '/' && pathname.startsWith(path)) return true;
    return false;
  };

  return (
    <>
      <Link href="/" className={isActive('/') ? 'active' : ''} onClick={onNavigate}>Home</Link>
      <Link href="/products" className={isActive('/products') ? 'active' : ''} onClick={onNavigate}>Products</Link>
      <Link href="/news" className={isActive('/news') ? 'active' : ''} onClick={onNavigate}>News</Link>
      <Link href="/about" className={isActive('/about') ? 'active' : ''} onClick={onNavigate}>About</Link>
      <Link href="/contact" className={isActive('/contact') ? 'active' : ''} onClick={onNavigate}>Contact</Link>
    </>
  );
}

export function Header() {
  const [mobileOpen, setMobileOpen] = useState(false);

  const closeMobile = () => setMobileOpen(false);

  return (
    <header>
      <div className="hd-inner">
        <Link href="/" className="logo" onClick={closeMobile}>
          <img src="/favicon.svg" className="mark" alt="Logo" />
          AI Marketer
        </Link>
        <nav className="mainnav">
          <NavLinks onNavigate={closeMobile} />
        </nav>
        <div className="hd-right">
          <Link href="/admin/login" className="btn btn-secondary">Admin login</Link>
          <Link href="/contact" className="btn btn-secondary" style={{ borderColor: 'transparent' }}>Contact sales</Link>
          <Link href="/products" className="btn btn-primary">Get started free</Link>
          <button className="hamburger" onClick={() => setMobileOpen(!mobileOpen)} aria-label="Toggle menu">
            {mobileOpen ? (
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M18 6L6 18M6 6l12 12"/></svg>
            ) : (
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="18" x2="21" y2="18"/></svg>
            )}
          </button>
        </div>
      </div>
      <div className={`mobile-menu ${mobileOpen ? 'open' : ''}`}>
        <NavLinks onNavigate={closeMobile} />
        <Link href="/admin/login" className="btn btn-secondary" onClick={closeMobile}>Admin login</Link>
        <Link href="/contact" className="btn btn-secondary" style={{ borderColor: 'transparent' }}>Contact sales</Link>
        <Link href="/products" className="btn btn-primary">Get started free</Link>
      </div>
    </header>
  );
}
