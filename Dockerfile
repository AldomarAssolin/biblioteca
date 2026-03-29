FROM python:3.11-slim

# Impede o Python de gerar arquivos pyc
ENV PYTHONDONTWRITEBYTECODE 1
# Impede o Python de reter logs na memória (imprime no console do docker)
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Instalar dependencias otimizadas primeiro
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo o codigo fonte inclusive a pasta dist/
COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
