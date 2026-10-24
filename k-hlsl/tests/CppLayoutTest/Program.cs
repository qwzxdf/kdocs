using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;
using KHlsl.Server;

// C++ の構造体のレイアウトの計算を、MSVC(x64)の sizeof / offsetof と突き合わせる。
// 計算した値を static_assert にして、cl でコンパイルする。外れた assert が不一致。
// 使い方: dotnet run -- [ランダム ケースの数]
internal static class Program
{
    private static int Main(string[] args)
    {
        int random = args.Length > 0 ? int.Parse(args[0]) : 150;
        var cases = new List<Tuple<string, string>>(Fixed());
        var rnd = new Random(20260202);
        for (int i = 0; i < random; i++) cases.Add(Generate(rnd, i));

        var cpp = new StringBuilder();
        cpp.AppendLine("#include <cstddef>\n#include <cstdint>\n#include <array>\n#include <DirectXMath.h>\nusing namespace DirectX;");
        var lineInfo = new Dictionary<int, string>();
        int skipped = 0, asserted = 0;
        int n = 0;
        foreach (var c in cases)
        {
            n++;
            var table = CppLayout.Collect(new[] { CBufferLayout.MakeSource("t.cpp", c.Item2) });
            cpp.AppendLine("namespace case" + n + " {");
            cpp.AppendLine(c.Item2);
            foreach (string name in CppLayout.StructNames(table, "t.cpp").Where(nm => !c.Item2.Contains("} in;") || nm != "In"))
            {
                var s = CppLayout.Layout(table, name);
                if (s == null || s.Incomplete || s.Problems.Count > 0)
                {
                    skipped++;
                    Console.WriteLine("SKIP " + c.Item1 + " " + name + ": " + (s == null ? "?" : string.Join("; ", s.Problems)));
                    continue;
                }
                Assert(cpp, lineInfo, c.Item1 + " " + name + " sizeof", "sizeof(" + name + ")", s.Size);
                Assert(cpp, lineInfo, c.Item1 + " " + name + " alignof", "alignof(" + name + ")", s.Align);
                foreach (var m in s.Members)
                    Assert(cpp, lineInfo, c.Item1 + " " + name + "." + m.Name, "offsetof(" + name + ", " + m.Name + ")", m.Offset);
                asserted += s.Members.Count + 2;
            }
            cpp.AppendLine("}");
        }
        string dir = Path.Combine(Path.GetTempPath(), "khlsl-cpptest");
        Directory.CreateDirectory(dir);
        string file = Path.Combine(dir, "cpp_cases.cpp");
        File.WriteAllText(file, cpp.ToString(), new UTF8Encoding(false));

        string bat = Path.Combine(dir, "cl.bat");
        File.WriteAllText(bat, "@echo off\r\ncall \"C:\\Program Files\\Microsoft Visual Studio\\18\\Community\\VC\\Auxiliary\\Build\\vcvars64.bat\" >nul 2>&1\r\ncd /d \"" + dir + "\"\r\ncl /nologo /utf-8 /std:c++20 /c /EHsc /wd4324 /wd4200 cpp_cases.cpp\r\n");
        var psi = new ProcessStartInfo("cmd.exe", "/c \"" + bat + "\"") { RedirectStandardOutput = true, RedirectStandardError = true, UseShellExecute = false, StandardOutputEncoding = Encoding.Latin1 };
        string output;
        using (var p = Process.Start(psi)) { output = p.StandardOutput.ReadToEnd() + p.StandardError.ReadToEnd(); p.WaitForExit(); }

        var bad = new HashSet<string>();
        var other = new List<string>();
        foreach (string line in output.Split('\n'))
        {
            var m = Regex.Match(line, @"cpp_cases\.cpp\((\d+)\): error (C\d+)");
            if (!m.Success) continue;
            int ln = int.Parse(m.Groups[1].Value);
            if (m.Groups[2].Value == "C2607" || m.Groups[2].Value == "C2338")
            {
                string info;
                if (lineInfo.TryGetValue(ln, out info)) bad.Add(info);
            }
            else other.Add(line.Trim());
        }
        foreach (var b in bad) Console.WriteLine("FAIL " + b);
        foreach (var o in other.Take(10)) Console.WriteLine("COMPILE " + o);
        Console.WriteLine("assert " + asserted + " 個 / 不一致 " + bad.Count + " / 除外 " + skipped + " / コンパイル エラー " + other.Count);
        if (bad.Count > 0 || other.Count > 0) Console.WriteLine("(生成したファイル: " + file + ")");
        return bad.Count == 0 && other.Count == 0 ? 0 : 1;
    }

    private static void Assert(StringBuilder cpp, Dictionary<int, string> lineInfo, string info, string expr, int value)
    {
        cpp.AppendLine("static_assert(" + expr + " == " + value + ");");
        // いまの行番号(1 始まり)を記録する
        int lineNo = cpp.ToString().Count(ch => ch == '\n');
        lineInfo[lineNo] = info + " (自分: " + value + ")";
    }

