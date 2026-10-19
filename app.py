import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from io import BytesIO
from datetime import datetime, date, timezone, timedelta

BR_TZ = timezone(timedelta(hours=-3))
from PIL import Image
import json
import os

icone = Image.open(os.path.join(os.path.dirname(__file__), "logo-corsan-att.png"))
# ---------------------------------------------------------------------------
# Configuracao da pagina
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="ELLO",
    page_icon=icone,
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
    "AMANDA BARCELLOS (AMANDA.BARCELLOS)": [8, 11, 15, 21, 23, 24, 35, 43, 47, 49, 66, 72, 83, 84, 85, 86, 87, 90, 95, 98, 108, 118, 131, 135, 136, 137, 139, 140, 141, 150, 161, 167, 175, 193, 200, 205, 214, 223, 237, 262, 270, 276, 289, 297, 412, 413, 425, 445, 451, 458, 465],
    "CAROLINE DE OLIVEIRA SANTOS (CAROLINE.OSANTOS)": [6, 10, 17, 18, 32, 37, 48, 50, 53, 58, 61, 67, 74, 75, 76, 77, 78, 80, 89, 91, 93, 103, 104, 109, 111, 113, 117, 120, 121, 123, 124, 125, 128, 133, 144, 146, 147, 151, 158, 168, 170, 171, 176, 197, 207, 211, 212, 215, 216, 218, 219, 235, 238, 240, 251, 280, 295, 299, 405, 418, 420, 421, 429, 435, 447, 455, 460, 499],
    "CLEVER FANFA SARMENTO JUNIOR (CLEVER.JUNIOR)": [82, 239],
    "ELIANA CATARINA BALOK CHAGAS (ELIANA.CHAGAS)": [31, 45],
    "FELIPE KENNE DE OLIVEIRA (FELIPE.KENNE)": [9, 14, 34, 44, 56, 64, 69, 100, 114, 152, 153, 156, 157, 165, 184, 196, 198, 258, 281, 283, 423, 466],
    "GABRIEL GODOI TEIXEIRA (GABRIEL.GODOI)": [5, 25, 28, 29, 70, 73, 110, 115, 119, 122, 162, 173, 180, 185, 191, 192, 208, 277, 279, 296, 433, 438, 497],
    "HELLEN SCHIMIDT DIAS (HELLEN.DIAS)": [7, 97],
    "IGOR MARTINI RODRIGUES (IGOR.MARTINI)": [12, 19, 27, 38, 54, 68, 81, 92, 106, 129, 169, 181, 195, 209, 221, 222, 228, 249, 275, 285, 292, 311, 403, 404, 416, 439, 444, 446, 463],
    "JULIA DA SILVA FLORES (JULIA.SFLORES)": [2, 4, 22, 26, 33, 36, 39, 40, 42, 51, 52, 55, 59, 60, 62, 63, 65, 79, 94, 99, 101, 102, 105, 107, 130, 148, 154, 159, 160, 163, 174, 177, 182, 186, 188, 189, 190, 199, 201, 202, 213, 220, 224, 229, 230, 231, 233, 241, 242, 256, 261, 286, 293, 409, 411, 426, 432, 441, 442, 443, 461],
    "MAYARA AMARAL DORNELLES (MAYARA.DORNELLES)": [46, 57, 132, 143, 145, 155, 187, 225, 226, 227, 245, 263, 272, 298, 414, 415, 430],
    "PEDRO ARTHUR ALVES DE FREITAS (PEDRO.FFREITAS)": [96, 210, 294],
    "PRISCILA DA SILVA LIMA (PRISCILA.LIMA)": [1, 13, 20, 30, 41, 71, 88, 116, 127, 138, 149, 164, 166, 178, 179, 204, 206, 217, 232, 236, 248, 250, 269, 284, 406, 410, 422, 467],
}

