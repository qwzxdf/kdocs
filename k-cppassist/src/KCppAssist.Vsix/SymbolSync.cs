using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.ComponentModel.Composition;
using System.IO;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading.Tasks;
using System.Windows.Threading;
using EnvDTE;
using Microsoft.VisualStudio.Editor;
using Microsoft.VisualStudio.Shell;
using Microsoft.VisualStudio.Shell.Interop;
using Microsoft.VisualStudio.Text;
using Microsoft.VisualStudio.Text.Editor;
using Microsoft.VisualStudio.Text.Operations;
using Microsoft.VisualStudio.Utilities;

namespace KCppAssist
{
    /// <summary>名前の変更と、呼び出しの引数の書き換えのうち、VS に触る部分(ファイルを集める、バッファーを書き換える、知らせる)。</summary>
    internal static class SymbolService
    {
        public const string EditTag = "K-CppAssist.Symbol";

        private static readonly string[] Exts = { ".cpp", ".cc", ".cxx", ".c++", ".h", ".hpp", ".hh", ".hxx", ".inl", ".ipp" };
        private const int MaxFiles = 6000;
        private const long MaxBytes = 2 * 1024 * 1024;

        public sealed class FileRefs
        {
            public string File, Text;
            public List<int> Certain = new List<int>();
            public List<int> Ambiguous = new List<int>();
        }

        public sealed class Analysis
        {
            public SymbolScan.Context Ctx = new SymbolScan.Context();
            public List<FileRefs> Files = new List<FileRefs>();     // 名前が出てくるファイル
            public bool Overloaded;
            public bool SameNameClass;                              // 同じ名前のクラスが、別のファイルにもある
        }

        private sealed class FileEntry
        {
            public long Ticks, Length;
            public Dictionary<string, HashSet<string>> Classes = new Dictionary<string, HashSet<string>>();
            public string[] Words;                                  // ファイルに出てくる識別子(並べ替え済み)
        }

        private static readonly ConcurrentDictionary<string, FileEntry> cache = new ConcurrentDictionary<string, FileEntry>(StringComparer.OrdinalIgnoreCase);
        private static readonly Regex WordRe = new Regex(@"[A-Za-z_]\w*", RegexOptions.Compiled);

        public static bool IsCppFile(string path)
        {
            string ext = path == null ? "" : Path.GetExtension(path).ToLowerInvariant();
            return Exts.Contains(ext);
        }

