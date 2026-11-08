---
title: 第 56 章 ビューポートを別プロセスから受ける
tags:
  - C#連携
---

# 第 56 章 ビューポートを別プロセスから受ける

エンジンを別のプロセスに出すと、ひとつ困ることが起きます。これまでビューポートは、エディタの中の子ウィンドウ（HWND）にエンジンが直接描いていました。プロセスが違うと、その手が使えません。エンジンが描いた絵を、エディタへ届ける道が別に要ります。

この章ではいちばん単純で確かめやすい道を作ります。エンジンが絵を共有メモリへ書きエディタがそれを `WriteableBitmap` に写す方法です。GPU のテクスチャを直接共有する方法のほうが速いのですが、その道は長くこの章では確かめられていません。先に動くものを作りあとから差し替えられる形にしておきます。

!!! info "このページを読む前に"
    - [第 53 章 プロセスを分ける：落ちても生きる構成](53-process-split.md)（なぜ別プロセスか）
    - [第 54 章 IEngineService を差し替える](54-remote-engine-service.md)（`RemoteEngineService`）
    - [第 55 章 エンジンをサーバーにする：EngineHost](55-engine-host.md)（エンジンの起動）
    - [第 36 章 ビューポートの選択肢](36-viewport-options.md)（子ウィンドウと共有テクスチャの比較）

## 絵の届け方を決める

エンジンの絵をエディタに出す道は、大きく 2 つあります。

1. **共有メモリ**: エンジンが、GPU で描いた絵を CPU のメモリに読み戻して、共有メモリに書く。エディタはそこから `WriteableBitmap` へコピーする
2. **共有テクスチャ**: D3D12 のテクスチャを共有ハンドルにして、エディタ側が D3D11、D3D9Ex 経由で `D3DImage` に出す。絵は GPU の中にとどまる

共有テクスチャは速い代わりにデバイスの種類の組み合わせ同期、アダプターの一致と確かめる点が多くあります。共有メモリは GPU から CPU への読み戻しが 1 回入りますが、仕組みは Win32 の `CreateFileMapping` だけで済みます。エディタのビューポートは 60 fps で 1080p までならコピーの時間も許せる範囲です（あとで測ります）。

この章は共有メモリを作ります。`RemoteEngineService` から見えるのは「新しい絵が、この番号のバッファーに出来た」という通知だけなので、将来 GPU 共有に替えても、エディタの他の部分は変わりません。

<svg class="fig flow" viewBox="0 0 720 250" role="img" aria-label="エンジンが共有メモリの 2 枚のバッファーへ交互に書き、エディタがパイプの通知を受けて、書き終えたほうをビットマップへコピーする"><defs><marker id="rvA" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">絵の受け渡し（共有メモリ）</text><rect x="16" y="44" width="190" height="130" rx="14" fill="rgba(148,163,184,0.18)" stroke="#94a3b8" stroke-width="2"/><text x="111" y="66" text-anchor="middle" style="font-size:12px;font-weight:600">EngineHost.exe</text><rect x="32" y="80" width="158" height="34" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="111" y="97" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">描く（GPU）</text><rect x="32" y="124" width="158" height="34" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="111" y="141" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">CPU へ読み戻す</text><rect x="268" y="44" width="184" height="130" rx="14" fill="rgba(229,170,40,0.18)" stroke="#e5aa28" stroke-width="2"/><text x="360" y="66" text-anchor="middle" style="font-size:12px;font-weight:600">共有メモリ</text><rect x="284" y="80" width="152" height="24" rx="6" fill="rgba(229,170,40,0.28)" stroke="#e5aa28" stroke-width="1.5"/><text x="360" y="92" text-anchor="middle" dominant-baseline="central" style="font-size:11px;font-weight:600">ヘッダー（64 バイト）</text><rect x="284" y="110" width="152" height="24" rx="6" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="1.5"/><text x="360" y="122" text-anchor="middle" dominant-baseline="central" style="font-size:11px;font-weight:600">バッファー 0</text><rect x="284" y="140" width="152" height="24" rx="6" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="1.5"/><text x="360" y="152" text-anchor="middle" dominant-baseline="central" style="font-size:11px;font-weight:600">バッファー 1</text><rect x="514" y="44" width="190" height="130" rx="14" fill="rgba(148,163,184,0.18)" stroke="#94a3b8" stroke-width="2"/><text x="609" y="66" text-anchor="middle" style="font-size:12px;font-weight:600">Editor.exe</text><rect x="530" y="80" width="158" height="34" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="609" y="97" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">FramePresenter</text><rect x="530" y="124" width="158" height="34" rx="9" fill="rgba(229,170,40,0.28)" stroke="#e5aa28" stroke-width="2"/><text x="609" y="141" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">WriteableBitmap</text><line x1="190" y1="141" x2="284" y2="122" stroke="currentColor" stroke-width="2" marker-end="url(#rvA)"/><line x1="436" y1="122" x2="530" y2="97" stroke="currentColor" stroke-width="2" marker-end="url(#rvA)"/><line x1="609" y1="114" x2="609" y2="124" stroke="currentColor" stroke-width="2" marker-end="url(#rvA)"/><text x="360" y="208" text-anchor="middle" style="font-size:12px;font-weight:400">tick の返事に「buffer = 1」と入る。エディタは、書き終わった番号のほうだけを読む。</text><text x="360" y="228" text-anchor="middle" style="font-size:12px;font-weight:400">エンジンは次の tick で、もう片方に書く。</text></svg>

