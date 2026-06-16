-- Schema MySQL do TáNaMesa (espelha o modelo da documentação, seção 5.3)
-- Para usar em produção: criar database, importar este arquivo e
-- substituir `database.py` por um adapter mysql-connector-python.

CREATE DATABASE IF NOT EXISTS tanamesa
    DEFAULT CHARACTER SET utf8mb4
    DEFAULT COLLATE utf8mb4_unicode_ci;

USE tanamesa;

CREATE TABLE IF NOT EXISTS usuario (
    id_usuario   INT AUTO_INCREMENT PRIMARY KEY,
    nome         VARCHAR(100) NOT NULL,
    email        VARCHAR(150) NOT NULL UNIQUE,
    senha        VARCHAR(255) NOT NULL,
    nickname     VARCHAR(50)  NOT NULL,
    tipo_usuario ENUM('aluno','professor') NOT NULL,
    criado_em    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS nivel (
    id_nivel  INT AUTO_INCREMENT PRIMARY KEY,
    descricao VARCHAR(50) NOT NULL,
    ordem     INT NOT NULL,
    ativo     TINYINT NOT NULL DEFAULT 1
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS peca (
    id_peca      INT AUTO_INCREMENT PRIMARY KEY,
    id_nivel     INT NOT NULL,
    lado_a       VARCHAR(100) NOT NULL,             -- representação exibida (metade A)
    lado_b       VARCHAR(100) NOT NULL,             -- representação exibida (metade B)
    chave_a      VARCHAR(20)  NOT NULL DEFAULT '',  -- função química p/ encaixe (metade A)
    chave_b      VARCHAR(20)  NOT NULL DEFAULT '',  -- função química p/ encaixe (metade B)
    tipo_conexao VARCHAR(30)  NOT NULL,
    ativo        TINYINT NOT NULL DEFAULT 1,
    FOREIGN KEY (id_nivel) REFERENCES nivel(id_nivel)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS partida (
    id_partida     INT AUTO_INCREMENT PRIMARY KEY,
    id_aluno       INT NOT NULL,
    id_nivel       INT NOT NULL,
    pontuacao      INT NOT NULL DEFAULT 0,
    acertos        INT NOT NULL DEFAULT 0,
    erros          INT NOT NULL DEFAULT 0,
    tempo_segundos INT NOT NULL DEFAULT 0,
    iniciada_em    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    encerrada_em   DATETIME NULL,
    FOREIGN KEY (id_aluno) REFERENCES usuario(id_usuario),
    FOREIGN KEY (id_nivel) REFERENCES nivel(id_nivel)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS jogada (
    id_jogada  INT AUTO_INCREMENT PRIMARY KEY,
    id_partida INT NOT NULL,
    id_peca    INT NOT NULL,
    acerto     TINYINT NOT NULL,
    feedback   VARCHAR(255),
    jogada_em  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_partida) REFERENCES partida(id_partida),
    FOREIGN KEY (id_peca)    REFERENCES peca(id_peca)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS relatorio (
    id_relatorio INT AUTO_INCREMENT PRIMARY KEY,
    id_professor INT NOT NULL,
    filtros      TEXT,
    formato      VARCHAR(10),
    arquivo_path TEXT,
    gerado_em    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_professor) REFERENCES usuario(id_usuario)
) ENGINE=InnoDB;
