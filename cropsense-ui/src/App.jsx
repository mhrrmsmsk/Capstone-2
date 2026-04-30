import { Routes, Route, NavLink, useLocation } from 'react-router-dom'
import { LayoutDashboard, FlaskConical, Sliders, UploadCloud, BarChart2, Menu, X, Info, Languages, Sun, Moon, Sprout } from 'lucide-react'
import { useState } from 'react'
import { useLang } from './i18n.jsx'
import Dashboard from './pages/Dashboard'
import Predict from './pages/Predict'
import Optimize from './pages/Optimize'
import Batch from './pages/Batch'
import Analysis from './pages/Analysis'
import About from './pages/About'

const S = {
  nav: {
    position: 'sticky', top: 0, zIndex: 100,
    background: 'var(--nav-bg)',
    backdropFilter: 'blur(20px)',
    WebkitBackdropFilter: 'blur(20px)',
    borderBottom: '1px solid var(--border)',
  },
  navInner: {
    maxWidth: '1280px', margin: '0 auto',
    padding: '0 20px',
    display: 'flex', alignItems: 'center', justifyContent: 'space-between',
    height: '60px',
  },
  logo: { display: 'flex', alignItems: 'center', gap: '10px', textDecoration: 'none' },
  logoIcon: {
    width: '34px', height: '34px', borderRadius: '10px',
    background: 'linear-gradient(135deg, var(--accent), var(--accent2))',
    display: 'flex', alignItems: 'center', justifyContent: 'center',
    boxShadow: '0 4px 12px var(--accent-glow)',
    flexShrink: 0,
  },
  logoText: { fontFamily: "'Space Grotesk', sans-serif", fontWeight: 700, fontSize: '1.1rem', color: 'var(--text)' },
  logoAi: {
    fontSize: '0.6rem', fontWeight: 700, color: 'var(--accent)',
    background: 'var(--accent-glow)', border: '1px solid rgba(34,197,94,0.3)',
    borderRadius: '6px', padding: '1px 6px', letterSpacing: '0.08em',
  },
  desktopNav: { display: 'flex', alignItems: 'center', gap: '2px' },
  rightSide: { display: 'flex', alignItems: 'center', gap: '8px' },
  iconBtn: {
    display: 'flex', alignItems: 'center', justifyContent: 'center',
    width: '36px', height: '36px', borderRadius: '10px',
    background: 'var(--surface2)', border: '1px solid var(--border)',
    color: 'var(--text2)', cursor: 'pointer', transition: 'all 0.2s',
    outline: 'none',
  },
  langBtn: {
    display: 'flex', alignItems: 'center', gap: '6px',
    padding: '7px 14px', borderRadius: '10px',
    background: 'var(--surface2)', border: '1px solid var(--border)',
    color: 'var(--text2)', cursor: 'pointer', transition: 'all 0.2s',
    fontSize: '0.75rem', fontWeight: 700, outline: 'none', letterSpacing: '0.05em',
  },
}

