import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# --- PAGE CONFIG ---
st.set_page_config(page_title="Cast Film ROI Advisor", layout="wide")

# --- TRANSLATION DICTIONARY ---
lang_dict = {
    "English": {
        "title": "ROI Estimate: High-Performance Multilayer CAST Line",
        "sidebar_mats": "Raw Material Costs (€/kg)",
        "sidebar_utils": "Global Parameters & Utilities",
        "recipe_title": "🧪 Recipe Configuration (Manual Comparison)",
        "line_std": "Standard CAST Line",
        "line_pre": "High-Perf CAST Line",
        "res_title": "🏁 Comparative Economic Analysis",
        "ann_save": "Total Annual Saving",
        "cost_kg": "Unit Cost (€/kg)",
        "chart_cost": "Variable Cost Breakdown (€/kg Film)",
        "chart_roi": "Full Investment Payback (Cash Flow)",
        "table_prod": "Actual Annual Production (kg)",
        "table_mat": "Raw Material Cost (€/year)",
        "table_ene": "Energy Cost (€/year)",
        "table_tot": "TOTAL VARIABLE COST (€/year)",
        "payback": "Individual Line Payback",
        "saving_kg": "Saving per kg",
        "shared_output": "Nominal Hourly Output (kg/h)",
        "oee_label": "OEE (Efficiency %)",
        "margin_label": "Assumed Sales Margin (€/kg)"
    },
    "Italiano": {
        "title": "Stima ROI: Linea CAST Multistrato High-Performance",
        "sidebar_mats": "Costi Materie Prime (€/kg)",
        "sidebar_utils": "Parametri Globali & Utility",
        "recipe_title": "🧪 Configurazione Ricetta (Confronto Manuale)",
        "line_std": "Linea CAST Standard",
        "line_pre": "Linea CAST High-Perf",
        "res_title": "🏁 Analisi Economica Comparativa",
        "ann_save": "Risparmio Totale Annuo",
        "cost_kg": "Costo Unitario (€/kg)",
        "chart_cost": "Composizione Costo Variabile (€/kg Film)",
        "chart_roi": "Payback Totale Investimento (Cash Flow)",
        "table_prod": "Produzione Annua Reale (kg)",
        "table_mat": "Costo Materia Prima (€/anno)",
        "table_ene": "Costo Energia (€/anno)",
        "table_tot": "COSTO TOTALE VARIABILE (€/anno)",
        "payback": "Payback Singola Linea",
        "saving_kg": "Risparmio al kg",
        "shared_output": "Portata Oraria Nominale (kg/h)",
        "oee_label": "OEE (Efficienza %)",
        "margin_label": "Margine di Vendita Ipotizzato (€/kg)"
    }
}

# --- LANGUAGE MANAGEMENT ---
if 'lang' not in st.session_state:
    st.session_state['lang'] = "English"

selected_lang = st.sidebar.selectbox(
    "Language / Lingua", 
    ["English", "Italiano"], 
    index=0 if st.session_state['lang'] == "English" else 1
)
st.session_state['lang'] = selected_lang
t = lang_dict[st.session_state['lang']]

# --- SIDEBAR: COSTS & UTILITIES ---
st.sidebar.header(t["sidebar_mats"])
c_pe = st.sidebar.number_input("PE (€/kg)", value=1.35, step=0.05)
c_pa = st.sidebar.number_input("PA (€/kg)", value=3.60, step=0.10)
c_evoh = st.sidebar.number_input("EVOH (€/kg)", value=8.80, step=0.20)
c_tie = st.sidebar.number_input("TIE (€/kg)", value=2.90, step=0.10)

st.sidebar.markdown("---")
st.sidebar.header(t["sidebar_utils"])
c_ene = st.sidebar.number_input("Energy Cost (€/kWh)", value=0.22, step=0.01)
h_an = st.sidebar.number_input("Available Hours/Year", value=7500, step=100)
# Added a margin to calculate a realistic payback on the whole machine
margin_fixed = st.sidebar.number_input(t["margin_label"], value=0.50, step=0.05, help="Difference between sales price and total production cost")

# --- MAIN BODY ---
st.title(t["title"])
st.markdown("---")
col_top1, col_top2 = st.columns(2)
with col_top1:
    p_shared = st.number_input(t["shared_output"], value=1000, step=100)
with col_top2:
    sec_shared = st.number_input("Shared Energy Consumption (kWh/kg)", value=0.45, format="%.2f")

# --- RECIPE & OEE COMPARISON ---
st.subheader(t["recipe_title"])

# Standard Line
st.markdown(f"#### 🔄 {t['line_std']}")
rs = st.columns(6)
p_pe_a = rs[0].number_input("% PE (Std)", 0, 100, 60, key="pe_a")
p_pa_a = rs[1].number_input("% PA (Std)", 0, 100, 20, key="pa_a")
p_evoh_a = rs[2].number_input("% EVOH (Std)", 0, 100, 10, key="evoh_a")
p_tie_a = rs[3].number_input("% TIE (Std)", 0, 100, 10, key="tie_a")
oee_a = rs[4].slider(f"{t['oee_label']} Std", 50, 100, 80, key="oee_a")
total_a = p_pe_a + p_pa_a + p_evoh_a + p_tie_a
rs[5].metric("Total Std", f"{total_a}%")