        /// <summary>
        /// root の下の C++ のファイルと、開いているファイル(openTexts)から、d を使っている場所を集める。UI スレッドの外で呼ぶ。
        /// extraKeys は、引数を変えたときの、変える前の引数の型の並び(これと同じ宣言は、オーバーロードに数えない)。
        /// collectRefs が false のときは、名前が出てくるファイルを集めるだけ(場所は調べない)。
        /// </summary>
        public static Analysis Analyze(string root, ISet<string> skip, SymbolScan.Decl d, string declFile, Dictionary<string, string> openTexts,
            List<List<string>> extraKeys, bool collectRefs)
        {
            var a = new Analysis();
            var bases = new Dictionary<string, HashSet<string>>();
            var classFiles = new Dictionary<string, List<string>>();
            var texts = new ConcurrentDictionary<string, string>(openTexts, StringComparer.OrdinalIgnoreCase);
            var candidates = new List<KeyValuePair<string, string>>();
            var seen = new HashSet<string>(StringComparer.OrdinalIgnoreCase);

            Action<string, Dictionary<string, HashSet<string>>> merge = (file, classes) =>
            {
                foreach (var kv in classes)
                {
                    HashSet<string> set;
                    if (!bases.TryGetValue(kv.Key, out set)) bases[kv.Key] = set = new HashSet<string>();
                    set.UnionWith(kv.Value);
                    List<string> files;
                    if (!classFiles.TryGetValue(kv.Key, out files)) classFiles[kv.Key] = files = new List<string>();
                    files.Add(file);
                }
            };

            // static の関数と、無名の namespace の中の関数は、そのファイルの中だけを見る(ほかのファイルの同じ名前は、別の関数)
            bool fileLocal = d.Kind == SymbolScan.Kind.Function && d.FileLocal;
            foreach (var kv in openTexts)
            {
                seen.Add(kv.Key);
                var local = new Dictionary<string, HashSet<string>>();
                SymbolScan.CollectClasses(kv.Value, local);
                merge(kv.Key, local);
                if (fileLocal && !string.Equals(kv.Key, declFile, StringComparison.OrdinalIgnoreCase)) continue;      // クラスの一覧だけ使う
                if (kv.Value.IndexOf(d.Name, StringComparison.Ordinal) >= 0) candidates.Add(new KeyValuePair<string, string>(kv.Key, kv.Value));
            }
            if (!string.IsNullOrEmpty(root) && Directory.Exists(root))
            {
                var stack = new Stack<string>();
                stack.Push(root);
                int read = 0;
                while (stack.Count > 0 && read < MaxFiles)
                {
                    string dir = stack.Pop();
                    try
                    {
                        foreach (FileInfo fi in new DirectoryInfo(dir).GetFiles())
                        {
                            string f = fi.FullName;
                            if (!IsCppFile(f) || !seen.Add(f)) continue;
                            read++;
                            try
                            {
                                if (fi.Length > MaxBytes) continue;
                                // 前に読んだときから変わっていないファイルは、覚えておいた「クラスの一覧」と「出てくる単語」で済ませる
                                string text = null;
                                FileEntry en;
                                if (!cache.TryGetValue(f, out en) || en.Ticks != fi.LastWriteTimeUtc.Ticks || en.Length != fi.Length)
                                {
                                    Encoding enc;
                                    text = RenameSync.ReadKeepingEncoding(f, out enc);
                                    en = new FileEntry { Ticks = fi.LastWriteTimeUtc.Ticks, Length = fi.Length };
                                    SymbolScan.CollectClasses(text, en.Classes);
                                    en.Words = WordRe.Matches(text).Cast<Match>().Select(x => string.Intern(x.Value)).Distinct().OrderBy(x => x, StringComparer.Ordinal).ToArray();
                                    cache[f] = en;
                                }
                                merge(f, en.Classes);
                                if (fileLocal) continue;
                                if (Array.BinarySearch(en.Words, d.Name, StringComparer.Ordinal) < 0) continue;
                                if (text == null) { Encoding enc; text = RenameSync.ReadKeepingEncoding(f, out enc); }
                                candidates.Add(new KeyValuePair<string, string>(f, text));
                                texts[f] = text;
                            }
                            catch (Exception) { }
                        }
                        foreach (string sub in Directory.GetDirectories(dir))
                        {
                            string leaf = Path.GetFileName(sub);
                            if (!skip.Contains(leaf) && !leaf.StartsWith("cmake-build", StringComparison.OrdinalIgnoreCase)) stack.Push(sub);
                        }
                    }
                    catch (Exception) { }
                }
            }

            a.Ctx.Bases = bases;
            a.Ctx.ClassTexts = cls =>
            {
                List<string> files;
                if (!classFiles.TryGetValue(cls, out files)) return null;
                return files.Select(f => texts.GetOrAdd(f, p =>
                {
                    try { Encoding enc; return RenameSync.ReadKeepingEncoding(p, out enc); }
                    catch (Exception) { return ""; }
                }));
            };

            SymbolScan.NormalizeKind(d, a.Ctx);      // 「ns::Func() {…}」は、クラスのメンバーではなく、名前空間の関数
            bool member = d.Class != null;
            var scans = candidates.ToDictionary(c => c.Key, c => FunctionScan.Scan(c.Value).Where(s => s.Name == d.Name).ToList(), StringComparer.OrdinalIgnoreCase);
            if (member)
            {
                var declares = new HashSet<string>(scans.Values.SelectMany(x => x).Where(s => s.Class != null).Select(s => s.Class));
                a.Ctx.Family = SymbolScan.BuildFamily(d.Class, d.Kind == SymbolScan.Kind.Method, bases, declares);
                if (d.Kind == SymbolScan.Kind.Method && (d.Sig == null || !d.Sig.InClass))
                    foreach (string t in a.Ctx.TextsOf(d.Class))
                    {
                        bool priv;
                        if (SymbolScan.DeclaresMethod(t, d.Class, d.Name, out priv)) { d.Private = priv; break; }
                    }
            }

            else
            {
                // 同じ名前の関数が、別の namespace にもあるか
                foreach (var s in scans.Values.SelectMany(x => x))
                    if ((s.Class == null || (!s.InClass && !a.Ctx.IsClass(s.Class))) && SyncPlan.ChainScore(s.Chain, d.Chain) == 0) a.Ctx.NameClash = true;
            }

            // 同じ名前で、引数の型の違う宣言があるか
            string declText;
            if (d.Sig != null && openTexts.TryGetValue(declFile, out declText) && d.Sig.Close <= declText.Length)
            {
                var mine = SignatureSync.KeyVariants(d.Sig.Inner(declText));
                if (extraKeys != null) mine = mine.Concat(extraKeys).ToList();
                if (mine.Count > 0)
                {
                    foreach (var c in candidates)
                        foreach (var s in scans[c.Key])
                        {
                            if (member ? !(s.Class != null && a.Ctx.Family.Contains(s.Class)) : s.Class != null) continue;
                            var keys = SignatureSync.KeyVariants(s.Inner(c.Value));
                            if (keys.Count > 0 && !SyncPlan.SameKeysAny(keys, mine)) a.Overloaded = true;
                        }
                    if (a.Overloaded) a.Ctx.OverloadKeys = mine;
                }
            }

            foreach (var c in candidates)
            {
                var fr = new FileRefs { File = c.Key, Text = c.Value };
                if (collectRefs)
                {
                    bool isDecl = string.Equals(c.Key, declFile, StringComparison.OrdinalIgnoreCase);
                    foreach (var r in SymbolScan.MemberRefs(c.Value, d, a.Ctx, isDecl ? d.Start : -1))
                        (r.Certain ? fr.Certain : fr.Ambiguous).Add(r.Start);
                    if (fr.Certain.Count == 0 && fr.Ambiguous.Count == 0) continue;
                }
                a.Files.Add(fr);
            }

            // 同じ名前のクラスが、別のファイルにも定義されている。そちらのファイル(と、同じ名前の cpp / ヘッダー)の中は、確かとは言えない
            List<string> defs;
            if (member && collectRefs && classFiles.TryGetValue(d.Class, out defs) && defs.Distinct(StringComparer.OrdinalIgnoreCase).Count() > 1)
            {
                string stem = Path.GetFileNameWithoutExtension(declFile);
                Func<string, bool> sameStem = f => string.Equals(Path.GetFileNameWithoutExtension(f), stem, StringComparison.OrdinalIgnoreCase);
                if (defs.Any(sameStem))
                {
                    var others = new HashSet<string>(defs.Where(f => !sameStem(f)).Select(Path.GetFileNameWithoutExtension), StringComparer.OrdinalIgnoreCase);
                    foreach (var fr in a.Files)
                    {
                        if (!others.Contains(Path.GetFileNameWithoutExtension(fr.File))) continue;
                        fr.Ambiguous.AddRange(fr.Certain);
                        fr.Certain.Clear();
                        a.SameNameClass = true;
                    }
                }
            }
            return a;
        }

        /// <summary>エディターで開いている C++ のファイルと、その今の文字。</summary>
        public static Dictionary<string, ITextSnapshot> OpenSnapshots(IVsEditorAdaptersFactoryService adapters)
        {
            ThreadHelper.ThrowIfNotOnUIThread();
            var map = new Dictionary<string, ITextSnapshot>(StringComparer.OrdinalIgnoreCase);
            try
            {
                var dte = (DTE)Package.GetGlobalService(typeof(DTE));
                foreach (Document doc in dte.Documents)
                {
                    try
                    {
                        string p = doc.FullName;
                        if (string.IsNullOrEmpty(p) || !IsCppFile(p) || map.ContainsKey(p)) continue;
                        ITextBuffer buf = SyncService.OpenBuffer(p, adapters);
                        if (buf != null) map[p] = buf.CurrentSnapshot;
                    }
                    catch (Exception) { }
                }
            }
            catch (Exception ex) { KCppAssistPackage.Log("symbol: list documents failed: " + ex.Message); }
            return map;
        }

