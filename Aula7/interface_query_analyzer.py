import os
import json
import re
import unicodedata
from collections import Counter
from datetime import datetime, time, timezone
from pathlib import Path

from rank_bm25 import BM25Okapi
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

# CONFIGURAÇÃO STREAMLIT
st.set_page_config(
    page_title="Assistente RAG",
    page_icon="💬",
    layout="wide",
)

# CAMINHOS
BASE_DIR = Path(__file__).resolve().parent

CAMINHO_FAISS = BASE_DIR / "faiss_index"

CAMINHO_INDEX = CAMINHO_FAISS / "index.faiss"
CAMINHO_PKL = CAMINHO_FAISS / "index.pkl"

CAMINHO_ENV = BASE_DIR / ".env"

# CONFIGURAÇÕES
MODELO_EMBEDDING = (
    "sentence-transformers/all-MiniLM-L6-v2"
)

MODELO_LLM = "gpt-5.4-mini"

# Quantidade final de chunks recuperados
K_BUSCA = 5

# Quantidade de candidatos por mecanismo antes da fusão
K_DENSO = 20
K_BM25 = 20

# O FAISS precisa buscar mais candidatos quando há filtro,
# pois o filtro é aplicado durante a recuperação do VectorStore.
FETCH_K_DENSO = 100

# Constante clássica do Reciprocal Rank Fusion
RRF_K = 60

# Pesos padrão da fusão final.
PESO_DENSO = 0.5
PESO_BM25 = 0.5

# Quando algum termo importante da pergunta não existe literalmente
# na base, a expansão lexical ganha mais peso no ranking final.
PESO_DENSO_COM_EXPANSAO = 0.35
PESO_BM25_COM_EXPANSAO = 0.65

# Pesos internos do ranking BM25 híbrido: consulta original + expansão.
PESO_BM25_ORIGINAL = 0.70
PESO_BM25_EXPANDIDO = 0.30
PESO_BM25_ORIGINAL_COM_TERMO_AUSENTE = 0.40
PESO_BM25_EXPANDIDO_COM_TERMO_AUSENTE = 0.60

# Limite de termos adicionais sugeridos pelo Query Analyzer.
MAX_TERMOS_EXPANDIDOS = 8

# METADADOS USADOS PELO QUERY ANALYZER
# Campos com vocabulário pequeno/fechado.
CAMPOS_CATEGORICOS = [
    "file_type",
    "document_nature",
    "doc_type",
    "sensitivity",
    "domain",
    "category",
    "module",
    "department",
    "priority",
    "status",
    "state",
]

# Campos normalmente mencionados como identificadores explícitos.
CAMPOS_IDENTIFICADORES = [
    "source_file",
    "ticket_id",
    "customer_id",
    "employee_id",
]

# h1/h2/h3, chunk_id, chunk_index, chunk_strategy, row, line e page
# permanecem disponíveis no contexto/diagnóstico, mas não são usados
# como filtros automáticos neste baseline.
CAMPOS_FILTRAVEIS = (
    CAMPOS_CATEGORICOS
    + CAMPOS_IDENTIFICADORES
)

# ALIASES CONTROLADOS DE METADADOS
# Esses aliases resolvem diferenças de vocabulário sem relaxar
# a intenção do usuário. Ex.:
# "VendeFácil Estoque" e "estoque" representam o mesmo módulo.

ALIASES_METADADOS = {
    "module": {
        "estoque": {
            "estoque",
            "vendefacil estoque",
        },
        "pay": {
            "pay",
            "vendefacil pay",
        },
        "pdv": {
            "pdv",
            "vendefacil pdv",
        },
        "analytics": {
            "analytics",
            "vendefacil analytics",
        },
        "ecommerce": {
            "ecommerce",
            "vendefacil loja",
            "loja",
        },
    },
    "domain": {
        "estoque": {
            "estoque",
            "vendefacil estoque",
        },
        "pay": {
            "pay",
            "vendefacil pay",
        },
        "pdv": {
            "pdv",
            "vendefacil pdv",
        },
        "analytics": {
            "analytics",
            "vendefacil analytics",
        },
        "ecommerce": {
            "ecommerce",
            "vendefacil loja",
            "loja",
        },
    },
}

CAMPO_DATA = "date"

# CARREGAR .ENV
load_dotenv(
    dotenv_path=CAMINHO_ENV
)

OPENAI_API_KEY = os.getenv(
    "OPENAI_API_KEY"
)


if not OPENAI_API_KEY:

    st.error(
        "OPENAI_API_KEY não encontrada no arquivo .env"
    )

    st.stop()

# VERIFICAR ARQUIVOS
if not CAMINHO_INDEX.exists():

    st.error(
        f"""
index.faiss não encontrado.

Caminho esperado:

{CAMINHO_INDEX}
"""
    )

    st.stop()


if not CAMINHO_PKL.exists():

    st.error(
        f"""
index.pkl não encontrado.

Caminho esperado:

{CAMINHO_PKL}
"""
    )

    st.stop()

# OPENAI
@st.cache_resource
def carregar_openai():

    return OpenAI(
        api_key=OPENAI_API_KEY
    )

# EMBEDDINGS
@st.cache_resource
def carregar_embeddings():

    return HuggingFaceEmbeddings(

        model_name=MODELO_EMBEDDING,

        model_kwargs={
            "device": "cpu"
        },

        encode_kwargs={
            "normalize_embeddings": True,
            "batch_size": 64,
        },
    )

# VECTORSTORE
@st.cache_resource
def carregar_vectorstore():

    embeddings = carregar_embeddings()

    return FAISS.load_local(

        folder_path=str(CAMINHO_FAISS),

        embeddings=embeddings,

        # Use apenas para um index.pkl confiável
        allow_dangerous_deserialization=True,
    )

# CARREGAR SISTEMA
try:

    client = carregar_openai()

    vectorstore = carregar_vectorstore()

except Exception as erro:

    st.error(
        "Erro ao carregar o sistema."
    )

    st.exception(
        erro
    )

    st.stop()

# INFORMAÇÕES DO ÍNDICE
quantidade_vetores = (
    vectorstore.index.ntotal
)
dimensao_faiss = (
    vectorstore.index.d
)
quantidade_mapeamentos = len(
    vectorstore.index_to_docstore_id
)

# VALIDAR ÍNDICE
if quantidade_vetores != quantidade_mapeamentos:
    st.warning(
        f"""
O número de vetores é diferente do número de documentos
mapeados pelo index.pkl.

Vetores FAISS: {quantidade_vetores}

Mapeamentos: {quantidade_mapeamentos}
"""
    )


# CATÁLOGO DE DOCUMENTOS, BM25 E QUERY ANALYZER

def normalizar_texto(texto: str) -> str:
    """Normalização simples usada apenas pela busca BM25."""
    texto = str(texto).lower()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(
        caractere
        for caractere in texto
        if not unicodedata.combining(caractere)
    )
    return texto


# Stopwords em português normalizadas (sem acentos), porque
# normalizar_texto() remove diacríticos antes da tokenização.
STOPWORDS_PT = {
    "a", "ao", "aos", "as", "o", "os",
    "um", "uma", "uns", "umas",
    "de", "da", "das", "do", "dos",
    "em", "na", "nas", "no", "nos",
    "para", "por", "com", "sem",
    "e", "ou", "mas",
    "que", "qual", "quais",
    "como", "quando", "onde",
    "e", "sao", "ser", "foi", "foram",
    "tem", "ter", "tinha", "tenham",
    "me", "meu", "minha", "meus", "minhas",
    "se", "sobre", "isso", "isto", "essa", "esse",
    "essas", "esses", "esta", "este", "estas", "estes",
    "dos", "das", "pelo", "pela", "pelos", "pelas",
}


CAMPOS_BM25_METADATA = [
    "source_file",
    "h1",
    "h2",
    "h3",
    "doc_type",
    "category",
    "department",
    "domain",
    "module",
]


def construir_texto_bm25(texto: str, metadados: dict) -> str:
    """
    Monta o texto pesquisável do BM25.

    Além do page_content, inclui metadados semânticos como h1/h2/h3,
    nome do arquivo, domínio e módulo. Isso é importante quando o termo
    consultado aparece no título/seção, mas não foi repetido no chunk.
    """
    partes = [str(texto)]

    for campo in CAMPOS_BM25_METADATA:
        valor = metadados.get(campo)

        if valor is None or valor == "":
            continue

        if isinstance(valor, (list, tuple, set)):
            partes.extend(str(item) for item in valor)
        else:
            partes.append(str(valor))

    return "\n".join(partes)


def tokenizar_bm25(texto: str) -> list[str]:
    """
    Tokeniza texto para BM25 removendo stopwords e tokens muito curtos.

    Exemplo:
        "Quais são as regras para férias?"
    vira aproximadamente:
        ["regras", "ferias"]
    """
    texto = normalizar_texto(texto)

    tokens = re.findall(
        r"\b[\w-]+\b",
        texto,
        flags=re.UNICODE,
    )

    return [
        token
        for token in tokens
        if token not in STOPWORDS_PT
        and len(token) > 2
    ]


@st.cache_data
def construir_base_bm25():
    """
    Extrai os chunks do docstore e cria um corpus lexical enriquecido
    com metadados semânticos. Também calcula a frequência documental
    dos termos para diagnóstico.
    """
    documentos = []
    corpus_tokenizado = []
    frequencia_documental = Counter()

    for indice_faiss, docstore_id in (
        vectorstore.index_to_docstore_id.items()
    ):
        documento = vectorstore.docstore.search(docstore_id)

        if not hasattr(documento, "page_content"):
            continue

        texto_bm25 = construir_texto_bm25(
            documento.page_content,
            documento.metadata,
        )
        tokens_bm25 = tokenizar_bm25(texto_bm25)
        tokens_unicos = set(tokens_bm25)

        documentos.append(
            {
                "indice_faiss": indice_faiss,
                "docstore_id": docstore_id,
                "texto": documento.page_content,
                "texto_bm25": texto_bm25,
                "tokens_bm25": tokens_bm25,
                "tokens_bm25_set": tokens_unicos,
                "metadados": documento.metadata,
            }
        )
        corpus_tokenizado.append(tokens_bm25)
        frequencia_documental.update(tokens_unicos)

    bm25 = BM25Okapi(corpus_tokenizado)

    return documentos, bm25, dict(frequencia_documental)


