using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;

namespace KCppAssist
{
    /// <summary>
    /// クラス・構造体・enum から、決まった形のコードを作る。VS に依存しない。
    /// 特殊メンバー関数、比較演算子、enum の文字列化、std::formatter、std::hash、JSON・cereal、
    /// Direct3D の入力レイアウト、定数バッファの並び(HLSL の 16 バイト境界)、初期化子リストの並べ替え。
    /// </summary>
    internal static class ClassGen
    {
        public static List<Refactor.Offer> Offers(string text, int caret, string eol, bool header)
        {
            var list = new List<Refactor.Offer>();
            string why;
            void Try(string id, string title) { if (Make(id, text, caret, eol, header, out why) != null) list.Add(new Refactor.Offer { Id = id, Title = L.T(title) }); }
            int ls = MemberScan.LineStart(text, caret);
            string near = text.Substring(Math.Max(0, ls - 200), Math.Min(text.Length, caret + 200) - Math.Max(0, ls - 200));
            if (near.Contains("enum")) Try("enumstr", "enum の ToString / FromString を作る");
            if (near.Contains(":")) Try("initorder", "初期化子リストを、メンバーの宣言の順に並べ替える");
            var cls = MemberScan.At(text, caret);
            if (cls == null) return list;
            // クラス全体を作り変える項目は、クラスそのものを指している行(クラス名・{・};・空の行・public: など)でだけ出す。
            // メンバー変数や関数の行で押したときに、クラス全体の項目が並ぶと、その行への操作と紛れる
            if (!AtClassLevel(text, caret)) return list;
            // コンストラクター・デストラクターは 3 通り。3 つ目(.h に宣言、.cpp に定義)は、ファイルをまたぐので、パッケージの側で、この 2 つのすぐ後ろに足す
            Try("ctordtor-default", "コンストラクター・デストラクターを作る (= default)");
            Try("ctordtor-inline", "コンストラクター・デストラクターを作る (.h に {} で書く)");
            Try("nocopymove", "コピー・ムーブを禁止する (= delete)");
            Try("nocopy", "コピー禁止・ムーブ可にする (= delete / = default)");
            Try("rule5", "コピー・ムーブ・デストラクターを = default で書く");
            Try("compare", "== と <=> を = default で作る");
            Try("formatter", "std::format で書けるようにする (std::formatter)");
            Try("hash", "std::unordered_map のキーにできるようにする (std::hash)");
            Try("json", "JSON に読み書きできるようにする (nlohmann)");
            Try("cereal", "cereal で保存できるようにする (serialize)");
            Try("inputlayout", "頂点構造体から入力レイアウトを作る (D3D)");
            Try("cbuffer", "定数バッファの並びを HLSL に合わせる (パディング)");
            return list;
        }

        public static Refactor.Change Make(string id, string text, int caret, string eol, bool header, out string why)
        {
            why = null;
            switch (id)
            {
                case "enumstr": return EnumString(text, caret, eol, out why);
                case "initorder": return InitOrder(text, caret, null, out why);
            }
            var cls = MemberScan.At(text, caret);
            if (cls == null) { why = "カーソルが、class / struct の中にありません"; return null; }
            switch (id)
            {
                case "ctordtor": return CtorDtor(text, cls, eol, CtorStyle.Declare, out why);
                case "ctordtor-default": return CtorDtor(text, cls, eol, CtorStyle.Default, out why);
                case "ctordtor-inline": return CtorDtor(text, cls, eol, CtorStyle.Inline, out why);
                case "nocopymove": return NoCopyMove(text, cls, eol, out why);
                case "nocopy": return Special(text, cls, eol, false, out why);
                case "rule5": return Special(text, cls, eol, true, out why);
                case "compare": return Compare(text, cls, eol, out why);
                case "formatter": return Formatter(text, cls, eol, out why);
                case "hash": return Hash(text, cls, eol, out why);
                case "json": return Json(text, cls, eol, out why);
                case "cereal": return Cereal(text, cls, eol, out why);
                case "inputlayout": return InputLayout(text, cls, eol, header, out why);
                case "cbuffer": return CBuffer(text, cls, eol, out why);
            }
            why = "知らない書き換えです: " + id;
            return null;
        }

        /// <summary>
        /// クラスの public の区画の末尾に、複数行を入れる。字下げは、その区画のメンバーに合わせる。
        /// lines の空文字は空行。
        /// </summary>
        private static void AddPublic(Refactor.Change ch, string text, MemberScan.ClassInfo cls, IList<string> lines, string eol)
        {
            const string Mark = "\u0001";
            var e = DefinitionGen.PlanPublicMember(text, cls.Scope.Open, cls.IsStruct, Mark, eol);
            int k = e.Text.IndexOf(Mark, StringComparison.Ordinal);
            int ls = e.Text.LastIndexOf('\n', k) + 1;
            string indent = e.Text.Substring(ls, k - ls);
            string joined = string.Join(eol, lines.Select((l, i) => i == 0 ? l : (l.Length == 0 ? "" : indent + l)));
            ch.Add(e.Position, 0, e.Text.Replace(Mark, joined));
        }

        /// <summary>クラスの外(囲んでいる一番外の namespace の後ろ。namespace がなければクラスの「};」の後ろ)に入れる位置。</summary>
        private static int AfterOutermost(string text, MemberScan.ClassInfo cls)
        {
            var s = cls.Scope;
            while (s.Parent != null) s = s.Parent;
            string m = CppText.Mask(text);
            int pos = s.Close + 1;
            if (s.IsClass)
            {
                int semi = m.IndexOf(';', pos);
                if (semi >= 0 && m.Substring(pos, semi - pos).Trim().Length == 0) pos = semi + 1;
            }
            else
            {
                // 「}  // namespace game」のコメントの後ろ
                pos = MemberScan.LineEnd(text, s.Close);
            }
            return pos;
        }

