---
title: Device and Factory
tags:
  - DirectX
---

# Device and Factory

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

D3D12 の出発点は <strong>DXGI ファクトリー</strong>で、GPU（アダプター）を選びそのアダプターから<strong>デバイス</strong>（`ID3D12Device`）を作ります。デバイスは GPU に「物を作らせる」窓口で、リソース、ヒープ、PSO、ルート シグネチャ、コマンド キューなどはすべてデバイスが作ります。<strong>命令を出す窓口はデバイスにはありません</strong>（命令はコマンド リストに記録します）。

!!! tip "ポイント"
    - デバイス ＝ 作る窓口。命令を出すのはデバイスではなく、[Command List](command-list.md) に記録する。
    - <strong>デバッグ レイヤーはデバイスを作る前に</strong>有効にする（`EnableDebugLayer`）。
    - アダプターは DXGI で選ぶ。高性能な GPU を優先する。
    - 機能レベルは 11.0 以上。個々の機能（DXR、メッシュ シェーダー）は `CheckFeatureSupport` で確認する。
    - 新しい機能は `ID3D12Device5`、`Device10` のような番号つきのインターフェースにある。

!!! info "このページを読む前に"
    `ComPtr<T>` は COM オブジェクトの参照カウントを自動で管理するスマート ポインタです（[所有権](../../basics/ownership.md)の考え方と同じです）。`IID_PPV_ARGS` や `QueryInterface` といった COM の書き方は、このページで出てきたときに説明します。D3D12 全体の見取り図は [DirectX 12 Guide](index.md) にあります。

## 全体の流れ

<svg class="fig flow" viewBox="0 0 720 276" role="img" aria-label="ファクトリーからアダプター、デバイスへ。デバイスが作る物"><defs><marker id="fdA" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">デバイスは「作る窓口」</text><rect x="16" y="52" width="150" height="44" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="91.0" y="74.0" text-anchor="middle" dominant-baseline="central" style="font-size:13px;font-weight:600">DXGI ファクトリー</text><rect x="206" y="52" width="170" height="44" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="291.0" y="74.0" text-anchor="middle" dominant-baseline="central" style="font-size:13px;font-weight:600">アダプター（GPU）</text><rect x="416" y="52" width="180" height="44" rx="9" fill="rgba(229,170,40,0.28)" stroke="#e5aa28" stroke-width="2"/><text x="506.0" y="74.0" text-anchor="middle" dominant-baseline="central" style="font-size:13px;font-weight:600">デバイス ID3D12Device</text><line x1="166" y1="74" x2="206" y2="74" stroke="currentColor" stroke-width="2" marker-end="url(#fdA)"/><line x1="376" y1="74" x2="416" y2="74" stroke="currentColor" stroke-width="2" marker-end="url(#fdA)"/><text x="186" y="66" text-anchor="middle" style="font-size:12px;font-weight:400">列挙</text><text x="396" y="66" text-anchor="middle" style="font-size:12px;font-weight:400">作る</text><rect x="16" y="168" width="160" height="44" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="96.0" y="190.0" text-anchor="middle" dominant-baseline="central" style="font-size:13px;font-weight:600">リソース・ヒープ</text><line x1="506" y1="96" x2="96" y2="168" stroke="currentColor" stroke-width="2" marker-end="url(#fdA)"/><rect x="186" y="168" width="160" height="44" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="266.0" y="190.0" text-anchor="middle" dominant-baseline="central" style="font-size:13px;font-weight:600">パイプライン（PSO）</text><line x1="506" y1="96" x2="266" y2="168" stroke="currentColor" stroke-width="2" marker-end="url(#fdA)"/><rect x="356" y="168" width="160" height="44" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="436.0" y="190.0" text-anchor="middle" dominant-baseline="central" style="font-size:13px;font-weight:600">コマンド キュー</text><line x1="506" y1="96" x2="436" y2="168" stroke="currentColor" stroke-width="2" marker-end="url(#fdA)"/><rect x="526" y="168" width="160" height="44" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="606.0" y="190.0" text-anchor="middle" dominant-baseline="central" style="font-size:13px;font-weight:600">フェンス（同期）</text><line x1="506" y1="96" x2="606" y2="168" stroke="currentColor" stroke-width="2" marker-end="url(#fdA)"/><text x="360" y="240" text-anchor="middle" style="font-size:12px;font-weight:400">リソースも PSO もキューも、デバイスが作る。命令を出す窓口はデバイスにはなく、</text><text x="360" y="258" text-anchor="middle" style="font-size:12px;font-weight:400">命令はコマンド リストに記録する。</text></svg>

