# TáNaMesa — Dominó Digital de Funções Inorgânicas

Gamificação acadêmica do curso de Ciência da Computação do Instituto Mauá
de Tecnologia, em parceria com a Etec Júlio de Mesquita, para apoio ao
aprendizado das funções inorgânicas no Ensino Médio.

## Como executar

Requer Python 3.10+ com `tkinter` (já incluso na maioria das distribuições).

```bash
cd TaNaMesa
python main.py
```

O banco de dados SQLite (`tanamesa.db`) é criado automaticamente na
primeira execução, junto com as peças do dominó dos três níveis.

## Estrutura

```
TaNaMesa/
├── main.py            # Entry point + roteador de telas
├── constants.py       # Paleta visual (Figma)
├── widgets.py         # Componentes reutilizáveis (topbar, sidebar, card…)
├── database.py        # Acesso ao SQLite + seed das peças
├── session.py         # Sessão do usuário autenticado
├── schema_mysql.sql   # Schema MySQL equivalente (documentação)
├── tanamesa.db        # SQLite (auto-criado)
└── screens/
    ├── login.py       # RF01 — autenticação
    ├── register.py    # Caso de uso "Realizar cadastro"
    ├── home.py        # Tela inicial
    ├── options.py     # RF06 — seleção de nível
    ├── game.py        # RF02–RF05 — partida + scoring
    ├── profile.py     # Visualizar / editar perfil
    ├── help.py        # Ajuda + regras do jogo
    ├── about.py       # Sobre o projeto
    └── report.py      # RF07 — relatórios (professor)
```

## Banco de dados

Por padrão a aplicação usa **SQLite** (zero-instalação). Para subir em
**MySQL** conforme previsto na documentação:

```bash
mysql -u root -p < schema_mysql.sql
pip install mysql-connector-python
```

E então substituir as chamadas em `database.py` pelo conector MySQL —
o restante do código depende apenas das funções públicas
(`autenticar`, `criar_usuario`, `carregar_pecas`, etc.), então a
migração se resume a trocar o adapter de conexão.

## Usuários de teste

Crie um cadastro pela tela de cadastro:

- **Aluno**: tipo "aluno" → joga partidas, vê próprio perfil.
- **Professor**: tipo "professor" → vê item adicional "Relatórios" na
  sidebar, com a lista de partidas encerradas de todos os alunos.

A senha tem exatamente 8 dígitos (regra de negócio RF/Cadastro).

## Mecânica do dominó

Cada peça tem dois lados, podendo conter:

- **fórmula** (HCl, NaOH, H2SO4…)
- **nome** (Ácido Clorídrico, Hidróxido de Sódio…)
- **classificação** (Ácido, Base, Sal, Óxido)
- **propriedade** (Libera H+ em água, pH < 7…)

Duas peças encaixam quando o valor exposto em uma extremidade do
tabuleiro é igual a um dos lados da peça da mão. O encaixe é
automaticamente orientado.

- **Nível fácil**: associação fórmula ↔ classificação
- **Nível médio**: associação fórmula ↔ nome
- **Nível difícil**: mistura nomes, fórmulas, propriedades e classificações

## Pontuação

| Evento  | Pontos |
|---------|-------:|
| Acerto  | +10    |
| Erro    | −2     |

Pontuação, acertos, erros e tempo são persistidos em `partida` ao final.
Cada tentativa de encaixe é registrada em `jogada` para uso pedagógico.

## Mapeamento Requisitos → Implementação

| Requisito | Onde está |
|-----------|-----------|
| RF01 — autenticação simples            | `screens/login.py` + `database.autenticar` |
| RF02 — peças conectam por correspondência | `screens/game.py` → `_encaixar` |
| RF03 — feedback imediato                | `screens/game.py` → `_flash` |
| RF04 — pontuação                        | `screens/game.py` (PONTOS_ACERTO/ERRO) |
| RF05 — tempo por partida                | `screens/game.py` → `_tick` |
| RF06 — níveis progressivos              | `screens/options.py` + tabela `nivel` |
| RF07 — relatórios                       | `screens/report.py` + `database.gerar_relatorio` |
| RNF01 — desktop                          | Tkinter (cross-platform) |
| RNF02 — proteção de dados                | Senha SHA-256 (`database.hash_senha`) |
| RNF04 — interface simples                | Layout do Figma replicado |
| RNF05 — armazenar desempenho             | Tabelas `partida` / `jogada` |
```
