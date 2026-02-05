# Gmail SMTP Setup for OTP Email Verification

## ✨ 100% FREE - No Credit Card Required!

This guide shows how to set up Gmail SMTP for sending OTP verification emails.

## 🔧 Gmail Setup (5 Minutes)

### Step 1: Enable 2-Factor Authentication

1. Go to [myaccount.google.com](https://myaccount.google.com)
2. Click **Security** in the left sidebar
3. Under "Signing in to Google", click **2-Step Verification**
4. Follow the prompts to enable it (you'll need your phone)

### Step 2: Generate App Password

1. Still in **Security** settings
2. Click **2-Step Verification** again
3. Scroll to bottom → Click **App passwords**
4. Select app: **Mail**
5. Select device: **Other (Custom name)**
6. Type: `ChatApp` or any name
7. Click **Generate**
8. **Copy the 16-character password** (looks like: `abcd efgh ijkl mnop`)

### Step 3: Update .env File

Update your `.env` file:
```env
SMTP_EMAIL=your-gmail@gmail.com
SMTP_PASSWORD=abcdefghijklmnop  # 16-char app password (no spaces)
```

### Step 4: Update Render Environment Variables

Go to Render Dashboard → your web service → **Environment** tab:

Add these variables:
- `SMTP_EMAIL` = your Gmail address
- `SMTP_PASSWORD` = your 16-character app password

Click **Save Changes**

## 📧 Email Limits

- **Gmail Free**: 500 emails/day
- **Google Workspace**: 2000 emails/day

Perfect for testing and small-scale apps!

## 🧪 Test It Locally

1. Update your `.env` with real Gmail credentials
2. Run migration:
```bash
python -m alembic upgrade head
```

3. Start server:
```bash
uvicorn app.main:app --reload
```

4. Test registration:
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"your-email@gmail.com","password":"pass123"}'
```

5. Send OTP:
```bash
curl -X POST "http://localhost:8000/auth/send-otp?email=your-email@gmail.com"
```

6. Check your Gmail inbox for the OTP!

7. Verify OTP:
```bash
curl -X POST "http://localhost:8000/auth/verify-otp?email=your-email@gmail.com&otp=123456"
```

## 🚀 Deploy to Render

1. **Push changes to GitHub:**
```bash
git add .
git commit -m "Switch to Gmail SMTP for free email"
git push
```

2. **Add env vars in Render:**
   - Go to web service → Environment
   - Add `SMTP_EMAIL`
   - Add `SMTP_PASSWORD`
   - Save (auto-redeploys)

3. **Run migration** (from local machine with Render DB in .env):
```bash
python -m alembic upgrade head
```

## ⚠️ Important Notes

- Use an **App Password**, NOT your regular Gmail password
- Keep the app password secret (don't commit to Git)
- The app password is 16 characters with no spaces
- You can revoke app passwords anytime in Google settings

## 🔒 Security Best Practices

- Never share your app password
- Add `.env` to `.gitignore`
- Use environment variables in production
- Consider using a dedicated Gmail account for sending emails

## 📊 Email Template

Your OTP emails include:
- ✨ Beautiful gradient header
- 🎯 Large, clear OTP code
- ⏰ 5-minute expiry notice
- 📱 Mobile-responsive design
- 📄 Plain text fallback

## 🆘 Troubleshooting

### "Username and Password not accepted"
- Make sure you enabled 2-Factor Authentication
- Use the **App Password**, not your regular password
- Remove any spaces from the app password

### "SMTP connection failed"
- Check your internet connection
- Verify SMTP_EMAIL and SMTP_PASSWORD are set
- Try generating a new app password

### "Too many login attempts"
- Wait 15 minutes and try again
- Gmail might be rate-limiting you

## 🎯 Next Steps

Once Gmail SMTP is working:
1. Test locally first
2. Deploy to Render with env vars
3. Update frontend with OTP verification screen (I can help!)

**No credit card, no third-party signups - just your Gmail!** 🎉
