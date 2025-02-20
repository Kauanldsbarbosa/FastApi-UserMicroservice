# Etapa de build
FROM python:3.12-alpine3.19 AS build

# Instalar dependências do sistema
RUN apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    libpq-dev \
    build-base

# Definir o diretório de trabalho
WORKDIR /app

# Atualizar pip e instalar dependências
RUN pip install --upgrade pip setuptools wheel

# Copiar e instalar dependências
COPY ./contrib/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Etapa final (reduz o tamanho da imagem)
FROM python:3.12-alpine3.19

# Criar usuário não-root
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

# Copiar apenas as dependências instaladas da etapa de build
COPY --from=build /usr/local /usr/local

# Definir o diretório de trabalho e usuário
WORKDIR /app
USER appuser

# Copiar a aplicação
COPY . .

# Entrypoint ou comando (se necessário)
# CMD ["python", "app.py"]
