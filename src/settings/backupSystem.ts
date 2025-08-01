import { writeFileSync, readFileSync, existsSync, mkdirSync, readdirSync, statSync, unlinkSync } from "fs";
import { join } from "path";
import { logger } from "./logger.js";

export interface BackupInfo {
    timestamp: string;
    filename: string;
    size: number;
    type: 'economy' | 'voice' | 'full';
    description?: string;
}

export class BackupSystem {
    private backupDir: string;
    private dataDir: string;

    constructor() {
        this.backupDir = join(process.cwd(), "data", "backups");
        this.dataDir = join(process.cwd(), "data");
        
        // Criar diretório de backup se não existir
        if (!existsSync(this.backupDir)) {
            mkdirSync(this.backupDir, { recursive: true });
        }
    }

    /**
     * Cria backup completo de todos os dados
     */
    async createFullBackup(description?: string): Promise<BackupInfo> {
        try {
            const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
            const filename = `full_backup_${timestamp}.json`;
            const backupPath = join(this.backupDir, filename);

            logger.log("🔄 Criando backup completo...");

            const backupData = {
                metadata: {
                    timestamp: new Date().toISOString(),
                    type: 'full',
                    description: description || 'Backup completo automático',
                    version: '1.0.0'
                },
                economy: this.getEconomyData(),
                voiceSessions: this.getVoiceSessionsData(),
                voiceChannels: this.getVoiceChannelsData()
            };

            writeFileSync(backupPath, JSON.stringify(backupData, null, 2));

            const stats = statSync(backupPath);
            const backupInfo: BackupInfo = {
                timestamp: new Date().toISOString(),
                filename,
                size: stats.size,
                type: 'full',
                description
            };

            logger.success(`✅ Backup completo criado: ${filename} (${this.formatFileSize(stats.size)})`);
            return backupInfo;

        } catch (error) {
            logger.error("❌ Erro ao criar backup completo:", error);
            throw error;
        }
    }

    /**
     * Cria backup apenas dos dados da economia
     */
    async createEconomyBackup(description?: string): Promise<BackupInfo> {
        try {
            const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
            const filename = `economy_backup_${timestamp}.json`;
            const backupPath = join(this.backupDir, filename);

            logger.log("🔄 Criando backup da economia...");

            const backupData = {
                metadata: {
                    timestamp: new Date().toISOString(),
                    type: 'economy',
                    description: description || 'Backup da economia',
                    version: '1.0.0'
                },
                economy: this.getEconomyData()
            };

            writeFileSync(backupPath, JSON.stringify(backupData, null, 2));

            const stats = statSync(backupPath);
            const backupInfo: BackupInfo = {
                timestamp: new Date().toISOString(),
                filename,
                size: stats.size,
                type: 'economy',
                description
            };

            logger.success(`✅ Backup da economia criado: ${filename} (${this.formatFileSize(stats.size)})`);
            return backupInfo;

        } catch (error) {
            logger.error("❌ Erro ao criar backup da economia:", error);
            throw error;
        }
    }

    /**
     * Cria backup apenas dos dados de voice tracking
     */
    async createVoiceBackup(description?: string): Promise<BackupInfo> {
        try {
            const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
            const filename = `voice_backup_${timestamp}.json`;
            const backupPath = join(this.backupDir, filename);

            logger.log("🔄 Criando backup do voice tracking...");

            const backupData = {
                metadata: {
                    timestamp: new Date().toISOString(),
                    type: 'voice',
                    description: description || 'Backup do voice tracking',
                    version: '1.0.0'
                },
                voiceSessions: this.getVoiceSessionsData(),
                voiceChannels: this.getVoiceChannelsData()
            };

            writeFileSync(backupPath, JSON.stringify(backupData, null, 2));

            const stats = statSync(backupPath);
            const backupInfo: BackupInfo = {
                timestamp: new Date().toISOString(),
                filename,
                size: stats.size,
                type: 'voice',
                description
            };

            logger.success(`✅ Backup do voice tracking criado: ${filename} (${this.formatFileSize(stats.size)})`);
            return backupInfo;

        } catch (error) {
            logger.error("❌ Erro ao criar backup do voice tracking:", error);
            throw error;
        }
    }

    /**
     * Lista todos os backups disponíveis
     */
    async listBackups(): Promise<BackupInfo[]> {
        try {
            if (!existsSync(this.backupDir)) {
                return [];
            }

            const files = readdirSync(this.backupDir)
                .filter(file => file.endsWith('.json'))
                .sort((a, b) => b.localeCompare(a)); // Mais recente primeiro

            const backups: BackupInfo[] = [];

            for (const filename of files) {
                try {
                    const filePath = join(this.backupDir, filename);
                    const stats = statSync(filePath);
                    
                    // Tentar ler metadados do backup
                    const backupData = JSON.parse(readFileSync(filePath, 'utf8'));
                    const metadata = backupData.metadata;

                    backups.push({
                        timestamp: metadata?.timestamp || stats.mtime.toISOString(),
                        filename,
                        size: stats.size,
                        type: metadata?.type || this.detectBackupType(filename),
                        description: metadata?.description
                    });
                } catch (error) {
                    logger.warn(`⚠️ Erro ao ler backup ${filename}:`, error);
                }
            }

            return backups;

        } catch (error) {
            logger.error("❌ Erro ao listar backups:", error);
            return [];
        }
    }

