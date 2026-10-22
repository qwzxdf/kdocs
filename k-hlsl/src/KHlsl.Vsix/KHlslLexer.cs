using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;
using Newtonsoft.Json.Linq;

namespace KHlsl.Vsix
{
    internal enum Tk
    {
        Comment, String, StringDelim, Number, Preprocessor, Keyword, Control, Visibility, Type, Function, MemberFunc,
        Semantic, Attribute, Enumerator, Macro, Operator, Namespace, Global, Local, Param, Member, Label, Identifier,
        Escape, Format,
        Rainbow1, Rainbow2, Rainbow3, Rainbow4, Rainbow5, Rainbow6, Rainbow7, Rainbow8, Rainbow9, RainbowError
    }

    internal struct Tok
    {
        public int Start, Length;
        public Tk Kind;
    }

    /// <summary>言語データ(hlsl.json)から作る、色付け用の語彙。</summary>
    internal sealed class Lexicon
    {
        public HashSet<string> Control = new HashSet<string>();
        public HashSet<string> Keywords = new HashSet<string>();
        public HashSet<string> ScalarTypes = new HashSet<string>();
        public HashSet<string> ResourceTypes = new HashSet<string>();
        public HashSet<string> Intrinsics = new HashSet<string>();
        public HashSet<string> Methods = new HashSet<string>();
        public HashSet<string> Semantics = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
        public HashSet<string> Attributes = new HashSet<string>();
        public HashSet<string> Constants = new HashSet<string>();
        public HashSet<string> Macros = new HashSet<string>();
        public HashSet<string> Special = new HashSet<string>();

        private static Lexicon _instance;
        private static readonly object Gate = new object();

        public static Lexicon Instance
        {
            get
            {
                lock (Gate)
                {
                    if (_instance == null) _instance = Load();
                    return _instance;
                }
            }
        }

        private static Lexicon Load()
        {
            var lx = new Lexicon();
            try
            {
                using (var s = typeof(Lexicon).Assembly.GetManifestResourceStream("hlsl.json"))
                using (var r = new StreamReader(s, System.Text.Encoding.UTF8))
                {
                    var o = JObject.Parse(r.ReadToEnd());
                    foreach (var k in (JArray)o["keywords"])
                    {
                        string n = (string)k["n"];
                        if ((string)k["k"] == "control") lx.Control.Add(n); else lx.Keywords.Add(n);
                    }
                    foreach (var t in (JArray)o["types"])
                    {
                        string n = (string)t["n"];
                        if (t["scalar"] != null && (bool)t["scalar"]) lx.ScalarTypes.Add(n); else lx.ResourceTypes.Add(n);
                    }
                    foreach (var f in (JArray)o["intrinsics"]) lx.Intrinsics.Add((string)f["n"]);
                    foreach (var g in (JObject)o["methods"])
                        foreach (var m in (JArray)g.Value) lx.Methods.Add((string)m["n"]);
                    foreach (var s2 in (JArray)o["semantics"]) lx.Semantics.Add((string)s2["n"]);
                    foreach (var a in (JArray)o["attributes"]) lx.Attributes.Add((string)a["n"]);
                    foreach (var c in (JArray)o["constants"]) lx.Constants.Add((string)c["n"]);
                    foreach (var m in (JArray)o["macros"]) lx.Macros.Add((string)m["n"]);
                    foreach (var sp in (JArray)o["special"]) lx.Special.Add((string)sp["n"]);
                }
            }
            catch (Exception) { }
            lx.Constants.Remove("true");
            lx.Constants.Remove("false");
            lx.Keywords.Add("true");
            lx.Keywords.Add("false");
            return lx;
        }
    }

