---
title: Constant Buffer Packing
tags:
  - DirectX
  - HLSL
---

# Constant Buffer Packing

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

シェーダーで `cbuffer` に `float3` を並べて、C++ の構造体にも同じ順で `XMFLOAT3` を並べたのに、2 つ目の値から先がずれる。色が変な場所から読まれる。バグを探してもコードは合っていて、見つからない。これは定数バッファの詰め方のきまりを知らないときに、だれでも一度はやる失敗です。

HLSL の `cbuffer` は、C++ の構造体のようには詰められません。16 バイトを 1 つの<strong>レジスタ</strong>として数え、変数をそのレジスタの中へ詰めていきます。変数は、レジスタの境界をまたげません。きまりはこれだけで、あとは型ごとの大きさが分かれば、どこに何が置かれるかを自分で計算できます。このページでは、そのきまりと、型ごとの大きさと、並べ替えて小さくする方法を説明します。

!!! tip "ポイント"
    - 定数バッファは 16 バイトの<strong>レジスタ</strong>の列。変数は、レジスタの境界（16 の倍数）をまたげない。またぎそうなら、次のレジスタの先頭へ送られる。
    - `float3` の直後の `float` は、同じレジスタに収まる。`float2` の直後の `float3` は、またぐので次のレジスタへ送られる。
    - 配列は、要素ごとにレジスタを 1 つ使う。`float c[3]` は 12 バイトではなく 36 バイトになる。
    - 行列と構造体は、新しいレジスタから始まる。`float3x3` は 36 バイトではなく 44 バイトになる。
    - 全体の大きさは、バッファを作るときに 16 の倍数へ切り上げる。
    - 自分の目で確かめるには、`dxc -Od -Fc` の出力の `Offset` を見る。K-HLSL を使うと、エディターで見られる。

!!! info "このページを読む前に"
    - [DirectX Concepts](index.md)（このセクションの地図。API に依存しない話だけを置いている）
    - [GPU Pipeline Overview](gpu-pipeline.md)（定数バッファは、シェーダーへ値を渡す入り口の 1 つ）

## 16 バイトのレジスタに詰める

GPU は、定数バッファを 16 バイトずつ（`float4` 1 つぶん）読みます。1 つのレジスタの中は、前から順に x・y・z・w の 4 つの 4 バイトの枠です。変数は、この枠に前から詰めていきます。詰められるのは、同じレジスタの中に全部収まるときだけです。収まらないとき、変数は次のレジスタの先頭から置かれ、手前の余りは使われません。

次の `cbuffer` で考えます。

```hlsl
cbuffer PerObject : register(b1)
{
    float4x4 world;      // 0〜63（レジスタ c0〜c3）
    float3 tint;         // 64〜75
    float alpha;         // 76〜79（tint の直後の float は、同じレジスタに入る）
    float2 uvScale;      // 80〜87
    float3 lightDir;     // 88 に置くと 100 までで、96 をまたぐ。次のレジスタの 96 から
    float intensity;     // 108〜111
    float shine;         // 112〜115
};
```

`tint`（12 バイト）と `alpha`（4 バイト）は、ぴったり 16 バイトで 1 つのレジスタに収まります。`uvScale`（8 バイト）のあとには 8 バイトの余りがありますが、`lightDir` は 12 バイトなので入りません。`lightDir` は次のレジスタの先頭の 96 へ送られ、88〜95 の 8 バイトが使われずに残ります。

