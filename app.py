import os
import logging
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default_secret_key_for_development")

# Global variables for data and user state
df = None
estado_usuarios = {}

def load_csv_data():
    """Load CSV data with proper encoding"""
    global df
    try:
        df = pd.read_csv("dados_corrigido.csv", encoding="ISO-8859-1")
        df['Numero do trabalhador'] = df['Numero do trabalhador'].astype(str).str.strip()
        logging.info(f"CSV loaded successfully with {len(df)} records")
    except Exception as e:
        logging.error(f"Error loading CSV: {e}")
        df = pd.DataFrame()  # Empty dataframe as fallback

@app.route("/webhook", methods=["POST"])
def webhook():
    """Handle incoming WhatsApp messages via Twilio webhook"""
    incoming_msg = request.values.get("Body", "").strip()
    user_number = request.values.get("From", "")
    
    logging.info(f"Received message from {user_number}: {incoming_msg}")
    
    response = MessagingResponse()
    msg = response.message()
    
    # Initialize user state if not exists
    if user_number not in estado_usuarios:
        msg.body("Olá, bem vindo à Unitrans Xinavane.\nHello, welcome to Unitrans Xinavane.\n\n1. Português\n2. English")
        estado_usuarios[user_number] = {"etapa": "escolher_idioma"}
        return str(response)
    
    estado = estado_usuarios[user_number]
    
    # Language selection
    if estado["etapa"] == "escolher_idioma":
        if incoming_msg == "1":
            estado["idioma"] = "pt"
        elif incoming_msg == "2":
            estado["idioma"] = "en"
        else:
            msg.body("Por favor escolha:\n1. Português\n2. English")
            return str(response)
        
        estado["etapa"] = "menu"
        if estado["idioma"] == "pt":
            msg.body("Certo, selecione uma das opções abaixo para obter assistência.\n1. Saldo de férias e faltas\n2. Dados Pessoais\n3. Comunicação Interna\n0. Voltar")
        else:
            msg.body("Alright, select one of the options below for assistance.\n1. Leave and absences\n2. Personal Data\n3. Internal Communication\n0. Back")
        return str(response)
    
    # Main menu
    if estado["etapa"] == "menu":
        if incoming_msg == "0":
            estado["etapa"] = "escolher_idioma"
            msg.body("Voltando ao menu inicial...\n\n1. Português\n2. English")
            return str(response)
        
        if incoming_msg in ["1", "2", "3"]:
            estado["opcao"] = incoming_msg
            estado["etapa"] = "pedir_matricula"
            if estado["idioma"] == "pt":
                msg.body("Certo, envie seu número de trabalhador.")
            else:
                msg.body("Sure, please send your employee number.")
            return str(response)
        else:
            if estado["idioma"] == "pt":
                msg.body("Opção inválida. Tente novamente.\n1. Saldo de férias e faltas\n2. Dados Pessoais\n3. Comunicação Interna\n0. Voltar")
            else:
                msg.body("Invalid option. Try again.\n1. Leave and absences\n2. Personal Data\n3. Internal Communication\n0. Back")
            return str(response)
    
    # Employee number input
    if estado["etapa"] == "pedir_matricula":
        matricula = incoming_msg.strip()
        
        # Check if CSV is loaded
        if df is None or df.empty:
            if estado["idioma"] == "pt":
                msg.body("Erro: Dados não disponíveis. Tente novamente mais tarde.")
            else:
                msg.body("Error: Data not available. Please try again later.")
            return str(response)
        
        resultado = df[df['Numero do trabalhador'] == matricula]
        
        if resultado.empty:
            if estado["idioma"] == "pt":
                msg.body("Número de trabalhador não encontrado. Verifique e tente novamente.")
            else:
                msg.body("Employee number not found. Please check and try again.")
            return str(response)
        
        trabalhador = resultado.iloc[0]
        idioma = estado["idioma"]
        opcao = estado["opcao"]
        
        if idioma == "pt":
            if opcao == "1":
                msg.body(
                    f"Olá {trabalhador['Nome']} 👋\n"
                    f"✅ Férias disponíveis: {trabalhador['Ferias']} dias\n"
                    f"❌ Faltas registradas: {trabalhador['Faltas']} dias\n\n"
                    "Caro colaborador, Justifique suas faltas em até 3 dias úteis, entregando ao RH os seguintes documentos:\n"
                    "- Atestado médico, em caso de doença;\n"
                    "- Certidão de óbito + declaração do bairro;\n"
                    "- Certidão de casamento, quando aplicável;\n"
                    "- Outros, conforme orientação do RH.\n\n0. Voltar"
                )
            elif opcao == "2":
                msg.body(
                    f"🪪 Numero de BI: {trabalhador['Numero de BI']}\n"
                    f"🚘 Carta de Condução: {trabalhador['Carta de Conducao']}\n"
                    f"📅 Contrato: {trabalhador['Inicio de Contrato']} até {trabalhador['Fim de contrato']}\n\n"
                    "Caro colaborador, atualize os seus documentos enviando-os ao departamento de RH.\n\n0. Voltar"
                )
            else:
                msg.body("📢 Caros Gestores de Linha, as folhas de salário (pay slips) já estão disponíveis. Podem levantá-las no departamento de RH.\n\n0. Voltar")
        else:
            if opcao == "1":
                msg.body(
                    f"Hello {trabalhador['Nome']} 👋\n"
                    f"✅ Available leave: {trabalhador['Ferias']} days\n"
                    f"❌ Recorded absences: {trabalhador['Faltas']} days\n\n"
                    "Dear colleague, please justify your absences within 3 working days by submitting:\n"
                    "- Medical certificate (if sick);\n"
                    "- Death certificate + bairro statement (if applicable);\n"
                    "- Marriage certificate (if applicable);\n"
                    "- Other documents as required by HR.\n\n0. Back"
                )
            elif opcao == "2":
                msg.body(
                    f"🪪 ID Number: {trabalhador['Numero de BI']}\n"
                    f"🚘 Driving License: {trabalhador['Carta de Conducao']}\n"
                    f"📅 Contract: {trabalhador['Inicio de Contrato']} to {trabalhador['Fim de contrato']}\n\n"
                    "Dear colleague, please update your documents with the HR department.\n\n0. Back"
                )
            else:
                msg.body("📢 Dear Line Managers, the payslips are now available. Please collect them at the HR department.\n\n0. Back")
        
        estado["etapa"] = "menu"
        return str(response)
    
    # Default response for unrecognized input
    if estado.get("idioma") == "pt":
        msg.body("Desculpe, não entendi. Envie '0' para voltar ao menu.")
    else:
        msg.body("Sorry, I didn't understand. Send '0' to return to the menu.")
    return str(response)

@app.route("/", methods=["GET"])
def index():
    """Basic endpoint to check if the webhook is working"""
    return "Unitrans Xinavane WhatsApp Bot is running! Use /webhook for Twilio integration."

@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "csv_loaded": df is not None and not df.empty,
        "total_employees": len(df) if df is not None else 0
    }

# Load CSV data when module is imported
load_csv_data()

if __name__ == "__main__":
    # Start the Flask app
    app.run(host="0.0.0.0", port=5000, debug=True)