(
    DOCUMENTOS_BM25,
    INDICE_BM25,
    FREQUENCIA_DOCUMENTAL_BM25,
) = construir_base_bm25()


def diagnosticar_termos_query(query: str) -> list[dict]:
    """Mostra em quantos chunks cada termo lexical da pergunta aparece."""
    termos = list(dict.fromkeys(tokenizar_bm25(query)))
    total = len(DOCUMENTOS_BM25)
    diagnostico = []

    for termo in termos:
        quantidade = int(FREQUENCIA_DOCUMENTAL_BM25.get(termo, 0))
        diagnostico.append(
            {
                "termo": termo,
                "chunks": quantidade,
                "percentual": (quantidade / total) if total else 0.0,
                "existe_na_base": quantidade > 0,
            }
        )

    return diagnostico



def construir_catalogo_metadados():
    """
    Constrói um vocabulário somente para campos que fazem sentido
    como filtros automáticos. Datas são resumidas por mínimo/máximo,
    evitando enviar milhares de timestamps ao LLM.
    """
    catalogo = {
        campo: set()
        for campo in CAMPOS_FILTRAVEIS
    }

    datas_validas = []

    for item in DOCUMENTOS_BM25:
        metadata = item["metadados"]

        for campo in CAMPOS_FILTRAVEIS:
            valor = metadata.get(campo)

            if valor is None or valor == "":
                continue

            if isinstance(valor, (list, tuple, set)):
                for parte in valor:
                    catalogo[campo].add(str(parte))
            else:
                catalogo[campo].add(str(valor))

        valor_data = metadata.get(CAMPO_DATA)
        data_convertida = converter_data_metadata(valor_data)
        if data_convertida is not None:
            datas_validas.append(data_convertida)

    resultado = {
        campo: sorted(valores)
        for campo, valores in catalogo.items()
    }

    if datas_validas:
        resultado["date_range"] = {
            "min": min(datas_validas).isoformat(sep=" "),
            "max": max(datas_validas).isoformat(sep=" "),
        }
    else:
        resultado["date_range"] = None

    return resultado


CATALOGO_METADADOS = None


def normalizar_datetime(dt):
    """
    Converte qualquer datetime para UTC sem tzinfo.

    Isso evita comparar datetimes offset-aware com offset-naive.
    Datas sem timezone são mantidas como horários locais/naive;
    datas com timezone são convertidas para UTC e depois ficam naive.
    """
    if dt is None:
        return None

    if dt.tzinfo is not None:
        dt = dt.astimezone(timezone.utc).replace(tzinfo=None)

    return dt


def converter_data_metadata(valor):
    """Converte datas dos metadados para datetime normalizado."""
    if valor is None or valor == "":
        return None

    if isinstance(valor, datetime):
        return normalizar_datetime(valor)

    texto = str(valor).strip().replace("Z", "+00:00")

    formatos = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
        "%d/%m/%Y %H:%M:%S",
        "%d/%m/%Y",
    ]

    try:
        return normalizar_datetime(
            datetime.fromisoformat(texto)
        )
    except ValueError:
        pass

    for formato in formatos:
        try:
            return normalizar_datetime(
                datetime.strptime(texto, formato)
            )
        except ValueError:
            continue

    return None


def normalizar_limite_data(valor, fim=False):
    """
    Valida datas produzidas pelo Query Analyzer e sempre devolve
    datetime sem tzinfo, compatível com converter_data_metadata().
    """
    if valor in (None, ""):
        return None

    texto = str(valor).strip().replace("Z", "+00:00")

    try:
        if len(texto) == 10:
            data = datetime.strptime(texto, "%Y-%m-%d").date()
            return datetime.combine(
                data,
                time.max if fim else time.min,
            )

        return normalizar_datetime(
            datetime.fromisoformat(texto)
        )
    except ValueError:
        return None


# Agora que converter_data_metadata existe, podemos construir o catálogo.
CATALOGO_METADADOS = construir_catalogo_metadados()


def limpar_json_llm(texto: str) -> dict:
    """
    Aceita JSON puro ou JSON envolvido em ```json ... ```.
    """
    texto = texto.strip()

    if texto.startswith("```"):
        texto = re.sub(
            r"^```(?:json)?\s*",
            "",
            texto,
            flags=re.IGNORECASE,
        )
        texto = re.sub(
            r"\s*```$",
            "",
            texto,
        )

    return json.loads(texto)


