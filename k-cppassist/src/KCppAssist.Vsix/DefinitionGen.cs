using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;

namespace KCppAssist
{
    /// <summary>
    /// ヘッダーの宣言から cpp の定義の雛形を作り、cpp の定義からヘッダーのクラスに足す宣言を作る。VS に依存しない。
    /// 文字の編集(位置と文字)だけを返す。ファイルを開く・書くのは呼び出し側。
    /// </summary>
    internal static class DefinitionGen
    {
        public sealed class Edit
        {
            public int Position;
            public string Text;
        }

        private static readonly Regex CommentRx = new Regex(@"/\*.*?\*/|//[^\r\n]*", RegexOptions.Singleline | RegexOptions.Compiled);
        private static readonly Regex AttrRx = new Regex(@"\[\[[^\]]*\]\]", RegexOptions.Compiled);
        private static readonly Regex AccessRx = new Regex(@"^\s*(?:public|protected|private)\s*:(?!:)", RegexOptions.Compiled);
        private static readonly Regex ExportRx = new Regex(@"\b(?:[A-Z][A-Z0-9_]*_API|[A-Z][A-Z0-9_]*EXPORT[A-Z0-9_]*)\b|__declspec\s*\([^)]*\)", RegexOptions.Compiled);
        private static readonly Regex DeclOnlyWords = new Regex(@"\b(?:virtual|static|explicit|inline|__cdecl|_Use_decl_annotations_)\b", RegexOptions.Compiled);
        private static readonly Regex Refuse = new Regex(@"\b(?:friend|constexpr|consteval|template|typedef|using)\b", RegexOptions.Compiled);

        private static string Clean(string s)
        {
            s = CommentRx.Replace(s, " ");
            return Regex.Replace(s, @"\s+", " ").Trim();
        }

        // ---- 宣言 → 定義 ----

        /// <summary>
        /// ヘッダーの宣言 decl(headerText の中)の、cpp の定義の雛形を足す編集を返す。作れないときは null で、理由を why に入れる。
        /// 置き場所は、同じクラスの前の宣言の定義の直後。なければ同じクラスの最後の定義の直後、それもなければ同じ namespace の定義の直後、最後は末尾。
        /// </summary>
        public static Edit PlanDefinition(string headerText, FunctionScan.Sig decl, string cppText, string eol, out string why)
        {
            why = null;
            if (decl.HasBody) { why = "本体のある関数です"; return null; }
            string inner = decl.Inner(headerText);
            if (SignatureSync.HasDirectives(inner)) { why = "引数の途中に #if があるので、雛形を作れません"; return null; }
            var ps = SignatureSync.SplitParams(inner);
            if (ps == null) { why = "引数を読めませんでした (書きかけかもしれません)"; return null; }

            // 戻り値の型
            // コメントは、Mask で空白にした文字から読む(長い /** ... */ の途中から切り出しても、中身が残らない)
            string before = CppText.Mask(headerText).Substring(decl.PrefixStart, Math.Max(0, decl.NameStart - decl.PrefixStart));
            while (AccessRx.IsMatch(before)) before = AccessRx.Replace(before, "", 1);
            if (Refuse.IsMatch(before)) { why = "friend・constexpr・template の関数は、雛形を作りません"; return null; }
            before = AttrRx.Replace(before, " ");
            before = ExportRx.Replace(before, " ");
            before = DeclOnlyWords.Replace(before, " ");
            string ret = Regex.Replace(before, @"\s+", " ").Trim();
            bool ctor = decl.Class != null && decl.Name == decl.Class;
            if (ret.Length == 0 && !ctor) { why = "戻り値の型を読めませんでした"; return null; }

            // 引数(既定値と SAL 注釈は除く)
            var cleaned = new List<string>();
            foreach (string p in ps)
            {
                string def;
                string core = SignatureSync.StripDefault(SignatureSync.StripComments(p), out def);
                cleaned.Add(Regex.Replace(core, @"\s+", " ").Trim());
            }

            // ')' のあと(const・noexcept・-> T)。override・final は定義に書かない
            string tail = Clean(headerText.Substring(decl.Close + 1, Math.Max(0, decl.End - decl.Close - 1)));
            if (Regex.IsMatch(tail, @"=\s*(?:0|default|delete)\b")) { why = "純粋仮想・= default・= delete の関数は、定義を作りません"; return null; }
            tail = Regex.Replace(tail, @"\b(?:override|final)\b", " ");
            tail = Regex.Replace(tail, @"\s+", " ").Trim();

            // 置き場所と、名前の修飾
            var cppSigs = FunctionScan.Scan(cppText).Where(s => s.HasBody && !s.InClass).ToList();
            var headerSigs = FunctionScan.Scan(headerText);
            FunctionScan.Sig anchor = null;

            // 同じクラス(か同じ namespace)で、この宣言より前にある宣言のうち、定義が cpp にあるもの(近い順)
            var siblings = headerSigs.Where(s => !s.HasBody && s.Open < decl.Open && s.InClass == decl.InClass && s.Chain.SequenceEqual(decl.Chain)).OrderByDescending(s => s.Open);
            foreach (var sib in siblings)
            {
                var sk = SignatureSync.KeyVariants(sib.Inner(headerText));
                var found = cppSigs.Where(d => SyncPlan.Counterpart(d, sib, true) > 0 && SyncPlan.SameKeysAny(SignatureSync.KeyVariants(d.Inner(cppText)), sk)).OrderByDescending(d => SyncPlan.Counterpart(d, sib, true)).FirstOrDefault();
                if (found != null) { anchor = found; break; }
            }
            if (anchor == null)
                anchor = cppSigs.Where(d => d.Class == decl.Class && SyncPlan.ChainScore(d.Chain, decl.Chain) > 0).OrderByDescending(d => d.End).FirstOrDefault();
            if (anchor == null)
                anchor = cppSigs.Where(d => d.Enclosing > 0 && d.Enclosing <= decl.Chain.Count && d.Chain.Take(d.Enclosing).SequenceEqual(decl.Chain.Take(d.Enclosing))).OrderByDescending(d => d.End).FirstOrDefault();

            // anchor が namespace の中にあれば、その分は修飾しない
            int skip = anchor != null && anchor.Enclosing > 0 && anchor.Enclosing <= decl.Chain.Count && anchor.Chain.Take(anchor.Enclosing).SequenceEqual(decl.Chain.Take(anchor.Enclosing)) ? anchor.Enclosing : 0;
            var quals = decl.Chain.Skip(skip).ToList();
            string name = (quals.Count > 0 ? string.Join("::", quals) + "::" : "") + decl.Name;

            var sb = new StringBuilder();
            if (ret.Length > 0) sb.Append(ret).Append(' ');
            sb.Append(name).Append('(').Append(string.Join(", ", cleaned)).Append(')');
            if (tail.Length > 0) sb.Append(' ').Append(tail);
            sb.Append(eol).Append('{').Append(eol);
            if (!ctor) sb.Append(ReturnLine(ret, eol));
            sb.Append('}');
            string stub = sb.ToString();

            if (anchor != null)
                return new Edit { Position = anchor.End + 1, Text = eol + eol + stub };
            bool endsWithNewline = cppText.EndsWith("\n");
            return new Edit { Position = cppText.Length, Text = (cppText.Length == 0 ? "" : (endsWithNewline ? eol : eol + eol)) + stub + eol };
        }

