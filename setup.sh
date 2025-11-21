#!/bin/bash

# ====================================
# Weather App - Script de Instalação
# ====================================

echo "🌤️  Weather App - Instalação Automática"
echo "========================================"
echo ""

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Verificar se está no diretório correto
if [ ! -f "ServerAPI.py" ]; then
    echo -e "${RED}❌ Erro: Execute este script no diretório WeatherApp${NC}"
    echo "   Uso: cd WeatherApp && ./setup.sh"
    exit 1
fi

echo -e "${BLUE}📋 Verificando pré-requisitos...${NC}"
echo ""

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 não encontrado${NC}"
    echo "   Instale Python 3.7+ e tente novamente"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo -e "${GREEN}✓ Python ${PYTHON_VERSION} encontrado${NC}"

# Verificar pip
if ! command -v pip3 &> /dev/null && ! command -v pip &> /dev/null; then
    echo -e "${RED}❌ pip não encontrado${NC}"
    echo "   Instale pip e tente novamente"
    exit 1
fi

echo -e "${GREEN}✓ pip encontrado${NC}"
echo ""

# Etapa 1: Criar ambiente virtual
echo -e "${YELLOW}1. Configurando ambiente virtual...${NC}"
if [ ! -d "venv" ]; then
    echo "   Criando ambiente virtual..."
    python3 -m venv venv
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}   ✓ Ambiente virtual criado${NC}"
    else
        echo -e "${RED}   ❌ Erro ao criar ambiente virtual${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}   ✓ Ambiente virtual já existe${NC}"
fi

# Ativar ambiente virtual
echo "   Ativando ambiente virtual..."
source venv/bin/activate

if [ $? -eq 0 ]; then
    echo -e "${GREEN}   ✓ Ambiente virtual ativado${NC}"
else
    echo -e "${RED}   ❌ Erro ao ativar ambiente virtual${NC}"
    exit 1
fi
echo ""

# Etapa 2: Instalar dependências
echo -e "${YELLOW}2. Instalando dependências Python...${NC}"
echo "   Isso pode levar alguns minutos..."
echo ""

pip install --upgrade pip --quiet 2>&1 | grep -v "already satisfied"

PACKAGES=("flask" "bcrypt" "requests" "PyJWT")

for package in "${PACKAGES[@]}"; do
    echo -n "   Instalando ${package}... "
    pip install "$package" --quiet 2>&1
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓${NC}"
    else
        echo -e "${RED}✗${NC}"
        echo -e "${RED}   Erro ao instalar ${package}${NC}"
        exit 1
    fi
done

echo ""
echo -e "${GREEN}✓ Todas as dependências instaladas${NC}"
echo ""

# Etapa 3: Verificar banco de dados
echo -e "${YELLOW}3. Verificando banco de dados SQLite...${NC}"

if [ -f "weatherapp.db" ]; then
    echo -e "${GREEN}   ✓ Banco de dados já existe${NC}"
    read -p "   Deseja recriar o banco? (s/N): " RECREATE
    if [[ "$RECREATE" =~ ^[Ss]$ ]]; then
        rm weatherapp.db
        echo "   Banco de dados removido"
    fi
fi

if [ ! -f "weatherapp.db" ]; then
    echo "   Inicializando banco de dados..."
    python3 -c "import ServerAPI; ServerAPI.init_db(); print('   ✓ Banco de dados inicializado')"
else
    echo -e "${GREEN}   ✓ Banco de dados pronto${NC}"
fi
echo ""

# Etapa 4: Verificar instalação
echo -e "${YELLOW}4. Verificando instalação...${NC}"

python3 -c "
import sys
try:
    import flask
    import bcrypt
    import requests
    import jwt
    import sqlite3
    print('   ✓ Todos os módulos importados com sucesso')
except ImportError as e:
    print(f'   ✗ Erro ao importar módulo: {e}')
    sys.exit(1)
"

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Erro na verificação${NC}"
    exit 1
fi
echo ""

# Etapa 5: Configuração opcional de email
echo -e "${YELLOW}5. Configuração de email (opcional)${NC}"
echo "   Para habilitar recuperação de senha, edite ServerAPI.py:"
echo "   - Linha 24: MAIL_USERNAME"
echo "   - Linha 25: MAIL_PASSWORD"
echo ""

# Resumo
echo -e "${GREEN}====================================${NC}"
echo -e "${GREEN}✓ Instalação concluída com sucesso!${NC}"
echo -e "${GREEN}====================================${NC}"
echo ""

# Informações finais
echo -e "${BLUE}📚 Próximos passos:${NC}"
echo ""
echo "   1. Para iniciar o servidor:"
echo -e "      ${YELLOW}source venv/bin/activate${NC}"
echo -e "      ${YELLOW}python ServerAPI.py${NC}"
echo ""
echo "   2. Acesse no navegador:"
echo -e "      ${BLUE}http://localhost:8080${NC}"
echo ""
echo "   3. Criar sua primeira conta e começar a usar!"
echo ""

# Perguntar se deseja iniciar agora
read -p "Deseja iniciar o servidor agora? (S/n): " START_NOW

if [[ ! "$START_NOW" =~ ^[Nn]$ ]]; then
    echo ""
    echo -e "${BLUE}🚀 Iniciando servidor...${NC}"
    echo -e "${YELLOW}   Pressione Ctrl+C para parar${NC}"
    echo ""
    sleep 2
    python ServerAPI.py
else
    echo ""
    echo -e "${GREEN}Para iniciar depois, execute:${NC}"
    echo -e "${YELLOW}  source venv/bin/activate && python ServerAPI.py${NC}"
    echo ""
fi
