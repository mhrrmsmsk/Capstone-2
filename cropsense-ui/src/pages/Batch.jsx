import { useState, useRef } from 'react'
import * as XLSX from 'xlsx'
import { api } from '../api'
import { Card, Btn, Spinner, ErrorMsg, SectionTitle, Badge } from '../components/ui'
import { useLang } from '../i18n.jsx'
import { UploadCloud, FileSpreadsheet, Download, Trash2, CheckCircle2 } from 'lucide-react'

function downloadCSV(rows) {
  const headers = ['Row', 'Top Crop', 'Probability %', 'Est. Yield', 'Input Type']
  const lines = [headers.join(',')]
  rows.forEach(r => {
    const top = r.recommended_crops?.[0]
    lines.push([
      r.row_index,
      `"${top?.name ?? ''}"`,
      top ? (top.probability * 100).toFixed(1) : '',
      r.estimated_yield?.toFixed(2) ?? '',
      r.input_type ?? ''
    ].join(','))
  })
  const blob = new Blob([lines.join('\n')], { type: 'text/csv' })
  const a = document.createElement('a')
  a.href = URL.createObjectURL(blob)
  a.download = 'cropsense_batch_results.csv'
  a.click()
}

export default function Batch() {
  const [rows, setRows]       = useState([])
  const [fileName, setFileName] = useState('')
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError]     = useState('')
  const inputRef = useRef()
  const { t, tc } = useLang()

  function handleFile(file) {
    if (!file) return
    setFileName(file.name)
    setError('')
    const reader = new FileReader()
    reader.onload = e => {
      try {
        const wb = XLSX.read(e.target.result, { type: 'array' })
        const ws = wb.Sheets[wb.SheetNames[0]]
        const data = XLSX.utils.sheet_to_json(ws, { defval: null })
        setRows(data)
        setResults(null)
      } catch {
        setError('Dosya okunamadı. Geçerli bir Excel veya CSV dosyası yükle.')
      }
    }
    reader.readAsArrayBuffer(file)
  }

  function onDrop(e) {
    e.preventDefault()
    handleFile(e.dataTransfer.files[0])
  }

  async function runBatch() {
    if (!rows.length) return
    setLoading(true); setError('')
    try {
      // Clean nulls per row
      const payload = rows.map(r => {
        const clean = {}
        Object.entries(r).forEach(([k, v]) => { if (v !== null && v !== '') clean[k] = v })
        return clean
      })
      const res = await api.batchPredict(payload)
      setResults(res.predictions || [])
    } catch(e) { setError(e.message) }
    finally { setLoading(false) }
  }

  const successCount = results?.filter(r => r.recommended_crops?.length).length ?? 0

  return (
    <div style={{ display:'flex', flexDirection:'column', gap:'28px' }} className="fade-in">
      <SectionTitle title={t('ba_title')} sub={t('ba_sub')} />

      <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fit, minmax(280px, 1fr))', gap:'20px', alignItems:'start' }}>

        {/* ── Upload panel ── */}
        <div style={{ display:'flex', flexDirection:'column', gap:'14px', minWidth:0 }}>
          <Card>
            {/* Drop zone */}
            <div
              onDrop={onDrop}
              onDragOver={e => e.preventDefault()}
              onClick={() => inputRef.current?.click()}
              style={{
                border:'2px dashed var(--border2)', borderRadius:'14px',
                padding:'32px 16px', display:'flex', flexDirection:'column',
                alignItems:'center', gap:'12px', cursor:'pointer',
                transition:'border-color 0.2s, background 0.2s',
              }}
              onMouseEnter={e => { e.currentTarget.style.borderColor='var(--accent)'; e.currentTarget.style.background='var(--accent-glow)' }}
              onMouseLeave={e => { e.currentTarget.style.borderColor='var(--border2)'; e.currentTarget.style.background='transparent' }}
            >
              <div style={{ width:'52px', height:'52px', borderRadius:'50%', background:'var(--surface2)', border:'1px solid var(--border)', display:'flex', alignItems:'center', justifyContent:'center' }}>
                <UploadCloud size={22} color="var(--accent)" />
              </div>
              <p style={{ fontSize:'0.875rem', color:'var(--text2)', textAlign:'center' }}>
                {t('ba_drop')} <span style={{ color:'var(--accent)', fontWeight:600 }}>{t('ba_click')}</span>
              </p>
              <p style={{ fontSize:'0.72rem', color:'var(--text3)' }}>{t('ba_fmt')}</p>
              <input ref={inputRef} type="file" accept=".xlsx,.xls,.csv" style={{ display:'none' }} onChange={e=>handleFile(e.target.files[0])} />
            </div>

            {fileName && (
              <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between', marginTop:'12px', background:'var(--surface2)', border:'1px solid var(--border)', borderRadius:'10px', padding:'8px 12px' }}>
                <div style={{ display:'flex', alignItems:'center', gap:'8px', minWidth:0 }}>
                  <FileSpreadsheet size={14} color="var(--accent)" />
                  <span style={{ fontSize:'0.75rem', color:'var(--text2)', overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap', maxWidth:'150px' }}>{fileName}</span>
                </div>
                <button onClick={()=>{ setRows([]); setFileName(''); setResults(null) }} style={{ background:'none', border:'none', cursor:'pointer', color:'var(--text3)', display:'flex', alignItems:'center' }}
                  onMouseEnter={e=>e.currentTarget.style.color='var(--red)'}
                  onMouseLeave={e=>e.currentTarget.style.color='var(--text3)'}
                >
                  <Trash2 size={14} />
                </button>
              </div>
            )}
          </Card>

          {rows.length > 0 && (
            <Card>
              {[
                { label: t('ba_rows'), val: rows.length },
                { label: t('ba_cols'), val: Object.keys(rows[0]||{}).length },
              ].map(s => (
                <div key={s.label} style={{ display:'flex', justifyContent:'space-between', alignItems:'center', padding:'6px 0', borderBottom:'1px solid var(--border)' }}>
                  <span style={{ fontSize:'0.78rem', color:'var(--text3)' }}>{s.label}</span>
                  <span style={{ fontSize:'0.875rem', fontWeight:700, color:'var(--text)' }}>{s.val}</span>
                </div>
              ))}
              {rows.length > 500 && (
                <p style={{ fontSize:'0.72rem', color:'var(--amber)', marginTop:'8px' }}>{t('ba_warn')}</p>
              )}
            </Card>
          )}

          <Btn onClick={runBatch} disabled={!rows.length||loading} style={{ width:'100%' }}>
            {loading ? t('ba_btn_loading') : `${rows.length} ${t('ba_btn')}`}
          </Btn>

          {results && (
            <Btn onClick={()=>downloadCSV(results)} variant="secondary" style={{ width:'100%' }}>
              <Download size={14} /> {t('ba_download')}
            </Btn>
          )}

          <ErrorMsg msg={error} />
        </div>

        {/* ── Results panel ── */}
        <div style={{ display:'flex', flexDirection:'column', gap:'14px', minWidth:0 }}>
          {!results && !loading && rows.length === 0 && (
            <Card>
              <div style={{ display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', padding:'60px 20px', gap:'14px' }}>
                <FileSpreadsheet size={36} color="var(--text3)" />
                <p style={{ color:'var(--text3)', fontSize:'0.875rem', textAlign:'center' }}>{t('ba_empty')}</p>
                <div style={{ fontSize:'0.75rem', color:'var(--text3)', textAlign:'center', lineHeight:1.6 }}>
                  <p>{t('ba_hint1')}</p>
                  <p>{t('ba_hint2')}</p>
                </div>
              </div>
            </Card>
          )}

          {rows.length > 0 && !results && !loading && (
            <Card>
              <p style={{ fontWeight:700, fontSize:'0.875rem', color:'var(--text)', marginBottom:'14px' }}>{t('ba_preview')}</p>
              <div style={{ overflowX:'auto' }}>
                <table className="cs-table">
                  <thead><tr>
                    {Object.keys(rows[0]).map(h => (
                      <th key={h} style={{ whiteSpace:'nowrap' }}>{h}</th>
                    ))}
                  </tr></thead>
                  <tbody>
                    {rows.slice(0,5).map((r,i) => (
                      <tr key={i}>
                        {Object.values(r).map((v,j) => (
                          <td key={j} style={{ whiteSpace:'nowrap' }}>{v ?? '—'}</td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </Card>
          )}

          {loading && <Spinner />}

          {results && !loading && (
            <Card>
              <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between', marginBottom:'16px' }}>
                <p style={{ fontWeight:700, fontSize:'0.875rem', color:'var(--text)' }}>{t('ba_results')}</p>
                <div style={{ display:'flex', alignItems:'center', gap:'6px' }}>
                  <CheckCircle2 size={14} color="var(--accent)" />
                  <span style={{ fontSize:'0.75rem', color:'var(--accent)', fontWeight:600 }}>{successCount} {t('ba_success')}</span>
                </div>
              </div>
              <div style={{ overflowX:'auto' }}>
                <table className="cs-table">
                  <thead><tr>
                    <th>{t('ba_col_row')}</th>
                    <th>{t('ba_col_crop')}</th>
                    <th>{t('ba_col_prob')}</th>
                    <th className="hide-mobile">{t('ba_col_yield')}</th>
                    <th className="hide-mobile">{t('ba_col_type')}</th>
                  </tr></thead>
                  <tbody>
                    {results.map(r => {
                      const top = r.recommended_crops?.[0]
                      return (
                        <tr key={r.row_index}>
                          <td style={{ color:'var(--text3)' }}>{r.row_index}</td>
                          <td style={{ color:'var(--text)', fontWeight:600 }}>{tc(top?.name) ?? '—'}</td>
                          <td>
                            <div style={{ display:'flex', alignItems:'center', gap:'8px' }}>
                              <div className="progress-track" style={{ width:'50px' }}>
                                <div className="progress-bar" style={{ width:`${(top?.probability??0)*100}%`, background:'var(--accent)' }} />
                              </div>
                              <span style={{ fontSize:'0.75rem', fontWeight:600, color:'var(--text2)' }}>{((top?.probability??0)*100).toFixed(0)}%</span>
                            </div>
                          </td>
                          <td className="hide-mobile" style={{ color:'var(--blue)', fontWeight:600 }}>{r.estimated_yield?.toFixed(2)??'—'}</td>
                          <td className="hide-mobile">
                            <Badge color={r.input_type==='complete'?'emerald':'amber'}>
                              {r.input_type==='complete'?t('ba_complete'):t('ba_partial')}
                            </Badge>
                          </td>
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
              </div>
            </Card>
          )}
        </div>
      </div>
    </div>
  )
}
