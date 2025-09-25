CREATE TABLE funcionario (
    id_funcionario INTEGER PRIMARY KEY AUTOINCREMENT,  
    nome TEXT NOT NULL UNIQUE,                          
    email TEXT NOT NULL,                                
    saldo_total REAL NOT NULL                           
);
