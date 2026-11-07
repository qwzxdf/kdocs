using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;
using KCppAssist;

/// <summary>
/// 実在のリポジトリのヘッダーと cpp で、Alt+R(宣言 ⇄ 定義を作る)・Alt+Q/W(代入文の切り出しと型)・Alt+E(ゲッター・セッター)・Alt+F(#include)の
/// VS に依存しない部分を、総当たりで試す。引数の同期(Alt+G と自動)は Corpus.cs。
/// 作る編集を実際に適用して、読み直したときに期待どおりの関数・クラスが見えるかを確かめる。
/// </summary>
static class Corpus2
{
    static readonly string[] HExt = { ".h", ".hpp", ".hh", ".hxx" };
    static readonly string[] CExt = { ".cpp", ".cc", ".cxx" };

    class R
    {
        public int Pairs, Skipped;
        // 宣言 → 定義
        public int D2F_Tried, D2F_Ok, D2F_Fail;
        public Dictionary<string, int> D2F_Refused = new Dictionary<string, int>();
        // 定義 → 宣言
        public int F2D_Tried, F2D_Ok, F2D_Fail;
        public Dictionary<string, int> F2D_Refused = new Dictionary<string, int>();
        // 代入文
        public int As_Lines, As_Found, As_Wrong, As_Typed;
        public double As_MaxMs;
        // ゲッター・セッター
        public int Acc_Members, Acc_Made, Acc_Refused, Acc_NoType, Acc_Fail;
        // #include
        public int Inc_Tried, Inc_Added, Inc_Already, Inc_Fail;
        public int Exceptions;
        public List<string> Fails = new List<string>();
        public List<string> Samples = new List<string>();
    }

    static string PrevLine(string t, int idx)
    {
        int e = LineStart(t, idx) - 1;
        while (e > 0)
        {
            int b = e; while (b > 0 && t[b - 1] != '\n') b--;
            string l = t.Substring(b, Math.Max(0, e - b)).Trim();
            if (l.Length > 0) return l.Length > 70 ? l.Substring(0, 70) : l;
            e = b - 1;
        }
        return "";
    }

    static string W(string x) { return Regex.Replace(x, @"\s+", ""); }

    static List<List<string>> Keys(FunctionScan.Sig s, string text) { return SignatureSync.KeyVariants(s.Inner(text)); }

    // PrefixStart は前の文の「;」の直後なので、同じ行に前の宣言が残っていることがある。
    // その行の残りが空白だけなら次の行の頭から、そうでなければ行頭から消す(前の宣言を巻き込まない)。
    static int LineStart(string t, int i)
    {
        int nl = i;
        while (nl < t.Length && (t[nl] == ' ' || t[nl] == '\t' || t[nl] == '\r')) nl++;
        if (nl < t.Length && t[nl] == '\n' && i > 0 && t[i - 1] != '\n') return nl + 1;
        while (i > 0 && t[i - 1] != '\n') i--;
        return i;
    }

    static string Apply(string text, int pos, string ins) { return text.Substring(0, pos) + ins + text.Substring(pos); }

    static void Count(Dictionary<string, int> d, string k) { int v; d.TryGetValue(k, out v); d[k] = v + 1; }

    static void Fail(R r, string msg) { if (r.Fails.Count < 60) r.Fails.Add(msg); }

