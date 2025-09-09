from typing import Any, Dict

# Importações específicas do Selenium para localizar elementos e aguardar condições
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Funções de log centralizadas
from utils.config import log_error, log_info


def perform_login(driver: Any, config: Dict[str, str]) -> bool:
    """Realiza login utilizando Selenium de forma genérica.

    Espera as seguintes chaves em data/config.json:
    - url: endereço da página de login
    - username: usuário de autenticação
    - password: senha de autenticação

    As chaves abaixo são opcionais (CSS selectors) e possuem padrões seguros:
    - username_selector: seletor do campo de usuário. Padrão: input[name="username"]
    - password_selector: seletor do campo de senha. Padrão: input[type="password"]
    - submit_selector: seletor do botão de envio. Padrão: button[type="submit"]
    - success_check_selector: seletor de um elemento que confirma login com sucesso (opcional)
    """
    url = config.get("url")
    user = config.get("username")
    pwd = config.get("password")

    # Se não houver credenciais ou URL, consideramos que o login não é necessário
    if not url or not user or not pwd:
        log_info("Login pulado: url/username/password não configurados.")
        return True

    username_selector = config.get("username_selector", 'input[name="username"]')
    password_selector = config.get("password_selector", 'input[type="password"]')
    submit_selector = config.get("submit_selector", 'button[type="submit"]')
    success_check_selector = config.get("success_check_selector")

    try:
        # Acessa a página de login
        driver.get(url)  # type: ignore[attr-defined]

        # Aguarda o carregamento e a presença dos campos de usuário e senha
        wait = WebDriverWait(driver, 30)
        user_el = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, username_selector)))
        pass_el = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, password_selector)))

        # Preenche credenciais
        user_el.clear()
        user_el.send_keys(user)
        pass_el.clear()
        pass_el.send_keys(pwd)

        # Clica no botão de login
        submit_el = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, submit_selector)))
        submit_el.click()

        # Caso um seletor de sucesso seja informado, aguardamos sua presença
        if success_check_selector:
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, success_check_selector)))

        log_info("Login realizado com sucesso.")
        return True
    except Exception as exc:
        log_error(f"Falha no login: {exc}")
        return False


