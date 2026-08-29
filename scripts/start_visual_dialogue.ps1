$ErrorActionPreference = 'Stop'
$root = 'Z:\visual-dialogue-gan'
$url = 'http://127.0.0.1:4173'
$listener = Get-NetTCPConnection -LocalAddress '127.0.0.1' -LocalPort 4173 -State Listen -ErrorAction SilentlyContinue

if (-not $listener) {
    Start-Process -FilePath 'python.exe' `
        -ArgumentList @('-m', 'http.server', '4173', '--directory', "$root\web", '--bind', '127.0.0.1') `
        -WorkingDirectory $root `
        -WindowStyle Hidden `
        -RedirectStandardOutput "$root\data\logs\web-prototype.stdout.log" `
        -RedirectStandardError "$root\data\logs\web-prototype.stderr.log"
    Start-Sleep -Seconds 1
}

Start-Process $url