    /// <summary>1 ファイルまるごとを字句に分ける。ブロック コメントが行をまたぐので、全体を一度に処理する。</summary>
    internal static class KHlslLexer
    {
        private static readonly Regex RxVecMat = new Regex(
            @"^(?:bool|int|uint|dword|half|float|double|min16float|min10float|min16int|min12int|min16uint|int16_t|uint16_t|float16_t|int32_t|uint32_t|float32_t|int64_t|uint64_t|float64_t)(?:[1-4](?:x[1-4])?)?$",
            RegexOptions.Compiled);
        private static readonly Regex RxUserTypes = new Regex(
            @"\b(?:struct|class|interface|enum(?:\s+class)?)\s+(?:\[[^\]]*\]\s*)*([A-Za-z_]\w*)|\btypedef\b[^;{}]*?\b([A-Za-z_]\w*)\s*;",
            RegexOptions.Compiled);
        private static readonly Regex RxDefines = new Regex(@"^[ \t]*#[ \t]*define[ \t]+([A-Za-z_]\w*)", RegexOptions.Compiled | RegexOptions.Multiline);
        private static readonly HashSet<string> TypeIntroducers = new HashSet<string> { "struct", "class", "interface", "enum", "namespace", "cbuffer", "tbuffer" };

        internal static bool IsVecMat(string w) { return RxVecMat.IsMatch(w); }

        private static bool IsIdStart(char c) { return char.IsLetter(c) || c == '_'; }
        private static bool IsId(char c) { return char.IsLetterOrDigit(c) || c == '_'; }

