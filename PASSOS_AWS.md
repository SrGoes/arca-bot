# 🚀 Guia Completo: Deploy do Arca Bot na AWS

## 📋 Pré-requisitos
- Conta AWS ativa
- AWS CLI configurado
- Docker instalado localmente
- Token do bot Discord

## 🎯 **Opção 1: AWS ECS Fargate (RECOMENDADO)**

### Passo 1: Criar repositório ECR
```bash
# Criar repositório para a imagem Docker
aws ecr create-repository --repository-name arca-bot --region us-east-1

# Obter URL do repositório (anote este valor)
aws ecr describe-repositories --repository-names arca-bot --region us-east-1
```

### Passo 2: Build e Push da imagem
```bash
# Na pasta do projeto
docker build -t arca-bot .

# Login no ECR (substitua ACCOUNT_ID)
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

# Tag da imagem
docker tag arca-bot:latest ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/arca-bot:latest

# Push da imagem
docker push ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/arca-bot:latest
```

### Passo 3: Criar Secrets no AWS Secrets Manager
```bash
# Criar secret para o BOT_TOKEN
aws secretsmanager create-secret \
    --name "arca-bot/discord-token" \
    --description "Token do Discord Bot" \
    --secret-string "SEU_BOT_TOKEN_AQUI" \
    --region us-east-1

# (Opcional) Criar secret para webhook
aws secretsmanager create-secret \
    --name "arca-bot/webhook-url" \
    --description "URL do Webhook para logs" \
    --secret-string "SUA_WEBHOOK_URL_AQUI" \
    --region us-east-1
```

### Passo 4: Criar EFS (para persistência de dados)
```bash
# Criar file system
aws efs create-file-system \
    --performance-mode generalPurpose \
    --throughput-mode provisioned \
    --provisioned-throughput-in-mibps 1 \
    --tags Key=Name,Value=arca-bot-data \
    --region us-east-1

# Anotar o FileSystemId retornado
```

### Passo 5: Configurar EFS Mount Target
```bash
# Obter subnet padrão da VPC
aws ec2 describe-subnets --filters "Name=default-for-az,Values=true" --region us-east-1

# Criar mount target (substitua SUBNET_ID e FILESYSTEM_ID)
aws efs create-mount-target \
    --file-system-id FILESYSTEM_ID \
    --subnet-id SUBNET_ID \
    --security-groups sg-xxxxxxxx \
    --region us-east-1
```

### Passo 6: Criar Cluster ECS
```bash
# Criar cluster
aws ecs create-cluster \
    --cluster-name arca-bot-cluster \
    --capacity-providers FARGATE \
    --default-capacity-provider-strategy capacityProvider=FARGATE,weight=1 \
    --region us-east-1
```

### Passo 7: Registrar Task Definition
```bash
# Editar o arquivo ecs-task-definition.json com seus dados:
# - ACCOUNT_ID: seu ID da conta AWS
# - REGION: sua região (us-east-1)
# - fs-XXXXXXXX: ID do seu EFS

# Registrar task definition
aws ecs register-task-definition \
    --cli-input-json file://ecs-task-definition.json \
    --region us-east-1
```

### Passo 8: Criar Service ECS
```bash
# Criar serviço (substitua os valores)
aws ecs create-service \
    --cluster arca-bot-cluster \
    --service-name arca-bot-service \
    --task-definition arca-bot:1 \
    --desired-count 1 \
    --launch-type FARGATE \
    --network-configuration "awsvpcConfiguration={subnets=[SUBNET_ID],securityGroups=[SECURITY_GROUP_ID],assignPublicIp=ENABLED}" \
    --region us-east-1
```

### Passo 9: Verificar deployment
```bash
# Verificar status do serviço
aws ecs describe-services \
    --cluster arca-bot-cluster \
    --services arca-bot-service \
    --region us-east-1

# Ver logs (substitua TASK_ARN)
aws logs get-log-events \
    --log-group-name /ecs/arca-bot \
    --log-stream-name ecs/arca-bot/TASK_ARN \
    --region us-east-1
```

## 🎯 **Opção 2: AWS App Runner (MAIS SIMPLES)**

### Passo 1: Preparar repositório GitHub
1. Faça push do código para seu repositório GitHub
2. Certifique-se que o arquivo `apprunner.yaml` está na raiz