def analisar_query(pergunta: str) -> dict:
    """
    Query Analyzer com saídas para recuperação e consultas analíticas:
    - query_semantica: versão limpa da intenção;
    - query_expandida: versão enriquecida apenas para recuperação;
    - termos_expandidos: sinônimos/termos relacionados para recall lexical;
    - filtros estruturados e intervalo temporal;
    - operação analítica opcional: todos, algum, contar ou distribuição;
    - campo/valor avaliado quando a pergunta exige agregação.

    A expansão é usada SOMENTE para recuperar candidatos. Ela nunca autoriza
    o LLM final a responder algo que não esteja sustentado pelos documentos.
    """
    catalogo_json = json.dumps(
        CATALOGO_METADADOS,
        ensure_ascii=False,
        indent=2,
    )

    instrucoes = f"""
Você é um Query Analyzer para um sistema RAG empresarial.

Extraia restrições de metadados somente quando estiverem EXPLICITAMENTE
presentes ou forem inequivocamente exigidas pela pergunta.

CAMPOS CATEGÓRICOS PERMITIDOS:
{', '.join(CAMPOS_CATEGORICOS)}

IDENTIFICADORES PERMITIDOS:
{', '.join(CAMPOS_IDENTIFICADORES)}

CAMPO TEMPORAL:
date

Além dos filtros, gere uma expansão de recuperação:
- query_semantica: preserve a intenção original em linguagem natural;
- query_expandida: reescreva a pergunta acrescentando termos úteis para
  recuperação, sem mudar a intenção;
- termos_expandidos: no máximo {MAX_TERMOS_EXPANDIDOS} palavras ou expressões
  curtas relacionadas ao conceito central. Não inclua stopwords.

REGRAS:
- Não invente filtros.
- Não converta um mero assunto em filtro estrutural.
- Ex.: "regras para férias" -> filtros={{}}.
- Ex.: "regras para férias nas políticas" -> category="policies".
- Ex.: "tickets críticos abertos" -> doc_type="ticket",
  priority="Crítica", status="Aberto", se esses valores existirem.
- Para identificadores, use apenas valores existentes no catálogo.
- Se identificar um source_file específico, NÃO infira doc_type, category,
  domain, module, department ou outros filtros adicionais apenas pelo significado
  do nome do arquivo. Só inclua outro filtro se ele estiver explicitamente pedido
  pelo usuário e for compatível com o mesmo documento.
- Todos os filtros retornados precisam poder coexistir no MESMO documento.
  Nunca retorne uma combinação apenas porque cada valor existe isoladamente
  em algum ponto do catálogo.
- module e domain podem possuir aliases equivalentes. Exemplos:
  "VendeFácil Estoque" = "estoque",
  "VendeFácil Pay" = "pay",
  "VendeFácil PDV" = "pdv".
  Prefira a variante que coexistir com os demais filtros da consulta.
- Ex.: se source_file="codigo_de_conduta.md" existir, não suponha que
  doc_type="manual" ou category="policies" sem evidência de coexistência.
- Para datas, converta expressões temporais para intervalo ISO.
  Ex.: "fevereiro de 2026" -> 2026-02-01 até 2026-02-28.
- Se não houver restrição temporal, use null nos dois limites.
- h1, h2, h3, chunk_id, chunk_index, chunk_strategy, row, line e page
  NÃO devem ser usados como filtros automáticos.
- A expansão deve ser conservadora: termos relacionados podem ampliar a busca,
  mas não devem pressupor fatos que não foram perguntados.
- Além de "filtros", devolva "filtros_explicitos" com os nomes dos campos
  que correspondem a restrições explicitamente pedidas pelo usuário.
- Se a pergunta disser "restritos", sensitivity é explícito.
- Se disser "módulo Pay" ou "sobre o módulo Pay", module é explícito.
- Se disser "tickets", doc_type é explícito.
- Se disser "críticos", priority é explícito.
- Se disser "abertos", status é explícito EM PERGUNTAS DE LISTAGEM.
- Retorne também "data_explicita": true somente se houver restrição temporal.

CONSULTAS ANALÍTICAS / AGREGAÇÕES:
- Identifique perguntas que exigem examinar o CONJUNTO COMPLETO de registros,
  e não apenas recuperar os K documentos mais semelhantes.
- operacao_analitica pode ser:
  "nenhuma", "todos", "algum", "contar" ou "distribuicao".
- Para "todos", a condição testada NÃO deve ser usada como filtro da população.
- Exemplo:
  "Todos os tickets do estado de São Paulo foram resolvidos?"
  -> filtros = {{"doc_type":"ticket", "state":"SP"}}
  -> filtros_explicitos = ["doc_type", "state"]
  -> operacao_analitica = "todos"
  -> campo_avaliado = "status"
  -> valor_avaliado = "Resolvido"
- NÃO coloque status="Resolvido" em filtros nesse exemplo, porque isso eliminaria
  justamente os tickets não resolvidos que precisam ser examinados.
- Exemplo de LISTAGEM:
  "Quais tickets de SP estão resolvidos?"
  -> operacao_analitica = "nenhuma"
  -> filtros pode conter doc_type="ticket", state="SP", status="Resolvido".
- Exemplo:
  "Existe algum ticket crítico aberto?"
  -> operacao_analitica = "algum"
  -> campo_avaliado pode ser "status" com valor "Aberto" e os demais critérios
     permanecem como filtros da população.
- Para "contar", use a população completa necessária à contagem.
- Para "distribuicao", campo_avaliado é o campo cujos valores devem ser contados.
- campo_avaliado deve ser um campo categórico permitido ou null.
- valor_avaliado deve usar o vocabulário real do catálogo ou null.
- Retorne SOMENTE JSON válido.

Formato obrigatório:
{{
  "query_semantica": "texto",
  "query_expandida": "texto",
  "termos_expandidos": ["termo 1", "termo 2"],
  "filtros": {{
    "campo": "valor"
  }},
  "filtros_explicitos": ["campo1", "campo2"],
  "filtro_data": {{
    "inicio": null,
    "fim": null
  }},
  "data_explicita": false,
  "operacao_analitica": "nenhuma",
  "campo_avaliado": null,
  "valor_avaliado": null,
  "justificativa": "texto curto"
}}
"""

    entrada = f"""
CATÁLOGO REAL DE METADADOS:
{catalogo_json}

PERGUNTA:
{pergunta}
"""

    try:
        resposta = client.responses.create(
            model=MODELO_LLM,
            instructions=instrucoes,
            input=entrada,
        )

        analise = limpar_json_llm(resposta.output_text)

        query_semantica = str(
            analise.get("query_semantica", pergunta)
        ).strip() or pergunta

        query_expandida = str(
            analise.get("query_expandida", query_semantica)
        ).strip() or query_semantica

        termos_expandidos_brutos = analise.get("termos_expandidos", [])
        if not isinstance(termos_expandidos_brutos, list):
            termos_expandidos_brutos = []

        termos_expandidos = []
        vistos = set()
        for termo in termos_expandidos_brutos:
            termo = str(termo).strip()
            if not termo:
                continue
            chave = normalizar_texto(termo).strip()
            if not chave or chave in vistos:
                continue
            vistos.add(chave)
            termos_expandidos.append(termo)
            if len(termos_expandidos) >= MAX_TERMOS_EXPANDIDOS:
                break

        filtros_validos = {}
        filtros_brutos = analise.get("filtros", {})

        if isinstance(filtros_brutos, dict):
            for campo, valor in filtros_brutos.items():
                if campo not in CAMPOS_FILTRAVEIS:
                    continue

                permitidos = CATALOGO_METADADOS.get(campo, [])
                valor_normalizado = normalizar_texto(valor).strip()

                valor_canonico = next(
                    (
                        permitido
                        for permitido in permitidos
                        if normalizar_texto(permitido).strip()
                        == valor_normalizado
                    ),
                    None,
                )

                if valor_canonico is not None:
                    filtros_validos[campo] = valor_canonico

        # --------------------------------------------------------
        # CONSULTA ANALÍTICA
        # --------------------------------------------------------
        operacoes_permitidas = {
            "nenhuma",
            "todos",
            "algum",
            "contar",
            "distribuicao",
        }

        operacao_analitica = normalizar_texto(
            analise.get(
                "operacao_analitica",
                "nenhuma",
            )
        ).strip()

        if operacao_analitica not in operacoes_permitidas:
            operacao_analitica = "nenhuma"

        campo_avaliado = analise.get(
            "campo_avaliado"
        )

        if campo_avaliado is not None:
            campo_avaliado = str(
                campo_avaliado
            ).strip()

        if campo_avaliado not in CAMPOS_CATEGORICOS:
            campo_avaliado = None

        valor_avaliado = analise.get(
            "valor_avaliado"
        )

        valor_avaliado_canonico = None

        if (
            campo_avaliado
            and valor_avaliado not in (None, "")
        ):
            permitidos_avaliacao = CATALOGO_METADADOS.get(
                campo_avaliado,
                [],
            )

            alvo_avaliacao = normalizar_texto(
                valor_avaliado
            ).strip()

            valor_avaliado_canonico = next(
                (
                    permitido
                    for permitido in permitidos_avaliacao
                    if normalizar_texto(
                        permitido
                    ).strip() == alvo_avaliacao
                ),
                None,
            )

        # Regra de segurança lógica:
        # em uma verificação universal ("todos"), o campo avaliado
        # não pode filtrar a população, senão os contraexemplos somem.
        if (
            operacao_analitica == "todos"
            and campo_avaliado
            and valor_avaliado_canonico is not None
            and campo_avaliado in filtros_validos
            and valores_equivalentes(
                filtros_validos[campo_avaliado],
                valor_avaliado_canonico,
            )
        ):
            filtros_validos.pop(
                campo_avaliado,
                None,
            )

        filtros_explicitos_brutos = analise.get(
            "filtros_explicitos",
            [],
        )

        if not isinstance(
            filtros_explicitos_brutos,
            list,
        ):
            filtros_explicitos_brutos = []

        # Só aceitamos como explícitos campos que:
        # 1. são filtráveis;
        # 2. realmente sobreviveram à validação de vocabulário.
        filtros_explicitos = []
        for campo in filtros_explicitos_brutos:
            campo = str(campo).strip()
            if (
                campo in CAMPOS_FILTRAVEIS
                and campo in filtros_validos
                and campo not in filtros_explicitos
            ):
                filtros_explicitos.append(campo)

        if (
            operacao_analitica == "todos"
            and campo_avaliado in filtros_explicitos
        ):
            filtros_explicitos = [
                campo
                for campo in filtros_explicitos
                if campo != campo_avaliado
            ]

        filtro_data_bruto = analise.get("filtro_data", {})
        if not isinstance(filtro_data_bruto, dict):
            filtro_data_bruto = {}

        inicio = normalizar_limite_data(
            filtro_data_bruto.get("inicio"),
            fim=False,
        )
        fim = normalizar_limite_data(
            filtro_data_bruto.get("fim"),
            fim=True,
        )

        if inicio is not None and fim is not None and inicio > fim:
            inicio = None
            fim = None

        data_explicita = bool(
            analise.get(
                "data_explicita",
                False,
            )
        )

        return {
            "query_semantica": query_semantica,
            "query_expandida": query_expandida,
            "termos_expandidos": termos_expandidos,
            "filtros": filtros_validos,
            "filtros_explicitos": filtros_explicitos,
            "filtro_data": {
                "inicio": inicio,
                "fim": fim,
            },
            "data_explicita": data_explicita,
            "operacao_analitica": operacao_analitica,
            "campo_avaliado": campo_avaliado,
            "valor_avaliado": valor_avaliado_canonico,
            "justificativa": str(
                analise.get("justificativa", "")
            ),
        }

    except Exception as erro:
        return {
            "query_semantica": pergunta,
            "query_expandida": pergunta,
            "termos_expandidos": [],
            "filtros": {},
            "filtros_explicitos": [],
            "filtro_data": {
                "inicio": None,
                "fim": None,
            },
            "data_explicita": False,
            "operacao_analitica": "nenhuma",
            "campo_avaliado": None,
            "valor_avaliado": None,
            "justificativa": (
                "Query Analyzer indisponível; "
                f"busca executada sem filtros. Erro: {erro}"
            ),
        }


def valores_equivalentes(valor_metadata, valor_filtro) -> bool:
    """
    Compara metadados de forma tolerante a maiúsculas/minúsculas
    e também aceita campos multivalorados.
    """
    alvo = normalizar_texto(valor_filtro).strip()

    if isinstance(
        valor_metadata,
        (list, tuple, set),
    ):
        return any(
            normalizar_texto(item).strip() == alvo
            for item in valor_metadata
        )

    return (
        normalizar_texto(valor_metadata).strip()
        == alvo
    )



def canonizar_alias_metadata(
    campo: str,
    valor,
):
    """
    Retorna uma representação canônica para aliases de module/domain.

    Exemplos:
        VendeFácil Estoque -> estoque
        estoque            -> estoque
        VendeFácil Pay     -> pay
        pay                -> pay
    """
    if valor is None:
        return None

    valor_normalizado = normalizar_texto(
        valor
    ).strip()

    grupos = ALIASES_METADADOS.get(
        campo,
        {},
    )

    for canonico, aliases in grupos.items():
        aliases_normalizados = {
            normalizar_texto(alias).strip()
            for alias in aliases
        }

        if valor_normalizado in aliases_normalizados:
            return canonico

    return valor_normalizado


def valores_equivalentes_por_campo(
    campo: str,
    valor_metadata,
    valor_esperado,
) -> bool:
    """
    Compara valores considerando aliases controlados para module/domain.
    """
    if valor_metadata is None or valor_esperado is None:
        return False

    if isinstance(
        valor_metadata,
        (list, tuple, set),
    ):
        return any(
            valores_equivalentes_por_campo(
                campo,
                item,
                valor_esperado,
            )
            for item in valor_metadata
        )

    if isinstance(
        valor_esperado,
        (list, tuple, set),
    ):
        return any(
            valores_equivalentes_por_campo(
                campo,
                valor_metadata,
                item,
            )
            for item in valor_esperado
        )

    return (
        canonizar_alias_metadata(
            campo,
            valor_metadata,
        )
        ==
        canonizar_alias_metadata(
            campo,
            valor_esperado,
        )
    )


def corresponde_filtros(
    metadata: dict,
    filtros: dict,
    filtro_data: dict | None = None,
) -> bool:
    """AND entre filtros estruturados e intervalo temporal."""
    for campo, valor_esperado in filtros.items():
        valor_atual = metadata.get(campo)

        if valor_atual is None:
            return False

        if not valores_equivalentes_por_campo(
            campo,
            valor_atual,
            valor_esperado,
        ):
            return False

    filtro_data = filtro_data or {}
    inicio = filtro_data.get("inicio")
    fim = filtro_data.get("fim")

    if inicio is not None or fim is not None:
        data_documento = converter_data_metadata(
            metadata.get(CAMPO_DATA)
        )

        if data_documento is None:
            return False

        # Evita comparação entre datetime timezone-aware e naive.
        if data_documento.tzinfo is not None:
            data_documento = data_documento.replace(tzinfo=None)
        if inicio is not None and inicio.tzinfo is not None:
            inicio = inicio.replace(tzinfo=None)
        if fim is not None and fim.tzinfo is not None:
            fim = fim.replace(tzinfo=None)

        if inicio is not None and data_documento < inicio:
            return False

        if fim is not None and data_documento > fim:
            return False

    return True




# VALIDAÇÃO CRUZADA / RECONCILIAÇÃO DOS FILTROS


PRIORIDADE_FILTROS = [
    "source_file",
    "ticket_id",
    "customer_id",
    "employee_id",
    "category",
    "doc_type",
    "domain",
    "module",
    "department",
    "priority",
    "status",
    "state",
    "sensitivity",
    "document_nature",
    "file_type",
]


