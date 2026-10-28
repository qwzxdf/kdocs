using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading;
using System.Threading.Tasks;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

namespace KHlsl.Server
{
    internal static class Program
    {
        private static int Main()
        {
            Console.OutputEncoding = new UTF8Encoding(false);
            var server = new Server(Console.OpenStandardInput(), Console.OpenStandardOutput());
            return server.Run();
        }
    }

    /// <summary>LSP のトランスポート(stdin / stdout)と、リクエストの振り分け。</summary>
    internal sealed partial class Server
    {
        private readonly Stream _in;
        private readonly Stream _out;
        private readonly object _writeLock = new object();
        private readonly Db _db;
        private readonly Dictionary<string, string> _docs = new Dictionary<string, string>();
        private readonly Dictionary<string, CancellationTokenSource> _diag = new Dictionary<string, CancellationTokenSource>();
        private readonly Dictionary<string, Tuple<DateTime, FileScan>> _incCache = new Dictionary<string, Tuple<DateTime, FileScan>>(StringComparer.OrdinalIgnoreCase);
        private bool _shutdown;
        private bool _warnedNoDxc;

        public Server(Stream input, Stream output)
        {
            _in = input;
            _out = output;
            _db = Db.Load();
            FileLog("server started pid=" + System.Diagnostics.Process.GetCurrentProcess().Id);
        }

        public int Run()
        {
            while (true)
            {
                JObject msg;
                try { msg = Read(); }
                catch (Exception) { return 1; }
                if (msg == null) return _shutdown ? 0 : 1;
                var sw = System.Diagnostics.Stopwatch.StartNew();
                try { Dispatch(msg); FileLog("   done " + (string)msg["method"] + " " + sw.ElapsedMilliseconds + "ms"); }
                catch (Exception ex)
                {
                    var id = msg["id"];
                    if (id != null) Respond(id, null);
                    Log("error: " + ex);
                }
                if ((string)msg["method"] == "exit") return _shutdown ? 0 : 1;
            }
        }

        // ---- 入出力 ----
        private JObject Read()
        {
            int contentLength = -1;
            while (true)
            {
                string line = ReadLine();
                if (line == null) return null;
                if (line.Length == 0) break;
                var m = Regex.Match(line, @"^Content-Length:\s*(\d+)", RegexOptions.IgnoreCase);
                if (m.Success) contentLength = int.Parse(m.Groups[1].Value);
            }
            if (contentLength < 0) return null;
            var buf = new byte[contentLength];
            int got = 0;
            while (got < contentLength)
            {
                int n = _in.Read(buf, got, contentLength - got);
                if (n <= 0) return null;
                got += n;
            }
            return JObject.Parse(Encoding.UTF8.GetString(buf));
        }

        private string ReadLine()
        {
            var sb = new StringBuilder();
            while (true)
            {
                int b = _in.ReadByte();
                if (b < 0) return sb.Length == 0 ? null : sb.ToString();
                if (b == '\n') return sb.ToString().TrimEnd('\r');
                sb.Append((char)b);
            }
        }

        private void Send(JObject o)
        {
            byte[] body = Encoding.UTF8.GetBytes(o.ToString(Formatting.None));
            byte[] head = Encoding.ASCII.GetBytes("Content-Length: " + body.Length + "\r\n\r\n");
            lock (_writeLock)
            {
                _out.Write(head, 0, head.Length);
                _out.Write(body, 0, body.Length);
                _out.Flush();
            }
        }

        private void Respond(JToken id, JToken result)
        {
            Send(new JObject { ["jsonrpc"] = "2.0", ["id"] = id, ["result"] = result ?? JValue.CreateNull() });
        }

        private void Notify(string method, JToken p)
        {
            Send(new JObject { ["jsonrpc"] = "2.0", ["method"] = method, ["params"] = p });
        }

        private static readonly string LogPath = Path.Combine(
            Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "K-HLSL", "server.log");

        private static void FileLog(string text)
        {
            try
            {
                Directory.CreateDirectory(Path.GetDirectoryName(LogPath));
                if (File.Exists(LogPath) && new FileInfo(LogPath).Length > 512 * 1024) File.Delete(LogPath);
                File.AppendAllText(LogPath, DateTime.Now.ToString("HH:mm:ss.fff") + " " + text + Environment.NewLine, Encoding.UTF8);
            }
            catch (Exception) { }
        }