### Passo 2: Criar serviço App Runner
```bash
# Criar arquivo de configuração
cat > apprunner-service.json << 'EOF'
{
  "ServiceName": "arca-bot",
  "SourceConfiguration": {
    "Repository": {
      "RepositoryUrl": "https://github.com/SrGoes/arca-bot",
      "SourceCodeVersion": {
        "Type": "BRANCH",
        "Value": "main"
      },
      "ConfigurationSource": "REPOSITORY"
    },
    "AutoDeploymentsEnabled": true
  },
  "InstanceConfiguration": {
    "Cpu": "0.25 vCPU",
    "Memory": "0.5 GB",
    "EnvironmentVariables": {
      "LOG_LEVEL": "3",
      "VOICE_DEBUG": "false",
      "NODE_ENV": "production"
    }
  }
}
EOF

# Criar serviço
aws apprunner create-service --cli-input-json file://apprunner-service.json --region us-east-1
```

### Passo 3: Adicionar secrets
```bash
# Primeiro, crie o secret no Secrets Manager
aws secretsmanager create-secret \
    --name "apprunner/arca-bot/bot-token" \
    --secret-string "SEU_BOT_TOKEN_AQUI" \
    --region us-east-1

# Depois atualize o serviço para usar o secret
# (Isso requer edição via Console AWS - mais fácil)
```

## 🎯 **Opção 3: EC2 simples (MAIS BARATO)**

### Passo 1: Lançar instância EC2
```bash
# Lançar EC2 t3.micro (free tier)
aws ec2 run-instances \
    --image-id ami-0abcdef1234567890 \
    --count 1 \
    --instance-type t3.micro \
    --key-name sua-chave \
    --security-groups default \
    --user-data file://user-data.sh \
    --region us-east-1
```

### Passo 2: Script de inicialização (user-data.sh)
```bash
#!/bin/bash
yum update -y
yum install -y docker git
service docker start
usermod -a -G docker ec2-user

# Instalar Docker Compose
curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Clonar repositório
git clone https://github.com/SrGoes/arca-bot.git /home/ec2-user/arca-bot
cd /home/ec2-user/arca-bot

# Criar .env
echo "BOT_TOKEN=SEU_TOKEN_AQUI" > .env
echo "LOG_LEVEL=3" >> .env
echo "VOICE_DEBUG=false" >> .env

# Iniciar bot
docker-compose up -d
```

### Passo 3: Conectar e verificar
```bash
# Conectar via SSH
ssh -i "sua-chave.pem" ec2-user@IP_DA_INSTANCIA

# Verificar logs
cd arca-bot
docker-compose logs -f
```

## 📊 **Monitoramento e Logs**

### CloudWatch Logs
```bash
# Criar log group
aws logs create-log-group --log-group-name /aws/ecs/arca-bot --region us-east-1

# Ver logs em tempo real
aws logs tail /aws/ecs/arca-bot --follow --region us-east-1
```

### Alarmes CloudWatch
```bash
# Criar alarme para CPU alta
aws cloudwatch put-metric-alarm \
    --alarm-name "ArcaBot-HighCPU" \
    --alarm-description "Alarme quando CPU > 80%" \
    --metric-name CPUUtilization \
    --namespace AWS/ECS \
    --statistic Average \
    --period 300 \
    --threshold 80 \
    --comparison-operator GreaterThanThreshold \
    --evaluation-periods 2 \
    --region us-east-1
```

## 💰 **Estimativa de Custos**

### ECS Fargate:
- vCPU: 0.25 = ~$7.30/mês
- Memória: 0.5GB = ~$0.80/mês  
- **Total: ~$8-10/mês**

### App Runner:
- 0.25 vCPU + 0.5GB = ~$12-15/mês
- **Total: ~$12-15/mês**

### EC2 t3.micro:
- Instância: $8.50/mês
- **Total: ~$8.50/mês**

## 🔧 **Comandos Úteis**

```bash
# Parar serviço ECS
aws ecs update-service --cluster arca-bot-cluster --service arca-bot-service --desired-count 0

# Reiniciar serviço
aws ecs update-service --cluster arca-bot-cluster --service arca-bot-service --desired-count 1

# Atualizar imagem
docker build -t arca-bot .
docker tag arca-bot:latest ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/arca-bot:latest
docker push ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/arca-bot:latest
aws ecs update-service --cluster arca-bot-cluster --service arca-bot-service --force-new-deployment

# Ver status
aws ecs describe-services --cluster arca-bot-cluster --services arca-bot-service
```

## ⚠️ **Pontos Importantes**

1. **Substitua todos os valores de exemplo** (ACCOUNT_ID, SUBNET_ID, etc.)
2. **Configure Security Groups** para permitir tráfego necessário
3. **Use Secrets Manager** para dados sensíveis (nunca hardcode tokens)
4. **Configure backups** dos dados do EFS
5. **Monitore custos** regularly

**Recomendação**: Comece com **ECS Fargate** para produção ou **EC2** para economia máxima.
