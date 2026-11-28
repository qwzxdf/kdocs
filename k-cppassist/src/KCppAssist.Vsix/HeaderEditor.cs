using System;
using System.Collections.Generic;
using System.Text;
using System.Text.RegularExpressions;

namespace KCppAssist
{
    /// <summary>定数(static constexpr)を、区画のどこに置くか。</summary>
    public enum ConstantPlacement { AfterTypes, SectionTop, BeforeMembers }

    /// <summary>クラスの宣言(ヘッダーの文字)を探し、メンバー変数を足す場所と文字を決める。VS に依存しない。</summary>
    internal static class HeaderEditor
    {
        public sealed class Edit
        {
            public int Position;
            public string Text;
        }

        /// <summary>class / struct の定義を探して、メンバー 1 行を入れる編集を返す。見つからなければ null。</summary>
        public static Edit Plan(string text, string className, string declaration, string eol)
        {
            var m = Regex.Match(text, @"\b(class|struct)\s+(?:[A-Za-z_]\w*\s+)*?" + Regex.Escape(className) + @"\b[^;{]*\{");
            if (!m.Success) return null;
            return PlanAt(text, m.Index + m.Length - 1, declaration, eol);
        }

        /// <summary>open の「{」で始まるクラスの本体の末尾に、メンバー 1 行を入れる編集を返す。</summary>
        public static Edit PlanAt(string text, int open, string declaration, string eol)
        {
            var old = PlanAtCore(text, open, declaration, eol);
            // 末尾の private: に、メンバー変数より後ろへ関数を足すときは、メンバー変数の前に置く(並びは 関数 → メンバー変数)
            if (old != null && declaration.IndexOf('\n') < 0 && declaration.Contains("("))
            {
                string head = CppText.Mask(text).Substring(0, open);
                bool isStruct = Regex.IsMatch(head.Substring(Math.Max(0, head.LastIndexOfAny(new[] { ';', '{', '}' }) + 1)), @"\bstruct\b");
                var rk = DefinitionGen.TryPlanRanked(text, open, isStruct, new[] { new DefinitionGen.Item { Rank = DefinitionGen.RankOf(declaration, DefinitionGen.ClassNameAt(text, open)), Text = declaration } }, eol, "private");
                if (rk != null && rk.Count == 1 && rk[0].Position < old.Position) return new Edit { Position = rk[0].Position, Text = rk[0].Text };
            }
            return old;
        }

        private static Edit PlanAtCore(string text, int open, string declaration, string eol)
        {
            int close = AccessorEditor.FindClose(text, open);
            if (close < 0) return null;

            // クラスの直下にある、最後のアクセス指定子
            var labels = ClassPlace.Labels(CppText.Mask(text), open, close);
            string lastSpec = labels.Count > 0 ? labels[labels.Count - 1].Name : null;

            // 閉じ括弧の行の頭
            int lineStart = close;
            while (lineStart > 0 && text[lineStart - 1] != '\n') lineStart--;
            bool braceFirst = text.Substring(lineStart, close - lineStart).Trim().Length == 0;
            string closeIndent = braceFirst ? text.Substring(lineStart, close - lineStart) : "";

            // メンバーの字下げは、閉じ括弧の直前にある行(アクセス指定子以外)に合わせる。なければ、ファイルの字下げ 1 段
            string unit = CppText.IndentUnit(text);
            string memberIndent = closeIndent + unit;
            int prevEnd = lineStart - 1;
            while (braceFirst && prevEnd > open)
            {
                int prevStart = prevEnd;
                while (prevStart > 0 && text[prevStart - 1] != '\n') prevStart--;
                string prev = text.Substring(prevStart, prevEnd - prevStart).TrimEnd('\r');
                prevEnd = prevStart - 1;
                if (prev.Trim().Length == 0) continue;
                if (Regex.IsMatch(prev, @"^\s*(public|protected|private)\s*:")) break;
                string indent = prev.Substring(0, prev.Length - prev.TrimStart().Length);
                if (indent.Length > closeIndent.Length) memberIndent = indent;
                break;
            }

            var sb = new StringBuilder();
            // private: が最後なら、その下に足す。そうでなければ、末尾に private: を作る。
            // ただし、指定子のない struct(全部 public の集成体)には作らない。private を混ぜると Vertex v{1, 2}; が書けなくなる
            int headFrom = Math.Max(0, text.LastIndexOfAny(new[] { ';', '{', '}' }, Math.Max(0, open - 1)) + 1);
            bool isStruct = Regex.IsMatch(text.Substring(headFrom, open - headFrom), @"\bstruct\b");
            bool needSpec = lastSpec != "private" && !(isStruct && lastSpec == null);
            if (needSpec)
            {
                // 指定子の位置とメンバーの字下げは、ファイルの書き方に合わせる(Google なら「 private:」と 2 字、VS の既定なら「private:」とタブ)
                memberIndent = closeIndent + unit;
                sb.Append(eol).Append(closeIndent).Append(CppText.LabelOffset(text)).Append("private:").Append(eol);
            }
            sb.Append(memberIndent).Append(declaration).Append(eol);
            return new Edit
            {
                Position = braceFirst ? lineStart : close,
                Text = braceFirst ? sb.ToString() : eol + sb.ToString(),
            };
        }

