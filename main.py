import uuid
import streamlit as st
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceExistsError
import os
import pymssql
from dotenv import load_dotenv
from PIL import Image
import io

# Carregar variáveis de ambiente
load_dotenv()

# Azure Blob Storage
BLOB_CONNECTION_STRING = os.getenv('BLOB_CONNECTION_STRING')
BLOB_CONTAINER_NAME = os.getenv('BLOB_CONTAINER_NAME', 'default-container')
BLOB_ACCOUNT_NAME = os.getenv('BLOB_ACCOUNT_NAME', 'myblobaccount')

# Configurações de validação
MAX_IMAGE_SIZE_MB = 5  # Tamanho máximo por imagem em MB
MAX_IMAGE_DIMENSION = 2000  # Largura/altura máxima em pixels
MIN_IMAGE_DIMENSION = 300  # Largura/altura mínima em pixels
MAX_TOTAL_IMAGES = 5  # Número máximo de imagens por produto

# Inicializar cliente do Azure Blob
BLOB_SERVICE_CLIENT = BlobServiceClient.from_connection_string(BLOB_CONNECTION_STRING)

# SQL Server
SQL_SERVER = os.getenv('SQL_SERVER', 'localhost')
SQL_DATABASE = os.getenv('SQL_DATABASE', 'mydatabase')
SQL_USERNAME = os.getenv('SQL_USERNAME', 'sa')
SQL_PASSWORD = os.getenv('SQL_PASSWORD')

# Interface Streamlit
st.title("Product Management System")
st.subheader("Add New Product")

# Campos do formulário
product_name = st.text_input("Enter Product Name", "Sample Product", max_chars=100)
product_description = st.text_area("Enter Product Description", "This is a sample product description.", max_chars=1000)
product_price = st.number_input("Enter Product Price", min_value=0.0, step=0.10, format="%.2f")
product_images = st.file_uploader(
    "Upload Product Images", 
    type=["jpg", "jpeg", "png"], 
    accept_multiple_files=True,
    help=f"Upload up to {MAX_TOTAL_IMAGES} images (JPEG/PNG), each under {MAX_IMAGE_SIZE_MB}MB and between {MIN_IMAGE_DIMENSION}-{MAX_IMAGE_DIMENSION}px in dimensions."
)

def validate_inputs(name, description, price, images):
    """Valida todos os campos de entrada"""
    errors = []
    
    # Validação do nome do produto
    if not name or name.strip() == "":
        errors.append("⚠️ Product name is required.")
    elif len(name) > 100:
        errors.append("⚠️ Product name must be less than 100 characters.")
    
    # Validação da descrição
    if not description or description.strip() == "":
        errors.append("⚠️ Product description is required.")
    elif len(description) > 1000:
        errors.append("⚠️ Product description must be less than 1000 characters.")
    
    # Validação do preço
    if price <= 0:
        errors.append("⚠️ Product price must be greater than zero.")
    
    # Validação das imagens
    if not images:
        errors.append("⚠️ At least one product image is required.")
    else:
        if len(images) > MAX_TOTAL_IMAGES:
            errors.append(f"⚠️ You can upload a maximum of {MAX_TOTAL_IMAGES} images.")
        
        for image in images:
            # Verifica tamanho do arquivo
            if image.size > MAX_IMAGE_SIZE_MB * 1024 * 1024:  # Convert MB to bytes
                errors.append(f"⚠️ Image {image.name} is too large. Maximum size is {MAX_IMAGE_SIZE_MB}MB.")
            
            # Verifica dimensões da imagem
            try:
                img = Image.open(io.BytesIO(image.getvalue()))
                width, height = img.size
                
                if width > MAX_IMAGE_DIMENSION or height > MAX_IMAGE_DIMENSION:
                    errors.append(f"⚠️ Image {image.name} dimensions ({width}x{height}) are too large. Maximum allowed is {MAX_IMAGE_DIMENSION}x{MAX_IMAGE_DIMENSION}px.")
                
                if width < MIN_IMAGE_DIMENSION or height < MIN_IMAGE_DIMENSION:
                    errors.append(f"⚠️ Image {image.name} dimensions ({width}x{height}) are too small. Minimum required is {MIN_IMAGE_DIMENSION}x{MIN_IMAGE_DIMENSION}px.")
                
                if img.format.lower() not in ['jpeg', 'jpg', 'png']:
                    errors.append(f"⚠️ Image {image.name} has invalid format. Only JPEG and PNG are allowed.")
                
            except Exception as e:
                errors.append(f"⚠️ Could not process image {image.name}. It may be corrupted or in an unsupported format.")
    
    return errors

