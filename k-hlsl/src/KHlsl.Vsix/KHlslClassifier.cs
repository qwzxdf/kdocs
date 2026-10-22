using System;
using System.Collections.Generic;
using System.ComponentModel.Composition;
using System.Windows.Media;
using Microsoft.VisualStudio.PlatformUI;
using Microsoft.VisualStudio.Shell;
using Microsoft.VisualStudio.Text;
using Microsoft.VisualStudio.Text.Classification;
using Microsoft.VisualStudio.Utilities;

namespace KHlsl.Vsix
{
    /// <summary>K-HLSL 専用の分類名。テーマが色を付けない物だけ、ここで明示的に色を決める。</summary>
    internal static class KHlslClassNames
    {
        public const string Function = "khlsl.function";
        public const string Number = "khlsl.number";
        public const string Semantic = "khlsl.semantic";
        public const string Attribute = "khlsl.attribute";
        public const string Constant = "khlsl.constant";
        public const string Macro = "khlsl.macro";
    }

    internal static class KHlslClassDefinitions
    {
        [Export] [Name(KHlslClassNames.Function)] [BaseDefinition("identifier")] internal static ClassificationTypeDefinition Function;
        [Export] [Name(KHlslClassNames.Number)] [BaseDefinition("number")] internal static ClassificationTypeDefinition Number;
        [Export] [Name(KHlslClassNames.Semantic)] [BaseDefinition("identifier")] internal static ClassificationTypeDefinition Semantic;
        [Export] [Name(KHlslClassNames.Attribute)] [BaseDefinition("identifier")] internal static ClassificationTypeDefinition Attribute;
        [Export] [Name(KHlslClassNames.Constant)] [BaseDefinition("identifier")] internal static ClassificationTypeDefinition Constant;
        [Export] [Name(KHlslClassNames.Macro)] [BaseDefinition("identifier")] internal static ClassificationTypeDefinition Macro;
    }

    internal static class KHlslPalette
    {
        public static bool IsDark()
        {
            try
            {
                var c = VSColorTheme.GetThemedColor(EnvironmentColors.ToolWindowBackgroundColorKey);
                return (0.299 * c.R + 0.587 * c.G + 0.114 * c.B) < 128;
            }
            catch (Exception) { return true; }
        }

        // 暗いテーマは VS Code の Dark+、明るいテーマは VS 標準(C++)に近い色
        public static Color Pick(string dark, string light)
        {
            return (Color)ColorConverter.ConvertFromString(IsDark() ? dark : light);
        }
    }

    internal abstract class KHlslFormat : ClassificationFormatDefinition
    {
        protected KHlslFormat(string display, string dark, string light)
        {
            DisplayName = display;
            ForegroundColor = KHlslPalette.Pick(dark, light);
        }
    }

    [Export(typeof(EditorFormatDefinition))] [ClassificationType(ClassificationTypeNames = KHlslClassNames.Function)]
    [Name("khlsl.function.format")] [UserVisible(true)] [Order(After = Priority.Default)]
    internal sealed class FunctionFormat : KHlslFormat { public FunctionFormat() : base("K-HLSL 関数", "#DCDCAA", "#74531F") { } }

    [Export(typeof(EditorFormatDefinition))] [ClassificationType(ClassificationTypeNames = KHlslClassNames.Number)]
    [Name("khlsl.number.format")] [UserVisible(true)] [Order(After = Priority.Default)]
    internal sealed class NumberFormat : KHlslFormat { public NumberFormat() : base("K-HLSL 数値", "#B5CEA8", "#098658") { } }

    [Export(typeof(EditorFormatDefinition))] [ClassificationType(ClassificationTypeNames = KHlslClassNames.Semantic)]
    [Name("khlsl.semantic.format")] [UserVisible(true)] [Order(After = Priority.Default)]
    internal sealed class SemanticFormat : KHlslFormat { public SemanticFormat() : base("K-HLSL セマンティクス", "#9CDCFE", "#1F377F") { } }

    [Export(typeof(EditorFormatDefinition))] [ClassificationType(ClassificationTypeNames = KHlslClassNames.Attribute)]
    [Name("khlsl.attribute.format")] [UserVisible(true)] [Order(After = Priority.Default)]
    internal sealed class AttributeFormat : KHlslFormat { public AttributeFormat() : base("K-HLSL 属性", "#4EC9B0", "#2B91AF") { } }

