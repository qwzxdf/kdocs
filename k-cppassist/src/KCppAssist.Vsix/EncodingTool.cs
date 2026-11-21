using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;

namespace KCppAssist
{
    /// <summary>
    /// ファイルの文字コードと改行を調べて、そろえる。VS に依存しない(画面は KCppAssistPackage.Encoding.cs)。
    /// 文字コードの決め方は RenameSync.ReadKeepingEncoding と同じ: BOM、厳密な UTF-8、どちらでもなければシフト JIS(932)。
    /// </summary>
    internal static class EncodingTool
    {
        public enum Kind { Ascii, Utf8, Utf8Bom, ShiftJis, Utf16LE, Utf16BE, Binary }

        public enum Target { Utf8Bom, Utf8, ShiftJis }

        public enum Eol { Keep, Crlf, Lf }

        public sealed class Info
        {
            public Kind Kind;
            public string Text;         // 読んだ文字(Binary のときは null)
            public string EolName;      // CRLF / LF / CR / 混在 / なし
        }

        public sealed class Plan
        {
            public Info Before;
            public byte[] NewBytes;     // 書き換えが要らなければ null
            public string Action;       // 一覧に出す「すること」
            public bool Blocked;        // 変換できない(Shift-JIS にない文字、バイナリ)
        }

        private static readonly Encoding Sjis = Encoding.GetEncoding(932, EncoderFallback.ExceptionFallback, DecoderFallback.ExceptionFallback);

        public static Info Detect(byte[] b)
        {
            var info = new Info();
            if (b.Length >= 3 && b[0] == 0xEF && b[1] == 0xBB && b[2] == 0xBF) { info.Kind = Kind.Utf8Bom; info.Text = new UTF8Encoding(false).GetString(b, 3, b.Length - 3); }
            else if (b.Length >= 2 && b[0] == 0xFF && b[1] == 0xFE) { info.Kind = Kind.Utf16LE; info.Text = new UnicodeEncoding(false, false).GetString(b, 2, b.Length - 2); }
            else if (b.Length >= 2 && b[0] == 0xFE && b[1] == 0xFF) { info.Kind = Kind.Utf16BE; info.Text = new UnicodeEncoding(true, false).GetString(b, 2, b.Length - 2); }
            else if (Array.IndexOf(b, (byte)0) >= 0) { info.Kind = Kind.Binary; info.EolName = "-"; return info; }
            else if (b.All(x => x < 0x80)) { info.Kind = Kind.Ascii; info.Text = Encoding.ASCII.GetString(b); }
            else
            {
                try { info.Text = new UTF8Encoding(false, true).GetString(b); info.Kind = Kind.Utf8; }
                catch (DecoderFallbackException)
                {
                    try { info.Text = Sjis.GetString(b); info.Kind = Kind.ShiftJis; }
                    catch (DecoderFallbackException) { info.Kind = Kind.Binary; info.EolName = "-"; return info; }
                }
            }
            info.EolName = EolOf(info.Text);
            return info;
        }

        public static string KindName(Kind k)
        {
            switch (k)
            {
                case Kind.Ascii: return "ASCII のみ";
                case Kind.Utf8: return "UTF-8 (BOM なし)";
                case Kind.Utf8Bom: return "UTF-8 (BOM 付き)";
                case Kind.ShiftJis: return "Shift-JIS";
                case Kind.Utf16LE: return "UTF-16 LE";
                case Kind.Utf16BE: return "UTF-16 BE";
                default: return "バイナリ?";
            }
        }

        public static string TargetName(Target t)
        {
            return t == Target.Utf8Bom ? "UTF-8 (BOM 付き)" : t == Target.Utf8 ? "UTF-8 (BOM なし)" : "Shift-JIS";
        }

        public static string EolOf(string text)
        {
            int crlf = 0, lf = 0, cr = 0;
            for (int i = 0; i < text.Length; i++)
            {
                if (text[i] == '\r') { if (i + 1 < text.Length && text[i + 1] == '\n') { crlf++; i++; } else cr++; }
                else if (text[i] == '\n') lf++;
            }
            int kinds = (crlf > 0 ? 1 : 0) + (lf > 0 ? 1 : 0) + (cr > 0 ? 1 : 0);
            if (kinds == 0) return "なし";
            if (kinds > 1) return "混在";
            return crlf > 0 ? "CRLF" : lf > 0 ? "LF" : "CR";
        }

        public static string ApplyEol(string text, Eol e)
        {
            if (e == Eol.Keep) return text;
            string lf = text.Replace("\r\n", "\n").Replace('\r', '\n');
            return e == Eol.Lf ? lf : lf.Replace("\n", "\r\n");
        }

        /// <summary>
        /// text を target の文字コードで書いたバイト列。Shift-JIS で書けない文字(絵文字、一部の記号、ハングルなど)があれば null で、
        /// その文字を lost に入れる(最大 8 個)。
        /// </summary>
        public static byte[] Encode(string text, Target target, List<string> lost)
        {
            if (target == Target.Utf8Bom) return new UTF8Encoding(true).GetPreamble().Concat(new UTF8Encoding(false).GetBytes(text)).ToArray();
            if (target == Target.Utf8) return new UTF8Encoding(false).GetBytes(text);
            try { return Sjis.GetBytes(text); }
            catch (EncoderFallbackException)
            {
                var seen = new HashSet<string>();
                for (int i = 0; i < text.Length; i++)
                {
                    string ch = char.IsHighSurrogate(text[i]) && i + 1 < text.Length ? text.Substring(i++, 2) : text[i].ToString();
                    try { Sjis.GetBytes(ch); }
                    catch (EncoderFallbackException) { if (seen.Add(ch) && lost != null && lost.Count < 8) lost.Add(ch); }
                }
                return null;
            }
        }

