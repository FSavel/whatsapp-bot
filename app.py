import os
import logging
from flask import Flask, request, session, render_template, jsonify
from werkzeug.middleware.proxy_fix import ProxyFix
from whatsapp_bot import WhatsAppBot
from hr_data import HRDataManager

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default_secret_key_change_in_production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Initialize bot and data manager
bot = WhatsAppBot()
hr_manager = HRDataManager()

# Simple in-memory session storage for user states
user_sessions = {}

@app.route('/')
def dashboard():
    """Dashboard for monitoring bot activity"""
    try:
        # Get basic stats
        total_employees = hr_manager.get_total_employees()
        return render_template('dashboard.html', total_employees=total_employees)
    except Exception as e:
        logger.error(f"Error loading dashboard: {e}")
        return render_template('dashboard.html', total_employees=0, error=str(e))

@app.route('/webhook', methods=['POST'])
def webhook():
    """Twilio WhatsApp webhook endpoint"""
    try:
        # Get incoming message data
        incoming_msg = request.values.get('Body', '').strip().upper()
        from_number = request.values.get('From', '')
        
        logger.info(f"Received message: '{incoming_msg}' from {from_number}")
        
        # Process message through bot
        response = bot.process_message(incoming_msg, from_number, hr_manager, user_sessions)
        
        logger.info(f"Sending response: {response}")
        return response
        
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        error_response = bot.create_twiml_response("Erro interno. Tente novamente mais tarde.")
        return error_response

@app.route('/api/stats')
def api_stats():
    """API endpoint for bot statistics"""
    try:
        stats = {
            'total_employees': hr_manager.get_total_employees(),
            'bot_active': True
        }
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
