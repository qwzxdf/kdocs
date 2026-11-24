using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Controls.Primitives;
using System.Windows.Documents;
using System.Windows.Markup;
using System.Windows.Media;
using Microsoft.VisualStudio.PlatformUI;

namespace KCppAssist.Vcpkg
{
    /// <summary>一覧の 1 行。ListBox の DataTemplate から、プロパティの名前で引く。</summary>
    internal sealed class Row
    {
        public string Rank { get; set; }
        public string Name { get; set; }
        public string Version { get; set; }
        public string Mark { get; set; }
        public string Desc { get; set; }
        public string Extra { get; set; }
        public string Status { get; set; }
        public Brush StatusBrush { get; set; }
        public PortInfo Port;
    }

    /// <summary>vcpkg.json の置き場所の候補(置き場所の選択欄の 1 件)。</summary>
    internal sealed class Target
    {
        public string Display;
        public string Dir;          // vcpkg.json を置くフォルダ
        public bool IsNew;          // まだ vcpkg.json がない
        public override string ToString() { return Display; }
    }

    /// <summary>
    /// vcpkg のパッケージ ブラウザー(NuGet のパッケージ マネージャー風)。「参照」「インストール済み」「更新」の 3 つのタブと、下のログ欄。
    /// 見た目は Fluent 風(FluentStyles)。部品はすべてこのファイルで組み立てる(XAML のファイルは使わない)。色は VS のテーマに合わせて、変わるたびに作り直す。
    /// </summary>
    internal sealed class VcpkgView : UserControl
    {
        private const string RowTemplate = @"
<DataTemplate xmlns='http://schemas.microsoft.com/winfx/2006/xaml/presentation'>
  <Grid>
    <Grid.ColumnDefinitions><ColumnDefinition Width='44'/><ColumnDefinition Width='*'/></Grid.ColumnDefinitions>
    <Border Background='{DynamicResource HoverBrush}' CornerRadius='5' Height='22' Width='36' VerticalAlignment='Top' Margin='0,1,0,0'>
      <TextBlock Text='{Binding Rank}' HorizontalAlignment='Center' VerticalAlignment='Center' FontSize='11' Foreground='{DynamicResource SubBrush}'/>
    </Border>
    <StackPanel Grid.Column='1'>
      <StackPanel Orientation='Horizontal'>
        <TextBlock Text='{Binding Name}' FontWeight='SemiBold' FontSize='14'/>
        <TextBlock Text='{Binding Version}' Foreground='{DynamicResource SubBrush}' Margin='10,2,0,0' FontSize='12'/>
        <TextBlock Text='{Binding Mark}' Foreground='{DynamicResource OkBrush}' Margin='10,2,0,0' FontSize='12'/>
      </StackPanel>
      <TextBlock Text='{Binding Desc}' TextTrimming='CharacterEllipsis' Foreground='{DynamicResource SubBrush}' Margin='0,2,0,0'/>
    </StackPanel>
  </Grid>
</DataTemplate>";

        private const string StatusTemplate = @"
<DataTemplate xmlns='http://schemas.microsoft.com/winfx/2006/xaml/presentation'>
  <Grid>
    <Grid.ColumnDefinitions><ColumnDefinition Width='*'/><ColumnDefinition Width='100'/><ColumnDefinition Width='110'/><ColumnDefinition Width='110'/><ColumnDefinition Width='120'/></Grid.ColumnDefinitions>
    <TextBlock Text='{Binding Name}' FontWeight='SemiBold'/>
    <TextBlock Grid.Column='1' Text='{Binding Extra}' Foreground='{DynamicResource SubBrush}'/>
    <TextBlock Grid.Column='2' Text='{Binding Version}'/>
    <TextBlock Grid.Column='3' Text='{Binding Desc}'/>
    <TextBlock Grid.Column='4' Text='{Binding Status}' Foreground='{Binding StatusBrush}' FontWeight='SemiBold'/>
  </Grid>
</DataTemplate>";

        public Func<List<KeyValuePair<string, string>>> ProjectDirs;      // (プロジェクト名, フォルダ)。VS のソリューションから取る
        public Func<string> SolutionDir;

        private List<PortInfo> _ports = new List<PortInfo>();
        private Dictionary<string, PortInfo> _byName = new Dictionary<string, PortInfo>(StringComparer.OrdinalIgnoreCase);
        private readonly Dictionary<string, string> _latest = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);   // GitHub の最新の版
        private VcpkgManifest _manifest;
        private PortInfo _selected;
        private CancellationTokenSource _cts;
        private bool _busy;
        private bool _loadingUi;
        private int _catIndex;                                         // 0 = すべて、1 以降 = VcpkgCatalog.Categories[i - 1]
        private readonly List<ToggleButton> _chips = new List<ToggleButton>();

        // 上の欄
        private readonly ComboBox _target = new ComboBox { MinWidth = 250 };
        private readonly ComboBox _triplet = new ComboBox { MinWidth = 190 };
        private readonly TextBlock _exeText = new TextBlock { FontSize = 11 };
        private readonly TabControl _tabs = new TabControl();

        // 参照
        private readonly TextBox _search = new TextBox { FontSize = 14 };
        private readonly TextBlock _searchHint = new TextBlock { IsHitTestVisible = false, Margin = new Thickness(11, 0, 0, 0), VerticalAlignment = VerticalAlignment.Center };
        private readonly ComboBox _sort = new ComboBox { MinWidth = 120 };
        private readonly WrapPanel _chipPanel = new WrapPanel { Margin = new Thickness(0, 8, 0, 0) };
        private readonly ListBox _list = new ListBox();
        private readonly TextBlock _count = new TextBlock { FontSize = 11, Margin = new Thickness(6, 6, 0, 0) };
        private readonly StackPanel _detail = new StackPanel();

        // インストール済み・更新
        private readonly ListBox _installed = new ListBox();
        private readonly ListBox _updates = new ListBox { SelectionMode = SelectionMode.Extended };
        private readonly TextBlock _installedNote = new TextBlock { TextWrapping = TextWrapping.Wrap, Margin = new Thickness(2, 0, 0, 8) };
        private readonly TextBlock _updatesNote = new TextBlock { TextWrapping = TextWrapping.Wrap, Margin = new Thickness(2, 0, 0, 8) };

        // 下の欄
        private readonly TextBox _log = new TextBox { IsReadOnly = true, VerticalScrollBarVisibility = ScrollBarVisibility.Auto, HorizontalScrollBarVisibility = ScrollBarVisibility.Auto, FontFamily = new FontFamily("Consolas"), FontSize = 12, TextWrapping = TextWrapping.NoWrap };
        private readonly ProgressBar _progress = new ProgressBar { Height = 3, IsIndeterminate = false, Visibility = Visibility.Collapsed, BorderThickness = new Thickness(0), Margin = new Thickness(0, 0, 0, 6) };
        private readonly CheckBox _chkBaseline = new CheckBox();
        private bool _baselineUi;
        private Button _btnInstall, _btnBaseline, _btnUndo, _btnCancel;
        private readonly TextBlock _hint = new TextBlock { TextWrapping = TextWrapping.Wrap, Margin = new Thickness(2, 0, 2, 6) };

