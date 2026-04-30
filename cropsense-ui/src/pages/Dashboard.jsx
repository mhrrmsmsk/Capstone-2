import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import { api } from '../api'
import { StatCard, Card, Btn, Input, Spinner, ErrorMsg } from '../components/ui'
import { useLang } from '../i18n.jsx'
import { Zap, TrendingUp, Leaf, ChevronRight, Sprout, FlaskConical, Target, Database } from 'lucide-react'

const COLORS = ['#22c55e','#34d399','#86efac','#4ade80','#16a34a','#15803d','#166534','#14532d']

function QuickPredict() {
  const [temp, setTemp]       = useState('')
  const [rain, setRain]       = useState('')
  const [ph, setPh]           = useState('')
  const [result, setResult]   = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError]     = useState('')
  const navigate = useNavigate()
  const { t, tc } = useLang()

  async function run() {
    const body = {}
    if (temp !== '') body.Temperature = parseFloat(temp)
    if (rain !== '') body.Rainfall    = parseFloat(rain)
    if (ph   !== '') body.pH          = parseFloat(ph)
    if (!Object.keys(body).length) { setError(t('db_qp_err')); return }
    setLoading(true); setError('')
    try { setResult(await api.predict(body)) }
    catch(e) { setError(e.message) }
    finally { setLoading(false) }
  }

  const top = result?.recommended_crops?.[0]

  return (
    <Card glow>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{
            width: '32px', height: '32px', borderRadius: '10px',
            background: 'var(--accent-glow)', border: '1px solid rgba(34,197,94,0.3)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}>
            <Zap size={15} color="var(--accent)" />
          </div>
          <div>
            <p style={{ fontWeight: 700, fontSize: '0.9rem', color: 'var(--text)' }}>{t('db_qp_title')}</p>
            <p style={{ fontSize: '0.72rem', color: 'var(--text3)', marginTop: '1px' }}>{t('db_qp_sub')}</p>
          </div>
        </div>
        <button
          onClick={() => navigate('/predict')}
          style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '0.75rem', color: 'var(--text3)', background: 'none', border: 'none', cursor: 'pointer', padding: '4px 8px', borderRadius: '8px', transition: 'all 0.15s' }}
          onMouseEnter={e => { e.currentTarget.style.color = 'var(--accent)'; e.currentTarget.style.background = 'var(--accent-glow)' }}
          onMouseLeave={e => { e.currentTarget.style.color = 'var(--text3)'; e.currentTarget.style.background = 'none' }}
        >
          {t('db_qp_full')} <ChevronRight size={12} />
        </button>
      </div>

      {/* Inputs */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px', marginBottom: '14px' }}>
        <Input label={t('db_qp_temp')} value={temp} onChange={e => setTemp(e.target.value)} placeholder="22" />
        <Input label={t('db_qp_rain')} value={rain} onChange={e => setRain(e.target.value)} placeholder="750" />
        <Input label="pH"              value={ph}   onChange={e => setPh(e.target.value)}   placeholder="6.5" step="0.1" />
      </div>

      {error && (
        <div style={{ marginBottom: '12px' }}>
          <ErrorMsg msg={error} />
        </div>
      )}

      <Btn onClick={run} disabled={loading} style={{ width: '100%' }}>
        {loading ? t('db_qp_btn_loading') : t('db_qp_btn')}
      </Btn>

      {result && !loading && (
        <div className="fade-in" style={{ borderTop: '1px solid var(--border)', marginTop: '16px', paddingTop: '16px', display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {/* Top result */}
          <div style={{
            background: 'linear-gradient(135deg, var(--accent-glow), transparent)',
            border: '1px solid rgba(34,197,94,0.25)',
            borderRadius: '14px', padding: '16px',
            display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          }}>
            <div>
              <p style={{ fontSize: '0.68rem', color: 'var(--accent)', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: '4px' }}>{t('db_qp_best')}</p>
              <p style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--text)', fontFamily: "'Space Grotesk', sans-serif", lineHeight: 1 }}>{tc(top?.name)}</p>
              <p style={{ fontSize: '0.72rem', color: 'var(--text3)', marginTop: '6px' }}>
                {t('db_qp_yield')}: <span style={{ color: 'var(--text)', fontWeight: 700 }}>{result.estimated_yield?.toFixed(2)}</span>
              </p>
            </div>
            <div style={{ textAlign: 'right' }}>
              <p style={{ fontSize: '2.4rem', fontWeight: 800, color: 'var(--accent)', fontFamily: "'Space Grotesk', sans-serif", lineHeight: 1 }}>
                {(top?.probability * 100).toFixed(0)}<span style={{ fontSize: '1.2rem' }}>%</span>
              </p>
              <p style={{ fontSize: '0.68rem', color: 'var(--text3)', marginTop: '4px' }}>{t('db_qp_conf')}</p>
            </div>
          </div>
          {/* Alternatives */}
          {result.recommended_crops?.slice(1, 4).map((c, i) => (
            <div key={c.name} style={{
              display: 'flex', alignItems: 'center', justifyContent: 'space-between',
              padding: '10px 14px', background: 'var(--surface2)',
              border: '1px solid var(--border)', borderRadius: '10px',
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <span style={{ fontSize: '0.68rem', color: 'var(--text3)', width: '16px' }}>#{i + 2}</span>
                <span style={{ fontSize: '0.875rem', color: 'var(--text2)', fontWeight: 500 }}>{tc(c.name)}</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <div style={{ width: '60px', height: '4px', background: 'var(--bg2)', borderRadius: '99px', overflow: 'hidden' }}>
                  <div style={{ width: `${c.probability * 100}%`, height: '100%', background: 'var(--accent)', borderRadius: '99px', opacity: 0.6 }} />
                </div>
                <span style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--text2)', width: '38px', textAlign: 'right' }}>
                  {(c.probability * 100).toFixed(1)}%
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </Card>
  )
}

export default function Dashboard() {
  const [stats, setStats]     = useState(null)
  const [crops, setCrops]     = useState([])
  const [loading, setLoading] = useState(true)
  const { t, tc } = useLang()

  useEffect(() => {
    Promise.all([api.stats(), api.crops()])
      .then(([s, c]) => { setStats(s); setCrops(c.crops) })
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <Spinner />

  const topCrops = stats?.crop_yield_ranking?.slice(0, 8) || []

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '32px' }} className="fade-in">

      {/* ── Hero ── */}
      <div style={{ position: 'relative', overflow: 'hidden', borderRadius: '20px', padding: '40px 32px', background: 'var(--surface)', border: '1px solid var(--border)', boxShadow: 'var(--card-shadow)' }}>
        {/* Orbs */}
        <div className="orb" style={{ width: '300px', height: '300px', background: 'var(--accent)', top: '-100px', right: '-60px', opacity: 0.12 }} />
        <div className="orb" style={{ width: '200px', height: '200px', background: 'var(--blue)', bottom: '-80px', left: '20%', opacity: 0.1 }} />

        <div style={{ position: 'relative', zIndex: 1, maxWidth: '600px' }}>
          <div style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', background: 'var(--accent-glow)', border: '1px solid rgba(34,197,94,0.3)', borderRadius: '99px', padding: '4px 14px', marginBottom: '16px' }}>
            <span className="dot-live" />
            <span style={{ fontSize: '0.72rem', fontWeight: 700, color: 'var(--accent)', letterSpacing: '0.06em', textTransform: 'uppercase' }}>{t('db_active')}</span>
          </div>
          <h1 style={{ fontSize: 'clamp(1.6rem, 4vw, 2.4rem)', fontWeight: 800, fontFamily: "'Space Grotesk', sans-serif", lineHeight: 1.15, color: 'var(--text)', marginBottom: '10px' }}>
            {t('db_title')}
          </h1>
          <p style={{ fontSize: '0.95rem', color: 'var(--text2)', lineHeight: 1.6, maxWidth: '480px' }}>{t('db_sub')}</p>
        </div>
      </div>

      {/* ── Stat row ── */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '16px' }}>
        <StatCard label={t('db_stat_crops')} value={stats?.total_crops || 22} sub={t('db_stat_crops_sub')} accent="violet" icon={<Sprout size={18} />} />
        <StatCard label={t('db_stat_ds')}    value={`${((stats?.total_samples || 15400)/1000).toFixed(1)}k`} sub={t('db_stat_ds_sub')} accent="amber" icon={<Database size={18} />} />
      </div>

      {/* ── Main grid ── */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '20px' }}>
        {/* Quick predict */}
        <div style={{ flex: '1 1 340px' }}>
          <QuickPredict />
        </div>

        {/* Yield ranking chart */}
        <div style={{ flex: '1 1 280px' }}>
          <Card style={{ height: '100%' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '20px' }}>
              <div style={{ width: '32px', height: '32px', borderRadius: '10px', background: 'var(--blue-glow)', border: '1px solid rgba(59,130,246,0.3)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <TrendingUp size={15} color="var(--blue)" />
              </div>
              <p style={{ fontWeight: 700, fontSize: '0.9rem', color: 'var(--text)' }}>{t('db_rank_title')}</p>
            </div>
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={topCrops} layout="vertical" margin={{ left: 0, right: 20, top: 0, bottom: 0 }}>
                <XAxis type="number" tick={{ fill: 'var(--text3)', fontSize: 10 }} axisLine={false} tickLine={false} />
                <YAxis type="category" dataKey="crop" tick={{ fill: 'var(--text2)', fontSize: 10 }} axisLine={false} tickLine={false} width={68} />
                <Tooltip
                  contentStyle={{ background: 'var(--surface2)', border: '1px solid var(--border2)', borderRadius: 10, color: 'var(--text)', fontSize: 12 }}
                  cursor={{ fill: 'var(--border)' }}
                  formatter={v => [v.toFixed(2), 'Avg Yield']}
                />
                <Bar dataKey="avg_yield" radius={[0, 6, 6, 0]}>
                  {topCrops.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </div>
      </div>

      {/* ── Supported crops ── */}
      <Card>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
          <div style={{ width: '32px', height: '32px', borderRadius: '10px', background: 'var(--violet-glow)', border: '1px solid rgba(139,92,246,0.3)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Leaf size={15} color="var(--violet)" />
          </div>
          <div>
            <p style={{ fontWeight: 700, fontSize: '0.9rem', color: 'var(--text)' }}>{t('db_crops_title')}</p>
            <p style={{ fontSize: '0.7rem', color: 'var(--text3)' }}>{crops.length} {t('db_stat_crops_sub')}</p>
          </div>
        </div>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
          {crops.map(c => (
            <span key={c} className="tag">{tc(c)}</span>
          ))}
        </div>
      </Card>

      {/* ── Feature cards ── */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px', alignItems: 'stretch' }}>
        {[
          { icon: FlaskConical, color: 'var(--accent)', glow: 'var(--accent-glow)', border: 'rgba(34,197,94,0.25)', label: t('nav_predict'), sub: t('pr_sub'), href: '/predict' },
          { icon: Target,       color: 'var(--violet)', glow: 'var(--violet-glow)', border: 'rgba(139,92,246,0.25)', label: t('nav_optimize'), sub: t('op_sub'), href: '/optimize' },
          { icon: TrendingUp,   color: 'var(--blue)',   glow: 'var(--blue-glow)',   border: 'rgba(59,130,246,0.25)', label: t('nav_analysis'), sub: t('an_sub'), href: '/analysis' },
        ].map(({ icon: Icon, color, glow, border, label, sub, href }) => (
          <a key={href} href={href} style={{ textDecoration: 'none', display: 'flex' }}>
            <div
              style={{ background: `linear-gradient(135deg, ${glow}, var(--surface))`, border: `1px solid ${border}`, borderRadius: '16px', padding: '20px', cursor: 'pointer', transition: 'transform 0.2s, box-shadow 0.2s', flex: 1 }}
              onMouseEnter={e => { e.currentTarget.style.transform = 'translateY(-2px)'; e.currentTarget.style.boxShadow = `0 8px 24px ${glow}` }}
              onMouseLeave={e => { e.currentTarget.style.transform = 'translateY(0)'; e.currentTarget.style.boxShadow = 'none' }}
            >
              <Icon size={22} color={color} style={{ marginBottom: '12px' }} />
              <p style={{ fontWeight: 700, fontSize: '0.9rem', color: 'var(--text)', marginBottom: '4px' }}>{label}</p>
              <p style={{ fontSize: '0.75rem', color: 'var(--text3)', lineHeight: 1.4 }}>{sub}</p>
            </div>
          </a>
        ))}
      </div>

    </div>
  )
}