        /// <summary>(位置, 長さ, 文字)の編集を、snap の位置で、まとめて 1 回の Undo で適用する。適用できなければ false。</summary>
        public static bool ApplyEdits(ITextSnapshot snap, List<Tuple<int, int, string>> edits, ITextUndoHistoryRegistry undo, string description)
        {
            if (edits.Count == 0) return true;
            ITextBuffer buffer = snap.TextBuffer;
            try
            {
                ITextUndoHistory history = null;
                if (undo != null) { try { undo.TryGetHistory(buffer, out history); } catch (Exception) { } }
                using (var tx = history == null ? null : history.CreateTransaction(description))
                {
                    using (var edit = buffer.CreateEdit(EditOptions.None, null, EditTag))
                    {
                        // snap が古ければ、いまの位置へ写してから置き換える
                        ITextSnapshot now = edit.Snapshot;
                        foreach (var e in edits.OrderByDescending(x => x.Item1))
                        {
                            var span = new SnapshotSpan(snap, e.Item1, e.Item2);
                            if (now != snap) span = snap.CreateTrackingSpan(span, SpanTrackingMode.EdgeExclusive).GetSpan(now);
                            edit.Replace(span, e.Item3);
                        }
                        if (edit.Apply() == null) return false;
                    }
                    if (tx != null) tx.Complete();
                }
                return true;
            }
            catch (Exception ex) { KCppAssistPackage.Log("symbol: edit failed: " + ex.Message); return false; }
        }

        /// <summary>閉じているファイルを、文字コードを保ったまま書き換える。変えた数を返す。UI スレッドの外で呼ぶ。</summary>
        public static int RewriteFile(string file, Func<string, List<SymbolScan.Edit>> plan)
        {
            try
            {
                Encoding enc;
                string text = RenameSync.ReadKeepingEncoding(file, out enc);
                var edits = plan(text);
                if (edits == null || edits.Count == 0) return 0;
                RenameSync.WriteKeepingEncoding(file, SymbolScan.Apply(text, edits), enc);
                return edits.Count;
            }
            catch (Exception ex) { KCppAssistPackage.Log("symbol: rewrite failed " + file + ": " + ex.Message); return 0; }
        }

        private static Guid paneGuid = new Guid("6E2B7C3A-91D4-4F0B-8E55-2C7A4D1B9F30");

        /// <summary>出力ウィンドウの「K-CppAssist」に書く。「ファイル(行): …」の行は、ダブルクリックでその場所へ飛べる。</summary>
        public static void Output(IEnumerable<string> lines)
        {
            ThreadHelper.ThrowIfNotOnUIThread();
            try
            {
                var ow = Package.GetGlobalService(typeof(SVsOutputWindow)) as IVsOutputWindow;
                if (ow == null) return;
                IVsOutputWindowPane pane;
                if (ow.GetPane(ref paneGuid, out pane) != 0 || pane == null)
                {
                    ow.CreatePane(ref paneGuid, "K-CppAssist", 1, 0);
                    ow.GetPane(ref paneGuid, out pane);
                }
                if (pane == null) return;
                foreach (string ln in lines) pane.OutputStringThreadSafe(ln + "\r\n");
            }
            catch (Exception ex) { KCppAssistPackage.Log("symbol: output failed: " + ex.Message); }
        }

        public static string LineText(string text, int pos)
        {
            int s = pos, e = pos;
            while (s > 0 && text[s - 1] != '\n') s--;
            while (e < text.Length && text[e] != '\n' && text[e] != '\r') e++;
            string ln = text.Substring(s, e - s).Trim();
            return ln.Length > 120 ? ln.Substring(0, 120) + "…" : ln;
        }
    }

    /// <summary>C/C++ のエディターが開くたびに、名前の変更をほかの場所へ写す監視を付ける。</summary>
    [Export(typeof(IWpfTextViewCreationListener))]
    [ContentType("C/C++")]
    [TextViewRole(PredefinedTextViewRoles.Document)]
    internal sealed class SymbolSyncListener : IWpfTextViewCreationListener
    {
        [Import] internal ITextDocumentFactoryService Documents { get; set; }
        [Import] internal ITextUndoHistoryRegistry Undo { get; set; }
        [Import] internal IVsEditorAdaptersFactoryService Adapters { get; set; }

        public void TextViewCreated(IWpfTextView view)
        {
            try { new SymbolSyncSession(view, this); }
            catch (Exception ex) { KCppAssistPackage.Log("symbol sync attach failed: " + ex); }
        }
    }

    /// <summary>
    /// 1 つのエディターについて、次の 2 つを見張る。
    /// 1. 宣言の名前(ローカル変数・引数・メンバー変数・メンバー関数・関数)を書き換えたら、それを使っている場所を、打つそばから同じ名前にする。
    ///    使っている場所は、最初の 1 文字を打ったときに決めて、位置で追いかける(名前では探し直さない)。途中の名前がほかの名前とぶつかっても、混ざらない。
    /// 2. 関数の引数を並べ替えた・消したら、カーソルが括弧の外へ出たときに、呼び出しの引数を同じ並びに直す。
    ///    (切り取って貼る途中の形で呼び出しを直すと、引数が失われるので、打つそばからは直さない)
    /// </summary>
    internal sealed class SymbolSyncSession
    {
        private sealed class Link
        {
            public ITextBuffer Buffer;
            public string File;
            public List<ITrackingSpan> Spans = new List<ITrackingSpan>();
        }

        private sealed class Run
        {
            public ITrackingSpan DeclSpan;
            public int DeclVersion;                                 // DeclSpan を作ったときの、バッファーの版
            public string OldName, FinalName;
            public SymbolScan.Decl Decl;
            public List<Link> Links = new List<Link>();
            public List<string> Closed = new List<string>();        // 開いていないファイル。終わったときに、ディスクの上で書き換える
            public SymbolScan.Context Ctx;
            public List<string> AmbiguousLines = new List<string>();
            public bool Resolving, Ended, Overloaded, SameNameClass;
            public string DiskName;                                 // 閉じているファイルに、いま書いてある名前
            public Task DiskTask;                                   // 閉じているファイルの書き換え(順に 1 つずつ行う)
        }

        private sealed class ArgWatch
        {
            public ITrackingSpan Inner;     // 括弧の中身
            public string OldInner;
        }

        private const int MaxOutputLines = 200;

        private readonly IWpfTextView view;
        private readonly SymbolSyncListener owner;
        private readonly ITextBuffer buffer;
        private readonly string path;
        private Run run;
        private ITrackingPoint fresh;       // いま新しく打っている識別子(打ち終わるまでは、名前の変更とみなさない)
        private ArgWatch argWatch;
        private bool pendingApply;
        private KeyValuePair<Run, ITextSnapshot>? pendingResolve;
        private readonly List<Run> pendingComplete = new List<Run>();
        private Run lastRun;                // 終えた名前の変更。元に戻す・やり直しで宣言の名前が変わったら、ほかのファイルも合わせる
        private Run pendingFollow;
        private ITrackingPoint declMiss;    // 宣言ではないと分かった識別子の頭(同じ識別子を打っている間、調べ直さない)
        private ITrackingPoint argMiss;     // 関数の宣言の括弧ではないと分かった「(」
        private DispatcherTimer focusTimer;

