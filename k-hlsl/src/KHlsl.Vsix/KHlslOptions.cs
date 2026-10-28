using System.Collections.Generic;
using System.ComponentModel;
using System.Drawing;
using System.Runtime.InteropServices;
using Microsoft.VisualStudio.Shell;

namespace KHlsl.Vsix
{
    /// <summary>
    /// ツール → オプション → K-HLSL → 色。色の見本から、K-HLSL の色を全部変えられる。
    /// 空欄の色は、既定(専用の色、または VS の C++ と同じ色)。自動生成した部分を含む。
    /// </summary>
    [ComVisible(true)]
    [Guid("8c4b1f6e-2d7a-4e39-b5c0-6a91d3e8f207")]
    public class KHlslColorOptions : DialogPage
    {
        [Category("1. 括弧"), DisplayName("レインボー括弧")]
        [Description("( ) [ ] { } を、入れ子の深さで色分けする。OFF にすると、演算子と同じ色になる。")]
        public bool Rainbow { get; set; } = true;

        [Category("1. 括弧"), DisplayName("対応しない括弧を赤くする")]
        [Description("対応する括弧のない ) ] } の背景を、薄い赤にする。")]
        public bool RainbowError { get; set; } = true;

        [Category("3. 専用色の ON / OFF"), DisplayName("制御キーワードの専用色")]
        [Description("OFF にすると、キーワードの色になる。")]
        public bool Control { get; set; } = true;

        [Category("3. 専用色の ON / OFF"), DisplayName("#include などの専用色")]
        [Description("OFF にすると、キーワードの色になる。")]
        public bool Preprocessor { get; set; } = true;

        [Category("3. 専用色の ON / OFF"), DisplayName("組み込み関数の専用色")]
        [Description("OFF にすると、独自の関数と同じ色になる。")]
        public bool Intrinsic { get; set; } = true;

        [Category("3. 専用色の ON / OFF"), DisplayName("public / private などの専用色")]
        [Description("OFF にすると、キーワードの色になる。")]
        public bool Visibility { get; set; } = true;

        [Category("3. 専用色の ON / OFF"), DisplayName("文字列のエスケープの専用色")]
        [Description("OFF にすると、文字列と同じ色になる。")]
        public bool Escape { get; set; } = true;

        [Category("3. 専用色の ON / OFF"), DisplayName("書式指定子の専用色")]
        [Description("OFF にすると、文字列と同じ色になる。")]
        public bool FormatSpec { get; set; } = true;

        [Category("3. 専用色の ON / OFF"), DisplayName("型・名前空間・ラベルの色分け")]
        [Description("OFF にすると、普通の識別子の色になる。")]
        public bool Types { get; set; } = true;

        [Category("3. 専用色の ON / OFF"), DisplayName("関数の色分け")]
        [Description("OFF にすると、普通の識別子の色になる。")]
        public bool Functions { get; set; } = true;

        [Category("3. 専用色の ON / OFF"), DisplayName("変数のスコープ別の色分け")]
        [Description("引数・ローカル・メンバー・グローバルを別の色にする。OFF にすると、すべて普通の識別子の色になる。")]
        public bool Variables { get; set; } = true;

        [Category("3. 専用色の ON / OFF"), DisplayName("マクロの色分け")]
        [Description("OFF にすると、普通の識別子の色になる。")]
        public bool Macros { get; set; } = true;

        [Category("3. 専用色の ON / OFF"), DisplayName("列挙子・セマンティクス・属性の色分け")]
        [Description("OFF にすると、普通の識別子の色になる。")]
        public bool Enumerators { get; set; } = true;

        [Category("4. キーワードと関数の色"), DisplayName("制御キーワード")]
        [Description("if for return など。既定は #D8A0DF")]
        public Color ColorControl { get; set; }

        [Category("4. キーワードと関数の色"), DisplayName("#include などのディレクティブ")]
        [Description("#include #define など。既定は #9B9B9B")]
        public Color ColorPreprocessor { get; set; }

