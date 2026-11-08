using System;
using System.Collections.Generic;
using System.Linq;
using KCppAssist;

/// <summary>switch の足りない case を足す(SwitchGen)と、コンストラクター生成(CtorGen)のテスト。</summary>
static class GenTests
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

    static string Sw(string text, string marker, string extra = null)
    {
        int caret = text.IndexOf(marker, StringComparison.Ordinal);
        var enums = SwitchGen.ParseEnums(text + (extra ?? ""));
        string why;
        var p = SwitchGen.Make(text, caret, enums, "\n", out why);
        if (p == null) return "!" + why;
        return text.Insert(p.Position, p.Text);
    }

    static string Ctor(string text, string marker)
    {
        int caret = text.IndexOf(marker, StringComparison.Ordinal);
        string why;
        var p = CtorGen.Make(text, caret, "\n", out why);
        if (p == null) return "!" + why;
        return text.Insert(p.Position, p.Text);
    }

    public static int Run()
    {
        // ---- ParseEnums ----
        var es = SwitchGen.ParseEnums("namespace game {\nenum class State { Idle, Walk = 2, Run };\nenum Color : int { Red, Green };\n}\n");
        Check("enum count", es.Count.ToString(), "2");
        Check("enum scoped", es[0].Scoped + "," + es[0].Name + "," + string.Join("|", es[0].Values) + "," + string.Join("::", es[0].Chain), "True,State,Idle|Walk|Run,game");
        Check("enum plain with base", es[1].Scoped + "," + string.Join("|", es[1].Values), "False,Red|Green");

        // ---- switch: case を足す ----
        string a =
            "enum class State { Idle, Walk, Run };\n" +
            "void f(State s) {\n" +
            "  switch (s) {\n" +
            "    case State::Idle:\n" +
            "      break;\n" +
            "  }\n" +
            "}\n";
        Check("scoped enum from labels", Sw(a, "switch"),
            "enum class State { Idle, Walk, Run };\n" +
            "void f(State s) {\n" +
            "  switch (s) {\n" +
            "    case State::Idle:\n" +
            "      break;\n" +
            "    case State::Walk:\n" +
            "      break;\n" +
            "    case State::Run:\n" +
            "      break;\n" +
            "  }\n" +
            "}\n");

        string b =
            "enum Color { Red, Green, Blue, ColorCount };\n" +
            "void g(Color c) {\n" +
            "  switch (c) {\n" +
            "    case Red: break;\n" +
            "    default: break;\n" +
            "  }\n" +
            "}\n";
        Check("before default, sentinel skipped", Sw(b, "switch"),
            "enum Color { Red, Green, Blue, ColorCount };\n" +
            "void g(Color c) {\n" +
            "  switch (c) {\n" +
            "    case Red: break;\n" +
            "    case Green:\n" +
            "      break;\n" +
            "    case Blue:\n" +
            "      break;\n" +
            "    default: break;\n" +
            "  }\n" +
            "}\n");

        string c2 =
            "enum class Dir { Up, Down };\n" +
            "void h(Dir d) {\n" +
            "  switch (d) {\n" +
            "  }\n" +
            "}\n";
        Check("empty switch: type from the parameter", Sw(c2, "switch"),
            "enum class Dir { Up, Down };\n" +
            "void h(Dir d) {\n" +
            "  switch (d) {\n" +
            "    case Dir::Up:\n" +
            "      break;\n" +
            "    case Dir::Down:\n" +
            "      break;\n" +
            "  }\n" +
            "}\n");

        Check("all covered", Sw(
            "enum class E { A, B };\nvoid f(E e) {\n  switch (e) {\n    case E::A: break;\n    case E::B: break;\n  }\n}\n", "switch"),
            "!足りない case はありません (E)");
        Check("not in a switch", Sw("enum class E { A };\nvoid f() {}\n", "void"), "!カーソルが、switch の中にありません");
        Check("unknown type", Sw("void f(int x) {\n  switch (x) {\n  }\n}\n", "switch"),
            "!enum の型を決められません。case を 1 つ書くか、変数の宣言が見える場所で試してください");

        // 修飾は、囲んでいる namespace の分を省く
        string d =
            "namespace game {\n" +
            "enum class Mode { On, Off };\n" +
            "void f(Mode m) {\n" +
            "  switch (m) {\n" +
            "  }\n" +
            "}\n" +
            "}\n";
        Check("qualifier relative to scope", Sw(d, "switch").Contains("case Mode::On:") ? "ok" : Sw(d, "switch"), "ok");

        // 別のファイル(ヘッダー)にある enum
        string e1 = "void f(Mode m) {\n  switch (m) {\n    case Mode::On: break;\n  }\n}\n";
        string hdr = "namespace game {\nenum class Mode { On, Off };\n}\n";
        Check("enum from another file", Sw(e1, "switch", hdr).Contains("case Mode::Off:") ? "ok" : Sw(e1, "switch", hdr), "ok");

        // 入れ子の switch は、いちばん内側
        string n =
            "enum class A { X, Y };\nenum class B { P, Q };\n" +
            "void f(A a, B b) {\n  switch (a) {\n    case A::X:\n      switch (b) {\n        case B::P: break;\n      }\n      break;\n  }\n}\n";
        string nr = Sw(n, "switch (b)");
        Check("inner switch", nr.Contains("case B::Q:") && !nr.Contains("case A::Y:") ? "ok" : nr, "ok");

        // ---- コンストラクター ----
        string k1 =
            "class Player {\n" +
            " public:\n" +
            "  void Update();\n" +
            "\n" +
            " private:\n" +
            "  std::string name_;\n" +
            "  int hp_ = 100;\n" +
            "  float speed_;\n" +
            "};\n";
        Check("class with public:", Ctor(k1, "Update"),
            "class Player {\n" +
            " public:\n" +
            "  Player(const std::string& name, int hp, float speed)\n" +
            "      : name_(name), hp_(hp), speed_(speed) {}\n" +
            "\n" +
            "  void Update();\n" +
            "\n" +
            " private:\n" +
            "  std::string name_;\n" +
            "  int hp_ = 100;\n" +
            "  float speed_;\n" +
            "};\n");

        string k2 =
            "struct Point {\n" +
            "  float x;\n" +
            "  float y;\n" +
            "};\n";
        Check("struct, two members", Ctor(k2, "float x"),
            "struct Point {\n" +
            "  Point(float x, float y) : x(x), y(y) {}\n" +
            "\n" +
            "  float x;\n" +
            "  float y;\n" +
            "};\n");

        string k3 =
            "class Counter {\n" +
            "  int count_;\n" +
            "};\n";
        Check("class with only private: explicit + restores private", Ctor(k3, "count_"),
            "class Counter {\n" +
            " public:\n" +
            "  explicit Counter(int count) : count_(count) {}\n" +
            "\n" +
            " private:\n" +
            "  int count_;\n" +
            "};\n");

        string k4 =
            "class Owner {\n" +
            " public:\n" +
            " private:\n" +
            "  std::unique_ptr<Foo> foo_;\n" +
            "  std::vector<int> v_;\n" +
            "  Foo* raw_;\n" +
            "  const int& ref_;\n" +
            "  static int count_;\n" +
            "  mutable int cache_;\n" +
            "  int arr_[4];\n" +
            "  int bits_ : 3;\n" +
            "  void Method();\n" +
            "  using X = int;\n" +
            "};\n";
        string r4 = Ctor(k4, "foo_");
        string r4h = r4.Substring(0, r4.IndexOf("private:", StringComparison.Ordinal));
        Check("param kinds", r4h.Contains("Owner(std::unique_ptr<Foo> foo,\n        const std::vector<int>& v,\n        Foo* raw,\n        const int& ref)")
            ? "ok" : r4, "ok");
        Check("move for unique_ptr", r4h.Contains("foo_(std::move(foo))") ? "ok" : r4, "ok");
        Check("static / mutable / array / bitfield skipped", r4h.Contains("count") || r4h.Contains("cache") || r4h.Contains("arr_(") || r4h.Contains("bits_(") ? r4 : "ok", "ok");

        // 長いときは折り返す
        string k5 =
            "struct Config {\n" +
            "  std::string windowTitle_;\n" +
            "  std::string assetDirectory_;\n" +
            "  int screenWidth_;\n" +
            "};\n";
        Check("wrapped", Ctor(k5, "windowTitle_"),
            "struct Config {\n" +
            "  Config(const std::string& windowTitle,\n" +
            "         const std::string& assetDirectory,\n" +
            "         int screenWidth)\n" +
            "      : windowTitle_(windowTitle),\n" +
            "        assetDirectory_(assetDirectory),\n" +
            "        screenWidth_(screenWidth) {}\n" +
            "\n" +
            "  std::string windowTitle_;\n" +
            "  std::string assetDirectory_;\n" +
            "  int screenWidth_;\n" +
            "};\n");

        // すでに同じ数の引数のコンストラクターがある
        string k6 = "struct S {\n  S(int a, int b) : a_(a), b_(b) {}\n  int a_;\n  int b_;\n};\n";
        Check("same-arity ctor exists", Ctor(k6, "S("), "!引数が 2 個のコンストラクターが、すでにあります");

        // 初期化リストの b{2} と本体を読み飛ばして、後ろのメンバーを拾う
        string k7 = "struct T {\n  T() : a_(1), b_{2} {}\n  int c_;\n  float d_;\n};\n";
        Check("init list with braces is skipped", Ctor(k7, "T()").Contains("T(int c, float d) : c_(c), d_(d) {}") ? "ok" : Ctor(k7, "T()"), "ok");

        Check("multi-declarator refused", Ctor("struct M {\n  int a, b;\n};\n", "int a"), "!1 行に複数のメンバーを宣言している行があります: int a, b");
        Check("no members", Ctor("struct N {\n  void f();\n};\n", "void"), "!データ メンバーが見つかりません");
        Check("not in class", Ctor("void f() {}\n", "void"), "!カーソルが、class / struct の中にありません");

        // 引数名: m_ 接頭辞と末尾の _
        string k8 = "struct U {\n  int m_value;\n  int size_;\n};\n";
        Check("param names", Ctor(k8, "m_value").Contains("U(int value, int size) : m_value(value), size_(size) {}") ? "ok" : Ctor(k8, "m_value"), "ok");

        Console.WriteLine("gen: " + pass + " passed, " + fail + " failed");
        return fail;
    }
}
