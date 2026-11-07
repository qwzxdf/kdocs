# Runs the VS-independent tests (type inference, statement scanning, signature sync, error-log parsing) with the bare compiler.
# Uses csc.exe from the Roslyn that ships with Visual Studio.
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$src = Join-Path $root 'src\KCppAssist.Vsix'
$vswhere = Join-Path ${env:ProgramFiles(x86)} 'Microsoft Visual Studio\Installer\vswhere.exe'
$vs = & $vswhere -latest -products * -requires Microsoft.Component.MSBuild -property installationPath
$csc = Join-Path $vs 'MSBuild\Current\Bin\Roslyn\csc.exe'

# 1. K-CppAssist core
$out = Join-Path ([System.IO.Path]::GetTempPath()) 'kcppassist-tests.exe'
$files = @('CppScan', 'CppText', 'AccessorEditor', 'HeaderEditor', 'TypeInference', 'AssignScan', 'ExprType', 'Scopes', 'FunctionScan', 'SignatureSync', 'SyncPlan', 'DefinitionGen', 'MoveGen') | ForEach-Object { Join-Path $src "$_.cs" }
& $csc -nologo "-out:$out" -langversion:latest (Join-Path $PSScriptRoot 'Tests.cs') (Join-Path $PSScriptRoot 'SyncTests.cs') (Join-Path $PSScriptRoot 'DefTests.cs') (Join-Path $PSScriptRoot 'MoveTests.cs') @files
if ($LASTEXITCODE -ne 0) { throw 'compile failed' }
& $out
$code = $LASTEXITCODE

# 2. Error log (all of ErrorLog\Core; the settings stub lives in ErrorLogTests.cs)
$outLog = Join-Path ([System.IO.Path]::GetTempPath()) 'kcppassist-errorlog-tests.exe'
$logFiles = Get-ChildItem (Join-Path $src 'ErrorLog\Core') -Filter *.cs | ForEach-Object FullName
& $csc -nologo "-out:$outLog" -langversion:latest (Join-Path $PSScriptRoot 'ErrorLogTests.cs') @logFiles
if ($LASTEXITCODE -ne 0) { throw 'errorlog compile failed' }
& $outLog | Select-Object -Last 1
if ($LASTEXITCODE -ne 0) { $code = 1 }

# 3. File rename sync (RenameSync only; no VS dependency)
$outRen = Join-Path ([System.IO.Path]::GetTempPath()) 'kcppassist-rename-tests.exe'
& $csc -nologo "-out:$outRen" -langversion:latest (Join-Path $PSScriptRoot 'RenameTests.cs') (Join-Path $src 'RenameSync.cs') (Join-Path $src 'StdHeaders.cs')
if ($LASTEXITCODE -ne 0) { throw 'rename compile failed' }
& $outRen | Select-Object -Last 3
if ($LASTEXITCODE -ne 0) { $code = 1 }

# 4. Argument-count check for make_unique / make_shared / new (CallCheck; no VS dependency)
$outCall = Join-Path ([System.IO.Path]::GetTempPath()) 'kcppassist-callcheck-tests.exe'
$callFiles = @('CallCheck', 'CppText', 'FunctionScan') | ForEach-Object { Join-Path $src "$_.cs" }
& $csc -nologo "-out:$outCall" -langversion:latest (Join-Path $PSScriptRoot 'CallCheckTests.cs') @callFiles
if ($LASTEXITCODE -ne 0) { throw 'callcheck compile failed' }
& $outCall
if ($LASTEXITCODE -ne 0) { $code = 1 }

exit $code
