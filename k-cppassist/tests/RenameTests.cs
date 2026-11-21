using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using KCppAssist;

// ファイル名の変更を、相手・#include・CMake に写す部分(RenameSync)のテスト
static class RenameTests
{
    static int pass, fail;

    static void Check(string name, bool ok)
    {
        if (ok) pass++; else { fail++; Console.WriteLine("FAIL: " + name); }
    }

    static RenameSync.Move M(string a, string b) { return new RenameSync.Move { Old = a, New = b }; }

    static string Fix(string text, string dir, RenameSync.Move[] moves, string[] roots, Func<string, bool> exists = null)
    {
        return RenameSync.Apply(text, RenameSync.RewriteIncludes(text, dir, moves, roots, exists));
    }

    static void Main()
    {
        // ---- 相手の決め方 ----
        var files = new HashSet<string>(StringComparer.OrdinalIgnoreCase) { @"C:\p\src\Foo.h", @"C:\p\src\Foo.cpp", @"C:\p\src\Baz.hpp", @"C:\p\src\Baz.cc" };
        Func<string, bool> ex = files.Contains;

        var p = RenameSync.PairOf(@"C:\p\src\Foo.h", @"C:\p\src\Bar.h", ex);
        Check("header rename finds cpp", p != null && p.Old == @"C:\p\src\Foo.cpp" && p.New == @"C:\p\src\Bar.cpp");
        p = RenameSync.PairOf(@"C:\p\src\Foo.cpp", @"C:\p\src\Bar.cpp", ex);
        Check("cpp rename finds header", p != null && p.Old == @"C:\p\src\Foo.h" && p.New == @"C:\p\src\Bar.h");
        p = RenameSync.PairOf(@"C:\p\src\Baz.hpp", @"C:\p\src\Qux.hpp", ex);
        Check("hpp finds cc", p != null && p.Old == @"C:\p\src\Baz.cc" && p.New == @"C:\p\src\Qux.cc");
        Check("same stem (extension only) is not a rename", RenameSync.PairOf(@"C:\p\src\Foo.h", @"C:\p\src\Foo.hpp", ex) == null);
        Check("moved to another folder is not handled", RenameSync.PairOf(@"C:\p\src\Foo.h", @"C:\p\core\Bar.h", ex) == null);
        files.Add(@"C:\p\src\Bar.cpp");
        Check("new name already used", RenameSync.PairOf(@"C:\p\src\Foo.h", @"C:\p\src\Bar.h", ex) == null);
        Check("no pair", RenameSync.PairOf(@"C:\p\src\Solo.h", @"C:\p\src\Solo2.h", ex) == null);
        Check("non-code file has no pair", RenameSync.PairOf(@"C:\p\src\Foo.txt", @"C:\p\src\Bar.txt", ex) == null);

        // ---- #include ----
        var moves = new[] { M(@"C:\p\src\Foo.h", @"C:\p\src\Bar.h"), M(@"C:\p\src\Foo.cpp", @"C:\p\src\Bar.cpp") };
        string t1 = "#include \"Foo.h\"\n#include <vector>\n#include \"Other.h\"\n";
        Check("same-folder include", Fix(t1, @"C:\p\src", moves, null) == "#include \"Bar.h\"\n#include <vector>\n#include \"Other.h\"\n");

        var mv2 = new[] { M(@"C:\p\src\core\Foo.h", @"C:\p\src\core\Bar.h") };
        string t2 = "#include \"core/Foo.h\"\n#include \"../src/core/Foo.h\"\n";
        string r2 = Fix(t2, @"C:\p\src\render", mv2, new[] { @"C:\p\src" });
        Check("root-relative include", r2.StartsWith("#include \"core/Bar.h\""));
        Check("dotdot include (via includer dir)", r2.Contains("#include \"../src/core/Bar.h\""));

        string t3 = "#include \"Foo.h\"\n";
        Check("same name, different file in the includer folder is untouched",
            Fix(t3, @"C:\p\other", moves, new[] { @"C:\p\src" }, f => string.Equals(f, @"C:\p\other\Foo.h", StringComparison.OrdinalIgnoreCase)) == t3);
        Check("no local file: the root one is the moved file", Fix(t3, @"C:\p\other", moves, new[] { @"C:\p\src" }) == "#include \"Bar.h\"\n");
        Check("an earlier root with a real file shadows the later one",
            Fix(t3, @"C:\p\other", moves, new[] { @"C:\p\inc", @"C:\p\src" }, f => string.Equals(f, @"C:\p\inc\Foo.h", StringComparison.OrdinalIgnoreCase)) == t3);
        Check("angle include via root", Fix("#include <core/Foo.h>\n", @"C:\p\app", mv2, new[] { @"C:\p\src" }) == "#include <core/Bar.h>\n");
        Check("angle include without root is untouched", Fix("#include <Foo.h>\n", @"C:\p\src", moves, null) == "#include <Foo.h>\n");
        Check("case-insensitive name", Fix("#include \"foo.H\"\n", @"C:\p\src", moves, null) == "#include \"Bar.h\"\n");
        Check("spacing around include is kept", Fix("  #  include   \"Foo.h\"   // note\n", @"C:\p\src", moves, null) == "  #  include   \"Bar.h\"   // note\n");
        Check("both files renamed in one text", Fix("#include \"Foo.h\"\n#include \"Foo.cpp\"\n", @"C:\p\src", moves, null) == "#include \"Bar.h\"\n#include \"Bar.cpp\"\n");

        // ---- CMake ----
        var cm = new[] { M(@"C:\p\src\Foo.cpp", @"C:\p\src\Bar.cpp") };
        string c1 = "add_executable(app src/Foo.cpp src/MyFoo.cpp src/Foo.cpp.in)\n";
        string r3 = RenameSync.Apply(c1, RenameSync.RewriteBuildFile(c1, @"C:\p", cm));
        Check("cmake: only the exact file", r3 == "add_executable(app src/Bar.cpp src/MyFoo.cpp src/Foo.cpp.in)\n");
        string c2 = "target_sources(app PRIVATE Foo.cpp\n  Other.cpp)\n";
        Check("cmake: bare name in the same folder", RenameSync.Apply(c2, RenameSync.RewriteBuildFile(c2, @"C:\p\src", cm)) == "target_sources(app PRIVATE Bar.cpp\n  Other.cpp)\n");
        string c3 = "set(SRC \"src\\Foo.cpp\")\n";
        Check("cmake: backslash form", RenameSync.Apply(c3, RenameSync.RewriteBuildFile(c3, @"C:\p", cm)) == "set(SRC \"src\\Bar.cpp\")\n");
        string c4 = "add_library(x ../src/Foo.cpp)\n";
        Check("cmake: dotdot relative", RenameSync.Apply(c4, RenameSync.RewriteBuildFile(c4, @"C:\p\app", cm)) == "add_library(x ../src/Bar.cpp)\n");

        // ---- 編集の適用 ----
        string a = "0123456789";
        var edits = new List<RenameSync.TextEdit>
        {
            new RenameSync.TextEdit { Start = 7, Length = 2, Text = "X" },
            new RenameSync.TextEdit { Start = 1, Length = 3, Text = "AB" },
            new RenameSync.TextEdit { Start = 2, Length = 1, Text = "overlap" },
        };
        Check("apply edits (ordered, overlap dropped)", RenameSync.Apply(a, edits) == "0AB456X9");

        // ---- 文字コードを保つ ----
        string dir = Path.Combine(Path.GetTempPath(), "kcppassist-rename-" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(dir);
        try
        {
            string jp = "#include \"Foo.h\"\n// 日本語のコメント\n";
            foreach (var enc in new Encoding[] { new UTF8Encoding(false), new UTF8Encoding(true), Encoding.GetEncoding(932) })
            {
                string path = Path.Combine(dir, "t" + enc.CodePage + (enc.GetPreamble().Length > 0 ? "bom" : "") + ".cpp");
                byte[] src = enc.GetPreamble().Concat(enc.GetBytes(jp)).ToArray();
                File.WriteAllBytes(path, src);
                Encoding got;
                string text = RenameSync.ReadKeepingEncoding(path, out got);
                Check("read text (" + enc.WebName + (enc.GetPreamble().Length > 0 ? " BOM" : "") + ")", text == jp);
                RenameSync.WriteKeepingEncoding(path, text, got);
                Check("round trip keeps bytes (" + enc.WebName + (enc.GetPreamble().Length > 0 ? " BOM" : "") + ")", File.ReadAllBytes(path).SequenceEqual(src));
            }
        }
        finally { try { Directory.Delete(dir, true); } catch (Exception) { } }

        // ---- 自分で決める対応 (設定) ----
        var custom = StdHeaders.ParseCustom("Vec3=\"math/vec3.h\";Json=<nlohmann/json.hpp>\nBad=foo;=x;NoHeader=;Empty=\"\"");
        Check("custom: two valid entries", custom.Count == 2 && custom["Vec3"] == "\"math/vec3.h\"" && custom["Json"] == "<nlohmann/json.hpp>");
        Check("custom: empty text", StdHeaders.ParseCustom("").Count == 0 && StdHeaders.ParseCustom(null).Count == 0);
        Check("custom: spaces are trimmed", StdHeaders.ParseCustom("  A = <a.h>  ")["A"] == "<a.h>");

        // ---- クラス名 ----
        var cls = RenameSync.ClassesIn("#pragma once\nclass Fwd;\nclass FOO_API Widget final : public Base {\n};\nstruct Pod {\n};\n");
        Check("classes: definitions only, in order", cls.Count == 2 && cls[0] == "Widget" && cls[1] == "Pod");
        Check("pick: same name ignoring case/underscore", RenameSync.PickClass(new[] { "Pod", "game_object" }, "GameObject") == "game_object");
        Check("pick: falls back to the first", RenameSync.PickClass(new[] { "Pod", "Other" }, "Foo") == "Pod");
        Check("pick: none", RenameSync.PickClass(new string[0], "Foo") == null);
        string src2 = "Foo f; FooBar g; m_Foo h; Foo::Foo() {} // Foo";
        Check("replace word: whole word only", RenameSync.Apply(src2, RenameSync.ReplaceWord(src2, "Foo", "Bar")) == "Bar f; FooBar g; m_Foo h; Bar::Bar() {} // Bar");

        // ---- フォルダーの名前の変更 ----
        var fmoves = new[] { M(@"C:\p\src\Render\Mesh.h", @"C:\p\src\Draw\Mesh.h"), M(@"C:\p\src\Render\Mesh.cpp", @"C:\p\src\Draw\Mesh.cpp") };
        Check("folder: include with folder", Fix("#include \"Render/Mesh.h\"\n", @"C:\p\src", fmoves, new string[0]) == "#include \"Draw/Mesh.h\"\n");
        Check("folder: include from root", Fix("#include \"src/Render/Mesh.h\"\n", @"C:\p\app", fmoves, new[] { @"C:\p" }) == "#include \"src/Draw/Mesh.h\"\n");
        Check("folder: same-folder include unchanged", Fix("#include \"Mesh.h\"\n", @"C:\p\src\Draw", fmoves, new string[0]) == "#include \"Mesh.h\"\n");

        // ---- コーディング スタイルごとの、ファイル名とクラス名の対応 ----
        string pre;
        Check("google: game_object corresponds to GameObject", RenameSync.Corresponds("GameObject", "game_object", out pre) && pre == "");
        Check("google: file -> class", RenameSync.ClassForNewStem("GameObject", "", "game_entity") == "GameEntity");
        Check("google: class -> file", RenameSync.StemForNewClass("GameEntity", "", "game_object") == "game_entity");
        Check("same: file -> class", RenameSync.ClassForNewStem("GameObject", "", "GameEntity") == "GameEntity");
        Check("same: class -> file", RenameSync.StemForNewClass("GameEntity", "", "GameObject") == "GameEntity");
        Check("acronym kept", RenameSync.StemForNewClass("HTTPServer", "", "GameObject") == "HTTPServer");
        Check("snake class & file", RenameSync.ClassForNewStem("game_object", "", "game_entity") == "game_entity");
        Check("snake class, pascal file", RenameSync.ClassForNewStem("game_object", "", "GameEntity") == "game_entity");
        Check("unreal: APawn corresponds to Pawn", RenameSync.Corresponds("APlayerController", "PlayerController", out pre) && pre == "A");
        Check("unreal: file -> class", RenameSync.ClassForNewStem("APlayerController", "A", "PlayerBrain") == "APlayerBrain");
        Check("unreal: class -> file", RenameSync.StemForNewClass("APlayerBrain", "A", "PlayerController") == "PlayerBrain");
        Check("mfc: CPlayer in player.h", RenameSync.Corresponds("CPlayer", "player", out pre) && pre == "C");
        Check("mfc: class -> snake file", RenameSync.StemForNewClass("CEnemyUnit", "C", "player") == "enemyunit");
        Check("Cat is not C + at", !RenameSync.Corresponds("Cat", "at", out pre));
        Check("kebab file", RenameSync.StemForNewClass("GameEntity", "", "game-object") == "game-entity");
        Check("camel class", RenameSync.ClassForNewStem("gameObject", "", "game_entity") == "gameEntity");
        Check("pick class by prefix", RenameSync.PickClass(new List<string> { "Helper", "UHealthComponent" }, "HealthComponent") == "UHealthComponent");

        Console.WriteLine("rename: pass=" + pass + " fail=" + fail);
        Environment.Exit(fail == 0 ? 0 : 1);
    }
}
