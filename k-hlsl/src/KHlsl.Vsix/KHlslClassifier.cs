using System;
using System.Collections.Generic;
using System.ComponentModel.Composition;
using System.Linq;
using System.Windows.Media;
using Microsoft.VisualStudio.Text;
using Microsoft.VisualStudio.Text.Classification;
using Microsoft.VisualStudio.Text.Editor;
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
        public const string Intrinsic = "khlsl.intrinsic";
        public const string Preprocessor = "khlsl.preprocessor";
        public const string Control = "khlsl.control";
        public const string Escape = "khlsl.escape";
        public const string Format = "khlsl.format";
        public const string RainbowError = "khlsl.rainbow.error";

        public static string Rainbow(int n) { return "khlsl.rainbow." + n; }
    }

    internal static class KHlslClassDefinitions
    {
        [Export] [Name(KHlslClassNames.Visibility)] internal static ClassificationTypeDefinition Visibility;
        [Export] [Name(KHlslClassNames.Intrinsic)] internal static ClassificationTypeDefinition Intrinsic;
        [Export] [Name(KHlslClassNames.Preprocessor)] internal static ClassificationTypeDefinition Preprocessor;
        [Export] [Name(KHlslClassNames.Control)] internal static ClassificationTypeDefinition Control;
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

    /// <summary>VS の C++ の既定色(ダーク / ライト)。エディターの背景の明るさで、どちらかを選ぶ。</summary>
    internal static class ThemeColors
    {
        public static Color Pick(string dark, string light)
        {
            bool isDark = true;
            try
            {
                var bg = Microsoft.VisualStudio.PlatformUI.VSColorTheme.GetThemedColor(Microsoft.VisualStudio.PlatformUI.EnvironmentColors.ToolWindowBackgroundColorKey);
                isDark = (bg.R * 299 + bg.G * 587 + bg.B * 114) / 1000 < 128;
            }
            catch (Exception) { }
            return (Color)ColorConverter.ConvertFromString(isDark ? dark : light);
        }
    }

    // #include・#define など。VS の C++ と同じ灰色
    [Export(typeof(EditorFormatDefinition))] [ClassificationType(ClassificationTypeNames = KHlslClassNames.Preprocessor)]
    [Name("khlsl.preprocessor.format")] [UserVisible(true)] [Order(After = Priority.High)]
    internal sealed class PreprocessorFormat : ClassificationFormatDefinition
    {
        public PreprocessorFormat() { DisplayName = "K-HLSL プリプロセッサ キーワード"; ForegroundColor = ThemeColors.Pick("#9B9B9B", "#808080"); }
    }

    // if・for・return など。VS の C++ の制御キーワードと同じ紫
    [Export(typeof(EditorFormatDefinition))] [ClassificationType(ClassificationTypeNames = KHlslClassNames.Control)]
    [Name("khlsl.control.format")] [UserVisible(true)] [Order(After = Priority.High)]
    internal sealed class ControlFormat : ClassificationFormatDefinition
    {
        public ControlFormat() { DisplayName = "K-HLSL 制御キーワード"; ForegroundColor = ThemeColors.Pick("#D8A0DF", "#8F08C4"); }
    }

    [Export(typeof(EditorFormatDefinition))] [ClassificationType(ClassificationTypeNames = KHlslClassNames.Intrinsic)]
    [Name("khlsl.intrinsic.format")] [UserVisible(true)] [Order(After = Priority.High)]
    internal sealed class IntrinsicFormat : KHlslFormat { public IntrinsicFormat() : base("K-HLSL 組み込み関数", "#569CD6") { } }

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
        [Import] internal ITextBufferFactoryService BufferFactory { get; set; }
        [Import] internal IContentTypeRegistryService ContentTypes { get; set; }
        [Import] internal IClassifierAggregatorService Aggregator { get; set; }
        [Import] internal IClassificationFormatMapService FormatMaps { get; set; }

        private static object _cppKeepAlive;
        private static bool _colorsHooked;

        public IClassifier GetClassifier(ITextBuffer buffer)
        {
            WarmUpCpp();
            HookColors();
            return buffer.Properties.GetOrCreateSingletonProperty(() => new KHlslClassifier(buffer, Registry));
        }

        // 設定ページで決めた色を、分類の書式へ反映する(空欄は、定義した既定の色)
        private void HookColors()
        {
            if (_colorsHooked) return;
            _colorsHooked = true;
            ApplyColors();
            KHlslSettings.Changed += (s, e) =>
            {
                var d = System.Windows.Application.Current != null ? System.Windows.Application.Current.Dispatcher : null;
                if (d != null) d.BeginInvoke(new Action(ApplyColors)); else ApplyColors();
            };
        }

        private void ApplyColors()
        {
            try
            {
                var map = FormatMaps.GetClassificationFormatMap("text");
                var items = new[]
                {
                    Tuple.Create(KHlslClassNames.Control, "color.control", ThemeColors.Pick("#D8A0DF", "#8F08C4")),
                    Tuple.Create(KHlslClassNames.Preprocessor, "color.preprocessor", ThemeColors.Pick("#9B9B9B", "#808080")),
                    Tuple.Create(KHlslClassNames.Intrinsic, "color.intrinsic", ThemeColors.Pick("#569CD6", "#0000FF")),
                    Tuple.Create(KHlslClassNames.Visibility, "color.visibility", Rgb("#696969")),
                    Tuple.Create(KHlslClassNames.Escape, "color.escape", Rgb("#FF00FF")),
                    Tuple.Create(KHlslClassNames.Format, "color.format", Rgb("#7B68EE")),
                    Tuple.Create(KHlslClassNames.Rainbow(1), "color.rainbow1", Rgb("#FF9900")),
                    Tuple.Create(KHlslClassNames.Rainbow(2), "color.rainbow2", Rgb("#FF1493")),
                    Tuple.Create(KHlslClassNames.Rainbow(3), "color.rainbow3", Rgb("#9ACD32")),
                    Tuple.Create(KHlslClassNames.Rainbow(4), "color.rainbow4", Rgb("#9400D3"))
                };
                map.BeginBatchUpdate();
                try
                {
                    foreach (var key in KHlslClassifier.UserKinds.Values)
                    {
                        var ut = Registry.GetClassificationType("khlsl.user." + key);
                        string uc = KHlslSettings.GetColor("color." + key);
                        if (ut != null && uc.Length > 0) map.SetTextProperties(ut, map.GetTextProperties(ut).SetForeground(Rgb(uc)));
                    }
                    foreach (var it in items)
                    {
                        var type = Registry.GetClassificationType(it.Item1);
                        if (type == null) continue;
                        string custom = KHlslSettings.GetColor(it.Item2);
                        Color c = custom.Length > 0 ? Rgb(custom) : it.Item3;
                        map.SetTextProperties(type, map.GetTextProperties(type).SetForeground(c));
                    }
                }
                finally { map.EndBatchUpdate(); }
            }
            catch (Exception ex) { KHlslPackage.Log("色の反映に失敗: " + ex.Message); }
        }

        private static Color Rgb(string hex) { return (Color)ColorConverter.ConvertFromString(hex); }

        /// <summary>
        /// 色は、VS の C++ の分類(cppFunction;Semantic など)を借りている。それらは、C++ のエディターが
        /// 動き出すまで登録されないので、C++ のファイルを開いていないセッションでも、動き出すように促す。
        /// </summary>
        private void WarmUpCpp()
        {
            if (_cppKeepAlive != null) return;
            _cppKeepAlive = new object();
            try
            {
                var ct = ContentTypes.GetContentType("C/C++");
                if (ct == null) return;
                var buf = BufferFactory.CreateTextBuffer("int main() { return 0; }" + Environment.NewLine, ct);
                var c = Aggregator.GetClassifier(buf);
                c.GetClassificationSpans(new SnapshotSpan(buf.CurrentSnapshot, 0, buf.CurrentSnapshot.Length));
                _cppKeepAlive = new object[] { buf, c };
                KHlslPackage.Log("C++ warm-up done");
            }
            catch (Exception ex) { KHlslPackage.Log("C++ warm-up failed: " + ex.Message); }
        }
    }

    internal sealed class KHlslClassifier : IClassifier
    {
        // 登録を待つ、C++ の意味的な分類
        private static readonly string[] SemanticNames =
        {
            "cppType", "cppFunction", "cppMemberFunction", "cppEnumerator", "cppMacro", "cppNamespace",
            "cppGlobalVariable", "cppLocalVariable", "cppParameter", "cppMemberField", "cppLabel"
        };

        // 設定ページで色を決めた項目は、元の分類に、khlsl.user.* の分類を重ねる
        internal static readonly Dictionary<Tk, string> UserKinds = new Dictionary<Tk, string>
        {
            { Tk.Comment, "comment" },
            { Tk.String, "string" },
            { Tk.Number, "number" },
            { Tk.Operator, "operator" },
            { Tk.Keyword, "keyword" },
            { Tk.Type, "type" },
            { Tk.Namespace, "namespace" },
            { Tk.Label, "label" },
            { Tk.Function, "function" },
            { Tk.MemberFunc, "memberfunc" },
            { Tk.Param, "param" },
            { Tk.Local, "local" },
            { Tk.Member, "member" },
            { Tk.Global, "global" },
            { Tk.Macro, "macro" },
            { Tk.Enumerator, "enumerator" },
            { Tk.Semantic, "semantic" },
            { Tk.Attribute, "attribute" },
            { Tk.Identifier, "identifier" },
        };

        private readonly ITextBuffer _buffer;
        private readonly IClassificationTypeRegistryService _registry;
        private Dictionary<Tk, IClassificationType> _types = new Dictionary<Tk, IClassificationType>();
        private readonly object _gate = new object();
        private ITextSnapshot _snapshot;
        private List<Tok> _tokens = new List<Tok>();
        private int _missing = int.MaxValue;
        private int _lastCheck = Environment.TickCount;

        public event EventHandler<ClassificationChangedEventArgs> ClassificationChanged;

        public KHlslClassifier(ITextBuffer buffer, IClassificationTypeRegistryService registry)
        {
            _buffer = buffer;
            _registry = registry;
            Resolve();
            buffer.Changed += OnChanged;
            KHlslSettings.Changed += OnSettingsChanged;
        }

        private void OnSettingsChanged(object sender, EventArgs e)
        {
            Resolve();
            var d = System.Windows.Application.Current != null ? System.Windows.Application.Current.Dispatcher : null;
            if (d != null) d.BeginInvoke(new Action(RaiseAll)); else RaiseAll();
        }

        /// <summary>分類名から、分類の型を引く。C++ 側が未登録の物は、近い型で代用して、あとで引き直す。</summary>
        private void Resolve()
        {
            var registry = _registry;
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

            var t = new Dictionary<Tk, IClassificationType>();
            t[Tk.Comment] = get("comment");
            t[Tk.String] = str;
            t[Tk.StringDelim] = combine(new[] { get("cppStringDelimiterCharacter"), str });
            t[Tk.Number] = get("number");
            // keyword などと重ねると、そちらの色が勝つので、専用の分類だけを使う
            t[Tk.Preprocessor] = get(KHlslClassNames.Preprocessor) ?? get("preprocessor keyword") ?? keyword;
            t[Tk.Keyword] = keyword;
            t[Tk.Control] = get(KHlslClassNames.Control) ?? keyword;
            t[Tk.Visibility] = combine(new[] { keyword, get(KHlslClassNames.Visibility) });
            t[Tk.Type] = semantic("cppType");
            t[Tk.Function] = semantic("cppFunction");
            t[Tk.MemberFunc] = semantic("cppMemberFunction");
            // identifier と重ねると、そちらの色が勝つので、専用の分類だけを使う
            // 色を決めていなければ、float3 などと同じ、テーマのキーワードの色(青)
            t[Tk.Intrinsic] = KHlslSettings.GetColor("color.intrinsic").Length > 0 ? (get(KHlslClassNames.Intrinsic) ?? keyword) : keyword;
            t[Tk.Semantic] = semantic("cppEnumerator");
            t[Tk.Attribute] = get("cppAttributeIdentifier") ?? semantic("cppType");
            t[Tk.Enumerator] = semantic("cppEnumerator");
            t[Tk.Macro] = semantic("cppMacro");
            t[Tk.Operator] = op;
            t[Tk.Namespace] = semantic("cppNamespace");
            t[Tk.Global] = semantic("cppGlobalVariable");
            t[Tk.Local] = semantic("cppLocalVariable");
            t[Tk.Param] = semantic("cppParameter");
            t[Tk.Member] = semantic("cppMemberField");
            t[Tk.Label] = semantic("cppLabel");
            t[Tk.Identifier] = identifier;
            t[Tk.Escape] = combine(new[] { get("cppStringEscapeCharacter"), str, get(KHlslClassNames.Escape) });
            t[Tk.Format] = combine(new[] { str, get(KHlslClassNames.Format) });
            for (int n = 1; n <= 9; n++)
                t[(Tk)((int)Tk.Rainbow1 + n - 1)] = combine(new[] { op, get(KHlslClassNames.Rainbow(n)) });
            t[Tk.RainbowError] = combine(new[] { op, get(KHlslClassNames.RainbowError) });

            // ツール → オプション → K-HLSL → 色 で OFF にした項目は、専用の色をやめる
            Func<string, bool> on = KHlslSettings.IsOn;
            if (!on(KHlslSettings.Rainbow))
                for (int n = 1; n <= 9; n++) t[(Tk)((int)Tk.Rainbow1 + n - 1)] = op;
            if (!on(KHlslSettings.RainbowError)) t[Tk.RainbowError] = op;
            if (!on(KHlslSettings.Control)) t[Tk.Control] = keyword;
            if (!on(KHlslSettings.Preprocessor)) t[Tk.Preprocessor] = get("preprocessor keyword") ?? keyword;
            if (!on(KHlslSettings.Intrinsic)) t[Tk.Intrinsic] = t[Tk.Function];
            if (!on(KHlslSettings.Visibility)) t[Tk.Visibility] = keyword;
            if (!on(KHlslSettings.Escape)) t[Tk.Escape] = str;
            if (!on(KHlslSettings.FormatSpec)) t[Tk.Format] = str;
            if (!on(KHlslSettings.Types)) { t[Tk.Type] = identifier; t[Tk.Namespace] = identifier; t[Tk.Label] = identifier; }
            if (!on(KHlslSettings.Functions)) { t[Tk.Function] = identifier; t[Tk.MemberFunc] = identifier; }
            if (!on(KHlslSettings.Variables)) { t[Tk.Global] = identifier; t[Tk.Local] = identifier; t[Tk.Param] = identifier; t[Tk.Member] = identifier; }
            if (!on(KHlslSettings.Macros)) t[Tk.Macro] = identifier;
            if (!on(KHlslSettings.Enumerators)) { t[Tk.Enumerator] = identifier; t[Tk.Semantic] = identifier; t[Tk.Attribute] = identifier; }

            foreach (var kv in UserKinds)
            {
                if (KHlslSettings.GetColor("color." + kv.Value).Length == 0) continue;
                var u = get("khlsl.user." + kv.Value);
                if (u != null && t.ContainsKey(kv.Key)) t[kv.Key] = combine(new[] { t[kv.Key], u });
            }

            _missing = SemanticNames.Count(nm => get(nm + ";Semantic") == null);
            _types = t;
        }

        private void RaiseAll()
        {
            var snap = _buffer.CurrentSnapshot;
            var h = ClassificationChanged;
            if (h != null) h(this, new ClassificationChangedEventArgs(new SnapshotSpan(snap, 0, snap.Length)));
        }

        private void OnChanged(object sender, TextContentChangedEventArgs e)
        {
            RaiseAll();
        }

        /// <summary>C++ の分類が、あとから登録されたら、引き直して、色を付け直す。</summary>
        private void RecheckTypes()
        {
            if (_missing == 0) return;
            int now = Environment.TickCount;
            if (now - _lastCheck < 1500) return;
            _lastCheck = now;
            int before = _missing;
            Resolve();
            if (_missing < before)
            {
                KHlslPackage.Log("C++ の分類が登録されたので、色を付け直す(未登録 " + before + " → " + _missing + ")");
                var d = System.Windows.Application.Current != null ? System.Windows.Application.Current.Dispatcher : null;
                if (d != null) d.BeginInvoke(new Action(RaiseAll), System.Windows.Threading.DispatcherPriority.ApplicationIdle);
            }
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
            RecheckTypes();
            var types = _types;
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
                if (!types.TryGetValue(toks[i].Kind, out t) || t == null) continue;
                int s = Math.Max(toks[i].Start, span.Start);
                int e = Math.Min(toks[i].Start + toks[i].Length, span.End);
                if (e > s) result.Add(new ClassificationSpan(new SnapshotSpan(span.Snapshot, s, e - s), t));
            }
            return result;
        }
    }
}
