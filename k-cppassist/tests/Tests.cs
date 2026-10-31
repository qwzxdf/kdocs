using System;
using System.Collections.Generic;
using System.Linq;
using KCppAssist;

static class Tests
{
    static int fail = 0, pass = 0;
    static void Eq(string name, object got, object want)
    {
        string g = got == null ? "<null>" : got.ToString(), w = want == null ? "<null>" : want.ToString();
        if (g == w) pass++; else { fail++; Console.WriteLine("FAIL " + name + ": got [" + g + "] want [" + w + "]"); }
    }

    static AssignScan.Assign At(string src)
    {
        int c = src.IndexOf('|');
        string text = src.Remove(c, 1);
        return AssignScan.Find(text, c);
    }

    // 型の推定を、部分の型を辞書で与えて組み立てる(Quick Info の代わり)
    static string Infer(string expr, Dictionary<string, string> known)
    {
        int off;
        expr = ExprType.StripParens(expr, out off);
        if (known.ContainsKey(expr)) return known[expr];
        var t = TypeInference.FromExpression(expr);
        if (t != null) return t;
        var b = ExprType.SplitBinary(expr);
        if (b != null) return ExprType.BinaryResult(b, b.Operands.Select(o => Infer(o.Key, known)).ToList());
        string op; int uo;
        var u = ExprType.Unary(expr, out op, out uo);
        if (u != null) return ExprType.UnaryResult(op, Infer(u, known));
        return ExprType.CastType(expr);
    }

