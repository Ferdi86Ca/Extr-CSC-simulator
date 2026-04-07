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
        "chart_roi": "Premium Line Extra-Price Recovery",
        "table_prod": "Actual Annual Production (kg)",
        "table_mat": "Raw Material Cost (€/year)",
        "table_ene": "Energy Cost (€/year)",
        "table_tot": "TOTAL VARIABLE COST (€/year)",
        "payback": "Extra-Investment Payback",
        "saving_kg": "Saving per kg",
        "shared_output": "Nominal Hourly Output (kg/h)",
        "oee_label": "OEE (Efficiency %)"
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
        "chart_roi": "Recupero Extra-Prezzo Linea Premium",
        "table_prod": "Produzione Annua Reale (kg)",
        "table_mat": "Costo Materia Prima (€/anno)",
        "table_ene": "Costo Energia (€/anno)",
        "table_tot": "COSTO TOTALE VARIABILE (€/anno)",
        "payback": "Payback Extra-Investimento",
        "saving_kg": "Risparmio al kg",
        "shared_output": "Portata Oraria Nominale (kg/h)",
        "oee_label": "OEE (Efficienza %)"
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

# --- SIDEBAR: RAW MATERIAL COSTS ---
st.sidebar.header(t["sidebar_mats"])
c_pe = st.sidebar.number_input("PE (€/kg)", value=1.35, step=0.05)
c_pa = st.sidebar.number_input("PA (€/kg)", value=3.60, step=0.10)
c_evoh = st.sidebar.number_input("EVOH (€/kg)", value=8.80, step=0.20)
c_tie = st.sidebar.number_input("TIE (€/kg)", value=2.90, step=0.10)

st.sidebar.markdown("---")
st.sidebar.header(t["sidebar_utils"])
c_ene = st.sidebar.number_input("Energy Cost (€/kWh)", value=0.22, step=0.01)
h_an = st.sidebar.number_input("Available Production Hours/Year", value=7500, step=100)

# --- MAIN BODY: SHARED PARAMETERS ---
st.title(t["title"])
st.markdown("---")
col_top1, col_top2 = st.columns(2)
with col_top1:
    p_shared = st.number_input(t["shared_output"], value=1000, step=100)
with col_top2:
    sec_shared = st.number_input("Shared Energy Consumption (kWh/kg)", value=0.45, format="%.2f")

# --- RECIPE COMPARISON ROWS ---
st.subheader(t["recipe_title"])

# Standard Line Recipe & OEE
st.markdown(f"#### 🔄 {t['line_std']}")
rs1, rs2, rs3, rs4, rs5, rs6 = st.columns(6)
with rs1: p_pe_a = st.number_input("% PE (Std)", 0, 100, 60, key="pe_a")
with rs2: p_pa_a = st.number_input("% PA (Std)", 0, 100, 20, key="pa_a")
with rs3: p_evoh_a = st.number_input("% EVOH (Std)", 0, 100, 10, key="evoh_a")
with rs4: p_tie_a = st.number_input("% TIE (Std)", 0, 100, 10, key="tie_a")
with rs5: oee_a = st.slider(f"{t['oee_label']} Std", 50, 100, 80, key="oee_a")
with rs6: 
    total_a = p_pe_a + p_pa_a + p_evoh_a + p_tie_a
    st.metric("Total Std", f"{total_a}%")

# Premium Line Recipe & OEE
st.markdown(f"#### ⚡ {t['line_pre']}")
rp1, rp2, rp3, rp4, rp5, rp6 = st.columns(6)
with rp1: p_pe_b = st.number_input("% PE (Pre)", 0, 100, 65, key="pe_b")
with rp2: p_pa_b = st.number_input("% PA (Pre)", 0, 100, 18, key="pa_b")
with rp3: p_evoh_b = st.number_input("% EVOH (Pre)", 0, 100, 9, key="evoh_b")
with rp4: p_tie_b = st.number_input("% TIE (Pre)", 0, 100, 8, key="tie_b")
with rp5: oee_b = st.slider(f"{t['oee_label']} Premium", 50, 100, 88, key="oee_b")
with rp6: 
    total_b = p_pe_b + p_pa_b + p_evoh_b + p_tie_b
    st.metric("Total Pre", f"{total_b}%")

