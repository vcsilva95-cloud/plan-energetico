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
