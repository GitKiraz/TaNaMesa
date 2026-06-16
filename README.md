# TáNaMesa — Dominó Digital de Funções Inorgânicas

Gamificação acadêmica do curso de Ciência da Computação do Instituto Mauá
de Tecnologia, em parceria com a Etec Júlio de Mesquita, para apoio ao
aprendizado das funções inorgânicas no Ensino Médio.

O aluno monta uma corrente de dominó **conectando substâncias da mesma
função química** (ácido, base, sal ou óxido), classificando fórmulas,
nomes e propriedades.

## Como executar

Requer **Python 3.10+** com `tkinter` (já incluso na maioria das distribuições).

### 1. Ambiente Python (venv)

```bash
python -m venv .venv
.venv/bin/python -m pip install -r requirements.txt   # instala o driver MySQL
```

### 2. Banco de dados — MySQL via Docker (recomendado)

```bash
docker compose up -d        # sobe o MySQL em container (espera ~10s na 1ª vez)
```

### 3. Rodar o app

```bash
.venv/bin/python src/main.py
```

> **Sem Docker?** Sem problema: se o MySQL não estiver acessível, o app
> **cai automaticamente para SQLite** (arquivo local `src/tanamesa.db`,
> criado na hora). Ou seja, `python src/main.py` roda de qualquer jeito.

O schema e as peças do dominó dos três níveis são criados/semeados
automaticamente na primeira execução, em qualquer um dos bancos.

## Estrutura

```
TaNaMesa/
├── docker-compose.yml     # MySQL local para dev/apresentação
├── requirements.txt       # mysql-connector-python (driver primário)
├── README.md
├── sql/
│   └── schema_mysql.sql   # schema MySQL de referência (import manual opcional)
└── src/
    ├── main.py            # entry point + roteador de telas (Aplicativo)
    ├── constants.py       # paleta visual
    ├── ui.py              # componentes Canvas (botões/peças/avatar arredondados)
    ├── widgets.py         # componentes de layout (barra lateral, cards, forms)
    ├── database.py        # acesso a dados (MySQL primário / SQLite fallback) + seed
    ├── session.py         # sessão do usuário autenticado
    └── screens/
        ├── _base.py       # TelaAutenticada (sidebar + área de conteúdo)
        ├── login.py       # RF01 — autenticação
        ├── register.py    # cadastro de usuário
        ├── home.py        # tela inicial
        ├── options.py     # RF06 — seleção de nível
        ├── game.py        # RF02–RF05 — partida + pontuação
        ├── profile.py     # visualizar / editar perfil
        ├── help.py        # ajuda + regras
        ├── about.py       # sobre o projeto
        └── report.py      # RF07 — relatórios (professor)
```

## Banco de dados

Backend **primário: MySQL**. O **SQLite é a segunda opção** (fallback
automático, zero-instalação). A seleção é feita pela variável de ambiente
`TANAMESA_DB`:

| `TANAMESA_DB`  | Comportamento |
|----------------|---------------|
| `mysql` (padrão) | Tenta MySQL; se indisponível, cai para SQLite |
| `sqlite`         | Força o arquivo local `src/tanamesa.db` |
| `mysql-strict`   | Exige MySQL e falha com erro claro se não conectar |

Conexão MySQL por variáveis de ambiente (com defaults de desenvolvimento
que já casam com o `docker-compose.yml`):

| Variável | Default |
|----------|---------|
| `MYSQL_HOST` | `localhost` |
| `MYSQL_PORT` | `3306` |
| `MYSQL_USER` | `root` |
| `MYSQL_PASSWORD` | *(vazio)* |
| `MYSQL_DATABASE` | `tanamesa` |

Comandos úteis do container:

```bash
docker compose up -d     # subir
docker compose ps        # status
docker compose down      # parar (mantém os dados)
docker compose down -v   # zerar o banco (demo limpa)
```

O app cria a database e as tabelas sozinho (não é preciso importar o
`sql/schema_mysql.sql` à mão — ele fica como documentação/import opcional).

## Usuários de teste

Crie um cadastro pela tela de cadastro:

- **Aluno**: joga partidas e vê o próprio perfil.
- **Professor**: ganha o item "Relatórios" na barra lateral, com a lista
  de partidas encerradas de todos os alunos.

A senha tem no mínimo 8 caracteres.

## Mecânica do dominó

Cada metade de peça exibe uma representação de uma substância e guarda,
internamente, a sua **função inorgânica**. Duas metades **encaixam quando
pertencem à mesma função** — então o aluno joga *classificando* (ex.: `HCl`
conecta em `pH < 7` porque ambos são **ácidos**). A peça é girada
automaticamente para encaixar.

As representações ficam mais abstratas conforme o nível:

- **Fácil** — fórmula ↔ classificação (mostra o nome da função como dica)
- **Médio** — fórmula ↔ nome (exige nomenclatura)
- **Difícil** — mistura fórmula, nome e propriedades (`pH < 7`,
  `Libera OH- em água`, `Composto iônico`, `Anidrido`…)

Cada nível é um conjunto de dominó completo e balanceado (20 peças, com
todas as funções bem distribuídas), garantindo partidas fluidas.

## Pontuação

| Evento | Pontos |
|--------|-------:|
| Acerto | +10 |
| Erro | −2 |
| Esvaziar a mão (vitória) | +50 bônus |

Pontuação, acertos, erros e tempo são persistidos em `partida` ao final.
Cada tentativa de encaixe é registrada em `jogada` para uso pedagógico.

## Mapeamento Requisitos → Implementação

| Requisito | Onde está |
|-----------|-----------|
| RF01 — autenticação                 | `src/screens/login.py` + `database.autenticar` |
| RF02 — peças conectam por função    | `src/screens/game.py` → `_encaixar` |
| RF03 — feedback imediato            | `src/screens/game.py` → `_aviso` |
| RF04 — pontuação                    | `src/screens/game.py` (`PONTOS_ACERTO`/`PONTOS_ERRO`) |
| RF05 — tempo por partida            | `src/screens/game.py` → `_cronometrar` |
| RF06 — níveis progressivos          | `src/screens/options.py` + tabela `nivel` |
| RF07 — relatórios                   | `src/screens/report.py` + `database.gerar_relatorio` |
| RNF01 — desktop                     | Tkinter (multiplataforma) |
| RNF02 — proteção de dados           | Senha SHA-256 (`database.hash_senha`) |
| RNF04 — interface simples           | Layout do protótipo replicado |
| RNF05 — armazenar desempenho        | Tabelas `partida` / `jogada` |
