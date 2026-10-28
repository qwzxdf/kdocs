using System;
using System.Collections.Generic;
using System.IO;

namespace KHlsl.Vsix
{
    /// <summary>
    /// 色の項目ごとの ON / OFF。パッケージが読み込まれる前にも、分類器から読めるように、
    /// %LOCALAPPDATA%\K-HLSL\colors.txt に「キー=0/1」で保存する(書いていない項目は ON)。
    /// OFF にした項目は、専用の色をやめて、近い標準の色(識別子・キーワード・演算子・文字列)になる。
    /// </summary>
    internal static class KHlslSettings
    {
        public const string Rainbow = "rainbow";
        public const string RainbowError = "rainbowError";
        public const string Control = "control";
        public const string Preprocessor = "preprocessor";
        public const string Intrinsic = "intrinsic";
        public const string Visibility = "visibility";
        public const string Escape = "escape";
        public const string FormatSpec = "formatSpec";
        public const string Types = "types";
        public const string Functions = "functions";
        public const string Variables = "variables";
        public const string Macros = "macros";
        public const string Enumerators = "enumerators";

        // 色(#RRGGBB。空欄は既定の色)
        public const string ColorControl = "color.control";
        public const string ColorPreprocessor = "color.preprocessor";
        public const string ColorIntrinsic = "color.intrinsic";
        public const string ColorVisibility = "color.visibility";
        public const string ColorEscape = "color.escape";
        public const string ColorFormat = "color.format";
        public const string ColorRainbow1 = "color.rainbow1";
        public const string ColorRainbow2 = "color.rainbow2";
        public const string ColorRainbow3 = "color.rainbow3";
        public const string ColorRainbow4 = "color.rainbow4";

        public static readonly string[] ColorKeys =
        {
            "color.control",
            "color.preprocessor",
            "color.intrinsic",
            "color.visibility",
            "color.escape",
            "color.format",
            "color.rainbow1",
            "color.rainbow2",
            "color.rainbow3",
            "color.rainbow4",
            "color.comment",
            "color.string",
            "color.number",
            "color.operator",
            "color.keyword",
            "color.type",
            "color.namespace",
            "color.label",
            "color.function",
            "color.memberfunc",
            "color.param",
            "color.local",
            "color.member",
            "color.global",
            "color.macro",
            "color.enumerator",
            "color.semantic",
            "color.attribute",
            "color.identifier"
        };

        public static readonly string[] Keys =
        {
            Rainbow, RainbowError, Control, Preprocessor, Intrinsic, Visibility, Escape, FormatSpec,
            Types, Functions, Variables, Macros, Enumerators
        };

        private static readonly string FilePath = Path.Combine(
            Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "K-HLSL", "colors.txt");

        private static readonly object Gate = new object();
        private static Dictionary<string, string> _values;

        /// <summary>保存したあとに呼ばれる。分類器が色を引き直す。</summary>
        public static event EventHandler Changed;

        public static bool IsOn(string key)
        {
            lock (Gate)
            {
                if (_values == null) _values = Load();
                string v;
                return !_values.TryGetValue(key, out v) || v != "0";
            }
        }

        /// <summary>色(#RRGGBB)。空欄・不正な値は空文字。</summary>
        public static string GetColor(string key)
        {
            lock (Gate)
            {
                if (_values == null) _values = Load();
                string v;
                if (!_values.TryGetValue(key, out v)) return "";
                v = (v ?? "").Trim();
                return System.Text.RegularExpressions.Regex.IsMatch(v, "^#[0-9A-Fa-f]{6}$") ? v : "";
            }
        }

        /// <summary>設定ページに出す色。保存した色が無ければ、既定の色(既定が無ければ空欄 = Color.Empty)。</summary>
        public static System.Drawing.Color GetColorValue(string key, string defaultHex)
        {
            string c = GetColor(key);
            if (c.Length == 0) c = defaultHex ?? "";
            return c.Length == 0 ? System.Drawing.Color.Empty : System.Drawing.ColorTranslator.FromHtml(c);
        }

        /// <summary>保存する値。空欄と、既定と同じ色は、空文字(既定のまま)。</summary>
        public static string ToHex(System.Drawing.Color c, string defaultHex)
        {
            if (c.IsEmpty || c.A == 0) return "";
            string hex = string.Format("#{0:X2}{1:X2}{2:X2}", c.R, c.G, c.B);
            return string.Equals(hex, defaultHex, StringComparison.OrdinalIgnoreCase) ? "" : hex;
        }

        public static void Save(IDictionary<string, string> values)
        {
            lock (Gate)
            {
                _values = new Dictionary<string, string>(values);
                try
                {
                    Directory.CreateDirectory(Path.GetDirectoryName(FilePath));
                    var lines = new List<string>();
                    foreach (var k in Keys)
                    {
                        string v;
                        lines.Add(k + "=" + (!_values.TryGetValue(k, out v) || v != "0" ? "1" : "0"));
                    }
                    foreach (var k in ColorKeys)
                    {
                        string v;
                        lines.Add(k + "=" + (_values.TryGetValue(k, out v) ? (v ?? "").Trim() : ""));
                    }
                    File.WriteAllLines(FilePath, lines);
                }
                catch (Exception ex) { KHlslPackage.Log("colors.txt の保存に失敗: " + ex.Message); }
            }
            var h = Changed;
            if (h != null) h(null, EventArgs.Empty);
        }

        private static Dictionary<string, string> Load()
        {
            var d = new Dictionary<string, string>();
            try
            {
                if (File.Exists(FilePath))
                    foreach (var line in File.ReadAllLines(FilePath))
                    {
                        int i = line.IndexOf('=');
                        if (i > 0) d[line.Substring(0, i).Trim()] = line.Substring(i + 1).Trim();
                    }
            }
            catch (Exception) { }
            return d;
        }
    }
}
