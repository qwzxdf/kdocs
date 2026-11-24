using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Net.Http;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading;
using System.Threading.Tasks;
using Newtonsoft.Json.Linq;

namespace KCppAssist.Vcpkg
{
    /// <summary>vcpkg.exe を実行した結果。</summary>
    internal sealed class RunResult
    {
        public int ExitCode;
        public string Output;
        public bool Canceled;
        public bool Ok { get { return ExitCode == 0 && !Canceled; } }
    }

    /// <summary>`vcpkg search` で分かる 1 件(名前・最新の版・説明・機能)。</summary>
    internal sealed class PortInfo
    {
        public string Name;
        public string Version;
        public string Description;
        public List<KeyValuePair<string, string>> Features = new List<KeyValuePair<string, string>>();   // 機能名 → 説明
    }

    /// <summary>GitHub の vcpkg に載っている、ポートの詳細(ホームページ・ライセンスなど)。</summary>
    internal sealed class PortDetail
    {
        public string Homepage, License, Supports, Version;           // Version: GitHub の vcpkg にある、最新の版
        public List<string> Dependencies = new List<string>();
        public Dictionary<string, string> FeatureDescriptions = new Dictionary<string, string>();
        public List<string> DefaultFeatures = new List<string>();      // 既定で入る機能(default-features)
    }

    /// <summary>vcpkg.exe の場所の特定と、実行、検索結果・詳細の取得、版の比較。画面からは、ここだけを使う。</summary>
    internal static class VcpkgTool
    {
        private static string _exe;

        /// <summary>キャッシュなどを置く %LOCALAPPDATA%\K-CppAssist\vcpkg。</summary>
        public static string DataDir
        {
            get
            {
                string d = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "K-CppAssist", "vcpkg");
                Directory.CreateDirectory(d);
                return d;
            }
        }