    [Export(typeof(EditorFormatDefinition))] [ClassificationType(ClassificationTypeNames = KHlslClassNames.Constant)]
    [Name("khlsl.constant.format")] [UserVisible(true)] [Order(After = Priority.Default)]
    internal sealed class ConstantFormat : KHlslFormat { public ConstantFormat() : base("K-HLSL 定数・列挙値", "#B8D7A3", "#6F008A") { } }

    [Export(typeof(EditorFormatDefinition))] [ClassificationType(ClassificationTypeNames = KHlslClassNames.Macro)]
    [Name("khlsl.macro.format")] [UserVisible(true)] [Order(After = Priority.Default)]
    internal sealed class MacroFormat : KHlslFormat { public MacroFormat() : base("K-HLSL マクロ", "#BD63C5", "#6F008A") { } }

    [Export(typeof(IClassifierProvider))]
    [ContentType(KHlslContentType.Name)]
    [Name("K-HLSL classifier")]
    internal sealed class KHlslClassifierProvider : IClassifierProvider
    {
        [Import] internal IClassificationTypeRegistryService Registry { get; set; }

        public IClassifier GetClassifier(ITextBuffer buffer)
        {
            return buffer.Properties.GetOrCreateSingletonProperty(() => new KHlslClassifier(buffer, Registry));
        }
    }

    internal sealed class KHlslClassifier : IClassifier
    {
        private readonly ITextBuffer _buffer;
        private readonly Dictionary<Tk, IClassificationType> _types = new Dictionary<Tk, IClassificationType>();
        private readonly object _gate = new object();
        private ITextSnapshot _snapshot;
        private List<Tok> _tokens = new List<Tok>();

        public event EventHandler<ClassificationChangedEventArgs> ClassificationChanged;

        public KHlslClassifier(ITextBuffer buffer, IClassificationTypeRegistryService registry)
        {
            _buffer = buffer;
            // テーマ(One Dark Pro など)が色を決める標準の分類名を、上から順に探して使う
            Func<string[], IClassificationType> get = names =>
            {
                foreach (var n in names)
                {
                    var t = registry.GetClassificationType(n);
                    if (t != null) return t;
                }
                return registry.GetClassificationType("identifier");
            };
            _types[Tk.Comment] = get(new[] { "comment" });
            _types[Tk.String] = get(new[] { "string" });
            _types[Tk.Number] = get(new[] { KHlslClassNames.Number, "number" });
            _types[Tk.Preprocessor] = get(new[] { "preprocessor keyword", "keyword" });
            _types[Tk.Keyword] = get(new[] { "keyword" });
            _types[Tk.Control] = get(new[] { "keyword - control", "keyword" });
            _types[Tk.Type] = get(new[] { "class name", "type" });
            _types[Tk.Function] = get(new[] { KHlslClassNames.Function, "identifier" });
            _types[Tk.Semantic] = get(new[] { KHlslClassNames.Semantic, "identifier" });
            _types[Tk.Attribute] = get(new[] { KHlslClassNames.Attribute, "identifier" });
            _types[Tk.Constant] = get(new[] { KHlslClassNames.Constant, "identifier" });
            _types[Tk.Macro] = get(new[] { KHlslClassNames.Macro, "identifier" });
            buffer.Changed += OnChanged;
        }

        private void OnChanged(object sender, TextContentChangedEventArgs e)
        {
            var snap = e.After;
            var h = ClassificationChanged;
            if (h != null) h(this, new ClassificationChangedEventArgs(new SnapshotSpan(snap, 0, snap.Length)));
        }

        private List<Tok> TokensFor(ITextSnapshot snap)
        {
            lock (_gate)
            {
                if (_snapshot != snap)
                {
                    _tokens = KHlslLexer.Lex(snap.GetText(), Lexicon.Instance);
                    _snapshot = snap;
                }
                return _tokens;
            }
        }

        public IList<ClassificationSpan> GetClassificationSpans(SnapshotSpan span)
        {
            var result = new List<ClassificationSpan>();
            var toks = TokensFor(span.Snapshot);
            int lo = 0, hi = toks.Count;
            while (lo < hi)
            {
                int mid = (lo + hi) / 2;
                if (toks[mid].Start + toks[mid].Length <= span.Start) lo = mid + 1; else hi = mid;
            }
            for (int i = lo; i < toks.Count && toks[i].Start < span.End; i++)
            {
                IClassificationType t;
                if (!_types.TryGetValue(toks[i].Kind, out t) || t == null) continue;
                int s = Math.Max(toks[i].Start, span.Start);
                int e = Math.Min(toks[i].Start + toks[i].Length, span.End);
                if (e > s) result.Add(new ClassificationSpan(new SnapshotSpan(span.Snapshot, s, e - s), t));
            }
            return result;
        }
    }
}
