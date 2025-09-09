from typing import Any, Dict, Optional, List
import csv
import json
import os
from datetime import datetime
from utils.config import log_info, log_error

# Estados mantidos em memória simples
_queue_items: List[Dict[str, Any]] = []
_queue_loaded: bool = False


def _project_root() -> str:
    """Retorna a pasta raiz do projeto (a partir deste arquivo).

    queue.py -> actions -> components -> Projetos -> (raiz deste módulo)
    """
    return os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


def _queue_path(config: Dict[str, Any]) -> str:
    return config.get("csv_queue_path") or os.path.join(_project_root(), "data", "queue.csv")


def _state_path(config: Dict[str, Any]) -> str:
    return config.get("state_path") or os.path.join(_project_root(), "logs", "state.json")


def _metrics_path(config: Dict[str, Any]) -> str:
    return config.get("metrics_path") or os.path.join(_project_root(), "logs", "metrics.json")


def _health_path(config: Dict[str, Any]) -> str:
    return config.get("health_path") or os.path.join(_project_root(), "logs", "health.json")


def _ensure_dir(path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)


def initialize_queue(driver: Any, config: Dict[str, Any]) -> bool:
    """Carrega itens de uma fila CSV simples (se existir) e indica se há itens.

    - O CSV deve ter cabeçalho. Cada linha vira um dicionário.
    - Esta implementação é intencionalmente simples para ser trocada por fonte real (API/DB).
    """
    global _queue_loaded, _queue_items

    if _queue_loaded:
        return len(_queue_items) > 0

    path = _queue_path(config)
    if not os.path.exists(path):
        _queue_loaded = True
        _queue_items = []
        return False

    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        _queue_items = [row for row in reader]
    _queue_loaded = True

    return len(_queue_items) > 0


def fetch_next_item(driver: Any, config: Dict[str, Any]) -> Optional[object]:
    """Retorna o próximo item e registra estado/health se necessário."""
    if not _queue_items:
        return None
    item = _queue_items.pop(0)

    # Atualiza health
    _ensure_dir(_health_path(config))
    with open(_health_path(config), 'w', encoding='utf-8') as f:
        json.dump({
            "last_fetch": datetime.utcnow().isoformat() + "Z",
            "remaining_items": len(_queue_items),
        }, f, ensure_ascii=False, indent=2)

    return item


def process_item(item: Any, driver: Any, config: Dict[str, Any]) -> None:
    """Processa um item e registra métricas simples.

    - Substitua esta função pela lógica do seu projeto.
    - Esta função apenas registra métrica de sucesso por padrão.
    """
    # Exemplo básico: loga o ID do item (se existir) e considera sucesso
    item_id = item.get("id") if isinstance(item, dict) else None
    log_info(f"Processando item{f' id={item_id}' if item_id else ''}...")
    success = True

    # Atualiza métricas
    _ensure_dir(_metrics_path(config))
    metrics = {"processed_total": 0, "processed_success": 0, "processed_error": 0}
    if os.path.exists(_metrics_path(config)):
        try:
            with open(_metrics_path(config), 'r', encoding='utf-8') as f:
                metrics = json.load(f)
        except Exception:
            pass

    metrics["processed_total"] = int(metrics.get("processed_total", 0)) + 1
    if success:
        metrics["processed_success"] = int(metrics.get("processed_success", 0)) + 1
    else:
        metrics["processed_error"] = int(metrics.get("processed_error", 0)) + 1

    with open(_metrics_path(config), 'w', encoding='utf-8') as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)

    # Log final do item
    if success:
        log_info(f"Item{f' id={item_id}' if item_id else ''} processado com sucesso.")
    else:
        log_error(f"Falha ao processar item{f' id={item_id}' if item_id else ''}.")