def contar_chunks_compativeis(
    filtros: dict,
    filtro_data: dict | None = None,
) -> int:
    """
    Conta quantos chunks reais do docstore satisfazem simultaneamente
    os filtros fornecidos.
    """
    return sum(
        1
        for item in DOCUMENTOS_BM25
        if corresponde_filtros(
            item["metadados"],
            filtros,
            filtro_data,
        )
    )



def resolver_alias_no_contexto(
    campo: str,
    valor_original,
    filtros: dict,
    filtro_data: dict | None = None,
):
    """
    Procura a variante REAL de um alias que aparece em documentos
    compatíveis com os demais filtros.

    Exemplo:
        doc_type=ticket + module=VendeFácil Estoque

    Se os tickets usam module=estoque, retorna "estoque".
    """
    filtros_contexto = {
        chave: valor
        for chave, valor in filtros.items()
        if chave != campo
    }

    candidatos = []

    for item in DOCUMENTOS_BM25:
        metadata = item["metadados"]

        if not corresponde_filtros(
            metadata,
            filtros_contexto,
            filtro_data,
        ):
            continue

        valor_real = metadata.get(
            campo
        )

        if valor_real in (None, ""):
            continue

        if valores_equivalentes_por_campo(
            campo,
            valor_real,
            valor_original,
        ):
            candidatos.append(
                str(valor_real)
            )

    if not candidatos:
        return None

    return Counter(
        candidatos
    ).most_common(1)[0][0]


def reconciliar_filtros(
    filtros: dict,
    filtro_data: dict | None = None,
    filtros_explicitos: list[str] | None = None,
    data_explicita: bool = False,
) -> tuple[dict, list[dict], int, dict]:
    """
    Valida a combinação dos filtros contra documentos reais sem alterar
    silenciosamente a intenção explícita do usuário.

    Regras:
    - filtros explícitos NUNCA são removidos para fabricar resultados;
    - filtros inferidos/resolvidos podem ser removidos se entrarem em
      conflito com restrições explícitas;
    - se todos os filtros conflitantes forem explícitos, a busca correta
      retorna zero resultados;
    - uma versão relaxada é calculada apenas para diagnóstico e NUNCA
      deve alimentar a resposta final.

    Exemplo:
        pergunta: "Quais documentos restritos existem sobre o módulo Pay?"

        sensitivity="restrito" -> explícito
        module="pay"            -> explícito

        Se a combinação não existir:
        filtros aplicados = ambos
        resultados = 0

        O sistema NÃO transforma a pergunta em "documentos sobre Pay".
    """
    filtros = dict(filtros or {})
    filtro_data = filtro_data or {
        "inicio": None,
        "fim": None,
    }

    filtros_explicitos = [
        campo
        for campo in (filtros_explicitos or [])
        if campo in filtros
    ]

    diagnostico = {
        "combinacao_original_valida": False,
        "restricoes_explicitas_preservadas": True,
        "sem_correspondencia_exata": False,
        "filtros_relaxados_apenas_diagnostico": {},
        "chunks_relaxados_apenas_diagnostico": 0,
        "data_explicita": bool(data_explicita),
    }

    if not filtros:
        total = contar_chunks_compativeis(
            {},
            filtro_data,
        )
        diagnostico["combinacao_original_valida"] = (
            total > 0
        )
        diagnostico["sem_correspondencia_exata"] = (
            total == 0
        )
        return {}, [], total, diagnostico

    total_completo = contar_chunks_compativeis(
        filtros,
        filtro_data,
    )

    if total_completo > 0:
        diagnostico["combinacao_original_valida"] = True
        diagnostico["aliases_resolvidos"] = {}
        return (
            filtros,
            [],
            total_completo,
            diagnostico,
        )

    # Antes de declarar conflito, tenta resolver aliases de module/domain
    # dentro do subconjunto definido pelos demais filtros.
    filtros_resolvidos = dict(
        filtros
    )
    aliases_resolvidos = {}

    for campo in (
        "module",
        "domain",
    ):
        if campo not in filtros_resolvidos:
            continue

        valor_original = filtros_resolvidos[
            campo
        ]

        valor_real = resolver_alias_no_contexto(
            campo,
            valor_original,
            filtros_resolvidos,
            filtro_data,
        )

        if (
            valor_real is not None
            and normalizar_texto(valor_real).strip()
            != normalizar_texto(valor_original).strip()
        ):
            aliases_resolvidos[campo] = {
                "original": valor_original,
                "aplicado": valor_real,
            }
            filtros_resolvidos[
                campo
            ] = valor_real

    total_resolvido = contar_chunks_compativeis(
        filtros_resolvidos,
        filtro_data,
    )

    if total_resolvido > 0:
        diagnostico["combinacao_original_valida"] = True
        diagnostico["aliases_resolvidos"] = aliases_resolvidos
        return (
            filtros_resolvidos,
            [],
            total_resolvido,
            diagnostico,
        )

    diagnostico["aliases_resolvidos"] = aliases_resolvidos

    # A combinação completa realmente não existe.
    diagnostico["sem_correspondencia_exata"] = True

    explicitos = {
        campo: filtros[campo]
        for campo in filtros_explicitos
    }

    inferidos = {
        campo: valor
        for campo, valor in filtros.items()
        if campo not in filtros_explicitos
    }

    # Primeiro preservamos TODAS as restrições explícitas.
    aplicados = dict(explicitos)
    removidos = []

    # Se os próprios filtros explícitos já não possuem interseção,
    # essa é a resposta correta da recuperação: zero.
    total_explicitos = contar_chunks_compativeis(
        aplicados,
        filtro_data,
    )

    if explicitos and total_explicitos == 0:
        for campo, valor in inferidos.items():
            removidos.append(
                {
                    "campo": campo,
                    "valor": valor,
                    "tipo": "inferido",
                    "motivo": (
                        "Filtro inferido removido porque as restrições "
                        "explícitas do usuário já não possuem interseção. "
                        "As restrições explícitas foram preservadas."
                    ),
                }
            )

        # Diagnóstico opcional: qual seria a quantidade se os filtros
        # explícitos fossem relaxados? Isso NÃO é usado na resposta.
        relaxados = {}
        ordem_relaxada = [
            campo
            for campo in PRIORIDADE_FILTROS
            if campo in filtros
        ] + [
            campo
            for campo in filtros
            if campo not in PRIORIDADE_FILTROS
        ]

        for campo in ordem_relaxada:
            tentativa = {
                **relaxados,
                campo: filtros[campo],
            }
            if contar_chunks_compativeis(
                tentativa,
                filtro_data,
            ) > 0:
                relaxados[campo] = filtros[campo]

        diagnostico[
            "filtros_relaxados_apenas_diagnostico"
        ] = relaxados

        diagnostico[
            "chunks_relaxados_apenas_diagnostico"
        ] = contar_chunks_compativeis(
            relaxados,
            filtro_data,
        ) if relaxados else 0

        return (
            aplicados,
            removidos,
            0,
            diagnostico,
        )

    # Há documentos que atendem às restrições explícitas.
    # Podemos tentar acrescentar filtros inferidos, um por vez.
    ordem_inferidos = [
        campo
        for campo in PRIORIDADE_FILTROS
        if campo in inferidos
    ] + [
        campo
        for campo in inferidos
        if campo not in PRIORIDADE_FILTROS
    ]

    for campo in ordem_inferidos:
        valor = inferidos[campo]

        tentativa = {
            **aplicados,
            campo: valor,
        }

        total_tentativa = contar_chunks_compativeis(
            tentativa,
            filtro_data,
        )

        if total_tentativa > 0:
            aplicados[campo] = valor
        else:
            removidos.append(
                {
                    "campo": campo,
                    "valor": valor,
                    "tipo": "inferido",
                    "motivo": (
                        "Filtro inferido removido porque conflitava "
                        "com as restrições explícitas do usuário."
                    ),
                }
            )

    total_final = contar_chunks_compativeis(
        aplicados,
        filtro_data,
    )

    diagnostico["sem_correspondencia_exata"] = (
        total_final == 0
    )

    return (
        aplicados,
        removidos,
        total_final,
        diagnostico,
    )


def obter_perfil_source_file(
    source_file: str,
) -> dict:
    """
    Mostra os valores reais de metadados presentes nos chunks
    pertencentes ao source_file selecionado.
    """
    perfil = {}

    for item in DOCUMENTOS_BM25:
        metadata = item["metadados"]

        if not valores_equivalentes_por_campo(
            "source_file",
            metadata.get("source_file"),
            source_file,
        ):
            continue

        for campo in CAMPOS_FILTRAVEIS:
            valor = metadata.get(campo)

            if valor in (None, ""):
                continue

            perfil.setdefault(
                campo,
                set(),
            )

            if isinstance(
                valor,
                (list, tuple, set),
            ):
                perfil[campo].update(
                    str(v)
                    for v in valor
                )
            else:
                perfil[campo].add(
                    str(valor)
                )

    return {
        campo: sorted(valores)
        for campo, valores in perfil.items()
    }


def chave_documento(
    texto: str,
    metadados: dict,
) -> tuple:
    """
    Chave estável para fundir o mesmo chunk recuperado
    por FAISS e BM25.
    """
    return (
        metadados.get("documento_id"),
        metadados.get("chunk_index"),
        metadados.get("source_file"),
        texto,
    )


def busca_densa(
    query: str,
    filtros: dict,
    filtro_data: dict | None = None,
) -> list[dict]:
    """
    Busca vetorial com filtro de metadados aplicado no próprio
    VectorStore. fetch_k > k é importante quando há filtro.
    """
    filtro_callable = None

    if filtros or any((filtro_data or {}).values()):
        filtro_callable = lambda metadata: corresponde_filtros(
            metadata,
            filtros,
            filtro_data,
        )

    # Quando há identificador exato, como source_file ou ticket_id,
    # o documento correto pode estar fora dos primeiros FETCH_K_DENSO
    # vetores antes da aplicação do filtro.
    possui_identificador_exato = any(
        campo in filtros
        for campo in CAMPOS_IDENTIFICADORES
    )

    fetch_k_efetivo = (
        quantidade_vetores
        if possui_identificador_exato
        else max(
            FETCH_K_DENSO,
            K_DENSO,
        )
    )

    resultados_brutos = (
        vectorstore
        .similarity_search_with_score(
            query,
            k=K_DENSO,
            filter=filtro_callable,
            fetch_k=fetch_k_efetivo,
        )
    )

    resultados = []

    for ranking, (
        documento,
        score,
    ) in enumerate(
        resultados_brutos,
        start=1,
    ):
        resultados.append(
            {
                "ranking_denso": ranking,
                "texto": documento.page_content,
                "metadados": documento.metadata,
                # No FAISS/LangChain, menor distância tende a ser melhor.
                "score_denso": float(score),
            }
        )

    return resultados


