#!/bin/bash

# Script de inicialização para EC2 Amazon Linux 2
# Este script será executado automaticamente quando a instância for iniciada

# Log de todas as operações
exec > >(tee /var/log/user-data.log)
exec 2>&1

echo "🚀 Iniciando configuração do Arca Bot na EC2..."

# Atualizar sistema
echo "📦 Atualizando sistema..."
yum update -y

# Instalar Docker
echo "🐳 Instalando Docker..."
yum install -y docker git
systemctl start docker
systemctl enable docker
usermod -a -G docker ec2-user

# Instalar Docker Compose
echo "🔧 Instalando Docker Compose..."
curl -L "https://github.com/docker/compose/releases/download/v2.20.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose

# Clonar repositório
echo "📥 Clonando repositório..."
cd /home/ec2-user
git clone https://github.com/SrGoes/arca-bot.git
cd arca-bot
chown -R ec2-user:ec2-user /home/ec2-user/arca-bot

# Criar arquivo .env (VOCÊ DEVE SUBSTITUIR SEU_BOT_TOKEN_AQUI)
echo "⚙️ Configurando variáveis de ambiente..."
cat > .env << 'EOF'
BOT_TOKEN=SEU_BOT_TOKEN_AQUI
NODE_OPTIONS=
LOG_LEVEL=3
VOICE_DEBUG=false
WEBHOOK_LOGS_URL=
EOF

# Iniciar o bot usando Docker Compose
echo "🚀 Iniciando Arca Bot..."
su - ec2-user -c "cd /home/ec2-user/arca-bot && docker-compose up -d"

# Configurar auto-start no boot
echo "🔄 Configurando auto-start..."
cat > /etc/systemd/system/arca-bot.service << 'EOF'
[Unit]
Description=Arca Bot Discord
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/home/ec2-user/arca-bot
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
TimeoutStartSec=0
User=ec2-user
Group=ec2-user

[Install]
WantedBy=multi-user.target
EOF

systemctl enable arca-bot.service

echo "✅ Configuração concluída!"
echo "📝 Próximos passos:"
echo "   1. Edite o arquivo /home/ec2-user/arca-bot/.env com seu BOT_TOKEN real"
echo "   2. Reinicie o serviço: sudo systemctl restart arca-bot"
echo "   3. Verifique os logs: cd /home/ec2-user/arca-bot && docker-compose logs -f"

# Criar script de help para o usuário
cat > /home/ec2-user/arca-bot-help.sh << 'EOF'
#!/bin/bash
echo "🤖 Comandos úteis do Arca Bot:"
echo ""
echo "📊 Ver status:     docker-compose ps"
echo "📝 Ver logs:       docker-compose logs -f"
echo "🔄 Reiniciar:      docker-compose restart"
echo "🛑 Parar:          docker-compose down"
echo "🚀 Iniciar:        docker-compose up -d"
echo "🔧 Editar config:  nano .env"
echo "📡 Atualizar bot:  git pull && docker-compose up -d --build"
echo ""
echo "📍 Localização: /home/ec2-user/arca-bot"
EOF

chmod +x /home/ec2-user/arca-bot-help.sh
chown ec2-user:ec2-user /home/ec2-user/arca-bot-help.sh

echo "🎉 Setup completo! Execute '/home/ec2-user/arca-bot-help.sh' para ver comandos úteis."
