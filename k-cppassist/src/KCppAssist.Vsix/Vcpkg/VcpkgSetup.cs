using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading;
using System.Threading.Tasks;

namespace KCppAssist.Vcpkg
{
    /// <summary>
    /// vcpkg を使うための土台: VS との連携(integrate install)の確認、.vcxproj のマニフェスト モード、vcpkg 本体の導入。
    /// </summary>
    internal static class VcpkgSetup
    {
        private static string LocalAppData { get { return Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData); } }

        // ---------- VS との連携 (vcpkg integrate install) ----------

        /// <summary>`vcpkg integrate install` が書き出すファイル。これがあれば、MSBuild が vcpkg を呼べる。</summary>
        public static string UserTargets { get { return Path.Combine(LocalAppData, "vcpkg", "vcpkg.user.targets"); } }

        public static bool Integrated { get { return File.Exists(UserTargets); } }

        // ---------- .vcxproj のマニフェスト モード ----------

        public static List<string> ProjectFiles(string dir)
        {
            try { return Directory.Exists(dir) ? Directory.GetFiles(dir, "*.vcxproj", SearchOption.TopDirectoryOnly).ToList() : new List<string>(); }
            catch { return new List<string>(); }
        }

        private static readonly Regex ManifestElem = new Regex(@"<VcpkgEnableManifest>\s*([^<]*?)\s*</VcpkgEnableManifest>", RegexOptions.IgnoreCase);
        private static readonly Regex EnabledElem = new Regex(@"<VcpkgEnabled>\s*([^<]*?)\s*</VcpkgEnabled>", RegexOptions.IgnoreCase);
        private static readonly Regex TripletElem = new Regex(@"<VcpkgTriplet>", RegexOptions.IgnoreCase);

        /// <summary>
        /// マニフェスト モードの状態。true: 有効、false: 無効、null: 書いていない(既定は無効)。
        /// 条件つきの指定が混ざるときは、1 つでも true があれば true とみなす。VcpkgEnabled が false だけのときは、vcpkg 自体が止まっているので false。
        /// </summary>
        public static bool? ManifestMode(string vcxproj)
        {
            string text;
            try { text = File.ReadAllText(vcxproj); } catch { return null; }
            var m = ManifestElem.Matches(text).Cast<Match>().Select(x => x.Groups[1].Value.Trim().ToLowerInvariant()).ToList();
            if (m.Count == 0) return null;
            if (!m.Any(v => v == "true")) return false;
            var e = EnabledElem.Matches(text).Cast<Match>().Select(x => x.Groups[1].Value.Trim().ToLowerInvariant()).ToList();
            if (e.Count > 0 && e.All(v => v == "false")) return false;
            return true;
        }

        /// <summary>
        /// .vcxproj で、マニフェスト モードを有効にする(VcpkgEnabled と VcpkgEnableManifest を true にする)。
        /// 書式は壊さず、必要な行だけを足す・書き換える。書き換えたときは true を返す。
        /// </summary>
        public static bool EnableManifest(string vcxproj, string triplet, out string message)
        {
            message = null;
            byte[] raw = File.ReadAllBytes(vcxproj);
            bool bom = raw.Length >= 3 && raw[0] == 0xEF && raw[1] == 0xBB && raw[2] == 0xBF;
            string text = new UTF8Encoding(false).GetString(raw, bom ? 3 : 0, raw.Length - (bom ? 3 : 0));
            string nl = text.Contains("\r\n") ? "\r\n" : "\n";
            string before = text;

            if (ManifestElem.IsMatch(text))
                text = ManifestElem.Replace(text, "<VcpkgEnableManifest>true</VcpkgEnableManifest>");
            // 止めてあった VcpkgEnabled(false)は、true に直す(戻したいときは、「元に戻す」ではなく、プロジェクトのプロパティで)
            if (EnabledElem.IsMatch(text))
                text = EnabledElem.Replace(text, "<VcpkgEnabled>true</VcpkgEnabled>");

            if (!ManifestElem.IsMatch(text))
            {
                var sb = new StringBuilder();
                sb.Append("  <PropertyGroup Label=\"Vcpkg\">").Append(nl);
                if (!EnabledElem.IsMatch(text)) sb.Append("    <VcpkgEnabled>true</VcpkgEnabled>").Append(nl);
                sb.Append("    <VcpkgEnableManifest>true</VcpkgEnableManifest>").Append(nl);
                if (!string.IsNullOrEmpty(triplet) && triplet != "x64-windows" && !TripletElem.IsMatch(text))
                    sb.Append("    <VcpkgTriplet>").Append(triplet).Append("</VcpkgTriplet>").Append(nl);
                sb.Append("  </PropertyGroup>").Append(nl);
                // 置き場所: Globals の PropertyGroup の直後。なければ、Microsoft.Cpp.Default.props の読み込みの前
                Match g = Regex.Match(text, @"<PropertyGroup[^>]*Label=""Globals""[^>]*>.*?</PropertyGroup>[ \t]*\r?\n", RegexOptions.Singleline);
                if (g.Success) text = text.Insert(g.Index + g.Length, sb.ToString());
                else
                {
                    Match d = Regex.Match(text, @"^[ \t]*<Import\s+Project=""[^""]*Microsoft\.Cpp\.Default\.props""", RegexOptions.Multiline);
                    if (!d.Success) { message = "Globals の PropertyGroup が見つかりませんでした"; return false; }
                    text = text.Insert(d.Index, sb.ToString());
                }
            }
            if (text == before) return false;
            byte[] body = new UTF8Encoding(false).GetBytes(text);
            using (var fs = new FileStream(vcxproj, FileMode.Create, FileAccess.Write))
            {
                if (bom) fs.Write(new byte[] { 0xEF, 0xBB, 0xBF }, 0, 3);
                fs.Write(body, 0, body.Length);
            }
            return true;
        }

