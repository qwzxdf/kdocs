using System;
using System.Collections.Generic;
using System.Linq;
using KCppAssist;

/// <summary>電球の書き換え(Refactor)と、クラスからの生成(ClassGen)のテスト。「|」がカーソル。</summary>
static class RefactorTests
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

    static void Has(string name, string got, params string[] parts)
    {
        foreach (string p in parts)
        {
            if (got != null && got.Contains(p)) { pass++; continue; }
            fail++;
            Console.WriteLine("FAIL " + name + ": missing [" + p.Replace("\n", "\\n") + "]");
            Console.WriteLine("  got : " + (got ?? "(null)").Replace("\n", "\\n"));
        }
    }

    static string R(string id, string src, bool header = false)
    {
        int c = src.IndexOf('|');
        string text = src.Remove(c, 1);
        string why;
        var ch = Refactor.Make(id, text, c, "\n", header, out why);
        return ch == null ? "!" + why : ch.Apply(text);
    }

    static List<string> Offers(string src, bool header = false)
    {
        int c = src.IndexOf('|');
        string text = src.Remove(c, 1);
        return Refactor.Offers(text, c, "\n", header).Select(o => o.Id).ToList();
    }

    public static int Run()
    {
        // ---- MemberScan ----
        var ci = MemberScan.At("struct V {\n  float x, y, z;\n  int* p, q;\n  XMFLOAT3 pos[2];\n  static int s;\n  void F();\n  int a = 1, b{2};\n};\n", 12);
        Check("scan names", string.Join(",", ci.Members.Select(m => m.Type + " " + m.Name + m.Array)), "float x,float y,float z,int* p,int q,XMFLOAT3 pos[2],int a,int b");
        var c2 = MemberScan.At("class A {\n public:\n  A(int v) : v_(v) {}\n  virtual void F() {}\n private:\n  int v_ = 0;\n};\n", 3);
        Check("scan access", c2.Members[0].Access + " " + c2.HasUserCtor + " " + c2.HasVirtual, "private True True");

        // ---- NULL / typedef / cast ----
        Check("nullptr", R("nullptr", "  p = NUL|L; q = NULL; // NULL\n  r = NULL;\n"), "  p = nullptr; q = nullptr; // NULL\n  r = NULL;\n");
        Check("nullptr file", R("nullptr-file", "  p = NUL|L;\n  r = NULL;\n"), "  p = nullptr;\n  r = nullptr;\n");
        Check("typedef", R("using", "typedef unsigned int| UINT32;  // 32 bit\n"), "using UINT32 = unsigned int;  // 32 bit\n");
        Check("typedef tmpl", R("using", "typedef std::map<int, std::string>| Table;\n"), "using Table = std::map<int, std::string>;\n");
        Check("typedef fn", R("using", "typedef void (*Callback|)(int, float);\n"), "using Callback = void (*)(int, float);\n");
        Check("typedef ptr", R("using", "typedef Foo* Fo|oPtr;\n"), "using FooPtr = Foo*;\n");
        Check("cast", R("cast", "  float r = (float)a / b + (int)v.size()|;\n"), "  float r = static_cast<float>(a) / b + static_cast<int>(v.size());\n");
        Check("cast paren", R("cast", "  x = (UINT)(a + b)|;\n"), "  x = static_cast<UINT>(a + b);\n");
        Check("cast chain", R("cast", "  x = (float)obj->items[i].w|;\n"), "  x = static_cast<float>(obj->items[i].w);\n");
        Check("cast sizeof", R("cast", "  n = sizeof(int)|;\n"), "!この行に、数の型への C のキャストがありません");
        Check("cast neg", R("cast", "  n = (int)-x|;\n"), "  n = static_cast<int>(-x);\n");

        // ---- 範囲 for ----
        Check("rangefor", R("rangefor", "  for (size_t i = 0; i < enemies_.size(); ++i) {|\n    enemies_[i].Update(dt);\n    Draw(enemies_[i]);\n  }\n"),
            "  for (auto& enemy : enemies_) {\n    enemy.Update(dt);\n    Draw(enemy);\n  }\n");
        Check("rangefor index used", R("rangefor", "  for (int i = 0; i < v.size(); i++) {|\n    v[i] = i;\n  }\n"), "!本体で i を、v[i] 以外にも使っています (番号が要るので、範囲 for にできません)");
        Check("rangefor erase", R("rangefor", "  for (int i = 0; i < v.size(); i++) {|\n    v[i].x = 0; v.push_back(v[i]);\n  }\n"), "!本体で v の要素を足し引きしています。範囲 for にすると、反復子が無効になります");
        Check("rangefor std::size", R("rangefor", "  for (int i = 0; i < std::size(items); i++) {|\n    sum += items[i];\n  }\n"), "  for (auto& item : items) {\n    sum += item;\n  }\n");
        Check("singular", Refactor.Singular("boxes") + " " + Refactor.Singular("m_list") + " " + Refactor.Singular("this->bodies_"), "box list_item body");

        // ---- if ----
        Check("negate ==", Refactor.Negate("a == b"), "a != b");
        Check("negate <", Refactor.Negate("hp < 0"), "hp >= 0");
        Check("negate !", Refactor.Negate("!IsAlive()"), "IsAlive()");
        Check("negate id", Refactor.Negate("ready"), "!ready");
        Check("negate &&", Refactor.Negate("a && b"), "!(a && b)");
        Check("negate tmpl", Refactor.Negate("x < y && z"), "!(x < y && z)");
        Check("negate ->", Refactor.Negate("p->hp > 0"), "p->hp <= 0");
        Check("negate <<", Refactor.Negate("(flags & (1 << 3))"), "!(flags & (1 << 3))");
        Check("invert", R("invertif", "  if (hp > 0) {|\n    Live();\n  } else {\n    Die();\n  }\n"), "  if (hp <= 0) {\n    Die();\n  } else {\n    Live();\n  }\n");
        Check("invert no else", R("invertif", "  if (hp > 0) {|\n    Live();\n  }\n"), "!else がない if です (早期 return のほうを使ってください)");
        Check("guard fn", R("guard", "void P::Update() {\n  if (alive_) {|\n    Move();\n    Shoot();\n  }\n}\n"), "void P::Update() {\n  if (!alive_) return;\n\n  Move();\n  Shoot();\n}\n");
        Check("guard loop", R("guard", "void F() {\n  for (auto& e : list) {\n    if (e.active) {|\n      e.Tick();\n    }\n  }\n}\n"), "void F() {\n  for (auto& e : list) {\n    if (!e.active) continue;\n\n    e.Tick();\n  }\n}\n");
        Check("guard nonvoid", R("guard", "int F() {\n  if (a) {|\n    return 1;\n  }\n}\n"), "!戻り値のある関数です。何を返すか決められないので、早期 return にできません");
        Check("guard not last", R("guard", "void F() {\n  if (a) {|\n    G();\n  }\n  H();\n}\n"), "!if の後ろに文が続いています。最後の文の if だけ早期 return にできます");

        // ---- auto ----
        Check("auto make_unique", R("auto", "  std::unique_ptr<Enemy> e = std::make_unique<Enemy>(1);|\n"), "  auto e = std::make_unique<Enemy>(1);\n");
        Check("auto new", R("auto", "  Enemy* e = new Enemy(1);|\n"), "  auto* e = new Enemy(1);\n");
        Check("auto iter", R("auto", "  std::vector<int>::iterator it = v.begin();|\n"), "  auto it = v.begin();\n");
        Check("auto cast", R("auto", "  const float f = static_cast<float>(n);|\n"), "  const auto f = static_cast<float>(n);\n");
        Check("auto refuse", R("auto", "  float f = 1;|\n"), "!右辺の型が float と同じだと言い切れません (auto にすると型が変わることがあります)");

        // ---- デバッグ出力 ----
        string dbg = R("dbg", "#include <Windows.h>\nvoid F() {\n  hp_ -= dam|age;\n}\n");
        Has("dbg", dbg, "  hp_ -= damage;\n  OutputDebugStringA(std::format(\"{}({}): hp_ = {}\\n\", __FILE__, __LINE__, hp_).c_str());  // KDBG\n", "#include <format>");
        Check("dbg clear", R("dbg-clear", "void F() {|\n  a = 1;\n  OutputDebugStringA(\"x\");  // KDBG\n}\n"), "void F() {\n  a = 1;\n}\n");

        // ---- 特殊メンバー関数・比較 ----
        Check("nocopy", R("nocopy", "class Tex|ture {\n public:\n  Texture(int w);\n};\n"),
            "class Texture {\n public:\n  Texture(int w);\n  Texture(const Texture&) = delete;\n  Texture& operator=(const Texture&) = delete;\n  Texture(Texture&&) noexcept = default;\n  Texture& operator=(Texture&&) noexcept = default;\n};\n");
        Has("nocopy default ctor", R("nocopy", "struct B|uf {\n  int n;\n};\n"), "  Buf() = default;\n");
        Has("rule5 virtual", R("rule5", "class Ba|se {\n public:\n  virtual void F();\n};\n"), "virtual ~Base() = default;", "Base(const Base&) = default;");
        Check("rule5 all", R("rule5", "class A| {\n public:\n  A();\n  ~A();\n  A(const A&);\n  A& operator=(const A&);\n  A(A&&);\n  A& operator=(A&&);\n};\n"), "!コピー・ムーブはすでに全部宣言してあります");
        Has("compare", R("compare", "#include <string>\nstruct P|t {\n  int x;\n  int y;\n};\n"), "  bool operator==(const Pt&) const = default;\n  auto operator<=>(const Pt&) const = default;\n", "#include <compare>");

        // ---- enum ----
        string es = R("enumstr", "namespace g {\nenum class Wea|pon { kSword, kBow = 3, kFirst = kSword };\n}\n");
        Has("enumstr", es, "constexpr std::string_view ToString(Weapon value) {", "case Weapon::kSword: return \"kSword\";", "case Weapon::kBow: return \"kBow\";",
            "constexpr std::optional<Weapon> WeaponFromString(std::string_view text) {", "if (text == \"kBow\") return Weapon::kBow;", "#include <optional>");
        Check("enumstr alias skipped", es.Contains("kFirst\"") ? "has" : "no", "no");
        Has("enumstr in class", R("enumstr", "class A {\n  enum State| { kIdle, kRun };\n};\n"), "static constexpr std::string_view ToString(State value)");

        // ---- formatter / hash ----
        string fm = R("formatter", "namespace game {\nstruct Hi|t {\n  XMFLOAT3 pos;\n  float damage;\n  Enemy* who;\n};\n}  // namespace game\n");
        Has("formatter", fm, "}  // namespace game\n\ntemplate <>", "struct std::formatter<game::Hit> {", "\"{{pos=({}, {}, {}), damage={}, who={}}}\"", "v.pos.x, v.pos.y, v.pos.z, v.damage, static_cast<const void*>(v.who)");
        Check("formatter private", R("formatter", "class A| {\n  int x_;\n};\n"), "!public のデータ メンバーがありません (formatter からは private を読めません)");
        Has("hash", R("hash", "struct Ke|y {\n  int x;\n  int y;\n};\n"), "struct std::hash<Key> {", "mix(std::hash<std::remove_cvref_t<decltype(v.y)>>{}(v.y));");

        // ---- JSON / cereal ----
        Has("json", R("json", "struct Sa|ve {\n  int level;\n  std::string name;\n  Foo* cache;\n};\n"), "NLOHMANN_DEFINE_TYPE_INTRUSIVE(Save, level, name)", "#include <nlohmann/json.hpp>");
        Has("cereal", R("cereal", "class Sa|ve {\n public:\n  int GetLevel() const;\n private:\n  int level_;\n};\n"), "  ar(CEREAL_NVP(level_));\n", " public:\n  int GetLevel() const;\n  template <class Archive>");

        // ---- 入力レイアウト ----
        string il = R("inputlayout", "#include <d3d12.h>\nstruct Ver|tex {\n  XMFLOAT3 position;\n  XMFLOAT3 normal;\n  XMFLOAT2 uv;\n  XMFLOAT2 uv2;\n};\n", true);
        Has("inputlayout", il, "inline constexpr D3D12_INPUT_ELEMENT_DESC kVertexInputLayout[] = {",
            "{\"POSITION\", 0, DXGI_FORMAT_R32G32B32_FLOAT, 0, offsetof(Vertex, position), D3D12_INPUT_CLASSIFICATION_PER_VERTEX_DATA, 0},",
            "{\"TEXCOORD\", 1, DXGI_FORMAT_R32G32_FLOAT, 0, offsetof(Vertex, uv2),");
        Has("inputlayout d3d11", R("inputlayout", "struct V| {\n  Vector3 pos;\n  Color color;\n};\n"), "constexpr D3D11_INPUT_ELEMENT_DESC kVInputLayout[] = {", "{\"COLOR\", 0, DXGI_FORMAT_R32G32B32A32_FLOAT");
        Check("inputlayout bad", R("inputlayout", "struct V| {\n  std::string s;\n};\n"), "!std::string s は、頂点の要素にできる型ではありません (float、XMFLOAT2〜4、Vector2〜4、uint32_t などにしてください)");

        // ---- 定数バッファ ----
        Check("cbuffer pad", R("cbuffer", "struct Cb| {\n  XMFLOAT4X4 world;\n  XMFLOAT3 light;\n  XMFLOAT3 color;\n  float power;\n};\n"),
            "struct Cb {\n  XMFLOAT4X4 world;\n  XMFLOAT3 light;\n  float pad0;\n  XMFLOAT3 color;\n  float power;\n};\nstatic_assert(sizeof(Cb) % 16 == 0, \"定数バッファの大きさは 16 の倍数にする\");\n");
        Has("cbuffer tail", R("cbuffer", "struct Cb| {\n  float time;\n};\n"), "  float time;\n  float pad0[3];\n");
        Check("cbuffer bool", R("cbuffer", "struct Cb| {\n  bool on;\n};\n"), "!on: bool は C++ で 1 バイト、HLSL で 4 バイトです。uint32_t か BOOL にしてください");
        Check("cbuffer arr", R("cbuffer", "struct Cb| {\n  float w[4];\n};\n"), "!w[4]: HLSL の配列は要素ごとに 16 バイトに広がるので、float の配列は並びが合いません。XMFLOAT4 の配列にしてください");
        Check("cbuffer ok", R("cbuffer", "struct Cb| {\n  XMFLOAT4 a;\n};\nstatic_assert(sizeof(Cb) % 16 == 0, \"\");\n"), "!Cb の並びは、HLSL と同じです (16 バイト)");
        Has("cbuffer float2 split", R("cbuffer", "struct Cb| {\n  XMFLOAT3 a;\n  XMFLOAT2 b;\n};\n"), "  XMFLOAT3 a;\n  float pad0;\n  XMFLOAT2 b;\n  float pad1[2];");

        // ---- 初期化子リスト ----
        Check("initorder", R("initorder", "class A {\n  A(int x) : c_(1), a_(x)|, b_(2) {}\n  int a_, b_, c_;\n};\n"), "class A {\n  A(int x) : a_(x), b_(2), c_(1) {}\n  int a_, b_, c_;\n};\n");
        Check("initorder base", R("initorder", "class A : public B {\n  A()| : b_(1), B(2), a_{3} {}\n  int a_;\n  int b_;\n};\n"), "class A : public B {\n  A() : B(2), a_{3}, b_(1) {}\n  int a_;\n  int b_;\n};\n");
        Check("initorder lines", R("initorder", "struct S {\n  S()|\n      : b(1),\n        a(2) {}\n  int a, b;\n};\n"), "struct S {\n  S()\n      : a(2),\n        b(1) {}\n  int a, b;\n};\n");
        string why;
        var cross = ClassGen.InitOrder("A::A() : y_(1), x_(2) {}\n", 3, "class A {\n  int x_;\n  int y_;\n};\n", out why);
        Check("initorder cpp", cross == null ? "!" + why : cross.Apply("A::A() : y_(1), x_(2) {}\n"), "A::A() : x_(2), y_(1) {}\n");


        // ---- クラスを別ファイルへ ----
        string hsrc = "#pragma once\n#include <vector>\n\nnamespace g {\n\n// 弾\nstruct Bul|let {\n  int x;\n};\n\nclass Gun {};\n\n}  // namespace g\n";
        int hc = hsrc.IndexOf('|'); string ht = hsrc.Remove(hc, 1);
        var ex = FileGen.ExtractClass(ht, hc, "Weapon.h", "\n", out why);
        Check("extract new", ex == null ? "!" + why : ex.NewHeader, "#pragma once\n\n#include <vector>\n\nnamespace g {\n\n// 弾\nstruct Bullet {\n  int x;\n};\n\n}\n");
        Check("extract old", ex == null ? "!" : ex.OldHeader.Apply(ht), "#pragma once\n#include <vector>\n#include \"Bullet.h\"\n\nnamespace g {\n\nclass Gun {};\n\n}  // namespace g\n");
        string cpp = "#include \"pch.h\"\n#include \"Weapon.h\"\n\nnamespace g {\n\n// 撃つ\nvoid Bullet::Fly() {\n  x++;\n}\n\nvoid Gun::Fire() {}\n\n}  // namespace g\n";
        var defs = FileGen.DefinitionsOf(cpp, "Bullet");
        Check("defs count", defs.Count.ToString(), "1");
        Check("new source", FileGen.NewSource(cpp, "Bullet", defs, "\n"), "#include \"pch.h\"\n#include \"Bullet.h\"\n\n#include \"Weapon.h\"\n\nnamespace g {\n\n// 撃つ\nvoid Bullet::Fly() {\n  x++;\n}\n\n}\n");
        string dh = "class A {\n public:\n  void F();\n  virtual void G() = 0;\n  A() = default;\n  int H() const;\n  void I() {}\n  friend void J();\n};\n";
        Check("declarations", string.Join(",", FileGen.Declarations(dh, Scopes.Parse(dh)[0]).Select(d => d.Name)), "F,H");

        // ---- Natvis ----
        var nc = MemberScan.At("namespace g {\nstruct P {\n  int x;\n  std::vector<int> v;\n};\n}\n", 20);
        string nv = ClassGen.NatvisMerge(null, nc.FullName, ClassGen.NatvisType(nc), "\n");
        Has("natvis new", nv, "<Type Name=\"g::P\">", "<DisplayString>{{x={x}, v={v}}}</DisplayString>", "</AutoVisualizer>");
        string nv2 = ClassGen.NatvisMerge(nv, "g::P", "  <Type Name=\"g::P\">\n    <DisplayString>new</DisplayString>\n  </Type>", "\n");
        Check("natvis replace", (nv2.Split(new[] { "<Type " }, StringSplitOptions.None).Length - 1) + " " + nv2.Contains("new</DisplayString>"), "1 True");

        // ---- 電球に出る項目 ----
        Check("offers class", string.Join(",", Offers("struct V| {\n  XMFLOAT3 pos;\n  float t;\n};\n", true)),
            "ctordtor-default,ctordtor-inline,nocopymove,nocopy,rule5,compare,formatter,hash,json,cereal,inputlayout,cbuffer");
        Check("offers on member line: no class items", string.Join(",", Offers("struct V {\n  XMFLOAT3 p|os;\n  float t;\n};\n", true)), "");
        Check("offers on empty line in class", string.Join(",", Offers("class V\n{\n|\n  std::unique_ptr<T> s_;\n};\n", true)), "ctordtor-default,ctordtor-inline,nocopymove,nocopy,rule5,compare,json,cereal");
        // コンストラクター・デストラクター: コピー・ムーブの宣言の上に置く。コピー・ムーブがあっても Foo() を作る
        string cm = "class E|\n{\npublic:\n\tE(const E&) = delete;\n\tE& operator=(const E&) = delete;\n\n\tint x_;\n};\n";
        Check("ctor default above copy", R("ctordtor-default", cm), "class E\n{\npublic:\n\tE() = default;\n\t~E() = default;\n\tE(const E&) = delete;\n\tE& operator=(const E&) = delete;\n\n\tint x_;\n};\n");
        Check("ctor inline", R("ctordtor-inline", "class A| {\n public:\n  void F();\n};\n"), "class A {\n public:\n  void F();\n  A() {}\n  ~A() {}\n};\n");
        Check("ctor declare (for cpp)", R("ctordtor", "class A| {\n public:\n  void F();\n};\n"), "class A {\n public:\n  void F();\n  A();\n  ~A();\n};\n");
        Check("offers if",string.Join(",", Offers("void F() {\n  if (a) {|\n    G();\n  }\n}\n")), "guard");

        // ---- pimpl ----
        {
            string ph = "#pragma once\n#include <string>\n\nnamespace Prest {\nclass Player {\npublic:\n    Player();\n    ~Player() = default;\n    int GetHp() const;\n    void Damage(int d);\nprivate:\n    int hp_ = 100;\n    std::string name_;\n};\n}\n";
            string pc = "#include \"Player.h\"\n\nnamespace Prest {\n\nPlayer::Player() : hp_(50), name_(\"p\")\n{\n}\n\nint Player::GetHp() const\n{\n    return hp_;\n}\n\nvoid Player::Damage(int d)\n{\n    this->hp_ -= d;\n}\n\n}\n";
            string pw;
            var pr = PimplGen.Make(ph, pc, ph.IndexOf("class Player"), "\n", out pw);
            Check("pimpl: made", pr == null ? "!" + pw : "ok", "ok");
            if (pr != null)
            {
                Has("pimpl: header", pr.Header, "    struct Impl;\n    std::unique_ptr<Impl> impl_;\n", "~Player();", "#include <memory>");
                Check("pimpl: header has no moved members", pr.Header.Contains("hp_") || pr.Header.Contains("name_") ? "found" : "none", "none");
                Has("pimpl: cpp", pr.Cpp,
                    "struct Player::Impl {\n    int hp_ = 100;\n    std::string name_;\n};\n\nPlayer::Player() : impl_(std::make_unique<Impl>())\n{\n    impl_->hp_ = 50;\n    impl_->name_ = \"p\";\n}",
                    "    return impl_->hp_;", "    impl_->hp_ -= d;", "Player::~Player() = default;");
            }
            // ヘッダーに本体のある関数がメンバーを使っていれば、作らない
            string ph2 = "class A {\npublic:\n    int Get() const { return v_; }\nprivate:\n    int v_;\n};\n";
            Check("pimpl: inline use refused", PimplGen.Make(ph2, "", ph2.IndexOf("class A"), "\n", out pw) == null ? "refused" : "made", "refused");
            // コンストラクターがないクラス: Foo() を足して、Impl を作る定義を置く
            string ph3 = "#include <memory>\nnamespace g {\nclass B {\npublic:\n    void F();\nprivate:\n    int n_ = 0;\n};\n}\n";
            string pc3 = "#include \"B.h\"\n\nnamespace g {\n\nvoid B::F()\n{\n    ++n_;\n}\n\n}\n";
            var pr3 = PimplGen.Make(ph3, pc3, ph3.IndexOf("class B"), "\n", out pw);
            Check("pimpl: no ctor made", pr3 == null ? "!" + pw : "ok", "ok");
            if (pr3 != null)
            {
                Has("pimpl: adds ctor/dtor decl", pr3.Header, "    B();", "    ~B();");
                Has("pimpl: ctor makes Impl", pr3.Cpp, "B::B()\n    : impl_(std::make_unique<Impl>())\n{\n}", "B::~B() = default;", "    ++impl_->n_;", "struct B::Impl {\n    int n_ = 0;\n};");
            }
            Check("pimpl: rewrite keeps obj.member", PimplGen.RewriteUses("a.hp_ + hp_ + p->hp_ + this->hp_", "a.hp_ + hp_ + p->hp_ + this->hp_", new[] { "hp_" }), "a.hp_ + impl_->hp_ + p->hp_ + impl_->hp_");
        }

        Console.WriteLine("Refactor: " + pass + " passed, " + fail + " failed");
        return fail;
    }
}