    private static IEnumerable<Tuple<string, string>> Fixed()
    {
        yield return Tuple.Create("basic", "struct S { char a; int b; double c; short d; bool e; };");
        yield return Tuple.Create("dxmath", "struct S { XMFLOAT3 a; float b; XMFLOAT4 c; XMFLOAT2 d; XMFLOAT4X4 e; XMFLOAT3 f; };");
        yield return Tuple.Create("xmvector", "struct S { float a; XMVECTOR b; XMFLOAT3 c; XMMATRIX d; };");
        yield return Tuple.Create("aligned types", "struct S { float a; XMFLOAT4A b; XMFLOAT3 c; XMFLOAT4X4A d; };");
        yield return Tuple.Create("nested", "struct In { float a; double b; }; struct S { char c; In i; short d; In j[2]; };");
        yield return Tuple.Create("array", "struct S { char a; float b[3]; short c[5]; double d[2]; char e; };");
        yield return Tuple.Create("alignas member", "struct S { char a; alignas(16) float b; char c; alignas(8) char d[3]; };");
        yield return Tuple.Create("alignas struct", "struct alignas(32) S { char a; int b; };\nstruct T { char a; S s; };");
        yield return Tuple.Create("declspec align", "struct __declspec(align(16)) S { char a; int b; };\nstruct T { char a; S s; char c; };");
        yield return Tuple.Create("pack 1", "#pragma pack(push, 1)\nstruct S { char a; int b; short c; double d; };\n#pragma pack(pop)\nstruct T { char a; int b; };");
        yield return Tuple.Create("pack 2", "#pragma pack(push, 2)\nstruct S { char a; int b; double c; };\n#pragma pack(pop)");
        yield return Tuple.Create("inherit", "struct A { int a; char b; };\nstruct B : A { char c; double d; };");
        yield return Tuple.Create("inherit empty", "struct A { };\nstruct B : A { int c; };");
        yield return Tuple.Create("constants", "#define N 3\nconstexpr int M = 4;\nstruct S { float a[N]; char b; int c[M * 2]; };");
        yield return Tuple.Create("std array", "struct S { char a; std::array<float, 4> b; std::array<char, 3> c; int d; };");
        yield return Tuple.Create("initializers", "struct S { float a = 1.0f; int b{3}; char c = 'x'; double d = 0.5; };");
        yield return Tuple.Create("multi declarators", "struct S { float a, b, c; char d, e; double f; };");
        yield return Tuple.Create("pointers", "struct S { char a; int* b; float* c[2]; char d; };");
        yield return Tuple.Create("alias", "using Vec3 = XMFLOAT3;\ntypedef float Real;\nstruct S { char a; Vec3 b; Real c; };");
        yield return Tuple.Create("nested definition", "struct S { char a; struct In { double d; char e; } in; short f; };");
        yield return Tuple.Create("members and statics", "struct S { static const int K = 3; char a; void f() {} int b; static int c; };");
        yield return Tuple.Create("access", "class S { public: char a; int b; public: char c; };");
        yield return Tuple.Create("const members", "struct S { const int a = 1; char b; mutable int c; };");
        yield return Tuple.Create("int types", "struct S { int8_t a; uint16_t b; int32_t c; uint64_t d; size_t e; uint8_t f; };");
        yield return Tuple.Create("padded cbuffer", "struct S { XMFLOAT4X4 world; XMFLOAT3 tint; float alpha; XMFLOAT2 uv; float pad0[2]; XMFLOAT3 dir; float inten; };");
    }

    private static readonly string[] Types =
    {
        "char", "bool", "short", "int", "float", "double", "int64_t", "uint8_t", "uint16_t", "uint32_t", "size_t", "int*",
        "XMFLOAT2", "XMFLOAT3", "XMFLOAT4", "XMINT3", "XMUINT4", "XMFLOAT4X4", "XMFLOAT3X3", "XMFLOAT4A", "XMVECTOR", "XMMATRIX"
    };

    private static Tuple<string, string> Generate(Random rnd, int n)
    {
        var sb = new StringBuilder();
        sb.AppendLine("struct SA { char a; int b; };");
        sb.AppendLine("struct SB { double a; char b; };");
        sb.AppendLine("struct SC { XMFLOAT3 a; float b; XMFLOAT4 c; };");
        bool pack = rnd.Next(8) == 0;
        if (pack) sb.AppendLine("#pragma pack(push, " + (1 << rnd.Next(4)) + ")");
        sb.AppendLine("struct S {");
        int count = 2 + rnd.Next(9);
        for (int i = 0; i < count; i++)
        {
            string t;
            int pick = rnd.Next(10);
            if (pick == 0) t = "SA"; else if (pick == 1) t = "SB"; else if (pick == 2) t = "SC";
            else t = Types[rnd.Next(Types.Length)];
            string al = rnd.Next(12) == 0 ? "alignas(" + (4 << rnd.Next(4)) + ") " : "";
            if (al.Length > 0 && (t.StartsWith("XMVECTOR") || t.StartsWith("XMMATRIX") || t.EndsWith("A"))) al = "";
            string arr = rnd.Next(5) == 0 ? "[" + (1 + rnd.Next(3)) + "]" : "";
            sb.AppendLine("  " + al + t + " m" + i + arr + ";");
        }
        sb.AppendLine("};");
        if (pack) sb.AppendLine("#pragma pack(pop)");
        return Tuple.Create("random #" + n, sb.ToString());
    }
}
