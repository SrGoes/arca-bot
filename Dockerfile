# Seguindo a documentação oficial da base Constatic
FROM docker.io/library/node:20

WORKDIR /bot

# Copiar arquivos de dependências
COPY ./package*.json .
RUN npm install

# Copiar código fonte
COPY . .

# Compilar TypeScript
RUN npm run build

# Criar diretório de dados
RUN mkdir -p data/backups

# Comando para iniciar o bot
CMD [ "npm", "start" ]
