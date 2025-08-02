import { createEvent } from "#base";
import { Events, VoiceState, EmbedBuilder, GuildMember } from "discord.js";
import { voiceTrackingStore, economyStore } from "#database";
import { logger } from "#settings";
import { VoiceConfig } from "../../../settings/voiceConfig.js";

// Maps para controlar intervalos e locks
const rewardIntervals = new Map<string, NodeJS.Timeout>();
const channelLocks = new Map<string, boolean>();

// Referência global ao client para uso em tasks
let globalClient: any = null;

createEvent({
    name: "voiceStateUpdate",
    event: Events.VoiceStateUpdate,
    async run(oldState: VoiceState, newState: VoiceState) {
        // Armazenar referência do client
        globalClient = newState.client;
        
        const oldChannelId = oldState.channelId;
        const newChannelId = newState.channelId;

        // Ignorar bots
        if (newState.member?.user.bot) return;

        try {
            // Usuário entrou em um canal de voz (estava fora)
            if (!oldChannelId && newChannelId) {
                await handleUserJoinVoice(newState);
            }
            // Usuário saiu de um canal de voz (agora está fora)
            else if (oldChannelId && !newChannelId) {
                await handleUserLeaveVoice(oldState);
            }
            // Usuário mudou de canal de voz
            else if (oldChannelId && newChannelId && oldChannelId !== newChannelId) {
                await handleUserChangeChannel(oldState, newState);
            }
            // Usuário apenas mudou estado (mute/deafen) - apenas atualizar atividade
            else if (oldChannelId && newChannelId && oldChannelId === newChannelId) {
                await handleUserStateChange(newState);
            }
        } catch (error) {
            logger.error("Erro no voice state update:", error);
        }
    }
});

// === HANDLERS PRINCIPAIS ===

async function handleUserJoinVoice(voiceState: VoiceState): Promise<void> {
    const { member, channel } = voiceState;
    if (!member || !channel) return;

    logger.log(`[VOICE] ${member.displayName} entrou no canal ${channel.name}`);

    // Verificar se é um canal válido
    if (!VoiceConfig.helpers.isValidVoiceChannel(channel)) {
        return;
    }

    // Verificar se já tem uma sessão ativa (pode ter mudado de canal)
    const existingSession = voiceTrackingStore.getActiveSession(member.id);
    if (existingSession) {
        if (VoiceConfig.verboseLogs) {
            logger.log(`[VOICE] ${member.displayName} já tem sessão ativa, atualizando...`);
        }
        // Apenas atualizar atividade se já estava ativo
        voiceTrackingStore.updateSessionActivity(member.id);
        await updateChannelStatusMessage(channel);
        return;
    }

    // Iniciar nova sessão
    voiceTrackingStore.startSession(
        member.id,
        channel.id,
        channel.name,
        channel.guild.id
    );

    if (VoiceConfig.verboseLogs) {
        logger.success(`[VOICE] Nova sessão iniciada para ${member.displayName}`);
    }

    // Iniciar sistema de recompensas
    startRewardInterval(member.id);

    // Atualizar mensagem de status do canal
    await updateChannelStatusMessage(channel);
}

async function handleUserLeaveVoice(voiceState: VoiceState): Promise<void> {
    const { member, channel } = voiceState;
    if (!member || !channel) return;

    if (VoiceConfig.verboseLogs) {
        logger.log(`[VOICE] ${member.displayName} saiu do canal ${channel.name}`);
    }

    // Verificar se é um canal válido
    if (!VoiceConfig.helpers.isValidVoiceChannel(channel)) return;

    const session = voiceTrackingStore.getActiveSession(member.id);
    if (!session) return;

    // Finalizar a sessão
    await finalizeUserSession(member, false);

    // Parar sistema de recompensas
    stopRewardInterval(member.id);

    // Atualizar mensagem de status do canal
    await updateChannelStatusMessage(channel);
}

