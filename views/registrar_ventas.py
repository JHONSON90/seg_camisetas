# import streamlit as st
# import pandas as pd
# from streamlit_gsheets import GSheetsConnection
# import time
# import traceback
# import plotly.express as px
# import plotly.graph_objects as go
# from datetime import datetime


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


# st.markdown('<div class="app-title">Registro y Control de Ventas</div>', unsafe_allow_html=True)
# st.markdown('<div class="app-subtitle">Cree nuevos pedidos y revise el histórico completo de facturación</div>', unsafe_allow_html=True)
        
# col_v_form, col_v_hist = st.columns([1, 2])
        
# with col_v_form:
#     st.markdown('<div class="glass-card">', unsafe_allow_html=True)
#     st.markdown('<h4>🛍️ Registrar Nueva Venta</h4>', unsafe_allow_html=True)
            
#     with st.form("sale_form", clear_on_submit=True):
#         client_name = st.text_input("Nombre del Cliente:", placeholder="Ej. Juan Pérez")
#         client_contact = st.text_input("Contacto (Teléfono/Email):", placeholder="Ej. +57 300 123 4567")
                
#         p_options = {p["id"]: f"{p['name']} (${p['price']:.2f})" for p in products}
#         selected_p_id = st.selectbox("Producto:", list(p_options.keys()), format_func=lambda x: p_options[x], key="sale_p")
                
#         selected_store = st.selectbox("Vendido desde:", stores, key="sale_store")
                
#         col_qty_date = st.columns(2)
#         with col_qty_date[0]:
#             qty = st.number_input("Cantidad:", min_value=1, value=1, step=1)
#         with col_qty_date[1]:
#             sale_date = st.date_input("Fecha:", value=datetime.now().date())
                    
#         prod_selected = p_options.get(selected_p_id)
#         #prod_price = products.get(selected_p_id, {}).get("price", 0)
#         total_est = prod_selected["price"] * qty if prod_selected else 0
                
#         st.markdown(f"**Total Estimado a Pagar:** `${total_est:,.2f}`")
                
#         amount_paid = st.number_input(
#             "Monto Pagado en el Acto ($):",
#             min_value=0.0,
#             max_value=float(total_est) if total_est > 0 else 1000.0,
#             value=float(total_est) if total_est > 0 else 0.0,
#             step=1.0,
#             help="Si el monto es menor al total estimado, se registrará una deuda para el cliente."
#         )
                
#         debt_val = total_est - amount_paid
#         if debt_val > 0.01:
#             st.warning(f"⚠️ Se registrará una deuda de **${debt_val:,.2f}** a nombre de {client_name if client_name else 'este cliente'}.")
                    
#         submit_sale = st.form_submit_button("Confirmar Venta")
                
#         if submit_sale:
#             df_ventas = conn.read(worksheet="Ventas", ttl=0)

#             if not client_name.strip():
#                 st.error("Por favor, ingrese el nombre del cliente.")
#             else:
#                 try:
#                     # Convert date to string YYYY-MM-DD
#                     sale_date_str = sale_date.strftime("%Y-%m-%d")
#                     new_row = pd.DataFrame([{
#                         "id": f"sale_{len(df_ventas) + 1}",
#                         "date": sale_date_str,
#                         "client_name": client_name,
#                         "client_contact": client_contact,
#                         "product_id": selected_p_id,
#                         "product_name": prod_selected["name"],
#                         "quantity": qty,
#                         "price": prod_selected["price"],
#                         "total_amount": total_est,
#                         "amount_paid": amount_paid,
#                         "debt_pending": debt_val,
#                         "store": selected_store,
#                         "status": "Pagado" if debt_val == 0 else "Deudor"
#                     }])
                    
#                     df_ventas = pd.concat([df_ventas, new_row], ignore_index=True)
#                     conn.update(
#                         worksheet="Ventas",
#                         data=df_ventas
#                     )
#                     st.success(f"Venta registrada. Total: ${total_est:,.2f}, Pagado: ${amount_paid:,.2f}")
#                     st.rerun()
#                 except Exception as e:
#                     st.error(f"Error al registrar la venta: {str(e)}")
#             st.markdown('</div>', unsafe_allow_html=True)
            
#         with col_v_hist:
#             st.markdown('<div class="section-header">Historial de Ventas</div>', unsafe_allow_html=True)
            
#             if sales_df:
#                 # Filter bar
#                 col_f1, col_f2 = st.columns(2)
#                 with col_f1:
#                     filter_store = st.selectbox("Filtrar por Tienda:", ["Todas"] + stores)
#                 with col_f2:
#                     search_client = st.text_input("Buscar por Cliente:", "")
                    
#                 # Process dataframe
#                 history_data = []
#                 for s in sales_df:
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


import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import time
import traceback
from datetime import datetime

# ─── Configuración ────────────────────────────────────────────────────────────
STORES = ["Casa", "Tienda Linares", "Nicolas", "Ipiales"]

conn = st.connection("gsheets", type=GSheetsConnection)