        private static string Ref(string type)
        {
            return Regex.IsMatch(type, @"^(?:(?:const\s+)?(?:bool|char|int|float|double|unsigned|long|short|size_t|u?int\d+_t|UINT|DWORD|BOOL)\b)") ? type : "const " + type + "&";
        }

        /// <summary>
        /// caret の行が、クラスそのものを指す行か。クラス名の行、「{」「}」「};」だけの行、空の行、アクセス指定子(public: など)の行。
        /// メンバー変数・関数・コメントの行は false。
        /// </summary>
        public static bool AtClassLevel(string text, int caret)
        {
            if (OnHead(text, caret)) return true;
            int ls = MemberScan.LineStart(text, caret), le = MemberScan.LineEnd(text, caret);
            string t = text.Substring(ls, le - ls).Trim();
            return t.Length == 0 || Regex.IsMatch(t, @"^(?:\{|\}\s*;?|(?:public|protected|private)\s*:)$");
        }

        /// <summary>caret が「class X」「struct X」を書いた行の上か。</summary>
        public static bool OnHead(string text, int caret)
        {
            int ls = MemberScan.LineStart(text, caret), le = MemberScan.LineEnd(text, caret);
            return Regex.IsMatch(CppText.Mask(text).Substring(ls, le - ls), @"^\s*(?:template\s*<[^>]*>\s*)?(?:class|struct)\s+(?:\w+\s+)*\w+\s*(?:final\s*)?(?::[^;{]*)?\{?\s*$");
        }

        // ---- コンストラクター・デストラクター / コピー・ムーブ禁止 ----

        /// <summary>Declare: 「Foo();」(cpp に定義を作る前の宣言)。Default: 「Foo() = default;」。Inline: 「Foo() {}」(ヘッダーに本体)。</summary>
        internal enum CtorStyle { Declare, Default, Inline }

        private static Refactor.Change CtorDtor(string text, MemberScan.ClassInfo cls, string eol, CtorStyle style, out string why)
        {
            why = null;
            string n = Regex.Escape(cls.Name);
            // 引数のないコンストラクターがなければ作る。コピー・ムーブのコンストラクターがあっても作る(それらがあると、暗黙の Foo() は作られないため、むしろ要る)
            bool hasDefault = MemberScan.HasFunction(cls, @"(?<![~\w])" + n + @"\s*\(\s*(?:void\s*)?\)");
            bool hasDtor = MemberScan.HasFunction(cls, "~" + n + @"\s*\(");
            string tail = style == CtorStyle.Default ? "() = default;" : style == CtorStyle.Inline ? "() {}" : "();";
            var lines = new List<string>();
            if (!hasDefault) lines.Add(cls.Name + tail);
            if (!hasDtor) lines.Add((cls.HasVirtual ? "virtual " : "") + "~" + cls.Name + tail);
            if (lines.Count == 0) { why = "コンストラクターとデストラクターは、もう宣言してあります"; return null; }
            var ch = new Refactor.Change();
            // コピー・ムーブの宣言があれば、その上に置く(コンストラクター → デストラクター → コピー → ムーブ の並びにする)
            int at = FirstCopyMoveLine(text, cls);
            if (at >= 0)
            {
                string ind = MemberScan.Indent(text, at);
                ch.Add(at, 0, string.Concat(lines.Select(l => ind + l + eol)));
            }
            else AddPublic(ch, text, cls, lines, eol);
            string what = string.Join(" と ", lines.Select(l => "~" + cls.Name == l.Replace("virtual ", "").Split('(')[0] ? "~" + cls.Name + "()" : cls.Name + "()"));
            ch.Message = cls.Name + " に " + what + (style == CtorStyle.Default ? " を = default で作りました" : style == CtorStyle.Inline ? " を {} で作りました" : " を宣言しました");
            return ch;
        }

        /// <summary>クラスの本体の直下で、コピー・ムーブのコンストラクターか代入演算子を宣言している最初の行の頭。なければ -1。</summary>
        private static int FirstCopyMoveLine(string text, MemberScan.ClassInfo cls)
        {
            string m = CppText.Mask(text);
            string n = Regex.Escape(cls.Name);
            var rx = new Regex(@"^\s*(?:" + n + @"\s*\(\s*(?:const\s+)?" + n + @"\s*&|" + n + @"\s*&\s*operator\s*=)");
            int depth = 0;
            int p = MemberScan.LineStart(text, cls.Scope.Open);
            for (int i = cls.Scope.Open; i < cls.Scope.Close; i++)
            {
                char c = m[i];
                if (c == '{') depth++;
                else if (c == '}') depth--;
                else if (c == '\n' && depth == 1)
                {
                    int ls = i + 1, le = MemberScan.LineEnd(text, ls);
                    if (le > ls && rx.IsMatch(m.Substring(ls, le - ls))) return ls;
                }
            }
            return -1;
        }

        private static Refactor.Change NoCopyMove(string text, MemberScan.ClassInfo cls, string eol, out string why)
        {
            why = null;
            string c = cls.Name, n = Regex.Escape(cls.Name);
            var lines = new List<string>();
            if (!MemberScan.HasFunction(cls, @"" + n + @"\s*\(\s*const\s+" + n + @"\s*&")) lines.Add(c + "(const " + c + "&) = delete;");
            if (!MemberScan.HasFunction(cls, @"operator\s*=\s*\(\s*const\s+" + n + @"\s*&")) lines.Add(c + "& operator=(const " + c + "&) = delete;");
            if (!MemberScan.HasFunction(cls, @"" + n + @"\s*\(\s*" + n + @"\s*&&")) lines.Add(c + "(" + c + "&&) = delete;");
            if (!MemberScan.HasFunction(cls, @"operator\s*=\s*\(\s*" + n + @"\s*&&")) lines.Add(c + "& operator=(" + c + "&&) = delete;");
            if (lines.Count == 0) { why = "コピーとムーブは、もう全部宣言してあります"; return null; }
            var ch = new Refactor.Change();
            AddPublic(ch, text, cls, lines, eol);
            ch.Message = c + " のコピーとムーブを禁止しました (" + lines.Count + " 個)";
            return ch;
        }

