---
title: ID3D12Object
tags:
  - DirectX
api:
  - ID3D12Object
  - ID3D12DeviceChild
---

# ID3D12Object

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
<span class="ver ver-11">D3D12</span>
`#include <d3d12.h>`
</div>

デバッグ レイヤーや PIX のメッセージに「ID3D12Resource 0x000001F4A3...」とアドレスだけが出ても、どのリソースのことか分かりません。そこで、オブジェクトに名前を付けておきます。名前を付ける `SetName` を持っているのが、`ID3D12Object` です。

デバイスから作る物（リソース、ヒープ、PSO、コマンド リスト、フェンスなど）はみな `ID3D12Object` を土台にしています。そのため `SetName` はどのオブジェクトにも使えます。土台にはもう 1 つ `ID3D12DeviceChild` があり、「このオブジェクトを作ったデバイス」を取り出す `GetDevice` を持っています。

!!! tip "ポイント"
    - `SetName` は全オブジェクトに付ける。デバッグ レイヤーと PIX の表示が読めるようになる。
    - 名前はワイド文字列（`L"..."`）。ゲームの動きは変わらない。
    - `SetPrivateData` で、オブジェクトに自分のデータを結びつけられる。
    - `GetDevice` は、作ったデバイスを取り出す。

!!! info "このページを読む前に"
    オブジェクトを作る流れは [Device and Factory](../factory-device.md)、デバッグ レイヤーのメッセージは [Debug Layer](../debug-layer.md) にあります。

## メソッド一覧

| メソッド | 役割 |
| --- | --- |
| [`SetName`](../factory-device.md#setname) | 名前を付ける |
| [`SetPrivateData`](#setprivatedata) | 任意のデータを結びつける |
| [`SetPrivateDataInterface`](#setprivatedatainterface) | COM のオブジェクトを結びつける |
| [`GetPrivateData`](#getprivatedata) | 結びつけたデータを取り出す |
| [`GetDevice`](#getdevice) | 作ったデバイスを取り出す |

`SetName` は [Device and Factory](../factory-device.md#setname) で説明しています。

## メソッドの詳しい説明

### SetPrivateData {#setprivatedata}

```cpp
HRESULT ID3D12Object::SetPrivateData(REFGUID guid, UINT DataSize, const void* pData);
```

オブジェクトに自分で決めた GUID を鍵にしてバイト列を結びつけます。ゲーム側の情報（リソースの種類、読み込んだファイル名など）をオブジェクトと一緒に持ち歩く用途です。

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `guid` | `REFGUID` | データの鍵。自分で作った GUID か、決まった GUID |
| `DataSize` | `UINT` | データのバイト数。`0` で、その鍵のデータを削除 |
| `pData` | `const void*` | データの先頭。内容はコピーされる |

データはコピーされるので、呼んだあとで元のメモリを解放して構いません。同じ `guid` で再び呼ぶと上書きされます。`DataSize` に 0 を渡し `pData` を `nullptr` にすると削除です。戻り値は成功なら `S_OK` です。

GUID のうち `WKPDID_D3DDebugObjectNameW`（`d3dcommon.h`）は、デバッグ ツールが名前として読む決まりの鍵です。`SetName` は、中でこれと同じ働きをします。

### SetPrivateDataInterface {#setprivatedatainterface}

```cpp
HRESULT ID3D12Object::SetPrivateDataInterface(REFGUID guid, const IUnknown* pData);
```

COM のオブジェクトを鍵に結びつけます。バイト列のコピーではなく、渡したオブジェクトの参照カウントが 1 増えて、結びつけた側のオブジェクトが消えるときに `Release` されます。`pData` が `nullptr` なら、その鍵の結びつけを外します。

結びつけた側のオブジェクトの寿命に別の COM オブジェクトの寿命を合わせたいときに使います。ふつうのゲームのコードでは出番は少なめです。

### GetPrivateData {#getprivatedata}

```cpp
HRESULT ID3D12Object::GetPrivateData(REFGUID guid, UINT* pDataSize, void* pData);
```

`SetPrivateData` で結びつけたデータを取り出します。

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `guid` | `REFGUID` | 鍵 |
| `pDataSize` | `UINT*` | 入力はバッファの大きさ、出力はデータの大きさ |
| `pData` | `void*` | 受け取るバッファ。`nullptr` なら大きさだけを調べる |

先に `pData` を `nullptr` にして呼ぶと、必要な大きさが `*pDataSize` に入ります。それでバッファを用意して、もう一度呼ぶのが定石です。バッファが小さいときや、その鍵のデータが無いときは失敗します。

### GetDevice {#getdevice}

```cpp
HRESULT ID3D12DeviceChild::GetDevice(REFIID riid, void** ppvDevice);
```

このオブジェクトを作ったデバイスを取り出します。

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `riid` | `REFIID` | 取り出したいインターフェースの ID。`ID3D12Device` など |
| `ppvDevice` | `void**` | 結果を受け取るポインタのアドレス |

```cpp
ComPtr<ID3D12Device> device;
resource->GetDevice(IID_PPV_ARGS(&device));
```

デバイスを引数で持ち回らなくても、リソースや PSO から辿れます。取り出すたびに参照カウントが 1 増えるので、`ComPtr` で受けます。戻り値は成功なら `S_OK` です。

## 関連ページ

- [Device and Factory](../factory-device.md)
- [Debug Layer](../debug-layer.md)
- [Microsoft Learn: ID3D12Object](https://learn.microsoft.com/ja-jp/windows/win32/api/d3d12/nn-d3d12-id3d12object)
