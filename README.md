<div align="center">

# 🎨 Logo Bot

### Telegram Bot for Adding Watermarks to Images

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Telegram](https://img.shields.io/badge/Telegram-Bot-0088CC.svg)](https://telegram.org/)
[![Pillow](https://img.shields.io/badge/Pillow-Latest-3776AB.svg)](https://python-pillow.org/)
[![Koyeb](https://img.shields.io/badge/Koyeb-Ready-121212.svg)](https://www.koyeb.com/)

**Multiple Styles • Customizable • Easy to Use**

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [Contributing](#-contributing)

[العربية](README-ar.md) | [English](#-logo-bot)

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Requirements](#-requirements)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [Project Structure](#-project-structure)
- [Technologies Used](#-technologies-used)
- [Deployment](#-deployment)
- [Contributing](#-contributing)

---

## 🎯 Overview

**Logo Bot** is a Telegram bot for adding watermarks (Logos) to images. Includes multiple placement styles, customizable size and opacity, user management, and Koyeb deployment support.

### ✨ Why Logo Bot?

- 🖼️ **Easy to Use** - Add watermarks in simple steps
- 🎨 **Customizable** - Adjustable size, opacity, and position
- 📍 **Multiple Styles** - Different options for watermark placement
- 🚀 **Easy Deployment** - Full Koyeb support

---

## 🌟 Features

### 🚀 Main Features

| Feature | Description |
|---------|-------------|
| 🖼️ **Watermark Addition** | Easily add logos to images |
| 📍 **Multiple Styles** | Different options for watermark placement (corner, center, etc.) |
| 🎚️ **Customizable** | Adjustable size and opacity |
| 👥 **User Management** | Track and manage users |
| 🚀 **Koyeb Deployment** | Easy deployment support on Koyeb |
| 🎯 **Easy to Use** | Simple and clear bot interface |

### 🎨 Customization Options

- ✅ **Size**: Watermark size ratio from image (10% - 50%)
- ✅ **Opacity**: Opacity level (0 - 255)
- ✅ **Position**: 9 different positions (top/middle/bottom × left/center/right)
- ✅ **Formats**: Support PNG, JPG, JPEG, WEBP

---

## 📦 Requirements

Before starting, make sure you have installed:

- **Python** 3.8 or higher
- **Telegram Bot Token** (from [@BotFather](https://t.me/BotFather))
- **Logo Image** in PNG format
- **Git**

---

## 🚀 Installation

### Installation Steps

```bash
# 1. Clone the repository
git clone https://github.com/3bkader-gpt/Logo_bot.git
cd Logo_bot

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install requirements
pip install -r requirements.txt

# 4. Set up environment file
cp .env.example .env
# Edit .env file with your data
```

### Setting up `.env` File

```env
BOT_TOKEN=your_telegram_bot_token_here
LOGO_PATH=path/to/your/logo.png
```

---

## ⚙️ Configuration

### Telegram Bot Setup

1. Talk to [@BotFather](https://t.me/BotFather)
2. Create a new bot using `/newbot`
3. Follow instructions and get Token
4. Add Token in `.env` file:
   ```env
   BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
   ```

### Logo Setup

1. Prepare logo image in PNG format (transparent background recommended)
2. Place image in project folder
3. Add path in `.env` file:
   ```env
   LOGO_PATH=./logo.png
   ```

### Customizing Default Settings

You can modify default settings in code:

```python
DEFAULT_SIZE = 0.15      # 15% of image size
DEFAULT_OPACITY = 200    # Medium opacity
DEFAULT_POSITION = "bottom-right"  # Bottom right
```

---

## 📖 Usage

### Usage Steps

1. ✅ **Search for the bot** in Telegram
2. ✅ **Start conversation** using `/start`
3. ✅ **Send image** you want to add watermark to
4. ✅ **Choose position** from menu
5. ✅ **Choose size** (small/medium/large)
6. ✅ **Choose opacity** (transparent/medium/opaque)
7. ✅ **Get modified image**

### Available Commands

| Command | Description |
|---------|-------------|
| `/start` | Start using the bot |
| `/help` | Show help and commands |
| `/settings` | Watermark settings |
| `/logo` | Change logo |

### Usage Examples

```
User: Send image
Bot: Choose watermark position:
      1. Top left
      2. Top center
      3. Top right
      ...

User: 1
Bot: Choose watermark size:
      1. Small (10%)
      2. Medium (20%)
      3. Large (30%)

User: 2
Bot: [Sends modified image]
```

---

## 📁 Project Structure

```
Logo_bot/
├── 📄 bot.py              # Main bot code
├── 📄 main.py              # Entry point
├── 📄 .env.example         # Environment file example
├── 📄 requirements.txt     # Requirements
└── 🖼️ logo.png             # Logo image (add yourself)
```

---

## 🛠️ Technologies Used

<div align="center">

| Technology | Description |
|------------|-------------|
| ![Python](https://img.shields.io/badge/Python-3.8+-3776AB?logo=python&logoColor=white) | Main programming language |
| ![Telegram](https://img.shields.io/badge/Telegram-Bot-0088CC?logo=telegram&logoColor=white) | Telegram bot |
| ![Pillow](https://img.shields.io/badge/Pillow-Latest-3776AB?logo=python&logoColor=white) | Image processing |
| ![Flask](https://img.shields.io/badge/Flask-Lightweight-000000?logo=flask&logoColor=white) | Web server (for Koyeb deployment) |

</div>

---

## 🚀 Deployment on Koyeb

### Deployment Steps

1. ✅ **Create account** on [Koyeb](https://www.koyeb.com)
2. ✅ **Link repository** from GitHub
3. ✅ **Add environment variables**:
   - `BOT_TOKEN`: Bot token
   - `LOGO_PATH`: Logo path
4. ✅ **Deploy application**

### Koyeb Settings

- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python main.py`
- **Environment**: Python 3.8+

---

## 🤝 Contributing

Contributions are welcome! 🎉

1. 🍴 Fork the project
2. 🌿 Create a branch (`git checkout -b feature/AmazingFeature`)
3. 💾 Commit (`git commit -m 'Add some AmazingFeature'`)
4. 📤 Push (`git push origin feature/AmazingFeature`)
5. 🔄 Open a Pull Request

### Contribution Ideas

- ✨ Add new watermark styles
- 🎨 Improve image processing quality
- 📱 Add animated image support (GIF)
- 🔄 Multi-logo support

---

## ⚠️ Important Notes

- ⚖️ Make sure you have permission to use images and watermarks
- 🔒 Protect your bot information
- 📊 Monitor memory usage when processing large images

---

## 📄 License

This project is open source and available for free use.

---

## 📞 Contact & Support

- 🐛 **Report Issues**: [Open an Issue](https://github.com/3bkader-gpt/Logo_bot/issues)
- 💡 **Suggest Features**: [Open an Issue](https://github.com/3bkader-gpt/Logo_bot/issues)
- 📧 **Email**: medo.omar.salama@gmail.com

---

<div align="center">

**Made with ❤️ by [Mohamed Omar](https://github.com/3bkader-gpt)**

⭐ If you like this project, don't forget to give it a star!

[⬆ Back to Top](#-logo-bot)

</div>