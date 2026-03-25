[README.md](https://github.com/user-attachments/files/26255925/README.md)
# Trilha de Carreira

Projeto em Python para gerar imagens da trilha de carreira por filial.

## Estrutura

- `trilha_carreira_graphviz.py`: gera os arquivos `.dot` e `.png`
- `trilha_layout.py`: configuracoes visuais do layout
- `trilha_dados.py`: base de fallback em Python
- `gerar_modelo_excel_trilha.py`: gera um arquivo Excel com abas de apoio
- `data/filiais_trilha.csv`: lista de filiais
- `data/trilha_cargos.csv`: cargos, grupos e cores
- `data/trilha_conexoes.csv`: conexoes entre cargos
- `data/trilha_modelo.xlsx`: modelo Excel com abas `filiais`, `cargos` e `conexoes`
- `Resultados/trilhas_carreira/`: saida dos arquivos gerados

## Como editar

### Filiais

Edite o arquivo `data/filiais_trilha.csv`.

Exemplo:

```csv
filial
Oliveira
Itatiba/71
Itatiba/72
```

### Cargos e grupos

Edite o arquivo `data/trilha_cargos.csv`.

Colunas:

- `grupo`
- `label_grupo`
- `cor_grupo`
- `cargo`

### Conexoes

Edite o arquivo `data/trilha_conexoes.csv`.

Colunas:

- `origem`
- `destino`

## Como gerar as imagens

No terminal, dentro da pasta do projeto:

```powershell
python trilha_carreira_graphviz.py
```

As imagens serao geradas em `Resultados/trilhas_carreira/`.

## Como gerar o Excel modelo

```powershell
python gerar_modelo_excel_trilha.py
```

O arquivo sera salvo em `data/trilha_modelo.xlsx`.

## Requisitos

- Python instalado
- Graphviz disponivel no computador para gerar `.png`

Se o Graphviz nao estiver disponivel, o script ainda consegue gerar o arquivo `.dot`.
