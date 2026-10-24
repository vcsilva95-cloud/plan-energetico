import streamlit as st
import plotly.graph_objects as go

from modelo import sistema, pl_unico

# --------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA
# --------------------------------------------------

st.set_page_config(
    page_title="Despacho Hidrotérmico",
    page_icon="⚡",
    layout="wide"
)

st.title("⚡ Despacho Hidrotérmico")
st.write("Planejamento Energético - PL Único")


# --------------------------------------------------
# DADOS DO PROBLEMA
# --------------------------------------------------

with st.expander("📋 Dados do problema", expanded=False):

    st.subheader("⚡ Sistema")

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            label="Carga",
            value="700 MW"
        )

    with col2:
        st.metric(
            label="Custo do déficit",
            value="R$ 5.969.520 / MWmês"
        )

    st.divider()

    # --------------------------------------------------
    # USINAS HIDRELÉTRICAS
    # --------------------------------------------------

    st.subheader("💧 Usinas Hidrelétricas")

    col1, col2 = st.columns(2)

    with col1:

        st.markdown("### UHE Chavantes")

        st.write("**Potência nominal:** 414 MW")
        st.write("**Produtibilidade (ρ):** 0,235 MWmed/hm³")
        st.write("**Volume máximo:** 8.795 hm³")
        st.write("**Volume mínimo:** 5.754 hm³")
        st.write("**Volume útil:** 3.041 hm³")

    with col2:

        st.markdown("### UHE Piraju")

        st.write("**Potência nominal:** 480 MW")
        st.write("**Produtibilidade (ρ):** 0,089 MWmed/hm³")
        st.write("**Volume máximo:** 84 hm³")
        st.write("**Volume mínimo:** 84 hm³")
        st.write("**Volume útil:** 0 hm³")

    st.divider()

    # --------------------------------------------------
    # USINAS TERMELÉTRICAS
    # --------------------------------------------------

    st.subheader("🔥 Usinas Termelétricas")

    col1, col2 = st.columns(2)

    with col1:

        st.markdown("### GT1 - UTE Termobahia")
        st.caption("Combustível: Gás")

        st.write("**Potência nominal:** 186 MW")
        st.write("**CVU:** R$ 424.080 / MWmês")

    with col2:

        st.markdown("### GT2 - UTE Pecém II")
        st.caption("Combustível: Diesel")

        st.write("**Potência nominal:** 144 MW")
        st.write("**CVU:** R$ 1.764.000 / MWmês")

# --------------------------------------------------
# PARAMETROS DA SIMULAÇÃO (CARGA E CENARIO)
# --------------------------------------------------

st.sidebar.header("⚙️ Parâmetros da simulação")

cenario_nome = st.sidebar.radio(
    "Cenário hidrológico",
    options=["Otimista", "Pessimista"],
    index=0
)

if cenario_nome == "Otimista":
    cenario = 0
else:
    cenario = 1


fator_carga = st.sidebar.slider(
    "Carga do sistema (%)",
    min_value=50,
    max_value=150,
    value=100,
    step=5
)

# --------------------------------------------------
# EXECUÇÃO DO MODELO
# --------------------------------------------------

resultado = pl_unico(
    sistema,
    cenario,
    False
)

# --------------------------------------------------
# RESULTADOS - DESPACHO DE GERAÇÃO
# --------------------------------------------------

st.divider()

st.header("📊 Resultados do Modelo")

estagios = list(range(1, 13))

# Geração hidráulica
gh_chavantes = resultado["UHE"][0]["gh"]
gh_piraju = resultado["UHE"][1]["gh"]

# Geração térmica
gt_termobahia = resultado["UTE"][0]["gt"]
gt_pecem = resultado["UTE"][1]["gt"]


fig_despacho = go.Figure()


# UHE Chavantes
fig_despacho.add_trace(
    go.Bar(
        x=estagios,
        y=gh_chavantes,
        name="UHE Chavantes",
        marker_color="#1565C0"
    )
)


# UHE Piraju
fig_despacho.add_trace(
    go.Bar(
        x=estagios,
        y=gh_piraju,
        name="UHE Piraju",
        marker_color="#42A5F5"
    )
)


# UTE Termobahia
fig_despacho.add_trace(
    go.Bar(
        x=estagios,
        y=gt_termobahia,
        name="UTE Termobahia",
        marker_color="#FF9800"
    )
)


# UTE Pecém II
fig_despacho.add_trace(
    go.Bar(
        x=estagios,
        y=gt_pecem,
        name="UTE Pecém II",
        marker_color="#E53935"
    )
)


fig_despacho.update_layout(

    title="Despacho de Geração por Estágio",

    xaxis_title="Estágio",

    yaxis_title="Geração (MWmed)",

    barmode="stack",

    legend_title="Fonte de geração",

    hovermode="x unified"
)


fig_despacho.update_xaxes(
    tickmode="linear",
    dtick=1
)


st.plotly_chart(
    fig_despacho,
    use_container_width=True
)

# --------------------------------------------------
# INFORMAÇÃO NA TELA
# --------------------------------------------------

st.subheader("Cenário de carga")

st.write(
    f"A carga utilizada na otimização será "
    f"{fator_carga}% da carga original."
)

if fator_carga == 100:
    st.success("Carga original do sistema")

elif fator_carga > 100:
    st.warning(
        f"Carga aumentada em {fator_carga - 100}%"
    )

else:
    st.info(
        f"Carga reduzida em {100 - fator_carga}%"
    )

st.info(
    f"🌧️ Cenário hidrológico selecionado: **{cenario_nome}**"
)
