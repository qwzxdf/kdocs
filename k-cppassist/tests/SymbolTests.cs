using System;
using System.Collections.Generic;
using System.Linq;
using KCppAssist;

static class SymbolTests
{
    static int pass = 0, fail = 0;

    static void Check(string name, string got, string want)
    {
        if (got == want) { pass++; return; }
        fail++;
        Console.WriteLine("FAIL " + name);
        Console.WriteLine("  got : " + (got ?? "<null>").Replace("\n", "\\n"));
        Console.WriteLine("  want: " + (want ?? "<null>").Replace("\n", "\\n"));
    }

    /// <summary>src の「|」の位置の宣言を to に変えたあとの文字(同じファイルの中だけ)。宣言でなければ "!"。</summary>
    static string Local(string src, string to)
    {
        int c = src.IndexOf('|');
        string text = src.Remove(c, 1);
        var d = SymbolScan.DeclAt(text, c);
        if (d == null) return "!";
        if (d.Kind != SymbolScan.Kind.Local && d.Kind != SymbolScan.Kind.Param) return "!" + d.Kind;
        var edits = SymbolScan.LocalRefs(text, d).Select(r => new SymbolScan.Edit { Start = r.Start, Length = d.Name.Length, Text = to }).ToList();
        edits.Add(new SymbolScan.Edit { Start = d.Start, Length = d.Name.Length, Text = to });
        return SymbolScan.Apply(text, edits);
    }

    /// <summary>
    /// files[0] の「|」の位置のメンバー・関数を to に変えたあとの、全ファイルの文字を「\n====\n」でつないだもの。
    /// あいまいな場所は「?」を前に付ける(変えない)。
    /// </summary>
    static string Member(string to, params string[] files)
    {
        int c = files[0].IndexOf('|');
        files = files.ToArray();
        files[0] = files[0].Remove(c, 1);
        var d = SymbolScan.DeclAt(files[0], c);
        if (d == null) return "!";
        if (d.Kind == SymbolScan.Kind.Local || d.Kind == SymbolScan.Kind.Param) return "!" + d.Kind;

        var bases = new Dictionary<string, HashSet<string>>();
        var declares = new HashSet<string>();
        foreach (string f in files)
        {
            SymbolScan.CollectClasses(f, bases);
            foreach (var s in FunctionScan.Scan(f)) if (s.Name == d.Name && s.Class != null) declares.Add(s.Class);
        }
        var ctx = new SymbolScan.Context { Bases = bases };
        SymbolScan.NormalizeKind(d, ctx);
        if (d.Class == null)
            foreach (string f in files)
                foreach (var s in FunctionScan.Scan(f))
                    if (s.Name == d.Name && (s.Class == null || (!s.InClass && !ctx.IsClass(s.Class))) && SyncPlan.ChainScore(s.Chain, d.Chain) == 0) ctx.NameClash = true;
        if (d.Class != null) ctx.Family = SymbolScan.BuildFamily(d.Class, d.Kind == SymbolScan.Kind.Method, bases, declares);
        ctx.ClassTexts = cls => files.Where(f => f.Contains("class " + cls) || f.Contains("struct " + cls));
        if (d.Kind == SymbolScan.Kind.Method && !d.Sig.InClass)
            foreach (string f in files)
            {
                bool priv;
                if (SymbolScan.DeclaresMethod(f, d.Class, d.Name, out priv)) { d.Private = priv; break; }
            }
        if (d.Sig != null)
        {
            var mine = SignatureSync.KeyVariants(d.Sig.Inner(files[0]));
            bool other = false;
            foreach (string f in files)
                foreach (var s in FunctionScan.Scan(f))
                {
                    if (s.Name != d.Name) continue;
                    if (d.Class != null ? !(s.Class != null && ctx.Family.Contains(s.Class)) : s.Class != null) continue;
                    if (!SyncPlan.SameKeysAny(SignatureSync.KeyVariants(s.Inner(f)), mine)) other = true;
                }
            if (other) ctx.OverloadKeys = mine;
        }

        var outs = new List<string>();
        for (int i = 0; i < files.Length; i++)
        {
            var refs = SymbolScan.MemberRefs(files[i], d, ctx, i == 0 ? d.Start : -1);
            var edits = refs.Select(r => new SymbolScan.Edit { Start = r.Start, Length = d.Name.Length, Text = r.Certain ? to : "?" + d.Name }).ToList();
            if (i == 0) edits.Add(new SymbolScan.Edit { Start = d.Start, Length = d.Name.Length, Text = to });
            outs.Add(SymbolScan.Apply(files[i], edits));
        }
        return string.Join("\n====\n", outs);
    }

