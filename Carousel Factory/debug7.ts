import fs from 'fs';
console.log('venv exists?', fs.existsSync('venv'));
console.log('pip exists?', fs.existsSync('venv/bin/pip'));
