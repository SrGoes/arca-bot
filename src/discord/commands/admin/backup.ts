import { 
    ApplicationCommandType, 
    ApplicationCommandOptionType, 
    Colors, 
    AttachmentBuilder, 
    ChatInputCommandInteraction, 
    PermissionFlagsBits 
} from "discord.js";
import { createCommand } from "#base";
import { backupSystem } from "#settings";
import { readFileSync } from "fs";
import { join } from "path";

createCommand({
    name: "backup",
    description: "👑 [ADMIN] Gerencia backups dos dados do bot",
    type: ApplicationCommandType.ChatInput,
    defaultMemberPermissions: PermissionFlagsBits.Administrator,
    options: [
        {
            name: "acao",
            description: "Ação a ser executada",
            type: ApplicationCommandOptionType.String,
            required: true,
            choices: [
                {
                    name: "💾 Criar backup completo",
                    value: "create_full"
                },
                {
                    name: "💰 Criar backup da economia",
                    value: "create_economy"
                },
                {
                    name: "🎤 Criar backup do voice tracking",
                    value: "create_voice"
                },
                {
                    name: "📋 Listar backups",
                    value: "list"
                },
                {
                    name: "⬇️ Baixar backup",
                    value: "download"
                },
                {
                    name: "🔄 Restaurar backup",
                    value: "restore"
                },
                {
                    name: "🗑️ Remover backup",
                    value: "delete"
                },
                {
                    name: "🧹 Limpar backups antigos",
                    value: "cleanup"
                }
            ]
        },
        {
            name: "arquivo",
            description: "Nome do arquivo de backup (para download/restore/delete)",
            type: ApplicationCommandOptionType.String,
            required: false
        },
        {
            name: "descricao",
            description: "Descrição do backup (opcional)",
            type: ApplicationCommandOptionType.String,
            required: false
        },
        {
            name: "manter",
            description: "Quantos backups manter na limpeza (padrão: 10)",
            type: ApplicationCommandOptionType.Integer,
            required: false,
            minValue: 1,
            maxValue: 50
        }
    ],
    async run(interaction: ChatInputCommandInteraction) {
        const action = interaction.options.getString("acao", true);
        const filename = interaction.options.getString("arquivo");
        const description = interaction.options.getString("descricao");
        const keepCount = interaction.options.getInteger("manter") || 10;

        await interaction.deferReply();

        try {
            switch (action) {
                case "create_full":
                    await handleCreateFullBackup(interaction, description);
                    break;
                    
                case "create_economy":
                    await handleCreateEconomyBackup(interaction, description);
                    break;
                    
                case "create_voice":
                    await handleCreateVoiceBackup(interaction, description);
                    break;
                    
                case "list":
                    await handleListBackups(interaction);
                    break;
                    
                case "download":
                    if (!filename) {
                        await interaction.editReply({
                            embeds: [{
                                color: Colors.Red,
                                title: "❌ Erro",
                                description: "Você precisa especificar o nome do arquivo para download."
                            }]
                        });
                        return;
                    }
                    await handleDownloadBackup(interaction, filename);
                    break;
                    
                case "restore":
                    if (!filename) {
                        await interaction.editReply({
                            embeds: [{
                                color: Colors.Red,
                                title: "❌ Erro",
                                description: "Você precisa especificar o nome do arquivo para restaurar."
                            }]
                        });
                        return;
                    }
                    await handleRestoreBackup(interaction, filename);
                    break;
                    
                case "delete":
                    if (!filename) {
                        await interaction.editReply({
                            embeds: [{
                                color: Colors.Red,
                                title: "❌ Erro",
                                description: "Você precisa especificar o nome do arquivo para remover."
                            }]
                        });
                        return;
                    }
                    await handleDeleteBackup(interaction, filename);
                    break;
                    
                case "cleanup":
                    await handleCleanupBackups(interaction, keepCount);
                    break;
            }
        } catch (error) {
            await interaction.editReply({
                embeds: [{
                    color: Colors.Red,
                    title: "❌ Erro no backup",
                    description: `Ocorreu um erro: ${error instanceof Error ? error.message : String(error)}`
                }]
            });
        }
    }
});

async function handleCreateFullBackup(interaction: ChatInputCommandInteraction, description?: string | null) {
    const backupInfo = await backupSystem.createFullBackup(description || undefined);
    
    await interaction.editReply({
        embeds: [{
            color: Colors.Green,
            title: "✅ Backup Completo Criado",
            fields: [
                {
                    name: "📁 Arquivo",
                    value: backupInfo.filename,
                    inline: true
                },
                {
                    name: "📊 Tamanho",
                    value: formatFileSize(backupInfo.size),
                    inline: true
                },
                {
                    name: "🕐 Data/Hora",
                    value: `<t:${Math.floor(new Date(backupInfo.timestamp).getTime() / 1000)}:F>`,
                    inline: false
                },
                {
                    name: "📝 Descrição",
                    value: backupInfo.description || "Backup completo",
                    inline: false
                }
            ],
            footer: { text: "Use '/backup download' para baixar o arquivo" }
        }]
    });
}

