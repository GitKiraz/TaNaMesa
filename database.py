"""
Camada de acesso a dados do TáNaMesa.

Por padrão usa SQLite (zero-instalação). A documentação prevê MySQL
para produção — o schema equivalente está em `schema_mysql.sql`.
"""
import hashlib
import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "tanamesa.db")


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS usuario (
    id_usuario   INTEGER PRIMARY KEY AUTOINCREMENT,
    nome         TEXT    NOT NULL,
    email        TEXT    NOT NULL UNIQUE,
    senha        TEXT    NOT NULL,
    nickname     TEXT    NOT NULL,
    tipo_usuario TEXT    NOT NULL CHECK (tipo_usuario IN ('aluno','professor')),
    criado_em    TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS nivel (
    id_nivel  INTEGER PRIMARY KEY AUTOINCREMENT,
    descricao TEXT    NOT NULL,
    ordem     INTEGER NOT NULL,
    ativo     INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS peca (
    id_peca       INTEGER PRIMARY KEY AUTOINCREMENT,
    id_nivel      INTEGER NOT NULL,
    lado_a        TEXT    NOT NULL,
    lado_b        TEXT    NOT NULL,
    tipo_conexao  TEXT    NOT NULL,
    ativo         INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (id_nivel) REFERENCES nivel(id_nivel)
);

CREATE TABLE IF NOT EXISTS partida (
    id_partida      INTEGER PRIMARY KEY AUTOINCREMENT,
    id_aluno        INTEGER NOT NULL,
    id_nivel        INTEGER NOT NULL,
    pontuacao       INTEGER NOT NULL DEFAULT 0,
    acertos         INTEGER NOT NULL DEFAULT 0,
    erros           INTEGER NOT NULL DEFAULT 0,
    tempo_segundos  INTEGER NOT NULL DEFAULT 0,
    iniciada_em     TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    encerrada_em    TEXT,
    FOREIGN KEY (id_aluno) REFERENCES usuario(id_usuario),
    FOREIGN KEY (id_nivel) REFERENCES nivel(id_nivel)
);

CREATE TABLE IF NOT EXISTS jogada (
    id_jogada   INTEGER PRIMARY KEY AUTOINCREMENT,
    id_partida  INTEGER NOT NULL,
    id_peca     INTEGER NOT NULL,
    acerto      INTEGER NOT NULL,
    feedback    TEXT,
    jogada_em   TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_partida) REFERENCES partida(id_partida),
    FOREIGN KEY (id_peca)    REFERENCES peca(id_peca)
);

CREATE TABLE IF NOT EXISTS relatorio (
    id_relatorio  INTEGER PRIMARY KEY AUTOINCREMENT,
    id_professor  INTEGER NOT NULL,
    filtros       TEXT,
    formato       TEXT,
    arquivo_path  TEXT,
    gerado_em     TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_professor) REFERENCES usuario(id_usuario)
);
"""


@contextmanager
def conn():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA foreign_keys = ON")
    try:
        yield c
        c.commit()
    finally:
        c.close()


def hash_senha(senha: str) -> str:
    return hashlib.sha256(senha.encode("utf-8")).hexdigest()


def init_db():
    """Cria tabelas e popula dados iniciais se ainda não existirem."""
    with conn() as c:
        c.executescript(SCHEMA_SQL)
        cur = c.execute("SELECT COUNT(*) AS n FROM nivel")
        if cur.fetchone()["n"] == 0:
            _seed(c)


# ---------------------------------------------------------------- Usuário ---

def criar_usuario(nome, email, senha, nickname, tipo_usuario):
    with conn() as c:
        c.execute(
            "INSERT INTO usuario (nome, email, senha, nickname, tipo_usuario) "
            "VALUES (?, ?, ?, ?, ?)",
            (nome, email, hash_senha(senha), nickname, tipo_usuario),
        )


def autenticar(email, senha, tipo_usuario):
    with conn() as c:
        row = c.execute(
            "SELECT * FROM usuario WHERE email = ? AND senha = ? AND tipo_usuario = ?",
            (email, hash_senha(senha), tipo_usuario),
        ).fetchone()
        return dict(row) if row else None


def atualizar_usuario(id_usuario, nome, email, nickname, senha=None):
    with conn() as c:
        if senha:
            c.execute(
                "UPDATE usuario SET nome=?, email=?, nickname=?, senha=? WHERE id_usuario=?",
                (nome, email, nickname, hash_senha(senha), id_usuario),
            )
        else:
            c.execute(
                "UPDATE usuario SET nome=?, email=?, nickname=? WHERE id_usuario=?",
                (nome, email, nickname, id_usuario),
            )


def buscar_usuario(id_usuario):
    with conn() as c:
        row = c.execute(
            "SELECT * FROM usuario WHERE id_usuario = ?", (id_usuario,)
        ).fetchone()
        return dict(row) if row else None


# ---------------------------------------------------------------- Níveis ----

def listar_niveis():
    with conn() as c:
        rows = c.execute(
            "SELECT * FROM nivel WHERE ativo = 1 ORDER BY ordem"
        ).fetchall()
        return [dict(r) for r in rows]


# ---------------------------------------------------------------- Peças -----

def carregar_pecas(id_nivel):
    with conn() as c:
        rows = c.execute(
            "SELECT * FROM peca WHERE id_nivel = ? AND ativo = 1",
            (id_nivel,),
        ).fetchall()
        return [dict(r) for r in rows]


# ---------------------------------------------------------------- Partida ---

def iniciar_partida(id_aluno, id_nivel):
    with conn() as c:
        cur = c.execute(
            "INSERT INTO partida (id_aluno, id_nivel) VALUES (?, ?)",
            (id_aluno, id_nivel),
        )
        return cur.lastrowid


def registrar_jogada(id_partida, id_peca, acerto, feedback):
    with conn() as c:
        c.execute(
            "INSERT INTO jogada (id_partida, id_peca, acerto, feedback) "
            "VALUES (?, ?, ?, ?)",
            (id_partida, id_peca, 1 if acerto else 0, feedback),
        )


def encerrar_partida(id_partida, pontuacao, acertos, erros, tempo_segundos):
    with conn() as c:
        c.execute(
            "UPDATE partida SET pontuacao=?, acertos=?, erros=?, "
            "tempo_segundos=?, encerrada_em=? WHERE id_partida=?",
            (pontuacao, acertos, erros, tempo_segundos,
             datetime.now().isoformat(timespec="seconds"), id_partida),
        )


# ---------------------------------------------------------------- Relatório -

def gerar_relatorio(id_professor, filtros=""):
    """Retorna lista de partidas dos alunos para visualização."""
    with conn() as c:
        rows = c.execute(
            """SELECT p.id_partida, u.nome, u.nickname, n.descricao AS nivel,
                      p.pontuacao, p.acertos, p.erros, p.tempo_segundos,
                      p.iniciada_em, p.encerrada_em
               FROM partida p
               JOIN usuario u ON u.id_usuario = p.id_aluno
               JOIN nivel n   ON n.id_nivel   = p.id_nivel
               WHERE p.encerrada_em IS NOT NULL
               ORDER BY p.encerrada_em DESC""",
        ).fetchall()
        c.execute(
            "INSERT INTO relatorio (id_professor, filtros, formato) VALUES (?, ?, ?)",
            (id_professor, filtros, "tela"),
        )
        return [dict(r) for r in rows]


# ---------------------------------------------------------------- Seed ------

def _seed(c):
    """Popula níveis e peças do dominó de funções inorgânicas."""
    niveis = [
        ("Nível fácil",   1),
        ("Nível médio",   2),
        ("Nível difícil", 3),
    ]
    c.executemany("INSERT INTO nivel (descricao, ordem) VALUES (?, ?)", niveis)

    # Cada peça: (lado_a, lado_b, tipo_conexao)
    # Para que duas peças "conectem", o valor textual exposto em uma extremidade
    # deve ser igual ao valor textual da extremidade adjacente.
    # Convenção: usar a forma canônica do conceito (ex.: "Ácido", "HCl", "Base").

    # ----- FÁCIL: associação por classificação (função inorgânica) -----
    faceis = [
        ("HCl",     "Ácido",   "formula-classificacao"),
        ("Ácido",   "H2SO4",   "classificacao-formula"),
        ("H2SO4",   "Ácido",   "formula-classificacao"),
        ("Ácido",   "HNO3",    "classificacao-formula"),
        ("NaOH",    "Base",    "formula-classificacao"),
        ("Base",    "KOH",     "classificacao-formula"),
        ("KOH",     "Base",    "formula-classificacao"),
        ("Base",    "Ca(OH)2", "classificacao-formula"),
        ("NaCl",    "Sal",     "formula-classificacao"),
        ("Sal",     "KNO3",    "classificacao-formula"),
        ("CaCO3",   "Sal",     "formula-classificacao"),
        ("Sal",     "CO2",     "classificacao-formula"),  # ponte intencional p/ óxido
        ("CO2",     "Óxido",   "formula-classificacao"),
        ("Óxido",   "Na2O",    "classificacao-formula"),
        ("Na2O",    "Óxido",   "formula-classificacao"),
        ("Óxido",   "HCl",     "classificacao-formula"),  # fecha o ciclo
    ]

    # ----- MÉDIO: associação por nome ↔ fórmula -----
    medios = [
        ("HCl",                  "Ácido Clorídrico", "formula-nome"),
        ("Ácido Clorídrico",     "H2SO4",            "nome-formula"),
        ("H2SO4",                "Ácido Sulfúrico",  "formula-nome"),
        ("Ácido Sulfúrico",      "HNO3",             "nome-formula"),
        ("HNO3",                 "Ácido Nítrico",    "formula-nome"),
        ("Ácido Nítrico",        "NaOH",             "nome-formula"),
        ("NaOH",                 "Hidróxido de Sódio","formula-nome"),
        ("Hidróxido de Sódio",   "KOH",              "nome-formula"),
        ("KOH",                  "Hidróxido de Potássio","formula-nome"),
        ("Hidróxido de Potássio","NaCl",             "nome-formula"),
        ("NaCl",                 "Cloreto de Sódio", "formula-nome"),
        ("Cloreto de Sódio",     "CaCO3",            "nome-formula"),
        ("CaCO3",                "Carbonato de Cálcio","formula-nome"),
        ("Carbonato de Cálcio",  "CO2",              "nome-formula"),
        ("CO2",                  "Dióxido de Carbono","formula-nome"),
        ("Dióxido de Carbono",   "HCl",              "nome-formula"),
    ]

    # ----- DIFÍCIL: mistura nomes, fórmulas, propriedades e classificações -----
    dificeis = [
        ("HCl",                "Libera H+ em água", "formula-propriedade"),
        ("Libera H+ em água",  "Ácido",             "propriedade-classificacao"),
        ("Ácido",              "Ácido Sulfúrico",   "classificacao-nome"),
        ("Ácido Sulfúrico",    "H2SO4",             "nome-formula"),
        ("H2SO4",              "pH < 7",            "formula-propriedade"),
        ("pH < 7",             "HNO3",              "propriedade-formula"),
        ("HNO3",               "Ácido Nítrico",     "formula-nome"),
        ("Ácido Nítrico",      "NaOH",              "nome-formula"),
        ("NaOH",               "Libera OH- em água","formula-propriedade"),
        ("Libera OH- em água", "Base",              "propriedade-classificacao"),
        ("Base",               "Hidróxido de Potássio","classificacao-nome"),
        ("Hidróxido de Potássio","KOH",             "nome-formula"),
        ("KOH",                "pH > 7",            "formula-propriedade"),
        ("pH > 7",             "Ca(OH)2",           "propriedade-formula"),
        ("Ca(OH)2",            "Hidróxido de Cálcio","formula-nome"),
        ("Hidróxido de Cálcio","NaCl",              "nome-formula"),
        ("NaCl",               "Composto iônico",   "formula-propriedade"),
        ("Composto iônico",    "Sal",               "propriedade-classificacao"),
        ("Sal",                "Carbonato de Cálcio","classificacao-nome"),
        ("Carbonato de Cálcio","CO2",               "nome-formula"),
        ("CO2",                "Óxido ácido",       "formula-propriedade"),
        ("Óxido ácido",        "Óxido",             "propriedade-classificacao"),
        ("Óxido",              "Na2O",              "classificacao-formula"),
        ("Na2O",               "HCl",               "formula-formula"),
    ]

    for descricao, ordem, lote in [
        ("Nível fácil",   1, faceis),
        ("Nível médio",   2, medios),
        ("Nível difícil", 3, dificeis),
    ]:
        id_nivel = c.execute(
            "SELECT id_nivel FROM nivel WHERE ordem = ?", (ordem,)
        ).fetchone()["id_nivel"]
        c.executemany(
            "INSERT INTO peca (id_nivel, lado_a, lado_b, tipo_conexao) "
            "VALUES (?, ?, ?, ?)",
            [(id_nivel, a, b, t) for (a, b, t) in lote],
        )


if __name__ == "__main__":
    init_db()
    print(f"Banco inicializado em: {DB_PATH}")
