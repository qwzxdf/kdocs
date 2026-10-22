# K-HLSL をビルドして、.vsix を bin\K-HLSL.vsix に作る。
# 事前に: Visual Studio の "Visual Studio extension development" ワークロード。
$ErrorActionPreference = 'Stop'
$root = $PSScriptRoot

$vswhere = Join-Path ${env:ProgramFiles(x86)} 'Microsoft Visual Studio\Installer\vswhere.exe'
$vs = & $vswhere -latest -products * -requires Microsoft.Component.MSBuild -property installationPath
$msbuild = Join-Path $vs 'MSBuild\Current\Bin\MSBuild.exe'
if (-not (Test-Path $msbuild)) { throw 'MSBuild.exe が見つかりません' }

python (Join-Path $root 'data\gen.py')
python (Join-Path $root 'tools\make_media.py')

$serverProj = Join-Path $root 'src\KHlsl.Server\KHlsl.Server.csproj'
$vsixProj = Join-Path $root 'src\KHlsl.Vsix\KHlsl.Vsix.csproj'
& $msbuild $serverProj '/restore' '/p:Configuration=Release' '/v:m' '/nologo'
if ($LASTEXITCODE -ne 0) { throw 'server build failed' }
& $msbuild $vsixProj '/restore' '/p:Configuration=Release' '/v:m' '/nologo'
if ($LASTEXITCODE -ne 0) { throw 'vsix build failed' }

New-Item -ItemType Directory -Force (Join-Path $root 'bin') | Out-Null
Copy-Item (Join-Path $root 'src\KHlsl.Vsix\bin\Release\net472\KHlsl.Vsix.vsix') (Join-Path $root 'bin\K-HLSL.vsix') -Force
Write-Host "OK: $(Join-Path $root 'bin\K-HLSL.vsix')"
