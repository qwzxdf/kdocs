---
title: 第 17 章 HwndHost でビューポートを実装する
tags:
  - C#連携
---

# 第 17 章 HwndHost でビューポートを実装する

この章で、<strong>エディタの真ん中に、エンジンの絵が出ます</strong>。`HwndHost` を継承した部品を作り、その中に Win32 の子ウィンドウを作って、その `HWND` で `Engine` を動かします。第 3〜4 章の色が変わるウィンドウが、WPF の画面の中に入る章です。

## この章の考え方

`HwndHost` は、WPF と Win32 の<strong>橋渡し役</strong>です。WPF の部品として、レイアウトに参加しながら、中身は Win32 のウィンドウです。

```text
ViewportView（UserControl）
 └─ ViewportHost（HwndHost を継承した、自分のクラス）
      └─ 子ウィンドウ（HWND）  ← BuildWindowCore で作る
           └─ Engine がここにスワップ チェーンを作る
```

`HwndHost` を継承したクラスが行う仕事は、次の 3 つです。

| 仕事 | 呼ばれる関数 | 内容 |
| --- | --- | --- |
| 子ウィンドウを作る | `BuildWindowCore` | Win32 の `CreateWindowEx` で、親（WPF 側）を指定して作る |
| 子ウィンドウを壊す | `DestroyWindowCore` | `DestroyWindow` で壊す |
| 大きさの変化を知る | `OnWindowPositionChanged` | WPF のレイアウトで大きさが変わるたびに、呼ばれる |

エンジンは、WPF の存在を知りません。<strong>`HWND` を 1 つ受け取り、そこへ描く</strong>だけです。第 4 章の Player が作ったウィンドウと、同じ使い方です。

## この章のゴール

- Win32 の子ウィンドウを、`HwndHost` で WPF に埋め込む。
- その `HWND` で `Engine` を作り、毎フレーム `Tick` する。
- ウィンドウの大きさを変えても、絵が追従する。
- 閉じるとき、正しい順序で後片付けする。

## 手順 1：モジュールとフォルダーを用意する

第 9 章と同じ作り方で、`Viewport` モジュールを作ります。

```text
Editor\Modules\Viewport\
  ViewportModule.cs
  Views\ViewportView.xaml / .xaml.cs
  ViewModels\ViewportViewModel.cs
  Controls\ViewportHost.cs      ← HwndHost
Editor\Interop\Win32.cs         ← Win32 API の宣言
```

`ViewportModule` は、`SceneTreeModule` と同じ形で、`RegionNames.Viewport` に `ViewportView` を登録します。`App.xaml.cs` の `ConfigureModuleCatalog` に、`moduleCatalog.AddModule<ViewportModule>();` を足します。

## 手順 2：Win32 API の宣言

子ウィンドウを作るために、<strong>user32.dll</strong> の関数を、P/Invoke で宣言します。`Interop\Win32.cs`:

```csharp
using System.Runtime.InteropServices;

namespace Editor.Interop;

// Win32 API の宣言。ビューポートの子ウィンドウに必要なものだけ。
internal static partial class Win32
{
    // ウィンドウ スタイル
    public const int WS_CHILD = 0x40000000;
    public const int WS_VISIBLE = 0x10000000;
    public const int WS_CLIPSIBLINGS = 0x04000000;
    public const int WS_CLIPCHILDREN = 0x02000000;

    public const uint CS_HREDRAW = 0x0002;
    public const uint CS_VREDRAW = 0x0001;
    public const int IDC_ARROW = 32512;

    [StructLayout(LayoutKind.Sequential)]
    public struct WNDCLASSEXW
    {
        public uint cbSize;
        public uint style;
        public nint lpfnWndProc;
        public int cbClsExtra;
        public int cbWndExtra;
        public nint hInstance;
        public nint hIcon;
        public nint hCursor;
        public nint hbrBackground;
        public nint lpszMenuName;
        public nint lpszClassName;
        public nint hIconSm;
    }

    [StructLayout(LayoutKind.Sequential)]
    public struct RECT
    {
        public int Left, Top, Right, Bottom;
    }

    [LibraryImport("user32.dll", EntryPoint = "RegisterClassExW", SetLastError = true)]
    public static partial ushort RegisterClassEx(in WNDCLASSEXW windowClass);

    [LibraryImport("user32.dll", EntryPoint = "CreateWindowExW", SetLastError = true, StringMarshalling = StringMarshalling.Utf16)]
    public static partial nint CreateWindowEx(
        int exStyle, string className, string windowName, int style,
        int x, int y, int width, int height, nint parent, nint menu, nint instance, nint param);

    [LibraryImport("user32.dll", SetLastError = true)]
    [return: MarshalAs(UnmanagedType.Bool)]
    public static partial bool DestroyWindow(nint hwnd);

    [LibraryImport("user32.dll")]
    [return: MarshalAs(UnmanagedType.Bool)]
    public static partial bool GetClientRect(nint hwnd, out RECT rect);

    [LibraryImport("user32.dll", EntryPoint = "LoadCursorW")]
    public static partial nint LoadCursor(nint instance, nint cursorName);

    [LibraryImport("user32.dll")]
    public static partial nint SetFocus(nint hwnd);

    [LibraryImport("kernel32.dll", EntryPoint = "GetModuleHandleW", StringMarshalling = StringMarshalling.Utf16)]
    public static partial nint GetModuleHandle(string? moduleName);
}
```

