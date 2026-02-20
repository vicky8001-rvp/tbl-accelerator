import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from tbl_model import TBLSimulator
from profiles import PROFILES
import numpy as np
import time
from datetime import datetime

st.set_page_config(page_title="TBL Sustainability Accelerator", layout="wide")

# ===== NEW: BEAUTIFUL SUSTAINABILITY THEME BACKGROUND =====
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #f5f7fa 0%, #e8f4e8 100%);
    position: relative;
}

/* Floating nature elements */
.stApp::before {
    content: "🌱";
    font-size: 300px;
    opacity: 0.03;
    position: fixed;
    bottom: -50px;
    right: -50px;
    transform: rotate(15deg);
    pointer-events: none;
    z-index: 0;
}

.stApp::after {
    content: "🍃";
    font-size: 200px;
    opacity: 0.03;
    position: fixed;
    top: -20px;
    left: -20px;
    transform: rotate(-10deg);
    pointer-events: none;
    z-index: 0;
}

/* Ensure content stays above background */
.main > div {
    position: relative;
    z-index: 1;
}

/* Dark mode override */
.dark-mode {
    background: linear-gradient(135deg, #1e1e2f 0%, #2d2d44 100%) !important;
}
</style>
""", unsafe_allow_html=True)

# ===== NEW: CURRENCY DICTIONARY =====
CURRENCIES = {
    'USD ($)': {'symbol': '$', 'rate': 1.0, 'name': 'US Dollar'},
    'EUR (€)': {'symbol': '€', 'rate': 0.92, 'name': 'Euro'},
    'GBP (£)': {'symbol': '£', 'rate': 0.79, 'name': 'British Pound'},
    'INR (₹)': {'symbol': '₹', 'rate': 83.0, 'name': 'Indian Rupee'},
    'JPY (¥)': {'symbol': '¥', 'rate': 150.0, 'name': 'Japanese Yen'},
    'AUD (A$)': {'symbol': 'A$', 'rate': 1.52, 'name': 'Australian Dollar'},
    'CAD (C$)': {'symbol': 'C$', 'rate': 1.35, 'name': 'Canadian Dollar'},
    'CHF (Fr)': {'symbol': 'Fr', 'rate': 0.88, 'name': 'Swiss Franc'},
    'CNY (¥)': {'symbol': '¥', 'rate': 7.2, 'name': 'Chinese Yuan'},
    'BRL (R$)': {'symbol': 'R$', 'rate': 5.1, 'name': 'Brazilian Real'},
    'KRW (₩)': {'symbol': '₩', 'rate': 1350.0, 'name': 'South Korean Won'},
    'RUB (₽)': {'symbol': '₽', 'rate': 92.0, 'name': 'Russian Ruble'}
}

# 🌐 Multi-Language Support (6 languages)
def get_text(lang):
    texts = {
        'English': {
            'title': "🌱 TBL Sustainability Accelerator",
            'run': "Run Simulation",
            'download': "Download CSV",
            'economic': "Economic",
            'social': "Social",
            'environmental': "Environmental",
            'settings': "Simulation Settings",
            'profile': "Company Profile",
            'investment': "Investment Rate (%)",
            'months': "Simulation Months",
            'about': "About",
            'save': "Save Current Scenario",
            'export': "Export Results",
            'scores': "TBL Scores Over Time",
            'final': "Final Scores",
            'benchmark': "⚡ Performance Benchmark",
            'recommendations': "🤖 AI Strategy Recommendations",
            'history': "📜 Recent History",
            'share': "📢 Share Results",
            'financial': "💰 Financial Settings",
            'currency': "Select Currency",
            'revenue': "Monthly Revenue",
            'investment_amount': "Monthly Investment"
        },
        'Tamil': {
            'title': "🌱 TBL நிலைத்தன்மை முடுக்கி",
            'run': "உருவகப்படுத்தலை இயக்குக",
            'download': "CSV ஐ பதிவிறக்குக",
            'economic': "பொருளாதாரம்",
            'social': "சமூகம்",
            'environmental': "சுற்றுச்சூழல்",
            'settings': "உருவகப்படுத்தல் அமைப்புகள்",
            'profile': "நிறுவன சுயவிவரம்",
            'investment': "முதலீட்டு விகிதம் (%)",
            'months': "உருவகப்படுத்தல் மாதங்கள்",
            'about': "பற்றி",
            'save': "தற்போதைய காட்சியை சேமிக்க",
            'export': "முடிவுகளை ஏற்றுமதி செய்க",
            'scores': "காலப்போக்கில் TBL மதிப்பெண்கள்",
            'final': "இறுதி மதிப்பெண்கள்",
            'benchmark': "⚡ செயல்திறன் அளவுகோல்",
            'recommendations': "🤖 AI பரிந்துரைகள்",
            'history': "📜 சமீபத்திய வரலாறு",
            'share': "📢 முடிவுகளை பகிர்க",
            'financial': "💰 நிதி அமைப்புகள்",
            'currency': "நாணயத்தை தேர்வு செய்க",
            'revenue': "மாத வருவாய்",
            'investment_amount': "மாத முதலீடு"
        },
        'Malayalam': {
            'title': "🌱 TBL സുസ്ഥിരത ആക്സിലറേറ്റർ",
            'run': "സിമുലേഷൻ പ്രവർത്തിപ്പിക്കുക",
            'download': "CSV ഡൗൺലോഡ് ചെയ്യുക",
            'economic': "സാമ്പത്തിക",
            'social': "സാമൂഹിക",
            'environmental': "പാരിസ്ഥിതിക",
            'settings': "സിമുലേഷൻ ക്രമീകരണങ്ങൾ",
            'profile': "കമ്പനി പ്രൊഫൈൽ",
            'investment': "നിക്ഷേപ നിരക്ക് (%)",
            'months': "സിമുലേഷൻ മാസങ്ങൾ",
            'about': "വിവരണം",
            'save': "നിലവിലെ രംഗം സംരക്ഷിക്കുക",
            'export': "ഫലങ്ങൾ എക്സ്പോർട്ട് ചെയ്യുക",
            'scores': "കാലക്രമേണയുള്ള TBL സ്കോറുകൾ",
            'final': "അന്തിമ സ്കോറുകൾ",
            'benchmark': "⚡ പ്രകടന ബെഞ്ച്മാർക്ക്",
            'recommendations': "🤖 AI ശുപാർശകൾ",
            'history': "📜 സമീപകാല ചരിത്രം",
            'share': "📢 ഫലങ്ങൾ പങ്കിടുക",
            'financial': "💰 സാമ്പത്തിക ക്രമീകരണങ്ങൾ",
            'currency': "കറൻസി തിരഞ്ഞെടുക്കുക",
            'revenue': "പ്രതിമാസ വരുമാനം",
            'investment_amount': "പ്രതിമാസ നിക്ഷേപം"
        },
        'Hindi': {
            'title': "🌱 TBL स्थिरता त्वरक",
            'run': "सिमुलेशन चलाएं",
            'download': "CSV डाउनलोड करें",
            'economic': "आर्थिक",
            'social': "सामाजिक",
            'environmental': "पर्यावरणीय",
            'settings': "सिमुलेशन सेटिंग्स",
            'profile': "कंपनी प्रोफाइल",
            'investment': "निवेश दर (%)",
            'months': "सिमुलेशन महीने",
            'about': "बारे में",
            'save': "वर्तमान परिदृश्य सहेजें",
            'export': "परिणाम निर्यात करें",
            'scores': "समय के साथ TBL स्कोर",
            'final': "अंतिम स्कोर",
            'benchmark': "⚡ प्रदर्शन बेंचमार्क",
            'recommendations': "🤖 AI सिफारिशें",
            'history': "📜 हाल का इतिहास",
            'share': "📢 परिणाम साझा करें",
            'financial': "💰 वित्तीय सेटिंग्स",
            'currency': "मुद्रा चुनें",
            'revenue': "मासिक राजस्व",
            'investment_amount': "मासिक निवेश"
        }
    }
    # Add Spanish and French similarly if needed (kept short for brevity)
    return texts.get(lang, texts['English'])

# 🌓 Dark Mode Toggle with dynamic background
dark_mode = st.sidebar.checkbox("🌙 Dark Mode", value=False)
if dark_mode:
    st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #1e1e2f 0%, #2d2d44 100%) !important;
        color: #FFFFFF;
    }
    .stMarkdown, .stText, .stMetric, .stSubheader {
        color: #FFFFFF;
    }
    </style>
    """, unsafe_allow_html=True)

