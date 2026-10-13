import os
import json
import asyncio
import uvicorn
from datetime import datetime
from collections import deque
from contextlib import asynccontextmanager
from typing import Dict, Any, Set
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

# ---------------------------------------------------------
# Configuración e Inyección de Dependencias
# ---------------------------------------------------------
PROD_ASSETS_STR = os.getenv("PRODUCTION_ASSETS", "")
MOB_ASSETS_STR = os.getenv("MOBILE_ASSETS", "")
HUM_ASSETS_STR = os.getenv("HUMAN_ASSETS", "")

ASSET_TASKS = {
    "robot": {"weld": "Soldadura", "drill": "Perforación", "pick_place": "Mover Pieza"},
    "mobile": {"transport": "Transporte", "patrol": "Patrulla", "scan": "Escaneo RADAR"},
    "human": {"transport": "Transporte", "assemble": "Ensamblaje", "inspect": "Inspección QA", "maintain": "Mantenimiento"}
}

ASSET_CATALOG = {}
for a in [a.strip() for a in PROD_ASSETS_STR.split(",") if a.strip()]: ASSET_CATALOG[a] = "robot"
for a in [a.strip() for a in MOB_ASSETS_STR.split(",") if a.strip()]: ASSET_CATALOG[a] = "mobile"
for a in [a.strip() for a in HUM_ASSETS_STR.split(",") if a.strip()]: ASSET_CATALOG[a] = "human"

ASSET_IDS = list(ASSET_CATALOG.keys())

# Estructuras en memoria y primitivas de sincronización
assets_state: Dict[str, Dict[str, Any]] = {}
asset_locks: Dict[str, asyncio.Lock] = {}
sse_clients: Set[asyncio.Queue] = set()

# Histórico acotado para prevenir Memory Leaks (máximo 100 eventos)
request_history = deque(maxlen=100)

RESERVED_ASSET_IDS = {"register", "status", "charge", "recover", "action"}


def _init_asset(asset_id: str, asset_type: str):
    """Inicializa las estructuras en memoria para un activo (usado al arrancar y al registrar)."""
    ASSET_CATALOG[asset_id] = asset_type
    assets_state[asset_id] = {
        "type": asset_type,
        "status": "idle",
        "battery": 100.0,
        "current_task": None
    }
    asset_locks[asset_id] = asyncio.Lock()


def append_to_history(asset_id: str, req_type: str, details: str):
    """Registra una petición de forma thread-safe en el entorno asíncrono."""
    timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
    asset_type = ASSET_CATALOG.get(asset_id, "system")
    request_history.appendleft({
        "timestamp": timestamp,
        "asset_id": asset_id,
        "asset_type": asset_type,
        "type": req_type,
        "details": details
    })


# ---------------------------------------------------------
# Lógica de Notificación SSE
# ---------------------------------------------------------
async def notify_clients():
    """Empuja el snapshot del estado global y el histórico a todas las colas de clientes activos."""
    # El payload ahora es un objeto compuesto para nutrir la nueva UI
    payload = {
        "state": assets_state,
        "history": list(request_history)
    }
    payload_json = json.dumps(payload)

    for queue in list(sse_clients):
        try:
            queue.put_nowait(payload_json)
        except asyncio.QueueFull:
            pass


# ---------------------------------------------------------
# Simulación Física Continua (Background Loop)
# ---------------------------------------------------------
async def battery_manager_loop():
    """Lazo de control que procesa la recarga/descanso de activos en background."""
    while True:
        await asyncio.sleep(0.5)
        state_mutated = False

        for asset_id, state in list(assets_state.items()):
            if state["status"] == "charging":
                # El activo puede haberse registrado justo tras copiar la lista
                if asset_id not in asset_locks:
                    continue
                async with asset_locks[asset_id]:
                    if state["battery"] < 100:
                        state["battery"] = min(100.0, state["battery"] + 2.5)
                        state_mutated = True
                    elif state["battery"] >= 100.0:
                        state["status"] = "idle"
                        state_mutated = True

        if state_mutated:
            await notify_clients()


