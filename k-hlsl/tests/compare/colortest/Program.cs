using System;
using System.Collections.Generic;
using System.ComponentModel.Composition;
using System.Linq;
using System.Reflection;
using System.Windows.Media;
using Microsoft.VisualStudio.Text.Classification;
using Microsoft.VisualStudio.Utilities;

/// <summary>
/// Viasfora の書式クラスを実際に生成し、K-HLSL の対応する書式クラスと、色・太字・不透明度・順序などを突き合わせる。
/// </summary>
internal static class Program
{
    private static int _ng;
    private static int _ok;

    private static int Main()
    {
        var core = Assembly.Load("Viasfora.Core");
        var rainbow = Assembly.Load("Viasfora.Rainbow");
        var mine = Assembly.Load("KHlsl.Vsix");

        var pairs = new List<Tuple<Assembly, string, string, string>>
        {
            Tuple.Create(core, "Winterdom.Viasfora.EditorFormats.FlowControlFormat", "KHlsl.Vsix.FlowFormat", "制御フロー キーワード"),
            Tuple.Create(core, "Winterdom.Viasfora.EditorFormats.VisibilityKeywordFormat", "KHlsl.Vsix.VisibilityFormat", "可視性 キーワード"),
            Tuple.Create(core, "Winterdom.Viasfora.EditorFormats.StringEscapeSequenceFormat", "KHlsl.Vsix.EscapeFormat", "文字列のエスケープ"),
            Tuple.Create(core, "Winterdom.Viasfora.EditorFormats.FormatSpecifierFormat", "KHlsl.Vsix.FormatSpecifierFormat", "書式指定子"),
            Tuple.Create(rainbow, "Winterdom.Viasfora.Rainbow.EditorFormats.RainbowErrorFormat", "KHlsl.Vsix.RainbowErrorFormat", "Rainbow 対応なし"),
        };
        for (int i = 1; i <= 9; i++)
            pairs.Add(Tuple.Create(rainbow, "Winterdom.Viasfora.Rainbow.EditorFormats.Rainbow" + i + "Format", "KHlsl.Vsix.Rainbow" + i + "Format", "Rainbow 括弧 " + i));

        foreach (var p in pairs)
        {
            var vt = p.Item1.GetType(p.Item2, true);
            var mt = mine.GetType(p.Item3, true);
            var v = (ClassificationFormatDefinition)Activator.CreateInstance(vt, true);
            var m = (ClassificationFormatDefinition)Activator.CreateInstance(mt, true);
            Console.WriteLine("== " + p.Item4);
            Check("前景色", Fmt(v.ForegroundColor), Fmt(m.ForegroundColor));
            Check("背景色", Fmt(v.BackgroundColor), Fmt(m.BackgroundColor));
            Check("前景色を変更可", v.ForegroundCustomizable, m.ForegroundCustomizable);
            Check("背景色を変更可", v.BackgroundCustomizable, m.BackgroundCustomizable);
            Check("太字", v.IsBold, m.IsBold);
            Check("斜体", v.IsItalic, m.IsItalic);
            Check("前景の不透明度", v.ForegroundOpacity, m.ForegroundOpacity);
            Check("背景の不透明度", v.BackgroundOpacity, m.BackgroundOpacity);
            Check("文字サイズ", v.FontRenderingSize, m.FontRenderingSize);
            Check("フォント", v.FontTypeface?.ToString(), m.FontTypeface?.ToString());
            Check("下線など", v.TextDecorations == null ? "-" : v.TextDecorations.Count.ToString(), m.TextDecorations == null ? "-" : m.TextDecorations.Count.ToString());

            // 属性: Order(After) と UserVisible
            Check("Order.After", Attr<OrderAttribute>(vt)?.After, Attr<OrderAttribute>(mt)?.After);
            Check("Order.Before", Attr<OrderAttribute>(vt)?.Before, Attr<OrderAttribute>(mt)?.Before);
            Check("UserVisible", Attr<UserVisibleAttribute>(vt)?.UserVisible, Attr<UserVisibleAttribute>(mt)?.UserVisible);
        }
        Console.WriteLine("\n一致 {0} 項目、不一致 {1} 項目", _ok, _ng);
        return _ng == 0 ? 0 : 1;
    }

    private static T Attr<T>(Type t) where T : Attribute
    {
        return t.GetCustomAttributes(typeof(T), true).Cast<T>().FirstOrDefault();
    }

    private static string Fmt(Color? c)
    {
        return c.HasValue ? "#" + c.Value.A.ToString("X2") + c.Value.R.ToString("X2") + c.Value.G.ToString("X2") + c.Value.B.ToString("X2") : "(なし)";
    }

    private static void Check(string what, object a, object b)
    {
        string sa = a == null ? "(なし)" : a.ToString();
        string sb = b == null ? "(なし)" : b.ToString();
        if (sa == sb) { _ok++; return; }
        _ng++;
        Console.WriteLine("   不一致 {0}: Viasfora={1}  K-HLSL={2}", what, sa, sb);
    }
}