        public VcpkgView()
        {
            Resources.MergedDictionaries.Add(FluentStyles.Styles);
            FluentStyles.ApplyColors(Resources);
            Padding = new Thickness(14, 10, 14, 10);
            FontSize = 13;
            Content = BuildLayout();
            Loaded += (s, e) => { VSColorTheme.ThemeChanged += OnThemeChanged; FluentStyles.ApplyColors(Resources); Start(); };
            Unloaded += (s, e) => VSColorTheme.ThemeChanged -= OnThemeChanged;
        }

        private void OnThemeChanged(ThemeChangedEventArgs e) { FluentStyles.ApplyColors(Resources); }

        // ---------- 組み立て ----------

        private static T Styled<T>(T c, string key) where T : FrameworkElement { c.SetResourceReference(FrameworkElement.StyleProperty, key); return c; }
        private static T Tinted<T>(T c, string brushKey, DependencyProperty p) where T : FrameworkElement { c.SetResourceReference(p, brushKey); return c; }

        private Button MakeButton(string ja, Action click, bool primary = false)
        {
            var b = Styled(new Button { Content = L.T(ja) }, primary ? "FPrimary" : "FButton");
            b.Click += (s, e) => click();
            return b;
        }

        private TextBlock Caption(string ja)
        {
            var t = new TextBlock { Text = L.T(ja), FontSize = 11, Margin = new Thickness(2, 0, 0, 3) };
            return Tinted(t, "SubBrush", TextBlock.ForegroundProperty);
        }

        private UIElement BuildLayout()
        {
            var root = new Grid();
            root.RowDefinitions.Add(new RowDefinition { Height = GridLength.Auto });
            root.RowDefinitions.Add(new RowDefinition { Height = new GridLength(1, GridUnitType.Star) });
            root.RowDefinitions.Add(new RowDefinition { Height = GridLength.Auto });
            root.RowDefinitions.Add(new RowDefinition { Height = new GridLength(140), MinHeight = 60 });
            Tinted(this, "BackBrush", BackgroundProperty);
            Tinted(this, "TextBrush", ForegroundProperty);

            // 上: 題名と、置き場所・トリプレット
            var top = new Grid { Margin = new Thickness(0, 0, 0, 12) };
            top.ColumnDefinitions.Add(new ColumnDefinition { Width = new GridLength(1, GridUnitType.Star) });
            top.ColumnDefinitions.Add(new ColumnDefinition { Width = GridLength.Auto });
            var title = new StackPanel();
            title.Children.Add(new TextBlock { Text = L.T("vcpkg パッケージ"), FontSize = 22, FontWeight = FontWeights.SemiBold });
            title.Children.Add(Tinted(_exeText, "SubBrush", TextBlock.ForegroundProperty));
            top.Children.Add(title);
            var pickers = new StackPanel { Orientation = Orientation.Horizontal, VerticalAlignment = VerticalAlignment.Bottom };
            var p1 = new StackPanel { Margin = new Thickness(0, 0, 12, 0) };
            p1.Children.Add(Caption("vcpkg.json の置き場所"));
            p1.Children.Add(Styled(_target, "FCombo"));
            var p2 = new StackPanel();
            p2.Children.Add(Caption("トリプレット"));
            p2.Children.Add(Styled(_triplet, "FCombo"));
            pickers.Children.Add(p1);
            pickers.Children.Add(p2);
            Grid.SetColumn(pickers, 1);
            top.Children.Add(pickers);
            _target.SelectionChanged += (s, e) => { if (!_loadingUi) OnTargetChanged(); };
            _triplet.SelectionChanged += (s, e) => { if (!_loadingUi) SaveTriplet(); };
            Grid.SetRow(top, 0);
            root.Children.Add(top);

            // タブ
            Styled(_tabs, "FTabs");
            _tabs.Items.Add(new TabItem { Header = L.T("参照"), Content = BuildBrowse() });
            _tabs.Items.Add(new TabItem { Header = L.T("インストール済み"), Content = BuildInstalled() });
            _tabs.Items.Add(new TabItem { Header = L.T("更新"), Content = BuildUpdates() });
            _tabs.SelectionChanged += (s, e) =>
            {
                if (!ReferenceEquals(e.OriginalSource, _tabs)) return;
                if (_tabs.SelectedIndex == 1) RefreshInstalled();
                else if (_tabs.SelectedIndex == 2) RefreshUpdates();
            };
            Grid.SetRow(_tabs, 1);
            root.Children.Add(_tabs);

            // 操作ボタンと進捗
            var bar = new StackPanel { Margin = new Thickness(0, 10, 0, 0) };
            var buttons = new WrapPanel();
            _btnInstall = MakeButton("インストール (vcpkg install)", () => RunInstall(), true);
            _btnBaseline = MakeButton("ベースラインを更新", () => RunBaseline());
            _btnUndo = MakeButton("元に戻す", () => UndoLast());
            _btnCancel = MakeButton("中止", () => { if (_cts != null) _cts.Cancel(); });
            _btnCancel.IsEnabled = false;
            buttons.Children.Add(_btnInstall);
            buttons.Children.Add(_btnBaseline);
            buttons.Children.Add(_btnUndo);
            buttons.Children.Add(_btnCancel);
            Styled(_chkBaseline, "FCheck");
            _chkBaseline.Content = L.T("ベースラインで版をそろえる (builtin-baseline)");
            _chkBaseline.ToolTip = L.T("入: vcpkg.json に builtin-baseline を書いて、全員が同じ版を使えるようにします。切: 書かずに、手元の vcpkg の最新のポートを使います。");
            _chkBaseline.VerticalAlignment = VerticalAlignment.Center;
            _chkBaseline.Margin = new Thickness(14, 0, 0, 0);
            _chkBaseline.Click += (s, e) => ToggleBaseline();
            buttons.Children.Add(_chkBaseline);
            bar.Children.Add(buttons);
            bar.Children.Add(_progress);
            _progress.SetResourceReference(Control.ForegroundProperty, "AccentBrush");
            _progress.SetResourceReference(Control.BackgroundProperty, "LineBrush");
            bar.Children.Add(Tinted(_hint, "AccentBrush", TextBlock.ForegroundProperty));
            Grid.SetRow(bar, 2);
            root.Children.Add(bar);

            // ログ
            Styled(_log, "FTextBox");
            _log.Padding = new Thickness(8);
            Grid.SetRow(_log, 3);
            root.Children.Add(_log);
            return root;
        }

        private Border Card(UIElement child, Thickness padding)
        {
            var b = new Border { CornerRadius = new CornerRadius(8), BorderThickness = new Thickness(1), Padding = padding, Child = child };
            b.SetResourceReference(Border.BackgroundProperty, "CardBrush");
            b.SetResourceReference(Border.BorderBrushProperty, "LineBrush");
            return b;
        }

