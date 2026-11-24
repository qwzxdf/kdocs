using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Xml.Linq;

namespace KCppAssist
{
    /// <summary>
    /// プロジェクトのプロパティ ページの「構成プロパティ」に、「よく使うプロパティ」のページを足す。
    /// 項目は新しい値ではなく、C/C++・リンカーなどにある元のプロパティの窓口(DataSource を元と同じにする)なので、
    /// ここで変えると .vcxproj の同じ要素が書き換わり、元のページと常に同じ値になる。
    /// 規則 XML は VS 自身の cl.xml などから項目の定義を写して作る(説明文・選択肢が VS の言語・版のままになる)。
    /// 規則は %LOCALAPPDATA%\K-CppAssist\KCommonProps.xml に書き、ユーザーの Microsoft.Cpp.(プラットフォーム).user.props から読み込ませる。
    /// </summary>
    internal static class CommonProps
    {
        private const string Ns = "http://schemas.microsoft.com/build/2009/properties";
        private const string Begin = "<!-- K-CppUltimateAssist begin -->";
        private const string End = "<!-- K-CppUltimateAssist end -->";
        private static readonly string[] Platforms = { "x64", "Win32", "ARM64" };

        // (規則の XML, 規則名, 取り込む項目)。順番がそのままページの順番になる。
        private sealed class Source
        {
            public string File, Rule, ItemType, Title;      // Title: ページ内の見出し(null なら、元の規則の名前)。同じ Title は 1 つにまとまる
            public string[] Names;
        }

        private static readonly Source[] Sources =
        {
            new Source { File = "cl.xml", Rule = "CL", Title = "外部ライブラリ", Names = new[] { "AdditionalIncludeDirectories" } },
            new Source { File = "link.xml", Rule = "Link", Title = "外部ライブラリ", Names = new[] { "AdditionalLibraryDirectories", "AdditionalDependencies" } },
            new Source { File = "general.xml", Rule = "ConfigurationGeneral", Names = new[] { "ConfigurationType", "PlatformToolset", "CharacterSet", "OutDir", "IntDir" } },
            new Source { File = "cl.xml", Rule = "CL", Names = new[] { "LanguageStandard", "LanguageStandard_C", "ConformanceMode", "WarningLevel", "SDLCheck",
                "MultiProcessorCompilation", "PreprocessorDefinitions", "ForcedIncludeFiles", "DisableSpecificWarnings",
                "PrecompiledHeader", "PrecompiledHeaderFile", "AdditionalOptions" } },
            new Source { File = "link.xml", Rule = "Link", Names = new[] { "SubSystem", "EntryPointSymbol" } },
            new Source { File = "mt.xml", Rule = "Manifest", Names = new[] { "EnableSegmentHeap", "AdditionalManifestFiles" } },
            new Source { File = "build_events.xml", Rule = "ConfigurationBuildEvents", Names = new[] { "PostBuildCommand", "PostBuildMessage" } },
        };

        /// <summary>規則とユーザーの props を作る(または、設定が切ってあれば消す)。VS の起動時に、バックグラウンドで呼ぶ。</summary>
        public static void Apply(bool enabled)
        {
            try
            {
                string local = Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData);
                string ruleFile = Path.Combine(local, "K-CppAssist", "KCommonProps.xml");
                string userDir = Path.Combine(local, "Microsoft", "MSBuild", "v4.0");

                string xml = enabled ? BuildRule() : null;
                if (enabled && xml == null) { KCppAssistPackage.Log("common props: VC rule files not found, skipped"); return; }
                if (enabled)
                {
                    Directory.CreateDirectory(Path.GetDirectoryName(ruleFile));
                    WriteIfChanged(ruleFile, xml, new System.Text.UTF8Encoding(true));
                }
                foreach (string p in Platforms) UpdateUserProps(Path.Combine(userDir, "Microsoft.Cpp." + p + ".user.props"), enabled ? ruleFile : null);
                KCppAssistPackage.Log("common props: " + (enabled ? "installed" : "removed"));
            }
            catch (Exception ex) { KCppAssistPackage.Log("common props failed: " + ex.Message); }
        }

        /// <summary>VS の MSBuild\Microsoft\VC\vNNN\(言語番号) を探す。実行中の devenv.exe の場所から上がって行く。</summary>
        private static string FindRuleDir()
        {
            string dir = AppContext.BaseDirectory;
            for (int i = 0; i < 2 && dir != null; i++) dir = Path.GetDirectoryName(dir.TrimEnd('\\'));   // ...\Common7\IDE → インストール先
            if (dir == null) return null;
            string vc = Path.Combine(dir, "MSBuild", "Microsoft", "VC");
            if (!Directory.Exists(vc)) return null;
            string ver = Directory.GetDirectories(vc, "v*").OrderByDescending(d => d, StringComparer.OrdinalIgnoreCase).FirstOrDefault(d => Directory.Exists(Path.Combine(d, "1033")) || Directory.GetDirectories(d).Any(x => File.Exists(Path.Combine(x, "cl.xml"))));
            if (ver == null) return null;
            string lcid = CultureInfo.InstalledUICulture.LCID.ToString(CultureInfo.InvariantCulture);
            string byLang = Path.Combine(ver, lcid);
            if (File.Exists(Path.Combine(byLang, "cl.xml"))) return byLang;
            string en = Path.Combine(ver, "1033");
            return File.Exists(Path.Combine(en, "cl.xml")) ? en : null;
        }

