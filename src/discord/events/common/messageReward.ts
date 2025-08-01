import { createEvent } from "#base";
import { EmbedBuilder, Events, Message } from "discord.js";
import { economyStore } from "#database";
import { EconomyConfig } from "#settings";

createEvent({
    name: "messageReward",
    event: Events.MessageCreate,
    async run(message: Message) {
        // Ignorar mensagens de bots
        if (message.author.bot) return;
        
        // Ignorar mensagens em DM
        if (!message.guild) return;
        
        // Ignorar mensagens que começam com prefixos de comando
        if (message.content.startsWith("/") || message.content.startsWith("!")) return;
        
        // Ignorar mensagens muito curtas (anti-spam)
        if (message.content.length < EconomyConfig.messages.minMessageLength) return;
        
        const userId = message.author.id;
        const reward = economyStore.addMessage(userId);
        
        if (reward.gained) {
            const embed = new EmbedBuilder()
                .setTitle("💰 Recompensa por Atividade!")
                .setDescription(`**${message.author.displayName}**, você ganhou **${reward.amount} Arca Coins** por ser ativo no chat!`)
                .addFields({
                    name: "💳 Novo Saldo",
                    value: `${reward.newBalance.toLocaleString("pt-BR")} Arca Coins`,
                    inline: true
                })
                .setColor("#4CAF50")
                .setThumbnail(message.author.displayAvatarURL())
                .setFooter({ text: "Continue participando para ganhar mais moedas!" })
                .setTimestamp();
            
            // Verificar se o canal pode receber mensagens
            if (message.channel.isTextBased() && "send" in message.channel) {
                // Enviar mensagem temporária
                const rewardMessage = await message.channel.send({ embeds: [embed] });
                
                // Deletar a mensagem de recompensa após tempo configurado
                setTimeout(() => {
                    rewardMessage.delete().catch(() => {});
                }, EconomyConfig.general.rewardMessageDuration * 1000);
            }
        }
    }
});
