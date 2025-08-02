import { writeFileSync, readFileSync, existsSync, mkdirSync } from "fs";
import { join } from "path";

export interface RaffleData {
    id: string;
    title: string;
    creatorId: string;
    channelId: string;
    messageId?: string;
    firstTicketPrice: number;
    participants: RaffleParticipant[];
    status: 'active' | 'ended' | 'cancelled';
    createdAt: string;
    winnerId?: string;
    totalPrize?: number;
}

export interface RaffleParticipant {
    userId: string;
    ticketCount: number;
    totalSpent: number;
    joinTime: string;
}

class RaffleStore {
    private filePath: string;

    constructor() {
        this.filePath = join(process.cwd(), "data", "raffles.json");
        this.ensureDataDir();
    }

    private ensureDataDir(): void {
        const dataDir = join(process.cwd(), "data");
        if (!existsSync(dataDir)) {
            mkdirSync(dataDir, { recursive: true });
        }
    }

    private getData(): Record<string, RaffleData> {
        if (!existsSync(this.filePath)) {
            return {};
        }
        try {
            const data = readFileSync(this.filePath, "utf8");
            return JSON.parse(data);
        } catch {
            return {};
        }
    }

    private saveData(data: Record<string, RaffleData>): void {
        writeFileSync(this.filePath, JSON.stringify(data, null, 2));
    }

    // Criar novo sorteio
    createRaffle(id: string, title: string, creatorId: string, channelId: string, firstTicketPrice: number): RaffleData {
        const data = this.getData();
        const raffle: RaffleData = {
            id,
            title,
            creatorId,
            channelId,
            firstTicketPrice,
            participants: [],
            status: 'active',
            createdAt: new Date().toISOString()
        };
        
        data[id] = raffle;
        this.saveData(data);
        return raffle;
    }

    // Obter sorteio por ID
    getRaffle(id: string): RaffleData | null {
        const data = this.getData();
        return data[id] || null;
    }

    // Obter todos os sorteios ativos
    getActiveRaffles(): RaffleData[] {
        const data = this.getData();
        return Object.values(data).filter(raffle => raffle.status === 'active');
    }

    // Obter sorteio ativo por canal
    getActiveRaffleByChannel(channelId: string): RaffleData | null {
        const activeRaffles = this.getActiveRaffles();
        return activeRaffles.find(raffle => raffle.channelId === channelId) || null;
    }

    // Adicionar/atualizar participante
    addParticipant(raffleId: string, userId: string, additionalTickets: number, costPaid: number): RaffleData | null {
        const data = this.getData();
        const raffle = data[raffleId];
        
        if (!raffle || raffle.status !== 'active') return null;

        const existingParticipant = raffle.participants.find(p => p.userId === userId);
        
        if (existingParticipant) {
            existingParticipant.ticketCount += additionalTickets;
            existingParticipant.totalSpent += costPaid;
        } else {
            raffle.participants.push({
                userId,
                ticketCount: additionalTickets,
                totalSpent: costPaid,
                joinTime: new Date().toISOString()
            });
        }

        this.saveData(data);
        return raffle;
    }

    // Obter participante específico
    getParticipant(raffleId: string, userId: string): RaffleParticipant | null {
        const raffle = this.getRaffle(raffleId);
        if (!raffle) return null;
        
        return raffle.participants.find(p => p.userId === userId) || null;
    }

    // Calcular total de tickets no sorteio
    getTotalTickets(raffleId: string): number {
        const raffle = this.getRaffle(raffleId);
        if (!raffle) return 0;
        
        return raffle.participants.reduce((total, p) => total + p.ticketCount, 0);
    }

    // Calcular total arrecadado
    getTotalPrize(raffleId: string): number {
        const raffle = this.getRaffle(raffleId);
        if (!raffle) return 0;
        
        return raffle.participants.reduce((total, p) => total + p.totalSpent, 0);
    }

    // Finalizar sorteio
    endRaffle(raffleId: string, winnerId: string): RaffleData | null {
        const data = this.getData();
        const raffle = data[raffleId];
        
        if (!raffle || raffle.status !== 'active') return null;

        raffle.status = 'ended';
        raffle.winnerId = winnerId;
        raffle.totalPrize = this.getTotalPrize(raffleId);
        
        this.saveData(data);
        return raffle;
    }

    // Cancelar sorteio
    cancelRaffle(raffleId: string): Array<{userId: string, amount: number}> {
        const data = this.getData();
        const raffle = data[raffleId];
        
        if (!raffle || raffle.status !== 'active') return [];

        // Preparar dados de refund
        const refunds = raffle.participants.map(p => ({
            userId: p.userId,
            amount: p.totalSpent
        }));

        raffle.status = 'cancelled';
        
        this.saveData(data);
        return refunds;
    }

    // Atualizar messageId do embed
    updateMessageId(raffleId: string, messageId: string): void {
        const data = this.getData();
        const raffle = data[raffleId];
        
        if (raffle) {
            raffle.messageId = messageId;
            this.saveData(data);
        }
    }

    // Limpar sorteios antigos (opcional - para manutenção)
    cleanOldRaffles(daysOld: number = 30): number {
        const data = this.getData();
        const cutoffDate = new Date();
        cutoffDate.setDate(cutoffDate.getDate() - daysOld);
        
        let removed = 0;
        for (const [id, raffle] of Object.entries(data)) {
            const raffleDate = new Date(raffle.createdAt);
            if (raffleDate < cutoffDate && raffle.status !== 'active') {
                delete data[id];
                removed++;
            }
        }
        
        if (removed > 0) {
            this.saveData(data);
        }
        
        return removed;
    }

    // Sortear vencedor baseado no número de tickets
    drawWinner(raffleId: string): RaffleParticipant | null {
        const raffle = this.getRaffle(raffleId);
        if (!raffle || raffle.participants.length === 0) return null;

        const totalTickets = this.getTotalTickets(raffleId);
        if (totalTickets === 0) return null;

        // Gerar número aleatório entre 1 e totalTickets
        const winningNumber = Math.floor(Math.random() * totalTickets) + 1;
        
        // Encontrar o vencedor baseado no ticket sorteado
        let currentTicket = 0;
        for (const participant of raffle.participants) {
            currentTicket += participant.ticketCount;
            if (winningNumber <= currentTicket) {
                // Finalizar sorteio
                this.endRaffle(raffleId, participant.userId);
                return participant;
            }
        }

        return null;
    }
}

export const raffleStore = new RaffleStore();
