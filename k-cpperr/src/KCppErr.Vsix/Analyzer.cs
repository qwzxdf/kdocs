using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;

namespace KCppErr
{
    /// <summary>エラーのグループから、自分のコードの場所と日本語のヒントを取り出す。</summary>
    public static class Analyzer
    {
        private static readonly string[] SystemMarks =
        {
            @"\vc\tools\msvc\", @"\windows kits\", @"\microsoft visual studio\", @"\vcpkg_installed\",
            @"\vcpkg\installed\", @"\vcpkg\packages\", @"/usr/include/", @"/usr/lib/"
        };

        /// <summary>ライブラリ(標準ライブラリ・Windows SDK・vcpkg)のファイルかどうか。</summary>
        public static bool IsLibraryFile(string path)
        {
            if (string.IsNullOrEmpty(path)) return false;
            string p = path.Replace('/', '\\').ToLowerInvariant();
            foreach (string mark in SystemMarks)
                if (p.Contains(mark.Replace('/', '\\'))) return true;
            return false;
        }

        /// <summary>自分のコードのファイルか。ソリューションのフォルダーが分かればその下、分からなければライブラリ以外。</summary>
        public static bool IsUserFile(string path, string solutionDir)
        {
            if (string.IsNullOrEmpty(path) || IsLibraryFile(path)) return false;
            if (string.IsNullOrEmpty(solutionDir)) return true;
            try
            {
                string full = Path.GetFullPath(path);
                string dir = Path.GetFullPath(solutionDir).TrimEnd('\\') + "\\";
                return full.StartsWith(dir, StringComparison.OrdinalIgnoreCase);
            }
            catch (Exception) { return true; }
        }

        /// <summary>
        /// エラーの原因として開く場所。主エラーが自分のコードならそこ、ライブラリの中なら、
        /// 呼び出しの経路のうち最初に出てくる自分のコード。なければ null。
        /// </summary>
        public static Frame FindUserFrame(ErrorGroup g, string solutionDir)
        {
            if (g.Primary.HasLocation && IsUserFile(g.Primary.File, solutionDir)) return g.Primary;
            foreach (Frame f in g.Frames)
                if (f.Kind == FrameKind.Trace && f.HasLocation && IsUserFile(f.File, solutionDir)) return f;
            foreach (Frame f in g.Frames)
                if (f.HasLocation && IsUserFile(f.File, solutionDir)) return f;
            return null;
        }

        /// <summary>主エラーがライブラリの中で出ているか(= 原因は別の場所にあるエラー)。</summary>
        public static bool IsInsideLibrary(ErrorGroup g)
        {
            return g.Primary.HasLocation && IsLibraryFile(g.Primary.File);
        }

        private static readonly Regex ArgList = new Regex(@"argument list '([^']*)'|引数リスト '([^']*)'", RegexOptions.Compiled);

        /// <summary>「渡した引数: (int, float)」のような、引数の並び。見つからなければ空。</summary>
        public static string FindArgumentList(ErrorGroup g)
        {
            var texts = new List<string>();
            texts.Add(g.Primary.Message);
            texts.AddRange(g.Primary.Details);
            foreach (Frame f in g.Frames)
            {
                texts.Add(f.Message);
                texts.AddRange(f.Details);
            }
            foreach (string t in texts)
            {
                Match m = ArgList.Match(t);
                if (m.Success) return m.Groups[1].Success ? m.Groups[1].Value : m.Groups[2].Value;
            }
            return "";
        }

        /// <summary>メッセージを短くする(長いテンプレート名で埋まらないように)。</summary>
        public static string Shorten(string s, int max)
        {
            if (s == null) return "";
            s = s.Replace("\r", "").Replace("\n", " ").Trim();
            return s.Length <= max ? s : s.Substring(0, max - 1) + "…";
        }