# ---------------------------------------------------------
# Gestión del Ciclo de Vida (Lifespan Pattern)
# ---------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    for asset_id in ASSET_IDS:
        _init_asset(asset_id, ASSET_CATALOG[asset_id])

    # Evento génesis
    append_to_history("SYSTEM", "INIT", "Simulación inicializada")

    bg_task = asyncio.create_task(battery_manager_loop())
    yield

    bg_task.cancel()
    assets_state.clear()
    asset_locks.clear()
    sse_clients.clear()
    request_history.clear()


app = FastAPI(title="Unified Asset Simulator", lifespan=lifespan)
templates = Jinja2Templates(directory="templates")
app.mount("/images", StaticFiles(directory="images"), name="images")


# ---------------------------------------------------------
# Modelos Pydantic
# ---------------------------------------------------------
class ActionRequest(BaseModel):
    duration: int = Field(..., gt=0, le=30, description="Duration in seconds")


class ChargeRequest(BaseModel):
    enable: bool = Field(..., description="Activar/Desactivar recarga o descanso")


class AssetRegisterRequest(BaseModel):
    asset_id: str = Field(..., min_length=1, max_length=64, pattern=r"^[A-Za-z0-9_./-]+$",
                          description="Identificador único del activo (se admiten subrutas tipo AssetID/IR3)")
    type: str = Field(..., description="Tipo de activo: robot, mobile o human")


# ---------------------------------------------------------
# APIs BFF e Interfaz UI
# ---------------------------------------------------------
@app.get("/")
async def serve_ui(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"asset_tasks": ASSET_TASKS}
    )


@app.get("/ui/stream")
async def sse_stream(request: Request):
    client_queue = asyncio.Queue()
    sse_clients.add(client_queue)

    async def event_generator():
        try:
            # Enviar estado inicial inmediato
            initial_payload = json.dumps({"state": assets_state, "history": list(request_history)})
            yield f"data: {initial_payload}\n\n"

            while True:
                if await request.is_disconnected():
                    break
                state_data = await client_queue.get()
                yield f"data: {state_data}\n\n"
        except asyncio.CancelledError:
            pass
        finally:
            if client_queue in sse_clients:
                sse_clients.remove(client_queue)

    return StreamingResponse(event_generator(), media_type="text/event-stream")


# ---------------------------------------------------------
# APIs de Control de Activos
# ---------------------------------------------------------
@app.post("/api/v1/assets/register", status_code=status.HTTP_201_CREATED)
async def register_asset(payload: AssetRegisterRequest):
    asset_id = payload.asset_id.strip()
    asset_type = payload.type.strip().lower()

    if not asset_id:
        raise HTTPException(status_code=400, detail="asset_id cannot be empty")
    if asset_id.startswith("/") or asset_id.endswith("/") or "//" in asset_id:
        raise HTTPException(status_code=400, detail="asset_id cannot start/end with '/' or contain '//'")
    if asset_type not in ASSET_TASKS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid asset type '{payload.type}'. Allowed: {list(ASSET_TASKS.keys())}"
        )
    if asset_id.lower() in RESERVED_ASSET_IDS:
        raise HTTPException(status_code=400, detail=f"asset_id '{asset_id}' is reserved")
    if asset_id in assets_state:
        raise HTTPException(status_code=409, detail=f"Asset '{asset_id}' already registered")

    # Sin await entre la comprobación y la inserción: atómico en asyncio
    _init_asset(asset_id, asset_type)
    append_to_history(asset_id, "REGISTER", f"Nuevo activo registrado de tipo {asset_type.upper()}")
    await notify_clients()

    return {"status": "registered", "asset": asset_id, "type": asset_type}