| 新しく出てきたもの | 説明 |
| --- | --- |
| `const int WS_CHILD = …` | Win32 のウィンドウ スタイルの定数。C++ の `windows.h` に書かれている値と同じ |
| `WS_CHILD` | 子ウィンドウ。親ウィンドウの中だけに表示される |
| `WS_CLIPSIBLINGS` / `WS_CLIPCHILDREN` | 兄弟・子のウィンドウと重なる部分を、描画から除く。ちらつきを防ぐ |
| `WNDCLASSEXW` | ウィンドウ クラスの設定。第 4 章の C++ と同じ構造体を、C# で再現している。`nint` の個数と並びを、そのまま合わせる |
| `public int Left, Top, Right, Bottom;` | 同じ型のフィールドを、カンマで並べて宣言する書き方 |
| `RECT` | 矩形。`GetClientRect` が、クライアント領域の大きさを返す（<strong>物理ピクセル</strong>） |
| `SetLastError = true` | 呼び出しの直後に、Windows の最後のエラー コードを保存する。`Marshal.GetLastPInvokeError()` で読める |
| `EntryPoint = "CreateWindowExW"` | DLL 内の関数名。C# のメソッド名（`CreateWindowEx`）と変えたいときに指定する。Windows API の `W` 付きが UTF-16 版 |
| `[return: MarshalAs(UnmanagedType.Bool)]` | 戻り値の `BOOL`（4 バイト）を `bool` に変換する指定（第 15 章） |
| `ushort` | 16 ビット符号なし整数。`RegisterClassEx` が返す「クラスのアトム」の型 |

## 手順 3：ViewportHost を書く

`Modules\Viewport\Controls\ViewportHost.cs`:

### 型とイベント

```csharp
using System.Runtime.InteropServices;
using System.Windows;
using System.Windows.Interop;

using Editor.Interop;

namespace Editor.Modules.Viewport.Controls;

// 子ウィンドウが準備できた、または大きさが変わったことを知らせる
public sealed class ViewportSizeEventArgs : EventArgs
{
    public nint Handle { get; }
    public uint Width { get; }
    public uint Height { get; }

    public ViewportSizeEventArgs(nint handle, uint width, uint height)
    {
        Handle = handle;
        Width = width;
        Height = height;
    }
}

// エンジンが描く子ウィンドウを、WPF の中に置く部品
public sealed class ViewportHost : HwndHost
{
    private const string ClassName = "MiniEngineViewport";
    private static bool s_classRegistered;

    private nint _hwnd;
    private bool _readyRaised;
    private uint _lastWidth, _lastHeight;

    public event EventHandler<ViewportSizeEventArgs>? HandleReady;       // 初めて大きさが決まった
    public event EventHandler<ViewportSizeEventArgs>? ViewportResized;   // 大きさが変わった
    public event EventHandler? HandleDestroying;                         // 壊される直前
```

| 新しく出てきたもの | 説明 |
| --- | --- |
| `HwndHost` | `System.Windows.Interop` の抽象クラス。Win32 のウィンドウを、WPF の部品として置くための基底クラス。継承して、`BuildWindowCore` と `DestroyWindowCore` を実装する |
| `EventArgs` | イベントの引数の基底クラス。値を運びたいときは、これを継承したクラスを作る |
| `EventHandler<T>` | `(object? sender, T e)` の形のデリゲート。第 5 章の `event` と組み合わせる |
| `sealed` | 継承を禁止する |
| `uint _lastWidth, _lastHeight;` | 同じ型のフィールドを、まとめて宣言 |
| `HandleReady` など 3 つのイベント | ビューポートの外（ビュー、ビューモデル）に、状態を知らせる |

