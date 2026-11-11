using System;
using System.Collections.Generic;
using System.ComponentModel.Composition;
using System.Linq;
using System.Text.RegularExpressions;
using System.Threading;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Documents;
using System.Windows.Media;
using Microsoft.VisualStudio.Language.Intellisense;
using Microsoft.VisualStudio.PlatformUI;
using Microsoft.VisualStudio.Shell;
using Microsoft.VisualStudio.Text;
using Microsoft.VisualStudio.Text.Classification;
using Microsoft.VisualStudio.Text.Editor;
using Microsoft.VisualStudio.Utilities;
using Newtonsoft.Json.Linq;

namespace KHlsl.Vsix
{
    /// <summary>
    /// ホバー(クイック ヒント)。言語サーバーの khlsl/hover が返す Markdown を、エディターと同じ色で描く。
    /// コード ブロックと `インライン コード` は K-HLSL の字句解析で色を付け、見出し・太字・斜体・表・区切り線も描き分ける。
    /// (言語サーバーの textDocument/hover は、VS の標準の表示が色を付けないので、広告しない。)
    /// </summary>
    [Export(typeof(IAsyncQuickInfoSourceProvider))]
    [Name("K-HLSL hover")]
    [ContentType(KHlslContentType.Name)]
    [Order(Before = "Default Quick Info Presenter")]
    internal sealed class KHlslHoverProvider : IAsyncQuickInfoSourceProvider
    {
        [Import] internal ITextDocumentFactoryService Documents = null;
        [Import] internal IClassificationFormatMapService FormatMaps = null;

        public IAsyncQuickInfoSource TryCreateQuickInfoSource(ITextBuffer textBuffer)
        {
            return new KHlslHoverSource(textBuffer, Documents, FormatMaps);
        }
    }

    internal sealed class KHlslHoverSource : IAsyncQuickInfoSource
    {
        private readonly ITextBuffer _buffer;
        private readonly ITextDocumentFactoryService _documents;
        private readonly IClassificationFormatMapService _maps;

        public KHlslHoverSource(ITextBuffer buffer, ITextDocumentFactoryService documents, IClassificationFormatMapService maps)
        {
            _buffer = buffer; _documents = documents; _maps = maps;
        }

        public async Task<QuickInfoItem> GetQuickInfoItemAsync(IAsyncQuickInfoSession session, CancellationToken cancellationToken)
        {
            try
            {
                var snapshot = _buffer.CurrentSnapshot;
                var point = session.GetTriggerPoint(snapshot);
                if (!point.HasValue) return null;
                ITextDocument doc;
                if (!_documents.TryGetTextDocument(_buffer, out doc)) return null;
                var line = point.Value.GetContainingLine();
                int col = point.Value - line.Start;
                string uri = new Uri(doc.FilePath).AbsoluteUri;

                JToken res = await KHlslLanguageClient.RequestAsync("khlsl/hover", new
                {
                    textDocument = new { uri },
                    position = new { line = line.LineNumber, character = col }
                }).ConfigureAwait(false);
                string md = res?["contents"]?["value"]?.ToString();
                if (string.IsNullOrEmpty(md)) return null;

                // 範囲(単語)。取れなければ、カーソルの位置
                Microsoft.VisualStudio.Text.Span span = new Microsoft.VisualStudio.Text.Span(point.Value.Position, 0);
                try
                {
                    var r = res["range"];
                    int s = snapshot.GetLineFromLineNumber((int)r["start"]["line"]).Start + (int)r["start"]["character"];
                    int e = snapshot.GetLineFromLineNumber((int)r["end"]["line"]).Start + (int)r["end"]["character"];
                    if (e > s && e <= snapshot.Length) span = new Microsoft.VisualStudio.Text.Span(s, e - s);
                }
                catch (Exception) { }

                await ThreadHelper.JoinableTaskFactory.SwitchToMainThreadAsync(cancellationToken);
                var tracking = snapshot.CreateTrackingSpan(span, SpanTrackingMode.EdgeInclusive);
                return new QuickInfoItem(tracking, new HoverRenderer(_buffer, _maps).Render(md));
            }
            catch (OperationCanceledException) { throw; }
            catch (Exception ex)
            {
                KHlslPackage.Log("hover failed: " + ex.Message);
                return null;
            }
        }

