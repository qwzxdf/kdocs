using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using KCppAssist;

/// <summary>
/// 実在のリポジトリのヘッダーと cpp で、引数の同期(AutoSync と同じ判定)を総当たりで試す。
/// ヘッダーの宣言(か cpp の定義)ごとに「引数を 1 つ足す」編集を作って、相手がどう書き換わるかを、
/// 名前・const・namespace とクラスの並び・引数の型から求めた正解と照合する。
/// </summary>
static class CorpusMain
{
    static readonly string[] HExt = { ".h", ".hpp", ".hh", ".hxx" };
    static readonly string[] CExt = { ".cpp", ".cc", ".cxx" };

    class Stats
    {
        public int Skipped, Pairs, Decls, Defs;
        public int HtoC_Ok, HtoC_Ambiguous, HtoC_NotFound, HtoC_Skip, HtoC_Wrong, HtoC_Inexact, HtoC_Other, HtoC_Suspicious;
        public int CtoH_Ok, CtoH_Ambiguous, CtoH_NotFound, CtoH_Skip, CtoH_Wrong, CtoH_Inexact, CtoH_Other, CtoH_Suspicious;
        public int Exceptions;
        public List<string> Samples = new List<string>();
    }

    static List<string> Keys(FunctionScan.Sig s, string text)
    {
        var l = SignatureSync.SplitParams(s.Inner(text));
        return l == null ? null : SignatureSync.TypeKeys(l);
    }

    static string W(string x) { return System.Text.RegularExpressions.Regex.Replace(x, @"\s+", ""); }

    static string Qualified(FunctionScan.Sig s) { return string.Join("::", s.Chain.Concat(new[] { s.Name })); }

    static string Line(string text, int pos)
    {
        int a = pos; while (a > 0 && text[a - 1] != '\n') a--;
        int b = pos; while (b < text.Length && text[b] != '\n') b++;
        return text.Substring(a, Math.Min(b - a, 140)).Trim();
    }

    /// <summary>text の sig の括弧に「引数を足す」編集をしたあとの文字と、足した位置。</summary>
    static string AddParam(string text, FunctionScan.Sig s, out int pos, out string ins)
    {
        string inner = s.Inner(text).Trim();
        if (inner.Length == 0) { pos = s.Open + 1; ins = "int kx_"; return text.Substring(0, pos) + ins + text.Substring(pos); }
        if (inner == "void") { pos = s.Open + 1; ins = "int kx_"; return text.Substring(0, s.Open + 1) + ins + text.Substring(s.Close); }
        pos = s.Close; ins = ", int kx_";
        return text.Substring(0, pos) + ins + text.Substring(pos);
    }

