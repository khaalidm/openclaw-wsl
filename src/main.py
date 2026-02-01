"""
OpenClaw Agent - Main Entry Point
Flask API server that bridges WhatsApp and the AI agent
"""
import asyncio
import signal
import sys
import subprocess
import threading
from pathlib import Path

from flask import Flask, request, jsonify
from flask_cors import CORS
from loguru import logger

from src.config.settings import settings
from src.agent.core import get_agent


# Configure logging
logger.remove()
logger.add(
    sys.stderr,
    level=settings.log_level.upper(),
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>"
)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize agent
agent = get_agent()


def run_async(coro):
    """Helper to run async code in Flask context."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "agent": "openclaw",
        "models": {
            "ollama": settings.ollama_model,
            "gemini": settings.gemini_model if settings.gemini_api_key else None
        }
    })


@app.route('/api/message', methods=['POST'])
def handle_message():
    """
    Handle incoming messages from WhatsApp channel.
    
    Expected JSON body:
    {
        "message": "user's message",
        "user_id": "phone number or unique id"
    }
    """
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No JSON data provided"}), 400
    
    message = data.get("message")
    user_id = data.get("user_id", "anonymous")
    
    if not message:
        return jsonify({"error": "No message provided"}), 400
    
    logger.info(f"API request from {user_id}: {message[:50]}...")
    
    try:
        response = run_async(agent.process_message(message, user_id))
        return jsonify(response)
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        return jsonify({
            "text": "I encountered an error processing your request.",
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/clear', methods=['POST'])
def clear_history():
    """Clear conversation history for a user."""
    data = request.get_json()
    user_id = data.get("user_id") if data else None
    
    if not user_id:
        return jsonify({"error": "No user_id provided"}), 400
    
    agent.clear_history(user_id)
    return jsonify({"success": True, "message": f"History cleared for {user_id}"})


@app.route('/api/status', methods=['GET'])
def get_status():
    """Get agent status."""
    return jsonify({
        "agent": "openclaw",
        "models": {
            "ollama": {
                "model": settings.ollama_model,
                "host": settings.ollama_host
            },
            "gemini": {
                "model": settings.gemini_model,
                "configured": bool(settings.gemini_api_key)
            }
        },
        "config": {
            "complexity_threshold": settings.complexity_threshold,
            "max_history": settings.max_history_length
        },
        "active_conversations": len(agent.conversations)
    })


def start_whatsapp_channel():
    """Start the WhatsApp Node.js process in a separate thread."""
    whatsapp_path = Path(__file__).parent / "channels" / "whatsapp" / "index.js"
    
    if not whatsapp_path.exists():
        logger.warning("WhatsApp channel not found, skipping...")
        return
    
    logger.info("Starting WhatsApp channel...")
    
    try:
        process = subprocess.Popen(
            ["node", str(whatsapp_path)],
            cwd=Path(__file__).parent.parent,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        # Stream output
        for line in iter(process.stdout.readline, ''):
            print(f"[WhatsApp] {line.rstrip()}")
        
    except Exception as e:
        logger.error(f"Failed to start WhatsApp channel: {e}")


def main():
    """Main entry point."""
    logger.info("╔════════════════════════════════════════╗")
    logger.info("║       OpenClaw Agent Starting          ║")
    logger.info("╚════════════════════════════════════════╝")
    
    # Start WhatsApp channel in background thread
    whatsapp_thread = threading.Thread(target=start_whatsapp_channel, daemon=True)
    whatsapp_thread.start()
    
    # Give WhatsApp a moment to start
    import time
    time.sleep(2)
    
    # Start Flask server
    logger.info(f"Starting API server on http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)


if __name__ == "__main__":
    main()
