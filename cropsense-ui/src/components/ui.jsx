/* All components use CSS variables from index.css for dark/light theming */

export function Card({ children, className = '', glow = false }) {
  return (
    <div
      className={className}
      style={{
        background: 'var(--surface)',
        border: '1px solid var(--border)',
        borderRadius: '16px',
        padding: '20px',
        boxShadow: glow ? 'var(--glow-green), var(--card-shadow)' : 'var(--card-shadow)',
        transition: 'box-shadow 0.2s, border-color 0.2s',
      }}
    >
      {children}
    </div>
  )
}

export function StatCard({ label, value, sub, accent = 'emerald', icon }) {
  const colors = {
    emerald: { glow: 'var(--accent-glow)',  txt: 'var(--accent)',  border: 'rgba(34,197,94,0.25)',  cls: 'stat-glow-green'  },
    blue:    { glow: 'var(--blue-glow)',    txt: 'var(--blue)',    border: 'rgba(59,130,246,0.25)',  cls: 'stat-glow-blue'   },
    violet:  { glow: 'var(--violet-glow)',  txt: 'var(--violet)',  border: 'rgba(139,92,246,0.25)', cls: 'stat-glow-violet' },
    amber:   { glow: 'var(--amber-glow)',   txt: 'var(--amber)',   border: 'rgba(245,158,11,0.25)', cls: 'stat-glow-amber'  },
  }[accent] || { glow: 'var(--accent-glow)', txt: 'var(--accent)', border: 'rgba(34,197,94,0.25)', cls: 'stat-glow-green' }

  return (
    <div
      className={`fade-in ${colors.cls}`}
      style={{
        background: `linear-gradient(135deg, ${colors.glow}, var(--surface))`,
        border: `1px solid ${colors.border}`,
        borderRadius: '16px',
        padding: '20px',
        position: 'relative',
        overflow: 'hidden',
      }}
    >
      {icon && (
        <div style={{ color: colors.txt, marginBottom: '12px', opacity: 0.8 }}>{icon}</div>
      )}
      <p style={{ fontSize: '0.68rem', color: 'var(--text3)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: '6px' }}>{label}</p>
      <p style={{ fontSize: '2rem', fontWeight: 800, color: colors.txt, lineHeight: 1, fontFamily: "'Space Grotesk', sans-serif" }}>{value}</p>
      {sub && <p style={{ fontSize: '0.72rem', color: 'var(--text3)', marginTop: '6px' }}>{sub}</p>}
    </div>
  )
}

export function Btn({ children, onClick, disabled, variant = 'primary', type = 'button', className = '' }) {
  const styles = {
    primary: {
      background: 'linear-gradient(135deg, var(--accent) 0%, var(--accent2) 100%)',
      color: '#fff',
      border: 'none',
      boxShadow: '0 4px 14px var(--accent-glow)',
    },
    secondary: {
      background: 'var(--surface2)',
      color: 'var(--text)',
      border: '1px solid var(--border2)',
      boxShadow: 'none',
    },
    danger: {
      background: 'var(--red-glow)',
      color: 'var(--red)',
      border: '1px solid rgba(239,68,68,0.3)',
      boxShadow: 'none',
    },
  }[variant] || {}

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={className}
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: '8px',
        padding: '10px 18px',
        borderRadius: '12px',
        fontSize: '0.875rem',
        fontWeight: 600,
        cursor: disabled ? 'not-allowed' : 'pointer',
        opacity: disabled ? 0.5 : 1,
        transition: 'all 0.2s',
        outline: 'none',
        fontFamily: 'inherit',
        ...styles,
      }}
      onMouseEnter={e => { if (!disabled) e.currentTarget.style.filter = 'brightness(1.12)' }}
      onMouseLeave={e => { e.currentTarget.style.filter = 'brightness(1)' }}
    >
      {children}
    </button>
  )
}

export function Input({ label, value, onChange, type = 'number', placeholder, step }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}>
      {label && (
        <label style={{ fontSize: '0.7rem', fontWeight: 600, color: 'var(--text3)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
          {label}
        </label>
      )}
      <input
        type={type}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        step={step}
        style={{
          background: 'var(--bg2)',
          border: '1px solid var(--border2)',
          borderRadius: '10px',
          padding: '9px 12px',
          fontSize: '0.875rem',
          color: 'var(--text)',
          outline: 'none',
          width: '100%',
          transition: 'border-color 0.2s, box-shadow 0.2s',
          fontFamily: 'inherit',
        }}
        onFocus={e => {
          e.target.style.borderColor = 'var(--accent)'
          e.target.style.boxShadow = '0 0 0 3px var(--accent-glow)'
        }}
        onBlur={e => {
          e.target.style.borderColor = 'var(--border2)'
          e.target.style.boxShadow = 'none'
        }}
      />
    </div>
  )
}

