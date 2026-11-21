using System;
using System.Collections.Generic;
using System.ComponentModel.Design;
using System.IO;
using System.Linq;
using System.Text;
using EnvDTE;
using Microsoft.VisualStudio.ComponentModelHost;
using Microsoft.VisualStudio.Editor;
using Microsoft.VisualStudio.Shell;
using Microsoft.VisualStudio.Text;
using Microsoft.VisualStudio.Text.Editor;
using Microsoft.VisualStudio.Text.Operations;
using Microsoft.VisualStudio.TextManager.Interop;
using Task = System.Threading.Tasks.Task;

namespace KCppAssist
{
    /// <summary>
    /// 電球(Ctrl+.)のリファクタリングと生成。計算は Refactor / ClassGen / FileGen。ここはエディターとファイルとのつなぎ。
    /// 1 つのファイルで済むものは Refactor.Make の編集をそのまま当てる。ファイルをまたぐもの(Natvis、
    /// 定義をまとめて作る、クラスを別ファイルへ、cpp の初期化子リスト)は、ここで相手のファイルを開く。
    /// </summary>
    public sealed partial class KCppAssistPackage
    {
        internal const int CmdRefactor = 0x0115;

        private void RegisterRefactorCommands(OleMenuCommandService commands)
        {
            commands.AddCommand(new OleMenuCommand((s, e) => ShowRefactorMenu(), new CommandID(CmdSet, CmdRefactor)));
        }

        private sealed class Active
        {
            public IWpfTextView View;
            public string Path, Text, Eol;
            public int Caret;
            public DTE Dte;
            public IVsEditorAdaptersFactoryService Adapters;
            public ITextUndoHistoryRegistry Undo;
        }

        private async System.Threading.Tasks.Task<Active> ActiveAsync()
        {
            await JoinableTaskFactory.SwitchToMainThreadAsync();
            var model = (IComponentModel)await GetServiceAsync(typeof(SComponentModel));
            var adapters = model.GetService<IVsEditorAdaptersFactoryService>();
            var manager = (IVsTextManager)await GetServiceAsync(typeof(SVsTextManager));
            var dte = (DTE)await GetServiceAsync(typeof(DTE));
            IVsTextView vsView;
            manager.GetActiveView(1, null, out vsView);
            IWpfTextView view = vsView == null ? null : adapters.GetWpfTextView(vsView);
            if (view == null) { await ReportAsync("アクティブなエディターがありません", true); return null; }
            string path = dte.ActiveDocument != null ? dte.ActiveDocument.FullName : null;
            if (path == null) { await ReportAsync("ファイルが保存されていません", true); return null; }
            string text = view.TextSnapshot.GetText();
            return new Active
            {
                View = view, Path = path, Text = text, Eol = CppText.Eol(text),
                Caret = view.Caret.Position.BufferPosition.Position, Dte = dte, Adapters = adapters,
                Undo = model.GetService<ITextUndoHistoryRegistry>(),
            };
        }

        /// <summary>電球の項目から呼ぶ。id の書き換えを、いまの文字で計算し直して当てる。</summary>
        internal void RunRefactor(string id)
        {
            _ = JoinableTaskFactory.RunAsync(async () =>
            {
                try { await RunRefactorAsync(id); }
                catch (Exception ex) { await ReportAsync("例外: " + ex.Message, true); Log(ex.ToString()); }
            });
        }

        private async Task RunRefactorAsync(string id)
        {
            var a = await ActiveAsync();
            if (a == null) return;
            switch (id)
            {
                case "natvis": await NatvisAsync(a); return;
                case "defs-all": await AllDefinitionsAsync(a); return;
                case "extract": await ExtractAsync(a); return;
                case "makecpp": await MakeCppAsync(a); return;
                case "ctordtor-cpp": await CtorDtorCppAsync(a); return;
            }
            string why;
            var ch = Refactor.Make(id, a.Text, a.Caret, a.Eol, IncludeService.IsHeader(a.Path), out why);
            if (ch == null && id == "initorder")
            {
                // cpp のコンストラクター: クラスの宣言はヘッダーにある
                var sig = FunctionScan.Scan(a.Text).FirstOrDefault(s => s.InitStart >= 0 && s.HasBody && s.PrefixStart <= a.Caret && a.Caret <= s.BodyOpen);
                if (sig != null && sig.Class != null)
                {
                    string header = HeaderTextFor(a.Path, sig.Class);
                    if (header != null) ch = ClassGen.InitOrder(a.Text, a.Caret, header, out why);
                }
            }
            if (ch == null) { await ReportAsync(why, true); return; }
            SyncService.ApplyEdits(a.View.TextBuffer, ch.Edits, a.Undo, "K-Cpp: " + id);
            await ReportAsync(ch.Message, false);
        }

