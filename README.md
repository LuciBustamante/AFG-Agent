# AFG-Agent
Criado com base no curso da WoMakersCode - 'Azure Frontier Girls'.

### :heavy_exclamation_mark: Importante
Agente criado com a ajuda do Gemini, pois não consegui abrir a conta na Azure

#### :cop: Sobre o agente:
**Criação de PR:** Cria um PR seguindo um template de boas práticas (Contexto, O que foi feito, Como testar), incentivando descrições ricas;

**Monitoramento (Timer):** Lista os PRs abertos e mostra um contador de tempo colorido (verde/amarelo/vermelho) indicando há quanto tempo o código está esperando revisão.


:pencil2: **Pré-requisitos e passo a passo**
1) Você precisará instalar as bibliotecas PyGithub (para a API) e rich (para o visual no terminal):

```
pip install PyGithub rich python-dotenv
```
2) Obtenha um Token do GitHub:
Vá em GitHub Settings -> Developer Settings -> Personal Access Tokens -> Tokens (classic).
Gere um token com permissão de repo.

3) Crie o arquivo .env:
Na mesma pasta do script, crie um arquivo chamado .env e cole o token:
```
GITHUB_TOKEN=ghp_SeuTokenSuperSecretoAqui123456
```

:paw_prints: **Como usar**
1) Para verificar o tempo dos PRs (O Contador):
Isso mostrará uma tabela colorida. Se o PR estiver aberto há mais de 3 dias, ficará Vermelho (Crítico).
```
python agent_pr.py status
```

2) Para abrir um novo PR (Boas Práticas):
O agente fará perguntas específicas para forçar você a não escrever apenas "bug fix" na descrição.
```
python agent_pr.py create
```
