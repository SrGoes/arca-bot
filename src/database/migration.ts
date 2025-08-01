import { readFileSync, writeFileSync, existsSync, mkdirSync } from "fs";
import { join } from "path";
import { logger } from "#settings";

interface OldUserData {
    created_at: string;
    updated_at: string;
    user_id: number | string; // Pode vir como number ou string
    balance: number;
    total_earned: number;
    total_spent: number;
    voice_time_minutes: number;
    message_count: number;
    daily_count: number;
    last_daily: string | null;
    last_message_reward: string | null;
    achievements: string[];
    preferences: Record<string, any>;
    transaction_history: Array<any>;
}

interface OldDataStructure {
    user: Record<string, OldUserData>;
}

interface NewUserEconomy {
    userId: string;
    balance: number;
    lastDaily: string | null;
    totalEarned: number;
    totalSpent: number;
    messageCount: number;
    lastMessageReward: string | null;
}

export class DataMigration {
    private oldDataPath: string;
    private newDataPath: string;
    private backupDir: string;

    constructor(oldDataPath?: string) {
        this.oldDataPath = oldDataPath || join(process.cwd(), "migration", "user_data.json");
        this.newDataPath = join(process.cwd(), "data", "economy.json");
        this.backupDir = join(process.cwd(), "data", "backup");
        
        // Criar diretório de backup se não existir
        if (!existsSync(this.backupDir)) {
            mkdirSync(this.backupDir, { recursive: true });
        }
    }

    /**
     * Migra dados da versão anterior para a nova estrutura
     */
    async migrateData(): Promise<void> {
        try {
            logger.log("🔄 Iniciando migração de dados...");

            // Verificar se o arquivo de dados antigos existe
            if (!existsSync(this.oldDataPath)) {
                logger.error(`❌ Arquivo de dados antigos não encontrado: ${this.oldDataPath}`);
                return;
            }

            // Carregar dados antigos como string primeiro para extrair IDs corretos
            const oldDataRaw = readFileSync(this.oldDataPath, "utf8");
            
            // Extrair IDs corretamente do JSON usando regex
            const correctIds = this.extractUserIdsFromJson(oldDataRaw);
            logger.log(`🔍 IDs extraídos do JSON: ${correctIds.join(', ')}`);
            
            const oldData: OldDataStructure = JSON.parse(oldDataRaw);

            // Carregar dados atuais (se existir)
            let currentData: Record<string, NewUserEconomy> = {};
            if (existsSync(this.newDataPath)) {
                const currentDataRaw = readFileSync(this.newDataPath, "utf8");
                currentData = JSON.parse(currentDataRaw);
                logger.log(`📊 Encontrados ${Object.keys(currentData).length} usuários existentes`);
            }

            let migratedCount = 0;
            let skippedCount = 0;
            let updatedCount = 0;
            let idIndex = 0;

            // Migrar cada usuário
            for (const [, oldUser] of Object.entries(oldData.user)) {
                // Usar o ID correto extraído do JSON
                const userIdString = correctIds[idIndex++] || String(oldUser.user_id);
                
                // Debug logs
                logger.log(`🔍 Processando usuário: ${userIdString}`);
                logger.log(`📄 Dados originais - user_id: ${oldUser.user_id} (tipo: ${typeof oldUser.user_id})`);
                logger.log(`📄 ID correto extraído: ${userIdString}`);

                // Verificar se o usuário já existe
                const userExists = currentData[userIdString];
                logger.log(`🔎 Usuário existe no sistema atual? ${userExists ? 'SIM' : 'NÃO'}`);
                
                if (userExists) {
                    logger.log(`📊 Dados atuais - balance: ${userExists.balance}, totalEarned: ${userExists.totalEarned}`);
                    logger.log(`📊 Dados migração - balance: ${oldUser.balance}, totalEarned: ${oldUser.total_earned}`);
                    
                    // Atualizar dados existentes apenas se os dados antigos forem mais recentes ou maiores
                    const shouldUpdate = this.shouldUpdateExistingUser(userExists, oldUser);
                    
                    if (shouldUpdate) {
                        currentData[userIdString] = this.convertUserData(oldUser, userIdString);
                        updatedCount++;
                        logger.log(`🔄 Atualizado usuário: ${userIdString}`);
                    } else {
                        skippedCount++;
                        logger.log(`⏭️ Mantido dados existentes para usuário: ${userIdString}`);
                    }
                } else {
                    // Novo usuário
                    currentData[userIdString] = this.convertUserData(oldUser, userIdString);
                    migratedCount++;
                    logger.log(`✅ Migrado novo usuário: ${userIdString}`);
                }
            }

            // Salvar dados migrados
            writeFileSync(this.newDataPath, JSON.stringify(currentData, null, 2));

            logger.success(`✅ Migração concluída!`);
            logger.success(`📊 Estatísticas:`);
            logger.success(`   - Novos usuários migrados: ${migratedCount}`);
            logger.success(`   - Usuários atualizados: ${updatedCount}`);
            logger.success(`   - Usuários mantidos: ${skippedCount}`);
            logger.success(`   - Total de usuários: ${Object.keys(currentData).length}`);

        } catch (error) {
            logger.error("❌ Erro durante a migração:", error);
            throw error;
        }
    }