        public SymbolSyncSession(IWpfTextView view, SymbolSyncListener owner)
        {
            this.view = view;
            this.owner = owner;
            buffer = view.TextBuffer;
            ITextDocument doc;
            if (owner.Documents.TryGetTextDocument(buffer, out doc)) path = doc.FilePath;
            buffer.Changed += OnChanged;
            buffer.PostChanged += OnPostChanged;
            view.Caret.PositionChanged += OnCaretMoved;
            view.LostAggregateFocus += OnLostFocus;
            view.GotAggregateFocus += OnGotFocus;
            view.Closed += OnClosed;
        }

        private void OnClosed(object sender, EventArgs e)
        {
            Guard("close", () => { EndRun(); CommitArgs(); });
            buffer.Changed -= OnChanged;
            buffer.PostChanged -= OnPostChanged;
            view.Caret.PositionChanged -= OnCaretMoved;
            view.LostAggregateFocus -= OnLostFocus;
            view.GotAggregateFocus -= OnGotFocus;
            view.Closed -= OnClosed;
            if (focusTimer != null) focusTimer.Stop();
        }

        private static void Guard(string what, Action action)
        {
            try { action(); }
            catch (Exception ex) { KCppAssistPackage.Log("symbol " + what + " failed: " + ex); }
        }

        private static OptionsPage Opt { get { return SyncService.Options; } }

        private static SymbolRenameMode Mode { get { var o = Opt; return o == null ? SymbolRenameMode.Off : o.SymbolMode; } }

        private bool UndoBusy()
        {
            try
            {
                ITextUndoHistory h;
                return owner.Undo.TryGetHistory(buffer, out h) && h.State != TextUndoHistoryState.Idle;
            }
            catch (Exception) { return false; }
        }

        // ---- 入力を見る ----

        private void OnChanged(object sender, TextContentChangedEventArgs e) { Guard("changed", () => OnChangedCore(e)); }

        private void OnChangedCore(TextContentChangedEventArgs e)
        {
            if (path == null) return;
            string tag = e.EditTag as string;
            if (tag != null && tag.StartsWith("K-CppAssist", StringComparison.Ordinal)) return;     // 拡張が自分で書き換えた
            if (!view.HasAggregateFocus) return;                                                    // 同じファイルを 2 つの窓で開いているとき、打っている窓だけが見る
            if (UndoBusy()) { fresh = null; argWatch = null; FollowUndo(); return; }                // 元に戻す・やり直し
            if (e.Changes.Count != 1) { EndRunLater(); fresh = null; return; }
            ITextChange ch = e.Changes[0];

            WatchArgs(e, ch);

            if (run != null)
            {
                SnapshotSpan sp = run.DeclSpan.GetSpan(e.After);
                if (ch.NewPosition >= sp.Start.Position && ch.NewEnd <= sp.End.Position) { pendingApply = true; return; }
                EndRunLater();
            }
            if (Mode == SymbolRenameMode.Off) return;

            // 変える前の文字で、書き換えた場所を含む識別子を探す
            ITextSnapshotLine line = e.Before.GetLineFromPosition(ch.OldPosition);
            if (ch.OldEnd > line.End.Position) { fresh = null; return; }
            if (!ch.NewText.All(CppText.IsId) || !ch.OldText.All(CppText.IsId)) { fresh = null; return; }
            string lt = line.GetText();
            int s = ch.OldPosition - line.Start.Position, en = ch.OldEnd - line.Start.Position;
            while (s > 0 && CppText.IsId(lt[s - 1])) s--;
            while (en < lt.Length && CppText.IsId(lt[en])) en++;
            if (en == s)
            {
                // 何もない所に打ち始めた。打ち終わる(カーソルが離れる)までは、新しい名前を書いているだけ
                fresh = ch.NewLength > 0 ? e.After.CreateTrackingPoint(ch.NewPosition, PointTrackingMode.Negative) : null;
                return;
            }
            if (char.IsDigit(lt[s])) return;
            int idStart = line.Start.Position + s, idEnd = line.Start.Position + en;
            if (fresh != null)
            {
                int fp = fresh.GetPosition(e.Before);
                if (fp >= idStart && fp <= idEnd) return;
                fresh = null;
            }

            // 宣言ではないと分かっている識別子を打っている間は、ファイル全体を調べ直さない
            if (declMiss != null && declMiss.GetPosition(e.Before) == idStart) return;
            declMiss = null;
            string text = e.Before.GetText();
            SymbolScan.Decl d = SymbolScan.DeclAt(text, idStart);
            if (d == null || d.Start != idStart) { declMiss = e.After.CreateTrackingPoint(idStart, PointTrackingMode.Negative); return; }

            var r = new Run
            {
                DeclSpan = e.Before.CreateTrackingSpan(idStart, idEnd - idStart, SpanTrackingMode.EdgeInclusive),
                DeclVersion = e.Before.Version.VersionNumber,
                OldName = d.Name,
                FinalName = d.Name,
                DiskName = d.Name,
                Decl = d,
            };
            if (d.Kind == SymbolScan.Kind.Local || d.Kind == SymbolScan.Kind.Param)
            {
                var link = new Link { Buffer = buffer, File = path };
                foreach (var rf in SymbolScan.LocalRefs(text, d))
                    link.Spans.Add(e.Before.CreateTrackingSpan(rf.Start, d.Name.Length, SpanTrackingMode.EdgeExclusive));
                if (link.Spans.Count == 0) { declMiss = e.After.CreateTrackingPoint(idStart, PointTrackingMode.Negative); return; }      // ほかに使っている場所がない
                r.Links.Add(link);
            }
            else
            {
                r.Resolving = true;
                pendingResolve = new KeyValuePair<Run, ITextSnapshot>(r, e.Before);
            }
            run = r;
            pendingApply = true;
        }

