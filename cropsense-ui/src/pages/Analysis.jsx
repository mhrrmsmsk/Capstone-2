import { useEffect, useState } from 'react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import { api } from '../api'
import { Card, Spinner, ErrorMsg, SectionTitle, Badge } from '../components/ui'
import { useLang } from '../i18n.jsx'
import { BarChart2, Sprout } from 'lucide-react'

const COLORS_CROP  = ['#22c55e','#34d399','#86efac','#4ade80','#16a34a','#15803d','#166534','#14532d','#052e16','#bbf7d0']
const COLORS_YIELD = ['#3b82f6','#60a5fa','#93c5fd','#bfdbfe','#2563eb','#1d4ed8','#1e40af','#1e3a8a','#eff6ff','#dbeafe']

function ImportanceChart({ data, colors, title, sub }) {
  if (!data?.length) return null
  const top10 = [...data].sort((a, b) => b.importance - a.importance).slice(0, 10)
  return (
    <Card>
      <div style={{ marginBottom:'16px' }}>
        <p style={{ fontWeight:700, fontSize:'0.875rem', color:'var(--text)' }}>{title}</p>
        {sub && <p style={{ fontSize:'0.72rem', color:'var(--text3)', marginTop:'3px' }}>{sub}</p>}
      </div>
      <ResponsiveContainer width="100%" height={280}>
        <BarChart data={top10} layout="vertical" margin={{ left: 8, right: 24, top:0, bottom:0 }}>
          <XAxis type="number" tick={{ fill:'var(--text3)', fontSize:10 }} axisLine={false} tickLine={false} />
          <YAxis type="category" dataKey="feature" tick={{ fill:'var(--text2)', fontSize:11 }} axisLine={false} tickLine={false} width={100} />
          <Tooltip
            contentStyle={{ background:'var(--surface2)', border:'1px solid var(--border2)', borderRadius:10, color:'var(--text)', fontSize:12 }}
            cursor={{ fill:'var(--border)' }}
            formatter={v => [v.toFixed(4), 'Importance']}
          />
          <Bar dataKey="importance" radius={[0,6,6,0]}>
            {top10.map((_,i) => <Cell key={i} fill={colors[i % colors.length]} />)}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </Card>
  )
}

