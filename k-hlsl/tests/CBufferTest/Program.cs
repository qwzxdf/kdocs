using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;
using KHlsl.Server;

// cbuffer のパッキングの計算を、本物の DXC(-Od -Fc の逆アセンブリ)と突き合わせる。
// 使い方: dotnet run -- [dxc.exe のパス] [ランダム ケースの数]
internal static class Program
{
    private static string dxc;
    private static int failed, passed;

    private static int Main(string[] args)
    {
        dxc = args.Length > 0 ? args[0] : FindDxc();
        int random = args.Length > 1 ? int.Parse(args[1]) : 150;
        if (dxc == null || !File.Exists(dxc)) { Console.WriteLine("dxc.exe が見つかりません"); return 2; }

        foreach (var c in Fixed()) Run(c.Item1, c.Item2, c.Item3);
        var rnd = new Random(20260101);
        for (int i = 0; i < random; i++) { var c = Generate(rnd, i); Run(c.Item1, c.Item2, c.Item3); }
        Console.WriteLine("一致 " + passed + " / 不一致 " + failed);
        return failed == 0 ? 0 : 1;
    }

    private static string FindDxc()
    {
        string kits = @"C:\Program Files (x86)\Windows Kits\10\bin";
        if (!Directory.Exists(kits)) return null;
        return Directory.GetDirectories(kits).OrderByDescending(d => d).Select(d => Path.Combine(d, "x64", "dxc.exe")).FirstOrDefault(File.Exists);
    }