        private void Log(string text)
        {
            FileLog(text);
            try { Notify("window/logMessage", new JObject { ["type"] = 4, ["message"] = "[K-HLSL] " + text }); }
            catch (Exception) { }
        }

        // ---- 振り分け ----
        private void Dispatch(JObject msg)
        {
            string method = (string)msg["method"];
            JToken id = msg["id"];
            JToken p = msg["params"];
            FileLog("<- " + method + (id != null ? " #" + id : "") + (p is JArray ? " [array params]" : "") + (p is JObject && p["position"] != null ? " @" + p["position"]["line"] + ":" + p["position"]["character"] : ""));
            switch (method)
            {
                case "initialize": Respond(id, Initialize()); break;
                case "initialized": System.Threading.Tasks.Task.Run(() => Warmup()); break;
                case "shutdown": _shutdown = true; Respond(id, null); break;
                case "exit": break;
                case "textDocument/didOpen":
                {
                    string uri = (string)p["textDocument"]["uri"];
                    _docs[uri] = (string)p["textDocument"]["text"];
                    ScheduleDiagnostics(uri, 0);
                    break;
                }
                case "textDocument/didChange":
                {
                    string uri = (string)p["textDocument"]["uri"];
                    var changes = (JArray)p["contentChanges"];
                    if (changes.Count > 0) _docs[uri] = (string)changes[changes.Count - 1]["text"];
                    ScheduleDiagnostics(uri, 700);
                    break;
                }
                case "textDocument/didSave":
                {
                    string uri = (string)p["textDocument"]["uri"];
                    if (p["text"] != null && p["text"].Type == JTokenType.String) _docs[uri] = (string)p["text"];
                    ScheduleDiagnostics(uri, 0);
                    break;
                }
                case "textDocument/didClose":
                {
                    string uri = (string)p["textDocument"]["uri"];
                    _docs.Remove(uri);
                    CancelDiag(uri);
                    Notify("textDocument/publishDiagnostics", new JObject { ["uri"] = uri, ["diagnostics"] = new JArray() });
                    break;
                }
                case "textDocument/completion": Respond(id, Completion(p)); break;
                case "textDocument/hover": Respond(id, Hover(p)); break;
                case "textDocument/signatureHelp": Respond(id, SignatureHelp(p)); break;
                case "textDocument/documentSymbol": Respond(id, DocumentSymbols(p)); break;
                case "textDocument/definition": Respond(id, Definition(p)); break;
                case "textDocument/codeLens": Respond(id, CodeLens(p)); break;
                case "textDocument/formatting": Respond(id, FormatRequest(p, -1, -1)); break;
                case "textDocument/rangeFormatting":
                    Respond(id, FormatRequest(p, (int)p["range"]["start"]["line"], (int)p["range"]["end"]["line"]));
                    break;
                case "textDocument/onTypeFormatting":
                {
                    int line = (int)p["position"]["line"];
                    Respond(id, FormatRequest(p, line, line));
                    break;
                }
                case "khlsl/cbuffers": Respond(id, CBuffersRequest(p)); break;
                case "khlsl/cppcompare": Respond(id, CppCompareRequest(p)); break;
                case "khlsl/cppstruct": Respond(id, CppStructProbe(p)); break;
                default:
                    if (id != null) Respond(id, null);
                    break;
            }
        }

        /// <summary>初回のリクエストが JIT で遅くならないよう、起動直後に一通り呼んでおく。</summary>
        private void Warmup()
        {
            try
            {
                string uri = "file:///khlsl-warmup/warmup.hlsl";
                string text = string.Join(Environment.NewLine, new[]
                {
                    "struct S { float3 p; };",
                    "Texture2D<float4> t : register(t0);",
                    "float4 f(float3 a) { return lerp(a.x, 1, 0.5); }",
                    "void main() { float4 c = t.Sample(s, 0); c.xyz; }",
                    ""
                });
                var td = new JObject { ["uri"] = uri };
                lock (_docs) _docs[uri] = text;
                Completion(new JObject { ["textDocument"] = td, ["position"] = new JObject { ["line"] = 3, ["character"] = 20 } });
                Completion(new JObject { ["textDocument"] = td, ["position"] = new JObject { ["line"] = 3, ["character"] = 30 } });
                Hover(new JObject { ["textDocument"] = td, ["position"] = new JObject { ["line"] = 2, ["character"] = 30 } });
                SignatureHelp(new JObject { ["textDocument"] = td, ["position"] = new JObject { ["line"] = 2, ["character"] = 38 } });
                DocumentSymbols(new JObject { ["textDocument"] = td });
                Definition(new JObject { ["textDocument"] = td, ["position"] = new JObject { ["line"] = 2, ["character"] = 7 } });
                lock (_docs) _docs.Remove(uri);
                FileLog("warmup done");
            }
            catch (Exception ex) { FileLog("warmup failed: " + ex.Message); }
        }