        /// <summary>
        /// open の「{」で始まるクラスに、メンバー変数か定数(static constexpr)を 1 行足す編集を返す。
        /// access は "public" か "private"。置き場所は、その指定子の最後の区画の中で、並び順(型 → 定数 → コンストラクター → 関数 → メンバー変数)を守る位置。
        /// その指定子の区画がなければ、public はクラスの先頭、private はクラスの末尾に、指定子ごと作る。空行は、前後の宣言と種類が違うときだけ入れる。
        /// </summary>
        public static Edit PlanMember(string text, int open, string access, bool constant, string declaration, string eol, ConstantPlacement placement = ConstantPlacement.AfterTypes)
        {
            string m = CppText.Mask(text);
            int close = Scopes.MatchBrace(m, open);
            if (close < 0) return null;
            string head = m.Substring(0, open);
            bool isStruct = Regex.IsMatch(head.Substring(Math.Max(0, head.LastIndexOfAny(new[] { ';', '{', '}' }) + 1)), @"\bstruct\b");

            var ranked = DefinitionGen.TryPlanRanked(text, open, isStruct,
                new[] { MakeItem(constant, placement, declaration) }, eol, access);
            if (ranked != null && ranked.Count == 1) return new Edit { Position = ranked[0].Position, Text = ranked[0].Text };

            var specs = ClassPlace.Labels(m, open, close);

            int lineStart = close;
            while (lineStart > 0 && text[lineStart - 1] != '\n') lineStart--;
            bool braceFirst = text.Substring(lineStart, close - lineStart).Trim().Length == 0;
            string closeIndent = braceFirst ? text.Substring(lineStart, close - lineStart) : "";
            string unit = CppText.IndentUnit(text);
            string memberIndent = closeIndent + unit;
            string label = closeIndent + CppText.LabelOffset(text);

            int idx = specs.FindLastIndex(x => x.Name == access);
            if (idx >= 0)
            {
                // 指定子はあるが、中身が空。指定子の行の下に入れる。すぐ次が別の指定子なら、空行で分ける
                int at = specs[idx].End;
                while (at < text.Length && text[at] != '\n' && text[at] != '\r') at++;
                var sb2 = new StringBuilder();
                sb2.Append(eol).Append(memberIndent).Append(declaration);
                if (idx + 1 < specs.Count)
                {
                    int nextLine = specs[idx + 1].Start;
                    while (nextLine > 0 && text[nextLine - 1] != '\n') nextLine--;
                    string gap = text.Substring(at, Math.Max(0, nextLine - at));
                    if (!Regex.IsMatch(gap, @"\n[ \t]*\r?\n")) sb2.Append(eol);
                }
                return new Edit { Position = at, Text = sb2.ToString() };
            }

            if (access == "public")
            {
                // public: がない。クラスの先頭に作る。もともとのメンバー(指定子なしの class では private)が続くなら、private: を足して private のまま残す
                int nlOpen = text.IndexOf('\n', open);
                if (braceFirst && nlOpen > open && nlOpen < close && m.Substring(open + 1, nlOpen - open - 1).Trim().Length == 0)
                {
                    int firstSpec = specs.Count > 0 ? specs[0].Start : close;
                    bool implicitPrivate = m.Substring(open + 1, firstSpec - open - 1).Trim().Length > 0;
                    bool hasBody = m.Substring(open + 1, close - open - 1).Trim().Length > 0;
                    var top = new StringBuilder();
                    top.Append(label).Append("public:").Append(eol).Append(memberIndent).Append(declaration).Append(eol);
                    if (implicitPrivate) top.Append(eol).Append(label).Append("private:").Append(eol);
                    else if (hasBody) top.Append(eol);
                    return new Edit { Position = nlOpen + 1, Text = top.ToString() };
                }
                var one = new StringBuilder();
                one.Append(eol).Append(closeIndent).Append(CppText.LabelOffset(text)).Append("public:").Append(eol).Append(memberIndent).Append(declaration).Append(eol);
                return new Edit { Position = braceFirst ? lineStart : close, Text = braceFirst ? one.ToString() : eol + one.ToString() };
            }

            // private: がない。クラスの末尾に作る。直前に宣言があって空行がなければ、空行を 1 行入れる
            int insertAt = braceFirst ? lineStart : close;
            string before = text.Substring(open + 1, insertAt - open - 1);
            bool hasContent = before.Trim().Length > 0;
            bool blankBefore = Regex.IsMatch(before, @"\n[ \t]*\r?\n[ \t]*\z");
            var sb = new StringBuilder();
            if (!braceFirst) sb.Append(eol);
            else if (hasContent && !blankBefore) sb.Append(eol);
            sb.Append(label).Append("private:").Append(eol).Append(memberIndent).Append(declaration).Append(eol);
            return new Edit { Position = insertAt, Text = sb.ToString() };
        }

        private static DefinitionGen.Item MakeItem(bool constant, ConstantPlacement placement, string declaration)
        {
            if (!constant) return new DefinitionGen.Item { Rank = 5, Text = declaration };
            switch (placement)
            {
                case ConstantPlacement.SectionTop: return new DefinitionGen.Item { Rank = -2, Text = declaration };            // 区画の先頭(型・using よりも前)
                case ConstantPlacement.BeforeMembers: return new DefinitionGen.Item { Rank = 5, Before = true, Text = declaration };   // メンバー変数の直前
                default: return new DefinitionGen.Item { Rank = -1, Text = declaration };                                        // 型・using の直後
            }
        }
    }
}