        private static string BuildRule()
        {
            string dir = FindRuleDir();
            if (dir == null) return null;
            XNamespace x = Ns;
            var categories = new XElement(x + "Rule.Categories");
            var props = new List<XElement>();
            var catNames = new Dictionary<string, string>();
            foreach (Source s in Sources)
            {
                string path = Path.Combine(dir, s.File);
                if (!File.Exists(path)) continue;
                XElement rule = XDocument.Load(path).Root;
                if (rule == null) continue;
                // 規則の DataSource(Persistence・ItemType・ラベル)は、項目が自分の DataSource を持たないときに、項目へ移す
                XElement ruleSource = rule.Elements(x + "Rule.DataSource").Elements(x + "DataSource").FirstOrDefault();
                string title = s.Title != null ? L.T(s.Title) : ((string)rule.Attribute("DisplayName") ?? s.Rule);
                string catName;
                bool newCategory = !catNames.TryGetValue(title, out catName);
                if (newCategory) catName = "K" + catNames.Count.ToString(CultureInfo.InvariantCulture);
                int before = props.Count;
                foreach (string name in s.Names)
                {
                    XElement src = rule.Elements().FirstOrDefault(e => (string)e.Attribute("Name") == name && e.Name.LocalName.EndsWith("Property", StringComparison.Ordinal) && Matches(e, s.ItemType));
                    if (src == null) continue;
                    var copy = new XElement(src);
                    copy.SetAttributeValue("Category", catName);
                    copy.SetAttributeValue("Visible", null);
                    if (!copy.Elements().Any(e => e.Name.LocalName.EndsWith(".DataSource", StringComparison.Ordinal)) && ruleSource != null)
                        copy.AddFirst(new XElement(x + (copy.Name.LocalName + ".DataSource"), new XElement(ruleSource)));
                    props.Add(copy);
                }
                if (props.Count == before || !newCategory) continue;
                catNames[title] = catName;
                categories.Add(new XElement(x + "Category", new XAttribute("Name", catName), new XAttribute("DisplayName", title), new XAttribute("Description", title)));
            }
            if (props.Count == 0) return null;

            string pageName = L.T("よく使うプロパティ");
            var root = new XElement(x + "Rule",
                new XAttribute("Name", "KCppAssistCommon"), new XAttribute("DisplayName", pageName),
                new XAttribute("PageTemplate", "generic"), new XAttribute("Description", pageName), new XAttribute("Order", "-1"),
                categories,
                new XElement(x + "Rule.DataSource", new XElement(x + "DataSource", new XAttribute("Persistence", "ProjectFile"))));
            foreach (XElement p in props) root.Add(p);
            return new XDocument(new XDeclaration("1.0", "utf-8", null), root).ToString();
        }

        // 同じ名前の項目が複数の規則にあるとき(ビルド イベントの Command など)は、ItemType で選ぶ
        private static bool Matches(XElement prop, string itemType)
        {
            if (itemType == null) return true;
            return prop.Descendants().Any(e => e.Name.LocalName == "DataSource" && (string)e.Attribute("ItemType") == itemType);
        }

        // user.props の中の、目印で挟んだ区間だけを入れ替える(ほかの内容は触らない)。ruleFile が null なら区間を消す
        private static void UpdateUserProps(string path, string ruleFile)
        {
            string block = ruleFile == null ? null :
                "  " + Begin + "\n  <ItemGroup>\n    <PropertyPageSchema Include=\"" + System.Security.SecurityElement.Escape(ruleFile) + "\" />\n  </ItemGroup>\n  " + End + "\n";
            string text = File.Exists(path) ? File.ReadAllText(path) : null;
            if (text == null)
            {
                if (block == null) return;
                text = "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n<Project ToolsVersion=\"4.0\" xmlns=\"http://schemas.microsoft.com/developer/msbuild/2003\">\n" + block + "</Project>\n";
                Directory.CreateDirectory(Path.GetDirectoryName(path));
                File.WriteAllText(path, text, new System.Text.UTF8Encoding(false));
                return;
            }
            int b = text.IndexOf(Begin, StringComparison.Ordinal);
            int e = text.IndexOf(End, StringComparison.Ordinal);
            string result;
            if (b >= 0 && e > b)
            {
                int bs = text.LastIndexOf('\n', b) + 1;                       // 区間の行頭から
                int ee = text.IndexOf('\n', e);
                ee = ee < 0 ? text.Length : ee + 1;                           // 区間の行末まで
                result = text.Substring(0, bs) + (block ?? "") + text.Substring(ee);
            }
            else
            {
                if (block == null) return;
                int close = text.LastIndexOf("</Project>", StringComparison.Ordinal);
                if (close < 0) return;                                        // 形が分からないファイルは触らない
                result = text.Substring(0, close) + block + text.Substring(close);
            }
            if (result != text) File.WriteAllText(path, result, new System.Text.UTF8Encoding(false));
        }

        private static void WriteIfChanged(string path, string content, System.Text.Encoding enc)
        {
            if (File.Exists(path) && File.ReadAllText(path) == content) return;
            File.WriteAllText(path, content, enc);
        }
    }
}
