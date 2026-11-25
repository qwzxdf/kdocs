using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

namespace KCppAssist.Vcpkg
{
    /// <summary>vcpkg.json の dependencies の 1 件。</summary>
    internal sealed class Dependency
    {
        public string Name;
        public string MinVersion;                                   // "version>=" (なければ null)
        public List<string> Features = new List<string>();
        public bool DefaultFeatures = true;                          // "default-features"
        public bool Host;
        public string Platform;
    }

    /// <summary>
    /// プロジェクトの vcpkg.json の読み書き。ほかのキー($schema、overrides、builtin-baseline など)と順番はそのまま残す。
    /// 書き込むたびに、直前の内容を覚えておき、「元に戻す」で戻せる(VS を閉じるまで)。
    /// </summary>
    internal sealed class VcpkgManifest
    {
        private static readonly Dictionary<string, Stack<string>> Undo = new Dictionary<string, Stack<string>>(StringComparer.OrdinalIgnoreCase);

        public string Path { get; private set; }
        public string Dir { get { return System.IO.Path.GetDirectoryName(Path); } }
        public JObject Root { get; private set; }
        private bool _crlf;

        public static string FileNameIn(string dir) { return System.IO.Path.Combine(dir, "vcpkg.json"); }

        /// <summary>読み込む。ファイルがなければ、空の vcpkg.json を、メモリの上に作る(Save するまでファイルは作らない)。</summary>
        public static VcpkgManifest Load(string path)
        {
            var m = new VcpkgManifest { Path = path };
            if (File.Exists(path))
            {
                string text = File.ReadAllText(path, Encoding.UTF8);
                m._crlf = text.Contains("\r\n");
                m.Root = JObject.Parse(text);
            }
            else
            {
                m._crlf = true;
                m.Root = new JObject { ["dependencies"] = new JArray() };
            }
            return m;
        }

        public bool Exists { get { return File.Exists(Path); } }

        public string Baseline { get { return (string)Root["builtin-baseline"]; } }

        public List<Dependency> Dependencies()
        {
            var list = new List<Dependency>();
            var arr = Root["dependencies"] as JArray;
            if (arr == null) return list;
            foreach (JToken t in arr)
            {
                var d = new Dependency();
                if (t.Type == JTokenType.String) d.Name = (string)t;
                else
                {
                    d.Name = (string)t["name"];
                    d.MinVersion = (string)t["version>="];
                    if (t["default-features"] != null) d.DefaultFeatures = (bool)t["default-features"];
                    if (t["host"] != null) d.Host = (bool)t["host"];
                    d.Platform = (string)t["platform"];
                    var f = t["features"] as JArray;
                    if (f != null) foreach (JToken x in f) d.Features.Add(x.Type == JTokenType.String ? (string)x : (string)x["name"]);
                }
                if (!string.IsNullOrEmpty(d.Name)) list.Add(d);
            }
            return list;
        }

        public Dependency Find(string name)
        {
            return Dependencies().FirstOrDefault(d => string.Equals(d.Name, name, StringComparison.OrdinalIgnoreCase));
        }

        /// <summary>追加する。すでにあれば、機能・バージョンの指定を置き換える。特別な指定がなければ、名前だけの文字列にする(書式をそろえる)。</summary>
        public void AddOrUpdate(Dependency dep)
        {
            var arr = Root["dependencies"] as JArray;
            if (arr == null) { arr = new JArray(); Root["dependencies"] = arr; }
            JToken value;
            if (dep.Features.Count == 0 && dep.DefaultFeatures && string.IsNullOrEmpty(dep.MinVersion) && !dep.Host && string.IsNullOrEmpty(dep.Platform))
                value = dep.Name;
            else
            {
                var o = new JObject { ["name"] = dep.Name };
                if (dep.Features.Count > 0) o["features"] = new JArray(dep.Features);
                if (!dep.DefaultFeatures) o["default-features"] = false;
                if (!string.IsNullOrEmpty(dep.MinVersion)) o["version>="] = dep.MinVersion;
                if (dep.Host) o["host"] = true;
                if (!string.IsNullOrEmpty(dep.Platform)) o["platform"] = dep.Platform;
                value = o;
            }
            for (int i = 0; i < arr.Count; i++)
            {
                string n = arr[i].Type == JTokenType.String ? (string)arr[i] : (string)arr[i]["name"];
                if (!string.Equals(n, dep.Name, StringComparison.OrdinalIgnoreCase)) continue;
                // 名前以外の指定(platform など)は、置き換えるときに、元の物を引き継ぐ
                if (value.Type == JTokenType.String && arr[i].Type == JTokenType.Object)
                {
                    var keep = (JObject)arr[i].DeepClone();
                    keep.Remove("features"); keep.Remove("default-features"); keep.Remove("version>=");
                    if (keep.Properties().Count() > 1) { Apply(keep, dep); value = keep; }
                }
                else if (value.Type == JTokenType.Object && arr[i].Type == JTokenType.Object)
                {
                    var keep = (JObject)arr[i].DeepClone();
                    Apply(keep, dep);
                    value = keep;
                }
                arr[i] = value;
                return;
            }
            arr.Add(value);
        }

