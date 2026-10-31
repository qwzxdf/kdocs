using System;
using System.Collections.Generic;
using System.Linq;
using KCppAssist;

static class SyncTests
{
    static int pass = 0, fail = 0;

    static void Check(string name, string got, string want)
    {
        if (got == want) { pass++; return; }
        fail++;
        Console.WriteLine("FAIL " + name);
        Console.WriteLine("  got : " + got.Replace("\n", "\\n"));
        Console.WriteLine("  want: " + want.Replace("\n", "\\n"));
    }

    /// <summary>
    /// 自動の引数合わせ(AutoSync.SyncOneAsync)と同じ手順を、文字だけで再現する。
    /// edited の before → after で変わった関数の相手を other から選んで、書き換えたあとの other を返す。
    /// 書き換えない場合は、"!理由" を返す。
    /// </summary>
    static string Sync(string before, string after, string other)
    {
        var sb = FunctionScan.Scan(before);
        var sa = FunctionScan.Scan(after);
        if (sb.Count != sa.Count) return "!関数の数が変わった";
        int idx = -1;
        for (int i = 0; i < sb.Count; i++)
            if (SignatureSync.Norm(sb[i].Inner(before)) != SignatureSync.Norm(sa[i].Inner(after))) { idx = i; break; }
        if (idx < 0) return "!変更なし";
        var edited = sb[idx];
        var oldList = SignatureSync.SplitParams(edited.Inner(before));
        var newList = SignatureSync.SplitParams(sa[idx].Inner(after));
        if (oldList == null || newList == null) return "!書きかけ";
        if (edited.HasBody && edited.InClass) return "!相手なし(クラスの中の本体)";

        bool wantDef = !edited.HasBody;
        var targets = new List<KeyValuePair<FunctionScan.Sig, int>>();
        foreach (var s in FunctionScan.Scan(other))
        {
            int score = SyncPlan.Counterpart(s, edited, wantDef);
            if (score > 0) targets.Add(new KeyValuePair<FunctionScan.Sig, int>(s, score));
        }
        var oldKeys = SignatureSync.TypeKeys(oldList);
        var newKeys = SignatureSync.TypeKeys(newList);
        Func<KeyValuePair<FunctionScan.Sig, int>, List<string>> keysOf = t => { var l = SignatureSync.SplitParams(t.Key.Inner(other)); return l == null ? null : SignatureSync.TypeKeys(l); };

        var matches = SyncPlan.Matches(targets, t => t.Value, keysOf, oldKeys);
        if (matches.Count == 0)
        {
            if (targets.Any(t => SyncPlan.SameKeys(keysOf(t), newKeys))) return "!もう合っている";
            return "!見つからない";
        }
        if (matches.Count > 1) return "!複数ある";
        var t0 = matches[0].Key;
        var cpList = SignatureSync.SplitParams(t0.Inner(other));
        if (cpList == null) return "!相手が書きかけ";
        string newInner = SignatureSync.Rebuild(oldList, newList, cpList, !wantDef, t0.Inner(other));
        return other.Substring(0, t0.Open + 1) + newInner + other.Substring(t0.Close);
    }

    static void Case(string name, string headerBefore, string headerAfter, string cpp, string wantCpp)
    {
        Check(name + " [H→cpp]", Sync(headerBefore, headerAfter, cpp), wantCpp);
    }

    static void CaseCpp(string name, string cppBefore, string cppAfter, string header, string wantHeader)
    {
        Check(name + " [cpp→H]", Sync(cppBefore, cppAfter, header), wantHeader);
    }

