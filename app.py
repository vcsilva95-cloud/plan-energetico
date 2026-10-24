import streamlit as st
import plotly.graph_objects as go

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
# BARRA LATERAL
# --------------------------------------------------

st.sidebar.header("⚙️ Parâmetros da simulação")

fator_carga = st.sidebar.slider(
    "Carga do sistema (%)",
    min_value=50,
    max_value=150,
    value=100,
    step=5
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
