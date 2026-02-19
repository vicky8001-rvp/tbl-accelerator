import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from tbl_model import TBLSimulator
from profiles import PROFILES

st.set_page_config(page_title="TBL Sustainability Accelerator", layout="wide")
st.title("🌱 TBL Sustainability Accelerator")
st.markdown("""
This tool simulates a company's Triple Bottom Line (economic, social, environmental) performance over time,
based on the framework of Svensson & Wagner (2015). It also benchmarks computation speed using different backends,
inspired by Duarte et al. (2019).
""")

# Sidebar inputs
with st.sidebar:
    st.header("Simulation Settings")
    profile = st.selectbox("Company Profile", list(PROFILES.keys()))
    invest_rate = st.slider("Investment Rate (%)", 0, 30, int(PROFILES[profile]["invest_rate"]*100), 1) / 100.0
    months = st.slider("Simulation Months", 12, 600, 120, 12)
    run_btn = st.button("Run Simulation")

    st.markdown("---")
    st.markdown("### About")
    st.markdown(PROFILES[profile]["description"])

# Main area
if run_btn:
    sim = TBLSimulator()
    with st.spinner("Running simulations and benchmarks..."):
        # Get results from all three backends
        results_np = sim.numpy_run(months, invest_rate, random_seed=42)
        df = pd.DataFrame(results_np)
        
        # Benchmark
        bench = sim.benchmark(months=months, invest_rate=invest_rate)
        
        # 📊 DOWNLOAD BUTTON - Add this new section
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 📥 Export Results")
        
        # Convert DataFrame to CSV
        csv = df.to_csv(index=False)
        
        # Create download button
        st.sidebar.download_button(
            label="📊 Download Simulation Data (CSV)",
            data=csv,
            file_name=f"tbl_results_{profile}_{months}months.csv",
            mime="text/csv",
            help="Click to download the simulation results as a CSV file"
        )
    # Display chart
    st.subheader("TBL Scores Over Time")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['month'], y=df['economic'], mode='lines', name='Economic'))
    fig.add_trace(go.Scatter(x=df['month'], y=df['social'], mode='lines', name='Social'))
    fig.add_trace(go.Scatter(x=df['month'], y=df['environmental'], mode='lines', name='Environmental'))
    fig.update_layout(xaxis_title="Month", yaxis_title="Score (normalized)", hovermode='x unified')
    st.plotly_chart(fig, use_container_width=True)

    # Final scores
    final = df.iloc[-1]
    col1, col2, col3 = st.columns(3)
    col1.metric("Final Economic Score", f"{final['economic']:.3f}")
    col2.metric("Final Social Score", f"{final['social']:.3f}")
    col3.metric("Final Environmental Score", f"{final['environmental']:.3f}")

    # Benchmark table
    st.subheader("⚡ Performance Benchmark")
    bench_df = pd.DataFrame([
        {"Backend": k, "Time (s)": f"{v:.3f}" if v else "N/A", "Speedup": f"{bench['Python (loop)']/v:.1f}x" if v else "N/A"}
        for k, v in bench.items() if v is not None
    ])
    st.table(bench_df)

    st.info(f"NumPy is typically 10-50x faster than pure Python. TensorFlow may add another 2-5x if GPU is available.")

else:
    st.info("👈 Adjust settings and click 'Run Simulation' to start.")
