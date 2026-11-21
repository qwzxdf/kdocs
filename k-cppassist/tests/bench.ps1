# 打つたび・カーソルが動くたびに走る処理の時間を測る。引数: 測るファイル(複数可)。
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$src = Join-Path $root 'src\KCppAssist.Vsix'
$vswhere = Join-Path ${env:ProgramFiles(x86)} 'Microsoft Visual Studio\Installer\vswhere.exe'
$vs = & $vswhere -latest -products * -requires Microsoft.Component.MSBuild -property installationPath
$csc = Join-Path $vs 'MSBuild\Current\Bin\Roslyn\csc.exe'
$out = Join-Path ([System.IO.Path]::GetTempPath()) 'kcppassist-bench.exe'
$files = @('CppScan', 'CppText', 'AccessorEditor', 'HeaderEditor', 'TypeInference', 'AssignScan', 'ExprType', 'Scopes', 'FunctionScan', 'SignatureSync', 'SyncPlan', 'DefinitionGen', 'MoveGen', 'IncludeTidy', 'ForwardDecl', 'SwitchGen', 'CtorGen', 'OverrideGen', 'ClassPlace', 'UsageGen', 'IncludeEditor', 'CallCheck', 'SymbolScan', 'EncodingTool', 'MemberScan', 'Refactor', 'ClassGen', 'FileGen', 'NewFileGen') | ForEach-Object { Join-Path $src "$_.cs" }
& $csc -nologo -optimize+ "-out:$out" -langversion:latest (Join-Path $PSScriptRoot 'Bench.cs') @files | Out-Null
if ($LASTEXITCODE -ne 0) { throw 'compile failed' }
& $out @args