export function Select({ label, value, onChange, options = [] }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}>
      {label && (
        <label style={{ fontSize: '0.7rem', fontWeight: 600, color: 'var(--text3)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
          {label}
        </label>
      )}
      <select
        value={value}
        onChange={onChange}
        style={{
          background: 'var(--bg2)',
          border: '1px solid var(--border2)',
          borderRadius: '10px',
          padding: '9px 12px',
          fontSize: '0.875rem',
          color: 'var(--text)',
          outline: 'none',
          width: '100%',
          transition: 'border-color 0.2s, box-shadow 0.2s',
          fontFamily: 'inherit',
          cursor: 'pointer',
          appearance: 'none',
          backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%2364748b' stroke-width='2'%3E%3Cpath d='m6 9 6 6 6-6'/%3E%3C/svg%3E")`,
          backgroundRepeat: 'no-repeat',
          backgroundPosition: 'right 12px center',
          paddingRight: '32px',
        }}
        onFocus={e => {
          e.target.style.borderColor = 'var(--accent)'
          e.target.style.boxShadow = '0 0 0 3px var(--accent-glow)'
        }}
        onBlur={e => {
          e.target.style.borderColor = 'var(--border2)'
          e.target.style.boxShadow = 'none'
        }}
      >
        {options.map(o => {
          const val = typeof o === 'object' ? o.value : o
          const lbl = typeof o === 'object' ? o.label : o
          return <option key={val} value={val} style={{ background: 'var(--bg3)', color: 'var(--text)' }}>{lbl}</option>
        })}
      </select>
    </div>
  )
}

export function Badge({ children, color = 'emerald' }) {
  const styles = {
    emerald: { bg: 'var(--accent-glow)',  color: 'var(--accent)',  border: 'rgba(34,197,94,0.3)'  },
    blue:    { bg: 'var(--blue-glow)',    color: 'var(--blue)',    border: 'rgba(59,130,246,0.3)'  },
    amber:   { bg: 'var(--amber-glow)',   color: 'var(--amber)',   border: 'rgba(245,158,11,0.3)'  },
    red:     { bg: 'var(--red-glow)',     color: 'var(--red)',     border: 'rgba(239,68,68,0.3)'   },
    slate:   { bg: 'var(--surface2)',     color: 'var(--text2)',   border: 'var(--border2)'        },
    violet:  { bg: 'var(--violet-glow)',  color: 'var(--violet)',  border: 'rgba(139,92,246,0.3)'  },
  }[color] || { bg: 'var(--accent-glow)', color: 'var(--accent)', border: 'rgba(34,197,94,0.3)' }

  return (
    <span style={{
      display: 'inline-flex',
      alignItems: 'center',
      padding: '2px 10px',
      borderRadius: '99px',
      fontSize: '0.68rem',
      fontWeight: 600,
      background: styles.bg,
      color: styles.color,
      border: `1px solid ${styles.border}`,
      letterSpacing: '0.02em',
    }}>
      {children}
    </span>
  )
}

export function Spinner() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '64px 16px', gap: '16px' }}>
      <div style={{ position: 'relative', width: '44px', height: '44px' }}>
        <div style={{
          position: 'absolute', inset: 0,
          borderRadius: '50%',
          border: '3px solid var(--border2)',
          borderTopColor: 'var(--accent)',
          animation: 'spin 0.8s linear infinite',
        }} />
        <div style={{
          position: 'absolute', inset: '8px',
          borderRadius: '50%',
          border: '2px solid var(--border)',
          borderBottomColor: 'var(--blue)',
          animation: 'spin 1.2s linear infinite reverse',
        }} />
      </div>
      <p style={{ fontSize: '0.75rem', color: 'var(--text3)' }}>Loading…</p>
      <style>{`@keyframes spin { to { transform: rotate(360deg) } }`}</style>
    </div>
  )
}

export function ErrorMsg({ msg }) {
  if (!msg) return null
  return (
    <div style={{
      background: 'var(--red-glow)',
      border: '1px solid rgba(239,68,68,0.3)',
      color: 'var(--red)',
      borderRadius: '12px',
      padding: '12px 16px',
      fontSize: '0.875rem',
      display: 'flex',
      alignItems: 'center',
      gap: '8px',
    }}>
      <span style={{ fontSize: '1rem' }}>⚠</span> {msg}
    </div>
  )
}

export function SectionTitle({ title, sub }) {
  return (
    <div style={{ marginBottom: '24px' }}>
      <h1 style={{ fontSize: '1.6rem', fontWeight: 800, color: 'var(--text)', fontFamily: "'Space Grotesk', sans-serif", lineHeight: 1.2 }}>
        {title}
      </h1>
      {sub && <p style={{ color: 'var(--text2)', fontSize: '0.875rem', marginTop: '6px', lineHeight: 1.5 }}>{sub}</p>}
    </div>
  )
}
