using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;

namespace KCppAssist.ErrorLog
{
    public enum SymKind
    {
        Unknown, Function, TemplateFunction, Method, StaticMethod, Ctor, Dtor, Operator,
        Variable, StaticVariable, VTable, Lambda, Special, CSymbol
    }

    /// <summary>
    /// リンカーが出す「__declspec(dllimport) public: __cdecl prest::Engine::Engine(struct prest::EngineDesc const &amp;)」を
    /// 分解して、読みやすい形(Pretty)と、クラス名・名前空間・種類に分けたもの。
    /// </summary>
    public sealed class SymInfo
    {
        public string Raw = "";
        public string Mangled = "";
        public string Pretty = "";
        public SymKind Kind = SymKind.Unknown;
        public bool Import;
        public string Access = "";
        public bool IsStatic;
        public bool IsVirtual;
        public string Return = "";
        public string Qualified = "";
        public string Name = "";
        public string Scope = "";
        public string Class = "";
        public string Namespace = "";
        public List<string> Params;
        public string Qualifiers = "";
        public string Note = "";
        /// <summary>ラムダのとき、その番号。外側の関数は Outer。</summary>
        public string LambdaId = "";
        public SymInfo Outer;

        public bool IsFunction { get { return Params != null; } }
        public bool IsMember { get { return Access.Length > 0; } }

        public string KindLabel
        {
            get
            {
                switch (Kind)
                {
                    case SymKind.Ctor: return "コンストラクター";
                    case SymKind.Dtor: return "デストラクター";
                    case SymKind.Method: return "メンバー関数";
                    case SymKind.StaticMethod: return "static メンバー関数";
                    case SymKind.Operator: return "演算子";
                    case SymKind.Function: return "関数";
                    case SymKind.TemplateFunction: return "関数テンプレート";
                    case SymKind.Variable: return "変数";
                    case SymKind.StaticVariable: return "static メンバー変数";
                    case SymKind.VTable: return "vtable";
                    case SymKind.Lambda: return "ラムダ";
                    case SymKind.Special: return "自動生成";
                    case SymKind.CSymbol: return "C の名前";
                }
                return "";
            }
        }
    }

    public static class SymbolPretty
    {
        private static readonly Regex Access = new Regex(@"^(public|private|protected):\s*", RegexOptions.Compiled);
        private static readonly Regex ParamTail = new Regex(@"^(?<h>.*\))(?<q>(?:\s*(?:const|volatile|noexcept|&&|&))*)\s*$", RegexOptions.Compiled | RegexOptions.Singleline);
        private static readonly Regex OperatorWord = new Regex(@"\boperator\b", RegexOptions.Compiled);
        private static readonly Regex LambdaId = new Regex(@"<lambda_(\w+)>", RegexOptions.Compiled);
        private static readonly Regex TemplateArgs = new Regex(@"<.*$", RegexOptions.Compiled | RegexOptions.Singleline);

        public static SymInfo Parse(string demangled, string mangled)
        {
            var info = new SymInfo { Raw = demangled ?? "", Mangled = mangled ?? "" };
            try { ParseCore(info); }
            catch (Exception)
            {
                info.Kind = SymKind.Unknown;
                info.Pretty = TypePretty.Type(info.Raw);
            }
            if (info.Pretty.Length == 0) info.Pretty = info.Raw;
            if (info.Mangled.StartsWith("__imp_", StringComparison.Ordinal)) info.Import = true;
            return info;
        }

