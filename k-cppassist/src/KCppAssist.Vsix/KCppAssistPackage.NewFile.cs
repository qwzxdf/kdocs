using System;
using System.Collections.Generic;
using System.ComponentModel.Composition;
using System.IO;
using System.Linq;
using System.Text;
using EnvDTE;
using Microsoft.VisualStudio.Shell;
using Microsoft.VisualStudio.Text;
using Microsoft.VisualStudio.Text.Editor;
using Microsoft.VisualStudio.Utilities;
using Task = System.Threading.Tasks.Task;

namespace KCppAssist
{
    /// <summary>
    /// 新しい空のファイルにひな形を書く(NewFileGen の呼び出し側)と、クラス名の上の電球から
    /// 「cpp を作る」「コンストラクター・デストラクターを作る (.h に宣言、.cpp に定義)」を行う。
    /// </summary>
    internal static class NewFileService
    {
        public const string EditTag = "K-CppAssist.NewFile";

        internal sealed class Style
        {
            public string Namespace = "";
            public string Indent = "\t";
            public string Eol = "\r\n";
        }

        private static readonly object gate = new object();
        private static string cacheRoot;
        private static DateTime cacheTime;
        private static Style cacheStyle;

        /// <summary>root の下の既存のヘッダー(新しい順に最大 300 個)から、namespace・字下げ・改行を調べる。60 秒だけ覚える。</summary>
        public static Style Detect(string root, ISet<string> skip)
        {
            lock (gate)
                if (cacheStyle != null && cacheRoot == root && (DateTime.UtcNow - cacheTime).TotalSeconds < 60) return cacheStyle;
            var files = new List<KeyValuePair<DateTime, string>>();
            try
            {
                var stack = new Stack<string>();
                if (!string.IsNullOrEmpty(root) && Directory.Exists(root)) stack.Push(root);
                int dirs = 0;
                while (stack.Count > 0 && dirs++ < 3000 && files.Count < 5000)
                {
                    string dir = stack.Pop();
                    try
                    {
                        foreach (string f in Directory.GetFiles(dir))
                            if (IncludeService.IsHeader(f)) files.Add(new KeyValuePair<DateTime, string>(File.GetLastWriteTimeUtc(f), f));
                        foreach (string d in Directory.GetDirectories(dir))
                        {
                            string leaf = Path.GetFileName(d);
                            if (skip.Contains(leaf) || leaf.StartsWith("cmake-build", StringComparison.OrdinalIgnoreCase) || leaf.StartsWith(".")) continue;
                            stack.Push(d);
                        }
                    }
                    catch (Exception) { }
                }
            }
            catch (Exception ex) { KCppAssistPackage.Log("new file: scan failed: " + ex.Message); }

            var texts = new List<string>();
            foreach (var kv in files.OrderByDescending(x => x.Key).Take(300))
            {
                try
                {
                    var fi = new FileInfo(kv.Value);
                    if (fi.Length > 512 * 1024) continue;
                    texts.Add(File.ReadAllText(kv.Value));
                }
                catch (Exception) { }
            }
            var st = new Style { Namespace = NewFileGen.DetectNamespace(texts) };
            string ind = NewFileGen.DetectIndent(texts);
            if (ind != null) st.Indent = ind;
            int crlf = texts.Sum(t => t.Split(new[] { "\r\n" }, StringSplitOptions.None).Length - 1);
            int lf = texts.Sum(t => t.Split('\n').Length - 1) - crlf;
            st.Eol = texts.Count > 0 && lf > crlf ? "\n" : "\r\n";
            lock (gate) { cacheRoot = root; cacheTime = DateTime.UtcNow; cacheStyle = st; }
            return st;
        }

        public static NewFileGen.Naming NamingOf(OptionsPage opt)
        {
            switch (opt.NewFileClassNaming)
            {
                case ClassNaming.PascalCase: return NewFileGen.Naming.Pascal;
                case ClassNaming.SnakeCase: return NewFileGen.Naming.Snake;
                case ClassNaming.CamelCase: return NewFileGen.Naming.Camel;
                default: return NewFileGen.Naming.SameAsFile;
            }
        }

