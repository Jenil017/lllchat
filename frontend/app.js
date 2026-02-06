// Configuration
const API_BASE_URL = `${window.location.protocol}//${window.location.host}`;
const WS_BASE_URL = `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}`;

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
const authSuccess = document.getElementById('authSuccess');
const messagesContainer = document.getElementById('messagesContainer');
const messageInput = document.getElementById('messageInput');
const sendBtn = document.getElementById('sendBtnIcon'); // Updated
const logoutBtn = document.getElementById('logoutBtn');
const usersList = document.getElementById('usersList');
const onlineCount = document.getElementById('onlineCount');
const activeCountText = document.getElementById('activeCountText');
const currentUsernameDisplay = document.getElementById('currentUsernameDisplay');
const typingIndicator = document.getElementById('typingIndicator');

// New OTP elements
const emailField = document.getElementById('emailField');
const passwordField = document.getElementById('passwordField');
const otpField = document.getElementById('otpField');
const otpInput = document.getElementById('otp');
const resendBtn = document.getElementById('resendBtn');

let isLoginMode = true;
let isVerificationMode = false;
let pendingEmail = '';

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

    // Resend OTP
    resendBtn.addEventListener('click', handleResendOTP);

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
}

// Auth UI Functions
function switchToLogin() {
    isLoginMode = true;
    isVerificationMode = false;
    loginTab.classList.add('active');
    registerTab.classList.remove('active');
    authTitle.textContent = 'Login';
    authSubmit.textContent = 'Login';
    usernameField.style.display = 'none';
    emailField.style.display = 'block';
    passwordField.style.display = 'block';
    otpField.style.display = 'none';
}

function switchToRegister() {
    isLoginMode = false;
    isVerificationMode = false;
    registerTab.classList.add('active');
    loginTab.classList.remove('active');
    authTitle.textContent = 'Register';
    authSubmit.textContent = 'Register';
    usernameField.style.display = 'block';
    emailField.style.display = 'block';
    passwordField.style.display = 'block';
    otpField.style.display = 'none';
}

function switchToVerification(email) {
    isVerificationMode = true;
    pendingEmail = email;
    authTitle.textContent = 'Verify Email';
    authSubmit.textContent = 'Verify OTP';
    usernameField.style.display = 'none';
    emailField.style.display = 'none';
    passwordField.style.display = 'none';
    otpField.style.display = 'block';
    otpInput.value = '';
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
    if (authSuccess) authSuccess.classList.remove('show');
    setTimeout(() => {
        authError.classList.remove('show');
    }, 5000);
}

function showSuccess(message) {
    if (authSuccess) {
        authSuccess.textContent = message;
        authSuccess.classList.add('show');
        authError.classList.remove('show');
        setTimeout(() => {
            authSuccess.classList.remove('show');
        }, 5000);
    }
}

