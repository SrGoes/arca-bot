import { ApplicationCommandType, EmbedBuilder, PermissionFlagsBits, GuildMember } from "discord.js";
import { createCommand } from "#base";
import { economyStore } from "#database";
import { isUserAdmin } from "#settings";

createCommand({
    name: "ranking",
    description: "👑 [ADMIN] Ver ranking completo de usuários com Arca Coins",
    type: ApplicationCommandType.ChatInput,
    async run(interaction) {
        // Verificar se o usuário é admin usando nossa função customizada
        const member = interaction.member as GuildMember;
        const userRoles = member.roles.cache.map(role => role.id);
        const hasAdminPermission = member.permissions.has(PermissionFlagsBits.Administrator);
        
        if (!isUserAdmin(interaction.user.id, userRoles, hasAdminPermission)) {
            const embed = new EmbedBuilder()
                .setTitle("❌ Acesso Negado")
                .setDescription("Você não tem permissão para usar este comando!")
                .setColor("#FF6B6B");

            await interaction.reply({ embeds: [embed], ephemeral: true });
            return;
        }
        const leaderboard = economyStore.getLeaderboard(0); // 0 = todos os usuários sem limite

        if (leaderboard.length === 0) {
            const embed = new EmbedBuilder()
                .setTitle("📊 Ranking de Arca Coins")
                .setDescription("Nenhum usuário encontrado no sistema de economia.")
                .setColor("#FFD700");

            await interaction.reply({ embeds: [embed], ephemeral: true });
            return;
        }

        const rankingText = await Promise.all(
            leaderboard.map(async (user, index) => {
                const balance = user.balance || 0; // Proteção contra null
                try {
                    const discordUser = await interaction.client.users.fetch(user.userId);
                    const medal = index === 0 ? "🥇" : index === 1 ? "🥈" : index === 2 ? "🥉" : `${index + 1}.`;
                    return `${medal} **${discordUser.displayName}** - ${balance.toLocaleString("pt-BR")} AC`;
                } catch {
                    const medal = index === 0 ? "🥇" : index === 1 ? "🥈" : index === 2 ? "🥉" : `${index + 1}.`;
                    return `${medal} **Usuário Desconhecido** - ${balance.toLocaleString("pt-BR")} AC`;
                }
            })
        );

        const totalUsers = leaderboard.length;
        const totalCoins = leaderboard.reduce((sum, user) => sum + (user.balance || 0), 0); // Proteção contra null

        const embed = new EmbedBuilder()
            .setTitle("📊 Ranking Completo de Arca Coins")
            .setDescription(`**Todos os usuários com Arca Coins:**\n\n${rankingText.join("\n")}`)
            .addFields(
                {
                    name: "📈 Estatísticas Gerais",
                    value: [
                        `👥 **Total de Usuários:** ${totalUsers}`,
                        `💰 **Total de Moedas:** ${totalCoins.toLocaleString("pt-BR")} AC`,
                        `📊 **Média Geral:** ${totalUsers > 0 ? Math.round(totalCoins / totalUsers).toLocaleString("pt-BR") : 0} AC`
                    ].join("\n"),
                    inline: false
                }
            )
            .setColor("#FFD700")
            .setFooter({ 
                text: `Solicitado por ${interaction.user.displayName} • Admin Only`, 
                iconURL: interaction.user.displayAvatarURL() 
            })
            .setTimestamp();

        await interaction.reply({ embeds: [embed], ephemeral: true });
    }
});