        // ---- 特殊メンバー関数 ----

        private static Refactor.Change Special(string text, MemberScan.ClassInfo cls, string eol, bool allDefault, out string why)
        {
            why = null;
            string n = Regex.Escape(cls.Name);
            var lines = new List<string>();
            bool hasCopyCtor = MemberScan.HasFunction(cls, @"\b" + n + @"\s*\(\s*const\s+" + n + @"\s*&");
            bool hasCopyAssign = MemberScan.HasFunction(cls, @"operator\s*=\s*\(\s*const\s+" + n + @"\s*&");
            bool hasMoveCtor = MemberScan.HasFunction(cls, @"\b" + n + @"\s*\(\s*" + n + @"\s*&&");
            bool hasMoveAssign = MemberScan.HasFunction(cls, @"operator\s*=\s*\(\s*" + n + @"\s*&&");
            bool hasDtor = MemberScan.HasFunction(cls, "~" + n + @"\s*\(");
            // コピー コンストラクターを 1 つでも宣言すると、暗黙の既定コンストラクターは作られなくなる
            if (!cls.HasUserCtor) lines.Add(cls.Name + "() = default;");
            if (allDefault && !hasDtor) lines.Add((cls.HasVirtual ? "virtual " : "") + "~" + cls.Name + "() = default;");
            string copy = allDefault ? "default" : "delete";
            if (!hasCopyCtor) lines.Add(cls.Name + "(const " + cls.Name + "&) = " + copy + ";");
            if (!hasCopyAssign) lines.Add(cls.Name + "& operator=(const " + cls.Name + "&) = " + copy + ";");
            if (!hasMoveCtor) lines.Add(cls.Name + "(" + cls.Name + "&&) noexcept = default;");
            if (!hasMoveAssign) lines.Add(cls.Name + "& operator=(" + cls.Name + "&&) noexcept = default;");
            if (!lines.Any(l => l.Contains("(const " + cls.Name) || l.Contains("&&)") || l.StartsWith("~") || l.StartsWith("virtual")))
            { why = "コピー・ムーブはすでに全部宣言してあります"; return null; }
            var ch = new Refactor.Change();
            if (!allDefault && cls.HasVirtual && !hasDtor) lines.Insert(0, "virtual ~" + cls.Name + "() = default;");
            AddPublic(ch, text, cls, lines, eol);
            ch.Message = cls.Name + " に" + (allDefault ? "コピー・ムーブを = default で" : "コピー禁止・ムーブ可を") + "書きました";
            return ch;
        }

        // ---- 比較演算子 ----

        private static Refactor.Change Compare(string text, MemberScan.ClassInfo cls, string eol, out string why)
        {
            why = null;
            if (MemberScan.HasFunction(cls, @"operator\s*(?:==|<=>)")) { why = "== か <=> が、すでにあります"; return null; }
            if (cls.Members.Count == 0) { why = "データ メンバーがありません"; return null; }
            var ch = new Refactor.Change();
            AddPublic(ch, text, cls, new[]
            {
                "bool operator==(const " + cls.Name + "&) const = default;",
                "auto operator<=>(const " + cls.Name + "&) const = default;",
            }, eol);
            Refactor.AddInclude(ch, text, "<compare>", eol);
            ch.Message = cls.Name + " に == と <=> を足しました (メンバーの型に比較がないと、= default は削除扱いになります)";
            return ch;
        }

        // ---- enum の文字列化 ----

        private static readonly Regex EnumHead = new Regex(@"\benum\s+(class\s+|struct\s+)?([A-Za-z_]\w*)\s*(?::\s*[\w:\s]+)?\{");

        private static Refactor.Change EnumString(string text, int caret, string eol, out string why)
        {
            why = null;
            string m = CppText.Mask(text);
            foreach (Match x in EnumHead.Matches(m))
            {
                int open = x.Index + x.Length - 1;
                int close = Scopes.MatchBrace(m, open);
                if (close < 0) continue;
                if (caret < MemberScan.LineStart(text, x.Index) || caret > close + 2) continue;
                int semi = m.IndexOf(';', close);
                if (semi < 0) { why = "enum の「;」が見つかりません"; return null; }
                var defs = SwitchGen.ParseEnums(text.Substring(x.Index, semi + 1 - x.Index));
                if (defs.Count == 0 || defs[0].Values.Count == 0) { why = "enum の値を読めません"; return null; }
                var def = defs[0];
                string name = def.Name;
                if (Regex.IsMatch(m, @"\bToString\s*\(\s*" + Regex.Escape(name) + @"\b")) { why = "ToString(" + name + ") はすでにあります"; return null; }
                var scopes = Scopes.Parse(text);
                var inClass = scopes.Where(s => s.Open < x.Index && x.Index < s.Close).OrderByDescending(s => s.Open).FirstOrDefault();
                bool member = inClass != null && inClass.IsClass;
                string q = member ? "static constexpr " : "constexpr ";
                string indent = MemberScan.Indent(text, x.Index);
                string unit = CppText.IndentUnit(text);
                string i1 = indent + unit, i2 = indent + unit + unit;
                var sb = new StringBuilder();
                sb.Append(eol).Append(eol);
                sb.Append(indent).Append(q).Append("std::string_view ToString(").Append(name).Append(" value) {").Append(eol);
                sb.Append(i1).Append("switch (value) {").Append(eol);
                foreach (string v in def.Values) sb.Append(i2).Append("case ").Append(name).Append("::").Append(v).Append(": return \"").Append(v).Append("\";").Append(eol);
                sb.Append(i1).Append("}").Append(eol);
                sb.Append(i1).Append("return \"?\";").Append(eol);
                sb.Append(indent).Append("}").Append(eol).Append(eol);
                sb.Append(indent).Append(q).Append("std::optional<").Append(name).Append("> ").Append(name).Append("FromString(std::string_view text) {").Append(eol);
                foreach (string v in def.Values) sb.Append(i1).Append("if (text == \"").Append(v).Append("\") return ").Append(name).Append("::").Append(v).Append(";").Append(eol);
                sb.Append(i1).Append("return std::nullopt;").Append(eol);
                sb.Append(indent).Append("}");
                var ch = new Refactor.Change().Add(semi + 1, 0, sb.ToString());
                Refactor.AddInclude(ch, text, "<optional>", eol);
                Refactor.AddInclude(ch, text, "<string_view>", eol);
                ch.Message = name + " の ToString と " + name + "FromString を作りました (" + def.Values.Count + " 値)";
                return ch;
            }
            why = "カーソルが enum の上にありません";
            return null;
        }

