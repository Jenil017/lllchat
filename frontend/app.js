// Configuration
const API_BASE_URL = 'http://localhost:8000';
const WS_BASE_URL = 'ws://localhost:8000';

// State
let socket = null;
let token = localStorage.getItem('jwt_token');
let currentUser = null;
let reconnectTimeout = null;
let heartbeatInterval = null;
let typingTimeout = null;

// DOM Elements
const authModal = document.getElementById('authModal');
const chatContainer = document.getElementById('chatContainer');
const authForm = document.getElementById('authForm');
const loginTab = document.getElementById('loginTab');
const registerTab = document.getElementById('registerTab');
const authTitle = document.getElementById('authTitle');
const authSubmit = document.getElementById('authSubmit');
const usernameField = document.getElementById('usernameField');
const authError = document.getElementById('authError');
const messagesContainer = document.getElementById('messagesContainer');
const messageInput = document.getElementById('messageInput');
const sendBtn = document.getElementById('sendBtn');
const logoutBtn = document.getElementById('logoutBtn');
const usersList = document.getElementById('usersList');
const onlineCount = document.getElementById('onlineCount');
const currentUsername = document.getElementById('currentUsername');
const typingIndicator = document.getElementById('typingIndicator');
const connectionStatus = document.getElementById('connectionStatus');
const mobileMenuToggle = document.getElementById('mobileMenuToggle');
const mobileOverlay = document.getElementById('mobileOverlay');
const sidebar = document.querySelector('.sidebar');

let isLoginMode = true;

// Initialize App
function init() {
    if (token) {
        loadCurrentUser();
    } else {
        showAuthModal();
    }

    setupEventListeners();
}

// Setup Event Listeners
function setupEventListeners() {
    // Auth tabs
    loginTab.addEventListener('click', () => switchToLogin());
    registerTab.addEventListener('click', () => switchToRegister());

    // Auth form
    authForm.addEventListener('submit', handleAuth);

    // Message input
    messageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

    messageInput.addEventListener('input', () => {
        if (socket && socket.readyState === WebSocket.OPEN) {
            sendTypingIndicator();
        }
    });

    // Send button
    sendBtn.addEventListener('click', sendMessage);

    // Logout
    logoutBtn.addEventListener('click', logout);

    // Mobile menu toggle
    if (mobileMenuToggle) {
        mobileMenuToggle.addEventListener('click', toggleMobileMenu);
    }

    if (mobileOverlay) {
        mobileOverlay.addEventListener('click', closeMobileMenu);
    }
}

// Mobile Menu Functions
function toggleMobileMenu() {
    if (sidebar) {
        sidebar.classList.toggle('show');
        mobileOverlay.classList.toggle('show');
    }
}

function closeMobileMenu() {
    if (sidebar) {
        sidebar.classList.remove('show');
        mobileOverlay.classList.remove('show');
    }
}

// Auth UI Functions
function switchToLogin() {
    isLoginMode = true;
    loginTab.classList.add('active');
    registerTab.classList.remove('active');
    authTitle.textContent = 'Login';
    authSubmit.textContent = 'Login';
    usernameField.style.display = 'none';
    document.getElementById('username').removeAttribute('required');
}

function switchToRegister() {
    isLoginMode = false;
    registerTab.classList.add('active');
    loginTab.classList.remove('active');
    authTitle.textContent = 'Register';
    authSubmit.textContent = 'Register';
    usernameField.style.display = 'block';
    document.getElementById('username').setAttribute('required', 'required');
}

function showAuthModal() {
    authModal.style.display = 'flex';
    chatContainer.style.display = 'none';
}

function hideAuthModal() {
    authModal.style.display = 'none';
    chatContainer.style.display = 'flex';
}

function showError(message) {
    authError.textContent = message;
    authError.classList.add('show');
    setTimeout(() => {
        authError.classList.remove('show');
    }, 5000);
}

// Authentication
async function handleAuth(e) {
    e.preventDefault();

    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const username = document.getElementById('username').value;

    try {
        if (isLoginMode) {
            await login(email, password);
        } else {
            await register(username, email, password);
        }
    } catch (error) {
        showError(error.message);
    }
}