@app.get("/api/v1/asset/{asset_id:path}/status")
async def get_status(asset_id: str):
    if asset_id not in assets_state:
        raise HTTPException(status_code=404, detail="Asset not found")

    # Registramos la petición de lectura explícita
    append_to_history(asset_id, "STATUS", "Telemetría solicitada por cliente externo")
    await notify_clients()  # Notificamos para que UI actualice histórico

    response_state = assets_state[asset_id].copy()
    if response_state.get("type") == "human":
        response_state["stamina"] = response_state.pop("battery", 100.0)
    return response_state


@app.post("/api/v1/asset/{asset_id:path}/charge")
@app.post("/api/v1/asset/{asset_id:path}/recover")
async def toggle_charge(asset_id: str, payload: ChargeRequest = None):
    if payload is None:
        payload = ChargeRequest(enable=True)  # If payload is not specified, it is enabled by default
    if asset_id not in assets_state:
        raise HTTPException(status_code=404, detail="Asset not found")

    async with asset_locks[asset_id]:
        state = assets_state[asset_id]
        is_human = state.get("type") == "human"

        if payload.enable:
            if state["status"] not in ["idle", "charging"]:
                detail_msg = "Asset must be idle to begin recovery" if is_human else "Asset must be idle to begin charging"
                raise HTTPException(status_code=409, detail=detail_msg)
            state["status"] = "charging"
            req_type = "RECOVER" if is_human else "CHARGE"
            req_desc = "Inicio de ciclo de recuperación"
            append_to_history(asset_id, req_type, req_desc)
        else:
            if state["status"] == "charging":
                state["status"] = "idle"
            req_type = "RECOVER" if is_human else "CHARGE"
            req_desc = "Interrupción de ciclo de recuperación"
            append_to_history(asset_id, req_type, req_desc)

    await notify_clients()
    if is_human:
        return {"status": "success", "recovering": payload.enable}
    return {"status": "success", "charging": payload.enable}


@app.post("/api/v1/asset/{asset_id:path}/action/{action_name}")
async def trigger_action(asset_id: str, action_name: str, payload: ActionRequest):
    if asset_id not in assets_state:
        raise HTTPException(status_code=404, detail="Asset not found")

    async with asset_locks[asset_id]:
        state = assets_state[asset_id]

        asset_type = state["type"]
        if action_name not in ASSET_TASKS.get(asset_type, {}):
            raise HTTPException(
                status_code=400,
                detail=f"Task '{action_name}' is not supported by {asset_type} assets. Allowed: {list(ASSET_TASKS[asset_type].keys())}"
            )

        if state["status"] != "idle":
            raise HTTPException(status_code=409, detail=f"Asset {asset_id} is busy/charging")

        required_battery = payload.duration * 2.0
        if state["battery"] < required_battery:
            err_msg = "Insufficient stamina for task" if asset_type == "human" else "Insufficient energy for task"
            raise HTTPException(status_code=400, detail=err_msg)

        state["status"] = "busy"
        state["current_task"] = action_name

        append_to_history(asset_id, "ACTION", f"Ejecución solicitada: {action_name.upper()} ({payload.duration}s)")

    await notify_clients()

    async def _run_simulation():
        try:
            for _ in range(payload.duration):
                await asyncio.sleep(1)
                async with asset_locks[asset_id]:
                    assets_state[asset_id]["battery"] -= 2.0
                await notify_clients()
        finally:
            async with asset_locks[asset_id]:
                assets_state[asset_id]["status"] = "idle"
                assets_state[asset_id]["current_task"] = None
            await notify_clients()

    simulation_task = asyncio.create_task(_run_simulation())

    try:
        await asyncio.shield(simulation_task)
    except asyncio.CancelledError:
        raise

    return {"status": "success", "asset": asset_id, "action_completed": action_name}


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("images/SMIA_favicon.ico")


if __name__ == "__main__":

    uvicorn.run(app, host="0.0.0.0", port=5000)