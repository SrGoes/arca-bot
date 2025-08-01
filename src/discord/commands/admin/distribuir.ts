import { ApplicationCommandOptionType, ApplicationCommandType, EmbedBuilder, PermissionFlagsBits, VoiceChannel } from "discord.js";
import { createCommand } from "#base";
import { economyStore } from "../../../database/economy.js";

createCommand({
    name: "distribuir",
    description: "👑 [ADMIN] Distribuir Arca Coins para todos os usuários em uma call",
    type: ApplicationCommandType.ChatInput,
    defaultMemberPermissions: PermissionFlagsBits.Administrator,
    options: [
        {
            name: "canal",
            description: "Canal de voz para distribuir as moedas",
            type: ApplicationCommandOptionType.Channel,
            required: true
        },
        {
            name: "quantidade",
            description: "Quantidade de Arca Coins para cada usuário",
            type: ApplicationCommandOptionType.Integer,
            required: true,
            minValue: 1
        },
        {
            name: "motivo",
            description: "Motivo da distribuição (opcional)",
            type: ApplicationCommandOptionType.String,
            required: false
        }
    ],
    async run(interaction) {
        const channel = interaction.options.getChannel("canal", true);
        const amount = interaction.options.getInteger("quantidade", true);
        const reason = interaction.options.getString("motivo") || "Distribuição administrativa";

        // Verificar se é um canal de voz
        if (!channel.isVoiceBased()) {
            const embed = new EmbedBuilder()
                .setTitle("❌ Erro na Distribuição")
                .setDescription("O canal selecionado deve ser um canal de voz!")
                .setColor("#FF6B6B");

            await interaction.reply({ embeds: [embed], ephemeral: true });
            return;
        }

        const voiceChannel = channel as VoiceChannel;
        const members = voiceChannel.members;

        if (members.size === 0) {
            const embed = new EmbedBuilder()
                .setTitle("❌ Canal Vazio")
                .setDescription("Não há usuários no canal de voz selecionado!")
                .setColor("#FF6B6B");

            await interaction.reply({ embeds: [embed], ephemeral: true });
            return;
        }

        // Filtrar apenas usuários (não bots)
        const users = members.filter(member => !member.user.bot);

        if (users.size === 0) {
            const embed = new EmbedBuilder()
                .setTitle("❌ Apenas Bots")
                .setDescription("O canal selecionado contém apenas bots!")
                .setColor("#FF6B6B");

            await interaction.reply({ embeds: [embed], ephemeral: true });
            return;
        }

        await interaction.deferReply();

        // Distribuir moedas para todos os usuários
        const updatedUsers: Array<{ name: string, newBalance: number }> = [];
        
        for (const [, member] of users) {
            const updatedUser = economyStore.addBalance(member.id, amount);
            updatedUsers.push({
                name: member.displayName,
                newBalance: updatedUser.balance
            });

            // Notificar cada usuário
            try {
                const userNotification = new EmbedBuilder()
                    .setTitle("🎉 Distribuição de Arca Coins!")
                    .setDescription(`Você recebeu **${amount.toLocaleString("pt-BR")} Arca Coins** na distribuição do canal ${voiceChannel.name}!`)
                    .setColor("#00FF7F")
                    .addFields(
                        {
                            name: "💳 Seu Novo Saldo",
                            value: `${updatedUser.balance.toLocaleString("pt-BR")} AC`,
                            inline: true
                        },
                        {
                            name: "📝 Motivo",
                            value: reason,
                            inline: false
                        }
                    )
                    .setTimestamp();

                await member.send({ embeds: [userNotification] });
            } catch {
                // Ignorar se não conseguir enviar DM
            }
        }

        const totalDistributed = amount * users.size;
        
        const embed = new EmbedBuilder()
            .setTitle("👑 Distribuição Realizada com Sucesso!")
            .setDescription(`**${amount.toLocaleString("pt-BR")} Arca Coins** foram distribuídos para **${users.size}** usuários no canal ${voiceChannel.name}`)
            .setColor("#00FF7F")
            .addFields(
                {
                    name: "💰 Por Usuário",
                    value: `${amount.toLocaleString("pt-BR")} AC`,
                    inline: true
                },
                {
                    name: "👥 Total de Usuários",
                    value: `${users.size} usuários`,
                    inline: true
                },
                {
                    name: "💎 Total Distribuído",
                    value: `${totalDistributed.toLocaleString("pt-BR")} AC`,
                    inline: true
                },
                {
                    name: "📝 Motivo",
                    value: reason,
                    inline: false
                },
                {
                    name: "👤 Administrador",
                    value: interaction.user.displayName,
                    inline: true
                },
                {
                    name: "🔊 Canal",
                    value: voiceChannel.name,
                    inline: true
                }
            )
            .setFooter({ text: "Todos os usuários foram notificados via DM" })
            .setTimestamp();

        // Adicionar lista de usuários se não for muito grande
        if (updatedUsers.length <= 10) {
            const usersList = updatedUsers
                .map(user => `• ${user.name}: ${user.newBalance.toLocaleString("pt-BR")} AC`)
                .join("\n");
            
            embed.addFields({
                name: "👥 Usuários Beneficiados",
                value: usersList,
                inline: false
            });
        } else {
            embed.addFields({
                name: "👥 Usuários Beneficiados",
                value: `Lista muito grande para exibir (${updatedUsers.length} usuários)`,
                inline: false
            });
        }

        await interaction.editReply({ embeds: [embed] });
    }
});
