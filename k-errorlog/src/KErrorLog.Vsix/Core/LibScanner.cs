using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Text;
using System.Threading;

namespace KErrorLog
{
    /// <summary>.lib に入っているシンボルの名前を調べる。</summary>
    public sealed class LibHit
    {
        public string Path = "";
        public ushort Machine;
        public bool IsImportLib;
        /// <summary>未解決のシンボルと同じ名前が、そのまま入っている。false なら、__imp_ の有無だけが違う名前。</summary>
        public bool Exact;

        public string FileName { get { return System.IO.Path.GetFileName(Path); } }

        public string MachineName { get { return LibScanner.MachineName(Machine); } }
    }

    /// <summary>
    /// ソリューションのフォルダーの下の .lib を読んで、未解決のシンボルが、どの .lib に入っているかを探す。
    /// .lib(COFF アーカイブ)の先頭にある「リンカー メンバー」(シンボル名の索引)だけを読むので、大きな .lib でも速い。
    /// </summary>
    public static class LibScanner
    {
        private static readonly HashSet<string> SkipDirs = new HashSet<string>(StringComparer.OrdinalIgnoreCase)
        {
            ".git", ".vs", "node_modules", "ipch", ".svn"
        };

        public static string MachineName(ushort m)
        {
            switch (m)
            {
                case 0x8664: return "x64";
                case 0x14C: return "x86";
                case 0xAA64: return "ARM64";
                case 0x1C4: return "ARM";
            }
            return m == 0 ? "?" : "0x" + m.ToString("X");
        }

        public static ushort MachineOf(string platform)
        {
            switch ((platform ?? "").ToLowerInvariant())
            {
                case "x64": return 0x8664;
                case "win32":
                case "x86": return 0x14C;
                case "arm64": return 0xAA64;
                case "arm": return 0x1C4;
            }
            return 0;
        }

        public static void Scan(List<UnresolvedSym> syms, string root, CancellationToken ct, int maxMilliseconds)
        {
            if (string.IsNullOrEmpty(root) || !Directory.Exists(root) || syms.Count == 0) return;

            // 探す名前 → (シンボル, 同じ名前か)
            var wanted = new Dictionary<string, List<KeyValuePair<UnresolvedSym, bool>>>(StringComparer.Ordinal);
            foreach (UnresolvedSym s in syms)
            {
                if (s.Mangled.Length == 0) continue;
                Want(wanted, s.Mangled, s, true);
                string variant = s.Mangled.StartsWith("__imp_", StringComparison.Ordinal) ? s.Mangled.Substring(6) : "__imp_" + s.Mangled;
                Want(wanted, variant, s, false);
            }

            var sw = Stopwatch.StartNew();
            int count = 0;
            foreach (string lib in EnumerateLibs(root, ct))
            {
                if (ct.IsCancellationRequested || sw.ElapsedMilliseconds > maxMilliseconds || ++count > 800) break;
                try { ScanOne(lib, wanted); }
                catch (Exception) { /* 壊れた・読めない .lib は飛ばす */ }
            }
        }

        private static void Want(Dictionary<string, List<KeyValuePair<UnresolvedSym, bool>>> d, string name, UnresolvedSym s, bool exact)
        {
            List<KeyValuePair<UnresolvedSym, bool>> list;
            if (!d.TryGetValue(name, out list)) d[name] = list = new List<KeyValuePair<UnresolvedSym, bool>>();
            list.Add(new KeyValuePair<UnresolvedSym, bool>(s, exact));
        }

        private static IEnumerable<string> EnumerateLibs(string root, CancellationToken ct)
        {
            var stack = new Stack<string>();
            stack.Push(root);
            while (stack.Count > 0 && !ct.IsCancellationRequested)
            {
                string dir = stack.Pop();
                string[] files = null;
                try { files = Directory.GetFiles(dir, "*.lib"); } catch (Exception) { }
                if (files != null) foreach (string f in files) yield return f;
                string[] subs = null;
                try { subs = Directory.GetDirectories(dir); } catch (Exception) { }
                if (subs == null) continue;
                foreach (string sub in subs)
                {
                    if (SkipDirs.Contains(Path.GetFileName(sub))) continue;
                    stack.Push(sub);
                }
            }
        }

        private static uint Be32(byte[] b, int o) { return (uint)(b[o] << 24 | b[o + 1] << 16 | b[o + 2] << 8 | b[o + 3]); }
        private static uint Le32(byte[] b, int o) { return (uint)(b[o] | b[o + 1] << 8 | b[o + 2] << 16 | b[o + 3] << 24); }