### 子ウィンドウの作成

```csharp
    protected override HandleRef BuildWindowCore(HandleRef hwndParent)
    {
        RegisterWindowClass();

        _hwnd = Win32.CreateWindowEx(
            exStyle: 0,
            className: ClassName,
            windowName: "",
            style: Win32.WS_CHILD | Win32.WS_VISIBLE | Win32.WS_CLIPSIBLINGS | Win32.WS_CLIPCHILDREN,
            x: 0, y: 0, width: 1, height: 1,           // 大きさは、あとで WPF が決める
            parent: hwndParent.Handle,
            menu: nint.Zero,
            instance: Win32.GetModuleHandle(null),
            param: nint.Zero);

        if (_hwnd == nint.Zero)
        {
            throw new InvalidOperationException(
                $"子ウィンドウの作成に失敗しました（Win32 エラー {Marshal.GetLastPInvokeError()}）");
        }
        return new HandleRef(this, _hwnd);
    }

    private static void RegisterWindowClass()
    {
        if (s_classRegistered) return;

        // 既定のウィンドウ プロシージャ（DefWindowProcW）のアドレスを、user32.dll から取る
        nint user32 = NativeLibrary.Load("user32.dll");
        nint defWindowProc = NativeLibrary.GetExport(user32, "DefWindowProcW");

        var windowClass = new Win32.WNDCLASSEXW
        {
            cbSize = (uint)Marshal.SizeOf<Win32.WNDCLASSEXW>(),
            style = Win32.CS_HREDRAW | Win32.CS_VREDRAW,
            lpfnWndProc = defWindowProc,
            hInstance = Win32.GetModuleHandle(null),
            hCursor = Win32.LoadCursor(nint.Zero, Win32.IDC_ARROW),
            lpszClassName = Marshal.StringToHGlobalUni(ClassName),
        };
        if (Win32.RegisterClassEx(in windowClass) == 0)
        {
            throw new InvalidOperationException(
                $"ウィンドウ クラスの登録に失敗しました（Win32 エラー {Marshal.GetLastPInvokeError()}）");
        }
        s_classRegistered = true;
    }
```

| 新しく出てきたもの | 説明 |
| --- | --- |
| `BuildWindowCore(HandleRef hwndParent)` | 子ウィンドウを作る関数。`hwndParent` は WPF が用意する<strong>親の HWND</strong>。作ったウィンドウを `HandleRef` で返す |
| `HandleRef` | ハンドルと、それを持つオブジェクトをペアにした構造体。ハンドルが使われている間、持ち主を GC に回収させないための物 |
| 名前付き引数 `exStyle: 0, …` | 引数が多い関数で、どの値が何かを分かりやすく書く |
| ビット OR（縦棒 1 本の演算子） | スタイルの定数を組み合わせる。C++ と同じ |
| `Marshal.GetLastPInvokeError()` | `SetLastError = true` の呼び出しの、直後のエラー コードを取る |
| `NativeLibrary.Load` / `GetExport` | DLL を読み込み、関数の<strong>アドレス</strong>を取る（第 15 章）。`DefWindowProcW` のアドレスを、ウィンドウ プロシージャとして使う |
| `DefWindowProcW` | 何も特別な処理をしない、既定のウィンドウ プロシージャ。この子ウィンドウは、メッセージを自前で処理せず、WPF（`HwndHost`）が受け取る |
| `Marshal.SizeOf<T>()` | 構造体の大きさ（バイト数）を返す。`cbSize` に必要 |
| `Marshal.StringToHGlobalUni` | C# の文字列を、ネイティブのメモリにコピーして UTF-16 のポインターを返す。ここでは一度だけ作って、解放しない（クラス名はプログラムの間ずっと必要） |
| `s_classRegistered` | クラスの登録は 1 回だけでよいので、`static` なフラグで管理する |

!!! note "なぜ自前でウィンドウ クラスを登録するのか"
    手軽に、既存のクラス `"static"` で子ウィンドウを作る例もありますが、`"static"` は<strong>マウス メッセージを親に素通しにする</strong>（`HTTRANSPARENT`）ので、第 19 章の入力が取れません。自分で登録したクラスなら、マウスのメッセージが、この子ウィンドウに届きます。

### 壊す