        private static void Apply(JObject o, Dependency dep)
        {
            o.Remove("features"); o.Remove("default-features"); o.Remove("version>=");
            if (dep.Features.Count > 0) o["features"] = new JArray(dep.Features);
            if (!dep.DefaultFeatures) o["default-features"] = false;
            if (!string.IsNullOrEmpty(dep.MinVersion)) o["version>="] = dep.MinVersion;
        }

        /// <summary>builtin-baseline を書く(なければ足す)。</summary>
        public void SetBaseline(string sha)
        {
            Root["builtin-baseline"] = sha;
        }

        /// <summary>builtin-baseline を消す(ベースラインでバージョンを固定しない)。</summary>
        public bool RemoveBaseline()
        {
            return Root.Remove("builtin-baseline");
        }

        public bool Remove(string name)
        {
            var arr = Root["dependencies"] as JArray;
            if (arr == null) return false;
            for (int i = 0; i < arr.Count; i++)
            {
                string n = arr[i].Type == JTokenType.String ? (string)arr[i] : (string)arr[i]["name"];
                if (string.Equals(n, name, StringComparison.OrdinalIgnoreCase)) { arr.RemoveAt(i); return true; }
            }
            return false;
        }

        /// <summary>書き込む。直前の内容を覚えておく(ファイルがまだなかったときは、「なかった」ことを覚える)。</summary>
        public void Save()
        {
            string before = File.Exists(Path) ? File.ReadAllText(Path, Encoding.UTF8) : null;
            string after = Serialize();
            if (before == after) return;
            Stack<string> st;
            if (!Undo.TryGetValue(Path, out st)) Undo[Path] = st = new Stack<string>();
            st.Push(before);
            Directory.CreateDirectory(Dir);
            File.WriteAllText(Path, after, new UTF8Encoding(false));
        }

        private string Serialize()
        {
            var sb = new StringBuilder();
            using (var sw = new StringWriter(sb))
            using (var w = new JsonTextWriter(sw) { Formatting = Formatting.Indented, Indentation = 2, IndentChar = ' ' })
                Root.WriteTo(w);
            string s = sb.ToString();
            if (_crlf) s = s.Replace("\r\n", "\n").Replace("\n", "\r\n");
            return s + (_crlf ? "\r\n" : "\n");
        }

        public static bool CanUndo(string path)
        {
            Stack<string> st;
            return Undo.TryGetValue(path, out st) && st.Count > 0;
        }

        /// <summary>直前の書き込みを元に戻す。ファイルがなかったときは、ファイルを消す。</summary>
        public static bool UndoLast(string path)
        {
            Stack<string> st;
            if (!Undo.TryGetValue(path, out st) || st.Count == 0) return false;
            string before = st.Pop();
            if (before == null) { if (File.Exists(path)) File.Delete(path); }
            else File.WriteAllText(path, before, new UTF8Encoding(false));
            return true;
        }

        // ---------- 入っているものの状態 ----------