        /// <summary>設定と、調べた既存の様子から、書き出しの設定を作る。</summary>
        public static NewFileGen.Options Build(OptionsPage opt, Style st)
        {
            var o = new NewFileGen.Options
            {
                MakeClass = opt.NewFileClass,
                IndentInNamespace = opt.NewFileIndentInNamespace,
                NamespaceComment = opt.NewFileNamespaceComment,
                Guard = opt.NewFileGuard == GuardKind.IncludeGuard ? NewFileGen.Guard.IncludeGuard : NewFileGen.Guard.PragmaOnce,
                Eol = st.Eol,
            };
            o.Naming = NamingOf(opt);
            switch (opt.NewFileNamespaceMode)
            {
                case NewFileNamespaceMode.Fixed: o.Namespace = (opt.NewFileNamespace ?? "").Trim(); break;
                case NewFileNamespaceMode.None: o.Namespace = ""; break;
                default: o.Namespace = st.Namespace; break;
            }
            switch (opt.NewFileIndent)
            {
                case IndentKind.Tab: o.Indent = "\t"; break;
                case IndentKind.Spaces2: o.Indent = "  "; break;
                case IndentKind.Spaces4: o.Indent = "    "; break;
                default: o.Indent = st.Indent; break;
            }
            return o;
        }

        /// <summary>
        /// VS の「クラスの追加」が作ったばかりのファイルを、ひな形の形(namespace・字下げ・{ の位置)に書き直した中身。
        /// そのファイルでなければ null。クラス名・基底クラス・#include・コンストラクターとデストラクターは引き継ぐ。
        /// </summary>
        public static string WizardContent(string path, string text, OptionsPage opt, Style st, out int caret)
        {
            caret = -1;
            var o = Build(opt, st);
            string stem = Path.GetFileNameWithoutExtension(path);
            if (IncludeService.IsHeader(path))
            {
                string head; List<string> members, includes;
                if (!NewFileGen.ParseWizardHeader(text, out head, out members, out includes)) return null;
                o.ClassHead = head; o.Members = members; o.Includes = includes; o.MakeClass = true;
                int c;
                string res = NewFileGen.Header(stem, o, out c);
                caret = c;
                return res;
            }
            List<string> incs, bodies;
            if (!NewFileGen.ParseWizardSource(text, out incs, out bodies)) return null;
            // /FI で pch を読み込むプロジェクトなら、VS が書いた #include "pch.h" は要らない
            if (opt.SkipForcedPch)
            {
                var forced = ForcedIncludes(path);
                incs = incs.Where(l =>
                {
                    var im = System.Text.RegularExpressions.Regex.Match(l, @"#\s*include\s*[""<]([^"">]+)["">]");
                    if (!im.Success || !IncludeTidy.IsPch(im.Groups[1].Value)) return true;
                    return !forced.Contains(Path.GetFileName(im.Groups[1].Value));
                }).ToList();
            }
            o.Includes = incs; o.Bodies = bodies;
            string src = NewFileGen.Source(null, o);
            int k = src.IndexOf("namespace", StringComparison.Ordinal);
            caret = k >= 0 ? Math.Min(src.Length, src.IndexOf('\n', k) + 1) : src.Length;
            return src;
        }

        /// <summary>
        /// path を含むプロジェクト(上のフォルダーへさかのぼって最初に見つかった .vcxproj)の、強制インクルード ファイル(/FI)のファイル名。
        /// どの構成のものも集める(Debug だけ /FI、のような分け方は、ほとんどないため)。見つからなければ空。
        /// </summary>
        public static HashSet<string> ForcedIncludes(string path)
        {
            var set = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
            try
            {
                string dir = Path.GetDirectoryName(path);
                for (int i = 0; i < 6 && !string.IsNullOrEmpty(dir); i++, dir = Path.GetDirectoryName(dir))
                {
                    string proj = Directory.GetFiles(dir, "*.vcxproj").FirstOrDefault();
                    if (proj == null) continue;
                    string xml = File.ReadAllText(proj);
                    foreach (System.Text.RegularExpressions.Match m in System.Text.RegularExpressions.Regex.Matches(xml, @"<ForcedIncludeFiles>([^<]*)</ForcedIncludeFiles>"))
                        foreach (string f in m.Groups[1].Value.Split(';'))
                        {
                            string t = f.Trim();
                            if (t.Length == 0 || t.StartsWith("%(")) continue;
                            set.Add(Path.GetFileName(t));
                        }
                    break;
                }
            }
            catch (Exception ex) { KCppAssistPackage.Log("new file: read forced includes failed: " + ex.Message); }
            return set;
        }