        private JToken Initialize()
        {
            return new JObject
            {
                ["capabilities"] = new JObject
                {
                    ["textDocumentSync"] = new JObject { ["openClose"] = true, ["change"] = 1, ["save"] = new JObject { ["includeText"] = true } },
                    ["completionProvider"] = new JObject { ["triggerCharacters"] = new JArray(".", ":", "#", "[", "(") },
                    ["hoverProvider"] = true,
                    ["signatureHelpProvider"] = new JObject { ["triggerCharacters"] = new JArray("(", ","), ["retriggerCharacters"] = new JArray(",") },
                    ["documentSymbolProvider"] = true,
                    ["definitionProvider"] = true,
                    ["codeLensProvider"] = new JObject { ["resolveProvider"] = false },
                    ["documentFormattingProvider"] = true,
                    ["documentRangeFormattingProvider"] = true,
                    ["documentOnTypeFormattingProvider"] = new JObject { ["firstTriggerCharacter"] = "}", ["moreTriggerCharacter"] = new JArray(";") }
                },
                ["serverInfo"] = new JObject { ["name"] = "K-HLSL", ["version"] = "1.3.6" }
            };
        }

        // ---- 整形 ----
        /// <summary>startLine〜endLine(-1 なら全体)の、整形で変わる行だけを、最小の TextEdit にして返す。</summary>
        private JToken FormatRequest(JToken p, int startLine, int endLine)
        {
            string uri = (string)p["textDocument"]["uri"];
            var opt = p["options"];
            int tab = opt != null && opt["tabSize"] != null ? (int)opt["tabSize"] : 4;
            bool spaces = opt == null || opt["insertSpaces"] == null || (bool)opt["insertSpaces"];
            var lines = HlslFormatter.SplitLines(TextOf(uri));
            var res = HlslFormatter.Format(lines, tab, spaces);
            var edits = new JArray();
            for (int i = 0; i < lines.Length; i++)
            {
                if (startLine >= 0 && (i < startLine || i > endLine)) continue;
                string a = lines[i], b = res[i];
                if (a == b) continue;
                int pre = 0;
                while (pre < a.Length && pre < b.Length && a[pre] == b[pre]) pre++;
                int suf = 0;
                while (suf < a.Length - pre && suf < b.Length - pre && a[a.Length - 1 - suf] == b[b.Length - 1 - suf]) suf++;
                edits.Add(new JObject
                {
                    ["range"] = Range(i, pre, i, a.Length - suf),
                    ["newText"] = b.Substring(pre, b.Length - suf - pre)
                });
            }
            return edits;
        }

        // ---- 診断 ----
        private void CancelDiag(string uri)
        {
            lock (_diag)
            {
                CancellationTokenSource old;
                if (_diag.TryGetValue(uri, out old)) { old.Cancel(); _diag.Remove(uri); }
            }
        }

        private void ScheduleDiagnostics(string uri, int delayMs)
        {
            CancelDiag(uri);
            var cts = new CancellationTokenSource();
            lock (_diag) _diag[uri] = cts;
            string text;
            if (!_docs.TryGetValue(uri, out text)) return;
            string path = PathOf(uri);
            Task.Run(() =>
            {
                try
                {
                    if (delayMs > 0) Task.Delay(delayMs, cts.Token).Wait(cts.Token);
                    if (cts.IsCancellationRequested) return;
                    var cfg = Config.For(path);
                    if (!cfg.diagnostics)
                    {
                        Notify("textDocument/publishDiagnostics", new JObject { ["uri"] = uri, ["diagnostics"] = new JArray() });
                        return;
                    }
                    List<Diag> diags; string problem;
                    string used = Dxc.Run(path, text, cfg, cts.Token, out diags, out problem);
                    if (cts.IsCancellationRequested) return;
                    if (problem != null)
                    {
                        if (!_warnedNoDxc)
                        {
                            _warnedNoDxc = true;
                            Notify("window/showMessage", new JObject { ["type"] = 2, ["message"] = "K-HLSL: " + problem });
                        }
                        return;
                    }
                    var arr = new JArray();
                    foreach (var d in diags)
                        arr.Add(new JObject
                        {
                            ["range"] = Range(d.Line, d.Col, d.Line, Math.Max(d.EndCol, d.Col + 1)),
                            ["severity"] = d.Severity,
                            ["source"] = "dxc" + (used != null ? " (" + used + ")" : ""),
                            ["message"] = d.Message
                        });
                    Notify("textDocument/publishDiagnostics", new JObject { ["uri"] = uri, ["diagnostics"] = arr });
                }
                catch (Exception) { }
            });
        }

