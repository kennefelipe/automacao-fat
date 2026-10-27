import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from io import BytesIO
from datetime import datetime, date, timezone, timedelta

BR_TZ = timezone(timedelta(hours=-3))
from PIL import Image
import json
import os
import re
import unicodedata

icone = Image.open(os.path.join(os.path.dirname(__file__), "logo-corsan-att.png"))
# ---------------------------------------------------------------------------
# Configuracao da pagina
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="HOP",
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

    /* Encosta o conteudo mais no topo, para a logo subir na tela */
    .stMainBlockContainer,
    div[data-testid="stMainBlockContainer"],
    section.main > div.block-container {
        padding-top: 1.6rem;
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

    /* Cards compactos (tela inicial) */
    .metric-card.compact {
        padding: 14px 18px;
        min-height: 96px;
        border-radius: 14px;
    }
    .metric-card.compact .metric-icon {
        top: 12px;
        left: 16px;
        width: 30px;
        height: 30px;
        font-size: 14px;
    }
    .metric-card.compact .metric-value {
        font-size: 28px;
        margin-top: 26px;
    }
    .metric-card.compact .metric-label {
        font-size: 11px;
        margin-top: 4px;
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
    "AMANDA BARCELLOS": [],
    "CAROLINE DE OLIVEIRA SANTOS": [10, 17, 35, 49, 58, 67, 75, 76, 80, 84, 90, 91, 95, 98, 103, 109, 113, 120, 121, 124, 125, 133, 135, 141, 144, 147, 150, 151, 175, 197, 207, 212, 214, 215, 219, 235, 237, 295, 297, 405, 412, 413, 418, 421, 429, 447, 451, 455],
    "CLEVER FANFA SARMENTO JUNIOR": [82, 210, 239],
    "DAIANE BARROS DE OLIVEIRA": [6, 8, 18, 21, 23, 32, 37, 43, 50, 61, 74, 77, 78, 86, 89, 93, 104, 111, 117, 123, 128, 136, 139, 140, 158, 168, 170, 171, 176, 193, 200, 211, 216, 238, 240, 251, 262, 270, 280, 289, 299, 420, 435, 445, 458, 460, 499],
    "ELIANA CATARINA BALOK CHAGAS": [31, 45, 96],
    "FELIPE KENNE DE OLIVEIRA": [9, 12, 14, 19, 34, 44, 47, 54, 56, 64, 68, 69, 100, 106, 114, 129, 131, 152, 153, 156, 157, 184, 196, 198, 205, 209, 228, 249, 258, 277, 281, 283, 292, 311, 423, 439, 446, 463, 466],
    "GABRIEL GODOI TEIXEIRA": [4, 5, 22, 25, 26, 29, 33, 36, 39, 42, 52, 55, 62, 63, 70, 94, 99, 101, 102, 110, 115, 122, 130, 159, 160, 162, 163, 173, 182, 185, 186, 188, 189, 190, 191, 192, 199, 201, 202, 208, 224, 229, 230, 231, 233, 242, 256, 279, 293, 296, 409, 411, 426, 433, 438, 441, 442, 443, 461],
    "HELLEN SCHIMIDT DIAS": [7, 97, 294],
    "IGOR MARTINI RODRIGUES": [27, 38, 81, 85, 92, 165, 169, 181, 195, 221, 222, 275, 285, 403, 404, 416, 444],
    "JULIA DA SILVA FLORES": [2, 15, 20, 28, 40, 53, 59, 60, 65, 66, 71, 72, 79, 88, 105, 116, 118, 146, 149, 161, 166, 167, 177, 178, 179, 204, 206, 218, 232, 248, 276, 284, 286, 406, 410, 432, 465, 497],
    "MAYARA AMARAL DORNELLES": [46, 57, 132, 143, 145, 155, 187, 225, 226, 227, 245, 263, 272, 298, 414, 415, 430],
    "PEDRO ARTHUR ALVES DE FREITAS": [],
    "PRISCILA DA SILVA LIMA": [1, 11, 13, 24, 30, 41, 48, 51, 73, 83, 87, 107, 108, 119, 127, 137, 138, 148, 154, 164, 174, 180, 213, 217, 220, 223, 236, 241, 250, 261, 269, 422, 425, 467],
}

# Tipos de servico com dono exclusivo, independentemente da zona da OS.
# 106008 Erro de Leitura e 206006 Retificacao de Disponibilidade: Pedro e
# Amanda, divididos por regiao (ESPECIALISTA_ZONAS logo abaixo).
CODIGOS_ESPECIALISTA = {"106008", "206006"}

# 112001 Devolucao de Valores - Ligacao: so da Daiane, no estado todo.
CODIGOS_EXCLUSIVOS = {
    "112001": "DAIANE BARROS DE OLIVEIRA",
    "206004": "DAIANE BARROS DE OLIVEIRA",
}

ESPECIALISTA_ZONAS = {
    "AMANDA BARCELLOS": [1, 2, 4, 5, 6, 8, 10, 11, 13, 15, 17, 18, 20, 21, 22, 23, 24, 25, 26, 28, 29, 30, 32, 33, 35, 36, 37, 39, 40, 41, 42, 43, 48, 49, 50, 51, 52, 53, 55, 58, 59, 60, 61, 62, 63, 65, 66, 67, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 83, 84, 86, 87, 88, 89, 90, 91, 93, 94, 95, 98, 99, 101, 102, 103, 104, 105, 107, 108, 109, 110, 111, 113, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 127, 128, 130, 133, 135, 136, 137, 138, 139, 140, 141, 144, 146, 147, 148, 149, 150, 151, 154, 158, 159, 160, 161, 162, 163, 164, 166, 167, 168, 170, 171, 173, 174, 175, 176, 177, 178, 179, 180, 182, 185, 186, 188, 189, 190, 191, 192, 193, 197, 199, 200, 201, 202, 204, 206, 207, 208, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 223, 224, 229, 230, 231, 232, 233, 235, 236, 237, 238, 240, 241, 242, 248, 250, 251, 256, 261, 262, 269, 270, 276, 279, 280, 284, 286, 289, 293, 295, 296, 297, 299, 405, 406, 409, 410, 411, 412, 413, 418, 420, 421, 422, 425, 426, 429, 432, 433, 435, 438, 441, 442, 443, 445, 447, 451, 455, 458, 460, 461, 465, 467, 497, 499],
    "PEDRO ARTHUR ALVES DE FREITAS": [7, 9, 12, 14, 19, 27, 31, 34, 38, 44, 45, 46, 47, 54, 56, 57, 64, 68, 69, 81, 82, 85, 92, 96, 97, 100, 106, 114, 129, 131, 132, 143, 145, 152, 153, 155, 156, 157, 165, 169, 181, 184, 187, 195, 196, 198, 205, 209, 210, 221, 222, 225, 226, 227, 228, 239, 245, 249, 258, 263, 272, 275, 277, 281, 283, 285, 292, 294, 298, 311, 403, 404, 414, 415, 416, 423, 430, 439, 444, 446, 463, 466],
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
    52: "Cerro Largo", 53: "Chapada", 54: "Charqueadas", 55: "Chiapetta",
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
    118: "Lajeado", 119: "Lavras do Sul", 120: "Liberato Salzano",
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
    256: "Doutor Maurício Cardoso", 257: "Entre-Ijuís", 258: "Cerrito",
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


def _codigo_inicial(valor):
    """Pega o codigo numerico que abre o campo: '106008' ou '106008 - ERRO...'."""
    m = re.match(r"\s*(\d{4,8})\b", str(valor))
    return m.group(1) if m else None


def detectar_coluna_codigo(df):
    """Descobre em qual coluna vem o codigo do tipo de servico.

    A extracao do SCAE pode trazer o codigo numa coluna propria ou junto do
    nome do tipo. Procuramos a coluna que contenha os codigos de regra
    exclusiva e tenha poucos valores distintos (tipo de servico e uma lista
    curta; numero de OS nao e).
    """
    procurados = CODIGOS_ESPECIALISTA | set(CODIGOS_EXCLUSIVOS)
    melhor, menos_unicos = None, None
    for col in df.columns:
        try:
            unicos = df[col].dropna().unique()
        except Exception:
            continue
        if len(unicos) == 0 or len(unicos) > 300:
            continue
        codigos = {_codigo_inicial(v) for v in unicos}
        if codigos & procurados:
            if melhor is None or len(unicos) < menos_unicos:
                melhor, menos_unicos = col, len(unicos)
    return melhor


# Usado so quando a extracao nao traz o codigo: identifica pelo nome do tipo.
_TEXTO_DOS_CODIGOS = {
    "106008": lambda t: "erro" in t and "leitura" in t,
    "206006": lambda t: ("disponibilidade" in t or "dispensa" in t)
                        and ("retifica" in t or "esgoto" in t),
    "112001": lambda t: "devolucao" in t and "valor" in t,
    "206004": lambda t: "cancelamento" in t and "fatura" in t and "service now" in t,
}


def serie_codigos(df):
    """(codigo do tipo de servico por linha, coluna usada).

    Se a extracao nao trouxer o codigo, deduz pelo nome do tipo de servico.
    """
    col = detectar_coluna_codigo(df)
    if col is not None:
        return df[col].map(_codigo_inicial), col

    if "Tipo de Solicitação" in df.columns:
        txt = df["Tipo de Solicitação"].map(norm_cidade)

        def pelo_nome(t):
            for cod, casa in _TEXTO_DOS_CODIGOS.items():
                if casa(t):
                    return cod
            return None

        return txt.map(pelo_nome), None

    return pd.Series(None, index=df.index, dtype="object"), None


STATUS_AGUARDANDO_RETORNO = "Aguardando Retorno"


def aplicar_status(df):
    """Cria a coluna Status.

    Regra especial, SO para Devolucao de Valores - Ligacao (codigo 112001):
    se o Parecer Tecnico contiver o marcador #00, o status fica
    'Aguardando Retorno'. Os demais tipos de solicitacao ficam sem status.
    """
    df = df.copy()
    df["Status"] = ""
    if "Parecer Técnico" not in df.columns:
        return df
    codigos, _ = serie_codigos(df)
    eh_devolucao = codigos == "112001"
    # #00 nao seguido de outro digito, para nao casar com #001, #002, etc.
    tem_marcador = df["Parecer Técnico"].astype(str).str.contains(r"#00(?!\d)", regex=True, na=False)
    df.loc[eh_devolucao & tem_marcador, "Status"] = STATUS_AGUARDANDO_RETORNO
    return df


def distribute_os(df):
    """Distribui as OS por colaborador baseado na zona.

    Erro de Leitura e Retificacao de Disponibilidade sao exclusivos de Pedro e
    Amanda, divididos por regiao, e por isso saem da fila normal antes do
    rateio por zona.
    """
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

    # Tipos com dono exclusivo saem antes: nao entram no rateio por zona
    codigos, _col = serie_codigos(df)
    marca_esp = codigos.isin(CODIGOS_ESPECIALISTA)
    marca_excl = codigos.isin(CODIGOS_EXCLUSIVOS)
    df_esp = df[marca_esp]
    df_normal = df[~(marca_esp | marca_excl)]

    for colab, zonas in active_collabs.items():
        mask = df_normal["Zona Ligacao"].isin(zonas)
        distribution[colab] = pd.concat([distribution[colab], df_normal[mask]])

    # Dono unico por tipo, no estado todo (ex.: devolucao de valores -> Daiane)
    for cod, dono in CODIGOS_EXCLUSIVOS.items():
        recorte = df[codigos == cod]
        if recorte.empty:
            continue
        alvo = dono
        if alvo not in distribution:
            info = absent_collabs.get(alvo, {})
            alvo = info.get("redirect_to")
            if alvo not in distribution:
                alvo = next(iter(distribution), None)
        if alvo is not None:
            distribution[alvo] = pd.concat([distribution[alvo], recorte])

    if not df_esp.empty:
        for colab, zonas in ESPECIALISTA_ZONAS.items():
            mask = df_esp["Zona Ligacao"].isin(zonas)
            if colab in distribution:
                distribution[colab] = pd.concat([distribution[colab], df_esp[mask]])
                continue
            # Especialista ausente: a fila dele nao pode sumir. Vai para quem
            # cobre a ausencia; se nao houver, para o outro especialista.
            info = absent_collabs.get(colab, {})
            alvo = info.get("redirect_to")
            if alvo not in distribution:
                alvo = next((o for o in ESPECIALISTA_ZONAS
                             if o != colab and o in distribution), None)
            if alvo is None:
                alvo = next(iter(distribution), None)
            if alvo is not None:
                distribution[alvo] = pd.concat([distribution[alvo], df_esp[mask]])

    for colab, info in absent_collabs.items():
        zonas_ausente = info["zonas"]
        os_ausente = df_normal[df_normal["Zona Ligacao"].isin(zonas_ausente)]

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


# Colunas que aparecem na tabela da tela e saem no Excel, nesta ordem.
# A extracao do SCAE traz muita coluna que o pessoal nao usa.
COLUNAS_EXPORT = [
    "Nº da Solicitação", "Nº Ligação", "Zona Ligacao",
    "Tipo de Solicitação", "Status", "Data Tramite", "Data Pedido",
]
COLUNAS_DATA = ["Data Tramite", "Data Pedido"]


def colunas_visiveis(df):
    """COLUNAS_EXPORT presentes no df, omitindo Status quando esta todo vazio."""
    cols = [c for c in COLUNAS_EXPORT if c in df.columns]
    if "Status" in cols:
        tem_status = df["Status"].astype(str).str.strip().ne("").any()
        if not tem_status:
            cols.remove("Status")
    return cols


def to_excel_download(df):
    """Exporta so as colunas da tela, na mesma ordem e ordenadas por tramite.

    As datas saem como data de verdade (nao texto), para continuar dando
    para ordenar e filtrar no Excel, com a aparencia dd/mm/aaaa hh:mm.
    """
    cols = colunas_visiveis(df)
    saida = df[cols].copy() if cols else df.copy()
    if "Data Tramite" in saida.columns:
        saida = saida.sort_values("Data Tramite", ascending=True)

    output = BytesIO()
    # datetime_format no writer: o pandas escreve cada celula de data com
    # formato proprio, que vence o formato da coluna.
    with pd.ExcelWriter(output, engine="xlsxwriter",
                        datetime_format="dd/mm/yyyy hh:mm") as writer:
        saida.to_excel(writer, index=False, sheet_name="OS")
        aba = writer.sheets["OS"]
        for i, col in enumerate(saida.columns):
            # pandas 3: astype(str) preserva NA, entao uma coluna toda vazia
            # devolve NaN aqui e o xlsxwriter rejeita a largura.
            maior = saida[col].astype(str).str.len().max()
            if pd.isna(maior):
                maior = 0
            larg = min(max(int(maior), len(str(col))) + 2, 50)
            if col in COLUNAS_DATA:
                larg = max(larg, 18)
            aba.set_column(i, i, larg)
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
LOGO_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo-hub-operacional.png")
ICONE_FAT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo-sidebar.png")
GEOJSON_RS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "rs_municipios.json")

# Paleta do mapa (validada contra a superficie #0F2044)
# Marinho -> azul vivo. O topo para em #2367c4 de proposito: acima disso o
# texto branco dos nomes das cidades deixa de ser legivel sobre o preenchimento.
MAPA_RAMPA = ["#15406e", "#18477c", "#1a4d8a", "#1c5cab", "#2060b8", "#2367c4"]
MAPA_SLOTS = ["#3987e5", "#d95926", "#199e70", "#c98500",
              "#d55181", "#008300", "#9085e9", "#e66767",
              "#1f9aa6", "#6f6fd0", "#a8742a", "#c75bbf"]
MAPA_OUTROS = "#7d8696"
MAPA_VAZIO = "rgba(255,255,255,0.05)"
MAPA_MUDO = "rgba(255,255,255,0.09)"
MAPA_BORDA = "rgba(255,255,255,0.18)"


def norm_cidade(nome: str) -> str:
    """Normaliza nome de cidade para casar com o GeoJSON (sem acento, sem hifen)."""
    s = unicodedata.normalize("NFKD", str(nome))
    s = "".join(c for c in s if not unicodedata.combining(c))
    return " ".join(s.lower().replace("-", " ").split())


@st.cache_data
def load_geojson():
    """Contornos dos 497 municipios do RS (IBGE). Retorna (geojson, key->codigo, codigo->nome)."""
    try:
        with open(GEOJSON_RS, encoding="utf-8") as f:
            geo = json.load(f)
    except Exception:
        return None, {}, {}
    key_to_cod, cod_to_nome = {}, {}
    for feat in geo["features"]:
        p = feat["properties"]
        key_to_cod[p["key"]] = p["codarea"]
        cod_to_nome[p["codarea"]] = p["nome"]
    return geo, key_to_cod, cod_to_nome


def zonas_do_colaborador(colab):
    """Zonas que a pessoa atende.

    Pedro e Amanda nao tem cidades proprias: o territorio deles e a regiao da
    fila especialista (Erro de Leitura / Retificacao de Disponibilidade).
    """
    zonas = COLABORADORES_ZONAS.get(colab) or []
    if zonas:
        return zonas
    return ESPECIALISTA_ZONAS.get(colab, [])


def donos_com_cidades():
    """Quem tem cidades proprias - os que aparecem no mapa por responsavel."""
    return sorted(c for c, z in COLABORADORES_ZONAS.items() if z)


def mapa_cores():
    """Cor fixa por colaborador, por ordem alfabetica (nao muda com filtro)."""
    return {n: MAPA_SLOTS[i % len(MAPA_SLOTS)]
            for i, n in enumerate(donos_com_cidades())}


def mapa_resumo(df_src):
    """[(nome, curto, cor, qtd_cidades, qtd_os)] por colaborador, do maior pro menor."""
    geo, key_to_cod, _ = load_geojson()
    if geo is None:
        return []

    zona_colab = {}
    for nome, zonas in COLABORADORES_ZONAS.items():
        for z in zonas:
            zona_colab[z] = nome

    cidades_de, cod_colab = {}, {}
    for z, cidade in ZONA_CIDADE.items():
        cod = key_to_cod.get(norm_cidade(cidade))
        dono = zona_colab.get(z)
        if cod and dono:
            cod_colab[cod] = dono
            cidades_de[dono] = cidades_de.get(dono, 0) + 1

    os_de = {}
    if "Zona Ligacao" in df_src.columns:
        for zona, qtd in df_src["Zona Ligacao"].value_counts().items():
            try:
                z = int(zona)
            except (TypeError, ValueError):
                continue
            dono = zona_colab.get(z)
            if dono:
                os_de[dono] = os_de.get(dono, 0) + int(qtd)

    cor_de = mapa_cores()
    linhas = [
        (n, n.split("(")[0].strip(), cor_de.get(n, MAPA_OUTROS),
         cidades_de.get(n, 0), os_de.get(n, 0))
        for n in donos_com_cidades()
    ]
    linhas.sort(key=lambda r: (-r[4], -r[3]))
    return linhas


def cidades_do_colaborador(df_src, colab):
    """[(cidade, qtd_os)] em ordem alfabetica - a lista de quem cuida do que."""
    zonas = zonas_do_colaborador(colab)
    os_por_zona = {}
    if "Zona Ligacao" in df_src.columns:
        for zona, qtd in df_src["Zona Ligacao"].value_counts().items():
            try:
                os_por_zona[int(zona)] = int(qtd)
            except (TypeError, ValueError):
                continue
    linhas = {}
    for z in zonas:
        cidade = ZONA_CIDADE.get(z)
        if cidade:
            linhas[cidade] = linhas.get(cidade, 0) + os_por_zona.get(z, 0)
    return sorted(linhas.items(), key=lambda r: norm_cidade(r[0]))


def _pontos(coords):
    if coords and isinstance(coords[0], (int, float)):
        yield coords
    else:
        for c in coords:
            yield from _pontos(c)


@st.cache_data
def mapa_centroides():
    """{codigo: (lon, lat)} - centro aproximado de cada municipio, para rotulos."""
    geo, _, _ = load_geojson()
    if geo is None:
        return {}
    centros = {}
    for feat in geo["features"]:
        pts = list(_pontos(feat["geometry"]["coordinates"]))
        if not pts:
            continue
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        centros[feat["properties"]["codarea"]] = (
            (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
        )
    return centros


def _limites(cods, centros, margem=0.10):
    """Janela de visualizacao que cobre os municipios, com uma folga em volta."""
    pts = [centros[c] for c in cods if c in centros]
    if not pts:
        return None, None
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    larg = max(max(xs) - min(xs), 0.5)
    alt = max(max(ys) - min(ys), 0.5)
    folga_x = larg * margem + 0.25
    folga_y = alt * margem + 0.25
    return ([min(xs) - folga_x, max(xs) + folga_x],
            [min(ys) - folga_y, max(ys) + folga_y])


def mapa_layout(fig, lon_range=None, lat_range=None):
    if lon_range and lat_range:
        fig.update_geos(
            visible=False,
            lonaxis_range=lon_range,
            lataxis_range=lat_range,
            projection_type="mercator",
            bgcolor="rgba(0,0,0,0)",
        )
    else:
        fig.update_geos(
            visible=False,
            fitbounds="locations",
            projection_type="mercator",
            bgcolor="rgba(0,0,0,0)",
        )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=0, b=0),
        height=720,
        dragmode="pan",
        showlegend=False,
        font=dict(color="#c3c2b7", size=12),
    )
    return fig


