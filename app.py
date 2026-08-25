from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

import json, shutil, os, uuid

from services import (
    preencher_documento,
    substituir_textos_documento,
    extrair_placeholders
)

app = FastAPI(
    title="SmartDocs API",
    description="API para automação e geração de documentos Word (.docx).",
    version="1.0.0"
)

app.mount("/js", StaticFiles(directory="js"), name="js")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------
# HOME
# -------------------------
@app.get("/")
def home():
    return FileResponse("index.html")


# -------------------------
# 1. GERAR DOCUMENTO (TEMPLATE + JSON)
# -------------------------
@app.post("/gerar-documento")
def gerar_documento(
    background_tasks: BackgroundTasks,
    dados_json: str = Form(...),
    arquivo: UploadFile = File(...)
):

    if not arquivo.filename.endswith(".docx"):
        raise HTTPException(status_code=400, detail="Envie apenas arquivos .docx")

    caminho_modelo = f"{uuid.uuid4()}.docx"

    with open(caminho_modelo, "wb") as buffer:
        shutil.copyfileobj(arquivo.file, buffer)

    try:
        dados = json.loads(dados_json)
    except:
        raise HTTPException(status_code=400, detail="JSON inválido")

    doc = preencher_documento(caminho_modelo, dados)

    nome_saida = f"documento_{uuid.uuid4()}.docx"
    doc.save(nome_saida)

    background_tasks.add_task(os.remove, caminho_modelo)
    background_tasks.add_task(os.remove, nome_saida)

    return FileResponse(
        path=nome_saida,
        filename=nome_saida,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        background=background_tasks
    )
@app.post("/substituir-livre")
async def substituir_livre(
    background_tasks: BackgroundTasks,
    arquivo: UploadFile = File(...),
    substituicoes_json: str = Form(...)
):
    if not arquivo.filename.endswith(".docx"):
        raise HTTPException(
            status_code=400,
            detail="Envie apenas arquivos .docx"
        )
    try:
        substituicoes = json.loads(substituicoes_json)
    except:
        raise HTTPException(
            status_code=400,
            detail="JSON inválido"
        )
    caminho_entrada = f"{uuid.uuid4()}.docx"

    with open(caminho_entrada, "wb") as f:
        f.write(await arquivo.read())

    doc = substituir_textos_documento(
        caminho_entrada,
        substituicoes
    )
    nome_saida = "documento_editado.docx"
    doc.save(nome_saida)

    background_tasks.add_task(os.remove, caminho_entrada)
    background_tasks.add_task(os.remove, nome_saida)

    return FileResponse(
        path=nome_saida,
        filename=nome_saida,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        background=background_tasks
    )

# -------------------------
# 2. SUBSTITUIÇÃO SIMPLES (1 TERMO)
# -------------------------
@app.post("/substituir-texto")
def substituir_texto(
    background_tasks: BackgroundTasks,
    texto_buscar: str,
    texto_novo: str,
    arquivo: UploadFile = File(...)
):

    if not arquivo.filename.endswith(".docx"):
        raise HTTPException(status_code=400, detail="Envie apenas arquivos .docx")

    caminho = f"{uuid.uuid4()}.docx"

    with open(caminho, "wb") as buffer:
        shutil.copyfileobj(arquivo.file, buffer)

    substituicoes = {
        texto_buscar: texto_novo
    }

    doc = substituir_textos_documento(caminho, substituicoes)

    nome_saida = f"editado_{uuid.uuid4()}.docx"
    doc.save(nome_saida)

    background_tasks.add_task(os.remove, caminho)
    background_tasks.add_task(os.remove, nome_saida)

    return FileResponse(
        path=nome_saida,
        filename=nome_saida,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        background=background_tasks
    )


# -------------------------
# 3. SUBSTITUIÇÃO MÚLTIPLA (SEM LOTE)
# -------------------------
@app.post("/substituir-varios")
async def substituir_varios(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    substituicoes_json: str = Form(...)
):

    if not file.filename.endswith(".docx"):
        raise HTTPException(status_code=400, detail="Envie apenas arquivos .docx")

    try:
        dados = json.loads(substituicoes_json)
    except:
        raise HTTPException(status_code=400, detail="JSON inválido")

    substituicoes = {
        f"{{{{{k}}}}}": v for k, v in dados.items()
    }

    caminho = f"{uuid.uuid4()}.docx"

    with open(caminho, "wb") as f:
        f.write(await file.read())

    doc = substituir_textos_documento(caminho, substituicoes)

    nome_saida = f"editado_{uuid.uuid4()}.docx"
    doc.save(nome_saida)

    background_tasks.add_task(os.remove, caminho)
    background_tasks.add_task(os.remove, nome_saida)

    return FileResponse(
        path=nome_saida,
        filename=nome_saida,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        background=background_tasks
    )

@app.post("/extrair-campos")
async def extrair_campos(
    arquivo: UploadFile = File(...)
):
    if not arquivo.filename.endswith(".docx"):
        raise HTTPException(
            status_code=400,
            detail="Envie apenas arquivos .docx"
        )
    caminho_temp = f"temp_{arquivo.filename}"
    with open(caminho_temp, "wb") as f:
        f.write(await arquivo.read())
    placeholders = extrair_placeholders(
        caminho_temp
    )
    os.remove(caminho_temp)
    return {
        "campos": placeholders
    }

# -------------------------
# 4. MODELOS SALVOS
# -------------------------
@app.post("/salvar-template")
async def salvar_template(
    arquivo: UploadFile = File(...)
):
    os.makedirs("templates", exist_ok=True)

    caminho = os.path.join(
        "templates",
        arquivo.filename
    )
    with open(caminho, "wb") as buffer:
        shutil.copyfileobj(
            arquivo.file,
            buffer
        )
    return {
        "mensagem": "Template salvo com sucesso",
        "arquivo": arquivo.filename
    }

@app.get("/templates")
async def listar_templates():

    os.makedirs("templates", exist_ok=True)
    arquivos = [
        arquivo
        for arquivo in os.listdir("templates")
        if arquivo.endswith(".docx")
    ]
    return {
        "templates": arquivos
    }

@app.get("/templates/{nome_template}/campos")
async def campos_template(nome_template: str):

    caminho_modelo = os.path.join(
        "templates",
        nome_template
    )

    if not os.path.exists(caminho_modelo):
        raise HTTPException(
            status_code=404,
            detail="Template não encontrado"
        )

    placeholders = extrair_placeholders(
        caminho_modelo
    )

    return {
        "campos": placeholders
    }

# -------------------------
# 5. GERAR TEMPLATES
# -------------------------
@app.post("/gerar-template")
def gerar_template_salvo(
    background_tasks: BackgroundTasks,
    template: str = Form(...),
    dados_json: str = Form(...)
):
    caminho_modelo = os.path.join(
        "templates",
        template
    )
    if not os.path.exists(caminho_modelo):
        raise HTTPException(
            status_code=404,
            detail="Template não encontrado"
        )
    try:
        dados = json.loads(dados_json)
    except:
        raise HTTPException(
            status_code=400,
            detail="JSON inválido"
        )
    doc = preencher_documento(
        caminho_modelo,
        dados
    )
    nome_saida = f"documento_{uuid.uuid4()}.docx"

    doc.save(nome_saida)

    background_tasks.add_task(
        os.remove,
        nome_saida
    )

    return FileResponse(
        path=nome_saida,
        filename=nome_saida,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        background=background_tasks
    )

@app.get("/frontend")
def frontend():
    return FileResponse("index.html")