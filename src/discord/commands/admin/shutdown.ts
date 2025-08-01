import { ApplicationCommandType, Colors, ChatInputCommandInteraction, PermissionFlagsBits } from "discord.js";
import { createCommand } from "#base";
import { gracefulShutdown } from "#settings";

createCommand({
    name: "shutdown",
    description: "👑 [ADMIN] Desliga o bot de forma segura",
    type: ApplicationCommandType.ChatInput,
    defaultMemberPermissions: PermissionFlagsBits.Administrator,
    dmPermission: false,
    async run(interaction: ChatInputCommandInteraction) {
        const embed = {
            color: Colors.Orange,
            description: `${interaction.client.user} está sendo desligado de forma segura...`,
            timestamp: new Date().toISOString()
        };

        await interaction.reply({ embeds: [embed] });

        // Aguarda um pouco para garantir que a resposta seja enviada
        setTimeout(() => {
            gracefulShutdown(interaction.client, "Manual shutdown requested by admin");
        }, 1000);
    }
});
