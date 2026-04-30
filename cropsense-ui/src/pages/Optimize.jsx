import { useEffect, useState } from 'react'
import { api } from '../api'
import { Card, Btn, Input, Select, Spinner, ErrorMsg, SectionTitle } from '../components/ui'
import { useLang } from '../i18n.jsx'
import { Sliders, RefreshCw, TrendingUp, TrendingDown, CheckCircle2 } from 'lucide-react'
import RecommendationPanel from '../components/RecommendationPanel'

const NUM_FEATURES = [
  { key: 'Temperature',     labelEn: 'Temperature (°C)',   placeholder: '20',  step: '0.1'  },
  { key: 'Rainfall',        labelEn: 'Rainfall (mm)',       placeholder: '750', step: '1'    },
  { key: 'pH',              labelEn: 'pH',                  placeholder: '6.5', step: '0.01' },
  { key: 'Light_Hours',     labelEn: 'Light Hours',         placeholder: '12',  step: '0.1'  },
  { key: 'Light_Intensity', labelEn: 'Light Intensity',     placeholder: '500', step: '1'    },
  { key: 'Rh',              labelEn: 'Humidity %',          placeholder: '70',  step: '0.1'  },
  { key: 'Nitrogen',        labelEn: 'Nitrogen (N)',        placeholder: '150', step: '1'    },
  { key: 'Phosphorus',      labelEn: 'Phosphorus (P)',      placeholder: '100', step: '1'    },
  { key: 'Potassium',       labelEn: 'Potassium (K)',       placeholder: '200', step: '1'    },
  { key: 'N_Ratio',         labelEn: 'N Ratio',             placeholder: '1.5', step: '0.01' },
  { key: 'P_Ratio',         labelEn: 'P Ratio',             placeholder: '1.0', step: '0.01' },
  { key: 'K_Ratio',         labelEn: 'K Ratio',             placeholder: '2.0', step: '0.01' },
]
const CAT_FEATURES = ['Fertility', 'Photoperiod', 'Category_pH', 'Soil_Type', 'Season']

function StatusIcon({ action }) {
  if (action === 'Keep') return <CheckCircle2 size={14} className="text-emerald-400" />
  if (action?.startsWith('Increase')) return <TrendingUp size={14} className="text-amber-400" />
  return <TrendingDown size={14} className="text-red-400" />
}