## なぜ 2 枚のバッファーか

バッファーが 1 枚だと、エンジンが次の絵を書いている途中に、エディタが読んでしまう危険があります。上半分が新しく、下半分が古い絵が出ます。これをティアリングと呼びます。

バッファーを 2 枚にして書く側と読む側が別の面を触るようにします。エンジンは `tick` の返事の中で「この番号に書き終えた」と伝えます。エディタはその返事を受けてから読み始めるので、読んでいる面にエンジンは書きません。エンジンが次の `tick` を受けて書くのは、もう片方の面です。

これで十分とは言い切れません。エディタのコピーが遅れて、エンジンが 2 回先の `tick` で同じ面に戻ってくれば、読んでいる途中の面に書かれます。この場合の手当ては、あとの「間に合わないとき」で扱います。

## エンジン側：FrameSurface

共有メモリは先頭の 64 バイトにヘッダーを置きその後ろにピクセルを並べます。ヘッダーに大きさを書くのはエディタが開いたときに中身を信用できるか確かめるためです。

```cpp
constexpr uint32_t kFrameMagic = 0x314D5246;   // 'F' 'R' 'M' '1'（リトル エンディアンで読むと 0x314D5246）
constexpr uint32_t kHeaderSize = 64;           // ヘッダーの大きさ。ピクセルはこの後ろから始まる
constexpr uint32_t kBufferCount = 2;           // ダブル バッファー

struct FrameHeader {                           // 共有メモリの先頭
  uint32_t magic;                              // kFrameMagic。別のものを開いてしまったときに気づくため
  uint32_t width;                              // ピクセル
  uint32_t height;
  uint32_t stride;                             // 1 行のバイト数（width * 4）
  uint32_t buffer_count;                       // 何枚あるか
  uint32_t reserved[3];
};
static_assert(sizeof(FrameHeader) <= kHeaderSize);
```

`magic` は、4 文字の目印です。文字の `'F' 'R' 'M' '1'` をリトル エンディアンで並べると 0x314D5246 になります。名前が偶然ぶつかった別の共有メモリを開いても、ここで気づけます。`reserved` は将来の拡張用の空きで、`static_assert` が、ヘッダーが 64 バイトからはみ出さないことを見張ります。