<svg class="fig flow" viewBox="0 0 662 394" role="img" aria-label="float3 lightDir が、行の境界をまたげないので次の行へ送られ、前に 8 バイトの隙間ができる"><text x="14" y="22" class="fig-title">PerObject のレイアウト（116 バイト、確保は 128 バイト）</text><text x="142" y="46" text-anchor="middle" style="font-size:11px;font-weight:400">+0</text><text x="286" y="46" text-anchor="middle" style="font-size:11px;font-weight:400">+4</text><text x="430" y="46" text-anchor="middle" style="font-size:11px;font-weight:400">+8</text><text x="574" y="46" text-anchor="middle" style="font-size:11px;font-weight:400">+12</text><text x="60" y="68" text-anchor="end" dominant-baseline="central" style="font-size:12px;font-weight:600">c0</text><rect x="70" y="52" width="576" height="30" fill="none" stroke="#94a3b8" stroke-width="1" stroke-dasharray="3 3"/><text x="60" y="102" text-anchor="end" dominant-baseline="central" style="font-size:12px;font-weight:600">c1</text><rect x="70" y="86" width="576" height="30" fill="none" stroke="#94a3b8" stroke-width="1" stroke-dasharray="3 3"/><text x="60" y="136" text-anchor="end" dominant-baseline="central" style="font-size:12px;font-weight:600">c2</text><rect x="70" y="120" width="576" height="30" fill="none" stroke="#94a3b8" stroke-width="1" stroke-dasharray="3 3"/><text x="60" y="170" text-anchor="end" dominant-baseline="central" style="font-size:12px;font-weight:600">c3</text><rect x="70" y="154" width="576" height="30" fill="none" stroke="#94a3b8" stroke-width="1" stroke-dasharray="3 3"/><text x="60" y="204" text-anchor="end" dominant-baseline="central" style="font-size:12px;font-weight:600">c4</text><rect x="70" y="188" width="576" height="30" fill="none" stroke="#94a3b8" stroke-width="1" stroke-dasharray="3 3"/><text x="60" y="238" text-anchor="end" dominant-baseline="central" style="font-size:12px;font-weight:600">c5</text><rect x="70" y="222" width="576" height="30" fill="none" stroke="#94a3b8" stroke-width="1" stroke-dasharray="3 3"/><text x="60" y="272" text-anchor="end" dominant-baseline="central" style="font-size:12px;font-weight:600">c6</text><rect x="70" y="256" width="576" height="30" fill="none" stroke="#94a3b8" stroke-width="1" stroke-dasharray="3 3"/><text x="60" y="306" text-anchor="end" dominant-baseline="central" style="font-size:12px;font-weight:600">c7</text><rect x="70" y="290" width="576" height="30" fill="none" stroke="#94a3b8" stroke-width="1" stroke-dasharray="3 3"/><rect x="71" y="52" width="574" height="30" rx="5" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="358.0" y="67.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">float4x4 world</text><rect x="71" y="86" width="574" height="30" rx="5" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="358.0" y="101.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">(続き)</text><rect x="71" y="120" width="574" height="30" rx="5" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="358.0" y="135.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">(続き)</text><rect x="71" y="154" width="574" height="30" rx="5" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="358.0" y="169.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">(続き)</text><rect x="71" y="188" width="430" height="30" rx="5" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="286.0" y="203.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">tint</text><rect x="503" y="188" width="142" height="30" rx="5" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="574.0" y="203.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">alpha</text><rect x="71" y="222" width="286" height="30" rx="5" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="214.0" y="237.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">uvScale</text><rect x="359" y="222" width="286" height="30" rx="5" fill="rgba(148,163,184,0.18)" stroke="#94a3b8" stroke-width="2" stroke-dasharray="4 3"/><text x="502.0" y="237.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:400">隙間 8</text><rect x="71" y="256" width="430" height="30" rx="5" fill="rgba(229,170,40,0.28)" stroke="#e5aa28" stroke-width="2"/><text x="286.0" y="271.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">lightDir</text><rect x="503" y="256" width="142" height="30" rx="5" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="574.0" y="271.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">inten</text><rect x="71" y="290" width="142" height="30" rx="5" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="142.0" y="305.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">shine</text><rect x="215" y="290" width="430" height="30" rx="5" fill="rgba(148,163,184,0.18)" stroke="#94a3b8" stroke-width="2" stroke-dasharray="4 3"/><text x="430.0" y="305.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:400">隙間 12</text><text x="14" y="344" style="font-size:12px;font-weight:400">lightDir（12 バイト）は、88〜100 で 96 の境界をまたぐので、96 から始まる。</text><text x="14" y="362" style="font-size:12px;font-weight:400">手前の 88〜96 は使われずに残る。末尾の 116〜128 は、確保の大きさを 16 の倍数にするための余り。</text></svg>

