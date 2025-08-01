import { ApplicationCommandOptionType, ApplicationCommandType, EmbedBuilder } from "discord.js";
import { createCommand } from "#base";
import { economyStore } from "../../../database/economy.js";

createCommand({
    name: "transferir",
    description: "💸 Transfira Arca Coins para outro usuário",
    type: ApplicationCommandType.ChatInput,
    options: [
        {
            name: "usuario",
            description: "Usuário que receberá as moedas",
            type: ApplicationCommandOptionType.User,
            required: true
        },
        {
            name: "quantidade",
            description: "Quantidade de Arca Coins para transferir",
            type: ApplicationCommandOptionType.Integer,
            required: true,
            minValue: 1
        }
    ],
    async run(interaction) {
        const targetUser = interaction.options.getUser("usuario", true);
        const amount = interaction.options.getInteger("quantidade", true);
        const senderId = interaction.user.id;

        // Verificações básicas
        if (targetUser.id === senderId) {
            const embed = new EmbedBuilder()
                .setTitle("❌ Erro na Transferência")
                .setDescription("Você não pode transferir moedas para si mesmo!")
                .setColor("#FF6B6B");

            await interaction.reply({ embeds: [embed], ephemeral: true });
            return;
        }

        if (targetUser.bot) {
            const embed = new EmbedBuilder()
                .setTitle("❌ Erro na Transferência")
                .setDescription("Você não pode transferir moedas para bots!")
                .setColor("#FF6B6B");

            await interaction.reply({ embeds: [embed], ephemeral: true });
            return;
        }

        const senderData = economyStore.getUser(senderId);

        if (senderData.balance < amount) {
            const embed = new EmbedBuilder()
                .setTitle("💳 Saldo Insuficiente")
                .setDescription(`Você não tem Arca Coins suficientes para esta transferência.`)
                .setColor("#FF6B6B")
                .addFields(
                    {
                        name: "💰 Seu Saldo",
                        value: `${senderData.balance.toLocaleString("pt-BR")} AC`,
                        inline: true
                    },
                    {
                        name: "💸 Tentativa de Transferência",
                        value: `${amount.toLocaleString("pt-BR")} AC`,
                        inline: true
                    }
                );

            await interaction.reply({ embeds: [embed], ephemeral: true });
            return;
        }

        // Realizar a transferência
        const updatedSender = economyStore.removeBalance(senderId, amount);
        const updatedReceiver = economyStore.addBalance(targetUser.id, amount);

        const embed = new EmbedBuilder()
            .setTitle("✅ Transferência Realizada!")
            .setDescription(`Transferência de **${amount.toLocaleString("pt-BR")} Arca Coins** realizada com sucesso!`)
            .setColor("#00FF7F")
            .addFields(
                {
                    name: "💸 Remetente",
                    value: `${interaction.user.displayName}\n**Novo saldo:** ${updatedSender.balance.toLocaleString("pt-BR")} AC`,
                    inline: true
                },
                {
                    name: "💰 Destinatário",
                    value: `${targetUser.displayName}\n**Novo saldo:** ${updatedReceiver.balance.toLocaleString("pt-BR")} AC`,
                    inline: true
                }
            )
            .setFooter({ text: "Obrigado por usar o sistema de economia!" })
            .setTimestamp();

        await interaction.reply({ embeds: [embed] });

        // Enviar notificação para o usuário que recebeu (se possível)
        try {
            const notificationEmbed = new EmbedBuilder()
                .setTitle("💰 Você Recebeu Arca Coins!")
                .setDescription(`**${interaction.user.displayName}** transferiu **${amount.toLocaleString("pt-BR")} Arca Coins** para você!`)
                .setColor("#00FF7F")
                .addFields({
                    name: "💳 Seu Novo Saldo",
                    value: `${updatedReceiver.balance.toLocaleString("pt-BR")} AC`,
                    inline: true
                })
                .setThumbnail(interaction.user.displayAvatarURL())
                .setTimestamp();

            await targetUser.send({ embeds: [notificationEmbed] });
        } catch {
            // Ignorar se não conseguir enviar DM
        }
    }
});
