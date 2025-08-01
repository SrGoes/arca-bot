import { ApplicationCommandType, EmbedBuilder } from "discord.js";
import { createCommand } from "#base";
import { economyStore } from "#database";
import { calculateDailyReward } from "#settings";

createCommand({
    name: "diario",
    description: "🎁 Colete sua recompensa diária de Arca Coins",
    type: ApplicationCommandType.ChatInput,
    async run(interaction) {
        const userId = interaction.user.id;

        if (!economyStore.canClaimDaily(userId)) {
            const user = economyStore.getUser(userId);
            const lastDaily = new Date(user.lastDaily!);
            const tomorrow = new Date(lastDaily);
            tomorrow.setDate(tomorrow.getDate() + 1);
            tomorrow.setHours(0, 0, 0, 0);

            const timeLeft = tomorrow.getTime() - Date.now();
            const hoursLeft = Math.floor(timeLeft / (1000 * 60 * 60));
            const minutesLeft = Math.floor((timeLeft % (1000 * 60 * 60)) / (1000 * 60));

            const embed = new EmbedBuilder()
                .setTitle("⏰ Recompensa Diária Já Coletada")
                .setDescription(`Você já coletou sua recompensa diária hoje!`)
                .setColor("#FF6B6B")
                .addFields({
                    name: "⏳ Próxima Recompensa",
                    value: `Em **${hoursLeft}h ${minutesLeft}m**`,
                    inline: false
                })
                .setFooter({ text: "A recompensa reseta à meia-noite" });

            await interaction.reply({ embeds: [embed], ephemeral: true });
            return;
        }

        // Usar configurações para calcular recompensa diária
        const dailyAmount = calculateDailyReward();
        const updatedUser = economyStore.claimDaily(userId, dailyAmount);

        const embed = new EmbedBuilder()
            .setTitle("🎁 Recompensa Diária Coletada!")
            .setDescription(`Parabéns! Você coletou sua recompensa diária!`)
            .setColor("#00FF7F")
            .setThumbnail(interaction.user.displayAvatarURL())
            .addFields(
                {
                    name: "💰 Recompensa Recebida",
                    value: `**${dailyAmount.toLocaleString("pt-BR")} Arca Coins**`,
                    inline: true
                },
                {
                    name: "💳 Novo Saldo",
                    value: `${updatedUser.balance.toLocaleString("pt-BR")} AC`,
                    inline: true
                }
            )
            .setFooter({ text: "Volte amanhã para mais recompensas!" })
            .setTimestamp();

        await interaction.reply({ embeds: [embed], ephemeral: true });
    }
});