        /// <summary>バッファーの書き換えは、Changed の中ではできないので、ここで行う。</summary>
        private void OnPostChanged(object sender, EventArgs e)
        {
            Guard("post", () =>
            {
                if (pendingComplete.Count > 0)
                {
                    var ended = pendingComplete.ToList();
                    pendingComplete.Clear();
                    foreach (Run r in ended) Complete(r);
                }
                if (pendingFollow != null)
                {
                    Run f = pendingFollow;
                    pendingFollow = null;
                    Follow(f);
                }
                if (pendingResolve != null)
                {
                    var pr = pendingResolve.Value;
                    pendingResolve = null;
                    _ = ResolveAsync(pr.Key, pr.Value);
                }
                if (!pendingApply) return;
                pendingApply = false;
                if (run != null) ApplyLive(run);
            });
        }

        private void OnCaretMoved(object sender, CaretPositionChangedEventArgs e)
        {
            Guard("caret", () =>
            {
                // ビューの文字は、バッファーより 1 つ古いことがある(書き換えの直後)。追いかけている範囲は新しい側にあるので、新しい側へ写して比べる
                SnapshotPoint c = e.NewPosition.BufferPosition;
                if (c.Snapshot != buffer.CurrentSnapshot) c = c.TranslateTo(buffer.CurrentSnapshot, PointTrackingMode.Positive);
                if (run != null)
                {
                    SnapshotSpan sp = run.DeclSpan.GetSpan(c.Snapshot);
                    if (c.Position < sp.Start.Position || c.Position > sp.End.Position) EndRun();
                }
                if (fresh != null)
                {
                    int fp = fresh.GetPosition(c.Snapshot);
                    int s = fp, en = fp;
                    while (s > 0 && CppText.IsId(c.Snapshot[s - 1])) s--;
                    while (en < c.Snapshot.Length && CppText.IsId(c.Snapshot[en])) en++;
                    if (c.Position < s || c.Position > en) fresh = null;
                }
                // 別の行へ動いたら、「宣言ではない」の覚えを捨てる(行を書き換えて、宣言になっているかもしれない)
                int line = c.GetContainingLine().LineNumber;
                if (declMiss != null && c.Snapshot.GetLineNumberFromPosition(declMiss.GetPosition(c.Snapshot)) != line) declMiss = null;
                if (argMiss != null && c.Snapshot.GetLineNumberFromPosition(argMiss.GetPosition(c.Snapshot)) != line) argMiss = null;
                if (argWatch != null)
                {
                    SnapshotSpan sp = argWatch.Inner.GetSpan(c.Snapshot);
                    if (c.Position < sp.Start.Position || c.Position > sp.End.Position) CommitArgs();
                }
            });
        }

        private void OnLostFocus(object sender, EventArgs e)
        {
            // 別のウィンドウを少し見ただけで、打ちかけの名前を閉じているファイルへ書かないように、少し待ってから終える。
            // 引数は、切り取って別のウィンドウから貼ることがあるので、ここでは確定しない(カーソルが括弧の外へ出たとき)
            Guard("focus", () =>
            {
                fresh = null;
                if (run == null) return;
                if (focusTimer == null)
                {
                    focusTimer = new DispatcherTimer(DispatcherPriority.Background, view.VisualElement.Dispatcher) { Interval = TimeSpan.FromMilliseconds(1500) };
                    focusTimer.Tick += (s2, e2) => Guard("focus timer", () =>
                    {
                        focusTimer.Stop();
                        if (!view.IsClosed && !view.HasAggregateFocus) EndRun();
                    });
                }
                focusTimer.Stop();
                focusTimer.Start();
            });
        }

        private void OnGotFocus(object sender, EventArgs e)
        {
            if (focusTimer != null) focusTimer.Stop();
        }

        // ---- 名前の変更 ----

        /// <summary>
        /// いまの宣言の名前。識別子として読めなければ null。
        /// 名前の前後に空白や記号を打った(const を前に足した、など)ときは、最後の識別子を名前とみなして、追いかける範囲をそこへ縮める。
        /// </summary>
        private string CurrentName(Run r)
        {
            ITextSnapshot snap = buffer.CurrentSnapshot;
            SnapshotSpan sp = r.DeclSpan.GetSpan(snap);
            string t = sp.GetText();
            if (SymbolScan.IsIdentifier(t)) return t;
            if (t.All(CppText.IsId)) return null;       // 空、数字で始まる、予約語(打っている途中)
            int end = t.Length;
            while (end > 0 && !CppText.IsId(t[end - 1])) end--;
            int start = end;
            while (start > 0 && CppText.IsId(t[start - 1])) start--;
            string last = t.Substring(start, end - start);
            if (!SymbolScan.IsIdentifier(last)) return null;
            r.DeclSpan = snap.CreateTrackingSpan(sp.Start.Position + start, last.Length, SpanTrackingMode.EdgeInclusive);
            r.DeclVersion = snap.Version.VersionNumber;
            return last;
        }

        private void ApplyLive(Run r)
        {
            string name = CurrentName(r);
            if (name == null) return;
            r.FinalName = name;
            if (Mode == SymbolRenameMode.Auto) ApplyName(r, name);
            ShowNote(r, name, false, 0);
        }

        /// <summary>追いかけている場所を、全部 name にする。変えた数を返す。</summary>
        private int ApplyName(Run r, string name, ITextBuffer except = null)
        {
            int n = 0;
            foreach (Link link in r.Links)
            {
                if (link.Buffer == except) continue;
                ITextSnapshot snap = link.Buffer.CurrentSnapshot;
                var edits = new List<Tuple<int, int, string>>();
                foreach (ITrackingSpan ts in link.Spans)
                {
                    SnapshotSpan sp = ts.GetSpan(snap);
                    if (sp.GetText() != name) edits.Add(Tuple.Create(sp.Start.Position, sp.Length, name));
                }
                if (edits.Count > 0 && SymbolService.ApplyEdits(snap, edits, owner.Undo, "K-CppAssist: 名前を変える")) n += edits.Count;
            }
            return n;
        }

        /// <summary>宣言の名前の頭の、ビューの文字での位置。ビューが、追いかけている範囲より古ければ -1(キャレットの行に出す)。</summary>
        private int AnchorOf(Run r)
        {
            ITextSnapshot vs = view.TextSnapshot;
            if (vs.Version.VersionNumber < r.DeclVersion) return -1;
            return r.DeclSpan.GetStartPoint(vs).Position;
        }

