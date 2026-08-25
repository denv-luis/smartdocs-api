function adicionarCampo() {

    const container = document.getElementById("campos");

    const div = document.createElement("div");

    div.classList.add("campo", "fade-in");

    div.innerHTML = `
        <input
            type="text"
            placeholder="Campo (ex: empresa)"
            class="chave"
        >

        <input
            type="text"
            placeholder="Valor (ex: Empresa XPTO)"
            class="valor"
        >
    `;

    container.appendChild(div);
}

function limparFormulario() {

    // limpa arquivo
    document.getElementById("arquivoInput").value = "";

    // limpa nome do arquivo
    document.getElementById("filesList").innerHTML = "";

    // limpa campos
    document.getElementById("campos").innerHTML = "";

    // limpa contador
    document.getElementById("contadorCampos").innerText = "";

    // limpa status
    document.getElementById("status").innerText = "";

    // limpa preview
    document.getElementById("previewCampos").innerHTML = "";

    // esconde preview
    document.getElementById("previewBox").style.display = "none";
}

function mostrarCamposDetectados(campos) {

    const container = document.getElementById("campos");

    const previewBox =
        document.getElementById("previewBox");

    const previewCampos =
        document.getElementById("previewCampos");

    // limpa campos antigos
    container.innerHTML = "";

    previewCampos.innerHTML = "";

    document.getElementById("contadorCampos").innerText =
        campos.length + " campos detectados automaticamente";

    campos.forEach(campo => {

        // PREVIEW
        const item = document.createElement("div");

        item.classList.add("preview-item", "fade-in");

        item.innerHTML = `✓ ${campo}`;

        previewCampos.appendChild(item);

        // INPUTS
        const div = document.createElement("div");

        div.classList.add("campo");

        div.innerHTML = `
            <label>
                Campo detectado
            </label>

            <input
                type="text"
                class="chave"
                value="${campo}"
                readonly
            >

            <label>
                Valor
            </label>

            <input
                type="text"
                class="valor"
                placeholder="Digite o valor"
            >
        `;

        container.appendChild(div);
    });

    previewBox.style.display = "block";
}

function validarCampos() {

    let camposVazios = false;

    document.querySelectorAll("#campos .campo").forEach(div => {

        const inputValor = div.querySelector(".valor");

        const valor = inputValor.value.trim();

        inputValor.classList.remove("input-error");

        if (!valor) {
            camposVazios = true;

            inputValor.classList.add("input-error");
        }
    });

    return !camposVazios;
}

function coletarDadosCampos() {

    const dados = {};

    document.querySelectorAll("#campos .campo").forEach(div => {

        const chave =
            div.querySelector(".chave").value.trim();

        const valor =
            div.querySelector(".valor").value.trim();

        if (chave) {
            dados[chave] = valor;
        }
    });

    return dados;
}

function finalizarProcessamento(button) {

    button.disabled = false;

    button.innerText = "Processar Documento";

    document.getElementById("loader").style.display = "none";
}