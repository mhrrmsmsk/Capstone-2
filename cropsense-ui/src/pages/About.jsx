import { useLang } from '../i18n.jsx'
import { Card } from '../components/ui'
import { Leaf, Brain, Zap, Database, Code2, CheckCircle2 } from 'lucide-react'

const MODEL_CARDS = [
  { label: 'CLASSIFIER', value: 'Random Forest', sub: 'Crop prediction',    color: 'var(--accent)',  glow: 'var(--accent-glow)',  border: 'rgba(34,197,94,0.25)'  },
  { label: 'REGRESSOR',  value: 'Random Forest', sub: 'Yield prediction',   color: 'var(--blue)',    glow: 'var(--blue-glow)',    border: 'rgba(59,130,246,0.25)' },
  { label: 'IMPUTER',    value: 'KNN',           sub: 'Missing value est.', color: 'var(--violet)',  glow: 'var(--violet-glow)', border: 'rgba(139,92,246,0.25)' },
]

const TECH_STACK = [
  { cat: 'Backend',   items: ['Python 3.11', 'FastAPI', 'scikit-learn', 'pandas', 'NumPy', 'joblib'] },
  { cat: 'Frontend',  items: ['React 19', 'Vite 8', 'Tailwind CSS v4', 'Recharts', 'React Router'] },
  { cat: 'ML Models', items: ['RandomForestClassifier', 'RandomForestRegressor', 'KNearestNeighbors', 'StandardScaler', 'LabelEncoder'] },
]

const STEPS = [
  { icon: Zap,          num: '01', color: 'var(--accent)',  glow: 'var(--accent-glow)',  border: 'rgba(34,197,94,0.2)'  },
  { icon: Brain,        num: '02', color: 'var(--blue)',    glow: 'var(--blue-glow)',    border: 'rgba(59,130,246,0.2)' },
  { icon: CheckCircle2, num: '03', color: 'var(--violet)',  glow: 'var(--violet-glow)', border: 'rgba(139,92,246,0.2)' },
]