        private UIElement BuildBrowse()
        {
            var g = new Grid();
            g.ColumnDefinitions.Add(new ColumnDefinition { Width = new GridLength(1.05, GridUnitType.Star), MinWidth = 270 });
            g.ColumnDefinitions.Add(new ColumnDefinition { Width = new GridLength(14) });
            g.ColumnDefinitions.Add(new ColumnDefinition { Width = new GridLength(1, GridUnitType.Star), MinWidth = 280 });

            var left = new Grid();
            left.RowDefinitions.Add(new RowDefinition { Height = GridLength.Auto });
            left.RowDefinitions.Add(new RowDefinition { Height = new GridLength(1, GridUnitType.Star) });
            left.RowDefinitions.Add(new RowDefinition { Height = GridLength.Auto });

            var tools = new StackPanel();
            var searchRow = new Grid();
            searchRow.ColumnDefinitions.Add(new ColumnDefinition { Width = new GridLength(1, GridUnitType.Star) });
            searchRow.ColumnDefinitions.Add(new ColumnDefinition { Width = GridLength.Auto });
            var searchHost = new Grid();
            Styled(_search, "FTextBox");
            _search.Padding = new Thickness(10, 7, 10, 7);
            _searchHint.Text = "🔍  " + L.T("名前や説明で検索");
            Tinted(_searchHint, "SubBrush", TextBlock.ForegroundProperty);
            _search.ToolTip = L.T("名前か説明の一部を入力すると、入力の途中から絞り込みます");
            _search.TextChanged += (s, e) =>
            {
                _searchHint.Visibility = _search.Text.Length == 0 ? Visibility.Visible : Visibility.Collapsed;
                if (!_loadingUi) RefreshBrowse();
            };
            searchHost.Children.Add(_search);
            searchHost.Children.Add(_searchHint);
            searchRow.Children.Add(searchHost);
            _sort.Margin = new Thickness(8, 0, 0, 0);
            _sort.Items.Add(L.T("おすすめ順"));
            _sort.Items.Add(L.T("名前順"));
            _sort.SelectedIndex = 0;
            Styled(_sort, "FCombo");
            _sort.SelectionChanged += (s, e) => { if (!_loadingUi) RefreshBrowse(); };
            Grid.SetColumn(_sort, 1);
            searchRow.Children.Add(_sort);
            tools.Children.Add(searchRow);

            Grid.SetRow(tools, 0);
            left.Children.Add(tools);

            _list.ItemTemplate = (DataTemplate)XamlReader.Parse(RowTemplate);
            Styled(_list, "FList");
            _list.SelectionChanged += (s, e) =>
            {
                var r = _list.SelectedItem as Row;
                if (r != null && r.Port != null) ShowDetail(r.Port);
            };
            Grid.SetRow(_list, 1);
            left.Children.Add(_list);
            Tinted(_count, "SubBrush", TextBlock.ForegroundProperty);
            Grid.SetRow(_count, 2);
            left.Children.Add(_count);
            g.Children.Add(left);

            var scroll = new ScrollViewer { VerticalScrollBarVisibility = ScrollBarVisibility.Auto, Content = _detail };
            _detail.Margin = new Thickness(0, 0, 4, 0);
            var card = Card(scroll, new Thickness(18, 14, 8, 14));
            Grid.SetColumn(card, 2);
            g.Children.Add(card);
            return g;
        }

        private UIElement BuildInstalled()
        {
            var g = new Grid();
            g.RowDefinitions.Add(new RowDefinition { Height = GridLength.Auto });
            g.RowDefinitions.Add(new RowDefinition { Height = GridLength.Auto });
            g.RowDefinitions.Add(new RowDefinition { Height = new GridLength(1, GridUnitType.Star) });
            g.RowDefinitions.Add(new RowDefinition { Height = GridLength.Auto });
            Tinted(_installedNote, "SubBrush", TextBlock.ForegroundProperty);
            Grid.SetRow(_installedNote, 0);
            g.Children.Add(_installedNote);
            var head = StatusHeader("名前", "指定", "入っている版", "最新の版", "状態");
            Grid.SetRow(head, 1);
            g.Children.Add(head);
            _installed.ItemTemplate = (DataTemplate)XamlReader.Parse(StatusTemplate);
            Styled(_installed, "FList");
            Grid.SetRow(_installed, 2);
            g.Children.Add(_installed);
            var btns = new WrapPanel { Margin = new Thickness(0, 10, 0, 0) };
            btns.Children.Add(MakeButton("詳細を見る", () => { var r = _installed.SelectedItem as Row; if (r != null) GoToBrowse(r.Name); }));
            btns.Children.Add(MakeButton("削除", () => RemoveSelected(_installed)));
            btns.Children.Add(MakeButton("この版以上にする", () => RaiseMinVersion(_installed)));
            Grid.SetRow(btns, 3);
            g.Children.Add(btns);
            return g;
        }

        private UIElement BuildUpdates()
        {
            var g = new Grid();
            g.RowDefinitions.Add(new RowDefinition { Height = GridLength.Auto });
            g.RowDefinitions.Add(new RowDefinition { Height = GridLength.Auto });
            g.RowDefinitions.Add(new RowDefinition { Height = new GridLength(1, GridUnitType.Star) });
            g.RowDefinitions.Add(new RowDefinition { Height = GridLength.Auto });
            Tinted(_updatesNote, "SubBrush", TextBlock.ForegroundProperty);
            Grid.SetRow(_updatesNote, 0);
            g.Children.Add(_updatesNote);
            var head = StatusHeader("名前", "指定", "入っている版", "最新の版", "状態");
            Grid.SetRow(head, 1);
            g.Children.Add(head);
            _updates.ItemTemplate = (DataTemplate)XamlReader.Parse(StatusTemplate);
            Styled(_updates, "FList");
            Grid.SetRow(_updates, 2);
            g.Children.Add(_updates);
            var btns = new WrapPanel { Margin = new Thickness(0, 10, 0, 0) };
            btns.Children.Add(MakeButton("選んだものを、この版以上にする", () => RaiseMinVersion(_updates)));
            btns.Children.Add(MakeButton("ベースラインを更新して、インストール", () => RunBaseline(true), true));
            Grid.SetRow(btns, 3);
            g.Children.Add(btns);
            return g;
        }

        private Grid StatusHeader(params string[] names)
        {
            var h = new Grid { Margin = new Thickness(10, 0, 10, 4) };
            double[] w = { 0, 100, 110, 110, 120 };
            for (int i = 0; i < names.Length; i++)
            {
                h.ColumnDefinitions.Add(new ColumnDefinition { Width = i == 0 ? new GridLength(1, GridUnitType.Star) : new GridLength(w[i]) });
                var t = Tinted(new TextBlock { Text = L.T(names[i]), FontSize = 11 }, "SubBrush", TextBlock.ForegroundProperty);
                Grid.SetColumn(t, i);
                h.Children.Add(t);
            }
            return h;
        }