        [Category("4. キーワードと関数の色"), DisplayName("組み込み関数")]
        [Description("mul saturate Sample など。既定は #E8892B")]
        public Color ColorIntrinsic { get; set; }

        [Category("4. キーワードと関数の色"), DisplayName("public / private など")]
        [Description("public private protected friend。既定は #696969")]
        public Color ColorVisibility { get; set; }

        [Category("5. 文字列の中の色"), DisplayName("文字列のエスケープ")]
        [Description("\n \x41 など。既定は #FF00FF")]
        public Color ColorEscape { get; set; }

        [Category("5. 文字列の中の色"), DisplayName("書式指定子")]
        [Description("%d %5.2f など。既定は #7B68EE")]
        public Color ColorFormat { get; set; }

        [Category("2. レインボー括弧の色"), DisplayName("レインボー括弧 1 番目")]
        [Description("最も外側の括弧。既定は #FF9900")]
        public Color ColorRainbow1 { get; set; }

        [Category("2. レインボー括弧の色"), DisplayName("レインボー括弧 2 番目")]
        [Description("既定は #FF1493")]
        public Color ColorRainbow2 { get; set; }

        [Category("2. レインボー括弧の色"), DisplayName("レインボー括弧 3 番目")]
        [Description("既定は #9ACD32")]
        public Color ColorRainbow3 { get; set; }

        [Category("2. レインボー括弧の色"), DisplayName("レインボー括弧 4 番目")]
        [Description("既定は #9400D3")]
        public Color ColorRainbow4 { get; set; }

        [Category("7. コメント・リテラルなどの色(空欄は、VS の C++ と同じ色)"), DisplayName("コメント")]
        [Description("VS の C++ の色を借りている")]
        public Color ColorComment { get; set; }

        [Category("7. コメント・リテラルなどの色(空欄は、VS の C++ と同じ色)"), DisplayName("文字列")]
        [Description("VS の C++ の色を借りている")]
        public Color ColorString { get; set; }

        [Category("7. コメント・リテラルなどの色(空欄は、VS の C++ と同じ色)"), DisplayName("数値")]
        [Description("VS の C++ の色を借りている")]
        public Color ColorNumber { get; set; }

        [Category("7. コメント・リテラルなどの色(空欄は、VS の C++ と同じ色)"), DisplayName("演算子")]
        [Description("VS の C++ の色を借りている")]
        public Color ColorOperator { get; set; }

        [Category("4. キーワードと関数の色"), DisplayName("キーワード(float struct など)")]
        [Description("VS の C++ の色を借りている")]
        public Color ColorKeyword { get; set; }

        [Category("6. 名前の色(空欄は、VS の C++ と同じ色)"), DisplayName("型")]
        [Description("VS の C++ の色を借りている")]
        public Color ColorType { get; set; }

        [Category("6. 名前の色(空欄は、VS の C++ と同じ色)"), DisplayName("名前空間")]
        [Description("VS の C++ の色を借りている")]
        public Color ColorNamespace { get; set; }

        [Category("6. 名前の色(空欄は、VS の C++ と同じ色)"), DisplayName("ラベル")]
        [Description("VS の C++ の色を借りている")]
        public Color ColorLabel { get; set; }

        [Category("6. 名前の色(空欄は、VS の C++ と同じ色)"), DisplayName("関数")]
        [Description("VS の C++ の色を借りている")]
        public Color ColorFunction { get; set; }

        [Category("6. 名前の色(空欄は、VS の C++ と同じ色)"), DisplayName("メンバー関数")]
        [Description("VS の C++ の色を借りている")]
        public Color ColorMemberfunc { get; set; }

        [Category("6. 名前の色(空欄は、VS の C++ と同じ色)"), DisplayName("引数")]
        [Description("VS の C++ の色を借りている")]
        public Color ColorParam { get; set; }

        [Category("6. 名前の色(空欄は、VS の C++ と同じ色)"), DisplayName("ローカル変数")]
        [Description("VS の C++ の色を借りている")]
        public Color ColorLocal { get; set; }