# ─── Lectura de datos ─────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Cargando datos...", ttl=60)
def cargar_productos() -> pd.DataFrame:
    df = conn.read(worksheet="Productos", ttl=60)
    df["price"] = pd.to_numeric(df["price"], errors="coerce").fillna(0.0)
    for store in STORES:
        if store in df.columns:
            df[store] = pd.to_numeric(df[store], errors="coerce").fillna(0).astype(int)
    return df


@st.cache_data(show_spinner="Cargando ventas...", ttl=60)
def cargar_ventas() -> pd.DataFrame:
    df = conn.read(worksheet="Ventas", ttl=60)
    if df.empty:
        return df
    df["total_amount"] = pd.to_numeric(df["total_amount"], errors="coerce").fillna(0)
    df["amount_paid"]  = pd.to_numeric(df["amount_paid"],  errors="coerce").fillna(0)
    df["quantity"]     = pd.to_numeric(df["quantity"],     errors="coerce").fillna(0)
    return df


# ─── Escritura ────────────────────────────────────────────────────────────────
def registrar_venta(product_id: str, store: str, qty: int,
                    client_name: str, client_contact: str,
                    sale_date: str, amount_paid: float) -> tuple[bool, str]:
    """
    1. Lee Productos y descuenta stock en la tienda seleccionada.
    2. Lee Ventas, genera nuevo ID y agrega la fila.
    3. Guarda ambas hojas.
    Retorna (exito: bool, mensaje: str).
    """
    try:
        # ── 1. Leer Productos fresco ──────────────────────────────────────────
        df_prod = conn.read(worksheet="Productos", ttl=0)
        df_prod["price"] = pd.to_numeric(df_prod["price"], errors="coerce").fillna(0.0)
        for s in STORES:
            if s in df_prod.columns:
                df_prod[s] = pd.to_numeric(df_prod[s], errors="coerce").fillna(0).astype(int)

        mask = df_prod["id"].astype(str) == str(product_id)
        if not mask.any():
            return False, f"Producto con ID '{product_id}' no encontrado."

        idx = df_prod[mask].index[0]
        stock_disp = int(df_prod.at[idx, store])
        if stock_disp < qty:
            return False, (
                f"Stock insuficiente en '{store}'. "
                f"Disponible: {stock_disp}, solicitado: {qty}."
            )

        unit_price   = float(df_prod.at[idx, "price"])
        product_name = str(df_prod.at[idx, "name"])
        total_amount = round(unit_price * qty, 2)
        debt         = round(total_amount - amount_paid, 2)
        status       = "Pagado" if debt <= 0.01 else "Deudor"

        # Descontar stock
        df_prod = df_prod.copy()
        df_prod.at[idx, store] = stock_disp - qty

        # ── 2. Leer Ventas fresco ─────────────────────────────────────────────
        df_ventas = conn.read(worksheet="Ventas", ttl=0)

        # Generar ID único
        if df_ventas.empty or "id" not in df_ventas.columns:
            nuevo_id = "sale_1"
        else:
            ids_num = []
            for v in df_ventas["id"].astype(str):
                try:
                    ids_num.append(int(v.split("_")[1]))
                except Exception:
                    pass
            nuevo_id = f"sale_{max(ids_num, default=0) + 1}"

        nueva_fila = pd.DataFrame([{
            "id":              nuevo_id,
            "date":            sale_date,
            "product_id":      product_id,
            "product_name":    product_name,
            "quantity":        qty,
            "price":           unit_price,
            "total_amount":    total_amount,
            "amount_paid":     round(amount_paid, 2),
            "client_name":     client_name,
            "client_contact":  client_contact,
            "store":           store,
            "status":          status,
        }])

        df_ventas = pd.concat([df_ventas, nueva_fila], ignore_index=True)

        # ── 3. Guardar ambas hojas ────────────────────────────────────────────
        conn.update(worksheet="Productos", data=df_prod)
        conn.update(worksheet="Ventas",    data=df_ventas)
        st.cache_data.clear()

        return True, (
            f"Venta registrada. Producto: **{product_name}** × {qty} | "
            f"Total: **${total_amount:,.2f}** | Pagado: **${amount_paid:,.2f}**"
            + (f" | Deuda: **${debt:,.2f}**" if debt > 0.01 else "")
        )

    except Exception as e:
        return False, f"Error inesperado: {e}\n{traceback.format_exc()}"


# ─── UI ───────────────────────────────────────────────────────────────────────
st.markdown('<div class="app-title">Registro y Control de Ventas</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="app-subtitle">Cree nuevos pedidos y revise el histórico completo de facturación</div>',
    unsafe_allow_html=True,
)

productos_df = cargar_productos()
ventas_df    = cargar_ventas()

if productos_df.empty:
    st.warning("No se pudieron cargar los productos. Verifica la conexión con Google Sheets.")
    st.stop()

col_form, col_hist = st.columns([1, 2])

