using System;
using System.Collections.Generic;
using System.Linq;
using KCppAssist;

// make_unique / make_shared / new の引数の個数チェック(CallCheck)のテスト
static class CallCheckTests
{
    static int pass, fail;

    static void Check(string name, bool ok)
    {
        if (ok) pass++; else { fail++; Console.WriteLine("FAIL: " + name); }
    }

    const string Header =
        "#pragma once\n" +
        "namespace gfx {\n" +
        "class SwapChain {\n" +
        "public:\n" +
        "    SwapChain(HWND hwnd);\n" +
        "    SwapChain(HWND hwnd, int count);\n" +
        "    ~SwapChain();\n" +
        "};\n" +
        "struct Vec { Vec() = default; Vec(float x, float y, float z = 0.0f) : x(x), y(y), z(z) {} float x, y, z; };\n" +
        "struct Plain { int a; int b; };\n" +
        "template <class T> class Box { public: Box(int a); };\n" +
        "class Derived : public SwapChain { public: using SwapChain::SwapChain; };\n" +
        "class Macro { public: DECLARE_CTOR(Macro) };\n" +
        "class Var { public: template <class... A> Var(A&&... a); };\n" +
        "class Two { public: explicit Two(int a, std::map<int, int> m); };\n" +
        "}\n";

    static Func<string, string, CallCheck.ClassInfo> Lookup(string header)
    {
        return (q, n) => CallCheck.ReadClass(header, n, q);
    }

    static List<CallCheck.Finding> Run(string code, CallCheck.Options o = null)
    {
        return CallCheck.Check(code, Lookup(Header), o);
    }

