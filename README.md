<div align="center">

# 🎨 Logo Bot

### <p align="center">
  <span style="color: #7E3ACE; font-size: 2.2em; font-weight: 700; letter-spacing: 2px; line-height: 1.6;">
    🎨 Telegram Bot for Logo Watermarking<br/>
    ⚡ Fast & Easy Image Processing<br/>
    🚀 Koyeb Deployment Ready
  </span>
</p>

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Telegram](https://img.shields.io/badge/Telegram-Bot-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)](https://telegram.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0.3-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active-success?style=for-the-badge)](https://github.com/3bkader-gpt/Logo_bot)

---

</div>

## 🌟 Features

<div align="center">

### ✨ **Powerful & Intuitive**

| 🎯 **Core Features** | 🎨 **Customization** | 🔧 **Management** |
|:---:|:---:|:---:|
| 🖼️ Logo Watermarking | 📏 Size Control | 👥 User Management |
| 🎭 Multiple Styles | 🎚️ Opacity Control | 📊 Status Monitoring |
| ⚡ Fast Processing | 💾 Settings Persistence | 🔐 Owner Controls |

</div>

### 🚀 **Key Highlights**

- 🎨 **Easy Logo Watermarking** - Add logos to images with just a few clicks
- 🎭 **Multiple Placement Styles** - 4 different logo placement options
- 📏 **Customizable Size** - Adjust logo size from 5% to 50% or use presets
- 🎚️ **Opacity Control** - Control logo transparency (low, medium, high, opaque)
- 👥 **User Management** - Add/remove authorized users (owner-only)
- 💾 **Settings Persistence** - Your preferences are saved per user
- 🔄 **Reset Functionality** - Reset logo to original version anytime
- 🚀 **Koyeb Ready** - Optimized for cloud deployment
- 📊 **Status Monitoring** - Check bot status and current settings
- 🔐 **Secure** - Environment variables for sensitive data

---

## 📸 Features in Detail

### 🎨 **Logo Placement Styles**

1. **Bottom Right Corner** - Classic watermark position
2. **Middle Right** - Vertical center alignment
3. **Top Left Corner** - Alternative corner placement
4. **Four Corners** - Logo in all four corners

### 📏 **Size Options**

- **Preset Sizes**: Small (10%), Medium (20%), Large (30%)
- **Custom Size**: Set any percentage from 5% to 50% using `/setsize <percentage>`
- **Preview Before Apply**: See how the logo looks before saving

### 🎚️ **Opacity Levels**

- **Low** (30%) - Subtle watermark
- **Medium** (50%) - Balanced visibility
- **High** (80%) - More prominent
- **Opaque** (100%) - Fully visible

---

## 🛠️ Tech Stack

<div align="center">

![Python](https://img.shields.io/badge/-Python-3776AB?style=flat-square&logo=python&logoColor=white)
![Telegram Bot API](https://img.shields.io/badge/-Telegram%20Bot%20API-2CA5E0?style=flat-square&logo=telegram&logoColor=white)
![Flask](https://img.shields.io/badge/-Flask-000000?style=flat-square&logo=flask&logoColor=white)
![Pillow](https://img.shields.io/badge/-Pillow-10.4.0-FF6B6B?style=flat-square&logo=python&logoColor=white)
![nest_asyncio](https://img.shields.io/badge/-nest_asyncio-1.6.0-4ECDC4?style=flat-square&logo=python&logoColor=white)

</div>

---

## 📦 Installation

### **Prerequisites**

```bash
# Make sure you have Python 3.11+ installed
python --version
```

### **Quick Start**

```bash
# 1️⃣ Clone the repository
git clone https://github.com/3bkader-gpt/Logo_bot.git
cd Logo_bot

# 2️⃣ Install dependencies
pip install -r requirements.txt

# 3️⃣ Set up environment variables
cp .env.example .env
# Edit .env file with your BOT_TOKEN

# 4️⃣ Run the bot
python main.py
```

---

## ⚙️ Configuration

### **Environment Variables Setup**

1. **Copy the example file:**
```bash
cp .env.example .env
```

2. **Edit `.env` file:**
```env
BOT_TOKEN=your_telegram_bot_token_here
KOYEB=0  # Set to 1 when deploying on Koyeb
```

### **Telegram Bot Setup**

1. **Create Bot:**
   - Message [@BotFather](https://t.me/botfather) on Telegram
   - Use `/newbot` command
   - Copy the bot token

2. **Add to `.env`:**
   ```env
   BOT_TOKEN=your_bot_token_here
   ```

### **Owner Configuration**

Edit `bot.py` to set your Telegram user ID:

```python
OWNERS = [1372068902, 6788399763]  # Add your user ID here
```

To get your user ID, message [@userinfobot](https://t.me/userinfobot) on Telegram.

---

## 🎮 Usage

### **For Users**

1. Start the bot: `/start`
2. Set logo (owners only): Press `Set Logo` and send your logo image
3. Add watermark: Press `Watermark` and send the image you want to watermark
4. Choose style: Select from 4 placement options
5. Done! The bot will send back the watermarked image

### **Commands**

- `/start` - Start the bot and see main menu
- `/help` - Show help message
- `/status` - Check current logo status and settings
- `/config size` - Configure logo size (preset options)
- `/setsize <percentage>` - Set custom logo size (5-50%)
- `/config opacity` - Configure logo opacity

### **Owner Commands**

- `/adduser <user_id>` - Add authorized user
- `/removeuser <user_id>` - Remove authorized user
- `/users` - List all authorized users
- `/clearusers` - Remove all authorized users

---

## 📁 Project Structure

```
Logo_bot/
├── 📄 bot.py                 # Main bot logic
├── 📄 main.py                # Entry point with Flask server
├── 📄 requirements.txt       # Python dependencies
├── 📄 .python-version        # Python version specification
├── 📄 .env.example           # Environment variables template
├── 📄 .gitignore             # Git ignore file
├── 📖 README.md              # This file
├── 📁 tmp/                   # Temporary image storage (auto-created)
├── 📄 logo_original.png      # Original logo (created when set)
├── 📄 logo_current.png       # Current logo with modifications
├── 📄 settings.json          # User settings (auto-created)
└── 📄 users.json             # Authorized users list (auto-created)
```

---

## 🚀 Deployment

### **Koyeb Deployment**

The bot is optimized for Koyeb deployment:

1. **Set Environment Variables in Koyeb:**
   ```env
   BOT_TOKEN=your_bot_token
   KOYEB=1
   ```

2. **Deploy:**
   - Connect your GitHub repository to Koyeb
   - Set environment variables in Koyeb dashboard
   - Deploy!

3. **Health Check:**
   - The bot includes a Flask server on port 8000
   - Visit `https://your-app.koyeb.app/` to check if it's running

### **Local Deployment**

```bash
# Set environment variable
export BOT_TOKEN="your_bot_token"

# Run without Koyeb mode
python main.py
```

### **Using .env File**

```bash
# Install python-dotenv (optional, for .env file support)
pip install python-dotenv

# Create .env file
cp .env.example .env
# Edit .env with your token

# Run
python main.py
```

---

## 🎯 Features Breakdown

### **Logo Management**

- ✅ Set logo (PNG/JPEG supported)
- ✅ Reset to original logo
- ✅ Automatic logo validation
- ✅ File size limits (5MB max)

### **Watermarking**

- ✅ Multiple placement styles
- ✅ Customizable size
- ✅ Opacity control
- ✅ Preview before apply
- ✅ High-quality output (JPEG 95% quality)

### **User Management**

- ✅ Owner-only logo management
- ✅ Authorized user system
- ✅ Per-user settings
- ✅ Settings persistence

---

## 🔒 Security

### **Access Control**

- **Owners**: Full access to all features
- **Authorized Users**: Can use watermarking features
- **Others**: Blocked from using the bot

### **Best Practices**

- ✅ Environment variables for sensitive data (BOT_TOKEN)
- ✅ User authentication system
- ✅ File size limits
- ✅ Input validation
- ✅ Error handling and logging
- ✅ `.gitignore` to prevent committing secrets

### **Security Checklist**

- [ ] Never commit `.env` file
- [ ] Use strong bot token
- [ ] Regularly update dependencies
- [ ] Monitor logs for suspicious activity
- [ ] Keep owner IDs secure

---

## 📊 Logging

The bot includes comprehensive logging:

- **Console Logging**: INFO level and above
- **File Logging**: DEBUG level with rotation
- **Log File**: `bot.log` (max 2MB, 3 backups)
- **Encoding**: UTF-8 for Arabic support

---

## 🤝 Contributing

Contributions are welcome! Feel free to:

1. 🍴 Fork the repository
2. 🌿 Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. 💾 Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. 📤 Push to the branch (`git push origin feature/AmazingFeature`)
5. 🔀 Open a Pull Request

---

## 📝 License

This project is licensed under the **MIT License**.

---

## 👨‍💻 Author

<div align="center">

### **Mohamed Omar**

[![GitHub](https://img.shields.io/badge/-GitHub-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/3bkader-gpt)
[![Email](https://img.shields.io/badge/-Email-D14836?style=for-the-badge&logo=gmail&logoColor=white)](mailto:medo.omar.salama@gmail.com)

---

### ⭐ **Star this repo if you find it helpful!**

<div align="center">

![GitHub stars](https://img.shields.io/github/stars/3bkader-gpt/Logo_bot?style=social)
![GitHub forks](https://img.shields.io/github/forks/3bkader-gpt/Logo_bot?style=social)

---

**Made with ❤️ by [Mohamed Omar](https://github.com/3bkader-gpt)**

<p align="center">
  <img src="https://komarev.com/ghpvc/?username=3bkader-gpt&color=blueviolet&style=flat-square" alt="Profile views" />
</p>

</div>

---

<div align="center">

### 🎉 **Thank you for visiting!**

<p align="center">
  <span style="color: #7E3ACE; font-size: 1.5em; font-weight: 600;">
    🎨 Happy Watermarking!<br/>
    🚀 Keep Building Amazing Things!
  </span>
</p>

</div>

---

<div align="center">

### 📞 **Support**

For issues and questions:
- Open an issue on GitHub
- Check the logs: `bot.log`
- Review the configuration in `bot.py`

</div>