def busca_bm25(
    query_original: str,
    termos_expandidos: list[str],
    filtros: dict,
    filtro_data: dict | None = None,
) -> tuple[list[dict], dict]:
    """
    Busca lexical em duas trilhas:
    1. consulta original;
    2. expansão controlada da consulta.

    Os dois rankings são fundidos por RRF lexical. Quando algum termo original
    não existe em toda a base, o ranking expandido recebe mais peso para tentar
    recuperar documentos que expressem o conceito com outra terminologia.
    """
    tokens_originais = list(dict.fromkeys(tokenizar_bm25(query_original)))

    texto_expandido = " ".join(str(t) for t in termos_expandidos)
    tokens_expandidos = list(dict.fromkeys(tokenizar_bm25(texto_expandido)))

    # Não repete na expansão tokens que já estavam na pergunta original.
    tokens_expandidos = [
        token
        for token in tokens_expandidos
        if token not in set(tokens_originais)
    ]

    diagnostico_originais = diagnosticar_termos_query(query_original)
    termos_ausentes = [
        item["termo"]
        for item in diagnostico_originais
        if not item["existe_na_base"]
    ]

    ha_termo_ausente = bool(termos_ausentes)

    if ha_termo_ausente:
        peso_original = PESO_BM25_ORIGINAL_COM_TERMO_AUSENTE
        peso_expandido = PESO_BM25_EXPANDIDO_COM_TERMO_AUSENTE
    else:
        peso_original = PESO_BM25_ORIGINAL
        peso_expandido = PESO_BM25_EXPANDIDO

    if not tokens_originais and not tokens_expandidos:
        return [], {
            "tokens_originais": [],
            "tokens_expandidos": [],
            "termos_ausentes": [],
            "expansao_ativada": False,
            "peso_original": peso_original,
            "peso_expandido": peso_expandido,
        }

    scores_originais = (
        INDICE_BM25.get_scores(tokens_originais)
        if tokens_originais
        else [0.0] * len(DOCUMENTOS_BM25)
    )
    scores_expandidos = (
        INDICE_BM25.get_scores(tokens_expandidos)
        if tokens_expandidos
        else [0.0] * len(DOCUMENTOS_BM25)
    )

    candidatos_base = []

    for idx, item in enumerate(DOCUMENTOS_BM25):
        if not corresponde_filtros(
            item["metadados"],
            filtros,
            filtro_data,
        ):
            continue

        score_original = float(scores_originais[idx])
        score_expandido = float(scores_expandidos[idx])

        if score_original <= 0 and score_expandido <= 0:
            continue

        tokens_documento = item["tokens_bm25_set"]

        termos_originais_correspondentes = [
            termo
            for termo in tokens_originais
            if termo in tokens_documento
        ]
        termos_expandidos_correspondentes = [
            termo
            for termo in tokens_expandidos
            if termo in tokens_documento
        ]

        candidatos_base.append(
            {
                "texto": item["texto"],
                "metadados": item["metadados"],
                "score_bm25_original": score_original,
                "score_bm25_expandido": score_expandido,
                "termos_originais_correspondentes": termos_originais_correspondentes,
                "termos_expandidos_correspondentes": termos_expandidos_correspondentes,
            }
        )

    # Rankings independentes para evitar somar scores BM25 de consultas
    # com escalas diferentes.
    ranking_original = sorted(
        candidatos_base,
        key=lambda x: x["score_bm25_original"],
        reverse=True,
    )
    ranking_expandido = sorted(
        candidatos_base,
        key=lambda x: x["score_bm25_expandido"],
        reverse=True,
    )

    pos_original = {}
    for pos, item in enumerate(ranking_original, start=1):
        if item["score_bm25_original"] > 0:
            chave = chave_documento(item["texto"], item["metadados"])
            pos_original[chave] = pos

    pos_expandido = {}
    for pos, item in enumerate(ranking_expandido, start=1):
        if item["score_bm25_expandido"] > 0:
            chave = chave_documento(item["texto"], item["metadados"])
            pos_expandido[chave] = pos

    resultados = []
    total_originais = max(len(tokens_originais), 1)
    total_expandidos = max(len(tokens_expandidos), 1)

    for item in candidatos_base:
        chave = chave_documento(item["texto"], item["metadados"])
        rank_original = pos_original.get(chave)
        rank_expandido = pos_expandido.get(chave)

        score_rrf_lexical = 0.0

        if rank_original is not None:
            score_rrf_lexical += (
                peso_original / (RRF_K + rank_original)
            )

        if rank_expandido is not None:
            score_rrf_lexical += (
                peso_expandido / (RRF_K + rank_expandido)
            )

        cobertura_original = (
            len(item["termos_originais_correspondentes"])
            / total_originais
            if tokens_originais else 0.0
        )
        cobertura_expandida = (
            len(item["termos_expandidos_correspondentes"])
            / total_expandidos
            if tokens_expandidos else 0.0
        )

        resultados.append(
            {
                **item,
                "ranking_bm25_original": rank_original,
                "ranking_bm25_expandido": rank_expandido,
                "score_rrf_lexical": float(score_rrf_lexical),
                "cobertura_original": float(cobertura_original),
                "cobertura_expandida": float(cobertura_expandida),
            }
        )

    resultados.sort(
        key=lambda x: (
            x["score_rrf_lexical"],
            x["cobertura_original"],
            x["cobertura_expandida"],
            x["score_bm25_original"],
            x["score_bm25_expandido"],
        ),
        reverse=True,
    )

    resultados = resultados[:K_BM25]

    for ranking, item in enumerate(resultados, start=1):
        item["ranking_bm25"] = ranking
        # Compatibilidade com a interface anterior.
        item["score_bm25"] = item["score_rrf_lexical"]
        item["matches_exatos"] = len(item["termos_originais_correspondentes"])
        item["cobertura_lexical"] = item["cobertura_original"]
        item["termos_correspondentes"] = item["termos_originais_correspondentes"]

    diagnostico = {
        "tokens_originais": tokens_originais,
        "tokens_expandidos": tokens_expandidos,
        "termos_ausentes": termos_ausentes,
        "expansao_ativada": bool(tokens_expandidos) and ha_termo_ausente,
        "peso_original": peso_original,
        "peso_expandido": peso_expandido,
    }

    return resultados, diagnostico


def fundir_rrf(
    resultados_densos: list[dict],
    resultados_bm25: list[dict],
    peso_denso: float = PESO_DENSO,
    peso_bm25: float = PESO_BM25,
) -> list[dict]:
    """Funde os rankings denso e lexical por Reciprocal Rank Fusion."""
    fundidos = {}

    for item in resultados_densos:
        chave = chave_documento(item["texto"], item["metadados"])

        if chave not in fundidos:
            fundidos[chave] = {
                "texto": item["texto"],
                "metadados": item["metadados"],
                "score_rrf": 0.0,
                "ranking_denso": None,
                "score_denso": None,
                "ranking_bm25": None,
                "score_bm25": None,
                "score_bm25_original": None,
                "score_bm25_expandido": None,
                "ranking_bm25_original": None,
                "ranking_bm25_expandido": None,
                "cobertura_original": None,
                "cobertura_expandida": None,
                "termos_originais_correspondentes": [],
                "termos_expandidos_correspondentes": [],
            }

        fundidos[chave]["ranking_denso"] = item["ranking_denso"]
        fundidos[chave]["score_denso"] = item["score_denso"]
        fundidos[chave]["score_rrf"] += (
            peso_denso / (RRF_K + item["ranking_denso"])
        )

    for item in resultados_bm25:
        chave = chave_documento(item["texto"], item["metadados"])

        if chave not in fundidos:
            fundidos[chave] = {
                "texto": item["texto"],
                "metadados": item["metadados"],
                "score_rrf": 0.0,
                "ranking_denso": None,
                "score_denso": None,
                "ranking_bm25": None,
                "score_bm25": None,
                "score_bm25_original": None,
                "score_bm25_expandido": None,
                "ranking_bm25_original": None,
                "ranking_bm25_expandido": None,
                "cobertura_original": None,
                "cobertura_expandida": None,
                "termos_originais_correspondentes": [],
                "termos_expandidos_correspondentes": [],
            }

        for campo in [
            "ranking_bm25",
            "score_bm25",
            "score_bm25_original",
            "score_bm25_expandido",
            "ranking_bm25_original",
            "ranking_bm25_expandido",
            "cobertura_original",
            "cobertura_expandida",
            "termos_originais_correspondentes",
            "termos_expandidos_correspondentes",
        ]:
            fundidos[chave][campo] = item.get(campo)

        fundidos[chave]["score_rrf"] += (
            peso_bm25 / (RRF_K + item["ranking_bm25"])
        )

    ranking_final = sorted(
        fundidos.values(),
        key=lambda item: item["score_rrf"],
        reverse=True,
    )[:K_BUSCA]

    for ranking, item in enumerate(ranking_final, start=1):
        item["ranking"] = ranking
        item["score"] = item["score_rrf"]

    return ranking_final

# CONSULTAS ANALÍTICAS SOBRE METADADOS
def chave_entidade_analitica(metadata: dict) -> str:
    """
    Tenta identificar a entidade de negócio para evitar contar vários
    chunks do mesmo registro como entidades diferentes.
    """
    for campo in (
        "ticket_id",
        "customer_id",
        "employee_id",
    ):
        valor = metadata.get(campo)
        if valor not in (None, ""):
            return f"{campo}:{valor}"

    # Para registros estruturados/semi-estruturados, row/line ajudam
    # a identificar o registro original.
    source_file = metadata.get(
        "source_file",
        "desconhecido",
    )

    if metadata.get("line") not in (None, ""):
        return (
            f"arquivo:{source_file}"
            f"::line:{metadata.get('line')}"
        )

    if metadata.get("row") not in (None, ""):
        return (
            f"arquivo:{source_file}"
            f"::row:{metadata.get('row')}"
        )

    chunk_id = metadata.get("chunk_id")
    if chunk_id not in (None, ""):
        return f"chunk:{chunk_id}"

    return (
        f"arquivo:{source_file}"
        f"::chunk:{metadata.get('chunk_index')}"
    )

