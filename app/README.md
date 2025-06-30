# Bot Telegram MVP - Guía de Instalación

## 📋 Requisitos Previos

- **Python 3.8+** instalado
- **Bot Token** de Telegram (obtenido de @BotFather)
- **Terminal/CMD** con permisos de instalación

## 🚀 Instalación Rápida

### 1. Preparar el Entorno

```bash
# Crear directorio del proyecto
mkdir telegram_bot_mvp
cd telegram_bot_mvp

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

### 2. Instalar Dependencias

```bash
# Instalar paquetes requeridos
pip install -r requirements.txt
```

### 3. Configurar Variables de Entorno

Crear archivo `.env` en la raíz del proyecto:

```env
# Bot Configuration
BOT_TOKEN=tu_bot_token_aqui
DEBUG=True

# Database
DB_PATH=data/bot_database.db

# Admin
ADMIN_USER_ID=tu_user_id_telegram
```

**⚠️ IMPORTANTE:** Reemplaza `tu_bot_token_aqui` con el token real de tu bot.

### 4. Estructura de Carpetas

El proyecto debe tener esta estructura:

```
telegram_bot/
├── config/
│   ├── __init__.py
│   ├── settings.py
│   └── database_config.py
├── database/
│   ├── __init__.py
│   ├── models.py
│   └── connection.py
├── middlewares/
│   ├── __init__.py
│   ├── auth_middleware.py
│   ├── session_middleware.py
│   └── admin_middleware.py
├── handlers/
│   ├── __init__.py
│   ├── start_handlers.py
│   ├── profile_handlers.py
│   ├── daily_gift_handlers.py
│   ├── help_handlers.py
│   └── admin_handlers.py
├── services/
│   ├── __init__.py
│   ├── user_service.py
│   ├── gift_service.py
│   └── admin_service.py
├── utils/
│   ├── __init__.py
│   ├── keyboards.py
│   └── messages.py
├── data/
├── .env
├── requirements.txt
└── main.py
```

### 5. Crear Carpeta de Datos

```bash
mkdir data
```

## ▶️ Ejecutar el Bot

```bash
# Activar entorno virtual (si no está activo)
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate     # Windows

# Ejecutar el bot
python main.py
```

## 🔧 Configuración Avanzada

### Obtener tu User ID de Telegram

1. Envía `/start` a @userinfobot
2. Copia el número de ID que aparece
3. Úsalo en `ADMIN_USER_ID` en el archivo `.env`

### Comandos Administrativos

Una vez configurado como admin:
- `/admin` - Panel de administración
- `/broadcast` - Enviar mensajes masivos (responder a un mensaje)

## 📱 Comandos de Usuario

- `/start` - Iniciar bot y registro
- `/profile` - Ver perfil y estadísticas
- `/daily` - Reclamar regalo diario
- `/help` - Ayuda y comandos

## 🐛 Solución de Problemas

### Error: "Token inválido"
- Verifica que el token en `.env` sea correcto
- Asegúrate de no tener espacios extra

### Error: "No se puede crear la base de datos"
- Verifica que la carpeta `data/` exista
- Revisa permisos de escritura

### Error: "Módulo no encontrado"
- Verifica que el entorno virtual esté activado
- Ejecuta `pip install -r requirements.txt` nuevamente

## 📊 Funcionalidades Incluidas

### ✅ Funcionalidades Activas
- Sistema de usuarios y registro automático
- Menú principal navegable
- Sistema básico de puntos (besitos)
- Regalos diarios con cooldown
- Panel de administración básico
- Sistema de ayuda contextual

### 🔜 Funcionalidades Futuras
- Sistema de misiones y tareas
- Gamificación avanzada con niveles
- Sistema de narrativa (LorePieces)
- Minijuegos interactivos
- Sistema de subastas VIP
- Notificaciones automáticas

## 🚀 Despliegue en Producción

Para desplegar en servidor:

1. Cambia `DEBUG=False` en `.env`
2. Usa un gestor de procesos como `systemd` o `supervisor`
3. Configura logs persistentes
4. Implementa backup automático de la base de datos

## 📞 Soporte

Si encuentras problemas:
1. Revisa los logs en la consola
2. Verifica la configuración del archivo `.env`
3. Asegúrate de que todas las dependencias estén instaladas

**¡Bot MVP listo para usar! 🎉**