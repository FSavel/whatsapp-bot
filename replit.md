# Unitrans Xinavane WhatsApp Bot

## Overview

This is a Flask-based WhatsApp chatbot that integrates with Twilio's messaging service to provide employee self-service capabilities for Unitrans Xinavane. The bot allows employees to query their personal data, leave balances, and access internal communications through WhatsApp in both Portuguese and English.

## System Architecture

The application follows a simple monolithic architecture with:

- **Backend**: Flask web application
- **Messaging Integration**: Twilio WhatsApp API
- **Data Storage**: CSV file-based data storage
- **State Management**: In-memory user session management
- **Multi-language Support**: Portuguese and English localization

## Key Components

### Flask Application (`app.py`)
- Main application logic with webhook endpoint
- User state management for conversation flow
- CSV data loading and processing
- Multi-language support system

### Entry Point (`main.py`)
- Application startup script
- Development server configuration

### Data Layer
- CSV file (`dados_corrigido.csv`) containing employee records
- Pandas DataFrame for data manipulation
- ISO-8859-1 encoding support for Portuguese characters

### Webhook Handler
- `/webhook` endpoint for receiving Twilio messages
- TwiML response generation
- User session state tracking

## Data Flow

1. **Incoming Message**: WhatsApp message received via Twilio webhook
2. **User State Check**: System checks if user has existing session
3. **Language Selection**: New users choose preferred language (Portuguese/English)
4. **Menu Navigation**: Users navigate through service options:
   - Leave and absences balance
   - Personal data queries
   - Internal communications
5. **Data Query**: System queries CSV data based on user requests
6. **Response Generation**: TwiML response sent back through Twilio
7. **State Update**: User session state updated for conversation continuity

## External Dependencies

### Core Dependencies
- **Flask**: Web framework for handling HTTP requests
- **Twilio**: WhatsApp messaging integration
- **Pandas**: CSV data processing and manipulation

### Environment Variables
- `SESSION_SECRET`: Flask session encryption key (defaults to development key)

### Third-party Services
- **Twilio WhatsApp API**: Message routing and delivery
- **Webhook endpoint**: Requires publicly accessible URL for Twilio integration

## Deployment Strategy

### Development Environment
- Local Flask development server
- Debug mode enabled
- Host: 0.0.0.0 (all interfaces)
- Port: 5000

### Production Considerations
- Requires secure HTTPS endpoint for Twilio webhooks
- Environment-specific session secret configuration
- Error handling and logging for production stability
- Potential migration from CSV to database for scalability

### Data Requirements
- CSV file (`dados_corrigido.csv`) must be present in application root
- Employee data with worker numbers for lookup functionality
- Proper encoding handling for Portuguese characters

## Changelog
- July 04, 2025: Initial setup
- July 04, 2025: WhatsApp bot fully deployed and configured with Twilio webhook integration

## User Preferences

Preferred communication style: Simple, everyday language.