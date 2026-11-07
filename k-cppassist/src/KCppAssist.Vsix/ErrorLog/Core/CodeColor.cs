using System;
using System.Collections.Generic;
using System.Text;
using System.Text.RegularExpressions;

namespace KCppAssist.ErrorLog
{
    /// <summary>整形した C++ の型・シグネチャを、役割ごとの色の Run に分ける。</summary>
    public static class CodeColor
    {
        private static readonly HashSet<string> Keywords = new HashSet<string>
        {
            "const", "volatile", "unsigned", "signed", "int", "long", "short", "char", "wchar_t", "char8_t", "char16_t", "char32_t",
            "bool", "float", "double", "void", "auto", "static", "virtual", "noexcept", "operator", "decltype", "nullptr_t",
            "__int64", "__int32", "__int16", "__int8", "template", "typename", "constexpr", "inline", "explicit", "override", "final"
        };

        private static readonly Regex Token = new Regex(
            @"(?<id>[A-Za-z_~][A-Za-z0-9_]*)|(?<num>\d+)|(?<ws>\s+)|(?<other>.)",
            RegexOptions.Compiled | RegexOptions.Singleline);

        public static List<Run> Tokenize(string s, bool boldFunc = true)
        {
            var runs = new List<Run>();
            if (string.IsNullOrEmpty(s)) return runs;

            int depthAngle = 0;
            foreach (Match m in Token.Matches(s))
            {
                if (m.Groups["id"].Success)
                {
                    string id = m.Groups["id"].Value;
                    int next = m.Index + m.Length;
                    char nc = next < s.Length ? s[next] : '\0';
                    bool scope = nc == ':' && next + 1 < s.Length && s[next + 1] == ':';
                    int k = next;
                    while (k < s.Length && s[k] == ' ') k++;
                    bool call = k < s.Length && s[k] == '(' && depthAngle == 0;

                    Role role;
                    bool bold = false;
                    if (Keywords.Contains(id)) role = Role.Keyword;
                    else if (scope) role = Role.Scope;
                    else if (call) { role = Role.Func; bold = boldFunc; }
                    else role = Role.Type;
                    runs.Add(new Run { Text = id, Role = role, Bold = bold });
                }
                else if (m.Groups["num"].Success)
                {
                    runs.Add(new Run { Text = m.Value, Role = Role.Number });
                }
                else if (m.Groups["ws"].Success)
                {
                    runs.Add(new Run { Text = m.Value, Role = Role.Normal });
                }
                else
                {
                    char c = m.Value[0];
                    if (c == '<') depthAngle++;
                    else if (c == '>' && depthAngle > 0) depthAngle--;
                    runs.Add(new Run { Text = m.Value, Role = Role.Punct });
                }
            }
            return Merge(runs);
        }

        /// <summary>同じ書式で続く Run をまとめる(Run の数を減らして、描画を軽くする)。</summary>
        public static List<Run> Merge(List<Run> runs)
        {
            var result = new List<Run>();
            foreach (Run r in runs)
            {
                if (result.Count > 0)
                {
                    Run p = result[result.Count - 1];
                    if (p.Role == r.Role && p.Bold == r.Bold && p.Italic == r.Italic && !p.IsLink && !r.IsLink)
                    {
                        p.Text += r.Text;
                        continue;
                    }
                }
                result.Add(r);
            }
            return result;
        }
    }

    /// <summary>
    /// エラーメッセージを、読みやすい Run の並びにする。
    /// 'A' や "A" で囲まれた C++ らしい部分は、型名を短くして色を付ける。
    /// </summary>
    public static class MessageFormat
    {
        private static readonly Regex Quoted = new Regex(@"'(?<q>[^']*)'|""(?<d>[^""]*)""", RegexOptions.Compiled);
        // リンカーの「(?Resize@Engine@prest@@QEAAXHH@Z)」のような、飾られた名前
        private static readonly Regex Mangled = new Regex(@"\((?<m>\?[^\s()]+|_[A-Za-z0-9_@$?]+@\d+)\)", RegexOptions.Compiled);

        public static List<Run> Format(string msg, Role baseRole)
        {
            var runs = new List<Run>();
            if (string.IsNullOrEmpty(msg)) return runs;

            int pos = 0;
            foreach (Match m in Quoted.Matches(msg))
            {
                if (m.Index > pos) AddPlain(runs, msg.Substring(pos, m.Index - pos), baseRole);
                string inner = m.Groups["q"].Success ? m.Groups["q"].Value : m.Groups["d"].Value;
                char qc = m.Groups["q"].Success ? '\'' : '"';
                if (LooksLikeCode(inner))
                {
                    runs.Add(new Run { Text = qc.ToString(), Role = Role.Dim });
                    runs.AddRange(CodeColor.Tokenize(PrettyAny(inner), false));
                    runs.Add(new Run { Text = qc.ToString(), Role = Role.Dim });
                }
                else
                {
                    AddPlain(runs, m.Value, baseRole);
                }
                pos = m.Index + m.Length;
            }
            if (pos < msg.Length) AddPlain(runs, msg.Substring(pos), baseRole);
            return CodeColor.Merge(runs);
        }

        private static void AddPlain(List<Run> runs, string text, Role role)
        {
            int pos = 0;
            foreach (Match m in Mangled.Matches(text))
            {
                if (m.Index > pos) runs.Add(new Run { Text = text.Substring(pos, m.Index - pos), Role = role });
                runs.Add(new Run { Text = m.Value, Role = Role.Dim });
                pos = m.Index + m.Length;
            }
            if (pos < text.Length) runs.Add(new Run { Text = text.Substring(pos), Role = role });
        }

        /// <summary>引用符の中身が、識別子・型・関数らしいか(英文の断片でないか)。</summary>
        public static bool LooksLikeCode(string s)
        {
            if (string.IsNullOrWhiteSpace(s)) return false;
            if (s.Contains("::") || s.Contains("<") || s.Contains("(") || s.Contains("__") || s.Contains("`")) return true;
            // 空白のない 1 語(識別子)
            if (s.IndexOf(' ') < 0 && Regex.IsMatch(s, @"^[A-Za-z_~][\w\.\*&\[\]]*$")) return true;
            // "const char *" のような、型だけの並び
            return Regex.IsMatch(s, @"^(?:const |unsigned |signed |struct |class |enum )*[A-Za-z_][\w:]*(?: ?[\*&]+)*(?: const)?$");
        }

        /// <summary>型または関数宣言として、読みやすい形にする。</summary>
        public static string PrettyAny(string s)
        {
            s = s.Trim();
            if (s.EndsWith(")", StringComparison.Ordinal) || s.Contains(") const"))
            {
                SymInfo info = SymbolPretty.Parse(s, "");
                if (info.IsFunction) return info.Pretty;
            }
            return TypePretty.Type(s);
        }
    }
}
