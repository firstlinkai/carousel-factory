import { spawn } from 'child_process';

const run = (cmd: string, args: string[]) => {
  return new Promise((resolve) => {
    console.log(`Running ${cmd} ${args.join(' ')}`);
    const proc = spawn(cmd, args, {shell: true});
    proc.stdout.on('data', (data) => process.stdout.write(data.toString()));
    proc.stderr.on('data', (data) => process.stderr.write(data.toString()));
    proc.on('close', (code) => resolve(code));
  });
};

(async () => {
    await run('whoami', []);
    await run('apt-get', ['update']);
    await run('apt-get', ['install', '-y', 'python3-pip', 'python3-venv']);
    await run('python3', ['-m', 'venv', 'venv']);
    await run('./venv/bin/pip', ['install', '-r', 'requirements.txt']);
})();