        public static List<Tok> Lex(string text, Lexicon lx)
        {
            var toks = new List<Tok>(text.Length / 4);
            var userTypes = new HashSet<string>();
            foreach (Match m in RxUserTypes.Matches(text))
            {
                var g = m.Groups[1].Success ? m.Groups[1] : m.Groups[2];
                userTypes.Add(g.Value);
            }
            var userMacros = new HashSet<string>();
            foreach (Match m in RxDefines.Matches(text)) userMacros.Add(m.Groups[1].Value);

            int n = text.Length, i = 0;
            bool lineStart = true;
            char prevCh = '\0', prev2Ch = '\0';       // 直前の記号(空白・識別子を除く)ではなく、直前の「意味のある」文字
            string prevWord = null;
            int prevEnd = 0;

            Action<int, int, Tk> add = (s, len, k) => toks.Add(new Tok { Start = s, Length = len, Kind = k });

            while (i < n)
            {
                char c = text[i];
                if (c == '\n') { lineStart = true; i++; continue; }
                if (char.IsWhiteSpace(c)) { i++; continue; }

                if (c == '/' && i + 1 < n && text[i + 1] == '/')
                {
                    int e = text.IndexOf('\n', i);
                    if (e < 0) e = n;
                    add(i, e - i, Tk.Comment);
                    i = e; continue;
                }
                if (c == '/' && i + 1 < n && text[i + 1] == '*')
                {
                    int e = text.IndexOf("*/", i + 2, StringComparison.Ordinal);
                    e = e < 0 ? n : e + 2;
                    add(i, e - i, Tk.Comment);
                    lineStart = false;
                    i = e; continue;
                }
                if (c == '#' && lineStart)
                {
                    int j = i + 1;
                    while (j < n && (text[j] == ' ' || text[j] == '\t')) j++;
                    int k = j;
                    while (k < n && char.IsLetter(text[k])) k++;
                    add(i, k - i, Tk.Preprocessor);
                    string word = text.Substring(j, k - j);
                    i = k;
                    if (word == "include")
                    {
                        int p = i;
                        while (p < n && (text[p] == ' ' || text[p] == '\t')) p++;
                        if (p < n && (text[p] == '"' || text[p] == '<'))
                        {
                            char close = text[p] == '"' ? '"' : '>';
                            int e = p + 1;
                            while (e < n && text[e] != close && text[e] != '\n' && text[e] != '\r') e++;
                            bool closed = e < n && text[e] == close;
                            if (closed) e++;
                            if (text[p] == '"') AddString(toks, text, p, e);
                            else
                            {
                                // <file> は、VS の C++ と同じく、< > を区切り文字、中を文字列にする
                                add(p, 1, Tk.StringDelim);
                                int inner = (closed ? e - 1 : e) - (p + 1);
                                if (inner > 0) add(p + 1, inner, Tk.String);
                                if (closed) add(e - 1, 1, Tk.StringDelim);
                            }
                            i = e;
                        }
                    }
                    else if (word == "pragma")
                    {
                        // #pragma once の once なども、プリプロセッサのキーワードの色にする
                        int p = i;
                        while (p < n && (text[p] == ' ' || text[p] == '\t')) p++;
                        int e = p;
                        while (e < n && IsId(text[e])) e++;
                        if (e > p) add(p, e - p, Tk.Preprocessor);
                        i = e;
                    }
                    else if (word == "define" || word == "undef")
                    {
                        int p = i;
                        while (p < n && (text[p] == ' ' || text[p] == '\t')) p++;
                        int e = p;
                        while (e < n && IsId(text[e])) e++;
                        if (e > p) add(p, e - p, Tk.Macro);
                        i = e;
                    }
                    lineStart = false;
                    prev2Ch = prevCh; prevCh = '\0'; prevWord = null;
                    continue;
                }
                lineStart = false;

                if (c == '"' || c == '\'')
                {
                    int e = i + 1;
                    while (e < n && text[e] != c && text[e] != '\n' && text[e] != '\r')
                    {
                        // 行末の \ は、次の行へ続かない(Viasfora は 1 行ずつ処理する)
                        if (text[e] == '\\' && e + 1 < n && text[e + 1] != '\n' && text[e + 1] != '\r') e++;
                        e++;
                    }
                    if (e < n && text[e] == c) e++;
                    AddString(toks, text, i, e);
                    i = e; prev2Ch = prevCh; prevCh = c; prevWord = null; continue;
                }

                if (char.IsDigit(c) || (c == '.' && i + 1 < n && char.IsDigit(text[i + 1])))
                {
                    int e = i;
                    if (c == '0' && i + 1 < n && (text[i + 1] == 'x' || text[i + 1] == 'X'))
                    {
                        e = i + 2;
                        while (e < n && Uri.IsHexDigit(text[e])) e++;
                    }
                    else
                    {
                        while (e < n && char.IsDigit(text[e])) e++;
                        if (e < n && text[e] == '.') { e++; while (e < n && char.IsDigit(text[e])) e++; }
                        if (e < n && (text[e] == 'e' || text[e] == 'E'))
                        {
                            int p = e + 1;
                            if (p < n && (text[p] == '+' || text[p] == '-')) p++;
                            if (p < n && char.IsDigit(text[p])) { e = p; while (e < n && char.IsDigit(text[e])) e++; }
                        }
                    }
                    while (e < n && (text[e] == 'f' || text[e] == 'F' || text[e] == 'h' || text[e] == 'H' || text[e] == 'u' || text[e] == 'U' || text[e] == 'l' || text[e] == 'L')) e++;
                    add(i, e - i, Tk.Number);
                    i = e; prev2Ch = prevCh; prevCh = '0'; prevWord = null; continue;
                }

                if (IsIdStart(c))
                {
                    int e = i;
                    while (e < n && IsId(text[e])) e++;
                    // 名前空間つき(dx::HitObject, vk::binding)
                    while (e + 2 < n && text[e] == ':' && text[e + 1] == ':' && IsIdStart(text[e + 2]))
                    {
                        e += 2;
                        while (e < n && IsId(text[e])) e++;
                    }
                    string q = text.Substring(i, e - i);
                    string w = q.Contains("::") ? q.Substring(q.LastIndexOf("::", StringComparison.Ordinal) + 2) : q;
                    int p = e;
                    while (p < n && (text[p] == ' ' || text[p] == '\t')) p++;
                    char nextCh = p < n ? text[p] : '\0';
                    bool call = nextCh == '(' || (nextCh == '<' && lx.Intrinsics.Contains(w));

                    int tokStart = i;
                    string classifyAs = q;
                    if (q.Contains("::") && !q.StartsWith("dx::", StringComparison.Ordinal) && !q.StartsWith("vk::", StringComparison.Ordinal))
                    {
                        // ns::name は、ns を名前空間、:: を演算子、最後の名前を普通に分類する(VS の C++ と同じ)
                        int segStart = i;
                        int idx;
                        string rest = q;
                        while ((idx = rest.IndexOf("::", StringComparison.Ordinal)) >= 0)
                        {
                            add(segStart, idx, Tk.Namespace);
                            add(segStart + idx, 1, Tk.Operator);
                            add(segStart + idx + 1, 1, Tk.Operator);
                            segStart += idx + 2;
                            rest = rest.Substring(idx + 2);
                        }
                        tokStart = segStart;
                        classifyAs = w;
                    }

                    Tk? kind = Classify(classifyAs, w, q == classifyAs ? prevCh : 'a', prev2Ch, prevWord, nextCh, call, lx, userTypes, userMacros);
                    // どれにも当たらない識別子は、VS の C++ と同じく identifier にする(あとの意味解析で付け替える)
                    add(tokStart, e - tokStart, kind ?? Tk.Identifier);
                    prev2Ch = prevCh; prevCh = 'a'; prevWord = q; prevEnd = e;
                    i = e; continue;
                }

                // 演算子・区切り(VS の C++ では、. :: -> ? : ; , もすべて operator)。括弧は、レインボー括弧が担当する
                if ("+-*/%&|^~!<>=?:;,.@".IndexOf(c) >= 0) add(i, 1, Tk.Operator);
                prev2Ch = prevCh; prevCh = c; prevWord = null;
                i++;
            }
            AddRainbowBraces(toks, text);
            KHlslSemantic.Run(text, toks, lx, userTypes);
            return toks;
        }