    static void Run(string name, string root, R r)
    {
        var files = Directory.EnumerateFiles(root, "*.*", SearchOption.AllDirectories).Where(f => !f.Contains(Path.DirectorySeparatorChar + ".git" + Path.DirectorySeparatorChar)).ToList();
        var headers = files.Where(f => HExt.Contains(Path.GetExtension(f).ToLowerInvariant())).ToList();
        var cppFiles = files.Where(f => CExt.Contains(Path.GetExtension(f).ToLowerInvariant())).ToList();
        var cpps = cppFiles.ToLookup(f => Path.GetFileNameWithoutExtension(f).ToLowerInvariant());
        var rng = new Random(1);

        // ---- Alt+R と Alt+G 以外: 1 ファイルずつ ----
        foreach (string f in cppFiles.Concat(headers))
        {
            string t;
            try { t = File.ReadAllText(f); } catch (Exception) { continue; }
            if (t.Length > 400 * 1024) continue;
            string eol = t.Contains("\r\n") ? "\r\n" : "\n";
            bool isHeader = HExt.Contains(Path.GetExtension(f).ToLowerInvariant());

            try
            {
                // Alt+Q / Alt+W: 「名前 = 右辺;」の文
                if (!isHeader)
                {
                    foreach (Match m in Regex.Matches(t, @"(?m)^[ \t]+(this\s*->\s*)?([A-Za-z_]\w*)\s*=(?!=)[^;{}]*;[ \t]*(?://[^\r\n]*)?\r?$"))
                    {
                        r.As_Lines++;
                        string nm = m.Groups[2].Value;
                        int caret = m.Index + m.Value.IndexOf(nm) + nm.Length / 2;
                        var sw = Stopwatch.StartNew();
                        var a = AssignScan.Find(t, caret);
                        sw.Stop();
                        r.As_MaxMs = Math.Max(r.As_MaxMs, sw.Elapsed.TotalMilliseconds);
                        if (a == null) { r.As_Wrong++; Fail(r, "代入 見つからない: " + Path.GetFileName(f) + ": " + m.Value.Trim() + "   ← 直前: " + PrevLine(t, m.Index)); continue; }
                        if (a.Name != nm || a.Rhs.Length == 0 || a.Rhs.EndsWith(";")) { r.As_Wrong++; Fail(r, "代入 切り出しが違う: " + Path.GetFileName(f) + ": " + m.Value.Trim() + " → " + a.Name + " = " + a.Rhs); continue; }
                        r.As_Found++;
                        string ty = TypeInference.FromExpression(Regex.Replace(a.Rhs, @"\s+", " "));
                        if (ty != null) { r.As_Typed++; if (r.Samples.Count < 400 && rng.Next(40) == 0) r.Samples.Add("型 " + ty + "  ← " + Regex.Replace(a.Rhs, @"\s+", " ")); }
                    }
                }

                // Alt+E: メンバー変数のゲッター・セッター
                if (isHeader)
                {
                    foreach (var cls in AccessorEditor.All(t))
                    {
                        string body = t.Substring(cls.Open + 1, cls.Close - cls.Open - 1);
                        string mask = CppText.Mask(body);
                        int depth = 0, ls = 0;
                        var seen = new HashSet<string>();
                        for (int i = 0; i <= mask.Length; i++)
                        {
                            if (i == mask.Length || mask[i] == '\n')
                            {
                                if (depth == 0 && i > ls)
                                {
                                    string line = mask.Substring(ls, i - ls);
                                    string member = AccessorEditor.NameFromDeclarationLine(line);
                                    if (member != null && seen.Add(member))
                                    {
                                        r.Acc_Members++;
                                        bool ro;
                                        string type = AccessorEditor.FindMemberType(t, cls, member, out ro);
                                        if (type == null) { r.Acc_NoType++; }
                                        else
                                        {
                                            string refused;
                                            var skipped = new List<string>();
                                            var lines = AccessorEditor.MakeLines(t, cls, member, type, ro, true, skipped, out refused);
                                            if (lines == null) r.Acc_Refused++;
                                            else if (lines.Count == 0) r.Acc_Refused++;
                                            else
                                            {
                                                var e = AccessorEditor.PlanPublic(t, cls, lines, eol, true);
                                                if (e == null || e.Position < cls.Open || e.Position > cls.Close) { r.Acc_Fail++; Fail(r, "ゲッター 編集の位置が外: " + Path.GetFileName(f) + " " + cls.Name + "::" + member); }
                                                else
                                                {
                                                    string t2 = Apply(t, e.Position, e.Text);
                                                    string m1 = CppText.Mask(t), m2 = CppText.Mask(t2);
                                                    bool balanced = m1.Count(c => c == '{') - m1.Count(c => c == '}') == m2.Count(c => c == '{') - m2.Count(c => c == '}');
                                                    var cls2 = AccessorEditor.All(t2).FirstOrDefault(c => c.Name == cls.Name && c.Open == cls.Open);
                                                    var added = FunctionScan.Scan(t2).Count - FunctionScan.Scan(t).Count;
                                                    if (!balanced || cls2 == null || added < 1) { r.Acc_Fail++; Fail(r, "ゲッター 壊れた: " + Path.GetFileName(f) + " " + cls.Name + "::" + member + " (" + type + ") 関数 +" + added + (balanced ? "" : " 括弧がずれた")); }
                                                    else
                                                    {
                                                        r.Acc_Made++;
                                                        if (r.Samples.Count < 400 && rng.Next(60) == 0) r.Samples.Add("ゲッター " + cls.Name + "::" + member + " (" + type + ") → " + string.Join(" / ", lines.Select(x => x.Trim())));
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                                ls = i + 1;
                            }
                            else if (mask[i] == '{') depth++;
                            else if (mask[i] == '}') depth--;
                        }
                    }
                }

                // Alt+F: #include を足す
                string stem = isHeader ? null : Path.GetFileNameWithoutExtension(f);
                var tokens = new List<string> { "<vector>", "<cstdint>", "\"zz_new_header.h\"" };
                if (stem != null) tokens.Add("\"" + stem + ".h\"");
                foreach (string tok in tokens)
                {
                    r.Inc_Tried++;
                    var e = IncludeEditor.Plan(t, tok, stem, eol);
                    string path = tok.Substring(1, tok.Length - 2);
                    if (e == null)
                    {
                        if (IncludeEditor.Has(t, path)) r.Inc_Already++;
                        else { r.Inc_Fail++; Fail(r, "include 足せない(でもまだ無い): " + Path.GetFileName(f) + " " + tok); }
                        continue;
                    }
                    string t2 = Apply(t, e.Position, e.Text);
                    bool has = IncludeEditor.Has(t2, path);
                    bool again = IncludeEditor.Plan(t2, tok, stem, eol) == null;
                    // 足した位置が、最初の「コードの行」より前か(ヘッダーのガード・pragma once のあとでもよい)
                    var firstCode = Regex.Match(t, @"(?m)^(?:namespace|class|struct|enum|template|typedef|using|extern|static|inline|void|int|bool|float)\b");
                    bool early = !firstCode.Success || e.Position <= firstCode.Index;
                    if (!has || !again || !early) { r.Inc_Fail++; Fail(r, "include 壊れた: " + Path.GetFileName(f) + " " + tok + (has ? "" : " 入っていない") + (again ? "" : " 2 回目も足す") + (early ? "" : " 位置がコードの後")); }
                    else r.Inc_Added++;
                }
            }
            catch (Exception ex) { r.Exceptions++; Fail(r, "例外 " + Path.GetFileName(f) + ": " + ex.GetType().Name + " " + ex.Message); }
        }

        // ---- Alt+R: 宣言 ⇄ 定義 ----
        foreach (string hp in headers)
        {
            foreach (string cp in cpps[Path.GetFileNameWithoutExtension(hp).ToLowerInvariant()])
            {
                string h, c;
                try { h = File.ReadAllText(hp); c = File.ReadAllText(cp); } catch (Exception) { continue; }
                if (h.Length + c.Length > 300 * 1024) { r.Skipped++; continue; }
                r.Pairs++;
                string eol = c.Contains("\r\n") ? "\r\n" : "\n";
                try
                {
                    var hs = FunctionScan.Scan(h);
                    var cs = FunctionScan.Scan(c);

                    // 宣言 → 定義: cpp から定義を 1 つ消して、雛形を作らせ、読み直す
                    foreach (var d in hs.Where(s => !s.HasBody && s.InClass))
                    {
                        var dk = Keys(d, h);
                        var defs = cs.Where(s => s.HasBody && !s.InClass && SyncPlan.Counterpart(s, d, true) > 0 && SyncPlan.SameKeysAny(Keys(s, c), dk)).ToList();
                        if (defs.Count != 1) continue;
                        var D = defs[0];
                        r.D2F_Tried++;
                        int start = LineStart(c, D.PrefixStart);
                        string c2 = c.Remove(start, D.End + 1 - start);
                        string why;
                        var edit = DefinitionGen.PlanDefinition(h, d, c2, eol, out why);
                        if (edit == null) { Count(r.D2F_Refused, why); continue; }
                        string c3 = Apply(c2, edit.Position, edit.Text);
                        var before = FunctionScan.Scan(c2);
                        var after = FunctionScan.Scan(c3);
                        var made = after.Where(s => s.HasBody && !s.InClass && SyncPlan.Counterpart(s, d, true) > 0 && SyncPlan.SameKeysAny(Keys(s, c3), dk)).ToList();
                        string stub = c3.Substring(edit.Position, Math.Min(edit.Text.Length, 400)).Trim();
                        if (after.Count != before.Count + 1 || made.Count == 0)
                        { r.D2F_Fail++; Fail(r, "定義を作る 読み直せない: " + Path.GetFileName(hp) + " " + string.Join("::", d.Chain) + "::" + d.Name + " (関数 " + before.Count + "→" + after.Count + ", 合う定義 " + made.Count + ")\n        " + stub.Replace("\n", "\n        ")); }
                        else { r.D2F_Ok++; if (r.Samples.Count < 400 && rng.Next(50) == 0) r.Samples.Add("定義の雛形\n        " + stub.Replace("\n", "\n        ")); }
                    }

                    // 定義 → 宣言: ヘッダーから宣言を 1 つ消して、宣言を作らせ、読み直す
                    foreach (var D in cs.Where(s => s.HasBody && !s.InClass && s.Class != null && s.Chain.Count > s.Enclosing))
                    {
                        var Dk = Keys(D, c);
                        var decls = hs.Where(s => !s.HasBody && s.InClass && SyncPlan.Counterpart(s, D, false) > 0 && SyncPlan.SameKeysAny(Keys(s, h), Dk)).ToList();
                        if (decls.Count != 1) continue;
                        var d = decls[0];
                        r.F2D_Tried++;
                        string why;
                        string declText = DefinitionGen.DeclarationFor(c, D, out why);
                        if (declText == null) { Count(r.F2D_Refused, why); continue; }
                        int start = LineStart(h, d.PrefixStart);
                        string h2 = h.Remove(start, d.End + 1 - start);
                        var scope = Scopes.Parse(h2).FirstOrDefault(s => s.IsClass && s.Chain().SequenceEqual(d.Chain));
                        if (scope == null) { Count(r.F2D_Refused, "クラスを探せない(テンプレートなど)"); continue; }
                        var edit = DefinitionGen.PlanPublicMember(h2, scope.Open, scope.IsStruct, declText, eol);
                        if (edit == null) { r.F2D_Fail++; Fail(r, "宣言を作る 編集が作れない: " + Path.GetFileName(hp) + " " + string.Join("::", d.Chain)); continue; }
                        string h3 = Apply(h2, edit.Position, edit.Text);
                        var before = FunctionScan.Scan(h2);
                        var after = FunctionScan.Scan(h3);
                        var made = after.Where(s => !s.HasBody && s.InClass && SyncPlan.Counterpart(s, D, false) > 0 && SyncPlan.SameKeysAny(Keys(s, h3), Dk)).ToList();
                        if (after.Count != before.Count + 1 || made.Count == 0)
                        { r.F2D_Fail++; Fail(r, "宣言を作る 読み直せない: " + Path.GetFileName(hp) + " " + string.Join("::", d.Chain) + "::" + d.Name + " → " + declText + " (関数 " + before.Count + "→" + after.Count + ", 合う宣言 " + made.Count + ")"); }
                        else { r.F2D_Ok++; if (r.Samples.Count < 400 && rng.Next(50) == 0) r.Samples.Add("宣言 " + declText); }
                    }
                }
                catch (Exception ex) { r.Exceptions++; Fail(r, "例外(組) " + Path.GetFileName(hp) + ": " + ex.GetType().Name + " " + ex.Message + " " + ex.StackTrace.Split('\n').FirstOrDefault()); }
            }
        }
    }

    static string Hist(Dictionary<string, int> d) { return d.Count == 0 ? "なし" : string.Join(" / ", d.OrderByDescending(x => x.Value).Select(x => x.Key + " " + x.Value)); }

    static int Main(string[] args)
    {
        bool verbose = args.Length > 1 && args[1] == "-v";
        int bad = 0;
        foreach (string dir in Directory.GetDirectories(args[0]))
        {
            var r = new R();
            var sw = Stopwatch.StartNew();
            Run(Path.GetFileName(dir), dir, r);
            Console.WriteLine("=== " + Path.GetFileName(dir) + "  (" + sw.ElapsedMilliseconds + " ms) ===");
            Console.WriteLine("  Alt+R 宣言→定義: 試した " + r.D2F_Tried + "  読み直して一致 " + r.D2F_Ok + "  失敗 " + r.D2F_Fail + "  作らない理由: " + Hist(r.D2F_Refused));
            Console.WriteLine("  Alt+R 定義→宣言: 試した " + r.F2D_Tried + "  読み直して一致 " + r.F2D_Ok + "  失敗 " + r.F2D_Fail + "  作らない理由: " + Hist(r.F2D_Refused));
            Console.WriteLine("  Alt+Q/W 代入文:  行 " + r.As_Lines + "  正しく切り出し " + r.As_Found + "  誤り " + r.As_Wrong + "  式から型が決まった " + r.As_Typed + "  最長 " + r.As_MaxMs.ToString("F1") + " ms");
            Console.WriteLine("  Alt+E ゲッター:  メンバー " + r.Acc_Members + "  作れた " + r.Acc_Made + "  作らない(型で拒否) " + r.Acc_Refused + "  型が読めない(配列・static) " + r.Acc_NoType + "  失敗 " + r.Acc_Fail);
            Console.WriteLine("  Alt+F #include:  試した " + r.Inc_Tried + "  足せた " + r.Inc_Added + "  すでにあった " + r.Inc_Already + "  失敗 " + r.Inc_Fail);
            Console.WriteLine("  対象の組 " + r.Pairs + "(300KB 超で省略 " + r.Skipped + ")  例外 " + r.Exceptions);
            foreach (string f in r.Fails.Take(verbose ? 30 : 8)) Console.WriteLine("    ! " + f);
            if (verbose) foreach (string s in r.Samples.Take(25)) Console.WriteLine("    . " + s);
            bad += r.D2F_Fail + r.F2D_Fail + r.As_Wrong + r.Acc_Fail + r.Inc_Fail + r.Exceptions;
        }
        Console.WriteLine("不具合の合計: " + bad);
        return bad == 0 ? 0 : 1;
    }
}
