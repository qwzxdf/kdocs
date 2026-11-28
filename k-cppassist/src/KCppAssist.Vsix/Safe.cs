using System;
using System.Collections.Generic;
using System.IO;
using System.Runtime.CompilerServices;

namespace KCppAssist
{
    /// <summary>
    /// 握りつぶす例外を、ログに残す。失敗しても処理は続けたいが、あとで原因を追えるようにする。
    /// 同じ場所の同じ例外は、最初の 3 回だけ書く(入力のたびに走る処理でログが埋まらないように)。
    /// 書き先(Sink)は、拡張機能の起動時に vsix.log へつなぐ。つながっていなければ何もしない(単体テストなど)。
    /// </summary>
    internal static class Safe
    {
        public static Action<string> Sink;

        private static readonly Dictionary<string, int> Counts = new Dictionary<string, int>();
        private const int MaxPerSite = 3;

        public static void Ignore(Exception ex, [CallerMemberName] string member = null, [CallerFilePath] string file = null, [CallerLineNumber] int line = 0)
        {
            var sink = Sink;
            if (sink == null || ex == null) return;
            string site = Path.GetFileName(file) + ":" + line;
            string key = site + " " + ex.GetType().Name;
            lock (Counts)
            {
                int n;
                Counts.TryGetValue(key, out n);
                Counts[key] = ++n;
                if (n > MaxPerSite) return;
            }
            try { sink("ignored " + ex.GetType().Name + " at " + site + " (" + member + "): " + ex.Message); }
            catch (Exception) { }
        }
    }
}
