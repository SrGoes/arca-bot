import { 
    EmbedBuilder, 
    ActionRowBuilder, 
    ButtonBuilder, 
    ButtonStyle
} from "discord.js";
import { createResponder, ResponderType } from "#base";
import { raffleStore, economyStore } from "#database";
import { RaffleConfig } from "#settings";
import { z } from "zod";

const raffleSchema = z.object({
    raffleId: z.string(),
});

// Função auxiliar para atualizar a mensagem do sorteio
async function updateRaffleMessage(raffle: any, client: any, winner?: any) {
    try {
        const channel = await client.channels.fetch(raffle.channelId);
        if (!channel || !channel.isTextBased()) return;

        const message = await channel.messages.fetch(raffle.messageId);
        if (!message) return;

        const participants = raffle.participants;

        let embed: EmbedBuilder;
        let components: ActionRowBuilder<ButtonBuilder>[] = [];

        if (winner) {
            // Sorteio finalizado
            embed = new EmbedBuilder()
                .setTitle(`🎉 ${raffle.title}`)
                .setDescription("**SORTEIO FINALIZADO!**")
                .setColor(RaffleConfig.colors.finished)
                .addFields(
                    { 
                        name: "🏆 Vencedor", 
                        value: `<@${winner.userId}>`, 
                        inline: false 
                    },
                    { 
                        name: "👥 Participantes", 
                        value: `${participants.length} pessoa${participants.length !== 1 ? 's' : ''}`, 
                        inline: true 
                    }
                );
        } else if (raffle.status === 'cancelled') {
            // Sorteio cancelado
            embed = new EmbedBuilder()
                .setTitle(`❌ ${raffle.title}`)
                .setDescription("**SORTEIO CANCELADO**")
                .setColor(RaffleConfig.colors.cancelled)
                .addFields({ 
                    name: "🔄 Status", 
                    value: "Todos os participantes foram reembolsados.", 
                    inline: false 
                });
        } else {
            // Sorteio ativo
            embed = new EmbedBuilder()
                .setTitle(`🎁 ${raffle.title}`)
                .setDescription(`💰 **Primeiro ticket:** ${raffle.firstTicketPrice} Arca Coins`)
                .setColor(RaffleConfig.colors.active)
                .addFields({ 
                    name: "👥 Participantes", 
                    value: `${participants.length} pessoa${participants.length !== 1 ? 's' : ''}`, 
                    inline: true 
                });

            const actionRow = new ActionRowBuilder<ButtonBuilder>()
                .addComponents(
                    new ButtonBuilder()
                        .setCustomId(`raffle_buy/${raffle.id}`)
                        .setLabel("🎫 Comprar Ticket")
                        .setStyle(ButtonStyle.Success),
                    new ButtonBuilder()
                        .setCustomId(`raffle_info/${raffle.id}`)
                        .setLabel("ℹ️ Meus Tickets")
                        .setStyle(ButtonStyle.Secondary)
                );

            components = [actionRow];
        }

        await message.edit({ embeds: [embed], components });
    } catch (error) {
        console.error("Erro ao atualizar mensagem do sorteio:", error);
    }
}

// Responder para comprar ticket
createResponder({
    customId: "raffle_buy/:raffleId",
    types: [ResponderType.Button],
    parse: raffleSchema.parse,
    async run(interaction, { raffleId }) {
        const user = interaction.user;
        const raffle = raffleStore.getRaffle(raffleId);

        if (!raffle) {
            await interaction.reply({ 
                content: "❌ Sorteio não encontrado!", 
                ephemeral: true 
            });
            return;
        }

        if (raffle.status !== 'active') {
            await interaction.reply({ 
                content: "❌ Este sorteio não está mais ativo!", 
                ephemeral: true 
            });
            return;
        }

        const balance = economyStore.getUser(user.id).balance;
        const userTickets = raffleStore.getParticipant(raffleId, user.id)?.ticketCount || 0;
        const ticketPrice = Math.round(raffle.firstTicketPrice * Math.pow(1.1, userTickets));

        if (balance < ticketPrice) {
            await interaction.reply({ 
                content: `❌ Saldo insuficiente! Você precisa de ${ticketPrice} Arca Coins para comprar o próximo ticket.`, 
                ephemeral: true 
            });
            return;
        }

        // Processar compra
        economyStore.removeBalance(user.id, ticketPrice);
        raffleStore.addParticipant(raffleId, user.id, 1, ticketPrice);

        // Atualizar embed principal
        await updateRaffleMessage(raffle, interaction.client);

        // Confirmação
        const confirmEmbed = new EmbedBuilder()
            .setTitle("✅ Ticket Comprado!")
            .setDescription(`Você comprou um ticket do sorteio **${raffle.title}**`)
            .setColor(RaffleConfig.colors.active)
            .addFields(
                { 
                    name: "💰 Valor Pago", 
                    value: `${ticketPrice} Arca Coins`, 
                    inline: true 
                },
                { 
                    name: "💳 Saldo Restante", 
                    value: `${economyStore.getUser(user.id).balance} Arca Coins`, 
                    inline: true 
                },
                { 
                    name: "🎫 Seus Tickets", 
                    value: `${raffleStore.getParticipant(raffleId, user.id)?.ticketCount || 0} ticket${(raffleStore.getParticipant(raffleId, user.id)?.ticketCount || 0) !== 1 ? 's' : ''}`, 
                    inline: true 
                }
            );

        await interaction.reply({ embeds: [confirmEmbed], ephemeral: true });
    }
});

