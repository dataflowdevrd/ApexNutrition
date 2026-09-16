import os
import streamlit as st
import pandas as pd
import plotly.express as px
from dotenv import load_dotenv
from supabase import create_client, Client

# Cargar variables de entorno
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("Faltan SUPABASE_URL y SUPABASE_KEY en el archivo .env")
    st.stop()

st.set_page_config(
    page_title="Apex Nutrition — Ops Dashboard",
    page_icon="⚡",
    layout="wide"
)

@st.cache_resource
def get_supabase_client() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

@st.cache_data(ttl=30)
def load_table(table_name: str, columns: str = "*") -> list[dict]:
    return supabase.table(table_name).select(columns).execute().data or []

supabase = get_supabase_client()

# Encabezado principal
st.title("⚡ Apex Nutrition — Dashboard Operativo")
st.caption("Control de Inventario Farmacéutico (DIGEMAPS), Facturación (DGII) y Logística")

# Obtener datos base
with st.spinner("Sincronizando con Supabase..."):
    try:
        ventas_data = load_table("ventas")
        lotes_data = load_table("lotes", "*, productos(nombre)")
        deliveries_data = load_table("deliveries")
        eventos_data = load_table("n8n_eventos_omnicanal")
    except Exception as error:
        st.error(f"No se pudieron cargar los datos de Supabase: {error}")
        st.stop()

df_ventas = pd.DataFrame(ventas_data)
df_lotes = pd.DataFrame(lotes_data)
df_deliveries = pd.DataFrame(deliveries_data)
df_eventos = pd.DataFrame(eventos_data)

# Métricas Principales (KPIs)
total_facturado = df_ventas["monto_total_dop"].sum() if not df_ventas.empty else 0.0
total_itbis = df_ventas["itbis_dop"].sum() if not df_ventas.empty else 0.0
stock_disponible = df_lotes["cantidad_actual"].sum() if not df_lotes.empty else 0
deliveries_pendientes = len(df_deliveries[df_deliveries["estado"] == "PENDIENTE"]) if not df_deliveries.empty else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("Ventas Totales", f"RD$ {total_facturado:,.2f}")
col2.metric("ITBIS Recaudado (18%)", f"RD$ {total_itbis:,.2f}")
col3.metric("Stock Total Gomitas", f"{stock_disponible:,} uds")
col4.metric("Despachos Pendientes", deliveries_pendientes)

st.divider()

# Pestañas de Gestión
tab_inventario, tab_fiscal, tab_logistica, tab_omnicanal = st.tabs([
    "📦 Inventario & Lotes (DIGEMAPS)",
    "🧾 Facturación & DGII",
    "🚚 Logística & Deliveries",
    "🌐 Eventos Omnicanal (n8n)"
])

# 1. Tab: Inventario Sanitario
with tab_inventario:
    st.subheader("Control de Lotes y Vencimiento")
    if not df_lotes.empty:
        df_lotes["producto"] = df_lotes["productos"].apply(lambda p: p["nombre"] if isinstance(p, dict) else "N/A")
        cols_mostrar = ["numero_lote", "producto", "cantidad_actual", "cantidad_inicial", "estado", "fecha_vencimiento"]
        st.dataframe(df_lotes[cols_mostrar], use_container_width=True)

        fig_lotes = px.bar(
            df_lotes,
            x="numero_lote",
            y="cantidad_actual",
            color="estado",
            title="Existencias Disponibles por Lote",
            labels={"cantidad_actual": "Unidades Disponibles", "numero_lote": "Lote"}
        )
        st.plotly_chart(fig_lotes, use_container_width=True)
    else:
        st.info("No hay lotes registrados actualmente.")

# 2. Tab: Facturación Fiscal
with tab_fiscal:
    st.subheader("Emisión de Comprobantes Fiscales")
    if not df_ventas.empty:
        col_f1, col_f2 = st.columns([2, 1])
        with col_f1:
            st.dataframe(
                df_ventas[["codigo_factura", "ncf", "tipo_ncf", "metodo_pago", "subtotal_dop", "itbis_dop", "monto_total_dop", "creado_en"]],
                use_container_width=True
            )
        with col_f2:
            fig_ncf = px.pie(
                df_ventas,
                names="tipo_ncf",
                title="Distribución de Comprobantes (B01 vs B02)",
                hole=0.4
            )
            st.plotly_chart(fig_ncf, use_container_width=True)
    else:
        st.info("Aún no se han emitido facturas fiscales.")

# 3. Tab: Despacho y Logística
with tab_logistica:
    st.subheader("Rutas y Envíos Programados")
    if not df_deliveries.empty:
        delivery_cols = [
            "direccion_destino", "distancia_km", "costo_envio_dop", "estado"
        ]
        st.dataframe(
            df_deliveries.reindex(columns=delivery_cols),
            use_container_width=True
        )
    else:
        st.info("No existen entregas registradas en cola.")

# 4. Tab: Ingesta Omnicanal
with tab_omnicanal:
    st.subheader("Registro de Webhooks n8n")
    if not df_eventos.empty:
        event_cols = [
            "canal_origen", "tipo_evento", "estado_procesamiento",
            "creado_en", "payload_json"
        ]
        st.dataframe(
            df_eventos.reindex(columns=event_cols),
            use_container_width=True
        )
    else:
        st.info("No hay eventos omnicanal registrados.")