async function handleUserChangeChannel(oldState: VoiceState, newState: VoiceState): Promise<void> {
    const { member } = newState;
    if (!member) return;

    const oldChannel = oldState.channel;
    const newChannel = newState.channel;
    
    if (VoiceConfig.verboseLogs) {
        logger.log(`[VOICE] ${member.displayName} mudou de ${oldChannel?.name} para ${newChannel?.name}`);
    }

    const session = voiceTrackingStore.getActiveSession(member.id);
    
    // Se não tem sessão ativa e está entrando em canal válido, criar nova
    if (!session && newChannel && VoiceConfig.helpers.isValidVoiceChannel(newChannel)) {
        voiceTrackingStore.startSession(
            member.id,
            newChannel.id,
            newChannel.name,
            newChannel.guild.id
        );
        
        if (VoiceConfig.verboseLogs) {
            logger.success(`[VOICE] Nova sessão iniciada para ${member.displayName} em ${newChannel.name}`);
        }
        
        // Iniciar sistema de recompensas
        if (VoiceConfig.helpers.shouldReceiveRewards(newChannel)) {
            startRewardInterval(member.id);
        }
        
        await updateChannelStatusMessage(newChannel);
        return;
    }

    // Se tem sessão ativa, apenas atualizar o canal
    if (session) {
        // Atualizar dados da sessão para o novo canal
        if (newChannel && VoiceConfig.helpers.isValidVoiceChannel(newChannel)) {
            // Manter a sessão mas atualizar canal
            voiceTrackingStore.updateSessionChannel(member.id, newChannel.id, newChannel.name);
            voiceTrackingStore.updateSessionActivity(member.id);
            
            if (VoiceConfig.verboseLogs) {
                logger.success(`[VOICE] Canal atualizado para ${member.displayName}: ${newChannel.name} (sessão mantida)`);
            }
            
            // Verificar se deve ajustar recompensas baseado no novo canal
            if (VoiceConfig.helpers.shouldReceiveRewards(newChannel)) {
                if (!rewardIntervals.has(member.id)) {
                    startRewardInterval(member.id);
                }
            } else {
                if (rewardIntervals.has(member.id)) {
                    stopRewardInterval(member.id);
                }
            }
            
            await updateChannelStatusMessage(newChannel);
        } else {
            // Saindo para canal inválido - finalizar sessão
            await finalizeUserSession(member, false);
            stopRewardInterval(member.id);
        }
    }

    // Atualizar status do canal antigo
    if (oldChannel) {
        await updateChannelStatusMessage(oldChannel);
    }
}

async function handleUserStateChange(voiceState: VoiceState): Promise<void> {
    const { member } = voiceState;
    if (!member) return;

    // Apenas atualizar atividade - não tratar como ausência
    voiceTrackingStore.updateSessionActivity(member.id);
}

// === SISTEMA DE RECOMPENSAS ===

function startRewardInterval(userId: string): void {
    // Limpar interval anterior se existir
    stopRewardInterval(userId);

    const interval = setInterval(async () => {
        await processUserReward(userId);
    }, VoiceConfig.rewards.rewardInterval * 60 * 1000);

    rewardIntervals.set(userId, interval);
}

function stopRewardInterval(userId: string): void {
    const interval = rewardIntervals.get(userId);
    if (interval) {
        clearInterval(interval);
        rewardIntervals.delete(userId);
    }
}

async function processUserReward(userId: string): Promise<void> {
    try {
        const session = voiceTrackingStore.getActiveSession(userId);
        if (!session) {
            stopRewardInterval(userId);
            return;
        }

        const currentMinutes = voiceTrackingStore.getSessionDuration(userId);
        
        // Verificar se já passou do tempo mínimo
        if (!VoiceConfig.helpers.isEligibleForReward(currentMinutes)) return;

        // Calcular recompensa baseada no tempo total
        const totalReward = VoiceConfig.helpers.calculateReward(currentMinutes);
        const currentReward = session.acEarned;
        const rewardToGive = totalReward - currentReward;

        if (rewardToGive > 0) {
            // Adicionar ao saldo do usuário
            economyStore.addBalance(userId, rewardToGive);
            
            // Atualizar sessão
            voiceTrackingStore.updateSessionReward(userId, rewardToGive);
            
            if (VoiceConfig.verboseLogs) {
                logger.log(`[VOICE] Recompensa de ${rewardToGive} AC dada para ${userId}`);
            }
        }

        // Atualizar mensagem de status se necessário
        if (globalClient && session.channelId) {
            const channel = globalClient.channels.cache.get(session.channelId);
            if (channel) {
                await updateChannelStatusMessage(channel);
            }
        }
    } catch (error) {
        logger.error(`Erro ao processar recompensa para ${userId}:`, error);
    }
}

// === SISTEMA DE MENSAGENS DE STATUS ===