        /// <summary>同じ名前のヘッダーか、型の索引から、className を宣言したヘッダーの文字を読む。開いていればエディターの文字。</summary>
        private static string HeaderTextFor(string path, string className)
        {
            string dir = Path.GetDirectoryName(path), stem = Path.GetFileNameWithoutExtension(path);
            var files = new[] { ".h", ".hpp", ".hh", ".hxx" }.Select(e => Path.Combine(dir, stem + e)).Where(File.Exists).ToList();
            files.AddRange(IncludeService.Index.Lookup(className));
            foreach (string f in files.Distinct(StringComparer.OrdinalIgnoreCase))
            {
                string t = CallCheckHub.OpenText(f) ?? SymbolService.ReadText(f);
                if (t != null && Scopes.Parse(t).Any(s => s.IsClass && s.Name == className)) return t;
            }
            return null;
        }

        // ---- 一覧(キーで開く) ----

        /// <summary>カーソルの位置で使える書き換えを一覧にして選ばせる(電球と同じ項目)。</summary>
        private void ShowRefactorMenu()
        {
            _ = JoinableTaskFactory.RunAsync(async () =>
            {
                try
                {
                    var a = await ActiveAsync();
                    if (a == null) return;
                    var offers = OffersAt(a.Path, a.Text, a.Caret, a.Eol);
                    if (offers.Count == 0) { await ReportAsync("この位置で使える書き換えはありません", true); return; }
                    var titles = offers.Select(o => o.Title).ToList();
                    string pick = Choose("書き換えを選んでください", titles);
                    if (pick == null) return;
                    await RunRefactorAsync(offers[titles.IndexOf(pick)].Id);
                }
                catch (Exception ex) { await ReportAsync("例外: " + ex.Message, true); Log(ex.ToString()); }
            });
        }

        /// <summary>電球と一覧に出す項目。1 ファイルの書き換えに、ファイルをまたぐものを足す。</summary>
        internal static List<Refactor.Offer> OffersAt(string path, string text, int caret, string eol)
        {
            bool header = IncludeService.IsHeader(path);
            var list = Refactor.Offers(text, caret, eol, header);
            if (!list.Any(o => o.Id == "initorder") && !header)
            {
                var sig = FunctionScan.Scan(text).FirstOrDefault(s => s.InitStart >= 0 && s.HasBody && s.PrefixStart <= caret && caret <= s.BodyOpen);
                if (sig != null && sig.Class != null) list.Add(new Refactor.Offer { Id = "initorder", Title = L.T("初期化子リストを、メンバーの宣言の順に並べ替える") });
            }
            var cls = MemberScan.At(text, caret);
            if (cls != null)
            {
                if (header && ClassGen.OnHead(text, caret))
                {
                    string stem0 = Path.GetFileNameWithoutExtension(path);
                    bool hasCpp = new[] { ".cpp", ".cc", ".cxx" }.Any(e => File.Exists(Path.Combine(Path.GetDirectoryName(path), stem0 + e)));
                    if (!hasCpp) list.Add(new Refactor.Offer { Id = "makecpp", Title = L.F("{0}.cpp を作る", stem0) });
                }
                if (header && ClassGen.AtClassLevel(text, caret))
                {
                    // 「.h に宣言、.cpp に定義」は、ほかの 2 通りのすぐ後ろに並べる
                    int k = list.FindLastIndex(o => o.Id == "ctordtor-default" || o.Id == "ctordtor-inline");
                    if (k >= 0) list.Insert(k + 1, new Refactor.Offer { Id = "ctordtor-cpp", Title = L.T("コンストラクター・デストラクターを作る (.h に宣言、.cpp に定義)") });
                }
                // クラス全体の項目は、クラスそのものを指している行でだけ(メンバーの行では出さない)
                bool classLevel = ClassGen.AtClassLevel(text, caret);
                if (classLevel && cls.Members.Count > 0) list.Add(new Refactor.Offer { Id = "natvis", Title = L.T("デバッガーの表示 (Natvis) を作る") });
                if (classLevel && header && FileGen.Declarations(text, cls.Scope).Count > 0) list.Add(new Refactor.Offer { Id = "defs-all", Title = L.T("定義のない関数を、cpp にまとめて作る") });
                if (classLevel && header && (cls.Scope.Parent == null || !cls.Scope.Parent.IsClass) && !string.Equals(Path.GetFileName(path), cls.Name + ".h", StringComparison.OrdinalIgnoreCase))
                    list.Add(new Refactor.Offer { Id = "extract", Title = L.F("クラスを {0}.h / .cpp に移す", cls.Name) });
            }
            // 使うライブラリ次第の項目は、設定で出したときだけ(初期値はどれも出さない)
            var opt = IncludeService.Options;
            if (opt != null)
                list.RemoveAll(o => (o.Id == "json" && !opt.OfferJson) || (o.Id == "cereal" && !opt.OfferCereal) || (o.Id == "natvis" && !opt.OfferNatvis));
            return list;
        }

