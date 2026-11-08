using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.RegularExpressions;

namespace KCppAssist
{
    /// <summary>クラスの本体のどこに、メンバーの宣言をまとめて入れるか。VS に依存しない。</summary>
    internal static class ClassPlace
    {
        /// <summary>本体の直下だけを残した文字。入れ子の { ... } は、「;」と空白に置き換える(位置と長さは、元と同じ)。</summary>
        public static string Depth0(string m, int open, int close)
        {
            var sb = new System.Text.StringBuilder(m.Substring(open + 1, close - open - 1));
            int depth = 0, start = -1;
            for (int i = 0; i < sb.Length; i++)
            {
                char c = sb[i];
                if (c == '{') { if (depth++ == 0) start = i; }
                else if (c == '}')
                {
                    if (--depth == 0 && start >= 0)
                    {
                        for (int k = start; k <= i; k++) if (sb[k] != '\n' && sb[k] != '\r') sb[k] = ' ';
                        sb[start] = ';';
                    }
                    if (depth < 0) depth = 0;
                }
                else if (depth > 0 && c != '\n' && c != '\r') sb[i] = ' ';
            }
            return sb.ToString();
        }

        private static readonly Regex Label = new Regex(@"(?<![:\w])(public|private|protected)\s*:(?!:)", RegexOptions.Compiled);

        /// <summary>block(宣言の並び。末尾は改行)を入れる位置と、実際に入れる文字。</summary>
        public static void Insert(string text, string m, Scopes.Scope cls, string block, string eol, out int pos, out string outText)
        {
            string d0 = Depth0(m, cls.Open, cls.Close);
            int off = cls.Open + 1;
            int firstPublicEnd = -1, firstLabelStart = -1;
            foreach (Match x in Label.Matches(d0))
            {
                if (firstLabelStart < 0) firstLabelStart = off + x.Index;
                if (x.Groups[1].Value == "public" && firstPublicEnd < 0) firstPublicEnd = off + x.Index + x.Length;
            }
            string classIndent = ClassIndent(text, cls);
            string labelIndent = firstLabelStart >= 0 ? LeadingSpace(text, firstLabelStart) : classIndent + " ";

            if (firstPublicEnd >= 0)
            {
                pos = NextLineStart(text, firstPublicEnd);
                outText = block + eol;
            }
            else if (cls.IsStruct)
            {
                pos = NextLineStart(text, cls.Open);
                outText = block + eol;
            }
            else
            {
                bool startsWithLabel = firstLabelStart >= 0 && text.Substring(cls.Open + 1, firstLabelStart - cls.Open - 1).Trim().Length == 0;
                if (startsWithLabel)
                {
                    pos = LineStart(text, firstLabelStart);
                    outText = labelIndent + "public:" + eol + block + eol;
                }
                else
                {
                    pos = NextLineStart(text, cls.Open);
                    outText = labelIndent + "public:" + eol + block + eol + labelIndent + "private:" + eol;
                }
            }
        }

        /// <summary>メンバーの字下げ。いまの最初のメンバー(ラベルでない最初の行)に合わせる。なければ、クラスの字下げ + 2。</summary>
        public static string MemberIndent(string text, string m, Scopes.Scope cls)
        {
            string classIndent = ClassIndent(text, cls);
            int p = NextLineStart(text, cls.Open);
            while (p < cls.Close)
            {
                int e = text.IndexOf('\n', p);
                if (e < 0 || e > cls.Close) e = cls.Close;
                string line = text.Substring(p, e - p);
                string t = line.Trim();
                if (t.Length > 0 && !Regex.IsMatch(m.Substring(p, e - p), @"^\s*(?:public|private|protected)\s*:\s*$") && m.Substring(p, e - p).Trim().Length > 0)
                {
                    string ind = LeadingSpace(text, p);
                    if (ind.Length > classIndent.Length) return ind;
                }
                p = e + 1;
            }
            return classIndent + "  ";
        }

        public static string ClassIndent(string text, Scopes.Scope cls)
        {
            int ls = LineStart(text, cls.Open);
            string ci = LeadingSpace(text, cls.Open);
            if (text.Substring(ls, cls.Open - ls).Trim().Length == 0 && ls > 1)
                ci = LeadingSpace(text, ls - 2);   // 「{」だけの行(Allman): クラス名の行の字下げ
            return ci;
        }

        public static int LineStart(string text, int pos)
        {
            int i = Math.Min(pos, text.Length);
            while (i > 0 && text[i - 1] != '\n') i--;
            return i;
        }

        public static int NextLineStart(string text, int pos)
        {
            int i = text.IndexOf('\n', Math.Min(pos, text.Length));
            return i < 0 ? text.Length : i + 1;
        }

        public static string LeadingSpace(string text, int pos)
        {
            int ls = LineStart(text, pos);
            int e = ls;
            while (e < text.Length && (text[e] == ' ' || text[e] == '\t')) e++;
            return text.Substring(ls, e - ls);
        }
    }
}