        // ---- std::formatter ----

        /// <summary>メンバーを std::format の引数にする式。DirectXMath / SimpleMath のベクトルは成分に分ける。</summary>
        private static void FormatArgs(MemberScan.Member mem, List<string> fields, List<string> args)
        {
            string t = Regex.Replace(mem.Type, @"^(?:const\s+)|(?:DirectX::|SimpleMath::)", "").Trim();
            string v = "v." + mem.Name;
            string[] comps = null;
            if (Regex.IsMatch(t, @"^(?:XMFLOAT2|XMINT2|XMUINT2|Vector2)$")) comps = new[] { "x", "y" };
            else if (Regex.IsMatch(t, @"^(?:XMFLOAT3|XMINT3|XMUINT3|Vector3)$")) comps = new[] { "x", "y", "z" };
            else if (Regex.IsMatch(t, @"^(?:XMFLOAT4|XMINT4|XMUINT4|Vector4|Quaternion)$")) comps = new[] { "x", "y", "z", "w" };
            else if (t == "Color") comps = new[] { "x", "y", "z", "w" };
            if (mem.Array.Length > 0) { fields.Add(mem.Name + "={}"); args.Add("std::span(" + v + ")"); return; }
            if (comps != null)
            {
                fields.Add(mem.Name + "=(" + string.Join(", ", comps.Select(_ => "{}")) + ")");
                args.AddRange(comps.Select(c => v + "." + c));
                return;
            }
            if (t.EndsWith("*") && !Regex.IsMatch(t, @"char\s*\*$")) { fields.Add(mem.Name + "={}"); args.Add("static_cast<const void*>(" + v + ")"); return; }
            fields.Add(mem.Name + "={}");
            args.Add(v);
        }

        private static Refactor.Change Formatter(string text, MemberScan.ClassInfo cls, string eol, out string why)
        {
            why = null;
            if (Regex.IsMatch(text, @"formatter\s*<\s*(?:[\w:]*::)?" + Regex.Escape(cls.Name) + @"\s*>")) { why = "std::formatter<" + cls.Name + "> はすでにあります"; return null; }
            var pub = cls.Members.Where(x => x.Access == "public").ToList();
            if (pub.Count == 0) { why = "public のデータ メンバーがありません (formatter からは private を読めません)"; return null; }
            var fields = new List<string>(); var args = new List<string>();
            foreach (var mem in pub) FormatArgs(mem, fields, args);
            string fmt = "{{" + string.Join(", ", fields) + "}}";
            string full = cls.FullName;
            string u1 = CppText.IndentUnit(text), u2 = u1 + u1;
            var sb = new StringBuilder();
            sb.Append(eol).Append(eol);
            sb.Append("template <>").Append(eol);
            sb.Append("struct std::formatter<").Append(full).Append("> {").Append(eol);
            sb.Append(u1).Append("constexpr auto parse(std::format_parse_context& ctx) { return ctx.begin(); }").Append(eol).Append(eol);
            sb.Append(u1).Append("auto format(const ").Append(full).Append("& v, std::format_context& ctx) const {").Append(eol);
            sb.Append(u2).Append("return std::format_to(ctx.out(), \"").Append(fmt).Append("\",").Append(eol);
            sb.Append(u2).Append(u2).Append(string.Join(", ", args)).Append(");").Append(eol);
            sb.Append(u1).Append("}").Append(eol);
            sb.Append("};");
            var ch = new Refactor.Change().Add(AfterOutermost(text, cls), 0, sb.ToString());
            Refactor.AddInclude(ch, text, "<format>", eol);
            if (pub.Any(x => x.Array.Length > 0)) Refactor.AddInclude(ch, text, "<span>", eol);
            ch.Message = "std::formatter<" + cls.Name + "> を作りました (public のメンバー " + pub.Count + " 個。配列の表示は C++23 の範囲の書式を使います)";
            return ch;
        }

        // ---- std::hash ----

