import { useEffect, useState } from 'react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import { api } from '../api'
import { Card, Btn, Input, Select, Spinner, ErrorMsg, SectionTitle, Badge } from '../components/ui'
import { useLang } from '../i18n.jsx'
import { FlaskConical, RefreshCw, ChevronDown, ChevronUp, Info } from 'lucide-react'

const NUM_FEATURES = [
  { key: 'Temperature',    labelEn: 'Temperature (°C)',   placeholder: '20',   step: '0.1' },
  { key: 'Rainfall',       labelEn: 'Rainfall (mm)',       placeholder: '750',  step: '1'   },
  { key: 'pH',             labelEn: 'pH',                  placeholder: '6.5',  step: '0.01'},
  { key: 'Light_Hours',    labelEn: 'Light Hours (h/day)', placeholder: '12',   step: '0.1' },
  { key: 'Light_Intensity',labelEn: 'Light Intensity',     placeholder: '500',  step: '1'   },
  { key: 'Rh',             labelEn: 'Relative Humidity %', placeholder: '70',   step: '0.1' },
  { key: 'Nitrogen',       labelEn: 'Nitrogen (N)',        placeholder: '150',  step: '1'   },
  { key: 'Phosphorus',     labelEn: 'Phosphorus (P)',      placeholder: '100',  step: '1'   },
  { key: 'Potassium',      labelEn: 'Potassium (K)',       placeholder: '200',  step: '1'   },
  { key: 'N_Ratio',        labelEn: 'N Ratio',             placeholder: '1.5',  step: '0.01'},
  { key: 'P_Ratio',        labelEn: 'P Ratio',             placeholder: '1.0',  step: '0.01'},
  { key: 'K_Ratio',        labelEn: 'K Ratio',             placeholder: '2.0',  step: '0.01'},
]
const CAT_FEATURES = ['Fertility', 'Photoperiod', 'Category_pH', 'Soil_Type', 'Season']
const BAR_COLORS = ['#22c55e','#34d399','#86efac','#4ade80','#16a34a']