    /**
     * Restaura um backup específico
     */
    async restoreBackup(filename: string): Promise<void> {
        try {
            const backupPath = join(this.backupDir, filename);
            
            if (!existsSync(backupPath)) {
                throw new Error(`Backup não encontrado: ${filename}`);
            }

            logger.log(`🔄 Restaurando backup: ${filename}`);

            // Criar backup dos dados atuais antes de restaurar
            await this.createFullBackup(`Backup antes de restaurar ${filename}`);

            const backupData = JSON.parse(readFileSync(backupPath, 'utf8'));

            // Restaurar dados da economia se existir
            if (backupData.economy) {
                const economyPath = join(this.dataDir, 'economy.json');
                writeFileSync(economyPath, JSON.stringify(backupData.economy, null, 2));
                logger.success("✅ Dados da economia restaurados");
            }

            // Restaurar dados de voice tracking se existir
            if (backupData.voiceSessions) {
                const voiceSessionsPath = join(this.dataDir, 'voice-sessions.json');
                writeFileSync(voiceSessionsPath, JSON.stringify(backupData.voiceSessions, null, 2));
                logger.success("✅ Sessões de voice tracking restauradas");
            }

            if (backupData.voiceChannels) {
                const voiceChannelsPath = join(this.dataDir, 'voice-channels.json');
                writeFileSync(voiceChannelsPath, JSON.stringify(backupData.voiceChannels, null, 2));
                logger.success("✅ Dados de canais de voz restaurados");
            }

            logger.success(`✅ Backup restaurado com sucesso: ${filename}`);

        } catch (error) {
            logger.error("❌ Erro ao restaurar backup:", error);
            throw error;
        }
    }

    /**
     * Remove um backup específico
     */
    async deleteBackup(filename: string): Promise<void> {
        try {
            const backupPath = join(this.backupDir, filename);
            
            if (!existsSync(backupPath)) {
                throw new Error(`Backup não encontrado: ${filename}`);
            }

            unlinkSync(backupPath);
            logger.success(`✅ Backup removido: ${filename}`);

        } catch (error) {
            logger.error("❌ Erro ao remover backup:", error);
            throw error;
        }
    }

    /**
     * Limpa backups antigos (mantém apenas os N mais recentes)
     */
    async cleanupOldBackups(keepCount: number = 10): Promise<void> {
        try {
            const backups = await this.listBackups();
            
            if (backups.length <= keepCount) {
                logger.log(`📊 ${backups.length} backups encontrados, nenhum será removido (limite: ${keepCount})`);
                return;
            }

            const toDelete = backups.slice(keepCount);
            let deletedCount = 0;

            for (const backup of toDelete) {
                try {
                    await this.deleteBackup(backup.filename);
                    deletedCount++;
                } catch (error) {
                    logger.warn(`⚠️ Erro ao remover backup ${backup.filename}:`, error);
                }
            }

            logger.success(`✅ Limpeza concluída: ${deletedCount} backups antigos removidos`);

        } catch (error) {
            logger.error("❌ Erro na limpeza de backups:", error);
            throw error;
        }
    }

    // Métodos privados para obter dados

    private getEconomyData(): any {
        const economyPath = join(this.dataDir, 'economy.json');
        if (existsSync(economyPath)) {
            return JSON.parse(readFileSync(economyPath, 'utf8'));
        }
        return {};
    }

    private getVoiceSessionsData(): any {
        const voiceSessionsPath = join(this.dataDir, 'voice-sessions.json');
        if (existsSync(voiceSessionsPath)) {
            return JSON.parse(readFileSync(voiceSessionsPath, 'utf8'));
        }
        return {};
    }

    private getVoiceChannelsData(): any {
        const voiceChannelsPath = join(this.dataDir, 'voice-channels.json');
        if (existsSync(voiceChannelsPath)) {
            return JSON.parse(readFileSync(voiceChannelsPath, 'utf8'));
        }
        return {};
    }

    private detectBackupType(filename: string): 'economy' | 'voice' | 'full' {
        if (filename.includes('economy')) return 'economy';
        if (filename.includes('voice')) return 'voice';
        return 'full';
    }

    private formatFileSize(bytes: number): string {
        const units = ['B', 'KB', 'MB', 'GB'];
        let size = bytes;
        let unitIndex = 0;

        while (size >= 1024 && unitIndex < units.length - 1) {
            size /= 1024;
            unitIndex++;
        }

        return `${size.toFixed(1)} ${units[unitIndex]}`;
    }
}

// Instância global para uso
export const backupSystem = new BackupSystem();
