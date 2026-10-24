using System;
using System.ComponentModel.Composition;
using System.Threading;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Documents;
using Microsoft.VisualStudio.Language.Intellisense;
using Microsoft.VisualStudio.PlatformUI;
using Microsoft.VisualStudio.Shell;
using Microsoft.VisualStudio.Text;
using Microsoft.VisualStudio.Utilities;
using Newtonsoft.Json.Linq;

namespace KHlsl.Vsix
{
    /// <summary>
    /// C++ の struct / class の名前にカーソルを置いたとき、標準のホバー(メモリ レイアウトなど)の下に、
    /// 「HLSL の cbuffer と比べる」リンクを足す。クリックすると、K-HLSL のツール ウィンドウで比較が開く。
    /// </summary>
    [Export(typeof(IAsyncQuickInfoSourceProvider))]
    [Name("K-HLSL C++ struct compare link")]
    [ContentType("C/C++")]
    [Order(After = "Default Quick Info Presenter")]
    internal sealed class CppQuickInfoProvider : IAsyncQuickInfoSourceProvider
    {
        [Import]
        internal ITextDocumentFactoryService Documents = null;

        public IAsyncQuickInfoSource TryCreateQuickInfoSource(ITextBuffer textBuffer)
        {
            return new CppQuickInfoSource(textBuffer, Documents);
        }
    }

    internal sealed class CppQuickInfoSource : IAsyncQuickInfoSource
    {
        private readonly ITextBuffer _buffer;
        private readonly ITextDocumentFactoryService _documents;

        public CppQuickInfoSource(ITextBuffer buffer, ITextDocumentFactoryService documents)
        {
            _buffer = buffer;
            _documents = documents;
        }

        public async Task<QuickInfoItem> GetQuickInfoItemAsync(IAsyncQuickInfoSession session, CancellationToken cancellationToken)
        {
            try
            {
                // HLSL の言語サーバーが動いていなければ(HLSL を一度も開いていなければ)、何も出さない
                if (!KHlslLanguageClient.IsConnected) return null;

                var snapshot = _buffer.CurrentSnapshot;
                var point = session.GetTriggerPoint(snapshot);
                if (!point.HasValue) return null;
                var line = point.Value.GetContainingLine();
                string lineText = line.GetText();
                int col = point.Value - line.Start;
                if (col >= lineText.Length || !IsIdent(lineText[col])) return null;
                int s = col, e = col;
                while (s > 0 && IsIdent(lineText[s - 1])) s--;
                while (e < lineText.Length && IsIdent(lineText[e])) e++;
                string word = lineText.Substring(s, e - s);
                if (word.Length == 0 || char.IsDigit(word[0])) return null;

                ITextDocument doc;
                if (!_documents.TryGetTextDocument(_buffer, out doc)) return null;

                string all = snapshot.GetText();
                if (all.IndexOf("struct", StringComparison.Ordinal) < 0 && all.IndexOf("class", StringComparison.Ordinal) < 0) return null;

                string path = doc.FilePath;
                int lineNo = line.LineNumber;
                var probe = await KHlslLanguageClient.RequestAsync("khlsl/cppstruct", new { cppPath = path, cppText = all, word, line = lineNo });
                if (probe == null || probe["found"] == null || !(bool)probe["found"]) return null;
                string name = (string)probe["name"];
                int size = (int)probe["size"];

                await ThreadHelper.JoinableTaskFactory.SwitchToMainThreadAsync(cancellationToken);
                var span = snapshot.CreateTrackingSpan(line.Start + s, e - s, SpanTrackingMode.EdgeInclusive);
                return new QuickInfoItem(span, MakeLink(path, all, name, size));
            }
            catch (OperationCanceledException) { throw; }
            catch (Exception ex)
            {
                KHlslPackage.Log("cpp quickinfo failed: " + ex.Message);
                return null;
            }
        }

        private static bool IsIdent(char c) { return char.IsLetterOrDigit(c) || c == '_'; }

        private static object MakeLink(string path, string text, string name, int size)
        {
            var link = new Hyperlink(new Run("HLSL の cbuffer と比べる"));
            link.Click += (s, e) =>
            {
                var package = KHlslPackage.Current;
                if (package != null) package.ShowCompare(path, text, name);
            };
            var block = new TextBlock { FontSize = 11, TextWrapping = TextWrapping.Wrap, MaxWidth = 420 };
            block.Inlines.Add(new Run("K-HLSL: " + name + "(" + size + " バイト)を "));
            block.Inlines.Add(link);
            block.Inlines.Add(new Run(" ▸"));
            return block;
        }

        public void Dispose() { }
    }
}