C++ 側の構造体で `XMFLOAT2 uvScale` の次に `XMFLOAT3 lightDir` を並べると、`lightDir` は 88 に置かれます。HLSL は 96 から読むので、8 バイトずれます。ずれた先では、`lightDir` の x に `lightDir.y` の値が入り、以降のメンバーも全部ずれます。

全体の大きさは 116 バイトですが、定数バッファの大きさは 16 の倍数にそろえるので、128 バイトで作ります。

## 型ごとの大きさ

スカラーは、`bool`・`int`・`uint`・`float` が 4 バイトです。ベクトルは成分の数を掛けた大きさで、`float3` なら 12 バイトです。大きさが 16 バイト以下の変数は、同じレジスタに収まるときだけ、その場所に置かれます。型の種類ごとの特徴を、順に見ます。

### bool

HLSL の `bool` は 4 バイトです。C++ の `bool` は 1 バイトなので、C++ 側では `uint32_t`（または `int32_t`）で受けます。`bool` を C++ の `bool` のまま並べると、後ろがすべてずれます。

### half と min16float

既定では、`half` も 4 バイトの `float` として扱われます。DXC に `-enable-16bit-types` を付けると、`half` は本当の 2 バイトになり、2 バイト単位で詰められます。`half3` は 6 バイトで、`half4` は 8 バイトです。この場合も、変数がレジスタの境界をまたげないきまりは変わりません。

`min16float` などの<strong>最小精度の型</strong>は、`-enable-16bit-types` を付けないとき、専用のレジスタに入ります。直前が普通の型なら、新しいレジスタから始まります。続けて並べた最小精度の型どうしは、4 バイト単位で詰められます。最小精度の型のあとに普通の型が来ると、また新しいレジスタから始まります。この挙動は、DXC の出力で確かめた結果で、ほかの配置のきまりとは別物です。最小精度の型は、定数バッファでは避けるのが無難です。

### double

`double` は 8 バイトで、置く位置も 8 の倍数にそろえられます。`double2` は 16 バイトで、1 レジスタを使い切ります。`double3` と `double4` は 16 バイトを超えるので、レジスタの先頭から始まり、複数のレジスタにまたがります。

### 行列

行列は、新しいレジスタから始まります。HLSL の既定は<strong>列優先</strong>で、列を 1 つずつ別のレジスタに入れます。`float3x3` は、3 列それぞれが 1 レジスタを使い、最後の列だけ 12 バイトなので、16 × 2 + 12 の 44 バイトです。9 つの `float` を並べた 36 バイトにはなりません。次の変数は、最後の列の余りに入れます。

`float4x4` は 64 バイトで、レジスタ 4 つをちょうど使います。`float2x4` は、列優先だと 4 列で各列が 8 バイト（レジスタ 1 つ）なので、16 × 3 + 8 の 56 バイトになります。

`row_major` を付けると、行ごとにレジスタを使います。`row_major float2x3` は、2 行それぞれが 1 レジスタで、16 + 12 の 28 バイトです。`#pragma pack_matrix(row_major)` や DXC の `-Zpr` で、全体の既定を行優先に変えることもできます。変えた場合は、列優先のつもりで計算した大きさとずれます。

### 配列

配列は、レジスタの先頭から始まり、要素ごとにレジスタを 1 つ以上使います。要素の間隔は 16 バイトの倍数です。全体の大きさは、最後の要素だけ切り上げません。`float c[3]` なら、先頭の 2 要素が 16 バイトずつで、最後の要素が 4 バイトなので、16 × 2 + 4 の 36 バイトです。