    /**
     * Extrai IDs de usuário corretamente do JSON bruto usando regex
     */
    private extractUserIdsFromJson(jsonString: string): string[] {
        const userIdRegex = /"user_id":\s*(\d+)/g;
        const ids: string[] = [];
        let match;
        
        while ((match = userIdRegex.exec(jsonString)) !== null) {
            ids.push(match[1]);
        }
        
        return ids;
    }

    /**
     * Remove IDs corrompidos (como 306978576929128450) mantendo apenas os corretos
     */
    async cleanCorruptedIds(): Promise<void> {
        try {
            if (!existsSync(this.newDataPath)) {
                logger.log("📄 Nenhum arquivo de economia encontrado para limpar.");
                return;
            }

            const currentDataRaw = readFileSync(this.newDataPath, "utf8");
            const currentData: Record<string, NewUserEconomy> = JSON.parse(currentDataRaw);
            
            // IDs conhecidos corrompidos (terminam em 50 ao invés de 60)
            const corruptedPattern = /(\d+)50$/;
            const cleanedData: Record<string, NewUserEconomy> = {};
            let removedCount = 0;

            for (const [userId, userData] of Object.entries(currentData)) {
                const match = userId.match(corruptedPattern);
                
                if (match) {
                    // ID corrompido - tentar encontrar o correto
                    const basePart = match[1];
                    const possibleCorrectId = basePart + "60";
                    
                    logger.log(`🧹 ID corrompido encontrado: ${userId}`);
                    logger.log(`🔍 Possível ID correto: ${possibleCorrectId}`);
                    
                    // Verificar se já existe o ID correto
                    if (currentData[possibleCorrectId]) {
                        logger.log(`⚠️ ID correto já existe, removendo o corrompido`);
                        removedCount++;
                        continue; // Pular o corrompido
                    } else {
                        // Corrigir o ID
                        userData.userId = possibleCorrectId;
                        cleanedData[possibleCorrectId] = userData;
                        logger.log(`✅ ID corrigido: ${userId} → ${possibleCorrectId}`);
                    }
                } else {
                    // ID não corrompido, manter
                    cleanedData[userId] = userData;
                }
            }

            // Salvar dados limpos
            writeFileSync(this.newDataPath, JSON.stringify(cleanedData, null, 2));
            
            logger.success(`🧹 Limpeza concluída!`);
            logger.success(`   - IDs corrompidos removidos: ${removedCount}`);
            logger.success(`   - Total de usuários: ${Object.keys(cleanedData).length}`);

        } catch (error) {
            logger.error("❌ Erro durante a limpeza:", error);
            throw error;
        }
    }