    static void Main()
    {
        // ---- クラスの読み取り ----
        var sc = CallCheck.ReadClass(Header, "SwapChain", null);
        Check("SwapChain: two ctors", sc != null && sc.Ctors.Count == 2);
        Check("SwapChain: arities", sc != null && sc.Ctors[0].Min == 1 && sc.Ctors[0].Max == 1 && sc.Ctors[1].Min == 2 && sc.Ctors[1].Max == 2);
        var vec = CallCheck.ReadClass(Header, "Vec", null);
        Check("Vec: default and default-arg ctor", vec != null && vec.Ctors.Count == 2 && vec.Ctors.Any(c => c.Min == 0 && c.Max == 0) && vec.Ctors.Any(c => c.Min == 2 && c.Max == 3));
        Check("aggregate is not checked", CallCheck.ReadClass(Header, "Plain", null) == null);
        Check("class template is not checked", CallCheck.ReadClass(Header, "Box", null) == null);
        Check("inherited ctors are not checked", CallCheck.ReadClass(Header, "Derived", null) == null);
        Check("macro class is not checked", CallCheck.ReadClass(Header, "Macro", null) == null);
        var var = CallCheck.ReadClass(Header, "Var", null);
        Check("variadic ctor is unbounded", var != null && var.Ctors[0].Max < 0);
        var two = CallCheck.ReadClass(Header, "Two", null);
        Check("comma inside <> is one parameter", two != null && two.Ctors[0].Min == 2 && two.Ctors[0].Max == 2);
        Check("unknown class", CallCheck.ReadClass(Header, "Nope", null) == null);
        Check("namespace qualifier must exist", CallCheck.ReadClass(Header, "SwapChain", "other") == null && CallCheck.ReadClass(Header, "SwapChain", "gfx") != null);

        // ---- 呼び出し ----
        var f = Run("auto p = std::make_unique<SwapChain>(h, 1, 2);\n");
        Check("make_unique too many", f.Count == 1 && f[0].Given == 3 && f[0].Message.Contains("多すぎ") && f[0].Message.Contains("SwapChain(HWND hwnd, int count)"));
        Check("too many: squiggle starts at the first extra argument", f.Count == 1 && "auto p = std::make_unique<SwapChain>(h, 1, 2);\n".Substring(f[0].Start, f[0].Length) == "2");
        Check("ok: 1 arg", Run("auto p = std::make_unique<SwapChain>(h);\n").Count == 0);
        Check("ok: 2 args", Run("auto p = std::make_shared<SwapChain>(h, 2);\n").Count == 0);
        f = Run("auto p = std::make_unique<SwapChain>();\n");
        Check("no default ctor: zero args is an error", f.Count == 1 && f[0].Given == 0 && f[0].Message.Contains("足りません"));
        Check("zero args: squiggle covers the parentheses", f.Count == 1 && "auto p = std::make_unique<SwapChain>();\n".Substring(f[0].Start, f[0].Length) == "()");
        Check("new too many", Run("auto* p = new SwapChain(a, b, c);\n").Count == 1);
        Check("new ok", Run("auto* p = new SwapChain(a, b);\n").Count == 0);
        Check("namespace-qualified type", Run("auto p = std::make_unique<gfx::SwapChain>(a, b, c);\n").Count == 1);
        Check("make_unique without std::", Run("auto p = make_unique<SwapChain>(a, b, c);\n").Count == 1);
        Check("other namespace's make_unique is not ours", Run("auto p = foo::make_unique<SwapChain>(a, b, c);\n").Count == 0);
        Check("member make_unique is not ours", Run("auto p = obj.make_unique<SwapChain>(a, b, c);\n").Count == 0);

        // 既定引数・可変長
        Check("default argument allows 2 or 3", Run("std::make_unique<Vec>(1.f, 2.f);\nstd::make_unique<Vec>(1.f, 2.f, 3.f);\nstd::make_unique<Vec>();\n").Count == 0);
        Check("Vec with 4 args", Run("std::make_unique<Vec>(1.f, 2.f, 3.f, 4.f);\n").Count == 1);
        Check("Vec with 1 literal arg is an error", Run("std::make_unique<Vec>(1.f);\n").Count == 1);
        Check("variadic accepts anything", Run("std::make_unique<Var>(1, 2, 3, 4, 5);\n").Count == 0);

        // 1 個だけ渡しているとき(コピー・ムーブかもしれない)
        Check("single non-literal arg may be a copy", Run("std::make_unique<Vec>(other);\n").Count == 0);
        Check("single literal arg cannot be a copy", Run("std::make_unique<Vec>(5);\n").Count == 1 && Run("std::make_unique<Vec>(\"x\");\n").Count == 1);

        // 調べないもの
        Check("aggregate never flagged", Run("std::make_unique<Plain>(1, 2, 3);\n").Count == 0);
        Check("template class never flagged", Run("new Box(1, 2, 3);\n").Count == 0);
        Check("std type never flagged", Run("std::make_unique<std::string>(1, 2, 3, 4);\n").Count == 0);
        Check("unknown type never flagged", Run("std::make_unique<Whatever>(1, 2, 3);\n").Count == 0);
        Check("pack expansion is skipped", Run("std::make_unique<SwapChain>(std::forward<A>(a)...);\n").Count == 0);
        Check("comment and string are ignored", Run("// std::make_unique<SwapChain>(1,2,3)\nconst char* s = \"new SwapChain(1,2,3)\";\n").Count == 0);
        Check("placement new is skipped", Run("new (buf) SwapChain(a, b, c);\n").Count == 0);
        Check("array new is skipped", Run("auto* p = new SwapChain[3];\n").Count == 0);

        // 引数の切り分け
        Check("commas inside nested calls and lambdas", Run("std::make_unique<SwapChain>(f(a, b), [](int x, int y){ return x; });\n").Count == 0);
        Check("template args with commas are one argument", Run("std::make_unique<SwapChain>(std::map<int, int>{}, 2);\n").Count == 0);
        Check("braced init with commas is one argument", Run("std::make_unique<SwapChain>(h, {1, 2});\n").Count == 0);
        Check("unbalanced call is skipped", Run("std::make_unique<SwapChain>(a, (b, c);\n").Count == 0);

        // 入力中
        string typing = "std::make_unique<Two>(1);\n";
        var o = new CallCheck.Options { Caret = typing.IndexOf("1") + 1 };
        Check("typing inside the call: 'too few' is held back", CallCheck.Check(typing, Lookup(Header), o).Count == 0 && o.Suppressed);
        o = new CallCheck.Options { Caret = typing.Length };
        Check("caret elsewhere: flagged", CallCheck.Check(typing, Lookup(Header), o).Count == 1 && !o.Suppressed);
        string many = "std::make_unique<SwapChain>(a, b, c);\n";
        o = new CallCheck.Options { Caret = many.IndexOf("c") + 1 };
        Check("typing inside the call: 'too many' is still flagged", CallCheck.Check(many, Lookup(Header), o).Count == 1);

        // 設定
        Check("make off", CallCheck.Check("std::make_unique<SwapChain>(a,b,c);\nnew SwapChain(a,b,c);\n", Lookup(Header), new CallCheck.Options { Make = false }).Count == 1);
        Check("new off", CallCheck.Check("std::make_unique<SwapChain>(a,b,c);\nnew SwapChain(a,b,c);\n", Lookup(Header), new CallCheck.Options { New = false }).Count == 1);
        Check("ignore list", CallCheck.Check("new SwapChain(a,b,c);\n", Lookup(Header), new CallCheck.Options { Ignore = new HashSet<string> { "SwapChain" } }).Count == 0);

        // 複数の指摘は位置の順
        var two2 = Run("new SwapChain(a,b,c);\nnew SwapChain();\n");
        Check("sorted by position", two2.Count == 2 && two2[0].Start < two2[1].Start);

        // 同じファイルのクラス
        Check("DefinesClass", CallCheck.DefinesClass(Header, "SwapChain") && !CallCheck.DefinesClass(Header, "Nope") && !CallCheck.DefinesClass("class A; enum class SwapChain {};", "SwapChain"));

        Console.WriteLine("callcheck: pass=" + pass + " fail=" + fail);
        Environment.Exit(fail == 0 ? 0 : 1);
    }
}