        // ---------- 起動 ----------

        private void Start()
        {
            try
            {
                string exe = VcpkgTool.FindExe(true);
                _exeText.Text = exe == null ? L.T("vcpkg が見つかりません") : exe;
                LoadTargets();
                if (exe == null) { ShowNoVcpkg(); return; }
                LoadPorts(false);
            }
            catch (Exception ex) { AppendLog("error: " + ex.Message); }
        }

        private void ShowNoVcpkg()
        {
            _detail.Children.Clear();
            Heading(L.T("vcpkg が見つかりません"));
            Paragraph(L.T("次のどれかの方法で入れてから、「もう一度探す」を押してください。"));
            Paragraph(L.T("1. Visual Studio インストーラー → 「C++ によるデスクトップ開発」→ 個別のコンポーネント → 「vcpkg パッケージ マネージャー」にチェックを入れて、変更する。"), 1, 10);
            Paragraph(L.T("2. git clone https://github.com/microsoft/vcpkg を実行して、フォルダの中で bootstrap-vcpkg.bat を実行する。そのあと、環境変数 VCPKG_ROOT にそのフォルダを設定する。"), 1, 8);
            var b = Styled(new Button { Content = L.T("もう一度探す"), HorizontalAlignment = HorizontalAlignment.Left, Margin = new Thickness(0, 14, 0, 0) }, "FPrimary");
            b.Click += (s, e) => Start();
            _detail.Children.Add(b);
        }

        private async void LoadPorts(bool refresh)
        {
            if (VcpkgTool.FindExe() == null) return;
            _count.Text = L.T("一覧を読み込んでいます…");
            try
            {
                _ports = await VcpkgTool.LoadPortsAsync(refresh, _manifest != null ? _manifest.Baseline : null, CancellationToken.None);
                _byName = _ports.GroupBy(p => p.Name, StringComparer.OrdinalIgnoreCase).ToDictionary(g => g.Key, g => g.First(), StringComparer.OrdinalIgnoreCase);
                RefreshBrowse();
                if (_ports.Count == 0) { _count.Text = L.T("一覧を取得できませんでした。vcpkg の出力は、下のログを見てください。"); AppendLog(VcpkgTool.LastError ?? ""); }
            }
            catch (Exception ex) { _count.Text = ex.Message; }
        }

        // ---------- 置き場所・トリプレット ----------

        private void LoadTargets()
        {
            _loadingUi = true;
            string previous = (_target.SelectedItem as Target) != null ? ((Target)_target.SelectedItem).Dir : null;
            _target.Items.Clear();
            var seen = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
            string sol = SolutionDir != null ? SolutionDir() : null;
            var projects = ProjectDirs != null ? ProjectDirs() : new List<KeyValuePair<string, string>>();
            Func<string, string> rel = d => !string.IsNullOrEmpty(sol) && d.StartsWith(sol, StringComparison.OrdinalIgnoreCase) ? "." + d.Substring(sol.Length).TrimEnd('\\') : d;
            // vcpkg.json があるフォルダ(ソリューションと、各プロジェクトから上へたどった所)
            var starts = new List<string>();
            if (!string.IsNullOrEmpty(sol)) starts.Add(sol);
            starts.AddRange(projects.Select(p => p.Value));
            foreach (string s in starts)
            {
                string m = VcpkgLocator.FindManifestDir(s);
                if (m != null && seen.Add(m)) _target.Items.Add(new Target { Dir = m, Display = rel(m) + "\\vcpkg.json" });
            }
            // まだない所(新しく作る)
            foreach (var p in projects)
                if (VcpkgLocator.FindManifestDir(p.Value) == null && seen.Add(p.Value))
                    _target.Items.Add(new Target { Dir = p.Value, IsNew = true, Display = L.F("{0} に新しく作る ({1})", "vcpkg.json", p.Key) });
            if (!string.IsNullOrEmpty(sol) && VcpkgLocator.FindManifestDir(sol) == null && seen.Add(sol))
                _target.Items.Add(new Target { Dir = sol, IsNew = true, Display = L.F("{0} に新しく作る ({1})", "vcpkg.json", L.T("ソリューション")) });
            int idx = 0;
            for (int i = 0; i < _target.Items.Count; i++) if (((Target)_target.Items[i]).Dir == previous) { idx = i; break; }
            if (_target.Items.Count > 0) _target.SelectedIndex = idx;
            _loadingUi = false;
            OnTargetChanged();
        }

        private Target CurrentTarget { get { return _target.SelectedItem as Target; } }

        private void OnTargetChanged()
        {
            Target t = CurrentTarget;
            _manifest = null;
            if (t != null)
            {
                try { _manifest = VcpkgManifest.Load(VcpkgManifest.FileNameIn(t.Dir)); }
                catch (Exception ex) { AppendLog(L.F("vcpkg.json を読めません: {0}", ex.Message)); }
            }
            _loadingUi = true;
            string keep = _triplet.SelectedItem as string ?? LoadSavedTriplet();
            _triplet.Items.Clear();
            foreach (string name in VcpkgLocator.Triplets(t != null ? t.Dir : null)) _triplet.Items.Add(name);
            int i = _triplet.Items.IndexOf(keep ?? "x64-windows");
            if (i < 0) i = _triplet.Items.IndexOf("x64-windows");
            if (i >= 0) _triplet.SelectedIndex = i;
            _loadingUi = false;
            UpdateButtons();
            RefreshBrowse();
            if (_tabs.SelectedIndex == 1) RefreshInstalled();
            if (_tabs.SelectedIndex == 2) RefreshUpdates();
        }

        private string TripletFile { get { return Path.Combine(VcpkgTool.DataDir, "triplet.txt"); } }
        private string LoadSavedTriplet() { try { return File.Exists(TripletFile) ? File.ReadAllText(TripletFile).Trim() : null; } catch { return null; } }
        private void SaveTriplet() { try { var t = _triplet.SelectedItem as string; if (t != null) File.WriteAllText(TripletFile, t); } catch { } }
        private string Triplet { get { return _triplet.SelectedItem as string ?? "x64-windows"; } }

        private void UpdateButtons()
        {
            Target t = CurrentTarget;
            bool has = t != null && !_busy;
            _btnInstall.IsEnabled = has && _manifest != null && _manifest.Exists && VcpkgTool.FindExe() != null;
            _btnBaseline.IsEnabled = has && VcpkgTool.FindExe() != null && _manifest != null && _manifest.Exists;
            _btnUndo.IsEnabled = has && VcpkgManifest.CanUndo(VcpkgManifest.FileNameIn(t.Dir));
            _btnCancel.IsEnabled = _busy;
            _chkBaseline.IsEnabled = has && _manifest != null && _manifest.Exists && VcpkgTool.FindExe() != null;
            _chkBaseline.IsChecked = _manifest != null && _manifest.Exists && !string.IsNullOrEmpty(_manifest.Baseline);
        }

