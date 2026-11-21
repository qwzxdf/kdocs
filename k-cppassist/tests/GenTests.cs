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

        // ---- #include の自動追加: 空行がないのに、グループが分かれていると見て空行を足さない ----
        {
            string src = "#include \"a.h\"\n#ifdef _WIN32\n#include <windows.h>\n#endif\n#include \"b.h\"\n\nvoid f() {}\n";
            var e = IncludeEditor.Plan(src, "<vector>", "a", "\n");
            string r = e == null ? "(null)" : src.Insert(e.Position, e.Text);
            Check("include: no blank lines in an unbroken block", r.Contains("\n\n#include <vector>") || r.Contains("<vector>\n\n#include") ? r : "ok", "ok");
            string src2 = "#include \"a.h\"\n\n#include <vector>\n\nvoid f() {}\n";
            var e2 = IncludeEditor.Plan(src2, "<windows.h>", "a", "\n");
            Check("include: new group between groups", e2 == null ? "(null)" : src2.Insert(e2.Position, e2.Text),
                "#include \"a.h\"\n\n#include <vector>\n\n#include <windows.h>\n\nvoid f() {}\n");
        }

        // ---- レビューで直した所 ----
        // switch: 別名の列挙子は case を作らない
        Check("switch: alias not added",
            Sw("enum class Dir { Up, Down, First = Up };\nvoid f(Dir d) {\n  switch (d) {\n    case Dir::Up:\n      break;\n  }\n}\n", "switch"),
            "enum class Dir { Up, Down, First = Up };\nvoid f(Dir d) {\n  switch (d) {\n    case Dir::Up:\n      break;\n    case Dir::Down:\n      break;\n  }\n}\n");
        Check("switch: alias label covers its target",
            Sw("enum class Dir { Up, Down, First = Up };\nvoid f(Dir d) {\n  switch (d) {\n    case Dir::First:\n      break;\n  }\n}\n", "switch"),
            "enum class Dir { Up, Down, First = Up };\nvoid f(Dir d) {\n  switch (d) {\n    case Dir::First:\n      break;\n    case Dir::Down:\n      break;\n  }\n}\n");
        // switch: default へ落ちる case の間には入れない
        Check("switch: fallthrough into default keeps order",
            Sw("enum class S { A, B, C };\nvoid f(S s) {\n  switch (s) {\n    case S::A:\n      Prep();\n    default:\n      Run();\n      break;\n  }\n}\n", "switch"),
            "enum class S { A, B, C };\nvoid f(S s) {\n  switch (s) {\n    case S::A:\n      Prep();\n    default:\n      Run();\n      break;\n    case S::B:\n      break;\n    case S::C:\n      break;\n  }\n}\n");
        Check("switch: after break goes before default",
            Sw("enum class S { A, B };\nvoid f(S s) {\n  switch (s) {\n    case S::A:\n      Prep();\n      break;\n    default:\n      break;\n  }\n}\n", "switch"),
            "enum class S { A, B };\nvoid f(S s) {\n  switch (s) {\n    case S::A:\n      Prep();\n      break;\n    case S::B:\n      break;\n    default:\n      break;\n  }\n}\n");
        Check("switch: grouped label before default is fallthrough",
            SwitchGen.EndsFlow("{ case X: ", 1, 10).ToString(), "False");
        Check("switch: return ends flow", SwitchGen.EndsFlow("{ case X: return 1; ", 1, 20).ToString(), "True");

        // コンストラクター: std::function のメンバーを落とさない
        Check("ctor: std::function member",
            Ctor("class Button {\n  std::string label_;\n  std::function<void()> on_click_;\n};\n", "label_"),
            "class Button {\n public:\n  Button(const std::string& label, const std::function<void()>& on_click)\n      : label_(label), on_click_(on_click) {}\n\n private:\n  std::string label_;\n  std::function<void()> on_click_;\n};\n");
        Check("ctor: paren outside angles", CtorGen.ParenOutsideAngles("void Run(int a)").ToString(), "True");
        Check("ctor: paren inside angles", CtorGen.ParenOutsideAngles("std::function<void(int)> cb_").ToString(), "False");

        // override: final の関数は足さない
        Check("override: final skipped",
            Ov("class Boss : public Enemy {\n public:\n  void Draw() const override;\n};\n", "Draw",
               "class Enemy {\n public:\n  void Update(float dt) override final;\n  virtual void Draw() const;\n  virtual void Hit(int n);\n};\n"),
            "class Boss : public Enemy {\n public:\n  void Hit(int n) override;\n\n  void Draw() const override;\n};\n");

        // 関数作成: 別の関数の同じ名前の変数を見ない
        Check("usage: other function's variable ignored",
            Us("void A() {\n  float speed = 1;\n}\nvoid B(int speed) {\n  Move(speed);\n}\n", "Move"),
            "void Move(int speed)");

        // 定義の雛形: 入れ子の型を修飾する、static の関数は作らない
        {
            string h = "class Player {\n public:\n  enum class State { Idle, Run };\n  struct Info { int hp; };\n  State GetState() const;\n  std::vector<Info> Infos();\n  int Count();\n};\n";
            Func<string, string> def = name =>
            {
                var sig = FunctionScan.Scan(h).First(s => s.Name == name);
                string why;
                var e = DefinitionGen.PlanDefinition(h, sig, "", "\n", out why);
                return e == null ? "!" + why : e.Text.Split('\n')[0];
            };
            Check("def: nested enum return", def("GetState"), "Player::State Player::GetState() const");
            Check("def: nested in template arg", def("Infos"), "std::vector<Player::Info> Player::Infos()");
            Check("def: plain return untouched", def("Count"), "int Player::Count()");
            string hs = "static float Lerp(float a, float b, float t);\n";
            var ss = FunctionScan.Scan(hs).First();
            string w;
            Check("def: static free function refused", DefinitionGen.PlanDefinition(hs, ss, "", "\n", out w) == null ? "null" : "made", "null");
        }

        // #include: pch.h より前に入れない、整理で pch.h を先頭に残す、SDK の <> は並べ替えない
        {
            var e = IncludeEditor.Plan("#include \"pch.h\"\n#include \"Player.h\"\n\nvoid f() {}\n", "<vector>", "Player", "\n");
            Check("include: after pch", e == null ? "(null)" : "#include \"pch.h\"\n#include \"Player.h\"\n\nvoid f() {}\n".Insert(e.Position, e.Text),
                "#include \"pch.h\"\n#include <vector>\n#include \"Player.h\"\n\nvoid f() {}\n");
            Check("tidy: pch stays first",
                IncludeTidy.Organize("#include \"pch.h\"\n#include \"Player.h\"\n#include <vector>\n", "Player", "\n"),
                "#include \"pch.h\"\n\n#include \"Player.h\"\n\n#include <vector>\n");
            Check("tidy: sdk order kept",
                IncludeTidy.Organize("#include <windows.h>\n#include <mmsystem.h>\n#include <vector>\n", null, "\n"),
                "#include <vector>\n\n#include <windows.h>\n#include <mmsystem.h>\n");
            Func<IncludeTidy.Item, ISet<string>> prov = it => new HashSet<string> { "Nothing" };
            Check("unused: pch kept", string.Join(",", IncludeTidy.Unused("#include \"pch.h\"\nint x;\n", null, prov).Select(i => i.Path)), "");
        }

        // ---- 3 回目のレビュー ----
        Check("mask: wide char literal keeps braces", CppText.Mask("if (c == L'a') { Jump(); }"), "if (c == L   ) { Jump(); }");
        Check("mask: u8 char literal", CppText.Mask("char c = u8'x'; int y;"), "char c = u8   ; int y;");
        Check("mask: digit separator", CppText.Mask("int n = 1'000'000;"), "int n = 1'000'000;");
        Check("mask: hex separator", CppText.Mask("int n = 0xFF'FF;"), "int n = 0xFF'FF;");
        {
            string header = "#pragma once\n#include \"Enemy.h\"\nclass Ai {\n  Enemy* target_;\n  void Chase() { target_->Move(); }\n};\n";
            var inc = IncludeTidy.Parse(header).First();
            string why;
            var r = ForwardDecl.Make(header, inc, ForwardDecl.Types("class Enemy {};\n"), new HashSet<string> { "Enemy" }, "\n", out why);
            Check("fwd: pointer used in inline body refused", r == null ? "null" : "made", "null");
            string ok = "#pragma once\n#include \"Enemy.h\"\nclass Ai {\n  Enemy* target_;\n  void Set(Enemy* e) { target_ = e; }\n};\n";
            var r2 = ForwardDecl.Make(ok, IncludeTidy.Parse(ok).First(), ForwardDecl.Types("class Enemy {};\n"), new HashSet<string> { "Enemy" }, "\n", out why);
            Check("fwd: pointer only stored is fine", r2 == null ? "null: " + why : "made", "made");
        }
        {
            string s = "struct Vertex {\n  float x;\n};\n";
            var e = HeaderEditor.PlanAt(s, s.IndexOf('{'), "float z;", "\n");
            Check("alt+w: struct without specifiers stays public", s.Insert(e.Position, e.Text), "struct Vertex {\n  float x;\n  float z;\n};\n");
            string c = "class Player {\n public:\n  void F();\n};\n";
            var e2 = HeaderEditor.PlanAt(c, c.IndexOf('{'), "int hp_;", "\n");
            Check("alt+w: class gets private", c.Insert(e2.Position, e2.Text), "class Player {\n public:\n  void F();\n\n private:\n  int hp_;\n};\n");
        }
        {
            var bx = ExprType.SplitBinary("offset + count");
            Check("type: long + unsigned int is unsigned long on MSVC", ExprType.BinaryResult(bx, new List<string> { "LONG", "UINT" }), "unsigned long");
            Check("type: long + int stays long", ExprType.BinaryResult(bx, new List<string> { "long", "int" }), "long");
        }

        // ---- 文字コードをそろえる ----
        {
            var sjis = System.Text.Encoding.GetEncoding(932);
            byte[] sj = sjis.GetBytes("// 体力\r\nint hp;\r\n");
            var info = EncodingTool.Detect(sj);
            Check("enc: detect shift-jis", info.Kind + " " + info.EolName, "ShiftJis CRLF");
            Check("enc: detect ascii", EncodingTool.Detect(System.Text.Encoding.ASCII.GetBytes("int x;\nint y;\n")).Kind + "", "Ascii");
            Check("enc: detect utf-8 bom", EncodingTool.Detect(new byte[] { 0xEF, 0xBB, 0xBF, (byte)'a' }).Kind + "", "Utf8Bom");
            Check("enc: detect mixed eol", EncodingTool.EolOf("a\r\nb\nc"), "混在");

            var p = EncodingTool.PlanFile(sj, EncodingTool.Target.Utf8Bom, EncodingTool.Eol.Keep);
            Check("enc: sjis to utf-8 bom", p.NewBytes != null && p.NewBytes[0] == 0xEF && new System.Text.UTF8Encoding(false).GetString(p.NewBytes, 3, p.NewBytes.Length - 3) == "// 体力\r\nint hp;\r\n" ? "ok" : "ng", "ok");
            Check("enc: ascii already utf-8", EncodingTool.PlanFile(System.Text.Encoding.ASCII.GetBytes("int x;\n"), EncodingTool.Target.Utf8, EncodingTool.Eol.Keep).Action, "そのまま");
            Check("enc: ascii needs bom", EncodingTool.PlanFile(System.Text.Encoding.ASCII.GetBytes("int x;\n"), EncodingTool.Target.Utf8Bom, EncodingTool.Eol.Keep).NewBytes != null ? "convert" : "keep", "convert");
            var lf = EncodingTool.PlanFile(System.Text.Encoding.ASCII.GetBytes("a\r\nb\r\n"), EncodingTool.Target.Utf8, EncodingTool.Eol.Lf);
            Check("enc: eol only", lf.NewBytes == null ? "null" : System.Text.Encoding.ASCII.GetString(lf.NewBytes) + "|" + lf.Action, "a\nb\n|改行 CRLF → LF");
            var emoji = EncodingTool.PlanFile(new System.Text.UTF8Encoding(false).GetBytes("// 😀 ok\n"), EncodingTool.Target.ShiftJis, EncodingTool.Eol.Keep);
            Check("enc: emoji blocks shift-jis", emoji.Blocked + " " + emoji.Action.Contains("😀"), "True True");
            Check("enc: binary", EncodingTool.Detect(new byte[] { 1, 0, 2, 3 }).Kind + "", "Binary");

            Check("editorconfig: header", EncodingTool.SectionHeader(new[] { ".h", ".cpp", "hpp" }), "[*.{h,cpp,hpp}]");
            Check("editorconfig: new file",
                EncodingTool.UpdateEditorConfig("", "[*.{h,cpp}]", "utf-8-bom", "crlf", "\n"),
                "# K-CppAssist が書きました。Visual Studio は、保存するときに、この文字コードと改行を使います\n[*.{h,cpp}]\ncharset = utf-8-bom\nend_of_line = crlf\n");
            Check("editorconfig: update existing section",
                EncodingTool.UpdateEditorConfig("root = true\n\n[*.{h,cpp}]\nindent_style = space\ncharset = latin1\n\n[*.md]\ncharset = utf-8\n", "[*.{h,cpp}]", "utf-8-bom", null, "\n"),
                "root = true\n\n[*.{h,cpp}]\nindent_style = space\ncharset = utf-8-bom\n\n[*.md]\ncharset = utf-8\n");
            Check("editorconfig: add key to section",
                EncodingTool.UpdateEditorConfig("[*.{h,cpp}]\nindent_size = 4\n\n[*.md]\n", "[*.{h,cpp}]", "utf-8", "lf", "\n"),
                "[*.{h,cpp}]\nindent_size = 4\ncharset = utf-8\nend_of_line = lf\n\n[*.md]\n");
            Check("editorconfig: append section",
                EncodingTool.UpdateEditorConfig("root = true\n", "[*.h]", "utf-8", null, "\n"),
                "root = true\n\n[*.h]\ncharset = utf-8\n");
        }


        // ---- 新しいファイルのひな形 ----
        {
            Check("name: same as file", NewFileGen.ClassName("game_object", NewFileGen.Naming.SameAsFile), "game_object");
            Check("name: pascal from snake", NewFileGen.ClassName("game_object", NewFileGen.Naming.Pascal), "GameObject");
            Check("name: snake from pascal", NewFileGen.ClassName("GameObject", NewFileGen.Naming.Snake), "game_object");
            Check("name: camel", NewFileGen.ClassName("game-object", NewFileGen.Naming.Camel), "gameObject");
            Check("name: acronym", NewFileGen.ClassName("HTTPServer", NewFileGen.Naming.Snake), "http_server");
            Check("name: digit start", NewFileGen.ClassName("3dModel", NewFileGen.Naming.SameAsFile), "_3dModel");
            Check("ns: most common", NewFileGen.DetectNamespace(new[] { "namespace Prest {\nint a;\n}\n", "namespace Prest {\n}\n", "namespace Other {\n}\n" }), "Prest");
            Check("ns: none", NewFileGen.DetectNamespace(new[] { "int a;\n" }), "");
            Check("ns: ignores std and nested", NewFileGen.DetectNamespace(new[] { "namespace std {\n}\nnamespace A::B {\n  namespace c {\n  }\n}\n" }), "A::B");
            Check("indent: tab", NewFileGen.DetectIndent(new[] { "class A {\n\tint a;\n\tint b;\n\tint c;\n\tint d;\n\tint e;\n};\n" }), "\t");
            Check("indent: 4 spaces", NewFileGen.DetectIndent(new[] { "class A {\n    int a;\n    int b;\n    int c;\n    int d;\n    int e;\n};\n" }), "    ");
            var o = new NewFileGen.Options { Namespace = "Prest", Indent = "\t", Eol = "\n", NamespaceComment = true };
            int caret;
            string h = NewFileGen.Header("game_object", o, out caret);
            Check("header: pragma once class", h, "#pragma once\n\nnamespace Prest {\n\nclass game_object {\npublic:\n\t\n};\n\n}  // namespace Prest\n");
            Check("header: caret on the empty line", h.Substring(caret - 1, 2), "\t\n");
            o.Naming = NewFileGen.Naming.Pascal; o.Namespace = ""; o.Guard = NewFileGen.Guard.IncludeGuard;
            Check("header: include guard, no namespace", NewFileGen.Header("game_object", o, out caret),
                "#ifndef GAME_OBJECT_H_\n#define GAME_OBJECT_H_\n\nclass GameObject {\npublic:\n\t\n};\n\n\n#endif  // GAME_OBJECT_H_\n");
            o = new NewFileGen.Options { Namespace = "A::B", MakeClass = false, Eol = "\n", NamespaceComment = false };
            Check("header: no class", NewFileGen.Header("x", o, out caret), "#pragma once\n\nnamespace A::B {\n\n\n}\n");
            o = new NewFileGen.Options { Namespace = "Prest", Eol = "\n", NamespaceComment = true };
            Check("source", NewFileGen.Source("Foo.h", o), "#include \"Foo.h\"\n\nnamespace Prest {\n\n\n}  // namespace Prest\n");
            Check("source: no header, no namespace", NewFileGen.Source(null, new NewFileGen.Options { Eol = "\n" }), "");
        }

        // ---- クラス名の上の電球 ----
        {
            string code = "class Foo {\npublic:\n\tint a;\n};\n";
            string why;
            var ch = Refactor.Make("ctordtor", code, 3, "\n", true, out why);
            string res = ch == null ? why : ch.Apply(code);
            Check("ctordtor: declares both", res.Contains("Foo();") && res.Contains("~Foo();") ? "ok" : res, "ok");
            string done = "class Foo {\npublic:\n\tFoo();\n\t~Foo();\n};\n";
            Check("ctordtor: already there", Refactor.Make("ctordtor", done, 3, "\n", true, out why) == null ? "null" : "made", "null");
            var nc = Refactor.Make("nocopymove", code, 3, "\n", true, out why);
            res = nc == null ? why : nc.Apply(code);
            Check("nocopymove: four deletes", res.Contains("Foo(const Foo&) = delete;") && res.Contains("Foo& operator=(const Foo&) = delete;") && res.Contains("Foo(Foo&&) = delete;") && res.Contains("Foo& operator=(Foo&&) = delete;") ? "ok" : res, "ok");
            Check("onhead: class line", ClassGen.OnHead(code, 3) ? "y" : "n", "y");
            Check("onhead: member line", ClassGen.OnHead(code, code.IndexOf("int a")) ? "y" : "n", "n");
            Check("offers: head shows ctordtor", Refactor.Offers(code, 3, "\n", true).Any(x => x.Id == "ctordtor") ? "y" : "n", "y");
            Check("offers: body hides ctordtor", Refactor.Offers(code, code.IndexOf("int a"), "\n", true).Any(x => x.Id == "ctordtor") ? "y" : "n", "n");
        }

        // ---- switch を打ったら、case と default を自動で入れる ----
        {
            string src = "enum class State { Idle, Walk, Run };\nvoid F(State s) {\n\tswitch (s) {\n\t\n\t}\n}\n";
            int caret2 = src.IndexOf("\t\n\t}") + 1;
            Check("autoswitch: empty body detected", SwitchGen.BodyEmptyAt(src, caret2) ? "y" : "n", "y");
            string why2;
            var en = SwitchGen.ParseEnums(src);
            var pl = SwitchGen.Make(src, caret2, en, "\n", out why2, true);
            string outText = pl == null ? why2 : src.Remove(pl.Position, pl.Length).Insert(pl.Position, pl.Text);
            Check("autoswitch: cases and default, tab indent",
                outText,
                "enum class State { Idle, Walk, Run };\nvoid F(State s) {\n\tswitch (s) {\n\t\tcase State::Idle:\n\t\t\tbreak;\n\t\tcase State::Walk:\n\t\t\tbreak;\n\t\tcase State::Run:\n\t\t\tbreak;\n\t\tdefault:\n\t\t\tbreak;\n\t}\n}\n");
            string plain = "enum Color { Red, Green };\nvoid G(Color c) {\n  switch (c) {}\n}\n";
            var pl2 = SwitchGen.Make(plain, plain.IndexOf("{}") + 1, SwitchGen.ParseEnums(plain), "\n", out why2, true);
            string out2 = pl2 == null ? why2 : plain.Remove(pl2.Position, pl2.Length).Insert(pl2.Position, pl2.Text);
            Check("autoswitch: plain enum, one-line body", out2.Contains("case Red:") && out2.Contains("case Green:") && out2.Contains("default:") ? "ok" : out2, "ok");
            string filled = "enum class State { Idle, Walk };\nvoid H(State s) {\n\tswitch (s) {\n\tcase State::Idle:\n\t\tbreak;\n\t}\n}\n";
            Check("autoswitch: not empty -> not triggered", SwitchGen.BodyEmptyAt(filled, filled.IndexOf("case")) ? "y" : "n", "n");
            string nodef = "enum class State { Idle };\nvoid K(State s) {\n\tswitch (s) {\n\tcase State::Idle:\n\t\tbreak;\n\t}\n}\n";
            var pl3 = SwitchGen.Make(nodef, nodef.IndexOf("case"), SwitchGen.ParseEnums(nodef), "\n", out why2, true);
            Check("autoswitch: default only when all cases exist", pl3 != null && pl3.Added.Count == 0 && pl3.AddedDefault ? "ok" : "ng", "ok");
            Check("autoswitch: no default requested -> nothing to add", SwitchGen.Make(nodef, nodef.IndexOf("case"), SwitchGen.ParseEnums(nodef), "\n", out why2) == null ? "null" : "made", "null");
            string ints = "void M(int n) {\n\tswitch (n) {\n\t\n\t}\n}\n";
            Check("autoswitch: int switch -> no plan", SwitchGen.Make(ints, ints.IndexOf("\t\n\t}") + 1, new List<SwitchGen.EnumDef>(), "\n", out why2, true) == null ? "null" : "made", "null");
        }

        Console.WriteLine("gen: " + pass + " passed, " + fail + " failed");
        return fail;
    }
}
