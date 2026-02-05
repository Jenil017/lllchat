# Chat Frontend - Quick Start Guide

## Overview

A simple, clean realtime chat frontend built with **pure HTML, CSS, and vanilla JavaScript**.

No frameworks, no build tools, no bundlers needed!

## Features

✅ **User Authentication** - Register and login  
✅ **JWT Token Storage** - Secure local storage  
✅ **Message History** - Load last 50 messages  
✅ **Real-Time Messaging** - WebSocket communication  
✅ **Online Users** - See who's connected  
✅ **Typing Indicator** - Know when others are typing  
✅ **Auto Reconnect** - Automatic WebSocket reconnection  
✅ **Responsive Design** - Works on mobile and desktop  

## File Structure

```
frontend/
├── index.html    # Main HTML structure
├── style.css     # Styles and animations
├── app.js        # JavaScript logic
└── README.md     # This file
```

## Getting Started

### 1. Make Sure Backend is Running

Your FastAPI backend must be running on:
```
http://localhost:8000
```

Start it with:
```bash
cd ..
python -m uvicorn app.main:app --reload
```

### 2. Open the Frontend

Simply open `index.html` in your browser:

**Option A: Double-click**
- Double-click `index.html` in File Explorer

**Option B: Python HTTP Server**
```bash
# In the frontend directory
python -m http.server 8080
```
Then visit: `http://localhost:8080`

**Option C: VS Code Live Server**
- Right-click `index.html` → "Open with Live Server"

### 3. Create an Account

1. Click "Register" tab
2. Enter username, email, and password
3. Click "Register" button
4. You'll be automatically logged in!

### 4. Start Chatting!

- Type a message in the input box
- Press Enter or click "Send"
- See messages appear in real-time
- Watch online users list update

## Usage Guide

### Authentication

**Register:**
- Username: 3-50 characters
- Email: Valid email format
- Password: Minimum 8 characters

**Login:**
- Email and password
- Token stored in `localStorage`
- Auto-login on page refresh

### Chatting

**Send Messages:**
- Type in the input box
- Press Enter or click Send
- Max 2000 characters

**Typing Indicator:**
- Start typing to notify others
- See when others are typing

**Rate Limit:**
- 5 messages per 5 seconds
- Error shown if exceeded

### Online Users

- Green dot = online
- Updates when users join/leave
- Shows current count

### Logout

- Click "Logout" button in sidebar
- Clears token and disconnects

## Features Explained

### Auto-Reconnect

If WebSocket disconnects:
- Status indicator turns red
- "Reconnecting..." shown
- Automatic retry after 3 seconds
- Seamless reconnection

### Heartbeat

- Ping sent every 30 seconds
- Keeps connection alive
- Detects disconnections

### Message Display

**Own Messages:**
- Aligned right
- Purple gradient background
- White text

**Others' Messages:**
- Aligned left
- White background
- Black text

All messages show:
- Username
- Time (HH:MM format)
- Content

## API Endpoints Used

### REST API
- `POST /auth/register` - Create account
- `POST /auth/login` - Get JWT token
- `GET /auth/me` - Get current user
- `GET /messages?limit=50` - Load history
- `GET /users/online` - Get online users

### WebSocket
- `WS /ws/chat?token=JWT` - Connect to chat

**Events Sent:**
- `send_message` - Send a message
- `typing` - Typing indicator
- `ping` - Heartbeat

**Events Received:**
- `new_message` - New message arrived
- `user_joined` - User connected
- `user_left` - User disconnected
- `user_typing` - Someone is typing
- `pong` - Heartbeat response
- `error` - Error occurred

## Customization

### Change Colors

Edit `style.css`:

```css
/* Main gradient */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

/* Change to your colors */
background: linear-gradient(135deg, #your-color-1 0%, #your-color-2 100%);
```

### Change API URL

Edit `app.js`:

```javascript
const API_BASE_URL = 'http://localhost:8000';
const WS_BASE_URL = 'ws://localhost:8000';
```

### Adjust Message Limit

Edit `app.js`:

```javascript
const response = await fetch(`${API_BASE_URL}/messages?limit=50`);
// Change 50 to your preferred limit (max 100)
```

## Troubleshooting

### "Failed to load messages"

**Problem:** Backend not running  
**Solution:** Start backend server:
```bash
python -m uvicorn app.main:app --reload
```

### "WebSocket connection failed"

**Problem:** Invalid or expired JWT token  
**Solution:** Logout and login again

### "CORS error"

**Problem:** Backend CORS not configured  
**Solution:** Backend already configured for `*` origins

### Token expired

**Problem:** JWT expires after 60 minutes  
**Solution:** Logout and login again (automatic on 401)

## Browser Compatibility

✅ Chrome/Edge (Recommended)  
✅ Firefox  
✅ Safari  
✅ Opera  

**Requirements:**
- WebSocket support
- localStorage support
- ES6 JavaScript

## Mobile Responsive

The app is fully responsive:
- Sidebar collapses to top on mobile
- Touch-friendly buttons
- Optimized for small screens

## Security Notes

- JWT token stored in localStorage
- All API calls use HTTPS (in production)
- WebSocket uses WSS (in production)
- Password sent over encrypted connection
- XSS prevention via text escaping

## Next Steps

**Enhancements you can add:**
1. Message editing (backend supports it)
2. Message deletion (backend supports it)
3. User avatars
4. Message timestamps
5. Sound notifications
6. Dark mode toggle
7. Emoji picker
8. File uploads

## Support

For backend issues, see:
- `../complete_documentation.md`
- `../test_report.md`

For frontend issues:
- Check browser console for errors
- Verify backend is running
- Check network tab for failed requests

---

**Enjoy your chat app!** 🎉
