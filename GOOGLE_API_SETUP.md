# Google Gemini API Setup Guide

Your project has been updated to use **Google Gemini API** (Free) instead of Ollama! 🎉

## ✅ Benefits of Google Gemini
- ✅ **Completely FREE** (60 requests per minute)
- ✅ **No local installation needed** (No Ollama required)
- ✅ **Powerful AI** (Better than many local models)
- ✅ **Easy to setup** (Just 2-3 minutes)

---

## Step 1: Get Your Google API Key

1. Go to: **https://makersuite.google.com/app/apikey**
2. Click on **"Create API Key"** button
3. Select **"Create API key in new Google Cloud project"**
4. Copy the generated API key (it starts with `AIza...`)

**Keep this key safe!** Don't share it with anyone.

---

## Step 2: Add API Key to `.env` File

1. In your backend folder, open or create `.env` file
2. Add this line:
```env
GOOGLE_API_KEY=your_api_key_here_AIza...
```

3. Replace `your_api_key_here_AIza...` with the key you copied

**Example:**
```env
FLASK_ENV=development
FLASK_APP=run.py
SECRET_KEY=your-secret-key-here-change-in-production
JWT_SECRET_KEY=your-jwt-secret-key-here-change-in-production

# MongoDB
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/educational_platform
MONGODB_DB_NAME=educational_platform

# Google Gemini API (ADD THIS)
GOOGLE_API_KEY=AIzaSyDxxx_your_actual_key_xxx

# Rest of your config...
FLASK_DEBUG=True
CORS_ORIGINS=http://localhost:3000,http://localhost:5000
```

---

## Step 3: Install Updated Dependencies

```bash
# Navigate to backend folder
cd "x:\Final year project\backend"

# Activate virtual environment (if not already activated)
venv\Scripts\activate

# Install the updated requirements
pip install --upgrade pip
pip install -r requirements.txt
```

---

## Step 4: Verify Setup (Optional)

Run this Python command to test if your API key works:

```python
import google.generativeai as genai

# Replace YOUR_API_KEY with your actual key
genai.configure(api_key="YOUR_API_KEY")

model = genai.GenerativeModel('gemini-pro')
response = model.generate_content("Say hello")
print(response.text)
```

---

## 🚀 You're Ready to Go!

Now you can start your backend:
```bash
python run.py
```

And your frontend:
```bash
cd frontend
npm run dev
```

---

## ⚠️ Important Notes

### Rate Limits (Free Tier)
- **60 requests per minute** (should be enough for testing)
- **1 request per second** per IP
- Refresh daily

### If You Need More Power
Google offers paid plans:
- **Pay-as-you-go**: $0.0025 per 1K input tokens, $0.0005 per 1K output tokens
- **Generous free tier** that covers most educational use cases

---

## Troubleshooting

### "API key not configured" Error
- Check `.env` file has `GOOGLE_API_KEY=AIza...`
- Make sure you didn't add extra spaces
- Restart your Flask server after adding the key

### "google-generativeai package not installed" Error
```bash
pip install google-generativeai
```

### "Access Denied" Error
- Get a new API key from https://makersuite.google.com/app/apikey
- Ensure your key is `AIza...` format

---

**Questions?** Check [Google AI Studio Documentation](https://ai.google.dev/)