if total_a != 100 or total_b != 100:
    st.warning("⚠️ Warning: One of the recipes does not sum to 100%!")

# --- CAPEX INPUTS ---
st.markdown("---")
col_c1, col_c2 = st.columns(2)
with col_c1:
    ca = st.number_input("CAPEX Standard Line (€)", value=4000000, step=100000)
with col_c2:
    cb = st.number_input("CAPEX Premium Line (€)", value=4000000, step=100000)

# --- CALCULATIONS ---
def calc_economics(capex, pe, pa, evoh, tie, oee):
    # OEE reduces the total actual kg produced per year
    actual_ann_kg = p_shared * h_an * (oee / 100)
    
    # Unit material cost based on specific recipe
    u_mat_cost = (pe*c_pe + pa*c_pa + evoh*c_evoh + tie*c_tie) / 100
    ann_mat_cost = actual_ann_kg * u_mat_cost
    
    # Energy is consumed on actual production
    ann_ene_cost = actual_ann_kg * sec_shared * c_ene
    
    tot_var_cost = ann_mat_cost + ann_ene_cost
    u_cost = tot_var_cost / actual_ann_kg if actual_ann_kg > 0 else 0
    
    return actual_ann_kg, ann_mat_cost, ann_ene_cost, tot_var_cost, u_cost

res_a = calc_economics(ca, p_pe_a, p_pa_a, p_evoh_a, p_tie_a, oee_a)
res_b = calc_economics(cb, p_pe_b, p_pa_b, p_evoh_b, p_tie_b, oee_b)

# --- RESULTS ---
st.markdown("---")
st.header(t["res_title"])

# Saving calculation: Comparing the cost of the Premium production vs what it would have costed on the Std line
ann_save = (res_a[4] - res_b[4]) * res_b[0]
extra_capex = cb - ca
# If CAPEX is same, payback is instant or non-applicable as it's a pure saving from day 1
pb_extra = extra_capex / ann_save if (ann_save > 0 and extra_capex > 0) else 0

m1, m2, m3 = st.columns(3)
m1.metric(t["saving_kg"], f"€ {(res_a[4] - res_b[4]):.3f}")
m2.metric(t["ann_save"], f"€ {ann_save:,.0f}")
if extra_capex > 0:
    m3.metric(t["payback"], f"{pb_extra:.2f} { 'Years' if st.session_state['lang'] == 'English' else 'Anni'}")
else:
    m3.metric(t["payback"], "0.00 (Same CAPEX)")

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
    yrs = list(range(11))
    cum_saving = [-extra_capex + (ann_save * y) for y in yrs]
    fig_roi = go.Figure()
    fig_roi.add_trace(go.Scatter(x=yrs, y=cum_saving, fill='tozeroy', line=dict(color='#00CC96', width=4)))
    fig_roi.add_hline(y=0, line_dash="dash", line_color="black")
    fig_roi.update_layout(title=t["chart_roi"], xaxis_title="Years", yaxis_title="€")
    st.plotly_chart(fig_roi, use_container_width=True)

# --- DATA TABLE ---
df_res = pd.DataFrame({
    "Description": [t["table_prod"], t["table_mat"], t["table_ene"], t["table_tot"], t["cost_kg"]],
    "Standard": [f"{res_a[0]:,.0f}", f"€ {res_a[1]:,.0f}", f"€ {res_a[2]:,.0f}", f"€ {res_a[3]:,.0f}", f"€ {res_a[4]:.3f}"],
    "Premium": [f"{res_b[0]:,.0f}", f"€ {res_b[1]:,.0f}", f"€ {res_b[2]:,.0f}", f"€ {res_b[3]:,.0f}", f"€ {res_b[4]:.3f}"]
})
st.table(df_res)