        private static void ScanOne(string path, Dictionary<string, List<KeyValuePair<UnresolvedSym, bool>>> wanted)
        {
            using (var fs = new FileStream(path, FileMode.Open, FileAccess.Read, FileShare.ReadWrite | FileShare.Delete))
            {
                var sig = new byte[8];
                if (fs.Read(sig, 0, 8) != 8 || Encoding.ASCII.GetString(sig) != "!<arch>\n") return;

                // 1 番目のリンカー メンバー(ビッグ エンディアン)
                byte[] first = ReadMember(fs, out long afterFirst);
                if (first == null || first.Length < 4) return;

                var found = new List<KeyValuePair<string, List<KeyValuePair<UnresolvedSym, bool>>>>();
                bool importLib = false;
                uint firstOffset = 0;

                uint count = Be32(first, 0);
                if (count > 0 && 4 + 4L * count < first.Length)
                {
                    firstOffset = Be32(first, 4);
                    int p = 4 + 4 * (int)count;
                    for (uint i = 0; i < count && p < first.Length; i++)
                    {
                        int e = p;
                        while (e < first.Length && first[e] != 0) e++;
                        string name = Encoding.ASCII.GetString(first, p, e - p);
                        p = e + 1;
                        Check(name, wanted, found, ref importLib);
                    }
                }
                else
                {
                    // 2 番目のリンカー メンバー(リトル エンディアン)しかない .lib
                    fs.Position = afterFirst;
                    byte[] second = ReadMember(fs, out long _);
                    if (second == null || second.Length < 8) return;
                    uint members = Le32(second, 0);
                    int symPos = 4 + 4 * (int)members;
                    if (symPos + 4 > second.Length) return;
                    if (members > 0) firstOffset = Le32(second, 4);
                    uint syms = Le32(second, symPos);
                    int p = symPos + 4 + 2 * (int)syms;
                    for (uint i = 0; i < syms && p < second.Length; i++)
                    {
                        int e = p;
                        while (e < second.Length && second[e] != 0) e++;
                        string name = Encoding.ASCII.GetString(second, p, e - p);
                        p = e + 1;
                        Check(name, wanted, found, ref importLib);
                    }
                }

                if (found.Count == 0) return;

                ushort machine = 0;
                if (firstOffset > 0 && firstOffset + 60 + 8 < fs.Length)
                {
                    fs.Position = firstOffset + 60;
                    var head = new byte[8];
                    if (fs.Read(head, 0, 8) == 8)
                    {
                        bool import = head[0] == 0 && head[1] == 0 && head[2] == 0xFF && head[3] == 0xFF;
                        machine = import ? (ushort)(head[6] | head[7] << 8) : (ushort)(head[0] | head[1] << 8);
                    }
                }

                foreach (var kv in found)
                    foreach (var target in kv.Value)
                    {
                        var hit = new LibHit { Path = path, Machine = machine, IsImportLib = importLib, Exact = target.Value };
                        if (target.Key.Libs == null) target.Key.Libs = new List<LibHit>();
                        target.Key.Libs.Add(hit);
                    }
            }
        }

        private static void Check(string name, Dictionary<string, List<KeyValuePair<UnresolvedSym, bool>>> wanted,
            List<KeyValuePair<string, List<KeyValuePair<UnresolvedSym, bool>>>> found, ref bool importLib)
        {
            if (name.StartsWith("__IMPORT_DESCRIPTOR_", StringComparison.Ordinal)) importLib = true;
            List<KeyValuePair<UnresolvedSym, bool>> targets;
            if (wanted.TryGetValue(name, out targets))
                found.Add(new KeyValuePair<string, List<KeyValuePair<UnresolvedSym, bool>>>(name, targets));
        }

        /// <summary>アーカイブのメンバー(ヘッダー 60 バイトと本体)を 1 つ読む。</summary>
        private static byte[] ReadMember(FileStream fs, out long after)
        {
            after = fs.Position;
            var header = new byte[60];
            if (fs.Read(header, 0, 60) != 60) return null;
            string sizeText = Encoding.ASCII.GetString(header, 48, 10).Trim();
            int size;
            if (!int.TryParse(sizeText, out size) || size < 0 || size > 512 * 1024 * 1024) return null;
            var data = new byte[size];
            int got = 0;
            while (got < size)
            {
                int n = fs.Read(data, got, size - got);
                if (n <= 0) return null;
                got += n;
            }
            after = fs.Position + (size % 2);
            return data;
        }
    }
}
