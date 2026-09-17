import os
import requests
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Apex Nutrition — Ops Console",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inyección de estilos modernos modo oscuro (Figma UI SaaS)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

    html, body, [class*="css"], .stApp {
        background:
            radial-gradient(circle at 80% -10%, rgba(88, 166, 255, 0.23), transparent 32%),
            radial-gradient(circle at 8% 85%, rgba(240, 136, 62, 0.10), transparent 28%),
            #080C14 !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        color: #E6EDF3;
    }
    
    [data-testid="stSidebar"] {
        background: rgba(15, 20, 31, 0.68) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.10);
        backdrop-filter: blur(22px);
        -webkit-backdrop-filter: blur(22px);
    }

    .card {
        background: linear-gradient(145deg, rgba(31, 43, 62, 0.68), rgba(15, 22, 34, 0.58));
        border: 1px solid rgba(255, 255, 255, 0.13);
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.07), 0 18px 45px rgba(0, 0, 0, 0.16);
        backdrop-filter: blur(18px);
        -webkit-backdrop-filter: blur(18px);
        border-radius: 16px;
        padding: 22px;
        margin-bottom: 18px;
    }
    .card-title {
        color: #8B949E;
        font-size: 13px;
        font-weight: 600;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        margin-bottom: 6px;
    }
    .card-metric {
        color: #FFFFFF;
        font-size: 26px;
        font-weight: 700;
        letter-spacing: -0.02em;
    }
    .card-sub {
        color: #58A6FF;
        font-size: 12px;
        margin-top: 4px;
        font-weight: 500;
    }

    .brand-kicker {
        color: #58A6FF;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.16em;
        text-transform: uppercase;
        margin-bottom: 8px;
    }
    .brand-title {
        color: #FFFFFF;
        font-size: 31px;
        line-height: 1.1;
        font-weight: 700;
        margin: 0;
    }
    .brand-copy {
        color: #8B949E;
        font-size: 14px;
        margin-top: 8px;
    }
    .item-card {
        background: linear-gradient(145deg, rgba(38, 54, 77, 0.66), rgba(16, 24, 37, 0.52));
        border: 1px solid rgba(255, 255, 255, 0.12);
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.06);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border-radius: 14px;
        padding: 16px;
        min-height: 122px;
        margin-bottom: 12px;
    }
    .item-card strong { color: #F0F6FC; font-size: 15px; }
    .item-meta { color: #8B949E; font-size: 12px; margin-top: 7px; }
    .item-value { color: #FFFFFF; font-size: 18px; font-weight: 700; margin-top: 12px; }
    .status-pill {
        display: inline-block;
        border-radius: 999px;
        padding: 4px 9px;
        color: #B6F2C2;
        background: rgba(46, 160, 67, 0.16);
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 0.04em;
        text-transform: uppercase;
    }
    .status-pill.warning { color: #FFD580; background: rgba(240, 136, 62, 0.16); }
    .status-pill.neutral { color: #B8C7DB; background: rgba(139, 148, 158, 0.14); }
    .section-label {
        color: #8B949E;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin: 8px 0 12px;
    }
    .map-link {
        display: block;
        width: 100%;
        box-sizing: border-box;
        padding: 9px 10px;
        border: 1px solid rgba(255, 255, 255, 0.14);
        border-radius: 8px;
        color: #B8D8FF !important;
        background: rgba(255, 255, 255, 0.06);
        text-align: center;
        text-decoration: none !important;
        font-size: 12px;
        font-weight: 600;
    }
    .map-link:hover {
        background: rgba(88, 166, 255, 0.16);
        border-color: rgba(88, 166, 255, 0.45);
    }
    /* Dropdown cerrado: se puede escoger con clic, pero no escribir texto. */
    [data-testid="stSelectbox"] [data-baseweb="select"] input {
        opacity: 0 !important;
        width: 0 !important;
        min-width: 0 !important;
        position: absolute !important;
        pointer-events: none !important;
    }
    @media (max-width: 760px) {
        .brand-title { font-size: 25px; }
        .card { padding: 16px; }
        .item-card { min-height: auto; }
        div.stButton > button, .map-link { min-height: 42px; }
    }
    
    /* Botones y formularios minimalistas */
    div.stButton > button {
        background: rgba(31, 111, 235, 0.78) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.16) !important;
        box-shadow: 0 8px 20px rgba(31, 111, 235, 0.18);
        backdrop-filter: blur(12px);
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 0.5rem 1rem !important;
    }
    div.stButton > button[kind="secondary"] {
        background: rgba(255, 255, 255, 0.06) !important;
        border-color: rgba(255, 255, 255, 0.12) !important;
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.05) !important;
    }
    .stTextInput > div > div > input, .stSelectbox > div > div {
        background: rgba(22, 27, 38, 0.62) !important;
        border: 1px solid rgba(255, 255, 255, 0.13) !important;
        color: white !important;
        border-radius: 8px !important;
        backdrop-filter: blur(12px);
    }
    /* Los selectores se usan solo como menus: no permiten escribir texto. */
    [data-baseweb="select"] input {
        caret-color: transparent !important;
        color: transparent !important;
        width: 1px !important;
        pointer-events: none !important;
    }
</style>
""", unsafe_allow_html=True)


def field(row, name, fallback="—"):
    value = row.get(name, fallback)
    return fallback if value is None or (isinstance(value, float) and pd.isna(value)) else value


def money(value):
    return f"RD$ {float(value or 0):,.2f}"


def status_class(status):
    status = str(status or "").upper()
    return "" if status in {"ACTIVO", "ENTREGADO", "PAGADO", "COMPLETADO"} else "warning" if status in {"PENDIENTE", "EN_RUTA", "PROCESANDO"} else "neutral"


def product_name(row):
    product = row.get("productos")
    return product.get("nombre", "Producto Apex") if isinstance(product, dict) else "Producto Apex"


def ncf_label(code):
    return {
        "B02": "Consumidor final",
        "B01": "Empresas",
    }.get(str(code), str(code))


def product_field(row, name, fallback=0):
    product = row.get("productos")
    return product.get(name, fallback) if isinstance(product, dict) else fallback


def save_delivery_status(delivery_id, widget_key):
    selected_state = st.session_state[widget_key]
    try:
        response = requests.patch(
            f"{API_URL}/deliveries/{delivery_id}/estado",
            params={"estado": selected_state},
            timeout=10,
        )
        if response.ok:
            st.session_state["delivery_status_message"] = "Estado actualizado automáticamente."
        else:
            st.session_state["delivery_status_error"] = "No se pudo actualizar el estado."
    except requests.RequestException:
        st.session_state["delivery_status_error"] = "No se pudo conectar con la API."

@st.cache_resource
def init_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

# Navegación Vertical (Sidebar UI)
with st.sidebar:
    st.markdown("### ⚡ **Apex Nutrition**")
    st.caption("Operations & Compliance")
    st.write("")
    navigation_items = ["Dashboard", "Catálogo & Lotes", "Facturación DGII", "Logística", "Webhooks n8n"]
    if "menu" not in st.session_state:
        st.session_state.menu = navigation_items[0]
    for navigation_item in navigation_items:
        if st.button(
            navigation_item,
            key=f"nav_{navigation_item}",
            use_container_width=True,
            type="primary" if st.session_state.menu == navigation_item else "secondary",
        ):
            st.session_state.menu = navigation_item
            st.rerun()
    menu = st.session_state.menu
    st.write("---")
    if st.button("🔄 Refrescar Datos", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# Carga de Datos
ventas = supabase.table("ventas").select("*").order("creado_en", desc=True).execute().data or []
lotes = supabase.table("lotes").select("*, productos(nombre, precio_base_dop, costo_produccion_dop)").execute().data or []
productos = supabase.table("productos").select("*").execute().data or []
deliveries = supabase.table("deliveries").select("*").order("creado_en", desc=True).execute().data or []

df_v = pd.DataFrame(ventas)
df_l = pd.DataFrame(lotes)
df_p = pd.DataFrame(productos)
df_d = pd.DataFrame(deliveries)

if not df_l.empty:
    df_l["precio_venta_unitario"] = df_l.apply(lambda row: product_field(row, "precio_base_dop"), axis=1)
    df_l["costo_unitario"] = df_l.apply(lambda row: product_field(row, "costo_produccion_dop"), axis=1)
    df_l["unidades_vendidas"] = (df_l["cantidad_inicial"] - df_l["cantidad_actual"]).clip(lower=0)

# --- VISTA 1: DASHBOARD SAAS (LAYOUT EXACTO A LA REFERENCIA) ---
if menu == "Dashboard":
    st.markdown('<div class="brand-kicker">Apex Performance System</div><h1 class="brand-title">Panel de control</h1><div class="brand-copy">Inventario, ventas y entregas de tu línea de creatina en un solo lugar.</div>', unsafe_allow_html=True)

    # Indicadores financieros calculados sobre el flujo real de ventas e inventario.
    now = pd.Timestamp(datetime.utcnow()).normalize()
    month_start = now.replace(day=1)
    month_end = month_start + pd.offsets.MonthEnd(0)
    days_elapsed = max(now.day, 1)
    days_in_month = month_end.day

    if not df_v.empty and "creado_en" in df_v:
        df_v["fecha_venta"] = pd.to_datetime(df_v["creado_en"], errors="coerce", utc=True).dt.tz_localize(None).dt.normalize()
        month_sales = df_v[df_v["fecha_venta"].between(month_start, now)]
    else:
        month_sales = pd.DataFrame()

    sales_column = "subtotal_dop" if "subtotal_dop" in df_v else "monto_total_dop"
    month_sales_total = month_sales[sales_column].sum() if not month_sales.empty else 0.0
    projected_month_sales = month_sales_total / days_elapsed * days_in_month
    total_sales_for_profit = df_v[sales_column].sum() if not df_v.empty else 0.0
    tot_itbis = df_v["itbis_dop"].sum() if not df_v.empty and "itbis_dop" in df_v else 0.0
    stock_act = df_l["cantidad_actual"].sum() if not df_l.empty else 0
    stock_value = (df_l["cantidad_actual"] * df_l["precio_venta_unitario"]).sum() if not df_l.empty else 0.0
    sold_cost = (df_l["unidades_vendidas"] * df_l["costo_unitario"]).sum() if not df_l.empty else 0.0
    delivery_cost = df_d["costo_envio_dop"].sum() if not df_d.empty and "costo_envio_dop" in df_d else 0.0
    net_profit = total_sales_for_profit - sold_cost - delivery_cost
    deliv_pend = len(df_d[df_d["estado"] == "PENDIENTE"]) if not df_d.empty and "estado" in df_d else 0

    c1, c2 = st.columns(2)
    c3, c4 = st.columns(2)

    with c1:
        st.markdown(f'<div class="card"><div class="card-title">Ventas del mes</div><div class="card-metric">{money(month_sales_total)}</div><div class="card-sub">Flujo acumulado real</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="card"><div class="card-title">Proyección de cierre</div><div class="card-metric">{money(projected_month_sales)}</div><div class="card-sub">Ritmo actual · {days_elapsed}/{days_in_month} días</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="card"><div class="card-title">Dinero en stock</div><div class="card-metric">{money(stock_value)}</div><div class="card-sub">Valor de venta · {int(stock_act):,} unidades</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="card"><div class="card-title">Ganancia neta estimada</div><div class="card-metric">{money(net_profit)}</div><div class="card-sub">Ventas - producción - delivery</div></div>', unsafe_allow_html=True)

    secondary_1, secondary_2, secondary_3 = st.columns(3)
    with secondary_1:
        st.markdown(f'<div class="card"><div class="card-title">ITBIS acumulado</div><div class="card-metric">{money(tot_itbis)}</div><div class="card-sub">Fiscal DGII</div></div>', unsafe_allow_html=True)
    with secondary_2:
        st.markdown(f'<div class="card"><div class="card-title">Unidades disponibles</div><div class="card-metric">{int(stock_act):,}</div><div class="card-sub">Inventario activo</div></div>', unsafe_allow_html=True)
    with secondary_3:
        st.markdown(f'<div class="card"><div class="card-title">Envíos pendientes</div><div class="card-metric">{deliv_pend}</div><div class="card-sub">Listos para despacho</div></div>', unsafe_allow_html=True)

    # Panel central: Curva de Facturación + Donut Chart de Inventario
    col_izq, col_der = st.columns([2.2, 1])

    with col_izq:
        st.markdown('<div class="card"><div class="card-title">Flujo diario y proyección mensual</div>', unsafe_allow_html=True)
        if not month_sales.empty:
            daily_sales = month_sales.groupby("fecha_venta")[sales_column].sum()
            dates = pd.date_range(month_start, month_end, freq="D")
            actual = daily_sales.reindex(dates, fill_value=0).cumsum()
            projection = pd.Series(range(1, len(dates) + 1), index=dates) * (month_sales_total / days_elapsed)
            fig_area = go.Figure()
            fig_area.add_trace(go.Scatter(
                x=actual.index,
                y=actual.values,
                fill="tozeroy",
                mode="lines+markers",
                name="Acumulado real",
                line=dict(color='#58A6FF', width=3, shape='spline'),
                fillcolor='rgba(88, 166, 255, 0.12)'
            ))
            fig_area.add_trace(go.Scatter(
                x=projection.index,
                y=projection.values,
                mode="lines",
                name="Proyección",
                line=dict(color="#F0883E", width=2, dash="dash")
            ))
            fig_area.update_layout(
                template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=20, r=20, t=10, b=20),
                height=260,
                xaxis=dict(showgrid=False, color='#6E7681', tickformat='%d %b'),
                yaxis=dict(showgrid=True, gridcolor='#1E2638', color='#6E7681')
            )
            st.plotly_chart(fig_area, use_container_width=True)
        else:
            st.info("Aún no hay ventas este mes para calcular una proyección.")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_der:
        st.markdown('<div class="card"><div class="card-title">Capacidad de Stock</div>', unsafe_allow_html=True)
        if not df_l.empty:
            cant_actual = int(df_l["cantidad_actual"].sum())
            cant_inicial = int(df_l["cantidad_inicial"].sum())
            consumido = max(0, cant_inicial - cant_actual)

            fig_donut = go.Figure(data=[go.Pie(
                labels=['Disponible', 'Vendido'],
                values=[cant_actual, consumido],
                hole=0.72,
                marker=dict(colors=['#58A6FF', '#F0883E']),
                textinfo='none'
            )])
            fig_donut.update_layout(
                showlegend=False,
                template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=10, r=10, t=10, b=10),
                height=180
            )
            st.plotly_chart(fig_donut, use_container_width=True)
            st.markdown(f"<div style='text-align: center; color: #8B949E; font-size: 13px;'>{cant_actual} disponibles de {cant_inicial} producidos</div>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Bloque inferior: actividad resumida, sin exponer el modelo de datos.
    bi1, bi2 = st.columns(2)
    with bi1:
        st.markdown('<div class="card"><div class="card-title">Despachos recientes</div>', unsafe_allow_html=True)
        if not df_d.empty:
            for _, delivery in df_d.head(3).iterrows():
                state = str(field(delivery, "estado", "PENDIENTE"))
                st.markdown(
                    f'<div class="item-card"><span class="status-pill {status_class(state)}">{state.replace("_", " ")}</span>'
                    f'<strong style="display:block;margin-top:10px">{field(delivery, "direccion_destino", "Destino pendiente")}</strong>'
                    f'<div class="item-meta">{field(delivery, "distancia_km", "-")} km · {money(field(delivery, "costo_envio_dop", 0))}</div></div>',
                    unsafe_allow_html=True,
                )
        else:
            st.info("Aún no hay despachos registrados.")
        st.markdown('</div>', unsafe_allow_html=True)

    with bi2:
        st.markdown('<div class="card"><div class="card-title">Ventas recientes</div>', unsafe_allow_html=True)
        if not df_v.empty:
            for _, sale in df_v.head(3).iterrows():
                st.markdown(
                    f'<div class="item-card"><span class="status-pill">{ncf_label(field(sale, "tipo_ncf", "B02"))}</span>'
                    f'<strong style="display:block;margin-top:10px">{field(sale, "codigo_factura", "Venta")}</strong>'
                    f'<div class="item-meta">NCF {field(sale, "ncf")} · {field(sale, "creado_en", "Fecha pendiente")}</div>'
                    f'<div class="item-value">{money(field(sale, "monto_total_dop", 0))}</div></div>',
                    unsafe_allow_html=True,
                )
        else:
            st.info("Aún no hay ventas registradas.")
        st.markdown('</div>', unsafe_allow_html=True)

# --- VISTA 2: CATÁLOGO & LOTES (CRUD) ---
elif menu == "Catálogo & Lotes":
    st.markdown('<div class="brand-kicker">Formula & inventory</div><h1 class="brand-title">Catálogo de productos</h1><div class="brand-copy">Controla cada lote de creatina desde producción hasta despacho.</div>', unsafe_allow_html=True)
    
    t1, t2 = st.tabs(["Lotes activos", "Abrir nuevo lote"])
    with t1:
        if not df_l.empty:
            filter_col, filter_status = st.columns([2, 1])
            with filter_col:
                search_lot = st.text_input("Buscar lote o producto", placeholder="Ej. creatina o LOTE-2026", label_visibility="collapsed")
            with filter_status:
                status_options = ["Todos"] + sorted(df_l["estado"].dropna().astype(str).unique().tolist()) if "estado" in df_l else ["Todos"]
                selected_status = st.selectbox("Estado", status_options, label_visibility="collapsed")

            visible_lots = df_l.copy()
            visible_lots["producto_nombre"] = visible_lots.apply(product_name, axis=1)
            if search_lot:
                term = search_lot.lower()
                visible_lots = visible_lots[
                    visible_lots["numero_lote"].astype(str).str.lower().str.contains(term)
                    | visible_lots["producto_nombre"].str.lower().str.contains(term)
                ]
            if selected_status != "Todos" and "estado" in visible_lots:
                visible_lots = visible_lots[visible_lots["estado"].astype(str) == selected_status]

            lot_columns = st.columns(3)
            for index, (_, lot) in enumerate(visible_lots.head(9).iterrows()):
                state = str(field(lot, "estado", "ACTIVO"))
                with lot_columns[index % 3]:
                    st.markdown(
                        f'<div class="item-card"><span class="status-pill {status_class(state)}">{state}</span>'
                        f'<strong style="display:block;margin-top:12px">{field(lot, "numero_lote")}</strong>'
                        f'<div class="item-meta">{product_name(lot)} · vence {field(lot, "fecha_vencimiento")}</div>'
                        f'<div class="item-value">{int(field(lot, "cantidad_actual", 0)):,} <span style="font-size:12px;color:#8B949E">unidades disponibles</span></div></div>',
                        unsafe_allow_html=True,
                    )
            if visible_lots.empty:
                st.info("No encontramos lotes con esos filtros.")
        else:
            st.info("Todavía no hay lotes en el inventario.")
    with t2:
        with st.form("form_lote"):
            st.markdown("**Aperturar nuevo lote de producto**")
            product_options = df_p["id"].tolist() if not df_p.empty else []
            p_id = st.selectbox("Producto", options=product_options, format_func=lambda x: df_p[df_p["id"] == x]["nombre"].values[0], disabled=not product_options)
            n_lote = st.text_input("Número de Lote", "LOTE-2026-002")
            c_ini = st.number_input("Cantidad Inicial", min_value=1, value=100)
            f_fab = st.date_input("Fecha Fabricación")
            f_ven = st.date_input("Fecha Vencimiento")
            if st.form_submit_button("Guardar en Supabase"):
                res = requests.post(f"{API_URL}/lotes", json={
                    "producto_id": p_id, "numero_lote": n_lote, "cantidad_inicial": c_ini,
                    "cantidad_actual": c_ini, "fecha_fabricacion": str(f_fab),
                    "fecha_vencimiento": str(f_ven), "estado": "ACTIVO"
                })
                if res.status_code == 201:
                    st.success("Lote aperturado.")
                    st.rerun()

# --- VISTA 3: FACTURACIÓN DGII (CRUD) ---
elif menu == "Facturación DGII":
    st.markdown('<div class="brand-kicker">Sales desk</div><h1 class="brand-title">Ventas y facturación</h1><div class="brand-copy">Convierte cada pedido de creatina en una venta trazable y lista para DGII.</div>', unsafe_allow_html=True)

    sale_col1, sale_col2, sale_col3 = st.columns(3)
    with sale_col1:
        st.markdown(f'<div class="card"><div class="card-title">Ventas emitidas</div><div class="card-metric">{len(df_v):,}</div><div class="card-sub">Comprobantes registrados</div></div>', unsafe_allow_html=True)
    with sale_col2:
        st.markdown(f'<div class="card"><div class="card-title">Ingresos acumulados</div><div class="card-metric">{money(df_v["monto_total_dop"].sum() if not df_v.empty else 0)}</div><div class="card-sub">Ventas brutas</div></div>', unsafe_allow_html=True)
    with sale_col3:
        st.markdown(f'<div class="card"><div class="card-title">ITBIS generado</div><div class="card-metric">{money(df_v["itbis_dop"].sum() if not df_v.empty else 0)}</div><div class="card-sub">Fiscal DGII</div></div>', unsafe_allow_html=True)
    
    with st.expander("⚡ Nueva Venta Transaccional"):
        with st.form("form_v"):
            l_disp = df_l[df_l["cantidad_actual"] > 0]
            l_id = st.selectbox("Lote", options=l_disp["id"].tolist(), format_func=lambda x: f"{l_disp[l_disp['id'] == x]['numero_lote'].values[0]} (Stock: {l_disp[l_disp['id'] == x]['cantidad_actual'].values[0]})")
            cant = st.number_input("Unidades", min_value=1, value=1)
            tipo_ncf = st.selectbox(
                "Tipo de cliente",
                ["B02", "B01"],
                format_func=ncf_label,
            )
            met = st.selectbox("Método de Pago", ["TRANSFERENCIA", "EFECTIVO", "TARJETA"])
            if st.form_submit_button("Emitir Comprobante"):
                res = requests.post(f"{API_URL}/ventas", json={
                    "tipo_ncf": tipo_ncf, "metodo_pago": met, "aplica_itbis": True,
                    "items": [{"lote_id": l_id, "cantidad": cant, "precio_unitario": 1850.00}]
                })
                if res.status_code == 201:
                    st.success(f"Emitido: {res.json().get('ncf')}")
                    st.rerun()

    if not df_v.empty:
        st.markdown('<div class="section-label">Últimos comprobantes</div>', unsafe_allow_html=True)
        invoice_columns = st.columns(3)
        for index, (_, sale) in enumerate(df_v.head(9).iterrows()):
            with invoice_columns[index % 3]:
                st.markdown(
                    f'<div class="item-card"><span class="status-pill">{ncf_label(field(sale, "tipo_ncf", "B02"))}</span>'
                    f'<strong style="display:block;margin-top:11px">{field(sale, "codigo_factura", "Venta")}</strong>'
                    f'<div class="item-meta">NCF {field(sale, "ncf")} · {field(sale, "creado_en", "Fecha pendiente")}</div>'
                    f'<div class="item-value">{money(field(sale, "monto_total_dop", 0))}</div></div>',
                    unsafe_allow_html=True,
                )

# --- VISTA 4: LOGÍSTICA ---
elif menu == "Logística":
    st.markdown('<div class="brand-kicker">Last mile</div><h1 class="brand-title">Entregas en movimiento</h1><div class="brand-copy">Sigue cada pedido desde el almacén hasta la puerta del cliente.</div>', unsafe_allow_html=True)
    with st.expander("＋ Crear entrega manual"):
        st.caption("Usa este formulario si n8n no creó el despacho automáticamente.")
        with st.form("form_delivery_manual"):
            delivery_col1, delivery_col2 = st.columns(2)
            with delivery_col1:
                if not df_v.empty and "id" in df_v.columns:
                    sale_options = df_v["id"].dropna().astype(str).tolist()
                    manual_sale_id = st.selectbox(
                        "Venta asociada",
                        options=sale_options,
                        format_func=lambda sale_id: (
                            f"{df_v.loc[df_v['id'].astype(str) == sale_id, 'codigo_factura'].iloc[0]} · "
                            f"{money(df_v.loc[df_v['id'].astype(str) == sale_id, 'monto_total_dop'].iloc[0])}"
                        ),
                    )
                    st.caption("El ID se obtiene automáticamente desde la venta seleccionada.")
                else:
                    manual_sale_id = None
                    st.warning("No hay ventas disponibles para asociar una entrega.")
                manual_address = st.text_input("Dirección de entrega", placeholder="Calle, número y referencia")
                manual_sector = st.text_input("Sector", placeholder="Ej. Piantini")
                manual_contact = st.text_input("Nombre del receptor", placeholder="Nombre del cliente")
            with delivery_col2:
                manual_phone = st.text_input("Teléfono", placeholder="809-000-0000")
                manual_lat = st.number_input("Latitud (opcional)", value=0.0, format="%.6f")
                manual_lng = st.number_input("Longitud (opcional)", value=0.0, format="%.6f")
                manual_distance = st.number_input("Distancia manual en km (opcional)", min_value=0.0, value=0.0, step=0.1)
            manual_notes = st.text_area("Notas para el mensajero", placeholder="Referencia, horario o indicación adicional")
            manual_submit = st.form_submit_button("Crear entrega", use_container_width=True)

            if manual_submit:
                if not manual_sale_id or not manual_address:
                    st.error("Selecciona una venta y completa la dirección de entrega.")
                elif (manual_lat == 0) != (manual_lng == 0):
                    st.error("Completa latitud y longitud juntas, o deja ambas vacías.")
                elif manual_lat == 0 and manual_lng == 0 and manual_distance == 0:
                    st.error("Añade coordenadas para calcular la ruta o indica la distancia manual.")
                else:
                    delivery_payload = {
                        "venta_id": manual_sale_id,
                        "direccion_destino": manual_address,
                        "sector": manual_sector or None,
                        "contacto_receptor": manual_contact or None,
                        "telefono_receptor": manual_phone or None,
                        "notas_entrega": manual_notes or None,
                    }
                    if manual_lat != 0 and manual_lng != 0:
                        delivery_payload.update({"destino_lat": manual_lat, "destino_lng": manual_lng})
                    else:
                        delivery_payload["distancia_km"] = manual_distance
                    try:
                        delivery_response = requests.post(f"{API_URL}/deliveries", json=delivery_payload, timeout=12)
                        if delivery_response.status_code == 201:
                            st.success("Entrega creada y lista para despacho.")
                            st.rerun()
                        else:
                            detail = delivery_response.json().get("detail", "No se pudo crear la entrega.")
                            st.error(detail)
                    except requests.RequestException:
                        st.error("No se pudo conectar con la API. Verifica que FastAPI esté ejecutándose.")

    with st.expander("📍 Cotizar una nueva ubicación"):
        st.caption("Usa las coordenadas que envía el checkout de tu web para calcular la ruta real.")
        quote_col1, quote_col2, quote_col3 = st.columns(3)
        with quote_col1:
            quote_lat = st.number_input("Latitud", value=18.4861, format="%.6f")
        with quote_col2:
            quote_lng = st.number_input("Longitud", value=-69.9312, format="%.6f")
        with quote_col3:
            st.write("")
            quote_clicked = st.button("Calcular costo", use_container_width=True)
        if quote_clicked:
            quote_response = requests.post(
                f"{API_URL}/deliveries/cotizar",
                json={"destino_lat": quote_lat, "destino_lng": quote_lng},
                timeout=10,
            )
            if quote_response.ok:
                quote = quote_response.json()
                st.success(f"{quote['distancia_km']} km · {quote.get('duracion_minutos', '-')} min · {money(quote['costo_envio_dop'])} · {quote.get('proveedor', 'OpenStreetMap')}")
            else:
                st.error(quote_response.json().get("detail", "No se pudo calcular la ruta."))

    if not df_d.empty:
        if st.session_state.pop("delivery_status_message", None):
            st.success("Estado actualizado automáticamente.")
        if st.session_state.pop("delivery_status_error", None):
            st.error("No se pudo actualizar el estado.")
        logistics_filter = st.selectbox("Filtrar por estado", ["Todos"] + sorted(df_d["estado"].dropna().astype(str).unique().tolist()) if "estado" in df_d else ["Todos"])
        visible_deliveries = df_d if logistics_filter == "Todos" or "estado" not in df_d else df_d[df_d["estado"].astype(str) == logistics_filter]
        delivery_columns = st.columns(3)
        for index, (_, delivery) in enumerate(visible_deliveries.head(12).iterrows()):
            state = str(field(delivery, "estado", "PENDIENTE"))
            with delivery_columns[index % 3]:
                st.markdown(
                    f'<div class="item-card"><span class="status-pill {status_class(state)}">{state.replace("_", " ")}</span>'
                    f'<strong style="display:block;margin-top:11px">{field(delivery, "direccion_destino", "Destino pendiente")}</strong>'
                    f'<div class="item-meta">{field(delivery, "distancia_km", "-")} km de distancia</div>'
                    f'<div class="item-value">{money(field(delivery, "costo_envio_dop", 0))}</div></div>',
                    unsafe_allow_html=True,
                )
                status_options = ["PENDIENTE", "EN_RUTA", "ENTREGADO", "CANCELADO"]
                next_state = st.selectbox(
                    "Estado del pedido",
                    status_options,
                    format_func=lambda value: value.replace("_", " "),
                    index=status_options.index(state) if state in status_options else 0,
                    key=f"delivery_state_{field(delivery, 'id', index)}",
                    on_change=save_delivery_status,
                    args=(field(delivery, "id"), f"delivery_state_{field(delivery, 'id', index)}"),
                    label_visibility="collapsed",
                )
                destination = field(delivery, "direccion_destino", "")
                latitude = field(delivery, "destino_lat", None)
                longitude = field(delivery, "destino_lng", None)
                if latitude is not None and longitude is not None:
                    maps_url = f"https://www.openstreetmap.org/?mlat={latitude}&mlon={longitude}#map=17/{latitude}/{longitude}"
                else:
                    query = f"{destination}, {field(delivery, 'sector', 'Santo Domingo')}, República Dominicana"
                    maps_url = f"https://www.openstreetmap.org/search?query={requests.utils.quote(str(query))}"
                st.markdown(f'<a class="map-link" href="{maps_url}" target="_blank">Vista mapa</a>', unsafe_allow_html=True)
        if visible_deliveries.empty:
            st.info("No hay entregas en este estado.")
    else:
        st.info("Todavía no hay entregas programadas.")

# --- VISTA 5: WEBHOOKS N8N ---
elif menu == "Webhooks n8n":
    st.markdown('<div class="brand-kicker">Connected commerce</div><h1 class="brand-title">Actividad omnicanal</h1><div class="brand-copy">Pedidos y mensajes que llegan desde los canales de Apex.</div>', unsafe_allow_html=True)
    evs = supabase.table("n8n_eventos_omnicanal").select("*").execute().data or []
    if evs:
        events = pd.DataFrame(evs)
        event_date_column = next((column for column in ["creado_en", "created_at", "fecha", "timestamp"] if column in events.columns), None)
        if event_date_column:
            events = events.sort_values(event_date_column, ascending=False)
        event_columns = st.columns(3)
        for index, (_, event) in enumerate(events.head(12).iterrows()):
            state = str(field(event, "estado_procesamiento", "RECIBIDO"))
            with event_columns[index % 3]:
                st.markdown(
                    f'<div class="item-card"><span class="status-pill {status_class(state)}">{state.replace("_", " ")}</span>'
                    f'<strong style="display:block;margin-top:11px">{field(event, "canal_origen", "Canal externo")}</strong>'
                    f'<div class="item-meta">{field(event, "creado_en", "Fecha pendiente")}</div>'
                    f'<div class="item-value" style="font-size:14px">Evento recibido</div></div>',
                    unsafe_allow_html=True,
                )
    else:
        st.info("Sin eventos encolados.")