        /// <summary>vcpkg.exe の場所。見つからなければ null。環境変数 VCPKG_ROOT → VS が覚えている場所 → C:\vcpkg → VS 付属、の順に探す。</summary>
        public static string FindExe(bool refresh = false)
        {
            if (_exe != null && !refresh && File.Exists(_exe)) return _exe;
            var dirs = new List<string>();
            string root = Environment.GetEnvironmentVariable("VCPKG_ROOT");
            if (!string.IsNullOrEmpty(root)) dirs.Add(root);
            try
            {
                string pathTxt = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "vcpkg", "vcpkg.path.txt");
                if (File.Exists(pathTxt)) dirs.Add(File.ReadAllText(pathTxt).Trim());
            }
            catch { }
            dirs.Add(@"C:\vcpkg");
            foreach (string pf in new[] { Environment.GetEnvironmentVariable("ProgramFiles"), Environment.GetEnvironmentVariable("ProgramFiles(x86)") })
            {
                if (string.IsNullOrEmpty(pf)) continue;
                string vsRoot = Path.Combine(pf, "Microsoft Visual Studio");
                if (!Directory.Exists(vsRoot)) continue;
                try
                {
                    foreach (string v in Directory.GetDirectories(vsRoot).OrderByDescending(x => x))
                        foreach (string ed in Directory.GetDirectories(v)) dirs.Add(Path.Combine(ed, "VC", "vcpkg"));
                }
                catch { }
            }
            // ports フォルダがある vcpkg(全部入り)を優先する。VS 付属の物は、manifest でしか、ポートを引けない
            string fallback = null;
            foreach (string d in dirs)
            {
                try
                {
                    string dir = d.Trim().Trim('"');
                    string exe = Path.Combine(dir, "vcpkg.exe");
                    if (!File.Exists(exe)) continue;
                    if (Directory.Exists(Path.Combine(dir, "ports"))) { _exe = exe; return exe; }
                    if (fallback == null) fallback = exe;
                }
                catch { }
            }
            _exe = fallback;
            return fallback;
        }

        /// <summary>ports フォルダがある(全部入り)vcpkg か。そうなら、どのフォルダからでも search などが使える。</summary>
        public static bool HasPorts
        {
            get { string r = Root; return r != null && Directory.Exists(Path.Combine(r, "ports")); }
        }

        /// <summary>
        /// search や depend-info を、プロジェクトに関係なく動かすためのフォルダ。
        /// 全部入りの vcpkg なら、ただのフォルダ。VS 付属の vcpkg は manifest がないとポートを引けないので、builtin-baseline つきの vcpkg.json を置いた作業フォルダを使う。
        /// </summary>
        public static async Task<string> NeutralDirAsync(string baselineHint, CancellationToken ct)
        {
            if (HasPorts) return DataDir;
            string dir = Path.Combine(DataDir, "work");
            Directory.CreateDirectory(dir);
            string shaFile = Path.Combine(dir, "baseline.txt");
            string sha = baselineHint;
            if (string.IsNullOrEmpty(sha) && File.Exists(shaFile) && DateTime.UtcNow - File.GetLastWriteTimeUtc(shaFile) < TimeSpan.FromDays(7)) sha = File.ReadAllText(shaFile).Trim();
            if (string.IsNullOrEmpty(sha))
            {
                try
                {
                    string j = await Http.GetStringAsync("https://api.github.com/repos/microsoft/vcpkg/commits/master");
                    sha = (string)JObject.Parse(j)["sha"];
                }
                catch { }
            }
            if (string.IsNullOrEmpty(sha) && File.Exists(shaFile)) sha = File.ReadAllText(shaFile).Trim();
            if (string.IsNullOrEmpty(sha)) return dir;
            File.WriteAllText(shaFile, sha);
            File.WriteAllText(Path.Combine(dir, "vcpkg.json"), "{"+"\n"+" \"name\": \"k-vcpkg-browser\", \"version\": \"0\", \"builtin-baseline\": \""+sha+"\" }\n", new UTF8Encoding(false));
            return dir;
        }

        /// <summary>vcpkg の置き場所(triplets フォルダがある所)。</summary>
        public static string Root
        {
            get { string e = FindExe(); return e == null ? null : Path.GetDirectoryName(e); }
        }

        /// <summary>vcpkg.exe を実行する。1 行出るたびに onLine を呼ぶ(別のスレッドから呼ばれる)。</summary>
        public static Task<RunResult> RunAsync(string arguments, string workDir, Action<string> onLine, CancellationToken ct)
        {
            return Task.Run(() =>
            {
                string exe = FindExe();
                var result = new RunResult();
                if (exe == null) { result.ExitCode = -1; result.Output = "vcpkg.exe not found"; return result; }
                var sb = new StringBuilder();
                var psi = new ProcessStartInfo(exe, arguments)
                {
                    WorkingDirectory = string.IsNullOrEmpty(workDir) ? DataDir : workDir,
                    UseShellExecute = false,
                    RedirectStandardOutput = true,
                    RedirectStandardError = true,
                    CreateNoWindow = true,
                    StandardOutputEncoding = Encoding.UTF8,
                    StandardErrorEncoding = Encoding.UTF8,
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
                    using (ct.Register(() => { try { Kill(p); } catch { } }))
                    {
                        p.WaitForExit();
                    }
                    p.WaitForExit();            // 出力の読み取りが終わるのを待つ
                    result.Canceled = ct.IsCancellationRequested;
                    result.ExitCode = p.ExitCode;
                }
                lock (sb) result.Output = sb.ToString();
                return result;
            });
        }

        internal static void Kill(Process p)
        {
            if (p.HasExited) return;
            try
            {
                var k = Process.Start(new ProcessStartInfo("taskkill", "/PID " + p.Id + " /T /F") { CreateNoWindow = true, UseShellExecute = false });
                if (k != null) k.WaitForExit(3000);
            }
            catch { p.Kill(); }
        }

        // ---------- 検索の一覧(全パッケージ) ----------

        /// <summary>直前の一覧の取得が失敗したときの、vcpkg の出力。</summary>
        public static string LastError;

        private static string PortsCache { get { return Path.Combine(DataDir, "ports.json"); } }

        /// <summary>全パッケージの一覧。`vcpkg search` の結果を、1 日だけキャッシュする。取れなければ、古いキャッシュを使う。</summary>
        public static async Task<List<PortInfo>> LoadPortsAsync(bool refresh, string baselineHint, CancellationToken ct)
        {
            string cache = PortsCache;
            if (!refresh && File.Exists(cache) && DateTime.UtcNow - File.GetLastWriteTimeUtc(cache) < TimeSpan.FromDays(1))
            {
                var c = ReadCache(cache);
                if (c != null && c.Count > 0) return c;
            }
            if (FindExe() != null)
            {
                string work = await NeutralDirAsync(baselineHint, ct);
                RunResult json = await RunAsync("search --x-json", work, null, ct);
                RunResult text = json.Ok ? await RunAsync("search --x-full-desc", work, null, ct) : null;
                LastError = json.Ok ? null : json.Output;
                if (json.Ok && text != null && text.Ok)
                {
                    List<PortInfo> list = Parse(json.Output, text.Output);
                    if (list.Count > 0) { WriteCache(cache, list); return list; }
                }
            }
            return ReadCache(cache) ?? new List<PortInfo>();
        }

        internal static List<PortInfo> Parse(string json, string text)
        {
            var map = new Dictionary<string, PortInfo>(StringComparer.OrdinalIgnoreCase);
            int from = json.IndexOf('{'), to = json.LastIndexOf('}');          // JSON のあとに、注意書きの行が付くことがある
            JObject root = JObject.Parse(json.Substring(from, to - from + 1));
            foreach (var kv in root)
            {
                var o = kv.Value as JObject;
                if (o == null) continue;
                string v = (string)o["version"] ?? (string)o["version-string"] ?? (string)o["version-semver"] ?? (string)o["version-date"] ?? "";
                int pv = o["port_version"] != null ? (int)o["port_version"] : 0;
                var desc = o["description"] as JArray;
                map[kv.Key] = new PortInfo
                {
                    Name = kv.Key,
                    Version = v + (pv > 0 ? "#" + pv : ""),
                    Description = desc == null ? "" : string.Join(" ", desc.Select(x => (string)x)),
                };
            }
            // 機能は "名前[機能]   説明" の行から取る
            var re = new Regex(@"^(\S+?)\[([^\]]+)\]\s*(.*)$");
            foreach (string line in text.Split('\n'))
            {
                Match m = re.Match(line.TrimEnd('\r'));
                if (!m.Success) continue;
                PortInfo p;
                if (map.TryGetValue(m.Groups[1].Value, out p) && m.Groups[2].Value != "core")
                    p.Features.Add(new KeyValuePair<string, string>(m.Groups[2].Value, m.Groups[3].Value.Trim()));
            }
            return map.Values.OrderBy(p => p.Name, StringComparer.OrdinalIgnoreCase).ToList();
        }

        private static void WriteCache(string path, List<PortInfo> list)
        {
            try
            {
                var arr = new JArray(list.Select(p => new JObject
                {
                    ["n"] = p.Name, ["v"] = p.Version, ["d"] = p.Description,
                    ["f"] = new JArray(p.Features.Select(f => new JArray(f.Key, f.Value))),
                }));
                File.WriteAllText(path, arr.ToString(Newtonsoft.Json.Formatting.None), new UTF8Encoding(false));
            }
            catch { }
        }

        private static List<PortInfo> ReadCache(string path)
        {
            try
            {
                if (!File.Exists(path)) return null;
                var arr = JArray.Parse(File.ReadAllText(path, Encoding.UTF8));
                return arr.Select(t =>
                {
                    var p = new PortInfo { Name = (string)t["n"], Version = (string)t["v"], Description = (string)t["d"] };
                    foreach (var f in (JArray)t["f"]) p.Features.Add(new KeyValuePair<string, string>((string)f[0], (string)f[1]));
                    return p;
                }).ToList();
            }
            catch { return null; }
        }

        // ---------- ポートの詳細(GitHub) ----------

        private static readonly HttpClient Http = CreateHttp();

        private static HttpClient CreateHttp()
        {
            var c = new HttpClient { Timeout = TimeSpan.FromSeconds(15) };
            c.DefaultRequestHeaders.UserAgent.ParseAdd("K-CppUltimateAssist");
            return c;
        }

        /// <summary>ホームページ・ライセンス・対応環境・依存を、GitHub の vcpkg の vcpkg.json から取る。1 度取ったものは、ファイルに残す。つながらなければ null。</summary>
        public static async Task<PortDetail> LoadDetailAsync(string name, CancellationToken ct)
        {
            if (!Regex.IsMatch(name ?? "", @"^[a-z0-9][a-z0-9\-]*$")) return null;       // URL に入れる前に、名前の形を確かめる
            string dir = Path.Combine(DataDir, "ports");
            Directory.CreateDirectory(dir);
            string file = Path.Combine(dir, name + ".json");
            string text = null;
            if (File.Exists(file) && DateTime.UtcNow - File.GetLastWriteTimeUtc(file) < TimeSpan.FromDays(1)) text = File.ReadAllText(file, Encoding.UTF8);
            if (text == null)
            {
                try
                {
                    text = await Http.GetStringAsync("https://raw.githubusercontent.com/microsoft/vcpkg/master/ports/" + name + "/vcpkg.json");
                    File.WriteAllText(file, text, new UTF8Encoding(false));
                }
                catch
                {
                    if (File.Exists(file)) text = File.ReadAllText(file, Encoding.UTF8);       // つながらなければ、古くても残っている物を使う
                }
            }
            if (text == null) return null;
            try
            {
                JObject o = JObject.Parse(text);
                var d = new PortDetail { Homepage = (string)o["homepage"], License = LicenseText(o["license"]), Supports = (string)o["supports"] };
                string v = (string)o["version"] ?? (string)o["version-semver"] ?? (string)o["version-date"] ?? (string)o["version-string"];
                if (v != null) d.Version = v + (o["port-version"] != null && (int)o["port-version"] > 0 ? "#" + (int)o["port-version"] : "");
                var deps = o["dependencies"] as JArray;
                if (deps != null)
                    foreach (JToken t in deps)
                    {
                        string n = t.Type == JTokenType.String ? (string)t : (string)t["name"];
                        bool host = t.Type == JTokenType.Object && t["host"] != null && (bool)t["host"];
                        if (!string.IsNullOrEmpty(n) && !host) d.Dependencies.Add(n);           // ビルド用の道具(host)は、実行時の依存ではないので外す
                    }
                var feats = o["features"] as JObject;
                if (feats != null)
                    foreach (var f in feats)
                    {
                        var fo = f.Value as JObject;
                        if (fo != null && fo["description"] != null) d.FeatureDescriptions[f.Key] = (string)fo["description"];
                    }
                var defs = o["default-features"] as JArray;
                if (defs != null)
                    foreach (JToken t in defs) { string n = t.Type == JTokenType.String ? (string)t : (string)t["name"]; if (!string.IsNullOrEmpty(n)) d.DefaultFeatures.Add(n); }
                return d;
            }
            catch { return null; }
        }

        private static string LicenseText(JToken t)
        {
            if (t == null) return null;
            return t.Type == JTokenType.String ? (string)t : null;
        }

        // ---------- 版の比較 ----------

        /// <summary>"3.2.10" と "3.10.0"、"2025-04-16"、"1.2.3#2" のような版を比べる。数字は数として、それ以外は文字として比べる。</summary>
        public static int CompareVersions(string a, string b)
        {
            a = StripPort(a); b = StripPort(b);
            string[] pa = Regex.Split(a ?? "", @"[.\-_+]");
            string[] pb = Regex.Split(b ?? "", @"[.\-_+]");
            for (int i = 0; i < Math.Max(pa.Length, pb.Length); i++)
            {
                string x = i < pa.Length ? pa[i] : "0";
                string y = i < pb.Length ? pb[i] : "0";
                long nx, ny;
                int c = long.TryParse(x, out nx) && long.TryParse(y, out ny) ? nx.CompareTo(ny) : string.Compare(x, y, StringComparison.OrdinalIgnoreCase);
                if (c != 0) return c;
            }
            return 0;
        }

        private static string StripPort(string v)
        {
            if (v == null) return "";
            int i = v.IndexOf('#');
            return i < 0 ? v : v.Substring(0, i);
        }
    }
}
