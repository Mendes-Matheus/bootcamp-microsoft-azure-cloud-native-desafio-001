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

        