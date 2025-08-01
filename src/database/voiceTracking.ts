import { writeFileSync, readFileSync, existsSync, mkdirSync } from "fs";
import { join } from "path";

// === INTERFACES ===

export interface VoiceSession {
    userId: string;
    channelId: string;
    channelName: string;
    guildId: string;
    startTime: string; // ISO string
    lastActivity: string; // ISO string
    totalMinutes: number;
    acEarned: number;
    isActive: boolean;
}

export interface AbsentUser {
    userId: string;
    channelId: string;
    channelName: string;
    guildId: string;
    absenceStart: string; // ISO string
    originalStartTime: string; // ISO string
    totalMinutesBeforeAbsence: number;
    acEarnedBeforeAbsence: number;
}

export interface ChannelStatus {
    channelId: string;
    messageId: string | null;
    lastUpdate: string; // ISO string
    activeUsers: string[]; // Array de user IDs
}

export interface VoiceTrackingData {
    activeSessions: Record<string, VoiceSession>; // userId -> session
    absentUsers: Record<string, AbsentUser>; // userId -> absence info
    channelStatuses: Record<string, ChannelStatus>; // channelId -> status
    lastSave: string; // ISO string
}

// === CLASSE PRINCIPAL ===

class VoiceTrackingStore {
    private dataPath: string;

    constructor() {
        this.dataPath = join(process.cwd(), "data", "voice_tracking_data.json");
        this.ensureDataDir();
    }

    private ensureDataDir(): void {
        const dataDir = join(process.cwd(), "data");
        if (!existsSync(dataDir)) {
            mkdirSync(dataDir, { recursive: true });
        }
    }

    // === CARREGAMENTO E SALVAMENTO ===

    private loadData(): VoiceTrackingData {
        if (!existsSync(this.dataPath)) {
            return this.getEmptyData();
        }

        try {
            const rawData = readFileSync(this.dataPath, "utf-8");
            const data = JSON.parse(rawData) as VoiceTrackingData;
            
            // Validar estrutura dos dados
            if (!data.activeSessions) data.activeSessions = {};
            if (!data.absentUsers) data.absentUsers = {};
            if (!data.channelStatuses) data.channelStatuses = {};
            if (!data.lastSave) data.lastSave = new Date().toISOString();

            return data;
        } catch (error) {
            console.error("Erro ao carregar dados de voice tracking:", error);
            return this.getEmptyData();
        }
    }

    private saveData(data: VoiceTrackingData): void {
        try {
            data.lastSave = new Date().toISOString();
            writeFileSync(this.dataPath, JSON.stringify(data, null, 2), "utf-8");
        } catch (error) {
            console.error("Erro ao salvar dados de voice tracking:", error);
        }
    }

    private getEmptyData(): VoiceTrackingData {
        return {
            activeSessions: {},
            absentUsers: {},
            channelStatuses: {},
            lastSave: new Date().toISOString()
        };
    }

    // === MÉTODOS DE SESSÃO ===

    startSession(userId: string, channelId: string, channelName: string, guildId: string): VoiceSession {
        const data = this.loadData();
        const now = new Date().toISOString();

        const session: VoiceSession = {
            userId,
            channelId,
            channelName,
            guildId,
            startTime: now,
            lastActivity: now,
            totalMinutes: 0,
            acEarned: 0,
            isActive: true
        };

        data.activeSessions[userId] = session;
        
        // Remover de ausentes se estava ausente
        delete data.absentUsers[userId];
        
        this.saveData(data);
        return session;
    }

    endSession(userId: string): VoiceSession | null {
        const data = this.loadData();
        const session = data.activeSessions[userId];

        if (!session) return null;

        // Calcular tempo total da sessão
        const now = new Date();
        const startTime = new Date(session.startTime);
        const totalMinutes = Math.floor((now.getTime() - startTime.getTime()) / (1000 * 60));

        session.totalMinutes = totalMinutes;
        session.isActive = false;
        session.lastActivity = now.toISOString();

        // Remover da lista de ativos
        delete data.activeSessions[userId];
        
        // Remover de ausentes se estava ausente
        delete data.absentUsers[userId];

        this.saveData(data);
        return session;
    }

    getActiveSession(userId: string): VoiceSession | null {
        const data = this.loadData();
        return data.activeSessions[userId] || null;
    }

    getAllActiveSessions(): VoiceSession[] {
        const data = this.loadData();
        return Object.values(data.activeSessions);
    }

