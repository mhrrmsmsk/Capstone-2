import { useState } from 'react'
import { Lightbulb, TrendingUp, TrendingDown, Thermometer, Droplets, Sun, Wind, Leaf, Scale } from 'lucide-react'
import { FlaskConical as Flask } from 'lucide-react'
import { Card } from './ui'
import { useLang } from '../i18n.jsx'

const ICON_MAP  = { thermometer: Thermometer, droplets: Droplets, flask: Flask, sun: Sun, wind: Wind, leaf: Leaf, scale: Scale }
const CAT_KEY   = { Climate: 'rec_cat_climate', Irrigation: 'rec_cat_irrigation', 'Soil pH': 'rec_cat_ph', Light: 'rec_cat_light', Humidity: 'rec_cat_humidity', Fertilizer: 'rec_cat_fertilizer', 'Nutrient Balance': 'rec_cat_balance' }
const CAT_COLOR = { Climate: 'var(--amber)', Irrigation: 'var(--blue)', 'Soil pH': 'var(--violet)', Light: 'var(--amber)', Humidity: 'var(--blue)', Fertilizer: 'var(--accent)', 'Nutrient Balance': 'var(--violet)' }
const CAT_GLOW  = { Climate: 'var(--amber-glow)', Irrigation: 'var(--blue-glow)', 'Soil pH': 'var(--violet-glow)', Light: 'var(--amber-glow)', Humidity: 'var(--blue-glow)', Fertilizer: 'var(--accent-glow)', 'Nutrient Balance': 'var(--violet-glow)' }

