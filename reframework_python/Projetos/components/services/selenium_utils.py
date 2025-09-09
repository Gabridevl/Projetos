from typing import Any, Optional
import os
from datetime import datetime

# Utilitários genéricos para uso com Selenium
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver  # type: ignore
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def wait_visible(driver: WebDriver, css_selector: str, timeout: int = 30):
    """Aguarda até que um elemento esteja visível na tela e o retorna.

    - Útil para evitar erros de interação antes do carregamento completo.
    """
    wait = WebDriverWait(driver, timeout)
    return wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, css_selector)))


def safe_click(driver: WebDriver, css_selector: str, timeout: int = 30) -> None:
    """Espera o botão/elemento ficar clicável e realiza o clique de forma segura."""
    wait = WebDriverWait(driver, timeout)
    el = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector)))
    el.click()


def take_screenshot(driver: WebDriver, folder: str, prefix: Optional[str] = None) -> str:
    """Tira um screenshot e salva na pasta indicada, retornando o caminho do arquivo.

    - A pasta é criada automaticamente, se não existir.
    - O nome do arquivo inclui timestamp para evitar sobrescrita.
    """
    os.makedirs(folder, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    name = f"{prefix + '_' if prefix else ''}{ts}.png"
    path = os.path.join(folder, name)
    try:
        driver.save_screenshot(path)
    except Exception:
        pass
    return path


