async function extrairCampos(arquivo) {
    const formData = new FormData();
    formData.append("arquivo", arquivo);

    const response = await fetch(
        `${API_URL}/extrair-campos`,
        {
            method: "POST",
            body: formData
        }
    );

    if (!response.ok) {
        throw new Error("Erro ao extrair campos.");
    }

    return await response.json();
    
}

async function gerarDocumento(formData, modo) {

    const rota =
        modo === "template"
            ? `${API_URL}/gerar-documento`
            : `${API_URL}/substituir-livre`;

    const response = await fetch(
        rota,
        {
            method: "POST",
            body: formData
        }
    );

    if (!response.ok) {
        throw new Error("Erro ao gerar documento");
    }

    return await response.blob();
}

async function carregarCamposTemplate(nomeTemplate) {

    const response = await fetch(
        `${API_URL}/templates/${encodeURIComponent(nomeTemplate)}/campos`
    );

    if (!response.ok) {
        throw new Error("Erro ao carregar campos do template");
    }

    return await response.json();
}

async function gerarTemplateSalvo(nomeTemplate, dados) {

    const formData = new FormData();

    formData.append(
        "template",
        nomeTemplate
    );

    formData.append(
        "dados_json",
        JSON.stringify(dados)
    );

    const response = await fetch(
        `${API_URL}/gerar-template`,
        {
            method: "POST",
            body: formData
        }
    );

    if (!response.ok) {
        throw new Error("Erro ao gerar documento pelo template");
    }

    return await response.blob();
}
