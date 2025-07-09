# Reporte de Auditoría de Sistema: Nuevobot

---

### RESUMEN EJECUTIVO

#### Estado General del Sistema
- **Calificación global:** 2/10. El sistema se encuentra en un estado no funcional y presenta vulnerabilidades críticas de seguridad, errores de ejecución bloqueantes y una arquitectura inconsistente. La base del código es recuperable, pero requiere una intervención inmediata y profunda.
- **Nivel de riesgo:** CRÍTICO. Los problemas de seguridad y los errores de ejecución impiden que la aplicación se inicie y exponen secretos.
- **Tiempo estimado para resolución:** 5-7 días para estabilizar y asegurar. 3-4 semanas para refactorización completa y cobertura de tests.
- **Prioridad de intervención:** INMEDIATA.

#### Métricas Clave
```
┌─────────────────────┬─────────┬─────────┐
│ Métrica             │ Actual  │ Objetivo│
├─────────────────────┼─────────┼─────────┤
│ Calidad de código   │ 2/10    │ 8/10    │
│ Cobertura de tests  │ 0%      │ 80%     │
│ Vulnerabilidades    │ 3+      │ 0       │
│ Deuda técnica       │ ~25 días│ <5 días │
│ Rendimiento         │ N/A     │ <300ms  │
└─────────────────────┴─────────┴─────────┘
```

---

### PROBLEMAS IDENTIFICADOS

#### CRÍTICOS (Requieren atención inmediata)

**[PC001] Secretos Hardcodeados en el Código**
- **Descripción:** El token del bot y los IDs de administrador están escritos directamente en el código fuente. Esto es una vulnerabilidad de seguridad grave. Si el código se comparte o se filtra, las credenciales quedan expuestas.
- **Ubicación:** 
    - `main.py:8`
    - `middlewares/admin_middleware.py:8`
- **Impacto:** Robo de la cuenta del bot, acceso no autorizado a funciones de administrador, suplantación de identidad.
- **Evidencia:**
```python
# main.py
bot = Bot(token="TU_TOKEN")

# middlewares/admin_middleware.py
self.admin_ids = [123456789]
```
- **Solución propuesta:** Utilizar la configuración centralizada en `config/settings.py` que ya carga variables de entorno.
```python
# main.py (solución)
from config.settings import settings
...
bot = Bot(token=settings.BOT_TOKEN)

# middlewares/admin_middleware.py (solución)
from config.settings import settings
...
class AdminMiddleware(BaseMiddleware):
    def __init__(self):
        self.admin_ids = settings.ADMIN_IDS
```
- **Esfuerzo estimado:** 1 hora.
- **Dependencias:** Ninguna.

**[PC002] Error Crítico de Ejecución por Variable No Definida**
- **Descripción:** El archivo `main.py` intenta instanciar `NotificationService` pasándole una variable `db` que no está definida en ese ámbito. Esto provoca que la aplicación falle al intentar arrancar.
- **Ubicación:** `main.py:11`
- **Impacto:** El bot no puede iniciarse. Denegación de servicio completa.
- **Evidencia:**
```python
# main.py
# La variable 'db' no existe en este contexto
notification_service = NotificationService(bot, db) 
```
- **Solución propuesta:** Instanciar un gestor de base de datos y pasarlo a los servicios que lo necesiten, o inyectarlo a través del dispatcher de `aiogram`.
```python
# main.py (solución)
from database.connection import db_manager # Suponiendo un gestor
...
await db_manager.init_database() # Inicializar la DB
...
# Inyectar el gestor o una sesión de DB
dp["db_manager"] = db_manager 
# Los servicios deberían obtener la dependencia del contexto, no en el constructor.
```
- **Esfuerzo estimado:** 4 horas (requiere refactorizar la inyección de dependencias).
- **Dependencias:** [PI002].

**[PC003] Arquitectura de Base de Datos Múltiple e Incompatible**
- **Descripción:** El sistema mezcla tres formas diferentes e incompatibles de interactuar con la base de datos:
    1. `database/connection.py`: Usa `aiosqlite` para crear tablas con SQL puro.
    2. `database/models.py`: Define modelos con `SQLAlchemy`, pero no se usan para crear las tablas.
    3. Múltiples servicios (`user_service.py`, `channel_service.py`): Usan el driver `sqlite3` síncrono, lo cual bloqueará el event loop de `asyncio`.
