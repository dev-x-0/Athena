import React,{useState,useEffect} from 'react';
import {createRoot} from 'react-dom/client';
import {motion,AnimatePresence} from 'framer-motion';
import {LayoutDashboard, Megaphone, Package, Boxes, Sparkles, BrainCircuit, Settings, ChevronRight, ArrowUpRight, ArrowDownRight, Search, Bell, Activity, ShieldCheck} from 'lucide-react';
import {LineChart,Line,XAxis,YAxis,Tooltip,ResponsiveContainer} from 'recharts';
import {
    campaigns,
    products,
    findings,
    trend,
    summary,
    loadDashboard
} from './data/demo';
import './index.css';
import logo from './assets/athena-logo.png';
import introVideo from './assets/athena-intro.mov';

function Mark(){
    return (
        <div className="relative h-10 w-10 rounded-xl border border-[#718198]/40 bg-[#0a1624] flex items-center justify-center overflow-hidden">
            <img
                src={logo}
                alt="Athena emblem"
                className="h-full w-full object-cover object-center opacity-95"
            />
        </div>
    );
}

function Intro({onEnter}){
    const [ended, setEnded] = useState(false);

    useEffect(() => {
        document.body.style.overflow = 'hidden';
        return () => { document.body.style.overflow = ''; };
    }, []);

    const finish = () => {
        if (!ended) setEnded(true);
    };

    return (
        <motion.div
            initial={{opacity: 1}}
            animate={{opacity: ended ? 0 : 1}}
            transition={{duration: 0.85, ease: 'easeInOut'}}
            onAnimationComplete={() => {
                if (ended) onEnter();
            }}
            className="fixed inset-0 z-[100] bg-[#050b13] overflow-hidden"
            aria-label="Athena introduction"
        >
            <video
                className="absolute inset-0 h-full w-full object-contain bg-[#050b13]"
                src={introVideo}
                autoPlay
                muted
                playsInline
                preload="auto"
                onEnded={finish}
                onError={finish}
            />

            <div className="absolute inset-0 pointer-events-none bg-[#050b13]/[0.02]" />

            {ended && (
                <motion.div
                    initial={{opacity: 0}}
                    animate={{opacity: 1}}
                    transition={{duration: 0.2}}
                    className="absolute inset-0 bg-[#050b13]"
                />
            )}
        </motion.div>
    );
}
function Sidebar({page,setPage}){let items=[['Overview',LayoutDashboard],['Campaigns',Megaphone],['Products',Package],['Inventory',Boxes],['Creatives',Sparkles],['Insights',BrainCircuit]];return <aside className="w-60 shrink-0 border-r border-[#1a2a3b] bg-[#060d16] p-5 hidden md:flex flex-col"><div className="flex items-center gap-3 mb-10"><Mark/><div><div className="font-semibold tracking-[.18em]">ATHENA</div></div></div><nav className="space-y-1">{items.map(([name,Icon])=><button key={name} onClick={()=>setPage(name)} className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition ${page===name?'bg-[#102033] text-[#e9eff6]':'text-[#718198] hover:text-[#cbd5e1] hover:bg-[#0b1724]'}`}><Icon size={16}/>{name}</button>)}</nav><div className="mt-auto"><div className="line mb-4"/><button className="w-full flex items-center gap-3 px-3 py-2.5 text-sm text-[#718198]"><Settings size={16}/>Settings</button></div></aside>}
function Topbar(){

    const syncTime = new Date().toLocaleTimeString(
        [],
        {
            hour: '2-digit',
            minute: '2-digit'
        }
    );

    return (
        <header className="h-16 border-b border-[#1a2a3b] flex items-center justify-between px-5 md:px-8 bg-[#07101b]/90">

            <div className="md:hidden flex items-center gap-2">
                <Mark/>
                <span className="tracking-[.18em] text-sm">
                    ATHENA
                </span>
            </div>

            <div className="hidden md:block text-xs text-[#718198]">
                Decision intelligence /
                <span className="text-[#b8c3d1]">
                    Overview
                </span>
            </div>

            <div className="flex items-center gap-4">

                <div className="hidden sm:flex items-center gap-2 text-xs text-[#718198]">

                    <span className="h-2 w-2 rounded-full bg-emerald-400"/>

                    Data synced · {syncTime}

                </div>

                <Bell
                    size={17}
                    className="text-[#718198]"
                />

            </div>

        </header>
    );
}
function KPI({label,value,note}){return <div className="rounded-xl border border-[#1a2a3b] bg-[#091522] p-4"><div className="text-[10px] uppercase tracking-[.18em] text-[#718198]">{label}</div><div className="mt-2 text-2xl font-semibold text-[#edf2f7]">{value}</div><div className="mt-1 text-[11px] text-[#65788e]">{note}</div></div>}
function Insight({f}){let map={critical:['#ff6b7d','CRITICAL'],warning:['#e4b35c','WARNING'],opportunity:['#5ed7bb','OPPORTUNITY'],observation:['#7f9bb8','OBSERVATION']};let [c,label]=map[f.type];return <div className="group rounded-xl border border-[#1a2a3b] bg-[#091522] p-4 hover:border-[#2a4056] transition"><div className="flex items-center justify-between"><span style={{color:c}} className="text-[9px] tracking-[.18em] font-semibold">{label}</span><ChevronRight size={15} className="text-[#52667c] group-hover:text-[#b7c4d3]"/></div><div className="mt-3 text-sm font-medium leading-5 text-[#e7edf4]">{f.title}</div><p className="mt-2 text-xs leading-5 text-[#7d8fa4]">{f.body}</p><div className="mt-3 flex items-center justify-between border-t border-[#172636] pt-3"><span className="text-[11px] text-[#a9b7c7]">{f.metric}</span><span className="text-[10px] text-[#a9b7c7]">{f.action} →</span></div></div>}
function Overview(){

    const formatCurrency = (value) => {

        if (Math.abs(value) >= 1000000) {
            return `₹${(value / 1000000).toFixed(1)}M`;
        }

        if (Math.abs(value) >= 1000) {
            return `₹${(value / 1000).toFixed(1)}K`;
        }

        return `₹${value.toFixed(0)}`;
    };

    return (

        <div>

            <div className="mb-7">

                <div className="text-xs uppercase tracking-[.2em] text-[#718198]">
                    Overview
                </div>

                <h1 className="mt-2 text-3xl font-medium tracking-tight">
                    Good afternoon.
                </h1>

                <p className="mt-1 text-sm text-[#718198]">
                    Here’s what Athena sees across your D2C operation.
                </p>

            </div>


            {/* =================================================
                LIVE KPI DATA
            ================================================= */}

            <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">

                <KPI
                    label="Ad spend"
                    value={formatCurrency(summary.ad_spend)}
                    note="Across active campaigns"
                />

                <KPI
                    label="Revenue"
                    value={formatCurrency(summary.revenue)}
                    note="Recorded net revenue"
                />

                <KPI
                    label="ROAS"
                    value={`${summary.roas.toFixed(2)}×`}
                    note="Revenue / ad spend"
                />

                <KPI
                    label="Contribution"
                    value={formatCurrency(summary.contribution)}
                    note="Revenue − cost − ads"
                />

            </div>


            <div className="grid lg:grid-cols-[1.55fr_1fr] gap-4 mt-4">


                {/* =================================================
                    PERFORMANCE TREND
                ================================================= */}

                <section className="rounded-xl border border-[#1a2a3b] bg-[#091522] p-5">

                    <div className="flex justify-between items-start mb-4">

                        <div>

                            <h2 className="text-sm font-medium">
                                Performance trend
                            </h2>

                            <p className="text-xs text-[#718198] mt-1">
                                Spend vs attributed revenue
                            </p>

                        </div>

                        <span className="text-[10px] text-[#65788e]">
                            Last {trend.length} days
                        </span>

                    </div>


                    <div className="h-64">

                        <ResponsiveContainer
                            width="100%"
                            height="100%"
                        >

                            <LineChart data={trend}>

                                <XAxis
                                    dataKey="d"
                                    hide
                                />

                                <YAxis hide/>

                                <Tooltip
                                    contentStyle={{
                                        background:'#08131f',
                                        border:'1px solid #22364b',
                                        borderRadius:8,
                                        color:'#fff'
                                    }}
                                />

                                <Line
                                    type="monotone"
                                    dataKey="revenue"
                                    stroke="#d8e0ea"
                                    strokeWidth={2}
                                    dot={false}
                                />

                                <Line
                                    type="monotone"
                                    dataKey="spend"
                                    stroke="#4b6b8b"
                                    strokeWidth={1.5}
                                    dot={false}
                                />

                            </LineChart>

                        </ResponsiveContainer>

                    </div>


                    <div className="flex gap-5 text-[10px] text-[#718198]">

                        <span>
                            — Revenue
                        </span>

                        <span className="text-[#4b6b8b]">
                            — Spend
                        </span>

                    </div>

                </section>


                {/* =================================================
                    ATHENA FINDINGS
                ================================================= */}

                <section>

                    <div className="flex items-center justify-between mb-3">

                        <div>

                            <h2 className="text-sm font-medium">
                                Athena’s attention
                            </h2>

                            <p className="text-xs text-[#718198] mt-1">
                                Prioritized findings
                            </p>

                        </div>

                        <button className="text-[10px] text-[#91a5ba] hover:text-white">
                            View all →
                        </button>

                    </div>


                    <div className="space-y-2">

                        {findings
                            .slice(0,3)
                            .map((f) => (

                                <Insight
                                    key={f.title}
                                    f={f}
                                />

                            ))
                        }

                    </div>

                </section>

            </div>

        </div>
    );
}
function Campaigns(){return <div><PageHead title="Campaigns" sub="Performance across paid channels."/><div className="flex items-center gap-3 mb-4"><div className="flex items-center gap-2 flex-1 max-w-sm rounded-lg border border-[#1a2a3b] bg-[#091522] px-3 py-2"><Search size={15} className="text-[#718198]"/><span className="text-xs text-[#52667c]">Search campaigns...</span></div><button className="text-xs border border-[#1a2a3b] rounded-lg px-3 py-2 text-[#8da0b4]">All platforms</button></div><Table headers={['Campaign','Platform','Spend','Revenue','ROAS','Conversions','Athena action']} rows={campaigns.map(c=>[c.name,c.platform,`₹${(c.spend/1000).toFixed(1)}K`,`₹${(c.revenue/1000).toFixed(1)}K`,c.roas?`${c.roas.toFixed(2)}x`:'0x',c.conv,c.status])}/></div>}
function Products(){return <div><PageHead title="Products" sub="Margin, inventory and advertising economics by SKU."/><Table headers={['SKU','Product','Margin','Stock','Ad spend','Revenue','ROAS','Status']} rows={products}/></div>}
function Insights(){return <div><PageHead title="Athena’s insights" sub="Decisions organized by urgency, opportunity and evidence."/><div className="grid md:grid-cols-2 gap-3">{findings.map(f=><Insight key={f.title} f={f}/>)}</div></div>}
function Placeholder({title,sub}){return <div><PageHead title={title} sub={sub}/><div className="rounded-xl border border-dashed border-[#24384d] bg-[#091522]/50 p-16 text-center"><Activity className="mx-auto text-[#52667c]" size={24}/><p className="mt-4 text-sm text-[#a7b5c5]">This view is ready for the normalized backend data.</p><p className="mt-1 text-xs text-[#61758a]">The UI contract can connect to your teammate’s processing layer here.</p></div></div>}
function PageHead({title,sub}){return <div className="mb-7"><div className="text-xs uppercase tracking-[.2em] text-[#718198]">Athena</div><h1 className="mt-2 text-3xl font-medium tracking-tight">{title}</h1><p className="mt-1 text-sm text-[#718198]">{sub}</p></div>}
function Table({headers,rows}){return <div className="overflow-x-auto rounded-xl border border-[#1a2a3b] bg-[#091522]"><table className="w-full text-left text-xs"><thead><tr className="border-b border-[#1a2a3b] text-[#65788e]">{headers.map(h=><th key={h} className="px-4 py-3 font-medium whitespace-nowrap">{h}</th>)}</tr></thead><tbody>{rows.map((r,i)=><tr key={i} className="border-b border-[#132333] last:border-0 hover:bg-[#0b1826] transition">{r.map((x,j)=><td key={j} className={`px-4 py-3.5 whitespace-nowrap ${j===0?'text-[#e5ebf2] font-medium':'text-[#8295a9]'}`}>{x}</td>)}</tr>)}</tbody></table></div>}
function App(){

    const [intro,setIntro] = useState(true);

    const [page,setPage] = useState(
        'Overview'
    );

    const [loading,setLoading] = useState(
        true
    );

    const [error,setError] = useState(
        null
    );

    const [,forceUpdate] = useState(0);


    useEffect(() => {

        loadDashboard()

            .then(() => {

                setLoading(false);

                forceUpdate(
                    value => value + 1
                );

            })

            .catch((err) => {

                console.error(
                    "Athena backend error:",
                    err
                );

                setError(
                    err.message
                );

                setLoading(false);

            });

    }, []);


    // =====================================================
    // LOADING
    // =====================================================

    if (loading){

        return (

            <div className="min-h-screen bg-[#07101b] text-white flex items-center justify-center">

                <div className="text-center">

                    <div className="text-2xl tracking-[.3em]">
                        ATHENA
                    </div>

                    <div className="mt-3 text-[10px] uppercase tracking-[.28em] text-[#718198]">
                        Initializing
                    </div>

                </div>

            </div>

        );

    }


    // =====================================================
    // ERROR
    // =====================================================

    if (error){

        return (

            <div className="min-h-screen bg-[#07101b] text-white flex items-center justify-center">

                <div className="text-center max-w-md">

                    <div className="text-2xl tracking-[.3em]">
                        ATHENA
                    </div>

                    <div className="mt-4 text-red-400">
                        Backend connection failed
                    </div>

                    <div className="mt-2 text-sm text-[#718198]">
                        {error}
                    </div>

                    <div className="mt-4 text-xs text-[#52667c]">
                        Make sure the Athena Python API is running on port 8000.
                    </div>

                </div>

            </div>

        );

    }


    // =====================================================
    // APPLICATION
    // =====================================================

    return (

        <>

            {intro && (

                <Intro
                    onEnter={() => setIntro(false)}
                />

            )}


            <div className="min-h-screen flex bg-[#07101b]">

                <Sidebar
                    page={page}
                    setPage={setPage}
                />


                <main className="flex-1 min-w-0">

                    <Topbar/>


                    <div className="p-5 md:p-8 max-w-[1500px] mx-auto">

                        {page === 'Overview' &&
                            <Overview/>
                        }

                        {page === 'Campaigns' &&
                            <Campaigns/>
                        }

                        {page === 'Products' &&
                            <Products/>
                        }

                        {page === 'Insights' &&
                            <Insights/>
                        }

                        {page === 'Inventory' &&

                            <Placeholder
                                title="Inventory"
                                sub="Stock health and advertising exposure."
                            />

                        }

                        {page === 'Creatives' &&

                            <Placeholder
                                title="Creatives"
                                sub="Creative performance across campaigns."
                            />

                        }

                    </div>

                </main>

            </div>

        </>

    );
}
createRoot(
    document.getElementById('root')
).render(
    <App/>
);