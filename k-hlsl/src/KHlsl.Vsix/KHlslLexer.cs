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
        Comment, String, Number, Preprocessor, Keyword, Control, Type, Function, Semantic, Attribute, Constant, Macro
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
            @"\b(?:struct|class|interface|enum(?:\s+class)?)\s+([A-Za-z_]\w*)|\btypedef\b[^;{}]*?\b([A-Za-z_]\w*)\s*;",
            RegexOptions.Compiled);
        private static readonly Regex RxDefines = new Regex(@"^[ \t]*#[ \t]*define[ \t]+([A-Za-z_]\w*)", RegexOptions.Compiled | RegexOptions.Multiline);
        private static readonly HashSet<string> TypeIntroducers = new HashSet<string> { "struct", "class", "interface", "enum", "namespace", "cbuffer", "tbuffer" };

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
            char prevCh = '\0';       // 直前の記号(空白・識別子を除く)ではなく、直前の「意味のある」文字
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
                            while (e < n && text[e] != close && text[e] != '\n') e++;
                            if (e < n && text[e] == close) e++;
                            add(p, e - p, Tk.String);
                            i = e;
                        }
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
                    prevCh = '\0'; prevWord = null;
                    continue;
                }
                lineStart = false;

                if (c == '"' || c == '\'')
                {
                    int e = i + 1;
                    while (e < n && text[e] != c && text[e] != '\n')
                    {
                        if (text[e] == '\\' && e + 1 < n) e++;
                        e++;
                    }
                    if (e < n && text[e] == c) e++;
                    add(i, e - i, Tk.String);
                    i = e; prevCh = c; prevWord = null; continue;
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
                    i = e; prevCh = '0'; prevWord = null; continue;
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

                    Tk? kind = Classify(q, w, prevCh, prevWord, nextCh, call, lx, userTypes, userMacros);
                    if (kind.HasValue) add(i, e - i, kind.Value);
                    prevCh = 'a'; prevWord = q; prevEnd = e;
                    i = e; continue;
                }

                prevCh = c; prevWord = null;
                i++;
            }
            return toks;
        }

        private static Tk? Classify(string q, string w, char prevCh, string prevWord, char nextCh, bool call,
            Lexicon lx, HashSet<string> userTypes, HashSet<string> userMacros)
        {
            if (q.StartsWith("dx::", StringComparison.Ordinal))
            {
                if (q == "dx::HitObject") return Tk.Type;
                return Tk.Function;
            }
            if (prevCh == '[' && (lx.Attributes.Contains(w) || q.StartsWith("vk::", StringComparison.Ordinal)))
                return Tk.Attribute;
            if (prevCh == ':')
            {
                if (w == "register" || w == "packoffset") return Tk.Keyword;
                if ((w == "read" || w == "write") && nextCh == '(') return Tk.Keyword;
                string sem = Regex.Replace(w, @"\d+$", "");
                if (lx.Semantics.Contains(sem) || lx.Semantics.Contains(w) || w.StartsWith("SV_", StringComparison.OrdinalIgnoreCase))
                    return Tk.Semantic;
            }
            if (lx.Control.Contains(w)) return Tk.Control;
            if (lx.Keywords.Contains(w)) return Tk.Keyword;
            if (lx.ScalarTypes.Contains(w) || RxVecMat.IsMatch(w)) return Tk.Keyword;
            if (prevWord != null && TypeIntroducers.Contains(prevWord)) return Tk.Type;
            if (lx.ResourceTypes.Contains(w) || lx.Special.Contains(w)) return Tk.Type;
            if (userTypes.Contains(w)) return Tk.Type;
            if (lx.Constants.Contains(w)) return Tk.Constant;
            if (lx.Macros.Contains(w) || userMacros.Contains(w)) return Tk.Macro;
            if (call && prevCh == '.' && lx.Methods.Contains(w)) return Tk.Function;
            if (call) return Tk.Function;
            return null;
        }
    }
}
