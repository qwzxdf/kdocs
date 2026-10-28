using System.Collections.Generic;
using System.ComponentModel;
using System.Runtime.InteropServices;
using Microsoft.VisualStudio.Shell;

namespace KHlsl.Vsix
{
    /// <summary>ツール → オプション → K-HLSL → 色。項目ごとに、専用の色を付けるかを選ぶ。色そのものは「フォントおよび色」で変える。</summary>
    [ComVisible(true)]
    [Guid("8c4b1f6e-2d7a-4e39-b5c0-6a91d3e8f207")]
    public class KHlslColorOptions : DialogPage
    {
        private const string Brackets = "1. 括弧";
        private const string Keywords = "2. キーワードと関数";
        private const string Names = "3. 名前の種類ごとの色";
        private const string Strings = "4. 文字列の中";

        [Category(Brackets), DisplayName("レインボー括弧")]
        [Description("( ) [ ] { } を、入れ子の深さで色分けする。OFF にすると、演算子と同じ色になる。")]
        public bool Rainbow { get; set; } = true;

        [Category(Brackets), DisplayName("対応しない括弧を赤くする")]
        [Description("対応する括弧のない ) ] } の背景を、薄い赤にする。")]
        public bool RainbowError { get; set; } = true;

        [Category(Keywords), DisplayName("制御キーワードの専用色")]
        [Description("if for while switch return などを、専用の色(既定は紫)にする。OFF にすると、キーワードの色になる。")]
        public bool Control { get; set; } = true;

        [Category(Keywords), DisplayName("#include などの専用色")]
        [Description("# で始まるディレクティブを、専用の色(既定は灰色)にする。OFF にすると、キーワードの色になる。")]
        public bool Preprocessor { get; set; } = true;

        [Category(Keywords), DisplayName("組み込み関数の専用色")]
        [Description("mul saturate Sample などを、専用の色(既定は橙)にする。OFF にすると、独自の関数と同じ色になる。")]
        public bool Intrinsic { get; set; } = true;

        [Category(Keywords), DisplayName("public / private などの色")]
        [Description("public private protected friend を、灰色にする。OFF にすると、キーワードの色になる。")]
        public bool Visibility { get; set; } = true;

        [Category(Names), DisplayName("型と名前空間")]
        [Description("型名・名前空間・ラベルに、C++ と同じ色を付ける。OFF にすると、普通の識別子の色になる。")]
        public bool Types { get; set; } = true;

        [Category(Names), DisplayName("関数")]
        [Description("独自の関数とメンバー関数に、C++ と同じ色を付ける。")]
        public bool Functions { get; set; } = true;

        [Category(Names), DisplayName("変数(スコープ別)")]
        [Description("引数・ローカル変数・メンバー・グローバル変数を、別々の色にする。OFF にすると、すべて普通の識別子の色になる。")]
        public bool Variables { get; set; } = true;

        [Category(Names), DisplayName("マクロ")]
        [Description("#define したマクロに、C++ と同じ色を付ける。")]
        public bool Macros { get; set; } = true;

        [Category(Names), DisplayName("列挙子・セマンティクス・属性")]
        [Description("列挙子・SV_Position などのセマンティクス・[numthreads] などの属性に、色を付ける。")]
        public bool Enumerators { get; set; } = true;

        [Category(Strings), DisplayName("エスケープ(\\n \\x41 など)")]
        [Description("文字列の中のエスケープを、マゼンタにする。OFF にすると、文字列と同じ色になる。")]
        public bool Escape { get; set; } = true;

        [Category(Strings), DisplayName("書式指定子(%d など)")]
        [Description("文字列の中の %d %5.2f などを、専用の色にする。OFF にすると、文字列と同じ色になる。")]
        public bool FormatSpec { get; set; } = true;

        private const string Colors = "5. 色(#RRGGBB。空欄は既定の色)";

        [Category(Colors), DisplayName("制御キーワード")] [Description("if for return など。例: #D8A0DF")]
        public string ColorControl { get; set; } = "";
        [Category(Colors), DisplayName("#include などのディレクティブ")] [Description("例: #9B9B9B")]
        public string ColorPreprocessor { get; set; } = "";
        [Category(Colors), DisplayName("組み込み関数")] [Description("mul saturate Sample など。例: #E8892B")]
        public string ColorIntrinsic { get; set; } = "";
        [Category(Colors), DisplayName("public / private など")] [Description("例: #696969")]
        public string ColorVisibility { get; set; } = "";
        [Category(Colors), DisplayName("文字列のエスケープ")] [Description("例: #FF00FF")]
        public string ColorEscape { get; set; } = "";
        [Category(Colors), DisplayName("書式指定子")] [Description("例: #7B68EE")]
        public string ColorFormat { get; set; } = "";
        [Category(Colors), DisplayName("レインボー括弧 1 番目")] [Description("例: #FF9900")]
        public string ColorRainbow1 { get; set; } = "";
        [Category(Colors), DisplayName("レインボー括弧 2 番目")] [Description("例: #FF1493")]
        public string ColorRainbow2 { get; set; } = "";
        [Category(Colors), DisplayName("レインボー括弧 3 番目")] [Description("例: #9ACD32")]
        public string ColorRainbow3 { get; set; } = "";
        [Category(Colors), DisplayName("レインボー括弧 4 番目")] [Description("例: #9400D3")]
        public string ColorRainbow4 { get; set; } = "";