        private void ShowNote(Run r, string name, bool done, int closedFiles)
        {
            if (name == r.OldName && !done) return;
            int places = r.Links.Sum(l => l.Spans.Count);
            int files = r.Links.Count(l => l.Spans.Count > 0) + r.Closed.Count;
            var lines = new List<string>();
            if (r.Resolving) lines.Add("使っている場所を調べています…");
            else
            {
                string where = files > 1 ? files + " ファイル " : "";
                if (Mode == SymbolRenameMode.Auto || done) lines.Add(where + places + " か所" + (r.Closed.Count > 0 ? "(開いているファイル)" : "") + "を変えました");
                else lines.Add(where + places + " か所を、カーソルが名前から離れたときに変えます");
                if (r.Closed.Count > 0)
                    lines.Add(done ? "閉じているファイル " + closedFiles + " 個も書き換えました" : "閉じているファイル " + r.Closed.Count + " 個は、打ち終えたときに書き換えます");
                if (r.Overloaded) lines.Add("同じ名前で引数の違う関数があるので、呼び出しは変えていません");
                if (r.SameNameClass) lines.Add("同じ名前のクラスが別のファイルにもあるので、そちらは変えていません");
                if (r.AmbiguousLines.Count > 0) lines.Add("同じ物か決められない " + r.AmbiguousLines.Count + " か所は変えていません(出力ウィンドウ)");
            }
            SyncPreview.ShowNote(view, AnchorOf(r), "名前を変える", r.OldName, name, lines);
        }

        private async Task ResolveAsync(Run r, ITextSnapshot before)
        {
            try
            {
                await ThreadHelper.JoinableTaskFactory.SwitchToMainThreadAsync();
                var opt = Opt;
                string root = IncludeService.RootFor(path);
                var skip = IncludeService.SkipDirs(opt);
                var snaps = SymbolService.OpenSnapshots(owner.Adapters);
                snaps[path] = before;
                var texts = snaps.ToDictionary(kv => kv.Key, kv => kv.Value.GetText(), StringComparer.OrdinalIgnoreCase);
                var a = await Task.Run(() => SymbolService.Analyze(root, skip, r.Decl, path, texts, null, true));
                await ThreadHelper.JoinableTaskFactory.SwitchToMainThreadAsync();

                r.Ctx = a.Ctx;
                r.Overloaded = a.Overloaded;
                r.SameNameClass = a.SameNameClass;
                bool amb = opt != null && opt.SymbolAmbiguous;
                int len = r.OldName.Length;
                foreach (var f in a.Files)
                {
                    var pos = amb ? f.Certain.Concat(f.Ambiguous).ToList() : f.Certain;
                    if (!amb)
                        foreach (int p in f.Ambiguous)
                            r.AmbiguousLines.Add(f.File + "(" + SymbolScan.LineOf(f.Text, p) + "): " + SymbolService.LineText(f.Text, p));
                    if (pos.Count == 0) continue;
                    ITextSnapshot snap;
                    if (!snaps.TryGetValue(f.File, out snap)) { r.Closed.Add(f.File); continue; }
                    var link = new Link { Buffer = snap.TextBuffer, File = f.File };
                    foreach (int p in pos)
                        if (p + len <= snap.Length && snap.GetText(p, len) == r.OldName)
                            link.Spans.Add(snap.CreateTrackingSpan(p, len, SpanTrackingMode.EdgeExclusive));
                    r.Links.Add(link);
                }
            }
            catch (Exception ex) { KCppAssistPackage.Log("symbol resolve failed: " + ex); }
            finally { r.Resolving = false; }

            Guard("resolved", () =>
            {
                if (r.Ended) { ApplyName(r, r.FinalName); Finish(r); }
                else if (run == r) ApplyLive(r);
            });
        }

        /// <summary>名前を追いかけるのをやめて、閉じているファイルを書き換える。</summary>
        private void EndRun()
        {
            Run r = Detach();
            if (r != null) Complete(r);
        }

        /// <summary>Changed の中から呼ぶ版。バッファーの書き換えは、PostChanged まで待つ。</summary>
        private void EndRunLater()
        {
            Run r = Detach();
            if (r != null) pendingComplete.Add(r);
        }

        private Run Detach()
        {
            Run r = run;
            if (r == null) return null;
            run = null;
            lastRun = r;
            pendingApply = false;
            r.Ended = true;
            string name = CurrentName(r);
            if (name != null) r.FinalName = name;
            return r;
        }

        private void Complete(Run r)
        {
            if (r.Resolving) return;                 // 調べ終わったときに、続きをする
            ApplyName(r, r.FinalName);
            Finish(r);
        }

        /// <summary>
        /// 元に戻す・やり直しが始まった。作業中のバッファーの中は Visual Studio が戻すが、ほかのファイルは戻らないので、
        /// 戻したあとの宣言の名前に、ほかのファイルを合わせる(PostChanged で行う)。
        /// </summary>
        private void FollowUndo()
        {
            if (run != null) { Run r = run; run = null; pendingApply = false; r.Ended = true; lastRun = r; }
            if (lastRun != null) pendingFollow = lastRun;
        }

        private void Follow(Run r)
        {
            string name = r.DeclSpan.GetText(buffer.CurrentSnapshot);
            if (!SymbolScan.IsIdentifier(name) || name == r.FinalName) return;
            string was = r.FinalName;
            r.FinalName = name;
            if (r.Resolving) return;                 // 調べ終わったときに、この名前で写す
            // 作業中のバッファーは、元に戻す操作の途中なので触らない(Visual Studio が戻している)
            int n = ApplyName(r, name, buffer);
            Finish(r);
            if (n > 0 || r.Closed.Count > 0) IncludeService.Status(was + " を " + name + " に戻したので、ほかのファイルも合わせました");
        }

        private static SymbolScan.Decl Renamed(SymbolScan.Decl d, string name)
        {
            var c = new SymbolScan.Decl { Kind = d.Kind, Name = name, Start = -1, Class = d.Class, Private = d.Private, FileLocal = d.FileLocal, Sig = d.Sig };
            c.Chain.AddRange(d.Chain);
            return c;
        }

