from typing import Any, Dict, Optional

# Importações dos módulos que implementam a lógica específica de cada projeto.
# Mantemos este arquivo como a “fachada” (pontos de extensão) para o REFramework.
from components.actions.login import perform_login
from components.actions.queue import (
    initialize_queue,
    fetch_next_item,
    process_item as process_queue_item,
)
from components.services.browser import create_driver, is_alive, close
from components.services.selenium_utils import take_screenshot


def open_driver(config: Dict[str, Any]):
    """Abre e retorna um driver de automação.

    - Por padrão, usa Selenium (ver services/browser.py) e lê parâmetros de
      data/config.json (browser, headless, download_dir).
    - Adapte create_driver() para trocar de tecnologia (Playwright, etc.).
    """
    return create_driver(config)


def is_platform_available(driver: Any, config: Dict[str, Any]) -> bool:
    """Valida se o driver/sessão está saudável e pronto para uso."""
    return is_alive(driver)


def login(driver: Any, config: Dict[str, Any]) -> bool:
    """Executa o login, caso necessário.

    - Implementação em actions/login.py
    - Deve ser idempotente (não falhar se já estiver logado)
    """
    return perform_login(driver, config)


def init_queue(driver: Any, config: Dict[str, Any]) -> Optional[object]:
    """Inicializa contexto/fila de trabalho e retorna algo truthy se houver itens."""
    return initialize_queue(driver, config)


def get_next_item(driver: Any, config: Dict[str, Any]) -> Optional[object]:
    """Obtém próximo item a ser processado (ou None se não houver)."""
    return fetch_next_item(driver, config)


def process_item(item: Any, driver: Any, config: Dict[str, Any]) -> None:
    """Processa um item da fila. Implementação em actions/queue.py."""
    process_queue_item(item, driver, config)


def cleanup_before_cycle(config: Dict[str, Any]) -> None:
    """Limpeza opcional antes do próximo ciclo (ex.: pastas temporárias)."""
    return None


def close_driver(driver: Any) -> None:
    """Fecha o driver de automação com segurança."""
    close(driver)


def capture_error_evidence(driver: Any, config: Dict[str, Any], prefix: str = "erro") -> None:
    """Captura evidência (screenshot) para auxiliar investigação de falhas."""
    folder = config.get("screenshot_folder") or "logs/screenshots/"
    try:
        take_screenshot(driver, folder, prefix=prefix)
    except Exception:
        pass