// Responder para ver informações dos tickets do usuário
createResponder({
    customId: "raffle_info/:raffleId",
    types: [ResponderType.Button],
    parse: raffleSchema.parse,
    async run(interaction, { raffleId }) {
        const user = interaction.user;
        const raffle = raffleStore.getRaffle(raffleId);

        if (!raffle) {
            await interaction.reply({ 
                content: "❌ Sorteio não encontrado!", 
                ephemeral: true 
            });
            return;
        }

        const userTickets = raffleStore.getParticipant(raffleId, user.id)?.ticketCount || 0;

        if (userTickets === 0) {
            const nextTicketPrice = raffle.firstTicketPrice;
            const notParticipatingEmbed = new EmbedBuilder()
                .setTitle("ℹ️ Informações do Sorteio")
                .setDescription(`**${raffle.title}**`)
                .setColor(RaffleConfig.colors.active)
                .addFields(
                    { 
                        name: "🎫 Seus Tickets", 
                        value: "Você ainda não tem tickets neste sorteio", 
                        inline: false 
                    },
                    { 
                        name: "💰 Próximo Ticket", 
                        value: `${nextTicketPrice} Arca Coins`, 
                        inline: true 
                    },
                    { 
                        name: "💳 Seu Saldo", 
                        value: `${economyStore.getUser(user.id).balance} Arca Coins`, 
                        inline: true 
                    }
                );

            await interaction.reply({ embeds: [notParticipatingEmbed], ephemeral: true });
        } else {
            const nextTicketPrice = Math.round(raffle.firstTicketPrice * Math.pow(1.1, userTickets));
            const participatingEmbed = new EmbedBuilder()
                .setTitle("ℹ️ Seus Tickets")
                .setDescription(`**${raffle.title}**`)
                .setColor(RaffleConfig.colors.active)
                .addFields(
                    { 
                        name: "🎫 Seus Tickets", 
                        value: `${userTickets} ticket${userTickets !== 1 ? 's' : ''}`, 
                        inline: true 
                    },
                    { 
                        name: "💰 Próximo Ticket", 
                        value: `${nextTicketPrice} Arca Coins`, 
                        inline: true 
                    },
                    { 
                        name: "💳 Seu Saldo", 
                        value: `${economyStore.getUser(user.id).balance} Arca Coins`, 
                        inline: true 
                    }
                );

            await interaction.reply({ embeds: [participatingEmbed], ephemeral: true });
        }
    }
});