```csharp
    protected override void DestroyWindowCore(HandleRef hwnd)
    {
        // エンジンの後片付けは、ウィンドウを壊す「前」に行う
        HandleDestroying?.Invoke(this, EventArgs.Empty);

        Win32.DestroyWindow(hwnd.Handle);
        _hwnd = nint.Zero;
    }
```

| 新しく出てきたもの | 説明 |
| --- | --- |
| `DestroyWindowCore` | `HwndHost` が破棄されるときに呼ばれる。子ウィンドウを壊す |
| 順序 | <strong>エンジンを先に破棄</strong>（スワップ チェーンを解放）してから、ウィンドウを壊す。逆にすると、DX12 が壊れた HWND を触ってエラーになる |

### 大きさの変化

```csharp
    protected override void OnWindowPositionChanged(Rect rcBoundingBox)
    {
        base.OnWindowPositionChanged(rcBoundingBox);
        if (_hwnd == nint.Zero) return;

        // 物理ピクセルの大きさは、クライアント領域から取る
        if (!Win32.GetClientRect(_hwnd, out var rect)) return;
        uint width = (uint)Math.Max(0, rect.Right - rect.Left);
        uint height = (uint)Math.Max(0, rect.Bottom - rect.Top);
        if (width == 0 || height == 0) return;                      // 最小化、折りたたみ
        if (width == _lastWidth && height == _lastHeight) return;   // 変化なし

        _lastWidth = width;
        _lastHeight = height;
        var args = new ViewportSizeEventArgs(_hwnd, width, height);

        if (!_readyRaised)
        {
            _readyRaised = true;
            HandleReady?.Invoke(this, args);
        }
        else
        {
            ViewportResized?.Invoke(this, args);
        }
    }
}
```

| 新しく出てきたもの | 説明 |
| --- | --- |
| `OnWindowPositionChanged(Rect)` | WPF のレイアウトで、位置や大きさが変わったとき（子ウィンドウを動かした後）に呼ばれる。ここでエンジンに、大きさを伝える |
| `Rect` | WPF の矩形（`double`）。<strong>デバイス非依存単位</strong>なので、直接ピクセルとして使わない |
| `GetClientRect` | 子ウィンドウの実際の大きさを、<strong>物理ピクセル</strong>で得る。DPI が 100% でない画面でも、正しい値になる |
| `Math.Max(0, …)` | 負の値を 0 にそろえる |
| 最初の呼び出しで `HandleReady` | エンジンの作成には、<strong>大きさが 0 でない</strong>ことが要る。大きさが決まった<strong>最初の</strong>瞬間に、`HandleReady` を出す |

!!! warning "DPI（画面の拡大率）の注意"
    画面の拡大率が 150% のモニターでは、WPF の 100 単位は、物理ピクセルで 150 です。エンジンには<strong>物理ピクセル</strong>を渡します。このため、`Rect` ではなく `GetClientRect` を使っています。さらに、複数モニターで拡大率が違う環境では、<strong>アプリを Per-Monitor DPI 対応にする</strong>必要があります。プロジェクトに `app.manifest` を追加し、`<dpiAwareness>PerMonitorV2</dpiAwareness>` と `<dpiAware>true/PM</dpiAware>` を設定してください（「追加 → 新しい項目 → アプリケーション マニフェスト ファイル」）。

## 手順 4：ビューとビューモデル

### ビュー

`Views\ViewportView.xaml`:

```xml
<UserControl x:Class="Editor.Modules.Viewport.Views.ViewportView"
             xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
             xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
             xmlns:prism="http://prismlibrary.com/"
             xmlns:controls="clr-namespace:Editor.Modules.Viewport.Controls"
             prism:ViewModelLocator.AutoWireViewModel="True">
    <Border Background="Black">
        <controls:ViewportHost x:Name="Host" />
    </Border>
</UserControl>
```

`HwndHost` はバインディングで扱いにくいので、<strong>ビューのコードビハインドで、ホストのイベントをビューモデルに橋渡し</strong>します。ビューモデルは、画面を知らず、`HWND` と数値だけを受け取ります。

`Views\ViewportView.xaml.cs`:

```csharp
using System.Windows.Controls;

using Editor.Modules.Viewport.ViewModels;

namespace Editor.Modules.Viewport.Views;

public partial class ViewportView : UserControl
{
    public ViewportView()
    {
        InitializeComponent();

        Host.HandleReady += (_, e) => ViewModel?.OnWindowReady(e.Handle, e.Width, e.Height);
        Host.ViewportResized += (_, e) => ViewModel?.OnWindowResized(e.Width, e.Height);
        Host.HandleDestroying += (_, _) => ViewModel?.OnWindowDestroying();
    }

    private ViewportViewModel? ViewModel => DataContext as ViewportViewModel;
}
```

