using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Globalization;

namespace KCppAssist
{
    /// <summary>画面に出す言語。設定の「表示する言語」。</summary>
    public enum UiLanguage { Japanese, English, ChineseSimplified, Korean, Spanish, Portuguese, German, French, Russian }

    /// <summary>
    /// 画面の文字の翻訳。日本語の原文をそのまま鍵にして、各言語の訳を引く。訳は Lang/strings.tsv に書き、tools/lang_gen.py で LangData.cs にする。
    /// 表にない文字や、その言語の欄が空の文字は、英語があれば英語、なければ日本語のまま出す(訳していない所が空にならないように)。
    /// 文の途中に名前が入るものは、F の「{0}」で書く(語順が言語ごとに違うため、文字列をつないで作らない)。
    /// </summary>
    internal static class L
    {
        /// <summary>いまの言語。設定を読んだとき・変えたときに、パッケージが入れる。</summary>
        public static volatile UiLanguage Current = UiLanguage.Japanese;

        public static string T(string ja)
        {
            if (string.IsNullOrEmpty(ja) || Current == UiLanguage.Japanese) return ja;
            string[] row;
            if (!LangData.Rows.TryGetValue(ja, out row)) return ja;
            int i = Column(Current);
            if (i >= 0 && i < row.Length && !string.IsNullOrEmpty(row[i])) return row[i];
            return string.IsNullOrEmpty(row[0]) ? ja : row[0];          // 英語にする
        }

        public static string F(string jaFormat, params object[] args)
        {
            try { return string.Format(T(jaFormat), args); }
            catch (FormatException) { return string.Format(jaFormat, args); }
        }

        // 文字コードの表などで、決まった言い回しを組み合わせた文を訳すための部品(長いものから順に置き換える)
        private static readonly string[] PhraseKeys =
        {
            "読めない (バイナリか、どの文字コードでもない)", "Shift-JIS にない文字があるので変換しない: ", "大きすぎるので飛ばす (8 MB 超)",
            "未保存なので飛ばす", "UTF-8 (BOM なし)", "UTF-8 (BOM 付き)", "変換しました", "ASCII のみ", "読めない: ", "失敗: ",
            "バイナリ?", "そのまま", "改行 ", "混在", "なし", "、",
        };

        /// <summary>決まった言い回しを組み合わせた文(「UTF-8 (BOM なし) → UTF-8 (BOM 付き)、改行 LF → CRLF」など)を、言い回しごとに訳す。</summary>
        public static string Phrases(string s)
        {
            if (string.IsNullOrEmpty(s) || Current == UiLanguage.Japanese) return s;
            string whole = T(s);
            if (whole != s) return whole;
            foreach (string k in PhraseKeys) if (s.Contains(k)) s = s.Replace(k, T(k));
            return s;
        }

        /// <summary>LangData の列の番号(英語が 0)。日本語は -1。</summary>
        public static int Column(UiLanguage lang)
        {
            string code;
            switch (lang)
            {
                case UiLanguage.English: code = "en"; break;
                case UiLanguage.ChineseSimplified: code = "zh"; break;
                case UiLanguage.Korean: code = "ko"; break;
                case UiLanguage.Spanish: code = "es"; break;
                case UiLanguage.Portuguese: code = "pt"; break;
                case UiLanguage.German: code = "de"; break;
                case UiLanguage.French: code = "fr"; break;
                case UiLanguage.Russian: code = "ru"; break;
                default: return -1;
            }
            return Array.IndexOf(LangData.Columns, code);
        }

        /// <summary>PC(Windows)の表示言語から決める。表にない言語は英語。</summary>
        public static UiLanguage FromCulture(CultureInfo c)
        {
            string n = c == null ? "" : c.Name.ToLowerInvariant();
            if (n.StartsWith("ja")) return UiLanguage.Japanese;
            if (n.StartsWith("zh")) return UiLanguage.ChineseSimplified;
            if (n.StartsWith("ko")) return UiLanguage.Korean;
            if (n.StartsWith("es")) return UiLanguage.Spanish;
            if (n.StartsWith("pt")) return UiLanguage.Portuguese;
            if (n.StartsWith("de")) return UiLanguage.German;
            if (n.StartsWith("fr")) return UiLanguage.French;
            if (n.StartsWith("ru")) return UiLanguage.Russian;
            return UiLanguage.English;
        }

    }

    /// <summary>設定の画面の分類名を、いまの言語で出す(VS は、最初に読んだときの値を覚えるので、言語を変えたら VS を開き直す)。</summary>
    internal sealed class LocCategoryAttribute : CategoryAttribute
    {
        public LocCategoryAttribute(string ja) : base(ja) { }
        protected override string GetLocalizedString(string value) { return L.T(value); }
    }

    internal sealed class LocDisplayNameAttribute : DisplayNameAttribute
    {
        public LocDisplayNameAttribute(string ja) : base(ja) { }
        public override string DisplayName { get { return L.T(DisplayNameValue); } }
    }

    internal sealed class LocDescriptionAttribute : DescriptionAttribute
    {
        public LocDescriptionAttribute(string ja) : base(ja) { }
        public override string Description { get { return L.T(DescriptionValue); } }
    }
}
