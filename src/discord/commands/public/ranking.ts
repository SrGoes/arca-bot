import { ApplicationCommandType, EmbedBuilder } from "discord.js";
import { createCommand } from "#base";
import { economyStore } from "../../../database/economy.js";

createCommand({
    name: "ranking",
    description: "🏆 Veja o ranking dos usuários mais ricos em Arca Coins",
    type: ApplicationCommandType.ChatInput,
    async run(interaction) {
        const leaderboard = economyStore.getLeaderboard(10);

        if (leaderboard.length === 0) {
            const embed = new EmbedBuilder()
                .setTitle("🏆 Ranking de Arca Coins")
                .setDescription("Nenhum usuário encontrado no sistema ainda!")
                .setColor("#FFD700");

            await interaction.reply({ embeds: [embed] });
            return;
        }

        const userRankings = await Promise.all(
            leaderboard.map(async (userData, index) => {
                const balance = userData.balance || 0; // Proteção contra null
                try {
                    const user = await interaction.client.users.fetch(userData.userId);
                    const medal = index === 0 ? "🥇" : index === 1 ? "🥈" : index === 2 ? "🥉" : "🏅";
                    return `${medal} **${index + 1}.** ${user.displayName}\n💰 ${balance.toLocaleString("pt-BR")} AC`;
                } catch {
                    return `🏅 **${index + 1}.** Usuário Desconhecido\n💰 ${balance.toLocaleString("pt-BR")} AC`;
                }
            })
        );

        const embed = new EmbedBuilder()
            .setTitle("🏆 Ranking de Arca Coins")
            .setDescription("Os usuários mais ricos do servidor!")
            .setColor("#FFD700")
            .addFields({
                name: "🎖️ Top 10",
                value: userRankings.join("\n\n"),
                inline: false
            })
            .setFooter({ 
                text: "Continue coletando moedas para subir no ranking!", 
                iconURL: interaction.client.user?.displayAvatarURL() 
            })
            .setTimestamp();

        // Mostrar posição do usuário atual se não estiver no top 10
        const currentUser = economyStore.getUser(interaction.user.id);
        const currentUserBalance = currentUser.balance || 0; // Proteção contra null
        const allUsers = economyStore.getLeaderboard(1000); // Pegar mais usuários para encontrar a posição
        const userPosition = allUsers.findIndex(u => u.userId === interaction.user.id);

        if (userPosition >= 10) {
            embed.addFields({
                name: "📍 Sua Posição",
                value: `**${userPosition + 1}º lugar** - ${currentUserBalance.toLocaleString("pt-BR")} AC`,
                inline: false
            });
        }

        await interaction.reply({ embeds: [embed] });
    }
});
