using System;
using System.Linq;
using KCppAssist;

/// <summary>宣言から定義の雛形、定義から宣言を作る部分(DefinitionGen)のテスト。</summary>
static class DefTests
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

    /// <summary>header の「name」という宣言(overload は引数に whole が含まれるもの)の雛形を cpp に足した結果。作れなければ "!理由"。</summary>
    static string Def(string header, string cpp, string name, string argHint = null)
    {
        var sig = FunctionScan.Scan(header).First(s => !s.HasBody && s.Name == name && (argHint == null || s.Inner(header).Contains(argHint)));
        string why;
        var e = DefinitionGen.PlanDefinition(header, sig, cpp, "\n", out why);
        if (e == null) return "!" + why;
        return cpp.Substring(0, e.Position) + e.Text + cpp.Substring(e.Position);
    }

    static string Decl(string cpp, string name)
    {
        var sig = FunctionScan.Scan(cpp).First(s => s.HasBody && s.Name == name);
        string why;
        return DefinitionGen.DeclarationFor(cpp, sig, out why) ?? "!" + why;
    }

    static string Member(string header, string className, string declaration)
    {
        var scope = Scopes.Parse(header).First(s => s.IsClass && s.Name == className);
        var e = DefinitionGen.PlanPublicMember(header, scope.Open, scope.IsStruct, declaration, "\n");
        if (e == null) return "!読めない";
        return header.Substring(0, e.Position) + e.Text + header.Substring(e.Position);
    }

    public static int Run()
    {
        // ---- 宣言 → 定義 ----
        string h1 = "class A {\n public:\n  void F(int a);\n  int G(float x, int y = 3) const;\n  static A* Create();\n  virtual void V(int a) override;\n  explicit A(int n);\n};\n";
        Check("末尾に足す(cpp が空)", Def(h1, "", "F"), "void A::F(int a)\n{\n}\n");
        Check("戻り値・const・既定値の除去", Def(h1, "", "G"), "int A::G(float x, int y) const\n{\n  return 0;\n}\n");
        Check("static を落とす・ポインターは nullptr", Def(h1, "", "Create"), "A* A::Create()\n{\n  return nullptr;\n}\n");
        Check("virtual・override を落とす", Def(h1, "", "V"), "void A::V(int a)\n{\n}\n");
        Check("コンストラクターは戻り値なし", Def(h1, "", "A"), "A::A(int n)\n{\n}\n");
        Check("同じクラスの前の定義の直後", Def("class A {\n public:\n  void F(int a);\n  void H(int a);\n};\n", "void A::F(int a) {\n  x = a;\n}\nvoid Other() {}\n", "H"),
              "void A::F(int a) {\n  x = a;\n}\n\nvoid A::H(int a)\n{\n}\nvoid Other() {}\n");
        Check("= 0 は作らない", Def("class A {\n public:\n  virtual void P() = 0;\n};\n", "", "P"), "!純粋仮想・= default・= delete の関数は、定義を作りません");
        Check("= default は作らない", Def("class A {\n public:\n  A() = default;\n};\n", "", "A"), "!純粋仮想・= default・= delete の関数は、定義を作りません");
        Check("friend は作らない", Def("class A {\n friend void F(A&);\n};\n", "", "F"), "!friend・constexpr・template の関数は、雛形を作りません");
        Check("参照を返すときは return を書かない", Def("class A {\n public:\n  int& Ref();\n};\n", "", "Ref"), "int& A::Ref()\n{\n}\n");
        Check("bool は false", Def("class A {\n public:\n  bool Ok() const;\n};\n", "", "Ok"), "bool A::Ok() const\n{\n  return false;\n}\n");
        Check("クラス型は {}", Def("class A {\n public:\n  std::string Name() const;\n};\n", "", "Name"), "std::string A::Name() const\n{\n  return {};\n}\n");
        Check("noexcept と後置の戻り値の型", Def("class A {\n public:\n  auto F(int a) const noexcept -> int;\n};\n", "", "F"), "auto A::F(int a) const noexcept -> int\n{\n}\n");
        Check("SAL 注釈と export マクロを落とす", Def("class A {\n public:\n  DX_API void __cdecl Draw(_In_ ID3D11Device* d, _Out_ int* n);\n};\n", "", "Draw"), "void A::Draw(ID3D11Device* d, int* n)\n{\n}\n");
        Check("コメントと public: を落とす", Def("class A {\n public:\n  // 描く\n  void F();\n};\n", "", "F"), "void A::F()\n{\n}\n");
        Check("namespace の中のクラスは完全修飾", Def("namespace g {\nclass A {\n public:\n  void F();\n};\n}\n", "", "F"), "void g::A::F()\n{\n}\n");
        Check("cpp が namespace の中なら、修飾しない", Def("namespace g {\nclass A {\n public:\n  void F();\n  void H();\n};\n}\n", "namespace g {\nvoid A::F() {}\n}  // namespace g\n", "H"),
              "namespace g {\nvoid A::F() {}\n\nvoid A::H()\n{\n}\n}  // namespace g\n");
        Check("自由関数(namespace の中)", Def("namespace g {\nvoid Free(int a);\n}\n", "", "Free"), "void g::Free(int a)\n{\n}\n");
        Check("グローバルの自由関数", Def("void Free(int a);\n", "", "Free"), "void Free(int a)\n{\n}\n");
        {
            string hdr = "class A {\n public:\n  void F();\n};\n";
            string why;
            var e = DefinitionGen.PlanDefinition(hdr, FunctionScan.Scan(hdr).First(x => x.Name == "F"), "int x;\r\n", "\r\n", out why);
            Check("CRLF の cpp には CRLF で足す", ("int x;\r\n".Substring(0, e.Position) + e.Text).Replace("\r", "R"), "int x;R\nR\nvoid A::F()R\n{R\n}R\n");
        }

        // ---- 定義 → 宣言 ----
        Check("基本", Decl("int A::G(float x, int y) const { return 1; }\n", "G"), "int G(float x, int y) const;");
        Check("_Use_decl_annotations_ と static を落とす", Decl("_Use_decl_annotations_ void A::F(int a) {}\n", "F"), "void F(int a);");
        Check("コンストラクターの初期化子リストを除く", Decl("A::A(int n) : x_(n), y_{0} {}\n", "A"), "A(int n);");
        Check("後置の戻り値の型", Decl("auto A::F(int a) const noexcept -> std::string { return {}; }\n", "F"), "auto F(int a) const noexcept -> std::string;");
        Check("自由関数は対象外", Decl("void Free(int a) {}\n", "Free"), "!Class::Func の形の定義ではありません");
        Check("template は対象外", Decl("template <typename T>\nvoid A::Set(T v) {}\n", "Set"), "!template・constexpr などの関数は、宣言を作りません");

        // ---- クラスの public に足す ----
        Check("public の末尾", Member("class A {\n public:\n  void F();\n\n private:\n  int x_;\n};\n", "A", "void G();"), "class A {\n public:\n  void F();\n  void G();\n\n private:\n  int x_;\n};\n");
        Check("public が最後", Member("class A {\n public:\n  void F();\n};\n", "A", "void G();"), "class A {\n public:\n  void F();\n  void G();\n};\n");
        Check("public が空", Member("class A {\n public:\n\n private:\n  int x_;\n};\n", "A", "void G();"), "class A {\n public:\n  void G();\n\n private:\n  int x_;\n};\n");
        Check("public がない class は末尾に作る", Member("class A {\n private:\n  int x_;\n};\n", "A", "void G();"), "class A {\n private:\n  int x_;\n\n public:\n  void G();\n};\n");
        Check("struct は先頭から public", Member("struct P {\n  int x;\n};\n", "P", "void G();"), "struct P {\n  int x;\n  void G();\n};\n");
        Check("コメントの中の public: は無視", Member("class A {\n public:\n  void F();  // public: です\n private:\n  int x_;\n};\n", "A", "void G();"), "class A {\n public:\n  void F();  // public: です\n  void G();\n private:\n  int x_;\n};\n");

        Console.WriteLine("def: pass=" + pass + " fail=" + fail);
        return fail;
    }
}
