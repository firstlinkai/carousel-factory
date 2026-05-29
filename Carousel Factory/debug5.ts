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
    await run('cat', ['/etc/os-release']);
    await run('apt-get', ['install', 'python3-pip', '-y']);
    await run('apk', ['add', 'py3-pip']);
})();
