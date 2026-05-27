# import streamlit as st
# import pandas as pd
# from streamlit_gsheets import GSheetsConnection
# import time
# import traceback
# import plotly.express as px
# import plotly.graph_objects as go
# from datetime import datetime

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

# conn = st.connection("gsheets", type=GSheetsConnection)

# @st.cache_data(show_spinner="Cargando datos de ingresos...", ttl=300)
# def cargar_datos_ingresos():
#     try:
#         products = conn.read(worksheet="Productos", ttl=300)
#         sales_df = conn.read(worksheet="Ventas", ttl=300)
#         stores = conn.read(worksheet="Tiendas", ttl=300)
#         placeholder = st.empty()
#         placeholder.success("Conexión exitosa!!")
#         time.sleep(1)
#         placeholder.empty()
#         return products, sales_df, stores
#     except Exception as e:
#         st.error(f"Error al conectar con Google Sheets: {str(e)}")
#         st.error(traceback.format_exc())
#         return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

# products, sales_df, stores = cargar_datos_ingresos()


# st.markdown('<div class="app-title">Control de Stock por Tienda</div>', unsafe_allow_html=True)
# st.markdown('<div class="app-subtitle">Monitoreo de inventario físico, transferencias entre tiendas y ajustes directos</div>', unsafe_allow_html=True)
        
# # Global Stock Table View
# st.markdown('<div class="section-header">Resumen de Existencias</div>', unsafe_allow_html=True)
        
# # Create product stock matrix
# matrix_data = []
# for p in products:
#     row = {"Producto": p["name"], "Precio Unitario": f"${p['price']:.2f}"}
#     total_p_stock = 0
#     for store in stores:
#         qty = p["stock_by_store"].get(store, 0)
#         row[store] = qty
#         total_p_stock += qty
#     row["Stock Total"] = total_p_stock
#     matrix_data.append(row)
            
# matrix_df = pd.DataFrame(matrix_data)
# st.dataframe(matrix_df, use_container_width=True, hide_index=True)
        
# # Two Columns for forms (Transfer and Add Stock)
# col_t, col_a = st.columns(2)
        
# with col_t:
#     st.markdown('<div class="glass-card">', unsafe_allow_html=True)
#     st.markdown('<h4>🔄 Transferir entre Tiendas</h4>', unsafe_allow_html=True)
            
#     with st.form("transfer_form", clear_on_submit=True):
#         p_options = {p["id"]: p["name"] for p in products}
#         selected_p_id = st.selectbox("Seleccione Producto:", list(p_options.keys()), format_func=lambda x: p_options[x])
                
#         col_stores = st.columns(2)
#         with col_stores[0]:
#             from_store = st.selectbox("Tienda Origen:", stores, key="src_store")
#         with col_stores[1]:
#             to_store = st.selectbox("Tienda Destino:", stores, key="dst_store")
                    
#         qty_transfer = st.number_input("Cantidad a Transferir:", min_value=1, value=1, step=1)
                
#         submit_transfer = st.form_submit_button("Realizar Transferencia")
                        
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
                
                
#             st.markdown('</div>', unsafe_allow_html=True)

import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import time
import traceback

# ─── Configuración ────────────────────────────────────────────────────────────
STORES = ["Casa", "Tienda Linares", "Nicolas", "Ipiales"]

conn = st.connection("gsheets", type=GSheetsConnection)


# ─── Lectura de datos ─────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Cargando inventario...", ttl=60)
def cargar_productos() -> pd.DataFrame:
    """Lee la hoja Productos y normaliza tipos."""
    try:
        df = conn.read(worksheet="Productos", ttl=60)
        for store in STORES:
            if store in df.columns:
                df[store] = pd.to_numeric(df[store], errors="coerce").fillna(0).astype(int)
        df["price"] = pd.to_numeric(df["price"], errors="coerce").fillna(0.0)
        return df
    except Exception as e:
        st.error(f"Error al leer Productos: {e}")
        st.error(traceback.format_exc())
        return pd.DataFrame()


# ─── Escritura en Google Sheets ───────────────────────────────────────────────
def guardar_productos(df: pd.DataFrame) -> bool:
    """Sobreescribe la hoja Productos con el DataFrame actualizado."""
    try:
        conn.update(worksheet="Productos", data=df)
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"Error al guardar en Google Sheets: {e}")
        st.error(traceback.format_exc())
        return False


def transferir_stock(df: pd.DataFrame, product_id: str, origen: str, destino: str, cantidad: int):
    """
    Resta `cantidad` del stock en `origen` y lo suma en `destino`.
    Valida stock suficiente y tiendas distintas.
    Retorna (df_actualizado, error_msg). Si error_msg es None, la operación fue exitosa.
    """
    if origen == destino:
        return df, "La tienda de origen y destino deben ser diferentes."

    mask = df["id"].astype(str) == str(product_id)
    if not mask.any():
        return df, f"Producto con ID '{product_id}' no encontrado."

    idx = df[mask].index[0]
    stock_origen = int(df.at[idx, origen])

    if cantidad <= 0:
        return df, "La cantidad debe ser mayor a cero."
    if stock_origen < cantidad:
        return df, f"Stock insuficiente en '{origen}'. Disponible: {stock_origen}, solicitado: {cantidad}."

    df = df.copy()
    df.at[idx, origen]  = stock_origen - cantidad
    df.at[idx, destino] = int(df.at[idx, destino]) + cantidad
    return df, None