        private void ToggleBaseline()
        {
            if (_manifest == null || !_manifest.Exists) return;
            if (_chkBaseline.IsChecked == true) { RunBaseline(); return; }
            try
            {
                if (_manifest.RemoveBaseline()) { _manifest.Save(); AppendLog(L.T("builtin-baseline を、vcpkg.json から消しました (「元に戻す」で戻せます)。")); }
            }
            catch (Exception ex) { AppendLog(ex.Message); }
            RefreshAfterChange();
        }

        // ---------- 参照 ----------

        private IEnumerable<Row> BuildRows()
        {
            string q = (_search.Text ?? "").Trim();
            string cat = null;
            bool byName = _sort.SelectedIndex == 1;
            bool ja = L.Current == UiLanguage.Japanese;
            var declared = _manifest != null ? new HashSet<string>(_manifest.Dependencies().Select(d => d.Name), StringComparer.OrdinalIgnoreCase) : new HashSet<string>();

            Func<PortInfo, Featured, Row> make = (p, f) => new Row
            {
                Port = p,
                Name = p.Name,
                Version = p.Version,
                Rank = f != null ? "#" + f.Rank : "",
                Mark = declared.Contains(p.Name) ? "✔ " + L.T("追加済み") : "",
                Desc = f != null ? (ja ? f.Ja : f.En) : p.Description,
            };

            IEnumerable<Row> rows;
            if (q.Length == 0)
            {
                // 最初の画面: おすすめを順位の順に(分野を選んだら、その分野だけ)
                rows = VcpkgCatalog.All.Where(f => cat == null || f.Category == cat)
                    .Select(f => { PortInfo p; return _byName.TryGetValue(f.Name, out p) ? make(p, f) : null; })
                    .Where(r => r != null);
                if (byName) rows = rows.OrderBy(r => r.Name, StringComparer.OrdinalIgnoreCase);
            }
            else
            {
                // 検索: 名前の先頭一致 → 名前に含む → 説明に含む の順。同じ段の中は、おすすめを先に
                string[] words = q.ToLowerInvariant().Split(new[] { ' ' }, StringSplitOptions.RemoveEmptyEntries);
                var scored = new List<Tuple<int, int, PortInfo, Featured>>();
                foreach (PortInfo p in _ports)
                {
                    Featured f = VcpkgCatalog.Find(p.Name);
                    if (cat != null && (f == null || f.Category != cat)) continue;
                    string n = p.Name.ToLowerInvariant();
                    string d = (p.Description + " " + (f != null ? f.Ja + " " + f.En : "")).ToLowerInvariant();
                    if (!words.All(w => n.Contains(w) || d.Contains(w))) continue;
                    int score = words.All(w => n.StartsWith(w, StringComparison.Ordinal)) ? 0 : words.All(w => n.Contains(w)) ? 1 : 2;
                    scored.Add(Tuple.Create(score, f != null ? f.Rank : int.MaxValue, p, f));
                }
                var ordered = byName ? scored.OrderBy(t => t.Item3.Name, StringComparer.OrdinalIgnoreCase) : scored.OrderBy(t => t.Item1).ThenBy(t => t.Item2).ThenBy(t => t.Item3.Name, StringComparer.OrdinalIgnoreCase);
                rows = ordered.Select(t => make(t.Item3, t.Item4));
            }
            return rows;
        }

        private void RefreshBrowse()
        {
            if (_ports == null) return;
            string keepName = (_list.SelectedItem as Row) != null ? ((Row)_list.SelectedItem).Name : (_selected != null ? _selected.Name : null);
            var all = BuildRows().ToList();
            var rows = all.Take(400).ToList();
            _loadingUi = true;
            _list.ItemsSource = rows;
            int keep = keepName == null ? -1 : rows.FindIndex(r => r.Name == keepName);
            if (keep >= 0) _list.SelectedIndex = keep;
            _loadingUi = false;
            bool searching = !string.IsNullOrWhiteSpace(_search.Text);
            _count.Text = all.Count > rows.Count ? L.F("{0} 件のうち、先頭の {1} 件を表示", all.Count, rows.Count)
                : searching ? L.F("{0} 件", all.Count) : L.F("おすすめ {0} 件 (全体は {1} 件。検索で探せます)", all.Count, _ports.Count);
            if (_selected == null && rows.Count > 0 && keep < 0) { _list.SelectedIndex = 0; }
        }

        private void GoToBrowse(string name)
        {
            _tabs.SelectedIndex = 0;
            _search.Text = name;
            PortInfo p;
            if (_byName.TryGetValue(name, out p)) ShowDetail(p);
        }

        // 詳細の部品
        private void Heading(string text)
        {
            _detail.Children.Add(new TextBlock { Text = text, FontSize = 20, FontWeight = FontWeights.SemiBold, TextWrapping = TextWrapping.Wrap, Margin = new Thickness(0, 0, 0, 4) });
        }

        private TextBlock Paragraph(string text, double opacity = 1, double top = 4)
        {
            var t = new TextBlock { Text = text, TextWrapping = TextWrapping.Wrap, Opacity = opacity, Margin = new Thickness(0, top, 0, 0) };
            _detail.Children.Add(t);
            return t;
        }

        private TextBlock Section(string text, double top = 16)
        {
            var t = new TextBlock { Text = text, FontWeight = FontWeights.SemiBold, FontSize = 14, Margin = new Thickness(0, top, 0, 2) };
            _detail.Children.Add(t);
            return t;
        }

        private void OpenUrl(string url)
        {
            Uri uri;
            if (!Uri.TryCreate(url, UriKind.Absolute, out uri) || (uri.Scheme != "https" && uri.Scheme != "http")) return;
            try { Process.Start(new ProcessStartInfo(uri.AbsoluteUri) { UseShellExecute = true }); } catch { }
        }