        /// <summary>Viasfora の既定の深さ(RainbowDepth)。この数の色を循環させる。</summary>
        public const int RainbowDepth = 4;

        /// <summary>
        /// レインボー括弧。Viasfora の既定(Unified)と同じく、( ) [ ] { } を 1 つのスタックで数える。
        /// 括弧の拾い方は Viasfora の CBraceScanner と同じ(コメント・文字列・文字リテラルの中は数えない)。
        /// 閉じ括弧が、直前の開き括弧と対応しないとき、またはスタックが空のときは RainbowError にして、スタックは変えない。
        /// </summary>
        private static void AddRainbowBraces(List<Tok> toks, string text)
        {
            var added = new List<Tok>();
            var stack = new Stack<char>();
            int n = text.Length;
            int i = 0;
            bool inComment = false;
            Func<int, char> at = k => k < n ? text[k] : '\0';
            while (i < n)
            {
                if (inComment)
                {
                    int e = text.IndexOf("*/", i, StringComparison.Ordinal);
                    if (e < 0) break;
                    i = e + 2;
                    inComment = false;
                    continue;
                }
                char c = text[i];
                if (c == '/' && at(i + 1) == '*') { inComment = true; i += 2; continue; }
                if (c == '/' && at(i + 1) == '/')
                {
                    int e = text.IndexOf('\n', i);
                    i = e < 0 ? n : e;
                    continue;
                }
                if (c == '"') { i = SkipLiteral(text, i + 1, '"'); continue; }
                if (c == 'u' && at(i + 1) == '8' && at(i + 2) == '\'') { i = SkipLiteral(text, i + 3, '\''); continue; }
                if (c == 'u' && at(i + 1) == '8' && at(i + 2) == '"') { i = SkipLiteral(text, i + 3, '"'); continue; }
                if (Uri.IsHexDigit(c) && at(i + 1) == '\'') { i += 2; continue; }
                if (c == '\'') { i = SkipLiteral(text, i + 1, '\''); continue; }
                if (c == '(' || c == '[' || c == '{')
                {
                    int depth = stack.Count;
                    added.Add(new Tok { Start = i, Length = 1, Kind = (Tk)((int)Tk.Rainbow1 + depth % RainbowDepth) });
                    stack.Push(c);
                }
                else if (c == ')' || c == ']' || c == '}')
                {
                    char open = c == ')' ? '(' : c == ']' ? '[' : '{';
                    if (stack.Count > 0 && stack.Peek() == open)
                    {
                        stack.Pop();
                        added.Add(new Tok { Start = i, Length = 1, Kind = (Tk)((int)Tk.Rainbow1 + stack.Count % RainbowDepth) });
                    }
                    else
                    {
                        added.Add(new Tok { Start = i, Length = 1, Kind = Tk.RainbowError });
                    }
                }
                i++;
            }
            if (added.Count == 0) return;
            toks.AddRange(added);
            toks.Sort((x, y) => x.Start.CompareTo(y.Start));
        }

