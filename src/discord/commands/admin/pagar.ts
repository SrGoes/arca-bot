import { ApplicationCommandOptionType, ApplicationCommandType, EmbedBuilder, PermissionFlagsBits } from "discord.js";
import { createCommand } from "#base";
import { economyStore } from "../../../database/economy.js";

createCommand({
    name: "pagar",
    description: "👑 [ADMIN] Dar Arca Coins para um usuário",
    type: ApplicationCommandType.ChatInput,
    defaultMemberPermissions: PermissionFlagsBits.Administrator,
    options: [
        {
            name: "usuario",
            description: "Usuário que receberá as moedas",
            type: ApplicationCommandOptionType.User,
            required: true
        },
        {
            name: "quantidade",
            description: "Quantidade de Arca Coins para dar",
            type: ApplicationCommandOptionType.Integer,
            required: true,
            minValue: 1
        },
        {
            name: "motivo",
            description: "Motivo do pagamento (opcional)",
            type: ApplicationCommandOptionType.String,
            required: false
        }
    ],
    async run(interaction) {
        const targetUser = interaction.options.getUser("usuario", true);
        const amount = interaction.options.getInteger("quantidade", true);
        const reason = interaction.options.getString("motivo") || "Pagamento administrativo";

        if (targetUser.bot) {
            const embed = new EmbedBuilder()
                .setTitle("❌ Erro no Pagamento")
                .setDescription("Não é possível dar moedas para bots!")
                .setColor("#FF6B6B");

            await interaction.reply({ embeds: [embed], ephemeral: true });
            return;
        }

        const updatedUser = economyStore.addBalance(targetUser.id, amount);

        const embed = new EmbedBuilder()
            .setTitle("👑 Pagamento Administrativo Realizado")
            .setDescription(`**${amount.toLocaleString("pt-BR")} Arca Coins** foram adicionados à conta de ${targetUser.displayName}`)
            .setColor("#FFD700")
            .setThumbnail(targetUser.displayAvatarURL())
            .addFields(
                {
                    name: "💰 Quantidade Adicionada",
                    value: `${amount.toLocaleString("pt-BR")} AC`,
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

        await interaction.reply({ embeds: [embed], ephemeral: true });

        // Notificar o usuário
        try {
            const userNotification = new EmbedBuilder()
                .setTitle("🎉 Você Recebeu Arca Coins!")
                .setDescription(`Um administrador adicionou **${amount.toLocaleString("pt-BR")} Arca Coins** à sua conta!`)
                .setColor("#FFD700")
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