    // ---- 手書きのケース ----
    private static IEnumerable<Tuple<string, string, bool>> Fixed()
    {
        yield return Tuple.Create("basic", @"
struct Light { float3 pos; float range; float3 color; };
cbuffer C { float4x4 viewProj; float3 eye; float time; float2 a; float3 b; float c[3]; Light lights[2]; bool flag; float3x3 m33; float d; row_major float2x3 rm; int2 i2; };
", false);
        yield return Tuple.Create("struct then scalar", @"
struct S { float a; float2 b; };
cbuffer C { float x; S s; float y; float3 z; };
", false);
        yield return Tuple.Create("struct pack after", @"
struct S { float3 a; float b; float c; };
cbuffer C { S s; float t; float u; float4 v; };
", false);
        yield return Tuple.Create("doubles", @"
cbuffer C { float a; double b; double2 c; double3 d; float e; double4 f; double g; };
", false);
        yield return Tuple.Create("half 32", @"
cbuffer C { half a; half3 b; float e; half f; };
", false);
        yield return Tuple.Create("min16 (no 16bit)", @"
cbuffer C { float a; min16float b; float c; min16float d; min16float e; float f; min16int2 g; float h; min16float3 i; };
", false);
        yield return Tuple.Create("half 16", @"
cbuffer C { half a; half3 b; min16float c; min16int2 d; float e; half4 f; half2x2 g; float16_t h; };
", true);
        yield return Tuple.Create("packoffset", @"
cbuffer C { float4 a : packoffset(c0); float b : packoffset(c1.y); float2 c : packoffset(c2); float d : packoffset(c1.x); };
", false);
        yield return Tuple.Create("matrices", @"
cbuffer C { float a; float4x4 b; float c; float2x2 d; float e; float4x3 f; float3x4 g; float h; row_major float3x3 i; column_major float2x4 j; };
", false);
        yield return Tuple.Create("pack_matrix", @"
#pragma pack_matrix(row_major)
cbuffer C { float a; float3x3 b; float c; float2x4 d; column_major float3x2 e; float f; };
", false);
        yield return Tuple.Create("arrays", @"
cbuffer C { float a[2]; float b; float2 c[3]; float d; int e[1]; float4x4 f[2]; float3 g[2]; float h; };
", false);
        yield return Tuple.Create("multi decl", @"
cbuffer C { float a, b, c; float3 d, e; float2 f; };
", false);
        yield return Tuple.Create("typedef", @"
typedef float3 Vec3;
typedef float4x4 Mat;
cbuffer C { float a; Vec3 b; float c; Mat d; };
", false);
        yield return Tuple.Create("inherit", @"
struct A { float a; float3 b; };
struct B : A { float c; float d; };
cbuffer C { float x; B b; float y; };
", false);
        yield return Tuple.Create("ConstantBuffer<T>", @"
struct Data { float4x4 m; float3 p; float s; uint flags; };
ConstantBuffer<Data> gData : register(b3);
", false);
        yield return Tuple.Create("nested arrays of struct", @"
struct In { float a; float2 b; };
struct Out { In i[2]; float c; };
cbuffer C { float x; Out o[2]; float y; };
", false);
        yield return Tuple.Create("array size constants", @"
#define N 3
#define M (N + 1)
static const int K = 2;
cbuffer C { float a[N]; float b; float2 c[M]; float d[K * 2]; float e[2][3]; };
", false);
        yield return Tuple.Create("vector<> matrix<>", @"
cbuffer C { vector<float,3> a; float b; matrix<float,3,3> c; vector<int,2> d; float e; matrix<float,2,4> f; };
", false);
    }

    // ---- ランダムなケース ----
    private static readonly string[] Types =
    {
        "float", "int", "uint", "bool", "float2", "float3", "float4", "int3", "uint2", "float4x4", "float3x3", "float2x3", "float3x2", "float4x3",
        "double", "double2", "double3", "half", "half3", "half2x3", "min16float", "min16int2", "row_major float3x4", "column_major float2x2", "row_major float4x4"
    };

    private static Tuple<string, string, bool> Generate(Random rnd, int n)
    {
        bool h16 = rnd.Next(4) == 0;
        var sb = new StringBuilder();
        sb.AppendLine("struct SA { float a; float3 b; };");
        sb.AppendLine("struct SB { float2 a; float b; float4 c; };");
        sb.AppendLine("struct SC { float a; float b; };");
        sb.AppendLine("cbuffer C {");
        int count = 3 + rnd.Next(9);
        for (int i = 0; i < count; i++)
        {
            string t;
            int pick = rnd.Next(10);
            if (pick == 0) t = "SA"; else if (pick == 1) t = "SB"; else if (pick == 2) t = "SC";
            else t = Types[rnd.Next(Types.Length)];
            // 16 ビット型を使わないときの min16 は専用のレジスタに入り、配列との組み合わせで DXC と合わない場合がある(未対応)
            if (h16 == false && (t.StartsWith("half") || t.StartsWith("min16"))) t = "float2";
            string arr = rnd.Next(5) == 0 ? "[" + (1 + rnd.Next(3)) + "]" : "";
            sb.AppendLine("  " + t + " m" + i + arr + ";");
        }
        sb.AppendLine("};");
        return Tuple.Create("random #" + n, sb.ToString(), h16);
    }

    // ---- 実行と比較 ----
    private static void Run(string name, string src, bool h16)
    {
        var sources = new[] { CBufferLayout.MakeSource("t.hlsl", src) };
        var table = CBufferLayout.Collect(sources);
        bool pragmaRow = Regex.IsMatch(src, @"#pragma\s+pack_matrix\s*\(\s*row_major");
        var opt = new LayoutOptions { Enable16Bit = h16, RowMajorDefault = pragmaRow };
        var blocks = CBufferLayout.LayoutAll(table, opt, false);

        // DXC は、使われている cbuffer しか出さない。全メンバーを触るシェーダーを足す
        var use = new StringBuilder();
        use.AppendLine("float4 main() : SV_Target { float r = 0;");
        foreach (var b in blocks)
            foreach (var m in b.Members)
                use.AppendLine("  r += (float)" + Access(m, b.Kind == "ConstantBuffer" ? b.Name + "." : "") + ";");
        use.AppendLine("  return r; }");

        string dir = Path.Combine(Path.GetTempPath(), "khlsl-cbtest");
        Directory.CreateDirectory(dir);
        string hlsl = Path.Combine(dir, "t.hlsl"), outp = Path.Combine(dir, "t.txt");
        File.WriteAllText(hlsl, src + use);
        if (File.Exists(outp)) File.Delete(outp);
        var psi = new ProcessStartInfo(dxc, "-T ps_6_2 -E main -Od -Fc \"" + outp + "\"" + (h16 ? " -enable-16bit-types" : "") + " \"" + hlsl + "\"")
        { RedirectStandardOutput = true, RedirectStandardError = true, UseShellExecute = false };
        string err;
        using (var p = Process.Start(psi)) { err = p.StandardError.ReadToEnd() + p.StandardOutput.ReadToEnd(); p.WaitForExit(); }
        if (!File.Exists(outp)) { Console.WriteLine("SKIP " + name + ": DXC がコンパイルできません\n" + Brief(err)); return; }

        var dumped = ParseDump(File.ReadAllText(outp));
        bool ok = true;
        var report = new StringBuilder();
        foreach (var b in blocks)
        {
            Tuple<List<Tuple<string, int>>, int> d;
            string key = b.Kind == "ConstantBuffer" ? b.Name : b.Name;
            if (!dumped.TryGetValue(key, out d)) { report.AppendLine("  DXC の出力に " + b.Name + " がありません"); ok = false; continue; }
            if (b.Incomplete) { report.AppendLine("  " + b.Name + ": 計算できませんでした: " + string.Join("; ", b.Problems)); ok = false; continue; }
            foreach (var mem in b.Members)
            {
                var hit = d.Item1.FirstOrDefault(x => x.Item1 == mem.Name);
                if (hit == null) { report.AppendLine("  " + b.Name + "." + mem.Name + ": DXC に無い"); ok = false; }
                else if (hit.Item2 != mem.Offset) { report.AppendLine("  " + b.Name + "." + mem.Name + " (" + mem.Type + (mem.ArrayCount > 0 ? "[" + mem.ArrayCount + "]" : "") + "): 自分 " + mem.Offset + " / DXC " + hit.Item2); ok = false; }
            }
            if (d.Item2 != b.Size && d.Item2 != b.PaddedSize) { report.AppendLine("  " + b.Name + " の大きさ: 自分 " + b.Size + " (" + b.PaddedSize + ") / DXC " + d.Item2); ok = false; }
        }
        if (ok) { passed++; Console.WriteLine("OK   " + name); }
        else { failed++; Console.WriteLine("FAIL " + name); Console.Write(report); Console.WriteLine(src); }
    }

    private static string Brief(string s) { return string.Join("\n", s.Split('\n').Take(6)); }

    // 全メンバーを触る式(最初の葉だけ)
    private static string Access(LMember m, string prefix)
    {
        string e = prefix + m.Name;
        if (m.ArrayCount > 0) e += "[0]";
        return Leaf(m, e);
    }

    private static string Leaf(LMember m, string e)
    {
        if (m.IsStruct)
        {
            var f = m.Fields[0];
            string fe = e + "." + f.Name;
            if (f.ArrayCount > 0) fe += "[0]";
            return Leaf(f, fe);
        }
        if (m.IsMatrix) return e + "[0][0]";
        if (m.Comps > 1) return e + ".x";
        return e;
    }

    // DXC の逆アセンブリから、cbuffer ごとの最上位メンバーのオフセットと全体の大きさを取る
    private static Dictionary<string, Tuple<List<Tuple<string, int>>, int>> ParseDump(string text)
    {
        var map = new Dictionary<string, Tuple<List<Tuple<string, int>>, int>>();
        string cur = null;
        List<Tuple<string, int>> members = null;
        var nested = new List<Tuple<string, int>>();
        foreach (var raw in text.Replace("\r", "").Split('\n'))
        {
            var cm = Regex.Match(raw, @"^; cbuffer (\w+)$");
            if (cm.Success) { cur = cm.Groups[1].Value; members = new List<Tuple<string, int>>(); nested = new List<Tuple<string, int>>(); continue; }
            if (cur == null) continue;
            var total = Regex.Match(raw, @"^;   \} (\w+);\s+; Offset:\s+\d+ Size:\s+(\d+)$");
            if (total.Success)
            {
                // ConstantBuffer<T> は、T の構造体が 1 段深く入っている
                var useList = members.Any(x => x.Item1 == cur) ? nested : members;
                map[cur] = Tuple.Create(useList, int.Parse(total.Groups[2].Value));
                cur = null;
                continue;
            }
            var mm = Regex.Match(raw, @"^; {7}(\S.*?)\s*; Offset:\s+(\d+)$");
            var mm2 = Regex.Match(raw, @"^; {11}(\S.*?)\s*; Offset:\s+(\d+)$");
            if (!mm.Success && !mm2.Success) continue;
            var hit = mm.Success ? mm : mm2;
            string decl = hit.Groups[1].Value.TrimEnd(';', ' ');
            decl = Regex.Replace(decl, @"(\[\d+\])+$", "");
            var nm = Regex.Match(decl, @"(\w+)$");
            if (nm.Success) (mm.Success ? members : nested).Add(Tuple.Create(nm.Groups[1].Value, int.Parse(hit.Groups[2].Value)));
        }
        return map;
    }
}
