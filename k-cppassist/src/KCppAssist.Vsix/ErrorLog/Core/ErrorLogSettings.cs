namespace KCppAssist.ErrorLog
{
    /// <summary>設定画面の「エラーログ」の値。ビルドのたびに(窓を作るときにも)設定から読み直す。別のスレッドからも読むので、値だけ持つ。</summary>
    public static class ErrorLogSettings
    {
        public static volatile bool FindLibs = true;          // .lib とソースを探して、原因を言い当てる
        public static volatile int MaxLibs = 800;             // 読む .lib の数の上限
        public static volatile int SearchMilliseconds = 6000; // 探す時間の上限
        public static volatile bool ShortenTypes = true;      // 型名を短くする
        public static volatile bool ShowHints = true;         // 日本語のヒントを出す
        public static volatile bool ShowAdvice = true;        // 「まず一番上から」の案内
        public static volatile bool ShowCascade = true;       // 連鎖の可能性
        public static volatile bool ShowExamples = true;      // 直し方の例
        public static volatile int MaxItems = 400;            // 一度に出すエラーの上限

        internal static void Load(OptionsPage o)
        {
            if (o == null) return;
            FindLibs = o.ErrorLogFindLibs;
            MaxLibs = o.ErrorLogMaxLibs < 1 ? 1 : o.ErrorLogMaxLibs;
            SearchMilliseconds = (o.ErrorLogSearchSeconds < 1 ? 1 : o.ErrorLogSearchSeconds) * 1000;
            ShortenTypes = o.ErrorLogShortenTypes;
            ShowHints = o.ErrorLogShowHints;
            ShowAdvice = o.ErrorLogShowOrderAdvice;
            ShowCascade = o.ErrorLogShowCascade;
            ShowExamples = o.ErrorLogShowExamples;
            MaxItems = o.ErrorLogMaxItems < 1 ? 1 : o.ErrorLogMaxItems;
        }
    }
}
