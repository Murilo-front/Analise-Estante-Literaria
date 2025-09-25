CREATE TABLE venda (
    id_livro INTEGER PRIMARY KEY AUTOINCREMENT,  
    nome_registro TEXT NOT NULL,                 
    nome_livro TEXT NOT NULL,                    
    valor REAL NOT NULL,                         
    data_venda TEXT NOT NULL                     
);
