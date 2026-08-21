# BibleLingo — runbook de produção

## Configuração obrigatória

Defina as variáveis antes de iniciar a API:

```bash
export BIBLELINGO_ENV=production
export BIBLELINGO_SECRET_KEY="gere-um-segredo-aleatorio-com-pelo-menos-32-caracteres"
export BIBLELINGO_TOKEN_HOURS=72
export BIBLELINGO_CORS_ORIGINS="https://app.exemplo.com"
export BIBLELINGO_DB_PATH="/var/lib/biblelingo/biblelingo.db"
```

`BIBLELINGO_SECRET_KEY` deve ser aleatória, privada e ter pelo menos 32 caracteres. Nunca use o segredo de desenvolvimento em produção. `BIBLELINGO_CORS_ORIGINS` deve listar somente origens confiáveis e não pode conter `*` quando credenciais estão habilitadas.

A API falha rapidamente no startup se o segredo, o prazo do token ou o CORS forem inválidos. O endpoint `/health` verifica apenas liveness. O endpoint `/health/ready` verifica a configuração e uma conexão funcional com o SQLite.

## Inicialização

```bash
uvicorn api.main:app --host 127.0.0.1 --port 8000
curl --fail http://127.0.0.1:8000/health
curl --fail http://127.0.0.1:8000/health/ready
```

Use HTTPS no proxy reverso. Não exponha o banco SQLite, arquivos de backup, tokens ou variáveis de ambiente por meio do servidor web.

## Backup

O mecanismo usa o backup online do SQLite e é compatível com WAL. Grave os snapshots fora do repositório e proteja-os com permissões de proprietário:

```bash
mkdir -p /var/backups/biblelingo
python scripts/backup_db.py \
  --database /var/lib/biblelingo/biblelingo.db \
  --output /var/backups/biblelingo/biblelingo-$(date -u +%Y%m%dT%H%M%SZ).sqlite
chmod 600 /var/backups/biblelingo/*.sqlite
```

Mantenha cópias rotacionadas, pelo menos uma cópia fora do host e uma política de retenção documentada. Não armazene backups no Git.

## Restauração

Pare a API antes de restaurar para impedir gravações concorrentes. O comando verifica `PRAGMA integrity_check` e troca o destino atomicamente:

```bash
systemctl stop biblelingo
python scripts/restore_db.py \
  /var/backups/biblelingo/snapshot.sqlite \
  --database /var/lib/biblelingo/biblelingo.db
systemctl start biblelingo
curl --fail http://127.0.0.1:8000/health/ready
```

Faça periodicamente uma restauração em ambiente separado. Os testes `tests/test_production.py` cobrem integridade, permissões e preservação de dados no round-trip.

## Verificações antes do deploy

```bash
python -m compileall app api tests main.py
python -m unittest discover -s tests -v
cd frontend && npm ci && npm run build
```

Nunca registre `BIBLELINGO_SECRET_KEY`, senhas ou tokens nos logs, tickets, artefatos de CI ou no repositório.
