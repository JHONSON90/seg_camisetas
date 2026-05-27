from altair.utils.schemapi import _deduplicate_additional_properties_errors
from altair.utils._vegafusion_data import vegafusion_data_transformer
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import db

# Page configuration
st.set_page_config(
    page_title="T-Shirt Track | Google Sheets Edition",
    page_icon="👕",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Premium Glassmorphic design
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');

/* Main font */
html, body, [class*="css"] {
    font-family: 'Outfit', sans-serif;
}

/* Background & general styles */
.stApp {
    background-color: #0B0F19;
    color: #E2E8F0;
}

/* Sidebar Styling */
section[data-testid="stSidebar"] {
    background-color: #0E1326 !important;
    border-right: 1px solid rgba(255, 255, 255, 0.05);
}

/* Glassmorphism Containers */
.glass-card {
    background: rgba(22, 28, 45, 0.6);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border-radius: 16px;
    border: 1px solid rgba(255, 255, 255, 0.06);
    padding: 22px;
    margin-bottom: 20px;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.glass-card:hover {
    border-color: rgba(99, 102, 241, 0.35);
    box-shadow: 0 8px 32px 0 rgba(99, 102, 241, 0.12);
    transform: translateY(-2px);
}

/* Metric styling */
.metric-label {
    font-size: 0.8rem;
    color: #94A3B8;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    font-weight: 600;
}
.metric-val {
    font-size: 2.1rem;
    font-weight: 800;
    margin-top: 5px;
    background: linear-gradient(135deg, #818CF8 0%, #C084FC 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.metric-icon {
    font-size: 1.8rem;
    color: #818CF8;
    opacity: 0.8;
}

/* Section Header */
.section-header {
    font-size: 1.6rem;
    font-weight: 700;
    color: #ffffff;
    margin-top: 10px;
    margin-bottom: 20px;
    border-left: 5px solid #818CF8;
    padding-left: 12px;
}

/* Gradient Main Title */
.app-title {
    font-size: 2.8rem;
    font-weight: 800;
    background: linear-gradient(135deg, #ffffff 40%, #818CF8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 2px;
}
.app-subtitle {
    color: #94A3B8;
    font-size: 1.05rem;
    margin-bottom: 25px;
}

/* Low Stock Banner */
.stock-warning-banner {
    background: rgba(245, 158, 11, 0.12);
    border: 1px solid rgba(245, 158, 11, 0.25);
    color: #FBBF24;
    border-radius: 12px;
    padding: 12px 18px;
    margin-bottom: 12px;
    font-weight: 500;
}

/* Custom Table View */
div[data-testid="stDataFrame"] {
    border: 1px solid rgba(255, 255, 255, 0.05) !important;
    border-radius: 12px !important;
}

/* Badge styles */
.badge-demo {
    background-color: #3b82f6;
    color: white;
    padding: 4px 10px;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
}
.badge-live {
    background-color: #10b981;
    color: white;
    padding: 4px 10px;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
}
</style>
""", unsafe_allow_html=True)

panel_general = st.Page(
    'views/panel.py',
    title="Panel General", 
    icon="📊",
)

control_stock = st.Page(
    'views/control_stock.py',
    title="Control de Stock",
    icon="👕",
)

control_deudores = st.Page(
    'views/control_deudores.py',
    title="Control de Deudores",
    icon="👥",
)

registrar_ventas = st.Page(
    'views/registrar_ventas.py',
    title="Registrar Ventas",
    icon="💸",
)

configuracion = st.Page(
    'views/configuracion.py',
    title="Configuración",
    icon="⚙️",
)

pg = st.navigation({
    "Menú Principal": [panel_general],
    "Vistas": [control_stock, control_deudores, registrar_ventas],
    "Configuración": [configuracion],
})

pg.run()


# # Helper function to display metrics
# def draw_metric(label, value, icon):
#     st.markdown(f"""
#     <div class="glass-card">
#         <div style="display: flex; justify-content: space-between; align-items: center;">
#             <div>
#                 <div class="metric-label">{label}</div>
#                 <div class="metric-val">{value}</div>
#             </div>
#             <div class="metric-icon">{icon}</div>
#         </div>
#     </div>
#     """, unsafe_allow_html=True)


# # Connection check
# has_creds = db.check_credentials_exist()

# # Initialize session state for Demo Mode if sheets not configured
# if "use_demo_mode" not in st.session_state:
#     st.session_state.use_demo_mode = False

# # Setup Wizard Render if no credentials are configured and they didn't toggle demo mode
# if not has_creds and not st.session_state.use_demo_mode:
#     st.markdown('<div class="app-title">⚙️ Conecte su Base de Datos de Google Sheets</div>', unsafe_allow_html=True)
#     st.markdown('<div class="app-subtitle">Siga la guía a continuación para enlazar su hoja de cálculo y activar la persistencia en la nube.</div>', unsafe_allow_html=True)
    
#     st.warning("⚠️ La aplicación está en modo de configuración. Rellene las credenciales de Google Sheets para poder operar con datos en tiempo real.")
    
#     # Guide columns
#     col_guide, col_action = st.columns([2, 1])
    
#     with col_guide:
#         st.markdown('<div class="glass-card">', unsafe_allow_html=True)
#         st.markdown("<h3>Guía de Configuración Paso a Paso</h3>", unsafe_allow_html=True)
        
#         tab1, tab2, tab3, tab4 = st.tabs([
#             "1. Hoja de Cálculo",
#             "2. Google Console & API",
#             "3. Compartir Acceso",
#             "4. Rellenar Secrets"
#         ])
        
#         with tab1:
#             st.markdown("""
#             #### Paso 1: Cree su Google Sheets
#             1. Vaya a [Google Sheets](https://docs.google.com/spreadsheets/) y cree una hoja de cálculo en blanco.
#             2. Copie la **URL completa** de la hoja desde la barra de direcciones de su navegador. Se verá similar a esto:
#                `https://docs.google.com/spreadsheets/d/1A2B3C4D5E.../edit`
#             """)
            
#         with tab2:
#             st.markdown("""
#             #### Paso 2: Habilite la API de Google Sheets y descargue las Credenciales
#             1. Vaya a [Google Cloud Console](https://console.cloud.google.com/) e inicie sesión.
#             2. Cree un **nuevo proyecto** (ej. `Camisetas Track`).
#             3. Busque y habilite las siguientes APIs en el buscador superior:
#                * **Google Sheets API**
#                * **Google Drive API**
#             4. Vaya a **API y Servicios > Credenciales**.
#             5. Haga clic en **+ Crear credenciales** y seleccione **Cuenta de servicio** (Service Account). Rellene los datos básicos (nombre y descripción) y haga clic en **Listo**.
#             6. Haga clic sobre la Cuenta de Servicio recién creada. Vaya a la pestaña **Claves** (Keys).
#             7. Haga clic en **Agregar clave > Crear clave nueva**, seleccione el formato **JSON** y haga clic en **Crear**. Se descargará un archivo JSON a su computadora. ¡Manténgalo seguro!
#             """)
            
#         with tab3:
# #             st.markdown("""
# #             #### Paso 3: Comparta la Hoja con la Cuenta de Servicio
# #             1. Abra el archivo JSON descargado en un editor de texto (como el Bloc de notas).
# #             2. Copie la dirección de correo electrónico que se encuentra bajo la variable `"client_email"` (se ve como: `mi-servicio@proyecto.iam.gserviceaccount.com`).
# #             3. Abra su hoja de cálculo de Google Sheets creada en el **Paso 1**.
# #             4. Haga clic en el botón **Compartir** (Share) en la esquina superior derecha.
# #             5. Pegue la dirección de correo electrónico de la cuenta de servicio y otorgue el rol de **Editor**. Desmarque "Notificar a los usuarios" y haga clic en **Compartir**.
# #             """)
            
# #         with tab4:
# #             st.markdown("""
# #             #### Paso 4: Configure el Archivo de Secretos
# #             1. Abra el archivo `.streamlit/secrets.toml` ubicado en el directorio raíz de este proyecto en su computadora.
# #             2. Reemplace la variable `spreadsheet_url` con la **URL de su Google Sheets**.
# #             3. Abra el archivo JSON de credenciales descargado de Google Cloud y copie los valores correspondientes en la sección `[gspread_credentials]` de su archivo `secrets.toml`.
# #                * *Nota: Asegúrese de que el campo `private_key` tenga el formato correcto con los saltos de línea escapados como `\\n` (tal como viene en la plantilla preestablecida).*
# #             """)
# #         st.markdown('</div>', unsafe_allow_html=True)
        
# #     with col_action:
# #         st.markdown('<div class="glass-card">', unsafe_allow_html=True)
# #         st.markdown("<h3>Acciones</h3>", unsafe_allow_html=True)
        
# #         st.write("Una vez completados los pasos anteriores y guardado el archivo `secrets.toml`, presione el botón de abajo para verificar la conexión inicial e instalar las tablas demo de camisetas automáticamente.")
        
# #         btn_verify = st.button("🔌 Verificar Conexión e Inicializar Tablas")
        
# #         if btn_verify:
# #             # Re-check in case they updated secrets file
# #             if db.check_credentials_exist():
# #                 with st.spinner("Conectando con Google Sheets y creando tablas..."):
# #                     success = db.init_google_sheets(force=False)
# #                     if success:
# #                         st.success("¡Enlazado con éxito! Las tablas Productos, Ventas y Tiendas han sido creadas en tu Google Sheet.")
# #                         st.rerun()
# #                     else:
# #                         st.error("No se pudo inicializar las tablas en Google Sheets. Revisa los logs.")
# #             else:
# #                 st.error("❌ Las credenciales en `.streamlit/secrets.toml` aún no se han configurado o contienen los placeholders iniciales.")
                
# #         st.markdown("---")
# #         st.write("Si desea previsualizar la interfaz y probar el sistema localmente con datos de prueba estáticos sin configurar las credenciales todavía, haga clic abajo:")
        
# #         btn_demo = st.button("👀 Entrar en Modo Vista Previa / Demo")
# #         if btn_demo:
# #             st.session_state.use_demo_mode = True
# #             st.rerun()
            
# #         st.markdown('</div>', unsafe_allow_html=True)
        
# # else:
#     # --- Load main app since credentials exist or user is previewing demo ---
    
#     # Fetch lists from the active DB layer
#     products = db.get_products()
#     sales = db.get_sales()
#     debtors = db.get_debtors()
#     stores = db.get_stores()
    
#     # Calculations for metrics
#     total_sales_revenue = sum(s["total_amount"] for s in sales)
#     total_cash_received = sum(s["amount_paid"] for s in sales)
#     total_debt_pending = sum(d["debt_pending"] for d in debtors)
#     total_stock_units = sum(sum(p["stock_by_store"].values()) for p in products)
    
#     # Convert sales to dataframe for plotting
#     sales_df = pd.DataFrame(sales)
    
#     # Sidebar Navigation
#     with st.sidebar:
#         st.markdown("<h2 style='color:#ffffff; font-weight:800; margin-bottom:5px;'>👕 T-Shirt Track</h2>", unsafe_allow_html=True)
        
#         # Display Database Connection Status Badge
#         if has_creds:
#             st.markdown("<span class='badge-live'>🟢 Google Sheets En Línea</span>", unsafe_allow_html=True)
#         else:
#             st.markdown("<span class='badge-demo'>🔵 Modo Demostración Local</span>", unsafe_allow_html=True)
            
#         st.markdown("<br><br>", unsafe_allow_html=True)
        
#         st.markdown("### Navegación")
#         page = st.radio(
#             "Ir a:",
#             [
#                 "📊 Panel General",
#                 "👕 Control de Stock",
#                 "💸 Registrar & Ver Ventas",
#                 "👥 Control de Deudores",
#                 "⚙️ Configuración"
#             ],
#             label_visibility="collapsed"
#         )
        
#         st.markdown("---")
#         st.markdown("### Estado de Almacenes")
#         # Small stock overview in sidebar
#         for store in stores:
#             store_stock = sum(p["stock_by_store"].get(store, 0) for p in products)
#             st.markdown(f"**{store}:** `{store_stock}` unidades")
            
#         if not has_creds:
#             st.markdown("---")
#             if st.button("🔌 Conectar Google Sheets"):
#                 st.session_state.use_demo_mode = False
#                 st.rerun()
                
#     # Page 1: Panel General (Dashboard)
#     if page == "📊 Panel General":
#         st.markdown('<div class="app-title">Panel de Control General</div>', unsafe_allow_html=True)
#         st.markdown('<div class="app-subtitle">Monitoreo de ingresos, stock global y saldos deudores sincronizados</div>', unsafe_allow_html=True)
        
#         # Low stock alerts (Threshold: < 15 units in a store for a product)
#         low_stock_alerts = []
#         for p in products:
#             for store, qty in p["stock_by_store"].items():
#                 if qty < 15:
#                     low_stock_alerts.append(f"⚠️ **{p['name']}** en **{store}** tiene stock crítico: `{qty}` unidades.")
                    
#         if low_stock_alerts:
#             with st.expander(f"🔔 Alertas de Stock Bajo ({len(low_stock_alerts)})", expanded=True):
#                 for alert in low_stock_alerts:
#                     st.markdown(f'<div class="stock-warning-banner">{alert}</div>', unsafe_allow_html=True)
                    
#         # Metric cards layout
#         m_col1, m_col2, m_col3, m_col4 = st.columns(4)
#         with m_col1:
#             draw_metric("Ventas Totales", f"${total_sales_revenue:,.2f}", "📈")
#         with m_col2:
#             draw_metric("Dinero Recaudado", f"${total_cash_received:,.2f}", "💵")
#         with m_col3:
#             draw_metric("Deuda Pendiente", f"${total_debt_pending:,.2f}", "💸")
#         with m_col4:
#             draw_metric("Stock Global", f"{total_stock_units} und", "📦")
            
#         st.markdown("<br>", unsafe_allow_html=True)
        
#         # Visualizations
#         col_chart1, col_chart2 = st.columns(2)
        
#         with col_chart1:
#             st.markdown('<div class="section-header">Ingresos por Producto</div>', unsafe_allow_html=True)
#             if not sales_df.empty:
#                 product_sales = sales_df.groupby("product_name").agg({
#                     "quantity": "sum",
#                     "total_amount": "sum"
#                 }).reset_index()
                
#                 fig_revenue = px.bar(
#                     product_sales,
#                     x="product_name",
#                     y="total_amount",
#                     labels={"product_name": "Producto", "total_amount": "Ingresos ($)"},
#                     color="total_amount",
#                     color_continuous_scale="Purples",
#                     template="plotly_dark"
#                 )
#                 fig_revenue.update_layout(
#                     plot_bgcolor="rgba(0,0,0,0)",
#                     paper_bgcolor="rgba(0,0,0,0)",
#                     font_family="Outfit",
#                     coloraxis_showscale=False,
#                     margin=dict(t=10, b=10, l=10, r=10),
#                     height=350
#                 )
#                 st.plotly_chart(fig_revenue, use_container_width=True)
#             else:
#                 st.info("No hay ventas registradas aún para graficar.")
                
#         with col_chart2:
#             st.markdown('<div class="section-header">Estado de Recaudo General</div>', unsafe_allow_html=True)
#             if total_sales_revenue > 0:
#                 fig_pie = go.Figure(data=[go.Pie(
#                     labels=["Cobrado (Efectivo)", "Pendiente (Deudas)"],
#                     values=[total_cash_received, total_debt_pending],
#                     hole=.4,
#                     marker_colors=["#10B981", "#EF4444"]
#                 )])
#                 fig_pie.update_layout(
#                     template="plotly_dark",
#                     plot_bgcolor="rgba(0,0,0,0)",
#                     paper_bgcolor="rgba(0,0,0,0)",
#                     font_family="Outfit",
#                     margin=dict(t=10, b=10, l=10, r=10),
#                     height=350
#                 )
#                 st.plotly_chart(fig_pie, use_container_width=True)
#             else:
#                 st.info("No hay datos de recaudos disponibles.")
                
#         st.markdown('<div class="section-header">Distribución de Stock por Tiendas</div>', unsafe_allow_html=True)
#         stock_data = []
#         for p in products:
#             for store, qty in p["stock_by_store"].items():
#                 stock_data.append({
#                     "Producto": p["name"],
#                     "Tienda": store,
#                     "Stock": qty
#                 })
#         stock_df = pd.DataFrame(stock_data)
        
#         fig_stock = px.bar(
#             stock_df,
#             x="Tienda",
#             y="Stock",
#             color="Producto",
#             barmode="group",
#             color_discrete_sequence=px.colors.qualitative.Bold,
#             template="plotly_dark"
#         )
#         fig_stock.update_layout(
#             plot_bgcolor="rgba(0,0,0,0)",
#             paper_bgcolor="rgba(0,0,0,0)",
#             font_family="Outfit",
#             margin=dict(t=10, b=10, l=10, r=10),
#             height=380
#         )
#         st.plotly_chart(fig_stock, use_container_width=True)
        
#     # Page 2: Control de Stock
#     elif page == "👕 Control de Stock":
#         st.markdown('<div class="app-title">Control de Stock por Tienda</div>', unsafe_allow_html=True)
#         st.markdown('<div class="app-subtitle">Monitoreo de inventario físico, transferencias entre tiendas y ajustes directos</div>', unsafe_allow_html=True)
        
#         # Global Stock Table View
#         st.markdown('<div class="section-header">Resumen de Existencias</div>', unsafe_allow_html=True)
        
#         # Create product stock matrix
#         matrix_data = []
#         for p in products:
#             row = {"Producto": p["name"], "Precio Unitario": f"${p['price']:.2f}"}
#             total_p_stock = 0
#             for store in stores:
#                 qty = p["stock_by_store"].get(store, 0)
#                 row[store] = qty
#                 total_p_stock += qty
#             row["Stock Total"] = total_p_stock
#             matrix_data.append(row)
            
#         matrix_df = pd.DataFrame(matrix_data)
#         st.dataframe(matrix_df, use_container_width=True, hide_index=True)
        
#         if not has_creds:
#             st.info("💡 Estás en modo de demostración. Las transferencias y ajustes se aplicarán localmente para esta sesión y no se guardarán en Google Sheets.")
            
#         # Two Columns for forms (Transfer and Add Stock)
#         col_t, col_a = st.columns(2)
        
#         with col_t:
#             st.markdown('<div class="glass-card">', unsafe_allow_html=True)
#             st.markdown('<h4>🔄 Transferir entre Tiendas</h4>', unsafe_allow_html=True)
            
#             with st.form("transfer_form", clear_on_submit=True):
#                 p_options = {p["id"]: p["name"] for p in products}
#                 selected_p_id = st.selectbox("Seleccione Producto:", list(p_options.keys()), format_func=lambda x: p_options[x])
                
#                 col_stores = st.columns(2)
#                 with col_stores[0]:
#                     from_store = st.selectbox("Tienda Origen:", stores, key="src_store")
#                 with col_stores[1]:
#                     to_store = st.selectbox("Tienda Destino:", stores, key="dst_store")
                    
#                 qty_transfer = st.number_input("Cantidad a Transferir:", min_value=1, value=1, step=1)
                
#                 submit_transfer = st.form_submit_button("Realizar Transferencia")
                
#                 if submit_transfer:
#                     try:
#                         if not has_creds:
#                             # Direct manipulation of local state for demo
#                             found = False
#                             for p in db.DEFAULT_PRODUCTS:
#                                 if p["id"] == selected_p_id:
#                                     if p["stock_by_store"].get(from_store, 0) < qty_transfer:
#                                         raise ValueError("Stock insuficiente en la tienda origen.")
#                                     p["stock_by_store"][from_store] -= qty_transfer
#                                     p["stock_by_store"][to_store] = p["stock_by_store"].get(to_store, 0) + qty_transfer
#                                     found = True
#                                     break
#                             st.success(f"¡[DEMO] Transferencia de {qty_transfer} '{p_options[selected_p_id]}' completada de {from_store} a {to_store}!")
#                         else:
#                             db.transfer_stock(selected_p_id, from_store, to_store, qty_transfer)
#                             st.success(f"¡Transferencia de {qty_transfer} '{p_options[selected_p_id]}' completada de {from_store} a {to_store}!")
#                         st.rerun()
#                     except Exception as e:
#                         st.error(f"Error: {str(e)}")
#             st.markdown('</div>', unsafe_allow_html=True)
            
#         with col_a:
#             st.markdown('<div class="glass-card">', unsafe_allow_html=True)
#             st.markdown('<h4>📥 Registrar Entrada/Ajuste de Stock</h4>', unsafe_allow_html=True)
            
#             with st.form("adjust_form", clear_on_submit=True):
#                 p_options = {p["id"]: p["name"] for p in products}
#                 selected_p_id_adj = st.selectbox("Seleccione Producto:", list(p_options.keys()), format_func=lambda x: p_options[x], key="adj_p")
                
#                 selected_store_adj = st.selectbox("Tienda/Ubicación:", stores, key="adj_store")
                
#                 col_adj_type = st.columns(2)
#                 with col_adj_type[0]:
#                     adj_type = st.radio("Tipo de Ajuste:", ["Entrada (Aumentar)", "Salida (Disminuir)"])
#                 with col_adj_type[1]:
#                     qty_adj = st.number_input("Cantidad:", min_value=1, value=5, step=1)
                    
#                 submit_adj = st.form_submit_button("Guardar Ajuste")
                
#                 if submit_adj:
#                     multiplier = 1 if "Entrada" in adj_type else -1
#                     final_change = qty_adj * multiplier
#                     try:
#                         if not has_creds:
#                             for p in db.DEFAULT_PRODUCTS:
#                                 if p["id"] == selected_p_id_adj:
#                                     cur = p["stock_by_store"].get(selected_store_adj, 0)
#                                     if cur + final_change < 0:
#                                         raise ValueError("El stock no puede quedar negativo.")
#                                     p["stock_by_store"][selected_store_adj] = cur + final_change
#                                     break
#                             st.success(f"¡[DEMO] Ajuste de stock de '{p_options[selected_p_id_adj]}' registrado!")
#                         else:
#                             db.adjust_stock(selected_p_id_adj, selected_store_adj, final_change)
#                             act_msg = "añadidas" if final_change > 0 else "retiradas"
#                             st.success(f"¡Se han {act_msg} {qty_adj} unidades de '{p_options[selected_p_id_adj]}' en {selected_store_adj}!")
#                         st.rerun()
#                     except Exception as e:
#                         st.error(f"Error: {str(e)}")
#             st.markdown('</div>', unsafe_allow_html=True)
            
#     # Page 3: Registrar & Ver Ventas
#     elif page == "💸 Registrar & Ver Ventas":
#         st.markdown('<div class="app-title">Registro y Control de Ventas</div>', unsafe_allow_html=True)
#         st.markdown('<div class="app-subtitle">Cree nuevos pedidos y revise el histórico completo de facturación</div>', unsafe_allow_html=True)
        
#         col_v_form, col_v_hist = st.columns([1, 2])
        
#         with col_v_form:
#             st.markdown('<div class="glass-card">', unsafe_allow_html=True)
#             st.markdown('<h4>🛍️ Registrar Nueva Venta</h4>', unsafe_allow_html=True)
            
#             with st.form("sale_form", clear_on_submit=True):
#                 client_name = st.text_input("Nombre del Cliente:", placeholder="Ej. Juan Pérez")
#                 client_contact = st.text_input("Contacto (Teléfono/Email):", placeholder="Ej. +57 300 123 4567")
                
#                 p_options = {p["id"]: f"{p['name']} (${p['price']:.2f})" for p in products}
#                 selected_p_id = st.selectbox("Producto:", list(p_options.keys()), format_func=lambda x: p_options[x], key="sale_p")
                
#                 selected_store = st.selectbox("Vendido desde:", stores, key="sale_store")
                
#                 col_qty_date = st.columns(2)
#                 with col_qty_date[0]:
#                     qty = st.number_input("Cantidad:", min_value=1, value=1, step=1)
#                 with col_qty_date[1]:
#                     sale_date = st.date_input("Fecha:", value=datetime.now().date())
                    
#                 # Dynamic calculation representation
#                 prod_selected = db.get_product_by_id(selected_p_id)
#                 total_est = prod_selected["price"] * qty if prod_selected else 0
                
#                 st.markdown(f"**Total Estimado a Pagar:** `${total_est:,.2f}`")
                
#                 amount_paid = st.number_input(
#                     "Monto Pagado en el Acto ($):",
#                     min_value=0.0,
#                     max_value=float(total_est) if total_est > 0 else 1000.0,
#                     value=float(total_est) if total_est > 0 else 0.0,
#                     step=1.0,
#                     help="Si el monto es menor al total estimado, se registrará una deuda para el cliente."
#                 )
                
#                 debt_val = total_est - amount_paid
#                 if debt_val > 0.01:
#                     st.warning(f"⚠️ Se registrará una deuda de **${debt_val:,.2f}** a nombre de {client_name if client_name else 'este cliente'}.")
                    
#                 submit_sale = st.form_submit_button("Confirmar Venta")
                
#                 if submit_sale:
#                     if not client_name.strip():
#                         st.error("Por favor, ingrese el nombre del cliente.")
#                     else:
#                         try:
#                             # Convert date to string YYYY-MM-DD
#                             sale_date_str = sale_date.strftime("%Y-%m-%d")
#                             if not has_creds:
#                                 # Mock local sale
#                                 new_mock_sale = {
#                                     "id": f"sale_{len() + 1001}",
#                                     "date": sale_date_str,
#                                     "product_id": selected_p_id,
#                                     "product_name": prod_selected["name"],
#                                     "quantity": qty,
#                                     "price": prod_selected["price"],
#                                     "total_amount": total_est,
#                                     "amount_paid": amount_paid,
#                                     "client_name": client_name.strip(),
#                                     "client_contact": client_contact.strip(),
#                                     "store": selected_store
#                                 }
#                                 # Deduct local stock
#                                 for p in db.DEFAULT_PRODUCTS:
#                                     if p["id"] == selected_p_id:
#                                         p["stock_by_store"][selected_store] -= qty
#                                         break
#                                 db.DEFAULT_SALES.append(new_mock_sale)
#                                 st.success(f"[DEMO] Venta registrada correctamente.")
#                             else:
#                                 sale_dt = datetime.combine(sale_date, datetime.min.time())
#                                 db.add_sale(
#                                     client_name=client_name.strip(),
#                                     client_contact=client_contact.strip(),
#                                     product_id=selected_p_id,
#                                     quantity=qty,
#                                     store=selected_store,
#                                     amount_paid=amount_paid,
#                                     sale_date=sale_dt
#                                 )
#                                 st.success(f"Venta registrada. Total: ${total_est:,.2f}, Pagado: ${amount_paid:,.2f}")
#                             st.rerun()
#                         except Exception as e:
#                             st.error(f"Error al registrar la venta: {str(e)}")
#             st.markdown('</div>', unsafe_allow_html=True)
            
#         with col_v_hist:
#             st.markdown('<div class="section-header">Historial de Ventas</div>', unsafe_allow_html=True)
            
#             if sales:
#                 # Filter bar
#                 col_f1, col_f2 = st.columns(2)
#                 with col_f1:
#                     filter_store = st.selectbox("Filtrar por Tienda:", ["Todas"] + stores)
#                 with col_f2:
#                     search_client = st.text_input("Buscar por Cliente:", "")
                    
#                 # Process dataframe
#                 history_data = []
#                 for s in sales:
#                     pending = s["total_amount"] - s["amount_paid"]
#                     status = "🔴 Deudor" if pending > 0.01 else "🟢 Pagado"
#                     history_data.append({
#                         "Fecha": s["date"],
#                         "Cliente": s["client_name"],
#                         "Producto": s["product_name"],
#                         "Cant.": s["quantity"],
#                         "Total ($)": s["total_amount"],
#                         "Pagado ($)": s["amount_paid"],
#                         "Deuda ($)": round(pending, 2),
#                         "Tienda": s["store"],
#                         "Estado": status
#                     })
#                 df_hist = pd.DataFrame(history_data)
                
#                 # Apply filters
#                 if filter_store != "Todas":
#                     df_hist = df_hist[df_hist["Tienda"] == filter_store]
#                 if search_client:
#                     df_hist = df_hist[df_hist["Cliente"].str.contains(search_client, case=False)]
                    
#                 st.dataframe(
#                     df_hist.sort_values(by="Fecha", ascending=False),
#                     use_container_width=True,
#                     hide_index=True
#                 )
                
#                 # Export CSV Option
#                 csv = df_hist.to_csv(index=False).encode('utf-8')
#                 st.download_button(
#                     label="📥 Exportar Historial a CSV",
#                     data=csv,
#                     file_name=f"historial_ventas_{datetime.now().strftime('%Y%m%d')}.csv",
#                     mime="text/csv"
#                 )
#             else:
#                 st.info("Aún no se han registrado transacciones.")
                
#     # Page 4: Control de Deudores
#     elif page == "👥 Control de Deudores":
#         st.markdown('<div class="app-title">Listado de Clientes Deudores</div>', unsafe_allow_html=True)
#         st.markdown('<div class="app-subtitle">Gestión de saldos pendientes y abonos de clientes</div>', unsafe_allow_html=True)
        
#         if debtors:
#             # Display Summary Info Card
#             st.markdown(f"""
#             <div class="glass-card" style="border-left: 5px solid #EF4444;">
#                 <h4 style="margin:0; color:#EF4444;">⚠️ Saldo Total en Mora</h4>
#                 <div style="font-size:2.3rem; font-weight:800; margin-top:8px;">${total_debt_pending:,.2f}</div>
#                 <p style="margin:5px 0 0 0; color:#94A3B8; font-size:0.9rem;">
#                     Hay <strong>{len(debtors)}</strong> clientes con saldos pendientes por pagar.
#                 </p>
#             </div>
#             """, unsafe_allow_html=True)
            
#             # Debtor Table view
#             debtor_table_data = []
#             for d in debtors:
#                 debtor_table_data.append({
#                     "ID Venta": d["sale_id"],
#                     "Fecha Venta": d["date"],
#                     "Cliente": d["client_name"],
#                     "Contacto": d["client_contact"],
#                     "Producto": d["product_name"],
#                     "Cant.": d["quantity"],
#                     "Valor Total ($)": d["total_amount"],
#                     "Abonado ($)": d["amount_paid"],
#                     "Deuda Pendiente ($)": d["debt_pending"],
#                     "Tienda": d["store"]
#                 })
#             df_debtors = pd.DataFrame(debtor_table_data)
#             st.dataframe(df_debtors, use_container_width=True, hide_index=True)
            
#             st.markdown("<br>", unsafe_allow_html=True)
            
#             # Form to Register Abono
#             st.markdown('<div class="glass-card">', unsafe_allow_html=True)
#             st.markdown('<h4>💳 Registrar Abono / Liquidar Deuda</h4>', unsafe_allow_html=True)
            
#             with st.form("abono_form", clear_on_submit=True):
#                 debtor_choices = {
#                     d["sale_id"]: f"{d['client_name']} ({d['product_name']}) - Debe: ${d['debt_pending']:.2f} [Tienda: {d['store']}]"
#                     for d in debtors
#                 }
                
#                 selected_sale_id = st.selectbox(
#                     "Seleccionar Deudor y Venta:",
#                     list(debtor_choices.keys()),
#                     format_func=lambda x: debtor_choices[x]
#                 )
                
#                 # Find selected debtor details to assist
#                 curr_debt = [d for d in debtors if d["sale_id"] == selected_sale_id][0]
                
#                 col_abono = st.columns(2)
#                 with col_abono[0]:
#                     abono_amount = st.number_input(
#                         "Monto del Abono ($):",
#                         min_value=0.01,
#                         max_value=float(curr_debt["debt_pending"]),
#                         value=float(curr_debt["debt_pending"]),
#                         step=1.0,
#                         help="Ingrese la cantidad que el cliente está pagando."
#                     )
#                 with col_abono[1]:
#                     st.markdown("<br>", unsafe_allow_html=True)
#                     is_full_payment = (abono_amount == float(curr_debt["debt_pending"]))
#                     if is_full_payment:
#                         st.info("💡 Esto liquidará completamente la deuda de este cliente.")
#                     else:
#                         st.info(f"💡 El saldo restante será de: ${float(curr_debt['debt_pending']) - abono_amount:.2f}")
                        
#                 submit_abono = st.form_submit_button("Aplicar Abono")
                
#                 if submit_abono:
#                     try:
#                         if not has_creds:
#                             # Mock local abono
#                             for s in db.DEFAULT_SALES:
#                                 if s["id"] == selected_sale_id:
#                                     s["amount_paid"] = round(s["amount_paid"] + abono_amount, 2)
#                                     break
#                             st.success(f"[DEMO] Abono de ${abono_amount:.2f} registrado exitosamente.")
#                         else:
#                             db.register_abono(selected_sale_id, abono_amount)
#                             st.success(f"¡Abono de ${abono_amount:.2f} registrado exitosamente a {curr_debt['client_name']}!")
#                         st.rerun()
#                     except Exception as e:
#                         st.error(f"Error al registrar abono: {str(e)}")
#             st.markdown('</div>', unsafe_allow_html=True)
#         else:
#             st.success("🎉 ¡Felicidades! No hay clientes deudores registrados. Todos los pedidos están saldados.")
            
#     # Page 5: Configuración
#     elif page == "⚙️ Configuración":
#         st.markdown('<div class="app-title">Configuración del Sistema</div>', unsafe_allow_html=True)
        
#         st.markdown('<div class="glass-card">', unsafe_allow_html=True)
#         st.markdown("<h4>Restablecer Base de Datos / Volver a Inicializar</h4>", unsafe_allow_html=True)
#         st.write("Si desea borrar todas las modificaciones hechas y restablecer el Google Sheet (o los datos locales demo) al estado original de demostración, puede hacerlo haciendo clic en el botón de abajo.")
        
#         if not has_creds:
#             st.warning("⚠️ Está operando en modo demostración. Al presionar el botón se restablecerán los datos locales temporales.")
            
#         confirm_reset = st.checkbox("Entiendo que esto borrará permanentemente los datos actuales.")
#         reset_btn = st.button("Restablecer a Datos de Fábrica", disabled=not confirm_reset)
        
#         if reset_btn:
#             try:
#                 if not has_creds:
#                     # For demo mode, we just reset the memory objects (which is already default, but we can re-assign if we had a reset routine)
#                     st.success("Modo demo restablecido.")
#                 else:
#                     db.init_google_sheets(force=True)
#                     st.success("¡Hojas de Google Sheets recreadas e inicializadas correctamente!")
#                 st.rerun()
#             except Exception as e:
#                 st.error(f"Error al restablecer: {str(e)}")
                
#         st.markdown('</div>', unsafe_allow_html=True)
        
#         st.markdown('<div class="glass-card">', unsafe_allow_html=True)
#         st.markdown("<h4>Información del Sistema</h4>", unsafe_allow_html=True)
        
#         if has_creds:
#             sheet_url_val = st.secrets["spreadsheet_url"]
#             st.markdown(f"""
#             - **Tipo de Base de Datos:** Google Sheets (En la nube)
#             - **URL de la Hoja:** [Abrir hoja en Google Drive]({sheet_url_val})
#             - **Cuenta de Servicio:** `{st.secrets["gspread_credentials"]["client_email"]}`
#             - **Productos Monitoreados:** 5
#             - **Puntos de Venta (Tiendas):** 4 ubicaciones (Principal, Norte, Sur, Almacén)
#             """)
#         else:
#             st.markdown("""
#             - **Tipo de Base de Datos:** Simulación de datos locales (Modo Vista Previa)
#             - **Estado de Conexión:** Sin credenciales activas.
#             - **Productos Monitoreados:** 5
#             - **Puntos de Venta (Tiendas):** 4 ubicaciones (Principal, Norte, Sur, Almacén)
#             """)
#         st.markdown('</div>', unsafe_allow_html=True)
