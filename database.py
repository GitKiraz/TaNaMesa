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
    lado_a        TEXT    NOT NULL,   -- representação exibida na metade A
    lado_b        TEXT    NOT NULL,   -- representação exibida na metade B
    chave_a       TEXT    NOT NULL DEFAULT '',  -- função química da metade A (encaixe)
    chave_b       TEXT    NOT NULL DEFAULT '',  -- função química da metade B (encaixe)
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
    """Cria tabelas e popula dados iniciais se ainda não existirem.

    Faz uma migração suave: bancos antigos (sem as colunas de função nas
    peças) ganham as colunas e têm o conteúdo do dominó re-semeado, sem
    apagar usuários nem o histórico de partidas/jogadas.
    """
    with conn() as c:
        c.executescript(SCHEMA_SQL)
        _migrar_colunas(c)

        if c.execute("SELECT COUNT(*) AS n FROM nivel").fetchone()["n"] == 0:
            _seed_niveis(c)

        # (Re)semeia as peças se não houver peças ativas já no formato novo
        # (com função química preenchida). Peças antigas são apenas
        # desativadas — preservando as FKs em `jogada`.
        ativas = c.execute(
            "SELECT COUNT(*) AS n FROM peca WHERE ativo = 1 AND chave_a <> ''"
        ).fetchone()["n"]
        if ativas == 0:
            c.execute("UPDATE peca SET ativo = 0")
            _seed_pecas(c)


def _migrar_colunas(c):
    """Adiciona colunas novas em bancos criados por versões anteriores."""
    cols = {r["name"] for r in c.execute("PRAGMA table_info(peca)")}
    if "chave_a" not in cols:
        c.execute("ALTER TABLE peca ADD COLUMN chave_a TEXT NOT NULL DEFAULT ''")
    if "chave_b" not in cols:
        c.execute("ALTER TABLE peca ADD COLUMN chave_b TEXT NOT NULL DEFAULT ''")


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

# As quatro funções inorgânicas são as "pontas" que se encaixam: duas
# metades conectam quando pertencem à MESMA função. O aluno, portanto,
# joga classificando substâncias — não casando textos idênticos.
FUNCOES = ["acido", "base", "sal", "oxido"]

# Representações de cada função por nível. Quanto mais avançado o nível,
# mais abstratas/variadas as formas (fórmula → nome → propriedade).
REPRESENTACOES = {
    # FÁCIL — fórmula ↔ classificação (inclui o nome da função como dica)
    1: {
        "acido": ["HCl", "H2SO4", "HNO3", "H3PO4", "Ácido"],
        "base":  ["NaOH", "KOH", "Ca(OH)2", "Mg(OH)2", "Base"],
        "sal":   ["NaCl", "KNO3", "CaCO3", "Na2SO4", "Sal"],
        "oxido": ["CO2", "Na2O", "CaO", "Fe2O3", "Óxido"],
    },
    # MÉDIO — nome ↔ fórmula (exige nomenclatura)
    2: {
        "acido": ["HCl", "Ácido Clorídrico", "H2SO4", "Ácido Sulfúrico",
                  "HNO3", "Ácido Nítrico", "H2CO3", "Ácido Carbônico"],
        "base":  ["NaOH", "Hidróxido de Sódio", "KOH", "Hidróxido de Potássio",
                  "Ca(OH)2", "Hidróxido de Cálcio", "NH4OH", "Hidróxido de Amônio"],
        "sal":   ["NaCl", "Cloreto de Sódio", "CaCO3", "Carbonato de Cálcio",
                  "KNO3", "Nitrato de Potássio", "Na2SO4", "Sulfato de Sódio"],
        "oxido": ["CO2", "Dióxido de Carbono", "CaO", "Óxido de Cálcio",
                  "Fe2O3", "Óxido de Ferro III", "SO3", "Trióxido de Enxofre"],
    },
    # DIFÍCIL — mistura fórmula, nome e propriedades
    3: {
        "acido": ["HCl", "Libera H+ em água", "pH < 7", "Ácido Sulfúrico",
                  "Sabor azedo", "H3PO4"],
        "base":  ["NaOH", "Libera OH- em água", "pH > 7", "Hidróxido de Cálcio",
                  "Sabor adstringente", "KOH"],
        "sal":   ["NaCl", "Composto iônico", "Cátion + ânion",
                  "Carbonato de Cálcio", "Vem de ácido + base", "KNO3"],
        "oxido": ["CO2", "Óxido ácido", "Binário com oxigênio",
                  "Óxido de Ferro III", "Anidrido", "CaO"],
    },
}


def _gerar_pecas(repres, repeticoes=2):
    """
    Monta um conjunto de dominó *bem conectado* a partir das representações.

    Gera o conjunto completo (todos os pares de funções, inclusive os
    "duplos"), repetido `repeticoes` vezes, variando a forma exibida de
    cada função a cada uso. Isso garante que cada função apareça em muitas
    peças — então a mão distribuída quase sempre tem jogadas, acabando com
    o bug de "trava na 1ª peça".

    Retorna lista de (lado_a, chave_a, lado_b, chave_b, tipo_conexao).
    """
    contador = {k: 0 for k in repres}

    def proxima(k):
        formas = repres[k]
        forma = formas[contador[k] % len(formas)]
        contador[k] += 1
        return forma

    pecas = []
    for _ in range(repeticoes):
        for i in range(len(FUNCOES)):
            for j in range(i, len(FUNCOES)):
                ka, kb = FUNCOES[i], FUNCOES[j]
                pecas.append((proxima(ka), ka, proxima(kb), kb, f"{ka}-{kb}"))
    return pecas


def _seed_niveis(c):
    niveis = [
        ("Nível fácil",   1),
        ("Nível médio",   2),
        ("Nível difícil", 3),
    ]
    c.executemany("INSERT INTO nivel (descricao, ordem) VALUES (?, ?)", niveis)


def _seed_pecas(c):
    """Popula as peças do dominó de funções inorgânicas (todos os níveis)."""
    for ordem, repres in REPRESENTACOES.items():
        id_nivel = c.execute(
            "SELECT id_nivel FROM nivel WHERE ordem = ?", (ordem,)
        ).fetchone()["id_nivel"]
        c.executemany(
            "INSERT INTO peca (id_nivel, lado_a, chave_a, lado_b, chave_b, "
            "tipo_conexao) VALUES (?, ?, ?, ?, ?, ?)",
            [(id_nivel, la, ka, lb, kb, t)
             for (la, ka, lb, kb, t) in _gerar_pecas(repres)],
        )


if __name__ == "__main__":
    init_db()
    print(f"Banco inicializado em: {DB_PATH}")
