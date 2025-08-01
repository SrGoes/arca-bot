// Configurações do Sistema de Voice Tracking - ARCA Bot
// Baseado na versão Python anterior, adaptado para TypeScript

export const VoiceConfig = {
    // === CONFIGURAÇÕES PRINCIPAIS ===
    enabled: true,
    
    // Habilitar logs detalhados do voice tracking (desabilite para produção)
    verboseLogs: process.env.VOICE_DEBUG === "true" || false,
    
    // Categoria de canais de voz válidos (nome da categoria)
    voiceChannelsCategory: "C.O.M.M.S OPS",
    
    // === RECOMPENSAS ===
    rewards: {
        // AC por hora de permanência em call
        acPerHour: 20,
        // Tempo mínimo para começar a receber recompensas (em minutos)
        minTimeForReward: 3,
        // Intervalo para atualização de recompensas (em minutos)
        rewardInterval: 1,
    },
    
    // === SISTEMA DE AUSÊNCIA ===
    absence: {
        // Tempo máximo de ausência permitido (em minutos)
        maxAbsenceMinutes: 5,
        // Recuperar sessões após restart do bot (em minutos)
        maxRestartRecoveryTime: 15,
    },
    
    // === MENSAGENS DE STATUS ===
    statusMessages: {
        // Ativar mensagens de status nos canais
        enabled: true,
        // Atualizar mensagens a cada X minutos
        updateInterval: 1,
        // Idade máxima da mensagem antes de recriar (em minutos)
        maxMessageAge: 10,
        // Apagar mensagens quando canal vazio
        deleteWhenEmpty: true,
    },
    
    // === NOTIFICAÇÕES ===
    notifications: {
        // Enviar resumo por DM quando usuário sai da call
        sendExitSummary: false,
        // Enviar notificação de ausência prolongada
        sendAbsenceNotification: false,
        // Enviar confirmação de retorno após ausência
        sendReturnConfirmation: false,
    },
    
    // === CONFIGURAÇÕES GERAIS ===
    general: {
        // Nome da moeda
        currencyName: "Arca Coin",
        // Símbolo da moeda
        currencySymbol: "AC",
        // Emoji da moeda
        currencyEmoji: "🪙",
        // Localização para formatação
        locale: "pt-BR",
    },
    
    // === CORES DOS EMBEDS ===
    colors: {
        active: 0x00FF00,      // Verde para status ativo
        warning: 0xFF9800,     // Laranja para avisos
        error: 0xFF6B6B,       // Vermelho para erros
        info: 0x2196F3,        // Azul para informações
        voice: 0x5865F2,       // Roxo Discord para voice
        absence: 0xFF6B6B,     // Vermelho para ausência
        success: 0x4CAF50,     // Verde para sucesso
    },
    
    // === MENSAGENS TEMPLATES ===
    messages: {
        // Título da mensagem de status
        statusTitle: "🎤 Status da Call - {channelName}",
        // Descrição da mensagem de status
        statusDescription: "**Usuários em C.O.M.M.S OPS**",
        // Formato de linha para cada usuário
        userStatusFormat: "👤 **{displayName}**\n⏱️ {timeStr} | 💰 {acEarned} AC",
        // Rodapé das mensagens
        footerText: "ARCA Bot | Atualizado a cada 1 min",
        // Mensagem quando não há usuários
        noUsersMessage: "Nenhum usuário na call no momento.",
        // Título do resumo de saída
        exitSummaryTitle: "🎤 Resumo da Sessão de Voz",
        // Título de ausência prolongada
        absenceTitle: "⏸️ Sessão Finalizada (Ausência Prolongada)",
        // Título de retorno após ausência
        returnTitle: "🔄 Retorno à Call Confirmado",
    },
    
    // === MÉTODOS HELPER ===
    helpers: {
        // Verificar se um canal é válido para voice tracking
        isValidVoiceChannel(channel: any): boolean {
            return channel && 
                   channel.type === 2 && // GUILD_VOICE
                   channel.parent && 
                   channel.parent.name.toUpperCase() === VoiceConfig.voiceChannelsCategory.toUpperCase();
        },
        
        // Formatar tempo em minutos para string legível
        formatDuration(minutes: number): string {
            if (minutes < 60) {
                return `${minutes}m`;
            }
            const hours = Math.floor(minutes / 60);
            const remainingMinutes = minutes % 60;
            return remainingMinutes > 0 ? `${hours}h ${remainingMinutes}m` : `${hours}h`;
        },
        
        // Calcular AC ganhos baseado no tempo
        calculateReward(minutes: number): number {
            const hours = minutes / 60;
            return Math.floor(hours * VoiceConfig.rewards.acPerHour);
        },
        
        // Formatar template de mensagem
        formatMessage(template: string, replacements: Record<string, string>): string {
            let formatted = template;
            for (const [key, value] of Object.entries(replacements)) {
                formatted = formatted.replace(new RegExp(`{${key}}`, 'g'), value);
            }
            return formatted;
        },
        
        // Verificar se o tempo é suficiente para recompensa
        isEligibleForReward(minutes: number): boolean {
            return minutes >= VoiceConfig.rewards.minTimeForReward;
        },
        
        // Verificar se a ausência excedeu o limite
        isAbsenceTooLong(absenceMinutes: number): boolean {
            return absenceMinutes >= VoiceConfig.absence.maxAbsenceMinutes;
        },
        
        // Verificar se pode recuperar sessão após restart
        canRecoverSession(minutesSinceRestart: number): boolean {
            return minutesSinceRestart <= VoiceConfig.absence.maxRestartRecoveryTime;
        },
        
        // Verificar se canal deve receber recompensas
        shouldReceiveRewards(channel: any): boolean {
            return VoiceConfig.helpers.isValidVoiceChannel(channel);
        }
    }
};