        // ---- Natvis ----

        private async Task NatvisAsync(Active a)
        {
            var cls = MemberScan.At(a.Text, a.Caret);
            if (cls == null || cls.Members.Count == 0) { await ReportAsync("データ メンバーのあるクラスの中で押してください", true); return; }
            Project proj = null;
            try { proj = a.Dte.ActiveDocument.ProjectItem?.ContainingProject; } catch (Exception) { }
            string projFile = null;
            try { projFile = proj?.FullName; } catch (Exception) { }
            if (string.IsNullOrEmpty(projFile)) { await ReportAsync("このファイルはプロジェクトに入っていません", true); return; }
            string file = Path.Combine(Path.GetDirectoryName(projFile), Path.GetFileNameWithoutExtension(projFile) + ".natvis");
            bool exists = File.Exists(file);
            string old = exists ? File.ReadAllText(file) : null;
            string merged = ClassGen.NatvisMerge(old, cls.FullName, ClassGen.NatvisType(cls), old != null && !old.Contains("\r\n") ? "\n" : "\r\n");
            if (merged == null) { await ReportAsync(Path.GetFileName(file) + " に </AutoVisualizer> がありません", true); return; }
            File.WriteAllText(file, merged, new UTF8Encoding(true));
            if (!exists)
            {
                try { proj.ProjectItems.AddFromFile(file); }
                catch (Exception ex) { Log("natvis add failed: " + ex.Message); }
            }
            await ReportAsync(Path.GetFileName(file) + " に " + cls.FullName + " の表示を" + (exists ? "書きました" : "作り、プロジェクトに足しました") + " (デバッグを始め直すと効きます)", false);
        }

        // ---- 定義のない関数をまとめて作る ----