        [Category("6. 名前の色(空欄は、VS の C++ と同じ色)"), DisplayName("メンバー変数")]
        [Description("VS の C++ の色を借りている")]
        public Color ColorMember { get; set; }

        [Category("6. 名前の色(空欄は、VS の C++ と同じ色)"), DisplayName("グローバル変数")]
        [Description("VS の C++ の色を借りている")]
        public Color ColorGlobal { get; set; }

        [Category("6. 名前の色(空欄は、VS の C++ と同じ色)"), DisplayName("マクロ")]
        [Description("VS の C++ の色を借りている")]
        public Color ColorMacro { get; set; }

        [Category("6. 名前の色(空欄は、VS の C++ と同じ色)"), DisplayName("列挙子")]
        [Description("VS の C++ の色を借りている")]
        public Color ColorEnumerator { get; set; }

        [Category("6. 名前の色(空欄は、VS の C++ と同じ色)"), DisplayName("セマンティクス(SV_Position など)")]
        [Description("VS の C++ の色を借りている")]
        public Color ColorSemantic { get; set; }

        [Category("6. 名前の色(空欄は、VS の C++ と同じ色)"), DisplayName("属性([numthreads] など)")]
        [Description("VS の C++ の色を借りている")]
        public Color ColorAttribute { get; set; }

        [Category("6. 名前の色(空欄は、VS の C++ と同じ色)"), DisplayName("その他の識別子")]
        [Description("VS の C++ の色を借りている")]
        public Color ColorIdentifier { get; set; }

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
            ColorControl = KHlslSettings.GetColorValue("color.control", "#D8A0DF");
            ColorPreprocessor = KHlslSettings.GetColorValue("color.preprocessor", "#9B9B9B");
            ColorIntrinsic = KHlslSettings.GetColorValue("color.intrinsic", "#E8892B");
            ColorVisibility = KHlslSettings.GetColorValue("color.visibility", "#696969");
            ColorEscape = KHlslSettings.GetColorValue("color.escape", "#FF00FF");
            ColorFormat = KHlslSettings.GetColorValue("color.format", "#7B68EE");
            ColorRainbow1 = KHlslSettings.GetColorValue("color.rainbow1", "#FF9900");
            ColorRainbow2 = KHlslSettings.GetColorValue("color.rainbow2", "#FF1493");
            ColorRainbow3 = KHlslSettings.GetColorValue("color.rainbow3", "#9ACD32");
            ColorRainbow4 = KHlslSettings.GetColorValue("color.rainbow4", "#9400D3");
            ColorComment = KHlslSettings.GetColorValue("color.comment", null);
            ColorString = KHlslSettings.GetColorValue("color.string", null);
            ColorNumber = KHlslSettings.GetColorValue("color.number", null);
            ColorOperator = KHlslSettings.GetColorValue("color.operator", null);
            ColorKeyword = KHlslSettings.GetColorValue("color.keyword", null);
            ColorType = KHlslSettings.GetColorValue("color.type", null);
            ColorNamespace = KHlslSettings.GetColorValue("color.namespace", null);
            ColorLabel = KHlslSettings.GetColorValue("color.label", null);
            ColorFunction = KHlslSettings.GetColorValue("color.function", null);
            ColorMemberfunc = KHlslSettings.GetColorValue("color.memberfunc", null);
            ColorParam = KHlslSettings.GetColorValue("color.param", null);
            ColorLocal = KHlslSettings.GetColorValue("color.local", null);
            ColorMember = KHlslSettings.GetColorValue("color.member", null);
            ColorGlobal = KHlslSettings.GetColorValue("color.global", null);
            ColorMacro = KHlslSettings.GetColorValue("color.macro", null);
            ColorEnumerator = KHlslSettings.GetColorValue("color.enumerator", null);
            ColorSemantic = KHlslSettings.GetColorValue("color.semantic", null);
            ColorAttribute = KHlslSettings.GetColorValue("color.attribute", null);
            ColorIdentifier = KHlslSettings.GetColorValue("color.identifier", null);
        }

