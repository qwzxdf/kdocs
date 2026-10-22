using System;
using System.Collections.Generic;
using System.ComponentModel.Composition;
using System.Linq;
using System.Windows.Media;
using Microsoft.VisualStudio.Text;
using Microsoft.VisualStudio.Text.Classification;
using Microsoft.VisualStudio.Utilities;

namespace KHlsl.Vsix
{
    /// <summary>
    /// Viasfora が付ける色(可視性キーワード・文字列のエスケープ・書式指定子・レインボー括弧)の分類名。
    /// それ以外は、VS の C++ と同じ分類名(cppFunction など)を使うので、テーマの C++ の色がそのまま使われる。
    /// </summary>
    internal static class KHlslClassNames
    {
        public const string Visibility = "khlsl.visibility";
        public const string Escape = "khlsl.escape";
        public const string Format = "khlsl.format";
        public const string RainbowError = "khlsl.rainbow.error";

        public static string Rainbow(int n) { return "khlsl.rainbow." + n; }
    }

    internal static class KHlslClassDefinitions
    {
        [Export] [Name(KHlslClassNames.Visibility)] internal static ClassificationTypeDefinition Visibility;
        [Export] [Name(KHlslClassNames.Escape)] internal static ClassificationTypeDefinition Escape;
        [Export] [Name(KHlslClassNames.Format)] internal static ClassificationTypeDefinition Format;
        [Export] [Name("khlsl.rainbow.1")] internal static ClassificationTypeDefinition Rainbow1;
        [Export] [Name("khlsl.rainbow.2")] internal static ClassificationTypeDefinition Rainbow2;
        [Export] [Name("khlsl.rainbow.3")] internal static ClassificationTypeDefinition Rainbow3;
        [Export] [Name("khlsl.rainbow.4")] internal static ClassificationTypeDefinition Rainbow4;
        [Export] [Name("khlsl.rainbow.5")] internal static ClassificationTypeDefinition Rainbow5;
        [Export] [Name("khlsl.rainbow.6")] internal static ClassificationTypeDefinition Rainbow6;
        [Export] [Name("khlsl.rainbow.7")] internal static ClassificationTypeDefinition Rainbow7;
        [Export] [Name("khlsl.rainbow.8")] internal static ClassificationTypeDefinition Rainbow8;
        [Export] [Name("khlsl.rainbow.9")] internal static ClassificationTypeDefinition Rainbow9;
        [Export] [Name(KHlslClassNames.RainbowError)] internal static ClassificationTypeDefinition RainbowError;
    }

    internal abstract class KHlslFormat : ClassificationFormatDefinition
    {
        // Viasfora の既定色は、テーマによらず固定
        protected KHlslFormat(string display, string color)
        {
            DisplayName = display;
            ForegroundColor = (Color)ColorConverter.ConvertFromString(color);
        }
    }

    [Export(typeof(EditorFormatDefinition))] [ClassificationType(ClassificationTypeNames = KHlslClassNames.Visibility)]
    [Name("khlsl.visibility.format")] [UserVisible(true)] [Order(After = Priority.High)]
    internal sealed class VisibilityFormat : KHlslFormat { public VisibilityFormat() : base("K-HLSL 可視性キーワード", "#696969") { } }

    [Export(typeof(EditorFormatDefinition))] [ClassificationType(ClassificationTypeNames = KHlslClassNames.Escape)]
    [Name("khlsl.escape.format")] [UserVisible(true)] [Order(After = Priority.High)]
    internal sealed class EscapeFormat : KHlslFormat { public EscapeFormat() : base("K-HLSL 文字列のエスケープ", "#FF00FF") { } }

    [Export(typeof(EditorFormatDefinition))] [ClassificationType(ClassificationTypeNames = KHlslClassNames.Format)]
    [Name("khlsl.format.format")] [UserVisible(true)] [Order(After = Priority.High)]
    internal sealed class FormatSpecifierFormat : KHlslFormat { public FormatSpecifierFormat() : base("K-HLSL 書式指定子", "#7B68EE") { } }

    [Export(typeof(EditorFormatDefinition))] [ClassificationType(ClassificationTypeNames = "khlsl.rainbow.1")]
    [Name("khlsl.rainbow.1.format")] [UserVisible(true)] [Order(After = Priority.High)]
    internal sealed class Rainbow1Format : KHlslFormat { public Rainbow1Format() : base("K-HLSL Rainbow 括弧 1", "#FF9900") { } }

    [Export(typeof(EditorFormatDefinition))] [ClassificationType(ClassificationTypeNames = "khlsl.rainbow.2")]
    [Name("khlsl.rainbow.2.format")] [UserVisible(true)] [Order(After = Priority.High)]
    internal sealed class Rainbow2Format : KHlslFormat { public Rainbow2Format() : base("K-HLSL Rainbow 括弧 2", "#FF1493") { } }

    [Export(typeof(EditorFormatDefinition))] [ClassificationType(ClassificationTypeNames = "khlsl.rainbow.3")]
    [Name("khlsl.rainbow.3.format")] [UserVisible(true)] [Order(After = Priority.High)]
    internal sealed class Rainbow3Format : KHlslFormat { public Rainbow3Format() : base("K-HLSL Rainbow 括弧 3", "#9ACD32") { } }

    [Export(typeof(EditorFormatDefinition))] [ClassificationType(ClassificationTypeNames = "khlsl.rainbow.4")]
    [Name("khlsl.rainbow.4.format")] [UserVisible(true)] [Order(After = Priority.High)]
    internal sealed class Rainbow4Format : KHlslFormat { public Rainbow4Format() : base("K-HLSL Rainbow 括弧 4", "#9400D3") { } }

