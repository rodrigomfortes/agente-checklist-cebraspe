# Agente Checklist CEBRASPE

Sistema de banco de dados para gerenciar checklists de materiais administrativos da CEBRASPE.

## Como rodar

1. **Clone o projeto**
```bash
git clone <url-do-repo>
cd agente-checklist-cebraspe
```

2. **Instale as dependências**
```bash
pip install -r requirements.txt
```

3. **Inicializar o banco (só uma vez)**
```bash
python -c "from database import init_database; init_database()"
```
Rodar isso no terminal

4. **Usar o sistema**
```python
from database import ChecklistDatabase
ChecklistDatabase.criar_checklist_dia1("minha_sessao")
```

## Estrutura

- `database/models.py` - Tabelas do banco
- `database/database.py` - Operações (criar, buscar, atualizar)
- `database/__init__.py` - Imports

Pronto! 🚀