        // ---- 共通の道具 ----
        private static string PathOf(string uri)
        {
            try { return new Uri(uri).LocalPath; } catch (Exception) { return uri; }
        }

        private static string UriOf(string path)
        {
            try { return new Uri(path).AbsoluteUri; } catch (Exception) { return path; }
        }

        private static JObject Range(int l1, int c1, int l2, int c2)
        {
            return new JObject
            {
                ["start"] = new JObject { ["line"] = l1, ["character"] = c1 },
                ["end"] = new JObject { ["line"] = l2, ["character"] = c2 }
            };
        }

        private static JObject Markdown(string md)
        {
            return new JObject { ["kind"] = "markdown", ["value"] = md };
        }

        private string TextOf(string uri)
        {
            string t;
            if (_docs.TryGetValue(uri, out t)) return t;
            // URI の書き方(ドライブ文字の大小、%20 など)が違っても、同じファイルなら、開いている本文を使う
            string path = PathOf(uri);
            foreach (var kv in _docs)
                if (string.Equals(PathOf(kv.Key), path, StringComparison.OrdinalIgnoreCase)) return kv.Value;
            try { return File.ReadAllText(path); } catch (Exception) { return ""; }
        }

        private static bool IsIdent(char c) { return char.IsLetterOrDigit(c) || c == '_'; }

        /// <summary>このファイルと、#include したファイルのシンボルをまとめる。</summary>
        private List<Sym> Collect(string uri, string text)
        {
            var result = new List<Sym>();
            string path = PathOf(uri);
            var visited = new HashSet<string>(StringComparer.OrdinalIgnoreCase) { path };
            var cfg = Config.For(path);
            var open = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);
            foreach (var kv in _docs) open[PathOf(kv.Key)] = kv.Value;
            var own = Analyzer.Scan(path, text);
            result.AddRange(own.Syms);
            var queue = new Queue<Tuple<string, string, int>>();
            foreach (var inc in own.Includes) queue.Enqueue(Tuple.Create(inc, path, 1));
            while (queue.Count > 0)
            {
                var item = queue.Dequeue();
                string resolved = ResolveInclude(item.Item1, item.Item2, cfg);
                if (resolved == null || !visited.Add(resolved)) continue;
                FileScan scan;
                string live;
                if (open.TryGetValue(resolved, out live)) scan = Analyzer.Scan(resolved, live);
                else
                {
                    DateTime stamp = File.GetLastWriteTimeUtc(resolved);
                    Tuple<DateTime, FileScan> c;
                    if (_incCache.TryGetValue(resolved, out c) && c.Item1 == stamp) scan = c.Item2;
                    else
                    {
                        string t;
                        try { t = File.ReadAllText(resolved); } catch (Exception) { continue; }
                        scan = Analyzer.Scan(resolved, t);
                        _incCache[resolved] = Tuple.Create(stamp, scan);
                    }
                }
                result.AddRange(scan.Syms.Where(s => !s.Local));
                if (item.Item3 < 8)
                    foreach (var inc in scan.Includes) queue.Enqueue(Tuple.Create(inc, resolved, item.Item3 + 1));
            }
            return result;
        }

        private static string ResolveInclude(string name, string fromFile, Config cfg)
        {
            try
            {
                var dirs = new List<string> { Path.GetDirectoryName(fromFile) };
                dirs.AddRange(cfg.ResolvedIncludeDirs());
                foreach (var d in dirs)
                {
                    string p = Path.GetFullPath(Path.Combine(d, name));
                    if (File.Exists(p)) return p;
                }
            }
            catch (Exception) { }
            return null;
        }
    }
}