async function updateChannelStatusMessage(channel: any): Promise<void> {
    if (!VoiceConfig.statusMessages.enabled) return;
    
    // Evitar múltiplas atualizações simultâneas no mesmo canal
    if (channelLocks.get(channel.id)) return;
    channelLocks.set(channel.id, true);

    try {
        // Obter usuários ativos no canal
        const activeUsers = getActiveUsersInChannel(channel);

        if (activeUsers.length === 0) {
            // Canal vazio - limpar mensagens e remover status
            await cleanupOldStatusMessages(channel);
            voiceTrackingStore.removeChannelStatus(channel.id);
            return;
        }

        // Criar embed de status
        const embed = await createStatusEmbed(channel, activeUsers);
        
        // Tentar recuperar mensagem existente
        const channelStatus = voiceTrackingStore.getChannelStatus(channel.id);
        let message = null;
        
        if (channelStatus?.messageId) {
            try {
                message = await channel.messages.fetch(channelStatus.messageId);
                
                // Verificar se a mensagem é muito antiga (10 minutos)
                const messageAge = Date.now() - message.createdTimestamp;
                const maxAge = VoiceConfig.statusMessages.maxMessageAge * 60 * 1000;
                
                if (messageAge > maxAge) {
                    // Mensagem antiga - deletar e criar nova
                    await message.delete();
                    message = null;
                }
            } catch (error) {
                // Mensagem não encontrada - criar nova
                message = null;
            }
        }
        
        if (message) {
            // Editar mensagem existente
            await message.edit({ embeds: [embed] });
            if (VoiceConfig.verboseLogs) {
                logger.log(`[VOICE] Status editado para canal ${channel.name} (${activeUsers.length} usuários)`);
            }
        } else {
            // Limpar mensagens antigas e criar nova
            await cleanupOldStatusMessages(channel);
            message = await channel.send({ embeds: [embed] });
            
            // Salvar referência da nova mensagem
            voiceTrackingStore.updateChannelStatus(
                channel.id,
                message.id,
                activeUsers.map(user => user.id)
            );
            
            if (VoiceConfig.verboseLogs) {
                logger.log(`[VOICE] Nova mensagem de status criada para canal ${channel.name} (${activeUsers.length} usuários)`);
            }
        }

    } catch (error) {
        logger.error(`Erro ao atualizar status do canal ${channel.name}:`, error);
    } finally {
        channelLocks.delete(channel.id);
    }
}

async function cleanupOldStatusMessages(channel: any): Promise<void> {
    try {
        const messages = await channel.messages.fetch({ limit: 30 });
        
        for (const message of messages.values()) {
            if (message.author.id === globalClient?.user?.id && 
                message.embeds.length > 0 &&
                message.embeds[0].title?.includes("Status da Call")) {
                try {
                    await message.delete();
                } catch (error) {
                    // Ignorar erros de deleção
                }
            }
        }
    } catch (error) {
        logger.error(`Erro ao limpar mensagens antigas:`, error);
    }
}

function getActiveUsersInChannel(channel: any): any[] {
    const activeUsers: any[] = [];
    
    for (const member of channel.members.values()) {
        if (!member.user.bot) {
            const session = voiceTrackingStore.getActiveSession(member.id);
            if (session && session.channelId === channel.id) {
                activeUsers.push(member);
            }
        }
    }
    
    return activeUsers;
}

async function createStatusEmbed(channel: any, activeUsers: any[]): Promise<EmbedBuilder> {
    const embed = new EmbedBuilder()
        .setTitle(VoiceConfig.helpers.formatMessage(VoiceConfig.messages.statusTitle, {
            channelName: channel.name
        }))
        .setDescription(VoiceConfig.messages.statusDescription)
        .setColor(VoiceConfig.colors.voice)
        .setTimestamp()
        .setFooter({ text: VoiceConfig.messages.footerText });

    if (activeUsers.length === 0) {
        embed.setDescription(VoiceConfig.messages.noUsersMessage);
        return embed;
    }

    const userLines: string[] = [];
    
    for (const member of activeUsers) {
        try {
            const session = voiceTrackingStore.getActiveSession(member.id);
            if (!session) continue;

            const duration = voiceTrackingStore.getSessionDuration(member.id);
            const timeStr = VoiceConfig.helpers.formatDuration(duration);
            const acEarned = session.acEarned;

            const userLine = VoiceConfig.helpers.formatMessage(VoiceConfig.messages.userStatusFormat, {
                displayName: member.displayName,
                timeStr,
                acEarned: acEarned.toString()
            });

            userLines.push(userLine);
        } catch (error) {
            logger.error(`Erro ao processar usuário ${member.id}:`, error);
        }
    }

    if (userLines.length > 0) {
        embed.addFields({
            name: `📊 ${activeUsers.length} usuário(s) ativo(s)`,
            value: userLines.join("\n\n"),
            inline: false
        });
    }

    return embed;
}

// === FINALIZAÇÃO DE SESSÕES ===

