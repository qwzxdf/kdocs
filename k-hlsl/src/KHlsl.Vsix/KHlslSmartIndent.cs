using System;
using System.ComponentModel.Composition;
using Microsoft.VisualStudio.Text;
using Microsoft.VisualStudio.Text.Editor;
using Microsoft.VisualStudio.Utilities;
using KHlsl.Server;

namespace KHlsl.Vsix
{
    /// <summary>Enter で入る新しい行の字下げ。if / for の本体、{ の中、case の中を、整形(Ctrl+K, D)と同じ規則で決める。</summary>
    [Export(typeof(ISmartIndentProvider))]
    [ContentType(KHlslContentType.Name)]
    internal sealed class KHlslSmartIndentProvider : ISmartIndentProvider
    {
        public ISmartIndent CreateSmartIndent(ITextView textView) { return new KHlslSmartIndent(textView); }
    }

    internal sealed class KHlslSmartIndent : ISmartIndent
    {
        private readonly ITextView _view;

        public KHlslSmartIndent(ITextView view) { _view = view; }

        public int? GetDesiredIndentation(ITextSnapshotLine line)
        {
            try
            {
                int tab = _view.Options.GetOptionValue(DefaultOptions.TabSizeOptionId);
                string before = line.Snapshot.GetText(0, line.Start.Position);
                if (before.Length == 0) return 0;
                return HlslFormatter.IndentForNewLine(before, line.GetText(), tab);
            }
            catch (Exception) { return null; }
        }

        public void Dispose() { }
    }
}
