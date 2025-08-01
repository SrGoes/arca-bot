import { ApplicationCommandType, ApplicationCommandOptionType, Colors, AttachmentBuilder, ChatInputCommandInteraction, PermissionFlagsBits } from "discord.js";
import { createCommand } from "#base";
import { dataMigration } from "#database";
import { writeFileSync, existsSync, unlinkSync } from "fs";
import { join } from "path";

createCommand({
    name: "migrar",
    description: "👑 [ADMIN] Migra dados de uma versão anterior do bot",
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
                    name: "📊 Analisar dados antigos",
                    value: "analyze"
                },
                {
                    name: "🔄 Executar migração",
                    value: "migrate"
                },
                {
                    name: "📁 Preparar arquivo exemplo",
                    value: "example"
                }
            ]
        },
        {
            name: "arquivo",
            description: "Arquivo JSON com os dados antigos (anexar ao comando)",
            type: ApplicationCommandOptionType.Attachment,
            required: false
        }
    ],
    async run(interaction: ChatInputCommandInteraction) {
        const action = interaction.options.getString("acao", true);
        const attachment = interaction.options.getAttachment("arquivo");

        await interaction.deferReply();

        try {
            switch (action) {
                case "example":
                    await handleCreateExample(interaction);
                    break;
                    
                case "analyze":
                    if (!attachment) {
                        await interaction.editReply({
                            embeds: [{
                                color: Colors.Red,
                                title: "❌ Erro",
                                description: "Você precisa anexar um arquivo JSON com os dados antigos para analisar."
                            }]
                        });
                        return;
                    }
                    await handleAnalyze(interaction, attachment);
                    break;
                    
                case "migrate":
                    if (!attachment) {
                        await interaction.editReply({
                            embeds: [{
                                color: Colors.Red,
                                title: "❌ Erro", 
                                description: "Você precisa anexar um arquivo JSON com os dados antigos para migrar."
                            }]
                        });
                        return;
                    }
                    await handleMigrate(interaction, attachment);
                    break;
            }
        } catch (error) {
            await interaction.editReply({
                embeds: [{
                    color: Colors.Red,
                    title: "❌ Erro na migração",
                    description: `Ocorreu um erro: ${error instanceof Error ? error.message : String(error)}`
                }]
            });
        }
    }
});

async function handleCreateExample(interaction: ChatInputCommandInteraction) {
    const exampleData = {
        user: {
            "306978576929128460": {
                created_at: "2025-07-28T14:42:41.149325+00:00",
                updated_at: "2025-07-31T12:11:19.547722+00:00",
                user_id: 306978576929128460,
                balance: 366652,
                total_earned: 366652,
                total_spent: 0,
                voice_time_minutes: 22,
                message_count: 0,
                daily_count: 0,
                last_daily: null,
                last_message_reward: null,
                achievements: [
                    "first_coins",
                    "hundred_club",
                    "thousand_club",
                    "rich_citizen",
                    "millionaire",
                    "first_call"
                ],
                preferences: {},
                transaction_history: []
            }
        }
    };

    const exampleJson = JSON.stringify(exampleData, null, 2);
    const buffer = Buffer.from(exampleJson, 'utf8');
    const attachment = new AttachmentBuilder(buffer, { name: 'exemplo_user_data.json' });

    await interaction.editReply({
        embeds: [{
            color: Colors.Blue,
            title: "📁 Arquivo de Exemplo Criado",
            description: "Use este arquivo como base para estruturar seus dados antigos.\n\n" +
                        "**Campos obrigatórios:**\n" +
                        "• `user_id` - ID do usuário\n" +
                        "• `balance` - Saldo atual\n" +
                        "• `total_earned` - Total ganho\n" +
                        "• `total_spent` - Total gasto\n" +
                        "• `message_count` - Contagem de mensagens\n" +
                        "• `last_daily` - Último daily (pode ser null)\n" +
                        "• `last_message_reward` - Última recompensa de mensagem",
            footer: { text: "Modifique este arquivo com seus dados reais e anexe novamente" }
        }],
        files: [attachment]
    });
}

async function handleAnalyze(interaction: ChatInputCommandInteraction, attachment: any) {
    try {
        // Download do arquivo anexado
        const response = await fetch(attachment.url);
        const fileContent = await response.text();
        
        // Salvar temporariamente
        const tempPath = join(process.cwd(), "temp_migration_data.json");
        writeFileSync(tempPath, fileContent);

        // Analisar dados
        await dataMigration.analyzeOldData(tempPath);

        // Parse para estatísticas
        const oldData = JSON.parse(fileContent);
        const users = Object.values(oldData.user || {}) as any[];
        
        const totalUsers = users.length;
        const totalBalance = users.reduce((sum: number, user: any) => sum + (user.balance || 0), 0);
        const totalEarned = users.reduce((sum: number, user: any) => sum + (user.total_earned || 0), 0);
        const usersWithDaily = users.filter((user: any) => user.last_daily).length;

        await interaction.editReply({
            embeds: [{
                color: Colors.Blue,
                title: "📊 Análise dos Dados Antigos",
                fields: [
                    {
                        name: "👥 Usuários",
                        value: `${totalUsers.toLocaleString()}`,
                        inline: true
                    },
                    {
                        name: "💰 Saldo Total",
                        value: `${totalBalance.toLocaleString()} moedas`,
                        inline: true
                    },
                    {
                        name: "📈 Total Ganho",
                        value: `${totalEarned.toLocaleString()} moedas`,
                        inline: true
                    },
                    {
                        name: "🗓️ Com Daily Ativo",
                        value: `${usersWithDaily} usuários`,
                        inline: true
                    },
                    {
                        name: "📊 Média de Saldo",
                        value: `${Math.round(totalBalance / totalUsers).toLocaleString()} moedas`,
                        inline: true
                    }
                ],
                footer: { text: "Use '/migrar migrate' com este arquivo para executar a migração" }
            }]
        });

        // Limpar arquivo temporário
        if (existsSync(tempPath)) {
            unlinkSync(tempPath);
        }

    } catch (error) {
        throw new Error(`Erro ao analisar arquivo: ${error instanceof Error ? error.message : String(error)}`);
    }
}

async function handleMigrate(interaction: ChatInputCommandInteraction, attachment: any) {
    try {
        // Download do arquivo anexado
        const response = await fetch(attachment.url);
        const fileContent = await response.text();
        
        // Salvar para migração
        const migrationPath = join(process.cwd(), "migration_data.json");
        writeFileSync(migrationPath, fileContent);

        // Executar migração
        dataMigration.setOldDataPath(migrationPath);
        await dataMigration.fullMigration();

        await interaction.editReply({
            embeds: [{
                color: Colors.Green,
                title: "✅ Migração Concluída",
                description: "Os dados foram migrados com sucesso!\n\n" +
                            "• Backup dos dados atuais foi criado\n" +
                            "• Dados antigos foram importados\n" +
                            "• Conflitos foram resolvidos automaticamente",
                footer: { text: "Verifique os logs do bot para mais detalhes" }
            }]
        });

        // Limpar arquivo temporário
        if (existsSync(migrationPath)) {
            unlinkSync(migrationPath);
        }

    } catch (error) {
        throw new Error(`Erro durante migração: ${error instanceof Error ? error.message : String(error)}`);
    }
}
