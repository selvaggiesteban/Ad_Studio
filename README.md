# Ad Studio

Ad Studio is a professional visual content generator for social media, designed to create brand-consistent images, carousels, thumbnails, and short-form videos using advanced AI models.

## 🚀 Features

- **Brand-Consistent Generation**: Load brand manuals (JSON) to ensure consistent colors, styles, and tones across all assets.
- **Multi-Format Support**: Pre-configured templates for Instagram, Facebook, LinkedIn, TikTok, YouTube, and more.
- **AI Engine Flexibility**: Supports NVIDIA NIM (Flux, etc.) and Pollinations.ai for high-quality image synthesis.
- **Automated Workflows**:
  - `image`: Single asset generation.
  - `carousel`: Slide-by-slide carousel creation.
  - `thumbnail`: Optimized YouTube thumbnails.
  - `video`: Short-form video generation via MoneyPrinterTurbo.
  - `batch`: Bulk generation from a JSON configuration file.

## 🛠️ Installation

### Prerequisites
- Python 3.10+
- A valid NVIDIA API Key (optional, for higher quality).

### Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/selvaggiesteban/Ad_Studio.git
   cd Ad_Studio
   ```

2. **Environment Setup**:
   - **Windows**:
     ```cmd
     setup.bat
     call venv\Scripts\activate
     ```
   - **macOS/Linux**:
     ```bash
     chmod +x setup.sh
     ./setup.sh
     source venv/bin/activate
     ```

3. **Configuration**:
   Copy the example environment file and add your API keys:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and provide your `NVIDIA_API_KEY` and the local path to `MONEY_PRINTER_TURBO`.

## 📖 Usage

### Basic Commands

**Generate an Image:**
```bash
python main.py image --type instagram_post --prompt "A futuristic coffee shop in Tokyo" --brand brand_manuals/my_brand.json
```

**Generate a Carousel:**
```bash
python main.py carousel --title "Top 5 AI Tools" --slides 5 --brand brand_manuals/my_brand.json
```

**Generate a YouTube Thumbnail:**
```bash
python main.py thumbnail --title "How to use Claude Code" --brand brand_manuals/my_brand.json --tone curious
```

**Generate a Video:**
```bash
python main.py video --prompt "The future of AI agents" --duration 15 --brand brand_manuals/my_brand.json
```

**Batch Generation:**
```bash
python main.py batch --file posts.json --brand brand_manuals/my_brand.json
```

### Brand Management
Create a new brand manual template:
```bash
python main.py brand --create "My New Brand"
```
List all available brand manuals:
```bash
python main.py brand --list
```

## 📁 Project Structure

- `brand/`: Logic for loading brand manuals and building prompts.
- `generators/`: Core AI integration for images, carousels, thumbnails, and videos.
- `formats/`: JSON definitions for social media dimensions and composition guides.
- `brand_manuals/`: Storage for brand identity profiles.
- `output/`: Generated assets, organized by brand.

## 📜 License
This project is licensed under the MIT License - see the `LICENSE` file for details.