        /// <summary>戻り値の型に合わせた、仮の return 文(void・参照・auto は何も書かない)。</summary>
        private static string ReturnLine(string ret, string eol)
        {
            string r = Regex.Replace(ret, @"\b(?:const|volatile|__cdecl|__stdcall|__fastcall|__vectorcall|XM_CALLCONV)\b", " ");
            r = Regex.Replace(r, @"\s+", " ").Trim();
            if (r == "void" || r.Length == 0 || r.Contains("&") || r == "auto" || r.StartsWith("decltype")) return "";
            if (r.EndsWith("*") || Regex.IsMatch(r, @"\b(?:unique_ptr|shared_ptr|weak_ptr|optional|function)\b")) return "  return " + (r.EndsWith("*") ? "nullptr" : "{}") + ";" + eol;
            if (r == "bool") return "  return false;" + eol;
            if (Regex.IsMatch(r, @"^(?:unsigned |signed )?(?:int|long|short|char|long long|size_t|float|double|u?int(?:8|16|32|64)_t|[A-Z][A-Z0-9_]*)$")) return "  return 0;" + eol;
            return "  return {};" + eol;
        }

        // ---- 定義 → 宣言 ----

        /// <summary>
        /// cpp の定義 def(cppText の中)の、ヘッダーのクラスに足す宣言 1 行(「型 名前(引数) const;」)を返す。
        /// クラスのメンバー関数の定義でなければ null で、理由を why に入れる。
        /// </summary>
        public static string DeclarationFor(string cppText, FunctionScan.Sig def, out string why)
        {
            why = null;
            if (!def.HasBody) { why = "本体のない関数です"; return null; }
            if (def.InClass) { why = "クラスの中に書いた関数です"; return null; }
            if (def.Class == null || def.Chain.Count <= def.Enclosing) { why = "Class::Func の形の定義ではありません"; return null; }
            string inner = def.Inner(cppText);
            if (SignatureSync.HasDirectives(inner)) { why = "引数の途中に #if があるので、宣言を作れません"; return null; }
            var ps = SignatureSync.SplitParams(inner);
            if (ps == null) { why = "引数を読めませんでした (書きかけかもしれません)"; return null; }

            string before = CppText.Mask(cppText).Substring(def.PrefixStart, Math.Max(0, def.NameStart - def.PrefixStart));
            if (Refuse.IsMatch(before)) { why = "template・constexpr などの関数は、宣言を作りません"; return null; }
            before = AttrRx.Replace(before, " ");
            before = Regex.Replace(before, @"\b(?:static|inline|virtual|_Use_decl_annotations_)\b", " ");
            string ret = Regex.Replace(before, @"\s+", " ").Trim();
            bool ctor = def.Name == def.Class;
            if (ret.Length == 0 && !ctor) { why = "戻り値の型を読めませんでした"; return null; }

            // ')' のあと、本体の「{」か初期化子リストの「:」の手前まで
            int j = def.Close + 1;
            while (j < cppText.Length)
            {
                char c = cppText[j];
                if (c == '{' || c == ';') break;
                if (c == ':')
                {
                    if (j + 1 < cppText.Length && cppText[j + 1] == ':') { j += 2; continue; }
                    break;
                }
                j++;
            }
            string tail = Clean(cppText.Substring(def.Close + 1, Math.Max(0, j - def.Close - 1)));

            var sb = new StringBuilder();
            if (ret.Length > 0) sb.Append(ret).Append(' ');
            sb.Append(def.Name).Append('(').Append(string.Join(", ", ps.Select(p => Regex.Replace(SignatureSync.StripComments(p), @"\s+", " ").Trim()))).Append(')');
            if (tail.Length > 0) sb.Append(' ').Append(tail);
            sb.Append(';');
            return sb.ToString();
        }

