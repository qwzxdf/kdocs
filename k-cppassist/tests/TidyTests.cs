using System;
using System.Collections.Generic;
using System.Linq;
using KCppAssist;

/// <summary>#include の整理と、使っていない #include の検出(IncludeTidy)のテスト。</summary>
static class TidyTests
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

    public static int Run()
    {
        // ---- 整理 ----
        Check("グループ分けと並べ替え",
            IncludeTidy.Organize("#include \"b.h\"\n#include <vector>\n#include \"a.h\"\n#include <stdio.h>\n#include \"scene.h\"\n#include <string>\n\nint x;\n", "scene", "\n"),
            "#include \"scene.h\"\n\n#include <stdio.h>\n\n#include <string>\n#include <vector>\n\n#include \"a.h\"\n#include \"b.h\"\n\nint x;\n");

        Check("重複を消す",
            IncludeTidy.Organize("#include <vector>\n#include <vector>\n#include <string>\n", null, "\n"),
            "#include <string>\n#include <vector>\n");

        Check("すでに整っていれば null",
            IncludeTidy.Organize("#include <string>\n#include <vector>\n\n#include \"a.h\"\n", null, "\n") ?? "null", "null");

        Check("#if の中は触らない",
            IncludeTidy.Organize("#include <vector>\n#include <array>\n#if _WIN32\n#include <windows.h>\n#include <d3d11.h>\n#endif\n", null, "\n"),
            "#include <array>\n#include <vector>\n#if _WIN32\n#include <windows.h>\n#include <d3d11.h>\n#endif\n");

        Check("コメントは次の #include についていく",
            IncludeTidy.Organize("#include <vector>\n// 設定\n#include <array>\n", null, "\n"),
            "// 設定\n#include <array>\n#include <vector>\n");

        Check("CRLF",
            IncludeTidy.Organize("#include <vector>\r\n#include <array>\r\n", null, "\r\n"),
            "#include <array>\r\n#include <vector>\r\n");

        Check("末尾に改行がなくても壊れない",
            IncludeTidy.Organize("#include <vector>\n#include <array>", null, "\n"),
            "#include <array>\n#include <vector>");

        Check("#define をはさむまとまりは別々",
            IncludeTidy.Organize("#define NOMINMAX\n#include <windows.h>\n#include <algorithm>\n", null, "\n"),
            "#define NOMINMAX\n#include <algorithm>\n\n#include <windows.h>\n");

        // ---- 使っていない #include ----
        var tables = new Dictionary<string, ISet<string>>
        {
            { "vector", new HashSet<string> { "vector" } },
            { "string", new HashSet<string> { "string", "to_string" } },
            { "scene.h", new HashSet<string> { "Scene" } },
            { "mystery.h", new HashSet<string>() },
        };
        Func<IncludeTidy.Item, ISet<string>> prov = it => { ISet<string> s; return tables.TryGetValue(it.Path, out s) ? s : null; };

        string cpp = "#include \"a.h\"\n#include <vector>\n#include <string>\n#include \"scene.h\"\n#include \"mystery.h\"\n#include \"unknown.h\"\n\nstd::vector<int> v;\n// std::string は、コメントの中だけ\nconst char* s = \"Scene\";\n";
        var unused = IncludeTidy.Unused(cpp, "a", prov).Select(i => i.Path).OrderBy(p => p).ToList();
        Check("使っていないものだけ", string.Join(",", unused), "scene.h,string");

        Check("自分のヘッダーと keep は残す",
            string.Join(",", IncludeTidy.Unused("#include \"a.h\"\n#include <string> // keep\n", "a", prov).Select(i => i.Path)), "");

        Check("消した結果",
            IncludeTidy.Remove(cpp, IncludeTidy.Unused(cpp, "a", prov)),
            "#include \"a.h\"\n#include <vector>\n#include \"mystery.h\"\n#include \"unknown.h\"\n\nstd::vector<int> v;\n// std::string は、コメントの中だけ\nconst char* s = \"Scene\";\n");

        // ---- ヘッダーが定義している名前 ----
        var names = IncludeTidy.Provided("#pragma once\nclass Foo {};\nenum class Mode { kA, kB = 2 };\nusing Id = int;\ntypedef unsigned long Handle;\n#define MAX_N 8\nconstexpr int kMax = 4;\nvoid Helper(int);\n");
        Check("定義の名前", string.Join(",", names.OrderBy(n => n, StringComparer.Ordinal)), "Foo,Handle,Helper,Id,MAX_N,Mode,kA,kB,kMax");

        Console.WriteLine("tidy: pass=" + pass + " fail=" + fail);
        return fail == 0 ? 0 : 1;
    }
}
