import { createEvent } from "#base";
import { Client, Events } from "discord.js";
import { recoverVoiceSessions } from "./voiceStateUpdate.js";
import { logger } from "#settings";

createEvent({
    name: "ready-voice-recovery",
    event: Events.ClientReady,
    async run(client: Client<true>) {
        logger.log("🔊 Inicializando sistema de Voice Tracking...");
        
        try {
            // Pequeno delay para garantir que tudo esteja carregado
            setTimeout(async () => {
                await recoverVoiceSessions(client);
            }, 2000);
            
            logger.success("Sistema de Voice Tracking inicializado com sucesso!");
        } catch (error) {
            logger.error("Erro ao inicializar Voice Tracking:", error);
        }
    }
});
