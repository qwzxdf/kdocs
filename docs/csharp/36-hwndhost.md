---
title: 第 36 章 HwndHost でビューポートを実装する
tags:
  - C#連携
---

# 第 36 章 HwndHost でビューポートを実装する

この章で、エディタの真ん中にエンジンの絵が出ます。`HwndHost` を継承した部品を作って、その中に Win32 の子ウィンドウを作り、その `HWND` で `Engine` を動かします。第 3〜4 章で作った「色が変わるウィンドウ」が WPF の画面の中に入るところです。

!!! info "このページを読む前に"
    - [第 35 章 3D ビューポートを埋め込む方法の比較](35-viewport-options.md)（前の章。ここまでの内容が前提になる）
    - [C# 連携](index.md)（このセクション全体の地図と、読む順番）


## HwndHost がやってくれること

`HwndHost` は、WPF と Win32 の橋渡し役です。WPF の部品としてレイアウトに参加しますが、中身は Win32 のウィンドウです。

```text
ViewportView（UserControl）
 └─ ViewportHost（HwndHost を継承した、自分のクラス）
      └─ 子ウィンドウ（HWND）  ← BuildWindowCore で作る
           └─ Engine がここにスワップ チェーンを作る
```

`HwndHost` を継承したクラスがやる仕事は 3 つです。`BuildWindowCore` で `CreateWindowEx` を呼んで子ウィンドウを作り、`DestroyWindowCore` でそれを壊し、`OnWindowPositionChanged` で WPF のレイアウトによる大きさの変化を受け取ります。

エンジンは WPF の存在を知りません。`HWND` を 1 つ受け取って、そこへ描くだけです。第 4 章の Player が作ったウィンドウに描くのと、まったく同じです。

## フォルダーを用意する

第 22 章と同じ作り方で、`Viewport` モジュールを作ります。

```text
Editor\Modules\Viewport\
  ViewportModule.cs
  Views\ViewportView.xaml / .xaml.cs
  ViewModels\ViewportViewModel.cs
  Controls\ViewportHost.cs      ← HwndHost
Editor\Interop\Win32.cs         ← Win32 API の宣言
```

`ViewportModule` は `SceneTreeModule` と同じ形で、`RegionNames.Viewport` に `ViewportView` を登録します。`App.xaml.cs` の `ConfigureModuleCatalog` に、`moduleCatalog.AddModule<ViewportModule>();` も足しておきます。

## Win32 API を宣言する

子ウィンドウを作るために、`user32.dll` の関数を P/Invoke で宣言します。

```csharp title="Interop/Win32.cs"
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

定数の値は、C++ の `windows.h` に書かれているものと同じです。`WS_CHILD` は「親の中だけに表示される子ウィンドウ」、`WS_CLIPSIBLINGS` と `WS_CLIPCHILDREN` は「兄弟や子と重なる部分を描画から除く」指定で、ちらつきを防ぎます。`WNDCLASSEXW` は第 4 章の C++ と同じ構造体を `nint` の個数や並びごと、そのまま C# で再現しています。`RECT` は矩形で、`GetClientRect` が返す値は物理ピクセルです。

`SetLastError = true` は、呼び出しの直後に Windows のエラー コードを保存する指定で、あとから `Marshal.GetLastPInvokeError()` で読めます。`EntryPoint = "CreateWindowExW"` は、DLL 内の関数名を指定します。C# のメソッド名と変えたいときに使います（Windows API の `W` 付きが UTF-16 版です）。

## ViewportHost を書く

まず、イベントの引数と、クラスの骨組みです。

```csharp title="Modules/Viewport/Controls/ViewportHost.cs"
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

// エンジンが描く子ウィンドウを WPF の中に置く部品
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

`EventArgs` は、イベントの引数の基底クラスです。値を運びたいときは、これを継承したクラスを作ります。ここでは、子ウィンドウのハンドルと大きさを運びます。`HandleReady` など 3 つのイベントは、ビューポートの外（ビューやビューモデル）に状態を知らせるためのものです。

### 子ウィンドウを作る

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

        // 既定のウィンドウ プロシージャ（DefWindowProcW）のアドレスを user32.dll から取る
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

`BuildWindowCore` の引数 `hwndParent` は、WPF が用意する親の HWND です。作った子ウィンドウを `HandleRef` に包んで返します。`HandleRef` は、ハンドルとその持ち主をペアにした構造体で、ハンドルが使われている間、持ち主が GC に回収されないようにします。引数が多い関数なので、`exStyle: 0` のように名前付き引数で書いて、どれが何か分かるようにしています。

ウィンドウ クラスは、アプリで 1 回だけ登録すればよいので、`static` のフラグで管理しています。ウィンドウ プロシージャには、何もしない既定の `DefWindowProcW` のアドレスを `user32.dll` から取って渡しました。メッセージの処理は WPF（`HwndHost`）が受け取るので、この子ウィンドウ自身は何もしなくて済みます。クラス名の文字列は、プログラムが動いている間ずっと必要なので、`StringToHGlobalUni` でコピーして、解放しません。

!!! note "「static」クラスで済ませない理由"
    手軽に既存の `"static"` クラスで子ウィンドウを作る例もあります。ただ、`"static"` はマウスのメッセージを親に素通しにしてしまうので、第 38 章のマウス入力が取れません。自分で登録したクラスなら、マウスのメッセージがこの子ウィンドウに届きます。

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

順序が大事です。エンジンを先に破棄してスワップ チェーンを解放してから、ウィンドウを壊します。逆にすると、DX12 が、壊れたあとの HWND を触ってエラーになります。

### 大きさの変化を受け取る

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

`OnWindowPositionChanged` は、WPF のレイアウトで位置や大きさが変わったときに呼ばれます。エンジンには、この関数で大きさを伝えます。

引数の `Rect` を使わず `GetClientRect` を使っているのは、`Rect` が WPF のデバイス非依存単位だからです。エンジンに渡すのは物理ピクセルでなければいけません。エンジンの作成には「大きさが 0 ではない」ことが必要なので、大きさが初めて決まった瞬間に `HandleReady` を出し、それ以降は `ViewportResized` を出します。

!!! warning "画面の拡大率（DPI）に気をつける"
    拡大率が 150% のモニターでは、WPF の 100 単位は物理ピクセルで 150 です。さらに、拡大率が違う複数のモニターを使う環境では、アプリを Per-Monitor DPI 対応にする必要があります。プロジェクトに `app.manifest` を追加して（「追加 → 新しい項目 → アプリケーション マニフェスト ファイル」）、`<dpiAwareness>PerMonitorV2</dpiAwareness>` と `<dpiAware>true/PM</dpiAware>` を設定します。

## ビューとビューモデル

ビューは、`ViewportHost` を置くだけです。

```xml title="Views/ViewportView.xaml"
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

`HwndHost` のイベントは、バインディングでは受けられません。そこで、ビューのコードビハインドで受けて、ビューモデルへ橋渡しします。ビューモデルは、画面を知らず、`HWND` と数値だけを受け取ります。

```csharp title="Views/ViewportView.xaml.cs"
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

`(_, e) => ...` の `_` は、使わない引数の名前で、「捨てる」という意味です。`DataContext as ViewportViewModel` は、型の変換に失敗すると `null` になる書き方で、`ViewModel?.OnWindowReady(...)` の `?.` が、`null` のときは何もしない扱いにしてくれます。

コードビハインドにロジックは書いていません。画面の部品のイベントをビューモデルへ渡すだけの用途なら、コードビハインドを使っても問題ありません。

```csharp title="ViewModels/ViewportViewModel.cs"
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

`CompositionTarget.Rendering` は、WPF が画面を 1 フレーム描くたびに、UI スレッドで呼ばれるイベントです。毎秒 60 回ほど呼ばれるので、ここをゲーム ループ代わりにしました。`Stopwatch` で経過時間を測って、`Tick` に渡しています（第 4 章の `steady_clock` と同じ役目です）。

後片付けの順序は、ループを止めてからエンジンを破棄することです。ループが動いたまま破棄すると、破棄済みのエンジンに `Tick` してしまいます。

ただし、このイベントが呼ばれる頻度は保証されていません。画面の更新が必要ないときは呼ばれないことがあり、ゲームの時間が止まる場合もあります。次の章で、専用のスレッドで一定の周期で回す方法に作り替えます。

## モジュールに登録する

```csharp title="ViewportModule.cs"
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

`IEngineService` は第 32 章で `RegisterSingleton` 済みなので、ビューモデルは同じ 1 つのエンジンを受け取ります。エンジンのログも、第 32 章の `NativeLog.Install` のおかげで、ログ タブに出ます。

## 動かしてみる

`F5` で起動します。

- ビューポートの領域で、色がなめらかに変わる（第 3 章の `Tick` の色）。
- ログ タブに「エンジンを初期化しました（W×H）」と、エンジン側の「Engine を作成しました」が出る。
- 仕切りをドラッグして大きさを変えても、色が出続ける。最小化して戻すと、描画が再開する。
- ウィンドウを閉じると、例外なく終了して、ログに「エンジンを破棄しました」が出る。
- メニューやパネル、タブは、普通に操作できる。

??? failure "ビューポートが真っ黒のまま"
    `HandleReady` が呼ばれていません。`OnWindowPositionChanged` が、大きさ 0 のままのはずです。`Border` の中の `Host` が、レイアウトで大きさを持っているかを確かめます。ログに「エンジンを初期化」が出ていなければ、そこで止まっています。

??? failure "ログに「Engine の作成に失敗」と出る"
    スワップ チェーンの作成に失敗しています。出力ウィンドウの `D3D12 ERROR` を見てください。`CreateSwapChainForHwnd` に渡しているのが、WPF の最上位ウィンドウの HWND ではなく、子ウィンドウの HWND になっているかも確かめます。

??? failure "リサイズすると真っ黒になる、エラーが出る"
    `Renderer::Resize` が、バック バッファの参照を残しています（第 3 章）。または、`Resize` の前に `WaitForGpu` していません。

??? failure "終了時にクラッシュする"
    エンジンを破棄する前にウィンドウが壊されています。`DestroyWindowCore` で、先に `HandleDestroying` を呼んでいるかを確認します。

??? failure "`controls:ViewportHost` が見つからない（`MC3074`）"
    `xmlns:controls` の名前空間が合っていないか、`ViewportHost` を作ったあとにまだビルドしていません。一度ビルドしてから XAML を開き直します。

??? failure "拡大率 150% の画面で、絵がぼやける"
    アプリが DPI 対応になっていません。`app.manifest` で PerMonitorV2 を指定します。

次の章では、描画ループを専用のスレッドで回す形に作り替えます。

[第 37 章 描画ループとスレッド](37-render-loop.md) へ進みます。
