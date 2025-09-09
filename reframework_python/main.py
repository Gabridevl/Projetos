import asyncio
import os
import shutil
from components import hooks
from utils.config import load_config, log_error, log_info, configure_logging


def _clean_bytecode_artifacts() -> None:
    """Remove diretórios __pycache__ e arquivos .pyc do projeto.

    - Mantém o ambiente limpo a cada inicialização, evitando lixo de builds.
    - Operação segura: ignora erros de remoção.
    """
    # Caminho de base: pasta do arquivo atual (Projetos/)
    base_dir = os.path.dirname(__file__)
    for root, dirs, files in os.walk(base_dir):
        # Remove diretórios __pycache__
        for d in list(dirs):
            if d == '__pycache__':
                full = os.path.join(root, d)
                try:
                    shutil.rmtree(full, ignore_errors=True)
                except Exception:
                    pass
        # Remove arquivos .pyc
        for f in files:
            if f.endswith('.pyc'):
                try:
                    os.remove(os.path.join(root, f))
                except Exception:
                    pass


# 1) Limpeza de caches/bytecode antes de qualquer coisa (se habilitado em config)
try:
    cfg_preview = load_config()
except Exception:
    cfg_preview = {}
if bool(cfg_preview.get("limpar_cache_no_start", True)):
    _clean_bytecode_artifacts()

# 2) Configura o sistema de log antes de iniciar o fluxo principal.
#    Se ativado em data/config.json, os logs serão gravados em logs/robo.log.
configure_logging()


async def wait_next_cycle(config):
    """Espera o tempo configurado entre ciclos de execução.

    - Este intervalo evita loops constantes quando não há itens a processar
      ou quando o portal/sistema está indisponível.
    """
    wait_time_in_minutes = config.get("wait_time_in_minutes", 2)
    log_info(f"Aguardando {wait_time_in_minutes} minuto(s) para novo ciclo.")
    await asyncio.sleep(wait_time_in_minutes * 60)


async def main():
    """Loop principal do REFramework.

    Fluxo em alto nível:
    1) Carrega configurações
    2) Abre/recupera driver
    3) Valida disponibilidade da plataforma
    4) Executa login (se necessário)
    5) Inicializa fila e busca itens
    6) Processa item
    7) Aguarda próximo ciclo quando não houver itens ou ocorrer falha recuperável
    """
    config = load_config()
    driver = None

    try:
        while True:
            # 1) Garante que há um driver aberto
            if not driver:
                driver = hooks.open_driver(config)
                if not driver:
                    log_error("Falha ao abrir driver. Aguardando próximo ciclo.")
                    await wait_next_cycle(config)
                    continue

            # 2) Verifica se a plataforma/driver está saudável
            if not hooks.is_platform_available(driver, config):
                hooks.close_driver(driver)
                driver = None
                await wait_next_cycle(config)
                continue

            # 3) Realiza login (idempotente: deve lidar com sessão já autenticada)
            if not hooks.login(driver, config):
                log_error("Falha no login. Aguardando próximo ciclo.")
                await wait_next_cycle(config)
                continue

            # 4) Inicializa fila/contexto. Se não houver itens, espera próximo ciclo
            if not hooks.init_queue(driver, config):
                log_info("Sem itens para processar.")
                hooks.cleanup_before_cycle(config)
                await wait_next_cycle(config)
                continue

            # 5) Busca um item e, se houver, processa
            item = hooks.get_next_item(driver, config)
            if item is None:
                log_info("Fila vazia.")
                hooks.cleanup_before_cycle(config)
                await wait_next_cycle(config)
                continue

            try:
                # Uso de await asyncio.sleep(0) para ceder o loop de eventos
                await asyncio.sleep(0)
                hooks.process_item(item, driver, config)
            except Exception as exc:
                # Qualquer erro durante o processamento do item deve ser tratado aqui
                # podendo incluir captura de evidências, retentativas, etc.
                log_error(f"Erro ao processar item: {exc}")
                # Captura de evidência de erro (screenshot)
                try:
                    hooks.capture_error_evidence(driver, config, prefix="process_item")
                except Exception:
                    pass
                await asyncio.sleep(0)

    finally:
        # Fecha o driver ao encerrar o programa (Ctrl+C, exceções, etc.)
        if driver:
            hooks.close_driver(driver)


if __name__ == "__main__":
    asyncio.run(main())