        public void Dispose() { }
    }

    /// <summary>Markdown を WPF の部品にする。</summary>
    internal sealed class HoverRenderer
    {
        private static readonly Regex Inline = new Regex(@"(`[^`\n]+`)|(\*\*[^*\n]+\*\*)|(\*[^*\n]+\*)", RegexOptions.Compiled);
        private static readonly Brush Muted = Freeze(new SolidColorBrush(Color.FromArgb(0xB0, 0x80, 0x80, 0x80)));
        private static readonly Brush CodeBg = Freeze(new SolidColorBrush(Color.FromArgb(0x1C, 0x80, 0x80, 0x80)));
        private static readonly Brush Accent = Freeze(new SolidColorBrush(Color.FromRgb(0x4C, 0x8B, 0xF5)));
        private static readonly Brush Rule = Freeze(new SolidColorBrush(Color.FromArgb(0x40, 0x80, 0x80, 0x80)));

        private readonly IClassificationFormatMap _map;
        private readonly KHlslClassifier _classifier;
        private readonly FontFamily _codeFont;
        private readonly double _codeSize;

        public HoverRenderer(ITextBuffer buffer, IClassificationFormatMapService maps)
        {
            _map = maps.GetClassificationFormatMap("text");
            KHlslClassifier c;
            buffer.Properties.TryGetProperty(typeof(KHlslClassifier), out c);
            _classifier = c;
            var d = _map.DefaultTextProperties;
            _codeFont = d.Typeface != null ? d.Typeface.FontFamily : new FontFamily("Consolas");
            _codeSize = Math.Min(d.FontRenderingEmSize > 0 ? d.FontRenderingEmSize : 13, 14);
        }

        private static Brush Freeze(Brush b) { b.Freeze(); return b; }

        public UIElement Render(string md)
        {
            var panel = new StackPanel { MaxWidth = 560 };
            var lines = md.Replace("\r", "").Split('\n');
            var para = new List<string>();
            Action flush = () =>
            {
                if (para.Count == 0) return;
                panel.Children.Add(Paragraph(para));
                para = new List<string>();
            };
            for (int i = 0; i < lines.Length; i++)
            {
                string l = lines[i];
                if (l.StartsWith("```", StringComparison.Ordinal))
                {
                    flush();
                    var code = new List<string>();
                    for (i++; i < lines.Length && !lines[i].StartsWith("```", StringComparison.Ordinal); i++) code.Add(lines[i]);
                    panel.Children.Add(CodeBlock(string.Join("\n", code)));
                }
                else if (l.Trim() == "---")
                {
                    flush();
                    panel.Children.Add(new Border { Height = 1, Background = Rule, Margin = new Thickness(0, 6, 0, 6) });
                }
                else if (l.Trim().Length == 0) flush();
                else para.Add(l);
            }
            flush();
            return panel;
        }

        private UIElement Paragraph(List<string> lines)
        {
            if (lines.All(x => x.TrimStart().StartsWith("|", StringComparison.Ordinal))) return Table(lines);
            var tb = NewText(false);
            tb.Margin = new Thickness(0, 2, 0, 4);
            var h = Regex.Match(lines[0], @"^(#{1,6})\s+(.*)$");
            if (h.Success)
            {
                tb.FontWeight = FontWeights.SemiBold;
                AddInlines(tb, h.Groups[2].Value);
                return tb;
            }
            for (int i = 0; i < lines.Count; i++)
            {
                if (i > 0) tb.Inlines.Add(new LineBreak());
                string s = lines[i];
                var b = Regex.Match(s, @"^\s*[-*]\s+(.*)$");
                if (b.Success) { tb.Inlines.Add(new Run("•  ") { Foreground = Muted }); s = b.Groups[1].Value; }
                AddInlines(tb, s);
            }
            return tb;
        }

