# Dockerfile para desenvolvimento
FROM docker.io/library/node:20-alpine

WORKDIR /app

# Instalar dependências do sistema
RUN apk add --no-cache git python3 make g++

# Copiar arquivos de dependências
COPY package*.json ./
RUN npm ci --only=production

# Copiar código fonte
COPY . .

# Compilar TypeScript
RUN npm run build

# Copiar e configurar script de inicialização
COPY docker-entrypoint.sh /app/
RUN chmod +x /app/docker-entrypoint.sh

# Criar diretório de dados com permissões corretas
RUN mkdir -p data/backups logs && \
    chown -R node:node /app

# Usar usuário não-root
USER node

# Comando para iniciar o bot
ENTRYPOINT ["/app/docker-entrypoint.sh"]