        private async void ShowDetail(PortInfo port)
        {
            _selected = port;
            Featured f = VcpkgCatalog.Find(port.Name);
            bool ja = L.Current == UiLanguage.Japanese;
            _detail.Children.Clear();

            // 題名と版
            var head = new StackPanel { Orientation = Orientation.Horizontal };
            head.Children.Add(new TextBlock { Text = port.Name, FontSize = 22, FontWeight = FontWeights.SemiBold, VerticalAlignment = VerticalAlignment.Center });
            var pill = new Border { CornerRadius = new CornerRadius(10), Padding = new Thickness(9, 1, 9, 2), Margin = new Thickness(12, 3, 0, 0), VerticalAlignment = VerticalAlignment.Center, Child = Tinted(new TextBlock { Text = port.Version, FontSize = 12 }, "SubBrush", TextBlock.ForegroundProperty) };
            pill.SetResourceReference(Border.BackgroundProperty, "HoverBrush");
            head.Children.Add(pill);
            _detail.Children.Add(head);
            if (f != null)
            {
                Tinted(Paragraph(L.F("おすすめ #{0}", f.Rank), 1, 4), "AccentBrush", TextBlock.ForegroundProperty);
                Paragraph(ja ? f.Ja : f.En, 1, 10);
                if (!string.IsNullOrEmpty(port.Description)) Tinted(Paragraph(port.Description, 1, 4), "SubBrush", TextBlock.ForegroundProperty);
            }
            else if (!string.IsNullOrEmpty(port.Description)) Paragraph(port.Description, 1, 10);

            var detailSlot = new StackPanel();          // ホームページなど(GitHub から取れたら埋める)
            _detail.Children.Add(detailSlot);

            // 機能
            Dependency existing = _manifest != null ? _manifest.Find(port.Name) : null;
            var checks = new List<CheckBox>();
            CheckBox defaults = null;
            StackPanel featurePanel = null;
            if (port.Features.Count > 0)
            {
                Section(L.T("機能 (feature)"));
                defaults = Styled(new CheckBox { Content = L.T("既定の機能を使う (default-features)"), IsChecked = existing == null || existing.DefaultFeatures, Margin = new Thickness(0, 6, 0, 4) }, "FCheck");
                _detail.Children.Add(defaults);
                featurePanel = new StackPanel { Margin = new Thickness(27, 2, 0, 0) };
                foreach (var kv in port.Features)
                {
                    var cb = Styled(new CheckBox { Tag = kv.Key, IsChecked = existing != null && existing.Features.Contains(kv.Key), Margin = new Thickness(0, 4, 0, 0) }, "FCheck");
                    var label = new TextBlock { TextWrapping = TextWrapping.Wrap };
                    label.Inlines.Add(new Run(kv.Key) { FontWeight = FontWeights.SemiBold });
                    if (!string.IsNullOrEmpty(kv.Value)) label.Inlines.Add(new Run("   " + kv.Value) { FontSize = 12 });
                    cb.Content = label;
                    checks.Add(cb);
                    featurePanel.Children.Add(cb);
                }
                _detail.Children.Add(featurePanel);
            }

            // 版
            Section(L.T("版"));
            var verRow = new StackPanel { Orientation = Orientation.Horizontal, Margin = new Thickness(0, 6, 0, 0) };
            var verMode = Styled(new ComboBox { MinWidth = 230 }, "FCombo");
            verMode.Items.Add(L.T("ベースラインの版 (指定しない)"));
            verMode.Items.Add(L.T("この版以上 (version>=)"));
            var verBox = Styled(new TextBox { MinWidth = 100, Margin = new Thickness(8, 0, 0, 0), Text = existing != null && existing.MinVersion != null ? existing.MinVersion : StripPortVersion(port.Version) }, "FTextBox");
            verMode.SelectedIndex = existing != null && existing.MinVersion != null ? 1 : 0;
            verBox.IsEnabled = verMode.SelectedIndex == 1;
            verMode.SelectionChanged += (s, e) => verBox.IsEnabled = verMode.SelectedIndex == 1;
            verRow.Children.Add(verMode);
            verRow.Children.Add(verBox);
            _detail.Children.Add(verRow);
            if (_manifest != null && _manifest.Exists && string.IsNullOrEmpty(_manifest.Baseline))
                Tinted(Paragraph(L.T("この vcpkg.json には builtin-baseline がありません。版を指定するには、「ベースラインを更新」を押して、先に書き込んでください。"), 1, 8), "WarnBrush", TextBlock.ForegroundProperty);

            // 操作
            var ops = new WrapPanel { Margin = new Thickness(0, 18, 0, 0) };
            var add = Styled(new Button { Content = existing == null ? L.T("追加") : L.T("設定を更新"), IsEnabled = CurrentTarget != null && !_busy }, "FPrimary");
            add.Click += (s, e) =>
            {
                var dep = new Dependency { Name = port.Name, DefaultFeatures = defaults == null || defaults.IsChecked == true };
                foreach (CheckBox cb in checks) if (cb.IsChecked == true) dep.Features.Add((string)cb.Tag);
                if (verMode.SelectedIndex == 1 && !string.IsNullOrWhiteSpace(verBox.Text)) dep.MinVersion = verBox.Text.Trim();
                AddDependency(dep);
            };
            ops.Children.Add(add);
            var rem = Styled(new Button { Content = L.T("削除"), IsEnabled = existing != null && !_busy }, "FButton");
            rem.Click += (s, e) => RemoveDependency(port.Name);
            ops.Children.Add(rem);
            var tree = Styled(new Button { Content = L.T("依存の木を見る"), IsEnabled = !_busy }, "FButton");
            tree.Click += (s, e) => ShowDependTree(port.Name);
            ops.Children.Add(tree);
            _detail.Children.Add(ops);

            // GitHub から、最新の版・ホームページ・ライセンス・依存を取る(取れなくても、上の内容は変わらない)
            PortDetail d = await VcpkgTool.LoadDetailAsync(port.Name, CancellationToken.None);
            if (!ReferenceEquals(_selected, port)) return;
            if (d == null)
            {
                detailSlot.Children.Add(Tinted(new TextBlock { Text = L.T("ホームページなどの詳細は、取得できませんでした (オフラインかもしれません)。"), FontSize = 12, Margin = new Thickness(0, 10, 0, 0), TextWrapping = TextWrapping.Wrap }, "SubBrush", TextBlock.ForegroundProperty));
                return;
            }
            if (!string.IsNullOrEmpty(d.Version)) _latest[port.Name] = d.Version;
            // 既定で入る機能に、印を付ける(チェックが切でも、「既定の機能を使う」が入なら入る)
            if (featurePanel != null)
                foreach (CheckBox cb in featurePanel.Children.OfType<CheckBox>())
                {
                    var tb = cb.Content as TextBlock;
                    if (tb != null && d.DefaultFeatures.Contains((string)cb.Tag))
                        tb.Inlines.InsertAfter(tb.Inlines.FirstInline, new Run("  [" + L.T("既定") + "]") { Foreground = (Brush)FindResource("AccentBrush"), FontSize = 11 });
                }
            Action<string, string> line = (label, value) =>
            {
                var p = new TextBlock { Margin = new Thickness(0, 5, 0, 0), TextWrapping = TextWrapping.Wrap };
                p.Inlines.Add(new Run(label + "   ") { FontSize = 12, Foreground = (Brush)FindResource("SubBrush") });
                p.Inlines.Add(new Run(value));
                detailSlot.Children.Add(p);
            };
            if (!string.IsNullOrEmpty(d.Version)) line(L.T("最新の版 (GitHub)"), d.Version);
            if (!string.IsNullOrEmpty(d.License)) line(L.T("ライセンス"), d.License);
            if (!string.IsNullOrEmpty(d.Supports)) line(L.T("対応する環境 (supports)"), d.Supports);
            if (d.Dependencies.Count > 0) line(L.T("依存するパッケージ"), string.Join(", ", d.Dependencies));
            if (!string.IsNullOrEmpty(d.Homepage))
            {
                var p = new TextBlock { Margin = new Thickness(0, 5, 0, 0), TextWrapping = TextWrapping.Wrap };
                p.Inlines.Add(new Run(L.T("ホームページ") + "   ") { FontSize = 12, Foreground = (Brush)FindResource("SubBrush") });
                var h = new Hyperlink(new Run(d.Homepage)) { Foreground = (Brush)FindResource("AccentBrush") };
                string url = d.Homepage;
                h.Click += (s, e) => OpenUrl(url);
                p.Inlines.Add(h);
                detailSlot.Children.Add(p);
            }
        }

