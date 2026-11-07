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

        // ---- 縮小変換の修正(static_cast) ----
        Func<string, string, string> nf = (line, ty) =>
        {
            var pl = NarrowFix.Make(line, ty);
            return pl == null ? null : line.Substring(0, pl.Start) + pl.Text + line.Substring(pl.Start + pl.Length);
        };
        Check("narrow: decl", nf("  int i = d;", "int") == "  int i = static_cast<int>(d);");
        Check("narrow: assign", nf("  x = a * 2.5;  // 注", "int") == "  x = static_cast<int>(a * 2.5);  // 注");
        Check("narrow: paren not doubled", nf("int n = (a + b);", "int") == "int n = static_cast<int>(a + b);");
        Check("narrow: return", nf("  return v.size();", "int") == "  return static_cast<int>(v.size());");
        Check("narrow: brace init", nf("  int narrow{3.5};", "int") == "  int narrow{static_cast<int>(3.5)};");
        Check("narrow: call with commas inside", nf("int n = std::min(a, b);", "int") == "int n = static_cast<int>(std::min(a, b));");
        Check("narrow: string with = and ; inside", nf("  int k = Foo(\"a=b;\");", "int") == "  int k = static_cast<int>(Foo(\"a=b;\"));");
        Check("narrow: already cast is left", nf("int i = static_cast<int>(d);", "int") == null);
        Check("narrow: compound assign refused", nf("  total += d;", "int") == null);
        Check("narrow: two declarators refused", nf("  int a = x, b = y;", "int") == null);
        Check("narrow: multi-line refused", nf("  int a = Foo(x,", "int") == null);
        Check("narrow: for header refused", nf("  for (int i = 0; i < n; ++i) {", "int") == null);
        Check("narrow: target en", NarrowFix.TargetType("conversion from 'double' to 'int', possible loss of data") == "int");
        Check("narrow: target ja", NarrowFix.TargetType("'初期化中': 'double' から 'int' への変換です。データが失われる可能性があります") == "int");
        Check("narrow: target unsigned", NarrowFix.TargetType("conversion from 'size_t' to 'unsigned int', possible loss of data") == "unsigned int");
        Check("narrow: pointer target refused", NarrowFix.TargetType("conversion from 'int' to 'char *'") == null);

        string ov = Render("1>C:\\src\\a.cpp(15,8): error C3668: 'Derived::Run': オーバーライド指定子 'override' を伴うメソッドは、基底クラス メソッドをオーバーライドしませんでした");
        Check("C3668 title says the cause", ov.Contains("基底クラスに同じ関数がありません"));

        Check("specific: C2440 int->string", Render("1>C:\\src\\a.cpp(11,9): error C2440: '初期化中': 'int' から 'std::string' に変換できません").Contains("「std::string」を作る変換が用意されていません"));
        Check("specific: C2440 const->ref", Render("1>C:\\src\\a.cpp(19,10): error C2440: '初期化中': 'const int' から 'int&' に変換できません").Contains("const の付いた値は、const のない参照では"));
        Check("specific: C2440 rvalue->ref", Render("1>C:\\src\\a.cpp(20,10): error C2440: '初期化中': 'int' から 'int&' に変換できません").Contains("名前のない値"));
        Check("specific: C2440 string->int", Render("1>C:\\src\\a.cpp(11,9): error C2440: '初期化中': 'const char [6]' から 'int' に変換できません").Contains("文字列"));
        Check("specific: C2440 double->ptr", Render("1>C:\\src\\a.cpp(11,9): error C2440: '初期化中': 'double' から 'int*' に変換できません").Contains("ポインターには入れられません"));
        Check("specific: C2664 arg", Render("1>C:\\src\\a.cpp(15,3): error C2664: 'void TakeRef(int&)': 引数 1 を 'int' から 'int&' へ変換できません").Contains("引数 1 に渡した"));
        Check("specific: C2660 count", Render("1>C:\\src\\a.cpp(14,3): error C2660: 'TakePoint': 関数に 2 個の引数を指定できません。").Contains("2 個の引数を受け取りません"));
        Check("specific: C2512 default ctor", Render("1>C:\\src\\a.cpp(36,13): error C2512: 'NoDefault': 既定のコンストラクターがありません").Contains("NoDefault() = default;"));
        Check("specific: C2280 deleted", Render("1>C:\\src\\a.cpp(38,19): error C2280: 'Deleted::Deleted(const Deleted &)': 削除された関数を参照しようとしています").Contains("delete されているので"));
        Check("specific: C2678 const +=", Render("1>C:\\src\\a.cpp(18,3): error C2678: 二項演算子 '+=': 型 'const std::string' の左オペランドを扱う演算子が見つかりません").Contains("演算子「+=」が使えません"));
        Check("specific: C2039 std spelling", Render("1>C:\\src\\a.cpp(16,8): error C2039: 'vectr': 'std' のメンバーではありません").Contains("まず綴りを確かめます(vector"));
        Check("specific: C2672 template", Render("1>C:\\src\\a.cpp(20,3): error C2672: 'Max': 一致するオーバーロードされた関数が見つかりませんでした").Contains("テンプレート引数が決まりません"));

        Console.WriteLine("errorlog: pass=" + pass + " fail=" + fail);
        Environment.Exit(fail == 0 ? 0 : 1);
    }
}