        // ---- クラスの public の末尾に足す ----

        /// <summary>
        /// open の「{」で始まるクラスの本体の、public の区画の末尾に、メンバー 1 行(宣言)を入れる編集を返す。
        /// public: がなければ、末尾に作る(struct は先頭から public)。読めなければ null。
        /// </summary>
        public static Edit PlanPublicMember(string text, int open, bool isStruct, string declaration, string eol)
        {
            string m = CppText.Mask(text);
            int close = Scopes.MatchBrace(m, open);
            if (close < 0) return null;

            var specs = new List<KeyValuePair<int, string>>();     // (指定子の頭, 名前)
            var specEnd = new Dictionary<int, int>();
            int depth = 0;
            for (int i = open; i < close; i++)
            {
                char c = m[i];
                if (c == '{') depth++;
                else if (c == '}') depth--;
                else if (depth == 1 && c == 'p' && (i == 0 || !(char.IsLetterOrDigit(m[i - 1]) || m[i - 1] == '_')))
                {
                    var s = Regex.Match(m.Substring(i, Math.Min(m.Length - i, 16)), @"^(public|protected|private)\s*:(?!:)");
                    if (s.Success) { specs.Add(new KeyValuePair<int, string>(i, s.Groups[1].Value)); specEnd[i] = i + s.Length; }
                }
            }

            int lineStart = close;
            while (lineStart > 0 && text[lineStart - 1] != '\n') lineStart--;
            bool braceFirst = text.Substring(lineStart, close - lineStart).Trim().Length == 0;
            string closeIndent = braceFirst ? text.Substring(lineStart, close - lineStart) : "";
            string memberIndent = closeIndent + "  ";

            int regionStart = -1, regionEnd = close;
            int last = specs.FindLastIndex(s => s.Value == "public");
            if (last >= 0)
            {
                regionStart = specEnd[specs[last].Key];
                if (last + 1 < specs.Count) regionEnd = specs[last + 1].Key;
            }
            else if (isStruct)
            {
                regionStart = open + 1;
                if (specs.Count > 0) regionEnd = specs[0].Key;
            }

            if (regionStart < 0)
            {
                // public: がない。末尾に作る
                var sb = new StringBuilder();
                sb.Append(eol).Append(closeIndent).Append(" public:").Append(eol).Append(memberIndent).Append(declaration).Append(eol);
                return new Edit { Position = braceFirst ? lineStart : close, Text = braceFirst ? sb.ToString() : eol + sb.ToString() };
            }

            int lastNonWs = regionEnd - 1;
            while (lastNonWs >= regionStart && char.IsWhiteSpace(m[lastNonWs])) lastNonWs--;
            bool hasMember = lastNonWs >= regionStart;
            if (!hasMember) lastNonWs = regionStart - 1;

            if (hasMember)
            {
                int ls = lastNonWs;
                while (ls > 0 && text[ls - 1] != '\n') ls--;
                string line = text.Substring(ls, lastNonWs - ls + 1);
                memberIndent = line.Substring(0, line.Length - line.TrimStart().Length);
            }

            int nl = text.IndexOf('\n', Math.Max(0, lastNonWs + 1));
            if (nl < 0 || nl > close) nl = close;
            else if (nl > 0 && text[nl - 1] == '\r') nl--;
            return new Edit { Position = nl, Text = eol + memberIndent + declaration };
        }
    }
}
