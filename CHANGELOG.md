# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.8] - 2025-07-18

### Added
- Suporte completo para Python 3.13
- Configuração otimizada para Python 3.13 no `pyproject.toml`
- Scripts de instalação atualizados para Python 3.13
- Sistema de .gitignore aprimorado com melhor organização e segurança
- Estrutura de projeto simplificada e otimizada

### Fixed
- **CRÍTICO**: Corrigido uso de `member.discriminator` depreciado no Discord.py 2.0+
- **CRÍTICO**: Corrigido uso de `datetime.utcnow()` depreciado no Python 3.12+
- **CRÍTICO**: Corrigido uso de `datetime.now()` sem timezone para Python 3.12+
- Resolvido warning de depreciação do `audioop` (solucionado no Python 3.13)
- Melhor compatibilidade com versões mais recentes do Discord.py

### Changed
- Migração de Python 3.8+ para Python 3.13+ como requisito mínimo
- Atualizados scripts de setup para usar Python 3.13
- Documentação atualizada para refletir Python 3.13
- Todos os usos de datetime agora usam timezone-aware objects
- Versão atualizada para v1.3.8 em todos os arquivos
- Consolidação de requirements.txt 
- Estrutura de arquivos simplificada para melhor manutenibilidade

### Removed
- Arquivos Docker desnecessários (`docker-compose.yml`, `Dockerfile`)
- Arquivos de documentação redundantes (`IMPROVEMENTS.md`, `DEPLOYMENT.md`, `CONTRIBUTING.md`, `CLEANUP_REPORT.md`)
- Arquivo `requirements-dev.txt` (consolidado em `requirements.txt`)
- Arquivo `Makefile` (funcionalidade movida para tasks do VS Code)
- Arquivos de debug movidos para pasta `tests/` (melhor organização)

### Security
- **CRÍTICO**: Token Discord removido do controle de versão e substituído por placeholder seguro
- Melhorias no .gitignore para proteger arquivos sensíveis (tokens, dados, logs)
- Proteção aprimorada contra exposição acidental de credenciais

## [1.3.7] - 2025-07-18

### Added
- Arquivo `requirements.txt` para dependências de produção
- Arquivo `requirements-dev.txt` para dependências de desenvolvimento
- Script `setup-venv.bat` para instalação com ambiente virtual
- Configuração do VS Code em `.vscode/settings.json`
- Pipeline CI/CD com GitHub Actions
- Configuração melhorada do pytest para testes assíncronos

### Fixed
- Corrigidos problemas de configuração nos testes
- Melhorada a estrutura de dependências do projeto
- Adicionado suporte para testes assíncronos

### Changed
- Melhorada a documentação do projeto
- Estrutura de dependências mais organizada
- Configuração do pytest atualizada

## [1.3.6] - Anterior

### Added
- Sistema de economia com Arca Coins
- Sistema de sorteios interativos
- Painel de carteiras em tempo real
- Sistema de permissões robusto
- Monitoramento de mudanças de cargos
- Backup automático de dados
- Sistema de cache inteligente
- Rate limiting para comandos
- Logs detalhados
- Testes unitários abrangentes

### Features
- ✅ Bot Discord funcional
- ✅ Sistema de economia completo
- ✅ Sorteios com interface interativa
- ✅ Painel de carteiras persistente
- ✅ Sistema de permissões por cargo
- ✅ Monitoramento de voz para recompensas
- ✅ Backup automático de dados
- ✅ Logs detalhados e estruturados
- ✅ Testes unitários
