using System;
using KCppAssist.ErrorLog;

namespace KCppAssist
{
    // ErrorLogSettings.Load が参照する設定の代わり(テスト用)
    internal class OptionsPage
    {
        public bool ErrorLogFindLibs = true;
        public int ErrorLogMaxLibs = 800, ErrorLogSearchSeconds = 6;
        public bool ErrorLogShortenTypes = true, ErrorLogShowHints = true;
        public bool ErrorLogShowOrderAdvice = true, ErrorLogShowCascade = true, ErrorLogShowExamples = true;
        public int ErrorLogMaxItems = 400;
    }
}

static class P
{
    static int pass, fail;
    static void Check(string name, bool ok)
    {
        if (ok) pass++; else { fail++; Console.WriteLine("FAIL: " + name); }
    }

    static string Render(string log, bool warnings = false)
    {
        var report = BuildLogParser.Parse(log);
        var input = new RenderInput
        {
            Report = report,
            Syms = Diagnoser.Collect(report),
            Ctx = new AnalysisContext { SolutionDir = "", Platform = "x64" },
        };
        return Renderer.Render(input, new RenderOptions { ShowWarnings = warnings }).ToPlainText();
    }

    static void Main()
    {
        string lnk = string.Join("\n", new[]
        {
            "1>------ ビルド開始: プロジェクト: App, 構成: Debug x64 ------",
            "1>main.obj : error LNK2019: 未解決の外部シンボル \"public: __cdecl Foo::Foo(void)\" (??0Foo@@QEAA@XZ) が関数 main で参照されました",
            "1>App.exe : fatal error LNK1120: 1 件の未解決の外部参照",
        });
        string o1 = Render(lnk);
        Console.WriteLine(o1);
        Check("lnk2019 shows symbol", o1.Contains("Foo::Foo"));
        Check("lnk2019 shows code", o1.Contains("LNK2019"));

        string tmpl = string.Join("\n", new[]
        {
            "1>C:\\src\\Main.cpp(12,5): error C2664: 'std::unique_ptr<int,std::default_delete<int>>::unique_ptr(std::unique_ptr<int,std::default_delete<int>> &&) noexcept': 引数 1 を 'const char [4]' から 'std::unique_ptr<int,std::default_delete<int>> &&' に変換できません",
        });
        ErrorLogSettings.ShortenTypes = true;
        string o2 = Render(tmpl);
        Console.WriteLine(o2);
        Check("shortened type", o2.Contains("std::unique_ptr<int>") && !o2.Contains("default_delete"));
        ErrorLogSettings.ShortenTypes = false;
        string o3 = Render(tmpl);
        Check("shorten off keeps raw", o3.Contains("default_delete"));
        ErrorLogSettings.ShortenTypes = true;

        string withHint = Render("1>C:\\src\\a.cpp(3,1): error C2512: 'Foo': 既定のコンストラクターがありません");
        ErrorLogSettings.ShowHints = false;
        string noHint = Render("1>C:\\src\\a.cpp(3,1): error C2512: 'Foo': 既定のコンストラクターがありません");
        ErrorLogSettings.ShowHints = true;
        Check("hint present by default", withHint.Contains("ヒント"));
        Check("hint hidden when off", !noHint.Contains("ヒント") && noHint.Contains("C2512"));

        // ---- 読みやすさの改善(連鎖・具体的な説明・例・警告のエラー扱い・変数と関数の二重定義) ----
        string casc = Render(string.Join("\n", new[]
        {
            "1>C:\\src\\Main.cpp(9,5): error C2065: 'GraphicsModule': 定義されていない識別子です",
            "1>C:\\src\\Main.cpp(10,8): error C2039: 'Init': 'GraphicsModule' のメンバーではありません",
        }));
        Check("order advice shown", casc.Contains("まず:") && casc.Contains("一番上のエラーから"));
        Check("cascade note on 2nd error", casc.Contains("連鎖の可能性") && casc.Contains("C2065"));
        Check("specific name used", casc.Contains("「GraphicsModule」が、この場所から見えていません"));
        Check("fix with Alt+F mentioned", casc.Contains("Alt+F"));

        string syn = Render(string.Join("\n", new[]
        {
            "1>C:\\src\\a.h(5,1): error C2143: 構文エラー: ';' が '}' の前にありません",
            "1>C:\\src\\a.h(9,1): error C2664: 'f': 引数 1 を 'int' から 'Foo' に変換できません",
        }));
        Check("syntax-error cascade note", syn.Contains("構文エラー (C2143) の影響"));

        string w = Render(string.Join("\n", new[]
        {
            "1>C:\\src\\a.cpp(5,3): warning C4996: 'strcpy': unsafe",
            "1>C:\\src\\a.cpp(5,3): error C2220: 次の警告はエラーとして扱われます",
        }), true);
        Check("C2220 title", w.Contains("警告がエラーとして扱われています"));
        Check("C2220 lists cause warning", w.Contains("原因の警告") && w.Contains("C4996"));

        string v = Render(string.Join("\n", new[]
        {
            "1>b.obj : error LNK2005: \"int g_count\" (?g_count@@3HA) は既に a.obj で定義されています",
        }));
        Check("LNK2005 variable advice", v.Contains("extern"));
        Check("LNK2005 variable not blamed on function body", !v.Contains("関数の本体を書いた"));
        string f2 = Render(string.Join("\n", new[]
        {
            "1>b.obj : error LNK2005: \"void __cdecl Foo(void)\" (?Foo@@YAXXZ) は既に a.obj で定義されています",
        }));
        Check("LNK2005 function advice", f2.Contains("関数の本体を書いた"));

        string priv = Render("1>C:\\src\\a.cpp(10,7): error C2248: 'Foo::x_': private メンバー (クラス 'Foo' で宣言されている) にアクセスできません");
        Check("C2248 has hint and example", priv.Contains("private / protected") && priv.Contains("例") && priv.Contains("GetX"));
        string mm = Render("1>C:\\src\\a.cpp(8,40): error C2589: '(': '::' の右側が不正なトークンです");
        Check("C2589 mentions NOMINMAX", mm.Contains("NOMINMAX"));

        string unk = Render("1>C:\\src\\a.cpp(8,40): error C9999: なにかのエラー");
        Check("unknown code gets fallback", unk.Contains("公式のページ") && unk.Contains("エラー コード"));
        string unkw = Render("1>C:\\src\\a.cpp(8,40): warning C9998: なにかの警告", true);
        Check("unknown warning gets fallback", unkw.Contains("ビルドは止まりません"));

        string z = Render("1>C:\\src\\a.cpp(3,1): error C2233: 'x': 配列");
        Check("C2233 fixed", z.Contains("ゼロ サイズ") && !z.Contains("メンバー アクセス"));
        string one = Render("1>C:\\src\\a.cpp(3,1): error C2065: 'x': 定義されていない識別子です");
        Check("single error has no order advice", !one.Contains("まず:"));

        ErrorLogSettings.ShowHints = false;
        string off = Render(string.Join("\n", new[]
        {
            "1>C:\\src\\a.cpp(9,5): error C2065: 'A': 定義されていない識別子です",
            "1>C:\\src\\a.cpp(10,8): error C2039: 'Init': 'A' のメンバーではありません",
        }));
        ErrorLogSettings.ShowHints = true;
        Check("hints off hides advice, example and specific", !off.Contains("まず:") && !off.Contains("このエラー:") && !off.Contains("例"));

        // ---- 設定の切り替え ----
        string two = string.Join("\n", new[]
        {
            "1>C:\\src\\a.cpp(9,5): error C2065: 'A': 定義されていない識別子です",
            "1>C:\\src\\a.cpp(10,8): error C2664: 'f': 引数 1 を 'A' から 'int' に変換できません",
            "1>C:\\src\\a.cpp(11,8): error C2248: 'Foo::x_': private メンバーにアクセスできません",
        });
        ErrorLogSettings.ShowAdvice = false;
        string noAdvice = Render(two);
        ErrorLogSettings.ShowAdvice = true;
        Check("advice off hides 'まず'", !noAdvice.Contains("まず:") && noAdvice.Contains("C2065"));
        ErrorLogSettings.ShowCascade = false;
        string noCasc = Render(two);
        ErrorLogSettings.ShowCascade = true;
        Check("cascade off hides notes", !noCasc.Contains("連鎖の可能性") && Render(two).Contains("連鎖の可能性"));
        ErrorLogSettings.ShowExamples = false;
        string noEx = Render(two);
        ErrorLogSettings.ShowExamples = true;
        Check("examples off hides 例", !noEx.Contains("例") && Render(two).Contains("例"));
        ErrorLogSettings.MaxItems = 1;
        string capped = Render(two);
        ErrorLogSettings.MaxItems = 400;
        Check("max items truncates", capped.Contains("省略") && capped.Contains("C2065") && !capped.Contains("C2248"));

        Console.WriteLine("errorlog: pass=" + pass + " fail=" + fail);
        Environment.Exit(fail == 0 ? 0 : 1);
    }
}
