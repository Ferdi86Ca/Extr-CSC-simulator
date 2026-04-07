import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Cast Film ROI Advisor", layout="wide")

# --- DIZIONARIO TRADUZIONI ---
lang_dict = {
    "Italiano": {
        "title": "Stima ROI: Linea CAST Multistrato High-Performance",
        "sidebar_mats": "Costi Materie Prime (€/kg)",
        "sidebar_utils": "Parametri Globali & Utility",
        "recipe_title": "🧪 Configurazione Ricetta (Set-point)",
        "accuracy_label": "Accuratezza Dosaggio (Oversizing %)",
        "line_std": "Linea CAST Standard",
        "line_pre": "Linea CAST High-Perf",
        "res_title": "🏁 Analisi Economica Comparativa",
        "ann_save": "Risparmio Totale Annuo",
        "cost_kg": "Costo Unitario (€/kg)",
        "chart_cost": "Composizione Costo Variabile (€/kg Film)",
        "chart_roi": "Recupero Extra-Prezzo Linea Premium",
        "table_prod": "Produzione Annua (kg)",
        "table_mat": "Costo Materia Prima (€/anno)",
        "table_ene": "Costo Energia (€/anno)",
        "table_tot": "COSTO TOTALE VARIABILE (€/anno)",
        "payback": "Payback Extra-Investimento",
        "saving_kg": "Risparmio al kg",
        "lang_label": "Lingua"
    },
    "English": {
        "title": "ROI Estimate: High-Performance Multilayer CAST Line",
        "sidebar_mats": "Raw Material Costs (€/kg)",
        "sidebar_utils": "Global Parameters & Utilities",
        "recipe_title": "🧪 Recipe Configuration (Set-point)",
        "accuracy_label": "Dosing Accuracy (Oversizing %)",
        "line_std": "Standard CAST Line",
        "line_pre": "High-Perf CAST Line",
        "res_title": "🏁 Comparative Economic Analysis",
        "ann_save": "Total Annual Saving",
        "cost_kg": "Unit Cost (€/kg)",
        "chart_cost": "Variable Cost Breakdown (€/kg Film)",
        "chart_roi": "Premium Line Extra-Price Recovery",
        "table_prod": "Annual Production (kg)",
        "table_mat": "Raw Material Cost (€/year)",
        "table_ene": "Energy Cost (€/year)",
        "table_tot": "TOTAL VARIABLE COST (€/year)",
        "payback": "Extra-Investment Payback",
        "saving_kg": "Saving per kg",
        "lang_label": "Language"
    }
}

# --- GESTIONE LINGUA (FIX TYPEERROR) ---
if 'lang' not in st.session_state:
    st.session_state['lang'] = "Italiano"

selected_lang = st.sidebar.selectbox(
    "Language / Lingua", 
    ["Italiano", "English"], 
    index=0 if st.session_state['lang'] == "Italiano" else 1
)
st.session_state['lang'] = selected_lang
t = lang_dict[st.session_state['lang']]

# --- SIDEBAR: COSTI MATERIE PRIME ---
st.sidebar.header(t["sidebar_mats"])
c_pe = st.sidebar.number_input("PE (€/kg)", value=1.30, step=0.05)
c_pa = st.sidebar.number_input("PA (€/kg)", value=3.50, step=0.10)
c_evoh = st.sidebar.number_input("EVOH (€/kg)", value=8.50, step=0.20)
c_tie = st.sidebar.number_input("TIE (€/kg)", value=2.80, step=0.10)

st.sidebar.markdown("---")
st.sidebar.header(t["sidebar_utils"])
c_ene = st.sidebar.number_input("Energy Cost (€/kWh)", value=0.22, step=0.01)
h_an = st.sidebar.number_input("Working Hours/Year", value=7500, step=100)

# --- CORPO PRINCIPALE: RICETTA ---
st.title(t["title"])
st.subheader(t["recipe_title"])

col_r1, col_r2, col_r3, col_r4 = st.columns(4)
with col_r1:
    p_pe = st.number_input("% PE", 0, 100, 60)
with col_r2:
    p_pa = st.number_input("% PA", 0, 100, 20)