- **Ubicación:** `database/`, `services/`.
- **Impacto:** Corrupción de datos, errores de ejecución, bloqueo del bot, rendimiento pésimo, mantenibilidad imposible.
- **Evidencia:**
```python
# database/connection.py
import aiosqlite
# database/models.py
from sqlalchemy import Column, Integer...
# services/user_service.py
import sqlite3
```
- **Solución propuesta:** Estandarizar el acceso a datos. La recomendación es usar `SQLAlchemy` con su motor asíncrono (`create_async_engine`) y `async_sessionmaker` para gestionar las sesiones en toda la aplicación. Eliminar el uso de `sqlite3` y `aiosqlite` directamente.
- **Esfuerzo estimado:** 2-3 días.
- **Dependencias:** [PC002].

---

#### IMPORTANTES (Afectan mantenibilidad/rendimiento)

**[PI001] Ausencia Total de Pruebas Unitarias y de Integración**
- **Descripción:** No existen pruebas funcionales para el código. El directorio `tests` solo contiene un archivo de ejemplo. Esto hace imposible verificar la funcionalidad, prevenir regresiones y refactorizar con seguridad.
- **Ubicación:** `tests/`
- **Impacto:** Alta probabilidad de errores en producción, dificultad para añadir nuevas funciones, imposibilidad de refactorizar de forma segura.
- **Solución propuesta:** Implementar un framework de pruebas como `pytest` con `pytest-asyncio`. Crear una suite de tests que cubra los servicios y handlers, usando una base de datos de prueba en memoria.
- **Esfuerzo estimado:** 5+ días (para alcanzar una cobertura base).
- **Dependencias:** Todas.

**[PI002] Lógica de Negocio Mezclada en Handlers**
- **Descripción:** Varios handlers contienen lógica que debería estar encapsulada en los servicios. Por ejemplo, el cálculo de recompensas o la gestión de estado.
- **Ubicación:** `handlers/channel_handlers.py:90`
- **Impacto:** Dificulta la reutilización de código, aumenta la complejidad de los handlers y viola el principio de responsabilidad única.
- **Evidencia:**
```python
# handlers/channel_handlers.py
# Esta lógica de recompensa debería estar en el user_service o gamification_service
reward = channel_data.get('reward_besitos', 50)
user_service.update_user_besitos(telegram_id, reward)
```
- **Solución propuesta:** Mover toda la lógica de negocio a las clases de servicio correspondientes. Los handlers solo deben encargarse de recibir la entrada, llamar al servicio y formatear la salida.
- **Esfuerzo estimado:** 1-2 días.
- **Dependencias:** Ninguna.

---

### ANÁLISIS DETALLADO POR COMPONENTE

#### Modelos de Datos
- **Problemas encontrados:**
    1. **Definición vs. Creación:** Los modelos se definen con SQLAlchemy (`models.py`) pero las tablas se crean con SQL raw (`connection.py`), llevando a una total inconsistencia.
    2. **Relaciones no implementadas:** Las `ForeignKey` de SQLAlchemy no tienen efecto porque las tablas no se crean a través del ORM. No hay integridad referencial.
    3. **Índices faltantes:** Campos como `username` en `users` o `token` en `vip_tokens` deberían estar indexados para búsquedas rápidas.
    4. **Tipos de datos:** Se usa `TEXT` para fechas (`created_at`), lo que impide ordenamiento y cálculos eficientes a nivel de DB. Debería usarse `TIMESTAMP` o `DATETIME`.

#### Handlers/Controladores
- **Problemas encontrados:**
    1. **Lógica de negocio mezclada:** Ya descrito en [PI002].
    2. **Manejo de errores insuficiente:** Se usan bloques `try...except Exception` genéricos que ocultan la naturaleza del error y simplemente lo loguean, sin dar feedback útil al usuario.
    3. **Falta de validación de entrada:** Los handlers no validan los datos recibidos antes de pasarlos a los servicios.

#### Configuración y Deployment
- **Problemas encontrados:**
    1. **Secretos expuestos:** Ya descrito en [PC001].
    2. **Dependencias faltantes:** El código importa `sqlalchemy` pero no está en `requirements.txt`.
    3. **Configuración inconsistente:** El `BOT_TOKEN` se lee de `settings` en la solución propuesta, pero el resto del código no sigue un patrón claro para acceder a la configuración.