# Premium Line
st.markdown(f"#### ⚡ {t['line_pre']}")
rp = st.columns(6)
p_pe_b = rp[0].number_input("% PE (Pre)", 0, 100, 65, key="pe_b")
p_pa_b = rp[1].number_input("% PA (Pre)", 0, 100, 18, key="pa_b")
p_evoh_b = rp[2].number_input("% EVOH (Pre)", 0, 100, 9, key="evoh_b")
p_tie_b = rp[3].number_input("% TIE (Pre)", 0, 100, 8, key="tie_b")
oee_b = rp[4].slider(f"{t['oee_label']} Premium", 50, 100, 88, key="oee_b")
total_b = p_pe_b + p_pa_b + p_evoh_b + p_tie_b
rp[5].metric("Total Pre", f"{total_b}%")

# --- CAPEX ---
st.markdown("---")
col_c1, col_c2 = st.columns(2)
ca = col_c1.number_input("CAPEX Standard Line (€)", value=4000000, step=100000)
cb = col_c2.number_input("CAPEX Premium Line (€)", value=4000000, step=100000)

# --- CALCULATIONS ---
def calc_economics(capex, pe, pa, evoh, tie, oee):
    ann_kg = p_shared * h_an * (oee / 100)
    u_mat_cost = (pe*c_pe + pa*c_pa + evoh*c_evoh + tie*c_tie) / 100
    ann_mat_cost = ann_kg * u_mat_cost
    ann_ene_cost = ann_kg * sec_shared * c_ene
    tot_var_cost = ann_mat_cost + ann_ene_cost
    u_cost = tot_var_cost / ann_kg if ann_kg > 0 else 0
    # Annual profit for payback calculation
    ann_profit = ann_kg * margin_fixed 
    return ann_kg, ann_mat_cost, ann_ene_cost, tot_var_cost, u_cost, ann_profit

res_a = calc_economics(ca, p_pe_a, p_pa_a, p_evoh_a, p_tie_a, oee_a)
res_b = calc_economics(cb, p_pe_b, p_pa_b, p_evoh_b, p_tie_b, oee_b)

ann_save = (res_a[4] - res_b[4]) * res_b[0]

# --- RESULTS ---
st.markdown("---")
st.header(t["res_title"])
m1, m2, m3 = st.columns(3)
m1.metric(t["saving_kg"], f"€ {(res_a[4] - res_b[4]):.3f}")
m2.metric(t["ann_save"], f"€ {ann_save:,.0f}")
# Individual payback calculation based on Margin + Operational Savings
pb_a = ca / res_a[5] if res_a[5] > 0 else 0
pb_b = cb / (res_b[5] + ann_save) if (res_b[5] + ann_save) > 0 else 0
m3.metric(t["payback"] + " (Premium)", f"{pb_b:.2f} Years")

# --- CHARTS ---
c1, c2 = st.columns(2)
with c1:
    fig_cost = go.Figure(data=[
        go.Bar(name='Material', x=['Std', 'Premium'], y=[res_a[1]/res_a[0], res_b[1]/res_b[0]], marker_color='#636EFA'),
        go.Bar(name='Energy', x=['Std', 'Premium'], y=[res_a[2]/res_a[0], res_b[2]/res_b[0]], marker_color='#EF553B')
    ])
    fig_cost.update_layout(barmode='stack', title=t["chart_cost"])
    st.plotly_chart(fig_cost, use_container_width=True)

with c2:
    # COMPARATIVE PAYBACK CHART
    yrs = [i/2 for i in range(21)] # 0 to 10 years with 6-month steps
    # Profit A = Production A * Margin
    # Profit B = Production B * Margin + (Saving per kg * Production B)
    cash_a = [-ca + (res_a[5] * y) for y in yrs]
    cash_b = [-cb + ((res_b[5] + ann_save) * y) for y in yrs]
    
    fig_pay = go.Figure()
    fig_pay.add_trace(go.Scatter(x=yrs, y=cash_a, name=t['line_std'], line=dict(color='grey', dash='dash')))
    fig_pay.add_trace(go.Scatter(x=yrs, y=cash_b, name=t['line_pre'], line=dict(color='#00CC96', width=4)))
    fig_pay.add_hline(y=0, line_dash="solid", line_color="black")
    fig_pay.update_layout(title=t["chart_roi"], xaxis_title="Years", yaxis_title="€ Cash Flow", hovermode="x unified")
    st.plotly_chart(fig_pay, use_container_width=True)

# --- DATA TABLE ---
df_res = pd.DataFrame({
    "Description": [t["table_prod"], t["table_mat"], t["table_ene"], t["table_tot"], t["cost_kg"]],
    "Standard": [f"{res_a[0]:,.0f}", f"€ {res_a[1]:,.0f}", f"€ {res_a[2]:,.0f}", f"€ {res_a[3]:,.0f}", f"€ {res_a[4]:.3f}"],
    "Premium": [f"{res_b[0]:,.0f}", f"€ {res_b[1]:,.0f}", f"€ {res_b[2]:,.0f}", f"€ {res_b[3]:,.0f}", f"€ {res_b[4]:.3f}"]
})
st.table(df_res)