        /// <summary>target と eol にそろえるために、そのファイルをどうするか。</summary>
        public static Plan PlanFile(byte[] bytes, Target target, Eol eol)
        {
            var p = new Plan { Before = Detect(bytes) };
            if (p.Before.Kind == Kind.Binary) { p.Blocked = true; p.Action = "読めない (バイナリか、どの文字コードでもない)"; return p; }

            string text = ApplyEol(p.Before.Text, eol);
            bool eolChanges = text != p.Before.Text;
            bool encOk = Already(p.Before.Kind, target);
            if (encOk && !eolChanges) { p.Action = "そのまま"; return p; }

            var lost = new List<string>();
            byte[] nb = Encode(text, target, lost);
            if (nb == null) { p.Blocked = true; p.Action = "Shift-JIS にない文字があるので変換しない: " + string.Join(" ", lost); return p; }
            if (nb.SequenceEqual(bytes)) { p.Action = "そのまま"; return p; }
            p.NewBytes = nb;
            var parts = new List<string>();
            if (!encOk) parts.Add(KindName(p.Before.Kind) + " → " + TargetName(target));
            if (eolChanges) parts.Add("改行 " + p.Before.EolName + " → " + (eol == Eol.Lf ? "LF" : "CRLF"));
            p.Action = string.Join("、", parts);
            return p;
        }

        /// <summary>いまの文字コードが、すでに target か。ASCII だけのファイルは、BOM なし UTF-8 とも Shift-JIS とも同じバイト列になる。</summary>
        public static bool Already(Kind k, Target t)
        {
            switch (t)
            {
                case Target.Utf8Bom: return k == Kind.Utf8Bom;
                case Target.Utf8: return k == Kind.Utf8 || k == Kind.Ascii;
                default: return k == Kind.ShiftJis || k == Kind.Ascii;
            }
        }

        // ---- .editorconfig ----

        /// <summary>.editorconfig の charset の値。Shift-JIS は .editorconfig の規格にないので null。</summary>
        public static string CharsetValue(Target t)
        {
            return t == Target.Utf8Bom ? "utf-8-bom" : t == Target.Utf8 ? "utf-8" : null;
        }

        /// <summary>拡張子の一覧から、.editorconfig の節の見出し([*.{h,cpp}])を作る。</summary>
        public static string SectionHeader(IEnumerable<string> exts)
        {
            var list = exts.Select(e => e.Trim().TrimStart('*').TrimStart('.')).Where(e => e.Length > 0).Distinct(StringComparer.OrdinalIgnoreCase).ToList();
            if (list.Count == 0) return null;
            return list.Count == 1 ? "[*." + list[0] + "]" : "[*.{" + string.Join(",", list) + "}]";
        }

        private static readonly Regex SectionLine = new Regex(@"^\s*\[(.*)\]\s*$", RegexOptions.Compiled);
        private static readonly Regex KeyLine = new Regex(@"^\s*([A-Za-z_][\w\-]*)\s*=", RegexOptions.Compiled);

        /// <summary>
        /// existing(.editorconfig の中身。なければ空)に、header の節の charset と end_of_line を書いた文字を返す。
        /// 同じ見出しの節があれば、その中の charset / end_of_line を書き換え(なければ足し)、ほかの行はそのまま残す。なければ末尾に節を足す。
        /// 値が null のキーは書かない(charset に null なら、charset には触らない)。
        /// </summary>
        public static string UpdateEditorConfig(string existing, string header, string charset, string endOfLine, string eolText)
        {
            existing = existing ?? "";
            var lines = existing.Replace("\r\n", "\n").Split('\n').ToList();
            if (lines.Count > 0 && lines[lines.Count - 1].Length == 0) lines.RemoveAt(lines.Count - 1);
            var want = new List<KeyValuePair<string, string>>();
            if (charset != null) want.Add(new KeyValuePair<string, string>("charset", charset));
            if (endOfLine != null) want.Add(new KeyValuePair<string, string>("end_of_line", endOfLine));
            if (want.Count == 0) return existing;

            int start = lines.FindIndex(l => l.Trim() == header);
            if (start < 0)
            {
                if (lines.Count > 0 && lines[lines.Count - 1].Trim().Length > 0) lines.Add("");
                if (existing.Length == 0) { lines.Add("# K-CppUltimateAssist が書きました。Visual Studio は、保存するときに、この文字コードと改行を使います"); }
                lines.Add(header);
                foreach (var kv in want) lines.Add(kv.Key + " = " + kv.Value);
            }
            else
            {
                int end = start + 1;
                while (end < lines.Count && !SectionLine.IsMatch(lines[end])) end++;
                foreach (var kv in want)
                {
                    int at = -1;
                    for (int i = start + 1; i < end; i++)
                    {
                        Match k = KeyLine.Match(lines[i]);
                        if (k.Success && string.Equals(k.Groups[1].Value, kv.Key, StringComparison.OrdinalIgnoreCase)) { at = i; break; }
                    }
                    if (at >= 0) lines[at] = kv.Key + " = " + kv.Value;
                    else
                    {
                        // 節の最後の中身のある行のあとに足す
                        int ins = end;
                        while (ins > start + 1 && lines[ins - 1].Trim().Length == 0) ins--;
                        lines.Insert(ins, kv.Key + " = " + kv.Value);
                        end++;
                    }
                }
            }
            return string.Join(eolText, lines) + eolText;
        }
    }
}