function FeatureTable({ data, accentColor, t }) {
  const sorted = [...data].sort((a,b) => b.importance - a.importance)
  return (
    <Card>
      <p style={{ fontWeight:700, fontSize:'0.875rem', color:'var(--text)', marginBottom:'14px' }}>{t('an_table')}</p>
      <div style={{ overflowX:'auto' }}>
        <table className="cs-table">
          <thead><tr>
            <th>{t('an_col_rank')}</th>
            <th>{t('an_col_feat')}</th>
            <th>{t('an_col_imp')}</th>
            <th className="hide-mobile">{t('an_col_bar')}</th>
          </tr></thead>
          <tbody>
            {sorted.map((d,i) => (
              <tr key={d.feature}>
                <td style={{ color:'var(--text3)' }}>#{i+1}</td>
                <td style={{ color:'var(--text)', fontWeight:500 }}>{d.feature}</td>
                <td style={{ color:accentColor, fontFamily:'monospace', fontWeight:600 }}>{d.importance.toFixed(4)}</td>
                <td className="hide-mobile">
                  <div className="progress-track" style={{ width:'80px' }}>
                    <div className="progress-bar" style={{ width:`${(d.importance/data[0]?.importance)*100}%`, background:accentColor }} />
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  )
}

export default function Analysis() {
  const [importance, setImportance] = useState(null)
  const [loading, setLoading]       = useState(true)
  const [error, setError]           = useState('')
  const [tab, setTab]               = useState('crop')
  const { t }                       = useLang()

  useEffect(() => {
    api.featureImportance()
      .then(setImportance)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <Spinner />

  const tabs = [
    { key: 'crop',  label: t('an_tab_crop')  },
    { key: 'yield', label: t('an_tab_yield') },
  ]

  const cropData  = importance?.crop  || []
  const yieldData = importance?.yield || []
  const top5crop  = [...cropData].sort((a,b)  => b.importance - a.importance).slice(0, 5)
  const top5yield = [...yieldData].sort((a,b) => b.importance - a.importance).slice(0, 5)

  return (
    <div style={{ display:'flex', flexDirection:'column', gap:'28px' }} className="fade-in">
      <SectionTitle title={t('an_title')} sub={t('an_sub')} />

      {error && <ErrorMsg msg={error} />}

      {!error && (
        <>
          {/* Tab switcher */}
          <div style={{ display:'flex', gap:'4px', borderBottom:'1px solid var(--border)', paddingBottom:0 }}>
            {tabs.map(tb => (
              <button
                key={tb.key}
                onClick={() => setTab(tb.key)}
                style={{
                  padding:'10px 18px', fontSize:'0.875rem', fontWeight:600,
                  background:'none', border:'none', cursor:'pointer',
                  borderBottom: tab===tb.key ? '2px solid var(--accent)' : '2px solid transparent',
                  color: tab===tb.key ? 'var(--accent)' : 'var(--text3)',
                  marginBottom:'-1px', transition:'color 0.15s',
                }}
                onMouseEnter={e => { if(tab!==tb.key) e.currentTarget.style.color='var(--text)' }}
                onMouseLeave={e => { if(tab!==tb.key) e.currentTarget.style.color='var(--text3)' }}
              >
                {tb.label}
              </button>
            ))}
          </div>

          {tab === 'crop' && (
            <div style={{ display:'flex', flexDirection:'column', gap:'20px' }} className="fade-in">
              <Card>
                <div style={{ display:'flex', alignItems:'center', gap:'8px', marginBottom:'14px' }}>
                  <BarChart2 size={15} color="var(--accent)" />
                  <p style={{ fontWeight:700, fontSize:'0.875rem', color:'var(--text)' }}>{t('an_top5_crop')}</p>
                </div>
                <div style={{ display:'flex', flexWrap:'wrap', gap:'8px' }}>
                  {top5crop.map((d,i) => (
                    <div key={d.feature} style={{ display:'flex', alignItems:'center', gap:'8px', background:'var(--surface2)', border:'1px solid var(--border)', borderRadius:'10px', padding:'8px 12px' }}>
                      <span style={{ fontSize:'0.68rem', color:'var(--text3)', fontWeight:600 }}>#{i+1}</span>
                      <span style={{ fontSize:'0.8rem', fontWeight:600, color:'var(--text)' }}>{d.feature}</span>
                      <Badge color="emerald">{(d.importance*100).toFixed(1)}%</Badge>
                    </div>
                  ))}
                </div>
              </Card>
              <ImportanceChart data={cropData} colors={COLORS_CROP} title={t('an_chart_crop')} sub={t('an_chart_sub')} />
              <FeatureTable data={cropData} accentColor="var(--accent)" t={t} />
            </div>
          )}

          {tab === 'yield' && (
            <div style={{ display:'flex', flexDirection:'column', gap:'20px' }} className="fade-in">
              <Card>
                <div style={{ display:'flex', alignItems:'center', gap:'8px', marginBottom:'14px' }}>
                  <Sprout size={15} color="var(--blue)" />
                  <p style={{ fontWeight:700, fontSize:'0.875rem', color:'var(--text)' }}>{t('an_top5_yield')}</p>
                </div>
                <div style={{ display:'flex', flexWrap:'wrap', gap:'8px' }}>
                  {top5yield.map((d,i) => (
                    <div key={d.feature} style={{ display:'flex', alignItems:'center', gap:'8px', background:'var(--surface2)', border:'1px solid var(--border)', borderRadius:'10px', padding:'8px 12px' }}>
                      <span style={{ fontSize:'0.68rem', color:'var(--text3)', fontWeight:600 }}>#{i+1}</span>
                      <span style={{ fontSize:'0.8rem', fontWeight:600, color:'var(--text)' }}>{d.feature}</span>
                      <Badge color="blue">{(d.importance*100).toFixed(1)}%</Badge>
                    </div>
                  ))}
                </div>
              </Card>
              <ImportanceChart data={yieldData} colors={COLORS_YIELD} title={t('an_chart_yield')} sub={t('an_chart_sub')} />
              <FeatureTable data={yieldData} accentColor="var(--blue)" t={t} />
            </div>
          )}
        </>
      )}
    </div>
  )
}