export default function Optimize() {
  const [crops, setCrops]     = useState([])
  const [catOpts, setCatOpts] = useState({})
  const [bounds, setBounds]   = useState({})
  const [crop, setCrop]       = useState('')
  const [vals, setVals]       = useState({})
  const [result, setResult]   = useState(null)
  const [recs, setRecs]               = useState(null)
  const [recsLoading, setRecsLoading] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError]     = useState('')
  const { t, tc, tf, tv } = useLang()

  useEffect(() => {
    Promise.all([api.crops(), api.featureBounds()]).then(([d, b]) => {
      setCrops(d.crops || [])
      setCatOpts(d.categorical_options || {})
      setBounds(b || {})
      if (d.crops?.length) setCrop(d.crops[0])
      const init = {}
      Object.entries(d.categorical_options || {}).forEach(([k, opts]) => { init[k] = opts[0] })
      setVals(init)
    })
  }, [])

  function set(k, v) { setVals(p => ({ ...p, [k]: v })) }
  function clear(k)  { setVals(p => { const n = { ...p }; delete n[k]; return n }) }

  async function analyze() {
    const body = { crop_name: crop }
    NUM_FEATURES.forEach(({ key }) => {
      if (vals[key] !== undefined && vals[key] !== '') body[key] = parseFloat(vals[key])
    })
    CAT_FEATURES.forEach(k => { if (vals[k]) body[k] = vals[k] })
    const oob = NUM_FEATURES.filter(({ key }) => {
      const v = parseFloat(vals[key]); const b = bounds[key]
      return !isNaN(v) && b && (v < b.min || v > b.max)
    })
    if (oob.length) { setError(`Out of range: ${oob.map(f => f.labelEn).join(', ')}`); return }
    setLoading(true); setError(''); setRecs(null)
    try {
      const res = await api.optimize(body)
      setResult(res)
      const optCond = res?.optimized_conditions || {}
      if (Object.keys(optCond).length) {
        const numVals = {}
        NUM_FEATURES.forEach(({ key }) => { if (vals[key] !== undefined && vals[key] !== '') numVals[key] = parseFloat(vals[key]) })
        setRecsLoading(true)
        api.recommendations({ crop_name: crop, optimized_conditions: optCond, current_values: numVals })
          .then(r => setRecs(r.recommendations || []))
          .catch(() => setRecs([]))
          .finally(() => setRecsLoading(false))
      }
    }
    catch(e) { setError(e.message) }
    finally { setLoading(false) }
  }

  // Build table rows
  const opt = result?.optimized_conditions || {}
  const rows = Object.entries(opt).map(([feat, v]) => {
    const current = vals[feat] !== undefined && vals[feat] !== ''
      ? parseFloat(vals[feat])
      : null
    const lo = v.min, hi = v.max, mean = v.mean

    let action = `Move to ${v.recommended}`
    let status = 'Adjust'

    if (typeof lo === 'number' && typeof hi === 'number' && current !== null) {
      if (current >= lo && current <= hi) { action = 'Keep'; status = 'Good' }
      else if (mean !== undefined) {
        action = current < mean ? `Increase → ${mean.toFixed(1)}` : `Decrease → ${mean.toFixed(1)}`
        status = 'Adjust'
      }
    } else if (typeof lo === 'string') {
      action = String(current) === lo ? 'Keep' : `Change to ${lo}`
      status  = String(current) === lo ? 'Good' : 'Adjust'
    }

    return { feat, featLabel: tf(feat, feat), current: current ?? '—', range: v.range, target: v.recommended, action, status }
  }).sort(a => (a.status === 'Adjust' ? -1 : 1))

  const adjustCount = rows.filter(r => r.status === 'Adjust').length
  const goodCount   = rows.filter(r => r.status === 'Good').length

  return (
    <div style={{ display:'flex', flexDirection:'column', gap:'28px' }} className="fade-in">
      <SectionTitle title={t('op_title')} sub={t('op_sub')} />

      <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fit, minmax(280px, 1fr))', gap:'20px', alignItems:'start' }}>

        {/* ── FORM ── */}
        <div style={{ display:'flex', flexDirection:'column', gap:'14px', minWidth:0 }}>
          <Card>
            <div style={{ display:'flex', alignItems:'center', gap:'8px', marginBottom:'14px' }}>
              <div style={{ width:'28px', height:'28px', borderRadius:'8px', background:'var(--violet-glow)', border:'1px solid rgba(139,92,246,0.3)', display:'flex', alignItems:'center', justifyContent:'center' }}>
                <Sliders size={13} color="var(--violet)" />
              </div>
              <span style={{ fontWeight:700, fontSize:'0.875rem', color:'var(--text)' }}>{t('op_target')}</span>
            </div>
            <Select label={t('op_select')} value={crop} onChange={e=>setCrop(e.target.value)}
              options={crops.map(c=>({ value:c, label:tc(c) }))} />
          </Card>

          <Card>
            <p style={{ fontWeight:700, fontSize:'0.875rem', color:'var(--text)', marginBottom:'4px' }}>{t('op_current')}
              <span style={{ fontWeight:400, color:'var(--text3)', fontSize:'0.75rem', marginLeft:'6px' }}>{t('op_current_opt')}</span>
            </p>
            <div style={{ display:'grid', gridTemplateColumns:'repeat(2,1fr)', gap:'10px', marginTop:'12px' }}>
              {NUM_FEATURES.map(({ key, labelEn, placeholder, step }) => (
                <div key={key} style={{ position:'relative' }}>
                  <Input
                    label={tf(key,labelEn)}
                    value={vals[key]??''}
                    onChange={e=>set(key,e.target.value)}
                    placeholder={placeholder}
                    step={step}
                    min={bounds[key]?.min}
                    max={bounds[key]?.max}
                  />
                  {vals[key]!==undefined && vals[key]!=='' && (
                    <button onClick={()=>clear(key)} style={{ position:'absolute', right:'8px', top:'26px', background:'none', border:'none', color:'var(--text3)', cursor:'pointer', fontSize:'0.75rem' }}>✕</button>
                  )}
                </div>
              ))}
            </div>
          </Card>

          <Card>
            <p style={{ fontSize:'0.7rem', fontWeight:600, color:'var(--text3)', textTransform:'uppercase', letterSpacing:'0.05em', marginBottom:'10px' }}>{t('op_cat')}</p>
            <div style={{ display:'grid', gridTemplateColumns:'repeat(2,1fr)', gap:'10px' }}>
              {CAT_FEATURES.map(k => (
                <Select key={k} label={tf(k,k)} value={vals[k]||''} onChange={e=>set(k,e.target.value)}
                  options={(catOpts[k]||[]).map(o=>({ value:o, label:tv(o) }))} />
              ))}
            </div>
          </Card>

          <div style={{ display:'flex', gap:'10px' }}>
            <Btn onClick={analyze} disabled={loading||!crop} style={{ flex:1 }}>
              {loading ? t('op_btn_loading') : t('op_btn')}
            </Btn>
            <Btn onClick={()=>{ setVals({}); setResult(null); setRecs(null) }} variant="secondary"><RefreshCw size={14} /></Btn>
          </div>
          <ErrorMsg msg={error} />
        </div>

        {/* ── RESULTS ── */}
        <div style={{ display:'flex', flexDirection:'column', gap:'14px', minWidth:0 }}>
          {!result && !loading && (
            <Card>
              <div style={{ display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', padding:'60px 20px', gap:'14px' }}>
                <div style={{ width:'64px', height:'64px', borderRadius:'50%', background:'var(--surface2)', border:'1px solid var(--border)', display:'flex', alignItems:'center', justifyContent:'center' }}>
                  <Sliders size={26} color="var(--text3)" />
                </div>
                <p style={{ color:'var(--text3)', fontSize:'0.875rem', textAlign:'center' }}>{t('op_empty')}</p>
              </div>
            </Card>
          )}

          {loading && <Spinner />}

          {result && !loading && (
            <>
              {/* Summary row */}
              <div style={{ display:'grid', gridTemplateColumns:'repeat(3,1fr)', gap:'10px' }}>
                {[
                  { val: tc(crop), label: t('op_target_crop'), bg:'var(--surface2)', border:'var(--border)', color:'var(--text)' },
                  { val: adjustCount, label: t('op_to_fix'),  bg:'var(--red-glow)',    border:'rgba(239,68,68,0.25)',   color:'var(--red)'    },
                  { val: goodCount,   label: t('op_ideal'),   bg:'var(--accent-glow)', border:'rgba(34,197,94,0.25)',   color:'var(--accent)' },
                ].map((s,i) => (
                  <div key={i} style={{ background:s.bg, border:`1px solid ${s.border}`, borderRadius:'14px', padding:'14px', textAlign:'center' }}>
                    <p style={{ fontSize:'1.5rem', fontWeight:800, color:s.color, fontFamily:"'Space Grotesk',sans-serif", lineHeight:1 }}>{s.val}</p>
                    <p style={{ fontSize:'0.68rem', color:'var(--text3)', marginTop:'6px' }}>{s.label}</p>
                  </div>
                ))}
              </div>

              {result.estimated_yield && (
                <div style={{ background:'var(--blue-glow)', border:'1px solid rgba(59,130,246,0.25)', borderRadius:'14px', padding:'14px 18px', display:'flex', alignItems:'center', justifyContent:'space-between' }}>
                  <span style={{ fontSize:'0.875rem', color:'var(--text2)' }}>{t('op_yield')}</span>
                  <span style={{ fontSize:'1.6rem', fontWeight:800, color:'var(--blue)', fontFamily:"'Space Grotesk',sans-serif" }}>{result.estimated_yield.toFixed(2)}</span>
                </div>
              )}

              {/* Action table */}
              <Card>
                <p style={{ fontWeight:700, fontSize:'0.875rem', color:'var(--text)', marginBottom:'14px' }}>{t('op_plan')}</p>
                <div style={{ overflowX:'auto' }}>
                  <table className="cs-table">
                    <thead><tr>
                      <th>{t('op_col_feat')}</th>
                      <th>{t('op_col_cur')}</th>
                      <th className="hide-mobile">{t('op_col_range')}</th>
                      <th>{t('op_col_target')}</th>
                      <th>{t('op_col_action')}</th>
                    </tr></thead>
                    <tbody>
                      {rows.map(r => (
                        <tr key={r.feat}>
                          <td style={{ color:'var(--text)', fontWeight:500 }}>{r.featLabel}</td>
                          <td>{r.current}</td>
                          <td className="hide-mobile">{r.range}</td>
                          <td style={{ color:'var(--blue)' }}>{tv(r.target)}</td>
                          <td>
                            <div style={{ display:'flex', alignItems:'center', gap:'6px' }}>
                              <StatusIcon action={r.action} />
                              <span style={{ color: r.action==='Keep' ? 'var(--accent)' : 'var(--amber)', fontSize:'0.72rem' }}>{r.action}</span>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </Card>
              {/* Recommendations */}
              <RecommendationPanel recs={recs} loading={recsLoading} cropName={tc(crop)} />
            </>
          )}
        </div>
      </div>
    </div>
  )
}