        private static string StripPortVersion(string v) { int i = (v ?? "").IndexOf('#'); return i < 0 ? v : v.Substring(0, i); }

        // ---------- 追加・削除・元に戻す ----------

        private bool EnsureManifest(out string error)
        {
            error = null;
            Target t = CurrentTarget;
            if (t == null) { error = L.T("プロジェクトの置き場所を選んでください。"); return false; }
            if (_manifest == null) _manifest = VcpkgManifest.Load(VcpkgManifest.FileNameIn(t.Dir));
            return true;
        }

        private async void AddDependency(Dependency dep)
        {
            string err;
            if (!EnsureManifest(out err)) { AppendLog(err); return; }
            try
            {
                bool created = !_manifest.Exists;
                _manifest.AddOrUpdate(dep);
                _manifest.Save();
                AppendLog(L.F("{0} を vcpkg.json に追加しました ({1})", dep.Name, _manifest.Path));
                if (created)
                {
                    // 新しく作ったときは、版を指定できるように、builtin-baseline も書き込む
                    await RunVcpkg("x-update-baseline --add-initial-baseline", false);
                    _manifest = VcpkgManifest.Load(_manifest.Path);
                    LoadTargets();
                }
                RefreshAfterChange();
                ShowUsageHint(dep.Name);
            }
            catch (Exception ex) { AppendLog(L.F("追加できませんでした: {0}", ex.Message)); }
        }

        private void RemoveDependency(string name)
        {
            string err;
            if (!EnsureManifest(out err)) { AppendLog(err); return; }
            try
            {
                if (_manifest.Remove(name)) { _manifest.Save(); AppendLog(L.F("{0} を vcpkg.json から削除しました", name)); }
                RefreshAfterChange();
            }
            catch (Exception ex) { AppendLog(L.F("削除できませんでした: {0}", ex.Message)); }
        }

        private void RemoveSelected(ListBox box)
        {
            foreach (Row r in box.SelectedItems.Cast<Row>().ToList()) RemoveDependency(r.Name);
        }

        private void RaiseMinVersion(ListBox box)
        {
            string err;
            if (!EnsureManifest(out err)) { AppendLog(err); return; }
            foreach (Row r in box.SelectedItems.Cast<Row>().ToList())
            {
                Dependency d = _manifest.Find(r.Name);
                string latest = LatestOf(r.Name);
                if (d == null || latest == null) continue;
                d.MinVersion = StripPortVersion(latest);
                _manifest.AddOrUpdate(d);
            }
            try { _manifest.Save(); AppendLog(L.T("「この版以上」を、最新の版に書き換えました。インストールで反映されます。")); }
            catch (Exception ex) { AppendLog(ex.Message); }
            RefreshAfterChange();
        }

        private void UndoLast()
        {
            Target t = CurrentTarget;
            if (t == null) return;
            string path = VcpkgManifest.FileNameIn(t.Dir);
            if (VcpkgManifest.UndoLast(path)) AppendLog(L.T("vcpkg.json を、直前の状態に戻しました。"));
            _manifest = VcpkgManifest.Load(path);
            LoadTargets();
        }

        private void RefreshAfterChange()
        {
            UpdateButtons();
            RefreshBrowse();
            if (_selected != null) ShowDetail(_selected);
            if (_tabs.SelectedIndex == 1) RefreshInstalled();
            if (_tabs.SelectedIndex == 2) RefreshUpdates();
        }

        // ---------- 入れたあとの案内 ----------

        private void ShowUsageHint(string name)
        {
            _hint.Text = L.F("次は「インストール」を押してください。CMake なら find_package({0} CONFIG REQUIRED) と target_link_libraries(...) で使います (正確な書き方は、インストール後のログに出ます)。MSBuild (.vcxproj) なら、プロジェクトの vcpkg のページで、「Use Vcpkg Manifest」を「はい」にしてください。", name);
        }

        // ---------- 実行 ----------

        private void SetBusy(bool busy)
        {
            _busy = busy;
            _progress.Visibility = busy ? Visibility.Visible : Visibility.Collapsed;
            _progress.IsIndeterminate = busy;
            UpdateButtons();
        }

        private void AppendLog(string line)
        {
            if (!Dispatcher.CheckAccess()) { Dispatcher.BeginInvoke(new Action(() => AppendLog(line))); return; }
            _log.AppendText(line + Environment.NewLine);
            _log.ScrollToEnd();
        }

        private async Task<RunResult> RunVcpkg(string args, bool clear, bool neutral = false)
        {
            Target t = CurrentTarget;
            if (VcpkgTool.FindExe() == null) { AppendLog(L.T("vcpkg が見つかりません")); return null; }
            if (clear) _log.Clear();
            AppendLog("> vcpkg " + args);
            SetBusy(true);
            _cts = new CancellationTokenSource();
            try
            {
                string work = neutral ? await VcpkgTool.NeutralDirAsync(_manifest != null ? _manifest.Baseline : null, _cts.Token) : (t != null ? t.Dir : null);
                RunResult r = await VcpkgTool.RunAsync(args, work, AppendLog, _cts.Token);
                AppendLog(r.Canceled ? L.T("中止しました。") : r.Ok ? L.T("完了しました。") : L.F("失敗しました (終了コード {0})。", r.ExitCode));
                if (!r.Ok && !r.Canceled) AppendLog(Diagnose(r.Output));
                return r;
            }
            finally { SetBusy(false); _cts = null; }
        }

        /// <summary>よくある失敗を、原因が分かる形で書き足す。</summary>
        private static string Diagnose(string output)
        {
            string o = output ?? "";
            if (o.Contains("baseline") && (o.Contains("git show") || o.Contains("failed to fetch") || o.Contains("not in")))
                return L.T("原因: ベースラインの指定が古い、または GitHub から取れません。「ベースラインを更新」を試すか、ネットワークを確かめてください。");
            if (o.Contains("Could not resolve host") || o.Contains("Failed to connect") || o.Contains("Unable to connect") || o.Contains("timed out") || o.Contains("curl: (") || o.Contains("download"))
                if (o.Contains("error"))
                    return L.T("原因: ネットワークに接続できないか、ダウンロードに失敗した可能性があります。つながっているか、プロキシの設定を確かめてください。");
            if (o.Contains("error: building") || o.Contains("BUILD_FAILED") || o.Contains("Building ") && o.Contains("failed"))
                return L.T("原因: パッケージのビルドに失敗しました。ログの、buildtrees の下にあるログ ファイル (*-err.log) を見ると、詳しい理由が分かります。");
            if (o.Contains("unsupported") || o.Contains("is only supported on"))
                return L.T("原因: このトリプレットでは、パッケージが対応していません。別のトリプレットを選んでください。");
            if (o.Contains("does not exist") || o.Contains("Could not find a package"))
                return L.T("原因: パッケージの名前が見つかりません。綴りと、ベースラインの版を確かめてください。");
            return L.T("原因は、上のログの、最初の「error:」の行から探してください。");
        }