def build_mapa(df_src, foco, modo):
    """Monta o mapa de cobertura do RS.

    Territorio vem de COLABORADORES_ZONAS (fixo); o volume de OS vem de df_src,
    que ja carrega os filtros ativos da tela.
    """
    geo, key_to_cod, cod_to_nome = load_geojson()
    if geo is None:
        return None, "Arquivo de mapa nao encontrado."

    zona_colab = {}
    for nome, zonas in COLABORADORES_ZONAS.items():
        for z in zonas:
            zona_colab[z] = nome

    cod_colab = {}
    for z, cidade in ZONA_CIDADE.items():
        cod = key_to_cod.get(norm_cidade(cidade))
        if cod and z in zona_colab:
            cod_colab[cod] = zona_colab[z]

    if not cod_colab:
        return None, "Nenhuma zona mapeada."

    # OS por municipio, respeitando os filtros da tela
    cod_os = {}
    if "Zona Ligacao" in df_src.columns:
        for zona, qtd in df_src["Zona Ligacao"].value_counts().items():
            try:
                z = int(zona)
            except (TypeError, ValueError):
                continue
            cidade = ZONA_CIDADE.get(z)
            if not cidade:
                continue
            cod = key_to_cod.get(norm_cidade(cidade))
            if cod:
                cod_os[cod] = cod_os.get(cod, 0) + int(qtd)

    todos_cods = [f["properties"]["codarea"] for f in geo["features"]]
    base = go.Choropleth(
        geojson=geo, locations=todos_cods, z=[0] * len(todos_cods),
        colorscale=[[0, MAPA_VAZIO], [1, MAPA_VAZIO]], showscale=False,
        marker=dict(line=dict(color="rgba(255,255,255,0.10)", width=0.3)),
        hoverinfo="skip", showlegend=False,
    )

    escala = [[i / (len(MAPA_RAMPA) - 1), c] for i, c in enumerate(MAPA_RAMPA)]
    curto = (foco or "").split("(")[0].strip()

    # ---- Colaborador em foco: destaca o territorio dele, esmaece o resto
    if foco in COLABORADORES_ZONAS:
        meus = [c for c, dono in cod_colab.items() if dono == foco]
        rotulo_extra = ""
        if not meus:
            # Pedro e Amanda: o territorio deles e a regiao da fila especialista
            zonas_esp = set(ESPECIALISTA_ZONAS.get(foco, []))
            alvo = {norm_cidade(ZONA_CIDADE[z]) for z in zonas_esp if z in ZONA_CIDADE}
            meus = [c for c in cod_colab
                    if norm_cidade(cod_to_nome.get(c, "")) in alvo]
            rotulo_extra = " (Erro de Leitura + Retif. de Disponibilidade)"
        outros = [c for c in cod_colab if c not in set(meus)]
        if not meus:
            return None, "Este colaborador nao tem zonas mapeadas."
        fig = go.Figure([base])
        if outros:
            fig.add_trace(go.Choropleth(
                geojson=geo, locations=outros, z=[0] * len(outros),
                colorscale=[[0, MAPA_MUDO], [1, MAPA_MUDO]], showscale=False,
                marker=dict(line=dict(color="rgba(255,255,255,0.12)", width=0.3)),
                hoverinfo="skip", showlegend=False,
            ))
        cd = [[cod_to_nome[c], cod_os.get(c, 0)] for c in meus]
        fig.add_trace(go.Choropleth(
            geojson=geo, locations=meus, z=[cod_os.get(c, 0) for c in meus],
            customdata=cd, colorscale=escala, showscale=True, showlegend=False,
            marker=dict(line=dict(color="#ffffff", width=0.7)),
            colorbar=dict(
                title=dict(text="OS", font=dict(color="#c3c2b7", size=11)),
                tickfont=dict(color="#c3c2b7", size=11),
                thickness=18, len=0.92, x=0.99, y=0.5, yanchor="middle",
                outlinewidth=0, tickformat="d",
            ),
            hovertemplate="<b>%{customdata[0]}</b><br>%{customdata[1]} OS<extra></extra>",
        ))

        # Nomes das cidades sobre o territorio, para saberem quais sao as suas
        centros = mapa_centroides()
        com_centro = [c for c in meus if c in centros]
        if com_centro:
            fig.add_trace(go.Scattergeo(
                lon=[centros[c][0] for c in com_centro],
                lat=[centros[c][1] for c in com_centro],
                text=[cod_to_nome[c] for c in com_centro],
                mode="text",
                textfont=dict(color="#ffffff", size=9, family="sans-serif"),
                textposition="middle center",
                hoverinfo="skip", showlegend=False,
            ))

        lon_r, lat_r = _limites(meus, centros)
        total_meu = sum(cod_os.get(c, 0) for c in meus)
        return (mapa_layout(fig, lon_r, lat_r),
                f"{curto}{rotulo_extra}: {len(meus)} cidades, {total_meu} OS")

    # ---- Visao Todos: por volume de OS
    if modo == "Onde esta o atraso":
        cods = sorted(cod_colab)
        cd = [[cod_to_nome[c], cod_colab[c].split("(")[0].strip(), cod_os.get(c, 0)] for c in cods]
        fig = go.Figure([base])
        fig.add_trace(go.Choropleth(
            geojson=geo, locations=cods, z=[cod_os.get(c, 0) for c in cods],
            customdata=cd, colorscale=escala, showlegend=False,
            marker=dict(line=dict(color=MAPA_BORDA, width=0.4)),
            colorbar=dict(
                title=dict(text="OS", font=dict(color="#c3c2b7", size=11)),
                tickfont=dict(color="#c3c2b7", size=11),
                thickness=18, len=0.92, x=0.99, y=0.5, yanchor="middle",
                outlinewidth=0, tickformat="d",
            ),
            hovertemplate="<b>%{customdata[0]}</b><br>%{customdata[1]}<br>%{customdata[2]} OS<extra></extra>",
        ))
        return mapa_layout(fig), None

    # ---- Visao Todos: por responsavel (cada colaborador com sua cor)
    cor_de = mapa_cores()
    por_dono = {}
    for cod, dono in cod_colab.items():
        por_dono.setdefault(dono, []).append(cod)

    fig = go.Figure([base])
    for dono in sorted(por_dono, key=lambda d: -len(por_dono[d])):
        lst = por_dono[dono]
        cor = cor_de.get(dono, MAPA_OUTROS)
        cd = [[cod_to_nome[c], dono.split("(")[0].strip(), cod_os.get(c, 0)] for c in lst]
        fig.add_trace(go.Choropleth(
            geojson=geo, locations=lst, z=[1] * len(lst), customdata=cd,
            colorscale=[[0, cor], [1, cor]], showscale=False, showlegend=False,
            marker=dict(line=dict(color=MAPA_BORDA, width=0.4)),
            hovertemplate="<b>%{customdata[0]}</b><br>%{customdata[1]}<br>%{customdata[2]} OS<extra></extra>",
        ))
    return mapa_layout(fig), None

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
        colab_names = ["Todos"] + sorted(COLABORADORES_ZONAS.keys())
        # Clique no grafico "OS por Colaborador" (painel ADM) escolhe o nome aqui.
        # Precisa ser aplicado ANTES de instanciar o selectbox: o Streamlit nao
        # deixa alterar a chave de um widget ja criado no mesmo run.
        pendente = st.session_state.pop("_colab_click_pending", None)
        if pendente in colab_names:
            st.session_state["colab_select"] = pendente
        st.markdown('<p style="color: rgba(255,255,255,0.6); font-size: 12px; text-transform: uppercase; letter-spacing: 1px;">Colaborador</p>', unsafe_allow_html=True)
        selected_colab = st.selectbox("Selecione seu nome", colab_names, key="colab_select", label_visibility="collapsed")
    else:
        selected_colab = "Todos"

    # Filtro por tipo de servico (multiplos; lista vazia = todos)
    if df_for_types is not None and "Tipo de Solicitação" in df_for_types.columns:
        tipos_disponiveis = sorted(df_for_types["Tipo de Solicitação"].dropna().unique().tolist())
        st.markdown('<p style="color: rgba(255,255,255,0.6); font-size: 12px; text-transform: uppercase; letter-spacing: 1px; margin-top: 8px;">Tipo de Serviço</p>', unsafe_allow_html=True)
        selected_tipos = st.multiselect(
            "Tipo de Serviço", tipos_disponiveis, key="tipo_multiselect",
            placeholder="Todos", label_visibility="collapsed",
        )
    else:
        selected_tipos = []

    if df_for_types is not None:
        st.markdown("---")

        # Upload do arquivo
    st.markdown('<p style="color: rgba(255,255,255,0.6); font-size: 12px; text-transform: uppercase; letter-spacing: 1px;">Carregar Extração</p>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("", type=["xlsx", "xls"], key="file_upload", label_visibility="collapsed")

    if uploaded_file is not None:
        try:
            df = pd.read_excel(uploaded_file)
            df["Data Tramite"] = pd.to_datetime(df["Data Tramite"], errors="coerce")
            df["Data Pedido"] = pd.to_datetime(df["Data Pedido"], errors="coerce")
            df = aplicar_status(df)
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
    # centraliza a logo: a coluna do meio e a unica que recebe conteudo
    _esq, _meio, _dir = st.columns([1, 2, 1])
    with _meio:
        st.image(logo, use_container_width=True)

# folga entre a logo e os cards
st.markdown("<div style='height: 30px'></div>", unsafe_allow_html=True)

is_todos = (selected_colab == "Todos")

# Dados filtrados pelo colaborador selecionado
if not is_todos and selected_colab in distribution:
    df_colab = distribution[selected_colab]
    df_view = df_colab if not df_colab.empty else df
else:
    df_colab = pd.DataFrame()
    df_view = df

# Aplicar filtro por tipo de servico (um ou mais tipos)
if selected_tipos:
    df_view = df_view[df_view["Tipo de Solicitação"].isin(selected_tipos)]

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

# TMAX: dias entre hoje e o tramite mais antigo em aberto (ontem = TMAX 1).
# Mesma regra da medida do BI: ignora datas futuras. Usa df_view, entao
# acompanha colaborador e tipo de solicitacao.
hoje_br = datetime.now(BR_TZ).date()
tmax = None
tmax_data = None
if "Data Tramite" in df_view.columns:
    datas_tramite = df_view["Data Tramite"].dropna().dt.date
    datas_tramite = datas_tramite[datas_tramite <= hoje_br]
    if not datas_tramite.empty:
        tmax_data = datas_tramite.min()
        tmax = (hoje_br - tmax_data).days

show_cards = is_todos or (not is_todos and selected_colab in distribution and not df_colab.empty)

if show_cards:
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown(render_metric_card(
            "\U0001f4cb", f"{total_os:,}".replace(",", "."),
            "OS's em aberto", "card-cyan compact"
        ), unsafe_allow_html=True)
    with col2:
        if cidade_atrasada != "-":
            cidade_html = (f'<span style="font-size:15px">{cidade_atrasada}</span> '
                           f'<span style="font-size:20px;font-weight:900">({qtd_cidade_atrasada})</span>')
        else:
            cidade_html = "-"
        st.markdown(render_metric_card(
            "\U0001f3d9️", cidade_html,
            "Cidade mais atrasada", "card-white compact"
        ), unsafe_allow_html=True)
    with col3:
        st.markdown(render_metric_card(
            "\U0001f4cb", str(tipos_count),
            "Tipos de serviços", "card-dark compact"
        ), unsafe_allow_html=True)
    with col4:
        dia_fmt = dia_mais_antigo.strftime("%d/%m") if dia_mais_antigo else "--"
        st.markdown(render_metric_card(
            "\U0001f4c5", dia_fmt,
            f"Dia mais atrasado ({qtd_dia_antigo} OS's)", "card-orange compact"
        ), unsafe_allow_html=True)
    with col5:
        tmax_txt = f"TMAX {tmax}" if tmax is not None else "-"
        tmax_label = (f"Trâmite mais antigo: {tmax_data.strftime('%d/%m')}"
                      if tmax_data else "Sem OS em aberto")
        st.markdown(render_metric_card(
            "⏱️", tmax_txt, tmax_label, "card-red compact"
        ), unsafe_allow_html=True)
elif not is_todos and selected_colab in distribution and df_colab.empty:
    st.info("Nenhuma OS atribuida para este colaborador.")
elif not is_todos:
    absence = load_absence_config()
    if selected_colab in absence:
        st.warning(f"{selected_colab} esta ausente. OS's redistribuidas.")

st.markdown("<div style='height: 20px'></div>", unsafe_allow_html=True)

tab_acomp, tab_mapa = st.tabs(["Acompanhamento", "Mapa de Cobertura"])

with tab_acomp:
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
    # Quantidade por tipo de servico - Grafico interativo
    # ---------------------------------------------------------------------------
    titulo_tipo = "Distribuição por Tipo de Serviço"
    if selected_dia is not None:
        titulo_tipo += " — " + selected_dia.strftime("%d/%m/%Y")

    st.markdown(
        f'<div class="section-title">{titulo_tipo}</div>',
        unsafe_allow_html=True,
    )

    tipo_counts = df_dia["Tipo de Solicitação"].value_counts()
    max_count = tipo_counts.max() if not tipo_counts.empty else 1

    # Estado do tipo de servico selecionado
    tipo_key = f"tipo_selecionado_{selected_colab}"
    selected_tipo = st.session_state.get(tipo_key)

    # Limpar selecao se o tipo nao existir mais nos dados filtrados
    if selected_tipo not in tipo_counts.index:
        selected_tipo = None
        st.session_state[tipo_key] = None

    if tipo_counts.empty:
        st.caption("Nenhuma OS para esta data.")
    else:
        tipos_plot = tipo_counts.index.tolist()

        fig_tipos = go.Figure(
            go.Bar(
                x=tipo_counts.values,
                y=tipos_plot,
                orientation="h",
                marker=dict(
                    color=[
                        "#00D4AA" if tipo == selected_tipo else "#FFB347"
                        for tipo in tipos_plot
                    ],
                    cornerradius=4,
                ),
                text=tipo_counts.values,
                textposition="outside",
                textfont=dict(
                    color="#FFFFFF",
                    size=12,
                    family="sans-serif",
                ),
                customdata=tipos_plot,
                hovertemplate=(
                    "<b>%{y}</b><br>"
                    "Quantidade: %{x}<extra></extra>"
                ),
            )
        )

        fig_tipos.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=0, r=40, t=10, b=0),
            height=max(300, len(tipos_plot) * 45),
            showlegend=False,
            xaxis=dict(
                visible=False,
                showgrid=False,
            ),
            yaxis=dict(
                color="rgba(255,255,255,0.85)",
                tickfont=dict(size=12),
                showgrid=False,
                autorange="reversed",
            ),
            bargap=0.3,
        )

        event_tipo = st.plotly_chart(
            fig_tipos,
            use_container_width=True,
            config={"displayModeBar": False},
            on_select="rerun",
            key=f"chart_tipos_{selected_colab}",
        )

        # Identificar a barra selecionada
        if (
            event_tipo
            and hasattr(event_tipo, "selection")
            and event_tipo.selection
            and event_tipo.selection.points
        ):
            ponto = event_tipo.selection.points[0]
            tipo_clicado = ponto.get("y")

            if tipo_clicado:
                if selected_tipo == tipo_clicado:
                    selected_tipo = None
                else:
                    selected_tipo = tipo_clicado

                st.session_state[tipo_key] = selected_tipo

        # Aplicar filtro pelo tipo de servico selecionado
        if selected_tipo is not None:
            df_dia = df_dia[
                df_dia["Tipo de Solicitação"] == selected_tipo
            ]

            st.markdown(
                '<div style="display:inline-flex;align-items:center;gap:8px;'
                'background:rgba(255,179,71,0.12);'
                'border:1px solid rgba(255,179,71,0.3);'
                'border-radius:20px;padding:6px 16px;margin:4px 0 12px 0;">'
                '<span style="color:#FFB347;font-size:13px;font-weight:600;">'
                'Filtrado por: '
                + str(selected_tipo)
                + '</span>'
                '<span style="color:rgba(255,255,255,0.4);font-size:11px;">'
                'Clique novamente na barra para limpar'
                '</span></div>',
                unsafe_allow_html=True,
            )

        # Botao para limpar o filtro
        if selected_tipo is not None:
            if st.button(
                "Limpar filtro de tipo de serviço",
                key=f"limpar_tipo_{selected_colab}",
            ):
                st.session_state[tipo_key] = None
                st.rerun()

    st.markdown(
        "<div style='height: 24px'></div>",
        unsafe_allow_html=True,
    )

    # ---------------------------------------------------------------------------
    # Tabela e Download (colaborador selecionado OU dia selecionado)
    # ---------------------------------------------------------------------------
    show_table = (
        (not is_todos or selected_dia is not None)
        and not df_dia.empty
    )

    if show_table:
        titulo_tabela = "Detalhamento"

        if not is_todos:
            titulo_tabela += (
                " — " + selected_colab.split("(")[0].strip()
            )

        if selected_dia is not None:
            titulo_tabela += (
                " — " + selected_dia.strftime("%d/%m/%Y")
            )

        st.markdown(
            f'<div class="section-title">{titulo_tabela}</div>',
            unsafe_allow_html=True,
        )

        available_cols = colunas_visiveis(df_dia)
        df_display = df_dia[available_cols].copy()
        df_display = df_display.sort_values(
            "Data Tramite",
            ascending=True,
        )

        for col in ["Data Tramite", "Data Pedido"]:
            if col in df_display.columns:
                df_display[col] = df_display[col].dt.strftime(
                    "%d/%m/%Y %H:%M"
                )

        st.dataframe(
            df_display,
            use_container_width=True,
            height=min(38 + 4 * 35, 38 + len(df_display) * 35),
            hide_index=True,
        )

        st.markdown(
            "<div style='height: 8px'></div>",
            unsafe_allow_html=True,
        )

        excel_data = to_excel_download(df_dia)

        label_parts = ["Baixar Excel"]

        if not is_todos:
            label_parts.append(
                selected_colab.split("(")[0].strip()
            )

        if selected_dia is not None:
            label_parts.append(selected_dia.strftime("%d/%m"))

        download_label = " - ".join(label_parts)

        fname_parts = ["OS"]

        if not is_todos:
            fname_parts.append(
                selected_colab.replace(" ", "_")
            )

        if selected_dia is not None:
            fname_parts.append(
                selected_dia.strftime("%Y%m%d")
            )

        fname_parts.append(
            datetime.now(BR_TZ).strftime("%H%M")
        )

        download_fname = "_".join(fname_parts) + ".xlsx"

        downloaded = st.download_button(
            label=download_label,
            data=excel_data,
            file_name=download_fname,
            mime=(
                "application/vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet"
            ),
            key=(
                f"btn_download_"
                f"{hash(str(selected_colab) + str(selected_dia)) % 99999}"
            ),
            use_container_width=True,
        )

        if downloaded and not is_todos:
            add_audit_entry(selected_colab, "download")



