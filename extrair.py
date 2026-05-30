
<!DOCTYPE html>

<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Marketing IA</title>

<style>
body{
    font-family: Arial, sans-serif;
    background:#1f2937;
    color:white;
    margin:0;
    padding:20px;
}

.container{
    max-width:900px;
    margin:auto;
}

.card{
    background:#374151;
    padding:20px;
    border-radius:10px;
    margin-bottom:20px;
}

input{
    width:100%;
    padding:12px;
    border:none;
    border-radius:8px;
    margin-bottom:10px;
}

button{
    padding:12px 20px;
    border:none;
    border-radius:8px;
    cursor:pointer;
    font-weight:bold;
}

.primary{
    background:#4f46e5;
    color:white;
}

.resultado{
    background:#111827;
    padding:15px;
    border-radius:10px;
    margin-top:15px;
    white-space:pre-wrap;
}
</style>

</head>

<body>

<div class="container">

<div class="card">
<h2>🚀 Marketing IA</h2>

<input
id="apiKey"
type="password"
placeholder="Cole sua chave Gemini aqui">

<input
id="produto"
type="text"
placeholder="Cole o link do produto">

<button class="primary" onclick="gerar()">
Gerar Marketing
</button>
</div>

<div id="saida" class="resultado"></div>

</div>

<script>
async function gerar(){

    const apiKey =
        document.getElementById("apiKey").value.trim();

    const link =
        document.getElementById("produto").value.trim();

    if(!apiKey){
        alert("Informe sua chave Gemini.");
        return;
    }

    if(!link){
        alert("Informe o link do produto.");
        return;
    }

    const prompt = `
Você é especialista em marketing digital.

Crie:

1. Texto para WhatsApp
2. Texto Instagram
3. Texto Facebook
4. Benefícios do produto
5. Gatilhos de urgência
6. 10 hashtags

Produto:
${link}
`;

    document.getElementById("saida").textContent =
        "Gerando...";

    try{

        const response = await fetch(
            "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=" + apiKey,
            {
                method:"POST",
                headers:{
                    "Content-Type":"application/json"
                },
                body:JSON.stringify({
                    contents:[
                        {
                            parts:[
                                {
                                    text:prompt
                                }
                            ]
                        }
                    ]
                })
            }
        );

        const data = await response.json();

        const texto =
            data.candidates?.[0]?.content?.parts?.[0]?.text
            || "Nenhuma resposta recebida.";

        document.getElementById("saida").textContent =
            texto;

    }catch(error){

        document.getElementById("saida").textContent =
            "Erro: " + error.message;

    }
}
</script>

</body>
</html>