    static string Kind(string src)
    {
        int c = src.IndexOf('|');
        var d = SymbolScan.DeclAt(src.Remove(c, 1), c);
        return d == null ? "none" : d.Kind.ToString();
    }

    static string Calls(string oldInner, string newInner, string text, string name, string cls)
    {
        var oldPs = SignatureSync.SplitParams(oldInner);
        var newPs = SignatureSync.SplitParams(newInner);
        int[] map = SymbolScan.ParamMap(oldPs, newPs);
        if (map == null) return "!ambiguous";
        if (SymbolScan.IsIdentity(map, oldPs.Count)) return "!same";
        var hasDef = newPs.Select(p => { string def; SignatureSync.StripDefault(p, out def); return def != null; }).ToArray();
        var d = new SymbolScan.Decl { Kind = cls == null ? SymbolScan.Kind.Function : SymbolScan.Kind.Method, Name = name, Class = cls };
        var ctx = new SymbolScan.Context();
        if (cls != null) ctx.Family.Add(cls);
        var skipped = new List<int>();
        var edits = SymbolScan.CallEdits(text, d, ctx, false, oldPs.Count, map, hasDef, skipped);
        return SymbolScan.Apply(text, edits) + (skipped.Count > 0 ? " !skipped=" + skipped.Count : "");
    }