    [Export(typeof(EditorFormatDefinition))] [ClassificationType(ClassificationTypeNames = "khlsl.rainbow.5")]
    [Name("khlsl.rainbow.5.format")] [UserVisible(true)] [Order(After = Priority.High)]
    internal sealed class Rainbow5Format : KHlslFormat { public Rainbow5Format() : base("K-HLSL Rainbow 括弧 5", "#696969") { } }

    [Export(typeof(EditorFormatDefinition))] [ClassificationType(ClassificationTypeNames = "khlsl.rainbow.6")]
    [Name("khlsl.rainbow.6.format")] [UserVisible(true)] [Order(After = Priority.High)]
    internal sealed class Rainbow6Format : KHlslFormat { public Rainbow6Format() : base("K-HLSL Rainbow 括弧 6", "#4169E1") { } }

    [Export(typeof(EditorFormatDefinition))] [ClassificationType(ClassificationTypeNames = "khlsl.rainbow.7")]
    [Name("khlsl.rainbow.7.format")] [UserVisible(true)] [Order(After = Priority.High)]
    internal sealed class Rainbow7Format : KHlslFormat { public Rainbow7Format() : base("K-HLSL Rainbow 括弧 7", "#DC143C") { } }

    [Export(typeof(EditorFormatDefinition))] [ClassificationType(ClassificationTypeNames = "khlsl.rainbow.8")]
    [Name("khlsl.rainbow.8.format")] [UserVisible(true)] [Order(After = Priority.High)]
    internal sealed class Rainbow8Format : KHlslFormat { public Rainbow8Format() : base("K-HLSL Rainbow 括弧 8", "#00CED1") { } }

    [Export(typeof(EditorFormatDefinition))] [ClassificationType(ClassificationTypeNames = "khlsl.rainbow.9")]
    [Name("khlsl.rainbow.9.format")] [UserVisible(true)] [Order(After = Priority.High)]
    internal sealed class Rainbow9Format : KHlslFormat { public Rainbow9Format() : base("K-HLSL Rainbow 括弧 9", "#008000") { } }

    [Export(typeof(EditorFormatDefinition))] [ClassificationType(ClassificationTypeNames = KHlslClassNames.RainbowError)]
    [Name("khlsl.rainbow.error.format")] [UserVisible(true)] [Order(After = Priority.High)]
    internal sealed class RainbowErrorFormat : ClassificationFormatDefinition
    {
        public RainbowErrorFormat()
        {
            DisplayName = "K-HLSL Rainbow 括弧(対応なし)";
            BackgroundColor = (Color)ColorConverter.ConvertFromString("#F08080");
            ForegroundCustomizable = false;
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
            Func<string, IClassificationType> get = name => registry.GetClassificationType(name);
            IClassificationType identifier = get("identifier");
            IClassificationType str = get("string");
            IClassificationType op = get("operator");
            IClassificationType keyword = get("keyword");

            // 複数の分類を重ねる(VS の C++ が、cppFunction;Semantic と identifier を重ねるのと同じ)
            Func<IClassificationType[], IClassificationType> combine = parts =>
            {
                var present = parts.Where(p => p != null).ToArray();
                if (present.Length == 0) return identifier;
                return present.Length == 1 ? present[0] : registry.CreateTransientClassificationType(present);
            };
            // C++ の意味的な色付け(cppXxx;Semantic + identifier)
            Func<string, IClassificationType> semantic = name =>
            {
                var s = get(name + ";Semantic");
                return s != null ? combine(new[] { s, identifier }) : (get(name) ?? identifier);
            };

            _types[Tk.Comment] = get("comment");
            _types[Tk.String] = str;
            _types[Tk.StringDelim] = combine(new[] { get("cppStringDelimiterCharacter"), str });
            _types[Tk.Number] = get("number");
            _types[Tk.Preprocessor] = get("preprocessor keyword") ?? keyword;
            _types[Tk.Keyword] = keyword;
            _types[Tk.Control] = get("cppControlKeyword") ?? keyword;
            _types[Tk.Visibility] = combine(new[] { keyword, get(KHlslClassNames.Visibility) });
            _types[Tk.Type] = semantic("cppType");
            _types[Tk.Function] = semantic("cppFunction");
            _types[Tk.MemberFunc] = semantic("cppMemberFunction");
            _types[Tk.Semantic] = semantic("cppEnumerator");
            _types[Tk.Attribute] = get("cppAttributeIdentifier") ?? semantic("cppType");
            _types[Tk.Enumerator] = semantic("cppEnumerator");
            _types[Tk.Macro] = semantic("cppMacro");
            _types[Tk.Operator] = op;
            _types[Tk.Namespace] = semantic("cppNamespace");
            _types[Tk.Global] = semantic("cppGlobalVariable");
            _types[Tk.Local] = semantic("cppLocalVariable");
            _types[Tk.Param] = semantic("cppParameter");
            _types[Tk.Member] = semantic("cppMemberField");
            _types[Tk.Label] = semantic("cppLabel");
            _types[Tk.Identifier] = identifier;
            _types[Tk.Escape] = combine(new[] { get("cppStringEscapeCharacter"), str, get(KHlslClassNames.Escape) });
            _types[Tk.Format] = combine(new[] { str, get(KHlslClassNames.Format) });
            for (int n = 1; n <= 9; n++)
                _types[(Tk)((int)Tk.Rainbow1 + n - 1)] = combine(new[] { op, get(KHlslClassNames.Rainbow(n)) });
            _types[Tk.RainbowError] = combine(new[] { op, get(KHlslClassNames.RainbowError) });
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
