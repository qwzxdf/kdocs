---
title: ComPtr
tags:
  - DirectX
api:
  - ComPtr
---

# ComPtr

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
`#include <wrl/client.h>`
</div>

DirectX のオブジェクト（デバイス、リソース、スワップ チェーンなど）は COM という仕組みで作られていて、`delete` ではなく `Release()` で手放します。作るたびに `Release()` を書くと、途中で `return` した枝や例外で書き忘れて、メモリがリークします。かといって手放し忘れを恐れて早く手放すと、まだ GPU や他の場所が使っている物を壊します。

そこで `std::unique_ptr` のように、スコープを抜けたら自動で `Release()` を呼ぶスマート ポインタを使います。それが `Microsoft::WRL::ComPtr<T>` です。COM の参照カウントを自分で数える代わりに `ComPtr` に任せます。メンバーはどれも小さいのですが、`Get` と `GetAddressOf` と `&` の使い分け、`Reset` の意味などを取り違えると、リークや二重解放になります。このページでは 1 つずつ見ます。

!!! tip "ポイント"
    - 持ち主は `ComPtr` 1 つにして、関数の引数に渡すときは `Get()` で生ポインタを渡す。
    - 新しく作るオブジェクトの受け取りは `IID_PPV_ARGS(&p)`。`&p` は古い中身を先に手放す。
    - `p.Reset()`（ComPtr のメソッド）と `p->Reset()`（オブジェクトのメソッド）は別物。1 文字の違いで意味が変わる。
    - 別のインターフェースが欲しいときは `As`。
    - `ComPtr` は参照カウントを数えるだけ。GPU がまだ使っているかどうかは知らない（待つのは自分）。

!!! info "このページを読む前に"
    所有権とスマート ポインタの考え方は [所有権](../../basics/ownership.md) にあります。COM のオブジェクトは `delete` できず、`Release()` で参照カウントを 1 減らして、0 になったら自分で消える、という点だけ押さえてください。

## 使う準備

```cpp
#include <wrl/client.h>

using Microsoft::WRL::ComPtr;

ComPtr<ID3D12Device> device;       // 最初は nullptr
// ... 作る ...
device->CreateFence(...);          // ふつうのポインタのように使う
// スコープを抜けると、デストラクターが Release() を呼ぶ
```

`ComPtr<T>` は `T*` を 1 つ持つクラスです。コピーすると参照カウントが 1 増え（`AddRef`）、デストラクターで 1 減ります（`Release`）。ムーブすると増減なしで持ち主だけが移ります。`ComPtr` は `std::unique_ptr` と違ってコピーできるので、`std::vector<ComPtr<...>>` や配列にそのまま入れられます。

## メソッド一覧

