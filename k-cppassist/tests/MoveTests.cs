using System;
using System.Linq;
using KCppAssist;

/// <summary>関数の本体を、ヘッダー ⇄ cpp で移す部分(MoveGen)のテスト。</summary>
static class MoveTests
{
    static int pass = 0, fail = 0;

    static void Check(string name, string got, string want)
    {
        if (got == want) { pass++; return; }
        fail++;
        Console.WriteLine("FAIL " + name);
        Console.WriteLine("  got : " + (got ?? "(null)").Replace("\n", "\\n"));
        Console.WriteLine("  want: " + want.Replace("\n", "\\n"));
    }

    /// <summary>ヘッダーの name(本体あり)を cpp に移した結果の「ヘッダー\n=====\ncpp」。移せなければ "!理由"。</summary>
    static string ToCpp(string header, string cpp, string name)
    {
        var sig = FunctionScan.Scan(header).First(s => s.HasBody && s.Name == name);
        string why;
        var plan = MoveGen.ToCpp(header, sig, cpp, "\n", out why);
        if (plan == null) return "!" + why;
        return MoveGen.Apply(header, plan.Source) + "=====\n" + MoveGen.Apply(cpp, plan.Target);
    }

    /// <summary>cpp の name(Class::Name の定義)を、ヘッダーの宣言へ移した結果。</summary>
    static string ToHeader(string cpp, string header, string name)
    {
        var def = FunctionScan.Scan(cpp).First(s => s.HasBody && s.Name == name);
        var decl = FunctionScan.Scan(header).First(s => !s.HasBody && s.Name == name);
        string why;
        var plan = MoveGen.ToHeader(cpp, def, header, decl, "\n", out why);
        if (plan == null) return "!" + why;
        return MoveGen.Apply(header, plan.Target) + "=====\n" + MoveGen.Apply(cpp, plan.Source);
    }

    public static int Run()
    {
        // ---- ヘッダー → cpp ----
        string h1 = "class A {\n public:\n  int Get() const { return x_; }\n  void Set(int v);\n private:\n  int x_;\n};\n";
        string c1 = "#include \"a.h\"\n\nvoid A::Set(int v) {\n  x_ = v;\n}\n";
        Check("1行の getter",
            ToCpp(h1, c1, "Get"),
            "class A {\n public:\n  int Get() const;\n  void Set(int v);\n private:\n  int x_;\n};\n=====\n#include \"a.h\"\n\nvoid A::Set(int v) {\n  x_ = v;\n}\n\nint A::Get() const {\n  return x_;\n}\n");

        string h2 = "class A {\n public:\n  void Run(int n) {\n    for (int i = 0; i < n; ++i) {\n      Step(i);\n    }\n  }\n  void Step(int i);\n};\n";
        Check("複数行(インデントを外す)",
            ToCpp(h2, "", "Run"),
            "class A {\n public:\n  void Run(int n);\n  void Step(int i);\n};\n=====\nvoid A::Run(int n) {\n  for (int i = 0; i < n; ++i) {\n    Step(i);\n  }\n}\n");

        string h3 = "class B {\n public:\n  B(int a, int b) : a_(a), b_(b) {}\n private:\n  int a_, b_;\n};\n";
        Check("コンストラクターの初期化子リスト",
            ToCpp(h3, "", "B"),
            "class B {\n public:\n  B(int a, int b);\n private:\n  int a_, b_;\n};\n=====\nB::B(int a, int b)\n    : a_(a), b_(b) {\n}\n");

        string h4 = "class C {\n public:\n  template <typename T> void F(T t) { use(t); }\n};\n";
        Check("template は移さない", ToCpp(h4, "", "F").StartsWith("!") ? "refused" : "moved", "refused");

        string h4b = "template <typename T>\nclass Box {\n public:\n  int Size() const { return n_; }\n private:\n  int n_;\n};\n";
        Check("template のクラスの中は移さない", ToCpp(h4b, "", "Size").StartsWith("!") ? "refused" : "moved", "refused");

        string h5 ="namespace n {\ninline int Twice(int x) { return x * 2; }\n}\n";
        Check("クラス外の inline",
            ToCpp(h5, "", "Twice"),
            "namespace n {\nint Twice(int x);\n}\n=====\nint n::Twice(int x) {\n  return x * 2;\n}\n");

        string h6 = "class D {\n public:\n  D() = default;\n  virtual int V() const override { return 1; }\n};\n";
        Check("override を定義に書かない",
            ToCpp(h6, "", "V"),
            "class D {\n public:\n  D() = default;\n  virtual int V() const override;\n};\n=====\nint D::V() const {\n  return 1;\n}\n");

        // ---- cpp → ヘッダー ----
        string h7 = "class A {\n public:\n  int Get() const;\n  void Set(int v);\n};\n";
        string c7 = "#include \"a.h\"\n\nint A::Get() const {\n  return x_;\n}\n\nvoid A::Set(int v) {\n  x_ = v;\n}\n";
        Check("cpp の getter をヘッダーへ",
            ToHeader(c7, h7, "Get"),
            "class A {\n public:\n  int Get() const { return x_; }\n  void Set(int v);\n};\n=====\n#include \"a.h\"\n\nvoid A::Set(int v) {\n  x_ = v;\n}\n");

        string c8 = "A::Run(int n) {\n  for (int i = 0; i < n; ++i) {\n    Step(i);\n  }\n}\n";
        string h8 = "class A {\n public:\n  void Run(int n);\n};\n";
        Check("複数行をヘッダーへ(インデントを付ける)",
            ToHeader("void " + c8, h8, "Run"),
            "class A {\n public:\n  void Run(int n) {\n    for (int i = 0; i < n; ++i) {\n      Step(i);\n    }\n  }\n};\n=====\n");

        string c9 = "void A::Set(int value) {\n  x_ = value;\n}\n";
        string h9 = "class A {\n public:\n  void Set(int v = 0);\n};\n";
        Check("引数の名前は cpp にそろえて、既定値は残す",
            ToHeader(c9, h9, "Set"),
            "class A {\n public:\n  void Set(int value = 0) { x_ = value; }\n};\n=====\n");

        string c10 = "B::B(int a, int b)\n    : a_(a), b_(b) {\n}\n";
        string h10 = "class B {\n public:\n  B(int a, int b);\n};\n";
        Check("初期化子リストをヘッダーへ",
            ToHeader(c10, h10, "B"),
            "class B {\n public:\n  B(int a, int b)\n      : a_(a), b_(b) {}\n};\n=====\n");

        Check("純粋仮想には移さない",
            ToHeader("int A::V() const {\n  return 1;\n}\n", "class A {\n public:\n  virtual int V() const = 0;\n};\n", "V").StartsWith("!") ? "refused" : "moved", "refused");

        // ---- 往復: ヘッダー → cpp → ヘッダー で、関数の中身が変わらない ----
        string rt = ToCpp(h2, "", "Run");
        string[] parts = rt.Split(new[] { "=====\n" }, StringSplitOptions.None);
        string back = ToHeader(parts[1], parts[0], "Run");
        string[] parts2 = back.Split(new[] { "=====\n" }, StringSplitOptions.None);
        Check("往復でヘッダーが元に戻る(Step の宣言は残る)", parts2[0], h2);

        Console.WriteLine("move: pass=" + pass + " fail=" + fail);
        return fail == 0 ? 0 : 1;
    }
}
