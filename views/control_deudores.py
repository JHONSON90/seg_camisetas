import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import time
import traceback

# ─── Conexión ────────────────────────────────────────────────────────────────
conn = st.connection("gsheets", type=GSheetsConnection)


# ─── Carga de datos ──────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Cargando datos de ventas...", ttl=60)
def cargar_ventas():
    """Lee la hoja Ventas y retorna un DataFrame."""
    try:
        df = conn.read(worksheet="Ventas", ttl=60)
        # Asegurar tipos correctos
        df["total_amount"] = pd.to_numeric(df["total_amount"], errors="coerce").fillna(0)
        df["amount_paid"]  = pd.to_numeric(df["amount_paid"],  errors="coerce").fillna(0)
        df["quantity"]     = pd.to_numeric(df["quantity"],     errors="coerce").fillna(0)
        return df
    except Exception as e:
        st.error(f"Error al leer Google Sheets (Ventas): {e}")
        st.error(traceback.format_exc())
        return pd.DataFrame()


def calcular_deudores(sales_df: pd.DataFrame) -> list[dict]:
    """Filtra ventas con saldo pendiente y retorna lista de deudores."""
    deudores = []
    for _, row in sales_df.iterrows():
        pendiente = float(row["total_amount"]) - float(row["amount_paid"])
        if pendiente > 0.01:
            deudores.append({
                "sale_id":       str(row["id"]),
                "date":          str(row["date"]),
                "client_name":   str(row["client_name"]),
                "client_contact":str(row["client_contact"]),
                "product_name":  str(row["product_name"]),
                "quantity":      int(row["quantity"]),
                "total_amount":  float(row["total_amount"]),
                "amount_paid":   float(row["amount_paid"]),
                "debt_pending":  round(pendiente, 2),
                "store":         str(row["store"]),
            })
    return deudores


def registrar_abono(sale_id: str, abono: float) -> bool:
    """
    Lee toda la hoja Ventas, actualiza amount_paid de la fila correspondiente
    y sobreescribe la hoja completa con conn.update().
    Retorna True si tuvo éxito.
    """
    try:
        # Leer hoja fresca (sin caché)
        df = conn.read(worksheet="Ventas", ttl=0)
        df["total_amount"] = pd.to_numeric(df["total_amount"], errors="coerce").fillna(0)
        df["amount_paid"]  = pd.to_numeric(df["amount_paid"],  errors="coerce").fillna(0)

        mask = df["id"].astype(str) == sale_id
        if not mask.any():
            st.error(f"No se encontró la venta con ID: {sale_id}")
            return False

        idx = df[mask].index[0]
        total   = float(df.at[idx, "total_amount"])
        pagado  = float(df.at[idx, "amount_paid"])
        deuda   = total - pagado

        if abono <= 0:
            st.error("El abono debe ser mayor a cero.")
            return False
        if abono > deuda + 0.01:
            st.error(f"El abono (${abono:.2f}) supera la deuda (${deuda:.2f}).")
            return False

        df.at[idx, "amount_paid"] = round(pagado + abono, 2)

        # Sobreescribir la hoja Ventas completa
        conn.update(worksheet="Ventas", data=df)

        # Limpiar caché para que la próxima lectura sea fresca
        st.cache_data.clear()
        return True

    except Exception as e:
        st.error(f"Error al registrar abono: {e}")
        st.error(traceback.format_exc())
        return False


# ─── UI ──────────────────────────────────────────────────────────────────────
def draw_metric(label, value, icon):
    st.markdown(f"""
    <div class="glass-card">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <div>
                <div class="metric-label">{label}</div>
                <div class="metric-val">{value}</div>
            </div>
            <div class="metric-icon">{icon}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


st.markdown('<div class="app-title">Listado de Clientes Deudores</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="app-subtitle">Gestión de saldos pendientes y abonos de clientes</div>',
    unsafe_allow_html=True,
)

# Cargar datos y calcular deudores
sales_df = cargar_ventas()
deudores = calcular_deudores(sales_df) if not sales_df.empty else []

if deudores:
    total_deuda = sum(d["debt_pending"] for d in deudores)

    # Tarjeta resumen
    st.markdown(f"""
        <div class="glass-card" style="border-left:5px solid #EF4444;">
            <h4 style="margin:0; color:#EF4444;">⚠️ Saldo Total en Mora</h4>
            <div style="font-size:2.3rem; font-weight:800; margin-top:8px;">${total_deuda:,.2f}</div>
            <p style="margin:5px 0 0 0; color:#94A3B8; font-size:0.9rem;">
                Hay <strong>{len(deudores)}</strong> clientes con saldos pendientes.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # Tabla de deudores
    df_tabla = pd.DataFrame([{
        "ID Venta":            d["sale_id"],
        "Fecha":               d["date"],
        "Cliente":             d["client_name"],
        "Contacto":            d["client_contact"],
        "Producto":            d["product_name"],
        "Cant.":               d["quantity"],
        "Valor Total ($)":     d["total_amount"],
        "Abonado ($)":         d["amount_paid"],
        "Deuda Pendiente ($)": d["debt_pending"],
        "Tienda":              d["store"],
    } for d in deudores])

    st.dataframe(df_tabla, use_container_width=True, hide_index=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Formulario de abono ──────────────────────────────────────────────────
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("<h4>💳 Registrar Abono / Liquidar Deuda</h4>", unsafe_allow_html=True)

    with st.form("abono_form", clear_on_submit=True):
        opciones = {
            d["sale_id"]: (
                f"{d['client_name']} — {d['product_name']} "
                f"| Debe: ${d['debt_pending']:.2f} [{d['store']}]"
            )
            for d in deudores
        }

        sale_id_seleccionado = st.selectbox(
            "Seleccionar Deudor y Venta:",
            list(opciones.keys()),
            format_func=lambda x: opciones[x],
        )

        deudor_actual = next(d for d in deudores if d["sale_id"] == sale_id_seleccionado)

        col_izq, col_der = st.columns(2)
        with col_izq:
            monto_abono = st.number_input(
                "Monto del Abono ($):",
                min_value=0.01,
                max_value=float(deudor_actual["debt_pending"]),
                value=float(deudor_actual["debt_pending"]),
                step=1.0,
                help="Cantidad que el cliente está pagando ahora.",
            )
        with col_der:
            st.markdown("<br>", unsafe_allow_html=True)
            if abs(monto_abono - deudor_actual["debt_pending"]) < 0.01:
                st.info("💡 Esto liquidará completamente la deuda.")
            else:
                restante = deudor_actual["debt_pending"] - monto_abono
                st.info(f"💡 Saldo restante tras el abono: ${restante:.2f}")

        submit = st.form_submit_button("✅ Aplicar Abono")

        if submit:
            exito = registrar_abono(sale_id_seleccionado, monto_abono)
            if exito:
                st.success(
                    f"¡Abono de ${monto_abono:.2f} registrado para {deudor_actual['client_name']}!"
                )
                time.sleep(1)
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

else:
    st.success("🎉 ¡No hay clientes deudores! Todos los pedidos están saldados.")