| 新しく出てきたもの | 説明 |
| --- | --- |
| `Host.HandleReady += (_, e) => …` | イベントの購読。`_` は、使わない引数の名前（<strong>破棄</strong>）。`(_, _)` のように、2 つ並べてもよい |
| `DataContext as ViewportViewModel` | `as` による型変換。失敗すると `null`。`DataContext` は `object?` 型なので、`as` で型を戻す |
| `ViewModel?.OnWindowReady(…)` | `null` のとき何もしない（`?.`） |
| 「コードビハインドを使ってよいか」 | <strong>見た目と画面部品の都合</strong>（`HwndHost` のイベント）を、ビューモデルに橋渡しするだけの用途なら、問題ない。ロジックは書かない |

### ビューモデル

`ViewModels\ViewportViewModel.cs`:

```csharp
using System.Diagnostics;
using System.Windows.Media;

using Prism.Mvvm;

using Editor.Services;

namespace Editor.Modules.Viewport.ViewModels;

public class ViewportViewModel : BindableBase
{
    private readonly IEngineService _engine;
    private readonly ILogService _log;
    private readonly Stopwatch _clock = new();
    private TimeSpan _previous;

    public ViewportViewModel(IEngineService engine, ILogService log)
    {
        _engine = engine;
        _log = log;
    }

    // 子ウィンドウが準備できた：エンジンを作り、描画ループを始める
    public void OnWindowReady(nint hwnd, uint width, uint height)
    {
        try
        {
            _engine.Initialize(hwnd, width, height);
        }
        catch (Exception e)
        {
            _log.Error($"エンジンの初期化に失敗: {e.Message}");
            return;
        }
        _log.Info($"エンジンを初期化しました（{width}x{height}）");

        _clock.Start();
        _previous = _clock.Elapsed;
        CompositionTarget.Rendering += OnRendering;
    }

    public void OnWindowResized(uint width, uint height)
    {
        if (!_engine.IsRunning) return;
        try { _engine.Resize(width, height); }
        catch (Exception e) { _log.Error($"リサイズに失敗: {e.Message}"); }
    }

    // ウィンドウが壊される前：ループを止め、エンジンを破棄する
    public void OnWindowDestroying()
    {
        CompositionTarget.Rendering -= OnRendering;
        _engine.Dispose();
        _log.Info("エンジンを破棄しました");
    }

    // WPF が 1 フレーム描くたびに呼ばれる
    private void OnRendering(object? sender, EventArgs e)
    {
        if (!_engine.IsRunning) return;

        TimeSpan now = _clock.Elapsed;
        float delta = (float)(now - _previous).TotalSeconds;
        _previous = now;

        try { _engine.Tick(delta); }
        catch (Exception ex)
        {
            CompositionTarget.Rendering -= OnRendering;      // 失敗が続くので、ループを止める
            _log.Error($"Tick に失敗: {ex.Message}");
        }
    }
}
```

| 新しく出てきたもの | 説明 |
| --- | --- |
| `CompositionTarget.Rendering` | <strong>WPF が画面を 1 フレーム描くたびに</strong>呼ばれるイベント。UI スレッドで、毎秒 60 回ほど。ゲーム ループの代わりに使える |
| `Stopwatch` | 経過時間を測る標準のクラス。`Elapsed` が `TimeSpan`。第 4 章の `steady_clock` に当たる |
| `TimeSpan` | 時間の長さを表す型。`.TotalSeconds` で秒（`double`）に変換できる |
| `(float)(…)` | `double` を `float` に明示的に変換する（第 5 章） |
| `catch (Exception e) { … }` | 失敗したら、ログに書き、アプリを落とさない |
| `-=` で購読を解除する | 破棄のときに、イベントの購読を外す。外し忘れると、破棄後も呼ばれ続ける |
| 順序 | `OnWindowDestroying` で、<strong>ループを止めてからエンジンを破棄</strong>する。ループが動いたまま破棄すると、破棄済みの物を `Tick` してしまう |

!!! note "CompositionTarget.Rendering の性質"
    このイベントは、WPF の描画の更新のタイミングで呼ばれます。画面の更新が必要ないときは、呼ばれないことがあるため、ゲームの時間の進みが止まる場合があります。ビューポートの描画では、毎フレーム呼ばれる動作が一般的ですが、<strong>呼ばれる頻度は保証されません</strong>。第 18 章で、専用のスレッドで一定の周期で回す方法を、比べます。

