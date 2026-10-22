using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

namespace KHlsl.Server
{
    /// <summary>.khlsl.json の内容。</summary>
    internal sealed class Config
    {
        public string dxc;
        public string target;                 // 例: "lib_6_9"。未指定なら新しい順に試す
        public string entry;
        public string hlslVersion;            // 例: "2021"
        public List<string> defines = new List<string>();
        public List<string> includeDirs = new List<string>();
        public List<string> args = new List<string>();
        public bool diagnostics = true;
        public bool enable16bit = false;

        public string Root;                   // .khlsl.json のあるフォルダー

        public static Config For(string docPath)
        {
            string dir = Path.GetDirectoryName(docPath);
            while (!string.IsNullOrEmpty(dir))
            {
                string p = Path.Combine(dir, ".khlsl.json");
                if (File.Exists(p))
                {
                    try
                    {
                        var c = JsonConvert.DeserializeObject<Config>(File.ReadAllText(p, Encoding.UTF8)) ?? new Config();
                        c.Root = dir;
                        if (c.defines == null) c.defines = new List<string>();
                        if (c.includeDirs == null) c.includeDirs = new List<string>();
                        if (c.args == null) c.args = new List<string>();
                        return c;
                    }
                    catch (Exception) { }
                }
                dir = Path.GetDirectoryName(dir);
            }
            return new Config { Root = Path.GetDirectoryName(docPath) };
        }

        public IEnumerable<string> ResolvedIncludeDirs()
        {
            foreach (var d in includeDirs)
                yield return Path.IsPathRooted(d) ? d : Path.GetFullPath(Path.Combine(Root, d));
        }
    }

    internal sealed class Diag
    {
        public int Line, Col, EndCol;
        public int Severity;   // 1 error, 2 warning, 3 info
        public string Message;
    }

    /// <summary>DXC を実際に呼んで診断を作る。独自の構文解析でエラーを出さないので、新しい構文でも誤検出しない。</summary>
    internal static class Dxc
    {
        private static string _cached;

        private static readonly string[] Fallbacks = { "lib_6_9", "lib_6_8", "lib_6_7", "lib_6_6", "lib_6_5", "lib_6_3" };

        public static string Find(Config cfg)
        {
            if (!string.IsNullOrEmpty(cfg.dxc) && File.Exists(cfg.dxc)) return cfg.dxc;
            if (_cached != null && File.Exists(_cached)) return _cached;
            string env = Environment.GetEnvironmentVariable("KHLSL_DXC");
            if (!string.IsNullOrEmpty(env) && File.Exists(env)) return _cached = env;
            foreach (var dir in (Environment.GetEnvironmentVariable("PATH") ?? "").Split(';'))
            {
                try
                {
                    string p = Path.Combine(dir.Trim('"'), "dxc.exe");
                    if (File.Exists(p)) return _cached = p;
                }
                catch (Exception) { }
            }
            string vk = Environment.GetEnvironmentVariable("VULKAN_SDK");
            if (!string.IsNullOrEmpty(vk))
            {
                string p = Path.Combine(vk, "Bin", "dxc.exe");
                if (File.Exists(p)) return _cached = p;
            }
            foreach (var root in new[]
            {
                Environment.GetEnvironmentVariable("ProgramFiles(x86)"),
                Environment.GetEnvironmentVariable("ProgramFiles")
            })
            {
                if (string.IsNullOrEmpty(root)) continue;
                string bin = Path.Combine(root, "Windows Kits", "10", "bin");
                if (!Directory.Exists(bin)) continue;
                var cands = Directory.GetDirectories(bin).Select(d => new { d, v = ParseVer(Path.GetFileName(d)) })
                    .OrderByDescending(x => x.v).ToList();
                foreach (var c in cands)
                {
                    string p = Path.Combine(c.d, "x64", "dxc.exe");
                    if (File.Exists(p)) return _cached = p;
                }
            }
            return null;
        }