def entidades_compativeis(
    filtros: dict,
    filtro_data: dict | None = None,
) -> list[dict]:
    """
    Retorna entidades únicas que satisfazem os filtros populacionais.
    """
    entidades = {}

    for item in DOCUMENTOS_BM25:
        metadata = item["metadados"]

        if not corresponde_filtros(
            metadata,
            filtros,
            filtro_data,
        ):
            continue

        chave = chave_entidade_analitica(
            metadata
        )

        if chave not in entidades:
            entidades[chave] = {
                "chave": chave,
                "metadados": metadata,
                "texto": item["texto"],
            }

    return list(
        entidades.values()
    )

def executar_consulta_analitica(
    analise: dict,
) -> dict | None:
    """
    Executa verificações de conjunto diretamente sobre os metadados.
    Isso evita usar Top-K para responder perguntas como:
    "Todos os tickets de SP foram resolvidos?"
    """
    operacao = analise.get(
        "operacao_analitica",
        "nenhuma",
    )

    if operacao == "nenhuma":
        return None

    filtros = dict(
        analise.get(
            "filtros",
            {},
        )
    )

    filtro_data = analise.get(
        "filtro_data",
        {
            "inicio": None,
            "fim": None,
        },
    )

    campo = analise.get(
        "campo_avaliado"
    )

    valor_alvo = analise.get(
        "valor_avaliado"
    )

    entidades = entidades_compativeis(
        filtros,
        filtro_data,
    )

    total = len(entidades)

    distribuicao = Counter()
    correspondentes = []
    divergentes = []

    if campo:
        for entidade in entidades:
            metadata = entidade[
                "metadados"
            ]

            valor = metadata.get(
                campo
            )

            valor_legivel = (
                str(valor)
                if valor not in (None, "")
                else "Não informado"
            )

            distribuicao[
                valor_legivel
            ] += 1

            if (
                valor_alvo is not None
                and valores_equivalentes(
                    valor,
                    valor_alvo,
                )
            ):
                correspondentes.append(
                    entidade
                )
            elif valor_alvo is not None:
                divergentes.append(
                    entidade
                )

    resultado = {
        "operacao": operacao,
        "filtros_populacao": filtros,
        "campo_avaliado": campo,
        "valor_avaliado": valor_alvo,
        "total_entidades": total,
        "distribuicao": dict(
            distribuicao
        ),
        "quantidade_correspondentes": len(
            correspondentes
        ),
        "quantidade_divergentes": len(
            divergentes
        ),
        "ids_correspondentes": [],
        "ids_divergentes": [],
        "resultado_booleano": None,
    }

    def obter_id(entidade):
        metadata = entidade[
            "metadados"
        ]

        for chave in (
            "ticket_id",
            "customer_id",
            "employee_id",
            "source_file",
        ):
            valor = metadata.get(
                chave
            )
            if valor not in (None, ""):
                return str(valor)

        return entidade[
            "chave"
        ]

    resultado["ids_correspondentes"] = [
        obter_id(item)
        for item in correspondentes
    ][:50]

    resultado["ids_divergentes"] = [
        obter_id(item)
        for item in divergentes
    ][:50]

    if operacao == "todos":
        # Em lógica universal, conjunto vazio não é tratado como confirmação
        # de negócio. Retornamos None para indicar ausência de dados.
        if total == 0:
            resultado[
                "resultado_booleano"
            ] = None
        elif campo and valor_alvo is not None:
            resultado[
                "resultado_booleano"
            ] = (
                len(divergentes) == 0
            )

    elif operacao == "algum":
        if total == 0:
            resultado[
                "resultado_booleano"
            ] = False
        elif campo and valor_alvo is not None:
            resultado[
                "resultado_booleano"
            ] = (
                len(correspondentes) > 0
            )
        else:
            resultado[
                "resultado_booleano"
            ] = (
                total > 0
            )

    elif operacao == "contar":
        resultado[
            "resultado_contagem"
        ] = (
            len(correspondentes)
            if campo and valor_alvo is not None
            else total
        )

    return resultado


def formatar_resposta_analitica(
    pergunta: str,
    resultado: dict,
) -> str:
    """
    Gera resposta determinística para agregações suportadas.
    Não depende do LLM para calcular contagens ou lógica universal.
    """
    operacao = resultado.get(
        "operacao"
    )

    total = resultado.get(
        "total_entidades",
        0,
    )

    campo = resultado.get(
        "campo_avaliado"
    )

    valor = resultado.get(
        "valor_avaliado"
    )

    distribuicao = resultado.get(
        "distribuicao",
        {},
    )

    if operacao == "todos":
        booleano = resultado.get(
            "resultado_booleano"
        )

        if booleano is None:
            return (
                "Não encontrei registros que atendam aos critérios "
                "da população consultada, então não é possível confirmar "
                "a condição para todos."
            )

        qtd_ok = resultado.get(
            "quantidade_correspondentes",
            0,
        )

        qtd_div = resultado.get(
            "quantidade_divergentes",
            0,
        )

        if booleano:
            resposta = (
                f"Sim. Todos os {total} registros encontrados "
                f"atendem à condição `{campo} = {valor}`."
            )
        else:
            resposta = (
                f"Não. Dos {total} registros encontrados, "
                f"{qtd_ok} atendem à condição `{campo} = {valor}` "
                f"e {qtd_div} não atendem."
            )

        if distribuicao:
            itens = ", ".join(
                f"{chave}: {quantidade}"
                for chave, quantidade
                in sorted(
                    distribuicao.items(),
                    key=lambda x: (
                        -x[1],
                        x[0],
                    ),
                )
            )
            resposta += (
                "\n\nDistribuição observada de "
                f"`{campo}`: {itens}."
            )

        ids_div = resultado.get(
            "ids_divergentes",
            [],
        )

        if ids_div:
            resposta += (
                "\n\nRegistros que não atendem à condição: "
                + ", ".join(ids_div)
                + "."
            )

        return resposta

    if operacao == "algum":
        booleano = resultado.get(
            "resultado_booleano"
        )

        if booleano:
            return (
                "Sim. Há pelo menos um registro que atende "
                "à condição solicitada."
            )

        return (
            "Não. Nenhum registro da população consultada "
            "atende à condição solicitada."
        )

    if operacao == "contar":
        quantidade = resultado.get(
            "resultado_contagem",
            total,
        )
        return (
            f"Foram encontrados {quantidade} registros "
            "que atendem aos critérios da consulta."
        )

    if operacao == "distribuicao":
        if not distribuicao:
            return (
                "Não encontrei valores para calcular a distribuição solicitada."
            )

        linhas = [
            f"- {chave}: {quantidade}"
            for chave, quantidade
            in sorted(
                distribuicao.items(),
                key=lambda x: (
                    -x[1],
                    x[0],
                ),
            )
        ]

        return (
            f"Distribuição de `{campo}` em {total} registros:\n"
            + "\n".join(linhas)
        )

    return (
        "A consulta analítica foi identificada, mas a operação "
        "não pôde ser executada."
    )


# BUSCA HÍBRIDA
def buscar_documentos(pergunta: str):
    """
    Pipeline:
      pergunta
        -> Query Analyzer
        -> diagnóstico lexical global
        -> expansão controlada quando necessário
        -> FAISS filtrado
        -> BM25 original + expandido filtrado
        -> RRF adaptativo
    """
    try:
        analise = analisar_query(pergunta)

        query_semantica = analise["query_semantica"]
        query_expandida = analise.get("query_expandida", query_semantica)
        termos_expandidos = analise.get("termos_expandidos", [])
        filtros_extraidos = dict(
            analise.get(
                "filtros",
                {},
            )
        )

        filtro_data = analise.get(
            "filtro_data",
            {"inicio": None, "fim": None},
        )

        filtros_explicitos = list(
            analise.get(
                "filtros_explicitos",
                [],
            )
        )

        data_explicita = bool(
            analise.get(
                "data_explicita",
                False,
            )
        )

        (
            filtros,
            filtros_removidos,
            chunks_compativeis_filtros,
            diagnostico_reconciliacao,
        ) = reconciliar_filtros(
            filtros_extraidos,
            filtro_data,
            filtros_explicitos=filtros_explicitos,
            data_explicita=data_explicita,
        )

        analise["filtros_extraidos"] = filtros_extraidos
        analise["filtros_explicitos"] = filtros_explicitos
        analise["filtros"] = filtros
        analise["filtros_removidos"] = filtros_removidos
        analise["chunks_compativeis_filtros"] = (
            chunks_compativeis_filtros
        )
        analise["diagnostico_reconciliacao"] = (
            diagnostico_reconciliacao
        )

        source_file_aplicado = filtros.get(
            "source_file"
        )

        analise["perfil_source_file"] = (
            obter_perfil_source_file(
                source_file_aplicado
            )
            if source_file_aplicado
            else {}
        )

        # Consultas analíticas usam a população completa que satisfaz
        # os filtros estruturados, em vez de inferir o resultado pelo Top-K.
        resultado_analitico = executar_consulta_analitica(
            analise
        )
        analise[
            "resultado_analitico"
        ] = resultado_analitico

        if diagnostico_reconciliacao.get(
            "sem_correspondencia_exata"
        ):
            analise["mensagem_sem_correspondencia"] = (
                "Nenhum chunk da base satisfaz simultaneamente todas "
                "as restrições explícitas da pergunta. Os filtros não "
                "foram relaxados para gerar a resposta."
            )
        else:
            analise["mensagem_sem_correspondencia"] = ""

        diagnostico_termos = diagnosticar_termos_query(pergunta)
        termos_ausentes = [
            item["termo"]
            for item in diagnostico_termos
            if not item["existe_na_base"]
        ]

        # Se há termo ausente, usamos a versão expandida também na busca densa.
        # Caso contrário, preservamos a query semântica mais fiel ao usuário.
        query_densa = (
            query_expandida
            if termos_ausentes
            else query_semantica
        )

        resultados_densos = busca_densa(
            query_densa,
            filtros,
            filtro_data,
        )

        resultados_bm25, diagnostico_bm25 = busca_bm25(
            pergunta,
            termos_expandidos,
            filtros,
            filtro_data,
        )

        expansao_ativa = diagnostico_bm25.get(
            "expansao_ativada",
            False,
        )

        if expansao_ativa:
            peso_denso_final = PESO_DENSO_COM_EXPANSAO
            peso_bm25_final = PESO_BM25_COM_EXPANSAO
        else:
            peso_denso_final = PESO_DENSO
            peso_bm25_final = PESO_BM25

        resultados = fundir_rrf(
            resultados_densos,
            resultados_bm25,
            peso_denso=peso_denso_final,
            peso_bm25=peso_bm25_final,
        )

        analise["query_densa_utilizada"] = query_densa
        analise["termos_ausentes_na_base"] = termos_ausentes
        analise["expansao_ativada"] = expansao_ativa
        analise["peso_denso_final"] = peso_denso_final
        analise["peso_bm25_final"] = peso_bm25_final

        return (
            resultados,
            analise,
            resultados_densos,
            resultados_bm25,
            diagnostico_bm25,
        )

    except Exception as erro:
        st.error("Erro durante a busca híbrida.")
        st.exception(erro)

        return (
            [],
            {
                "query_semantica": pergunta,
                "query_expandida": pergunta,
                "query_densa_utilizada": pergunta,
                "termos_expandidos": [],
                "filtros": {},
                "filtro_data": {"inicio": None, "fim": None},
                "justificativa": str(erro),
                "expansao_ativada": False,
            },
            [],
            [],
            {
                "tokens_originais": tokenizar_bm25(pergunta),
                "tokens_expandidos": [],
                "termos_ausentes": [],
                "expansao_ativada": False,
            },
        )