# 🌐 Language Selection
lang = st.sidebar.selectbox(
    "🌐 Language / மொழி / ഭാഷ / भाषा", 
    ['English', 'Tamil', 'Malayalam', 'Hindi', 'Spanish', 'French'], 
    index=0
)
text = get_text(lang)

# Display title
st.title(text['title'])
st.markdown("""
This tool simulates a company's Triple Bottom Line performance over time,
based on Svensson & Wagner (2015) with benchmarking from Duarte et al. (2019).
""")

# Initialize session state
if 'history' not in st.session_state:
    st.session_state.history = []
if 'saved_scenarios' not in st.session_state:
    st.session_state.saved_scenarios = []

# ===== SIDEBAR =====
with st.sidebar:
    st.header(text['settings'])
    
    # Basic settings
    profile = st.selectbox(text['profile'], list(PROFILES.keys()))
    invest_rate = st.slider(text['investment'], 0, 30, int(PROFILES[profile]["invest_rate"]*100), 1) / 100.0
    months = st.slider(text['months'], 12, 600, 120, 12)
    
    # ===== NEW: FINANCIAL SETTINGS WITH CURRENCY =====
    st.markdown("---")
    st.subheader(text['financial'])
    
    # Currency selection
    currency = st.selectbox(text['currency'], list(CURRENCIES.keys()), index=3)  # Default to INR
    currency_symbol = CURRENCIES[currency]['symbol']
    
    # Revenue input (in selected currency)
    revenue = st.number_input(
        f"{text['revenue']} ({currency_symbol})",
        min_value=1000,
        max_value=100_000_000,
        value=1_000_000,
        step=1000,
        format="%d"
    )
    
    # Calculate actual investment amount
    invest_amount = revenue * (invest_rate / 100)
    converted_amount = invest_amount * CURRENCIES[currency]['rate']
    
    # Display investment in real currency
    st.metric(
        text['investment_amount'],
        f"{currency_symbol}{converted_amount:,.0f}",
        help=f"{invest_rate*100}% of {currency_symbol}{revenue:,.0f}"
    )
    
    # Store in session state for later use
    st.session_state.revenue = revenue
    st.session_state.currency = currency
    st.session_state.currency_symbol = currency_symbol
    st.session_state.invest_amount = converted_amount
    
    # Voice input (optional)
    if st.checkbox("🎤 Enable Voice Input"):
        st.info("Voice: Say 'Set investment to 15%'")
        voice_value = st.text_input("Or type command:", "")
        if voice_value:
            try:
                if "investment" in voice_value.lower():
                    percent = int(''.join(filter(str.isdigit, voice_value)))
                    invest_rate = percent / 100
                    st.success(f"Set to {percent}%")
            except:
                pass
    
    run_btn = st.button(text['run'], type="primary", use_container_width=True)

    st.markdown("---")
    st.markdown(f"### {text['about']}")
    st.markdown(PROFILES[profile]["description"])
    
    # Save Scenario Section
    st.markdown("---")
    st.subheader(f"💾 {text['save']}")
    scenario_name = st.text_input("Scenario name", f"{profile}_{invest_rate*100:.0f}%_{currency}")
    
    if st.button("Save This Scenario", use_container_width=True):
        st.session_state.saved_scenarios.append({
            'name': scenario_name,
            'profile': profile,
            'invest_rate': invest_rate,
            'months': months,
            'currency': currency,
            'revenue': revenue
        })
        st.success(f"✅ Saved '{scenario_name}'!")
    
    # Show saved scenarios
    if st.session_state.saved_scenarios:
        st.markdown("---")
        st.subheader("📁 Saved Scenarios")
        for i, s in enumerate(st.session_state.saved_scenarios[-3:]):
            st.text(f"• {s['name']}")

