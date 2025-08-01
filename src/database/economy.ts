import { writeFileSync, readFileSync, existsSync, mkdirSync } from "fs";
import { join } from "path";
import { EconomyConfig, calculateMessageReward } from "#settings";

export interface UserEconomy {
    userId: string;
    balance: number;
    lastDaily: string | null;
    totalEarned: number;
    totalSpent: number;
    messageCount: number;
    lastMessageReward: string | null;
}

class EconomyStore {
    private filePath: string;

    constructor() {
        this.filePath = join(process.cwd(), "data", "economy.json");
        this.ensureDataDir();
    }

    private ensureDataDir(): void {
        const dataDir = join(process.cwd(), "data");
        if (!existsSync(dataDir)) {
            mkdirSync(dataDir, { recursive: true });
        }
    }

    private getData(): Record<string, UserEconomy> {
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

    private saveData(data: Record<string, UserEconomy>): void {
        writeFileSync(this.filePath, JSON.stringify(data, null, 2));
    }

    getUser(userId: string): UserEconomy {
        const data = this.getData();
        if (!data[userId]) {
            data[userId] = {
                userId,
                balance: 0,
                lastDaily: null,
                totalEarned: 0,
                totalSpent: 0,
                messageCount: 0,
                lastMessageReward: null
            };
            this.saveData(data);
        }

        // Garantir que valores numéricos nunca sejam null/undefined
        const user = data[userId];
        user.balance = user.balance || 0;
        user.totalEarned = user.totalEarned || 0;
        user.totalSpent = user.totalSpent || 0;
        user.messageCount = user.messageCount || 0;

        return user;
    }

    updateUser(userId: string, updates: Partial<UserEconomy>): UserEconomy {
        const data = this.getData();
        const user = this.getUser(userId);
        
        data[userId] = { ...user, ...updates };
        this.saveData(data);
        
        return data[userId];
    }

    addBalance(userId: string, amount: number): UserEconomy {
        const user = this.getUser(userId);
        return this.updateUser(userId, {
            balance: user.balance + amount,
            totalEarned: user.totalEarned + (amount > 0 ? amount : 0)
        });
    }

    removeBalance(userId: string, amount: number): UserEconomy {
        const user = this.getUser(userId);
        const newBalance = Math.max(0, user.balance - amount);
        return this.updateUser(userId, {
            balance: newBalance,
            totalSpent: user.totalSpent + (user.balance - newBalance)
        });
    }

    canClaimDaily(userId: string): boolean {
        const user = this.getUser(userId);
        if (!user.lastDaily) return true;

        const lastDaily = new Date(user.lastDaily);
        const today = new Date();
        
        // Resetar à meia-noite
        const todayMidnight = new Date(today.getFullYear(), today.getMonth(), today.getDate());
        const lastDailyMidnight = new Date(lastDaily.getFullYear(), lastDaily.getMonth(), lastDaily.getDate());
        
        return todayMidnight.getTime() > lastDailyMidnight.getTime();
    }

    claimDaily(userId: string, amount: number): UserEconomy {
        const now = new Date().toISOString();
        this.addBalance(userId, amount);
        return this.updateUser(userId, {
            lastDaily: now
        });
    }

    getLeaderboard(limit: number = 1000): UserEconomy[] {
        const data = this.getData();
        const allUsers = Object.values(data).sort((a, b) => b.balance - a.balance);
        return limit > 0 ? allUsers.slice(0, limit) : allUsers;
    }

    // Sistema de recompensas por mensagem
    canGainMessageReward(userId: string): boolean {
        const user = this.getUser(userId);
        
        // Cooldown configurável entre recompensas
        if (user.lastMessageReward) {
            const lastReward = new Date(user.lastMessageReward);
            const now = new Date();
            const cooldownMs = EconomyConfig.messages.cooldownMinutes * 60 * 1000;
            
            return (now.getTime() - lastReward.getTime()) >= cooldownMs;
        }
        
        return true;
    }

    addMessage(userId: string): { gained: boolean; amount: number; newBalance: number } {
        const user = this.getUser(userId);
        const newMessageCount = user.messageCount + 1;
        
        // Atualizar contador de mensagens
        this.updateUser(userId, { messageCount: newMessageCount });
        
        // Usar configurações para recompensas
        const messagesForReward = EconomyConfig.messages.messagesForReward;
        const rewardAmount = calculateMessageReward();
        
        if (newMessageCount % messagesForReward === 0 && this.canGainMessageReward(userId)) {
            const updatedUser = this.addBalance(userId, rewardAmount);
            this.updateUser(userId, { lastMessageReward: new Date().toISOString() });
            
            return {
                gained: true,
                amount: rewardAmount,
                newBalance: updatedUser.balance
            };
        }
        
        return {
            gained: false,
            amount: 0,
            newBalance: user.balance
        };
    }
}

export const economyStore = new EconomyStore();
