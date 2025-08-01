import { ApplicationCommandOptionType, ApplicationCommandType, EmbedBuilder, PermissionFlagsBits } from "discord.js";
import { createCommand } from "#base";
import { economyStore } from "../../../database/economy.js";

createCommand({
    name: "remover",
    description: "👑 [ADMIN] Remover Arca Coins de um usuário",
    type: ApplicationCommandType.ChatInput,
    defaultMemberPermissions: PermissionFlagsBits.Administrator,
    options: [
        {
            name: "usuario",
            description: "Usuário que terá as moedas removidas",
            type: ApplicationCommandOptionType.User,
            required: true
        },
        {
            name: "quantidade",
            description: "Quantidade de Arca Coins para remover",
            type: ApplicationCommandOptionType.Integer,
            required: true,
            minValue: 1
        },
        {
            name: "motivo",
            description: "Motivo da remoção (opcional)",
            type: ApplicationCommandOptionType.String,
            required: false
        }
    ],
    async run(interaction) {
        const targetUser = interaction.options.getUser("usuario", true);
        const amount = interaction.options.getInteger("quantidade", true);
        const reason = interaction.options.getString("motivo") || "Remoção administrativa";

        if (targetUser.bot) {
            const embed = new EmbedBuilder()
                .setTitle("❌ Erro na Remoção")
                .setDescription("Não é possível remover moedas de bots!")
                .setColor("#FF6B6B");

            await interaction.reply({ embeds: [embed], ephemeral: true });
            return;
        }

        const userData = economyStore.getUser(targetUser.id);
        const actualRemoved = Math.min(amount, userData.balance);
        const updatedUser = economyStore.removeBalance(targetUser.id, amount);

        const embed = new EmbedBuilder()
            .setTitle("👑 Remoção Administrativa Realizada")
            .setDescription(`**${actualRemoved.toLocaleString("pt-BR")} Arca Coins** foram removidos da conta de ${targetUser.displayName}`)
            .setColor("#FF6B6B")
            .setThumbnail(targetUser.displayAvatarURL())
            .addFields(
                {
                    name: "💸 Quantidade Removida",
                    value: `${actualRemoved.toLocaleString("pt-BR")} AC`,
                    inline: true
                },
                {
                    name: "💳 Novo Saldo",
                    value: `${updatedUser.balance.toLocaleString("pt-BR")} AC`,
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
                }
            )
            .setFooter({ text: "Ação administrativa registrada" })
            .setTimestamp();

        if (actualRemoved < amount) {
            embed.addFields({
                name: "⚠️ Aviso",
                value: `O usuário tinha apenas ${userData.balance.toLocaleString("pt-BR")} AC, então foi removido o máximo possível.`,
                inline: false
            });
        }

        await interaction.reply({ embeds: [embed], ephemeral: true });

        // Notificar o usuário
        try {
            const userNotification = new EmbedBuilder()
                .setTitle("📉 Arca Coins Removidos")
                .setDescription(`Um administrador removeu **${actualRemoved.toLocaleString("pt-BR")} Arca Coins** da sua conta.`)
                .setColor("#FF6B6B")
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

            await targetUser.send({ embeds: [userNotification] });
        } catch {
            // Ignorar se não conseguir enviar DM
        }
    }
});
