# 📦 Product Management System

Sistema simples para gerenciamento de produtos com imagens, feito em **Python** e utilizando **Streamlit** para a interface web, **Azure Blob Storage** para o armazenamento de imagens e **SQL Server** como banco de dados relacional.

---

## 🚀 Funcionalidades

- Cadastro de novos produtos com:
  
  - Nome
  
  - Descrição
  
  - Preço
  
  - Upload de até 5 imagens (.jpg, .jpeg, .png)

- Validação de imagens:
  
  - Tamanho máximo: 5MB
  
  - Dimensões: entre 300x300px e 2000x2000px

- Armazenamento de imagens no **Azure Blob Storage**

- Armazenamento dos dados no **SQL Server**

- Listagem de todos os produtos cadastrados com exibição das imagens

---

## 🛠️ Tecnologias Utilizadas

- [Streamlit](https://streamlit.io/)

- [Azure Blob Storage](https://learn.microsoft.com/pt-br/azure/storage/blobs/)

- [Pymssql](http://www.pymssql.org/en/stable/)

- [Pillow (PIL)](https://python-pillow.org/)

- [Python-dotenv](https://pypi.org/project/python-dotenv/)

---

## ☁️ Configuração no Azure (Banco de Dados, Armazenamento e Grupo de Recursos)

### 1. 🔹 Criar Grupo de Recursos

- Acesse o [Portal do Azure](https://portal.azure.com/)
- Vá para **"Grupos de Recursos"** > **"Criar"**
- Preencha os dados e crie o grupo

### 2. 🗃️ Criar Conta de Armazenamento

- Vá em **"Contas de Armazenamento"** > **"Criar"**
- Após criar, acesse a conta > **"Contêineres"** > **Criar novo contêiner**
- Copie a **connection string** em **"Chaves de acesso"** ou **"Cadeia de Conexão"**

### 3. 🧱 Criar Banco de Dados SQL Server

- Vá para **"SQL Databases"** > **"Criar"**
- Crie um servidor SQL e banco de dados
- Libere seu IP no firewall do servidor
- Execute o seguinte script para criar as tabelas:

```sql
CREATE TABLE Produtos (
    id INT IDENTITY(1,1) PRIMARY KEY,
    nome NVARCHAR(100) NOT NULL,
    descricao NVARCHAR(1000) NOT NULL,
    preco DECIMAL(10, 2) NOT NULL
);

CREATE TABLE ProdutoImagens (
    id INT IDENTITY(1,1) PRIMARY KEY,
    produto_id INT NOT NULL,
    image_url NVARCHAR(255) NOT NULL,
    ordem INT NOT NULL DEFAULT 0,
    FOREIGN KEY (produto_id) REFERENCES Produtos(id)
);
```

---

## ⚙️ Instalação e Execução

### 1. Clonar o repositório

```bash
git clone https://github.com/seu-usuario/product-management-system.git
cd product-management-system
```

### 2. Criar e configurar o `.env`

Crie um arquivo `.env` com o seguinte conteúdo, substituindo com seus dados reais:

```env
BLOB_CONNECTION_STRING=your_azure_blob_connection_string
BLOB_CONTAINER_NAME=your_container_name
BLOB_ACCOUNT_NAME=your_account_name

SQL_SERVER=your_sql_server
SQL_DATABASE=your_database_name
SQL_USERNAME=your_username
SQL_PASSWORD=your_password
```

### 3. Crie e ative um ambiente virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

### 5. Instalar as dependências

```bash
pip install -r requirements.txt
```

### 5. Rodar a aplicação

```bash
streamlit run main.py
```

---

## 🖼️ Interface

### Cadastro de Produto

- Formulário para inserção de dados

- Upload de imagens com validação automática

- Armazenamento automático ao clicar em "Save Product"

### Lista de Produtos

- Exibição dos produtos salvos com nome, descrição, preço e imagens

---

## ✅ Requisitos das Imagens

- Formatos suportados: `.jpg`, `.jpeg`, `.png`

- Tamanho máximo por imagem: **5 MB**

- Dimensão mínima: **300x300 px**

- Dimensão máxima: **2000x2000 px**

- Máximo de **5 imagens por produto**

---

## 🧪 Exemplo de Uso

1. Preencha os dados do produto.

2. Faça upload das imagens.

3. Clique em **Save Product**.

4. Clique em **Load Products** para visualizar os produtos salvos.

---

## 🛡️ Observações de Segurança

- Não exponha seu arquivo `.env` em repositórios públicos.

- Assegure-se de configurar as permissões no **Azure Blob Storage** adequadamente.

- O código inclui rollback automático caso o upload de alguma imagem falhe.

---
