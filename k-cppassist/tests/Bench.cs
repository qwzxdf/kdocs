using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using KCppAssist;

// 打つたび・カーソルが動くたびに走る、VS に依存しない処理の時間を測る(tests\bench.ps1 から使う)。
// 引数: 測るファイル(大きいヘッダーや cpp)。
static class Bench
{
    static void Time(string name, int n, Action run)
    {
        run();                                     // JIT の分を除く
        var sw = Stopwatch.StartNew();
        for (int i = 0; i < n; i++) run();
        Console.WriteLine("{0,-28} {1,8:0.00} ms", name, sw.Elapsed.TotalMilliseconds / n);
    }

    static void Main(string[] args)
    {
        foreach (string path in args)
        {
            string text = File.ReadAllText(path);
            Console.WriteLine("== " + Path.GetFileName(path) + " (" + text.Length / 1024 + " KB, " + text.Count(c => c == '\n') + " lines)");
            int caret = text.Length / 2;
            string eol = CppText.Eol(text);
            bool header = path.EndsWith(".h");
            Time("CppText.Mask", 20, () => CppText.Mask(text));
            Time("Scopes.Parse", 20, () => Scopes.Parse(text));
            Time("FunctionScan.Scan", 20, () => FunctionScan.Scan(text));
            Time("AssignScan.Find", 20, () => AssignScan.Find(text, caret));
            Time("MemberScan.At", 20, () => MemberScan.At(text, caret));
            Time("Refactor.Offers", 20, () => Refactor.Offers(text, caret, eol, header));
            Time("ClassGen.OnHead", 20, () => ClassGen.OnHead(text, caret));
            Time("SymbolScan.DeclAt", 20, () => SymbolScan.DeclAt(text, caret));
            Time("SwitchGen.BodyEmptyAt", 20, () => { int o; SwitchGen.BodyEmptyAt(text, caret, out o); });
            Time("IncludeTidy.Parse", 20, () => IncludeTidy.Parse(text));
            Time("CallCheck.Check (new string)", 10, () => CallCheck.Check(new string(text.ToCharArray()), (n, q) => null, new CallCheck.Options()));
            Time("SymbolScan.DeclAt (new string)", 10, () => SymbolScan.DeclAt(new string(text.ToCharArray()), caret));
            // VS はカーソルが動くたびに Snapshot.GetText() で新しい string を作るので、使い回しの効かない(冷えた)時間も測る
            Time("Offers (new string)", 10, () => Refactor.Offers(new string(text.ToCharArray()), caret, eol, header));
            Time("Scan (new string)", 10, () => FunctionScan.Scan(new string(text.ToCharArray())));
            Time("Scan+Parse (new string)", 10, () => { string t = new string(text.ToCharArray()); FunctionScan.Scan(t); Scopes.Parse(t); });
            foreach (string id in new[] { "nullptr", "using", "cast", "rangefor", "invertif", "guard", "auto", "enumstr", "initorder", "nocopy", "rule5", "compare", "formatter", "hash", "json", "cereal", "inputlayout", "cbuffer" })
            {
                string why;
                Time("  Make " + id, 5, () => Refactor.Make(id, new string(text.ToCharArray()), caret, eol, header, out why));
                Time("    (same string)", 5, () => Refactor.Make(id, text, caret, eol, header, out why));
            }
        }
    }
}
