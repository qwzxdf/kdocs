using System;
using System.IO;
using System.Text;

namespace KCppAssist.ErrorLog
{
    /// <summary>
    /// ソースを、エディターと同じ文字コードで読む。BOM があればそれ、なければ UTF-8 として厳密に読めれば UTF-8、読めなければシフト JIS(932)。
    /// File.ReadAllLines は BOM のない Shift-JIS を UTF-8 として読むので、日本語のコメントのある行が文字化けして、
    /// エディターの行と一致しなくなる(「クリックで修正」が「ファイルが変わっています」と断られる)。
    /// </summary>
    public static class SourceText
    {
        public static string Read(string path)
        {
            byte[] b = File.ReadAllBytes(path);
            if (b.Length >= 3 && b[0] == 0xEF && b[1] == 0xBB && b[2] == 0xBF) return new UTF8Encoding(false).GetString(b, 3, b.Length - 3);
            if (b.Length >= 2 && b[0] == 0xFF && b[1] == 0xFE) return new UnicodeEncoding(false, false).GetString(b, 2, b.Length - 2);
            if (b.Length >= 2 && b[0] == 0xFE && b[1] == 0xFF) return new UnicodeEncoding(true, false).GetString(b, 2, b.Length - 2);
            try { return new UTF8Encoding(false, true).GetString(b); }
            catch (DecoderFallbackException)
            {
                try { return Encoding.GetEncoding(932).GetString(b); }
                catch (Exception) { return Encoding.Default.GetString(b); }
            }
        }

        public static string[] ReadLines(string path)
        {
            // File.ReadAllLines と同じく、改行は CRLF・LF・CR のどれでもよく、末尾の改行のあとに空の行は作らない
            string text = Read(path).Replace("\r\n", "\n").Replace('\r', '\n');
            if (text.EndsWith("\n", StringComparison.Ordinal)) text = text.Substring(0, text.Length - 1);
            return text.Split('\n');
        }
    }
}