<svg class="fig flow" viewBox="0 0 662 224" role="img" aria-label="配列は要素ごとに 16 バイトの行を使う。最後の要素の後ろの余りには、次の変数が入れる"><text x="14" y="22" class="fig-title">float c[3]; float d; のレイアウト</text><text x="142" y="46" text-anchor="middle" style="font-size:11px;font-weight:400">+0</text><text x="286" y="46" text-anchor="middle" style="font-size:11px;font-weight:400">+4</text><text x="430" y="46" text-anchor="middle" style="font-size:11px;font-weight:400">+8</text><text x="574" y="46" text-anchor="middle" style="font-size:11px;font-weight:400">+12</text><text x="60" y="68" text-anchor="end" dominant-baseline="central" style="font-size:12px;font-weight:600">c0</text><rect x="70" y="52" width="576" height="30" fill="none" stroke="#94a3b8" stroke-width="1" stroke-dasharray="3 3"/><text x="60" y="102" text-anchor="end" dominant-baseline="central" style="font-size:12px;font-weight:600">c1</text><rect x="70" y="86" width="576" height="30" fill="none" stroke="#94a3b8" stroke-width="1" stroke-dasharray="3 3"/><text x="60" y="136" text-anchor="end" dominant-baseline="central" style="font-size:12px;font-weight:600">c2</text><rect x="70" y="120" width="576" height="30" fill="none" stroke="#94a3b8" stroke-width="1" stroke-dasharray="3 3"/><rect x="71" y="52" width="142" height="30" rx="5" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="142.0" y="67.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">c[0]</text><rect x="215" y="52" width="430" height="30" rx="5" fill="rgba(148,163,184,0.18)" stroke="#94a3b8" stroke-width="2" stroke-dasharray="4 3"/><text x="430.0" y="67.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:400">隙間 12</text><rect x="71" y="86" width="142" height="30" rx="5" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="142.0" y="101.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">c[1]</text><rect x="215" y="86" width="430" height="30" rx="5" fill="rgba(148,163,184,0.18)" stroke="#94a3b8" stroke-width="2" stroke-dasharray="4 3"/><text x="430.0" y="101.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:400">隙間 12</text><rect x="71" y="120" width="142" height="30" rx="5" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="142.0" y="135.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">c[2]</text><rect x="215" y="120" width="142" height="30" rx="5" fill="rgba(229,170,40,0.28)" stroke="#e5aa28" stroke-width="2"/><text x="286.0" y="135.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">d</text><rect x="359" y="120" width="286" height="30" rx="5" fill="rgba(148,163,184,0.18)" stroke="#94a3b8" stroke-width="2" stroke-dasharray="4 3"/><text x="502.0" y="135.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:400"></text><text x="14" y="174" style="font-size:12px;font-weight:400">配列 float c[3] は、要素ごとに 1 行（16 バイト）を使う。大きさは 16 × 2 + 4 = 36 バイトで、</text><text x="14" y="192" style="font-size:12px;font-weight:400">最後の要素のあとの余りには、次の変数 d が入る。</text></svg>

つまり `float weights[8]` は 32 バイトではなく 116 バイトになり、`float4 weights[8]` で受けて `.x` を使う書き方と、使うレジスタの数が同じです。大きさをむだにしたくないときは、`float4` の配列に 4 つずつ詰めて、シェーダー側で `weights[i / 4][i % 4]` のように取り出します。

最後の要素の余りには、次の変数が入ります。図の `d` がそうです。この余りを知らないと、C++ 側で配列の直後に 12 バイトのパディングを入れてしまい、ずれの原因になります。

### 構造体

構造体は、新しいレジスタから始まります。中のメンバーには、ここまでと同じ規則が働きます。構造体の配列は、要素ごとに 16 バイトの倍数へ切り上げた間隔で並びます。

構造体の最後のレジスタに余りがあれば、次の変数はそこへ入ります。たとえば `float3` と `float` と `float` を持つ 20 バイトの構造体の直後に `float` を置くと、その `float` は 20 に置かれ、次のレジスタへ送られません。C++ の構造体のように、構造体の大きさを 16 の倍数へ切り上げて次を置く、という動きにはなりません。