        private static Refactor.Change Hash(string text, MemberScan.ClassInfo cls, string eol, out string why)
        {
            why = null;
            if (Regex.IsMatch(text, @"hash\s*<\s*(?:[\w:]*::)?" + Regex.Escape(cls.Name) + @"\s*>")) { why = "std::hash<" + cls.Name + "> はすでにあります"; return null; }
            var pub = cls.Members.Where(x => x.Access == "public" && x.Array.Length == 0).ToList();
            if (pub.Count == 0) { why = "public のデータ メンバー(配列以外)がありません"; return null; }
            string full = cls.FullName;
            string u1 = CppText.IndentUnit(text), u2 = u1 + u1;
            var sb = new StringBuilder();
            sb.Append(eol).Append(eol);
            sb.Append("template <>").Append(eol);
            sb.Append("struct std::hash<").Append(full).Append("> {").Append(eol);
            sb.Append(u1).Append("size_t operator()(const ").Append(full).Append("& v) const noexcept {").Append(eol);
            sb.Append(u2).Append("size_t h = 0;").Append(eol);
            sb.Append(u2).Append("auto mix = [&h](size_t x) { h ^= x + 0x9e3779b9 + (h << 6) + (h >> 2); };").Append(eol);
            foreach (var mem in pub)
                sb.Append(u2).Append("mix(std::hash<std::remove_cvref_t<decltype(v.").Append(mem.Name).Append(")>>{}(v.").Append(mem.Name).Append("));").Append(eol);
            sb.Append(u2).Append("return h;").Append(eol);
            sb.Append(u1).Append("}").Append(eol);
            sb.Append("};");
            var ch = new Refactor.Change().Add(AfterOutermost(text, cls), 0, sb.ToString());
            Refactor.AddInclude(ch, text, "<functional>", eol);
            Refactor.AddInclude(ch, text, "<type_traits>", eol);
            ch.Message = "std::hash<" + cls.Name + "> を作りました (メンバー " + pub.Count + " 個。== がなければ、== と <=> も作ってください)";
            return ch;
        }

        // ---- JSON(nlohmann)・cereal ----

        private static Refactor.Change Json(string text, MemberScan.ClassInfo cls, string eol, out string why)
        {
            why = null;
            if (Regex.IsMatch(text, @"NLOHMANN_DEFINE_TYPE_\w+\s*\(\s*" + Regex.Escape(cls.Name) + @"\b")) { why = "NLOHMANN_DEFINE_TYPE はすでにあります"; return null; }
            var ms = cls.Members.Where(x => !x.Type.EndsWith("*") && !x.Type.EndsWith("&")).ToList();
            if (ms.Count == 0) { why = "保存できるデータ メンバーがありません"; return null; }
            var ch = new Refactor.Change();
            var lines = new List<string>
            {
                "NLOHMANN_DEFINE_TYPE_INTRUSIVE(" + cls.Name + ", " + string.Join(", ", ms.Select(x => x.Name)) + ")",
            };
            AddPublic(ch, text, cls, lines, eol);
            Refactor.AddInclude(ch, text, "<nlohmann/json.hpp>", eol);
            string skipped = cls.Members.Count > ms.Count ? "。ポインターと参照のメンバーは入れていません" : "";
            ch.Message = cls.Name + " を JSON に読み書きできるようにしました (メンバー " + ms.Count + " 個" + skipped + ")";
            return ch;
        }

        private static Refactor.Change Cereal(string text, MemberScan.ClassInfo cls, string eol, out string why)
        {
            why = null;
            if (MemberScan.HasFunction(cls, @"\bserialize\s*\(")) { why = "serialize はすでにあります"; return null; }
            var ms = cls.Members.Where(x => !x.Type.EndsWith("*") && !x.Type.EndsWith("&")).ToList();
            if (ms.Count == 0) { why = "保存できるデータ メンバーがありません"; return null; }
            var ch = new Refactor.Change();
            var lines = new List<string>
            {
                "template <class Archive>",
                "void serialize(Archive& ar) {",
                CppText.IndentUnit(text) + "ar(" + string.Join(", ", ms.Select(x => "CEREAL_NVP(" + x.Name + ")")) + ");",
                "}",
            };
            AddPublic(ch, text, cls, lines, eol);
            Refactor.AddInclude(ch, text, "<cereal/cereal.hpp>", eol);
            ch.Message = cls.Name + " に serialize を作りました (メンバー " + ms.Count + " 個。std::vector などは cereal/types/vector.hpp の #include も要ります)";
            return ch;
        }

        // ---- Direct3D の入力レイアウト ----

        private sealed class VType { public int Size; public int Align; public string Format; public int Comp; }

        private static VType VertexType(string type)
        {
            string t = Regex.Replace(type, @"^(?:const\s+)|(?:DirectX::|SimpleMath::|DirectX::SimpleMath::)", "").Trim();
            switch (t)
            {
                case "float": return new VType { Size = 4, Format = "R32_FLOAT", Comp = 1 };
                case "XMFLOAT2": case "Vector2": case "float2": return new VType { Size = 8, Format = "R32G32_FLOAT", Comp = 2 };
                case "XMFLOAT3": case "Vector3": case "float3": return new VType { Size = 12, Format = "R32G32B32_FLOAT", Comp = 3 };
                case "XMFLOAT4": case "Vector4": case "Color": case "Quaternion": case "float4": return new VType { Size = 16, Format = "R32G32B32A32_FLOAT", Comp = 4 };
                case "uint32_t": case "UINT": case "unsigned int": case "std::uint32_t": return new VType { Size = 4, Format = "R32_UINT", Comp = 1 };
                case "int32_t": case "int": case "INT": case "std::int32_t": return new VType { Size = 4, Format = "R32_SINT", Comp = 1 };
                case "XMUINT2": return new VType { Size = 8, Format = "R32G32_UINT", Comp = 2 };
                case "XMUINT3": return new VType { Size = 12, Format = "R32G32B32_UINT", Comp = 3 };
                case "XMUINT4": return new VType { Size = 16, Format = "R32G32B32A32_UINT", Comp = 4 };
                case "XMINT2": return new VType { Size = 8, Format = "R32G32_SINT", Comp = 2 };
                case "XMINT3": return new VType { Size = 12, Format = "R32G32B32_SINT", Comp = 3 };
                case "XMINT4": return new VType { Size = 16, Format = "R32G32B32A32_SINT", Comp = 4 };
                case "XMUBYTEN4": return new VType { Size = 4, Format = "R8G8B8A8_UNORM", Comp = 4 };
                case "XMUBYTE4": return new VType { Size = 4, Format = "R8G8B8A8_UINT", Comp = 4 };
            }
            return null;
        }

