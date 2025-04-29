import streamlit as st
from app.pages.payments import loan_data as payments




@st.fragment()
def resumen_ahorros():
    if 'savings' not in st.session_state:
        st.session_state.savings = payments(last=True, tipo_concepto=33)

    savings = st.session_state.savings
    with st.expander(":material/savings: Resumen de Ahorros", expanded=False):
       
        if savings:
            total_actual = savings['total_actual']
            concepto_descripcion = savings['detalle'][0][1]

            st.markdown(f"**{concepto_descripcion}**")
            st.text_input(label=">Saldo actual", type="password", value=f"RD$ {format(total_actual, ',.2f')}")
            
        else:
            st.button(":blue[No tienes ahorros]", type="tertiary", icon=":material/savings:")
      