デバイスを作るまでに関数を 6 つ使います。呼ぶ順に並べると次のとおりです。

| 関数 | 役割 |
| --- | --- |
| [`D3D12GetDebugInterface`](#d3d12getdebuginterface) | デバッグ レイヤーを操作する口を取り出す |
| [`EnableDebugLayer`](#enabledebuglayer) | デバッグ レイヤーを有効にする |
| [`CreateDXGIFactory2`](#createdxgifactory2) | ファクトリーを作る |
| [`EnumAdapterByGpuPreference`](#enumadapterbygpupreference) | GPU を性能の高い順に 1 つずつ取り出す |
| [`GetDesc1`](#getdesc1) | アダプターの名前や種類を調べる |
| [`D3D12CreateDevice`](#d3d12createdevice) | デバイスを作る |

デバイスができたあとに使うのが、機能を調べる [`CheckFeatureSupport`](#checkfeaturesupport)、番号つきのインターフェースを取り出す [`QueryInterface`（`As`）](#queryinterface-as)、デバッグ用に名前を付ける [`SetName`](#setname) です。

## 作る流れ

まず、6 つの関数をつなげた形を示します。1 つずつの引数と戻り値は次の「関数の詳しい説明」で見ます。

```cpp
#include <d3d12.h>
#include <dxgi1_6.h>
#include <wrl/client.h>

using Microsoft::WRL::ComPtr;

// 1. デバッグ レイヤー（デバイスを作る「前」）。
UINT factory_flags = 0;
#if defined(_DEBUG)
{
  ComPtr<ID3D12Debug> debug;
  if (SUCCEEDED(D3D12GetDebugInterface(IID_PPV_ARGS(&debug)))) {
    debug->EnableDebugLayer();
    factory_flags |= DXGI_CREATE_FACTORY_DEBUG;
  }
}
#endif

// 2. ファクトリー。
ComPtr<IDXGIFactory6> factory;
CreateDXGIFactory2(factory_flags, IID_PPV_ARGS(&factory));

// 3. 高性能な GPU から順に見て、D3D12 に対応する最初のアダプターを選ぶ。
ComPtr<IDXGIAdapter1> adapter;
for (UINT i = 0;
     factory->EnumAdapterByGpuPreference(i, DXGI_GPU_PREFERENCE_HIGH_PERFORMANCE, IID_PPV_ARGS(&adapter)) !=
     DXGI_ERROR_NOT_FOUND;
     ++i) {
  DXGI_ADAPTER_DESC1 desc;
  adapter->GetDesc1(&desc);
  if (desc.Flags & DXGI_ADAPTER_FLAG_SOFTWARE) continue;  // WARP（ソフトウェア）は飛ばす
  // 最後の引数が nullptr だと、作れるかどうかだけを確認する（デバイスは作らない）。
  if (SUCCEEDED(D3D12CreateDevice(adapter.Get(), D3D_FEATURE_LEVEL_11_0, __uuidof(ID3D12Device), nullptr))) break;
}

// 4. デバイス。
ComPtr<ID3D12Device> device;
HRESULT hr = D3D12CreateDevice(adapter.Get(), D3D_FEATURE_LEVEL_11_0, IID_PPV_ARGS(&device));
if (FAILED(hr)) {
  // 失敗: GPU が D3D12 に対応していない。WARP（ソフトウェア）で再試行する
}
```

アダプターの列挙は DXGI の仕事で、D3D12 の関数ではありません。次の「関数の詳しい説明」で使う関数を 1 つずつ説明します。

## 関数の詳しい説明

### D3D12GetDebugInterface {#d3d12getdebuginterface}

```cpp
HRESULT D3D12GetDebugInterface(REFIID riid, void** ppvDebug);
```

デバッグ レイヤーを操作するためのインターフェース（`ID3D12Debug`）を取り出します。デバイスはまだありません。この関数はデバイスとは無関係に呼べるただの関数です。

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `riid` | `REFIID` | 取り出したいインターフェースの ID。`ID3D12Debug` なら `__uuidof(ID3D12Debug)` |
| `ppvDebug` | `void**` | 結果を受け取るポインタのアドレス |

`riid` と `ppvDebug` の 2 つは `IID_PPV_ARGS(&debug)` でまとめて書きます。後ろの `D3D12CreateDevice` の節でこのマクロの意味を説明します。

戻り値は `HRESULT` です。成功すれば `S_OK` で `ppvDebug` に入ったポインタが使えます。失敗したときはそのポインタを使えません。たとえば、Windows の「グラフィックス ツール」（オプション機能）が入っていない PC では失敗します。リリース版の PC に入っていないのはふつうなので、失敗しても止まらずデバッグ レイヤーなしで続けるのが定石です。上のコードはそのとおりに `SUCCEEDED` で分けています。

### EnableDebugLayer {#enabledebuglayer}

```cpp
void ID3D12Debug::EnableDebugLayer();
```

デバッグ レイヤーを有効にします。引数も戻り値もありません。

タイミングが大事で <strong>デバイスを作る前</strong>に呼びます。作ったあとで呼ぶとすでにあるデバイスが削除されてしまいます。レイヤーが有効になるとリソースの使い方の間違いやバリアの抜けなどが、Visual Studio の出力ウィンドウにメッセージとして出ます。実行は遅くなるので `#if defined(_DEBUG)` でデバッグ ビルドだけに入れます。詳しくは [Debug Layer](debug-layer.md) にまとめています。

### CreateDXGIFactory2 {#createdxgifactory2}

```cpp
HRESULT CreateDXGIFactory2(UINT Flags, REFIID riid, void** ppFactory);
```

DXGI のファクトリーを作ります。ファクトリーは GPU（アダプター）の一覧を取り出したりスワップ チェーンを作ったりするための入り口です。

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `Flags` | `UINT` | `0`、または `DXGI_CREATE_FACTORY_DEBUG` |
| `riid` | `REFIID` | 取り出すインターフェースの ID。ここでは `IDXGIFactory6` |
| `ppFactory` | `void**` | 結果を受け取るポインタのアドレス |

`Flags` に `DXGI_CREATE_FACTORY_DEBUG` を渡すと DXGI 側のデバッグ メッセージ（スワップ チェーンの作り方の間違いなど）も出るようになります。デバッグ レイヤーを有効にできたときだけ渡します。それ以外は `0` です。

`IDXGIFactory6` の `6` は機能を足すたびに増えてきた番号です（あとの [QueryInterface](#queryinterface-as) の節で説明します）。このあと使う `EnumAdapterByGpuPreference` はこの 6 から入ったので、`IDXGIFactory6` で受け取ります。Windows 10 の 1803 より前では取り出せません。

戻り値は `HRESULT` で成功は `S_OK` です。通常の PC で失敗することはまずありません。

### EnumAdapterByGpuPreference {#enumadapterbygpupreference}

```cpp
HRESULT IDXGIFactory6::EnumAdapterByGpuPreference(
    UINT Adapter,
    DXGI_GPU_PREFERENCE GpuPreference,
    REFIID riid,
    void** ppvAdapter);
```

PC に載っている GPU を指定した優先順で 1 つずつ取り出します。

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `Adapter` | `UINT` | 何番目か。0 から始めて `DXGI_ERROR_NOT_FOUND` が返るまで 1 ずつ増やす |
| `GpuPreference` | `DXGI_GPU_PREFERENCE` | 並べ替えの基準（下の表） |
| `riid` | `REFIID` | 取り出すインターフェースの ID。ここでは `IDXGIAdapter1` |
| `ppvAdapter` | `void**` | 結果を受け取るポインタのアドレス |

`GpuPreference` には次の 3 つがあります。

| 値 | 並び順 |
| --- | --- |
| `DXGI_GPU_PREFERENCE_UNSPECIFIED` | 指定なし（`EnumAdapters1` と同じ順） |
| `DXGI_GPU_PREFERENCE_MINIMUM_POWER` | 消費電力が低い順（内蔵 GPU が先） |
| `DXGI_GPU_PREFERENCE_HIGH_PERFORMANCE` | 性能が高い順（外付け GPU が先） |

ゲームでは `HIGH_PERFORMANCE` を使います。ノート PC には内蔵 GPU と外付け GPU が両方載っていることがあり、順番を気にせずに最初の 1 つを取ると、遅い内蔵 GPU になりがちだからです。

戻り値は成功なら `S_OK` です。`Adapter` が範囲を超えると `DXGI_ERROR_NOT_FOUND` が返ります。これは「エラー」というより「もう GPU は残っていない」という終わりの合図で、`for` ループの終了条件に使います。

### GetDesc1 {#getdesc1}

```cpp
HRESULT IDXGIAdapter1::GetDesc1(DXGI_ADAPTER_DESC1* pDesc);
```

アダプターの名前や種類を調べます。引数は結果を書き込む `DXGI_ADAPTER_DESC1` 1 つだけです。戻り値は成功なら `S_OK` です。

構造体のうち使うことが多い項目は次の 4 つです。

| 項目 | 意味 |
| --- | --- |
| `Description` | GPU の名前（`WCHAR[128]`）。ログに出す |
| `VendorId` | メーカーの番号。`0x10DE` が NVIDIA、`0x1002` が AMD、`0x8086` が Intel、`0x1414` が Microsoft（WARP） |
| `DedicatedVideoMemory` | GPU 専用のメモリ（VRAM）の大きさ（バイト） |
| `Flags` | `DXGI_ADAPTER_FLAG_SOFTWARE` が立っていれば、GPU ではなくソフトウェア（WARP） |

上のコードで `Flags` を見ているのは、WARP を飛ばすためです。WARP は GPU がない PC でも D3D12 を動かすために CPU が代わりに描く仕組みで、とても遅いため最初の候補にはしません。使うのは本物の GPU がどれも使えなかったときの最後の手段です。

### D3D12CreateDevice {#d3d12createdevice}

```cpp
HRESULT D3D12CreateDevice(
    IUnknown* pAdapter,
    D3D_FEATURE_LEVEL MinimumFeatureLevel,
    REFIID riid,
    void** ppDevice);
```

デバイスを作ります。

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `pAdapter` | `IUnknown*` | 使う GPU。`nullptr` で既定のアダプター |
| `MinimumFeatureLevel` | `D3D_FEATURE_LEVEL` | 必要な最低の機能レベル |
| `riid` | `REFIID` | 取り出すインターフェースの ID。`ID3D12Device` など |
| `ppDevice` | `void**` | 結果を受け取るポインタのアドレス。`nullptr` なら作らずに確認だけする |

4 つの引数を 1 つずつ見ます。

#### pAdapter

使う GPU を渡します。前の節で選んだ `adapter.Get()` がここに入ります。`nullptr` を渡すとシステムが「既定」とみなすアダプターが使われます。

既定に任せてよさそうに見えますが、ノート PC のように内蔵 GPU と外付け GPU が両方ある環境では、内蔵のほうが既定になることがあります。何も指定しないまま動かして「手元では速いのに、友達の PC では遅い」となる原因の 1 つです。ゲームでは `EnumAdapterByGpuPreference` で高性能なほうを選んで渡します。

#### MinimumFeatureLevel

「この GPU が少なくともここまでの機能を持っていないならデバイスを作らなくてよい」という下限です。`D3D_FEATURE_LEVEL_11_0`、`11_1`、`12_0`、`12_1`、`12_2` から選びます。下限を満たさない GPU では `D3D12CreateDevice` が失敗するので、高い値を渡すほど遊べる環境が狭くなります。

D3D12 で渡せる最低値は 11.0 です。これは D3D11 世代の古い GPU でもドライバーさえ D3D12 に対応していれば、D3D12 の API 自体は使えるようにするためです。ただし、そうした GPU は機能が限られます。DXR やメッシュ シェーダーのような新しい機能は使えませんし、リソース バインディングもいちばん低い Tier 1 にとどまります。

通常は 11.0 を渡して使いたい機能があるときだけ `CheckFeatureSupport` で確かめます。機能レベルを高くすると「使わない機能が足りないだけ」の GPU まで遊べなくなるからです。

#### riid と ppDevice

この 2 つは「どのインターフェースの形で受け取るか」と「受け取る先」のペアです。COM のオブジェクトは同じ実体に対して、機能が違う何種類ものインターフェース（`ID3D12Device`、`ID3D12Device5` など）を持てます。`riid` でその種類を ID（`__uuidof(ID3D12Device)`）で指定し `ppDevice` に結果のポインタを書き込んでもらいます。

型と ID を別々に書くと食い違ったときに実行時エラーになります。そこで `IID_PPV_ARGS(&device)` を使います。これは `device` の型から `riid` を自動で求め `ppDevice` に `void**` として渡してくれるマクロで、型を 1 回しか書かずに済みます。

`ppDevice` に `nullptr` を渡すとデバイスは作らず「作れるかどうか」だけを確かめます。前の節のアダプター選びで使っていたのは、この使い方です。確認だけのときは成功しても `S_OK` ではなく別の成功値が返ることがあるので、`SUCCEEDED` で判定します。

#### 戻り値

成功なら `ppDevice` にデバイスが入ります。失敗する主な原因は次のとおりです。

| 原因 | 対処 |
| --- | --- |
| GPU かドライバーが D3D12 に対応していない | ドライバーを更新する。だめなら WARP（`IDXGIFactory4::EnumWarpAdapter`）で再試行する |
| `MinimumFeatureLevel` が GPU の機能レベルより高い | 渡す値を下げる |
| デバッグ レイヤーを有効にしたのに、「グラフィックス ツール」が入っていない | ツールを入れるかデバッグ レイヤーを外す |
| メモリ不足 | 他のアプリを閉じる。VRAM が足りないことが多い |

### CheckFeatureSupport {#checkfeaturesupport}

```cpp
HRESULT ID3D12Device::CheckFeatureSupport(
    D3D12_FEATURE Feature,
    void* pFeatureSupportData,
    UINT FeatureSupportDataSize);
```

「この GPU とドライバーはこの機能を持っていますか」とデバイスに聞きます。

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `Feature` | `D3D12_FEATURE` | 何を聞くか（`D3D12_FEATURE_D3D12_OPTIONS5` など） |
| `pFeatureSupportData` | `void*` | 答えを書き込む構造体。`Feature` ごとに型が決まっている |
| `FeatureSupportDataSize` | `UINT` | その構造体のサイズ。`sizeof` で渡す |

戻り値は `HRESULT` です。成功なら `S_OK` で構造体に答えが入ります。聞いた機能を動いている Windows やドライバーが知らないと `E_INVALIDARG` で失敗します。

機能レベル 11.0 や 12.0 という数字 1 つでは、DXR やメッシュ シェーダーを持っているかどうかまでは分かりません。そこで、使う前に機能ごとに聞きます。

<svg class="fig flow" viewBox="0 0 720 252" role="img" aria-label="機能レベルで足切りし、機能ごとに CheckFeatureSupport で聞く"><defs><marker id="fdB" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">足切りと、機能ごとの確認</text><rect x="12" y="56" width="112" height="46" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="68.0" y="79.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">アダプター</text><rect x="152" y="56" width="142" height="46" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="223.0" y="79.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">D3D12CreateDevice</text><rect x="322" y="56" width="152" height="46" rx="9" fill="rgba(229,170,40,0.28)" stroke="#e5aa28" stroke-width="2"/><text x="398.0" y="79.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">デバイス</text><rect x="502" y="56" width="190" height="46" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="597.0" y="79.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">CheckFeatureSupport</text><line x1="124" y1="79" x2="152" y2="79" stroke="currentColor" stroke-width="2" marker-end="url(#fdB)"/><line x1="294" y1="79" x2="322" y2="79" stroke="currentColor" stroke-width="2" marker-end="url(#fdB)"/><line x1="474" y1="79" x2="502" y2="79" stroke="currentColor" stroke-width="2" marker-end="url(#fdB)"/><text x="223" y="124" text-anchor="middle" style="font-size:12px;font-weight:400">足切り：最低の機能レベル</text><text x="223" y="142" text-anchor="middle" style="font-size:12px;font-weight:400">（11_0）に満たない GPU は失敗</text><line x1="597" y1="102" x2="597" y2="150" stroke="currentColor" stroke-width="2" marker-end="url(#fdB)"/><text x="597" y="124" text-anchor="middle" style="font-size:12px;font-weight:400">機能ごとに聞く</text><rect x="372" y="156" width="108" height="40" rx="9" fill="rgba(148,163,184,0.18)" stroke="#94a3b8" stroke-width="2"/><text x="426.0" y="176.0" text-anchor="middle" dominant-baseline="central" style="font-size:11px;font-weight:600">DXR</text><rect x="488" y="156" width="108" height="40" rx="9" fill="rgba(148,163,184,0.18)" stroke="#94a3b8" stroke-width="2"/><text x="542.0" y="176.0" text-anchor="middle" dominant-baseline="central" style="font-size:11px;font-weight:600">メッシュ シェーダー</text><rect x="604" y="156" width="108" height="40" rx="9" fill="rgba(148,163,184,0.18)" stroke="#94a3b8" stroke-width="2"/><text x="658.0" y="176.0" text-anchor="middle" dominant-baseline="central" style="font-size:11px;font-weight:600">バインドレス</text><text x="360" y="232" text-anchor="middle" style="font-size:12px;font-weight:400">ゲームは、聞いた答えに合わせて機能を入れ替える（DXR の影をオン／オフ、など）。</text></svg>

```cpp
// DXR（レイトレーシング）の対応。
D3D12_FEATURE_DATA_D3D12_OPTIONS5 options5 = {};
device->CheckFeatureSupport(D3D12_FEATURE_D3D12_OPTIONS5, &options5, sizeof(options5));
bool dxr = options5.RaytracingTier >= D3D12_RAYTRACING_TIER_1_0;

// シェーダー モデルの、最大の対応。
D3D12_FEATURE_DATA_SHADER_MODEL shader_model = {D3D_SHADER_MODEL_6_6};
device->CheckFeatureSupport(D3D12_FEATURE_SHADER_MODEL, &shader_model, sizeof(shader_model));
// shader_model.HighestShaderModel に、対応する最大の SM が入る。

// リソース バインディングの段階（バインドレスに影響する）。
D3D12_FEATURE_DATA_D3D12_OPTIONS options = {};
device->CheckFeatureSupport(D3D12_FEATURE_D3D12_OPTIONS, &options, sizeof(options));
// options.ResourceBindingTier（1・2・3）
```

構造体を `= {}` でゼロ初期化しているのは、わざとです。聞いた機能を Windows やドライバーが知らないと呼び出しは失敗しますが、そのとき構造体はゼロのままなので、`NOT_SUPPORTED`（対応していない）と同じ意味になり特別な処理が要りません。

調べたい機能ごとに確認する構造体とフィールドが違います。5 つを 1 つずつ見ます。

#### DXR（レイトレーシング）

確認するのは `OPTIONS5.RaytracingTier` です。`NOT_SUPPORTED` なら DXR は使えません。`TIER_1_0` なら光線を飛ばすシェーダー（`DispatchRays`）が使えます。`TIER_1_1` はそれに加えてピクセル シェーダーやコンピュート シェーダーの中から光線を飛ばす `RayQuery`（インライン レイトレーシング）と、`ExecuteIndirect` での `DispatchRays` が使えます。影だけを DXR で出すのような使い方をするなら `RayQuery` が使える 1.1 のほうが組み込みやすいです。

DXR のシェーダーを使うにはシェーダー モデル 6.3 以上、`RayQuery` には 6.5 以上が必要なので、シェーダー モデルの確認とあわせて見ます。

#### メッシュ シェーダー

確認するのは `OPTIONS7.MeshShaderTier` です。`TIER_1` なら頂点シェーダーの代わりにメッシュ シェーダー（とその前段の増幅シェーダー）を使えます。メッシュ シェーダーはシェーダー モデル 6.5 以上が必要です。

メッシュ シェーダーを使うパイプラインは、通常の `CreateGraphicsPipelineState` では作れません。パイプライン ステート ストリーム（`ID3D12Device2::CreatePipelineState`）で作ります。そのため、`Device2` 以降が取れるかどうかも同時に確認します。

#### シェーダー モデル

`D3D12_FEATURE_SHADER_MODEL` はほかの機能と違って構造体に最初から値を入れて聞きます。上のコードでは `D3D_SHADER_MODEL_6_6` を入れて「6.6 まで使えるか」と聞いています。答えは同じフィールド `HighestShaderModel` に「GPU とドライバーが対応する最大の値」として戻ってきます。

聞いた値を動いている Windows 側が知らないと呼び出し自体が失敗します。新しいシェーダー モデルを使うゲームでは、高い値から順に聞いて成功した最初の値を採用します。

シェーダー モデルが高いほどシェーダーで使える機能が増えます。6.3 で DXR、6.5 でメッシュ シェーダーと `RayQuery`、6.6 で次のバインドレスに使う `ResourceDescriptorHeap` が加わります。

#### リソース バインディング（バインドレス）

確認するのは `OPTIONS.ResourceBindingTier` で `1`、`2`、`3` のどれかが返ります。これはシェーダーに渡すテクスチャやバッファの扱いにどこまで自由があるかを示します。

Tier 1 は 1 回の描画で使えるテクスチャの数などに小さな上限があります。Tier 2 はその上限が大きくなりサイズを決めない配列（unbounded array）が使えるようになります。Tier 3 は上限が実質なくなりさらにディスクリプタ ヒープの中にまだ何も書いていない空きがあってもよくなります。

この「空きがあってもよい」がバインドレスに必須の条件です。バインドレスはテクスチャを 1 枚ずつ束ねる代わりに全テクスチャのディスクリプタを 1 つの巨大なヒープに入れ、シェーダーが番号で選ぶ方式だからです。したがってバインドレスを前提にするゲームは、Tier 3 が使えるかどうかを最初に確認します。

#### 拡張バリア（Enhanced Barriers） {#enhanced-barriers}

確認するのは `OPTIONS12.EnhancedBarriersSupported` です。`TRUE` なら従来の `ResourceBarrier` の代わりに新しいバリア API（`ID3D12GraphicsCommandList7::Barrier`）が使えます。従来のバリアが「状態（`D3D12_RESOURCE_STATES`）」で表したのに対して、拡張バリアは「同期の範囲・アクセスの種類・レイアウト」を分けて指定でき必要以上に待たせずに済みます。使うには `ID3D12Device10` と Agility SDK の対応する版が必要です。

### QueryInterface（As） {#queryinterface-as}

```cpp
HRESULT IUnknown::QueryInterface(REFIID riid, void** ppvObject);
```

同じオブジェクトを別のインターフェースの窓口から取り出します。`ComPtr` では `As` という名前で包まれています。

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `riid` | `REFIID` | 取り出したいインターフェースの ID |
| `ppvObject` | `void**` | 結果を受け取るポインタのアドレス |

`ComPtr::As(&device5)` なら引数は受け取る `ComPtr` のアドレス 1 つだけで、ID は型から自動で決まります。戻り値は `HRESULT` で成功なら `S_OK` です。そのインターフェースを持っていなければ `E_NOINTERFACE` で失敗します。失敗したときは新しい機能が使えないだけなので、古いインターフェースで続けるかその機能を切ります。

D3D12 は機能を足すたびに `ID3D12Device1`、`…Device5`、`…Device10` のように番号つきのインターフェースを増やしてきました。古いインターフェースにメソッドを足すとすでに出荷されたゲームやドライバーが壊れるので、足すときは必ず新しい番号にします。実体は同じデバイスで窓口だけが番号ごとにあります。

<svg class="fig flow" viewBox="0 0 720 248" role="img" aria-label="同じデバイスを、番号つきのインターフェースで取り出す"><defs><marker id="fdC" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">番号つきインターフェース</text><rect x="16" y="74" width="150" height="50" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="91.0" y="99.0" text-anchor="middle" dominant-baseline="central" style="font-size:13px;font-weight:600">device</text><text x="91" y="146" text-anchor="middle" style="font-size:11px;font-weight:400">ComPtr&lt;ID3D12Device&gt;</text><rect x="270" y="38" width="434" height="190" rx="14" fill="rgba(148,163,184,0.18)" stroke="#94a3b8" stroke-width="2"/><text x="487" y="60" text-anchor="middle" style="font-size:12px;font-weight:600">1 つのデバイス（実体は 1 つ。窓口が番号ごとにある）</text><rect x="290" y="84" width="124" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="352.0" y="104.0" text-anchor="middle" dominant-baseline="central" style="font-size:11px;font-weight:600">ID3D12Device</text><rect x="428" y="84" width="124" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="490.0" y="104.0" text-anchor="middle" dominant-baseline="central" style="font-size:11px;font-weight:600">ID3D12Device1</text><rect x="566" y="84" width="124" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="628.0" y="104.0" text-anchor="middle" dominant-baseline="central" style="font-size:11px;font-weight:600">ID3D12Device2</text><rect x="290" y="148" width="124" height="40" rx="9" fill="rgba(229,170,40,0.28)" stroke="#e5aa28" stroke-width="2"/><text x="352.0" y="168.0" text-anchor="middle" dominant-baseline="central" style="font-size:11px;font-weight:600">ID3D12Device5</text><rect x="428" y="148" width="124" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="490.0" y="168.0" text-anchor="middle" dominant-baseline="central" style="font-size:11px;font-weight:600">ID3D12Device8</text><rect x="566" y="148" width="124" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="628.0" y="168.0" text-anchor="middle" dominant-baseline="central" style="font-size:11px;font-weight:600">ID3D12Device10</text><line x1="166" y1="99" x2="266" y2="99" stroke="currentColor" stroke-width="2" marker-end="url(#fdC)"/><text x="216" y="90" text-anchor="middle" style="font-size:12px;font-weight:600">As</text><text x="487" y="214" text-anchor="middle" style="font-size:12px;font-weight:400">device.As(&amp;device5) で、同じデバイスの Device5 の窓口を取り出す</text></svg>

```cpp
ComPtr<ID3D12Device5> device5;
if (SUCCEEDED(device.As(&device5))) {
  // DXR のステート オブジェクト（CreateStateObject）や、
  // 加速構造のサイズ見積もり（GetRaytracingAccelerationStructurePrebuildInfo）が使える
}
```

`As` が成功することと前の節で調べた GPU の対応は別の話で、両方が揃って初めて機能が使えます。番号ごとに何が増えたかを見ます。

#### ID3D12Device1

パイプライン ライブラリ（`CreatePipelineLibrary`）が増えました。作った PSO をファイルに保存して、次の起動で読み戻すための仕組みで、シェーダーのコンパイルを毎回やり直さずに済みます。ほかに複数のフェンスの完了をまとめて待つ `SetEventOnMultipleFenceCompletion` もあります。

#### ID3D12Device2

`CreatePipelineState` が増えました。従来の PSO は 1 つの巨大な構造体（`D3D12_GRAPHICS_PIPELINE_STATE_DESC`）に全部を書く形でしたがこれは、必要な項目だけを「ストリーム」として並べて渡せます。メッシュ シェーダーのパイプラインは、この形でしか作れません。

#### ID3D12Device5

DXR のための機能が入りました。レイトレーシング用のパイプラインを表すステート オブジェクト（`CreateStateObject`）と加速構造に必要なメモリの大きさを事前に調べる `GetRaytracingAccelerationStructurePrebuildInfo` が代表です。DXR を使うゲームはほぼここから入ります。

#### ID3D12Device8

リソースの作成まわりが拡張されました。`CreateCommittedResource2` と `CreatePlacedResource1` は新しい記述子 `D3D12_RESOURCE_DESC1` を受け取りサンプラー フィードバックのようなテクスチャの機能を扱えます。`GetResourceAllocationInfo2` は複数のリソースを 1 つのヒープに並べるとき全体でいくら要るかを調べます。

#### ID3D12Device10

拡張バリアに対応したリソース作成です。`CreateCommittedResource3` は作る時点のレイアウト（状態の代わりに使う拡張バリア側の考え方）を指定できます。拡張バリアを使うならこちらで作ったリソースが前提です。

コマンド リストにも同じ番号つきの系列があります（`ID3D12GraphicsCommandList4`、`…6`、`…7`）。DXR のコマンドは `List4`、メッシュ シェーダーの描画は `List6`、拡張バリアの `Barrier` は `List7` にあります。

### SetName {#setname}

```cpp
HRESULT ID3D12Object::SetName(LPCWSTR Name);
```

デバイスやリソースなど D3D12 のオブジェクトに名前を付けます。

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `Name` | `LPCWSTR` | 名前。ワイド文字列（`L"..."`）で渡す |

戻り値は `HRESULT` で成功は `S_OK` です。ゲームの動きは変わりません。

```cpp
device->SetName(L"Main Device");
resource->SetName(L"GBuffer Albedo");  // PIX やデバッグ レイヤーに名前が出る
```

名前は PIX（GPU のデバッガー）の画面とデバッグ レイヤーのメッセージに出ます。名前がないとメッセージが「ID3D12Resource 0x000001F4A3...」のようなアドレスだけになります。全オブジェクトに付けておくとデバッグがはるかに楽になります。

## 後始末

D3D12 は終了前に <strong>GPU がすべての仕事を終えるのを待つ</strong>必要があります。GPU がまだ使っているリソースを解放するとクラッシュします。

```cpp
WaitForGpu();  // フェンスで GPU の完了を待つ（fence.md）
// そのあとで ComPtr を解放する（リソース → デバイスの順）
```

## よくあるミス

??? failure "デバッグ レイヤーを有効にしたのにメッセージが出ない"
    `EnableDebugLayer` をデバイスを作ったあとに呼んでいます。デバイスを作る前に呼びます。

??? failure "`D3D12CreateDevice` が失敗する"
    GPU が D3D12 に対応していないか「グラフィックス ツール」が入っていないのにデバッグ レイヤーを要求しています。WARP アダプターで再試行します。

??? failure "ノート PC で内蔵 GPU が選ばれて遅い"
    アダプターを `nullptr`（既定）に任せています。`EnumAdapterByGpuPreference(HIGH_PERFORMANCE)` で選びます。

??? failure "終了時にクラッシュする（GPU がリソースを使用中）"
    GPU の完了を待たずにリソースを解放しています。終了前にフェンスで待ちます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] デバイス ＝ 作る窓口。D3D12 に即時コンテキストは無い
    - [x] デバッグ レイヤーは、デバイスを作る「前」に有効にする
    - [x] ファクトリー → アダプター（高性能 GPU）→ `D3D12CreateDevice`
    - [x] 機能は `CheckFeatureSupport` で、確認してから使う
    - [x] 新しい機能は番号つきのインターフェース（`Device5` など）
    - [x] 終了前に GPU の完了を待つ

## 関連ページ

- [DirectX 12 Guide](index.md)
- [Command Queue](command-queue.md)
- [Debug Layer](debug-layer.md)
- [Microsoft Learn: D3D12CreateDevice](https://learn.microsoft.com/ja-jp/windows/win32/api/d3d12/nf-d3d12-d3d12createdevice)