def upload_blob(file):
    """Faz upload de um arquivo para o Azure Blob Storage"""
    try:
        blob_name = str(uuid.uuid4()) + os.path.splitext(file.name)[1]  # Mantém a extensão original
        blob_client = BLOB_SERVICE_CLIENT.get_blob_client(container=BLOB_CONTAINER_NAME, blob=blob_name)
        
        # Verifica se o blob já existe (embora improvável com UUID)
        if blob_client.exists():
            raise ResourceExistsError(f"Blob {blob_name} already exists.")
        
        blob_client.upload_blob(file.read(), overwrite=True)
        image_url = f"https://{BLOB_ACCOUNT_NAME}.blob.core.windows.net/{BLOB_CONTAINER_NAME}/{blob_name}"
        st.success(f"Image uploaded successfully: {image_url}")
        return image_url
    except Exception as e:
        st.error(f"Error uploading image {file.name}: {e}")
        return None

def insert_product(product_name, product_description, product_price, product_images):
    """Insere um novo produto no banco de dados com imagens em tabela separada"""
    try:
        # Validação permanece a mesma
        validation_errors = validate_inputs(product_name, product_description, product_price, product_images)
        if validation_errors:
            for error in validation_errors:
                st.error(error)
            return False
        
        # Conexão com o banco de dados
        conn = pymssql.connect(server=SQL_SERVER, user=SQL_USERNAME, password=SQL_PASSWORD, database=SQL_DATABASE)
        cursor = conn.cursor()
        
        # 1. Insere o produto principal (sem imagens)
        query_produto = "INSERT INTO Produtos (nome, descricao, preco) OUTPUT INSERTED.id VALUES (%s, %s, %s)"
        cursor.execute(query_produto, (product_name, product_description, product_price))
        
        # Obtém o ID do produto recém-inserido
        produto_id = cursor.fetchone()[0]
        
        # 2. Insere cada imagem individualmente
        for idx, image in enumerate(product_images):
            image_url = upload_blob(image)
            if image_url:
                query_imagem = """
                INSERT INTO ProdutoImagens (produto_id, image_url, ordem) 
                VALUES (%s, %s, %s)
                """
                cursor.execute(query_imagem, (produto_id, image_url, idx))
            else:
                conn.rollback()  # Reverte tudo se algum upload falhar
                conn.close()
                return False
        
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        st.error(f"Error inserting product: {str(e)}")
        return False
    
def list_products():
    """Lista todos os produtos do banco de dados"""
    try:
        conn = pymssql.connect(server=SQL_SERVER, user=SQL_USERNAME, password=SQL_PASSWORD, database=SQL_DATABASE)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Produtos ORDER BY nome")
        products = cursor.fetchall()
        conn.close()
        return products
    except Exception as e:
        st.error(f"Error fetching products: {str(e)}")
        return []
    
def list_products_screen():
    """Exibe a lista de produtos na interface"""
    products = list_products()
    
    if not products:
        st.info("No products found in the database.")
        return
    
    for product in products:
        st.subheader(product[1])  # nome
        st.write(f"**Description:** {product[2]}")  # descricao
        st.write(f"**Price:** ${product[3]:.2f}")  # preco
        
        # Você precisará implementar a recuperação de imagens aqui (produto_id = product[0])
        # Exemplo (se quiser buscar imagens relacionadas):
        conn = pymssql.connect(server=SQL_SERVER, user=SQL_USERNAME, password=SQL_PASSWORD, database=SQL_DATABASE)
        cursor = conn.cursor()
        cursor.execute("SELECT image_url FROM ProdutoImagens WHERE produto_id = %s ORDER BY ordem", (product[0],))
        images = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        if images:
            cols = st.columns(len(images))
            for idx, url in enumerate(images):
                try:
                    cols[idx].image(url, width=150, caption=f"Image {idx+1}")
                except:
                    cols[idx].error(f"Could not load image from URL: {url}")
        
        st.markdown("---")
       
# Botão para salvar produto
if st.button('Save Product'):
    if insert_product(product_name, product_description, product_price, product_images if product_images else []):
        st.success("Product saved successfully!")
        # Limpa os campos após o sucesso (opcional)
        product_name = ""
        product_description = ""
        product_price = 0.0
        product_images = []

# Botão para listar produtos
st.header("Product List")
if st.button('Load Products'):
    list_products_screen()