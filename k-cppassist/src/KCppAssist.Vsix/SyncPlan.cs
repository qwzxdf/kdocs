using System;
using System.Collections.Generic;
using System.Linq;

namespace KCppAssist
{
    /// <summary>
    /// 変えた関数(edited)の相手(ヘッダーの宣言 ⇔ cpp の定義)を、候補の中から選ぶ。VS に依存しない。
    /// 名前・const・namespace とクラスの並び・引数の型で決める。
    /// </summary>
    internal static class SyncPlan
    {
        /// <summary>
        /// 候補 s が edited の相手になれるか。なれなければ 0、namespace とクラスの並びが完全に同じなら 2、
        /// 片方が相手の末尾と一致するだけ(cpp が using namespace で修飾を省いている、など)なら 1。
        /// </summary>
        public static int Counterpart(FunctionScan.Sig s, FunctionScan.Sig edited, bool wantDefinition)
        {
            if (s.Name != edited.Name || s.IsConst != edited.IsConst) return 0;
            if (wantDefinition) { if (!(s.HasBody && !s.InClass)) return 0; }
            else if (s.HasBody) return 0;
            return ChainScore(s.Chain, edited.Chain);
        }

        public static int ChainScore(List<string> a, List<string> b)
        {
            if (a.SequenceEqual(b)) return 2;
            var shorter = a.Count <= b.Count ? a : b;
            var longer = a.Count <= b.Count ? b : a;
            if (shorter.Count == 0) return 1;
            return longer.Skip(longer.Count - shorter.Count).SequenceEqual(shorter) ? 1 : 0;
        }

        /// <summary>
        /// 候補のうち、相手になれて、引数の型が oldKeys と同じものを返す。点(Counterpart)の高いものだけ残す。
        /// 1 つなら、それが写し先。0 なら見つからない。2 つ以上なら、決められない(何も書き換えない)。
        /// </summary>
        public static List<T> Matches<T>(IEnumerable<T> targets, Func<T, int> score, Func<T, List<string>> keys, List<string> oldKeys)
        {
            var ok = targets.Where(t => score(t) > 0 && SameKeys(keys(t), oldKeys)).ToList();
            if (ok.Count == 0) return ok;
            int top = ok.Max(score);
            return ok.Where(t => score(t) == top).ToList();
        }

        public static bool SameKeys(List<string> a, List<string> b) { return a != null && b != null && a.SequenceEqual(b); }
    }
}
