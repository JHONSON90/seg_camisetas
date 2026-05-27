import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import time
import traceback
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

def draw_metric(label, value, icon):
    st.markdown(f"""
    <div class="glass-card">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <div class="metric-label">{label}</div>
                <div class="metric-val">{value}</div>
            </div>
            <div class="metric-icon">{icon}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data(show_spinner="Cargando datos de ingresos...", ttl=300)
def cargar_datos_ingresos():
    try:
        products = conn.read(worksheet="Productos", ttl=300)
        sales_df = conn.read(worksheet="Ventas", ttl=300)
        placeholder = st.empty()
        placeholder.success("Conexión exitosa!!")
        time.sleep(1)
        placeholder.empty()
        return products, sales_df
    except Exception as e:
        st.error(f"Error al conectar con Google Sheets: {str(e)}")
        st.error(traceback.format_exc())
        return pd.DataFrame(), pd.DataFrame()


products, sales_df = cargar_datos_ingresos()

def get_debtors():
    """Dynamically parses sales to calculate active debtors list."""
    sales = sales_df
    sales["saldo"] = sales["total_amount"] - sales["amount_paid"]
    debtors = sales[sales["saldo"] > 0]
    return debtors

debtors = get_debtors()

total_sales_revenue = sum(sales_df["total_amount"]) if sales_df is not None else 0
total_cash_received = sum(sales_df["amount_paid"]) if sales_df is not None else 0
total_debt_pending = sum(debtors["saldo"])if debtors is not None else 0
columnas_suma = ["Casa", "Tienda Linares","Nicolas","Ipiales"]
products['cantidad_total'] = products[columnas_suma].sum(axis=1)
total_stock_units = sum(products['cantidad_total']) if products is not None else 0

st.markdown('<div class="app-title">Panel de Control General</div>', unsafe_allow_html=True)
st.markdown('<div class="app-subtitle">Monitoreo de ingresos, stock global y saldos deudores sincronizados</div>', unsafe_allow_html=True)

# Low stock alerts (Threshold: < 15 units in a store for a product)
# low_stock_alerts = []
# for p in products:
#     for store, qty in p["stock_by_store"].items():
#         if qty < 15:
#             low_stock_alerts.append(f"⚠️ **{p['name']}** en **{store}** tiene stock crítico: `{qty}` unidades.")
                    
# if low_stock_alerts:
#     with st.expander(f"🔔 Alertas de Stock Bajo ({len(low_stock_alerts)})", expanded=True):
#         for alert in low_stock_alerts:
#             st.markdown(f'<div class="stock-warning-banner">{alert}</div>', unsafe_allow_html=True)
                    
# Metric cards layout
m_col1, m_col2, m_col3, m_col4 = st.columns(4)
with m_col1:
    draw_metric("Ventas Totales", f"${total_sales_revenue:,.2f}", "📈")
with m_col2:
    draw_metric("Dinero Recaudado", f"${total_cash_received:,.2f}", "💵")
with m_col3:
    draw_metric("Deuda Pendiente", f"${total_debt_pending:,.2f}", "💸")
with m_col4:
    draw_metric("Stock Global", f"{total_stock_units} und", "📦")
            
st.markdown("<br>", unsafe_allow_html=True)
        
# Visualizations
col_chart1, col_chart2 = st.columns(2)
        
with col_chart1:
    st.markdown('<div class="section-header">Ingresos por Producto</div>', unsafe_allow_html=True)
    if not sales_df.empty:
        product_sales = sales_df.groupby("product_name").agg({
            "quantity": "sum",
            "total_amount": "sum"
        }).reset_index()
                
        fig_revenue = px.bar(
            product_sales,
            x="product_name",
            y="total_amount",
            labels={"product_name": "Producto", "total_amount": "Ingresos ($)"},
            color="total_amount",
            color_continuous_scale="Purples",
            template="plotly_dark"
        )
        fig_revenue.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_family="Outfit",
            coloraxis_showscale=False,
            margin=dict(t=10, b=10, l=10, r=10),
            height=350
        )
        st.plotly_chart(fig_revenue, use_container_width=True)
    else:
        st.info("No hay ventas registradas aún para graficar.")