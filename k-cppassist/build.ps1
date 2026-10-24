# K-CppAssist をビルドして、.vsix を bin\K-CppAssist.vsix に作る。
# 事前に: Visual Studio の "Visual Studio extension development" ワークロード。
$ErrorActionPreference = 'Stop'
$root = $PSScriptRoot

$vswhere = Join-Path ${env:ProgramFiles(x86)} 'Microsoft Visual Studio\Installer\vswhere.exe'
$vs = & $vswhere -latest -products * -requires Microsoft.Component.MSBuild -property installationPath
$msbuild = Join-Path $vs 'MSBuild\Current\Bin\MSBuild.exe'
if (-not (Test-Path $msbuild)) { throw 'MSBuild.exe が見つかりません' }

$proj = Join-Path $root 'src\KCppAssist.Vsix\KCppAssist.Vsix.csproj'
& $msbuild $proj '/restore' '/p:Configuration=Release' '/v:m' '/nologo'
if ($LASTEXITCODE -ne 0) { throw 'vsix build failed' }

New-Item -ItemType Directory -Force (Join-Path $root 'bin') | Out-Null
Copy-Item (Join-Path $root 'src\KCppAssist.Vsix\bin\Release\net472\KCppAssist.Vsix.vsix') (Join-Path $root 'bin\K-CppAssist.vsix') -Force
Write-Host "OK: $(Join-Path $root 'bin\K-CppAssist.vsix')"
