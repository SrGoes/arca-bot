import { ApplicationCommandType, EmbedBuilder } from "discord.js";
import { createCommand } from "#base";

createCommand({
    name: "economia",
    description: "📋 Veja todos os comandos do sistema de economia",
    type: ApplicationCommandType.ChatInput,
    async run(interaction) {
        const embed = new EmbedBuilder()
            .setTitle("🏦 Sistema de Economia - Arca Coins")
            .setDescription("Bem-vindo ao sistema de economia do servidor! Aqui você pode ganhar, gastar e gerenciar suas **Arca Coins** (AC).")
            .setColor("#4169E1")
            .setThumbnail(interaction.client.user?.displayAvatarURL())
            .addFields(
                {
                    name: "🎁 **Comando Diário**",
                    value: "Use `/diario` para ganhar Arca Coins por dia!\n*Reseta à meia-noite*",
                    inline: false
                },
                {
                    name: "📋 **Comandos Disponíveis**",
                    value: [
                        "`/saldo` - Ver seu saldo e estatísticas",
                        "`/diario` - Reclamar recompensa diária",
                        "`/transferir` - Transferir moedas para outros",
                        "`/economia` - Mostrar esta ajuda"
                    ].join("\n"),
                    inline: false
                },
                {
                    name: "👑 **Comandos Admin**",
                    value: [
                        "`/pagar` - Dar moedas a um usuário",
                        "`/remover` - Remover moedas de um usuário",
                        "`/distribuir` - Distribuir moedas para call inteira"
                    ].join("\n"),
                    inline: false
                },
                {
                    name: "💡 **Dicas**",
                    value: [
                        "• Colete sua recompensa diária todos os dias",
                        "• Participe das atividades do servidor",
                        "• Mantenha-se ativo para ganhar bônus"
                    ].join("\n"),
                    inline: false
                }
            )
            .setFooter({ 
                text: "Sistema desenvolvido para o servidor", 
                iconURL: interaction.guild?.iconURL() || undefined 
            })
            .setTimestamp();

        await interaction.reply({ embeds: [embed], ephemeral: true });
    }
});