function CropBar({ crops }) {
  return (
    <ResponsiveContainer width="100%" height={200}>
      <BarChart data={crops} layout="vertical" margin={{ left: 0, right: 24, top: 4, bottom: 0 }}>
        <XAxis type="number" domain={[0,100]} tick={{ fill:'var(--text3)', fontSize:10 }} tickFormatter={v=>`${v}%`} axisLine={false} tickLine={false} />
        <YAxis type="category" dataKey="displayName" tick={{ fill:'var(--text2)', fontSize:11 }} axisLine={false} tickLine={false} width={110} />
        <Tooltip
          contentStyle={{ background:'var(--surface2)', border:'1px solid var(--border2)', borderRadius:10, color:'var(--text)', fontSize:12 }}
          cursor={{ fill:'var(--border)' }}
          formatter={v => [`${v.toFixed(1)}%`, 'Probability']}
        />
        <Bar dataKey="pct" radius={[0,6,6,0]}>
          {crops.map((_,i) => <Cell key={i} fill={BAR_COLORS[i % BAR_COLORS.length]} />)}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}

function CollapseCard({ title, children, defaultOpen = false }) {
  const [open, setOpen] = useState(defaultOpen)
  return (
    <Card>
      <button
        onClick={() => setOpen(o => !o)}
        style={{ display:'flex', alignItems:'center', justifyContent:'space-between', width:'100%', background:'none', border:'none', cursor:'pointer', padding:0 }}
      >
        <span style={{ fontWeight:700, fontSize:'0.875rem', color:'var(--text)' }}>{title}</span>
        {open
          ? <ChevronUp size={16} color="var(--text3)" />
          : <ChevronDown size={16} color="var(--text3)" />}
      </button>
      {open && (
        <div className="fade-in" style={{ marginTop:'14px', overflowX:'auto' }}>
          {children}
        </div>
      )}
    </Card>
  )
}

export default function Predict() {
  const [catOpts, setCatOpts]         = useState({})
  const [vals, setVals]               = useState({})
  const [result, setResult]           = useState(null)
  const [loading, setLoading]         = useState(false)
  const [error, setError]             = useState('')
  const { t, tc, tf, tv } = useLang()

  useEffect(() => {
    api.crops().then(d => {
      setCatOpts(d.categorical_options || {})
      const init = {}
      Object.entries(d.categorical_options || {}).forEach(([k, opts]) => { init[k] = opts[0] })
      setVals(v => ({ ...v, ...init }))
    })
  }, [])

  function set(key, val) { setVals(v => ({ ...v, [key]: val })) }
  function clear(key)    { setVals(v => { const n = { ...v }; delete n[key]; return n }) }

  function reset() {
    const init = {}
    Object.entries(catOpts).forEach(([k, opts]) => { init[k] = opts[0] })
    setVals(init); setResult(null); setError('')
  }

  async function predict() {
    const body = {}
    NUM_FEATURES.forEach(({ key }) => {
      if (vals[key] !== undefined && vals[key] !== '') body[key] = parseFloat(vals[key])
    })
    CAT_FEATURES.forEach(k => { if (vals[k]) body[k] = vals[k] })
    if (!Object.keys(body).length) { setError(t('pr_err_min')); return }
    setLoading(true); setError('')
    try { setResult(await api.predict(body)) }
    catch(e) { setError(e.message) }
    finally { setLoading(false) }
  }

  const crops      = (result?.recommended_crops || []).map(c => ({ ...c, pct: c.probability * 100, displayName: tc(c.name) }))
  const top        = crops[0]
  const missing    = result?.estimated_missing_values || {}
  const opt        = result?.optimized_conditions || {}
  const filledCount = NUM_FEATURES.filter(f => vals[f.key] !== undefined && vals[f.key] !== '').length

  return (
    <div style={{ display:'flex', flexDirection:'column', gap:'28px' }} className="fade-in">
      <SectionTitle title={t('pr_title')} sub={t('pr_sub')} />

      <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fit, minmax(300px, 1fr))', gap:'20px', alignItems:'start' }}>

        {/* ── FORM ── */}
        <div style={{ display:'flex', flexDirection:'column', gap:'16px', minWidth:0 }}>
          <Card>
            <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between', marginBottom:'16px' }}>
              <div style={{ display:'flex', alignItems:'center', gap:'8px' }}>
                <div style={{ width:'28px', height:'28px', borderRadius:'8px', background:'var(--accent-glow)', border:'1px solid rgba(34,197,94,0.3)', display:'flex', alignItems:'center', justifyContent:'center' }}>
                  <FlaskConical size={13} color="var(--accent)" />
                </div>
                <span style={{ fontWeight:700, fontSize:'0.875rem', color:'var(--text)' }}>{t('pr_num')}</span>
              </div>
              <span style={{ fontSize:'0.68rem', fontWeight:600, padding:'2px 8px', borderRadius:'99px', background: filledCount > 0 ? 'var(--accent-glow)' : 'var(--surface2)', color: filledCount > 0 ? 'var(--accent)' : 'var(--text3)', border:`1px solid ${filledCount > 0 ? 'rgba(34,197,94,0.3)' : 'var(--border)'}` }}>
                {filledCount}/{NUM_FEATURES.length} {t('pr_filled')}
              </span>
            </div>
            <div style={{ display:'grid', gridTemplateColumns:'repeat(2,1fr)', gap:'10px' }}>
              {NUM_FEATURES.map(({ key, labelEn, placeholder, step }) => (
                <div key={key} style={{ position:'relative' }}>
                  <Input label={tf(key,labelEn)} value={vals[key]??''} onChange={e=>set(key,e.target.value)} placeholder={placeholder} step={step} />
                  {vals[key]!==undefined && vals[key]!=='' && (
                    <button onClick={()=>clear(key)} style={{ position:'absolute', right:'8px', top:'26px', background:'none', border:'none', color:'var(--text3)', cursor:'pointer', fontSize:'0.75rem', lineHeight:1 }}>✕</button>
                  )}
                </div>
              ))}
            </div>
          </Card>

          <Card>
            <div style={{ display:'flex', alignItems:'center', gap:'8px', marginBottom:'14px' }}>
              <span style={{ fontWeight:700, fontSize:'0.875rem', color:'var(--text)' }}>{t('pr_cat')}</span>
              <span style={{ fontSize:'0.7rem', color:'var(--text3)' }}>{t('pr_cat_opt')}</span>
            </div>
            <div style={{ display:'grid', gridTemplateColumns:'repeat(2,1fr)', gap:'10px' }}>
              {CAT_FEATURES.map(k => (
                <Select key={k} label={tf(k,k)} value={vals[k]||''} onChange={e=>set(k,e.target.value)}
                  options={(catOpts[k]||[]).map(o=>({ value:o, label:tv(o) }))} />
              ))}
            </div>
          </Card>

          <div style={{ display:'flex', gap:'10px' }}>
            <Btn onClick={predict} disabled={loading} style={{ flex:1 }}>
              {loading ? t('pr_btn_loading') : t('pr_btn')}
            </Btn>
            <Btn onClick={reset} variant="secondary"><RefreshCw size={14} /></Btn>
          </div>
          <ErrorMsg msg={error} />
        </div>

        {/* ── RESULTS ── */}
        <div style={{ display:'flex', flexDirection:'column', gap:'16px', minWidth:0 }}>
          {!result && !loading && (
            <Card>
              <div style={{ display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', padding:'60px 20px', gap:'14px' }}>
                <div style={{ width:'64px', height:'64px', borderRadius:'50%', background:'var(--surface2)', border:'1px solid var(--border)', display:'flex', alignItems:'center', justifyContent:'center' }}>
                  <FlaskConical size={26} color="var(--text3)" />
                </div>
                <p style={{ color:'var(--text3)', fontSize:'0.875rem', textAlign:'center' }}>{t('pr_empty')}</p>
              </div>
            </Card>
          )}

          {loading && <Spinner />}

          {result && !loading && (
            <>
              {/* Top crop */}
              <div style={{ background:'linear-gradient(135deg, var(--accent-glow), var(--surface))', border:'1px solid rgba(34,197,94,0.25)', borderRadius:'16px', padding:'20px', boxShadow:'var(--card-shadow)' }}>
                <div style={{ display:'flex', alignItems:'flex-start', justifyContent:'space-between', gap:'12px' }}>
                  <div>
                    <p style={{ fontSize:'0.68rem', color:'var(--accent)', fontWeight:700, textTransform:'uppercase', letterSpacing:'0.08em', marginBottom:'6px' }}>{t('pr_best')}</p>
                    <p style={{ fontSize:'2rem', fontWeight:800, color:'var(--text)', fontFamily:"'Space Grotesk',sans-serif", lineHeight:1 }}>{tc(top?.name)}</p>
                    <p style={{ fontSize:'0.78rem', color:'var(--text2)', marginTop:'8px' }}>
                      {t('pr_yield')}: <span style={{ color:'var(--text)', fontWeight:700, fontSize:'1.1rem' }}>{result.estimated_yield?.toFixed(2)}</span>
                    </p>
                  </div>
                  <div style={{ textAlign:'right', flexShrink:0 }}>
                    <p style={{ fontSize:'3rem', fontWeight:800, color:'var(--accent)', fontFamily:"'Space Grotesk',sans-serif", lineHeight:1 }}>
                      {top?.pct.toFixed(0)}<span style={{ fontSize:'1.4rem' }}>%</span>
                    </p>
                    <p style={{ fontSize:'0.68rem', color:'var(--text3)', marginTop:'4px' }}>{t('pr_conf')}</p>
                  </div>
                </div>
              </div>

              {/* Chart */}
              <Card>
                <p style={{ fontWeight:700, fontSize:'0.875rem', color:'var(--text)', marginBottom:'14px' }}>{t('pr_dist')}</p>
                <CropBar crops={crops} />
              </Card>

              {/* Input type */}
              <div style={{ display:'flex', alignItems:'center', gap:'8px' }}>
                <Info size={13} color="var(--text3)" />
                <span style={{ fontSize:'0.75rem', color:'var(--text3)' }}>{t('pr_type')}:{' '}
                  <Badge color={result.input_type === 'complete' ? 'emerald' : 'amber'}>
                    {result.input_type === 'complete' ? t('pr_complete') : t('pr_partial')}
                  </Badge>
                </span>
              </div>

              {/* Missing values */}
              {Object.keys(missing).length > 0 && (
                <CollapseCard title={`${t('pr_missing_title')} (${Object.keys(missing).length})`}>
                  <table className="cs-table">
                    <thead><tr>
                      <th>{t('op_col_feat')}</th>
                      <th>{t('op_col_range')}</th>
                      <th>{t('op_col_target')}</th>
                    </tr></thead>
                    <tbody>
                      {Object.entries(missing).map(([feat,v]) => (
                        <tr key={feat}>
                          <td style={{ color:'var(--text)', fontWeight:500 }}>{tf(feat,feat)}</td>
                          <td>{v.range}</td>
                          <td style={{ color:'var(--accent)', fontWeight:600 }}>{tv(v.recommended)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </CollapseCard>
              )}

              {/* Optimized conditions */}
              {Object.keys(opt).length > 0 && (
                <CollapseCard title={`${tc(top?.name)} ${t('pr_opt_title')}`}>
                  <table className="cs-table">
                    <thead><tr>
                      <th>{t('op_col_feat')}</th>
                      <th>{t('op_col_range')}</th>
                      <th>{t('op_col_target')}</th>
                    </tr></thead>
                    <tbody>
                      {Object.entries(opt).map(([feat,v]) => (
                        <tr key={feat}>
                          <td style={{ color:'var(--text)', fontWeight:500 }}>{tf(feat,feat)}</td>
                          <td>{v.range}</td>
                          <td style={{ color:'var(--blue)', fontWeight:600 }}>{tv(v.recommended)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </CollapseCard>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  )
}
