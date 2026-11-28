using System;
using System.Collections.Generic;
using System.Linq;
using KCppAssist;

/// <summary>#include を前方宣言に置き換える部分(ForwardDecl)のテスト。</summary>
static class FwdTests
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

    const string Scene = "#pragma once\nnamespace game {\nclass Scene {};\nstruct Camera {};\n}\n";

    static string Make(string header, string incPath, string provider)
    {
        var inc = IncludeTidy.Parse(header).First(i => i.Path == incPath);
        string why;
        var r = ForwardDecl.Make(header, inc, ForwardDecl.Types(provider), IncludeTidy.Provided(provider), "\n", out why);
        return r == null ? "!" + why : r.NewText + "|" + r.CppToken + "|" + string.Join(",", r.Names);
    }

    public static int Run()
    {
        Check("ポインターだけなら前方宣言にする",
            Make("#pragma once\n#include <vector>\n#include \"scene.h\"\n\nclass Game {\n public:\n  void Set(game::Scene* s);\n  game::Camera& cam();\n};\n", "scene.h", Scene),
            "#pragma once\n#include <vector>\n\nnamespace game {\nclass Scene;\nstruct Camera;\n}  // namespace game\n\nclass Game {\n public:\n  void Set(game::Scene* s);\n  game::Camera& cam();\n};\n|\"scene.h\"|Scene,Camera");

        Check("値のメンバーは、前方宣言にできない",
            Make("#include \"scene.h\"\nclass G {\n  game::Scene s_;\n};\n", "scene.h", Scene).StartsWith("!") ? "refused" : "made", "refused");

        Check("継承は、前方宣言にできない",
            Make("#include \"scene.h\"\nclass G : public game::Scene {};\n", "scene.h", Scene).StartsWith("!") ? "refused" : "made", "refused");

        Check("関数の本体の中で使うなら、前方宣言にできない",
            Make("#include \"scene.h\"\nclass G {\n  void F(game::Scene* s) { game::Scene* t = s; }\n};\n", "scene.h", Scene).StartsWith("!") ? "refused" : "made", "refused");

        Check("shared_ptr の中は、前方宣言にできる",
            Make("#include <memory>\n#include \"scene.h\"\nclass G {\n  std::shared_ptr<game::Scene> s_;\n};\n", "scene.h", Scene),
            "#include <memory>\n\nnamespace game {\nclass Scene;\n}  // namespace game\n\nclass G {\n  std::shared_ptr<game::Scene> s_;\n};\n|\"scene.h\"|Scene");

        // unique_ptr も前方宣言にできる(コンストラクター・デストラクターは、呼び出し側が MoveSpecialsOut で cpp に移す)
        Check("unique_ptr の中は、前方宣言にできる",
            Make("#include <memory>\n#include \"scene.h\"\nclass G {\n  std::unique_ptr<game::Scene> s_;\n};\n", "scene.h", Scene).StartsWith("!") ? "refused" : "made", "made");

        // ---- unique_ptr のクラスの、コンストラクター・デストラクター・ムーブを宣言だけにする ----
        string ecm = "namespace Prest {\n\tclass TCPServer;\n\tclass E\n\t{\n\tpublic:\n\t\tE() = default;\n\t\t~E() = default;\n\t\tE(const E&) = delete;\n\t\tE& operator=(const E&) = delete;\n\t\tE(E&&) noexcept = default;\n\t\tE& operator=(E&&) noexcept = default;\n\n\t\tstd::unique_ptr<TCPServer> server_;\n\t};\n}\n";
        List<string> mv;
        Check("unique_ptr: specials become declarations", ForwardDecl.MoveSpecialsOut(ecm, new[] { "TCPServer" }, "\n", out mv),
            "namespace Prest {\n\tclass TCPServer;\n\tclass E\n\t{\n\tpublic:\n\t\tE();\n\t\t~E();\n\t\tE(const E&) = delete;\n\t\tE& operator=(const E&) = delete;\n\t\tE(E&&) noexcept;\n\t\tE& operator=(E&&) noexcept;\n\n\t\tstd::unique_ptr<TCPServer> server_;\n\t};\n}\n");
        Check("unique_ptr: moved list", string.Join(",", mv), "E::E,E::~E,E::E(&&),E::operator=(&&)");
        string nodtor = "class G {\n public:\n  void F();\n private:\n  std::unique_ptr<Scene> s_;\n};\n";
        Check("unique_ptr: adds ~G(); when missing", ForwardDecl.MoveSpecialsOut(nodtor, new[] { "game::Scene" }, "\n", out mv),
            "class G {\n public:\n  ~G();\n\n  void F();\n private:\n  std::unique_ptr<Scene> s_;\n};\n");
        Check("unique_ptr: other class untouched", ForwardDecl.MoveSpecialsOut("class G {\n public:\n  ~G() = default;\n  std::unique_ptr<Other> o_;\n};\n", new[] { "Scene" }, "\n", out mv), "class G {\n public:\n  ~G() = default;\n  std::unique_ptr<Other> o_;\n};\n");
        Check("unique_ptr: = default body", ForwardDecl.AsDefaulted("E::~E()\n{\n}", "\n"), "E::~E() = default;");

        Check("型以外(定数・関数)も使っていれば、残す",
            Make("#include \"util.h\"\nclass G {\n  Widget* w_;\n  int n_ = kMax;\n};\n", "util.h", "class Widget {};\nconstexpr int kMax = 3;\n").StartsWith("!") ? "refused" : "made", "refused");

        Check("使っていない型は、理由を返す",
            Make("#include \"scene.h\"\nclass G {};\n", "scene.h", Scene),
            "!このヘッダーの型を、使っていません");

        Check("グローバルの型は namespace なし",
            Make("#pragma once\n#include \"w.h\"\nclass G {\n  Widget* w_;\n};\n", "w.h", "class Widget {};\n"),
            "#pragma once\n\nclass Widget;\n\nclass G {\n  Widget* w_;\n};\n|\"w.h\"|Widget");

        Check("template のクラスは対象にしない",
            ForwardDecl.Types("template <typename T>\nclass Box {};\nclass Plain {};\n").Count + "", "1");

        Console.WriteLine("fwd: pass=" + pass + " fail=" + fail);
        return fail == 0 ? 0 : 1;
    }
}
