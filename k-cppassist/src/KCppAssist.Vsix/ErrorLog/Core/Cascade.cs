using System;
using System.Collections.Generic;
using System.Linq;

namespace KCppAssist.ErrorLog
{
    /// <summary>
    /// 連鎖して出ているエラーを見つける。1 つの原因(未定義の名前、構文エラー)から、あとのエラーが何件も出ることが多い。
    /// 見つけたものには「連鎖の可能性」と書き、先頭には「まず一番上から直す」と案内する。推測なので、断定はしない。
    /// </summary>
    public static class Cascade
    {
        public sealed class Result
        {
            public Dictionary<Diag, string> Notes = new Dictionary<Diag, string>();
            /// <summary>連鎖の元になっていそうな、最初のエラー(なければ null)。</summary>
            public Diag Root;
        }

        // 連鎖の元になりやすいエラー
        private static readonly HashSet<string> RootCodes = new HashSet<string>(StringComparer.OrdinalIgnoreCase)
        {
            "C1083", "C1189", "C1010", "C1004", "C1075", "C2143", "C2146", "C2059", "C2061", "C3646", "C2065", "C2027", "C2504", "C2653", "C2628", "C2632", "C1070", "C1071"
        };

        // 引用符の中の名前が「未定義」と言われるエラー
        private static readonly HashSet<string> UndefinedCodes = new HashSet<string>(StringComparer.OrdinalIgnoreCase)
        {
            "C2065", "C3861", "C2061", "C3646", "C2146", "C2653", "C2504", "C2027"
        };

        private static readonly HashSet<string> SyntaxCodes = new HashSet<string>(StringComparer.OrdinalIgnoreCase)
        {
            "C2143", "C2059", "C2146", "C1004", "C1075", "C2628", "C2632", "C1070", "C1071"
        };

        public static Result Analyze(BuildReport report)
        {
            var res = new Result();
            if (report == null) return res;
            List<Diag> errors = report.Diags.Where(d => d.Sev == Sev.Error && d.Kind == DiagKind.Generic && !d.IsLinker && !d.IsSummary).ToList();
            if (errors.Count < 2) return res;

            res.Root = errors.FirstOrDefault(e => RootCodes.Contains(e.Code));

            // 未定義と言われた名前 → その最初のエラー
            var undefined = new Dictionary<string, Diag>(StringComparer.Ordinal);
            for (int i = 0; i < errors.Count; i++)
            {
                Diag e = errors[i];
                if (!UndefinedCodes.Contains(e.Code)) continue;
                var q = Hints.Quoted(e.Message);
                if (q.Count > 0 && !undefined.ContainsKey(q[0])) undefined[q[0]] = e;
            }

            Diag syntaxRoot = errors.FirstOrDefault(e => SyntaxCodes.Contains(e.Code) && e.HasLocation);
            int syntaxIndex = syntaxRoot == null ? -1 : errors.IndexOf(syntaxRoot);

            for (int i = 0; i < errors.Count; i++)
            {
                Diag e = errors[i];
                string note = null;

                // 1) 上で未定義と言われた名前を、含んでいる
                foreach (string name in Hints.Quoted(e.Message))
                {
                    Diag u;
                    if (undefined.TryGetValue(name, out u) && u != e && errors.IndexOf(u) < i)
                    {
                        note = "「" + name + "」が、上のエラー (" + u.Code + ") で、未定義と言われています。そちらを直すと、消える可能性があります。";
                        break;
                    }
                }

                // 2) 同じファイルの、構文エラーより後ろ
                if (note == null && syntaxRoot != null && i > syntaxIndex && e != syntaxRoot && !SyntaxCodes.Contains(e.Code)
                    && string.Equals(e.File, syntaxRoot.File, StringComparison.OrdinalIgnoreCase) && e.Line >= syntaxRoot.Line)
                {
                    note = "同じファイルの、上の構文エラー (" + syntaxRoot.Code + ") の影響で出ている可能性があります。そちらを先に直します。";
                }

                if (note != null) res.Notes[e] = note;
            }
            return res;
        }
    }
}
