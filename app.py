import streamlit as st
import plotly.graph_objects as go
import copy

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
# ALTERAÇÃO DA CARGA PELO SLIDER
# --------------------------------------------------

# Faz uma cópia do sistema original
sistema_simulacao = copy.deepcopy(sistema)

# Calcula a carga correspondente ao percentual escolhido
carga_modificada = [
    carga * fator_carga / 100
    for carga in sistema["DGer"]["Carga"]
]

# Coloca a carga modificada no sistema que será otimizado
sistema_simulacao["DGer"]["Carga"] = carga_modificada


# --------------------------------------------------
# EXECUÇÃO DO MODELO
# --------------------------------------------------

resultado = pl_unico(sistema_simulacao,cenario,False)


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

# Déficit
deficit = resultado["Deficit"]

# --------------------------------------------------
# CUSTOS POR ESTÁGIO
# --------------------------------------------------

cvu_termobahia = 424080
cvu_pecem = 1764000
custo_deficit = 5969520

custo_termobahia = [
    gt_termobahia[i] * cvu_termobahia
    for i in range(12)
]

custo_pecem = [
    gt_pecem[i] * cvu_pecem
    for i in range(12)
]

custo_deficit_estagio = [
    deficit[i] * custo_deficit
    for i in range(12)
]

custo_estagio = [
    custo_termobahia[i]
    + custo_pecem[i]
    + custo_deficit_estagio[i]
    for i in range(12)
]

custo_total_operacao = sum(custo_estagio)

st.divider()

st.subheader("💰 Custo de Operação por Estágio")

fig_custo = go.Figure()

# Termobahia
fig_custo.add_trace(
    go.Bar(
        x=estagios,
        y=custo_termobahia,
        name="UTE Termobahia",
        marker_color="#FF9800"
    )
)

# Pecém II
fig_custo.add_trace(
    go.Bar(
        x=estagios,
        y=custo_pecem,
        name="UTE Pecém II",
        marker_color="#E53935"
    )
)

# Déficit
fig_custo.add_trace(
    go.Bar(
        x=estagios,
        y=custo_deficit_estagio,
        name="Déficit",
        marker_color="#9E9E9E"
    )
)

fig_custo.update_layout(
    xaxis_title="Estágio",
    yaxis_title="Custo (R$)",
    barmode="stack",
    legend_title="Componente do custo",
    hovermode="x unified"
)

fig_custo.update_xaxes(
    tickmode="linear",
    dtick=1
)

st.plotly_chart(
    fig_custo,
    use_container_width=True
)

custo_formatado = (
    f"{custo_total_operacao:,.2f}"
    .replace(",", "X")
    .replace(".", ",")
    .replace("X", ".")
)

st.metric(
    label="💰 Custo total de operação",
    value=f"R$ {custo_formatado}"
)

# --------------------------------------------------
# VERIFICAÇÃO DO BALANÇO DE DEMANDA
# --------------------------------------------------

carga_modelo = sistema_simulacao["DGer"]["Carga"]

geracao_total = []

for i in range(12):

    total = (
        gh_chavantes[i]
        + gh_piraju[i]
        + gt_termobahia[i]
        + gt_pecem[i]
        + deficit[i])

    geracao_total.append(total)

fig_despacho = go.Figure()


# UHE Chavantes
fig_despacho.add_trace(
    go.Bar(
        x=estagios,
        y=gh_chavantes,
        name="UHE Chavantes",
        marker_color="#1565C0"))


# UHE Piraju
fig_despacho.add_trace(
    go.Bar(
        x=estagios,
        y=gh_piraju,
        name="UHE Piraju",
        marker_color="#42A5F5"))


# UTE Termobahia
fig_despacho.add_trace(
    go.Bar(
        x=estagios,
        y=gt_termobahia,
        name="UTE Termobahia",
        marker_color="#FF9800"))


# UTE Pecém II
fig_despacho.add_trace(
    go.Bar(
        x=estagios,
        y=gt_pecem,
        name="UTE Pecém II",
        marker_color="#E53935"))

# Déficit
fig_despacho.add_trace(
    go.Bar(
        x=estagios,
        y=deficit,
        name="Déficit",
        marker_color="#9E9E9E"))

# Linha da carga
fig_despacho.add_trace(
    go.Scatter(
        x=estagios,
        y=carga_modelo,
        mode="lines+markers",
        name="Carga",
        line=dict(
            color="black",
            width=3,
            dash="dash"
        ),
        marker=dict(
            size=7,
            color="black"
        )
    )
)

# --------------------------------------------------
# TESTE DO BALANÇO
# --------------------------------------------------

tolerancia = 0.01

erro_maximo = max(
    abs(geracao_total[i] - carga_modelo[i])
    for i in range(12)
)

if erro_maximo <= tolerancia:

    st.success(
        "✅ Balanço de demanda conferido: "
        "geração + déficit = carga em todos os estágios."
    )

else:

    st.error(
        f"⚠️ Erro no balanço de demanda. "
        f"Maior diferença encontrada: "
        f"{erro_maximo:.2f} MWmed."
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
