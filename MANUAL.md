# Manual de Instrucoes - Automacao Faturamento

---

## 1. Estrutura do Projeto

```
automacao-fat/
  .streamlit/config.toml   ← Cores e tema do dashboard
  app.py                   ← Codigo principal (zonas, login, layout)
  requirements.txt         ← Dependencias Python
  run.sh                   ← Script de inicializacao local
```

Tudo que voce precisa editar esta em **dois arquivos**: `app.py` e `.streamlit/config.toml`.

---

## 2. Como Subir o Repositorio no GitHub

### Passo a passo

1. Acesse [github.com/new](https://github.com/new)
2. Em **Repository name**, digite: `automacao-fat`
3. Selecione **Private** (recomendado)
4. Clique em **Create repository**
5. No terminal (local ou nesta sessao), execute:

```bash
cd automacao-fat
git remote add origin https://github.com/SEU_USUARIO/automacao-fat.git
git push -u origin main
```

---

## 3. Como Publicar no Streamlit Cloud (gerar o link)

### Passo a passo

1. Acesse [share.streamlit.io](https://share.streamlit.io)
2. Faca login com sua conta GitHub
3. Clique em **New app**
4. Preencha:
   - **Repository**: `SEU_USUARIO/automacao-fat`
   - **Branch**: `main`
   - **Main file path**: `app.py`
5. Clique em **Deploy!**

O Streamlit vai gerar um link publico no formato:

```
https://SEU_USUARIO-automacao-fat-app-XXXX.streamlit.app
```

Compartilhe esse link com a equipe.

> Toda vez que voce fizer um commit no GitHub, o Streamlit Cloud
> atualiza o app automaticamente em poucos segundos.

---

## 4. Como Editar as Zonas dos Colaboradores

Este e o passo mais importante. Cada colaborador precisa ter suas zonas atribuidas.

### Onde editar

**Arquivo:** `app.py`
**Linha:** aproximadamente 251 (procure por `COLABORADORES_ZONAS`)

### Como acessar pelo GitHub

1. Va ao repositorio no GitHub: `github.com/SEU_USUARIO/automacao-fat`
2. Clique no arquivo `app.py`
3. Clique no icone de lapis (Edit this file) no canto superior direito
4. Localize o bloco `COLABORADORES_ZONAS`

### O que editar

Voce vai encontrar isso:

```python
COLABORADORES_ZONAS = {
    # "Colaborador 01": [],  # Preencher com as zonas
    # "Colaborador 02": [],  # Preencher com as zonas
    # ...
}
```

**Descomente** (remova o `#` da frente) e preencha com o nome real e as zonas.
Exemplo preenchido:

```python
COLABORADORES_ZONAS = {
    "Maria Silva": [1, 2, 5, 7, 8, 9, 10, 11, 12],
    "Joao Santos": [13, 14, 15, 19, 20, 21, 22, 23],
    "Ana Costa": [27, 28, 29, 30, 31, 34, 35, 37],
    "Pedro Lima": [38, 39, 40, 42, 43, 44, 45, 46],
    "Carla Souza": [48, 49, 50, 51, 53, 54, 56, 57],
    "Lucas Oliveira": [58, 61, 62, 63, 64, 65, 68, 69],
    "Fernanda Rocha": [70, 72, 73, 74, 75, 77, 79, 80],
    "Ricardo Alves": [81, 82, 83, 84, 85, 86, 87, 89],
    "Juliana Dias": [90, 93, 94, 95, 96, 97, 98, 100],
    "Bruno Martins": [101, 102, 103, 104, 105, 106, 107, 109],
    "Patricia Reis": [110, 114, 116, 117, 118, 119, 121, 122],
    "Gustavo Nunes": [123, 127, 129, 130, 131, 133, 136, 139],
    "Amanda Ferreira": [140, 143, 145, 146, 147, 148, 149, 150],
    "Diego Cardoso": [151, 153, 154, 155, 156, 157, 160, 161],
    "Sabrina Teixeira": [162, 164, 165, 166, 167, 168, 169, 170],
}
```

### Regras importantes

- Os nomes devem estar entre **aspas** `"Nome Sobrenome"`
- As zonas sao **numeros** separados por virgula dentro de **colchetes** `[1, 2, 3]`
- Cada linha termina com **virgula** `,`
- A ultima linha tambem leva virgula
- Nao repita zonas entre colaboradores (cada zona pertence a um unico responsavel)

### Como salvar

1. Apos editar, role para baixo no GitHub
2. Escreva uma mensagem de commit, ex: `Atualiza zonas dos colaboradores`
3. Clique em **Commit changes**
4. O Streamlit Cloud atualiza automaticamente

---

## 5. Como Alterar o Login ADM

### Onde editar

**Arquivo:** `app.py`
**Linha:** aproximadamente 272 (procure por `ADMIN_USER`)

### Valores atuais

```python
ADMIN_USER = "admin"
ADMIN_PASS = "fat2026"
```

### Para alterar

Troque os valores entre aspas:

```python
ADMIN_USER = "seu_usuario"
ADMIN_PASS = "sua_senha_segura"
```

---

## 6. Como Editar Cores e Tema do Dashboard

### 6.1 Cores gerais (tema Streamlit)

**Arquivo:** `.streamlit/config.toml`

```toml
[theme]
primaryColor = "#00C896"               # Cor principal (botoes, destaques)
backgroundColor = "#0A1628"            # Fundo da pagina
secondaryBackgroundColor = "#131D35"   # Fundo de cards e sidebar
textColor = "#FFFFFF"                  # Cor do texto
```

Para alterar, troque os codigos hexadecimais. Exemplos de paletas:

| Estilo          | primaryColor | backgroundColor | secondaryBg  | textColor |
|-----------------|-------------|-----------------|-------------|-----------|
| Azul escuro (atual) | `#00C896` | `#0A1628` | `#131D35` | `#FFFFFF` |
| Preto moderno   | `#6C63FF`   | `#0D0D0D`       | `#1A1A2E`   | `#FFFFFF` |
| Cinza corporativo | `#2196F3` | `#1E1E1E`       | `#2D2D2D`   | `#E0E0E0` |
| Claro           | `#00C896`   | `#FFFFFF`       | `#F0F2F6`   | `#1A1A1A` |

### 6.2 Cores dos cards de metricas

**Arquivo:** `app.py`
Procure por `/* Card laranja */`, `/* Card ciano */`, etc. no bloco CSS (entre as linhas 79 e 128).

Cada card tem um gradiente com duas cores:

```css
/* Card laranja - Total de OS */
.card-orange {
    background: linear-gradient(135deg, #FF9A2E 0%, #FFB347 100%);
}

/* Card ciano - Dia mais atrasado */
.card-cyan {
    background: linear-gradient(135deg, #00D4AA 0%, #4DE8C8 100%);
}

/* Card vermelho - Dias de atraso */
.card-red {
    background: linear-gradient(135deg, #FF4D4D 0%, #FF6B6B 100%);
}

/* Card branco - Colaboradores presentes */
.card-white {
    background: linear-gradient(135deg, #E8EDF5 0%, #FFFFFF 100%);
}

/* Card azul escuro - Distribuicao por colaborador */
.card-dark {
    background: linear-gradient(135deg, #1A2D4A 0%, #243B5C 100%);
}
```

Troque as cores hex para personalizar. O primeiro valor e o canto superior esquerdo, o segundo e o canto inferior direito do gradiente.

### 6.3 Cor do grafico de barras

**Arquivo:** `app.py`
Procure por `st.bar_chart` (linha 617):

```python
st.bar_chart(os_dia_df.set_index("Data"), color="#00C896", height=300)
```

Troque `#00C896` pela cor desejada.

### 6.4 Cor dos botoes de download

**Arquivo:** `app.py`
Procure por `.stDownloadButton` no CSS (linha 215):

```css
.stDownloadButton > button {
    background: linear-gradient(135deg, #00C896 0%, #00A87A 100%) !important;
}
```

---

## 7. Como Editar o Layout

### 7.1 Alterar quantidade de cards por linha

**Arquivo:** `app.py`
Procure por `cols_per_row` (linha 593):

```python
cols_per_row = 5  # Mude para 3, 4 ou 5
```

### 7.2 Alterar metricas exibidas no topo

Procure por `# Metricas principais` (linha 501). As 4 colunas sao `col1, col2, col3, col4`.
Para trocar a ordem, mova os blocos `with col1:`, `with col2:`, etc.

Para alterar o icone de um card, troque o primeiro parametro do `render_metric_card`:

```python
render_metric_card(
    "📋",           # ← Icone (emoji)
    f"{total_os}",   # ← Valor grande
    "Total de OS",   # ← Texto descritivo
    "card-orange"    # ← Classe de cor (card-orange, card-cyan, card-red, card-white, card-dark)
)
```

### 7.3 Alterar proporcao das colunas

Procure por `st.columns([3, 2])` (linha 534). Os numeros definem a proporcao:
- `[3, 2]` = coluna esquerda ocupa 60%, direita 40%
- `[1, 1]` = ambas iguais (50/50)
- `[2, 1]` = esquerda 66%, direita 33%

### 7.4 Alterar tamanho das fontes

No CSS, procure por `.metric-value` (linha 66):

```css
.metric-card .metric-value {
    font-size: 42px;   /* Tamanho do numero grande */
}
.metric-card .metric-label {
    font-size: 13px;   /* Tamanho do texto descritivo */
}
```

---

## 8. Fluxo de Uso Diario

```
1. Extraia o arquivo Excel do SCAE
2. Acesse o link do Streamlit (compartilhado)
3. Na barra lateral, faca upload do arquivo .xlsx
4. Os dados sao processados automaticamente
5. Selecione seu nome e clique em "Baixar Excel"
6. (ADM) Faca login para gerenciar ausencias e ver auditoria
```

---

## 9. Dicas Uteis

- **Para encontrar qualquer trecho no GitHub:** abra o arquivo `app.py`, pressione `Ctrl+F` (ou `Cmd+F` no Mac) e busque pelo texto
- **Cores hexadecimais:** use [htmlcolorcodes.com](https://htmlcolorcodes.com/pt/) para escolher cores
- **Erro ao subir:** verifique se o `requirements.txt` esta no repositorio
- **App nao atualiza:** va ao painel do Streamlit Cloud e clique em "Reboot app"
- **Para rodar localmente:** execute `./run.sh` no terminal