        /// <summary>文字列・文字リテラルの終わりまで読み飛ばす。Viasfora と同じく、行末で終わる。</summary>
        private static int SkipLiteral(string text, int start, char quote)
        {
            int n = text.Length;
            int j = start;
            while (j < n && text[j] != '\n' && text[j] != '\r')
            {
                if (text[j] == '\\')
                {
                    if (j + 1 >= n || text[j + 1] == '\n' || text[j + 1] == '\r') return j + 1;
                    j += 2;
                    continue;
                }
                if (text[j] == quote) return j + 1;
                j++;
            }
            return j;
        }


        /// <summary>
        /// 文字列を、通常の部分・エスケープ・書式指定子に分ける(Viasfora の CStringScanner と同じ規則)。
        /// エスケープは バックスラッシュの次の 1 文字と、x X u(4 桁まで) U(8 桁まで) に続く 16 進数字。
        /// 書式指定子は % に続く英数字(% だけは対象外、%% は読み飛ばす)。
        /// </summary>
        private static void AddString(List<Tok> toks, string text, int start, int end)
        {
            int plain = start;
            int i = start + 1;
            // CStringScanner は、先頭の 1 文字(引用符)を飛ばし、最後の 1 文字を範囲から外す
            int stop = end > start + 1 ? end - 1 : end;
            Action<int, int, Tk> add = (s2, len, k) => { if (len > 0) toks.Add(new Tok { Start = s2, Length = len, Kind = k }); };
            // VS の C++ と同じく、引用符は区切り文字、中身は文字列の色にする
            add(start, 1, Tk.StringDelim);
            plain = start + 1;
            bool closedLiteral = end > start + 1 && text[end - 1] == text[start];
            int contentEnd = closedLiteral ? end - 1 : end;
            while (i < stop)
            {
                char ch = text[i];
                if (ch == '\\')
                {
                    add(plain, i - plain, Tk.String);
                    int p = i + 1;
                    char kind = p < stop ? text[p] : '\0';
                    // Viasfora は、次の 1 文字が範囲(最後の 1 文字を除く)の外でも、エスケープの長さに含める
                    p++;
                    if (kind == 'x' || kind == 'X' || kind == 'u' || kind == 'U')
                    {
                        int max = kind == 'u' ? 4 : kind == 'U' ? 8 : int.MaxValue;
                        int count = 0;
                        while (p < stop && Uri.IsHexDigit(text[p]) && count < max) { p++; count++; }
                    }
                    add(i, p - i, Tk.Escape);
                    plain = i = p;
                    continue;
                }
                if (ch == '%')
                {
                    if (i + 1 < stop && text[i + 1] == '%') { i += 2; continue; }
                    int p = i + 1;
                    while (p < stop && text[p] != '\\' && ((text[p] >= 'A' && text[p] <= 'Z') || (text[p] >= 'a' && text[p] <= 'z') || (text[p] >= '0' && text[p] <= '9'))) p++;
                    if (p - i >= 2)
                    {
                        add(plain, i - plain, Tk.String);
                        add(i, p - i, Tk.Format);
                        plain = i = p;
                        continue;
                    }
                    // 書式指定子にならなかったとき、Viasfora は % の次の 1 文字も読み飛ばす
                    i = Math.Min(stop, p + 1);
                    continue;
                }
                i++;
            }
            add(plain, contentEnd - plain, Tk.String);
            if (closedLiteral) add(end - 1, 1, Tk.StringDelim);
        }