// Authentication
async function handleAuth(e) {
    e.preventDefault();

    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const username = document.getElementById('username').value;
    const otp = otpInput.value;

    try {
        if (isVerificationMode) {
            await verifyOTP(pendingEmail, otp);
        } else if (isLoginMode) {
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

    const data = await response.json();
    switchToVerification(data.email);
    showSuccess('Registration successful! Please check your email for the OTP.');
}

async function verifyOTP(email, otp) {
    const response = await fetch(`${API_BASE_URL}/auth/verify-otp?email=${encodeURIComponent(email)}&otp=${encodeURIComponent(otp)}`, {
        method: 'POST'
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Verification failed');
    }

    const data = await response.json();
    token = data.access_token;
    localStorage.setItem('jwt_token', token);

    await loadCurrentUser();
    showSuccess('Email verified successfully!');
}

async function handleResendOTP() {
    if (!pendingEmail) return;

    try {
        const response = await fetch(`${API_BASE_URL}/auth/send-otp?email=${encodeURIComponent(pendingEmail)}`, {
            method: 'POST'
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to resend OTP');
        }

        showSuccess('New OTP sent to your email.');
    } catch (error) {
        showError(error.message);
    }
}

async function login(email, password) {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
    });

    if (!response.ok) {
        const error = await response.json();
        if (response.status === 403 && error.detail.includes('verify')) {
            switchToVerification(email);
            throw new Error(error.detail);
        }
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
        currentUsernameDisplay.textContent = currentUser.username;

        // Set user avatar in sidebar
        const avatarContainer = document.getElementById('userAvatarContainer');
        avatarContainer.innerHTML = `<img src="https://i.pravatar.cc/150?u=${currentUser.username}" alt="${currentUser.username}">`;

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
        data.messages.reverse().forEach(msg => {
            displayMessage(msg);
        });
        scrollToBottom();

    } catch (error) {
        console.error('Error loading messages:', error);
    }
}

function displayMessage(msg) {
    const isOwn = currentUser && msg.user_id === currentUser.id;
    const wrapper = document.createElement('div');
    wrapper.className = `message-wrapper ${isOwn ? 'own' : ''}`;

    const time = new Date(msg.created_at).toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit'
    });

    wrapper.innerHTML = `
        <div class="user-avatar-small">
            <img src="https://i.pravatar.cc/100?u=${msg.username}" alt="${msg.username}">
        </div>
        <div class="message-content-wrapper">
            <div class="message-info">
                <span class="msg-username">${msg.username}</span>
                <span class="msg-time">${time}</span>
            </div>
            <div class="message-bubble">
                ${escapeHtml(msg.content)}
            </div>
        </div>
    `;

    messagesContainer.appendChild(wrapper);
}

function sendMessage() {
    const content = messageInput.value.trim();
    if (!content || !socket || socket.readyState !== WebSocket.OPEN) return;

    socket.send(JSON.stringify({
        event: 'send_message',
        data: { content }
    }));

    messageInput.value = '';
}

function sendTypingIndicator() {
    if (typingTimeout) clearTimeout(typingTimeout);
    typingTimeout = setTimeout(() => {
        if (socket && socket.readyState === WebSocket.OPEN) {
            socket.send(JSON.stringify({ event: 'typing', data: {} }));
        }
    }, 300);
}

// Online Users
async function loadOnlineUsers() {
    try {
        const response = await fetch(`${API_BASE_URL}/users/online`);
        if (!response.ok) throw new Error('Failed to load online users');
        const users = await response.json();
        updateOnlineUsers(users);
    } catch (error) {
        console.error('Error loading online users:', error);
    }
}

function updateOnlineUsers(users) {
    usersList.innerHTML = '';
    onlineCount.textContent = users.length;
    activeCountText.textContent = users.length;

    users.forEach(user => {
        const div = document.createElement('div');
        div.className = 'user-list-item';
        div.innerHTML = `
            <div class="user-avatar-small">
                <img src="https://i.pravatar.cc/100?u=${user.username}" alt="${user.username}">
                <div class="status-dot"></div>
            </div>
            <span>${user.username}</span>
        `;
        usersList.appendChild(div);
    });
}

// WebSocket
function connectWebSocket() {
    if (socket) socket.close();
    socket = new WebSocket(`${WS_BASE_URL}/ws/chat?token=${token}`);

    socket.onopen = () => {
        console.log('WebSocket connected');
        if (heartbeatInterval) clearInterval(heartbeatInterval);
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

    socket.onclose = () => {
        if (token && currentUser) {
            setTimeout(connectWebSocket, 3000);
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
        case 'user_joined':
        case 'user_left':
            loadOnlineUsers();
            break;
        case 'user_typing':
            showTypingIndicator(data.username);
            break;
        case 'error':
            alert(data.message);
            break;
    }
}

function showTypingIndicator(username) {
    typingIndicator.textContent = `${username} is typing...`;
    setTimeout(() => {
        typingIndicator.textContent = '';
    }, 3000);
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

function stringToColor(str) {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
        hash = str.charCodeAt(i) + ((hash << 5) - hash);
    }
    const c = (hash & 0x00FFFFFF).toString(16).toUpperCase();
    return '#' + '00000'.substring(0, 6 - c.length) + c;
}

// Initialize app
document.addEventListener('DOMContentLoaded', init);
