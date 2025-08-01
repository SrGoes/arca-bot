// Configurações do Sistema de Economia - Arca Bot
export const EconomyConfig = {
    // === RECOMPENSAS POR CALL DE VOZ ===
    voiceRewards: {
        // Intervalo entre recompensas (em minutos)
        rewardIntervalMinutes: 5,
        // Valor mínimo da recompensa por intervalo
        rewardMin: 50,
        // Valor máximo da recompensa por intervalo
        rewardMax: 150,
        // Tempo mínimo na call para começar a receber recompensas (em minutos)
        minimumTimeForReward: 2,
        // ID da categoria do Discord onde as calls vão ter recompensas
        // Para pegar o ID: Clique com botão direito na categoria > Copiar ID
        rewardCategoryId: "", // Substitua pelo ID da categoria desejada
        // Canais específicos para recompensas (deixe vazio para usar toda a categoria)
        specificChannelIds: [] as string[],
    },

    // === RECOMPENSAS DIÁRIAS ===
    daily: {
        // Valor fixo da recompensa diária
        baseAmount: 1000,
        // Valor aleatório adicional (min-max)
        bonusMin: 100,
        bonusMax: 600,
    },

    // === RECOMPENSAS POR MENSAGEM ===
    messages: {
        // Número de mensagens necessárias para ganhar recompensa
        messagesForReward: 10,
        // Valor mínimo da recompensa por mensagem
        rewardMin: 25,
        // Valor máximo da recompensa por mensagem
        rewardMax: 75,
        // Cooldown entre recompensas (em minutos)
        cooldownMinutes: 5,
        // Tamanho mínimo da mensagem para contar (anti-spam)
        minMessageLength: 5,
    },

    // === RANKING ===
    ranking: {
        // Número máximo de usuários no ranking (0 = todos)
        maxUsers: 0,
        // Mostrar usuários inativos no ranking
        showInactive: true,
    },

    // === TRANSFERÊNCIAS ===
    transfer: {
        // Valor mínimo para transferência
        minAmount: 1,
        // Taxa de transferência (% do valor) - 0 = sem taxa
        transferFee: 0,
        // Limite máximo de transferência por transação (0 = sem limite)
        maxTransferAmount: 0,
    },

    // === COMANDOS ADMIN ===
    admin: {
        // Limite máximo para comando /pagar (0 = sem limite)
        maxPayAmount: 0,
        // Limite máximo para comando /remover (0 = sem limite)
        maxRemoveAmount: 0,
        // Valor mínimo para distribuição na call
        minDistributeAmount: 1,
        // IDs dos cargos que podem usar comandos de admin (vazio = usar permissões do Discord)
        // Para pegar o ID do cargo: Clique com botão direito no cargo > Copiar ID do Cargo
        adminRoleIds: [
            // "123456789012345678", // Exemplo: ID do cargo "Moderador"
            // "987654321098765432", // Exemplo: ID do cargo "Admin"
        ] as string[],
        // IDs dos usuários que podem usar comandos de admin (além dos cargos)
        // Para pegar o ID do usuário: Clique com botão direito no usuário > Copiar ID do Usuário
        adminUserIds: [
            // "306978576929128460", // Exemplo: ID do usuário específico
        ] as string[],
        // Se true, usa apenas os IDs configurados. Se false, também aceita permissão Administrator do Discord
        strictMode: false,
    },

    // === SISTEMA GERAL ===
    general: {
        // Nome da moeda
        currencyName: "Arca Coin",
        // Símbolo da moeda
        currencySymbol: "AC",
        // Emoji da moeda
        currencyEmoji: "🪙",
        // Tempo de exibição das mensagens de recompensa (segundos)
        rewardMessageDuration: 10,
        // Formato de localização para números
        numberLocale: "pt-BR",
    },

    // === CORES DOS EMBEDS ===
    colors: {
        success: "#4CAF50",      // Verde
        error: "#FF6B6B",        // Vermelho
        warning: "#FF9800",      // Laranja
        info: "#2196F3",         // Azul
        economy: "#FFD700",      // Dourado
        neutral: "#9E9E9E",      // Cinza
    },

    // === MENSAGENS DO SISTEMA ===
    systemMessages: {
        // Mensagens de erro
        errors: {
            insufficientFunds: "Você não tem Arca Coins suficientes!",
            invalidUser: "Usuário inválido ou não encontrado!",
            cannotTransferToSelf: "Você não pode transferir moedas para si mesmo!",
            cannotTransferToBots: "Você não pode transferir moedas para bots!",
            alreadyClaimedDaily: "Você já coletou sua recompensa diária hoje!",
            notInVoiceChannel: "Você precisa estar em um canal de voz para distribuir moedas!",
            noUsersInVoice: "Não há usuários (não-bots) no canal de voz!",
        },
        
        // Mensagens de sucesso
        success: {
            dailyClaimed: "Parabéns! Você coletou sua recompensa diária!",
            transferComplete: "Transferência realizada com sucesso!",
            paymentComplete: "Pagamento realizado com sucesso!",
            removalComplete: "Remoção realizada com sucesso!",
            distributionComplete: "Distribuição realizada com sucesso!",
            messageReward: "Você ganhou uma recompensa por ser ativo no chat!",
        },
    },
};