        /// <summary>メンバーの名前から意味名(セマンティクス)を決める。決まらなければ TEXCOORD。</summary>
        public static string Semantic(string name)
        {
            string n = name.ToLowerInvariant().Trim('_');
            if (n.StartsWith("m_")) n = n.Substring(2);
            if (Regex.IsMatch(n, @"^(?:pos|position|p)\d*$")) return "POSITION";
            if (Regex.IsMatch(n, @"^(?:normal|nrm|norm|n)\d*$")) return "NORMAL";
            if (Regex.IsMatch(n, @"^(?:tangent|tan)\d*$")) return "TANGENT";
            if (Regex.IsMatch(n, @"^(?:binormal|bitangent)\d*$")) return "BINORMAL";
            if (Regex.IsMatch(n, @"^(?:color|colour|col|diffuse)\d*$")) return "COLOR";
            if (Regex.IsMatch(n, @"^(?:blendindices|boneindices|bones|joints|indices)\d*$")) return "BLENDINDICES";
            if (Regex.IsMatch(n, @"^(?:blendweight|blendweights|weights|weight)\d*$")) return "BLENDWEIGHT";
            return "TEXCOORD";
        }

        private static Refactor.Change InputLayout(string text, MemberScan.ClassInfo cls, string eol, bool header, out string why)
        {
            why = null;
            if (cls.Members.Count == 0) { why = "データ メンバーがありません"; return null; }
            string arrName = "k" + cls.Name + "InputLayout";
            if (text.Contains(arrName)) { why = arrName + " はすでにあります"; return null; }
            var rows = new List<string>();
            var hlsl = new List<string>();
            var count = new Dictionary<string, int>();
            foreach (var mem in cls.Members)
            {
                var vt = VertexType(mem.Type);
                if (vt == null || mem.Array.Length > 0) { why = mem.Type + " " + mem.Name + mem.Array + " は、頂点の要素にできる型ではありません (float、XMFLOAT2〜4、Vector2〜4、uint32_t などにしてください)"; return null; }
                string sem = Semantic(mem.Name);
                int idx;
                count.TryGetValue(sem, out idx);
                count[sem] = idx + 1;
                rows.Add("{\"" + sem + "\", " + idx + ", DXGI_FORMAT_" + vt.Format + ", 0, offsetof(" + cls.FullName + ", " + mem.Name + "), {CLASS}, 0},");
                string ht = vt.Format.EndsWith("UINT") ? "uint" : vt.Format.EndsWith("SINT") ? "int" : "float";
                hlsl.Add(ht + (vt.Comp > 1 ? vt.Comp.ToString() : "") + " " + mem.Name.Trim('_') + " : " + sem + (idx > 0 || sem == "TEXCOORD" ? idx.ToString() : "") + ";");
            }
            // D3D12 の #include があれば D3D12、なければ D3D11
            bool d12 = Regex.IsMatch(text, @"#\s*include\s*[<""]d3d12") || (!Regex.IsMatch(text, @"#\s*include\s*[<""]d3d11") && Regex.IsMatch(text, @"\bD3D12_|\bID3D12"));
            string api = d12 ? "D3D12" : "D3D11";
            // D3D11 は D3D11_INPUT_PER_VERTEX_DATA、D3D12 は D3D12_INPUT_CLASSIFICATION_PER_VERTEX_DATA(名前が違う)
            string cls12 = d12 ? "D3D12_INPUT_CLASSIFICATION_PER_VERTEX_DATA" : "D3D11_INPUT_PER_VERTEX_DATA";
            var sb = new StringBuilder();
            sb.Append(eol).Append(eol);
            sb.Append(header ? "inline constexpr " : "constexpr ").Append(api).Append("_INPUT_ELEMENT_DESC ").Append(arrName).Append("[] = {").Append(eol);
            foreach (string r in rows) sb.Append(CppText.IndentUnit(text)).Append(r.Replace("{CLASS}", cls12)).Append(eol);
            sb.Append("};");
            // 構造体のすぐ後ろ(同じ namespace の中)。入れ子の構造体なら、一番外のクラスの後ろ
            var top = cls.Scope;
            while (top.Parent != null && top.Parent.IsClass) top = top.Parent;
            int after = AfterClass(text, new MemberScan.ClassInfo { Scope = top });
            var ch = new Refactor.Change().Add(after, 0, sb.ToString().Replace(eol, eol + MemberScan.Indent(text, top.Close)).Replace(eol + MemberScan.Indent(text, top.Close) + eol, eol + eol));
            Refactor.AddInclude(ch, text, "<cstddef>", eol);
            ch.Message = arrName + " を作りました (" + api + "、要素 " + rows.Count + " 個)";
            return ch;
        }

        // ---- 定数バッファの並び ----

        private sealed class CbType { public int Size; public int Align; public bool Matrix; public string Error; }

        private static CbType CbTypeOf(string type)
        {
            string t = Regex.Replace(type, @"^(?:const\s+)|(?:DirectX::|SimpleMath::|DirectX::SimpleMath::)", "").Trim();
            switch (t)
            {
                case "float": case "int": case "uint32_t": case "int32_t": case "UINT": case "INT": case "DWORD": case "BOOL": case "unsigned int": case "std::uint32_t": case "std::int32_t":
                    return new CbType { Size = 4, Align = 4 };
                case "XMFLOAT2": case "XMINT2": case "XMUINT2": case "Vector2": return new CbType { Size = 8, Align = 4 };
                case "XMFLOAT3": case "XMINT3": case "XMUINT3": case "Vector3": return new CbType { Size = 12, Align = 4 };
                case "XMFLOAT4": case "XMINT4": case "XMUINT4": case "Vector4": case "Color": case "Quaternion": return new CbType { Size = 16, Align = 4 };
                case "XMVECTOR": return new CbType { Size = 16, Align = 16 };
                case "XMFLOAT4X4": case "Matrix": return new CbType { Size = 64, Align = 4, Matrix = true };
                case "XMMATRIX": return new CbType { Size = 64, Align = 16, Matrix = true };
                case "bool": return new CbType { Error = "bool は C++ で 1 バイト、HLSL で 4 バイトです。uint32_t か BOOL にしてください" };
                case "XMFLOAT3X3": return new CbType { Error = "XMFLOAT3X3 は HLSL の float3x3 と並びが違います (HLSL は行ごとに 16 バイト)。XMFLOAT4X4 か XMFLOAT3X4 にしてください" };
                case "double": return new CbType { Error = "double は、定数バッファではほとんど使いません。float にしてください" };
            }
            return null;
        }