        private static Version ParseVer(string s)
        {
            Version v;
            return Version.TryParse(s, out v) ? v : new Version(0, 0);
        }

        /// <summary>ファイルの先頭 30 行の "// khlsl: ..." から、追加の引数を取る。</summary>
        public static List<string> MagicArgs(string text)
        {
            var args = new List<string>();
            int count = 0;
            foreach (var raw in text.Split('\n'))
            {
                if (++count > 30) break;
                var m = Regex.Match(raw, @"^\s*//\s*khlsl:\s*(.*)$");
                if (!m.Success) continue;
                foreach (Match t in Regex.Matches(m.Groups[1].Value, @"""[^""]*""|\S+"))
                    args.Add(t.Value.Trim('"'));
            }
            return args;
        }

        public static string Run(string docPath, string text, Config cfg, CancellationToken ct, out List<Diag> diags, out string problem)
        {
            diags = new List<Diag>();
            problem = null;
            string exe = Find(cfg);
            if (exe == null)
            {
                problem = "dxc.exe が見つかりません。.khlsl.json の \"dxc\" か、環境変数 KHLSL_DXC に dxc.exe のパスを指定してください(Windows SDK か DirectXShaderCompiler の配布物に入っています)。";
                return null;
            }
            var magic = MagicArgs(text);
            bool userTarget = magic.Contains("-T") || cfg.args.Contains("-T");
            string temp = Path.Combine(Path.GetTempPath(), "khlsl", (uint)docPath.GetHashCode() + "_" + Path.GetFileName(docPath));
            Directory.CreateDirectory(Path.GetDirectoryName(temp));
            File.WriteAllText(temp, text, new UTF8Encoding(false));

            var targets = userTarget ? new[] { (string)null } : (cfg.target != null ? new[] { cfg.target } : Fallbacks);
            string last = null;
            foreach (var t in targets)
            {
                if (ct.IsCancellationRequested) return null;
                var a = new List<string>();
                if (t != null) { a.Add("-T"); a.Add(t); }
                if (cfg.entry != null && !magic.Contains("-E")) { a.Add("-E"); a.Add(cfg.entry); }
                if (cfg.hlslVersion != null) { a.Add("-HV"); a.Add(cfg.hlslVersion); }
                if (cfg.enable16bit) a.Add("-enable-16bit-types");
                a.Add("-I"); a.Add(Path.GetDirectoryName(docPath));
                foreach (var d in cfg.ResolvedIncludeDirs()) { a.Add("-I"); a.Add(d); }
                foreach (var d in cfg.defines) { a.Add("-D"); a.Add(d); }
                a.AddRange(cfg.args);
                a.AddRange(magic);
                a.Add("-Fo"); a.Add("NUL");
                a.Add(temp);

                string output = Exec(exe, a, Path.GetDirectoryName(docPath), ct);
                last = output;
                if (output == null) return null;
                // プロファイルが古い DXC で使えないときは、次の候補へ
                if (!userTarget && cfg.target == null && Regex.IsMatch(output, @"(unknown|invalid|unsupported)\s+(shader model|target|profile)|Unknown target|invalid profile|not supported", RegexOptions.IgnoreCase)
                    && output.IndexOf(t, StringComparison.Ordinal) >= 0 && !Regex.IsMatch(output, @":\d+:\d+: error:"))
                    continue;
                diags = Parse(output, temp, docPath);
                return t;
            }
            diags = Parse(last ?? "", temp, docPath);
            return null;
        }

        private static string Exec(string exe, List<string> args, string cwd, CancellationToken ct)
        {
            var psi = new ProcessStartInfo
            {
                FileName = exe,
                Arguments = string.Join(" ", args.Select(Quote)),
                WorkingDirectory = cwd,
                UseShellExecute = false,
                CreateNoWindow = true,
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                StandardOutputEncoding = Encoding.UTF8,
                StandardErrorEncoding = Encoding.UTF8
            };
            var sb = new StringBuilder();
            using (var p = new Process { StartInfo = psi })
            {
                p.OutputDataReceived += (s, e) => { if (e.Data != null) lock (sb) sb.AppendLine(e.Data); };
                p.ErrorDataReceived += (s, e) => { if (e.Data != null) lock (sb) sb.AppendLine(e.Data); };
                try { p.Start(); } catch (Exception) { return null; }
                p.BeginOutputReadLine();
                p.BeginErrorReadLine();
                using (ct.Register(() => { try { if (!p.HasExited) p.Kill(); } catch (Exception) { } }))
                {
                    if (!p.WaitForExit(20000)) { try { p.Kill(); } catch (Exception) { } }
                    p.WaitForExit();
                }
                if (ct.IsCancellationRequested) return null;
            }
            lock (sb) return sb.ToString();
        }

        private static string Quote(string s)
        {
            if (s.Length > 0 && s.IndexOfAny(new[] { ' ', '\t', '"' }) < 0) return s;
            return "\"" + s.Replace("\\", "\\\\").Replace("\"", "\\\"") + "\"";
        }

        private static readonly Regex RxDiag = new Regex(@"^(?<file>.+?):(?<line>\d+):(?<col>\d+): (?<sev>fatal error|error|warning|note|remark): (?<msg>.*)$", RegexOptions.Compiled);

        public static List<Diag> Parse(string output, string temp, string docPath)
        {
            var list = new List<Diag>();
            Diag prev = null;
            string[] lines = output.Replace("\r", "").Split('\n');
            string text = null;
            try { text = File.ReadAllText(temp); } catch (Exception) { }
            string[] src = text == null ? new string[0] : text.Split('\n');
            foreach (var raw in lines)
            {
                var m = RxDiag.Match(raw);
                if (!m.Success) continue;
                string file = m.Groups["file"].Value;
                string sev = m.Groups["sev"].Value;
                string msg = m.Groups["msg"].Value;
                int line = int.Parse(m.Groups["line"].Value) - 1;
                int col = Math.Max(0, int.Parse(m.Groups["col"].Value) - 1);
                bool mine = SamePath(file, temp) || SamePath(file, docPath);
                // ライブラリ ターゲットで検証しているための、ノイズの警告は出さない
                if (msg.StartsWith("#pragma once in main file", StringComparison.Ordinal)
                    || Regex.IsMatch(msg, @"^attribute '.+' ignored without accompanying shader attribute")) { prev = null; continue; }
                if (sev == "note")
                {
                    if (prev != null)
                        prev.Message += "\n" + (mine ? "" : Path.GetFileName(file) + ":" + (line + 1) + ": ") + msg;
                    continue;
                }
                var d = new Diag { Severity = sev == "warning" ? 2 : sev == "remark" ? 3 : 1 };
                if (mine)
                {
                    d.Line = line; d.Col = col;
                    string sl = line < src.Length ? src[line].TrimEnd('\r') : "";
                    int e = col;
                    while (e < sl.Length && (char.IsLetterOrDigit(sl[e]) || sl[e] == '_')) e++;
                    d.EndCol = e > col ? e : Math.Min(col + 1, Math.Max(col, sl.Length));
                    d.Message = msg;
                }
                else
                {
                    // インクルードしたファイル側のエラー。このファイルの先頭に出す
                    d.Line = 0; d.Col = 0; d.EndCol = 1;
                    d.Message = Path.GetFileName(file) + ":" + (line + 1) + ": " + msg;
                }
                list.Add(d);
                prev = d;
            }
            return list;
        }

        private static bool SamePath(string a, string b)
        {
            try { return string.Equals(Path.GetFullPath(a), Path.GetFullPath(b), StringComparison.OrdinalIgnoreCase); }
            catch (Exception) { return false; }
        }
    }
}