```cpp
class FrameSurface {
 public:
  FrameSurface(const FrameSurface&) = delete;
  FrameSurface& operator=(const FrameSurface&) = delete;

  static std::unique_ptr<FrameSurface> Create(const std::wstring& name, uint32_t width, uint32_t height) {
    const uint32_t stride = width * 4;                                  // BGRA 8 ビット
    const uint64_t size = kHeaderSize + static_cast<uint64_t>(stride) * height * kBufferCount;
    HANDLE mapping = CreateFileMappingW(INVALID_HANDLE_VALUE, nullptr, PAGE_READWRITE,
                                        static_cast<DWORD>(size >> 32), static_cast<DWORD>(size), name.c_str());
    if (mapping == nullptr) return nullptr;
    void* view = MapViewOfFile(mapping, FILE_MAP_ALL_ACCESS, 0, 0, 0);
    if (view == nullptr) {
      CloseHandle(mapping);
      return nullptr;
    }
    auto surface = std::unique_ptr<FrameSurface>(new FrameSurface(mapping, static_cast<uint8_t*>(view), stride, height));
    auto* header = reinterpret_cast<FrameHeader*>(view);
    *header = {kFrameMagic, width, height, stride, kBufferCount, {0, 0, 0}};
    return surface;
  }
```

`CreateFileMappingW` の最初の引数に `INVALID_HANDLE_VALUE` を渡すとファイルを使わずにページング ファイルを裏打ちにしたメモリが取れます。大きさは 64 ビットの値を上位と下位に分けて渡します（1080p の 2 枚なら約 15.8 MiB と、32 ビットに収まりますが書式は変えません）。`name` はエディタが `OpenExisting` で探すための名前です。

大きさの計算は `64 + width × 4 × height × 2` です。1280×720 なら 64 + 5,120 × 720 × 2 = 7,372,864 バイト（約 7 MiB）、1920×1080 なら 約 15.8 MiB になります。

```cpp
  ~FrameSurface() {
    UnmapViewOfFile(view_);
    CloseHandle(mapping_);
  }

  uint8_t* Buffer(uint32_t index) { return view_ + kHeaderSize + static_cast<size_t>(stride_) * height_ * index; }
  uint32_t stride() const { return stride_; }
  uint32_t height() const { return height_; }

 private:
  FrameSurface(HANDLE mapping, uint8_t* view, uint32_t stride, uint32_t height)
      : mapping_(mapping), view_(view), stride_(stride), height_(height) {}

  HANDLE mapping_;
  uint8_t* view_;
  uint32_t stride_;
  uint32_t height_;
};
```

`Buffer(index)` は、index 番目の面の先頭アドレスです。64 バイトのヘッダーを飛ばして、1 枚の大きさ（stride × height）を index 回ぶん進めます。コピーを禁止しているのは、ハンドルの二重解放を防ぐためです。

## 大きさが変わったら、名前を替える

ウィンドウのサイズが変わると、絵の大きさも変わります。共有メモリは作ったあとに大きさを変えられないので、作り直しになります。このとき、同じ名前では作れません。エディタがまだ古いものを開いていれば、同じ名前の `CreateFileMapping` はその古いものを返してしまいます。

そこで、作り直すたびに名前の末尾の番号を増やします。

```cpp
void MakeSurface(uint32_t w, uint32_t h) {
  g_width = w;
  g_height = h;
  ++g_generation;                                                       // 世代番号。作り直すたびに増やす
  const std::wstring name = L"MiniEngineFrame." + std::to_wstring(g_generation);
  g_surface = FrameSurface::Create(name, w, h);                         // 古い g_surface は、ここで閉じる
}
```

名前は `initialize` と `resize` の返事に入れてエディタへ教えます。

```json
{"id":3,"ok":true,"result":{"surface":"MiniEngineFrame.2","width":640,"height":360}}
```

エディタは新しい名前を開き開けたら古いものを閉じます。順番を逆にすると閉じたあとに開けなかったときに表示する絵が一瞬なくなります。

## エディタ側：SharedFrame

エディタは名前で共有メモリを開きヘッダーを確かめます。ここでヘッダーの値をそのまま信用しないことが大切です。エンジンが落ちかけて書きかけのヘッダーを残すこともあります。巨大な幅を信じて確保やコピーをすると、エディタのほうが落ちます。

```csharp
public sealed unsafe class SharedFrame : IDisposable
{
    private const uint Magic = 0x314D5246;     // 'F' 'R' 'M' '1'
    private const int HeaderSize = 64;
    private const int MaxSize = 16384;         // 幅・高さの上限。壊れたヘッダーで巨大な値を信じないため

    private readonly MemoryMappedFile _file;
    private readonly MemoryMappedViewAccessor _view;
    private byte* _base;

    public int Width { get; }
    public int Height { get; }
    public int Stride { get; }
    public int BufferCount { get; }
```