async function register(username, email, password) {
    const response = await fetch(`${API_BASE_URL}/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, email, password })
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Registration failed');
    }

    // Auto login after successful registration
    await login(email, password);
}

async function login(email, password) {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Login failed');
    }

    const data = await response.json();
    token = data.access_token;
    localStorage.setItem('jwt_token', token);

    await loadCurrentUser();
}

async function loadCurrentUser() {
    try {
        const response = await fetch(`${API_BASE_URL}/auth/me`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (!response.ok) {
            if (response.status === 401) {
                logout();
                return;
            }
            throw new Error('Failed to load user');
        }

        currentUser = await response.json();
        currentUsername.textContent = `@${currentUser.username}`;

        hideAuthModal();
        await loadMessages();
        await loadOnlineUsers();
        connectWebSocket();

    } catch (error) {
        console.error('Error loading user:', error);
        logout();
    }
}

function logout() {
    if (socket) {
        socket.close();
    }

    localStorage.removeItem('jwt_token');
    token = null;
    currentUser = null;

    if (heartbeatInterval) {
        clearInterval(heartbeatInterval);
    }

    messagesContainer.innerHTML = '';
    usersList.innerHTML = '';

    showAuthModal();
}

// Messages
async function loadMessages() {
    try {
        const response = await fetch(`${API_BASE_URL}/messages?limit=50`);

        if (!response.ok) {
            throw new Error('Failed to load messages');
        }

        const data = await response.json();

        messagesContainer.innerHTML = '';

        // Display messages in reverse order (oldest first)
        data.messages.reverse().forEach(msg => {
            displayMessage(msg);
        });

        scrollToBottom();

    } catch (error) {
        console.error('Error loading messages:', error);
    }
}

function displayMessage(msg) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message';

    if (currentUser && msg.user_id === currentUser.id) {
        messageDiv.classList.add('own');
    }

    const time = new Date(msg.created_at).toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit'
    });

    messageDiv.innerHTML = `
        <div class="message-bubble">
            <div class="message-header">
                <span class="message-username">${msg.username}</span>
                <span class="message-time">${time}</span>
            </div>
            <div class="message-content">${escapeHtml(msg.content)}</div>
        </div>
    `;

    messagesContainer.appendChild(messageDiv);
}

function sendMessage() {
    const content = messageInput.value.trim();

    if (!content || !socket || socket.readyState !== WebSocket.OPEN) {
        return;
    }

    socket.send(JSON.stringify({
        event: 'send_message',
        data: { content }
    }));

    messageInput.value = '';
}

function sendTypingIndicator() {
    if (typingTimeout) {
        clearTimeout(typingTimeout);
    }

    typingTimeout = setTimeout(() => {
        if (socket && socket.readyState === WebSocket.OPEN) {
            socket.send(JSON.stringify({
                event: 'typing',
                data: {}
            }));
        }
    }, 300);
}

// Online Users
async function loadOnlineUsers() {
    try {
        const response = await fetch(`${API_BASE_URL}/users/online`);

        if (!response.ok) {
            throw new Error('Failed to load online users');
        }

        const users = await response.json();
        updateOnlineUsers(users);

    } catch (error) {
        console.error('Error loading online users:', error);
    }
}

function updateOnlineUsers(users) {
    usersList.innerHTML = '';
    onlineCount.textContent = users.length;

    users.forEach(user => {
        const li = document.createElement('li');
        li.textContent = user.username;
        usersList.appendChild(li);
    });
}

// WebSocket
function connectWebSocket() {
    if (socket) {
        socket.close();
    }

    updateConnectionStatus(false);

    socket = new WebSocket(`${WS_BASE_URL}/ws/chat?token=${token}`);

    socket.onopen = () => {
        console.log('WebSocket connected');
        updateConnectionStatus(true);

        // Start heartbeat
        if (heartbeatInterval) {
            clearInterval(heartbeatInterval);
        }
        heartbeatInterval = setInterval(() => {
            if (socket.readyState === WebSocket.OPEN) {
                socket.send(JSON.stringify({ event: 'ping', data: {} }));
            }
        }, 30000);
    };

    socket.onmessage = (event) => {
        try {
            const message = JSON.parse(event.data);
            handleWebSocketMessage(message);
        } catch (error) {
            console.error('Error parsing WebSocket message:', error);
        }
    };

    socket.onerror = (error) => {
        console.error('WebSocket error:', error);
        updateConnectionStatus(false);
    };

    socket.onclose = () => {
        console.log('WebSocket disconnected');
        updateConnectionStatus(false);

        if (heartbeatInterval) {
            clearInterval(heartbeatInterval);
        }

        // Auto reconnect after 3 seconds
        if (token && currentUser) {
            reconnectTimeout = setTimeout(() => {
                console.log('Attempting to reconnect...');
                connectWebSocket();
            }, 3000);
        }
    };
}

function handleWebSocketMessage(message) {
    const { event, data } = message;

    switch (event) {
        case 'new_message':
            displayMessage(data);
            scrollToBottom();
            break;

        case 'message_edited':
            // Update message UI (simplified - just reload for now)
            console.log('Message edited:', data);
            break;

        case 'message_deleted':
            // Remove message from UI (simplified - just log for now)
            console.log('Message deleted:', data);
            break;

        case 'user_joined':
            loadOnlineUsers();
            break;

        case 'user_left':
            loadOnlineUsers();
            break;

        case 'user_typing':
            showTypingIndicator(data.username);
            break;

        case 'pong':
            // Heartbeat response - ignore
            break;

        case 'error':
            console.error('WebSocket error:', data.message);
            alert(data.message);
            break;

        default:
            console.log('Unknown event:', event, data);
    }
}

function showTypingIndicator(username) {
    typingIndicator.textContent = `${username} is typing...`;

    setTimeout(() => {
        typingIndicator.textContent = '';
    }, 3000);
}

function updateConnectionStatus(connected) {
    if (connected) {
        connectionStatus.classList.remove('disconnected');
        connectionStatus.title = 'Connected';
        sendBtn.disabled = false;
    } else {
        connectionStatus.classList.add('disconnected');
        connectionStatus.title = 'Disconnected - Reconnecting...';
        sendBtn.disabled = true;
    }
}

// Utility Functions
function scrollToBottom() {
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', init);
