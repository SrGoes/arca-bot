import { 
    ApplicationCommandOptionType, 
    ApplicationCommandType, 
    EmbedBuilder, 
    ActionRowBuilder, 
    ButtonBuilder, 
    ButtonStyle
} from "discord.js";
import { createCommand } from "#base";
import { raffleStore } from "#database";
import { RaffleConfig } from "#settings";
import { randomUUID } from "crypto";

createCommand({
    name: "sorteio",
    description: "🎰 Sistema de sorteios do servidor",
    type: ApplicationCommandType.ChatInput,
    options: [
        {
            name: "criar",
            description: "Criar um novo sorteio (Admin)",
            type: ApplicationCommandOptionType.Subcommand,
            options: [
                {
                    name: "titulo",
                    description: "Título do sorteio (prêmio)",
                    type: ApplicationCommandOptionType.String,
                    required: true,
                    maxLength: 100
                },
                {
                    name: "primeiro_ticket",
                    description: "Valor do primeiro ticket em Arca Coins",
                    type: ApplicationCommandOptionType.Integer,
                    required: true,
                    minValue: RaffleConfig.minFirstTicketPrice,
                    maxValue: RaffleConfig.maxFirstTicketPrice
                }
            ]
        },
        {
            name: "painel",
            description: "Abrir painel administrativo do sorteio ativo (Admin)",
            type: ApplicationCommandOptionType.Subcommand
        }
    ],
    async run(interaction) {
        const subcommand = interaction.options.getSubcommand();

        // Verificar permissões de admin para comandos administrativos
        const isAdmin = interaction.member?.permissions?.has("Administrator") || false;
        const adminCommands = ["criar", "painel"];

        if (adminCommands.includes(subcommand) && !isAdmin) {
            const errorEmbed = new EmbedBuilder()
                .setTitle("❌ Sem Permissão")
                .setDescription("Apenas administradores podem usar este comando.")
                .setColor(RaffleConfig.colors.cancelled);

            await interaction.reply({ embeds: [errorEmbed], ephemeral: true });
            return;
        }

        switch (subcommand) {
            case "criar":
                await handleCreate(interaction);
                break;
            case "painel":
                await handlePanel(interaction);
                break;
        }
    }
});

async function handleCreate(interaction: any) {
    const titulo = interaction.options.getString("titulo", true);
    const primeiroTicket = interaction.options.getInteger("primeiro_ticket", true);
    const channelId = interaction.channelId;

    // Verificar se já existe sorteio ativo no canal
    const existingRaffle = raffleStore.getActiveRaffleByChannel(channelId);
    if (existingRaffle) {
        const errorEmbed = new EmbedBuilder()
            .setTitle("❌ Erro ao Criar Sorteio")
            .setDescription("Já existe um sorteio ativo neste canal!")
            .setColor(RaffleConfig.colors.cancelled)
            .addFields({
                name: "📋 Sorteio Ativo",
                value: `**${existingRaffle.title}**\nPrimeiro ticket: ${existingRaffle.firstTicketPrice} AC`,
                inline: false
            });

        await interaction.reply({ embeds: [errorEmbed], ephemeral: true });
        return;
    }

    // Criar novo sorteio
    const raffleId = randomUUID();
    const raffle = raffleStore.createRaffle(
        raffleId,
        titulo,
        interaction.user.id,
        channelId,
        primeiroTicket
    );

    // Criar embed público
    const embed = createRaffleEmbed(raffle);
    const buttons = createRaffleButtons(raffleId);

    const message = await interaction.reply({ 
        embeds: [embed], 
        components: [buttons],
        fetchReply: true 
    });

    // Salvar messageId
    raffleStore.updateMessageId(raffleId, message.id);

    // Confirmação em DM para o admin
    try {
        const confirmEmbed = new EmbedBuilder()
            .setTitle("✅ Sorteio Criado com Sucesso!")
            .setDescription(`Seu sorteio **${titulo}** foi criado!`)
            .setColor(RaffleConfig.colors.active)
            .addFields(
                {
                    name: "🎫 Primeiro Ticket",
                    value: `${primeiroTicket} AC`,
                    inline: true
                },
                {
                    name: "📍 Canal",
                    value: `<#${channelId}>`,
                    inline: true
                },
                {
                    name: "🆔 ID do Sorteio",
                    value: `\`${raffleId}\``,
                    inline: false
                }
            )
            .setFooter({ text: "Use /sorteio painel para gerenciar" });

        await interaction.followUp({ embeds: [confirmEmbed], ephemeral: true });
    } catch (error) {
        console.error("Erro ao enviar confirmação:", error);
    }
}