# FORMATAR METADADOS
def obter_metadata(
    metadados,
    chave,
    padrao="Não informado",
):
    valor = metadados.get(
        chave
    )
    if valor is None or valor == "":
        return padrao

    return valor

# MONTAR CONTEXTO PARA O GPT
def montar_contexto(
    resultados,
):
    partes = []
    for resultado in resultados:
        metadata = resultado[
            "metadados"
        ]

        source_file = obter_metadata(
            metadata,
            "source_file",
        )

        file_type = obter_metadata(
            metadata,
            "file_type",
        )

        document_nature = obter_metadata(
            metadata,
            "document_nature",
        )

        doc_type = obter_metadata(
            metadata,
            "doc_type",
        )

        sensitivity = obter_metadata(
            metadata,
            "sensitivity",
        )

        domain = obter_metadata(
            metadata,
            "domain",
        )

        category = obter_metadata(
            metadata,
            "category",
        )
        # Outros campos que eventualmente tenham sido
        # adicionados por adicionar_metadata()

        metadata_completo = "\n".join(
            f"{chave}: {valor}"
            for chave, valor
            in metadata.items()
        )

        parte = f"""
============================================================
[FONTE {resultado["ranking"]}]
============================================================

Arquivo: {source_file}
Tipo de arquivo: {file_type}
Natureza: {document_nature}
Tipo de documento: {doc_type}
Sensibilidade: {sensitivity}
Domínio: {domain}
Categoria: {category}

Score híbrido (RRF):
{resultado["score_rrf"]:.6f}

Ranking denso:
{resultado.get("ranking_denso")}

Distância FAISS:
{resultado.get("score_denso")}

Ranking BM25:
{resultado.get("ranking_bm25")}

Score BM25:
{resultado.get("score_bm25")}

METADADOS COMPLETOS:

{metadata_completo}

CONTEÚDO:

{resultado["texto"]}
"""
        partes.append(
            parte
        )

    return "\n\n".join(
        partes
    )

# GERAR RESPOSTA
def gerar_resposta(
    pergunta,
    resultados,
    analise_query=None,
):
    if analise_query:
        resultado_analitico = analise_query.get(
            "resultado_analitico"
        )

        if resultado_analitico is not None:
            return formatar_resposta_analitica(
                pergunta,
                resultado_analitico,
            )

    if not resultados:
        return (
            "Não encontrei informações "
            "nos documentos recuperados."
        )
    contexto = montar_contexto(
        resultados
    )

    # INSTRUÇÕES DO RAG
    instrucoes = """
Você é um assistente que responde perguntas utilizando
uma base documental por meio de RAG
(Retrieval-Augmented Generation).

Utilize SOMENTE as informações presentes no contexto
recuperado.

REGRAS:

1. Leia todos os trechos recuperados antes de responder.

2. Utilize somente informações presentes nos documentos.

3. Não invente informações.

4. Não utilize conhecimento externo para completar
informações ausentes.

5. Combine informações de diferentes fontes quando isso
for necessário.

6. Quando possível, informe de qual arquivo veio a informação.

Exemplo:

Segundo o arquivo "manual_pdv.md" [FONTE 2], ...

7. Você pode utilizar os metadados para entender a origem
e o contexto dos documentos.

8. Se houver informações conflitantes entre diferentes
documentos, informe a divergência.

9. Não diga que uma informação não existe antes de analisar
todos os trechos fornecidos.

10. Se não houver informações suficientes no contexto,
responda:

"Não encontrei essa informação nos documentos recuperados."

11. Responda sempre em português do Brasil.

12. Seja claro, direto e organizado.

13. Alguns trechos podem ter sido recuperados por expansão semântica ou lexical.
A expansão serve somente para localizar candidatos. Não trate um termo relacionado
como prova de que o documento responde à pergunta.

14. Só responda sobre o conceito perguntado se o conteúdo recuperado o sustentar
explicitamente ou por equivalência inequívoca. Caso contrário, use a resposta de
insuficiência definida na regra 10.
"""

    entrada = f"""
============================================================
CONTEXTO RECUPERADO
============================================================
{contexto}

============================================================
PERGUNTA
============================================================
{pergunta}

============================================================
RESPOSTA
============================================================
"""

    # OPENAI
    try:
        resposta = client.responses.create(
            model=MODELO_LLM,
            instructions=instrucoes,
            input=entrada,
        )
        return resposta.output_text

    except Exception as erro:
        return (
            "Erro ao consultar a OpenAI:\n\n"
            f"{erro}"
        )

# INTERFACE
st.title(
    "💬 Assistente RAG"
)

st.caption(
    "Query Analyzer + Aliases de Metadados + Agregação Estruturada + FAISS + BM25 + RRF + OpenAI"
)

st.success(
    "Base FAISS carregada com sucesso."
)

# INFORMAÇÕES DO SISTEMA
with st.expander(
    "⚙️ Informações do sistema",
):
    col1, col2, col3 = st.columns(
        3
    )
    with col1:
        st.metric(
            "Vetores FAISS",
            quantidade_vetores,
        )

    with col2:
        st.metric(
            "Documentos mapeados",
            quantidade_mapeamentos,
        )

    with col3:
        st.metric(
            "Dimensão",
            dimensao_faiss,
        )

    st.write(
        "**Modelo de embeddings:**",
        MODELO_EMBEDDING,
    )

    st.write(
        "**Modelo LLM:**",
        MODELO_LLM,
    )

    st.write(
        "**K da busca:**",
        K_BUSCA,
    )

    st.write(
        "**Pasta FAISS:**",
        str(CAMINHO_FAISS),
    )

# INSPECIONAR DOCSTORE
with st.expander(
    "🧪 Inspecionar index.pkl",
):
    quantidade_inspecao = st.slider(
        "Quantidade de chunks:",
        min_value=1,
        max_value=20,
        value=5,
    )

    contador = 0
    for (
        indice_faiss,
        docstore_id,
    ) in (
        vectorstore
        .index_to_docstore_id
        .items()
    ):
        if contador >= quantidade_inspecao:
            break

        documento = (
            vectorstore
            .docstore
            .search(
                docstore_id
            )
        )

        st.markdown(
            f"### Chunk {contador + 1}"
        )

        st.write(
            "**Índice FAISS:**",
            indice_faiss,
        )

        st.write(
            "**ID no Docstore:**",
            docstore_id,
        )

        st.write(
            "**Metadados:**"
        )

        st.json(
            documento.metadata
        )

        st.write(
            "**Conteúdo:**"
        )

        st.code(
            documento.page_content,
            language=None,
        )

        st.divider()

        contador += 1

# HISTÓRICO
if "mensagens" not in st.session_state:
    st.session_state.mensagens = []

for mensagem in st.session_state.mensagens:
    with st.chat_message(
        mensagem["role"]
    ):
        st.write(
            mensagem["content"]
        )

# CHAT
pergunta = st.chat_input(
    "Digite sua pergunta..."
)

