# Sistema de Consulta de Materiais com Login

Sistema completo de consulta e gerenciamento de materiais com sistema de autenticação e controle de acesso por níveis de usuário.

## 🔐 Credenciais de Administrador
- **Usuário:** admin
- **Senha:** kowa2013

## 🚀 Instalação e Execução

### Pré-requisitos
- Python 3.11 ou superior
- pip (gerenciador de pacotes Python)

### Passos para instalação

1. **Clonar o repositório**
   ```bash
   git clone https://github.com/kowalskymansur/portal.git
   cd portal
   ```

2. **Criar ambiente virtual**
   ```bash
   python -m venv venv
   ```

3. **Ativar ambiente virtual**
   - **Linux/Mac:**
     ```bash
     source venv/bin/activate
     ```
   - **Windows:**
     ```bash
     venv\Scripts\activate
     ```

4. **Instalar dependências**
   ```bash
   pip install -r requirements.txt
   ```

5. **Executar o sistema**
   ```bash
   python src/main.py
   ```

6. **Acessar o sistema**
   - Abra o navegador e acesse: `http://localhost:5000`
   - Faça login com as credenciais de administrador

## 👥 Níveis de Acesso

### 1. Leitura
- Visualizar materiais
- Pesquisar e filtrar
- Exportar dados

### 2. Edição
- Todas as funcionalidades de "Leitura"
- Cadastrar novos materiais
- Editar materiais existentes

### 3. Exclusão
- Todas as funcionalidades de "Edição"
- Excluir materiais
- Gerenciar categorias

### 4. Administrador
- Todas as funcionalidades de "Exclusão"
- Gerenciar usuários
- Criar, editar e excluir usuários
- Alterar níveis de acesso

## 🛠️ Funcionalidades

### Sistema de Autenticação
- Login seguro com hash de senhas
- Sessões persistentes
- Logout funcional

### Gerenciamento de Materiais
- 206 materiais pré-cadastrados
- Pesquisa avançada
- Filtros por categoria
- Exportação para Excel
- Impressão otimizada

### Administração de Usuários (apenas administradores)
- Criar novos usuários
- Definir níveis de acesso
- Ativar/desativar usuários
- Excluir usuários
- Pesquisar e filtrar usuários

### Interface
- Design responsivo
- Modo escuro/claro
- Navegação por abas
- Controle de acesso dinâmico

## 📊 Dados
O sistema inclui 206 materiais organizados em 3 categorias:
- **Materiais de Rede** (códigos MP*)
- **Materiais de Construção** (códigos MC*)
- **Acessórios e Instrumentos** (códigos AI*)

## 🔧 Tecnologias Utilizadas
- **Backend:** Flask, SQLAlchemy, SQLite
- **Frontend:** HTML5, CSS3, JavaScript
- **Autenticação:** bcrypt, JWT
- **Banco de Dados:** SQLite

## 📝 Observações Importantes
- O banco de dados é criado automaticamente na primeira execução
- O usuário administrador é criado automaticamente
- Os dados são persistidos no arquivo `src/database/app.db`
- Para backup, copie o arquivo do banco de dados

## 🆘 Suporte
Em caso de problemas:
1. Verifique se todas as dependências foram instaladas
2. Certifique-se de que a porta 5000 está disponível
3. Verifique se o ambiente virtual está ativado
4. Consulte os logs no terminal para identificar erros

## 📄 Licença
Sistema desenvolvido para gerenciamento de materiais de almoxarifado.