| メソッド | 役割 |
| --- | --- |
| [`operator->`](#operator-arrow) | 中のオブジェクトのメソッドを呼ぶ |
| [`Get`](#get) | 生ポインタを借りる（参照カウントは増えない） |
| [`GetAddressOf`](#getaddressof) | 中のポインタのアドレスを返す |
| [`ReleaseAndGetAddressOf`](#releaseandgetaddressof) | 先に手放してから、アドレスを返す（`&p` と同じ） |
| [`Reset`](#reset) | 手放して空にする |
| [`As`](#as) | 別のインターフェースを取り出す |
| [`Detach`](#detach) | 手放さずに、持ち主をやめる |
| [`Attach`](#attach) | 生ポインタの持ち主になる |
| [`IID_PPV_ARGS`](#iid_ppv_args) | 型と受け取り先をまとめて書くマクロ |

## メソッドの詳しい説明

### operator-> {#operator-arrow data-toc-label="operator->"}

```cpp
T* ComPtr<T>::operator->() const;
```

中のポインタを返します。`device->CreateFence(...)` のように、ふつうのポインタと同じ書き方でメソッドを呼べます。

中身が `nullptr` のときに呼ぶと、ふつうのポインタと同じくクラッシュします。`ComPtr` が空かどうかは `if (device)`、または `device.Get() != nullptr` で確かめられます。作成に失敗した（`HRESULT` が `FAILED`）あとのポインタは空のままなので、戻り値を確認せずに続けるとここで落ちます。

### Get {#get}

```cpp
T* ComPtr<T>::Get() const;
```

中の生ポインタを返します。参照カウントは増えません。

D3D12 の関数は `ID3D12Resource*` のような生ポインタを引数に取るので、`ComPtr` から渡すときに使います。

```cpp
command_list->SetPipelineState(pso.Get());
command_list->ResourceBarrier(1, &barrier);  // barrier の中の pResource にも back_buffer.Get() を入れる
```

返ってきた生ポインタを `ComPtr` と別に持ち続けてはいけません。持ち主の `ComPtr` が `Reset` されたりスコープを抜けたりすると、そのポインタは無効になります。関数に渡して呼び出しの間だけ使うのが原則です。

「`ExecuteCommandLists` に渡すリストの配列」のように、`ID3D12CommandList*` の配列を作る場面でも `Get()` を使います。`ComPtr` の配列のまま渡すことはできません。

### GetAddressOf {#getaddressof}

```cpp
T* const* ComPtr<T>::GetAddressOf() const;
```

中のポインタを入れている場所のアドレスを返します。「作った物を受け取る」関数（`void**` や `ID3D12Resource**` を引数に取るもの）に渡す口です。

```cpp
ComPtr<ID3DBlob> error;
D3DCompileFromFile(path, nullptr, nullptr, "main", "vs_5_0", 0, 0, &code, error.GetAddressOf());
```

`GetAddressOf` は、いま入っている物を手放しません。すでに何かが入った `ComPtr` に対して呼んで、受け取り関数が新しい物を書き込むと、古い物の参照が `Release` されないまま上書きされます。これがリークの原因です。空の `ComPtr` に 1 回だけ使うなら安全です。ループで同じ変数に何度も受け取るときは、次の `ReleaseAndGetAddressOf`（または `&`）を使います。

### ReleaseAndGetAddressOf {#releaseandgetaddressof}

```cpp
T** ComPtr<T>::ReleaseAndGetAddressOf();
```

先に中の物を手放して（`Release`）から、空になったポインタのアドレスを返します。

```cpp
ComPtr<IDXGIAdapter1> adapter;
for (UINT i = 0; factory->EnumAdapterByGpuPreference(i, pref, IID_PPV_ARGS(&adapter)) != DXGI_ERROR_NOT_FOUND; ++i) {
  // adapter には毎回、新しいアダプターが入る。古いほうは自動で Release されている
}
```

`IID_PPV_ARGS(&adapter)` の `&adapter` は、`ComPtr` では `ReleaseAndGetAddressOf` と同じ働きをします。「ループの中で同じ `ComPtr` に何度も受け取る」場面で安全なのはこのためです。ふだんはこちらで足りるので、`GetAddressOf` を使うのは「`IID_PPV_ARGS` が使えない関数（型を指定した `ID3DBlob**` を受ける `D3DCompileFromFile` など）」に絞ります。

### Reset {#reset}

```cpp
unsigned long ComPtr<T>::Reset();
```

中の物を手放して（`Release`）`nullptr` にします。戻り値は、手放したあとの参照カウントです。

```cpp
for (auto& buffer : back_buffers) buffer.Reset();     // バック バッファの参照を全部手放す
swap_chain->ResizeBuffers(...);                       // 参照が残っていると失敗する
```

スワップ チェーンのバック バッファを作り直す前のように、「この参照をいま手放したい」ときに使います。スコープを抜けるのを待たなくてよくなります。

!!! warning "`.Reset()` と `->Reset()` は別物"
    `ID3D12CommandAllocator` と `ID3D12GraphicsCommandList` には、`Reset` というメソッドがあります。アロケーターのメモリを巻き戻したりリストを記録し直したりするメソッドです。
    ```cpp
    allocator->Reset();    // アロケーターのメモリを巻き戻す（オブジェクトは残る）
    allocator.Reset();     // ComPtr が手放す（アロケーターが消える。ほかに持ち主がいなければ破棄される）
    ```
    ドット（`.`）は `ComPtr` 自身のメソッド、矢印（`->`）は中のオブジェクトのメソッドです。毎フレームの先頭で巻き戻したいのに `.` と書くと、アロケーターが消えて次の `->` で `nullptr` を参照してクラッシュします。コンパイルは通ってしまうので、見た目で気づく癖をつけます。

### As {#as}

```cpp
template <typename U>
HRESULT ComPtr<T>::As(ComPtr<U>* p) const;
```

同じオブジェクトを別のインターフェースの形で取り出します（COM の `QueryInterface` を包んだものです）。

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `p` | `ComPtr<U>*` | 受け取る `ComPtr` のアドレス |

`U` の型から取り出すインターフェースの ID が決まるので、`riid` を書かずに済みます。戻り値は `HRESULT` で、成功なら `S_OK` です。そのオブジェクトが `U` を持っていなければ `E_NOINTERFACE` で失敗し、`p` は空のままです。

```cpp
ComPtr<IDXGISwapChain1> swap_chain1;
// ... CreateSwapChainForHwnd で作る ...
ComPtr<IDXGISwapChain3> swap_chain;
if (FAILED(swap_chain1.As(&swap_chain))) {
  // この OS では IDXGISwapChain3 を取り出せない
}
```

取り出した `swap_chain` と元の `swap_chain1` は、同じ実体を指します。参照カウントが 1 増えるので、どちらを先に手放しても実体は消えません。番号つきのインターフェース（`ID3D12Device5` や `IDXGISwapChain3` など）を取り出す場面で使います。

### Detach {#detach}

```cpp
T* ComPtr<T>::Detach();
```

中のポインタを返し、`ComPtr` を空にします。`Release` は呼びません。参照カウントは減らないので、受け取ったポインタの持ち主は、これを呼んだ側になります。

COM の外に所有権を渡すとき（C のコードに渡して向こうで `Release` してもらう場合など）に使います。受け取った側が `Release` しないと、そのままリークです。ふだんのゲームのコードで使うことはほとんどありません。

### Attach {#attach}

```cpp
void ComPtr<T>::Attach(T* other);
```

すでに参照カウントを 1 持っている生ポインタ `other` の持ち主にこの `ComPtr` がなります。`AddRef` は呼びません。いま入っている物があれば、先に手放します。

「生ポインタを返す古い API から受け取る」ときに使います。`AddRef` 済みの物を受け取ったのに、`ComPtr` のコンストラクターやコピーで包むと、参照カウントが 1 多くなって解放されません。`Attach` なら 1 つ分だけを引き継げます。`Detach` の逆の操作です。

### IID_PPV_ARGS {#iid_ppv_args}

```cpp
#define IID_PPV_ARGS(ppType) __uuidof(**(ppType)), IID_PPV_ARGS_Helper(ppType)
```

D3D12 や DXGI で「作った物を受け取る」関数は、`REFIID riid` と `void** ppv` の 2 つの引数がペアになっています。たとえば `ID3D12Device::CreateFence(..., REFIID riid, void** ppFence)` です。`riid` に取り出したいインターフェースの ID を `ppv` に受け取り先のアドレスを渡します。

```cpp
ComPtr<ID3D12Fence> fence;
device->CreateFence(0, D3D12_FENCE_FLAG_NONE, IID_PPV_ARGS(&fence));
// 展開すると: ..., __uuidof(ID3D12Fence), reinterpret_cast<void**>(&fence)
```

この 2 つを手で書くと、型と ID が食い違ったときにコンパイルは通るのに実行時に落ちます。`IID_PPV_ARGS(&fence)` は `fence` の型から `riid` を求め、`ppv` と合わせて 2 つの引数に展開してくれます。型を 1 回しか書かないので食い違えません。`ComPtr` の `&` は前に入っていた物を手放すので（[`ReleaseAndGetAddressOf`](#releaseandgetaddressof)）、そのまま受け取り先に使えます。

引数に渡せるのは「インターフェースへのポインタ」のアドレスだけです。`ID3D12Fence*` 型の変数のアドレスや `ComPtr<ID3D12Fence>` のアドレスは渡せますが、`void*` 変数のアドレスはコンパイルが通りません。型から ID を求められないからです。

## 使い分けの早見

| やりたいこと | 書き方 |
| --- | --- |
| 作った物を受け取る | `IID_PPV_ARGS(&p)` |
| 生ポインタを引数に渡す | `p.Get()` |
| 型を指定した `T**` を受ける関数に渡す | `p.GetAddressOf()`（空の `p` のとき）、または `&p` |
| 参照を手放す | `p.Reset()` |
| 別のインターフェースが欲しい | `p.As(&q)` |
| 空かどうか確かめる | `if (p)` |

## よくあるミス

??? failure "毎フレーム `allocator.Reset()` と書いてクラッシュする"
    `.` は `ComPtr` を空にします。巻き戻したいのは矢印の `allocator->Reset()` です。

??? failure "ループで受け取るたびにメモリが増える"
    `GetAddressOf()` を使い回しています。すでに入っている物の参照を手放さずに上書きするためです。`&p`（`IID_PPV_ARGS(&p)`）か、先に `Reset()` を呼びます。

??? failure "`ResizeBuffers` が失敗する"
    バック バッファの `ComPtr` が残っています。すべて `Reset()` してから呼びます。

??? failure "終了時に GPU がクラッシュする"
    `ComPtr` は参照カウントを数えるだけで、GPU がまだ使っているかは知りません。デストラクターで `Release` されて消えても、命令が実行中だと落ちます。終了前にフェンスで GPU の完了を待ちます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] COM のオブジェクトは `ComPtr` で持つ。`Release()` は書かない
    - [x] 受け取りは `IID_PPV_ARGS(&p)`、引数に渡すときは `p.Get()`
    - [x] `p.Reset()`（ComPtr）と `p->Reset()`（オブジェクト）を取り違えない
    - [x] 別のインターフェースは `As`
    - [x] ループで何度も受け取るなら `GetAddressOf` ではなく `&p`

## 関連ページ

- [所有権](../../basics/ownership.md)
- [Microsoft Learn: ComPtr クラス](https://learn.microsoft.com/ja-jp/cpp/cppcx/wrl/comptr-class)
