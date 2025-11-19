# 🌤️ Weather App - Aplicação de Consulta Climática

Uma aplicação web moderna desenvolvida em Flask para consulta de condições climáticas em tempo real, com sistema completo de autenticação de usuários.

## 📋 Sobre o Projeto

Este projeto é uma aplicação web que permite aos usuários consultar informações meteorológicas de qualquer cidade do mundo. A aplicação conta com sistema de registro e login seguro, utilizando criptografia bcrypt para proteção de senhas e sessões persistentes.

## ✨ Funcionalidades

### 🔐 Autenticação
- **Registro de Usuários**: Cadastro com nome, email e senha
- **Login Seguro**: Autenticação com bcrypt e gerenciamento de sessões
- **Sessão Persistente**: Opção "Lembrar-me" com duração de 7 dias
- **Logout Seguro**: Encerramento de sessão com cookies de controle

### 🌍 Consulta Climática
- **Busca por Cidade**: Pesquisa de qualquer cidade do mundo
- **Informações em Tempo Real**:
  - 🌡️ Temperatura atual
  - 💨 Velocidade e direção do vento
  - 💧 Umidade relativa do ar
  - 🌅 Horário do nascer do sol
  - 🌇 Horário do pôr do sol
  - ☁️ Código de condição climática

## 🛠️ Tecnologias Utilizadas

### Backend
- **Flask**: Framework web Python
- **MySQL Connector**: Conexão com banco de dados MySQL
- **bcrypt**: Criptografia de senhas
- **Requests**: Requisições HTTP para APIs externas
- **UUID**: Geração de identificadores únicos

### Frontend
- **HTML5**: Estrutura das páginas
- **CSS3**: Estilização moderna com animações
- **Jinja2**: Sistema de templates do Flask
- **Google Fonts (Inter)**: Tipografia

### APIs Externas
- **Open-Meteo API**: Dados meteorológicos em tempo real
- **Geocoding API**: Conversão de nomes de cidades em coordenadas

### Banco de Dados
- **MySQL**: Armazenamento de dados dos usuários

## 📁 Estrutura do Projeto

```
ProjetoDeExtensao_Updatev2/
│
├── ServerAPI.py              # Aplicação principal Flask
├── Templates/                # Templates HTML
│   ├── base.html            # Template base com estilos globais
│   ├── login.html           # Página de login
│   ├── register.html        # Página de registro
│   └── dashboard.html       # Página principal de consulta
│
└── Prints_Atualizacao/      # Capturas de tela da aplicação
```

## 🗄️ Estrutura do Banco de Dados

### Tabela: `users`
```sql
CREATE TABLE users (
    id VARCHAR(36) PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    senha VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🚀 Como Executar

### Pré-requisitos
- Python 3.7+
- MySQL Server
- pip (gerenciador de pacotes Python)

### Instalação

1. **Clone ou baixe o projeto**
```bash
cd ProjetoDeExtensao_Updatev2
```

2. **Instale as dependências**
```bash
pip install flask mysql-connector-python bcrypt requests
```

3. **Configure o banco de dados MySQL**
```sql
CREATE DATABASE weatherapp;
USE weatherapp;

CREATE TABLE users (
    id VARCHAR(36) PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    senha VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

4. **Configure as credenciais do banco de dados**

Edite o arquivo `ServerAPI.py` e altere as credenciais de conexão:
```python
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="seu_usuario",
        password="sua_senha",
        database="weatherapp"
    )
```

5. **Execute a aplicação**
```bash
python ServerAPI.py
```

6. **Acesse no navegador**
```
http://localhost:8000
```

## 🎨 Interface do Usuário

### Design Moderno
- Tema escuro com gradientes radiais
- Efeitos de luz animados (breathing effect)
- Cards com glassmorphism (blur effect)
- Animações suaves de entrada
- Layout responsivo e centralizado

### Paleta de Cores
- **Primária**: #7b67ff (roxo vibrante)
- **Background**: #0d0f18 / #161926 (tons escuros)
- **Cards**: rgba(255, 255, 255, 0.07) com backdrop blur
- **Erro**: #ff4e70 (vermelho)
- **Sucesso**: #4effb0 (verde)

## 🔒 Segurança

### Medidas Implementadas
1. **Criptografia de Senhas**: bcrypt com salt automático
2. **Sessões Seguras**: 
   - HttpOnly cookies
   - SameSite='Lax'
   - Secret key para assinatura
3. **Validação de Dados**: Verificação de campos obrigatórios
4. **Proteção de Rotas**: Redirecionamento para login se não autenticado
5. **UUIDs**: Identificadores únicos para cada usuário

## 📡 APIs Utilizadas

### Open-Meteo API
- **Endpoint**: `https://api.open-meteo.com/v1/forecast`
- **Dados**: Temperatura, vento, umidade, nascer/pôr do sol
- **Gratuita**: Sem necessidade de API key

### Geocoding API
- **Endpoint**: `https://geocoding-api.open-meteo.com/v1/search`
- **Função**: Converter nomes de cidades em coordenadas (lat/lon)
- **Idioma**: Português (pt)

## 🔄 Fluxo da Aplicação

1. **Acesso Inicial** → Redirecionamento para página de login
2. **Novo Usuário** → Registro com validação de email único
3. **Login** → Autenticação e criação de sessão
4. **Dashboard** → Consulta de clima por cidade
5. **Logout** → Encerramento de sessão

## 🐛 Tratamento de Erros

- ❌ Email já cadastrado
- ❌ Credenciais inválidas
- ❌ Cidade não encontrada
- ❌ Erro na API de clima
- ❌ Campos obrigatórios vazios

## 📝 Notas de Desenvolvimento

### Configurações do Flask
- **Host**: 0.0.0.0 (aceita conexões externas)
- **Port**: 8000
- **Debug**: True (desenvolvimento)

### Sessões
- **Duração**: 7 dias (se "Lembrar-me" ativado)
- **Cookie de Último Usuário**: 30 dias

## 🔮 Possíveis Melhorias Futuras

- [ ] Histórico de buscas do usuário
- [ ] Favoritos de cidades
- [ ] Previsão para próximos dias
- [ ] Gráficos de temperatura
- [ ] Notificações de alertas climáticos
- [ ] Tema claro/escuro
- [ ] Recuperação de senha
- [ ] Validação de email
- [ ] Internacionalização (i18n)
- [ ] API REST própria

**Desenvolvido com ❤️ usando Flask e Open-Meteo API**
