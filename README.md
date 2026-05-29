<img width="1376" height="768" alt="Carousel_Factory_Banner" src="https://github.com/user-attachments/assets/9cc6faf6-2db7-40f6-b13f-f34777c7a3df" />


# 🎠 Carousel Factory

> **Transform any brand URL into agency-grade Instagram carousel slides in under 2 minutes.**

Carousel Factory is an industrial-grade, automated content generation engine built for digital agencies and DTC brands. It scrapes live brand identity, generates psychologically-framed copy via Gemini AI, and renders pixel-perfect slides using deterministic code — no AI-generated images, no "AI slop," no manual revision loops.

---

## ✨ Features

- **Brand Intelligence Scraping** — Extracts live hex colors, font families, and CSS variables directly from any website's DOM and stylesheets
- **AI-Powered Copywriting** — Uses Gemini 2.5 Flash with structured JSON mode to write high-converting carousel copy using the proven PAS (Problem → Agitation → Solution) framework
- **Deterministic Rendering** — Pillow-based typography engine renders text mathematically using local `.ttf`/`.otf` fonts — pixel-perfect, consistent kerning, zero hallucinations
- **Auto Font Resolution** — Automatically downloads detected Google Fonts; falls back gracefully to the bundled default sans-serif
- **Live Rerender** — Edit slide copy in the UI and re-render slides instantly without re-scraping or re-generating
- **HTML Gallery Preview** — Outputs a self-contained `index.html` for quick in-browser review of all generated slides
- **ZIP Export** — One-click download of all rendered slides as a `.zip` archive
- **Graceful Fallbacks** — Every layer (scraping, LLM, font) has a deterministic fallback so the pipeline never hard-fails on missing credentials

---

## 🖼️ Output

Each run produces a **6-slide Instagram carousel** (1080×1350px) structured as:

| Slide | Framework Stage | Purpose |
|-------|----------------|---------|
| 1 | **Hook** | Grab attention immediately |
| 2 | **Problem** | Surface the core pain point |
| 3 | **Agitation** | Amplify the stakes |
| 4 | **Solution** | Introduce the brand's answer |
| 5 | **Proof** | Case study, stat, or social proof |
| 6 | **CTA** | Tell them exactly what to do next |

Slides alternate between centered and left-aligned layouts and include dot-grid overlays, accent shapes, top-bar highlights, and a branded footer with a slide progress indicator.

---

## 🏗️ Architecture

```
carousel-factory/
│
├── src/
│   ├── main.py                 # Pipeline orchestrator (4-step runner)
│   ├── scraper/
│   │   └── scraper.py          # Brand Intelligence Layer
│   ├── content/
│   │   └── generator.py        # Content Generation Layer (Gemini)
│   └── renderer/
│       └── renderer.py         # Deterministic Rendering Engine (Pillow)
│
├── server.ts                   # Express.js API wrapper
├── src/App.tsx                 # React frontend (Vite, Tailwind)
│
├── assets/
│   └── fonts/
│       └── Default-Sans.ttf    # Bundled fallback font
│
├── output/                     # Generated slides + gallery (git-ignored)
├── brand_config.json           # Scraper output — brand identity schema
├── content_plan.json           # Generator output — slide copy plan
│
├── requirements.txt            # Python dependencies
├── package.json                # Node dependencies
├── .env.example                # Environment variable template
└── test_run.sh                 # End-to-end CLI test runner
```

### Layer 1 — Brand Intelligence (`scraper/scraper.py`)

1. Fetches the target URL via **Apify** (headless browser) or falls back to a direct `requests` GET
2. Parses `<style>` blocks and linked external stylesheets with **BeautifulSoup**
3. Extracts `background-color`, `color`, and `font-family` from `body`, `h1`, and `h2` selectors via regex
4. Builds a frequency-ranked **color palette** from all hex values found across stylesheets
5. Converts `rgb()`/`rgba()` values to `#RRGGBB` hex
6. Attempts to **download detected Google Fonts** via the Fonts API; falls back to bundled `Default-Sans.ttf`
7. Validates the assembled config against the `brand_config.json` schema with safe color fallbacks
8. Writes the validated config to `brand_config.json`

### Layer 2 — Content Generation (`content/generator.py`)

1. Reads `brand_config.json` and injects brand name into the system prompt
2. Calls **Gemini 2.5 Flash** with `response_mime_type: "application/json"` to guarantee structured output
3. Enforces the 6-slide PAS framework via the system instruction; constrains title length (≤7 words) and body length (≤20 words)
4. Optionally calls **Gemini 2.5 Flash Image** to generate per-slide background elements keyed to brand colors and `visual_prompt` descriptions
5. Saves the full plan to `content_plan.json`
6. Falls back to a hardcoded mock plan if `GEMINI_API_KEY` is absent (safe for local testing)

### Layer 3 — Deterministic Rendering (`renderer/renderer.py`)

1. Reads `brand_config.json` (colors, fonts, layout settings) and the individual slide's content dict
2. Creates a `1080×1350` Pillow canvas filled with the brand background color
3. Composites the optional AI-generated element image with a brand-colored overlay for readability
4. Renders a subtle **dot-grid overlay** and a per-slide **abstract accent shape** (ellipse / polygon / rectangle, cycling by slide number)
5. Applies a solid **top accent bar** in the primary brand color
6. Loads `.ttf` fonts (96pt title, 48pt body, 32pt footer); falls back to Pillow's default font
7. **Word-wraps** all text to `(canvas_width − 240px)` using bounding-box measurement
8. Alternates **center/left alignment** by slide parity
9. Draws a text shadow pass before the main pass for depth
10. Renders a branded footer with the domain name and `N / 6` slide counter
11. Saves the result as a JPEG to `output/slide_NN.jpg`