# PROCESSAR
if pergunta:
    # USUÁRIO
    st.session_state.mensagens.append(
        {
            "role": "user",
            "content": pergunta,
        }
    )
    with st.chat_message(
        "user"
    ):
        st.write(
            pergunta
        )

    # RECUPERAÇÃO
    with st.spinner(
        "Buscando informações na base..."
    ):
        (
            resultados,
            analise_query,
            resultados_densos,
            resultados_bm25,
            diagnostico_bm25,
        ) = buscar_documentos(
            pergunta
        )

    # GERAÇÃO
    with st.chat_message(
        "assistant"
    ):
        with st.spinner(
            "Gerando resposta..."
        ):
            resposta = gerar_resposta(
                pergunta,
                resultados,
                analise_query=analise_query,
            )

        st.write(
            resposta
        )

        # FONTES RECUPERADAS
        with st.expander(
            "📚 Fontes recuperadas",
        ):
            if not resultados:
                st.warning(
                    "Nenhum resultado recuperado."
                )
            for resultado in resultados:
                metadata = resultado[
                    "metadados"
                ]
                source_file = obter_metadata(
                    metadata,
                    "source_file",
                )
                doc_type = obter_metadata(
                    metadata,
                    "doc_type",
                )
                category = obter_metadata(
                    metadata,
                    "category",
                )
                domain = obter_metadata(
                    metadata,
                    "domain",
                )
                sensitivity = obter_metadata(
                    metadata,
                    "sensitivity",
                )
                st.markdown(
                    f"""
### Resultado {resultado["ranking"]}

**Arquivo:** `{source_file}`

**Tipo de documento:** `{doc_type}`

**Categoria:** `{category}`

**Domínio:** `{domain}`

**Sensibilidade:** `{sensitivity}`

**Score híbrido (RRF):** `{resultado["score_rrf"]:.6f}`

**Ranking denso:** `{resultado.get("ranking_denso")}`  
**Distância FAISS:** `{resultado.get("score_denso")}`

**Ranking BM25:** `{resultado.get("ranking_bm25")}`  
**Score BM25:** `{resultado.get("score_bm25")}`
"""
                )
                st.write(
                    "**Conteúdo:**"
                )
                st.code(
                    resultado["texto"],
                    language=None,
                )
                st.write(
                    "**Todos os metadados:**"
                )
                st.json(
                    metadata
                )
                st.divider()

        # CONTEXTO DO GPT
        with st.expander(
            "🧠 Contexto enviado ao GPT",
        ):
            if resultados:
                contexto = montar_contexto(
                    resultados
                )
                st.code(
                    contexto,
                    language=None,
                )
            else:
                st.write(
                    "Nenhum contexto enviado."
                )

        # DIAGNÓSTICO
        with st.expander(
            "🔎 Diagnóstico da busca",
        ):
            st.write(
                "**Vetores FAISS:**",
                quantidade_vetores,
            )
            st.write(
                "**Mapeamentos index.pkl:**",
                quantidade_mapeamentos,
            )
            st.write(
                "**Dimensão:**",
                dimensao_faiss,
            )
            st.write(
                "**K solicitado:**",
                K_BUSCA,
            )

            st.subheader(
                "Query Analyzer"
            )
            st.write(
                "**Query semântica:**",
                analise_query.get(
                    "query_semantica"
                ),
            )
            st.write(
                "**Query expandida:**",
                analise_query.get(
                    "query_expandida"
                ),
            )
            st.write(
                "**Query usada no FAISS:**",
                analise_query.get(
                    "query_densa_utilizada"
                ),
            )
            st.write(
                "**Termos expandidos:**",
                analise_query.get(
                    "termos_expandidos",
                    [],
                ),
            )
            st.write(
                "**Expansão ativada:**",
                analise_query.get(
                    "expansao_ativada",
                    False,
                ),
            )
            st.write(
                "**Pesos finais Denso/BM25:**",
                {
                    "denso": analise_query.get("peso_denso_final"),
                    "bm25": analise_query.get("peso_bm25_final"),
                },
            )
            st.write(
                "**Filtros extraídos pelo Query Analyzer:**"
            )
            st.json(
                analise_query.get(
                    "filtros_extraidos",
                    analise_query.get(
                        "filtros",
                        {},
                    ),
                )
            )

            st.write(
                "**Filtros marcados como explícitos na pergunta:**"
            )
            st.json(
                analise_query.get(
                    "filtros_explicitos",
                    [],
                )
            )

            st.write(
                "**Filtros realmente aplicados após validação cruzada:**"
            )
            st.json(
                analise_query.get(
                    "filtros",
                    {},
                )
            )

            diagnostico_reconciliacao_diag = analise_query.get(
                "diagnostico_reconciliacao",
                {},
            )

            aliases_resolvidos_diag = (
                diagnostico_reconciliacao_diag.get(
                    "aliases_resolvidos",
                    {},
                )
            )

            if aliases_resolvidos_diag:
                st.info(
                    "O sistema encontrou aliases equivalentes de metadados "
                    "e os converteu para a variante usada no subconjunto."
                )
                st.write(
                    "**Aliases resolvidos:**"
                )
                st.json(
                    aliases_resolvidos_diag
                )

            if diagnostico_reconciliacao_diag.get(
                "sem_correspondencia_exata"
            ):
                st.error(
                    "Nenhum chunk satisfaz simultaneamente todas as "
                    "restrições explícitas. O sistema preservou a intenção "
                    "da pergunta e NÃO relaxou esses filtros para produzir "
                    "resultados artificiais."
                )

                filtros_relaxados_diag = (
                    diagnostico_reconciliacao_diag.get(
                        "filtros_relaxados_apenas_diagnostico",
                        {},
                    )
                )

                if filtros_relaxados_diag:
                    st.write(
                        "**Combinação relaxada apenas para diagnóstico "
                        "(não usada na resposta):**"
                    )
                    st.json(
                        filtros_relaxados_diag
                    )
                    st.write(
                        "**Chunks nessa combinação relaxada:**",
                        diagnostico_reconciliacao_diag.get(
                            "chunks_relaxados_apenas_diagnostico",
                            0,
                        ),
                    )

            filtros_removidos_diag = analise_query.get(
                "filtros_removidos",
                [],
            )

            if filtros_removidos_diag:
                st.warning(
                    "Um ou mais filtros INFERIDOS pelo Query Analyzer "
                    "foram removidos por incompatibilidade. Restrições "
                    "explicitamente pedidas pelo usuário foram preservadas."
                )
                st.write(
                    "**Filtros removidos por incompatibilidade:**"
                )
                st.json(
                    filtros_removidos_diag
                )

            st.write(
                "**Chunks compatíveis com os filtros aplicados:**",
                analise_query.get(
                    "chunks_compativeis_filtros",
                    0,
                ),
            )

            perfil_source_diag = analise_query.get(
                "perfil_source_file",
                {},
            )

            if perfil_source_diag:
                st.write(
                    "**Perfil real do `source_file` selecionado:**"
                )
                st.json(
                    perfil_source_diag
                )

            filtro_data_diag = analise_query.get(
                "filtro_data",
                {},
            )
            st.write(
                "**Intervalo de datas:**",
                {
                    "inicio": str(filtro_data_diag.get("inicio"))
                    if filtro_data_diag.get("inicio") else None,
                    "fim": str(filtro_data_diag.get("fim"))
                    if filtro_data_diag.get("fim") else None,
                },
            )

            st.write(
                "**Operação analítica:**",
                analise_query.get(
                    "operacao_analitica",
                    "nenhuma",
                ),
            )

            st.write(
                "**Campo avaliado:**",
                analise_query.get(
                    "campo_avaliado"
                ),
            )

            st.write(
                "**Valor avaliado:**",
                analise_query.get(
                    "valor_avaliado"
                ),
            )

            resultado_analitico_diag = analise_query.get(
                "resultado_analitico"
            )

            if resultado_analitico_diag is not None:
                st.subheader(
                    "Agregação estruturada"
                )
                st.json(
                    resultado_analitico_diag
                )
                st.caption(
                    "Esse resultado foi calculado sobre todos os registros "
                    "compatíveis com os filtros populacionais; o Top-K vetorial "
                    "não é usado para decidir a agregação."
                )

            st.write(
                "**Justificativa do Query Analyzer:**",
                analise_query.get(
                    "justificativa",
                    "",
                ),
            )

            if analise_query.get(
                "filtros_removidos"
            ):
                st.caption(
                    "A justificativa acima é a saída original do LLM. "
                    "Os filtros efetivamente usados são os exibidos após "
                    "a validação cruzada contra o docstore."
                )
            st.write(
                "**Resultados finais encontrados:**",
                len(resultados),
            )

            st.subheader("Busca densa (FAISS)")
            if resultados_densos:
                for item in resultados_densos:
                    metadata = item["metadados"]
                    source_file = obter_metadata(
                        metadata,
                        "source_file",
                    )
                    st.write(
                        f'{item["ranking_denso"]}. '
                        f'{source_file} | '
                        f'distância={item["score_denso"]:.6f}'
                    )
            else:
                st.info("Nenhum resultado na busca densa.")

            st.subheader("Busca esparsa (BM25)")

            st.write(
                "**Tokens originais:**",
                diagnostico_bm25.get("tokens_originais", []),
            )
            st.write(
                "**Tokens de expansão:**",
                diagnostico_bm25.get("tokens_expandidos", []),
            )

            diagnostico_termos = diagnosticar_termos_query(pergunta)
            st.write("**Presença dos termos originais em toda a base BM25:**")
            for termo_info in diagnostico_termos:
                st.write(
                    f'- `{termo_info["termo"]}`: '
                    f'{termo_info["chunks"]} chunks '
                    f'({termo_info["percentual"]:.2%})'
                )

            termos_ausentes = diagnostico_bm25.get("termos_ausentes", [])
            if termos_ausentes:
                st.warning(
                    "Termos originais ausentes da base: "
                    + ", ".join(termos_ausentes)
                    + ". A expansão controlada foi usada apenas para recuperação."
                )

            st.write(
                "**Pesos internos BM25 original/expandido:**",
                {
                    "original": diagnostico_bm25.get("peso_original"),
                    "expandido": diagnostico_bm25.get("peso_expandido"),
                },
            )

            if resultados_bm25:
                for item in resultados_bm25:
                    metadata = item["metadados"]
                    source_file = obter_metadata(metadata, "source_file")
                    st.write(
                        f'{item["ranking_bm25"]}. '
                        f'{source_file} | '
                        f'RRF-lexical={item["score_rrf_lexical"]:.6f} | '
                        f'BM25-original={item["score_bm25_original"]:.4f} '
                        f'(rank={item.get("ranking_bm25_original")}) | '
                        f'BM25-expandido={item["score_bm25_expandido"]:.4f} '
                        f'(rank={item.get("ranking_bm25_expandido")}) | '
                        f'originais={item.get("termos_originais_correspondentes", [])} | '
                        f'expandidos={item.get("termos_expandidos_correspondentes", [])}'
                    )
            else:
                st.info("Nenhum resultado lexical útil encontrado.")

            st.subheader("Ranking final (RRF)")
            if resultados:
                for resultado in resultados:
                    metadata = resultado["metadados"]
                    source_file = obter_metadata(
                        metadata,
                        "source_file",
                    )
                    st.write(
                        f'{resultado["ranking"]}. '
                        f'{source_file} | '
                        f'RRF={resultado["score_rrf"]:.6f} | '
                        f'denso={resultado.get("ranking_denso")} | '
                        f'BM25={resultado.get("ranking_bm25")}'
                    )
            else:
                st.info("Nenhum resultado após a fusão RRF.")

    # SALVAR RESPOSTA
    st.session_state.mensagens.append(
        {
            "role": "assistant",
            "content": resposta,
        }
    )