import { writeFileSync } from "fs";
import { join } from "path";

/**
 * Classe para gerenciar health checks do bot
 */
export class HealthCheck {
    private healthFilePath: string;
    private lastHeartbeat: Date;
    private isHealthy: boolean;

    constructor() {
        this.healthFilePath = join(process.cwd(), "data", "health.json");
        this.lastHeartbeat = new Date();
        this.isHealthy = true;
        
        // Atualizar health check a cada 30 segundos
        setInterval(() => this.updateHealth(), 30000);
    }

    /**
     * Marca o bot como saudável
     */
    markHealthy(): void {
        this.isHealthy = true;
        this.lastHeartbeat = new Date();
        this.updateHealth();
    }

    /**
     * Marca o bot como não saudável
     */
    markUnhealthy(reason?: string): void {
        this.isHealthy = false;
        this.updateHealth(reason);
    }

    /**
     * Atualiza o arquivo de health check
     */
    private updateHealth(reason?: string): void {
        const healthData = {
            status: this.isHealthy ? "healthy" : "unhealthy",
            lastHeartbeat: this.lastHeartbeat.toISOString(),
            timestamp: new Date().toISOString(),
            uptime: process.uptime(),
            memoryUsage: process.memoryUsage(),
            reason: reason || null
        };

        try {
            writeFileSync(this.healthFilePath, JSON.stringify(healthData, null, 2));
        } catch (error) {
            console.error("Erro ao atualizar health check:", error);
        }
    }

    /**
     * Retorna o status atual de saúde
     */
    getHealthStatus(): { isHealthy: boolean; lastHeartbeat: Date } {
        return {
            isHealthy: this.isHealthy,
            lastHeartbeat: this.lastHeartbeat
        };
    }
}

// Instância global
export const healthCheck = new HealthCheck();