    /**
     * Converte dados do formato antigo para o novo
     */
    private convertUserData(oldUser: OldUserData, userIdString: string): NewUserEconomy {
        return {
            userId: userIdString,
            balance: oldUser.balance || 0,
            lastDaily: oldUser.last_daily,
            totalEarned: oldUser.total_earned || 0,
            totalSpent: oldUser.total_spent || 0,
            messageCount: oldUser.message_count || 0,
            lastMessageReward: oldUser.last_message_reward
        };
    }

    /**
     * Determina se deve atualizar um usuário existente
     */
    private shouldUpdateExistingUser(existingUser: NewUserEconomy, oldUser: OldUserData): boolean {
        const balanceCondition = oldUser.balance > existingUser.balance;
        const earnedCondition = oldUser.total_earned > existingUser.totalEarned;
        const messageCondition = oldUser.message_count > existingUser.messageCount;
        
        logger.log(`🔍 Verificação de update:`);
        logger.log(`   Balance: ${oldUser.balance} > ${existingUser.balance} = ${balanceCondition}`);
        logger.log(`   Earned: ${oldUser.total_earned} > ${existingUser.totalEarned} = ${earnedCondition}`);
        logger.log(`   Messages: ${oldUser.message_count} > ${existingUser.messageCount} = ${messageCondition}`);
        
        const shouldUpdate = balanceCondition || earnedCondition || messageCondition;
        logger.log(`   Resultado: ${shouldUpdate ? 'ATUALIZAR' : 'MANTER'}`);
        
        return shouldUpdate;
    }

    /**
     * Cria um backup dos dados atuais antes da migração
     */
    async createBackup(): Promise<void> {
        if (existsSync(this.newDataPath)) {
            const backupPath = join(this.backupDir, `economy.backup.${Date.now()}.json`);
            const currentData = readFileSync(this.newDataPath, "utf8");
            writeFileSync(backupPath, currentData);
            logger.success(`💾 Backup criado: ${backupPath}`);
        }
    }

    /**
     * Migração completa com backup
     */
    async fullMigration(oldDataPath?: string): Promise<void> {
        if (oldDataPath) {
            this.oldDataPath = oldDataPath;
        }

        try {
            // Criar backup
            await this.createBackup();
            
            // Executar migração
            await this.migrateData();
            
            logger.success("🎉 Migração completa realizada com sucesso!");
            
        } catch (error) {
            logger.error("❌ Falha na migração completa:", error);
            throw error;
        }
    }

    /**
     * Define o caminho do arquivo de dados antigos
     */
    setOldDataPath(path: string): void {
        this.oldDataPath = path;
    }

    /**
     * Exibe estatísticas dos dados antigos sem migrar
     */
    async analyzeOldData(filePath?: string): Promise<void> {
        const dataPath = filePath || this.oldDataPath;
        
        if (!existsSync(dataPath)) {
            logger.error(`❌ Arquivo não encontrado: ${dataPath}`);
            return;
        }

        try {
            const oldDataRaw = readFileSync(dataPath, "utf8");
            const oldData: OldDataStructure = JSON.parse(oldDataRaw);
            
            const users = Object.values(oldData.user);
            const totalUsers = users.length;
            const totalBalance = users.reduce((sum, user) => sum + (user.balance || 0), 0);
            const totalEarned = users.reduce((sum, user) => sum + (user.total_earned || 0), 0);
            const usersWithDaily = users.filter(user => user.last_daily).length;
            
            logger.log("📊 Análise dos dados antigos:");
            logger.log(`   - Total de usuários: ${totalUsers}`);
            logger.log(`   - Saldo total: ${totalBalance.toLocaleString()} moedas`);
            logger.log(`   - Total ganho histórico: ${totalEarned.toLocaleString()} moedas`);
            logger.log(`   - Usuários com daily: ${usersWithDaily}`);
            logger.log(`   - Média de saldo: ${Math.round(totalBalance / totalUsers).toLocaleString()} moedas`);
            
        } catch (error) {
            logger.error("❌ Erro ao analisar dados antigos:", error);
        }
    }
}

// Instância global para uso
export const dataMigration = new DataMigration();