# ---------------------------------------------------------------------------
# Base do mapa: respeita tipo e dia, mas nao o colaborador
# (o mapa tem o proprio seletor no painel da esquerda)
# ---------------------------------------------------------------------------
df_mapa = df
if selected_tipos:
    df_mapa = df_mapa[df_mapa["Tipo de Solicitação"].isin(selected_tipos)]
if selected_dia is not None:
    df_mapa = df_mapa[df_mapa["Data Tramite"].dt.date == selected_dia]

with tab_mapa:
    # O colaborador vem do seletor da sidebar; aqui so escolhemos a leitura do mapa.
    foco_mapa = "Todos" if is_todos else selected_colab

    col_filtro, col_mapa = st.columns([1, 3.6], gap="medium")

    with col_filtro:
        if is_todos:
            st.markdown(
                '<p style="color: rgba(255,255,255,0.6); font-size: 12px;'
                ' text-transform: uppercase; letter-spacing: 1px; margin-bottom: 4px;">Visualizar</p>',
                unsafe_allow_html=True,
            )
            modo_mapa = st.radio(
                "Modo do mapa",
                ["Por responsavel", "Onde esta o atraso"],
                label_visibility="collapsed",
                key="modo_mapa",
            )
        else:
            modo_mapa = "Por responsavel"

        resumo = mapa_resumo(df_mapa) if is_todos else []

        if is_todos and modo_mapa == "Por responsavel" and resumo:
            st.markdown(
                '<p style="color: rgba(255,255,255,0.6); font-size: 12px;'
                ' text-transform: uppercase; letter-spacing: 1px; margin: 16px 0 6px 0;">Responsaveis</p>',
                unsafe_allow_html=True,
            )
            chave = []
            for _n, curto, cor, n_cid, n_os in resumo:
                chave.append(
                    '<div style="display:flex;align-items:flex-start;gap:8px;margin-bottom:6px;">'
                    f'<span style="width:11px;height:11px;border-radius:3px;background:{cor};'
                    'flex:0 0 auto;margin-top:3px;"></span>'
                    f'<span style="color:rgba(255,255,255,0.82);font-size:11px;line-height:1.3;">{curto}'
                    f'<br><span style="color:rgba(255,255,255,0.38);font-size:10px;">'
                    f'{n_cid} cidades &middot; {n_os} OS</span></span></div>'
                )
            st.markdown("".join(chave), unsafe_allow_html=True)
        elif not is_todos:
            lista = cidades_do_colaborador(df_dia, selected_colab)
            st.markdown(
                '<p style="color: rgba(255,255,255,0.6); font-size: 12px;'
                ' text-transform: uppercase; letter-spacing: 1px; margin-bottom: 6px;">'
                f'Suas cidades ({len(lista)})</p>',
                unsafe_allow_html=True,
            )
            itens = []
            for cidade, qtd in lista:
                destaque = "rgba(255,255,255,0.82)" if qtd else "rgba(255,255,255,0.45)"
                badge = (
                    f'<span style="color:#86b6ef;font-size:10px;font-weight:700;">{qtd}</span>'
                    if qtd else '<span style="color:rgba(255,255,255,0.25);font-size:10px;">0</span>'
                )
                itens.append(
                    '<div style="display:flex;justify-content:space-between;gap:8px;'
                    'padding:3px 0;border-bottom:1px solid rgba(255,255,255,0.05);">'
                    f'<span style="color:{destaque};font-size:11px;line-height:1.3;">{cidade}</span>'
                    f'{badge}</div>'
                )
            st.markdown(
                '<div style="max-height:620px;overflow-y:auto;padding-right:6px;">'
                + "".join(itens) + "</div>",
                unsafe_allow_html=True,
            )

    with col_mapa:
        fig_mapa, nota_mapa = build_mapa(df_dia if not is_todos else df_mapa, foco_mapa, modo_mapa)
        if fig_mapa is None:
            st.caption(nota_mapa or "Mapa indisponivel.")
        else:
            st.plotly_chart(
                fig_mapa,
                use_container_width=True,
                config={
                    "scrollZoom": True,
                    "displayModeBar": False,
                    "doubleClick": "reset",
                },
                key="mapa_rs",
            )

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
        # Nota dos filtros ativos (dia + tipo + colaborador vindos do topo da tela)
        filtros_ativos = []
        if not is_todos:
            filtros_ativos.append(selected_colab.split("(")[0].strip())
        if selected_tipos:
            filtros_ativos.append(selected_tipos[0] if len(selected_tipos) == 1
                                  else f"{len(selected_tipos)} tipos de servico")
        if selected_dia is not None:
            filtros_ativos.append(selected_dia.strftime("%d/%m/%Y"))
        if filtros_ativos:
            st.markdown(
                '<div style="display:inline-flex;align-items:center;gap:8px;'
                'background:rgba(0,212,170,0.12);border:1px solid rgba(0,212,170,0.3);'
                'border-radius:20px;padding:6px 16px;margin-bottom:12px;">'
                '<span style="color:#00D4AA;font-size:13px;font-weight:600;">Filtrado por: '
                + " · ".join(filtros_ativos) + "</span></div>",
                unsafe_allow_html=True,
            )

        col_chart1, col_chart2 = st.columns(2)

        with col_chart1:
            st.markdown('<div class="section-title">Top 15 Cidades com Mais OS Pendente</div>', unsafe_allow_html=True)
            # df_dia ja carrega dia + tipo + colaborador selecionados no topo
            if "Zona Ligacao" in df_dia.columns and not df_dia.empty:
                df_city = df_dia.copy()
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
                st.info("Sem OS para os filtros selecionados.")

        with col_chart2:
            st.markdown('<div class="section-title">OS Pendente por Colaborador</div>', unsafe_allow_html=True)
            # Ranking recalculado sobre o dia + tipo selecionados (todos os colaboradores)
            dist_adm = distribute_os(df_mapa)
            colab_os = {name: len(d) for name, d in dist_adm.items() if not d.empty}
            colab_os = dict(sorted(colab_os.items(), key=lambda x: x[1], reverse=False))
            full_names = list(colab_os.keys())
            names = [n.split("(")[0].strip() for n in full_names]
            values = list(colab_os.values())
            short_to_full = {c.split("(")[0].strip(): c for c in COLABORADORES_ZONAS}
            if values:
                # destaca o colaborador escolhido; esmaece os demais
                if is_todos:
                    cores = ["#00C896"] * len(full_names)
                else:
                    cores = ["#00C896" if n == selected_colab else "rgba(0,200,150,0.25)"
                             for n in full_names]
                fig_colab = go.Figure(go.Bar(
                    x=values,
                    y=names,
                    orientation="h",
                    text=values,
                    textposition="outside",
                    textfont=dict(color="white", size=12, family="Arial"),
                    marker=dict(color=cores),
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
                ev_colab = st.plotly_chart(
                    fig_colab, use_container_width=True,
                    config={"displayModeBar": False},
                    on_select="rerun", key="adm_colab_sel",
                )
                # Clicar numa barra seleciona o colaborador no topo (filtra tudo)
                if ev_colab and ev_colab.selection and ev_colab.selection.points:
                    clicado = ev_colab.selection.points[0].get("y")
                    full = short_to_full.get(clicado)
                    if full and full != selected_colab:
                        st.session_state["_colab_click_pending"] = full
                        st.rerun()
                if is_todos:
                    st.caption("Clique numa barra para filtrar todo o painel por aquele colaborador. "
                               "Para voltar a todos, use o seletor na barra lateral.")
            else:
                st.info("Nenhuma OS para os filtros selecionados.")

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
