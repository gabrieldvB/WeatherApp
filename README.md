# 🌤️ Weather App - Aplicação Completa de Clima

Uma aplicação web moderna desenvolvida em **Flask** e **SQLite** para consulta de condições climáticas em tempo real, com sistema completo de autenticação, histórico, favoritos e muito mais.

![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)
![SQLite](https://img.shields.io/badge/SQLite-3-lightgrey.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## ✨ Funcionalidades Principais

### 🔐 Autenticação e Segurança
- ✅ Sistema completo de registro e login
- ✅ Criptografia de senhas com **bcrypt**
- ✅ Recuperação de senha via email
- ✅ Validação de email com token único
- ✅ Sessões seguras (HttpOnly, SameSite)
- ✅ Tokens JWT para reset de senha
- ✅ Proteção contra SQL injection

### 🌍 Consulta de Clima
- ✅ Busca de clima por cidade em tempo real
- ✅ Informações completas:
  - 🌡️ Temperatura atual
  - 💨 Velocidade e direção do vento
  - 💧 Umidade relativa do ar
  - 🌅 Horário do nascer do sol
  - 🌇 Horário do pôr do sol
  - ☁️ Ícone da condição climática

### 📊 Recursos Avançados
- ✅ **Previsão de 7 dias** com temperaturas e precipitação
- ✅ **Gráficos interativos** (Chart.js) das próximas 24h
- ✅ **Histórico de buscas** (últimas 10 cidades)
- ✅ **Cidades favoritas** com acesso rápido
- ✅ **Tema claro/escuro** com toggle animado
- ✅ **Notificações toast** para alertas
- ✅ **Internacionalização** (PT/EN)

### 🔌 API REST
- ✅ Endpoint `/api/weather/<city>` para dados climáticos
- ✅ APIs para favoritos, histórico e configurações
- ✅ Respostas em JSON
- ✅ Autenticação de endpoints protegidos

## 🛠️ Tecnologias Utilizadas

### Backend
- **Python 3.7+**
- **Flask 3.0+** - Framework web
- **SQLite 3** - Banco de dados (sem necessidade de servidor)
- **bcrypt** - Criptografia de senhas
- **PyJWT** - Tokens de autenticação
- **Requests** - Requisições HTTP
- **smtplib** - Envio de emails

### Frontend
- **HTML5/CSS3** - Estrutura e estilização
- **JavaScript (Vanilla)** - Interatividade
- **Chart.js** - Gráficos interativos
- **Jinja2** - Templates dinâmicos
- **Google Fonts** - Tipografia (Inter)

### APIs Externas
- **Open-Meteo API** - Dados meteorológicos gratuitos
- **Geocoding API** - Conversão cidade → coordenadas

## 📁 Estrutura do Projeto

```
WeatherApp/
│
├── ServerAPI.py              # 🐍 Aplicação Flask principal
├── weatherapp.db             # 💾 Banco de dados SQLite
├── setup.sh                  # 🚀 Script de instalação automática
├── README.md                 # 📖 Documentação
│
├── templates/                # 📄 Templates HTML
│   ├── base.html            # Template base
│   ├── login.html           # Página de login
│   ├── register.html        # Página de registro
│   ├── dashboard.html       # Dashboard principal
│   ├── forgot_password.html # Recuperação de senha
│   └── reset_password.html  # Redefinição de senha
│
├── static/                   # 🎨 Arquivos estáticos
│   ├── css/
│   │   └── themes.css       # Estilos claro/escuro
│   └── js/
│       ├── theme.js         # Toggle de tema
│       └── charts.js        # Gráficos Chart.js
│
├── translations/             # 🌍 Arquivos de idioma
│   ├── pt.json              # Português
│   └── en.json              # Inglês
│
└── venv/                     # 📦 Ambiente virtual Python
```

## 🗄️ Estrutura do Banco de Dados (SQLite)

### Tabela: `users`
| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | TEXT | UUID único do usuário |
| nome | TEXT | Nome completo |
| email | TEXT | Email (único) |
| senha | TEXT | Hash bcrypt da senha |
| theme | TEXT | Tema preferido (dark/light) |
| language | TEXT | Idioma (pt/en) |
| email_verified | INTEGER | Email confirmado (0/1) |
| email_verification_token | TEXT | Token de verificação |
| created_at | TIMESTAMP | Data de criação |

### Tabela: `search_history`
| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | INTEGER | ID auto-incremento |
| user_id | TEXT | ID do usuário |
| city_name | TEXT | Nome da cidade |
| latitude | REAL | Latitude |
| longitude | REAL | Longitude |
| searched_at | TIMESTAMP | Data da busca |

### Tabela: `favorite_cities`
| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | INTEGER | ID auto-incremento |
| user_id | TEXT | ID do usuário |
| city_name | TEXT | Nome da cidade |
| latitude | REAL | Latitude |
| longitude | REAL | Longitude |
| added_at | TIMESTAMP | Data de adição |

### Tabela: `password_reset_tokens`
| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | INTEGER | ID auto-incremento |
| user_id | TEXT | ID do usuário |
| token | TEXT | Token JWT único |
| created_at | TIMESTAMP | Data de criação |
| expires_at | TIMESTAMP | Data de expiração |
| used | INTEGER | Token usado (0/1) |

## 🚀 Instalação e Execução

### 📋 Pré-requisitos
- **Python 3.7+**
- **pip** (gerenciador de pacotes Python)
- **Git** (opcional, para clonar o repositório)

### ⚡ Instalação Rápida (Recomendado)

Execute o script de instalação automática:

```bash
cd WeatherApp
chmod +x setup.sh
./setup.sh
```

O script irá:
1. ✅ Criar ambiente virtual Python
2. ✅ Instalar todas as dependências
3. ✅ Inicializar o banco de dados SQLite
4. ✅ Verificar a instalação
5. ✅ Iniciar o servidor automaticamente

### 🔧 Instalação Manual

#### 1. Clone ou baixe o repositório
```bash
git clone https://github.com/username/weather-app.git
cd weather-app/WeatherApp
```

#### 2. Crie um ambiente virtual
```bash
python3 -m venv venv
```

#### 3. Ative o ambiente virtual
```bash
# Linux/Mac
source venv/bin/activate

# Windows
venv\Scripts\activate
```

#### 4. Instale as dependências
```bash
pip install flask bcrypt requests PyJWT
```

#### 5. (Opcional) Configure o email
Edite `ServerAPI.py` (linhas 22-26) para habilitar recuperação de senha:

```python
app.config['MAIL_USERNAME'] = 'seu_email@gmail.com'
app.config['MAIL_PASSWORD'] = 'sua_senha_de_app'  # Senha de app do Gmail
```

**Como obter senha de app do Gmail:**
1. Acesse: https://myaccount.google.com/security
2. Ative "Verificação em duas etapas"
3. Vá em: https://myaccount.google.com/apppasswords
4. Gere uma senha de app

#### 6. Execute a aplicação
```bash
python ServerAPI.py
```

#### 7. Acesse no navegador
```
http://localhost:8080
```

### 🐳 Executar (após instalação)

```bash
cd WeatherApp
source venv/bin/activate  # Linux/Mac
python ServerAPI.py
```

### 🛑 Parar o servidor
Pressione `Ctrl + C` no terminal

## 🎯 Como Usar

### 1️⃣ Criar uma conta
1. Clique em "Criar conta"
2. Preencha nome, email e senha
3. (Opcional) Verifique seu email

### 2️⃣ Buscar clima
1. Digite o nome de uma cidade
2. Clique em "Buscar" ou pressione Enter
3. Visualize:
   - Temperatura atual
   - Previsão de 7 dias
   - Gráfico de 24 horas
   - Umidade, vento, nascer/pôr do sol

### 3️⃣ Adicionar favoritos
1. Após buscar uma cidade
2. Clique no botão "☆ Adicionar aos Favoritos"
3. Acesse rapidamente na barra lateral

### 4️⃣ Ver histórico
- Suas últimas 10 buscas aparecem automaticamente
- Clique para buscar novamente
- Use "Limpar histórico" para remover

### 5️⃣ Alternar tema
- Clique no toggle no topo da página
- Escolha entre tema claro ou escuro
- Preferência é salva automaticamente

## 🔧 Configurações Avançadas

### Alterar porta do servidor
Edite `ServerAPI.py` (linha 610):
```python
app.run(host="0.0.0.0", port=8080, debug=True)  # Altere 8080
```

### Desabilitar modo debug (produção)
```python
app.run(host="0.0.0.0", port=8080, debug=False)
```

### Adicionar novo idioma
1. Crie `translations/novo_idioma.json`
2. Copie a estrutura de `pt.json`
3. Traduza os valores

## 🐛 Solução de Problemas

### Erro: "Module not found"
```bash
pip install flask bcrypt requests PyJWT
```

### Erro: "Permission denied"
```bash
chmod +x setup.sh
```

### Porta 8080 em uso
Altere a porta em `ServerAPI.py` ou mate o processo:
```bash
lsof -ti:8080 | xargs kill -9
```

### Banco de dados corrompido
Delete `weatherapp.db` e reinicie a aplicação (será recriado)

## 📡 Documentação da API

### Endpoints Públicos

#### `GET /api/weather/<city>`
Retorna dados climáticos de uma cidade.

**Exemplo:**
```bash
curl http://localhost:8080/api/weather/London
```

**Resposta:** JSON com dados da Open-Meteo API

### Endpoints Autenticados

#### `POST /api/favorite`
Adiciona/remove cidade dos favoritos.

**Body:**
```json
{
  "city_name": "London",
  "latitude": 51.5074,
  "longitude": -0.1278
}
```

#### `DELETE /api/clear-history`
Limpa o histórico de buscas.

#### `POST /api/update-theme`
Atualiza tema (light/dark).

**Body:**
```json
{
  "theme": "light"
}
```

#### `POST /api/update-language`
Atualiza idioma (pt/en).

**Body:**
```json
{
  "language": "en"
}
```

## 📊 Estatísticas do Projeto

- **Linhas de código:** ~600 (Python)
- **Templates HTML:** 6
- **Tabelas do banco:** 4
- **APIs integradas:** 2
- **Idiomas suportados:** 2
- **Dependências:** 4

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📝 Licença

Este projeto é 100% open source.

## 👨‍💻 Autores
https://github.com/gabrieldvB && https://github.com/GalakCV

**Desenvolvido com ❤️ usando Flask, SQLite e Open-Meteo API**

---


⭐ Se este projeto foi útil, considere dar uma estrela no GitHub!