        private static Refactor.Change CBuffer(string text, MemberScan.ClassInfo cls, string eol, out string why)
        {
            why = null;
            if (cls.Members.Count == 0) { why = "データ メンバーがありません"; return null; }
            // HLSL の規則: 1 つのメンバーは 16 バイトの境界をまたがない。配列と行列は 16 バイトの境界から始まり、
            // 配列の要素はどれも 16 バイトの境界から始まる(最後の要素の後ろは詰める)。
            int cpp = 0, hlsl = 0, padNo = 0;
            var names = new HashSet<string>(cls.Members.Select(x => x.Name));
            var ch = new Refactor.Change();
            var inserted = new List<string>();
            foreach (var mem in cls.Members)
            {
                var t = CbTypeOf(mem.Type);
                if (t == null) { why = mem.Type + " " + mem.Name + " の大きさが分かりません (float、XMFLOAT2〜4、XMFLOAT4X4、uint32_t などにしてください)"; return null; }
                if (t.Error != null) { why = mem.Name + ": " + t.Error; return null; }
                int n = 1;
                if (mem.Array.Length > 0)
                {
                    Match a = Regex.Match(mem.Array, @"^\[(\d+)\]$");
                    if (!a.Success) { why = mem.Name + mem.Array + " の要素数が分かりません (数で書いた 1 次元の配列だけ)"; return null; }
                    n = int.Parse(a.Groups[1].Value);
                    if (t.Size % 16 != 0 && n > 1) { why = mem.Name + mem.Array + ": HLSL の配列は要素ごとに 16 バイトに広がるので、" + mem.Type + " の配列は並びが合いません。XMFLOAT4 の配列にしてください"; return null; }
                }
                int start;
                if (mem.Array.Length > 0 || t.Matrix) start = Up16(hlsl);
                else start = (hlsl % 16) + t.Size > 16 ? Up16(hlsl) : hlsl;
                int cppStart = (cpp + t.Align - 1) / t.Align * t.Align;
                if (cppStart > start) { why = mem.Name + " の C++ の位置 (" + cppStart + ") が HLSL の位置 (" + start + ") より後ろです。XMVECTOR・XMMATRIX の前を 16 バイトにそろえてください"; return null; }
                if (start > cppStart)
                {
                    int floats = (start - cppStart) / 4;
                    string pn; do { pn = "pad" + padNo++; } while (names.Contains(pn));
                    string decl = "float " + pn + (floats > 1 ? "[" + floats + "]" : "") + ";";
                    inserted.Add(mem.Name + " の前に " + (floats * 4) + " バイト");
                    ch.Add(MemberScan.LineStart(text, mem.Start), 0, MemberScan.Indent(text, mem.Start) + decl + eol);
                    cppStart = start;
                }
                cpp = cppStart + t.Size * n;
                hlsl = start + (n > 1 ? 16 * (n - 1) + t.Size : t.Size);
                // 同じ行の「float x, y;」は、行の前に詰め物を入れられない
                if (cls.Members.Count(o => o.Start == mem.Start) > 1 && ch.Edits.Any(e => e.Item1 == MemberScan.LineStart(text, mem.Start)))
                { why = "1 行に複数のメンバーがある所に詰め物が要ります。1 行 1 メンバーにしてください"; return null; }
            }
            int total = Up16(Math.Max(hlsl, cpp));
            var last = cls.Members[cls.Members.Count - 1];
            if (total > cpp)
            {
                int floats = (total - cpp) / 4;
                string pn; do { pn = "pad" + padNo++; } while (names.Contains(pn));
                inserted.Add("末尾に " + (floats * 4) + " バイト");
                ch.Add(MemberScan.LineEnd(text, last.End), 0, eol + MemberScan.Indent(text, last.Start) + "float " + pn + (floats > 1 ? "[" + floats + "]" : "") + ";");
            }
            string assert = "static_assert(sizeof(" + cls.Name + ") % 16 == 0, \"定数バッファの大きさは 16 の倍数にする\");";
            if (!text.Contains("sizeof(" + cls.Name + ") % 16"))
            {
                int after = AfterClass(text, cls);
                ch.Add(after, 0, eol + MemberScan.Indent(text, cls.Scope.Close) + assert);
            }
            if (ch.Edits.Count == 0) { why = cls.Name + " の並びは、HLSL と同じです (" + total + " バイト)"; return null; }
            ch.Message = inserted.Count == 0 ? cls.Name + " の並びは HLSL と同じです。static_assert だけ足しました (" + total + " バイト)"
                : cls.Name + " に詰め物を足しました (" + string.Join("、", inserted) + "。全体 " + total + " バイト)";
            return ch;
        }

        private static int Up16(int x) { return (x + 15) / 16 * 16; }

        private static int AfterClass(string text, MemberScan.ClassInfo cls)
        {
            string m = CppText.Mask(text);
            int semi = m.IndexOf(';', cls.Scope.Close);
            return semi < 0 ? cls.Scope.Close + 1 : semi + 1;
        }

        // ---- 初期化子リストの並べ替え ----