        /// <summary>新しい空のファイルの中身と、カーソルの位置(なければ -1)。書く必要がなければ null。</summary>
        public static string Content(string path, OptionsPage opt, Style st, out int caret)
        {
            caret = -1;
            var o = Build(opt, st);
            string stem = Path.GetFileNameWithoutExtension(path);
            if (IncludeService.IsHeader(path))
            {
                int c;
                string text = NewFileGen.Header(stem, o, out c);
                caret = c;
                return text;
            }
            string ext = Path.GetExtension(path).ToLowerInvariant();
            if (ext != ".cpp" && ext != ".cc" && ext != ".cxx") return null;
            string dir = Path.GetDirectoryName(path);
            string header = new[] { ".h", ".hpp", ".hh", ".hxx" }.Select(e => stem + e).FirstOrDefault(h => File.Exists(Path.Combine(dir, h)));
            string src = NewFileGen.Source(header, o);
            // namespace の中の空行にカーソルを置く
            int k = src.IndexOf("namespace", StringComparison.Ordinal);
            if (k >= 0)
            {
                int nl = src.IndexOf('\n', k);
                caret = nl < 0 ? src.Length : nl + 1 + (src.Length > nl + 1 && src[nl + 1] == '\r' ? 0 : 0);
                caret = Math.Min(src.Length, nl + 1);
            }
            else caret = src.Length;
            return src;
        }
    }

    /// <summary>エディターが、空の C / C++ ファイルを開いたとき、ひな形を書く。</summary>
    [Export(typeof(IWpfTextViewCreationListener))]
    [ContentType("C/C++")]
    [TextViewRole(PredefinedTextViewRoles.Document)]
    internal sealed class NewFileListener : IWpfTextViewCreationListener
    {
        [Import] internal Microsoft.VisualStudio.Text.ITextDocumentFactoryService Documents { get; set; }

        public void TextViewCreated(IWpfTextView view)
        {
            try
            {
                var opt = IncludeService.Options;
                if (opt == null || !opt.NewFileTemplate) return;
                ITextDocument doc;
                if (Documents == null || !Documents.TryGetTextDocument(view.TextBuffer, out doc)) return;
                string path = doc.FilePath;
                if (string.IsNullOrEmpty(path) || !File.Exists(path)) return;
                if (view.Properties.ContainsProperty(typeof(NewFileListener))) return;
                view.Properties.AddProperty(typeof(NewFileListener), true);
                // 作ったばかり(2 分以内)のものだけ。昔からある空のファイルには触らない
                if (new FileInfo(path).Length > 2048) return;
                if ((DateTime.UtcNow - File.GetCreationTimeUtc(path)).TotalMinutes > 2) return;
                string now = view.TextBuffer.CurrentSnapshot.GetText();
                // 空(BOM だけ・#pragma once だけ)か、VS の「クラスの追加」が作ったままの形(class X { }; と、#include だけの cpp)
                bool blank = NewFileGen.IsBlank(now);
                if (!blank && !IsWizard(path, now)) return;
                var ignored = ThreadHelper.JoinableTaskFactory.RunAsync(() => FillAsync(view, path, blank ? null : now));
            }
            catch (Exception ex) { KCppAssistPackage.Log("new file listener failed: " + ex.Message); }
        }

        private static bool IsWizard(string path, string text)
        {
            string h; List<string> a, b, c;
            if (IncludeService.IsHeader(path)) return NewFileGen.ParseWizardHeader(text, out h, out a, out c);
            return NewFileGen.ParseWizardSource(text, out a, out b);
        }

        private static async Task FillAsync(IWpfTextView view, string path, string wizardText)
        {
            try
            {
                var opt = IncludeService.Options;
                string root = IncludeService.RootFor(path);
                var skip = IncludeService.SkipDirs(opt);
                NewFileService.Style st = null;
                // Auto でなければ、既存のヘッダーを調べなくてよい(調べるのは、namespace か字下げが Auto のときだけ)
                bool needScan = opt.NewFileNamespaceMode == NewFileNamespaceMode.Auto || opt.NewFileIndent == IndentKind.Auto || true;
                if (needScan) st = await Task.Run(() => NewFileService.Detect(root, skip));
                await ThreadHelper.JoinableTaskFactory.SwitchToMainThreadAsync();
                var buf = view.TextBuffer;
                string cur = buf.CurrentSnapshot.GetText();
                // 調べている間に、何か書かれた
                if (wizardText == null ? !NewFileGen.IsBlank(cur) : cur != wizardText) return;
                int caret;
                string text = wizardText == null
                    ? NewFileService.Content(path, opt, st ?? new NewFileService.Style(), out caret)
                    : NewFileService.WizardContent(path, wizardText, opt, st ?? new NewFileService.Style(), out caret);
                if (text == null) return;
                using (var edit = buf.CreateEdit(EditOptions.None, null, NewFileService.EditTag))
                {
                    edit.Replace(0, buf.CurrentSnapshot.Length, text);
                    edit.Apply();
                }
                if (caret >= 0 && caret <= buf.CurrentSnapshot.Length)
                    view.Caret.MoveTo(new SnapshotPoint(buf.CurrentSnapshot, caret));
                KCppAssistPackage.Log("new file: wrote template to " + Path.GetFileName(path) + (wizardText != null ? " (from the Add Class wizard)" : ""));
            }
            catch (Exception ex) { KCppAssistPackage.Log("new file fill failed: " + ex); }
        }
    }