        /// <summary>閉じているファイルを、いまの名前(FinalName)に書き換えて、結果を知らせる。</summary>
        private void Finish(Run r)
        {
            string from = r.DiskName, to = r.FinalName;
            if (from == to) return;
            r.DiskName = to;
            var opt = Opt;
            bool amb = opt != null && opt.SymbolAmbiguous;
            SymbolScan.Decl was = Renamed(r.Decl, from);
            var closed = new List<string>();
            foreach (string f in r.Closed)
            {
                // 調べたあとで開かれたファイルは、エディターの上で書き換える
                ITextBuffer buf = SyncService.OpenBuffer(f, owner.Adapters);
                if (buf == null) { closed.Add(f); continue; }
                ITextSnapshot snap = buf.CurrentSnapshot;
                var edits = SymbolScan.MemberRefs(snap.GetText(), was, r.Ctx, -1).Where(x => x.Certain || amb)
                    .Select(x => Tuple.Create(x.Start, from.Length, to)).ToList();
                SymbolService.ApplyEdits(snap, edits, owner.Undo, "K-CppAssist: 名前を変える");
            }
            r.DiskTask = FinishAsync(r, was, to, closed, amb, r.DiskTask);
        }

        private async Task FinishAsync(Run r, SymbolScan.Decl was, string name, List<string> closed, bool amb, Task previous)
        {
            try
            {
                if (previous != null) await previous;        // 前の書き換えが終わってから(同じファイルを、同時に書かない)
                var written = new List<string>();
                if (closed.Count > 0)
                {
                    var done = await Task.Run(() =>
                    {
                        var list = new List<string>();
                        foreach (string f in closed)
                        {
                            int n = SymbolService.RewriteFile(f, text => SymbolScan.MemberRefs(text, was, r.Ctx, -1).Where(x => x.Certain || amb)
                                .Select(x => new SymbolScan.Edit { Start = x.Start, Length = was.Name.Length, Text = name }).ToList());
                            if (n > 0) list.Add(f + ": " + n + " か所");
                        }
                        return list;
                    });
                    written.AddRange(done);
                }
                await ThreadHelper.JoinableTaskFactory.SwitchToMainThreadAsync();
                int places = r.Links.Sum(l => l.Spans.Count);
                var outLines = new List<string>();
                if (written.Count > 0 || r.AmbiguousLines.Count > 0)
                {
                    outLines.Add("---- " + was.Name + " → " + name + " ----");
                    if (written.Count > 0) { outLines.Add("閉じていたファイルを書き換えて、保存しました:"); outLines.AddRange(written.Select(x => "  " + x)); }
                    if (r.AmbiguousLines.Count > 0)
                    {
                        outLines.Add("同じ物か決められないので、変えていない場所(同じクラスのメンバーなら、手で直してください):");
                        outLines.AddRange(r.AmbiguousLines.Take(MaxOutputLines));
                        if (r.AmbiguousLines.Count > MaxOutputLines) outLines.Add("  …ほか " + (r.AmbiguousLines.Count - MaxOutputLines) + " か所");
                    }
                    SymbolService.Output(outLines);
                }
                if (places == 0 && written.Count == 0 && r.AmbiguousLines.Count == 0) return;
                if (!view.IsClosed && closed.Count > 0) ShowNote(r, name, true, written.Count);
                IncludeService.Status(was.Name + " を " + name + " に変えました(" + (places + written.Count) + " か所"
                    + (r.AmbiguousLines.Count > 0 ? "。決められない " + r.AmbiguousLines.Count + " か所は、出力ウィンドウの K-CppAssist に出しました" : "") + ")");
            }
            catch (Exception ex) { KCppAssistPackage.Log("symbol finish failed: " + ex); }
        }

        // ---- 引数の並べ替え・削除を、呼び出しへ写す ----

        private void WatchArgs(TextContentChangedEventArgs e, ITextChange ch)
        {
            var opt = Opt;
            if (opt == null || !opt.CallArgSync) { argWatch = null; return; }
            if (argWatch != null)
            {
                SnapshotSpan sp = argWatch.Inner.GetSpan(e.After);
                if (ch.NewPosition >= sp.Start.Position && ch.NewEnd <= sp.End.Position) return;
                CommitArgs();
            }
            // 書き換えた場所が、括弧の中か(「;」「{」「}」を越えずに、閉じていない「(」が左にあるか)を、先に軽く見る
            ITextSnapshot before = e.Before;
            int depth = 0, open = -1;
            for (int i = ch.OldPosition - 1, n = 0; i >= 0 && n < 3000; i--, n++)
            {
                char c = before[i];
                if (c == ')') depth++;
                else if (c == '(') { if (depth == 0) { open = i; break; } depth--; }
                else if (c == ';' || c == '{' || c == '}') break;
            }
            if (open < 0) return;
            // 呼び出しの括弧(関数の宣言ではない)と分かっている間は、ファイル全体を調べ直さない
            if (argMiss != null && argMiss.GetPosition(before) == open) return;
            argMiss = null;
            string text = before.GetText();
            var sig = FunctionScan.Scan(text).FirstOrDefault(x => x.Open == open);
            if (sig == null || ch.OldEnd > sig.Close) { argMiss = e.After.CreateTrackingPoint(open, PointTrackingMode.Negative); return; }
            argWatch = new ArgWatch
            {
                Inner = before.CreateTrackingSpan(sig.Open + 1, sig.Close - sig.Open - 1, SpanTrackingMode.EdgeInclusive),
                OldInner = sig.Inner(text),
            };
        }

        /// <summary>カーソルが括弧の外へ出た。引数の並びが変わっていれば、呼び出しを直す。</summary>
        private void CommitArgs()
        {
            ArgWatch w = argWatch;
            if (w == null) return;
            argWatch = null;
            var opt = Opt;
            if (opt == null || !opt.CallArgSync || path == null) return;

            ITextSnapshot snap = buffer.CurrentSnapshot;
            SnapshotSpan sp = w.Inner.GetSpan(snap);
            string newInner = sp.GetText();
            if (SignatureSync.Norm(newInner) == SignatureSync.Norm(w.OldInner)) return;
            if (SignatureSync.HasDirectives(newInner) || SignatureSync.HasDirectives(w.OldInner)) return;
            var oldPs = SignatureSync.SplitParams(w.OldInner);
            var newPs = SignatureSync.SplitParams(newInner);
            if (oldPs == null || newPs == null) return;
            int[] map = SymbolScan.ParamMap(oldPs, newPs);
            if (map == null)
            {
                IncludeService.Status("同じ型の引数のどれを消したか決められないので、呼び出しは直していません(引数の名前を残して消すと、直せます)");
                return;
            }
            if (SymbolScan.IsIdentity(map, oldPs.Count)) return;        // 名前や型を変えただけ

            string text = snap.GetText();
            var sig = FunctionScan.Scan(text).FirstOrDefault(x => x.Open == sp.Start.Position - 1 && x.Close == sp.End.Position);
            if (sig == null) return;
            if (sig.Class != null && sig.Name == sig.Class) return;     // コンストラクターの呼び出し(Foo(…)、make_unique<Foo>(…))は、追えない
            string m = CppText.Mask(text);
            var d = new SymbolScan.Decl
            {
                Kind = sig.Class != null ? SymbolScan.Kind.Method : SymbolScan.Kind.Function,
                Name = sig.Name,
                Class = sig.Class,
                Sig = sig,
                Start = SymbolScan.NamePos(m, sig),
            };
            if (sig.Class == null) d.Chain.AddRange(sig.Chain);
            var hasDef = newPs.Select(p => { string def; SignatureSync.StripDefault(p, out def); return def != null; }).ToArray();
            _ = SyncCallsAsync(d, snap, oldPs.Count, map, hasDef, SignatureSync.KeyVariants(w.OldInner));
        }

