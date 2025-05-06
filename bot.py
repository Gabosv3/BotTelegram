from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ConversationHandler, ContextTypes, filters
)
from datetime import datetime

# Estados
NAME, SEG, STRUCTURE_TYPE, STRUCTURE, PARCELAS, START_TIME, END_TIME, ACTIVIDADES = range(8)

# Mapa de nombres
name_map = {
    "griselda": "Tec. Griselda Arely Romero de Palacios CEN-01088",
    "jeymi": "Tec. Jeymi Karina Castellano Soto CEN-01170",
    "susana": "Tec. Susana Stefhany Mena Manzano CEN-00982",
    "jennifer": "Tec. Jennifer Carolina Araujo Quintanilla CEN-01161",
    "rosana": "Tec. Rosana Concepcion Molina CEN-01052",
}

# Inicia conversación
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("¿Cuál es tu nombre?")
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name_input = update.message.text.strip().lower()
    if not name_input:
        await update.message.reply_text("Por favor ingresa un nombre válido.")
        return NAME

    name = name_map.get(name_input, f"{update.message.text} CEN-00857")
    context.user_data["nombre"] = name
    await update.message.reply_text("¿Cuál es tu SEG?")
    return SEG

async def get_seg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    seg = update.message.text.strip()
    if not seg:
        await update.message.reply_text("Por favor ingresa un SEG válido.")
        return SEG

    context.user_data["seg"] = seg
    await update.message.reply_text("¿Cuál es el tipo de estructura?")
    return STRUCTURE_TYPE

async def get_structure_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tipo = update.message.text.strip()
    if not tipo:
        await update.message.reply_text("Por favor ingresa un tipo de estructura válido.")
        return STRUCTURE_TYPE

    context.user_data["tipo_estructura"] = tipo
    await update.message.reply_text("¿Cuál es la estructura?")
    return STRUCTURE

async def get_structure(update: Update, context: ContextTypes.DEFAULT_TYPE):
    estructura = update.message.text.strip()
    if not estructura:
        await update.message.reply_text("Por favor ingresa una estructura válida.")
        return STRUCTURE

    context.user_data["estructura"] = estructura
    await update.message.reply_text("¿Número de parcelas?")
    return PARCELAS

async def get_parcelas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    parcelas = update.message.text.strip()
    if not parcelas.isdigit() or int(parcelas) <= 0:
        await update.message.reply_text("Por favor ingresa un número válido de parcelas (mayor a 0).")
        return PARCELAS

    context.user_data["parcelas"] = parcelas
    await update.message.reply_text("¿Hora de inicio? (Formato: HH:MM)")
    return START_TIME

async def get_start_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    inicio = update.message.text.strip()
    try:
        datetime.strptime(inicio, "%H:%M")
    except ValueError:
        await update.message.reply_text("Formato de hora no válido. Usa HH:MM (ej. 14:30).")
        return START_TIME

    context.user_data["inicio"] = inicio
    await update.message.reply_text("¿Hora de fin? (Formato: HH:MM)")
    return END_TIME

async def get_end_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    fin = update.message.text.strip()
    try:
        fin_dt = datetime.strptime(fin, "%H:%M")
        inicio_dt = datetime.strptime(context.user_data["inicio"], "%H:%M")
        if fin_dt <= inicio_dt:
            await update.message.reply_text("La hora de fin debe ser posterior a la hora de inicio.")
            return END_TIME
    except ValueError:
        await update.message.reply_text("Formato de hora no válido. Usa HH:MM (ej. 16:45).")
        return END_TIME

    context.user_data["fin"] = fin
    await update.message.reply_text("¿Qué actividades realizó? (Escriba uno o más separados por coma)\nEjemplo: Comercial, Pequeño Productor, pesca,economico , Patio, ninguno")
    return ACTIVIDADES

async def get_actividades(update: Update, context: ContextTypes.DEFAULT_TYPE):
    actividades = update.message.text.strip()
    if not actividades:
        await update.message.reply_text("Por favor ingresa al menos una actividad.")
        return ACTIVIDADES

    context.user_data["actividades"] = actividades

    # Calcular duración
    inicio = datetime.strptime(context.user_data["inicio"], "%H:%M")
    fin = datetime.strptime(context.user_data["fin"], "%H:%M")
    duracion = (fin - inicio).seconds // 60

    # Resumen
    resumen = (
        f"Equipo: Gabriel Antonio Castillo Alegria CEN-00857\n\n"
        f"{context.user_data['nombre']}\n"
        f"SEG: {context.user_data['seg']}\n\n"
        f"Tipo de estructura: {context.user_data['tipo_estructura']}\n"
        f"Estructura: {context.user_data['estructura']}\n"
        f"Tiempo promedio entrevista: {duracion} minutos\n"
        f"Principales Incidencias: 0\n"
        f"Nota: Tipo de estructura.\n"
        f"N° de parcelas: {context.user_data['parcelas']}\n\n"
        f"🟢 Actividades: {context.user_data['actividades']}"
    )

    await update.message.reply_text("✅ Registro completo:")
    await update.message.reply_text(resumen)
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Operación cancelada.")
    return ConversationHandler.END

def main():
    TOKEN = "AQUÍ_VA_TU_TOKEN"  # Reemplaza con tu token real

    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            SEG: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_seg)],
            STRUCTURE_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_structure_type)],
            STRUCTURE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_structure)],
            PARCELAS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_parcelas)],
            START_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_start_time)],
            END_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_end_time)],
            ACTIVIDADES: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_actividades)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    print("Bot corriendo...")
    app.run_polling()

if __name__ == "__main__":
    main()
