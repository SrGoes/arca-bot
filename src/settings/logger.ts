import chalk from "chalk";

// Níveis de log: 0 = silent, 1 = error, 2 = warn, 3 = info, 4 = debug
const LOG_LEVEL = parseInt(process.env.LOG_LEVEL || "2"); // Padrão: apenas errors e warnings

type LogParams = [message?: any, ...params: any[]];

function log(...params: LogParams){
    if (LOG_LEVEL >= 3) {
        return console.log(...params);
    }
}

function success(...params: LogParams){
    if (LOG_LEVEL >= 3) {
        return console.log(chalk.green(`✓`), ...params);
    }
}

function warn(...params: LogParams){
    if (LOG_LEVEL >= 2) {
        return console.warn(chalk.yellow(`▲`), ...params);
    }
}

function error(...params: LogParams){
    if (LOG_LEVEL >= 1) {
        return console.error(chalk.red(`✖︎`), ...params);
    }
}

function debug(...params: LogParams){
    if (LOG_LEVEL >= 4) {
        return console.log(chalk.gray(`[DEBUG]`), ...params);
    }
}

export const logger = {
    log,
    success,
    warn,
    error,
    debug,
};