        /// <summary>vcpkg_installed\vcpkg\status を読んで、入っているパッケージのバージョン(トリプレット別)を返す。「名前:トリプレット」→ バージョン。</summary>
        public Dictionary<string, string> InstalledVersions()
        {
            var map = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);
            // コマンド ラインでは vcpkg_installed\vcpkg\status、MSBuild では vcpkg_installed\(トリプレット)\vcpkg\status に書かれる
            string root = System.IO.Path.Combine(Dir, "vcpkg_installed");
            var files = new List<string> { System.IO.Path.Combine(root, "vcpkg", "status") };
            try { if (Directory.Exists(root)) foreach (string d in Directory.GetDirectories(root)) files.Add(System.IO.Path.Combine(d, "vcpkg", "status")); }
            catch { }
            foreach (string status in files.Where(File.Exists)) ReadStatus(status, map);
            return map;
        }

        private static void ReadStatus(string status, Dictionary<string, string> map)
        {
            try
            {
                string pkg = null, ver = null, arch = null, st = null; bool feature = false;
                foreach (string raw in File.ReadAllLines(status, Encoding.UTF8).Concat(new[] { "" }))
                {
                    if (raw.Length == 0)
                    {
                        if (pkg != null && !feature && st != null && st.EndsWith("installed", StringComparison.Ordinal)) map[pkg + ":" + arch] = ver;
                        pkg = ver = arch = st = null; feature = false;
                        continue;
                    }
                    int i = raw.IndexOf(':');
                    if (i < 0) continue;
                    string k = raw.Substring(0, i), v = raw.Substring(i + 1).Trim();
                    if (k == "Package") pkg = v;
                    else if (k == "Version") ver = v;
                    else if (k == "Architecture") arch = v;
                    else if (k == "Status") st = v;
                    else if (k == "Feature") feature = true;
                }
            }
            catch { }
        }

        /// <summary>入っているバージョンを、トリプレットを問わずに引く(複数あれば、いちばん新しい物)。</summary>
        public static string InstalledVersion(Dictionary<string, string> map, string name)
        {
            string best = null;
            foreach (var kv in map)
            {
                if (!kv.Key.StartsWith(name + ":", StringComparison.OrdinalIgnoreCase)) continue;
                if (best == null || VcpkgTool.CompareVersions(kv.Value, best) > 0) best = kv.Value;
            }
            return best;
        }
    }

    /// <summary>vcpkg.json の探し方と、トリプレットの一覧。</summary>
    internal static class VcpkgLocator
    {
        /// <summary>フォルダから上へ(最大 6 階層)たどって、vcpkg.json のあるフォルダを探す。</summary>
        public static string FindManifestDir(string start)
        {
            string d = start;
            for (int i = 0; i < 6 && !string.IsNullOrEmpty(d); i++)
            {
                if (File.Exists(VcpkgManifest.FileNameIn(d))) return d;
                d = System.IO.Path.GetDirectoryName(d);
            }
            return null;
        }

        /// <summary>vcpkg の triplets と community、vcpkg.json のそばにある自作のトリプレット(.cmake)を、名前の一覧にする。</summary>
        public static List<string> Triplets(string manifestDir)
        {
            var set = new SortedSet<string>(StringComparer.OrdinalIgnoreCase);
            string root = VcpkgTool.Root;
            if (root != null)
                foreach (string sub in new[] { "triplets", System.IO.Path.Combine("triplets", "community") })
                {
                    string d = System.IO.Path.Combine(root, sub);
                    if (!Directory.Exists(d)) continue;
                    foreach (string f in Directory.GetFiles(d, "*.cmake")) set.Add(System.IO.Path.GetFileNameWithoutExtension(f));
                }
            foreach (string d in OverlayDirs(manifestDir))
                foreach (string f in Directory.GetFiles(d, "*.cmake")) set.Add(System.IO.Path.GetFileNameWithoutExtension(f));
            return set.ToList();
        }

        /// <summary>自作のトリプレットがありそうなフォルダ(vcpkg.json のフォルダとその親)。VCPKG_TARGET_ARCHITECTURE を書いた .cmake があるものだけ。</summary>
        public static List<string> OverlayDirs(string manifestDir)
        {
            var list = new List<string>();
            string d = manifestDir;
            for (int i = 0; i < 2 && !string.IsNullOrEmpty(d); i++, d = System.IO.Path.GetDirectoryName(d))
            {
                try
                {
                    if (Directory.GetFiles(d, "*.cmake").Any(f => File.ReadAllText(f).Contains("VCPKG_TARGET_ARCHITECTURE"))) list.Add(d);
                }
                catch { }
            }
            return list;
        }
    }
}
