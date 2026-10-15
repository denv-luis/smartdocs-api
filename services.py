from docx import Document
import os, re


def copiar_estilo(origem, destino):

    destino.bold = origem.bold
    destino.italic = origem.italic
    destino.underline = origem.underline

    destino.font.name = origem.font.name
    destino.font.size = origem.font.size
    destino.font.bold = origem.font.bold
    destino.font.italic = origem.font.italic

    try:
        destino.font.color.rgb = origem.font.color.rgb
    except:
        pass


def substituir_runs(paragraph, substituicoes):
    runs = paragraph.runs

    if not runs:
        return

    texto_completo = "".join(run.text for run in runs)

    for buscar, substituir in substituicoes.items():
        if not buscar or buscar not in texto_completo:
            continue

        texto_completo = "".join(run.text for run in runs)

        while buscar.casefold() in texto_completo.casefold():
            inicio = texto_completo.casefold().find(buscar.casefold())
            fim = inicio + len(buscar)

            posicao = 0
            run_inicio = None
            run_fim = None
            offset_inicio = 0
            offset_fim = 0

            for i, run in enumerate(runs):
                proxima_posicao = posicao + len(run.text)

                if run_inicio is None and posicao <= inicio < proxima_posicao:
                    run_inicio = i
                    offset_inicio = inicio - posicao

                if posicao < fim <= proxima_posicao:
                    run_fim = i
                    offset_fim = fim - posicao
                    break

                posicao = proxima_posicao

            if run_inicio is None or run_fim is None:
                break

            if run_inicio == run_fim:
                run = runs[run_inicio]
                run.text = (
                    run.text[:offset_inicio]
                    + str(substituir)
                    + run.text[offset_fim:]
                )
            else:
                primeiro = runs[run_inicio]
                ultimo = runs[run_fim]

                primeiro.text = (
                    primeiro.text[:offset_inicio]
                    + str(substituir)
                    + ultimo.text[offset_fim:]
                )

                for i in range(run_inicio + 1, run_fim + 1):
                    runs[i].text = ""

            texto_completo = "".join(run.text for run in runs)


def aplicar_substituicoes(doc, substituicoes):

    def processar_tabelas(tabelas):
        for tabela in tabelas:
            for linha in tabela.rows:
                for celula in linha.cells:
                    for p in celula.paragraphs:
                        substituir_runs(p, substituicoes)

                    # Tabelas dentro de outras tabelas
                    processar_tabelas(celula.tables)

    # Parágrafos do documento
    for p in doc.paragraphs:
        substituir_runs(p, substituicoes)

    # Tabelas do documento
    processar_tabelas(doc.tables)

    # Cabeçalhos e rodapés de cada seção
    for secao in doc.sections:
        for area in (secao.header, secao.footer):
            for p in area.paragraphs:
                substituir_runs(p, substituicoes)

            processar_tabelas(area.tables)

    return doc



def substituir_textos_documento(
    caminho_modelo,
    substituicoes
):

    if not os.path.exists(caminho_modelo):
        raise Exception("Arquivo não encontrado")

    doc = Document(caminho_modelo)

    doc = aplicar_substituicoes(
        doc,
        substituicoes
    )

    return doc


def preencher_documento(
    caminho_modelo,
    dados
):

    substituicoes = {
        f"{{{{{k}}}}}": v
        for k, v in dados.items()
    }

    return substituir_textos_documento(
        caminho_modelo,
        substituicoes
    )

def extrair_placeholders(caminho_modelo):
    if not os.path.exists(caminho_modelo):
        raise Exception("Arquivo não encontrado")
    
    doc = Document(caminho_modelo)
    textos = []

    #Parágrafos
    for p in doc.paragraphs:
        textos.append(p.text)

    #Tabelas
    for tabela in doc.tables:
        for linha in tabela.rows:
            for celula in linha.cells:
                for p in celula.paragraphs:
                    textos.append(p.text)

    #Header/Footer
    for secao in doc.sections:
        for p in secao.header.paragraphs:
            textos.append(p.text)

        for p in secao.footer.paragraphs:
            textos.append(p.text)

    texto_completo = "\n".join(textos)
    encontrados = re.findall(
        r"\{\{(.*?)\}\}",
        texto_completo
    )
    #remove duplicados
    placeholders = list(set(encontrados))
    return placeholders