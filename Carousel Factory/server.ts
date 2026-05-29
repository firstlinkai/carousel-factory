import express from 'express';
import path from 'path';
import fs from 'fs';
import { spawn } from 'child_process';
import { createServer as createViteServer } from 'vite';

async function startServer() {
  const app = express();
  const PORT = 3000;

  app.use(express.json());

  // Ensure output directory exists and is served statically
  const outputDir = path.join(process.cwd(), 'output');
  if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
  }
  app.use('/output', express.static(outputDir));

  app.post('/api/generate', (req, res) => {
    const { url, topic } = req.body;
    
    if (!url || !topic) {
      return res.status(400).json({ error: 'URL and Topic are required' });
    }

    console.log(`[API] Generating carousel for ${url} | ${topic}`);
    
    const proc = spawn('python3', ['src/main.py', url, topic], { cwd: process.cwd() });
    
    let logs = '';
    
    proc.stdout.on('data', (data) => {
        const str = data.toString();
        logs += str;
        console.log(`[Python] ${str.trim()}`);
    });

    proc.stderr.on('data', (data) => {
        const str = data.toString();
        logs += str;
        console.error(`[Python Err] ${str.trim()}`);
    });

    proc.on('close', (code) => {
        console.log(`[API] Python process closed with code ${code}`);
        
        let slides: string[] = [];
        let contentPlan = [];
        try {
            if (fs.existsSync(outputDir)) {
                slides = fs.readdirSync(outputDir)
                    .filter(file => file.endsWith('.jpg') || file.endsWith('.png'))
                    .sort()
                    .map(file => `/output/${file}?t=${Date.now()}`); // cache bust to force reload images
            }
            if (fs.existsSync('content_plan.json')) {
                contentPlan = JSON.parse(fs.readFileSync('content_plan.json', 'utf8'));
            }
        } catch (err) {
            console.error("Error reading output dir", err);
        }
        
        res.json({
            success: code === 0,
            slides,
            contentPlan,
            logs
        });
    });
  });

  app.post('/api/rerender', (req, res) => {
    const { contentPlan } = req.body;
    if (!contentPlan) {
        return res.status(400).json({ error: 'contentPlan is required' });
    }
    
    // Write new content plan
    fs.writeFileSync('content_plan.json', JSON.stringify(contentPlan, null, 4));
    
    // Write a python script to just run the renderer
    const pyScript = `
import os
import json
import sys

# Ensure correct path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/src'))

from renderer.renderer import render_slide

with open('content_plan.json', 'r') as f:
    plan = json.load(f)

output_dir = 'output'
os.makedirs(output_dir, exist_ok=True)


for slide in plan:
    slide_num = slide.get("slide_number", 0)
    output_file = os.path.join(output_dir, f"slide_{slide_num:02d}.jpg")
    render_slide('brand_config.json', slide, output_file)
print("Rerendering complete")
`;
    fs.writeFileSync('rerender.py', pyScript);
    
    const proc = spawn('python3', ['rerender.py'], { cwd: process.cwd() });
    
    let logs = '';
    proc.stdout.on('data', data => logs += data.toString());
    proc.stderr.on('data', data => logs += data.toString());
    
    proc.on('close', (code) => {
        let slides: string[] = [];
        try {
            if (fs.existsSync(outputDir)) {
                slides = fs.readdirSync(outputDir)
                    .filter(file => file.endsWith('.jpg') || file.endsWith('.png'))
                    .sort()
                    .map(file => `/output/${file}?t=${Date.now()}`); 
            }
        } catch (err) { }
        
        res.json({ success: code === 0, slides, logs });
    });
  });

  app.get('/api/download', (req, res) => {
    if (!fs.existsSync(outputDir)) {
        return res.status(404).send("No layout found");
    }
    const proc = spawn('python3', ['-c', "import shutil; shutil.make_archive('output_archive', 'zip', 'output')"]);
    proc.on('close', () => {
        res.download(path.join(process.cwd(), 'output_archive.zip'), 'carousel_export.zip');
    });
  });

  // Vite middleware for development
  if (process.env.NODE_ENV !== "production") {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: "spa",
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.join(process.cwd(), 'dist');
    app.use(express.static(distPath));
    app.get('*', (req, res) => {
      res.sendFile(path.join(distPath, 'index.html'));
    });
  }

  app.listen(PORT, "0.0.0.0", () => {
    console.log(`Server running on http://localhost:${PORT}`);
  });
}

startServer();