export default function About() {
  const { t } = useLang()

  const STEP_DATA = [
    { title: t('ab_step1_title'), body: t('ab_step1_body') },
    { title: t('ab_step2_title'), body: t('ab_step2_body') },
    { title: t('ab_step3_title'), body: t('ab_step3_body') },
  ]

  return (
    <div style={{ display:'flex', flexDirection:'column', gap:'40px', maxWidth:'860px', margin:'0 auto' }} className="fade-in">

      {/* ── Hero ── */}
      <div style={{ textAlign:'center', padding:'32px 0 8px' }}>
        <div style={{ display:'inline-flex', alignItems:'center', justifyContent:'center', width:'72px', height:'72px', borderRadius:'20px', background:'var(--accent)', marginBottom:'20px', boxShadow:'0 8px 32px var(--accent-glow)' }}>
          <Leaf size={30} color="#fff" />
        </div>
        <h1 style={{ fontSize:'2.4rem', fontWeight:800, color:'var(--text)', fontFamily:"'Space Grotesk',sans-serif", marginBottom:'10px' }}>{t('ab_title')}</h1>
        <p style={{ color:'var(--text2)', fontSize:'1rem', maxWidth:'480px', margin:'0 auto', lineHeight:1.6 }}>{t('ab_sub')}</p>
      </div>

      {/* ── What is CropSense? ── */}
      <Card>
        <div style={{ display:'flex', alignItems:'center', gap:'12px', marginBottom:'14px' }}>
          <div style={{ width:'36px', height:'36px', borderRadius:'10px', background:'var(--accent-glow)', border:'1px solid rgba(34,197,94,0.25)', display:'flex', alignItems:'center', justifyContent:'center' }}>
            <Brain size={17} color="var(--accent)" />
          </div>
          <h2 style={{ fontSize:'1.05rem', fontWeight:700, color:'var(--text)' }}>{t('ab_what_title')}</h2>
        </div>
        <p style={{ color:'var(--text2)', lineHeight:1.75, fontSize:'0.9rem' }}>{t('ab_what_body')}</p>
      </Card>

      {/* ── How it works ── */}
      <div>
        <h2 style={{ fontSize:'1.05rem', fontWeight:700, color:'var(--text)', marginBottom:'16px' }}>{t('ab_how_title')}</h2>
        <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fit, minmax(220px, 1fr))', gap:'14px' }}>
          {STEPS.map(({ icon: Icon, num, color, glow, border }, idx) => (
            <div key={num} style={{ background:glow, border:`1px solid ${border}`, borderRadius:'16px', padding:'20px', display:'flex', flexDirection:'column', gap:'12px' }}>
              <div style={{ display:'flex', alignItems:'center', gap:'12px' }}>
                <span style={{ fontSize:'2.2rem', fontWeight:900, color, opacity:0.25, fontFamily:"'Space Grotesk',sans-serif", lineHeight:1 }}>{num}</span>
                <div style={{ width:'34px', height:'34px', borderRadius:'10px', background:glow, border:`1px solid ${border}`, display:'flex', alignItems:'center', justifyContent:'center' }}>
                  <Icon size={16} color={color} />
                </div>
              </div>
              <h3 style={{ fontWeight:700, color:'var(--text)', fontSize:'0.9rem' }}>{STEP_DATA[idx].title}</h3>
              <p style={{ fontSize:'0.8rem', color:'var(--text2)', lineHeight:1.65 }}>{STEP_DATA[idx].body}</p>
            </div>
          ))}
        </div>
      </div>

      {/* ── Models & Performance ── */}
      <div>
        <h2 style={{ fontSize:'1.05rem', fontWeight:700, color:'var(--text)', marginBottom:'16px' }}>{t('ab_models_title')}</h2>
        <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fit, minmax(200px, 1fr))', gap:'14px' }}>
          {MODEL_CARDS.map(({ label, value, sub, color, glow, border }) => (
            <div key={label} style={{ background:glow, border:`1px solid ${border}`, borderRadius:'16px', padding:'20px' }}>
              <p style={{ fontSize:'0.65rem', color:'var(--text3)', fontWeight:700, textTransform:'uppercase', letterSpacing:'0.08em', marginBottom:'8px' }}>{label}</p>
              <p style={{ fontSize:'1.25rem', fontWeight:800, color, fontFamily:"'Space Grotesk',sans-serif" }}>{value}</p>
              <p style={{ fontSize:'0.72rem', color:'var(--text3)', marginTop:'4px' }}>{sub}</p>
            </div>
          ))}
        </div>
      </div>

      {/* ── Key Features ── */}
      <Card>
        <div style={{ display:'flex', alignItems:'center', gap:'12px', marginBottom:'18px' }}>
          <div style={{ width:'36px', height:'36px', borderRadius:'10px', background:'var(--violet-glow)', border:'1px solid rgba(139,92,246,0.25)', display:'flex', alignItems:'center', justifyContent:'center' }}>
            <CheckCircle2 size={17} color="var(--violet)" />
          </div>
          <h2 style={{ fontSize:'1.05rem', fontWeight:700, color:'var(--text)' }}>{t('ab_feat_title')}</h2>
        </div>
        <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fit, minmax(240px, 1fr))', gap:'10px' }}>
          {[t('ab_feat1'), t('ab_feat2'), t('ab_feat3'), t('ab_feat4'), t('ab_feat5'), t('ab_feat6')].map((feat, i) => (
            <div key={i} style={{ display:'flex', alignItems:'flex-start', gap:'10px' }}>
              <div style={{ width:'20px', height:'20px', borderRadius:'50%', background:'var(--accent-glow)', border:'1px solid rgba(34,197,94,0.25)', display:'flex', alignItems:'center', justifyContent:'center', flexShrink:0, marginTop:'1px' }}>
                <CheckCircle2 size={11} color="var(--accent)" />
              </div>
              <span style={{ fontSize:'0.85rem', color:'var(--text2)', lineHeight:1.55 }}>{feat}</span>
            </div>
          ))}
        </div>
      </Card>

      {/* ── Tech Stack ── */}
      <div>
        <h2 style={{ fontSize:'1.05rem', fontWeight:700, color:'var(--text)', marginBottom:'16px' }}>{t('ab_tech_title')}</h2>
        <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fit, minmax(220px, 1fr))', gap:'14px' }}>
          {TECH_STACK.map(({ cat, items }) => (
            <Card key={cat}>
              <div style={{ display:'flex', alignItems:'center', gap:'8px', marginBottom:'12px' }}>
                <Code2 size={14} color="var(--text3)" />
                <p style={{ fontWeight:700, fontSize:'0.875rem', color:'var(--text)' }}>{cat}</p>
              </div>
              <div style={{ display:'flex', flexWrap:'wrap', gap:'6px' }}>
                {items.map(item => (
                  <span key={item} style={{ fontSize:'0.7rem', background:'var(--surface2)', border:'1px solid var(--border)', color:'var(--text2)', padding:'3px 8px', borderRadius:'6px' }}>{item}</span>
                ))}
              </div>
            </Card>
          ))}
        </div>
      </div>

      {/* ── Dataset ── */}
      <Card>
        <div style={{ display:'flex', alignItems:'center', gap:'12px', marginBottom:'14px' }}>
          <div style={{ width:'36px', height:'36px', borderRadius:'10px', background:'var(--amber-glow)', border:'1px solid rgba(245,158,11,0.25)', display:'flex', alignItems:'center', justifyContent:'center' }}>
            <Database size={17} color="var(--amber)" />
          </div>
          <h2 style={{ fontSize:'1.05rem', fontWeight:700, color:'var(--text)' }}>{t('ab_data_title')}</h2>
        </div>
        <p style={{ color:'var(--text2)', lineHeight:1.75, fontSize:'0.9rem', marginBottom:'16px' }}>{t('ab_data_body')}</p>
        <div style={{ display:'grid', gridTemplateColumns:'repeat(3,1fr)', gap:'10px' }}>
          {[
            { v: '15,400', l: 'Samples'    },
            { v: '22',     l: 'Crop Types' },
            { v: '17',     l: 'Features'   },
          ].map(({ v, l }) => (
            <div key={l} style={{ background:'var(--amber-glow)', border:'1px solid rgba(245,158,11,0.2)', borderRadius:'12px', padding:'14px', textAlign:'center' }}>
              <p style={{ fontSize:'1.4rem', fontWeight:800, color:'var(--amber)', fontFamily:"'Space Grotesk',sans-serif" }}>{v}</p>
              <p style={{ fontSize:'0.7rem', color:'var(--text3)', marginTop:'4px' }}>{l}</p>
            </div>
          ))}
        </div>
      </Card>

    </div>
  )
}
