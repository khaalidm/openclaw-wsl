/**
 * WhatsApp Channel Integration for OpenClaw Agent
 * Uses whatsapp-web.js for WhatsApp Web automation
 */

require('dotenv').config();
const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const axios = require('axios');

// Configuration
const AGENT_API_URL = process.env.AGENT_API_URL || 'http://localhost:5000';
const SESSION_PATH = process.env.WHATSAPP_SESSION_PATH || './data/whatsapp-session';
const ALLOWED_NUMBERS = process.env.WHATSAPP_ALLOWED_NUMBERS 
    ? process.env.WHATSAPP_ALLOWED_NUMBERS.split(',').map(n => n.trim())
    : [];

console.log('╔════════════════════════════════════════╗');
console.log('║   OpenClaw WhatsApp Channel Starting   ║');
console.log('╚════════════════════════════════════════╝');
console.log('');

// Initialize WhatsApp client
const client = new Client({
    authStrategy: new LocalAuth({
        dataPath: SESSION_PATH
    }),
    puppeteer: {
        headless: true,
        args: [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--disable-accelerated-2d-canvas',
            '--no-first-run',
            '--no-zygote',
            '--disable-gpu'
        ]
    }
});

// QR Code event - scan this with WhatsApp
client.on('qr', (qr) => {
    console.log('\n📱 Scan this QR code with WhatsApp:\n');
    qrcode.generate(qr, { small: true });
    console.log('\n');
});

// Ready event
client.on('ready', () => {
    console.log('✅ WhatsApp client is ready!');
    console.log(`📞 Allowed numbers: ${ALLOWED_NUMBERS.length > 0 ? ALLOWED_NUMBERS.join(', ') : 'All numbers'}`);
    console.log(`🔗 Agent API: ${AGENT_API_URL}`);
    console.log('');
    console.log('Waiting for messages...');
});

// Authentication event
client.on('authenticated', () => {
    console.log('🔐 WhatsApp authenticated successfully');
});

// Auth failure event
client.on('auth_failure', (message) => {
    console.error('❌ WhatsApp authentication failed:', message);
});

// Disconnected event
client.on('disconnected', (reason) => {
    console.log('📴 WhatsApp disconnected:', reason);
    console.log('Attempting to reconnect...');
    client.initialize();
});

/**
 * Check if a number is allowed to interact with the bot
 */
function isAllowedNumber(number) {
    if (ALLOWED_NUMBERS.length === 0) {
        return true; // Allow all if no restrictions
    }
    return ALLOWED_NUMBERS.some(allowed => number.includes(allowed));
}

/**
 * Send message to the Python agent API
 */
async function sendToAgent(message, userId) {
    try {
        const response = await axios.post(`${AGENT_API_URL}/api/message`, {
            message: message,
            user_id: userId
        }, {
            timeout: 60000 // 60 second timeout
        });
        
        return response.data;
    } catch (error) {
        console.error('Error sending to agent:', error.message);
        return {
            text: "I'm sorry, I encountered an error. Please try again.",
            success: false,
            error: error.message
        };
    }
}

/**
 * Format response for WhatsApp
 */
function formatResponse(response) {
    let text = response.text || 'No response generated.';
    
    // Add model indicator if available
    if (response.model && response.model !== 'system') {
        const modelEmoji = response.model === 'gemini' ? '🌟' : '🦙';
        text = `${text}\n\n_${modelEmoji} ${response.model}_`;
    }
    
    return text;
}

// Message event - handle incoming messages
client.on('message', async (msg) => {
    // Ignore messages from groups (optional - remove if you want group support)
    if (msg.from.includes('@g.us')) {
        return;
    }
    
    // Get sender's number
    const senderNumber = msg.from.replace('@c.us', '');
    
    // Check if allowed
    if (!isAllowedNumber(senderNumber)) {
        console.log(`⚠️ Blocked message from: ${senderNumber}`);
        return;
    }
    
    const messageBody = msg.body.trim();
    
    // Ignore empty messages
    if (!messageBody) {
        return;
    }
    
    console.log(`📨 Message from ${senderNumber}: ${messageBody.substring(0, 50)}...`);
    
    // Show typing indicator
    const chat = await msg.getChat();
    await chat.sendStateTyping();
    
    try {
        // Send to agent
        const response = await sendToAgent(messageBody, senderNumber);
        
        // Format and send response
        const formattedResponse = formatResponse(response);
        await msg.reply(formattedResponse);
        
        console.log(`✅ Replied to ${senderNumber} using ${response.model || 'unknown'}`);
    } catch (error) {
        console.error('Error processing message:', error);
        await msg.reply("I'm sorry, something went wrong. Please try again.");
    }
});

// Error handling
client.on('error', (error) => {
    console.error('WhatsApp client error:', error);
});

// Start the client
console.log('🚀 Initializing WhatsApp client...');
client.initialize();

// Graceful shutdown
process.on('SIGINT', async () => {
    console.log('\nShutting down WhatsApp client...');
    await client.destroy();
    process.exit(0);
});