// Função helper para calcular recompensa por call de voz
export function calculateVoiceReward(): number {
    const { rewardMin, rewardMax } = EconomyConfig.voiceRewards;
    return Math.floor(Math.random() * (rewardMax - rewardMin + 1)) + rewardMin;
}

// Função helper para validar se um canal deve ter recompensas de voz
export function shouldChannelHaveVoiceRewards(channelId: string, categoryId: string | null): boolean {
    const { rewardCategoryId, specificChannelIds } = EconomyConfig.voiceRewards;
    
    // Se há canais específicos configurados, verificar se está na lista
    if (specificChannelIds.length > 0) {
        return specificChannelIds.includes(channelId);
    }
    
    // Senão, verificar se está na categoria configurada
    if (rewardCategoryId && categoryId) {
        return categoryId === rewardCategoryId;
    }
    
    return false;
}

// Função helper para calcular recompensa diária
export function calculateDailyReward(): number {
    const { baseAmount, bonusMin, bonusMax } = EconomyConfig.daily;
    const bonus = Math.floor(Math.random() * (bonusMax - bonusMin + 1)) + bonusMin;
    return baseAmount + bonus;
}

// Função helper para calcular recompensa por mensagem
export function calculateMessageReward(): number {
    const { rewardMin, rewardMax } = EconomyConfig.messages;
    return Math.floor(Math.random() * (rewardMax - rewardMin + 1)) + rewardMin;
}

// Função helper para formatar moeda
export function formatCurrency(amount: number): string {
    const { numberLocale, currencySymbol } = EconomyConfig.general;
    return `${amount.toLocaleString(numberLocale)} ${currencySymbol}`;
}

// Função helper para validar valor de transferência
export function validateTransferAmount(amount: number, userBalance: number): { valid: boolean; message?: string } {
    const { minAmount, maxTransferAmount } = EconomyConfig.transfer;
    
    if (amount < minAmount) {
        return { valid: false, message: `Valor mínimo para transferência: ${formatCurrency(minAmount)}` };
    }
    
    if (maxTransferAmount > 0 && amount > maxTransferAmount) {
        return { valid: false, message: `Valor máximo para transferência: ${formatCurrency(maxTransferAmount)}` };
    }
    
    if (amount > userBalance) {
        return { valid: false, message: EconomyConfig.systemMessages.errors.insufficientFunds };
    }
    
    return { valid: true };
}

// Função helper para verificar se um usuário é admin
export function isUserAdmin(userId: string, userRoles: string[], hasAdminPermission: boolean): boolean {
    const { adminRoleIds, adminUserIds, strictMode } = EconomyConfig.admin;
    
    // Verificar se o usuário está na lista de admins
    if (adminUserIds.includes(userId)) {
        return true;
    }
    
    // Verificar se o usuário tem algum cargo de admin
    if (adminRoleIds.length > 0) {
        const hasAdminRole = userRoles.some(roleId => adminRoleIds.includes(roleId));
        if (hasAdminRole) {
            return true;
        }
    }
    
    // Se não está em modo estrito, também aceita permissão Administrator do Discord
    if (!strictMode && hasAdminPermission) {
        return true;
    }
    
    return false;
}
