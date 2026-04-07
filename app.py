import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Cast Film Multilayer Comparator", layout="wide")

# --- TRADUZIONI E STILI ---
t = {
    "title": "Stima ROI: Linea CAST Multistrato High-Performance",
    "sidebar": "Parametri Globali & Costi Materie",
    "recipe_title": "Configurazione Ricetta (Set-point)",
    "accuracy_label": "Accuratezza Dosaggio (Oversizing %)",
    "result_title": "Analisi Economica Comparativa",
    "annual_save": "Risparmio Totale Annuo",
}

# --- SIDEBAR: COSTI MATERIE PRIME ---
st.sidebar.header(f"💰 {t['sidebar']}")
c_pe = st.sidebar.number_input("Costo PE (€/kg)", value=1.30, step=0.05)
c_pa = st.sidebar.number_input("Costo PA (€/kg)", value=3.50, step=0.10)
c_evoh = st.sidebar.number_input("Costo EVOH (€/kg)", value=8.50, step=0.20)
c_tie = st.sidebar.number_input("Costo TIE (Adesivo) (€/kg)", value=2.80, step=0.10)

st.sidebar.markdown("---")
c_ene = st.sidebar.number_input("Costo Energia (€/kWh)", value=0.22)
h_an = st.sidebar.number_input("Ore Produzione Annue", value=7500)

# --- CORPO PRINCIPALE: DEFINIZIONE RICETTA ---
st.title(t["title"])
st.markdown("---")

st.subheader(f"🧪 {t['recipe_title']}")
col_r1, col_r2, col_r3, col_r4 = st.columns(4)
with col_r1:
    p_pe = st.number_input("% PE", 0, 100, 60)
with col_r2:
    p_pa = st.number_input("% PA", 0, 100, 20)
with col_r3:
    p_evoh = st.number_input("% EVOH", 0, 100, 10)
with col_r4:
    p_tie = st.number_input("% TIE", 0, 100, 10)

# Validazione Ricetta
total_p = p_pe + p_pa + p_evoh + p_tie
if total_p != 100:
    st.error(f"Attenzione: La somma delle percentuali è {total_p}%. Deve essere 100%.")

# Calcolo Costo Teorico Ricetta (€/kg)
theoretical_cost_kg = (p_pe*c_pe + p_pa*c_pa + p_evoh*c_evoh + p_tie*c_tie) / 100

# --- COMPARAZIONE LINEE ---
st.markdown("---")
col_l, col_r = st.columns(2)

with col_l:
    st.subheader("🔄 Linea CAST Standard")
    ca = st.number_input("CAPEX Linea Standard (€)", value=1200000)
    seca = st.number_input("SEC Standard (kWh/kg)", value=0.55)
    acca = st.slider("Oversizing Standard (%)", 2.0, 8.0, 5.0, help="Quanto materiale in più viene dosato per sicurezza a causa dell'instabilità")
    output_a = st.number_input("Output Reale Standard (kg/h)", value=600)

with col_r:
    st.subheader("⚡ Linea CAST High-Perf")
    cb = st.number_input("CAPEX Linea Premium (€)", value=1800000)
    secb = st.number_input("SEC Premium (kWh/kg)", value=0.42)
    accb = st.slider("Oversizing Premium (%)", 0.5, 4.0, 1.5, help="Maggiore precisione = minore spreco di materiali costosi")
    output_b = st.number_input("Output Reale Premium (kg/h)", value=650)

# --- CALCOLI FINANZIARI ---
def calculate_line_performance(capex, sec, accuracy, hourly_output):
    ann_prod_kg = hourly_output * h_an
    # Costo materiale influenzato dall'accuratezza (più errore = più consumo)
    real_material_cost_kg = theoretical_cost_kg * (1 + accuracy / 100)
    ann_material_cost = ann_prod_kg * real_material_cost_kg
    
    ann_energy_cost = ann_prod_kg * sec * c_ene
    
    total_variable_cost = ann_material_cost + ann_energy_cost
    cost_per_kg_produced = total_variable_cost / ann_prod_kg
    
    return ann_prod_kg, ann_material_cost, ann_energy_cost, total_variable_cost, cost_per_kg_produced

res_a = calculate_line_performance(ca, seca, acca, output_a)
res_b = calculate_line_performance(cb, secb, accb, output_b)

# --- DISPLAY RISULTATI ---
st.markdown("---")
st.header(t["result_title"])

m1, m2, m3 = st.columns(3)
annual_saving = (res_a[4] - res_b[4]) * res_b[0] # Risparmio basato sulla produzione della linea B
extra_capex = cb - ca
payback_extra = extra_capex / annual_saving if annual_saving > 0 else 0

m1.metric("Risparmio al kg", f"€ {(res_a[4] - res_b[4]):.3f}")
m2.metric(t["annual_save"], f"€ {annual_saving:,.0f}")
m3.metric("Payback Extra-Investimento", f"{payback_extra:.2f} Anni")

# --- GRAFICI ---
c1, c2 = st.columns(2)

with c1:
    # Breakdown del costo al kg
    fig_cost = go.Figure(data=[
        go.Bar(name='Materiale', x=['Standard', 'Premium'], y=[theoretical_cost_kg*(1+acca/100), theoretical_cost_kg*(1+accb/100)]),
        go.Bar(name='Energia', x=['Standard', 'Premium'], y=[seca*c_ene, secb*c_ene])
    ])
    fig_cost.update_layout(barmode='stack', title="Composizione Costo Variabile (€/kg Film)")
    st.plotly_chart(fig_cost, use_container_width=True)

with c2:
    # Analisi del risparmio cumulativo
    yrs = list(range(8))
    cum_saving = [-extra_capex + (annual_saving * y) for y in yrs]
    fig_savings = go.Figure()
    fig_savings.add_trace(go.Scatter(x=yrs, y=cum_savings, fill='tozeroy', name="Net Saving", line=dict(color='green')))
    fig_savings.add_hline(y=0, line_dash="dash", line_color="red")
    fig_savings.update_layout(title="Recupero Extra-Prezzo Linea Premium", xaxis_title="Anni", yaxis_title="€")
    st.plotly_chart(fig_savings, use_container_width=True)

# --- TABELLA DETTAGLIATA ---
st.subheader("Dettaglio Costi Annuali")
data = {
    "Descrizione": ["Produzione Annua (kg)", "Costo Materia Prima (€/anno)", "Costo Energia (€/anno)", "COSTO TOTALE VARIABILE (€/anno)", "COSTO UNITARIO (€/kg)"],
    "Linea Standard": [f"{res_a[0]:,.0f}", f"€ {res_a[1]:,.0f}", f"€ {res_a[2]:,.0f}", f"€ {res_a[3]:,.0f}", f"€ {res_a[4]:.3f}"],
    "Linea Premium": [f"{res_b[0]:,.0f}", f"€ {res_b[1]:,.0f}", f"€ {res_b[2]:,.0f}", f"€ {res_b[3]:,.0f}", f"€ {res_b[4]:.3f}"]
}
st.table(pd.DataFrame(data))