    public static int Run()
    {
        // ---- 1. 同名の関数が複数(オーバーロード) ----
        string h1 = "class A {\n public:\n  void Add(int a);\n  void Add(float a);\n};\n";
        string c1 = "void A::Add(int a) {}\nvoid A::Add(float a) {}\n";
        Case("overload: int 側を変える", h1, h1.Replace("Add(int a)", "Add(int a, int b)"), c1,
             "void A::Add(int a, int b) {}\nvoid A::Add(float a) {}\n");
        Case("overload: float 側を変える", h1, h1.Replace("Add(float a)", "Add(float a, float b)"), c1,
             "void A::Add(int a) {}\nvoid A::Add(float a, float b) {}\n");
        CaseCpp("overload: cpp の float 側", c1, c1.Replace("Add(float a)", "Add(float a, float b)"), h1,
                "class A {\n public:\n  void Add(int a);\n  void Add(float a, float b);\n};\n");
        // 同じ型の並びの、const あり・なし
        string h1c = "class A {\n public:\n  int Get() const;\n  int Get();\n};\n";
        string c1c = "int A::Get() const { return 1; }\nint A::Get() { return 2; }\n";
        Case("const オーバーロード: const 側", h1c, h1c.Replace("int Get() const", "int Get(int i) const"), c1c,
             "int A::Get(int i) const { return 1; }\nint A::Get() { return 2; }\n");
        Case("const オーバーロード: 非 const 側", h1c, h1c.Replace("int Get();", "int Get(int i);"), c1c,
             "int A::Get() const { return 1; }\nint A::Get(int i) { return 2; }\n");
        // 別のクラスの同名関数
        string h1d = "class A {\n public:\n  void Update(int x);\n};\nclass B {\n public:\n  void Update(int x);\n};\n";
        string c1d = "void A::Update(int x) {}\nvoid B::Update(int x) {}\n";
        Case("別クラスの同名: A", h1d, h1d.Replace("class A {\n public:\n  void Update(int x)", "class A {\n public:\n  void Update(int x, int y)"), c1d,
             "void A::Update(int x, int y) {}\nvoid B::Update(int x) {}\n");

        // ---- 2. 引数の名前が違う ----
        string h2 = "class Alloc {\n public:\n  Alloc(Dev* device, int type);\n};\n";
        string c2 = "Alloc::Alloc(Dev* d, int t) {}\n";
        Case("名前違い: 引数を足す", h2, h2.Replace("int type)", "int type, float scale)"), c2, "Alloc::Alloc(Dev* d, int t, float scale) {}\n");
        Case("名前違い: 真ん中を消す", h2, h2.Replace("Dev* device, int type", "int type"), c2, "Alloc::Alloc(int t) {}\n");
        Case("名前違い: 先頭に足す", h2, h2.Replace("(Dev* device", "(int id, Dev* device"), c2, "Alloc::Alloc(int id, Dev* d, int t) {}\n");
        string h2u = "class A {\n public:\n  void F(int, float);\n};\n";
        string c2u = "void A::F(int x, float y) {}\n";
        Case("ヘッダーは名前なし: 足す", h2u, h2u.Replace("float)", "float, bool)"), c2u, "void A::F(int x, float y, bool) {}\n");
        CaseCpp("ヘッダーは名前なし: cpp で改名", c2u, c2u.Replace("int x", "int count"), h2u, "class A {\n public:\n  void F(int count, float);\n};\n");
        Case("ヘッダーで改名(cpp は変えない)", h2u.Replace("void F(int, float)", "void F(int a, float b)"), h2u.Replace("void F(int, float)", "void F(int count, float b)"), c2u,
             "void A::F(int x, float y) {}\n");     // ヘッダーの改名は、cpp(本文が名前を使う)に写さない
        // 型だけ変える(名前は変えない)なら、cpp の名前は残したい
        Case("型の変更: 名前は相手のまま", "class A {\n public:\n  void F(int a);\n};\n", "class A {\n public:\n  void F(float a);\n};\n", "void A::F(int x) {}\n", "void A::F(float x) {}\n");

        // ---- 3. 既定値 ----
        string h3 = "class A {\n public:\n  void F(int a = 3);\n};\n";
        string c3 = "void A::F(int a) {}\n";
        Case("既定値: ヘッダーに足す", h3, h3.Replace("int a = 3)", "int a = 3, int b = 4)"), c3, "void A::F(int a, int b) {}\n");
        CaseCpp("既定値: cpp に足す(ヘッダーの既定値は残る)", c3, c3.Replace("int a)", "int a, int b)"), h3, "class A {\n public:\n  void F(int a = 3, int b);\n};\n");
        string h3b = "class A {\n public:\n  void F(Vec3 v = Vec3(1, 2, 3), int b = 0);\n};\n";
        Case("既定値に括弧とカンマ", h3b, h3b.Replace("int b = 0)", "int b = 0, int c = 1)"), "void A::F(Vec3 v, int b) {}\n", "void A::F(Vec3 v, int b, int c) {}\n");

        // ---- 4. namespace ----
        string h4 = "namespace game {\nvoid Update(float dt);\n}\n";
        string h4n = "namespace game {\nvoid Update(float dt, int n);\n}\n";
        Case("ns: 同じ namespace ブロック", h4, h4n, "namespace game {\nvoid Update(float dt) {}\n}\n", "namespace game {\nvoid Update(float dt, int n) {}\n}\n");
        Case("ns: cpp は game:: で修飾", h4, h4n, "void game::Update(float dt) {}\n", "void game::Update(float dt, int n) {}\n");
        Case("ns: cpp は using namespace(修飾なし)", h4, h4n, "using namespace game;\nvoid Update(float dt) {}\n", "using namespace game;\nvoid Update(float dt, int n) {}\n");
        CaseCpp("ns: cpp(修飾)からヘッダー", "void game::Update(float dt) {}\n", "void game::Update(float dt, int n) {}\n", h4, h4n);
        string h4ab = "namespace a {\nvoid F(int x);\n}\nnamespace b {\nvoid F(int x);\n}\n";
        string c4ab = "namespace a {\nvoid F(int x) {}\n}\nnamespace b {\nvoid F(int x) {}\n}\n";
        Case("ns: 同名関数 a を変える", h4ab, h4ab.Replace("namespace a {\nvoid F(int x)", "namespace a {\nvoid F(int x, int y)"), c4ab,
             "namespace a {\nvoid F(int x, int y) {}\n}\nnamespace b {\nvoid F(int x) {}\n}\n");
        Case("ns: 同名関数 b を変える", h4ab, h4ab.Replace("namespace b {\nvoid F(int x)", "namespace b {\nvoid F(int x, int y)"), c4ab,
             "namespace a {\nvoid F(int x) {}\n}\nnamespace b {\nvoid F(int x, int y) {}\n}\n");
        Case("ns: cpp が a::F / b::F の修飾", h4ab, h4ab.Replace("namespace b {\nvoid F(int x)", "namespace b {\nvoid F(int x, int y)"),
             "void a::F(int x) {}\nvoid b::F(int x) {}\n", "void a::F(int x) {}\nvoid b::F(int x, int y) {}\n");
        string h4nest = "namespace a::b {\nvoid F(int x);\n}\n";
        Case("ns: a::b と入れ子の namespace", h4nest, h4nest.Replace("int x)", "int x, int y)"), "namespace a {\nnamespace b {\nvoid F(int x) {}\n}\n}\n",
             "namespace a {\nnamespace b {\nvoid F(int x, int y) {}\n}\n}\n");
        string h4cls = "namespace game {\nclass A {\n public:\n  void F(int x);\n};\n}\n";
        Case("ns: namespace の中のクラスを game::A:: で修飾", h4cls, h4cls.Replace("int x)", "int x, int y)"), "void game::A::F(int x) {}\n", "void game::A::F(int x, int y) {}\n");
        Case("ns: namespace の中のクラスで cpp も namespace ブロック", h4cls, h4cls.Replace("int x)", "int x, int y)"), "namespace game {\nvoid A::F(int x) {}\n}\n", "namespace game {\nvoid A::F(int x, int y) {}\n}\n");
        string h4g = "void F(int x);\nnamespace n {\nvoid F(int x);\n}\n";
        string c4g = "void F(int x) {}\nvoid n::F(int x) {}\n";
        Case("ns: グローバルの F を変える", h4g, h4g.Replace("void F(int x);\nnamespace", "void F(int x, int y);\nnamespace"), c4g, "void F(int x, int y) {}\nvoid n::F(int x) {}\n");
        Case("ns: n::F を変える", h4g, h4g.Replace("namespace n {\nvoid F(int x)", "namespace n {\nvoid F(int x, int y)"), c4g, "void F(int x) {}\nvoid n::F(int x, int y) {}\n");
        // 別の namespace にある同名クラス
        string h4cc = "namespace a {\nclass W {\n public:\n  void F(int x);\n};\n}\nnamespace b {\nclass W {\n public:\n  void F(int x);\n};\n}\n";
        string c4cc = "void a::W::F(int x) {}\nvoid b::W::F(int x) {}\n";
        Case("ns: 別 namespace の同名クラス a", h4cc, h4cc.Replace("namespace a {\nclass W {\n public:\n  void F(int x)", "namespace a {\nclass W {\n public:\n  void F(int x, int y)"), c4cc,
             "void a::W::F(int x, int y) {}\nvoid b::W::F(int x) {}\n");

        // ---- 5. コンストラクター・初期化子リスト・修飾 ----
        string h5 = "class A {\n public:\n  explicit A(int a);\n  virtual void G(int a) const override;\n  static void S(int a);\n};\n";
        Case("ctor: 初期化子リスト", h5, h5.Replace("A(int a)", "A(int a, int b)"), "A::A(int a) : a_(a), b_{0}, c_(Foo(a, 1)) { Init(); }\n",
             "A::A(int a, int b) : a_(a), b_{0}, c_(Foo(a, 1)) { Init(); }\n");
        Case("virtual const override", h5, h5.Replace("G(int a)", "G(int a, int b)"), "void A::G(int a) const {}\n", "void A::G(int a, int b) const {}\n");
        Case("static", h5, h5.Replace("S(int a)", "S(int a, int b)"), "void A::S(int a) {}\n", "void A::S(int a, int b) {}\n");
        string h5api = "class ENGINE_API A {\n public:\n  ENGINE_API void F(int a);\n};\n";
        Case("API マクロ", h5api, h5api.Replace("F(int a)", "F(int a, int b)"), "void A::F(int a) {}\n", "void A::F(int a, int b) {}\n");

        // ---- 6. 型の書き方 ----
        string h6 = "class A {\n public:\n  void F(std::map<int, int> m, int b);\n};\n";
        Case("テンプレートの引数にカンマ", h6, h6.Replace("int b)", "int b, float c)"), "void A::F(std::map<int, int> m, int b) {}\n", "void A::F(std::map<int, int> m, int b, float c) {}\n");
        string h6f = "class A {\n public:\n  void F(std::function<void(int, int)> cb);\n};\n";
        Case("std::function の引数", h6f, h6f.Replace("cb)", "cb, int n)"), "void A::F(std::function<void(int, int)> cb) {}\n", "void A::F(std::function<void(int, int)> cb, int n) {}\n");
        string h6p = "class A {\n public:\n  void F(const std::string& s, int (*fn)(int), int a[4]);\n};\n";
        Case("参照・関数ポインター・配列", h6p, h6p.Replace("a[4])", "a[4], bool z)"), "void A::F(const std::string& s, int (*fn)(int), int a[4]) {}\n",
             "void A::F(const std::string& s, int (*fn)(int), int a[4], bool z) {}\n");
        Case("型の書き方の違い(const の位置・スペース)", "class A {\n public:\n  void F(const Foo& f);\n};\n", "class A {\n public:\n  void F(const Foo& f, int n);\n};\n",
             "void A::F(Foo const & f) {}\n", "void A::F(Foo const & f, int n) {}\n");

        // ---- 7. 並べ替え・削除 ----
        string h7 = "class A {\n public:\n  void F(int a, float b, bool c);\n};\n";
        Case("並べ替え+削除", h7, h7.Replace("int a, float b, bool c", "bool c, int a"), "void A::F(int a, float b, bool c) {}\n", "void A::F(bool c, int a) {}\n");
        Case("全部消す", h7, h7.Replace("int a, float b, bool c", ""), "void A::F(int a, float b, bool c) {}\n", "void A::F() {}\n");
        Case("(void) の cpp に足す", "class A {\n public:\n  void F();\n};\n", "class A {\n public:\n  void F(int a);\n};\n", "void A::F(void) {}\n", "void A::F(int a) {}\n");

        // ---- 8. 書式 ----
        string h8 = "class A {\n public:\n  void F(int a, int b);\n};\n";
        Case("cpp は複数行の引数", h8, h8.Replace("int b)", "int b, int c)"), "void A::F(int a,\n          int b) {}\n", "void A::F(int a,\n          int b,\n          int c) {}\n");
        Case("CRLF", h8.Replace("\n", "\r\n"), h8.Replace("\n", "\r\n").Replace("int b)", "int b, int c)"), "void A::F(int a,\r\n          int b) {}\r\n", "void A::F(int a,\r\n          int b,\r\n          int c) {}\r\n");
        Case("コメントが引数の間にある", h8, h8.Replace("int b)", "int b, int c)"), "void A::F(int a /* 回数 */, int b) {}\n", "void A::F(int a /* 回数 */, int b, int c) {}\n");

        // ---- 9. 相手にならないもの・見つからないもの ----
        Check("相手の定義がない", Sync("class A {\n public:\n  void Orphan(int a);\n};\n", "class A {\n public:\n  void Orphan(int a, int b);\n};\n", "void A::Other(int a) {}\n"), "!見つからない");
        Check("クラスの中の本体", Sync("class A {\n public:\n  void F(int a) { x_ = a; }\n};\n", "class A {\n public:\n  void F(int a, int b) { x_ = a; }\n};\n", "void A::F(int a) {}\n"), "!相手なし(クラスの中の本体)");
        Check("書きかけ(末尾のカンマ)", Sync(h8, h8.Replace("int b)", "int b, )"), "void A::F(int a, int b) {}\n"), "!書きかけ");
        Check("もう合っている", Sync(h8, h8.Replace("int b)", "int b, int c)"), "void A::F(int a, int b, int c) {}\n"), "!もう合っている");
        Check("演算子は対象外(落ちない)", Sync("class A {\n public:\n  A& operator=(const A& o);\n  void F(int a);\n};\n", "class A {\n public:\n  A& operator=(const A& o);\n  void F(int a, int b);\n};\n", "void A::F(int a) {}\n"),
              "void A::F(int a, int b) {}\n");
        Check("同じ関数が cpp に 2 つ", Sync(h8, h8.Replace("int b)", "int b, int c)"), "void A::F(int a, int b) {}\nvoid A::F(int a, int b) {}\n"), "!複数ある");

        // ---- 10. 自由関数・テンプレート ----
        Case("自由関数", "void Util(int a);\n", "void Util(int a, int b);\n", "void Util(int a) {}\n", "void Util(int a, int b) {}\n");
        Case("テンプレートメンバー", "class A {\n public:\n  template <typename T>\n  void Set(T v);\n};\n", "class A {\n public:\n  template <typename T>\n  void Set(T v, int n);\n};\n",
             "template <typename T>\nvoid A::Set(T v) {}\n", "template <typename T>\nvoid A::Set(T v, int n) {}\n");
        Case("struct と public 既定", "struct P {\n  void F(int a);\n};\n", "struct P {\n  void F(int a, int b);\n};\n", "void P::F(int a) {}\n", "void P::F(int a, int b) {}\n");

        // ---- 11. さらに壊れやすそうなもの ----
        string h11a = "class A {\n public:\n  void F(Foo *p, int &r);\n};\n";
        Case("ポインター・参照のスペースの違い", h11a, h11a.Replace("int &r)", "int &r, int n)"), "void A::F(Foo* p, int& r) {}\n", "void A::F(Foo* p, int& r, int n) {}\n");
        string h11b = "class Outer1 {\n public:\n  class Inner {\n   public:\n    void F(int x);\n  };\n};\nclass Outer2 {\n public:\n  class Inner {\n   public:\n    void F(int x);\n  };\n};\n";
        Case("入れ子クラスの同名(Outer1)", h11b, h11b.Replace("class Outer1 {\n public:\n  class Inner {\n   public:\n    void F(int x)", "class Outer1 {\n public:\n  class Inner {\n   public:\n    void F(int x, int y)"),
             "void Outer1::Inner::F(int x) {}\nvoid Outer2::Inner::F(int x) {}\n", "void Outer1::Inner::F(int x, int y) {}\nvoid Outer2::Inner::F(int x) {}\n");
        string h11c = "class A {\n public:\n  auto F(int a) -> int;\n  [[nodiscard]] int G(int a) const noexcept;\n};\n";
        Case("後置の戻り値の型", h11c, h11c.Replace("auto F(int a)", "auto F(int a, int b)"), "auto A::F(int a) -> int { return a; }\n", "auto A::F(int a, int b) -> int { return a; }\n");
        Case("[[nodiscard]] と noexcept", h11c, h11c.Replace("G(int a)", "G(int a, int b)"), "int A::G(int a) const noexcept { return a; }\n", "int A::G(int a, int b) const noexcept { return a; }\n");
        string h11d = "class A {\n public:\n  void F(const char* s = \"a,b)\", int n = 0);\n};\n";
        Case("既定値の文字列にカンマと括弧", h11d, h11d.Replace("int n = 0)", "int n = 0, int m = 1)"), "void A::F(const char* s, int n) {}\n", "void A::F(const char* s, int n, int m) {}\n");
        string h11e = "class A {\n public:\n  void F(std::vector<std::pair<int, int>> v, Args&&... args);\n};\n";
        Case("入れ子のテンプレートと可変長引数", h11e, h11e.Replace("Args&&... args)", "Args&&... args, int z)"), "void A::F(std::vector<std::pair<int, int>> v, Args&&... args) {}\n", "void A::F(std::vector<std::pair<int, int>> v, Args&&... args, int z) {}\n");
        Case("cpp で引数を消すと、ヘッダーの既定値も消える", "void A::F(int a, int b) {}\n", "void A::F(int a) {}\n", "class A {\n public:\n  void F(int a, int b = 0);\n};\n", "class A {\n public:\n  void F(int a);\n};\n");
        CaseCpp("cpp に足す: 既定値のないヘッダー", "void A::F(int a) {}\n", "void A::F(int a, int b) {}\n", "class A {\n public:\n  void F(int a);\n};\n", "class A {\n public:\n  void F(int a, int b);\n};\n");
        CaseCpp("cpp で型だけ変える: ヘッダーも型が変わる", "void A::F(int x) {}\n", "void A::F(float x) {}\n", "class A {\n public:\n  void F(int a);\n};\n", "class A {\n public:\n  void F(float a);\n};\n");
        Check("extern \"C\" の中", Sync("extern \"C\" {\nvoid F(int a);\n}\n", "extern \"C\" {\nvoid F(int a, int b);\n}\n", "void F(int a) {}\n"), "void F(int a, int b) {}\n");
        Check("無名 namespace", Sync("namespace {\nvoid F(int a);\n}\n", "namespace {\nvoid F(int a, int b);\n}\n", "namespace {\nvoid F(int a) {}\n}\n"), "namespace {\nvoid F(int a, int b) {}\n}\n");
        Check("= default は相手なし", Sync("class A {\n public:\n  A(int a) = default;\n};\n", "class A {\n public:\n  A(int a, int b) = default;\n};\n", "A::A(int a) {}\n"), "A::A(int a, int b) {}\n");

        Check("既定値の順序: 後ろに既定値なしが来る", SignatureSync.DefaultsOutOfOrder(SignatureSync.SplitParams("int a = 3, int b")).ToString(), "True");
        Check("既定値の順序: 正しい", SignatureSync.DefaultsOutOfOrder(SignatureSync.SplitParams("int a, int b = 3, int c = 4")).ToString(), "False");

        Console.WriteLine("sync: pass=" + pass + " fail=" + fail);
        return fail;
    }
}