        public override void LoadSettingsFromStorage()
        {
            Rainbow = KHlslSettings.IsOn(KHlslSettings.Rainbow);
            RainbowError = KHlslSettings.IsOn(KHlslSettings.RainbowError);
            Control = KHlslSettings.IsOn(KHlslSettings.Control);
            Preprocessor = KHlslSettings.IsOn(KHlslSettings.Preprocessor);
            Intrinsic = KHlslSettings.IsOn(KHlslSettings.Intrinsic);
            Visibility = KHlslSettings.IsOn(KHlslSettings.Visibility);
            Escape = KHlslSettings.IsOn(KHlslSettings.Escape);
            FormatSpec = KHlslSettings.IsOn(KHlslSettings.FormatSpec);
            Types = KHlslSettings.IsOn(KHlslSettings.Types);
            Functions = KHlslSettings.IsOn(KHlslSettings.Functions);
            Variables = KHlslSettings.IsOn(KHlslSettings.Variables);
            Macros = KHlslSettings.IsOn(KHlslSettings.Macros);
            Enumerators = KHlslSettings.IsOn(KHlslSettings.Enumerators);
            ColorControl = KHlslSettings.GetColor(KHlslSettings.ColorControl);
            ColorPreprocessor = KHlslSettings.GetColor(KHlslSettings.ColorPreprocessor);
            ColorIntrinsic = KHlslSettings.GetColor(KHlslSettings.ColorIntrinsic);
            ColorVisibility = KHlslSettings.GetColor(KHlslSettings.ColorVisibility);
            ColorEscape = KHlslSettings.GetColor(KHlslSettings.ColorEscape);
            ColorFormat = KHlslSettings.GetColor(KHlslSettings.ColorFormat);
            ColorRainbow1 = KHlslSettings.GetColor(KHlslSettings.ColorRainbow1);
            ColorRainbow2 = KHlslSettings.GetColor(KHlslSettings.ColorRainbow2);
            ColorRainbow3 = KHlslSettings.GetColor(KHlslSettings.ColorRainbow3);
            ColorRainbow4 = KHlslSettings.GetColor(KHlslSettings.ColorRainbow4);
        }

        public override void SaveSettingsToStorage()
        {
            KHlslSettings.Save(new Dictionary<string, string>
            {
                { KHlslSettings.Rainbow, Rainbow ? "1" : "0" },
                { KHlslSettings.RainbowError, RainbowError ? "1" : "0" },
                { KHlslSettings.Control, Control ? "1" : "0" },
                { KHlslSettings.Preprocessor, Preprocessor ? "1" : "0" },
                { KHlslSettings.Intrinsic, Intrinsic ? "1" : "0" },
                { KHlslSettings.Visibility, Visibility ? "1" : "0" },
                { KHlslSettings.Escape, Escape ? "1" : "0" },
                { KHlslSettings.FormatSpec, FormatSpec ? "1" : "0" },
                { KHlslSettings.Types, Types ? "1" : "0" },
                { KHlslSettings.Functions, Functions ? "1" : "0" },
                { KHlslSettings.Variables, Variables ? "1" : "0" },
                { KHlslSettings.Macros, Macros ? "1" : "0" },
                { KHlslSettings.Enumerators, Enumerators ? "1" : "0" },
                { KHlslSettings.ColorControl, ColorControl },
                { KHlslSettings.ColorPreprocessor, ColorPreprocessor },
                { KHlslSettings.ColorIntrinsic, ColorIntrinsic },
                { KHlslSettings.ColorVisibility, ColorVisibility },
                { KHlslSettings.ColorEscape, ColorEscape },
                { KHlslSettings.ColorFormat, ColorFormat },
                { KHlslSettings.ColorRainbow1, ColorRainbow1 },
                { KHlslSettings.ColorRainbow2, ColorRainbow2 },
                { KHlslSettings.ColorRainbow3, ColorRainbow3 },
                { KHlslSettings.ColorRainbow4, ColorRainbow4 }
            });
        }
    }
}