    public static int Run()
    {
        // ---- 宣言の見分け ----
        Check("kind local", Kind("void f() {\n  int co|unt = 0;\n}"), "Local");
        Check("kind use is not decl", Kind("void f() {\n  int count = 0;\n  co|unt++;\n}"), "none");
        Check("kind expr is not decl", Kind("void f(int a, int b) {\n  int c = a * |b;\n}"), "none");
        Check("kind call arg is not decl", Kind("void f(int a, int b) {\n  g(a * |b);\n}"), "none");
        Check("kind return is not decl", Kind("int f(int x) {\n  return |x;\n}"), "none");
        Check("kind compare is not decl", Kind("void f(int a, int b) {\n  if (a < |b) {}\n}"), "none");
        Check("kind param", Kind("void f(int a, float |b) {\n}"), "Param");
        Check("kind param type is not decl", Kind("void f(Fo|o a) {\n}"), "none");
        Check("kind field", Kind("class A {\n  int h|p_ = 0;\n};"), "Field");
        Check("kind method decl", Kind("class A {\n  void Up|date(float dt);\n};"), "Method");
        Check("kind method def", Kind("void A::Up|date(float dt) {\n}"), "Method");
        Check("kind function", Kind("int Ad|d(int a, int b);"), "Function");
        Check("kind ctor is not renamed", Kind("class A {\n  A|(int x);\n};"), "none");
        Check("kind for", Kind("void f() {\n  for (int |i = 0; i < 3; ++i) {}\n}"), "Local");
        Check("kind range for", Kind("void f(std::vector<int>& v) {\n  for (auto& |e : v) {}\n}"), "Local");
        Check("kind if init", Kind("void f() {\n  if (auto |it = m.find(1); it != m.end()) {}\n}"), "Local");
        Check("kind template type", Kind("void f() {\n  std::map<int, std::string> |names;\n}"), "Local");
        Check("kind keyword", Kind("void f() {\n  in|t x = 0;\n}"), "none");
        Check("kind type name in class", Kind("class A {\n  Fo|o x_;\n};"), "none");

        // 行を複製して、写しの名前を書き換えているときは、名前の変更とみなさない
        Check("kind duplicated local", Kind("void f() {\n  int hp = 1;\n  int h|p = 1;\n  use(hp);\n}"), "none");
        Check("kind same name in another block", Kind("void f() {\n  { int hp = 1; }\n  int h|p = 1;\n  use(hp);\n}"), "Local");
        Check("kind duplicated field", Kind("class A {\n  int hp_ = 0;\n  int h|p_ = 0;\n};"), "none");
        Check("kind duplicated method decl", Kind("class A {\n  void Update(float dt);\n  void Up|date(float dt);\n};"), "none");
        Check("kind overload is not a duplicate", Kind("class A {\n  void Update(float dt);\n  void Up|date(int n);\n};"), "Method");
        Check("kind duplicated definition", Kind("void A::Update(float dt) {\n}\nvoid A::Up|date(float dt) {\n}"), "none");
        Check("kind decl and def in one file", Kind("void Run(int n);\nvoid R|un(int n) {\n}"), "Function");
        Check("kind duplicated param", Kind("void f(int a, int |a) {\n}"), "none");
        Check("kind field with function type", Kind("class A {\n  std::function<void(int)> on_h|it_;\n};"), "Field");

        // ---- ローカル変数・引数 ----
        Check("local basic",
            Local("void f() {\n  int |hp = 3;\n  hp += 1;\n  g(hp, obj.hp, p->hp);\n}", "life"),
            "void f() {\n  int life = 3;\n  life += 1;\n  g(life, obj.hp, p->hp);\n}");
        Check("local scope ends at block",
            Local("void f() {\n  {\n    int |x = 1;\n    use(x);\n  }\n  use(x);\n}", "y"),
            "void f() {\n  {\n    int y = 1;\n    use(y);\n  }\n  use(x);\n}");
        Check("local shadowed in inner block",
            Local("void f() {\n  int |x = 1;\n  {\n    int x = 2;\n    use(x);\n  }\n  use(x);\n}", "y"),
            "void f() {\n  int y = 1;\n  {\n    int x = 2;\n    use(x);\n  }\n  use(y);\n}");
        Check("local not before decl",
            Local("void f() {\n  use(x);\n  int |x = 1;\n  use(x);\n}", "y"),
            "void f() {\n  use(x);\n  int y = 1;\n  use(y);\n}");
        Check("local in comment and string untouched",
            Local("void f() {\n  int |x = 1; // x\n  puts(\"x\");\n  use(x);\n}", "y"),
            "void f() {\n  int y = 1; // x\n  puts(\"x\");\n  use(y);\n}");
        Check("for loop var",
            Local("void f() {\n  for (int |i = 0; i < n; ++i) a[i] = i;\n  use(i);\n}", "k"),
            "void f() {\n  for (int k = 0; k < n; ++k) a[k] = k;\n  use(i);\n}");
        Check("for loop var block",
            Local("void f() {\n  for (auto& |e : list) {\n    e.Draw();\n  }\n}", "item"),
            "void f() {\n  for (auto& item : list) {\n    item.Draw();\n  }\n}");
        Check("if init covers else",
            Local("void f() {\n  if (auto |p = Get()) {\n    p->A();\n  } else {\n    Log(p);\n  }\n  p = 0;\n}", "q"),
            "void f() {\n  if (auto q = Get()) {\n    q->A();\n  } else {\n    Log(q);\n  }\n  p = 0;\n}");
        Check("param in definition",
            Local("void A::Set(int |hp) {\n  hp_ = hp;\n  this->hp = hp;\n}", "value"),
            "void A::Set(int value) {\n  hp_ = value;\n  this->hp = value;\n}");
        Check("param in ctor init list",
            Local("A::A(int |hp, int mp) : hp(hp), mp_(mp) {\n  Log(hp);\n}", "h"),
            "A::A(int h, int mp) : hp(h), mp_(mp) {\n  Log(h);\n}");
        Check("param in declaration only",
            Local("class A {\n  void Set(int |hp);\n  int hp;\n};", "value"),
            "class A {\n  void Set(int value);\n  int hp;\n};");
        Check("lambda capture and body",
            Local("void f() {\n  int |n = 0;\n  auto g = [n, &r](int x) { return n + x; };\n}", "count"),
            "void f() {\n  int count = 0;\n  auto g = [count, &r](int x) { return count + x; };\n}");
        Check("lambda param shadows",
            Local("void f() {\n  int |x = 0;\n  auto g = [](int x) { return x; };\n  use(x);\n}", "y"),
            "void f() {\n  int y = 0;\n  auto g = [](int x) { return x; };\n  use(y);\n}");
        Check("designated initializer untouched",
            Local("void f() {\n  int |x = 0;\n  P p{.x = x};\n}", "y"),
            "void f() {\n  int y = 0;\n  P p{.x = y};\n}");

        // ---- メンバー変数 ----
        Check("field private, header and cpp",
            Member("life_",
                "class Player {\n public:\n  int Hp() const { return hp_; }\n private:\n  int |hp_ = 0;\n};",
                "void Player::Hit(int d) {\n  hp_ -= d;\n  this->hp_ = 0;\n}\nvoid Enemy::Hit() {\n  hp_ = 1;\n}\nbool Player::Same(const Player& o) {\n  return hp_ == o.hp_;\n}"),
            "class Player {\n public:\n  int Hp() const { return life_; }\n private:\n  int life_ = 0;\n};" + "\n====\n" +
            "void Player::Hit(int d) {\n  life_ -= d;\n  this->life_ = 0;\n}\nvoid Enemy::Hit() {\n  hp_ = 1;\n}\nbool Player::Same(const Player& o) {\n  return life_ == o.life_;\n}");
        Check("field shadowed by param and local",
            Member("life",
                "class P {\n  int |hp;\n};",
                "void P::Set(int hp) {\n  this->hp = hp;\n}\nvoid P::Tick() {\n  hp++;\n  { int hp = 2; use(hp); }\n  hp--;\n}\nP::P(int hp) : hp(hp) {}"),
            "class P {\n  int life;\n};" + "\n====\n" +
            "void P::Set(int hp) {\n  this->life = hp;\n}\nvoid P::Tick() {\n  life++;\n  { int hp = 2; use(hp); }\n  life--;\n}\nP::P(int hp) : life(hp) {}");
        Check("public field: receiver type decides",
            Member("px",
                "struct Vec {\n  float |x;\n};",
                "struct Other { float x; };\nvoid Move(Vec& v, Other& o, std::vector<Vec>& list, VecRef r, std::string s) {\n  v.x = o.x;\n  Vec w;\n  w.x = 1;\n  auto p = std::make_unique<Vec>();\n  p->x = 2;\n  list[0].x = 3;\n  list.x();\n  r.x = 4;\n  s.x();\n}"),
            "struct Vec {\n  float px;\n};" + "\n====\n" +
            "struct Other { float x; };\nvoid Move(Vec& v, Other& o, std::vector<Vec>& list, VecRef r, std::string s) {\n  v.px = o.x;\n  Vec w;\n  w.px = 1;\n  auto p = std::make_unique<Vec>();\n  p->px = 2;\n  list[0].px = 3;\n  list.x();\n  r.?x = 4;\n  s.x();\n}");
        Check("field through member of another class",
            Member("life",
                "struct Enemy {\n  int |hp;\n};",
                "struct Item { int hp; };\nclass Game {\n  Enemy* boss_;\n  std::unique_ptr<Enemy> sub_;\n  Item item_;\n};",
                "void Game::Tick() {\n  boss_->hp--;\n  sub_->hp--;\n  item_.hp--;\n  sub_.hp();\n}"),
            "struct Enemy {\n  int life;\n};" + "\n====\n" +
            "struct Item { int hp; };\nclass Game {\n  Enemy* boss_;\n  std::unique_ptr<Enemy> sub_;\n  Item item_;\n};" + "\n====\n" +
            "void Game::Tick() {\n  boss_->life--;\n  sub_->life--;\n  item_.hp--;\n  sub_.hp();\n}");
        Check("static member definition",
            Member("total_",
                "class C {\n  static int |count_;\n};",
                "int C::count_ = 0;\nvoid C::Add() { ++count_; }\nint D::count_ = 0;"),
            "class C {\n  static int total_;\n};" + "\n====\n" +
            "int C::total_ = 0;\nvoid C::Add() { ++total_; }\nint D::count_ = 0;");
        Check("field used in derived class",
            Member("life_",
                "class Actor {\n protected:\n  int |hp_;\n};\nclass Enemy : public Actor {\n  void Hit() { hp_--; }\n};",
                "void Enemy::Heal() { hp_++; }\nvoid Wall::Heal() { hp_++; }"),
            "class Actor {\n protected:\n  int life_;\n};\nclass Enemy : public Actor {\n  void Hit() { life_--; }\n};" + "\n====\n" +
            "void Enemy::Heal() { life_++; }\nvoid Wall::Heal() { hp_++; }");
        Check("field in destructor",
            Member("buf_",
                "class B {\n  char* |data_;\n  ~B();\n};",
                "B::~B() {\n  delete[] data_;\n}\nbool B::operator==(const B& o) const {\n  return data_ == o.data_;\n}"),
            "class B {\n  char* buf_;\n  ~B();\n};" + "\n====\n" +
            "B::~B() {\n  delete[] buf_;\n}\nbool B::operator==(const B& o) const {\n  return buf_ == o.buf_;\n}");

        // ---- メンバー関数 ----
        Check("method from declaration",
            Member("Tick",
                "class Player {\n public:\n  void |Update(float dt);\n  void Run() { Update(0.1f); }\n};",
                "class Enemy {\n  void Update(float dt);\n};\nvoid Player::Update(float dt) {\n  Update(dt);\n  this->Update(dt);\n}\nvoid Enemy::Update(float dt) {}\nvoid Game::Loop(Player& p, Enemy* e) {\n  p.Update(1);\n  e->Update(1);\n  x.y.Update(2);\n  Update(3);\n}"),
            "class Player {\n public:\n  void Tick(float dt);\n  void Run() { Tick(0.1f); }\n};" + "\n====\n" +
            "class Enemy {\n  void Update(float dt);\n};\nvoid Player::Tick(float dt) {\n  Tick(dt);\n  this->Tick(dt);\n}\nvoid Enemy::Update(float dt) {}\nvoid Game::Loop(Player& p, Enemy* e) {\n  p.Tick(1);\n  e->Update(1);\n  x.y.?Update(2);\n  Update(3);\n}");
        Check("method from definition",
            Member("Tick",
                "void Player::|Update(float dt) {\n}",
                "class Player {\n  void Update(float dt);\n};\nclass Enemy {\n  void Update(float dt);\n};"),
            "void Player::Tick(float dt) {\n}" + "\n====\n" +
            "class Player {\n  void Tick(float dt);\n};\nclass Enemy {\n  void Update(float dt);\n};");
        Check("virtual method renames overrides",
            Member("Tick",
                "class Actor {\n public:\n  virtual void |Update(float dt);\n};",
                "class Enemy : public Actor {\n public:\n  void Update(float dt) override;\n};\nclass Wall {\n  void Update(float dt);\n};",
                "void Enemy::Update(float dt) {\n  Actor::Update(dt);\n}\nvoid Wall::Update(float dt) {}"),
            "class Actor {\n public:\n  virtual void Tick(float dt);\n};" + "\n====\n" +
            "class Enemy : public Actor {\n public:\n  void Tick(float dt) override;\n};\nclass Wall {\n  void Update(float dt);\n};" + "\n====\n" +
            "void Enemy::Tick(float dt) {\n  Actor::Tick(dt);\n}\nvoid Wall::Update(float dt) {}");
        Check("override renames base",
            Member("Tick",
                "class Enemy : public Actor {\n public:\n  void |Update(float dt) override;\n};",
                "class Actor {\n public:\n  virtual void Update(float dt);\n};"),
            "class Enemy : public Actor {\n public:\n  void Tick(float dt) override;\n};" + "\n====\n" +
            "class Actor {\n public:\n  virtual void Tick(float dt);\n};");
        Check("overloads: only the matching pair",
            Member("Put",
                "class Bag {\n  void |Add(int id);\n  void Add(const Item& item);\n};",
                "void Bag::Add(int id) {}\nvoid Bag::Add(const Item& item) { Add(item.id); }"),
            "class Bag {\n  void Put(int id);\n  void Add(const Item& item);\n};" + "\n====\n" +
            "void Bag::Put(int id) {}\nvoid Bag::Add(const Item& item) { ?Add(item.id); }");
        Check("pointer to member",
            Member("Tick",
                "class T {\n  void |Run();\n};",
                "void f() {\n  auto p = &T::Run;\n  std::thread t(&T::Run, this);\n}"),
            "class T {\n  void Tick();\n};" + "\n====\n" +
            "void f() {\n  auto p = &T::Tick;\n  std::thread t(&T::Tick, this);\n}");

        // ---- 関数 ----
        Check("free function",
            Member("Sum",
                "int |Add(int a, int b);",
                "int Add(int a, int b) { return a + b; }\nvoid f(Calc& c) {\n  int x = Add(1, 2);\n  c.Add(3, 4);\n  int Add2 = 0;\n}",
                "class Bag {\n  void Add(int id);\n  void Fill() { Add(1); }\n};"),
            "int Sum(int a, int b);" + "\n====\n" +
            "int Sum(int a, int b) { return a + b; }\nvoid f(Calc& c) {\n  int x = Sum(1, 2);\n  c.Add(3, 4);\n  int Add2 = 0;\n}" + "\n====\n" +
            "class Bag {\n  void Add(int id);\n  void Fill() { Add(1); }\n};");
        Check("namespaced function",
            Member("Clamp01",
                "namespace math {\nfloat |Saturate(float v);\n}",
                "float a = math::Saturate(2);\nfloat b = other::Saturate(2);"),
            "namespace math {\nfloat Clamp01(float v);\n}" + "\n====\n" +
            "float a = math::Clamp01(2);\nfloat b = other::Saturate(2);");

        Check("function: call inside a class that inherits the same name",
            Member("Sum",
                "int |Add(int a, int b);",
                "class Base {\n public:\n  void Add(int id);\n};\nclass Bag : public Base {\n  void Fill();\n  void Other();\n};",
                "void Bag::Fill() { Add(1); }\nvoid Free() { Add(1, 2); }"),
            "int Sum(int a, int b);" + "\n====\n" +
            "class Base {\n public:\n  void Add(int id);\n};\nclass Bag : public Base {\n  void Fill();\n  void Other();\n};" + "\n====\n" +
            "void Bag::Fill() { Add(1); }\nvoid Free() { Sum(1, 2); }");

        Check("function defined with a namespace qualifier",
            Member("Saturate",
                "float math::|Clamp(float v) {\n  return v;\n}",
                "namespace math {\nfloat Clamp(float v);\n}\nfloat a = math::Clamp(2);\nclass Box {\n  float Clamp(float v);\n};"),
            "float math::Saturate(float v) {\n  return v;\n}" + "\n====\n" +
            "namespace math {\nfloat Saturate(float v);\n}\nfloat a = math::Saturate(2);\nclass Box {\n  float Clamp(float v);\n};");
        Check("function: same name in another namespace",
            Member("Setup",
                "namespace a {\nvoid |Init();\nvoid Run() { Init(); }\n}",
                "namespace b {\nvoid Init();\nvoid Run() { Init(); }\n}\nvoid Main() {\n  a::Init();\n  b::Init();\n  Init();\n}"),
            "namespace a {\nvoid Setup();\nvoid Run() { Setup(); }\n}" + "\n====\n" +
            "namespace b {\nvoid Init();\nvoid Run() { ?Init(); }\n}\nvoid Main() {\n  a::Setup();\n  b::Init();\n  ?Init();\n}");
        {
            string src = "static void Helper() {}\nnamespace {\nvoid Hidden() {}\n}\nvoid Shown() {}";
            Check("file local: static", SymbolScan.DeclAt(src, src.IndexOf("Helper")).FileLocal.ToString(), "True");
            Check("file local: unnamed namespace", SymbolScan.DeclAt(src, src.IndexOf("Hidden")).FileLocal.ToString(), "True");
            Check("file local: plain", SymbolScan.DeclAt(src, src.IndexOf("Shown")).FileLocal.ToString(), "False");
        }

        Check("function passed as a callback",
            Member("HandleKey",
                "void |OnKey(int key);",
                "void Setup(Window* w) {\n  SetCallback(w, OnKey);\n  auto f = &OnKey;\n  Handler h = OnKey;\n  int OnKeyCount = 0;\n  OnKey(3);\n}\nvoid Other(int OnKey) {\n  Use(OnKey);\n}"),
            "void HandleKey(int key);" + "\n====\n" +
            "void Setup(Window* w) {\n  SetCallback(w, HandleKey);\n  auto f = &HandleKey;\n  Handler h = HandleKey;\n  int OnKeyCount = 0;\n  HandleKey(3);\n}\nvoid Other(int OnKey) {\n  Use(OnKey);\n}");
        Check("range for over a member container",
            Member("Tick",
                "class Enemy {\n public:\n  void |Update(float dt);\n};",
                "class Wall {\n public:\n  void Update(float dt);\n};\nclass Game {\n  std::vector<Enemy> enemies_;\n  std::vector<std::unique_ptr<Enemy>> owned_;\n  std::vector<Wall> walls_;\n  std::array<Enemy, 4> fixed_;\n};",
                "void Game::Tick(float dt) {\n  for (auto& e : enemies_) e.Update(dt);\n  for (auto& o : owned_) {\n    o->Update(dt);\n  }\n  for (auto& w : walls_) w.Update(dt);\n  enemies_[0].Update(dt);\n  walls_[0].Update(dt);\n  auto& first = enemies_.front();\n  first.Update(dt);\n  for (const auto& f : fixed_) f.Update(dt);\n}"),
            "class Enemy {\n public:\n  void Tick(float dt);\n};" + "\n====\n" +
            "class Wall {\n public:\n  void Update(float dt);\n};\nclass Game {\n  std::vector<Enemy> enemies_;\n  std::vector<std::unique_ptr<Enemy>> owned_;\n  std::vector<Wall> walls_;\n  std::array<Enemy, 4> fixed_;\n};" + "\n====\n" +
            "void Game::Tick(float dt) {\n  for (auto& e : enemies_) e.Tick(dt);\n  for (auto& o : owned_) {\n    o->Tick(dt);\n  }\n  for (auto& w : walls_) w.Update(dt);\n  enemies_[0].Tick(dt);\n  walls_[0].Update(dt);\n  auto& first = enemies_.front();\n  first.Tick(dt);\n  for (const auto& f : fixed_) f.Tick(dt);\n}");
        Check("element type vector", SymbolScan.ElementType("const std::vector<Enemy>&"), "Enemy");
        Check("element type nested", SymbolScan.ElementType("std::vector<std::unique_ptr<Enemy>>"), "std::unique_ptr<Enemy>");
        Check("element type array", SymbolScan.ElementType("std::array<Enemy, 4>"), "Enemy");
        Check("element type not a container", SymbolScan.ElementType("std::map<int, Enemy>") ?? "null", "null");
        {
            string body = "void f() {\n  int a = 1;\n  int b = 2;\n  use(a, obj.b);\n}";
            int from = body.IndexOf('{'), to = body.Length;
            var own = new HashSet<int> { body.IndexOf("a = 1"), body.IndexOf("a, obj") };
            Check("conflict: name already used", SymbolScan.NameUsedIn(body, from, to, "b", own).ToString(), "True");
            Check("conflict: free name", SymbolScan.NameUsedIn(body, from, to, "c", own).ToString(), "False");
            Check("conflict: own places do not count", SymbolScan.NameUsedIn(body, from, to, "a", own).ToString(), "False");
            Check("conflict: member of another object does not count",
                SymbolScan.NameUsedIn("void f() {\n  int a = 1;\n  use(obj.b);\n}", 0, 40, "b", new HashSet<int>()).ToString(), "False");
            var cx = new SymbolScan.Context { ClassTexts = c => new[] { "class P {\n  int hp_;\n  void Heal();\n};" } };
            Check("conflict: field exists", SymbolScan.MemberExists(cx, "P", "hp_", true).ToString(), "True");
            Check("conflict: method exists (renaming a field)", SymbolScan.MemberExists(cx, "P", "Heal", true).ToString(), "True");
            Check("conflict: method vs method is an overload", SymbolScan.MemberExists(cx, "P", "Heal", false).ToString(), "False");
            Check("conflict: no such member", SymbolScan.MemberExists(cx, "P", "mp_", true).ToString(), "False");
        }

        // ---- 型の判定 ----
        var fam = new HashSet<string> { "Enemy" };
        Check("verdict plain", SymbolScan.TypeVerdict("const Enemy&", null, fam, false).ToString(), "Yes");
        Check("verdict pointer", SymbolScan.TypeVerdict("game::Enemy*", null, fam, true).ToString(), "Yes");
        Check("verdict other", SymbolScan.TypeVerdict("Player", null, fam, false).ToString(), "No");
        Check("verdict unique_ptr arrow", SymbolScan.TypeVerdict("std::unique_ptr<Enemy>", null, fam, true).ToString(), "Yes");
        Check("verdict unique_ptr dot", SymbolScan.TypeVerdict("std::unique_ptr<Enemy>", null, fam, false).ToString(), "No");
        Check("verdict vector", SymbolScan.TypeVerdict("std::vector<Enemy>", null, fam, false).ToString(), "No");
        Check("verdict auto unknown", SymbolScan.TypeVerdict("auto", " = Find(3)", fam, true).ToString(), "Unknown");
        Check("verdict auto new", SymbolScan.TypeVerdict("auto*", " = new Enemy(3)", fam, true).ToString(), "Yes");
        Check("verdict auto ctor", SymbolScan.TypeVerdict("auto", " = Enemy{1}", fam, false).ToString(), "Yes");

        // ---- 継承 ----
        var bases = new Dictionary<string, HashSet<string>>();
        SymbolScan.CollectClasses("class A {};\nclass B : public A {};\nstruct C final : public B, private Base<int> {};\nclass D {};", bases);
        Check("family down", string.Join(",", SymbolScan.BuildFamily("A", false, bases, new HashSet<string>()).OrderBy(x => x)), "A,B,C");
        Check("family up needs declare", string.Join(",", SymbolScan.BuildFamily("C", true, bases, new HashSet<string> { "B" }).OrderBy(x => x)), "B,C");

        // ---- 呼び出しの引数 ----
        Check("args swap",
            Calls("int a, float b", "float b, int a", "void g() {\n  Move(1, 2.0f);\n  Move(x + 1, f(a, b));\n}", "Move", null),
            "void g() {\n  Move(2.0f, 1);\n  Move(f(a, b), x + 1);\n}");
        Check("args remove middle",
            Calls("int a, float b, bool c", "int a, bool c", "void g() { Move(1, 2.0f, true); }", "Move", null),
            "void g() { Move(1, true); }");
        Check("args remove with omitted default",
            Calls("int a, float b, bool c = false", "float b, bool c = false", "void g() { Move(1, 2.0f); }", "Move", null),
            "void g() { Move(2.0f); }");
        Check("args add without value is skipped",
            Calls("int a", "int a, float speed", "void g() { Move(1); }", "Move", null),
            "void g() { Move(1); } !skipped=1");
        Check("args add with default at tail",
            Calls("int a, int b", "int b, int a, float speed = 1", "void g() { Move(1, 2); }", "Move", null),
            "void g() { Move(2, 1); }");
        Check("args rename only", Calls("int a, int b", "int x, int b", "void g() { Move(1, 2); }", "Move", null), "!same");
        Check("args type only", Calls("int a, int b", "long a, int b", "void g() { Move(1, 2); }", "Move", null), "!same");
        Check("args method by receiver",
            Calls("int a, int b", "int b, int a", "void G::Run(Player& p, Enemy& e) {\n  p.Move(1, 2);\n  e.Move(1, 2);\n}", "Move", "Player"),
            "void G::Run(Player& p, Enemy& e) {\n  p.Move(2, 1);\n  e.Move(1, 2);\n}");
        Check("args declaration untouched",
            Calls("int a, int b", "int b, int a", "void Move(int a, int b);\nvoid g() { Move(1, 2); }", "Move", null),
            "void Move(int a, int b);\nvoid g() { Move(2, 1); }");
        Check("args remove one of two with the same type",
            Calls("int x, int y", "int height", "void g() { Move(1, 2); }", "Move", null), "!ambiguous");
        Check("args remove by name keeps the right one",
            Calls("int x, int y", "int y", "void g() { Move(1, 2); }", "Move", null), "void g() { Move(2); }");
        Check("verdict alias is unknown", SymbolScan.TypeVerdict("EnemyRef", null, fam, false, n => n == "Player").ToString(), "Unknown");
        Check("verdict known other class", SymbolScan.TypeVerdict("Player*", null, fam, true, n => n == "Player").ToString(), "No");
        Check("verdict std type", SymbolScan.TypeVerdict("std::string", null, fam, false, n => false).ToString(), "No");
        Check("verdict builtin", SymbolScan.TypeVerdict("int", null, fam, false, n => false).ToString(), "No");
        Check("args swap same type by name",
            Calls("int x, int y", "int y, int x", "void g() { Move(1, 2); }", "Move", null),
            "void g() { Move(2, 1); }");

        Console.WriteLine("symbol: " + pass + " passed, " + fail + " failed");
        return fail;
    }
}