### Layer 4 — API & Frontend (`server.ts` + `src/App.tsx`)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/generate` | `POST` | Accepts `{ url, topic }`, spawns the Python pipeline, returns slide URLs + content plan |
| `/api/rerender` | `POST` | Accepts an edited `contentPlan`, writes it to disk, rerenders slides without re-scraping |
| `/api/download` | `GET` | ZIPs the `output/` directory and streams it as `carousel_export.zip` |
| `/output/*` | `GET` | Static file serving for rendered slide images |

The React frontend is a Vite SPA with Tailwind CSS, served via Vite middleware in development and from the `dist/` build in production.

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- `pip` and `npm`

### 1. Clone

```bash
git clone https://github.com/firstlinkai/carousel-factory
cd carousel-factory
```

### 2. Configure environment

```bash
cp .env.example .env
```

Edit `.env` and add your keys:

```env
GEMINI_API_KEY="your_gemini_api_key_here"
APIFY_TOKEN="your_apify_token_here"   # Optional — scraper falls back to requests
```

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | Yes (for AI copy) | [Google AI Studio](https://aistudio.google.com/) API key |
| `APIFY_TOKEN` | No | [Apify](https://apify.com/) token for JS-rendered page scraping. Omit to use direct HTTP scraping. |

### 3. Install dependencies

```bash
pip install -r requirements.txt
npm install
```

### 4. Run

**Option A — Full-stack UI (recommended)**

```bash
npm run dev
```

Opens on `http://localhost:3000`. Enter a brand URL and content topic in the UI.

**Option B — CLI pipeline only**

```bash
./test_run.sh
```

Or directly:

```bash
PYTHONPATH="." python3 src/main.py "https://yourbrand.com" "Your carousel topic"
```

### 5. View output

- **UI:** The React app displays slides inline with live rerender support
- **Browser:** Open `output/index.html` for the standalone gallery
- **Files:** Individual slides are at `output/slide_01.jpg` through `output/slide_06.jpg`

---

## ⚙️ Configuration Reference

### `brand_config.json` Schema

Generated automatically by the scraper. Can be edited manually before rerending.

```json
{
  "brand_name": "yourbrand.com",
  "colors": {
    "primary":    "#ffffff",   // Title text color
    "secondary":  "#cccccc",   // Body text + footer color
    "background": "#1a1a2e"    // Canvas background
  },
  "fonts": {
    "title": "assets/fonts/YourFont-Bold.ttf",
    "body":  "assets/fonts/YourFont-Regular.ttf"
  },
  "layout_settings": {
    "width":          1080,
    "height":         1350,
    "title_y_offset": 500,
    "body_y_offset":  700,
    "margin_x":       100
  }
}
```

### `content_plan.json` Schema

Generated automatically by Gemini. Can be edited in the UI (live rerender) or directly on disk.

```json
[
  {
    "slide_number": 1,
    "title": "Short, punchy title",
    "body": "Supporting copy, max 20 words.",
    "visual_prompt": "Description used to generate the background element image.",
    "element_image_path": "output/elements/slide_01.jpg"
  }
]
```

---

## 🛠️ Development

### Run only the scraper

```bash
PYTHONPATH="." python3 src/scraper/scraper.py
# Output: brand_config.json
```

### Run only the content generator

```bash
PYTHONPATH="." python3 src/content/generator.py
# Output: content_plan.json
```

### Run only the renderer

```bash
PYTHONPATH="." python3 src/renderer/renderer.py
# Output: output/slide_01.jpg (sample slide)
```

### Rerender from existing content plan

```bash
PYTHONPATH="." python3 rerender.py
```

### Build for production

```bash
npm run build
npm start
```

---

## 📦 Dependencies

### Python

| Package | Version | Purpose |
|---------|---------|---------|
| `Pillow` | 10.3.0 | Deterministic image rendering |
| `beautifulsoup4` | 4.12.3 | HTML/CSS parsing |
| `apify-client` | 1.6.4 | Headless browser scraping |
| `google-generativeai` | 0.8.3 | Gemini API (copy + image generation) |
| `requests` | (transitive) | HTTP fallback scraping + font downloads |

### Node / Frontend

| Package | Purpose |
|---------|---------|
| `express` | API server |
| `vite` + `@vitejs/plugin-react` | React dev server + bundler |
| `tailwindcss` | UI styling |
| `lucide-react` | Icon set |
| `tsx` | TypeScript execution for `server.ts` |
| `motion` | Animations |

---

## 🔒 Environment & Secrets

- **Never commit your `.env` file.** It is listed in `.gitignore` by default.
- The `assets/fonts/` directory includes a bundled `Default-Sans.ttf` fallback. Custom fonts are downloaded to this directory at runtime and are also `.gitignore`d (`assets/fonts/` except `.gitkeep`).
- The `output/` directory is `.gitignore`d. Rendered slides are ephemeral build artifacts.

---

## 🗺️ Roadmap

- [ ] Multi-brand config presets
- [ ] Custom slide count (currently fixed at 6)
- [ ] Additional layout templates (full-bleed image, split-panel)
- [ ] Batch processing (multiple URLs / topics in one run)
- [ ] Export to Canva-compatible format
- [ ] Webhook / CI integration for automated content pipelines

---

## 📄 License

MIT — see [LICENSE](LICENSE) for details.

---

<img width="1024" height="1024" alt="Carousel_Factory_logo" src="https://github.com/user-attachments/assets/01e13065-a4bb-4627-9c0b-7e0e2202182a" />


## 🙏 Acknowledgments

Built with [Pillow](https://python-pillow.org/), [Google Gemini](https://ai.google.dev/), [Apify](https://apify.com/), and [React](https://react.dev/).
