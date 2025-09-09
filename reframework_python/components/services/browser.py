from typing import Any, Dict, Optional
import os


def _ensure_dir(path: str) -> None:
    """Garante que o diretório existe (cria se não existir)."""
    os.makedirs(path, exist_ok=True)


def _chrome_driver(config: Dict[str, Any]):
    """Cria um WebDriver do Chrome configurado conforme o config."""
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service as ChromeService
    from webdriver_manager.chrome import ChromeDriverManager

    download_dir = config.get("download_dir") or os.path.join(os.getcwd(), "downloads")
    _ensure_dir(download_dir)

    options = Options()
    if str(config.get("headless", True)).lower() in ("1", "true", "yes"):  # tolera string/bool
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    prefs = {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
    }
    options.add_experimental_option("prefs", prefs)

    # webdriver-manager baixa e gerencia o binário do driver automaticamente
    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver


def _edge_driver(config: Dict[str, Any]):
    """Cria um WebDriver do Edge configurado conforme o config."""
    from selenium import webdriver
    from selenium.webdriver.edge.options import Options
    from selenium.webdriver.edge.service import Service as EdgeService
    from webdriver_manager.microsoft import EdgeChromiumDriverManager

    download_dir = config.get("download_dir") or os.path.join(os.getcwd(), "downloads")
    _ensure_dir(download_dir)

    options = Options()
    if str(config.get("headless", True)).lower() in ("1", "true", "yes"):
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.add_experimental_option(
        "prefs",
        {
            "download.default_directory": download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
        },
    )

    # webdriver-manager baixa e gerencia o binário do driver automaticamente
    service = EdgeService(EdgeChromiumDriverManager().install())
    driver = webdriver.Edge(service=service, options=options)
    return driver


def create_driver(config: Dict[str, Any]) -> Optional[Any]:
    """Cria e retorna um WebDriver do Selenium baseado em config.

    Config esperada:
    - browser: "chrome" | "edge" (padrão: chrome)
    - headless: bool (padrão: True)
    - download_dir: str (pasta para downloads)
    """
    browser = str(config.get("browser", "chrome")).lower()
    try:
        if browser == "edge":
            return _edge_driver(config)
        return _chrome_driver(config)
    except Exception:
        return None


def is_alive(driver: Any) -> bool:
    try:
        _ = driver.current_url  # type: ignore[attr-defined]
        return True
    except Exception:
        return False


def close(driver: Any) -> None:
    try:
        driver.quit()  # type: ignore[attr-defined]
    except Exception:
        pass


