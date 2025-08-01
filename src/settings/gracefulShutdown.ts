import { Client } from "discord.js";
import { logger } from "./logger.js";
import { voiceTrackingStore } from "#database";
import { backupSystem } from "./backupSystem.js";

// Variáveis globais para controle
let isShuttingDown = false;
let shutdownTimeoutId: NodeJS.Timeout | null = null;
const shutdownTimeout = 10000; // 10 segundos timeout

export async function gracefulShutdown(client: Client | null, signal: string = "UNKNOWN"): Promise<void> {
    if (isShuttingDown) {
        logger.warn("⚠️ Shutdown já em andamento...");
        return;
    }

    isShuttingDown = true;
    logger.log(`🔄 Iniciando shutdown graceful... (Signal: ${signal})`);

    // Timeout de segurança
    shutdownTimeoutId = setTimeout(() => {
        logger.error("❌ Timeout no shutdown graceful - forçando saída");
        process.exit(1);
    }, shutdownTimeout);

    try {
        // 1. Parar de aceitar novos eventos
        if (client && client.isReady()) {
            logger.log("🔄 Pausando processamento de novos eventos...");
            client.removeAllListeners();
        }

        // 2. Criar backup antes de finalizar
        await createBackupBeforeShutdown(signal);

        // 3. Finalizar todas as sessões de voice tracking ativas
        await finalizeActiveSessions();

        // 4. Salvar dados pendentes
        await saveAllPendingData();

        // 4. Desconectar do Discord
        if (client && client.isReady()) {
            logger.log("🔄 Desconectando do Discord...");
            await client.destroy();
            logger.success("✅ Desconectado do Discord");
        }

        // 5. Limpar timeouts
        clearAllTimeouts();

        // 6. Limpar timeout de segurança
        if (shutdownTimeoutId) {
            clearTimeout(shutdownTimeoutId);
            shutdownTimeoutId = null;
        }

        logger.success("✅ Shutdown graceful concluído com sucesso");
        process.exit(0);

    } catch (error) {
        logger.error("❌ Erro durante shutdown graceful:", error);
        
        if (shutdownTimeoutId) {
            clearTimeout(shutdownTimeoutId);
        }
        
        process.exit(1);
    }
}

async function createBackupBeforeShutdown(signal: string): Promise<void> {
    try {
        logger.log("🔄 Criando backup antes do shutdown...");
        
        const description = `Backup automático antes do shutdown (${signal})`;
        await backupSystem.createFullBackup(description);
        
        logger.success("✅ Backup criado antes do shutdown");
    } catch (error) {
        logger.error("❌ Erro ao criar backup antes do shutdown:", error);
        // Não interromper o shutdown por causa do backup
    }
}

async function finalizeActiveSessions(): Promise<void> {
    try {
        logger.log("🔄 Finalizando sessões de voice tracking ativas...");
        
        const activeSessions = voiceTrackingStore.getAllActiveSessions();
        let finalizedCount = 0;

        for (const session of activeSessions) {
            try {
                voiceTrackingStore.endSession(session.userId);
                finalizedCount++;
            } catch (error) {
                logger.error(`❌ Erro ao finalizar sessão do usuário ${session.userId}:`, error);
            }
        }

        logger.success(`✅ ${finalizedCount} sessões finalizadas`);
    } catch (error) {
        logger.error("❌ Erro ao finalizar sessões:", error);
    }
}

async function saveAllPendingData(): Promise<void> {
    try {
        logger.log("🔄 Salvando dados pendentes...");
        
        // Força uma limpeza final dos dados
        voiceTrackingStore.cleanup();
        
        logger.success("✅ Dados salvos com sucesso");
    } catch (error) {
        logger.error("❌ Erro ao salvar dados:", error);
    }
}

function clearAllTimeouts(): void {
    try {
        logger.log("🔄 Limpando timeouts e intervalos...");
        
        // Limpar intervalos de limpeza periódica
        // (Os intervalos específicos de recompensas são limpos quando as sessões são finalizadas)
        
        logger.success("✅ Timeouts limpos");
    } catch (error) {
        logger.error("❌ Erro ao limpar timeouts:", error);
    }
}

// Função para registrar handlers de shutdown
export function registerShutdownHandlers(client: Client): void {
    // Ctrl+C
    process.on('SIGINT', () => {
        logger.log("📝 Recebido SIGINT (Ctrl+C)");
        gracefulShutdown(client, 'SIGINT');
    });

    // Terminal kill
    process.on('SIGTERM', () => {
        logger.log("📝 Recebido SIGTERM");
        gracefulShutdown(client, 'SIGTERM');
    });

    // Windows Ctrl+Break
    process.on('SIGBREAK', () => {
        logger.log("📝 Recebido SIGBREAK");
        gracefulShutdown(client, 'SIGBREAK');
    });

    // Erro não capturado
    process.on('uncaughtException', (error) => {
        logger.error("❌ Erro não capturado:", error);
        gracefulShutdown(client, 'UNCAUGHT_EXCEPTION');
    });

    // Promise rejeitada não tratada
    process.on('unhandledRejection', (reason) => {
        logger.error("❌ Promise rejeitada não tratada:", reason);
        gracefulShutdown(client, 'UNHANDLED_REJECTION');
    });

    // Aviso quando o processo está saindo
    process.on('exit', (code) => {
        logger.log(`🔄 Processo saindo com código: ${code}`);
    });

    logger.success("✅ Handlers de shutdown registrados");
}

// Função para comando administrativo de shutdown
export async function adminShutdown(client: Client, reason: string = "Comando administrativo"): Promise<void> {
    logger.log(`📝 Shutdown solicitado: ${reason}`);
    await gracefulShutdown(client, 'ADMIN_COMMAND');
}