`unsafe` なのは、コピーでポインターを使うためです（プロジェクトの設定で `AllowUnsafeBlocks` を有効にします）。`MaxSize` の 16384 は、このサンプルでの一例です。D3D12 の 2D テクスチャの最大の辺が 16384 なので、それに合わせました。

```csharp
    public static SharedFrame Open(string name)
    {
        var file = MemoryMappedFile.OpenExisting(name, MemoryMappedFileRights.Read);
        var view = file.CreateViewAccessor(0, 0, MemoryMappedFileAccess.Read);
        byte* p = null;
        view.SafeMemoryMappedViewHandle.AcquirePointer(ref p);

        uint magic = view.ReadUInt32(0);
        int width = view.ReadInt32(4), height = view.ReadInt32(8), stride = view.ReadInt32(12), count = view.ReadInt32(16);
        bool valid = magic == Magic && width is > 0 and <= MaxSize && height is > 0 and <= MaxSize
                     && stride == width * 4 && count is >= 1 and <= 4
                     && HeaderSize + (long)stride * height * count <= view.Capacity;
        if (!valid)
        {
            view.SafeMemoryMappedViewHandle.ReleasePointer();
            view.Dispose();
            file.Dispose();
            throw new InvalidDataException($"共有メモリ '{name}' のヘッダーが不正です。");
        }
        return new SharedFrame(file, view, p, width, height, stride, count);
    }
```

読み取り専用（`Read`）で開くのは、エディタ側からエンジンの絵を壊さないためです。検査の最後の行が実際の共有メモリの大きさ（`view.Capacity`）にヘッダーが言う大きさが収まるかを見ます。ヘッダーだけ大きな値でメモリが小さい場合に範囲外を読むのを防ぎます。検査に落ちたら確保したものを解放してから例外にします。解放を忘れると不正な共有メモリを開いたまま残ります。

```csharp
    // buffer 番目の絵を、dest（stride が destStride の画像）へ、行ごとにコピーする
    public void CopyBufferTo(int buffer, nint dest, int destStride)
    {
        if ((uint)buffer >= (uint)BufferCount) throw new ArgumentOutOfRangeException(nameof(buffer));
        byte* src = _base + HeaderSize + (long)Stride * Height * buffer;
        int rowBytes = Math.Min(Stride, destStride);
        for (int y = 0; y < Height; y++)
        {
            Buffer.MemoryCopy(src + (long)y * Stride, (byte*)dest + (long)y * destStride, destStride, rowBytes);
        }
    }
```

コピーを 1 行ずつにするのは、コピー先の `WriteableBitmap` の 1 行の長さ（`BackBufferStride`）が、こちらの `Stride` と同じとは限らないからです。同じなら一度にコピーできますが、違ったときにずれた絵が出ます。`buffer` の範囲検査はエンジンから届く番号も信用しない、という考えです。

```csharp
    public void Dispose()
    {
        if (_base != null)
        {
            _view.SafeMemoryMappedViewHandle.ReleasePointer();
            _base = null;
        }
        _view.Dispose();
        _file.Dispose();
    }
}
```

## WPF に出す：FramePresenter

`WriteableBitmap` は CPU のメモリを書き換えて表示できる WPF の画像です。`Lock` で裏のバッファー（`BackBuffer`）を借りコピーして、`AddDirtyRect` で書き換えた範囲を伝え `Unlock` で返します。

```csharp
public sealed class FramePresenter
{
    public WriteableBitmap? Bitmap { get; private set; }

    // 絵を写す。大きさが変わっていたら、ビットマップを作り直す（Image.Source を差し替える合図に、true を返す）
    public bool Present(Editor.Engine.SharedFrame frame, int buffer)
    {
        bool recreated = false;
        if (Bitmap is null || Bitmap.PixelWidth != frame.Width || Bitmap.PixelHeight != frame.Height)
        {
            Bitmap = new WriteableBitmap(frame.Width, frame.Height, 96, 96, PixelFormats.Bgr32, null);   // A は無視する形式
            recreated = true;
        }

        Bitmap.Lock();
        try
        {
            frame.CopyBufferTo(buffer, Bitmap.BackBuffer, Bitmap.BackBufferStride);
            Bitmap.AddDirtyRect(new Int32Rect(0, 0, frame.Width, frame.Height));
        }
        finally
        {
            Bitmap.Unlock();
        }
        return recreated;
    }
}
```