def ajustar_stock(df: pd.DataFrame, product_id: str, tienda: str, cantidad: int, es_entrada: bool):
    """
    Suma o resta `cantidad` del stock de `tienda`.
    Retorna (df_actualizado, error_msg).
    """
    mask = df["id"].astype(str) == str(product_id)
    if not mask.any():
        return df, f"Producto con ID '{product_id}' no encontrado."

    idx = df[mask].index[0]
    stock_actual = int(df.at[idx, tienda])
    delta = cantidad if es_entrada else -cantidad

    nuevo_stock = stock_actual + delta
    if nuevo_stock < 0:
        return df, f"No se puede reducir el stock por debajo de 0. Stock actual en '{tienda}': {stock_actual}."

    df = df.copy()
    df.at[idx, tienda] = nuevo_stock
    return df, None


# ─── UI ───────────────────────────────────────────────────────────────────────
st.markdown('<div class="app-title">Control de Stock por Tienda</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="app-subtitle">Inventario físico, transferencias entre tiendas y ajustes de stock</div>',
    unsafe_allow_html=True,
)

productos_df = cargar_productos()

if productos_df.empty:
    st.warning("No se pudieron cargar los productos. Verifica la conexión con Google Sheets.")
    st.stop()

# ── Tabla resumen de stock ────────────────────────────────────────────────────
st.markdown("### 📦 Resumen de Existencias")

columnas_visibles = ["name", "price"] + STORES
df_tabla = productos_df[columnas_visibles].copy()
df_tabla["Stock Total"] = df_tabla[STORES].sum(axis=1)
df_tabla = df_tabla.rename(columns={"name": "Producto", "price": "Precio ($)"})

st.dataframe(df_tabla, use_container_width=True, hide_index=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Formularios: dos columnas independientes ───────────────────────────────────
col_t, col_a = st.columns(2)

# ── Formulario 1: Transferencia ───────────────────────────────────────────────
with col_t:
    st.markdown("#### 🔄 Transferir entre Tiendas")

    with st.form("transfer_form", clear_on_submit=True):
        opciones_prod = {
            str(row["id"]): row["name"]
            for _, row in productos_df.iterrows()
        }

        prod_id_transfer = st.selectbox(
            "Producto:",
            list(opciones_prod.keys()),
            format_func=lambda x: opciones_prod[x],
            key="t_product",
        )

        c1, c2 = st.columns(2)
        with c1:
            origen = st.selectbox("Tienda Origen:", STORES, key="t_origen")
        with c2:
            destino = st.selectbox("Tienda Destino:", STORES, key="t_destino")

        # Mostrar stock disponible en origen (informativo)
        mask = productos_df["id"].astype(str) == prod_id_transfer
        if mask.any():
            stock_disp = int(productos_df.loc[mask, origen].values[0])
            st.caption(f"Stock disponible en '{origen}': **{stock_disp}** unidades")

        cantidad_transfer = st.number_input(
            "Cantidad a transferir:", min_value=1, value=1, step=1, key="t_cantidad"
        )

        submit_transfer = st.form_submit_button("✅ Realizar Transferencia")

    if submit_transfer:
        df_actualizado, error = transferir_stock(
            productos_df, prod_id_transfer, origen, destino, cantidad_transfer
        )
        if error:
            st.error(f"❌ {error}")
        else:
            if guardar_productos(df_actualizado):
                nombre_prod = opciones_prod[prod_id_transfer]
                st.success(
                    f"✅ Transferencia exitosa: **{cantidad_transfer}** unidades de "
                    f"**{nombre_prod}** de '{origen}' → '{destino}'."
                )
                time.sleep(1)
                st.rerun()

# ── Formulario 2: Ajuste de stock ─────────────────────────────────────────────
with col_a:
    st.markdown("#### 📥 Entrada / Ajuste de Stock")

    with st.form("adjust_form", clear_on_submit=True):
        opciones_prod_adj = {
            str(row["id"]): row["name"]
            for _, row in productos_df.iterrows()
        }

        prod_id_adj = st.selectbox(
            "Producto:",
            list(opciones_prod_adj.keys()),
            format_func=lambda x: opciones_prod_adj[x],
            key="a_product",
        )

        tienda_adj = st.selectbox("Tienda / Ubicación:", STORES, key="a_tienda")

        # Stock actual informativo
        mask_adj = productos_df["id"].astype(str) == prod_id_adj
        if mask_adj.any():
            stock_act = int(productos_df.loc[mask_adj, tienda_adj].values[0])
            st.caption(f"Stock actual en '{tienda_adj}': **{stock_act}** unidades")

        c3, c4 = st.columns(2)
        with c3:
            tipo_ajuste = st.radio(
                "Tipo:",
                ["➕ Entrada", "➖ Salida"],
                key="a_tipo",
            )
        with c4:
            cantidad_adj = st.number_input(
                "Cantidad:", min_value=1, value=1, step=1, key="a_cantidad"
            )

        submit_adj = st.form_submit_button("💾 Guardar Ajuste")

    if submit_adj:
        es_entrada = tipo_ajuste.startswith("➕")
        df_actualizado, error = ajustar_stock(
            productos_df, prod_id_adj, tienda_adj, cantidad_adj, es_entrada
        )
        if error:
            st.error(f"❌ {error}")
        else:
            if guardar_productos(df_actualizado):
                nombre_prod = opciones_prod_adj[prod_id_adj]
                accion = "agregadas a" if es_entrada else "retiradas de"
                st.success(
                    f"✅ **{cantidad_adj}** unidades de **{nombre_prod}** {accion} '{tienda_adj}'."
                )
                time.sleep(1)
                st.rerun()