        private static void ParseCore(SymInfo info)
        {
            string s = info.Raw.Trim();
            if (s.Length == 0) return;

            // 引用符も括弧もない名前は、C のシンボル(main、WinMain、pe_set_log_callback など)
            if (s.IndexOf(' ') < 0 && s.IndexOf('(') < 0 && s.IndexOf("::", StringComparison.Ordinal) < 0 && s.IndexOf('<') < 0)
            {
                info.Kind = SymKind.CSymbol;
                info.Name = s;
                info.Qualified = s;
                info.Pretty = s;
                return;
            }

            if (s.IndexOf("<lambda_", StringComparison.Ordinal) >= 0)
            {
                ParseLambda(info, s);
                return;
            }

            // 先頭の印を外す
            string t = s;
            while (true)
            {
                if (t.StartsWith("__declspec(dllimport)", StringComparison.Ordinal)) { info.Import = true; t = t.Substring(21).TrimStart(); continue; }
                if (t.StartsWith("__declspec(dllexport)", StringComparison.Ordinal)) { t = t.Substring(21).TrimStart(); continue; }
                Match am = Access.Match(t);
                if (am.Success) { info.Access = am.Groups[1].Value; t = t.Substring(am.Length); continue; }
                if (t.StartsWith("static ", StringComparison.Ordinal)) { info.IsStatic = true; t = t.Substring(7).TrimStart(); continue; }
                if (t.StartsWith("virtual ", StringComparison.Ordinal)) { info.IsVirtual = true; t = t.Substring(8).TrimStart(); continue; }
                break;
            }
            t = TypePretty.Clean(t).Trim();

            // 引数リスト(最後の括弧)と、そのあとの const など
            string head = t;
            string paramText = null;
            string qualifiers = "";
            Match pm = ParamTail.Match(t);
            if (pm.Success)
            {
                string h = pm.Groups["h"].Value;
                int close = h.Length - 1;
                int open = MatchOpenParen(h, close);
                if (open >= 0)
                {
                    head = h.Substring(0, open).TrimEnd();
                    paramText = h.Substring(open + 1, close - open - 1);
                    qualifiers = pm.Groups["q"].Value.Trim();
                }
            }

            // 戻り値の型と、修飾名(ns::Class::Name)を分ける
            int from = head.Length;
            Match op = null;
            foreach (Match m in OperatorWord.Matches(head)) op = m;
            if (op != null) from = op.Index;
            int qs = FindQualStart(head, from);
            string ret = head.Substring(0, qs).Trim();
            string qual = head.Substring(qs).Trim();
            if (qual.Length == 0)
            {
                info.Pretty = TypePretty.Type(t);
                return;
            }

            qual = TypePretty.Simplify(qual);
            List<string> comps = SplitScope(qual);
            string name = comps[comps.Count - 1];
            comps.RemoveAt(comps.Count - 1);

            info.Return = TypePretty.Type(ret);
            info.Name = name;
            info.Qualifiers = qualifiers;
            if (paramText != null)
            {
                info.Params = new List<string>();
                foreach (string p in TypePretty.SplitTop(paramText))
                {
                    string pp = TypePretty.Type(p);
                    if (pp.Length == 0) continue;
                    info.Params.Add(pp);
                }
                if (info.Params.Count == 1 && info.Params[0] == "void") info.Params.Clear();
            }

            string nameBase = TemplateArgs.Replace(name, "");
            if (info.IsMember && comps.Count > 0)
            {
                info.Class = comps[comps.Count - 1];
                var ns = comps.Take(comps.Count - 1).ToList();
                info.Namespace = string.Join("::", ns);
            }
            else
            {
                info.Namespace = string.Join("::", comps);
            }
            info.Scope = string.Join("::", comps);

            // `scalar deleting destructor' などの、コンパイラが作る名前
            string classBase = TemplateArgs.Replace(info.Class, "");
            if (nameBase.StartsWith("`scalar deleting destructor'", StringComparison.Ordinal)
                || nameBase.StartsWith("`vector deleting destructor'", StringComparison.Ordinal))
            {
                info.Kind = SymKind.Dtor;
                info.Name = name = "~" + classBase;
                nameBase = name;
                info.Note = "delete 式から呼ばれる、コンパイラが作るデストラクターのラッパー";
                info.Return = "";
            }
            else if (nameBase == "`vftable'" || nameBase == "`vbtable'")
            {
                info.Kind = SymKind.VTable;
                info.Note = nameBase == "`vftable'" ? "仮想関数の表 (vtable)" : "仮想基底クラスの表 (vbtable)";
                info.Pretty = info.Scope.Length > 0 ? info.Scope : name;
                info.Qualified = info.Pretty;
                return;
            }
            else if (nameBase.StartsWith("`dynamic initializer for", StringComparison.Ordinal))
            {
                info.Kind = SymKind.Special;
                info.Note = "グローバル変数の初期化処理(コンパイラが作る)";
            }
            else if (info.Params == null)
            {
                info.Kind = info.IsMember && info.IsStatic ? SymKind.StaticVariable : SymKind.Variable;
            }
            else if (info.IsMember && classBase.Length > 0 && nameBase == classBase)
            {
                info.Kind = SymKind.Ctor;
                info.Return = "";
            }
            else if (nameBase.StartsWith("~", StringComparison.Ordinal))
            {
                info.Kind = SymKind.Dtor;
                info.Return = "";
            }
            else if (nameBase.StartsWith("operator", StringComparison.Ordinal))
            {
                info.Kind = SymKind.Operator;
            }
            else if (info.IsMember)
            {
                info.Kind = info.IsStatic ? SymKind.StaticMethod : SymKind.Method;
            }
            else
            {
                info.Kind = name.IndexOf('<') >= 0 ? SymKind.TemplateFunction : SymKind.Function;
            }

            info.Qualified = comps.Count > 0 ? string.Join("::", comps) + "::" + name : name;

            var sb = new StringBuilder();
            if (info.IsStatic) sb.Append("static ");
            if (info.IsVirtual) sb.Append("virtual ");
            if (info.Return.Length > 0) sb.Append(info.Return).Append(' ');
            sb.Append(info.Qualified);
            if (info.Params != null)
            {
                sb.Append('(').Append(string.Join(", ", info.Params)).Append(')');
                if (info.Qualifiers.Length > 0) sb.Append(' ').Append(info.Qualifiers);
            }
            info.Pretty = TypePretty.Tidy(sb.ToString());
        }

