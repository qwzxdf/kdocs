using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;
using KHlsl.Vsix;

/// <summary>
/// VS の C++ エディターが、各トークンに付けた分類名(probe-cpp.log。K-HLSL の調査用コードで書き出した物)と、
/// 同じ C++ のソースを K-HLSL のレキサーに通した結果を、トークンごとに突き合わせる。
/// 使い方: classtest.exe <ソース.cpp> <probe-cpp.log>
/// </summary>
internal static class Program
{
    private static readonly Dictionary<Tk, string> Names = new Dictionary<Tk, string>
    {
        { Tk.Comment, "comment" }, { Tk.String, "string" }, { Tk.StringDelim, "cppStringDelimiterCharacter" },
        { Tk.Number, "number" }, { Tk.Preprocessor, "preprocessor keyword" }, { Tk.Keyword, "keyword" },
        { Tk.Control, "cppControlKeyword" }, { Tk.Visibility, "keyword" }, { Tk.Type, "cppType" },
        { Tk.Function, "cppFunction" }, { Tk.MemberFunc, "cppMemberFunction" }, { Tk.Semantic, "cppEnumerator" },
        { Tk.Attribute, "cppAttributeIdentifier" }, { Tk.Enumerator, "cppEnumerator" }, { Tk.Macro, "cppMacro" },
        { Tk.Operator, "operator" }, { Tk.Namespace, "cppNamespace" }, { Tk.Global, "cppGlobalVariable" },
        { Tk.Local, "cppLocalVariable" }, { Tk.Param, "cppParameter" }, { Tk.Member, "cppMemberField" },
        { Tk.Label, "cppLabel" }, { Tk.Escape, "cppStringEscapeCharacter" }, { Tk.Format, "string" },
        { Tk.Identifier, "identifier" },
    };

    private static int Main(string[] args)
    {
        string text = File.ReadAllText(args[0], Encoding.UTF8);
        var toks = KHlslLexer.Lex(text, Lexicon.Instance);
        var mine = new Dictionary<int, string>();
        foreach (var t in toks)
        {
            string name;
            if (t.Kind >= Tk.Rainbow1) name = "operator";
            else if (!Names.TryGetValue(t.Kind, out name)) continue;
            if (t.Kind == Tk.Escape || t.Kind == Tk.Format) { if (!mine.ContainsKey(t.Start)) mine[t.Start] = name; continue; }
            mine[t.Start] = name;
        }

        var rx = new Regex(@"^C  \[(\d+)\] (.*?)  =>  (.*)$");
        int total = 0, same = 0, differ = 0, missing = 0;
        var report = new List<string>();
        foreach (var line in File.ReadAllLines(args[1], Encoding.UTF8))
        {
            var m = rx.Match(line);
            if (!m.Success) continue;
            int pos = int.Parse(m.Groups[1].Value);
            string snippet = m.Groups[2].Value;
            string names = m.Groups[3].Value;
            if (snippet.Trim().Length == 0 || names.StartsWith("CppInactiveCode", StringComparison.Ordinal)) continue;
            // 先頭の分類名だけを見る(cppFoo;Semantic - identifier - (TRANSIENT) → cppFoo)
            string first = names.Split(new[] { " - " }, StringSplitOptions.None)[0].Replace(";Semantic", "");
            if (names.Contains("CppInactiveCode")) continue;
            // VS 側のトークンが複数文字の演算子(++; など)のときは、先頭だけを見る
            total++;
            string got;
            if (!mine.TryGetValue(pos, out got)) { missing++; report.Add(string.Format("  欠け   [{0}] {1}   VS={2}   K-HLSL=(なし)", pos, snippet, first)); continue; }
            if (got == first) same++;
            else { differ++; report.Add(string.Format("  違う   [{0}] {1}   VS={2}   K-HLSL={3}", pos, snippet, first, got)); }
        }
        foreach (var r in report.Take(60)) Console.WriteLine(r);
        Console.WriteLine("\nトークン {0} 件: 一致 {1}、違う {2}、欠け {3}", total, same, differ, missing);
        return differ + missing == 0 ? 0 : 1;
    }
}
