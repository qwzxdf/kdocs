# VS に依存しない部分(型の推定・文の切り出し・引数の同期)のテストを、コンパイラ単体で実行する。
# Visual Studio の Roslyn の csc.exe を使う。
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$src = Join-Path $root 'src\KCppAssist.Vsix'
$vswhere = Join-Path ${env:ProgramFiles(x86)} 'Microsoft Visual Studio\Installer\vswhere.exe'
$vs = & $vswhere -latest -products * -requires Microsoft.Component.MSBuild -property installationPath
$csc = Join-Path $vs 'MSBuild\Current\Bin\Roslyn\csc.exe'
$out = Join-Path $env:TEMP 'kcppassist-tests.exe'
$files = @('CppScan', 'CppText', 'AccessorEditor', 'HeaderEditor', 'TypeInference', 'AssignScan', 'ExprType', 'Scopes', 'FunctionScan', 'SignatureSync', 'SyncPlan') | ForEach-Object { Join-Path $src "$_.cs" }
& $csc -nologo "-out:$out" -langversion:latest (Join-Path $PSScriptRoot 'Tests.cs') (Join-Path $PSScriptRoot 'SyncTests.cs') @files
if ($LASTEXITCODE -ne 0) { throw 'compile failed' }
& $out
exit $LASTEXITCODE