        private static void ParseLambda(SymInfo info, string s)
        {
            info.Kind = SymKind.Lambda;
            Match id = LambdaId.Match(s);
            info.LambdaId = id.Success ? id.Groups[1].Value : "";

            // 外側の関数は、最初の ` と、対応する ' の間に入っている
            int p = s.IndexOf('`');
            if (p >= 0)
            {
                int depth = 0, end = -1;
                for (int k = p; k < s.Length; k++)
                {
                    if (s[k] == '`') depth++;
                    else if (s[k] == '\'')
                    {
                        depth--;
                        if (depth == 0) { end = k; break; }
                    }
                }
                if (end > p)
                {
                    string inner = s.Substring(p + 1, end - p - 1);
                    info.Outer = Parse(inner, "");
                    info.Pretty = info.Outer.Pretty;
                    info.Qualified = info.Outer.Qualified;
                    info.Name = info.Outer.Name;
                    info.Namespace = info.Outer.Namespace;
                    info.Class = info.Outer.Class;
                    return;
                }
            }
            info.Pretty = TypePretty.Type(s);
        }

        private static int MatchOpenParen(string s, int close)
        {
            int depth = 0;
            for (int k = close; k >= 0; k--)
            {
                if (s[k] == ')') depth++;
                else if (s[k] == '(')
                {
                    depth--;
                    if (depth == 0) return k;
                }
            }
            return -1;
        }

        /// <summary>head の from より前を右から左へ読み、「ns::Class::name&lt;...&gt;」の始まりの位置を返す。</summary>
        private static int FindQualStart(string head, int from)
        {
            int i = from;
            while (i > 0)
            {
                char c = head[i - 1];
                if (c == '>')
                {
                    int depth = 0, k = i - 1;
                    for (; k >= 0; k--)
                    {
                        if (head[k] == '>' && !(k > 0 && head[k - 1] == '-')) depth++;
                        else if (head[k] == '<')
                        {
                            depth--;
                            if (depth == 0) break;
                        }
                    }
                    if (k < 0) break;
                    i = k;
                    continue;
                }
                if (c == '\'')
                {
                    int depth = 0, k = i - 1;
                    for (; k >= 0; k--)
                    {
                        if (head[k] == '\'') depth++;
                        else if (head[k] == '`')
                        {
                            depth--;
                            if (depth == 0) break;
                        }
                    }
                    if (k < 0) break;
                    i = k;
                    continue;
                }
                if (char.IsLetterOrDigit(c) || c == '_' || c == ':' || c == '~' || c == '$' || c == '}' || c == '{' || c > 127) { i--; continue; }
                break;
            }
            return i;
        }

        /// <summary>修飾名を、最上位の「::」で分ける。</summary>
        public static List<string> SplitScope(string qual)
        {
            var list = new List<string>();
            int depth = 0, start = 0;
            for (int k = 0; k < qual.Length; k++)
            {
                char c = qual[k];
                if (c == '<' || c == '`' || c == '(') depth++;
                else if ((c == '>' && !(k > 0 && qual[k - 1] == '-')) || c == '\'' || c == ')') depth--;
                else if (c == ':' && depth == 0 && k + 1 < qual.Length && qual[k + 1] == ':')
                {
                    list.Add(qual.Substring(start, k - start));
                    start = k + 2;
                    k++;
                }
            }
            list.Add(qual.Substring(start));
            // 先頭の「::」(グローバル)で生じる空要素を捨てる
            var result = list.Where(x => x.Length > 0).ToList();
            if (result.Count == 0) result.Add(qual);
            return result;
        }
    }
}
