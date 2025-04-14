import streamlit as st
from app.pages.payments import loan_data as payments
@st.fragment
def resumen_ahorros():
    if 'savings' not in st.session_state:
        st.session_state.savings = payments(last=True, tipo_concepto=33)

    savings = st.session_state.savings
    with st.expander("Resumen de Ahorros", expanded=True if savings else False):
       
        if savings:
            total_actual = savings['total_actual']
            concepto_descripcion = savings['detalle'][0][1]

            # Mostrar el balance enmascarado o visible según el estado
            total_actual_text = "****" if st.session_state.mask_balances else f"RD$ {format(total_actual, ',.2f')}"

            # CSS personalizado para estilizar el texto
            st.markdown("""
                <style>
                    .prestamo-text {
                        font-size: 16px;
                        font-weight: bold;
                        color: #333;
                        margin-top: 0px;
                        margin-bottom: 0px;
                    }
                    .caption-text {
                        font-size: 14px;
                        color: #666;
                        margin-top: -8px;
                        margin-bottom: 0px;
                    }
                    .amount-text {  
                        font-size: 30px;
                        font-weight: bold;
                        color: #007BFF;
                        margin-top: 0px;
                    }
                </style>
            """, unsafe_allow_html=True)

            st.markdown(f'<p class="prestamo-text">{concepto_descripcion}</p>', unsafe_allow_html=True)
            st.markdown('<p class="caption-text">Saldo actual</p>', unsafe_allow_html=True)
            st.markdown(f'<p class="amount-text">{total_actual_text}</p>', unsafe_allow_html=True)
        else:
            _, colp, _ = st.columns([2, 3, 1])
            colp.button(":blue[No tienes ahorros]", type="tertiary", icon=":material/savings:")
      