        private static readonly Dictionary<string, string> Hints = new Dictionary<string, string>
        {
            ["C2664"] = "引数の型が、関数(コンストラクタ)の宣言と合っていません。「元のメッセージ」の「cannot convert argument N」で、N 番目の引数が原因です。",
            ["C2665"] = "どのオーバーロードにも引数が合っていません。渡した引数の個数と型を、「候補」の宣言と見比べてください。",
            ["C2661"] = "その個数の引数を受け取るオーバーロードがありません。引数の数を数え直してください。",
            ["C2660"] = "その関数は、渡した個数の引数を受け取りません。",
            ["C2512"] = "引数なしで作れません(既定コンストラクタがない)。引数を渡すか、既定コンストラクタを足します。",
            ["C2440"] = "その型へ変換できません。明示的な変換が要るか、型そのものが違っています。",
            ["C2679"] = "この型に対応する演算子(代入や << など)がありません。",
            ["C2676"] = "この型に、その二項演算子が定義されていません。",
            ["C2678"] = "この型に、その二項演算子が定義されていません。",
            ["C2280"] = "削除された関数を呼んでいます。unique_ptr などコピーできない型をコピーしていないか確認してください。std::move が要ります。",
            ["C2039"] = "そのメンバーは、クラスにありません。綴りと、クラスの種類を確認してください。",
            ["C2065"] = "宣言されていない名前です。綴り、#include、名前空間(std:: など)を確認してください。",
            ["C3861"] = "その名前の関数が見つかりません。#include と、名前空間(std:: など)を確認してください。",
            ["C2146"] = "構文エラーです。直前の行の「;」や「)」の抜けが多いです。",
            ["C2143"] = "構文エラーです。直前の行の「;」や「)」の抜けが多いです。",
            ["C2059"] = "構文エラーです。直前の行の「;」や「)」の抜けが多いです。",
            ["C2338"] = "static_assert に失敗しています。メッセージに、条件が書かれています。",
            ["C7500"] = "concept の条件を満たしていません。「元のメッセージ」に、満たしていない条件が出ています。",
            ["C7602"] = "concept の条件を満たしていません。「元のメッセージ」に、満たしていない条件が出ています。",
            ["C2672"] = "テンプレートの引数に合う関数が見つかりません。渡した型を確認してください。",
            ["C2955"] = "テンプレート引数が足りないか、型として使えません。",
            ["C2784"] = "テンプレート引数を推論できません。引数の型を確認してください。",
            ["C2782"] = "テンプレート引数を推論できません。引数の型を確認してください。",
            ["C2893"] = "テンプレートの特殊化に失敗しました。渡した型を確認してください。",
            ["LNK2019"] = "定義が見つかりません(未解決の外部シンボル)。関数の本体を書いたか、.lib を追加したか、cpp をプロジェクトに入れたかを確認してください。",
            ["LNK2001"] = "定義が見つかりません(未解決の外部シンボル)。関数の本体を書いたか、.lib を追加したか確認してください。",
            ["LNK1104"] = "ファイルを開けません。.lib のパスと、実行中の exe が残っていないかを確認してください。",
            ["LNK2005"] = "同じ名前の定義が重複しています。ヘッダーに関数の本体を書いていないか(inline が要る)を確認してください。",
        };

        public static string HintFor(ErrorGroup g, string solutionDir)
        {
            string hint;
            Hints.TryGetValue(g.Primary.Code ?? "", out hint);
            var parts = new List<string>();
            if (IsInsideLibrary(g))
            {
                Frame user = FindUserFrame(g, solutionDir);
                parts.Add(user != null
                    ? "エラーはライブラリの中(" + Path.GetFileName(g.Primary.File) + ")で出ていますが、原因は、あなたのコードの " + Path.GetFileName(user.File) + " の " + user.Line + " 行目です。"
                    : "エラーはライブラリの中(" + Path.GetFileName(g.Primary.File) + ")で出ています。「呼び出しの経路」を辿ると、あなたのコードの場所が分かります。");
            }
            if (hint != null) parts.Add(hint);
            string args = FindArgumentList(g);
            if (args.Length > 0) parts.Add("渡した引数: " + args);
            return string.Join("\n", parts);
        }
    }
}
