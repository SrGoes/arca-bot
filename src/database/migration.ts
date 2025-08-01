import { readFileSync, writeFileSync, existsSync, mkdirSync } from "fs";
import { join } from "path";
import { logger } from "#settings";

interface OldUserData {
    created_at: string;
    updated_at: string;
    user_id: number;
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

            // Carregar dados antigos
            const oldDataRaw = readFileSync(this.oldDataPath, "utf8");
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

            // Migrar cada usuário
            for (const [, oldUser] of Object.entries(oldData.user)) {
                const userIdString = String(oldUser.user_id);

                // Verificar se o usuário já existe
                const userExists = currentData[userIdString];
                
                if (userExists) {
                    // Atualizar dados existentes apenas se os dados antigos forem mais recentes ou maiores
                    const shouldUpdate = this.shouldUpdateExistingUser(userExists, oldUser);
                    
                    if (shouldUpdate) {
                        currentData[userIdString] = this.convertUserData(oldUser);
                        updatedCount++;
                        logger.log(`🔄 Atualizado usuário: ${userIdString}`);
                    } else {
                        skippedCount++;
                        logger.log(`⏭️ Mantido dados existentes para usuário: ${userIdString}`);
                    }
                } else {
                    // Novo usuário
                    currentData[userIdString] = this.convertUserData(oldUser);
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
     * Converte dados do formato antigo para o novo
     */
    private convertUserData(oldUser: OldUserData): NewUserEconomy {
        return {
            userId: String(oldUser.user_id),
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
        // Atualizar se os dados antigos têm mais moedas ou estatísticas maiores
        return (
            oldUser.balance > existingUser.balance ||
            oldUser.total_earned > existingUser.totalEarned ||
            oldUser.message_count > existingUser.messageCount
        );
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
