import { spawn } from 'child_process';

const run = (cmd: string, args: string[]) => {
  return new Promise((resolve) => {
    console.log(`Running ${cmd} ${args.join(' ')}`);
    const proc = spawn(cmd, args);
    proc.stdout.on('data', (data) => process.stdout.write(data.toString()));
    proc.stderr.on('data', (data) => process.stderr.write(data.toString()));
    proc.on('error', (err) => console.error(`Error starting ${cmd}:`, err));
    proc.on('close', (code) => {
      console.log(`Process ${cmd} exited with code ${code}`);
      resolve(code);
    });
  });
};

(async () => {
    await run('python3', ['-m', 'pip', 'install', '-r', 'requirements.txt', '--break-system-packages']);
})();