// Responder para sortear (admin)
createResponder({
    customId: "raffle_draw/:raffleId",
    types: [ResponderType.Button],
    parse: raffleSchema.parse,
    async run(interaction, { raffleId }) {
        const raffle = raffleStore.getRaffle(raffleId);

        if (!raffle) {
            await interaction.reply({ 
                content: "❌ Sorteio não encontrado!", 
                ephemeral: true 
            });
            return;
        }

        if (raffle.creatorId !== interaction.user.id) {
            await interaction.reply({ 
                content: "❌ Apenas o criador do sorteio pode sortear!", 
                ephemeral: true 
            });
            return;
        }

        const totalTickets = raffleStore.getTotalTickets(raffleId);
        if (totalTickets === 0) {
            await interaction.reply({ 
                content: "❌ Não há tickets vendidos para sortear!", 
                ephemeral: true 
            });
            return;
        }

        // Sortear vencedor
        const winner = raffleStore.drawWinner(raffleId);
        if (!winner) {
            await interaction.reply({ 
                content: "❌ Erro ao sortear vencedor!", 
                ephemeral: true 
            });
            return;
        }

        // Atualizar embed principal para finalizado
        await updateRaffleMessage(raffle, interaction.client, winner);

        // Resposta para o admin
        const adminEmbed = new EmbedBuilder()
            .setTitle("🎉 Sorteio Realizado!")
            .setDescription(`O sorteio **${raffle.title}** foi finalizado!`)
            .setColor(RaffleConfig.colors.finished)
            .addFields({
                name: "🏆 Vencedor",
                value: `<@${winner.userId}>`,
                inline: false
            });

        await interaction.reply({ embeds: [adminEmbed], ephemeral: true });

        // Anunciar resultado no canal
        const resultEmbed = new EmbedBuilder()
            .setTitle("🎉 RESULTADO DO SORTEIO!")
            .setDescription(`**🏆 PRÊMIO: ${raffle.title}**`)
            .setColor(RaffleConfig.colors.finished)
            .addFields(
                {
                    name: "🏆 VENCEDOR",
                    value: `<@${winner.userId}>`,
                    inline: false
                },
                {
                    name: "👥 Participantes",
                    value: `${raffle.participants.length} pessoa${raffle.participants.length !== 1 ? 's' : ''} participou${raffle.participants.length !== 1 ? 'ram' : ''}`,
                    inline: false
                }
            )
            .setTimestamp();

        await interaction.followUp({ embeds: [resultEmbed] });
    }
});

// Responder para cancelar sorteio (admin)
createResponder({
    customId: "raffle_cancel/:raffleId",
    types: [ResponderType.Button],
    parse: raffleSchema.parse,
    async run(interaction, { raffleId }) {
        const confirmButton = new ActionRowBuilder<ButtonBuilder>()
            .addComponents(
                new ButtonBuilder()
                    .setCustomId(`raffle_confirm_cancel/${raffleId}`)
                    .setLabel("✅ Confirmar Cancelamento")
                    .setStyle(ButtonStyle.Danger)
            );

        const confirmEmbed = new EmbedBuilder()
            .setTitle("⚠️ Confirmar Cancelamento")
            .setDescription("Tem certeza que deseja cancelar o sorteio?")
            .setColor(RaffleConfig.colors.cancelled)
            .addFields({
                name: "🔄 Refund",
                value: "Todos os participantes receberão refund total de suas Arca Coins.",
                inline: false
            });

        await interaction.reply({ 
            embeds: [confirmEmbed], 
            components: [confirmButton], 
            ephemeral: true 
        });
    }
});

// Responder para confirmar cancelamento
createResponder({
    customId: "raffle_confirm_cancel/:raffleId",
    types: [ResponderType.Button],
    parse: raffleSchema.parse,
    async run(interaction, { raffleId }) {
        const raffle = raffleStore.getRaffle(raffleId);

        if (!raffle) {
            await interaction.reply({ 
                content: "❌ Sorteio não encontrado!", 
                ephemeral: true 
            });
            return;
        }

        if (raffle.creatorId !== interaction.user.id) {
            await interaction.reply({ 
                content: "❌ Apenas o criador do sorteio pode cancelá-lo!", 
                ephemeral: true 
            });
            return;
        }

        // Processar refunds
        const refunds = raffleStore.cancelRaffle(raffleId);
        for (const refund of refunds) {
            economyStore.addBalance(refund.userId, refund.amount);
        }

        // Buscar sorteio atualizado e atualizar embed principal
        const cancelledRaffle = raffleStore.getRaffle(raffleId);
        if (cancelledRaffle) {
            await updateRaffleMessage(cancelledRaffle, interaction.client);
        }

        const cancelEmbed = new EmbedBuilder()
            .setTitle("✅ Sorteio Cancelado")
            .setDescription(`O sorteio **${raffle.title}** foi cancelado e todos os participantes foram reembolsados.`)
            .setColor(RaffleConfig.colors.cancelled)
            .addFields({
                name: "🔄 Refunds Processados",
                value: `${refunds.length} participante${refunds.length !== 1 ? 's' : ''} reembolsado${refunds.length !== 1 ? 's' : ''}`,
                inline: false
            });

        await interaction.update({ embeds: [cancelEmbed], components: [] });

        // Anunciar cancelamento no canal
        const publicCancelEmbed = new EmbedBuilder()
            .setTitle("❌ SORTEIO CANCELADO")
            .setDescription(`O sorteio **${raffle.title}** foi cancelado pelo organizador.`)
            .setColor(RaffleConfig.colors.cancelled)
            .addFields({
                name: "🔄 Refund Automático",
                value: "Todos os participantes receberam suas Arca Coins de volta.",
                inline: false
            });

        await interaction.followUp({ embeds: [publicCancelEmbed] });
    }
});