### packoffset

`: packoffset(c1.y)` を付けると、変数の置き場所を自分で決められます。`c1` はレジスタの番号で、`.y` はその中の位置です。`.x` が 0 バイト、`.y` が 4 バイト、`.z` が 8 バイト、`.w` が 12 バイトです。`packoffset` を使うと、宣言の順とメモリの並びが一致しなくてもよくなりますが、自分で衝突を避ける責任が出ます。

## ConstantBuffer&lt;T&gt; の場合

Shader Model 5.1 以降の `ConstantBuffer<T>` は、`T` の構造体を定数バッファとして使います。レイアウトの規則は `cbuffer` と同じで、`T` のメンバーが先頭から詰められます。構造体の型を共有したいときに便利ですが、この場合も先頭はレジスタの境界です。

## 並べ替えて小さくする

詰め方のきまりを知っていれば、メンバーの順番を変えるだけで、むだな隙間を減らせます。目安は 3 つです。

1. 行列・配列・構造体のように、新しいレジスタから始まる物を先に置く。
2. 16 バイトの `float4` は、そのままレジスタ 1 つに入るので、順番を気にしなくてよい。
3. `float3` と `float`、`float2` と `float2` のように、足して 16 バイトになる組を作る。

たとえば次の `cbuffer` は 124 バイトになり、確保の大きさは 128 バイトです。

```hlsl
cbuffer Wasteful
{
    float3 a;       //   0〜11   （次の float4 が入らないので、12〜15 の 4 バイトが隙間）
    float4 b;       //  16〜31
    float c;        //  32〜35   （次の行列が新しいレジスタから始まるので、36〜47 の 12 バイトが隙間）
    float4x4 m;     //  48〜111
    float d;        // 112〜115
    float2 e;       // 116〜123
};
```

順番を `m`・`b`・`a`・`c`・`e`・`d` に直すと、全体が 108 バイトになり、確保の大きさは 112 バイトです。16 バイト減るだけですが、オブジェクトごとに毎フレーム送る定数バッファなら、数が増えるほど効いてきます。

C++ 側の構造体も、同じ順番に直します。HLSL だけ並べ替えると、またずれます。

## C++ の構造体を合わせる

C++ 側は、2 つのことで HLSL と同じ配置にできます。1 つ目は、`XMFLOAT3` の直後に `float` を置くような、収まる並びはそのまま書くことです。2 つ目は、HLSL で隙間になる場所に、明示的にパディングの変数を入れることです。

```cpp
struct PerObject {
  DirectX::XMFLOAT4X4 world;      //   0
  DirectX::XMFLOAT3 tint;         //  64
  float alpha;                    //  76
  DirectX::XMFLOAT2 uv_scale;     //  80
  float pad0[2];                  //  88  ← HLSL の隙間（lightDir が 96 から始まるため）
  DirectX::XMFLOAT3 light_dir;    //  96
  float intensity;                // 108
  float shine;                    // 112
  float pad1[3];                  // 116  ← 確保の大きさを 16 の倍数にする
};
static_assert(sizeof(PerObject) == 128);
static_assert(offsetof(PerObject, light_dir) == 96);
```

`sizeof` と `offsetof` を `static_assert` で確かめると、ずれたときにコンパイルで止まります。実行して絵がおかしくなってから、バイトを数える必要がなくなります。行列の転置の話は、[Constant Buffer（DirectX 11）](../dx11/constant-buffer.md) と [Constant Buffer（DirectX 12）](../dx12/constant-buffer.md) にあります。

## 自分で確かめる

DXC に `-Od -Fc` を付けると、逆アセンブリに各変数のオフセットが出ます。