async function handleCreateEconomyBackup(interaction: ChatInputCommandInteraction, description?: string | null) {
    const backupInfo = await backupSystem.createEconomyBackup(description || undefined);
    
    await interaction.editReply({
        embeds: [{
            color: Colors.Gold,
            title: "✅ Backup da Economia Criado",
            fields: [
                {
                    name: "📁 Arquivo",
                    value: backupInfo.filename,
                    inline: true
                },
                {
                    name: "📊 Tamanho",
                    value: formatFileSize(backupInfo.size),
                    inline: true
                },
                {
                    name: "🕐 Data/Hora",
                    value: `<t:${Math.floor(new Date(backupInfo.timestamp).getTime() / 1000)}:F>`,
                    inline: false
                }
            ]
        }]
    });
}

async function handleCreateVoiceBackup(interaction: ChatInputCommandInteraction, description?: string | null) {
    const backupInfo = await backupSystem.createVoiceBackup(description || undefined);
    
    await interaction.editReply({
        embeds: [{
            color: Colors.Blue,
            title: "✅ Backup do Voice Tracking Criado",
            fields: [
                {
                    name: "📁 Arquivo",
                    value: backupInfo.filename,
                    inline: true
                },
                {
                    name: "📊 Tamanho",
                    value: formatFileSize(backupInfo.size),
                    inline: true
                },
                {
                    name: "🕐 Data/Hora",
                    value: `<t:${Math.floor(new Date(backupInfo.timestamp).getTime() / 1000)}:F>`,
                    inline: false
                }
            ]
        }]
    });
}

async function handleListBackups(interaction: ChatInputCommandInteraction) {
    const backups = await backupSystem.listBackups();
    
    if (backups.length === 0) {
        await interaction.editReply({
            embeds: [{
                color: Colors.Yellow,
                title: "📁 Lista de Backups",
                description: "Nenhum backup encontrado."
            }]
        });
        return;
    }

    // Mostrar apenas os 10 mais recentes
    const recentBackups = backups.slice(0, 10);
    
    const fields = recentBackups.map((backup) => {
        const typeEmoji = backup.type === 'full' ? '💾' : backup.type === 'economy' ? '💰' : '🎤';
        const date = new Date(backup.timestamp);
        
        return {
            name: `${typeEmoji} ${backup.filename}`,
            value: `📊 ${formatFileSize(backup.size)} | 🕐 <t:${Math.floor(date.getTime() / 1000)}:R>\n${backup.description ? `📝 ${backup.description}` : ''}`,
            inline: false
        };
    });

    await interaction.editReply({
        embeds: [{
            color: Colors.Blue,
            title: "📁 Lista de Backups",
            description: `Mostrando ${recentBackups.length} de ${backups.length} backups disponíveis`,
            fields: fields.slice(0, 10), // Discord limit
            footer: { text: "Use '/backup download arquivo:[nome]' para baixar um backup" }
        }]
    });
}

async function handleDownloadBackup(interaction: ChatInputCommandInteraction, filename: string) {
    const backupPath = join(process.cwd(), "data", "backups", filename);
    
    try {
        const fileContent = readFileSync(backupPath);
        const attachment = new AttachmentBuilder(fileContent, { name: filename });

        await interaction.editReply({
            embeds: [{
                color: Colors.Green,
                title: "⬇️ Download do Backup",
                description: `Arquivo: **${filename}**\nTamanho: **${formatFileSize(fileContent.length)}**`
            }],
            files: [attachment]
        });
    } catch (error) {
        throw new Error(`Erro ao baixar backup: ${error instanceof Error ? error.message : String(error)}`);
    }
}

async function handleRestoreBackup(interaction: ChatInputCommandInteraction, filename: string) {
    await backupSystem.restoreBackup(filename);
    
    await interaction.editReply({
        embeds: [{
            color: Colors.Orange,
            title: "🔄 Backup Restaurado",
            description: `O backup **${filename}** foi restaurado com sucesso!\n\n` +
                        "⚠️ **Importante:** Um backup dos dados atuais foi criado automaticamente antes da restauração.",
            footer: { text: "O bot pode precisar ser reiniciado para aplicar todas as mudanças" }
        }]
    });
}

async function handleDeleteBackup(interaction: ChatInputCommandInteraction, filename: string) {
    await backupSystem.deleteBackup(filename);
    
    await interaction.editReply({
        embeds: [{
            color: Colors.Green,
            title: "🗑️ Backup Removido",
            description: `O backup **${filename}** foi removido com sucesso.`
        }]
    });
}

async function handleCleanupBackups(interaction: ChatInputCommandInteraction, keepCount: number) {
    await backupSystem.cleanupOldBackups(keepCount);
    
    await interaction.editReply({
        embeds: [{
            color: Colors.Green,
            title: "🧹 Limpeza de Backups",
            description: `Limpeza concluída! Os **${keepCount}** backups mais recentes foram mantidos.\n\n` +
                        "Backups mais antigos foram removidos automaticamente."
        }]
    });
}

function formatFileSize(bytes: number): string {
    const units = ['B', 'KB', 'MB', 'GB'];
    let size = bytes;
    let unitIndex = 0;

    while (size >= 1024 && unitIndex < units.length - 1) {
        size /= 1024;
        unitIndex++;
    }

    return `${size.toFixed(1)} ${units[unitIndex]}`;
}
