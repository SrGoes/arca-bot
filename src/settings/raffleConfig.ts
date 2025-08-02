// Configurações do Sistema de Sorteio - Arca Bot
export const RaffleConfig = {
    // === CONFIGURAÇÕES BÁSICAS ===
    // Multiplicador para preço progressivo dos tickets
    priceMultiplier: 1.1,
    
    // Valor mínimo para o primeiro ticket
    minFirstTicketPrice: 1,
    
    // Valor máximo para o primeiro ticket
    maxFirstTicketPrice: 10000,
    
    // Número máximo de tickets por usuário (0 = ilimitado)
    maxTicketsPerUser: 50,
    
    // Número máximo de participantes no sorteio (0 = ilimitado)
    maxParticipants: 100,
    
    // === PERMISSÕES ===
    // Roles que podem criar sorteios (deixe vazio para permitir qualquer admin)
    allowedRoles: [] as string[],
    
    // === INTERFACE ===
    // Cores dos embeds
    colors: {
        active: 0x00FF7F,      // Verde para sorteio ativo
        ended: 0xFFD700,       // Dourado para sorteio finalizado
        cancelled: 0xFF6B6B,   // Vermelho para sorteio cancelado
        admin: 0x4169E1,       // Azul para painel admin
        finished: 0xFFD700     // Dourado para sorteio finalizado com vencedor
    },
    
    // Emojis utilizados
    emojis: {
        ticket: "🎫",
        prize: "🏆",
        participants: "👥",
        creator: "👑",
        time: "⏰",
        money: "💰"
    }
};

// Função para calcular o preço do próximo ticket
export function calculateTicketPrice(firstTicketPrice: number, currentTicketCount: number): number {
    if (currentTicketCount === 0) return firstTicketPrice;
    return Math.round(firstTicketPrice * Math.pow(RaffleConfig.priceMultiplier, currentTicketCount));
}

// Função para calcular preço total de uma quantidade de tickets
export function calculateTotalPrice(firstTicketPrice: number, currentTickets: number, newTickets: number): number {
    let total = 0;
    for (let i = 0; i < newTickets; i++) {
        total += calculateTicketPrice(firstTicketPrice, currentTickets + i);
    }
    return total;
}