```text title="dxc -T ps_6_0 -E main -Od -Fc out.txt shader.hlsl の出力（抜粋）"
; cbuffer PerObject
; {
;
;   struct hostlayout.PerObject
;   {
;
;       column_major float4x4 world;                  ; Offset:    0
;       float3 tint;                                  ; Offset:   64
;       float alpha;                                  ; Offset:   76
;       float2 uvScale;                               ; Offset:   80
;       float3 lightDir;                              ; Offset:   96
;       float intensity;                              ; Offset:  108
;       float shine;                                  ; Offset:  112
;
;   } PerObject;                                      ; Offset:    0 Size:   116
```

`Offset` が各変数の位置で、最後の `Size` が全体の大きさです。注意点が 2 つあります。使われていない `cbuffer` は出力に出ません（`-Od` を付けても消えます）。使われていない変数だけの `cbuffer` を確かめたいときは、全部の変数を 1 回ずつ触るダミーのシェーダーを足します。

毎回これをやるのは面倒です。[K-HLSL](../../khlsl/index.md) は、`cbuffer` や `ConstantBuffer<T>` の名前にカーソルを置くとレジスタの図を出します。C++ の構造体の名前にカーソルを置くと、HLSL の `cbuffer` と比べて、ずれた場所を表と図で教えてくれます。計算の部分は、ここに書いた規則を実装したもので、DXC の出力と突き合わせて確かめています。

## よくあるミス

??? failure "float3 の直後に float3 を並べて、2 つ目がずれる"
    `float3 a; float3 b;` は、a が 0〜11、b が 12〜23 になりそうですが、b は 16 の境界をまたぐので 16〜27 に置かれます。C++ の `XMFLOAT3` を 2 つ並べると、b は 12 に置かれるので、4 バイトずれます。間に `float pad;` を入れるか、`float4` にします。

??? failure "bool を C++ の bool で受けている"
    HLSL の `bool` は 4 バイトです。C++ の `bool` は 1 バイトなので、直後の変数が 3 バイトずれます。`uint32_t` で受けます。

??? failure "float の配列を、そのまま float の配列で渡している"
    `float values[4]` は、HLSL では要素ごとに 16 バイトを使うので、52 バイトです。C++ の `float values[4]` は 16 バイトです。配列の要素を `float4` にして `.x` で使うか、`float4` の配列に 4 つずつ詰めます。

??? failure "float3x3 を 36 バイトだと思っている"
    列優先の `float3x3` は、3 列が別のレジスタに入り、44 バイトです。C++ 側で 9 つの `float` を並べると合いません。`float4x3` や `float4x4` に広げて、渡すのが確実です。

??? failure "全体の大きさを 16 の倍数にしていない"
    定数バッファの大きさは 16 の倍数が必要です。HLSL の計算が 116 バイトでも、C++ 側で作るバッファは 128 バイトにします。DirectX 12 では、定数バッファ ビューの大きさが 256 の倍数になるきまりもあります。

## これだけ覚える

!!! success "これだけ覚える"
    - [x] 16 バイトのレジスタに詰める。またぐなら、次のレジスタの先頭へ送られる
    - [x] `float3` の直後の `float` は収まる。`float2` の直後の `float3` は収まらない
    - [x] 配列は要素ごとにレジスタ 1 つ。最後の要素の余りには、次の変数が入る
    - [x] 行列と構造体は、新しいレジスタから始まる。`float3x3` は 44 バイト
    - [x] `bool` は 4 バイト。C++ では `uint32_t` で受ける
    - [x] 全体は 16 の倍数にそろえる
    - [x] C++ は `static_assert` で、`sizeof` と `offsetof` を確かめる

## 関連ページ

- [Constant Buffer（DirectX 11）](../dx11/constant-buffer.md)
- [Constant Buffer（DirectX 12）](../dx12/constant-buffer.md)
- [Coordinate Conventions](conventions.md)
- [K-HLSL](../../khlsl/index.md)
- [Microsoft Learn: パッキング規則](https://learn.microsoft.com/ja-jp/windows/win32/direct3dhlsl/dx-graphics-hlsl-packing-rules)
