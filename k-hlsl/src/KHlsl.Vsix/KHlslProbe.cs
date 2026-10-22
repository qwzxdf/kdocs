using System;
using System.ComponentModel.Composition;
using System.IO;
using System.Linq;
using System.Text;
using System.Windows.Threading;
using Microsoft.VisualStudio.Text;
using Microsoft.VisualStudio.Text.Classification;
using Microsoft.VisualStudio.Text.Editor;
using Microsoft.VisualStudio.Text.Tagging;
using Microsoft.VisualStudio.Utilities;

namespace KHlsl.Vsix
{
    /// <summary>
    /// 調査用(一時的)。C/C++ のファイルを開いたとき、各トークンに付いている分類名を
    /// %LOCALAPPDATA%\K-HLSL\probe-cpp.log に書き出す。Viasfora のタグも含める。
    /// </summary>
    [Export(typeof(IWpfTextViewCreationListener))]
    [ContentType("C/C++")]
    [TextViewRole(PredefinedTextViewRoles.Document)]
    internal sealed class KHlslProbe : IWpfTextViewCreationListener
    {
        [Import] internal IClassifierAggregatorService Classifiers { get; set; }
        [Import] internal IViewTagAggregatorFactoryService TagAggregators { get; set; }

        public void TextViewCreated(IWpfTextView textView)
        {
            var timer = new DispatcherTimer { Interval = TimeSpan.FromSeconds(6) };
            timer.Tick += (s, e) =>
            {
                timer.Stop();
                try { Dump(textView); } catch (Exception ex) { Write("probe failed: " + ex); }
            };
            timer.Start();
        }

        private static void Write(string text)
        {
            string dir = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "K-HLSL");
            Directory.CreateDirectory(dir);
            File.AppendAllText(Path.Combine(dir, "probe-cpp.log"), text + Environment.NewLine, Encoding.UTF8);
        }

        private void Dump(IWpfTextView view)
        {
            var snap = view.TextSnapshot;
            var all = new SnapshotSpan(snap, 0, Math.Min(snap.Length, 6000));
            Write("==== content type: " + view.TextBuffer.ContentType.TypeName);
            var classifier = Classifiers.GetClassifier(view.TextBuffer);
            foreach (var cs in classifier.GetClassificationSpans(all))
            {
                string text = cs.Span.GetText().Replace("\r", "").Replace("\n", "<LF>").Replace("\t", "<TAB>");
                if (text.Trim().Length == 0) continue;
                Write("C  [" + cs.Span.Start.Position + "] " + (text.Length > 30 ? text.Substring(0, 30) : text) + "  =>  " + cs.ClassificationType.Classification);
            }
            var agg = TagAggregators.CreateTagAggregator<IClassificationTag>(view);
            foreach (var t in agg.GetTags(all))
            {
                foreach (var sp in t.Span.GetSpans(snap))
                {
                    string text = sp.GetText().Replace("\r", "").Replace("\n", "<LF>").Replace("\t", "<TAB>");
                    if (text.Trim().Length == 0) continue;
                    Write("T  [" + sp.Start.Position + "] " + (text.Length > 30 ? text.Substring(0, 30) : text) + "  =>  " + t.Tag.ClassificationType.Classification);
                }
            }
            Write("==== end");
        }
    }
}