        /// <summary>
        /// コンストラクターの初期化子リストを、メンバーの宣言の順に並べる(C5038 / -Wreorder の警告を消す)。
        /// 基底クラス(メンバーでない名前)は先頭のまま。classText は、クラスの宣言のある文字(null なら text)。
        /// </summary>
        public static Refactor.Change InitOrder(string text, int caret, string classText, out string why)
        {
            why = null;
            var sig = FunctionScan.Scan(text).FirstOrDefault(s => s.InitStart >= 0 && s.HasBody && s.PrefixStart <= caret && caret <= s.BodyOpen);
            if (sig == null) { why = "カーソルが、初期化子リストのあるコンストラクターの上にありません"; return null; }
            string ct = classText ?? text;
            string cname = sig.Class ?? sig.Name;
            var scope = Scopes.Parse(ct).Where(s => s.IsClass && s.Name == cname).OrderBy(s => sig.InClass ? Math.Abs(s.Open - sig.Open) : 0).FirstOrDefault();
            if (scope == null) { why = "クラス " + cname + " の宣言が見つかりません"; return null; }
            var order = MemberScan.Of(ct, scope).Members.Select(x => x.Name).ToList();
            string m = CppText.Mask(text);
            int from = sig.InitStart + 1, to = sig.BodyOpen;
            // 初期化子は「name(…)」か「name{…}」。「,」で分ける
            var items = new List<Tuple<int, int>>();
            int st = from, depth = 0;
            for (int i = from; i < to; i++)
            {
                char c = m[i];
                if (c == '(' || c == '{' || c == '[' || c == '<') depth++;
                else if (c == ')' || c == '}' || c == ']' || c == '>') depth--;
                else if (c == ',' && depth == 0) { items.Add(Tuple.Create(st, i)); st = i + 1; }
            }
            items.Add(Tuple.Create(st, to));
            var parsed = items.Select(it =>
            {
                string raw = text.Substring(it.Item1, it.Item2 - it.Item1).Trim();
                Match nm = Regex.Match(CppText.Mask(raw), @"^([A-Za-z_][\w:<>]*)\s*[({]");
                return new { Raw = raw, Name = nm.Success ? nm.Groups[1].Value : null };
            }).ToList();
            if (parsed.Any(p => p.Name == null)) { why = "初期化子リストを読めません"; return null; }
            var sorted = parsed.Select((p, i) => new { p.Raw, p.Name, I = i, Key = order.IndexOf(p.Name) })
                .OrderBy(p => p.Key < 0 ? -1 : 1).ThenBy(p => p.Key < 0 ? p.I : p.Key).ToList();
            if (sorted.Select(p => p.I).SequenceEqual(Enumerable.Range(0, parsed.Count))) { why = "初期化子リストは、すでに宣言の順です"; return null; }
            // 2 つ目の初期化子が行の頭にあれば(1 行に 1 つずつ書いてあれば)、その字下げで並べ直す
            int second = items[1].Item1;
            while (second < to && char.IsWhiteSpace(text[second]) && text[second] != '\n') second++;
            if (second < to && text[second] == '\n') { second++; while (second < to && (text[second] == ' ' || text[second] == '\t')) second++; }
            bool perLine = text.Substring(MemberScan.LineStart(text, second), second - MemberScan.LineStart(text, second)).Trim().Length == 0
                && MemberScan.LineStart(text, second) > MemberScan.LineStart(text, from);
            string eolS = CppText.Eol(text);
            string sep = perLine ? "," + eolS + MemberScan.Indent(text, second) : ", ";
            // 先頭の「:」の後ろの空白と、本体の「{」の前の空白は、元のまま残す
            string region = text.Substring(from, to - from);
            string lead = region.Substring(0, region.Length - region.TrimStart().Length);
            string trail = region.Substring(region.TrimEnd().Length);
            string res = lead + string.Join(sep, sorted.Select(p => p.Raw)) + trail;
            var ch = new Refactor.Change().Add(from, to - from, res);
            ch.Message = "初期化子リストを、メンバーの宣言の順に並べ替えました (初期化は、書いた順ではなく宣言の順に行われます)";
            return ch;
        }

        // ---- Natvis ----

        /// <summary>デバッガーの 1 行表示(DisplayString)。public・private を問わず、先頭から 4 つまでのメンバー。</summary>
        public static string NatvisType(MemberScan.ClassInfo cls)
        {
            var ms = cls.Members.Take(4).ToList();
            string disp = "{{" + string.Join(", ", ms.Select(x => x.Name + "={" + x.Name + "}")) + (cls.Members.Count > 4 ? ", ..." : "") + "}}";
            return "  <Type Name=\"" + cls.FullName + "\">\n    <DisplayString>" + Xml(disp) + "</DisplayString>\n  </Type>";
        }

        private static string Xml(string s) { return s.Replace("&", "&amp;").Replace("<", "&lt;").Replace(">", "&gt;"); }

        /// <summary>natvis の文字(なければ null)に、型の項目を足すか、同じ名前の項目を置き換える。</summary>
        public static string NatvisMerge(string existing, string typeName, string entry, string eol)
        {
            entry = entry.Replace("\n", eol);
            if (string.IsNullOrEmpty(existing))
                return "<?xml version=\"1.0\" encoding=\"utf-8\"?>" + eol
                    + "<!-- K-CppUltimateAssist が作った。デバッガーのウォッチ・ホバーで、型を 1 行で見せる -->" + eol
                    + "<AutoVisualizer xmlns=\"http://schemas.microsoft.com/vstudio/debugger/natvis/2010\">" + eol
                    + entry + eol + "</AutoVisualizer>" + eol;
            var rx = new Regex(@"[ \t]*<Type\s+Name=""" + Regex.Escape(typeName) + @"""[\s\S]*?</Type>");
            if (rx.IsMatch(existing)) return rx.Replace(existing, entry.Replace("$", "$$"), 1);
            int end = existing.LastIndexOf("</AutoVisualizer>", StringComparison.Ordinal);
            if (end < 0) return null;
            return existing.Substring(0, end) + entry + eol + existing.Substring(end);
        }
    }
}