# ---------------------------------------------------------------------------
# MAPEAMENTO ZONA -> CIDADE
# ---------------------------------------------------------------------------
ZONA_CIDADE = {
    1: "Agudo", 2: "Ajuricaba", 4: "Alecrim", 5: "Alegrete", 6: "Alpestre",
    7: "Alvorada", 8: "Antonio Prado", 9: "Arambare", 10: "Aratiba",
    11: "Arroio do Meio", 12: "Arroio dos Ratos", 13: "Arroio do Tigre",
    14: "Arroio Grande", 15: "Arvorezinha", 17: "Barao de Cotegipe",
    18: "Barracão", 19: "Barra do Ribeiro", 20: "Barros Cassal",
    21: "Bento Goncalves", 22: "Boa Vista do Burica", 23: "Bom Jesus",
    24: "Bom Retiro do Sul", 25: "Bossoroca", 26: "Braga", 27: "Butia",
    28: "Caçapava do Sul", 29: "Cacequi", 30: "Cachoeira do Sul",
    31: "Cachoeirinha", 32: "Cacique Doble", 33: "Caibaté", 34: "Camaqua",
    35: "Cambara do Sul", 36: "Campina das Missões", 37: "Campinas do Sul",
    38: "Campo Bom", 39: "Campo Novo", 40: "Nao-Me-Toque",
    41: "Candelária", 42: "Cândido Godoi", 43: "Canela", 44: "Canguçu",
    45: "Canoas", 46: "Capao da Canoa", 47: "Capela de Santana",
    48: "Carazinho", 49: "Carlos Barbosa", 50: "Casca", 51: "Catuipe",
    52: "Cerro Largo", 53: "Chapada", 54: "Charqueadas", 55: "Chiapeta",
    56: "Chui", 57: "Cidreira", 58: "Ciriaco", 59: "Colorado",
    60: "Condor", 61: "Constantina", 62: "Coronel Bicaco",
    63: "Crissiumal", 64: "Cristal", 65: "Cruz Alta",
    66: "Cruzeiro do Sul", 67: "David Canabarro", 68: "Dois Irmaos",
    69: "Dom Feliciano", 70: "Dom Pedrito", 71: "Dona Francisca",
    72: "Encantado", 73: "Encruzilhada do Sul", 74: "Erebango",
    75: "Erechim", 76: "Erval Grande", 77: "Erval Seco",
    78: "Esmeralda", 79: "Espumoso", 80: "Estacao",
    81: "Estancia Velha", 82: "Esteio", 83: "Estrela",
    84: "Farroupilha", 85: "Feliz", 86: "Flores da Cunha",
    87: "Fontoura Xavier", 88: "Formigueiro", 89: "Frederico Westphalen",
    90: "Garibaldi", 91: "Gaurama", 92: "General Camara",
    93: "Getulio Vargas", 94: "Giruá", 95: "Gramado", 96: "Gravatai",
    97: "Guaiba", 98: "Guapore", 99: "Guarani das Missões",
    100: "Herval", 101: "Horizontina", 102: "Humaitá", 103: "Ibiaca",
    104: "Ibiraiaras", 105: "Ibiruba", 106: "Igrejinha", 107: "Ijui",
    108: "Ilopolis", 109: "Irai", 110: "Itaqui",
    111: "Itatiba do Sul", 113: "Jacutinga", 114: "Jaguarao",
    115: "Jaguari", 116: "Julio de Castilhos", 117: "Lagoa Vermelha",
    118: "Lajeado", 119: "Lavras do Sul", 120: "Liberato Sauzano",
    121: "Machadinho", 122: "Manoel Viana", 123: "Marau",
    124: "Marcelino Ramos", 125: "Mariano Moro", 127: "Mata",
    128: "Maximiliano de Almeida", 129: "Minas do Leao",
    130: "Miraguaí", 131: "Montenegro", 132: "Mostardas",
    133: "Nonoai", 135: "Nova Araca", 136: "Nova Bassano",
    137: "Nova Brescia", 138: "Nova Palma", 139: "Nova Petropolis",
    140: "Nova Prata", 141: "Nova Roma do Sul", 143: "Osorio",
    144: "Paim Filho", 145: "Palmares do Sul",
    146: "Palmeira das Missoes", 147: "Palmitinho", 148: "Panambi",
    149: "Pantano Grande", 150: "Parai", 151: "Passo Fundo",
    152: "Pedras Altas", 153: "Pedro Osorio", 154: "Pejucara",
    155: "Balneario Pinhal", 156: "Pinheiro Machado", 157: "Piratini",
    158: "Planalto", 159: "Porto Lucena", 160: "Porto Xavier",
    161: "Putinga", 162: "Quarai", 163: "Redentora",
    164: "Restinga Seca", 165: "Rio Grande", 166: "Rio Pardo",
    167: "Roca Sales", 168: "Rodeio Bonito", 169: "Rolante",
    170: "Ronda Alta", 171: "Rondinha", 173: "Rosario do Sul",
    174: "Salto do Jacui", 175: "Salvador do Sul", 176: "Sananduva",
    177: "Santa Barbara do Sul", 178: "Santa Cruz do Sul",
    179: "Santa Maria", 180: "Santana da Boa Vista",
    181: "Nova Santa Rita", 182: "Santa Rosa",
    184: "Santa Vitoria do Palmar", 185: "Santiago",
    186: "Santo Angelo", 187: "Santo Antonio da Patrulha",
    188: "Santo Antonio das Missões", 189: "Santo Augusto",
    190: "Santo Cristo", 191: "Sao Borja",
    192: "Sao Francisco de Assis", 193: "Sao Francisco de Paula",
    194: "São Gabriel", 195: "Sao Jeronimo",
    196: "Sao Jose do Norte", 197: "Sao Jose do Ouro",
    198: "Sao Lourenco do Sul", 199: "São Luiz Gonzaga",
    200: "Sao Marcos", 201: "São Martinho", 202: "São Nicolau",
    204: "Sao Pedro do Sul", 205: "Sao Sebastiao do Cai",
    206: "Sao Sepe", 207: "Sao Valentim",
    208: "Sao Vicente do Sul", 209: "Sapiranga",
    210: "Sapucaia do Sul", 211: "Sarandi", 212: "Seberi",
    213: "Selbach", 214: "Serafina Correa", 215: "Sertao",
    216: "Severiano de Almeida", 217: "Sobradinho", 218: "Soledade",
    219: "Tapejara", 220: "Tapera", 221: "Tapes", 222: "Taquara",
    223: "Taquari", 224: "Tenente Portela", 225: "Terra de Areia",
    226: "Torres", 227: "Tramandai", 228: "Tres Coroas",
    229: "Três de Maio", 230: "Três Passos", 231: "Tucunduva",
    232: "Tupancireta", 233: "Tuparendi", 235: "Vacaria",
    236: "Venancio Aires", 237: "Veranopolis", 238: "Viadutos",
    239: "Viamao", 240: "Vicente Dutra", 241: "Victor Graeff",
    242: "Independência", 245: "Xangri-La", 248: "Silveira Martins",
    249: "Portao", 250: "Faxinal do Soturno", 251: "Caicara",
    256: "Mauricio Cardoso", 257: "Entre Ijuís", 258: "Cerrito",
    261: "Campos Borges", 262: "Fagundes Varela",
    263: "Capivari do Sul", 269: "Dilermando de Aguiar",
    270: "Jaquirana", 272: "Imbe", 275: "Triunfo", 276: "Paverama",
    277: "Aceguá", 279: "Maçambará", 280: "Entre Rios do Sul",
    281: "Capão do Leão", 283: "Amaral Ferrador", 284: "Itaara",
    285: "Parobe", 286: "Fortaleza dos Valos", 289: "Vila Flores",
    292: "Morro Reuter", 293: "Sede Nova", 294: "Eldorado do Sul",
    295: "Trindade do Sul", 296: "Nova Esperanca do Sul",
    297: "Cotipora", 298: "Glorinha", 299: "Faxinalzinho",
    311: "Nova Hartz", 403: "Riozinho", 404: "Cerro Grande do Sul",
    405: "Água Santa", 406: "Ivora", 408: "Vista Alegre",
    409: "Vista Gaucha", 410: "Lagoao",
    411: "São Miguel das Missões", 412: "Ipe", 413: "Barao",
    414: "Arroio do Sal", 415: "Tres Cachoeiras",
    416: "Santa Maria do Herval", 418: "Sao Joao da Urtiga",
    419: "Sao Jorge", 420: "Aurea", 421: "Caseiros",
    422: "Boqueirao do Leao", 423: "Morro Redondo",
    425: "Sao Jose do Herval", 426: "Barra Do Guarita",
    429: "Taquarucu do Sul", 430: "Tavares", 432: "Alto Alegre",
    433: "Barra do Quarai", 435: "Jaboticaba", 438: "Unistalda",
    439: "Sentinela do Sul", 441: "Tiradentes do Sul",
    442: "Inhacorá", 443: "Derrubadas", 444: "Barao do Triunfo",
    445: "Sao Pedro da Serra", 446: "Sertao Santana",
    447: "Santo Expedito do Sul", 449: "Campestre da Serra",
    451: "Pinto Bandeira", 452: "São José do Inhacorá",
    455: "Ametista do Sul", 458: "Sao Jose dos Ausentes",
    460: "Pinheirinho do Vale", 461: "Bom Progresso",
    463: "Mariana Pimentel", 465: "Marques de Souza",
    466: "Chuvisca", 467: "Vila Nova do Sul", 468: "Passa Sete",
    490: "Lagoa Bonita do Sul", 491: "Rio dos Indios",
    497: "Santa Margarida do Sul", 498: "Itapuca",
    499: "Muitos Capoes",
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
        "timestamp": datetime.now(BR_TZ).strftime("%d/%m/%Y %H:%M:%S"),
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
            max_len = max(df[col].astype(str).str.len().max(), len(col)) + 2
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
# Logo (carregada uma vez e cacheada)
# ---------------------------------------------------------------------------
LOGO_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo-faturamento-opcao1-branco.png")
ICONE_FAT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo-sidebar.png")

@st.cache_resource
def load_logo(path: str):
    """Carrega a logo e recorta o espaço transparente em volta."""
    try:
        img = Image.open(path).convert("RGBA")
        bbox = img.getchannel("A").getbbox()  # área não transparente
        if bbox:
            img = img.crop(bbox)
        return img
    except Exception:
        return None

@st.cache_resource
def load_logo_centralizada_no_c(path: str, altura_ae: float = 0.25):
    """Centraliza pelo C/CORSAN, ignorando o 'ae' do canto superior direito,
    mas mantendo o 'ae' na imagem (adiciona margem transparente do lado oposto)."""
    try:
        img = Image.open(path).convert("RGBA")
        img = img.crop(img.getchannel("A").getbbox())
        w, h = img.size

        # mede só a parte de baixo, onde o 'ae' não existe
        corpo = img.crop((0, int(h * altura_ae), w, h))
        esq, _, dir_, _ = corpo.getchannel("A").getbbox()
        centro_c = (esq + dir_) / 2

        pad = int(round(abs(w - 2 * centro_c)))
        nova = Image.new("RGBA", (w + pad, h), (0, 0, 0, 0))
        if centro_c < w / 2:            # 'ae' sobra à direita -> margem à esquerda
            nova.paste(img, (pad, 0))
        else:                           # 'ae' sobra à esquerda -> margem à direita
            nova.paste(img, (0, 0))
        return nova
    except Exception:
        return None

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    logo = load_logo_centralizada_no_c(ICONE_FAT)
    if logo is not None:
        st.markdown(
            """
            <style>
            /* sobe o conteúdo da sidebar */
            [data-testid="stSidebarHeader"] {
                height: 0.2rem;
                min-height: 0;
                padding: 0;
            }
            [data-testid="stSidebarUserContent"] {
                padding-top: 0 !important;
            }

            /* centraliza e controla o tamanho da logo */
            [data-testid="stSidebar"] [data-testid="stImage"] {
                display: flex;
                justify-content: center;
            }
            [data-testid="stSidebar"] [data-testid="stImage"] img {
                width: 230px !important;   /* ajuste o tamanho aqui */
                max-width: 100%;
                height: auto;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )
        st.image(logo)
    else:
        # Fallback caso o arquivo nao seja encontrado
        st.markdown("""
        <div style="text-align: center; padding: 20px 0 10px 0;">
            <div style="font-size: 28px; font-weight: 800; color: #00C896;">
                FATURAMENTO
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Login ADM
    if not st.session_state.is_admin:
        with st.expander("Login", expanded=False):
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
            <span style="color: #00C896; font-weight: 600;">Admin Conectado</span>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Sair", key="btn_logout", use_container_width=True):
            st.session_state.is_admin = False
            st.rerun()

    st.markdown("---")

        # Dados carregados (usado para decidir o que aparece na sidebar)
    df_for_types = st.session_state.get("df_loaded")

    # Seletor de colaborador (so aparece depois do upload)
    if df_for_types is not None and COLABORADORES_ZONAS:
        st.markdown('<p style="color: rgba(255,255,255,0.6); font-size: 12px; text-transform: uppercase; letter-spacing: 1px;">Colaborador</p>', unsafe_allow_html=True)
        colab_names = ["Todos"] + sorted(COLABORADORES_ZONAS.keys())
        selected_colab = st.selectbox("Selecione seu nome", colab_names, key="colab_select", label_visibility="collapsed")
    else:
        selected_colab = "Todos"

    # Filtro por tipo de servico
    if df_for_types is not None and "Tipo de Solicitação" in df_for_types.columns:
        tipos_disponiveis = sorted(df_for_types["Tipo de Solicitação"].dropna().unique().tolist())
        st.markdown('<p style="color: rgba(255,255,255,0.6); font-size: 12px; text-transform: uppercase; letter-spacing: 1px; margin-top: 8px;">Tipo de Serviço</p>', unsafe_allow_html=True)
        selected_tipo = st.selectbox("Tipo de Serviço", ["Todos"] + tipos_disponiveis, key="tipo_select", label_visibility="collapsed")
    else:
        selected_tipo = "Todos"

    st.markdown("---")

        # Upload do arquivo
    st.markdown('<p style="color: rgba(255,255,255,0.6); font-size: 12px; text-transform: uppercase; letter-spacing: 1px;">Carregar Extração</p>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("", type=["xlsx", "xls"], key="file_upload", label_visibility="collapsed")

    if uploaded_file is not None:
        try:
            df = pd.read_excel(uploaded_file)
            df["Data Tramite"] = pd.to_datetime(df["Data Tramite"], errors="coerce")
            df["Data Pedido"] = pd.to_datetime(df["Data Pedido"], errors="coerce")
            primeira_carga = st.session_state.df_loaded is None
            st.session_state.df_loaded = df
            st.success(f"{len(df)} registros carregados")
            if primeira_carga:
                st.rerun()
        except Exception as e:
            st.error(f"Erro ao carregar: {e}")

    st.markdown("---")
    st.markdown(f"""
    <div style="text-align: center; color: rgba(255,255,255,0.3); font-size: 11px; padding: 10px 0;">
        Atualizado em {datetime.now(BR_TZ).strftime("%d/%m/%Y %H:%M")}
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
            Faça o upload da extração do SCAE na barra lateral para iniciar a distribuição das ordens de serviço.
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ---------------------------------------------------------------------------
# Calculos principais
# ---------------------------------------------------------------------------
distribution = distribute_os(df)

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
logo = load_logo(LOGO_PATH)

if logo is not None:
    st.image(logo, width=400)

st.markdown("<div style='height: 8px'></div>", unsafe_allow_html=True)

is_todos = (selected_colab == "Todos")

# Dados filtrados pelo colaborador selecionado
if not is_todos and selected_colab in distribution:
    df_colab = distribution[selected_colab]
    df_view = df_colab if not df_colab.empty else df
else:
    df_colab = pd.DataFrame()
    df_view = df

# Aplicar filtro por tipo de servico
if selected_tipo != "Todos":
    df_view = df_view[df_view["Tipo de Solicitação"] == selected_tipo]

total_os = len(df_view)
os_por_dia = df_view.groupby(df_view["Data Tramite"].dt.date).size()
dia_mais_antigo = os_por_dia.index.min() if not os_por_dia.empty else date.today()
qtd_dia_antigo = os_por_dia.get(dia_mais_antigo, 0)

# ---------------------------------------------------------------------------
# Cards de metricas
# ---------------------------------------------------------------------------
# Calcular cidade mais atrasada
df_cidade_src = df_view
cidade_atrasada = "-"
qtd_cidade_atrasada = 0
if not df_cidade_src.empty and "Zona Ligacao" in df_cidade_src.columns and "Data Tramite" in df_cidade_src.columns:
    df_sorted = df_cidade_src.sort_values("Data Tramite", ascending=True)
    for _, row in df_sorted.iterrows():
        zona = row.get("Zona Ligacao")
        if zona and int(zona) in ZONA_CIDADE:
            cidade_atrasada = ZONA_CIDADE[int(zona)]
            break
    if cidade_atrasada != "-":
        zonas_da_cidade = [z for z, c in ZONA_CIDADE.items() if c == cidade_atrasada]
        qtd_cidade_atrasada = len(df_cidade_src[df_cidade_src["Zona Ligacao"].isin(zonas_da_cidade)])

tipos_count = df_view["Tipo de Solicitação"].nunique() if not df_view.empty else 0

show_cards = is_todos or (not is_todos and selected_colab in distribution and not df_colab.empty)

if show_cards:
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(render_metric_card(
            "\U0001f4cb", f"{total_os:,}".replace(",", "."),
            "OS's em aberto", "card-cyan"
        ), unsafe_allow_html=True)
    with col2:
        dia_fmt = dia_mais_antigo.strftime("%d/%m") if dia_mais_antigo else "--"
        st.markdown(render_metric_card(
            "\U0001f4c5", dia_fmt,
            f"Dia mais atrasado ({qtd_dia_antigo} OS's)", "card-red"
        ), unsafe_allow_html=True)
    with col3:
        st.markdown(render_metric_card(
            "\U0001f4cb", str(tipos_count),
            "Tipos de serviços", "card-orange"
        ), unsafe_allow_html=True)
    with col4:
        if cidade_atrasada != "-":
            cidade_html = f'<span style="font-size:20px">{cidade_atrasada}</span> <span style="font-size:28px;font-weight:900">({qtd_cidade_atrasada})</span>'
        else:
            cidade_html = "-"
        st.markdown(render_metric_card(
            "\U0001f3d9️", cidade_html,
            "Cidade mais atrasada", "card-white"
        ), unsafe_allow_html=True)
elif not is_todos and selected_colab in distribution and df_colab.empty:
    st.info("Nenhuma OS atribuida para este colaborador.")
elif not is_todos:
    absence = load_absence_config()
    if selected_colab in absence:
        st.warning(f"{selected_colab} esta ausente. OS's redistribuidas.")

st.markdown("<div style='height: 20px'></div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Acompanhamento pelo Tramite (grafico interativo - clique no dia)
# ---------------------------------------------------------------------------
st.markdown('<div class="section-title">Acompanhamento pelo Tramite</div>', unsafe_allow_html=True)

os_dia_df = os_por_dia.reset_index()
os_dia_df.columns = ["Data", "Quantidade"]
os_dia_df = os_dia_df[os_dia_df["Quantidade"] > 0]
os_dia_df = os_dia_df.sort_values("Data")
os_dia_df["Data_fmt"] = os_dia_df["Data"].apply(lambda d: d.strftime("%d/%m"))

selected_dia = None

if not os_dia_df.empty:
    fig_os_dia = go.Figure(
        go.Bar(
            x=os_dia_df["Data_fmt"],
            y=os_dia_df["Quantidade"],
            marker=dict(
                color="#00D4AA",
                cornerradius=4,
            ),
            text=os_dia_df["Quantidade"],
            textposition="outside",
            textfont=dict(color="#FFFFFF", size=13, family="sans-serif"),
        )
    )
    fig_os_dia.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=10, b=0),
        height=300,
        xaxis=dict(
            color="rgba(255,255,255,0.6)",
            tickfont=dict(size=12),
            showgrid=False,
            showline=False,
        ),
        yaxis=dict(
            visible=False,
            showgrid=False,
        ),
        bargap=0.3,
    )

    chart_key = f"chart_tramite_{selected_colab}"
    event = st.plotly_chart(
        fig_os_dia,
        use_container_width=True,
        config={"displayModeBar": False},
        on_select="rerun",
        key=chart_key,
    )

    if event and hasattr(event, "selection") and event.selection and event.selection.points:
        clicked_fmt = event.selection.points[0].get("x")
        if clicked_fmt:
            match = os_dia_df[os_dia_df["Data_fmt"] == clicked_fmt]
            if not match.empty:
                selected_dia = match.iloc[0]["Data"]

# ---------------------------------------------------------------------------
# Filtro por dia (aplicado nas secoes abaixo)
# ---------------------------------------------------------------------------
if selected_dia is not None:
    df_dia = df_view[df_view["Data Tramite"].dt.date == selected_dia]
    dia_label = selected_dia.strftime("%d/%m/%Y")
    st.markdown(
        '<div style="display:inline-flex;align-items:center;gap:8px;background:rgba(0,212,170,0.12);'
        'border:1px solid rgba(0,212,170,0.3);border-radius:20px;padding:6px 16px;margin:4px 0 12px 0;">'
        '<span style="color:#00D4AA;font-size:13px;font-weight:600;">'
        '\U0001f4c5 Filtrado por: ' + dia_label + '</span>'
        '<span style="color:rgba(255,255,255,0.4);font-size:11px;">Clique novamente na barra para limpar</span>'
        '</div>',
        unsafe_allow_html=True,
    )
else:
    df_dia = df_view

total_filtrado = len(df_dia)

st.markdown("<div style='height: 24px'></div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Quantidade por tipo de servico - Grafico de barras horizontal amarelo
# ---------------------------------------------------------------------------
titulo_tipo = "Distribuição por Tipo de Serviço"
if selected_dia is not None:
    titulo_tipo += " — " + selected_dia.strftime("%d/%m/%Y")
st.markdown(f'<div class="section-title">{titulo_tipo}</div>', unsafe_allow_html=True)

tipo_counts = df_dia["Tipo de Solicitação"].value_counts()
max_count = tipo_counts.max() if not tipo_counts.empty else 1

if tipo_counts.empty:
    st.caption("Nenhuma OS para esta data.")
else:
    for tipo, count in tipo_counts.items():
        pct = (count / total_filtrado) * 100 if total_filtrado > 0 else 0
        bar_width = (count / max_count) * 100
        st.markdown(
            '<div style="margin-bottom: 10px;">'
            '<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">'
            f'<span style="color: rgba(255,255,255,0.85); font-size: 13px; font-weight: 500;">{tipo}</span>'
            f'<span style="color: #FFB347; font-size: 14px; font-weight: 700;">{count} '
            f'<span style="font-size:11px; color: rgba(255,255,255,0.4);">({pct:.1f}%)</span></span>'
            '</div>'
            '<div style="background: rgba(255,255,255,0.06); border-radius: 6px; height: 28px; overflow: hidden;">'
            f'<div style="background: linear-gradient(90deg, #FF9A2E, #FFB347); width: {bar_width}%;'
            ' height: 100%; border-radius: 6px; transition: width 0.5s ease;"></div>'
            '</div>'
            '</div>',
            unsafe_allow_html=True,
        )

st.markdown("<div style='height: 24px'></div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Tabela e Download (colaborador selecionado OU dia selecionado)
# ---------------------------------------------------------------------------
show_table = (not is_todos or selected_dia is not None) and not df_dia.empty

if show_table:
    titulo_tabela = "Detalhamento"
    if not is_todos:
        titulo_tabela += " — " + selected_colab.split("(")[0].strip()
    if selected_dia is not None:
        titulo_tabela += " — " + selected_dia.strftime("%d/%m/%Y")
    st.markdown(f'<div class="section-title">{titulo_tabela}</div>', unsafe_allow_html=True)

    display_cols = [
        "Nº da Solicitação", "Nº Ligação", "Zona Ligacao",
        "Tipo de Solicitação", "Data Tramite", "Data Pedido",
    ]
    available_cols = [c for c in display_cols if c in df_dia.columns]
    df_display = df_dia[available_cols].copy()
    df_display = df_display.sort_values("Data Tramite", ascending=True)

    for col in ["Data Tramite", "Data Pedido"]:
        if col in df_display.columns:
            df_display[col] = df_display[col].dt.strftime("%d/%m/%Y %H:%M")

    st.dataframe(
        df_display,
        use_container_width=True,
        height=min(38 + 4 * 35, 38 + len(df_display) * 35),
        hide_index=True,
    )

    st.markdown("<div style='height: 8px'></div>", unsafe_allow_html=True)

    excel_data = to_excel_download(df_dia)
    label_parts = ["Baixar Excel"]
    if not is_todos:
        label_parts.append(selected_colab.split("(")[0].strip())
    if selected_dia is not None:
        label_parts.append(selected_dia.strftime("%d/%m"))
    download_label = " - ".join(label_parts)

    fname_parts = ["OS"]
    if not is_todos:
        fname_parts.append(selected_colab.replace(" ", "_"))
    if selected_dia is not None:
        fname_parts.append(selected_dia.strftime("%Y%m%d"))
    fname_parts.append(datetime.now(BR_TZ).strftime("%H%M"))
    download_fname = "_".join(fname_parts) + ".xlsx"

    downloaded = st.download_button(
        label=download_label,
        data=excel_data,
        file_name=download_fname,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key=f"btn_download_{hash(str(selected_colab) + str(selected_dia)) % 99999}",
        use_container_width=True,
    )
    if downloaded and not is_todos:
        add_audit_entry(selected_colab, "download")

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

    tab_overview, tab_absence, tab_audit = st.tabs(["Visao Geral", "Cobertura de Ausencias", "Historico / Auditoria"])

    # -----------------------------------------------------------------------
    # Tab: Visao Geral (Top cidades + Ranking colaboradores)
    # -----------------------------------------------------------------------
    with tab_overview:
        col_chart1, col_chart2 = st.columns(2)

        with col_chart1:
            st.markdown('<div class="section-title">Top 15 Cidades com Mais OS Pendente</div>', unsafe_allow_html=True)
            if "Zona Ligacao" in df.columns:
                df_city = df.copy()
                df_city["Cidade"] = df_city["Zona Ligacao"].map(ZONA_CIDADE)
                city_counts = df_city["Cidade"].dropna().value_counts().head(15).sort_values(ascending=True)
                if not city_counts.empty:
                    fig_city = go.Figure(go.Bar(
                        x=city_counts.values,
                        y=city_counts.index,
                        orientation="h",
                        text=city_counts.values,
                        textposition="outside",
                        textfont=dict(color="white", size=12, family="Arial"),
                        marker=dict(
                            color=city_counts.values,
                            colorscale=[[0, "#FF6B6B"], [1, "#FF4D4D"]],
                        ),
                    ))
                    fig_city.update_layout(
                        plot_bgcolor="rgba(0,0,0,0)",
                        paper_bgcolor="rgba(0,0,0,0)",
                        font=dict(color="rgba(255,255,255,0.7)", size=12),
                        margin=dict(l=0, r=40, t=10, b=10),
                        height=450,
                        xaxis=dict(visible=False),
                        yaxis=dict(automargin=True),
                        bargap=0.3,
                    )
                    st.plotly_chart(fig_city, use_container_width=True, config={"displayModeBar": False})
                else:
                    st.info("Sem dados de cidade disponíveis.")
            else:
                st.info("Coluna 'Zona Ligacao' nao encontrada.")

        with col_chart2:
            st.markdown('<div class="section-title">OS Pendente por Colaborador</div>', unsafe_allow_html=True)
            if distribution:
                colab_os = {name: len(d) for name, d in distribution.items() if not d.empty}
                colab_os = dict(sorted(colab_os.items(), key=lambda x: x[1], reverse=False))
                names = [n.split("(")[0].strip() for n in colab_os.keys()]
                values = list(colab_os.values())
                if values:
                    fig_colab = go.Figure(go.Bar(
                        x=values,
                        y=names,
                        orientation="h",
                        text=values,
                        textposition="outside",
                        textfont=dict(color="white", size=12, family="Arial"),
                        marker=dict(
                            color=values,
                            colorscale=[[0, "#00A87A"], [1, "#00C896"]],
                        ),
                    ))
                    fig_colab.update_layout(
                        plot_bgcolor="rgba(0,0,0,0)",
                        paper_bgcolor="rgba(0,0,0,0)",
                        font=dict(color="rgba(255,255,255,0.7)", size=12),
                        margin=dict(l=0, r=40, t=10, b=10),
                        height=450,
                        xaxis=dict(visible=False),
                        yaxis=dict(automargin=True),
                        bargap=0.3,
                    )
                    st.plotly_chart(fig_colab, use_container_width=True, config={"displayModeBar": False})
                else:
                    st.info("Nenhuma OS distribuída.")
            else:
                st.info("Nenhum colaborador configurado.")

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
                        "registered_at": datetime.now(BR_TZ).strftime("%d/%m/%Y %H:%M:%S"),
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