with col_r3:
    p_evoh = st.number_input("% EVOH", 0, 100, 10)
with col_r4:
    p_tie = st.number_input("% TIE", 0, 100, 10)

# Verifica somma 100%
if p_pe + p_pa + p_evoh + p_tie != 100:
    st.warning("⚠️ The sum of percentages is not 100% / La somma non è 100%")

theoretical_cost_kg = (p_pe*c_pe + p_pa*c_pa + p_evoh*c_evoh + p_tie*c_tie) / 100

# --- COMPARAZIONE LINEE ---
st.markdown("---")
col_l, col_r = st.columns(2)

with col_l:
    st.subheader(f"🔄 {t['line_std']}")
    ca = st.number_input("CAPEX Standard (€)", value=1200000, step=50000)
    seca = st.number_input("SEC Standard (kWh/kg)", value=0.55, format="%.2f")
    acca = st.slider(f"{t['accuracy_label']} Std", 0.0, 10.0, 5.0)
    out_a = st.number_input("Output Std (kg/h)", value=600, step=50)

with col_r:
    st.subheader(f"⚡ {t['line_pre']}")
    cb = st.number_input("CAPEX Premium (€)", value=1800000, step=50000)
    secb = st.number_input("SEC Premium (kWh/kg)", value=0.42, format="%.2f")
    accb = st.slider(f"{t['accuracy_label']} Premium", 0.0, 10.0, 1.5)
    out_b = st.number_input("Output Premium (kg/h)", value=650, step=50)

# --- FUNZIONE CALCOLO ---
def calc_perf(capex, sec, accuracy, output):
    ann_kg = output * h_an
    # L'accuratezza incide direttamente sul consumo di materiale per kg di prodotto finito
    real_mat_cost_kg = theoretical_cost_kg * (1 + accuracy / 100)
    ann_mat_cost = ann_kg * real_mat_cost_kg
    ann_ene_cost = ann_kg * sec * c_ene
    tot_var_cost = ann_mat_cost + ann_ene_cost
    u_cost = tot_var_cost / ann_kg
    return ann_kg, ann_mat_cost, ann_ene_cost, tot_var_cost, u_cost

res_a = calc_perf(ca, seca, acca, out_a)
res_b = calc_perf(cb, secb, accb, out_b)

# --- RISULTATI ---
st.markdown("---")
st.header(t["res_title"])

ann_save = (res_a[4] - res_b[4]) * res_b[0]
extra_capex = cb - ca
pb_extra = extra_capex / ann_save if ann_save > 0 else 0

m1, m2, m3 = st.columns(3)
m1.metric(t["saving_kg"], f"€ {(res_a[4] - res_b[4]):.3f}")
m2.metric(t["ann_save"], f"€ {ann_save:,.0f}")
m3.metric(t["payback"], f"{pb_extra:.2f} { 'Years' if st.session_state['lang'] == 'English' else 'Anni'}")

# --- GRAFICI ---
c1, c2 = st.columns(2)
with c1:
    fig_cost = go.Figure(data=[
        go.Bar(name='Material', x=['Std', 'Premium'], y=[theoretical_cost_kg*(1+acca/100), theoretical_cost_kg*(1+accb/100)], marker_color='#636EFA'),
        go.Bar(name='Energy', x=['Std', 'Premium'], y=[seca*c_ene, secb*c_ene], marker_color='#EF553B')
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

# --- TABELLA ---
df_res = pd.DataFrame({
    "Description": [t["table_prod"], t["table_mat"], t["table_ene"], t["table_tot"], t["cost_kg"]],
    "Standard": [f"{res_a[0]:,.0f}", f"€ {res_a[1]:,.0f}", f"€ {res_a[2]:,.0f}", f"€ {res_a[3]:,.0f}", f"€ {res_a[4]:.3f}"],
    "Premium": [f"{res_b[0]:,.0f}", f"€ {res_b[1]:,.0f}", f"€ {res_b[2]:,.0f}", f"€ {res_b[3]:,.0f}", f"€ {res_b[4]:.3f}"]
})
st.table(df_res)
