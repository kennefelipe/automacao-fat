import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime, date
from PIL import Image
import json
import os

icone = image.open ("logo-corsan.png")
# ---------------------------------------------------------------------------
# Configuracao da pagina
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Distribuição Ordens de Serviço",
    page_icon= (icone),
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
AUDIT_FILE = "audit_log.json"
ABSENCE_FILE = "absence_config.json"
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# CSS customizado - design escuro com gradiente azul
# ---------------------------------------------------------------------------
st.markdown("""
<style>
    /* Fundo principal */
    .stApp {
        background: linear-gradient(135deg, #0A1628 0%, #0F2044 50%, #0A1628 100%);
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0D1B2E 0%, #162D50 100%);
        border-right: 1px solid rgba(255,255,255,0.05);
    }

    /* Cards de metricas */
    .metric-card {
        border-radius: 16px;
        padding: 24px 28px;
        text-align: left;
        position: relative;
        overflow: hidden;
        min-height: 130px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .metric-card .metric-icon {
        position: absolute;
        top: 16px;
        left: 20px;
        width: 44px;
        height: 44px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
    }
    .metric-card .metric-value {
        font-size: 42px;
        font-weight: 800;
        line-height: 1;
        margin-top: 40px;
    }
    .metric-card .metric-label {
        font-size: 13px;
        margin-top: 6px;
        opacity: 0.85;
        line-height: 1.3;
    }

    /* Card laranja */
    .card-orange {
        background: linear-gradient(135deg, #FF9A2E 0%, #FFB347 100%);
        color: #1a1a1a;
    }
    .card-orange .metric-icon {
        background: rgba(255,255,255,0.3);
        color: #1a1a1a;
    }

    /* Card ciano */
    .card-cyan {
        background: linear-gradient(135deg, #00D4AA 0%, #4DE8C8 100%);
        color: #1a1a1a;
    }
    .card-cyan .metric-icon {
        background: rgba(255,255,255,0.3);
        color: #1a1a1a;
    }

    /* Card branco */
    .card-white {
        background: linear-gradient(135deg, #E8EDF5 0%, #FFFFFF 100%);
        color: #1a1a1a;
    }
    .card-white .metric-icon {
        background: rgba(0,150,100,0.15);
        color: #00966A;
    }

    /* Card azul escuro */
    .card-dark {
        background: linear-gradient(135deg, #1A2D4A 0%, #243B5C 100%);
        color: #FFFFFF;
        border: 1px solid rgba(255,255,255,0.08);
    }
    .card-dark .metric-icon {
        background: rgba(0,200,150,0.15);
        color: #00C896;
    }

    /* Card vermelho */
    .card-red {
        background: linear-gradient(135deg, #FF4D4D 0%, #FF6B6B 100%);
        color: #FFFFFF;
    }
    .card-red .metric-icon {
        background: rgba(255,255,255,0.25);
        color: #FFFFFF;
    }

    /* Tabela customizada */
    .data-table {
        background: rgba(19, 29, 53, 0.8);
        border-radius: 12px;
        padding: 20px;
        border: 1px solid rgba(255,255,255,0.06);
    }

    /* Titulo da secao */
    .section-title {
        color: #FFFFFF;
        font-size: 16px;
        font-weight: 600;
        margin-bottom: 16px;
        padding-bottom: 8px;
        border-bottom: 1px solid rgba(255,255,255,0.08);
    }

    /* Header */
    .main-header {
        padding: 0 0 8px 0;
    }
    .main-header .subtitle {
        color: rgba(255,255,255,0.5);
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 3px;
        margin-bottom: 4px;
    }
    .main-header h1 {
        color: #FFFFFF;
        font-size: 36px;
        font-weight: 800;
        margin: 0;
    }

    /* Esconder decoracao streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header[data-testid="stHeader"] {background: transparent;}

    /* Barra de servicos */
    .service-bar {
        background: rgba(19, 29, 53, 0.6);
        border-radius: 8px;
        padding: 10px 16px;
        margin: 4px 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border: 1px solid rgba(255,255,255,0.04);
    }
    .service-bar .service-name {
        color: #FFFFFF;
        font-size: 13px;
        font-weight: 500;
    }
    .service-bar .service-count {
        color: #00C896;
        font-size: 16px;
        font-weight: 700;
    }

    /* Badges */
    .badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 600;
    }
    .badge-success { background: rgba(0,200,150,0.15); color: #00C896; }
    .badge-warning { background: rgba(255,154,46,0.15); color: #FF9A2E; }
    .badge-danger { background: rgba(255,77,77,0.15); color: #FF4D4D; }

    /* Streamlit elements */
    .stSelectbox label, .stFileUploader label, .stMultiSelect label {
        color: rgba(255,255,255,0.7) !important;
    }
    div[data-testid="stMetric"] {
        background: rgba(19, 29, 53, 0.6);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 12px;
        padding: 16px;
    }
    .stDownloadButton > button {
        background: linear-gradient(135deg, #00C896 0%, #00A87A 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 8px 24px !important;
    }
    .stDownloadButton > button:hover {
        background: linear-gradient(135deg, #00A87A 0%, #008B64 100%) !important;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        background: rgba(19, 29, 53, 0.6);
        border-radius: 8px;
        color: rgba(255,255,255,0.6);
        border: 1px solid rgba(255,255,255,0.06);
        padding: 8px 20px;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #00C896 0%, #00A87A 100%) !important;
        color: #FFFFFF !important;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# MAPEAMENTO DE ZONAS POR COLABORADOR
# Preencha as zonas de cada colaborador abaixo.
# Exemplo: "Nome": [1, 2, 3, 10, 15]
# ---------------------------------------------------------------------------
COLABORADORES_ZONAS = {
    "AMANDA BARCELLOS (AMANDA.BARCELLOS)": [12, 19, 27, 38, 54, 68, 81, 92, 106, 129, 169, 181, 195, 209, 221, 222, 228, 249, 275, 285, 292, 311, 403, 404, 416, 439, 444, 446, 463],
    "CAROLINE DE OLIVEIRA SANTOS (CAROLINE.OSANTOS)": [6, 10, 17, 18, 32, 37, 48, 50, 53, 58, 61, 67, 74, 75, 76, 77, 78, 80, 89, 91, 93, 103, 104, 109, 111, 113, 117, 120, 121, 123, 124, 125, 128, 133, 144, 146, 147, 151, 158, 168, 170, 171, 176, 197, 207, 211, 212, 215, 216, 218, 219, 235, 238, 240, 251, 280, 295, 299, 405, 408, 418, 420, 421, 429, 435, 447, 455, 460, 491, 499],
    "CLEVER FANFA SARMENTO JUNIOR (CLEVER.JUNIOR)": [82, 97],
    "COLABORADOR 1": [8, 11, 15, 21, 23, 24, 35, 43, 47, 49, 66, 72, 83, 84, 85, 86, 87, 90, 95, 98, 108, 118, 131, 135, 136, 137, 139, 140, 141, 150, 161, 167, 175, 193, 200, 205, 214, 223, 237, 262, 270, 276, 289, 297, 412, 413, 419, 425, 445, 449, 451, 458, 465, 498],
    "COLABORADOR 2": [46, 57, 132, 143, 145, 155, 187, 225, 226, 227, 245, 263, 272, 298, 414, 415, 430],
    "ELIANA CATARINA BALOK CHAGAS (ELIANA.CHAGAS)": [7, 96, 210, 294],
    "FELIPE KENNE DE OLIVEIRA (FELIPE.KENNE)": [13, 30, 71, 88, 116, 127, 164, 204, 232, 236, 250, 467, 468, 490],
    "GABRIEL GODOI TEIXEIRA (GABRIEL.GODOI)": [25, 28, 29, 70, 73, 115, 119, 173, 180, 185, 192, 194, 208, 277, 296, 438, 497],
    "HELLEN SCHIMIDT DIAS (HELLEN.DIAS)": [31, 45, 239],
    "IGOR MARTINI RODRIGUES (IGOR.MARTINI)": [5, 110, 122, 162, 191, 279, 433],
    "JULIA DA SILVA FLORES (JULIA.SFLORES)": [2, 4, 22, 26, 33, 36, 39, 40, 42, 51, 52, 55, 59, 60, 62, 63, 65, 79, 94, 99, 101, 102, 105, 107, 130, 148, 154, 159, 160, 163, 174, 177, 182, 186, 188, 189, 190, 199, 201, 202, 213, 220, 224, 229, 230, 231, 233, 241, 242, 256, 257, 261, 286, 293, 409, 411, 426, 432, 441, 442, 443, 452, 461],
    "MAYARA AMARAL DORNELLES (MAYARA.DORNELLES)": [179],
    "PEDRO ARTHUR ALVES DE FREITAS (PEDRO.FFREITAS)": [9, 14, 34, 44, 56, 64, 69, 100, 114, 152, 153, 156, 157, 165, 184, 196, 198, 258, 281, 283, 423, 466],
    "PRISCILA DA SILVA LIMA (PRISCILA.LIMA)": [1, 20, 41, 138, 149, 166, 178, 206, 217, 248, 269, 284, 406, 410, 422],
}

# ---------------------------------------------------------------------------
# Credenciais ADM
# ---------------------------------------------------------------------------
ADMIN_USER = "admin"
ADMIN_PASS = "fat2026"

# ---------------------------------------------------------------------------
# Funcoes auxiliares
# ---------------------------------------------------------------------------

def load_audit_log():
    if os.path.exists(AUDIT_FILE):
        with open(AUDIT_FILE, "r") as f:
            return json.load(f)
    return []


def save_audit_log(log):
    with open(AUDIT_FILE, "w") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)


def add_audit_entry(colaborador, action="download"):
    log = load_audit_log()
    log.append({
        "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "colaborador": colaborador,
        "action": action,
    })
    save_audit_log(log)


def load_absence_config():
    if os.path.exists(ABSENCE_FILE):
        with open(ABSENCE_FILE, "r") as f:
            return json.load(f)
    return {}


def save_absence_config(config):
    with open(ABSENCE_FILE, "w") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


def distribute_os(df):
    """Distribui as OS por colaborador baseado na zona."""
    if not COLABORADORES_ZONAS:
        st.warning("Nenhum colaborador cadastrado. Preencha o dicionario COLABORADORES_ZONAS no codigo.")
        return {}

    absence = load_absence_config()
    active_collabs = {}
    absent_collabs = {}

    for colab, zonas in COLABORADORES_ZONAS.items():
        if colab in absence:
            absent_collabs[colab] = {
                "zonas": zonas,
                "redirect_to": absence[colab].get("redirect_to"),
                "distribute_all": absence[colab].get("distribute_all", False),
            }
        else:
            active_collabs[colab] = zonas

    distribution = {colab: pd.DataFrame() for colab in active_collabs}

    for colab, zonas in active_collabs.items():
        mask = df["Zona Ligacao"].isin(zonas)
        distribution[colab] = pd.concat([distribution[colab], df[mask]])

    for colab, info in absent_collabs.items():
        zonas_ausente = info["zonas"]
        os_ausente = df[df["Zona Ligacao"].isin(zonas_ausente)]

        if os_ausente.empty:
            continue

        if info.get("redirect_to") and info["redirect_to"] in active_collabs:
            target = info["redirect_to"]
            distribution[target] = pd.concat([distribution[target], os_ausente])
        elif info.get("distribute_all"):
            active_list = list(active_collabs.keys())
            if active_list:
                chunks = [os_ausente.iloc[i::len(active_list)] for i in range(len(active_list))]
                for idx, ac in enumerate(active_list):
                    if idx < len(chunks):
                        distribution[ac] = pd.concat([distribution[ac], chunks[idx]])

    for colab in distribution:
        distribution[colab] = distribution[colab].drop_duplicates(subset=["Nº da Solicitação"])

    return distribution


def to_excel_download(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="OS")
        worksheet = writer.sheets["OS"]
        for i, col in enumerate(df.columns):
            max_len = max(df[col].astype(str).map(len).max(), len(col)) + 2
            max_len = min(max_len, 50)
            worksheet.set_column(i, i, max_len)
    return output.getvalue()


def render_metric_card(icon, value, label, card_class):
    return f"""
    <div class="metric-card {card_class}">
        <div class="metric-icon">{icon}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-label">{label}</div>
    </div>
    """


# ---------------------------------------------------------------------------
# Estado da sessao
# ---------------------------------------------------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False
if "df_loaded" not in st.session_state:
    st.session_state.df_loaded = None

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 20px 0 10px 0;">
        <div style="font-size: 28px; font-weight: 800; color: #00C896;">
            FATURAMENTO
        </div>
        <div style="font-size: 11px; color: rgba(255,255,255,0.4); letter-spacing: 2px;">
            AUTOMACAO
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Login ADM
    if not st.session_state.is_admin:
        with st.expander("Login ADM", expanded=False):
            user_input = st.text_input("Usuario", key="adm_user")
            pass_input = st.text_input("Senha", type="password", key="adm_pass")
            if st.button("Entrar", key="btn_login", use_container_width=True):
                if user_input == ADMIN_USER and pass_input == ADMIN_PASS:
                    st.session_state.is_admin = True
                    st.rerun()
                else:
                    st.error("Credenciais invalidas")
    else:
        st.markdown("""
        <div style="background: rgba(0,200,150,0.1); border: 1px solid rgba(0,200,150,0.3);
                    border-radius: 8px; padding: 10px; text-align: center; margin-bottom: 10px;">
            <span style="color: #00C896; font-weight: 600;">ADM Conectado</span>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Sair", key="btn_logout", use_container_width=True):
            st.session_state.is_admin = False
            st.rerun()

    st.markdown("---")

    # Upload do arquivo
    st.markdown('<p style="color: rgba(255,255,255,0.6); font-size: 12px; text-transform: uppercase; letter-spacing: 1px;">Carregar Extracao SCAE</p>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("", type=["xlsx", "xls"], key="file_upload", label_visibility="collapsed")

    if uploaded_file is not None:
        try:
            df = pd.read_excel(uploaded_file)
            df["Data Tramite"] = pd.to_datetime(df["Data Tramite"], errors="coerce")
            df["Data Pedido"] = pd.to_datetime(df["Data Pedido"], errors="coerce")
            st.session_state.df_loaded = df
            st.success(f"{len(df)} registros carregados")
        except Exception as e:
            st.error(f"Erro ao carregar: {e}")

    st.markdown("---")
    st.markdown(f"""
    <div style="text-align: center; color: rgba(255,255,255,0.3); font-size: 11px; padding: 10px 0;">
        Atualizado em {datetime.now().strftime("%d/%m/%Y %H:%M")}
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Conteudo principal
# ---------------------------------------------------------------------------
df = st.session_state.df_loaded

if df is None:
    st.markdown("""
    <div style="display: flex; flex-direction: column; align-items: center; justify-content: center;
                min-height: 60vh; text-align: center;">
        <div style="font-size: 64px; margin-bottom: 20px; opacity: 0.3;">📂</div>
        <h2 style="color: rgba(255,255,255,0.6); font-weight: 400;">Nenhum arquivo carregado</h2>
        <p style="color: rgba(255,255,255,0.3); max-width: 400px;">
            Faca o upload da extracao do SCAE na barra lateral para iniciar a distribuicao das ordens de servico.
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ---------------------------------------------------------------------------
# Calculos principais
# ---------------------------------------------------------------------------
total_os = len(df)
os_por_dia = df.groupby(df["Data Tramite"].dt.date).size()
dia_mais_antigo = os_por_dia.index.min() if not os_por_dia.empty else date.today()
qtd_dia_antigo = os_por_dia.get(dia_mais_antigo, 0)
dias_atraso = (date.today() - dia_mais_antigo).days if dia_mais_antigo else 0
total_colaboradores_ativos = len([c for c in COLABORADORES_ZONAS if c not in load_absence_config()])

distribution = distribute_os(df)

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.markdown("""
<div class="main-header">
    <div class="subtitle">FATURAMENTO</div>
    <h1>Distribuicao de OS</h1>
</div>
""", unsafe_allow_html=True)

st.markdown("<div style='height: 8px'></div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Metricas principais
# ---------------------------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(render_metric_card(
        "📋", f"{total_os:,}".replace(",", "."),
        "Total de OS em aberto", "card-orange"
    ), unsafe_allow_html=True)

with col2:
    dia_fmt = dia_mais_antigo.strftime("%d/%m") if dia_mais_antigo else "--"
    st.markdown(render_metric_card(
        "📅", dia_fmt,
        f"Dia mais atrasado ({qtd_dia_antigo} OS)", "card-cyan"
    ), unsafe_allow_html=True)

with col3:
    st.markdown(render_metric_card(
        "⏳", f"{dias_atraso}",
        "Dias de atraso", "card-red"
    ), unsafe_allow_html=True)

with col4:
    st.markdown(render_metric_card(
        "👥", f"{total_colaboradores_ativos}",
        f"Colaboradores presentes (de {len(COLABORADORES_ZONAS)})", "card-white"
    ), unsafe_allow_html=True)

st.markdown("<div style='height: 20px'></div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Quantidade por tipo de servico - Grafico de barras horizontal amarelo
# ---------------------------------------------------------------------------
st.markdown('<div class="section-title">Quantidade por Tipo de Servico</div>', unsafe_allow_html=True)

tipo_counts = df["Tipo de Solicitação"].value_counts()
max_count = tipo_counts.max() if not tipo_counts.empty else 1

for tipo, count in tipo_counts.items():
    pct = (count / total_os) * 100
    bar_width = (count / max_count) * 100
    st.markdown(f"""
    <div style="margin-bottom: 10px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
            <span style="color: rgba(255,255,255,0.85); font-size: 13px; font-weight: 500;">{tipo}</span>
            <span style="color: #FFB347; font-size: 14px; font-weight: 700;">{count} <span style="font-size:11px; color: rgba(255,255,255,0.4);">({pct:.1f}%)</span></span>
        </div>
        <div style="background: rgba(255,255,255,0.06); border-radius: 6px; height: 28px; overflow: hidden;">
            <div style="background: linear-gradient(90deg, #FF9A2E, #FFB347); width: {bar_width}%;
                        height: 100%; border-radius: 6px; transition: width 0.5s ease;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height: 24px'></div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Detalhamento por colaborador - Selecao + Tabela + Download
# ---------------------------------------------------------------------------
st.markdown('<div class="section-title">Detalhamento por Colaborador</div>', unsafe_allow_html=True)

if not COLABORADORES_ZONAS:
    st.info("Configure os colaboradores e suas zonas no codigo para habilitar a distribuicao.")
else:
    colab_names = list(COLABORADORES_ZONAS.keys())
    selected_colab = st.selectbox("Selecione seu nome", colab_names, key="colab_select")

    if selected_colab and selected_colab in distribution:
        df_colab = distribution[selected_colab]

        col_info1, col_info2, col_info3 = st.columns(3)
        with col_info1:
            st.markdown(render_metric_card(
                "📄", str(len(df_colab)),
                "OS atribuidas", "card-orange"
            ), unsafe_allow_html=True)
        with col_info2:
            zonas_colab = COLABORADORES_ZONAS.get(selected_colab, [])
            st.markdown(render_metric_card(
                "📍", str(len(zonas_colab)),
                "Zonas responsavel", "card-cyan"
            ), unsafe_allow_html=True)
        with col_info3:
            tipos_colab = df_colab["Tipo de Solicitação"].nunique() if not df_colab.empty else 0
            st.markdown(render_metric_card(
                "📋", str(tipos_colab),
                "Tipos de servico", "card-dark"
            ), unsafe_allow_html=True)

        st.markdown("<div style='height: 12px'></div>", unsafe_allow_html=True)

        if not df_colab.empty:
            display_cols = [
                "Nº da Solicitação", "Nº Ligação", "Zona Ligacao",
                "Tipo de Solicitação", "Data Tramite", "Data Pedido",
            ]
            available_cols = [c for c in display_cols if c in df_colab.columns]
            df_display = df_colab[available_cols].copy()
            df_display = df_display.sort_values("Data Tramite", ascending=True)

            for col in ["Data Tramite", "Data Pedido"]:
                if col in df_display.columns:
                    df_display[col] = df_display[col].dt.strftime("%d/%m/%Y %H:%M")

            st.dataframe(
                df_display,
                use_container_width=True,
                height=min(400, 38 + len(df_display) * 35),
                hide_index=True,
            )

            st.markdown("<div style='height: 8px'></div>", unsafe_allow_html=True)

            excel_data = to_excel_download(df_colab)
            downloaded = st.download_button(
                label=f"Baixar Excel - {selected_colab}",
                data=excel_data,
                file_name=f"OS_{selected_colab.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="btn_download_colab",
                use_container_width=True,
            )
            if downloaded:
                add_audit_entry(selected_colab, "download")
        else:
            st.info("Nenhuma OS atribuida para este colaborador.")
    elif selected_colab:
        absence = load_absence_config()
        if selected_colab in absence:
            st.warning(f"{selected_colab} esta ausente. OS redistribuidas.")

st.markdown("<div style='height: 24px'></div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# OS por dia (grafico)
# ---------------------------------------------------------------------------
st.markdown('<div class="section-title">OS por Dia (Data Tramite)</div>', unsafe_allow_html=True)

os_dia_df = os_por_dia.reset_index()
os_dia_df.columns = ["Data", "Quantidade"]
os_dia_df = os_dia_df.sort_values("Data")
st.bar_chart(os_dia_df.set_index("Data"), color="#00C896", height=300)


# ===========================================================================
# PAINEL ADMINISTRATIVO
# ===========================================================================
if st.session_state.is_admin:
    st.markdown("<div style='height: 30px'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(0,200,150,0.08) 0%, rgba(0,100,80,0.08) 100%);
                border: 1px solid rgba(0,200,150,0.2); border-radius: 12px; padding: 16px 20px; margin-bottom: 16px;">
        <span style="color: #00C896; font-size: 18px; font-weight: 700;">Painel Administrativo</span>
        <span style="color: rgba(255,255,255,0.4); font-size: 12px; margin-left: 12px;">Acesso restrito</span>
    </div>
    """, unsafe_allow_html=True)

    tab_absence, tab_audit = st.tabs(["Cobertura de Ausencias", "Historico / Auditoria"])

    # -----------------------------------------------------------------------
    # Tab: Cobertura de Ausencias
    # -----------------------------------------------------------------------
    with tab_absence:
        st.markdown("Selecione o colaborador ausente e defina o redirecionamento das OS.")

        if not COLABORADORES_ZONAS:
            st.info("Configure os colaboradores primeiro.")
        else:
            absence = load_absence_config()
            all_collabs = list(COLABORADORES_ZONAS.keys())

            col_a1, col_a2 = st.columns(2)

            with col_a1:
                st.markdown("**Registrar Ausencia**")
                absent_colab = st.selectbox("Colaborador ausente", all_collabs, key="absent_select")
                redirect_mode = st.radio(
                    "Redirecionamento",
                    ["Redirecionar para colega especifico", "Distribuir para todos"],
                    key="redirect_mode",
                )

                target_colab = None
                if redirect_mode == "Redirecionar para colega especifico":
                    available = [c for c in all_collabs if c != absent_colab]
                    target_colab = st.selectbox("Redirecionar para", available, key="target_select")

                if st.button("Confirmar Ausencia", key="btn_confirm_absence", use_container_width=True):
                    config = {
                        "redirect_to": target_colab if redirect_mode == "Redirecionar para colega especifico" else None,
                        "distribute_all": redirect_mode == "Distribuir para todos",
                        "registered_at": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                    }
                    absence[absent_colab] = config
                    save_absence_config(absence)
                    add_audit_entry(absent_colab, f"ausencia_registrada -> {target_colab or 'todos'}")
                    st.success(f"Ausencia de {absent_colab} registrada!")
                    st.rerun()

            with col_a2:
                st.markdown("**Ausencias Ativas**")
                if absence:
                    for colab, info in absence.items():
                        dest = info.get("redirect_to", "Todos")
                        if info.get("distribute_all"):
                            dest = "Distribuido para todos"
                        registered = info.get("registered_at", "")

                        st.markdown(f"""
                        <div style="background: rgba(255,77,77,0.08); border: 1px solid rgba(255,77,77,0.2);
                                    border-radius: 8px; padding: 12px; margin-bottom: 8px;">
                            <div style="color: #FF6B6B; font-weight: 600;">{colab}</div>
                            <div style="color: rgba(255,255,255,0.5); font-size: 12px;">
                                Redirecionado para: {dest}<br>
                                Registrado em: {registered}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                    st.markdown("")
                    remove_colab = st.selectbox("Remover ausencia de", list(absence.keys()), key="remove_abs")
                    if st.button("Remover Ausencia", key="btn_remove_absence", use_container_width=True):
                        del absence[remove_colab]
                        save_absence_config(absence)
                        add_audit_entry(remove_colab, "ausencia_removida")
                        st.success(f"Ausencia de {remove_colab} removida!")
                        st.rerun()
                else:
                    st.info("Nenhuma ausencia registrada.")

    # -----------------------------------------------------------------------
    # Tab: Historico / Auditoria
    # -----------------------------------------------------------------------
    with tab_audit:
        st.markdown("Registro de todas as acoes realizadas no sistema.")

        audit_log = load_audit_log()

        if audit_log:
            audit_df = pd.DataFrame(audit_log)
            audit_df = audit_df.sort_values("timestamp", ascending=False)

            # Filtros
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                filter_colab = st.multiselect(
                    "Filtrar por colaborador",
                    audit_df["colaborador"].unique().tolist(),
                    key="filter_audit_colab",
                )
            with col_f2:
                filter_action = st.multiselect(
                    "Filtrar por acao",
                    audit_df["action"].unique().tolist(),
                    key="filter_audit_action",
                )

            if filter_colab:
                audit_df = audit_df[audit_df["colaborador"].isin(filter_colab)]
            if filter_action:
                audit_df = audit_df[audit_df["action"].isin(filter_action)]

            st.markdown(f"""
            <div style="margin-bottom: 12px; color: rgba(255,255,255,0.5); font-size: 13px;">
                Total de registros: <strong style="color:#00C896">{len(audit_df)}</strong>
            </div>
            """, unsafe_allow_html=True)

            for _, row in audit_df.iterrows():
                action_icon = "📥" if row["action"] == "download" else "🔄"
                action_color = "#00C896" if row["action"] == "download" else "#FF9A2E"
                st.markdown(f"""
                <div style="background: rgba(19,29,53,0.6); border-radius: 8px; padding: 10px 16px;
                            border: 1px solid rgba(255,255,255,0.04); margin-bottom: 6px;
                            display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <span style="margin-right: 8px;">{action_icon}</span>
                        <span style="color: #FFFFFF; font-weight: 500;">{row['colaborador']}</span>
                        <span style="color: {action_color}; font-size: 12px; margin-left: 8px;">{row['action']}</span>
                    </div>
                    <span style="color: rgba(255,255,255,0.4); font-size: 12px;">{row['timestamp']}</span>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<div style='height: 10px'></div>", unsafe_allow_html=True)
            if st.button("Limpar Historico", key="btn_clear_audit"):
                save_audit_log([])
                st.success("Historico limpo!")
                st.rerun()
        else:
            st.info("Nenhum registro de auditoria ainda.")
