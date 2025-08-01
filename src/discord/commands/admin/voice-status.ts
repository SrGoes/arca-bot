import { createCommand } from "#base";
import { ApplicationCommandOptionType, EmbedBuilder } from "discord.js";
import { voiceTrackingStore } from "#database";
import { VoiceConfig } from "../../../settings/voiceConfig.js";
import { isUserAdmin } from "../../../settings/economyConfig.js";

createCommand({
    name: "voice-status",
    description: "Mostra o status atual do sistema de voice tracking",
    defaultMemberPermissions: ["Administrator"],
    options: [
        {
            name: "acao",
            description: "Ação a ser executada",
            type: ApplicationCommandOptionType.String,
            required: false,
            choices: [
                { name: "Status Geral", value: "status" },
                { name: "Sessões Ativas", value: "active" },
                { name: "Usuários Ausentes", value: "absent" },
                { name: "Limpeza", value: "cleanup" }
            ]
        }
    ],
    async run(interaction) {
        // Verificar se o usuário é administrador
        const member = interaction.member;
        if (!member) {
            await interaction.reply({
                content: "❌ Erro: Não foi possível identificar o usuário.",
                ephemeral: true
            });
            return;
        }

        const userRoles = member.roles instanceof Array ? member.roles : Array.from(member.roles.cache.keys());
        const hasAdminPermission = member.permissions.has("Administrator");
        
        if (!isUserAdmin(interaction.user.id, userRoles, hasAdminPermission)) {
            await interaction.reply({
                content: "❌ Você não tem permissão para usar este comando. Apenas administradores podem acessar o status do voice tracking.",
                ephemeral: true
            });
            return;
        }

        const acao = interaction.options.getString("acao") || "status";

        try {
            switch (acao) {
                case "status":
                    await showGeneralStatus(interaction);
                    break;
                case "active":
                    await showActiveSessions(interaction);
                    break;  
                case "absent":
                    await showAbsentUsers(interaction);
                    break;
                case "cleanup":
                    await performCleanup(interaction);
                    break;
            }
        } catch (error) {
            console.error("Erro no comando voice-status:", error);
            await interaction.reply({
                content: "❌ Erro ao executar comando de voice status.",
                ephemeral: true
            });
        }
    }
});

async function showGeneralStatus(interaction: any): Promise<void> {
    const activeSessions = voiceTrackingStore.getAllActiveSessions();
    const absentUsers = voiceTrackingStore.getAllAbsentUsers();
    const channelStatuses = voiceTrackingStore.getAllChannelStatuses();

    const embed = new EmbedBuilder()
        .setTitle("🎤 Status do Sistema de Voice Tracking")
        .setDescription("**Visão geral do sistema ARCA Voice Tracking**")
        .setColor(VoiceConfig.colors.info)
        .setTimestamp()
        .addFields(
            {
                name: "📊 Estatísticas Gerais",
                value: [
                    `🟢 **Sessões Ativas:** ${activeSessions.length}`,
                    `⏸️ **Usuários Ausentes:** ${absentUsers.length}`,
                    `📺 **Canais com Status:** ${channelStatuses.length}`,
                    `⚙️ **Sistema:** ${VoiceConfig.enabled ? "Ativo" : "Inativo"}`
                ].join("\n"),
                inline: false
            },
            {
                name: "🎯 Configurações",
                value: [
                    `💰 **AC por Hora:** ${VoiceConfig.rewards.acPerHour}`,
                    `⏱️ **Tempo Mín. Recompensa:** ${VoiceConfig.rewards.minTimeForReward} min`,
                    `⏸️ **Limite Ausência:** ${VoiceConfig.absence.maxAbsenceMinutes} min`,
                    `📂 **Categoria:** ${VoiceConfig.voiceChannelsCategory}`
                ].join("\n"),
                inline: false
            }
        )
        .setFooter({ text: "ARCA Bot - Voice Tracking System" });

    if (activeSessions.length > 0) {
        const topSessions = activeSessions
            .sort((a, b) => {
                const durationA = voiceTrackingStore.getSessionDuration(a.userId);
                const durationB = voiceTrackingStore.getSessionDuration(b.userId);
                return durationB - durationA;
            })
            .slice(0, 5);

        const sessionList = topSessions.map(session => {
            const duration = voiceTrackingStore.getSessionDuration(session.userId);
            const timeStr = VoiceConfig.helpers.formatDuration(duration);
            return `• <@${session.userId}> - ${session.channelName} (${timeStr})`;
        }).join("\n");

        embed.addFields({
            name: "🎤 Top 5 Sessões Ativas",
            value: sessionList,
            inline: false
        });
    }

    await interaction.reply({ embeds: [embed], ephemeral: true });
}