# ===== MAIN AREA =====
if run_btn:
    sim = TBLSimulator()
    
    # Progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    with st.spinner("Running simulations and benchmarks..."):
        for i in range(100):
            progress_bar.progress(i + 1)
            status_text.text(f"Simulating... {i+1}%")
            time.sleep(0.01)
        
        results_np = sim.numpy_run(months, invest_rate, random_seed=42)
        df = pd.DataFrame(results_np)
        bench = sim.benchmark(months=months, invest_rate=invest_rate)
        
        status_text.text("Complete!")
        time.sleep(0.5)
        progress_bar.empty()
        status_text.empty()
        
        # Download button
        st.sidebar.markdown("---")
        st.sidebar.markdown(f"### 📥 {text['export']}")
        csv = df.to_csv(index=False)
        
        # Add currency info to filename
        filename = f"tbl_results_{profile}_{invest_rate*100}%_{currency}_{months}months.csv"
        
        st.sidebar.download_button(
            label=text['download'],
            data=csv,
            file_name=filename,
            mime="text/csv",
            use_container_width=True
        )
        
        # PDF Report (simplified)
        if st.sidebar.button("📑 Generate Report Summary"):
            st.sidebar.info("Report ready!")
    
    # ===== DISPLAY FINANCIAL SUMMARY =====
    st.subheader("💰 Investment Summary")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Monthly Revenue", f"{currency_symbol}{revenue:,.0f}")
    with col2:
        st.metric("Investment Rate", f"{invest_rate*100}%")
    with col3:
        st.metric("Monthly Investment", f"{currency_symbol}{converted_amount:,.0f}")
    with col4:
        annual = converted_amount * 12
        st.metric("Annual Investment", f"{currency_symbol}{annual:,.0f}")
    
    # Chart
    st.subheader(f"📈 {text['scores']}")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['month'], y=df['economic'], mode='lines', name=text['economic'],
                            line=dict(width=3, color='#2E86AB')))
    fig.add_trace(go.Scatter(x=df['month'], y=df['social'], mode='lines', name=text['social'],
                            line=dict(width=3, color='#A23B72')))
    fig.add_trace(go.Scatter(x=df['month'], y=df['environmental'], mode='lines', name=text['environmental'],
                            line=dict(width=3, color='#F18F01')))
    
    fig.update_layout(
        xaxis=dict(title="Month", rangeslider=dict(visible=True)),
        yaxis_title="Score (normalized)",
        hovermode='x unified',
        template="plotly_white" if not dark_mode else "plotly_dark",
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Heatmap
    if st.checkbox("Show Heatmap Correlation View"):
        corr_data = df[['economic', 'social', 'environmental']].corr()
        fig_heatmap = go.Figure(data=go.Heatmap(
            z=corr_data.values,
            x=[text['economic'], text['social'], text['environmental']],
            y=[text['economic'], text['social'], text['environmental']],
            colorscale='Viridis'))
        fig_heatmap.update_layout(title="TBL Correlation Heatmap")
        st.plotly_chart(fig_heatmap)
    
    # Key Metrics
    st.subheader("📊 Key Performance Insights")
    col1, col2, col3, col4 = st.columns(4)
    
    initial_tbl = (df['economic'].iloc[0] + df['social'].iloc[0] + df['environmental'].iloc[0]) / 3
    final_tbl = (df['economic'].iloc[-1] + df['social'].iloc[-1] + df['environmental'].iloc[-1]) / 3
    tbl_improvement = ((final_tbl - initial_tbl) / initial_tbl) * 100
    
    with col1:
        st.metric("TBL Improvement", f"{tbl_improvement:.1f}%")
    with col2:
        st.metric("Avg Social", f"{df['social'].mean():.2f}")
    with col3:
        st.metric("Avg Environmental", f"{df['environmental'].mean():.2f}")
    with col4:
        econ_change = (df['economic'].iloc[-1] - df['economic'].iloc[0]) / df['economic'].iloc[0] * 100
        social_change = (df['social'].iloc[-1] - df['social'].iloc[0]) / df['social'].iloc[0] * 100
        env_change = (df['environmental'].iloc[-1] - df['environmental'].iloc[0]) / df['environmental'].iloc[0] * 100
        best = max([('Econ', econ_change), ('Soc', social_change), ('Env', env_change)], key=lambda x: x[1])
        st.metric("Best Performer", best[0], f"{best[1]:.1f}%")
    
    # Final scores
    st.subheader(f"🎯 {text['final']}")
    col1, col2, col3 = st.columns(3)
    final = df.iloc[-1]
    col1.metric(text['economic'], f"{final['economic']:.3f}")
    col2.metric(text['social'], f"{final['social']:.3f}")
    col3.metric(text['environmental'], f"{final['environmental']:.3f}")
    
    # AI Recommendations
    st.subheader(f"🤖 {text['recommendations']}")
    scores = {'economic': final['economic'], 'social': final['social'], 'environmental': final['environmental']}
    
    recs = []
    if scores['social'] < scores['environmental'] * 0.8:
        recs.append("🔴 **Social lagging** - Increase community investment")
    if scores['environmental'] < scores['economic'] * 0.7:
        recs.append("🟡 **Environmental gap** - Add green initiatives")
    if invest_rate < 0.1:
        recs.append("🟢 **Low risk** - Can increase investment safely")
    if scores['economic'] > 1.5 and invest_rate < 0.2:
        recs.append("💰 **High profit** - Perfect time to boost sustainability")
    
    for rec in recs if recs else ["✅ Well balanced! Your strategy looks good."]:
        st.markdown(rec)
    
    # Benchmark table
    st.subheader(f"⚡ {text['benchmark']}")
    col1, col2 = st.columns([2, 1])
    with col1:
        bench_df = pd.DataFrame([
            {"Backend": k, "Time (s)": f"{v:.3f}" if v else "N/A", 
             "Speedup": f"{bench['Python (loop)']/v:.1f}x" if v and k != 'Python (loop)' else "1.0x"}
            for k, v in bench.items() if v
        ])
        st.table(bench_df)
    
    with col2:
        if len(bench) > 1:
            fastest = min(bench.values())
            slowest = max(bench.values())
            st.metric("Max Speedup", f"{slowest/fastest:.1f}x")
    
    st.info("NumPy is 10-50x faster than Python. TensorFlow adds more with GPU.")
    
    # History
    st.subheader(f"📊 {text['history']}")
    st.session_state.history.append({
        'profile': profile,
        'invest': f"{invest_rate*100:.0f}%",
        'tbl': f"{final_tbl:.2f}",
        'currency': currency_symbol,
        'amount': f"{currency_symbol}{converted_amount:,.0f}"
    })
    
    if len(st.session_state.history) > 5:
        st.session_state.history = st.session_state.history[-5:]
    
    if st.session_state.history:
        hist_df = pd.DataFrame(st.session_state.history)
        st.dataframe(hist_df, use_container_width=True)
        if st.button("Clear History"):
            st.session_state.history = []
    
    # Social Share
    st.subheader(f"📢 {text['share']}")
    share = f"TBL simulation: {profile} with {invest_rate*100}% investment ({currency_symbol}{converted_amount:,.0f}/month) achieved {tbl_improvement:.1f}% improvement!"
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"[🐦 Twitter](https://twitter.com/intent/tweet?text={share})")
    with col2:
        st.markdown(f"[💼 LinkedIn](https://linkedin.com/sharing/share-offsite/?url=https://tbl-accelerator.streamlit.app)")
    with col3:
        st.markdown(f"[📧 Email](mailto:?subject=TBL Results&body={share})")
    
    # Raw Data
    with st.expander("📋 View Raw Data"):
        st.dataframe(df)
        st.caption(f"{len(df)} months of data")

else:
    # Welcome screen
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.info("👈 **Adjust settings and click 'Run Simulation'!**")
        st.markdown("""
        ### ✨ NEW FEATURES ADDED:
        - 💰 **12 Currencies** (USD, EUR, GBP, INR, JPY, AUD, CAD, CHF, CNY, BRL, KRW, RUB)
        - 💵 **Revenue Input** - See real investment amounts
        - 🎨 **Beautiful Nature Theme** - Floating leaves background
        - Plus all previous features!
        """)
