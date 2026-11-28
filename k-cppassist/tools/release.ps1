# K-CppUltimateAssist release script: bump version in every place, test, build, publish to docs, commit, push, install.
#
#   powershell -File k-cppassist\tools\release.ps1 -Version 0.35.0 -NoteFile note.txt
#
# note.txt: UTF-8 text. The changelog row text (without the leading "| x.y.z |" and the trailing "|").
# Options: -NoTest  -NoPush  -NoInstall  -NoCommit
# Stops at the first failure. Nothing is committed or pushed unless build and tests succeed.
param(
    [Parameter(Mandatory = $true)][string]$Version,
    [Parameter(Mandatory = $true)][string]$NoteFile,
    [switch]$NoTest, [switch]$NoPush, [switch]$NoInstall, [switch]$NoCommit
)
$ErrorActionPreference = 'Stop'
$utf8 = New-Object System.Text.UTF8Encoding($false)
$kroot = Split-Path -Parent $PSScriptRoot            # ...\k-cppassist
$repo = Split-Path -Parent $kroot                    # repository root
$src = Join-Path $kroot 'src\KCppAssist.Vsix'
$docsDir = Join-Path $repo 'docs\kcppassist'
$index = Join-Path $docsDir 'index.md'
if ($Version -notmatch '^\d+\.\d+\.\d+$') { throw "bad version: $Version" }
$note = ([IO.File]::ReadAllText((Resolve-Path $NoteFile), $utf8)).Trim()
if ($note.Length -eq 0) { throw 'note is empty' }

function Read-Text($p) { [IO.File]::ReadAllText($p, $utf8) }
function Write-Text($p, $s) { [IO.File]::WriteAllText($p, $s, $utf8) }

# 1. version in the manifest and in the package attribute
$mf = Join-Path $src 'source.extension.vsixmanifest'
$t = Read-Text $mf
$m = [regex]::Match($t, '(<Identity [^>]*?\sVersion=")([^"]+)(")')
if (-not $m.Success) { throw 'Identity Version not found' }
$old = $m.Groups[2].Value
if ([version]$Version -le [version]$old) { throw "version must be greater than $old" }
Write-Text $mf ($t.Substring(0, $m.Groups[2].Index) + $Version + $t.Substring($m.Groups[2].Index + $m.Groups[2].Length))

$pk = Join-Path $src 'KCppAssistPackage.cs'
$t = Read-Text $pk
$m = [regex]::Match($t, '(InstalledProductRegistration\([^\r\n]*?")(\d+\.\d+\.\d+)("\))')
if (-not $m.Success) { throw 'InstalledProductRegistration version not found' }
Write-Text $pk ($t.Substring(0, $m.Groups[2].Index) + $Version + $t.Substring($m.Groups[2].Index + $m.Groups[2].Length))
Write-Host "version $old -> $Version"

# 2. language data, tests, build
& python (Join-Path $kroot 'tools\lang_gen.py'); if ($LASTEXITCODE -ne 0) { throw 'lang_gen failed' }
& python (Join-Path $kroot 'tools\lang_check.py'); if ($LASTEXITCODE -ne 0) { throw 'lang_check failed' }
if (-not $NoTest) { & powershell -NoProfile -File (Join-Path $kroot 'tests\run.ps1'); if ($LASTEXITCODE -ne 0) { throw 'tests failed' } }
& powershell -NoProfile -File (Join-Path $kroot 'build.ps1'); if ($LASTEXITCODE -ne 0) { throw 'build failed' }
$built = Join-Path $kroot 'bin\K-CppAssist.vsix'

# 3. the built vsix must carry the new version
Add-Type -AssemblyName System.IO.Compression.FileSystem
$zip = [IO.Compression.ZipFile]::OpenRead($built)
try
{
    $e = $zip.GetEntry('extension.vsixmanifest')
    $sr = New-Object IO.StreamReader($e.Open(), $utf8)
    $mtext = $sr.ReadToEnd(); $sr.Close()
}
finally { $zip.Dispose() }
if ($mtext -notmatch ('<Identity [^>]*?\sVersion="' + [regex]::Escape($Version) + '"')) { throw "built vsix is not $Version" }