## 手順 5：モジュールの登録

`ViewportModule.cs`:

```csharp
using Prism.Ioc;
using Prism.Modularity;
using Prism.Regions;

using Editor.Infrastructure;
using Editor.Modules.Viewport.Views;

namespace Editor.Modules.Viewport;

public class ViewportModule : IModule
{
    public void RegisterTypes(IContainerRegistry containerRegistry)
    {
    }

    public void OnInitialized(IContainerProvider containerProvider)
    {
        var regionManager = containerProvider.Resolve<IRegionManager>();
        regionManager.RegisterViewWithRegion(RegionNames.Viewport, typeof(ViewportView));
    }
}
```

`IEngineService` は、第 13 章で `RegisterSingleton` 済みです。ビューモデルは、<strong>同じ 1 つのエンジン</strong>を受け取ります。

## 手順 6：エンジンのログを流す

第 13 章の `NativeLog.Install` は、`App.OnInitialized` で呼びました。これで、エンジンの `LogInfo("Engine を作成しました（…）")` が、ログ タブに出ます。

## 動作確認

`F5` で起動します。

| 見る所 | 期待する結果 |
| --- | --- |
| ビューポートの領域 | <strong>色が、なめらかに変わる</strong>（第 3 章の `Tick` の色） |
| ログ タブ | 「エンジンを初期化しました（W×H）」と、エンジン側の「Engine を作成しました」が出る |
| 仕切りをドラッグ | ビューポートの大きさが変わっても、色が出続ける |
| ウィンドウを最小化 → 戻す | 描画が再開する |
| ウィンドウを閉じる | 例外なく終了する。ログに「エンジンを破棄しました」 |
| 周囲の WPF の部品 | メニュー、パネル、タブが、普通に操作できる |

## よくあるミス

??? failure "ビューポートが真っ黒のまま"
    `HandleReady` が呼ばれていない（`OnWindowPositionChanged` が、大きさ 0 のまま）。`Border` の中の `Host` が、レイアウトで大きさを持っているか確認する。ログに「エンジンを初期化」が出ていなければ、そこで止まっている。

??? failure "ログに「Engine の作成に失敗」が出る"
    スワップ チェーンの作成に失敗している。出力ウィンドウの `D3D12 ERROR` を確認する。`CreateSwapChainForHwnd` に、WPF の最上位ウィンドウの HWND を渡していないか（<strong>子ウィンドウ</strong>の HWND を渡す）。

??? failure "リサイズすると真っ黒、またはエラーが出る"
    `Renderer::Resize` が、バック バッファの参照を残している（第 3 章）。または、`Resize` の前に `WaitForGpu` していない。

??? failure "終了時にクラッシュする"
    エンジンの破棄より前に、ウィンドウが壊されている。`DestroyWindowCore` で、先に `HandleDestroying` を呼んでいるか確認する。

??? failure "`MC3074`／`controls:ViewportHost` が見つからない"
    `xmlns:controls` の名前空間が合っていない。または、`ViewportHost` を作ったあと、まだ<strong>ビルドしていない</strong>。一度ビルドしてから XAML を開く。

??? failure "拡大率 150% の画面で、絵がぼやける"
    アプリが DPI 対応になっていない。`app.manifest` に PerMonitorV2 を指定する。

??? failure "メニューを開くと、ビューポートの上に出ない"
    `Menu` や `ContextMenu` は、独立したウィンドウなので、通常は上に出る。出ない場合は、`Popup` ではなく、同じ `Grid` の中に置いた部品でメニューを作ってしまっている。

## この章のまとめ

- `HwndHost` を継承し、`BuildWindowCore` で子ウィンドウを作り、`DestroyWindowCore` で壊す。
- エンジンには、<strong>子ウィンドウの HWND と、物理ピクセルの大きさ</strong>を渡す。
- 破棄は、<strong>ループを止める → エンジンを破棄 → ウィンドウを壊す</strong>の順。
- ビューのコードビハインドは、`HwndHost` のイベントをビューモデルへ橋渡しするだけにする。

## 次の章へ

次の章（[第 18 章 描画ループとスレッド](18-render-loop.md)）では、描画ループを回す方法を比べます。UI スレッドで回す方法、専用の描画スレッドで回す方法、そして、エンジンのスレッド安全性を考えます。
