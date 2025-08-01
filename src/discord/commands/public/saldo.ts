import { ApplicationCommandType, EmbedBuilder } from "discord.js";
import { createCommand } from "#base";
import { economyStore } from "../../../database/economy.js";

createCommand({
    name: "saldo",
    description: "🪙 Veja seu saldo e estatísticas de Arca Coins",
    type: ApplicationCommandType.ChatInput,
    async run(interaction) {
        const userId = interaction.user.id;
        const user = economyStore.getUser(userId);

        // Garantir que os valores não sejam null/undefined
        const balance = user.balance || 0;
        const totalEarned = user.totalEarned || 0;
        const totalSpent = user.totalSpent || 0;
        const messageCount = user.messageCount || 0;

        const embed = new EmbedBuilder()
            .setTitle("💰 Seu Saldo de Arca Coins")
            .setColor("#FFD700")
            .setThumbnail(interaction.user.displayAvatarURL())
            .addFields(
                {
                    name: "🪙 Saldo Atual",
                    value: `**${balance.toLocaleString("pt-BR")}** Arca Coins`,
                    inline: true
                },
                {
                    name: "📈 Total Ganho",
                    value: `${totalEarned.toLocaleString("pt-BR")} AC`,
                    inline: true
                },
                {
                    name: "📉 Total Gasto",
                    value: `${totalSpent.toLocaleString("pt-BR")} AC`,
                    inline: true
                },
                {
                    name: "💬 Mensagens Enviadas",
                    value: `${messageCount.toLocaleString("pt-BR")} mensagens`,
                    inline: true
                },
                {
                    name: "⏰ Próxima Recompensa",
                    value: `${10 - (messageCount % 10)} mensagens`,
                    inline: true
                },
                {
                    name: "🎁 Diário",
                    value: economyStore.canClaimDaily(userId) 
                        ? "✅ Disponível! Use `/diario`" 
                        : "⏳ Já coletado hoje",
                    inline: true
                }
            )
            .setFooter({ 
                text: "Use /economia para ver todos os comandos", 
                iconURL: interaction.client.user?.displayAvatarURL() 
            })
            .setTimestamp();

        await interaction.reply({ embeds: [embed], ephemeral: true });
    }
});