        private async void RunInstall()
        {
            if (_manifest == null || !_manifest.Exists) return;
            var args = new StringBuilder("install --triplet " + Quote(Triplet));
            foreach (string d in VcpkgLocator.OverlayDirs(CurrentTarget.Dir)) args.Append(" --overlay-triplets=" + Quote(d));
            RunResult r = await RunVcpkg(args.ToString(), true);
            if (r != null && r.Ok)
            {
                string usage = ExtractUsage(r.Output);
                _hint.Text = usage.Length > 0 ? usage : L.T("インストールが終わりました。");
            }
            RefreshAfterChange();
        }

        /// <summary>vcpkg のログから、「使い方」の行(find_package など)を取り出す。</summary>
        private static string ExtractUsage(string output)
        {
            if (string.IsNullOrEmpty(output)) return "";
            var lines = output.Split('\n').Select(l => l.TrimEnd('\r')).Where(l => l.Contains("find_package") || l.Contains("target_link_libraries") || l.Contains("provides CMake targets")).Take(8);
            return string.Join("\n", lines);
        }

        private async void RunBaseline(bool thenInstall = false)
        {
            if (_manifest == null || !_manifest.Exists) return;
            string args = "x-update-baseline" + (string.IsNullOrEmpty(_manifest.Baseline) ? " --add-initial-baseline" : "");
            RunResult r = await RunVcpkg(args, true);
            _manifest = VcpkgManifest.Load(_manifest.Path);
            if (r != null && r.Ok && thenInstall) RunInstall();
            else RefreshAfterChange();
        }

        private async void ShowDependTree(string name)
        {
            RunResult r = await RunVcpkg("depend-info " + Quote(name) + " --format=tree --triplet " + Quote(Triplet), true, true);
            if (r != null && r.Ok) _hint.Text = L.F("{0} の依存の木を、下のログに出しました。", name);
        }

        private static string Quote(string s) { return "\"" + (s ?? "").Replace("\"", "") + "\""; }

        // ---------- インストール済み・更新 ----------

        /// <summary>最新の版。GitHub の vcpkg で分かった版と、ローカルの一覧の版の、新しいほう(ローカルの一覧は、vcpkg のコピーが古いと、古い)。</summary>
        private string LatestOf(string name)
        {
            PortInfo p;
            _byName.TryGetValue(name, out p);
            string local = p != null ? p.Version : null;
            string remote;
            _latest.TryGetValue(name, out remote);
            if (remote == null) return local;
            if (local == null) return remote;
            return VcpkgTool.CompareVersions(remote, local) >= 0 ? remote : local;
        }

        private List<Row> StatusRows()
        {
            var rows = new List<Row>();
            if (_manifest == null || !_manifest.Exists) return rows;
            Dictionary<string, string> inst = _manifest.InstalledVersions();
            foreach (Dependency d in _manifest.Dependencies())
            {
                PortInfo p;
                _byName.TryGetValue(d.Name, out p);
                string have = VcpkgManifest.InstalledVersion(inst, d.Name);
                string latest = LatestOf(d.Name);
                string status; string brush = "TextBrush";
                if (latest == null) { status = L.T("一覧にありません"); brush = "SubBrush"; }
                else if (have == null) { status = L.T("未インストール"); brush = "WarnBrush"; }
                else if (VcpkgTool.CompareVersions(latest, have) > 0) { status = L.T("更新あり"); brush = "AccentBrush"; }
                else { status = L.T("最新"); brush = "OkBrush"; }
                rows.Add(new Row
                {
                    Name = d.Name, Port = p,
                    Extra = d.MinVersion != null ? ">= " + d.MinVersion : "-",
                    Version = have ?? "-",
                    Desc = latest ?? "?",
                    Status = status,
                    StatusBrush = (Brush)FindResource(brush),
                });
            }
            return rows;
        }

        /// <summary>vcpkg.json の各パッケージの最新の版を、GitHub から取る(最初の表示は、ローカルの版。取れたら表を作り直す)。</summary>
        private async Task FetchLatestAsync()
        {
            if (_manifest == null || !_manifest.Exists) return;
            string[] names = _manifest.Dependencies().Select(d => d.Name).Where(n => !_latest.ContainsKey(n)).ToArray();
            if (names.Length == 0) return;
            PortDetail[] ds = await Task.WhenAll(names.Select(n => VcpkgTool.LoadDetailAsync(n, CancellationToken.None)));
            for (int i = 0; i < names.Length; i++) if (ds[i] != null && !string.IsNullOrEmpty(ds[i].Version)) _latest[names[i]] = ds[i].Version;
        }

        private async void RefreshInstalled()
        {
            ShowInstalled();
            await FetchLatestAsync();
            if (_tabs.SelectedIndex == 1) ShowInstalled();
        }

        private void ShowInstalled()
        {
            var rows = StatusRows();
            _installed.ItemsSource = rows;
            if (_manifest == null || !_manifest.Exists) _installedNote.Text = L.T("この場所には vcpkg.json がありません。「参照」でパッケージを追加すると、作られます。");
            else
            {
                int missing = rows.Count(r => r.Version == "-");
                string baseline = _manifest.Baseline;
                _installedNote.Text = L.F("{0} 個のパッケージ。未インストール: {1} 個。ベースライン: {2}", rows.Count, missing, string.IsNullOrEmpty(baseline) ? L.T("なし") : baseline.Substring(0, Math.Min(10, baseline.Length)));
            }
        }

        private async void RefreshUpdates()
        {
            ShowUpdates();
            await FetchLatestAsync();
            if (_tabs.SelectedIndex == 2) ShowUpdates();
        }

        private void ShowUpdates()
        {
            var rows = StatusRows().Where(r => r.Status == L.T("更新あり")).ToList();
            _updates.ItemsSource = rows;
            if (_manifest == null || !_manifest.Exists) _updatesNote.Text = L.T("この場所には vcpkg.json がありません。");
            else if (rows.Count == 0) _updatesNote.Text = L.T("更新できるパッケージは、ありません (入っている版が、一覧の最新と同じか、まだインストールしていません)。");
            else _updatesNote.Text = L.F("{0} 個のパッケージに、新しい版があります。実際にどの版が入るかは、vcpkg.json のベースラインで決まります。「ベースラインを更新」で、全体を新しくできます。", rows.Count);
        }
    }
}