形式を `Bgr32` にしているのはエンジンの BGRA のうちアルファを無視して表示するためです。`Bgra32` にするとアルファが 0 の画素が透けて、ビューポートの後ろの色が混ざります。`try / finally` で `Unlock` を必ず呼ぶのは `Lock` したまま例外で抜けると、それ以降の `Lock` が固まるからです。

`WriteableBitmap` は UI スレッドの持ち物です。`Present` は UI スレッドで呼びます。`Image.Source` に `Bitmap` を設定するのは、最初に作ったときと、`true` が返ったときだけです。

## RemoteEngineService に足す

第 54 章の `RemoteEngineService` に絵の受け取りを足します。足すのは `Frame` と 2 つのイベント、`OpenSurface` です。

```csharp
// 足す：エンジンが絵を書き込む共有メモリ。大きさが変わると、新しいものに替わる
public SharedFrame? Frame { get; private set; }

// 足す：Tick のあとに、新しい絵が出来たことを知らせる（描画スレッドから呼ばれる）。引数は、絵が入ったバッファーの番号
public event Action<int>? FrameReady;

// 足す：Frame が新しいものに替わったとき
public event Action? FrameChanged;

public void Initialize(nint windowHandle, uint width, uint height)
{
    if (_running) throw new InvalidOperationException("すでに初期化されています");
    OpenSurface(Call("initialize", new { width, height }));
    _running = true;
}

public void Resize(uint width, uint height) => OpenSurface(Call("resize", new { width, height }));

public void Tick(float deltaSeconds)
{
    JsonElement reply = Call("tick", new { dt = deltaSeconds }).GetProperty("result");
    FrameReady?.Invoke(reply.GetProperty("buffer").GetInt32());
}

private void OpenSurface(JsonElement reply)
{
    string name = reply.GetProperty("result").GetProperty("surface").GetString()!;
    SharedFrame? old = Frame;
    Frame = SharedFrame.Open(name);
    FrameChanged?.Invoke();
    old?.Dispose();                              // 通知のあとで閉じる（受け手が、古いものを使い終わっている前提）
}
```

`Initialize` の `windowHandle` は、この構成では使いません。HWND を渡しても、別プロセスの子ウィンドウにはならないからです。`IEngineService` の形を変えないために、引数だけ残します。

`FrameReady` は描画スレッドで起きます。そこで `WriteableBitmap` を触ってはいけません。受け手は、UI スレッドへ切り替えてから `Present` を呼びます。

## UI スレッドへ渡す：間に合わないとき

描画スレッドが 60 fps で `FrameReady` を起こし、UI スレッドが重い処理で遅れると、`Dispatcher.BeginInvoke` の列が溜まります。古い絵を順に写しても意味がありません。最新の 1 枚だけ写せばよいので、「前のコピーがまだ終わっていなければ、今回は捨てる」ようにします。

```csharp
private int _copyPending;                        // 0 = 空き、1 = UI スレッドでコピー待ち

private void OnFrameReady(int buffer)
{
    if (Interlocked.Exchange(ref _copyPending, 1) == 1) return;     // 前のコピーが終わっていない。今回は捨てる

    Dispatcher.BeginInvoke(() =>
    {
        try
        {
            if (_engine.Frame is { } frame && _presenter.Present(frame, buffer))
                ViewportImage.Source = _presenter.Bitmap;           // 大きさが変わったときだけ差し替える
        }
        finally
        {
            Volatile.Write(ref _copyPending, 0);
        }
    });
}
```

`Interlocked.Exchange` は旗を 1 にして前の値を返します。前の値が 1 だったなら前のコピーが待っているので、今回の通知は捨てます。コピーの終わりで 0 に戻します。