async function showActiveSessions(interaction: any): Promise<void> {
    const activeSessions = voiceTrackingStore.getAllActiveSessions();

    const embed = new EmbedBuilder()
        .setTitle("🎤 Sessões Ativas")
        .setColor(VoiceConfig.colors.active)
        .setTimestamp();

    if (activeSessions.length === 0) {
        embed.setDescription("Nenhuma sessão ativa no momento.");
        await interaction.reply({ embeds: [embed], ephemeral: true });
        return;
    }

    const sessionGroups: Record<string, any[]> = {};
    activeSessions.forEach(session => {
        if (!sessionGroups[session.channelName]) {
            sessionGroups[session.channelName] = [];
        }
        sessionGroups[session.channelName].push(session);
    });

    for (const [channelName, sessions] of Object.entries(sessionGroups)) {
        const sessionList = sessions.map(session => {
            const duration = voiceTrackingStore.getSessionDuration(session.userId);
            const timeStr = VoiceConfig.helpers.formatDuration(duration);
            return `• <@${session.userId}> - ${timeStr} (${session.acEarned} AC)`;
        }).join("\n");

        embed.addFields({
            name: `🔊 ${channelName} (${sessions.length} usuários)`,
            value: sessionList,
            inline: false
        });
    }

    embed.setDescription(`**${activeSessions.length} sessões ativas encontradas**`);
    await interaction.reply({ embeds: [embed], ephemeral: true });
}

async function showAbsentUsers(interaction: any): Promise<void> {
    const absentUsers = voiceTrackingStore.getAllAbsentUsers();

    const embed = new EmbedBuilder()
        .setTitle("⏸️ Usuários Ausentes")
        .setColor(VoiceConfig.colors.warning)
        .setTimestamp();

    if (absentUsers.length === 0) {
        embed.setDescription("Nenhum usuário ausente no momento.");
        await interaction.reply({ embeds: [embed], ephemeral: true });
        return;
    }

    const absentList = absentUsers.map(absentUser => {
        // Sistema de ausência removido - valores zerados
        const absenceDuration = 0;
        const remainingTime = 0;
        const timeStr = VoiceConfig.helpers.formatDuration(absenceDuration);
        const remainingStr = VoiceConfig.helpers.formatDuration(Math.max(0, remainingTime));
        
        return [
            `• <@${absentUser.userId}> - **${absentUser.channelName}**`,
            `  ⏱️ Ausente há: ${timeStr}`,
            `  ⏰ Restam: ${remainingStr}`,
            `  💰 AC antes da ausência: ${absentUser.acEarnedBeforeAbsence}`
        ].join("\n");
    }).join("\n\n");

    embed.setDescription(`**${absentUsers.length} usuários ausentes**\n\n${absentList}`);
    embed.addFields({
        name: "ℹ️ Informação",
        value: `Usuários ausentes por mais de ${VoiceConfig.absence.maxAbsenceMinutes} minutos terão suas sessões finalizadas automaticamente.`,
        inline: false
    });

    await interaction.reply({ embeds: [embed], ephemeral: true });
}

async function performCleanup(interaction: any): Promise<void> {
    try {
        voiceTrackingStore.cleanup();

        const embed = new EmbedBuilder()
            .setTitle("🧹 Limpeza Executada")
            .setDescription("Limpeza do sistema de voice tracking executada com sucesso!")
            .setColor(VoiceConfig.colors.success)
            .setTimestamp()
            .addFields({
                name: "📋 Ações Executadas",
                value: [
                    "• Sessões antigas removidas",
                    "• Ausências expiradas limpas",
                    "• Status de canais validado",
                    "• Dados salvos"
                ].join("\n"),
                inline: false
            })
            .setFooter({ text: "ARCA Bot - Sistema de Limpeza" });

        await interaction.reply({ embeds: [embed], ephemeral: true });
    } catch (error) {
        console.error("Erro na limpeza:", error);
        await interaction.reply({
            content: "❌ Erro ao executar limpeza do sistema.",
            ephemeral: true
        });
    }
}
