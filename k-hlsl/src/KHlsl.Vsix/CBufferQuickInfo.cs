using System;
using System.ComponentModel.Composition;
using System.IO;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using Microsoft.VisualStudio.Language.Intellisense;
using Microsoft.VisualStudio.PlatformUI;
using Microsoft.VisualStudio.Shell;
using Microsoft.VisualStudio.Text;
using Microsoft.VisualStudio.Utilities;
using Newtonsoft.Json.Linq;

namespace KHlsl.Vsix
{
    /// <summary>
    /// cbuffer・ConstantBuffer&lt;T&gt;・struct の名前にカーソルを置いたとき、ホバーにレジスタの図を出す。
    /// 言語サーバーの khlsl/cbuffers で、レイアウトを計算してもらう。
    /// </summary>
    [Export(typeof(IAsyncQuickInfoSourceProvider))]
    [Name("K-HLSL cbuffer quick info")]
    [ContentType(KHlslContentType.Name)]
    [Order(Before = "Default Quick Info Presenter")]
    internal sealed class CBufferQuickInfoProvider : IAsyncQuickInfoSourceProvider
    {
        [Import]
        internal ITextDocumentFactoryService Documents = null;

        public IAsyncQuickInfoSource TryCreateQuickInfoSource(ITextBuffer textBuffer)
        {
            return new CBufferQuickInfoSource(textBuffer, Documents);
        }
    }

    internal sealed class CBufferQuickInfoSource : IAsyncQuickInfoSource
    {
        private readonly ITextBuffer _buffer;
        private readonly ITextDocumentFactoryService _documents;

        public CBufferQuickInfoSource(ITextBuffer buffer, ITextDocumentFactoryService documents)
        {
            _buffer = buffer;
            _documents = documents;
        }

        public async Task<QuickInfoItem> GetQuickInfoItemAsync(IAsyncQuickInfoSession session, CancellationToken cancellationToken)
        {
            try
            {
                var snapshot = _buffer.CurrentSnapshot;
                var point = session.GetTriggerPoint(snapshot);
                if (!point.HasValue) return null;

                // カーソル位置の識別子を取る
                var line = point.Value.GetContainingLine();
                string text = line.GetText();
                int col = point.Value - line.Start;
                if (col >= text.Length || !IsIdent(text[col])) return null;
                int s = col, e = col;
                while (s > 0 && IsIdent(text[s - 1])) s--;
                while (e < text.Length && IsIdent(text[e])) e++;
                string word = text.Substring(s, e - s);
                if (word.Length == 0 || char.IsDigit(word[0])) return null;

                ITextDocument doc;
                if (!_documents.TryGetTextDocument(_buffer, out doc)) return null;

                // 軽い下調べ: ファイルに cbuffer / ConstantBuffer / struct が 1 つもなければ、何も聞かない
                string all = snapshot.GetText();
                if (all.IndexOf("cbuffer", StringComparison.Ordinal) < 0 && all.IndexOf("tbuffer", StringComparison.Ordinal) < 0
                    && all.IndexOf("ConstantBuffer", StringComparison.Ordinal) < 0 && all.IndexOf("struct", StringComparison.Ordinal) < 0)
                    return null;

                JToken result = await KHlslLanguageClient.RequestCBuffersAsync(doc.FilePath, true);
                var blocks = result?["blocks"] as JArray;
                if (blocks == null) return null;
                JObject block = null;
                foreach (JObject b in blocks)
                    if ((string)b["name"] == word && (string)b["kind"] != "struct") { block = b; break; }
                if (block == null)
                    foreach (JObject b in blocks)
                        if ((string)b["name"] == word && (string)b["kind"] == "struct") { block = b; break; }
                if (block == null) return null;

                await ThreadHelper.JoinableTaskFactory.SwitchToMainThreadAsync(cancellationToken);
                var span = snapshot.CreateTrackingSpan(line.Start + s, e - s, SpanTrackingMode.EdgeInclusive);
                return new QuickInfoItem(span, MakeContent(block));
            }
            catch (OperationCanceledException) { throw; }
            catch (Exception ex)
            {
                KHlslPackage.Log("quickinfo failed: " + ex.Message);
                return null;
            }
        }

        private static bool IsIdent(char c) { return char.IsLetterOrDigit(c) || c == '_'; }

        // ホバーは小さめの字で、図と 1 行の説明だけにする(オフセットの細かい値は、升目の上にカーソルを置くと出る)
        private static object MakeContent(JObject b)
        {
            int size = (int)b["size"], padded = (int)b["paddedSize"], wasted = (int)b["wasted"];
            string summary = (string)b["title"] + "  " + size + " バイト(" + padded / 16 + " レジスタ)・隙間 " + wasted + " バイト";
            var r = b["reorder"] as JObject;
            if (r != null) summary += "・並べ替えで " + (int)r["saved"] + " バイト減";
            var panel = new StackPanel();
            panel.Children.Add(new TextBlock { Text = summary, FontSize = 11, FontWeight = FontWeights.SemiBold, Foreground = null, Margin = new Thickness(0, 0, 0, 4), TextWrapping = TextWrapping.Wrap, MaxWidth = 420 });
            var grid = CBufferGrid.Build(b, 18, 22, 9, EnvironmentColors.ToolTipTextBrushKey, null);
            panel.Children.Add(grid);
            var problems = (JArray)b["problems"];
            if (problems.Count > 0)
                panel.Children.Add(new TextBlock { Text = "⚠ " + string.Join(" / ", problems.Select(x => (string)x)), FontSize = 10, TextWrapping = TextWrapping.Wrap, MaxWidth = 420, Margin = new Thickness(0, 4, 0, 0) });
            return panel;
        }

        public void Dispose() { }
    }
}