これでエンジンと UI の速さが違っても、UI は最新に近い絵を写し続けます。ただし、`buffer` の面にエンジンが 2 回先の `tick` で書き戻っていれば、写している途中の面が書き換わります。そのときは、半分が新しい絵が 1 フレームだけ出ます。60 fps の中の 1 コマなので気づきにくいのですが、気になるなら `kBufferCount` を 3 にします。ヘッダーには面の数を書いてあるので、エディタ側は変えずに済みます。

## 測ってみる

WPF のテスト プロジェクトで、次の順に動かしました。テスト用のエンジンはフレーム番号、x、y を B、G、R に入れた絵を書くだけのものです。

1. `initialize` で 1280×720 の共有メモリを作る
2. `tick` を 3 回呼び、`Present` したあと、ビットマップの 1 画素（x=100、y=50）を読む
3. `resize` で 640×360 に替える
4. 1280×720 と 1920×1080 で、`Present` を 200 回呼んだ平均を測る

```text title="実行結果（Release、同じ PC）"
tick 1: buffer=1 size=1280x720 pixel(100,50) B=1 G=100 R=50
tick 2: buffer=0 size=1280x720 pixel(100,50) B=2 G=100 R=50
tick 3: buffer=1 size=1280x720 pixel(100,50) B=3 G=100 R=50
after resize: FrameChanged=2 recreated=True size=640x360
1280x720: 0.08 ms per copy (3.5 MiB)
1920x1080: 0.17 ms per copy (7.9 MiB)
missing -> FileNotFoundException
```

`B` がフレーム番号どおりに増え `buffer` が 1、0、1 と交互に替わっています。`G=100 R=50` は x と y が正しい場所に写っている証拠です。`resize` のあと `FrameChanged` が 2 回（初期化と resize）起きビットマップが作り直されました。存在しない名前を開くと `FileNotFoundException` になります。

コピーの時間は、1280×720 で 0.08 ms、1920×1080 で 0.17 ms でした。60 fps の 1 フレームが 16.7 ms なので、1 % 前後です。ただし、これは共有メモリからビットマップへのコピーだけの値です。エンジンの GPU から CPU への読み戻しは含みません。

## GPU から CPU へ読み戻す（確かめていない）

本物のエンジンでは、描いた絵が GPU のテクスチャにあるので、共有メモリに書く前に CPU へ読み戻します。D3D12 の手順は次のとおりです。ここの C++ はコンパイルしていません。ヒープやバリアの組み立ては、このサイトの `dx12_util.h`（[DirectX 12 の補助関数](../directx/dx12/util.md)）の関数を使う前提で書きましたが、手元のエンジンで動かして確かめたものではありません。

1. `GetCopyableFootprints` で、テクスチャの 1 行の幅（RowPitch）と、全体の大きさを調べる
2. 大きさ分の READBACK ヒープのバッファーを作る（`MakeHeapProperties(D3D12_HEAP_TYPE_READBACK)` と `MakeBufferDesc`）
3. レンダー ターゲットを `COPY_SOURCE` に遷移させ（`MakeTransitionBarrier`）、`CopyTextureRegion` でバッファーへコピーする
4. フェンスで GPU の完了を待つ
5. バッファーを `Map` して、共有メモリへ、1 行ずつコピーする

```cpp
// 確かめていない。GPU が書いた絵を、共有メモリの buffer へ移す手順（要点だけ）
D3D12_PLACED_SUBRESOURCE_FOOTPRINT footprint = {};
UINT64 total_bytes = 0;
device->GetCopyableFootprints(&render_target_desc, 0, 1, 0, &footprint, nullptr, nullptr, &total_bytes);

// footprint.Footprint.RowPitch は 256 バイトの倍数。width * 4 より大きいことがある
const uint8_t* mapped = nullptr;
D3D12_RANGE read_range = {0, static_cast<SIZE_T>(total_bytes)};
readback_buffer->Map(0, &read_range, reinterpret_cast<void**>(const_cast<uint8_t**>(&mapped)));
for (UINT y = 0; y < height; ++y) {
  memcpy(dest + y * dest_stride, mapped + y * footprint.Footprint.RowPitch, width * 4);   // 行ごと。幅が違うため
}
readback_buffer->Unmap(0, nullptr);
```

