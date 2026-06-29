import streamlit as st
import asyncio
import re
import pandas as pd
import altair as alt
import io
import csv
from api_client import ClienteOpenLibrary
from analyzer import AnalizadorBiblioteca

# ==========================================
# CONFIGURACIÓN DE LA INTERFAZ & ESTILOS
# ==========================================
st.set_page_config(
    page_title="Auditoría Bibliográfica | PCyT",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilos inyectados para lograr un acabado moderno y profesional
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');

    html, body, [class*="css"], .stApp {
        font-family: 'Outfit', sans-serif;
    }

    .main-title {
        background: linear-gradient(135deg, #4f46e5 0%, #06b6d4 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 0.2rem;
    }

    .sub-title {
        font-size: 1.1rem;
        color: #6b7280;
        text-align: center;
        margin-bottom: 2rem;
    }

    .kpi-container {
        background: rgba(128, 128, 128, 0.05);
        border: 1px solid rgba(128, 128, 128, 0.15);
        border-radius: 14px;
        padding: 1.25rem;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.02);
        margin-bottom: 1rem;
    }

    .kpi-title {
        font-size: 0.85rem;
        font-weight: 600;
        color: #4f46e5;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .kpi-value {
        font-size: 2.2rem;
        font-weight: 700;
        margin-top: 0.2rem;
    }

    .section-border {
        font-size: 1.3rem;
        font-weight: 600;
        border-left: 4px solid #4f46e5;
        padding-left: 0.75rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)


# Helper para la lógica de sanitización de nombres de archivo
def sanear_nombre_reporte(tematica: str) -> str:
    saneado = re.sub(r"[^\w\s-]", "", tematica).strip().lower()
    saneado = re.sub(r"[-\s]+", "_", saneado)
    return f"reporte_{saneado}.csv"


# ==========================================
# MARQUESINA PRINCIPAL
# ==========================================
st.markdown("<h1 class='main-title'>Analizador Crítico de Literatura Científica</h1>", unsafe_allow_html=True)
st.markdown(
    "<p class='sub-title'>Auditoría automatizada de obsolescencia tecnológica y sesgo idiomático en tiempo real</p>",
    unsafe_allow_html=True)

# Inicialización segura del estado de la sesión
if "analizador" not in st.session_state:
    st.session_state.analizador = None
if "tematica_activa" not in st.session_state:
    st.session_state.tematica_activa = ""

# ==========================================
# PANEL DE CONTROL DE INGESTA
# ==========================================
with st.container():
    col_term, col_size = st.columns([3, 1])
    with col_term:
        tematica_input = st.text_input(
            "Término técnico de investigación:",
            placeholder="Ej: 'quantum computing', 'compiler design', 'distributed systems'...",
            value=st.session_state.tematica_activa
        ).strip()
    with col_size:
        limite_input = st.slider("Tamaño de muestra a evaluar:", min_value=20, max_value=150, value=100, step=10)

    col_btn, _ = st.columns([1, 3])
    with col_btn:
        disparar_auditoria = st.button("🔬 Iniciar Auditoría", type="primary", use_container_width=True)

# Procesamiento lógico acoplado a la API
if disparar_auditoria:
    if not tematica_input:
        st.warning("Por favor, introduzca una temática válida para consultar.")
    else:
        st.session_state.tematica_activa = tematica_input
        with st.spinner(f"Ejecutando peticiones cooperativas asíncronas para '{tematica_input}'..."):
            cliente = ClienteOpenLibrary()
            libros_recuperados = asyncio.run(cliente.buscar_libros_async(tematica_input, limit=limite_input))

            if not libros_recuperados:
                st.error("No se obtuvieron registros válidos. Revise la consola o intente otro término técnico.")
                st.session_state.analizador = None
            else:
                st.session_state.analizador = AnalizadorBiblioteca(libros_recuperados)
                st.success(
                    f"Análisis completado. Se validaron e indexaron {len(libros_recuperados)} obras de forma defensiva.")

# ==========================================
# DESPLIEGUE DEL DASHBOARD ANALÍTICO
# ==========================================
if st.session_state.analizador:
    analizador = st.session_state.analizador
    total_muestra = len(analizador.lista_libros)
    idiomas_stats = analizador.obtener_porcentajes_idiomas()
    promedio_ediciones = analizador.calcular_promedio_ediciones()
    brecha_linguistica = idiomas_stats["ingles"] - idiomas_stats["espanol"]

    # Fila Superior de Impacto Visual (KPI Cards en una sola línea de f-string)
    st.markdown("<div class='section-border'>Métricas Globales de Diagnóstico</div>", unsafe_allow_html=True)
    kpi_col1, kpi_col2, kpi_col3 = st.columns(3)

    with kpi_col1:
        st.markdown(
            f"<div class='kpi-container'><div class='kpi-title'>Muestra Auditada</div><div class='kpi-value'>{total_muestra}</div><small style='color:#6b7280;'>Registros libres de corrupción</small></div>",
            unsafe_allow_html=True)
    with kpi_col2:
        st.markdown(
            f"<div class='kpi-container'><div class='kpi-title'>Promedio de Ediciones</div><div class='kpi-value'>{promedio_ediciones:.2f}</div><small style='color:#6b7280;'>Reimpresiones por volumen</small></div>",
            unsafe_allow_html=True)
    with kpi_col3:
        color_alerta = "#f43f5e" if brecha_linguistica > 40 else "#f59e0b"
        st.markdown(
            f"<div class='kpi-container'><div class='kpi-title' style='color:{color_alerta};'>Desventaja Idiomática</div><div class='kpi-value' style='color:{color_alerta};'>{brecha_linguistica:.1f}%</div><small style='color:#6b7280;'>Brecha de acceso directo (EN vs ES)</small></div>",
            unsafe_allow_html=True)

    # Organización Multi pestaña para aislar secciones analíticas
    tab_graficos, tab_clasicos, tab_datos = st.tabs([
        "📊 Diagnósticos Críticos",
        "🏆 Clásicos de Referencia",
        "🗂️ Registro Crudo de Ingesta"
    ])

    with tab_graficos:
        col_g1, col_g2 = st.columns(2)

        with col_g1:
            st.markdown("<div class='section-border'>Métrica A: Índice de Vigencia Temporal</div>",
                        unsafe_allow_html=True)
            vol_pre_2000 = len(analizador.filtrar_por_decada(1900, 1999))
            vol_2000_2009 = len(analizador.filtrar_por_decada(2000, 2009))
            vol_2010_2019 = len(analizador.filtrar_por_decada(2010, 2019))
            vol_2020_pres = len(analizador.filtrar_por_decada(2020, 2030))

            df_decadas = pd.DataFrame({
                "Rango Temporal": ["Anteriores (<2000)", "Años 2000-2009", "Años 2010-2019", "Vanguardia (>=2020)"],
                "Volumen de Obras": [vol_pre_2000, vol_2000_2009, vol_2010_2019, vol_2020_pres]
            })

            grafico_barras = alt.Chart(df_decadas).mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6).encode(
                x=alt.X("Rango Temporal:O", sort=None, title=None),
                y=alt.Y("Volumen de Obras:Q", title="Cantidad de Textos"),
                color=alt.Color("Rango Temporal:N", scale=alt.Scale(range=["#c084fc", "#818cf8", "#60a5fa", "#2dd4bf"]),
                                legend=None),
                tooltip=["Rango Temporal", "Volumen de Obras"]
            ).properties(height=300)

            st.altair_chart(grafico_barras, use_container_width=True)
            st.caption("Visualiza el ritmo de envejecimiento y obsolescencia de los textos disponibles.")

        with col_g2:
            st.markdown("<div class='section-border'>Métrica B: Brecha Lingüística Real</div>", unsafe_allow_html=True)
            df_idiomas = pd.DataFrame({
                "Idioma Evaluado": ["Inglés (eng)", "Español (spa)"],
                "Disponibilidad Porcentual (%)": [idiomas_stats["ingles"], idiomas_stats["espanol"]]
            })

            grafico_idiomas = alt.Chart(df_idiomas).mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6).encode(
                x=alt.X("Idioma Evaluado:O", title=None),
                y=alt.Y("Disponibilidad Porcentual (%):Q", scale=alt.Scale(domain=[0, 100])),
                color=alt.Color("Idioma Evaluado:N", scale=alt.Scale(range=["#4f46e5", "#f43f5e"]), legend=None),
                tooltip=["Idioma Evaluado", "Disponibilidad Porcentual (%)"]
            ).properties(height=300)

            st.altair_chart(grafico_idiomas, use_container_width=True)
            st.caption(
                "Muestra la asimetría de publicación técnica a la que se enfrentan investigadores de habla hispana.")

    with tab_clasicos:
        st.markdown("<div class='section-border'>Métrica C: Obras con Mayor Historial de Reedición</div>",
                    unsafe_allow_html=True)
        obras_clasicas = analizador.obtener_clasicos(5)

        lista_tabla_clasicos = []
        for rango, libro in enumerate(obras_clasicas, 1):
            lista_tabla_clasicos.append({
                "Puesto": f"🏆 {rango}",
                "Título de la Obra": libro.titulo,
                "Cuerpo de Autores": libro.autores,
                "Año Publicación": libro.anio if libro.anio > 0 else "N/D",
                "Cantidad de Ediciones": libro.cant_ediciones,
                "Ficha Técnica": f"https://openlibrary.org{libro.id_crudo}"
            })

        df_clasicos = pd.DataFrame(lista_tabla_clasicos)

        st.data_editor(
            df_clasicos,
            use_container_width=True,
            hide_index=True,
            disabled=True,
            column_config={
                "Ficha Técnica": st.column_config.LinkColumn(
                    "Ficha Técnica ↗",
                    display_text="Ver en Open Library 📖",
                    help="Abre la ficha técnica oficial y el registro analítico en Open Library"
                )
            }
        )
        st.info(
            "Nota: Estas obras representan núcleos bibliográficos sólidos cuya relevancia se mantiene vigente a pesar de la volatilidad del área.")

    with tab_datos:
        st.markdown("<div class='section-border'>Muestra Integral de Datos Normalizados</div>", unsafe_allow_html=True)

        dataset_completo = [{
            "ID Sanitizado": l.id_limpio,
            "Título Completo": l.titulo,
            "Autores": l.autores,
            "Año Original": l.anio if l.anio > 0 else "N/D",
            "Volumen Ediciones": l.cant_ediciones,
            "Idiomas Mapeados": ", ".join(l.idiomas) if l.idiomas else "N/D",
            "Acceso Web": f"https://openlibrary.org{l.id_crudo}"
        } for l in analizador.lista_libros]

        df_completo = pd.DataFrame(dataset_completo)

        st.data_editor(
            df_completo,
            use_container_width=True,
            hide_index=True,
            disabled=True,
            column_config={
                "Acceso Web": st.column_config.LinkColumn(
                    "Acceso Web ↗",
                    display_text="Abrir Obra 🌐",
                    help="Direcciona directamente al perfil del libro en internet"
                )
            }
        )

        st.markdown("---")
        nombre_csv_reporte = sanear_nombre_reporte(st.session_state.tematica_activa)

        output_stream = io.StringIO()
        escritor_csv = csv.writer(output_stream, delimiter=";")
        escritor_csv.writerow(["ID Limpio", "Titulo", "Autores", "Anio Publicacion", "Ediciones", "Idiomas"])
        for l in analizador.lista_libros:
            escritor_csv.writerow([l.id_limpio, l.titulo, l.autores, l.anio if l.anio > 0 else "N/D", l.cant_ediciones,
                                   ", ".join(l.idiomas)])

        st.download_button(
            label="📥 Descargar Diagnóstico como CSV",
            data=output_stream.getvalue().encode("utf-8"),
            file_name=nombre_csv_reporte,
            mime="text/csv",
            use_container_width=True
        )
else:
    st.info(
        "Indique un tópico científico en el control de mando superior y ejecute la auditoría para inicializar los motores estadísticos.")