# 🏭 Sistema de Ordens de Produção (Production Orders System)

Projeto de interconexão entre front-end, back-end e banco de dados desenvolvido como requisito para obtenção do título de **Técnico em Cibersistemas para Automação** pelo **SENAI** e **WEG** (Jaraguá do Sul/SC - 2026).

Este sistema visa gerenciar o ciclo de vida de ordens de produção industriais, alinhando-se aos conceitos da Indústria 4.0 e normas de comunicação industrial, servindo como uma ponte robusta entre o chão de fábrica e sistemas de gestão (ERP/MES).

---

## 🛠️ Tecnologias Utilizadas

O projeto foi construído utilizando uma arquitetura moderna e leve, dividida nas seguintes camadas:

* **Front-end:** HTML5, CSS3 e JavaScript (Vanilla).
* **Back-end:** Python 3 com microframework Flask.
* **Banco de Dados:** SQLite (Relacional).
* **Segurança:** Autenticação baseada em `API Key` e sanitização de dados de entrada.

---

## ✨ Funcionalidades

* **Dashboard Visual:** Interface web intuitiva para monitoramento de ordens e status da API em tempo real.
* **Gestão Completa (CRUD):**
  * Criação de novas ordens especificando produto e quantidade.
  * Leitura e listagem de ordens com filtros de status (*Pending*, *In Progress*, *Completed*).
  * Atualização dinâmica do status de produção.
  * Exclusão permanente de ordens.
* **Segurança Avançada:** Proteção contra ataques XSS (Cross-Site Scripting) via sanitização de inputs e rotas de modificação protegidas por chaves de API.
* **Rastreabilidade:** Geração automática de *timestamp* na criação de cada ordem.

---

## 🚀 Como Executar o Projeto Localmente

### Pré-requisitos
* [Python 3.x](https://www.python.org/downloads/) instalado na máquina.
* Gerenciador de pacotes `pip`.

### Passo a passo

1. **Clone este repositório:**
   ```bash
   git clone [https://github.com/seu-usuario/production-orders-system.git](https://github.com/seu-usuario/production-orders-system.git)
   cd production-orders-system
   ```

2. **Instale as dependências do Back-end:**
   ```bash
   pip install flask flask-cors python-dotenv
   ```

3. **Configure as Variáveis de Ambiente:**
   Crie um arquivo chamado `.env` na raiz do projeto e adicione a sua chave de segurança:
   ```env
   API_KEY=senai-cybersystems-2026-secure-key
   ```
   *(Nota: A chave acima deve coincidir com a chave configurada no arquivo `script.js` para que o front-end consiga se comunicar com as rotas protegidas).*

4. **Inicie o Servidor:**
   ```bash
   python app.py
   ```
   *O banco de dados `orders.db` será inicializado automaticamente caso não exista.*

5. **Acesse a Aplicação:**
   Abra o seu navegador e acesse: `http://localhost:5000`

---

## 📡 Documentação da API (Rotas)

A comunicação segue os padrões REST.

| Método | Rota | Descrição | Autenticação | Resposta de Sucesso |
| :--- | :--- | :--- | :---: | :--- |
| **GET** | `/status` | Health check da API | ❌ | `200 OK` (JSON com status) |
| **GET** | `/orders` | Lista todas as ordens (aceita `?status=`) | ❌ | `200 OK` (Array JSON) |
| **GET** | `/orders/<id>` | Busca uma ordem específica pelo ID | ❌ | `200 OK` (JSON da ordem) |
| **POST** | `/orders` | Cria nova ordem. Body: `{product, quantity}` | ✅ | `201 Created` |
| **PUT** | `/orders/<id>` | Atualiza o status. Body: `{status}` | ✅ | `200 OK` |
| **DELETE**| `/orders/<id>` | Remove uma ordem pelo ID | ✅ | `200 OK` |

*Para rotas com autenticação (✅), é obrigatório enviar o cabeçalho `X-API-Key` na requisição HTTP.*

---

## 🔒 Segurança e Tratamento de Erros

O sistema conta com tratamento global de erros HTTP, retornando mensagens padronizadas em formato JSON para facilitar a integração:

* `400 Bad Request`: Dados inválidos ou ausentes.
* `401 Unauthorized`: Autenticação necessária (API Key ausente).
* `403 Forbidden`: Acesso negado (API Key incorreta).
* `404 Not Found`: Recurso/Ordem não encontrada.
* `405 Method Not Allowed`: Método HTTP não permitido na rota.

---

## 👥 Autores

* **João Vitor Kasteller Debeterco**

Desenvolvido para a turma de Cibersistemas para Automação MA-77 (CentroWEG).
