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

    static string Ov(string text, string marker, string other)
    {
        int caret = text.IndexOf(marker, StringComparison.Ordinal);
        string why;
        var p = OverrideGen.Make(text, caret, new List<string> { other }, "\n", out why);
        if (p == null) return "!" + why;
        return text.Insert(p.Position, p.Text);
    }

    static string Us(string text, string marker)
    {
        string why;
        var u = UsageGen.Find(text, text.IndexOf(marker, StringComparison.Ordinal), out why);
        if (u == null) return "!" + why;
        string s = u.Signature();
        if (u.Unknown.Count > 0) s += " |unknown=" + string.Join(",", u.Unknown);
        if (u.ReturnGuessed) s += " |guessed";
        if (u.Receiver != null) s += " |recv=" + u.Receiver + (u.ReceiverType != null ? " type=" + u.ReceiverType : "");
        return s;
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

        // ---- override ----
        string baseH =
            "class Shape {\n" +
            " public:\n" +
            "  virtual ~Shape() = default;\n" +
            "  virtual void Draw(Renderer& r, int layer = 0) const = 0;\n" +
            "  virtual float Area() const = 0;\n" +
            "  virtual void Update(float dt) {}\n" +
            "  void NotVirtual();\n" +
            "};\n";
        string d1 =
            "class Circle : public Shape {\n" +
            " public:\n" +
            "  Circle(float r);\n" +
            "\n" +
            " private:\n" +
            "  float r_;\n" +
            "};\n";
        Check("override: pure virtuals only", Ov(d1, "Circle(", baseH),
            "class Circle : public Shape {\n" +
            " public:\n" +
            "  void Draw(Renderer& r, int layer) const override;\n" +
            "  float Area() const override;\n" +
            "\n" +
            "  Circle(float r);\n" +
            "\n" +
            " private:\n" +
            "  float r_;\n" +
            "};\n");

        string d2 =
            "class Circle : public Shape {\n" +
            " public:\n" +
            "  void Draw(Renderer& r, int layer) const override;\n" +
            "  float Area() const override;\n" +
            "};\n";
        Check("override: remaining non-pure virtuals", Ov(d2, "Draw", baseH),
            "class Circle : public Shape {\n" +
            " public:\n" +
            "  void Update(float dt) override;\n" +
            "\n" +
            "  void Draw(Renderer& r, int layer) const override;\n" +
            "  float Area() const override;\n" +
            "};\n");

        string d3 = "struct Sq : Shape {\n  float w;\n};\n";
        string r3 = Ov(d3, "float w", baseH);
        Check("override: struct, default public", r3.StartsWith("struct Sq : Shape {\n  void Draw(Renderer& r, int layer) const override;\n  float Area() const override;\n\n  float w;") ? "ok" : r3, "ok");

        // 2 段の継承: 孫は、祖父の仮想関数も対象
        string mid = "class Mid : public Shape {\n public:\n  float Area() const override;\n};\n";
        string d4 = "class Leaf : public Mid {\n  int x;\n};\n";
        string r4o = Ov(d4, "int x", baseH + mid);
        Check("override: through two levels", r4o.Contains("void Draw(Renderer& r, int layer) const override;") ? "ok" : r4o, "ok");

        Check("override: no base", Ov("class A {\n  int x;\n};\n", "int x", baseH), "!基底クラスがありません。class A : public Base の形にしてください");
        Check("override: base not found", Ov("class A : public Zzz {\n  int x;\n};\n", "int x", baseH), "!基底クラスの定義が見つかりません (Zzz)");
        Check("override: all done", Ov("class A : public Shape {\n public:\n  void Draw(Renderer& r, int layer) const override;\n  float Area() const override;\n  void Update(float dt) override;\n};\n", "Draw", baseH), "!足りない仮想関数はありません");

        // ---- 使用箇所から関数を作る ----
        string u1 =
            "void Player::Update(float dt) {\n" +
            "  int hp = 3;\n" +
            "  std::string name = \"a\";\n" +
            "  Heal(hp, name, 2.5f, dt);\n" +
            "}\n";
        Check("usage: statement call", Us(u1, "Heal"), "void Heal(int hp, const std::string& name, float arg3, float dt)");
        Check("usage: args unknown", Us("void f() {\n  Foo(bar(), x + 1);\n}\n", "Foo"), "void Foo(int arg1, int arg2) |unknown=bar(),x + 1");
        Check("usage: bool from if", Us("void f() {\n  if (IsDead(3)) {}\n}\n", "IsDead"), "bool IsDead(int arg1)");
        Check("usage: bool from !", Us("void f() {\n  bool b = !IsDead(3);\n}\n", "IsDead"), "bool IsDead(int arg1)");
        Check("usage: type from declaration", Us("void f() {\n  float x = GetSpeed();\n}\n", "GetSpeed"), "float GetSpeed()");
        Check("usage: type from assignment", Us("void f() {\n  double d;\n  d = Calc(1);\n}\n", "Calc"), "double Calc(int arg1)");
        Check("usage: auto is unknown", Us("void f() {\n  auto x = Calc(1);\n}\n", "Calc"), "int Calc(int arg1) |guessed");
        Check("usage: return type", Us("float Speed() {\n  return Calc();\n}\n", "Calc"), "float Calc()");
        Check("usage: receiver", Us("void f(Enemy& e) {\n  e.Hit(5);\n}\n", "Hit"), "void Hit(int arg1) |recv=e. type=Enemy");
        Check("usage: pointer receiver", Us("void f() {\n  std::unique_ptr<Enemy> e;\n  e->Hit();\n}\n", "Hit"), "void Hit() |recv=e-> type=Enemy");
        Check("usage: not a call", Us("void f() {\n  int x = 3;\n}\n", "x = 3"), "!カーソルの行に、関数の呼び出しが見つかりません");
        Check("usage: declaration with parens is not a call", Us("void f() {\n  std::string s(\"a\");\n}\n", "std::string"), "!カーソルの行に、関数の呼び出しが見つかりません");
        string fd; int fpos;
        {
            string src = "void A() {}\n\nvoid B() {\n  Foo(1);\n}\n";
            string why2; var u = UsageGen.Find(src, src.IndexOf("Foo"), out why2);
            UsageGen.PlanFreeDefinition(src, src.IndexOf("void B"), u, "\n", out fpos, out fd);
            Check("usage: free definition", src.Insert(fpos, fd), "void A() {}\n\nvoid Foo(int arg1) {\n  // TODO: Foo を実装する\n}\n\nvoid B() {\n  Foo(1);\n}\n");
        }

        Console.WriteLine("gen: " + pass + " passed, " + fail + " failed");
        return fail;
    }
}
