# Quick Start Guide

## Initial Setup

1. **Activate virtual environment**:
   ```bash
   pyenv local brazilian_cds_feeder
   ```

2. **Verify installation**:
   ```bash
   pip list | grep -E "pandas|fastapi|uvicorn"
   ```

3. **Configure environment** (optional):
   ```bash
   cp .env.example .env
   # Edit .env if needed
   ```

## Daily Usage

### Update CDS Data
```bash
python scripts/update_cds.py
```

Expected output:
```
============================================================
Iniciando atualização de dados CDS do Brasil
============================================================
Buscando dados do Investing.com...
✓ Dados capturados: 23 registros
Atualizando armazenamento local...
============================================================
Atualização concluída com sucesso!
Total de registros: 23
Data mais recente: 2025-11-07
Último valor: 146.0900
============================================================
```

### Start API Server
```bash
python scripts/start_api.py
```

Access:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Test API Endpoints

**Health Check**:
```bash
curl http://localhost:8000/health
```

**Get Latest Data**:
```bash
curl http://localhost:8000/cds/latest?n=5
```

**Get Statistics**:
```bash
curl http://localhost:8000/cds/stats
```

**Get Filtered Data**:
```bash
curl "http://localhost:8000/cds/?start_date=2025-10-01&limit=20"
```

## File Locations

- **CSV Data**: `data/brasil_CDS_historical.csv`
- **Logs**: Console output (configure BetterStack for remote logging)
- **Backups**: `data/brasil_CDS_historical__bkp_*.csv`

## Common Commands

### Update Data + Start API (Recommended Workflow)
```bash
# Update data first
python scripts/update_cds.py

# Then start API
python scripts/start_api.py
```

### Development Mode (Auto-reload)
Edit `.env` and set:
```
API_RELOAD=true
```

Then start API:
```bash
python scripts/start_api.py
```

## Troubleshooting

### "No module named 'src'"
Solution: Run from project root directory

### "CSV file not found"
Solution: Run `python scripts/update_cds.py` first

### "Connection timeout"
Solution: Check internet connection or increase timeout in `.env`:
```
REQUEST_TIMEOUT=30
```

## Project Status

✅ Data scraping working
✅ CSV storage working  
✅ API functional
✅ Logging configured
✅ Documentation complete

## Next Actions

1. Schedule automatic updates (cron job)
2. Add unit tests
3. Deploy to production
4. Add monitoring