async function finalizeUserSession(member: GuildMember | null, wasAbsent: boolean = false): Promise<void> {
    if (!member) return;

    const session = voiceTrackingStore.endSession(member.id);
    if (!session) return;

    // Calcular valores finais
    const totalMinutes = session.totalMinutes;

    if (VoiceConfig.verboseLogs) {
        logger.log(`[VOICE] Sessão finalizada para ${member.displayName}: ${totalMinutes}min, ${session.acEarned} AC`);
    }

    // Parar sistema de recompensas
    stopRewardInterval(member.id);

    // Enviar resumo por DM se habilitado
    if (VoiceConfig.notifications.sendExitSummary) {
        await sendExitSummaryDM(member, session, wasAbsent);
    }

    // Atualizar status do canal se ainda existe
    if (globalClient && session.channelId) {
        const channel = globalClient.channels.cache.get(session.channelId);
        if (channel) {
            await updateChannelStatusMessage(channel);
        }
    }
}

// === NOTIFICAÇÕES DM ===

async function sendExitSummaryDM(member: GuildMember, session: any, wasAbsent: boolean): Promise<void> {
    try {
        const user = economyStore.getUser(member.id);
        const timeStr = VoiceConfig.helpers.formatDuration(session.totalMinutes);
        
        const embed = new EmbedBuilder()
            .setTitle(VoiceConfig.messages.exitSummaryTitle)
            .setDescription(`Olá **${member.displayName}**! Aqui está o resumo da sua participação na call:`)
            .setColor(wasAbsent ? VoiceConfig.colors.absence : VoiceConfig.colors.voice)
            .setTimestamp()
            .setThumbnail(member.displayAvatarURL())
            .setFooter({ text: "ARCA Organization - Obrigado por participar!" })
            .addFields(
                { name: "⏱️ Tempo Total", value: timeStr, inline: true },
                { name: "💰 AC Ganhos", value: `${session.acEarned} AC`, inline: true },
                { name: "💳 Saldo Atual", value: `${user.balance} AC`, inline: true }
            );

        await member.send({ embeds: [embed] });
        logger.log(`[VOICE] Resumo enviado por DM para ${member.displayName}`);
    } catch (error) {
        // DMs podem estar fechadas - não é um erro crítico
    }
}

// === RECUPERAÇÃO APÓS RESTART ===

export async function recoverVoiceSessions(client: any): Promise<void> {
    if (!VoiceConfig.enabled) return;

    globalClient = client;
    if (VoiceConfig.verboseLogs) {
        logger.log("[VOICE] Iniciando recuperação de sessões...");
    }

    try {
        const data = voiceTrackingStore.getRecoveryData();
        let recoveredSessions = 0;
        let cleanedSessions = 0;

        // Verificar sessões ativas
        for (const session of Object.values(data.activeSessions)) {
            const guild = client.guilds.cache.get(session.guildId);
            if (!guild) {
                voiceTrackingStore.endSession(session.userId);
                cleanedSessions++;
                continue;
            }

            try {
                const channel = guild.channels.cache.get(session.channelId);
                if (!channel || !VoiceConfig.helpers.isValidVoiceChannel(channel)) {
                    voiceTrackingStore.endSession(session.userId);
                    cleanedSessions++;
                    continue;
                }

                const member = guild.members.cache.get(session.userId);
                if (!member || !member.voice || member.voice.channelId !== session.channelId) {
                    voiceTrackingStore.endSession(session.userId);
                    cleanedSessions++;
                    continue;
                }

                // Reativar sistema de recompensas para todas as sessões existentes
                startRewardInterval(session.userId);
                recoveredSessions++;
                if (VoiceConfig.verboseLogs) {
                    logger.log(`[VOICE] Sessão recuperada: ${member.displayName} em ${channel.name}`);
                }
            } catch (error) {
                logger.error(`Erro ao recuperar sessão ${session.userId}:`, error);
                voiceTrackingStore.endSession(session.userId);
                cleanedSessions++;
            }
        }

        // Atualizar mensagens de status dos canais ativos
        const activeChannels = new Set<string>();
        for (const session of voiceTrackingStore.getAllActiveSessions()) {
            activeChannels.add(session.channelId);
        }

        for (const channelId of activeChannels) {
            const channel = client.channels.cache.get(channelId);
            if (channel && VoiceConfig.helpers.isValidVoiceChannel(channel)) {
                await updateChannelStatusMessage(channel);
            }
        }

        logger.success(`[VOICE] Recuperação concluída: ${recoveredSessions} recuperadas, ${cleanedSessions} limpas`);
    } catch (error) {
        logger.error("[VOICE] Erro na recuperação de sessões:", error);
    }
}

// === LIMPEZA PERIÓDICA ===

// Executar limpeza a cada hora
setInterval(() => {
    voiceTrackingStore.cleanup();
}, 60 * 60 * 1000);