        /// <summary>.vcxproj で、vcpkg を OFF にする(VcpkgEnabled を false にする。なければ、足す)。書き換えたときは true。</summary>
        public static bool Disable(string vcxproj, out string message)
        {
            message = null;
            byte[] raw = File.ReadAllBytes(vcxproj);
            bool bom = raw.Length >= 3 && raw[0] == 0xEF && raw[1] == 0xBB && raw[2] == 0xBF;
            string text = new UTF8Encoding(false).GetString(raw, bom ? 3 : 0, raw.Length - (bom ? 3 : 0));
            string nl = text.Contains("\r\n") ? "\r\n" : "\n";
            string before = text;
            if (EnabledElem.IsMatch(text)) text = EnabledElem.Replace(text, "<VcpkgEnabled>false</VcpkgEnabled>");
            else
            {
                string group = "  <PropertyGroup Label=\"Vcpkg\">" + nl + "    <VcpkgEnabled>false</VcpkgEnabled>" + nl + "  </PropertyGroup>" + nl;
                Match g = Regex.Match(text, @"<PropertyGroup[^>]*Label=""Globals""[^>]*>.*?</PropertyGroup>[ \t]*\r?\n", RegexOptions.Singleline);
                if (g.Success) text = text.Insert(g.Index + g.Length, group);
                else
                {
                    Match d = Regex.Match(text, @"^[ \t]*<Import\s+Project=""[^""]*Microsoft\.Cpp\.Default\.props""", RegexOptions.Multiline);
                    if (!d.Success) { message = "Globals の PropertyGroup が見つかりませんでした"; return false; }
                    text = text.Insert(d.Index, group);
                }
            }
            if (text == before) return false;
            byte[] body = new UTF8Encoding(false).GetBytes(text);
            using (var fs = new FileStream(vcxproj, FileMode.Create, FileAccess.Write))
            {
                if (bom) fs.Write(new byte[] { 0xEF, 0xBB, 0xBF }, 0, 3);
                fs.Write(body, 0, body.Length);
            }
            return true;
        }

        // ---------- vcpkg 本体を入れる ----------

        public static string FindGit()
        {
            foreach (string dir in (Environment.GetEnvironmentVariable("PATH") ?? "").Split(';'))
            {
                try { string p = Path.Combine(dir.Trim().Trim('"'), "git.exe"); if (File.Exists(p)) return p; } catch (Exception swallowed) { Safe.Ignore(swallowed); }
            }
            foreach (string pf in new[] { Environment.GetEnvironmentVariable("ProgramFiles"), Environment.GetEnvironmentVariable("ProgramFiles(x86)") })
            {
                if (string.IsNullOrEmpty(pf)) continue;
                string p = Path.Combine(pf, "Git", "cmd", "git.exe");
                if (File.Exists(p)) return p;
            }
            return null;
        }

        public static string VsInstaller
        {
            get
            {
                string pf = Environment.GetEnvironmentVariable("ProgramFiles(x86)");
                if (string.IsNullOrEmpty(pf)) return null;
                string p = Path.Combine(pf, "Microsoft Visual Studio", "Installer", "vs_installer.exe");
                return File.Exists(p) ? p : null;
            }
        }