    public sealed partial class KCppAssistPackage
    {
        /// <summary>クラスを囲んでいる namespace の名前(外側から順)を「A::B」にする。なければ空。</summary>
        private static string NamespaceOf(MemberScan.ClassInfo cls)
        {
            var names = new List<string>();
            for (var s = cls.Scope.Parent; s != null; s = s.Parent)
                if (!s.IsClass && !string.IsNullOrEmpty(s.Name)) names.Insert(0, s.Name);
            return string.Join("::", names);
        }

        /// <summary>ヘッダーと同じ名前の cpp を作る(すでにあれば、そのパス)。プロジェクトにも足す。</summary>
        private async System.Threading.Tasks.Task<string> EnsureCppAsync(Active a, MemberScan.ClassInfo cls)
        {
            string dir = Path.GetDirectoryName(a.Path), stem = Path.GetFileNameWithoutExtension(a.Path);
            string existing = new[] { ".cpp", ".cc", ".cxx" }.Select(e => Path.Combine(dir, stem + e)).FirstOrDefault(File.Exists);
            if (existing != null) return existing;
            string root = IncludeService.RootFor(a.Path);
            var opt = SyncService.Options;
            var others = await Task.Run(() => SyncService.Candidates(a.Path, cls.Name, root, true, opt).Where(f => !IncludeService.IsHeader(f)).ToList());
            if (others.Count > 0) return others[0];
            await JoinableTaskFactory.SwitchToMainThreadAsync();

            var st = await Task.Run(() => NewFileService.Detect(root, IncludeService.SkipDirs(opt)));
            await JoinableTaskFactory.SwitchToMainThreadAsync();
            var o = NewFileService.Build(opt, st);
            o.Namespace = NamespaceOf(cls);                         // cpp は、クラスを囲んでいる namespace に合わせる
            string cppPath = Path.Combine(dir, stem + ".cpp");
            string src = NewFileGen.Source(Path.GetFileName(a.Path), o);
            File.WriteAllText(cppPath, src, new UTF8Encoding(true));
            try
            {
                var proj = a.Dte.ActiveDocument.ProjectItem?.ContainingProject;
                if (proj != null) proj.ProjectItems.AddFromFile(cppPath);
            }
            catch (Exception ex) { Log("make cpp: add to project failed: " + ex.Message); }
            return cppPath;
        }

        private async Task MakeCppAsync(Active a)
        {
            var cls = MemberScan.At(a.Text, a.Caret);
            if (cls == null) { await ReportAsync("クラスの上で押してください", true); return; }
            string before = Path.Combine(Path.GetDirectoryName(a.Path), Path.GetFileNameWithoutExtension(a.Path) + ".cpp");
            bool existed = File.Exists(before);
            string cpp = await EnsureCppAsync(a, cls);
            await JoinableTaskFactory.SwitchToMainThreadAsync();
            if (existed || !string.Equals(cpp, before, StringComparison.OrdinalIgnoreCase))
            { await ReportAsync(Path.GetFileName(cpp) + " はすでにあります", true); return; }
            try { a.Dte.ItemOperations.OpenFile(cpp); } catch (Exception ex) { Log("make cpp: open failed: " + ex.Message); }
            await ReportAsync(Path.GetFileName(cpp) + " を作り、プロジェクトに足しました", false);
        }

        /// <summary>コンストラクター・デストラクターを .h に宣言して、.cpp に定義を作る。cpp がなければ作る。</summary>
        private async Task CtorDtorCppAsync(Active a)
        {
            string why;
            var ch = Refactor.Make("ctordtor", a.Text, a.Caret, a.Eol, true, out why);
            if (ch == null) { await ReportAsync(why, true); return; }
            var cls = MemberScan.At(a.Text, a.Caret);
            SyncService.ApplyEdits(a.View.TextBuffer, ch.Edits, a.Undo, "K-Cpp: コンストラクター・デストラクターを作る");
            string cpp = await EnsureCppAsync(a, cls);
            await JoinableTaskFactory.SwitchToMainThreadAsync();
            var a2 = await ActiveAsync();
            if (a2 == null) return;
            await AllDefinitionsAsync(a2);
        }
    }
}