        private async Task AllDefinitionsAsync(Active a)
        {
            var cls = MemberScan.At(a.Text, a.Caret);
            if (cls == null) { await ReportAsync("クラスの中で押してください", true); return; }
            string root = IncludeService.RootFor(a.Path);
            var opt = SyncService.Options;
            var cpps = await Task.Run(() => SyncService.Candidates(a.Path, cls.Name, root, true, opt).Where(f => !IncludeService.IsHeader(f)).ToList());
            await JoinableTaskFactory.SwitchToMainThreadAsync();
            if (cpps.Count == 0) { await ReportAsync(cls.Name + " の cpp が見つかりません。先に cpp を作ってください", true); return; }
            ITextBuffer buf = SyncService.OpenForEdit(cpps[0], a.Adapters);
            if (buf == null) { await ReportAsync(Path.GetFileName(cpps[0]) + " を開けませんでした", true); return; }
            int made = 0;
            var failed = new List<string>();
            foreach (var decl in FileGen.Declarations(a.Text, cls.Scope))
            {
                string cppText = buf.CurrentSnapshot.GetText();
                if (FunctionScan.Scan(cppText).Any(s => SyncPlan.Counterpart(s, decl, true) > 0)) continue;
                string cEol = cppText.Contains("\r\n") ? "\r\n" : a.Eol;
                string why;
                var def = DefinitionGen.PlanDefinition(a.Text, decl, cppText, cEol, out why);
                if (def == null) { failed.Add(decl.Name); continue; }
                SyncService.Insert(buf, def.Position, def.Text, a.Undo, "K-Cpp: 定義を作る");
                made++;
            }
            ReturnTo(a.Path, cpps[0]);
            if (made == 0 && failed.Count == 0) { await ReportAsync("定義のない関数はありません", true); return; }
            await ReportAsync(Path.GetFileName(cpps[0]) + " に定義を " + made + " 個作りました" + (failed.Count > 0 ? " (作れなかったもの: " + string.Join(", ", failed) + ")" : ""), false);
        }

        // ---- クラスを別ファイルへ ----

        private async Task ExtractAsync(Active a)
        {
            if (!IncludeService.IsHeader(a.Path)) { await ReportAsync("ヘッダーのクラスの中で押してください", true); return; }
            string why;
            var ex = FileGen.ExtractClass(a.Text, a.Caret, Path.GetFileName(a.Path), a.Eol, out why);
            if (ex == null) { await ReportAsync(why, true); return; }
            string dir = Path.GetDirectoryName(a.Path);
            string newH = Path.Combine(dir, ex.ClassName + ".h");
            string newCpp = Path.Combine(dir, ex.ClassName + ".cpp");
            if (File.Exists(newH)) { await ReportAsync(Path.GetFileName(newH) + " はすでにあります", true); return; }

            // 元の cpp(同じ名前)から、このクラスの定義を移す
            string oldCpp = new[] { ".cpp", ".cc", ".cxx" }.Select(e => Path.Combine(dir, Path.GetFileNameWithoutExtension(a.Path) + e)).FirstOrDefault(File.Exists);
            ITextBuffer cppBuf = null;
            List<Tuple<int, int>> defs = null;
            string cppText = null;
            if (oldCpp != null && !File.Exists(newCpp))
            {
                cppBuf = SyncService.OpenForEdit(oldCpp, a.Adapters);
                if (cppBuf != null)
                {
                    cppText = cppBuf.CurrentSnapshot.GetText();
                    defs = FileGen.DefinitionsOf(cppText, ex.ClassName);
                }
            }

            var enc = new UTF8Encoding(true);
            File.WriteAllText(newH, ex.NewHeader, enc);
            string cppMsg = "";
            if (defs != null && defs.Count > 0)
            {
                string cEol = CppText.Eol(cppText);
                File.WriteAllText(newCpp, FileGen.NewSource(cppText, ex.ClassName, defs, cEol), enc);
                SyncService.ApplyEdits(cppBuf, defs.Select(d => Tuple.Create(d.Item1, d.Item2 - d.Item1, "")).ToList(), a.Undo, "K-Cpp: 定義を移す");
                cppMsg = "。定義 " + defs.Count + " 個を " + Path.GetFileName(newCpp) + " に移しました";
            }
            SyncService.ApplyEdits(a.View.TextBuffer, ex.OldHeader.Edits, a.Undo, "K-Cpp: クラスを移す");

            // プロジェクトに足す
            try
            {
                var proj = a.Dte.ActiveDocument.ProjectItem?.ContainingProject;
                if (proj != null)
                {
                    proj.ProjectItems.AddFromFile(newH);
                    if (cppMsg.Length > 0) proj.ProjectItems.AddFromFile(newCpp);
                }
            }
            catch (Exception e2) { Log("extract add failed: " + e2.Message); }
            await ReportAsync(ex.OldHeader.Message + cppMsg + " (元のファイルは保存していません)", false);
        }
    }
}
