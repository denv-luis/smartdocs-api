let templateSelecionado = null;
const fileInput = document.getElementById("arquivoInput");
const dropArea = document.getElementById("dropArea");
const filesList = document.getElementById("filesList");


async function carregarCamposAutomaticamente() {

    const arquivo = fileInput.files[0];

    if (!arquivo) return;

    const data = await extrairCampos(arquivo);

    console.log(data);

    mostrarCamposDetectados(data.campos);
}


dropArea.addEventListener("click", () => {
    fileInput.click();
});


dropArea.addEventListener("dragover", (e) => {

    e.preventDefault();

    dropArea.classList.add("dragover");
});


dropArea.addEventListener("dragleave", () => {

    dropArea.classList.remove("dragover");
});


dropArea.addEventListener("drop", async (e) => {

    e.preventDefault();

    dropArea.classList.remove("dragover");

    fileInput.files = e.dataTransfer.files;

    const file = fileInput.files[0];

    if (file) {

        filesList.innerHTML = "📄 " + file.name;

        await carregarCamposAutomaticamente();
    }
});

fileInput.addEventListener("change", async () => {

    const file = fileInput.files[0];

    if (file) {

        filesList.innerHTML = "📄 " + file.name;

        await carregarCamposAutomaticamente();
    }
});


function adicionarDadosAoFormulario(formData, dados, modo) {

    if (modo === "template") {

        formData.append(
            "dados_json",
            JSON.stringify(dados)
        );

    } else {

        formData.append(
            "substituicoes_json",
            JSON.stringify(dados)
        );
    }
}


document.getElementById("form").addEventListener("submit", async function(e) {

    e.preventDefault();

    const status = document.getElementById("status");

    const button =
        document.querySelector("button[type='submit']");

    status.innerText = "⏳ Processando...";

    document.getElementById("loader").style.display = "block";

    button.disabled = true;

    button.innerText = "Processando...";

    const formData = new FormData();

    // Arquivo
    const arquivo = fileInput.files[0];

    if (!arquivo && !templateSelecionado) {

        status.innerText =
            "❌ Selecione um arquivo ou um template salvo!";

        button.disabled = false;

        button.innerText = "Processar Documento";

        document.getElementById("loader").style.display =
            "none";

        return;
    }

    if (arquivo) {
        formData.append("arquivo", arquivo);
    }

    // Dados dos campos
    const dados = coletarDadosCampos();

    if (!validarCampos()) {

        status.innerText =
            "❌ Preencha todos os campos antes de continuar!";

        button.disabled = false;

        button.innerText = "Processar Documento";

        document.getElementById("loader").style.display =
            "none";

        return;
    }

    const modo =
        document.getElementById("modo").value;

    adicionarDadosAoFormulario(
        formData,
        dados,
        modo
    );

    try {

        let blob;
        if(templateSelecionado) {
            blob = await gerarTemplateSalvo(
                templateSelecionado,
                dados
            );
        } else {
            blob = await gerarDocumento(
                formData,
                modo
            );
        }

        const link =
            document.createElement("a");

        link.href =
            window.URL.createObjectURL(blob);

        link.download =
            "documento.docx";

        link.click();

        status.innerText =
            "✅ Documento gerado com sucesso!";

    } catch (error) {

        status.innerText =
            "❌ Erro: " + error.message;

    } finally {

        finalizarProcessamento(button);
    }
});

async function carregarTemplates() {

    const response = await fetch(
        `${API_URL}/templates`
    );

    const data = await response.json();

    const lista =
        document.getElementById("listaTemplates");

    lista.innerHTML = "";

    data.templates.forEach(template => {

        const div = document.createElement("div");

        div.classList.add("template-item");

        div.innerHTML =
            "📄 " +
            template.replace(".docx", "");

        div.addEventListener("click", () => {

            carregarTemplateSalvo(template);

        });

        lista.appendChild(div);

    });
}

async function carregarTemplateSalvo(nomeTemplate) {

    templateSelecionado = nomeTemplate;

    try {

        const modo =
            document.getElementById("modo");

        modo.value = "template";

        const arquivoInput =
            document.getElementById("arquivoInput");

        arquivoInput.value = "";

        document.getElementById("filesList").innerText =
            "📄 " + nomeTemplate;

        const data =
            await carregarCamposTemplate(nomeTemplate);

        mostrarCamposDetectados(data.campos);

    } catch (error) {

        document.getElementById("status").innerText =
            "❌ " + error.message;

    }

}

carregarTemplates();