    updateSessionActivity(userId: string): void {
        const data = this.loadData();
        const session = data.activeSessions[userId];
        
        if (session) {
            session.lastActivity = new Date().toISOString();
            this.saveData(data);
        }
    }

    updateSessionChannel(userId: string, newChannelId: string, newChannelName: string): void {
        const data = this.loadData();
        const session = data.activeSessions[userId];
        
        if (session) {
            session.channelId = newChannelId;
            session.channelName = newChannelName;
            session.lastActivity = new Date().toISOString();
            this.saveData(data);
        }
    }

    updateSessionReward(userId: string, acAmount: number): void {
        const data = this.loadData();
        const session = data.activeSessions[userId];
        
        if (session) {
            session.acEarned += acAmount;
            session.lastActivity = new Date().toISOString();
            this.saveData(data);
        }
    }

    // === MÉTODOS DE AUSÊNCIA (SIMPLIFICADO) ===
    // Sistema de ausência removido para evitar notificações falsas
    
    markUserAsAbsent(_userId: string): AbsentUser | null {
        // Função mantida para compatibilidade - não faz nada
        return null;
    }

    returnFromAbsence(_userId: string): VoiceSession | null {
        // Função mantida para compatibilidade - não faz nada  
        return null;
    }

    getAbsentUser(_userId: string): AbsentUser | null {
        // Função mantida para compatibilidade - sempre retorna null
        return null;
    }

    getAllAbsentUsers(): AbsentUser[] {
        // Função mantida para compatibilidade - sempre retorna array vazio
        return [];
    }

    finalizeAbsentSession(userId: string): { session: VoiceSession | null, absentInfo: AbsentUser | null } {
        // Simplificado - apenas finaliza a sessão normalmente
        const session = this.endSession(userId);
        return { session, absentInfo: null };
    }

    // === MÉTODOS DE STATUS DO CANAL ===

    updateChannelStatus(channelId: string, messageId: string | null, activeUsers: string[]): void {
        const data = this.loadData();
        
        data.channelStatuses[channelId] = {
            channelId,
            messageId,
            lastUpdate: new Date().toISOString(),
            activeUsers: [...activeUsers]
        };

        this.saveData(data);
    }

    getChannelStatus(channelId: string): ChannelStatus | null {
        const data = this.loadData();
        return data.channelStatuses[channelId] || null;
    }

    removeChannelStatus(channelId: string): void {
        const data = this.loadData();
        delete data.channelStatuses[channelId];
        this.saveData(data);
    }

    getAllChannelStatuses(): ChannelStatus[] {
        const data = this.loadData();
        return Object.values(data.channelStatuses);
    }

    // === MÉTODOS DE UTILIDADE ===

    getSessionDuration(userId: string): number {
        const session = this.getActiveSession(userId);
        if (!session) return 0;

        const now = new Date();
        const startTime = new Date(session.startTime);
        return Math.floor((now.getTime() - startTime.getTime()) / (1000 * 60));
    }

    // === LIMPEZA E RECUPERAÇÃO ===

    cleanup(): void {
        const data = this.loadData();
        const now = new Date();
        let hasChanges = false;

        // Limpar sessões muito antigas (mais de 24 horas)
        for (const [userId, session] of Object.entries(data.activeSessions)) {
            const sessionStart = new Date(session.startTime);
            const hoursSinceStart = (now.getTime() - sessionStart.getTime()) / (1000 * 60 * 60);
            
            if (hoursSinceStart > 24) {
                delete data.activeSessions[userId];
                hasChanges = true;
            }
        }

        // Limpar ausências muito antigas (mais de 2 horas)
        for (const [userId, absentUser] of Object.entries(data.absentUsers)) {
            const absenceStart = new Date(absentUser.absenceStart);
            const hoursSinceAbsence = (now.getTime() - absenceStart.getTime()) / (1000 * 60 * 60);
            
            if (hoursSinceAbsence > 2) {
                delete data.absentUsers[userId];
                hasChanges = true;
            }
        }

        if (hasChanges) {
            this.saveData(data);
        }
    }

    getRecoveryData(): VoiceTrackingData {
        return this.loadData();
    }

    isRecentRestart(): boolean {
        const data = this.loadData();
        const lastSave = new Date(data.lastSave);
        const now = new Date();
        const minutesSinceLastSave = (now.getTime() - lastSave.getTime()) / (1000 * 60);
        
        return minutesSinceLastSave <= 15; // Considera restart recente se menos de 15 min
    }
}

// === INSTÂNCIA SINGLETON ===
export const voiceTrackingStore = new VoiceTrackingStore();