        // ペイロードのアクセス修飾子(DXR 1.2)で使うステージ名
        private static readonly HashSet<string> PayloadStages = new HashSet<string> { "anyhit", "closesthit", "miss", "caller" };

        // VS の C++ で cppControlKeyword になる語
        private static readonly HashSet<string> ControlWords = new HashSet<string>
        {
            "if", "else", "for", "while", "do", "switch", "case", "default", "break", "continue", "return", "goto",
            "discard", "throw", "try", "catch"
        };

        // Viasfora の C++ の既定の可視性キーワード(keyword の分類のものだけに効く)
        private static readonly HashSet<string> VisibilityWords = new HashSet<string> { "public", "private", "protected", "internal", "friend" };

        private static Tk? Classify(string q, string w, char prevCh, char prev2Ch, string prevWord, char nextCh, bool call,
            Lexicon lx, HashSet<string> userTypes, HashSet<string> userMacros)
        {
            if (q == "defined") return Tk.Preprocessor;
            if (q.StartsWith("dx::", StringComparison.Ordinal))
            {
                if (q == "dx::HitObject") return Tk.Type;
                return Tk.Function;
            }
            if (prevCh == '[' && (lx.Attributes.Contains(w) || q.StartsWith("vk::", StringComparison.Ordinal) || prev2Ch == '['))
                return Tk.Attribute;
            if ((prevCh == '(' || prevCh == ',') && (nextCh == ',' || nextCh == ')') && PayloadStages.Contains(w))
                return Tk.Enumerator;
            if (prevCh == ':')
            {
                if (w == "register" || w == "packoffset") return Tk.Keyword;
                if ((w == "read" || w == "write") && nextCh == '(') return Tk.Keyword;
                string sem = Regex.Replace(w, @"\d+$", "");
                if (lx.Semantics.Contains(sem) || lx.Semantics.Contains(w) || w.StartsWith("SV_", StringComparison.OrdinalIgnoreCase))
                    return Tk.Semantic;
            }
            // VS の C++ は、制御キーワード(goto throw try catch も含む)を、keyword とは別の分類にする
            if (ControlWords.Contains(w)) return Tk.Control;
            bool isKeyword = lx.Control.Contains(w) || lx.Keywords.Contains(w);
            // Viasfora の可視性キーワードは、keyword の分類のものだけが対象
            if (isKeyword && VisibilityWords.Contains(w)) return Tk.Visibility;
            if (isKeyword) return Tk.Keyword;
            if (lx.ScalarTypes.Contains(w) || RxVecMat.IsMatch(w)) return Tk.Keyword;
            if (prevWord == "namespace") return Tk.Namespace;
            if (prevWord == "goto") return Tk.Label;
            if (prevWord != null && TypeIntroducers.Contains(prevWord)) return Tk.Type;
            if (lx.ResourceTypes.Contains(w)) return Tk.Type;
            if (lx.Special.Contains(w)) return Tk.Global;
            if (userTypes.Contains(w)) return Tk.Type;
            if (lx.Constants.Contains(w)) return Tk.Enumerator;
            if (lx.Macros.Contains(w) || userMacros.Contains(w)) return Tk.Macro;
            if (call && prevCh == '.') return Tk.MemberFunc;
            if (call) return Tk.Function;
            return null;
        }
    }
}
