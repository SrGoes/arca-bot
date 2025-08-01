import { z } from "zod";

export const envSchema = z.object({
    BOT_TOKEN: z.string("Discord Bot Token is required").min(1),
    WEBHOOK_LOGS_URL: z.url().optional(),
    NODE_OPTIONS: z.string().optional(),
    LOG_LEVEL: z.string().regex(/^[0-4]$/).default("3"),
    VOICE_DEBUG: z.string().regex(/^(true|false)$/).default("false")
});