        private UIElement Table(List<string> lines)
        {
            var rows = new List<string[]>();
            foreach (var l in lines)
            {
                string t = l.Trim();
                if (t.StartsWith("|", StringComparison.Ordinal)) t = t.Substring(1);
                if (t.EndsWith("|", StringComparison.Ordinal)) t = t.Substring(0, t.Length - 1);
                var cells = t.Split('|').Select(x => x.Trim()).ToArray();
                if (cells.All(c => Regex.IsMatch(c, @"^:?-{2,}:?$"))) continue;   // |---|---| の行
                rows.Add(cells);
            }
            var grid = new Grid { Margin = new Thickness(0, 2, 0, 6) };
            int cols = rows.Count == 0 ? 0 : rows.Max(r => r.Length);
            for (int c = 0; c < cols; c++) grid.ColumnDefinitions.Add(new ColumnDefinition { Width = GridLength.Auto });
            for (int r = 0; r < rows.Count; r++)
            {
                grid.RowDefinitions.Add(new RowDefinition { Height = GridLength.Auto });
                for (int c = 0; c < rows[r].Length; c++)
                {
                    var tb = NewText(false);
                    tb.Margin = new Thickness(0, 0, 14, 1);
                    if (r == 0) { tb.FontWeight = FontWeights.SemiBold; tb.Foreground = Muted; }
                    AddInlines(tb, rows[r][c]);
                    Grid.SetRow(tb, r); Grid.SetColumn(tb, c);
                    grid.Children.Add(tb);
                }
            }
            return grid;
        }

        private TextBlock NewText(bool code)
        {
            var tb = new TextBlock { TextWrapping = TextWrapping.Wrap };
            tb.SetResourceReference(TextBlock.ForegroundProperty, EnvironmentColors.ToolTipTextBrushKey);
            if (code) { tb.FontFamily = _codeFont; tb.FontSize = _codeSize; }
            return tb;
        }

        private UIElement CodeBlock(string code)
        {
            var tb = NewText(true);
            AddColored(tb.Inlines, code);
            return new Border
            {
                Background = CodeBg,
                BorderBrush = Accent,
                BorderThickness = new Thickness(3, 0, 0, 0),
                CornerRadius = new CornerRadius(3),
                Padding = new Thickness(9, 6, 9, 6),
                Margin = new Thickness(0, 2, 0, 6),
                Child = tb
            };
        }

        private void AddInlines(TextBlock tb, string s)
        {
            int pos = 0;
            foreach (Match m in Inline.Matches(s))
            {
                if (m.Index > pos) tb.Inlines.Add(new Run(s.Substring(pos, m.Index - pos)));
                if (m.Groups[1].Success)
                {
                    var span = new System.Windows.Documents.Span { FontFamily = _codeFont, FontSize = _codeSize, Background = CodeBg };
                    AddColored(span.Inlines, m.Value.Substring(1, m.Length - 2));
                    tb.Inlines.Add(span);
                }
                else if (m.Groups[2].Success) tb.Inlines.Add(new Run(m.Value.Substring(2, m.Length - 4)) { FontWeight = FontWeights.SemiBold });
                else tb.Inlines.Add(new Run(m.Value.Substring(1, m.Length - 2)) { FontStyle = FontStyles.Italic, Foreground = Muted });
                pos = m.Index + m.Length;
            }
            if (pos < s.Length) tb.Inlines.Add(new Run(s.Substring(pos)));
        }

        /// <summary>K-HLSL の字句解析で、エディターと同じ色の Run を並べる。</summary>
        private void AddColored(InlineCollection inlines, string code)
        {
            List<Tok> toks;
            try { toks = KHlslLexer.Lex(code, Lexicon.Instance); }
            catch (Exception) { inlines.Add(new Run(code)); return; }
            int pos = 0;
            foreach (var t in toks.OrderBy(x => x.Start))
            {
                if (t.Start < pos || t.Length <= 0) continue;
                if (t.Start > pos) inlines.Add(new Run(code.Substring(pos, t.Start - pos)));
                var run = new Run(code.Substring(t.Start, t.Length));
                var type = _classifier != null ? _classifier.TypeOf(t.Kind) : null;
                if (type != null)
                {
                    var p = _map.GetTextProperties(type);
                    if (!p.ForegroundBrushEmpty) run.Foreground = p.ForegroundBrush;
                    if (!p.BoldEmpty && p.Bold) run.FontWeight = FontWeights.Bold;
                    if (!p.ItalicEmpty && p.Italic) run.FontStyle = FontStyles.Italic;
                }
                inlines.Add(run);
                pos = t.Start + t.Length;
            }
            if (pos < code.Length) inlines.Add(new Run(code.Substring(pos)));
        }
    }
}