    static void Run(string name, string root, Stats st, bool verbose)
    {
        var files = Directory.EnumerateFiles(root, "*.*", SearchOption.AllDirectories).Where(f => !f.Contains(Path.DirectorySeparatorChar + ".git" + Path.DirectorySeparatorChar)).ToList();
        var headers = files.Where(f => HExt.Contains(Path.GetExtension(f).ToLowerInvariant())).ToList();
        var cpps = files.Where(f => CExt.Contains(Path.GetExtension(f).ToLowerInvariant())).ToLookup(f => Path.GetFileNameWithoutExtension(f).ToLowerInvariant());

        var slow = new List<KeyValuePair<long, string>>();
        foreach (string hp in headers)
        {
            foreach (string cp in cpps[Path.GetFileNameWithoutExtension(hp).ToLowerInvariant()])
            {
                string h, c;
                try { h = File.ReadAllText(hp); c = File.ReadAllText(cp); } catch (Exception) { continue; }
                if (h.Length + c.Length > 300 * 1024) { st.Skipped++; continue; }
                st.Pairs++;
                List<FunctionScan.Sig> sh, sc;
                var sw = Stopwatch.StartNew();
                try { sh = FunctionScan.Scan(h); sc = FunctionScan.Scan(c); }
                catch (Exception ex) { st.Exceptions++; st.Samples.Add("EXC scan " + Path.GetFileName(hp) + ": " + ex.Message); continue; }
                sw.Stop();
                slow.Add(new KeyValuePair<long, string>(sw.ElapsedMilliseconds, Path.GetFileName(hp) + "+" + Path.GetFileName(cp) + " (" + (h.Length + c.Length) / 1024 + " KB)"));

                // ---- ヘッダー → cpp ----
                foreach (var d in sh.Where(s => !s.HasBody))
                {
                    st.Decls++;
                    var dk = Keys(d, h);
                    if (dk == null) { st.HtoC_Skip++; continue; }
                    int pos; string ins;
                    string h2 = AddParam(h, d, out pos, out ins);
                    string res;
                    try { res = SyncTests.Sync(h, h2, c); }
                    catch (Exception ex) { st.Exceptions++; st.Samples.Add("EXC H→C " + Qualified(d) + ": " + ex.Message); continue; }

                    var gt = sc.Where(s => s.HasBody && !s.InClass && s.Name == d.Name && s.IsConst == d.IsConst && SyncPlan.ChainScore(s.Chain, d.Chain) > 0 && SyncPlan.SameKeys(Keys(s, c), dk)).ToList();
                    int top = gt.Count == 0 ? 0 : gt.Max(s => SyncPlan.ChainScore(s.Chain, d.Chain));
                    var best = gt.Where(s => SyncPlan.ChainScore(s.Chain, d.Chain) == top).ToList();

                    if (res.StartsWith("!"))
                    {
                        if (res == "!複数ある") { if (best.Count > 1) st.HtoC_Ambiguous++; else { st.HtoC_Wrong++; st.Samples.Add("H→C 複数あると言ったが正解は 1 つ: " + Qualified(d) + " @" + Path.GetFileName(hp)); } }
                        else if (res == "!見つからない")
                        {
                            if (gt.Count > 0) { st.HtoC_Wrong++; st.Samples.Add("H→C 正解があるのに見つからない: " + Qualified(d) + " @" + Path.GetFileName(hp)); }
                            else
                            {
                                st.HtoC_NotFound++;
                                // 定義が cpp に文字としてあるのに見つからなかったもの(解析の取りこぼしの疑い)
                                string simple = System.Text.RegularExpressions.Regex.Escape(d.Name);
                                var rx = new System.Text.RegularExpressions.Regex(@"(?m)^[^\r\n;]*\b" + (d.Chain.Count > 0 ? System.Text.RegularExpressions.Regex.Escape(d.Chain.Last()) + @"\s*::\s*" : "") + simple + @"\s*\([^;{]*\)[^;{]*\{");
                                if (rx.IsMatch(c)) { st.HtoC_Suspicious++; if (st.Samples.Count < 400) st.Samples.Add("H→C 疑い(文字としては定義がある): " + Qualified(d) + "(" + SignatureSync.Norm(d.Inner(h)) + ") @" + Path.GetFileName(hp)); }
                            }
                        }
                        else { st.HtoC_Other++; st.Samples.Add("H→C 別の理由 " + res + ": " + Qualified(d)); }
                        continue;
                    }
                    // 書き換えた。正解の定義の「)」の位置に、「, int kx_」だけが入っているか
                    var expectedPositions = best.Select(s => s.Close).ToList();
                    int diffAt = 0; while (diffAt < c.Length && diffAt < res.Length && c[diffAt] == res[diffAt]) diffAt++;
                    bool lengthOk = res.Length - c.Length == ins.Length || (res.Length - c.Length == "int kx_".Length - (SignatureSync.Norm(d.Inner(h)) == "void" ? 4 : 0));
                    if (best.Count == 1 && (diffAt == best[0].Close || diffAt == best[0].Open + 1 || diffAt <= best[0].Close && diffAt >= best[0].Open + 1))
                    {
                        string expected = null;
                        int p2; string i2;
                        string c2 = AddParam(c, best[0], out p2, out i2);
                        expected = c2;
                        if (W(res) == W(expected)) st.HtoC_Ok++;
                        else { st.HtoC_Inexact++; st.Samples.Add("H→C 不正確: " + Qualified(d) + "\n      元: " + Line(c, best[0].Open) + "\n      後: " + Line(res, best[0].Open)); }
                    }
                    else
                    {
                        st.HtoC_Wrong++;
                        st.Samples.Add("H→C 違う場所を書き換えた: " + Qualified(d) + "(" + SignatureSync.Norm(d.Inner(h)) + ") @" + Path.GetFileName(hp) + " → " + Line(res, diffAt) + (best.Count == 0 ? " [正解なし]" : ""));
                    }
                    _ = lengthOk;
                }

                // ---- cpp → ヘッダー ----
                foreach (var d in sc.Where(s => s.HasBody && !s.InClass))
                {
                    st.Defs++;
                    var dk = Keys(d, c);
                    if (dk == null) { st.CtoH_Skip++; continue; }
                    int pos; string ins;
                    string c2 = AddParam(c, d, out pos, out ins);
                    string res;
                    try { res = SyncTests.Sync(c, c2, h); }
                    catch (Exception ex) { st.Exceptions++; st.Samples.Add("EXC C→H " + Qualified(d) + ": " + ex.Message); continue; }

                    var gt = sh.Where(s => !s.HasBody && s.Name == d.Name && s.IsConst == d.IsConst && SyncPlan.ChainScore(s.Chain, d.Chain) > 0 && SyncPlan.SameKeys(Keys(s, h), dk)).ToList();
                    int top = gt.Count == 0 ? 0 : gt.Max(s => SyncPlan.ChainScore(s.Chain, d.Chain));
                    var best = gt.Where(s => SyncPlan.ChainScore(s.Chain, d.Chain) == top).ToList();

                    if (res.StartsWith("!"))
                    {
                        if (res == "!複数ある") { if (best.Count > 1) st.CtoH_Ambiguous++; else { st.CtoH_Wrong++; st.Samples.Add("C→H 複数あると言ったが正解は 1 つ: " + Qualified(d)); } }
                        else if (res == "!見つからない")
                        {
                            if (gt.Count > 0) { st.CtoH_Wrong++; st.Samples.Add("C→H 正解があるのに見つからない: " + Qualified(d) + " @" + Path.GetFileName(cp)); }
                            else st.CtoH_NotFound++;
                        }
                        else { st.CtoH_Other++; st.Samples.Add("C→H 別の理由 " + res + ": " + Qualified(d)); }
                        continue;
                    }
                    int diffAt = 0; while (diffAt < h.Length && diffAt < res.Length && h[diffAt] == res[diffAt]) diffAt++;
                    if (best.Count == 1 && diffAt >= best[0].Open + 1 && diffAt <= best[0].Close)
                    {
                        int p2; string i2;
                        string h2 = AddParam(h, best[0], out p2, out i2);
                        // ヘッダーの新しい引数は、cpp と同じ「int kx_」(既定値なし)
                        if (W(res) == W(h2)) st.CtoH_Ok++;
                        else { st.CtoH_Inexact++; st.Samples.Add("C→H 不正確: " + Qualified(d) + "\n      元: " + Line(h, best[0].Open) + "\n      後: " + Line(res, best[0].Open)); }
                    }
                    else
                    {
                        st.CtoH_Wrong++;
                        st.Samples.Add("C→H 違う場所を書き換えた: " + Qualified(d) + " @" + Path.GetFileName(cp) + " → " + Line(res, diffAt) + (best.Count == 0 ? " [正解なし]" : ""));
                    }
                }
            }
        }

        Console.WriteLine("=== " + name + " ===");
        Console.WriteLine("  組(ヘッダー+cpp): " + st.Pairs + "(300KB 超で省略 " + st.Skipped + ")" + "   宣言: " + st.Decls + "   定義: " + st.Defs + "   例外: " + st.Exceptions);
        Console.WriteLine("  H→cpp  正確に反映: " + st.HtoC_Ok + "  複数(書かない): " + st.HtoC_Ambiguous + "  見つからない: " + st.HtoC_NotFound + "(うち疑い " + st.HtoC_Suspicious + ")  不正確: " + st.HtoC_Inexact + "  違う場所/取りこぼし: " + st.HtoC_Wrong + "  その他: " + st.HtoC_Other + "  読めない: " + st.HtoC_Skip);
        Console.WriteLine("  cpp→H  正確に反映: " + st.CtoH_Ok + "  複数(書かない): " + st.CtoH_Ambiguous + "  見つからない: " + st.CtoH_NotFound + "  不正確: " + st.CtoH_Inexact + "  違う場所/取りこぼし: " + st.CtoH_Wrong + "  その他: " + st.CtoH_Other + "  読めない: " + st.CtoH_Skip);
        Console.WriteLine("  解析が遅い順: " + string.Join(" / ", slow.OrderByDescending(x => x.Key).Take(3).Select(x => x.Key + "ms " + x.Value)));
        foreach (string s in st.Samples.Where(s => !s.StartsWith("H→C 疑い")).Take(verbose ? 40 : 12)) Console.WriteLine("    - " + s);
        foreach (string s in st.Samples.Where(s => s.StartsWith("H→C 疑い")).Take(verbose ? 25 : 8)) Console.WriteLine("    - " + s);
    }

    static int Main(string[] args)
    {
        bool verbose = args.Length > 1 && args[1] == "-v";
        string root = args[0];
        foreach (string dir in Directory.GetDirectories(root))
            Run(Path.GetFileName(dir), dir, new Stats(), verbose);
        return 0;
    }
}
