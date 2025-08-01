import settings from "../../settings.json" with { type: "json" };
import { envSchema } from "./env.schema.js";

import "./global.js";
import { logger } from "./logger.js";
import { validateEnv } from "./env.validate.js";
export * from "./error.js";
export * from "./economyConfig.js";
export * from "./voiceConfig.js";
export * from "./raffleConfig.js";
export * from "./gracefulShutdown.js";
export * from "./backupSystem.js";
export * from "./healthCheck.js";

const env = validateEnv(envSchema);

export { settings, logger, env };