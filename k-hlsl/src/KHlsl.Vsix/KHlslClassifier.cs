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
        public const string Flow = "khlsl.flow";
        public const string Visibility = "khlsl.visibility";
        public const string Escape = "khlsl.escape";
        public const string Format = "khlsl.format";
        public const string Rainbow = "khlsl.rainbow.";
        public const string RainbowError = "khlsl.rainbow.error";
    }

    internal static class KHlslClassDefinitions
    {
        [Export] [Name(KHlslClassNames.Function)] [BaseDefinition("identifier")] internal static ClassificationTypeDefinition Function;
        [Export] [Name(KHlslClassNames.Number)] [BaseDefinition("number")] internal static ClassificationTypeDefinition Number;
        [Export] [Name(KHlslClassNames.Semantic)] [BaseDefinition("identifier")] internal static ClassificationTypeDefinition Semantic;
        [Export] [Name(KHlslClassNames.Attribute)] [BaseDefinition("identifier")] internal static ClassificationTypeDefinition Attribute;
        [Export] [Name(KHlslClassNames.Constant)] [BaseDefinition("identifier")] internal static ClassificationTypeDefinition Constant;
        [Export] [Name(KHlslClassNames.Macro)] [BaseDefinition("identifier")] internal static ClassificationTypeDefinition Macro;
        [Export] [Name(KHlslClassNames.Flow)] [BaseDefinition("keyword")] internal static ClassificationTypeDefinition Flow;
        [Export] [Name(KHlslClassNames.Visibility)] [BaseDefinition("keyword")] internal static ClassificationTypeDefinition Visibility;
        [Export] [Name(KHlslClassNames.Escape)] [BaseDefinition("string")] internal static ClassificationTypeDefinition Escape;
        [Export] [Name(KHlslClassNames.Format)] [BaseDefinition("string")] internal static ClassificationTypeDefinition Format;
        [Export] [Name("khlsl.rainbow.1")] [BaseDefinition("identifier")] internal static ClassificationTypeDefinition Rainbow1;
        [Export] [Name("khlsl.rainbow.2")] [BaseDefinition("identifier")] internal static ClassificationTypeDefinition Rainbow2;
        [Export] [Name("khlsl.rainbow.3")] [BaseDefinition("identifier")] internal static ClassificationTypeDefinition Rainbow3;
        [Export] [Name("khlsl.rainbow.4")] [BaseDefinition("identifier")] internal static ClassificationTypeDefinition Rainbow4;
        [Export] [Name("khlsl.rainbow.5")] [BaseDefinition("identifier")] internal static ClassificationTypeDefinition Rainbow5;
        [Export] [Name("khlsl.rainbow.6")] [BaseDefinition("identifier")] internal static ClassificationTypeDefinition Rainbow6;
        [Export] [Name("khlsl.rainbow.7")] [BaseDefinition("identifier")] internal static ClassificationTypeDefinition Rainbow7;
        [Export] [Name("khlsl.rainbow.8")] [BaseDefinition("identifier")] internal static ClassificationTypeDefinition Rainbow8;
        [Export] [Name("khlsl.rainbow.9")] [BaseDefinition("identifier")] internal static ClassificationTypeDefinition Rainbow9;
        [Export] [Name("khlsl.rainbow.error")] [BaseDefinition("identifier")] internal static ClassificationTypeDefinition RainbowError;
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

    // Viasfora の既定色(テーマによらず固定)
    [Export(typeof(EditorFormatDefinition))] [ClassificationType(ClassificationTypeNames = KHlslClassNames.Flow)]
    [Name("khlsl.flow.format")] [UserVisible(true)] [Order(After = Priority.Default)]
    internal sealed class FlowFormat : KHlslFormat { public FlowFormat() : base("K-HLSL 制御フロー キーワード", "#FF4500", "#FF4500") { } }

    [Export(typeof(EditorFormatDefinition))] [ClassificationType(ClassificationTypeNames = KHlslClassNames.Visibility)]
    [Name("khlsl.visibility.format")] [UserVisible(true)] [Order(After = Priority.Default)]
    internal sealed class VisibilityFormat : KHlslFormat { public VisibilityFormat() : base("K-HLSL 可視性キーワード", "#696969", "#696969") { } }

    [Export(typeof(EditorFormatDefinition))] [ClassificationType(ClassificationTypeNames = KHlslClassNames.Escape)]
    [Name("khlsl.escape.format")] [UserVisible(true)] [Order(After = Priority.Default)]
    internal sealed class EscapeFormat : KHlslFormat { public EscapeFormat() : base("K-HLSL 文字列のエスケープ", "#FF00FF", "#FF00FF") { } }

    [Export(typeof(EditorFormatDefinition))] [ClassificationType(ClassificationTypeNames = KHlslClassNames.Format)]
    [Name("khlsl.format.format")] [UserVisible(true)] [Order(After = Priority.Default)]
    internal sealed class FormatSpecifierFormat : KHlslFormat { public FormatSpecifierFormat() : base("K-HLSL 書式指定子", "#7B68EE", "#7B68EE") { } }

    [Export(typeof(EditorFormatDefinition))] [ClassificationType(ClassificationTypeNames = "khlsl.rainbow.1")]
    [Name("khlsl.rainbow.1.format")] [UserVisible(true)] [Order(After = Priority.Default)]
    internal sealed class Rainbow1Format : KHlslFormat { public Rainbow1Format() : base("K-HLSL Rainbow 括弧 1", "#FF9900", "#FF9900") { } }

    [Export(typeof(EditorFormatDefinition))] [ClassificationType(ClassificationTypeNames = "khlsl.rainbow.2")]
    [Name("khlsl.rainbow.2.format")] [UserVisible(true)] [Order(After = Priority.Default)]
    internal sealed class Rainbow2Format : KHlslFormat { public Rainbow2Format() : base("K-HLSL Rainbow 括弧 2", "#FF1493", "#FF1493") { } }

    [Export(typeof(EditorFormatDefinition))] [ClassificationType(ClassificationTypeNames = "khlsl.rainbow.3")]
    [Name("khlsl.rainbow.3.format")] [UserVisible(true)] [Order(After = Priority.Default)]
    internal sealed class Rainbow3Format : KHlslFormat { public Rainbow3Format() : base("K-HLSL Rainbow 括弧 3", "#9ACD32", "#9ACD32") { } }

    [Export(typeof(EditorFormatDefinition))] [ClassificationType(ClassificationTypeNames = "khlsl.rainbow.4")]
    [Name("khlsl.rainbow.4.format")] [UserVisible(true)] [Order(After = Priority.Default)]
    internal sealed class Rainbow4Format : KHlslFormat { public Rainbow4Format() : base("K-HLSL Rainbow 括弧 4", "#9400D3", "#9400D3") { } }

    [Export(typeof(EditorFormatDefinition))] [ClassificationType(ClassificationTypeNames = "khlsl.rainbow.5")]
    [Name("khlsl.rainbow.5.format")] [UserVisible(true)] [Order(After = Priority.Default)]
    internal sealed class Rainbow5Format : KHlslFormat { public Rainbow5Format() : base("K-HLSL Rainbow 括弧 5", "#696969", "#696969") { } }

    [Export(typeof(EditorFormatDefinition))] [ClassificationType(ClassificationTypeNames = "khlsl.rainbow.6")]
    [Name("khlsl.rainbow.6.format")] [UserVisible(true)] [Order(After = Priority.Default)]
    internal sealed class Rainbow6Format : KHlslFormat { public Rainbow6Format() : base("K-HLSL Rainbow 括弧 6", "#4169E1", "#4169E1") { } }

    [Export(typeof(EditorFormatDefinition))] [ClassificationType(ClassificationTypeNames = "khlsl.rainbow.7")]
    [Name("khlsl.rainbow.7.format")] [UserVisible(true)] [Order(After = Priority.Default)]
    internal sealed class Rainbow7Format : KHlslFormat { public Rainbow7Format() : base("K-HLSL Rainbow 括弧 7", "#DC143C", "#DC143C") { } }

    [Export(typeof(EditorFormatDefinition))] [ClassificationType(ClassificationTypeNames = "khlsl.rainbow.8")]
    [Name("khlsl.rainbow.8.format")] [UserVisible(true)] [Order(After = Priority.Default)]
    internal sealed class Rainbow8Format : KHlslFormat { public Rainbow8Format() : base("K-HLSL Rainbow 括弧 8", "#00CED1", "#00CED1") { } }

    [Export(typeof(EditorFormatDefinition))] [ClassificationType(ClassificationTypeNames = "khlsl.rainbow.9")]
    [Name("khlsl.rainbow.9.format")] [UserVisible(true)] [Order(After = Priority.Default)]
    internal sealed class Rainbow9Format : KHlslFormat { public Rainbow9Format() : base("K-HLSL Rainbow 括弧 9", "#008000", "#008000") { } }

    [Export(typeof(EditorFormatDefinition))] [ClassificationType(ClassificationTypeNames = "khlsl.rainbow.error")]
    [Name("khlsl.rainbow.error.format")] [UserVisible(true)] [Order(After = Priority.Default)]
    internal sealed class RainbowErrorFormat : ClassificationFormatDefinition
    {
        public RainbowErrorFormat()
        {
            DisplayName = "K-HLSL Rainbow 括弧(対応なし)";
            BackgroundColor = (Color)ColorConverter.ConvertFromString("#F08080");
        }
    }

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
            _types[Tk.Flow] = get(new[] { KHlslClassNames.Flow, "keyword" });
            _types[Tk.Visibility] = get(new[] { KHlslClassNames.Visibility, "keyword" });
            _types[Tk.Escape] = get(new[] { KHlslClassNames.Escape, "string" });
            _types[Tk.Format] = get(new[] { KHlslClassNames.Format, "string" });
            _types[Tk.Rainbow1] = get(new[] { "khlsl.rainbow.1", "identifier" });
            _types[Tk.Rainbow2] = get(new[] { "khlsl.rainbow.2", "identifier" });
            _types[Tk.Rainbow3] = get(new[] { "khlsl.rainbow.3", "identifier" });
            _types[Tk.Rainbow4] = get(new[] { "khlsl.rainbow.4", "identifier" });
            _types[Tk.Rainbow5] = get(new[] { "khlsl.rainbow.5", "identifier" });
            _types[Tk.Rainbow6] = get(new[] { "khlsl.rainbow.6", "identifier" });
            _types[Tk.Rainbow7] = get(new[] { "khlsl.rainbow.7", "identifier" });
            _types[Tk.Rainbow8] = get(new[] { "khlsl.rainbow.8", "identifier" });
            _types[Tk.Rainbow9] = get(new[] { "khlsl.rainbow.9", "identifier" });
            _types[Tk.RainbowError] = get(new[] { KHlslClassNames.RainbowError, "identifier" });
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