行ごとにコピーする理由はエディタ側の `CopyBufferTo` と同じです。READBACK バッファーの 1 行は、256 バイトの倍数に切り上げられる（`RowPitch`）ので、幅 × 4 とは違います。1280×720 なら 5,120 バイトでちょうど 256 の倍数ですが、1000 ピクセル幅なら 4,000 が 4,096 になります。ここを忘れると斜めにずれた絵が出ます。

読み戻しは GPU の完了を待つぶんそのフレームの遅延が増えます。待たないために前のフレームの絵を読み戻し、1 フレーム遅れて表示する作りにすることもあります。

## マウスとキーを送る

絵が別プロセスにあるとビューポート上のマウスやキーは、エディタが受けてエンジンへ送ることになります。第 54 章の命令と同じくパイプのメッセージです。ただし、マウスの移動は毎フレーム何度も起きるので、返事を待つ命令にはしません。`id` のない通知（第 53 章）として送り返事は期待しません。

```json
{"cmd":"input_mouse","args":{"x":412,"y":230,"buttons":1,"wheel":0}}
```

ここのコードはこの章では書いていません。座標は絵の左上を原点にしたピクセルで送りビューポートの表示サイズと絵の大きさが違うときは、エディタ側で換算します。

## 共有テクスチャへの道

共有メモリでは読み戻しの遅延と CPU の帯域が上限になります。4K のビューポートや 120 fps を目指すなら GPU 共有を考えることになります。

1. エンジンが `ID3D12Device::CreateSharedHandle` で、テクスチャの共有ハンドルを作る
2. エディタが D3D11 のデバイスで、そのハンドルを開く
3. D3D9Ex 経由で `D3DImage` に出す

この 3 つのつなぎはデバイスの種類ごとの制約がありこの章では動かしていません。`RemoteEngineService` のイベントが「この番号の絵が出来た」という形なので、`FrameReady` を受けて共有テクスチャの面を切り替える実装に後から替えられます。

## よくあるミス

??? failure "ビューポートが、ずれた模様になる"
    **原因**: コピー先の `BackBufferStride` が、`width * 4` と同じとは限りません。まとめてコピーすると、行がずれます。
    **対処**: 1 行ずつ、コピー先の stride で進めます（`CopyBufferTo`）。

??? failure "大きさを変えたら、エディタが落ちる"
    **原因**: 共有メモリを同じ名前で作り直すと、エディタの開いている古いものが返ります。大きさが違うまま読むと、範囲外を触ります。
    **対処**: 作り直すたびに名前の番号を増やし、エディタは開けたあとで古いものを閉じます。

??? failure "ときどき、上下で別の絵が見える"
    **原因**: エディタのコピー中に、エンジンが同じ面に書き戻ってきます。
    **対処**: 面を 3 枚にします。それでも出るなら、UI のコピーが 16 ms 以上かかっている別の原因を探します。

??? failure "透けた絵になる"
    **原因**: ビットマップの形式が `Bgra32` で、エンジンが書いたアルファが 0 のままです。
    **対処**: `Bgr32` にするか、エンジンがアルファを 255 で書きます。

## まとめ

- 別プロセスのエンジンの絵は、共有メモリの 2 枚のバッファーに書き、エディタが `WriteableBitmap` へ写す
- 大きさが変わったら、共有メモリの名前を替えて、エディタは開けてから古いものを閉じる
- ヘッダーの値は信用せず、`magic`・上限・実際の大きさで確かめる
- コピーは 1080p で 0.17 ms だった。GPU 側の読み戻しと共有テクスチャは、この章では確かめていない

!!! note "確かめたもの、確かめていないもの"
    共有メモリの作成（C++）、`SharedFrame`、`FramePresenter`、`RemoteEngineService` の追加部分はテスト用のサーバーとつないでコンパイルして確かめた（C++ は g++ の `-Wall -Wextra` で警告なし）。D3D12 の読み戻し、入力の送信、UI 側の間引き（`OnFrameReady`）、共有テクスチャはコンパイルも実行もしていない。

次は、エンジンが落ちたときの扱いです。[第 57 章 落ちたら立て直す](57-recovery.md) へ進みます。
