from docx import Document
import os

def debug_paragrafo(paragraph):
    print("\n--- PARÁGRAFO ---")
    for i, run in enumerate(paragraph.runs):
        print(
            f"RUN {i}:",
            repr(run.text)
        )

def substituir_runs(paragraph, substituicoes):
    texto_completo = "".join(run.text for run in paragraph.runs)
    texto_original = texto_completo
    for buscar, substituir in substituicoes.items():
        texto_completo = texto_completo.replace(
            buscar,
            str(substituir)
        )

    #nada mudou
    if texto_completo == texto_original:
        return
    
    #remove runs antigos
    for run in paragraph.runs:
        run.text = ""

    #recria texto completo
    if paragraph.runs:
        paragraph.runs[0].text = texto_completo
    else:
        paragraph.add_run(texto_completo)

def aplicar_substituicoes(doc, substituicoes):

    # Parágrafos
    for p in doc.paragraphs:
        substituir_runs(p, substituicoes)

    # Tabelas
    for tabela in doc.tables:
        for linha in tabela.rows:
            for celula in linha.cells:
                for p in celula.paragraphs:
                    substituir_runs(p, substituicoes)

    # Header / Footer
    for secao in doc.sections:
        for p in secao.header.paragraphs:
            substituir_runs(p, substituicoes)

        for p in secao.footer.paragraphs:
            substituir_runs(p, substituicoes)

    return doc


def substituir_textos_documento(caminho_modelo, substituicoes):

    if not os.path.exists(caminho_modelo):
        raise Exception("Arquivo não encontrado")

    doc = Document(caminho_modelo)

    doc = aplicar_substituicoes(doc, substituicoes)

    return doc


def preencher_documento(caminho_modelo, dados):

    substituicoes = {
        f"{{{{{k}}}}}": v for k, v in dados.items()
    }

    return substituir_textos_documento(caminho_modelo, substituicoes)