        public static Task<RunResult> RunProcessAsync(string file, string args, string workDir, Action<string> onLine, CancellationToken ct)
        {
            return Task.Run(() =>
            {
                var result = new RunResult();
                var sb = new StringBuilder();
                var psi = new ProcessStartInfo(file, args)
                {
                    WorkingDirectory = string.IsNullOrEmpty(workDir) ? VcpkgTool.DataDir : workDir,
                    UseShellExecute = false,
                    RedirectStandardOutput = true,
                    RedirectStandardError = true,
                    CreateNoWindow = true,
                };
                using (var p = new Process { StartInfo = psi })
                {
                    DataReceivedEventHandler h = (s, e) =>
                    {
                        if (e.Data == null) return;
                        lock (sb) sb.AppendLine(e.Data);
                        if (onLine != null) onLine(e.Data);
                    };
                    p.OutputDataReceived += h;
                    p.ErrorDataReceived += h;
                    try { p.Start(); }
                    catch (Exception ex) { result.ExitCode = -1; result.Output = ex.Message; return result; }
                    p.BeginOutputReadLine();
                    p.BeginErrorReadLine();
                    using (ct.Register(() => { try { VcpkgTool.Kill(p); } catch (Exception swallowed) { Safe.Ignore(swallowed); } })) { p.WaitForExit(); }
                    p.WaitForExit();
                    result.Canceled = ct.IsCancellationRequested;
                    result.ExitCode = p.ExitCode;
                }
                lock (sb) result.Output = sb.ToString();
                return result;
            });
        }

        /// <summary>
        /// 指定のフォルダーに vcpkg を入れる: git clone → bootstrap-vcpkg.bat → 環境変数 VCPKG_ROOT(ユーザー)を設定。
        /// ベースラインの解決には履歴が要るので、浅い clone(--depth)にはしない。
        /// </summary>
        public static async Task<bool> InstallVcpkgAsync(string folder, bool setRoot, Action<string> log, CancellationToken ct)
        {
            string git = FindGit();
            if (git == null) { log(L.T("git が見つかりません。先に Git を入れてください (Visual Studio インストーラーの「Git for Windows」、または winget install Git.Git)。")); return false; }
            folder = (folder ?? "").Trim().Trim('"');
            if (folder.Length == 0) { log(L.T("入れるフォルダーを指定してください。")); return false; }
            if (Directory.Exists(folder) && Directory.EnumerateFileSystemEntries(folder).Any() && !File.Exists(Path.Combine(folder, "bootstrap-vcpkg.bat")))
            { log(L.F("{0} は空ではありません。空のフォルダーか、まだないフォルダーを指定してください。", folder)); return false; }

            if (!File.Exists(Path.Combine(folder, "bootstrap-vcpkg.bat")))
            {
                log("> git clone https://github.com/microsoft/vcpkg.git " + folder);
                RunResult c = await RunProcessAsync(git, "clone https://github.com/microsoft/vcpkg.git \"" + folder + "\"", null, log, ct);
                if (!c.Ok) { log(c.Canceled ? L.T("中止しました。") : L.F("git clone に失敗しました (終了コード {0})。", c.ExitCode)); return false; }
            }
            log("> bootstrap-vcpkg.bat -disableMetrics");
            RunResult b = await RunProcessAsync("cmd.exe", "/c \"bootstrap-vcpkg.bat -disableMetrics\"", folder, log, ct);
            if (!b.Ok || !File.Exists(Path.Combine(folder, "vcpkg.exe")))
            { log(b.Canceled ? L.T("中止しました。") : L.F("bootstrap に失敗しました (終了コード {0})。", b.ExitCode)); return false; }

            if (setRoot)
            {
                try
                {
                    Environment.SetEnvironmentVariable("VCPKG_ROOT", folder, EnvironmentVariableTarget.User);
                    Environment.SetEnvironmentVariable("VCPKG_ROOT", folder, EnvironmentVariableTarget.Process);
                    log(L.F("環境変数 VCPKG_ROOT を {0} に設定しました (ユーザー)。起動済みの Visual Studio には、再起動すると反映されます。", folder));
                }
                catch (Exception ex) { log(L.F("VCPKG_ROOT を設定できませんでした: {0}", ex.Message)); }
            }
            return true;
        }
    }
}
