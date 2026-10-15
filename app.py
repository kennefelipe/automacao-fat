import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime, date
import json
import os

# ---------------------------------------------------------------------------
# Configuracao da pagina
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Automacao Faturamento",
    page_icon="⚡",
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
    # "Colaborador 01": [],  # Preencher com as zonas
    # "Colaborador 02": [],  # Preencher com as zonas
    # "Colaborador 03": [],  # Preencher com as zonas
    # "Colaborador 04": [],  # Preencher com as zonas
    # "Colaborador 05": [],  # Preencher com as zonas
    # "Colaborador 06": [],  # Preencher com as zonas
    # "Colaborador 07": [],  # Preencher com as zonas
    # "Colaborador 08": [],  # Preencher com as zonas
    # "Colaborador 09": [],  # Preencher com as zonas
    # "Colaborador 10": [],  # Preencher com as zonas
    # "Colaborador 11": [],  # Preencher com as zonas
    # "Colaborador 12": [],  # Preencher com as zonas
    # "Colaborador 13": [],  # Preencher com as zonas
    # "Colaborador 14": [],  # Preencher com as zonas
    # "Colaborador 15": [],  # Preencher com as zonas
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
# Quantidade por tipo de servico
# ---------------------------------------------------------------------------
col_chart, col_download = st.columns([3, 2])

with col_chart:
    st.markdown('<div class="section-title">Quantidade por Tipo de Servico</div>', unsafe_allow_html=True)
    tipo_counts = df["Tipo de Solicitação"].value_counts()
    for tipo, count in tipo_counts.items():
        pct = (count / total_os) * 100
        st.markdown(f"""
        <div class="service-bar">
            <span class="service-name">{tipo}</span>
            <span class="service-count">{count} <span style="font-size:11px; color: rgba(255,255,255,0.4);">({pct:.1f}%)</span></span>
        </div>
        """, unsafe_allow_html=True)

with col_download:
    st.markdown('<div class="section-title">Baixar Relatorio por Colaborador</div>', unsafe_allow_html=True)

    if not COLABORADORES_ZONAS:
        st.info("Configure os colaboradores e suas zonas no codigo para habilitar a distribuicao.")
    else:
        colab_names = list(COLABORADORES_ZONAS.keys())
        selected_colab = st.selectbox("Selecione seu nome", colab_names, key="colab_select")

        if selected_colab and selected_colab in distribution:
            df_colab = distribution[selected_colab]
            st.markdown(f"""
            <div style="background: rgba(19,29,53,0.6); border-radius: 8px; padding: 12px;
                        border: 1px solid rgba(255,255,255,0.06); margin: 8px 0;">
                <span style="color: rgba(255,255,255,0.5); font-size: 12px;">OS atribuidas:</span>
                <span style="color: #00C896; font-size: 20px; font-weight: 700; margin-left: 8px;">{len(df_colab)}</span>
            </div>
            """, unsafe_allow_html=True)

            if not df_colab.empty:
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

# ---------------------------------------------------------------------------
# Distribuicao por colaborador (resumo)
# ---------------------------------------------------------------------------
if distribution:
    st.markdown("<div style='height: 20px'></div>", unsafe_allow_html=True)
    st.markdown('<div class="section-title">Distribuicao por Colaborador</div>', unsafe_allow_html=True)

    cols_per_row = 5
    colab_items = [(k, v) for k, v in distribution.items()]

    for i in range(0, len(colab_items), cols_per_row):
        cols = st.columns(cols_per_row)
        for j, col in enumerate(cols):
            idx = i + j
            if idx < len(colab_items):
                name, df_c = colab_items[idx]
                with col:
                    st.markdown(render_metric_card(
                        "📄", str(len(df_c)),
                        name, "card-dark"
                    ), unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# OS por dia (grafico)
# ---------------------------------------------------------------------------
st.markdown("<div style='height: 20px'></div>", unsafe_allow_html=True)
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