export default function RecommendationPanel({ recs, loading, cropName }) {
  const { t, lang } = useLang()
  const [activeTab, setActiveTab] = useState(null)

  if (loading) {
    return (
      <Card>
        <div style={{ display:'flex', alignItems:'center', gap:'10px', color:'var(--text3)', fontSize:'0.85rem' }}>
          <Lightbulb size={16} color="var(--amber)" />
          {t('rec_loading')}
        </div>
      </Card>
    )
  }

  if (!recs || recs.length === 0) return null

  // Group by category
  const grouped = {}
  recs.forEach(r => {
    if (!grouped[r.category]) grouped[r.category] = []
    grouped[r.category].push(r)
  })
  const categories = Object.keys(grouped)
  const selected = activeTab || categories[0]
  const selectedRecs = grouped[selected] || []

  // Summary line: count increase vs decrease
  const increaseCount = recs.filter(r => r.direction === 'increase').length
  const decreaseCount = recs.filter(r => r.direction === 'decrease').length

  return (
    <Card>
      {/* ── Header ── */}
      <div style={{ display:'flex', alignItems:'center', gap:'12px', marginBottom:'14px' }}>
        <div style={{ width:'34px', height:'34px', borderRadius:'10px', background:'var(--amber-glow)', border:'1px solid rgba(245,158,11,0.3)', display:'flex', alignItems:'center', justifyContent:'center', flexShrink:0 }}>
          <Lightbulb size={16} color="var(--amber)" />
        </div>
        <div>
          <p style={{ fontWeight:700, fontSize:'0.9rem', color:'var(--text)' }}>{t('rec_title')}</p>
          <p style={{ fontSize:'0.7rem', color:'var(--text3)' }}>{t('rec_sub')}</p>
        </div>
      </div>

      {/* ── Summary banner ── */}
      <div style={{ background:'var(--surface2)', border:'1px solid var(--border)', borderRadius:'12px', padding:'12px 16px', marginBottom:'14px', display:'flex', flexWrap:'wrap', gap:'12px', alignItems:'center' }}>
        {cropName && (
          <span style={{ fontSize:'0.78rem', color:'var(--text)', fontWeight:700 }}>
            🌱 {cropName}
          </span>
        )}
        <span style={{ fontSize:'0.75rem', color:'var(--text2)' }}>
          {t('rec_total', { n: recs.length }) || `${recs.length} ${t('rec_title').toLowerCase()}`}
        </span>
        <span style={{ display:'flex', alignItems:'center', gap:'4px', fontSize:'0.72rem', color:'var(--accent)' }}>
          <TrendingUp size={12} /> {increaseCount} {t('rec_increase')}
        </span>
        <span style={{ display:'flex', alignItems:'center', gap:'4px', fontSize:'0.72rem', color:'var(--red)' }}>
          <TrendingDown size={12} /> {decreaseCount} {t('rec_decrease')}
        </span>
        <span style={{ fontSize:'0.72rem', color:'var(--text3)', marginLeft:'auto' }}>
          {categories.length} {lang === 'tr' ? 'kategori' : 'categories'}
        </span>
      </div>

      {/* ── Category tabs ── */}
      <div style={{ display:'flex', flexWrap:'wrap', gap:'6px', marginBottom:'14px' }}>
        {categories.map(cat => {
          const Icon  = ICON_MAP[grouped[cat][0]?.icon] || Leaf
          const color = CAT_COLOR[cat] || 'var(--accent)'
          const glow  = CAT_GLOW[cat]  || 'var(--accent-glow)'
          const isActive = selected === cat
          return (
            <button
              key={cat}
              onClick={() => setActiveTab(cat)}
              style={{
                display:'flex', alignItems:'center', gap:'6px',
                padding:'6px 12px', borderRadius:'99px',
                background: isActive ? glow : 'var(--surface2)',
                border: `1px solid ${isActive ? color : 'var(--border)'}`,
                color: isActive ? color : 'var(--text3)',
                fontSize:'0.72rem', fontWeight: isActive ? 700 : 500,
                cursor:'pointer', transition:'all 0.15s',
              }}
            >
              <Icon size={12} color={isActive ? color : 'var(--text3)'} />
              {t(CAT_KEY[cat] || 'rec_cat_fertilizer')}
              <span style={{ background: isActive ? color : 'var(--border)', color: isActive ? '#fff' : 'var(--text3)', borderRadius:'99px', padding:'1px 6px', fontSize:'0.6rem', fontWeight:700 }}>
                {grouped[cat].length}
              </span>
            </button>
          )
        })}
      </div>

      {/* ── Detail cards for selected category ── */}
      <div style={{ display:'flex', flexDirection:'column', gap:'10px' }}>
        {selectedRecs.map((rec, i) => {
          const Icon  = ICON_MAP[rec.icon] || Leaf
          const color = CAT_COLOR[rec.category] || 'var(--accent)'
          const glow  = CAT_GLOW[rec.category]  || 'var(--accent-glow)'
          return (
            <div key={i} style={{ background:glow, border:`1px solid ${color}33`, borderRadius:'12px', padding:'14px 16px' }}>
              <div style={{ display:'flex', alignItems:'center', gap:'8px', marginBottom:'8px' }}>
                <Icon size={14} color={color} />
                <span style={{ fontSize:'0.78rem', fontWeight:700, color:'var(--text)' }}>
                  {rec.feature.replace(/_/g, ' ')}
                </span>
                <span style={{ marginLeft:'auto', display:'flex', alignItems:'center', gap:'5px', fontSize:'0.7rem' }}>
                  {rec.direction === 'increase'
                    ? <TrendingUp size={13} color="var(--accent)" />
                    : <TrendingDown size={13} color="var(--red)" />}
                  <span style={{ color: rec.direction === 'increase' ? 'var(--accent)' : 'var(--red)', fontWeight:600 }}>
                    {rec.direction === 'increase' ? t('rec_increase') : t('rec_decrease')}
                  </span>
                  {rec.target != null && (
                    <span style={{ color:'var(--text3)' }}>
                      → <span style={{ color:'var(--text)', fontWeight:700 }}>{rec.target}</span>
                    </span>
                  )}
                </span>
              </div>
              <p style={{ fontSize:'0.82rem', color:'var(--text2)', lineHeight:1.65, margin:0 }}>
                {rec.advice?.[lang] || rec.advice?.en}
              </p>
            </div>
          )
        })}
      </div>
    </Card>
  )
}