# 4. docs: replace the vsix, the download link, the size, and add the changelog row
Get-ChildItem $docsDir -Filter 'K-CppUltimateAssist-*.vsix' | ForEach-Object { & git -C $repo rm -q -f $_.FullName | Out-Null; if (Test-Path $_.FullName) { Remove-Item $_.FullName -Force } }
$dest = Join-Path $docsDir "K-CppUltimateAssist-$Version.vsix"
Copy-Item $built $dest -Force
$kb = [int][math]::Round((Get-Item $dest).Length / 1024.0)
$t = Read-Text $index
$nl = if ($t.Contains("`r`n")) { "`r`n" } else { "`n" }
$t = [regex]::Replace($t, 'K-CppUltimateAssist-\d+\.\d+\.\d+\.vsix', "K-CppUltimateAssist-$Version.vsix")
$t = [regex]::Replace($t, 'K-CppUltimateAssist \d+\.\d+\.\d+ をダウンロード（\.vsix、約 \d+ KB）', ('K-CppUltimateAssist ' + $Version + ' ' + [regex]::Unescape('をダウンロード（.vsix、約 ') + $kb + ' KB' + [regex]::Unescape('）')))
$rm = [regex]::Match($t, '(?m)^\| \d+\.\d+\.\d+ \|')
if (-not $rm.Success) { throw 'changelog table not found' }
$t = $t.Insert($rm.Index, "| $Version | $note |$nl")
Write-Text $index $t
$left = Get-ChildItem (Join-Path $repo 'docs') -Recurse -Filter *.md | Select-String -Pattern 'K-CppUltimateAssist-\d+\.\d+\.\d+\.vsix' | Where-Object { $_.Line -notmatch [regex]::Escape($Version) }
if ($left) { $left | ForEach-Object { Write-Warning ("stale link: " + $_.Path + ':' + $_.LineNumber) }; throw 'stale vsix link remains' }
& python (Join-Path $repo 'tools\check_docs.py') (Join-Path $repo 'docs')
if ($LASTEXITCODE -ne 0) { throw 'check_docs failed' }

# 5. commit and push
if (-not $NoCommit)
{
    & git -C $repo add -A 'docs/kcppassist' 'k-cppassist'
    $msg = "K-CppUltimateAssist ${Version}: " + $note.Substring(0, [math]::Min(60, $note.Length)) + "`n`nCo-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>"
    $msgFile = Join-Path ([IO.Path]::GetTempPath()) 'kcppassist-release-msg.txt'
    Write-Text $msgFile $msg
    & git -C $repo commit -q -F $msgFile
    if ($LASTEXITCODE -ne 0) { throw 'commit failed' }
    if (-not $NoPush) { & git -C $repo push -q origin main; if ($LASTEXITCODE -ne 0) { throw 'push failed' } }
}

# 6. install into Visual Studio (close it first)
if (-not $NoInstall)
{
    $vs = & (Join-Path ${env:ProgramFiles(x86)} 'Microsoft Visual Studio\Installer\vswhere.exe') -latest -prerelease -property installationPath
    $vsi = Join-Path $vs 'Common7\IDE\VSIXInstaller.exe'
    $dev = Join-Path $vs 'Common7\IDE\devenv.exe'
    foreach ($p in (Get-Process devenv -ErrorAction SilentlyContinue))
    {
        try { $dte = [Runtime.InteropServices.Marshal]::GetActiveObject('VisualStudio.DTE'); $dte.ExecuteCommand('File.SaveAll'); $dte.Quit() }
        catch { $p.CloseMainWindow() | Out-Null }
    }
    Start-Sleep 8
    & $vsi /quiet '/uninstall:KCppAssist.7d1f3b52-4c80-4e9a-b6a3-0e8f25c91d74'; Write-Host "uninstall $LASTEXITCODE"
    & $vsi /quiet $built; Write-Host "install $LASTEXITCODE"
    if ($LASTEXITCODE -ne 0) { throw 'install failed' }
    & $dev /updateconfiguration
}
Write-Host "released $Version"