        private sealed class CallPlan
        {
            public string File, Text;
            public List<SymbolScan.Edit> Edits;
            public List<int> Skipped = new List<int>();
        }

        private async Task SyncCallsAsync(SymbolScan.Decl d, ITextSnapshot snapNow, int oldCount, int[] map, bool[] hasDef, List<List<string>> oldKeys)
        {
            try
            {
                await ThreadHelper.JoinableTaskFactory.SwitchToMainThreadAsync();
                var opt = Opt;
                bool amb = opt != null && opt.SymbolAmbiguous;
                string root = IncludeService.RootFor(path);
                var skip = IncludeService.SkipDirs(opt);
                var snaps = SymbolService.OpenSnapshots(owner.Adapters);
                snaps[path] = snapNow;
                var texts = snaps.ToDictionary(kv => kv.Key, kv => kv.Value.GetText(), StringComparer.OrdinalIgnoreCase);

                SymbolService.Analysis a = null;
                var plans = await Task.Run(() =>
                {
                    a = SymbolService.Analyze(root, skip, d, path, texts, oldKeys, false);
                    var list = new List<CallPlan>();
                    foreach (var f in a.Files)
                    {
                        var p = new CallPlan { File = f.File, Text = f.Text };
                        p.Edits = SymbolScan.CallEdits(f.Text, d, a.Ctx, amb, oldCount, map, hasDef, p.Skipped);
                        if (p.Edits.Count > 0 || p.Skipped.Count > 0) list.Add(p);
                    }
                    return list;
                });
                await ThreadHelper.JoinableTaskFactory.SwitchToMainThreadAsync();

                int done = 0, files = 0;
                var notes = new List<string>();
                var closed = new List<CallPlan>();
                foreach (var p in plans)
                {
                    foreach (int s in p.Skipped) notes.Add(p.File + "(" + SymbolScan.LineOf(p.Text, s) + "): " + SymbolService.LineText(p.Text, s));
                    if (p.Edits.Count == 0) continue;
                    ITextSnapshot snap;
                    if (!snaps.TryGetValue(p.File, out snap)) { closed.Add(p); continue; }
                    // 調べている間に書き換わっていたら、位置がずれているので、やめる
                    if (snap.TextBuffer.CurrentSnapshot != snap && snap.TextBuffer.CurrentSnapshot.GetText() != p.Text)
                    {
                        notes.Add(p.File + ": 調べている間に書き換わったので、呼び出しを直していません");
                        continue;
                    }
                    var edits = p.Edits.Select(x => Tuple.Create(x.Start, x.Length, x.Text)).ToList();
                    if (SymbolService.ApplyEdits(snap.TextBuffer.CurrentSnapshot, edits, owner.Undo, "K-CppAssist: 呼び出しの引数を合わせる")) { done += edits.Count; files++; }
                }
                if (closed.Count > 0)
                {
                    var ctx = a.Ctx;
                    var written = await Task.Run(() =>
                    {
                        var list = new List<string>();
                        foreach (var p in closed)
                        {
                            int n = SymbolService.RewriteFile(p.File, t => SymbolScan.CallEdits(t, d, ctx, amb, oldCount, map, hasDef, new List<int>()));
                            if (n > 0) list.Add(p.File + ": " + n + " か所");
                        }
                        return list;
                    });
                    await ThreadHelper.JoinableTaskFactory.SwitchToMainThreadAsync();
                    if (written.Count > 0)
                    {
                        done += written.Count;
                        files += written.Count;
                        notes.Insert(0, "閉じていたファイルの呼び出しを書き換えました:");
                        notes.InsertRange(1, written.Select(x => "  " + x));
                    }
                }

                string label = (d.Class == null ? "" : d.Class + "::") + d.Name;
                int skipped = plans.Sum(p => p.Skipped.Count);
                if (notes.Count > 0)
                {
                    var outLines = new List<string> { "---- " + label + " の呼び出しの引数 ----" };
                    if (skipped > 0)
                        outLines.Add(a.Overloaded ? "同じ名前で引数の違う関数があるので、次の呼び出しは直していません:"
                            : "次の呼び出しは、自動では直していません(足した引数に渡す値がない、受け手の型が分からない、など):");
                    outLines.AddRange(notes.Take(MaxOutputLines));
                    if (notes.Count > MaxOutputLines) outLines.Add("  …ほか " + (notes.Count - MaxOutputLines) + " 行");
                    SymbolService.Output(outLines);
                }
                if (done == 0 && skipped == 0) return;
                var lines = new List<string>();
                if (done > 0) lines.Add((files > 1 ? files + " ファイル " : "") + done + " か所の呼び出しを、新しい引数の並びに直しました");
                if (skipped > 0) lines.Add(skipped + " か所は直していません(出力ウィンドウ)");
                if (!view.IsClosed)
                {
                    int anchor = d.Start >= 0 ? snapNow.CreateTrackingPoint(Math.Min(d.Start, snapNow.Length), PointTrackingMode.Negative).GetPosition(view.TextSnapshot) : -1;
                    SyncPreview.ShowNote(view, anchor, label + " の呼び出し", null, null, lines);
                }
                IncludeService.Status(label + " の呼び出し " + done + " か所の引数を直しました" + (skipped > 0 ? "(" + skipped + " か所は直していません。出力ウィンドウの K-CppAssist)" : ""));
            }
            catch (Exception ex) { KCppAssistPackage.Log("symbol call sync failed: " + ex); }
        }
    }
}