        public override void SaveSettingsToStorage()
        {
            var d = new Dictionary<string, string>();
            d[KHlslSettings.Rainbow] = Rainbow ? "1" : "0";
            d[KHlslSettings.RainbowError] = RainbowError ? "1" : "0";
            d[KHlslSettings.Control] = Control ? "1" : "0";
            d[KHlslSettings.Preprocessor] = Preprocessor ? "1" : "0";
            d[KHlslSettings.Intrinsic] = Intrinsic ? "1" : "0";
            d[KHlslSettings.Visibility] = Visibility ? "1" : "0";
            d[KHlslSettings.Escape] = Escape ? "1" : "0";
            d[KHlslSettings.FormatSpec] = FormatSpec ? "1" : "0";
            d[KHlslSettings.Types] = Types ? "1" : "0";
            d[KHlslSettings.Functions] = Functions ? "1" : "0";
            d[KHlslSettings.Variables] = Variables ? "1" : "0";
            d[KHlslSettings.Macros] = Macros ? "1" : "0";
            d[KHlslSettings.Enumerators] = Enumerators ? "1" : "0";
            d["color.control"] = KHlslSettings.ToHex(ColorControl, "#D8A0DF");
            d["color.preprocessor"] = KHlslSettings.ToHex(ColorPreprocessor, "#9B9B9B");
            d["color.intrinsic"] = KHlslSettings.ToHex(ColorIntrinsic, "#E8892B");
            d["color.visibility"] = KHlslSettings.ToHex(ColorVisibility, "#696969");
            d["color.escape"] = KHlslSettings.ToHex(ColorEscape, "#FF00FF");
            d["color.format"] = KHlslSettings.ToHex(ColorFormat, "#7B68EE");
            d["color.rainbow1"] = KHlslSettings.ToHex(ColorRainbow1, "#FF9900");
            d["color.rainbow2"] = KHlslSettings.ToHex(ColorRainbow2, "#FF1493");
            d["color.rainbow3"] = KHlslSettings.ToHex(ColorRainbow3, "#9ACD32");
            d["color.rainbow4"] = KHlslSettings.ToHex(ColorRainbow4, "#9400D3");
            d["color.comment"] = KHlslSettings.ToHex(ColorComment, null);
            d["color.string"] = KHlslSettings.ToHex(ColorString, null);
            d["color.number"] = KHlslSettings.ToHex(ColorNumber, null);
            d["color.operator"] = KHlslSettings.ToHex(ColorOperator, null);
            d["color.keyword"] = KHlslSettings.ToHex(ColorKeyword, null);
            d["color.type"] = KHlslSettings.ToHex(ColorType, null);
            d["color.namespace"] = KHlslSettings.ToHex(ColorNamespace, null);
            d["color.label"] = KHlslSettings.ToHex(ColorLabel, null);
            d["color.function"] = KHlslSettings.ToHex(ColorFunction, null);
            d["color.memberfunc"] = KHlslSettings.ToHex(ColorMemberfunc, null);
            d["color.param"] = KHlslSettings.ToHex(ColorParam, null);
            d["color.local"] = KHlslSettings.ToHex(ColorLocal, null);
            d["color.member"] = KHlslSettings.ToHex(ColorMember, null);
            d["color.global"] = KHlslSettings.ToHex(ColorGlobal, null);
            d["color.macro"] = KHlslSettings.ToHex(ColorMacro, null);
            d["color.enumerator"] = KHlslSettings.ToHex(ColorEnumerator, null);
            d["color.semantic"] = KHlslSettings.ToHex(ColorSemantic, null);
            d["color.attribute"] = KHlslSettings.ToHex(ColorAttribute, null);
            d["color.identifier"] = KHlslSettings.ToHex(ColorIdentifier, null);
            KHlslSettings.Save(d);
        }
    }
}
