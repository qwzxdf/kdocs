using System;
using System.Collections.Generic;
using System.ComponentModel.Composition;
using System.IO;
using System.Linq;
using System.Threading.Tasks;
using System.Windows.Threading;
using Microsoft.VisualStudio.Shell;
using Microsoft.VisualStudio.Text;
using Microsoft.VisualStudio.Text.Editor;
using Microsoft.VisualStudio.Text.Operations;
using Microsoft.VisualStudio.Utilities;

namespace KCppAssist
{
    /// <summary>
    /// switch (列挙型の値) { と打って改行したとき、本体が空なら、enum の値ごとの case(break つき)と default: を自動で入れる。
    /// enum の型が決められない(整数の switch など)ときは、何もしない。
    /// </summary>
    [Export(typeof(IWpfTextViewCreationListener))]
    [ContentType("C/C++")]
    [TextViewRole(PredefinedTextViewRoles.Document)]
    internal sealed class AutoSwitchListener : IWpfTextViewCreationListener
    {
        [Import] internal ITextDocumentFactoryService Documents { get; set; }
        [Import] internal ITextUndoHistoryRegistry Undo { get; set; }

        public void TextViewCreated(IWpfTextView view)
        {
            try { new AutoSwitchSession(view, this); }
            catch (Exception ex) { KCppAssistPackage.Log("auto switch attach failed: " + ex); }
        }
    }

    internal sealed class AutoSwitchSession
    {
        private readonly IWpfTextView view;
        private readonly AutoSwitchListener owner;
        private readonly DispatcherTimer timer;
        private string path;
        private bool busy;
        private int lastVersion = -1;       // 同じ版では、2 回試さない
        // 自動で case を入れた switch の「{」。あとで本体を消されても(Ctrl+Z も含めて)、同じ switch には 2 度と入れない
        private readonly List<ITrackingPoint> handled = new List<ITrackingPoint>();

        public AutoSwitchSession(IWpfTextView view, AutoSwitchListener owner)
        {
            this.view = view;
            this.owner = owner;
            ITextDocument doc;
            if (owner.Documents.TryGetTextDocument(view.TextBuffer, out doc)) path = doc.FilePath;
            timer = new DispatcherTimer(DispatcherPriority.ApplicationIdle, view.VisualElement.Dispatcher) { Interval = TimeSpan.FromMilliseconds(300) };
            timer.Tick += OnTick;
            view.TextBuffer.Changed += OnChanged;
            view.Closed += OnClosed;
        }

        private void OnClosed(object sender, EventArgs e)
        {
            timer.Stop();
            timer.Tick -= OnTick;
            view.TextBuffer.Changed -= OnChanged;
            view.Closed -= OnClosed;
        }

        private static bool Enabled { get { var o = IncludeService.Options; return o != null && o.AutoSwitch; } }

        private void OnChanged(object sender, TextContentChangedEventArgs e)
        {
            try
            {
                if (!Enabled) return;
                string tag = e.EditTag as string;
                if (tag != null && tag.StartsWith("K-CppAssist", StringComparison.Ordinal)) return;        // 拡張が自分で書いた
                bool trigger = false;
                foreach (var c in e.Changes)
                    if (c.NewText.IndexOf('\n') >= 0 || c.NewText.IndexOf('{') >= 0) { trigger = true; break; }
                if (!trigger) return;
                timer.Stop();
                timer.Start();
            }
            catch (Exception ex) { KCppAssistPackage.Log("auto switch OnChanged failed: " + ex.Message); }
        }

        private async void OnTick(object sender, EventArgs e)
        {
            timer.Stop();
            if (busy || !Enabled || path == null || !view.HasAggregateFocus) return;
            busy = true;
            try { await TryAsync(); }
            catch (Exception ex) { KCppAssistPackage.Log("auto switch failed: " + ex); }
            finally { busy = false; }
        }

        private async Task TryAsync()
        {
            ITextSnapshot snap = view.TextSnapshot;
            if (snap.Version.VersionNumber == lastVersion) return;
            lastVersion = snap.Version.VersionNumber;
            int caret = view.Caret.Position.BufferPosition.TranslateTo(snap, PointTrackingMode.Positive).Position;
            string text = snap.GetText();
            int open;
            if (!SwitchGen.BodyEmptyAt(text, caret, out open)) return;
            if (handled.Any(tp => tp.GetPosition(snap) == open)) return;

            string file = path;
            var enums = await Task.Run(() => SwitchEnums.Gather(file, text));
            await ThreadHelper.JoinableTaskFactory.SwitchToMainThreadAsync();
            if (view.TextSnapshot.Version.VersionNumber != snap.Version.VersionNumber) return;     // 調べている間に、打たれた
            string eol = CppText.Eol(text);
            string why;
            var plan = SwitchGen.Make(text, caret, enums, eol, out why, true);
            if (plan == null) return;
            var edits = new List<Tuple<int, int, string>> { Tuple.Create(plan.Position, plan.Length, plan.Text) };
            if (SymbolService.ApplyEdits(snap, edits, owner.Undo, "K-Cpp: switch の case を入れる"))
            {
                handled.Add(snap.CreateTrackingPoint(open, PointTrackingMode.Negative));
                if (handled.Count > 100) handled.RemoveAt(0);
                KCppAssistPackage.Log("auto switch: " + plan.EnumName + " " + plan.Added.Count + " case(s)" + (plan.AddedDefault ? " + default" : ""));
            }
        }
    }

    /// <summary>switch の enum の定義を集める。このファイルと、#include をたどった先(2 段まで)から。</summary>
    internal static class SwitchEnums
    {
        public static List<SwitchGen.EnumDef> Gather(string path, string text)
        {
            var enums = SwitchGen.ParseEnums(text);
            string root = IncludeService.RootFor(path);
            var seen = new HashSet<string>(StringComparer.OrdinalIgnoreCase) { path };
            var queue = new List<Tuple<string, string, int>> { Tuple.Create(path, text, 0) };
            for (int qi = 0; qi < queue.Count && qi < 60; qi++)
            {
                var cur = queue[qi];
                if (cur.Item3 >= 2) continue;
                foreach (var inc in IncludeTidy.Parse(cur.Item2).Where(i => !i.Angle))
                {
                    string file = KCppAssistPackage.ProvidedCache.Resolve(inc, cur.Item1, root);
                    if (file == null || !seen.Add(file)) continue;
                    string t;
                    try { t = File.ReadAllText(file); } catch (Exception) { continue; }
                    enums.AddRange(SwitchGen.ParseEnums(t));
                    queue.Add(Tuple.Create(file, t, cur.Item3 + 1));
                }
            }
            return enums;
        }
    }
}