    static void Main()
    {
        // ---- 文の切り出し ----
        var a = At("void A::F() {\n  stri|de_ = 3;\n}");
        Eq("single", a == null ? null : a.Name + "=" + a.Rhs, "stride_=3");
        a = At("void A::F() {\n  stride_ = 3;|\n}");
        Eq("after semicolon", a == null ? null : a.Name + "=" + a.Rhs, "stride_=3");
        a = At("void A::F() {\n  total_ = a +\n      b |+ c;\n}");
        Eq("multiline cont op", a == null ? null : a.Rhs.Replace("\n", "\\n").Replace(" ", ""), "a+\\nb+c");
        a = At("void A::F() {\n  v_ = Foo(a,\n         b|);\n  y = 2;\n}");
        Eq("multiline call", a == null ? null : a.Name + "=" + a.Rhs.Replace("\n", "").Replace(" ", ""), "v_=Foo(a,b)");
        a = At("void A::F() {\n  x_ = c\n      ? 1\n      : |2;\n}");
        Eq("multiline ternary", a == null ? null : a.Rhs.Replace("\n", "").Replace(" ", ""), "c?1:2");
        a = At("void A::F() {\n  auto f = [this] { count_ = 1|; };\n}");
        Eq("lambda one line", a == null ? null : a.Name + "=" + a.Rhs, "count_=1");
        a = At("void A::F() {\n  auto f = [this] {\n    count_ = comp|ute();\n  };\n}");
        Eq("lambda multi", a == null ? null : a.Name + "=" + a.Rhs, "count_=compute()");
        a = At("void A::F() {\n  if (x) { y_ = 2; }\n  z_ |= 5;\n}");
        Eq("second stmt after block", a == null ? null : a.Name + "=" + a.Rhs, "z_=5");
        a = At("void A::F() {\n  int x |= 0;\n}");
        Eq("already typed", a, null);
        a = At("void A::F() {\n  x_ += |1;\n}");
        Eq("compound", a, null);
        a = At("void A::F() {\n  this->w_ = 4|;\n}");
        Eq("this", a == null ? a : (object)(a.HasThis + a.Name), "Truew_");
        a = At("void A::F() {\n  m_ = Foo{1, 2}|;\n}");
        Eq("init list", a == null ? null : a.Rhs, "Foo{1, 2}");
        a = At("void A::F() {\n  m_ = foo()|\n  n_ = 2;\n}");
        Eq("no semicolon", a == null ? null : a.Rhs, "foo()");
        a = At("void A::F() {\n  // c\n  p_ = 1|; // trailing\n}");
        Eq("comment", a == null ? null : a.Rhs, "1");
        a = At("void A::F() {\n  case_ = 1; default: q_ = 2|;\n}");
        Eq("label", a == null ? null : a.Name, "q_");

        // ---- 式の型 ----
        var k = new Dictionary<string, string> {
            {"a","int"}, {"b","int"}, {"f","float"}, {"d","double"}, {"u","UINT"}, {"u2","UINT"}, {"n","size_t"}, {"s","std::string"},
            {"v","XMFLOAT3"}, {"p","char*"}, {"c","char"}, {"flag","bool"}, {"o", "std::chrono::steady_clock::time_point"}
        };
        Eq("int+int", Infer("a + b", k), "int");
        Eq("int+float", Infer("a + f", k), "float");
        Eq("float*double", Infer("f * d", k), "double");
        Eq("UINT+UINT", Infer("u + u2", k), "UINT");
        Eq("int+UINT", Infer("a + u", k), "unsigned int");
        Eq("size_t*2", Infer("n * 2", k), "unsigned long long");
        Eq("size_t*size_t", Infer("n * n", k), "size_t");
        Eq("char+char", Infer("c + c", k), "int");
        Eq("cmp", Infer("a < b", k), "bool");
        Eq("cmp==", Infer("a == b", k), "bool");
        Eq("logic", Infer("flag && a > 0", k), "bool");
        Eq("!x", Infer("!flag", k), "bool");
        Eq("-x", Infer("-a", k), "int");
        Eq("shift", Infer("u << 2", k), "UINT");
        Eq("string+lit", Infer("s + \"x\"", k), "std::string");
        Eq("lit+string", Infer("\"x\" + s", k), "std::string");
        Eq("vec*float", Infer("v * f", k), "XMFLOAT3");
        Eq("float*vec", Infer("f * v", k), "XMFLOAT3");
        Eq("ptr+int", Infer("p + 2", k), "char*");
        Eq("ptr-ptr", Infer("p - p", k), "ptrdiff_t");
        Eq("time-time", Infer("o - o", k), null);
        Eq("a+b*f", Infer("a + b * f", k), "float");
        Eq("parens", Infer("(a + b) * d", k), "double");
        Eq("float lit", Infer("a * 1.5f", k), "float");
        Eq("double lit", Infer("a / 2.0", k), "double");
        Eq("cast", Infer("(float)a", k), "float");
        Eq("cast+op", Infer("(float)a + 1", k), "float");
        Eq("exp", Infer("1e-3 * a", k), "double");
        Eq("template no op", Infer("std::make_unique<Foo>(a)", k), "std::unique_ptr<Foo>");
        Eq("addr", Infer("&a", k), "int*");
        Eq("unknown", Infer("zzz + a", k), null);

        // ---- クラス ----
        string cpp = "namespace game {\nvoid Outer::Inner::Func() {\n  x_ = 1;\n}\n}\n";
        var r = CppScan.EnclosingClassRef(cpp, cpp.IndexOf("x_"));
        Eq("nested ref", r == null ? null : r.Qualified + "|" + string.Join(",", r.Namespaces), "Outer::Inner|game");

        string hdr = "namespace game {\nclass Outer {\n public:\n  class Inner { int a_; };\n};\n}\nnamespace ui {\nclass Inner { int b_; };\nclass Outer { public: class Inner { int c_; }; };\n}\n";
        var ms = Scopes.Matches(hdr, r);
        Eq("matches count", ms.Count, 2);
        Eq("pick game::Outer::Inner", string.Join("::", ms[0].Key.Chain()), "game::Outer::Inner");

        string cpp2 = "namespace ui {\nvoid Inner::Func() {\n  x_ = 1;\n}\n}\n";
        var r2 = CppScan.EnclosingClassRef(cpp2, cpp2.IndexOf("x_"));
        var ms2 = Scopes.Matches(hdr, r2);
        Eq("ui::Inner first", string.Join("::", ms2[0].Key.Chain()), "ui::Inner");

        string inclass = "class W {\n public:\n  void Set() {\n    count_ = 1;\n  }\n private:\n  int count_;\n};\n";
        var r3 = CppScan.EnclosingClassRef(inclass, inclass.IndexOf("count_ = 1"));
        Eq("in-class", r3 == null ? null : r3.Name + "@" + r3.InFileOpen, "W@" + (inclass.IndexOf('{')));

        string lam = "void W::Run() {\n  auto f = [this] {\n    count_ = 2;\n  };\n}\n";
        var r4 = CppScan.EnclosingClassRef(lam, lam.IndexOf("count_ = 2"));
        Eq("lambda in member", r4 == null ? null : r4.Name, "W");

        string nonmember = "void Free() {\n  x = 1;\n}\n";
        Eq("free function", CppScan.EnclosingClassRef(nonmember, nonmember.IndexOf("x = 1")), null);


        // ---- 挿入位置: 同名の入れ子クラスのうち、選んだほうに入る ----
        var game = ms[0].Key;
        var ed = HeaderEditor.PlanAt(hdr, game.Open, "int z_;", "\n");
        Eq("insert inside game::Outer::Inner", ed != null && ed.Position > game.Open && ed.Position <= game.Close, true);
        var ui = ms2[0].Key;
        var ed2 = HeaderEditor.PlanAt(hdr, ui.Open, "int z_;", "\n");
        Eq("insert inside ui::Inner", ed2 != null && ed2.Position > ui.Open && ed2.Position <= ui.Close, true);

        // ---- 文の切り出しの追加ケース ----
        a = At("void A::F() {\n  x_ = a\n      + b\n      +| c;\n}");
        Eq("leading-op continuation", a == null ? null : a.Rhs.Replace("\n", "").Replace(" ", ""), "a+b+c");
        a = At("void A::F() {\n  foo(1);\n  |y_ = bar();\n}");
        Eq("caret at indent", a == null ? null : a.Name, "y_");
        a = At("void A::F() {\n  while (x) {\n    y_ = 1|;\n  }\n}");
        Eq("in while block", a == null ? null : a.Name, "y_");
        a = At("void A::F() {\n  std::sort(v.begin(), v.end(), [](int a, int b) { return a < b; });\n  |z_ = 3;\n}");
        Eq("after lambda call", a == null ? null : a.Name, "z_");
        a = At("void A::F() {\n  foo(1);|\n}");
        Eq("not assignment", a, null);

        Console.WriteLine("pass=" + pass + " fail=" + fail);
        int f2 = SyncTests.Run();
        Environment.Exit(fail == 0 && f2 == 0 ? 0 : 1);
    }
}