# ── Formulario de nueva venta ──────────────────────────────────────────────────
with col_form:
    st.markdown("#### 🛍️ Registrar Nueva Venta")

    # Selectbox de producto FUERA del formulario para poder calcular precio en tiempo real
    opciones_prod = {
        str(row["id"]): f"{row['name']}  —  ${row['price']:.2f}"
        for _, row in productos_df.iterrows()
    }

    prod_id_sel = st.selectbox(
        "Producto:",
        list(opciones_prod.keys()),
        format_func=lambda x: opciones_prod[x],
        key="venta_producto",
    )

    tienda_sel = st.selectbox("Vendido desde:", STORES, key="venta_tienda")

    # Info de stock disponible
    mask_prod = productos_df["id"].astype(str) == prod_id_sel
    if mask_prod.any():
        precio_unit = float(productos_df.loc[mask_prod, "price"].values[0])
        precio_min = float(productos_df.loc[mask_prod, "Min_price"].values[0])
        stock_disp  = int(productos_df.loc[mask_prod, tienda_sel].values[0])
        st.caption(f"Stock disponible en **{tienda_sel}**: {stock_disp} unidades")
    else:
        precio_unit = 0.0
        stock_disp  = 0

    with st.form("sale_form", clear_on_submit=True):
        client_name    = st.text_input("Nombre del Cliente:", placeholder="Ej. Juan Pérez")
        client_contact = st.text_input("Contacto:", placeholder="+57 300 123 4567")

        col_q, col_d = st.columns(2)
        with col_q:
            qty = st.number_input(
                "Cantidad:",
                min_value=1,
                max_value=max(stock_disp, 1),
                value=1,
                step=1,
            )
        with col_d:
            sale_date = st.date_input("Fecha:", value=datetime.now().date())

        valor_unt = st.number_input(
                "Valor Unitario:",
                min_value=float(precio_min),
                max_value=float(precio_unit),
                value=float(precio_unit),
                step=1000.00,
                format="%.2f"
            )

        total_est = round(valor_unt * qty, 2)
        st.markdown(f"**Total estimado:** `${total_est:,.2f}`")    

        amount_paid = st.number_input(
            "Monto Pagado ($):",
            min_value=0.0,
            max_value=float(total_est) if total_est > 0 else 999999.0,
            value=float(total_est),
            step=1.0,
            help="Si es menor al total, se registrará una deuda.",
        )

        deuda_est = total_est - amount_paid
        if deuda_est > 0.01:
            st.warning(
                f"⚠️ Deuda de **${deuda_est:,.2f}** a nombre de "
                f"{client_name if client_name.strip() else 'este cliente'}."
            )

        submit = st.form_submit_button("✅ Confirmar Venta")

    # Lógica fuera del form
    if submit:
        if not client_name.strip():
            st.error("Por favor, ingrese el nombre del cliente.")
        elif stock_disp < qty:
            st.error(f"Stock insuficiente en '{tienda_sel}'. Disponible: {stock_disp}.")
        else:
            ok, msg = registrar_venta(
                product_id=prod_id_sel,
                store=tienda_sel,
                qty=qty,
                client_name=client_name.strip(),
                client_contact=client_contact.strip(),
                sale_date=sale_date.strftime("%Y-%m-%d"),
                amount_paid=amount_paid,
            )
            if ok:
                st.success(msg)
                time.sleep(1)
                st.rerun()
            else:
                st.error(f"❌ {msg}")

# ── Historial de ventas ────────────────────────────────────────────────────────
with col_hist:
    st.markdown("#### 📋 Historial de Ventas")

    if ventas_df.empty:
        st.info("Aún no se han registrado transacciones.")
    else:
        # Filtros
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            filtro_tienda = st.selectbox("Filtrar por Tienda:", ["Todas"] + STORES, key="hist_tienda")
        with col_f2:
            buscar_cliente = st.text_input("Buscar Cliente:", "", key="hist_cliente")

        # Construir tabla
        df_hist = ventas_df.copy()
        df_hist["Deuda ($)"] = (
            df_hist["total_amount"] - df_hist["amount_paid"]
        ).round(2).clip(lower=0)
        df_hist["Estado"] = df_hist["Deuda ($)"].apply(
            lambda d: "🔴 Deudor" if d > 0.01 else "🟢 Pagado"
        )

        df_hist = df_hist.rename(columns={
            "date":         "Fecha",
            "client_name":  "Cliente",
            "product_name": "Producto",
            "quantity":     "Cant.",
            "total_amount": "Total ($)",
            "amount_paid":  "Pagado ($)",
            "store":        "Tienda",
        })

        columnas_mostrar = ["Fecha", "Cliente", "Producto", "Cant.",
                            "Total ($)", "Pagado ($)", "Deuda ($)", "Tienda", "Estado"]
        df_hist = df_hist[columnas_mostrar]

        # Aplicar filtros
        if filtro_tienda != "Todas":
            df_hist = df_hist[df_hist["Tienda"] == filtro_tienda]
        if buscar_cliente.strip():
            df_hist = df_hist[
                df_hist["Cliente"].str.contains(buscar_cliente.strip(), case=False, na=False)
            ]

        st.dataframe(
            df_hist.sort_values("Fecha", ascending=False),
            use_container_width=True,
            hide_index=True,
        )

        csv = df_hist.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Exportar a CSV",
            data=csv,
            file_name=f"ventas_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
        )