async function handlePanel(interaction: any) {
    const channelId = interaction.channelId;
    const raffle = raffleStore.getActiveRaffleByChannel(channelId);

    if (!raffle) {
        const errorEmbed = new EmbedBuilder()
            .setTitle("❌ Nenhum Sorteio Ativo")
            .setDescription("Não há sorteio ativo neste canal.")
            .setColor(RaffleConfig.colors.cancelled);

        await interaction.reply({ embeds: [errorEmbed], ephemeral: true });
        return;
    }

    // Verificar se é o criador do sorteio
    if (raffle.creatorId !== interaction.user.id) {
        const errorEmbed = new EmbedBuilder()
            .setTitle("❌ Sem Permissão")
            .setDescription("Apenas o criador do sorteio pode acessar o painel administrativo.")
            .setColor(RaffleConfig.colors.cancelled);

        await interaction.reply({ embeds: [errorEmbed], ephemeral: true });
        return;
    }

    const totalTickets = raffleStore.getTotalTickets(raffle.id);

    const embed = new EmbedBuilder()
        .setTitle("🎛️ Painel Administrativo - Sorteio")
        .setDescription(`**🏆 PRÊMIO: ${raffle.title}**`)
        .setColor(RaffleConfig.colors.admin)
        .addFields(
            {
                name: "📊 Estatísticas",
                value: [
                    `${RaffleConfig.emojis.participants} **Participantes:** ${raffle.participants.length}`,
                    `${RaffleConfig.emojis.ticket} **Total de Tickets:** ${totalTickets}`,
                    `${RaffleConfig.emojis.prize} **Primeiro Ticket:** ${raffle.firstTicketPrice} AC`
                ].join("\n"),
                inline: false
            }
        );

    // Lista de participantes (limitada a 10 primeiros)
    if (raffle.participants.length > 0) {
        const participantsList = raffle.participants
            .sort((a, b) => b.ticketCount - a.ticketCount)
            .slice(0, 10)
            .map((p, index) => `${index + 1}. <@${p.userId}> - ${p.ticketCount} tickets (${p.totalSpent} AC)`)
            .join("\n");

        embed.addFields({
            name: "👥 Top Participantes",
            value: participantsList + (raffle.participants.length > 10 ? `\n... e mais ${raffle.participants.length - 10}` : ""),
            inline: false
        });
    }

    const adminButtons = new ActionRowBuilder<ButtonBuilder>()
        .addComponents(
            new ButtonBuilder()
                .setCustomId(`raffle_draw/${raffle.id}`)
                .setLabel("🎲 Sortear Agora")
                .setStyle(ButtonStyle.Success)
                .setDisabled(totalTickets === 0),
            new ButtonBuilder()
                .setCustomId(`raffle_cancel/${raffle.id}`)
                .setLabel("❌ Cancelar (Refund)")
                .setStyle(ButtonStyle.Danger)
        );

    await interaction.reply({ 
        embeds: [embed], 
        components: [adminButtons], 
        ephemeral: true 
    });
}

function createRaffleEmbed(raffle: any): EmbedBuilder {
    return new EmbedBuilder()
        .setTitle(`🎰 SORTEIO ATIVO`)
        .setDescription(`**🏆 PRÊMIO: ${raffle.title}**`)
        .setColor(RaffleConfig.colors.active)
        .addFields(
            {
                name: `${RaffleConfig.emojis.ticket} Primeiro Ticket`,
                value: `${raffle.firstTicketPrice} AC`,
                inline: true
            },
            {
                name: `${RaffleConfig.emojis.participants} Participantes`,
                value: `${raffle.participants.length}`,
                inline: true
            },
            {
                name: `${RaffleConfig.emojis.creator} Criado por`,
                value: `<@${raffle.creatorId}>`,
                inline: false
            }
        )
        .setTimestamp();
}

function createRaffleButtons(raffleId: string): ActionRowBuilder<ButtonBuilder> {
    return new ActionRowBuilder<ButtonBuilder>()
        .addComponents(
            new ButtonBuilder()
                .setCustomId(`raffle_buy/${raffleId}`)
                .setLabel("🎫 Comprar Ticket")
                .setStyle(ButtonStyle.Primary),
            new ButtonBuilder()
                .setCustomId(`raffle_info/${raffleId}`)
                .setLabel("ℹ️ Meus Tickets")
                .setStyle(ButtonStyle.Secondary)
        );
}
