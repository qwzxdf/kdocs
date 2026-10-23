using System;
using KCppErr;

// 実際の MSVC の出力に近い形で、解析を確かめる。失敗したら終了コード 1。
class Program
{
    static int failed;

    static void Check(bool ok, string what)
    {
        Console.WriteLine((ok ? "OK   " : "FAIL ") + what);
        if (!ok) failed = 1;
    }

    static int Main()
    {
        string sol = @"D:\game";
        string text = string.Join("\n", new[]
        {
            "1>------ ビルド開始: プロジェクト: game, 構成: Debug x64 ------",
            "1>Main.cpp",
            @"1>C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC\14.40.33807\include\memory(3511,14): error C2665: 'prest::SwapChain::SwapChain': オーバーロードされた関数ですべての引数の型を変換できませんでした",
            @"1>D:\game\src\SwapChain.h(12,5): message : 'prest::SwapChain::SwapChain(HWND,int)' の可能性があります",
            @"1>D:\game\src\SwapChain.h(8,5): message : or       'prest::SwapChain::SwapChain(const prest::SwapChain &)'",
            @"1>C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC\14.40.33807\include\memory(3511,14): message : 引数リスト '(int, float)' を一致させようとしているとき",
            @"1>C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC\14.40.33807\include\memory(3520): message : see reference to function template instantiation 'std::unique_ptr<prest::SwapChain,std::default_delete<prest::SwapChain>> std::make_unique<prest::SwapChain,int,float,0>(int &&,float &&)' being compiled",
            @"1>D:\game\src\Main.cpp(42,30): message : see reference to function template instantiation 'std::unique_ptr<prest::SwapChain> std::make_unique<prest::SwapChain,int,float,0>(int &&,float &&)' being compiled",
            "1>        with",
            "1>        [",
            "1>            _Ty=prest::SwapChain",
            "1>        ]",
            @"1>D:\game\src\Main.cpp(50,9): warning C4100: 'x': 引数は関数の本体部で 1 度も参照されません",
            "1>Generating Code...",
            @"1>LINK : fatal error LNK1104: ファイル 'foo.lib' を開けません。",
            "1>プロジェクト \"game.vcxproj\" のビルドが完了しました -- 失敗。",
        });

        var groups = BuildOutputParser.Parse(text);
        Check(groups.Count == 3, "3 グループ(error, warning, LNK): " + groups.Count);

        var g = groups[0];
        Check(g.Primary.Code == "C2665", "コード C2665");
        Check(g.Primary.File.EndsWith(@"include\memory") && g.Primary.Line == 3511 && g.Primary.Col == 14, "主エラーの場所(Program Files を含む)");
        Check(Analyzer.IsInsideLibrary(g), "主エラーはライブラリの中");
        Check(g.Frames.Count == 5, "補足の診断が 5 個: " + g.Frames.Count);

        var user = Analyzer.FindUserFrame(g, sol);
        Check(user != null && user.File.EndsWith("Main.cpp") && user.Line == 42, "原因の場所は Main.cpp の 42 行目");
        Check(user != null && user.Details.Count == 4 && user.Details[2] == "_Ty=prest::SwapChain", "with [ _Ty= ] が補足として付く");
        Check(Analyzer.FindArgumentList(g) == "(int, float)", "渡した引数 (int, float)");
        string hint = Analyzer.HintFor(g, sol);
        Check(hint.Contains("Main.cpp") && hint.Contains("42"), "ヒントに Main.cpp と 42 が入る");

        Check(!groups[1].IsError && groups[1].Primary.Code == "C4100", "警告 C4100");
        Check(groups[2].Primary.Code == "LNK1104" && groups[2].Primary.Line == 0, "リンカーのエラーは行番号なし");
        Check(Analyzer.FindUserFrame(groups[2], sol) == null, "リンカーのエラーに場所はない");

        // 同じエラーの重複(ビルド出力が 2 回出る場合)は 1 つにする
        Check(BuildOutputParser.Parse(text + "\n" + text).Count == 3, "重複は除かれる");

        // GCC / Clang
        var gcc = BuildOutputParser.Parse(string.Join("\n", new[]
        {
            "/usr/include/c++/13/bits/unique_ptr.h:1070:30: error: no matching function for call to 'Foo::Foo(int, float)'",
            "/home/me/game/main.cpp:42:30:   required from here",
            "/home/me/game/foo.h:8:5: note: candidate: 'Foo::Foo(int)'",
        }));
        Check(gcc.Count == 1 && gcc[0].Frames.Count == 2, "GCC の形式");
        var gu = Analyzer.FindUserFrame(gcc[0], "/home/me/game");
        Check(gu != null && gu.Line == 42, "GCC: required from here が原因の場所");

        return failed;
    }
}