function Navbar() {
  const [open, setOpen] = useState(false)
  const location = useLocation()
  const { lang, setLang, theme, toggleTheme, t } = useLang()

  const NAV = [
    { to: '/',         label: t('nav_dashboard'), icon: LayoutDashboard },
    { to: '/predict',  label: t('nav_predict'),   icon: FlaskConical },
    { to: '/optimize', label: t('nav_optimize'),  icon: Sliders },
    { to: '/batch',    label: t('nav_batch'),      icon: UploadCloud },
    { to: '/analysis', label: t('nav_analysis'),  icon: BarChart2 },
    { to: '/about',    label: t('nav_about'),      icon: Info },
  ]

  return (
    <nav style={S.nav}>
      <div style={S.navInner}>
        {/* Logo */}
        <NavLink to="/" style={S.logo}>
          <div style={S.logoIcon}>
            <Sprout size={17} color="#fff" />
          </div>
          <span style={S.logoText}>CropSense</span>
          <span style={S.logoAi} className="hide-mobile">AI</span>
        </NavLink>

        {/* Desktop nav */}
        <div style={S.desktopNav} className="hide-mobile" id="desktop-nav">
          {NAV.map(({ to, label, icon: Icon }) => {
            const active = to === '/' ? location.pathname === '/' : location.pathname.startsWith(to)
            return (
              <NavLink
                key={to}
                to={to}
                className={`nav-pill${active ? ' active' : ''}`}
              >
                <Icon size={14} />
                {label}
              </NavLink>
            )
          })}
        </div>

        {/* Right controls */}
        <div style={S.rightSide}>
          <button
            style={S.langBtn}
            onClick={() => setLang(l => l === 'en' ? 'tr' : 'en')}
            title="Switch language"
            onMouseEnter={e => { e.currentTarget.style.borderColor = 'var(--accent)'; e.currentTarget.style.color = 'var(--accent)' }}
            onMouseLeave={e => { e.currentTarget.style.borderColor = 'var(--border)'; e.currentTarget.style.color = 'var(--text2)' }}
          >
            <Languages size={13} />
            {lang === 'en' ? 'TR' : 'EN'}
          </button>

          <button
            style={S.iconBtn}
            onClick={toggleTheme}
            title={theme === 'dark' ? 'Light mode' : 'Dark mode'}
            onMouseEnter={e => { e.currentTarget.style.borderColor = 'var(--accent)'; e.currentTarget.style.color = 'var(--accent)' }}
            onMouseLeave={e => { e.currentTarget.style.borderColor = 'var(--border)'; e.currentTarget.style.color = 'var(--text2)' }}
          >
            {theme === 'dark' ? <Sun size={15} /> : <Moon size={15} />}
          </button>

          {/* Mobile burger */}
          <button
            style={{ ...S.iconBtn, display: 'none' }}
            id="burger-btn"
            className="show-mobile"
            onClick={() => setOpen(o => !o)}
          >
            {open ? <X size={18} /> : <Menu size={18} />}
          </button>
        </div>
      </div>

      {/* Mobile menu */}
      {open && (
        <div
          className="slide-down"
          style={{
            borderTop: '1px solid var(--border)',
            background: 'var(--nav-bg)',
            backdropFilter: 'blur(20px)',
            padding: '12px 16px 16px',
            display: 'flex', flexDirection: 'column', gap: '4px',
          }}
        >
          {NAV.map(({ to, label, icon: Icon }) => {
            const active = to === '/' ? location.pathname === '/' : location.pathname.startsWith(to)
            return (
              <NavLink
                key={to}
                to={to}
                onClick={() => setOpen(false)}
                className={`nav-pill${active ? ' active' : ''}`}
                style={{ justifyContent: 'flex-start' }}
              >
                <Icon size={15} />
                {label}
              </NavLink>
            )
          })}
        </div>
      )}

      <style>{`
        @media (min-width: 768px) {
          #desktop-nav { display: flex !important; }
          #burger-btn  { display: none !important; }
          .show-mobile { display: none !important; }
        }
        @media (max-width: 767px) {
          #desktop-nav { display: none !important; }
          #burger-btn  { display: flex !important; }
        }
      `}</style>
    </nav>
  )
}

export default function App() {
  const { t } = useLang()
  return (
    <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <Navbar />

      <main style={{ flex: 1, maxWidth: '1280px', width: '100%', margin: '0 auto', padding: '32px 20px' }}>
        <Routes>
          <Route path="/"         element={<Dashboard />} />
          <Route path="/predict"  element={<Predict />} />
          <Route path="/optimize" element={<Optimize />} />
          <Route path="/batch"    element={<Batch />} />
          <Route path="/analysis" element={<Analysis />} />
          <Route path="/about"    element={<About />} />
        </Routes>
      </main>

      {/* Footer */}
      <footer>
        <div className="footer-line" />
        <div style={{
          maxWidth: '1280px', margin: '0 auto',
          padding: '24px 20px',
          display: 'flex', flexWrap: 'wrap', alignItems: 'center', justifyContent: 'space-between', gap: '12px',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <div style={{
              width: '26px', height: '26px', borderRadius: '8px',
              background: 'linear-gradient(135deg, var(--accent), var(--accent2))',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
            }}>
              <Sprout size={13} color="#fff" />
            </div>
            <span style={{ fontWeight: 700, fontSize: '0.85rem', color: 'var(--text2)', fontFamily: "'Space Grotesk', sans-serif" }}>CropSense AI</span>
          </div>
          <p style={{ fontSize: '0.72rem', color: 'var(--text3)', textAlign: 'center' }}>{t('footer')}</p>
          <div style={{ display: 'flex', gap: '6px', alignItems: 'center' }}>
            <span className="dot-live" style={{ width: '6px', height: '6px' }} />
            <span style={{ fontSize: '0.7rem', color: 'var(--text3)' }}>All systems operational</span>
          </div>
        </div>
      </footer>
    </div>
  )
}