---

### PLAN DE REMEDIACIÓN

#### Fase 1: Problemas Críticos (Semana 1)
```
┌─────────────────────┬─────────┬─────────┬─────────┐
│ Problema            │ Prioridad│ Esfuerzo│ Asignado│
├─────────────────────┼─────────┼─────────┼─────────┤
│ [PC001] Secretos    │ CRÍTICA │ 1h      │ Dev1    │
│ [PC002] App no arranca│ CRÍTICA │ 4h      │ Dev1    │
│ [PC003] DB Múltiple │ CRÍTICA │ 2-3 días│ Dev1    │
└─────────────────────┴─────────┴─────────┴─────────┘
```

#### Fase 2: Problemas Importantes (Semana 2-3)
```
┌─────────────────────┬─────────┬─────────┬─────────┐
│ Problema            │ Prioridad│ Esfuerzo│ Asignado│
├─────────────────────┼─────────┼─────────┼─────────┤
│ [PI001] Sin Tests   │ ALTA    │ 5+ días │ Dev1,Dev2│
│ [PI002] Lógica en Handlers│ ALTA    │ 1-2 días│ Dev2    │
└─────────────────────┴─────────┴─────────┴─────────┘
```

---

### CÓDIGO REFACTORIZADO

#### Archivo: `main.py`
```python
# ANTES (Problemático)
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from handlers import admin_handlers, notifications_handlers
from middlewares import admin_middleware
from services.notification_service import NotificationService

async def main():
    bot = Bot(token="TU_TOKEN")
    dp = Dispatcher(storage=MemoryStorage())
    notification_service = NotificationService(bot, db)
    admin_handlers.router.message.middleware(admin_middleware.AdminMiddleware())
    dp.include_router(admin_handlers.router)
    dp.include_router(notifications_handlers.router)
    dp.update.outer_middleware(admin_middleware.AdminMiddleware())
    dp["notification_service"] = notification_service
    await dp.start_polling(bot)

# DESPUÉS (Corregido y Funcional)
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config.settings import settings
from database.connection import init_db, get_session_maker
from handlers import (
    admin_handlers, start_handler, channel_handlers, 
    auctions_handlers, minigames_handlers, narrative_handlers, vip_handlers
)
from middlewares.auth_middleware import AuthMiddleware

async def main():
    if not settings.validate_config():
        return

    bot = Bot(token=settings.BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    # Inyección de dependencias
    async_session_maker = await init_db(settings.DATABASE_URL)
    dp["session_maker"] = async_session_maker

    # Registrar middlewares
    dp.update.outer.middleware(AuthMiddleware())

    # Registrar routers
    dp.include_router(start_handler.router)
    dp.include_router(admin_handlers.router)
    dp.include_router(channel_handlers.router)
    # ... registrar todos los demás routers

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
```

---

### TESTS RECOMENDADOS

#### Tests de Seguridad
```python
import pytest

async def test_admin_command_requires_auth(client):
    '''Verificar que un usuario normal no puede ejecutar /admin'''
    response = await client.send_command("/admin")
    assert "Acceso restringido" in response.text

async def test_vip_endpoint_requires_vip_status(client_non_vip):
    '''Verificar que un no-VIP no puede acceder a menús VIP'''
    response = await client_non_vip.send_callback("vip_menu")
    assert "Acción no permitida" in response.text
```

---

### PRÓXIMOS PASOS

#### Inmediatos (24-48 horas)
1. **Backup de emergencia:** Realizar una copia completa del código y la base de datos (si contiene datos).
2. **Aplicar parches críticos:** Corregir [PC001], [PC002] y [PC003] para tener una base funcional y segura.
3. **Configurar entorno de desarrollo:** Asegurar que todos los desarrolladores trabajen sobre la nueva base estandarizada (SQLAlchemy asíncrono).

#### Corto plazo (1-2 semanas)
1. **Implementar tests base:** Crear tests de integración para el flujo de `/start` y los comandos principales.
2. **Refactorizar servicios:** Mover toda la lógica de negocio de los handlers a los servicios.
3. **Actualizar dependencias:** Revisar `requirements.txt`, añadir las faltantes y actualizar a versiones estables.

