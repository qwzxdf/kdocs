---
title: CPU から GPU へ
tags:
  - 3Dゲーム
  - 描画
---

# CPU から GPU へ

**描画の最初の工程**は、CPU が「何をどう描くか」を GPU に伝えることです。GPU は自分では何も決めません。CPU が用意した頂点のデータと設定を受け取り、命令どおりに描くだけです。このページでは、頂点バッファ・インデックス バッファ・入力レイアウト・定数バッファ・ドロー コール・GPU が非同期で動くしくみを説明します。

!!! tip "ポイント"
    - GPU に渡すのは<strong>データ（頂点・インデックス・定数・テクスチャ）</strong>と<strong>設定（シェーダー・ブレンドなど）</strong>と命令（ドロー コール）。
    - 頂点は頂点バッファ、どの頂点で三角形を作るかはインデックス バッファ。
    - 入力レイアウトでバッファのバイト列を「位置」「色」…として読む方法を教える。
    - 定数バッファは描画全体で共通の値（行列・光の向きなど）。
    - CPU と GPU は並行して動く。CPU が命令を積み、GPU が少し遅れて実行する。

!!! info "このページを読む前に"
    - [描画の流れ（入門）](index.md)（このセクション全体の地図と、読む順番）
    - [行列](../../gamemath/matrices.md)（行列の基礎）
    - [座標系](../../gamemath/coordinate-systems.md)（このサイトの座標系の約束）

## CPU と GPU の分担

<svg class="fig illust" viewBox="0 0 780 260" role="img" aria-label="CPU と GPU の分担">
<text x="20" y="24" class="fig-title">CPU は「準備と命令」、GPU は「大量の計算」</text>
<rect x="30" y="50" width="300" height="180" rx="10" fill="#4c8bf5" fill-opacity="0.15" stroke="#4c8bf5" stroke-width="2"/>
<text x="180" y="78" text-anchor="middle" style="font-size:15px;font-weight:700">CPU</text>
<text x="50" y="108" style="font-size:12px">・ゲームの更新（位置・当たり判定）</text>
<text x="50" y="130" style="font-size:12px">・何を描くか決める（カリング）</text>
<text x="50" y="152" style="font-size:12px">・バッファ・行列・設定を用意</text>
<text x="50" y="174" style="font-size:12px">・ドロー コールを発行</text>
<text x="50" y="208" style="font-size:12px;fill:#e5484d">得意：複雑な判断・順序のある処理</text>
<rect x="450" y="50" width="300" height="180" rx="10" fill="#2ea043" fill-opacity="0.15" stroke="#2ea043" stroke-width="2"/>
<text x="600" y="78" text-anchor="middle" style="font-size:15px;font-weight:700">GPU</text>
<text x="470" y="108" style="font-size:12px">・頂点を変換（数万〜数百万点）</text>
<text x="470" y="130" style="font-size:12px">・三角形をピクセルに分解</text>
<text x="470" y="152" style="font-size:12px">・ピクセルの色を計算（数百万点）</text>
<text x="470" y="174" style="font-size:12px">・深度・ブレンドして書き込む</text>
<text x="470" y="208" style="font-size:12px;fill:#e5484d">得意：同じ計算を大量に並列で</text>
<line x1="332" y1="140" x2="448" y2="140" stroke="currentColor" stroke-width="2"/>
<text x="390" y="130" text-anchor="middle" style="font-size:12px">命令とデータ</text>
</svg>

## GPU に渡すもの

**1 回の描画に必要な材料**です。

| 材料 | 内容 | 例 |
| --- | --- | --- |
| 頂点バッファ | 頂点のデータ（位置・法線・UV など）の並び | モデルの 1 万個の頂点 |
| インデックス バッファ | 頂点の番号で三角形を指定する並び | (0, 1, 2) = 1 つめの三角形 |
| 入力レイアウト | 頂点 1 個のバイト列の読み方 | 「位置が 12 バイト、法線が 12 バイト、UV が 8 バイト」 |
| 定数バッファ | シェーダーに渡す、共通の値 | ワールド行列・カメラ・光 |
| テクスチャ | 画像データ | 色・法線マップ |
| シェーダー | 頂点・ピクセルのプログラム | コンパイル済み |
| ステート | 深度テスト・ブレンドなどの設定 | 深度テストあり、ブレンドなし |
| 描画先 | 結果を書く画像 | バックバッファ |

## 頂点バッファ

**頂点バッファ**は、頂点のデータを並べた配列です。1 頂点が持つデータを「頂点属性」と呼びます。

<svg class="fig illust" viewBox="0 0 780 200" role="img" aria-label="頂点バッファ">
<text x="20" y="24" class="fig-title">頂点バッファ：頂点 1 個 ＝ 位置 ＋ 法線 ＋ UV</text>
<g font-size="12">
<rect x="30" y="50" width="220" height="50" fill="#4c8bf5" fill-opacity="0.25" stroke="#4c8bf5"/><text x="140" y="80" text-anchor="middle">頂点 0</text>
<rect x="250" y="50" width="220" height="50" fill="#2ea043" fill-opacity="0.25" stroke="#2ea043"/><text x="360" y="80" text-anchor="middle">頂点 1</text>
<rect x="470" y="50" width="220" height="50" fill="#e5aa28" fill-opacity="0.25" stroke="#e5aa28"/><text x="580" y="80" text-anchor="middle">頂点 2</text>
<text x="700" y="80">…</text>
</g>
<g font-size="11">
<rect x="30" y="120" width="100" height="30" fill="#4c8bf5" fill-opacity="0.5"/><text x="80" y="140" text-anchor="middle">位置 float3</text>
<rect x="130" y="120" width="80" height="30" fill="#2ea043" fill-opacity="0.5"/><text x="170" y="140" text-anchor="middle">法線</text>
<rect x="210" y="120" width="40" height="30" fill="#e5aa28" fill-opacity="0.6"/><text x="230" y="140" text-anchor="middle">UV</text>
</g>
<text x="260" y="140" style="font-size:12px">← 頂点 0 の中身（合計 32 バイト）</text>
<text x="30" y="180" style="font-size:12px">GPU には「ただのバイト列」として渡る。どう読むかは入力レイアウトで教える</text>
</svg>

```cpp
struct Vertex {
  DirectX::SimpleMath::Vector3 position;
  DirectX::SimpleMath::Vector3 normal;
  DirectX::SimpleMath::Vector2 uv;
};

const Vertex vertices[] = {
    {{-0.5f, -0.5f, 0.0f}, {0, 0, -1}, {0, 1}},
    {{0.0f, 0.5f, 0.0f}, {0, 0, -1}, {0.5f, 0}},
    {{0.5f, -0.5f, 0.0f}, {0, 0, -1}, {1, 1}},
};

D3D11_BUFFER_DESC desc = {};
desc.ByteWidth = sizeof(vertices);
desc.Usage = D3D11_USAGE_IMMUTABLE;
desc.BindFlags = D3D11_BIND_VERTEX_BUFFER;

D3D11_SUBRESOURCE_DATA data = {};
data.pSysMem = vertices;

device->CreateBuffer(&desc, &data, vertex_buffer.GetAddressOf());
```

| 点 | 説明 |
| --- | --- |
| `IMMUTABLE` | 作った後は変更しない（GPU が最も速く扱える）。動くモデルでも頂点は同じでよい（動かすのは変換行列） |
| `BindFlags` | このバッファを「頂点バッファ」として使う宣言 |
| データは最初に一度だけ送る | 毎フレーム送らない（遅くなる） |

## インデックス バッファ

**四角形を描くのに頂点が 4 個あれば足りる**のに、三角形 2 枚だと 6 頂点（2 個が重複）になります。インデックス バッファは、頂点の番号の並びで三角形を指定し、重複を避けます。

<svg class="fig illust" viewBox="0 0 780 240" role="img" aria-label="インデックス バッファ">
<text x="20" y="24" class="fig-title">四角形 ＝ 頂点 4 個 ＋ インデックス 6 個</text>
<g transform="translate(40,50)">
<rect x="0" y="0" width="140" height="140" fill="none" stroke="currentColor" stroke-opacity="0.3"/>
<polygon points="0,0 140,0 140,140" fill="#4c8bf5" fill-opacity="0.3" stroke="#4c8bf5" stroke-width="2"/>
<polygon points="0,0 140,140 0,140" fill="#2ea043" fill-opacity="0.3" stroke="#2ea043" stroke-width="2"/>
<circle cx="0" cy="0" r="6" fill="currentColor"/><circle cx="140" cy="0" r="6" fill="currentColor"/><circle cx="140" cy="140" r="6" fill="currentColor"/><circle cx="0" cy="140" r="6" fill="currentColor"/>
<text x="-18" y="-6" style="font-size:13px">0</text><text x="146" y="-6" style="font-size:13px">1</text><text x="146" y="158" style="font-size:13px">2</text><text x="-18" y="158" style="font-size:13px">3</text>
</g>
<g transform="translate(260,60)" style="font-size:13px">
<text x="0" y="0" style="font-weight:700">頂点バッファ（4 個）</text>
<text x="0" y="26">[0] 左上 [1] 右上 [2] 右下 [3] 左下</text>
<text x="0" y="70" style="font-weight:700">インデックス バッファ（6 個）</text>
<text x="0" y="96" style="fill:#4c8bf5">0, 1, 2</text><text x="70" y="96">← 1 枚目（右上）</text>
<text x="0" y="120" style="fill:#2ea043">0, 2, 3</text><text x="70" y="120">← 2 枚目（左下）</text>
<text x="0" y="160" style="font-size:12px">頂点 0 と 2 を共有 → 重複を省ける</text>
</g>
</svg>

```cpp
const uint16_t indices[] = {0, 1, 2, 0, 2, 3};

D3D11_BUFFER_DESC desc = {};
desc.ByteWidth = sizeof(indices);
desc.Usage = D3D11_USAGE_IMMUTABLE;
desc.BindFlags = D3D11_BIND_INDEX_BUFFER;
D3D11_SUBRESOURCE_DATA data = {indices};
device->CreateBuffer(&desc, &data, index_buffer.GetAddressOf());
```

三角形の頂点の並ぶ向きは大事です。このサイトの座標系（左手系）では画面から見て時計回りが「表」で、反対側（反時計回り）は裏として描かれません（[ラスタライズ](rasterize.md)のカリング）。

| 点 | 説明 |
| --- | --- |
| `uint16_t` か `uint32_t` | 頂点数が 65535 以下なら 16 ビットで足りる（メモリが半分） |
| メッシュ全体が 1 つの束 | 頂点が共有されるほど、データも処理も減る |
| 頂点キャッシュ | GPU は変換済みの頂点を覚えているので、隣接する三角形で頂点を使い回すと速い（メッシュ最適化ツールで並び替える） |

## 入力レイアウト

**頂点バッファはただのバイト列**です。「最初の 12 バイトは位置、次の 12 バイトは法線…」と教えるのが入力レイアウトです。

```cpp
const D3D11_INPUT_ELEMENT_DESC layout[] = {
    {"POSITION", 0, DXGI_FORMAT_R32G32B32_FLOAT, 0, 0, D3D11_INPUT_PER_VERTEX_DATA, 0},
    {"NORMAL", 0, DXGI_FORMAT_R32G32B32_FLOAT, 0, 12, D3D11_INPUT_PER_VERTEX_DATA, 0},
    {"TEXCOORD", 0, DXGI_FORMAT_R32G32_FLOAT, 0, 24, D3D11_INPUT_PER_VERTEX_DATA, 0},
};
```

```hlsl
struct VSInput {
  float3 position : POSITION;
  float3 normal : NORMAL;
  float2 uv : TEXCOORD0;
};
```

| 項目 | 内容 |
| --- | --- |
| セマンティクス名 | `POSITION`・`NORMAL`・`TEXCOORD`。HLSL の入力と対応させる名前 |
| フォーマット | `R32G32B32_FLOAT` ＝ 4 バイト浮動小数が 3 個（float3） |
| オフセット | 頂点の先頭から何バイト目か（0・12・24） |
| 入力スロット | 複数の頂点バッファに分けて渡すとき、どのバッファか |

## 定数バッファ

**頂点ごとに違うデータ**は頂点バッファですが、全頂点で共通の値（ワールド行列・カメラ・光）は定数バッファで渡します。

```cpp
struct alignas(16) PerObject {
  DirectX::SimpleMath::Matrix world;
  DirectX::SimpleMath::Matrix view_projection;
};

D3D11_BUFFER_DESC desc = {};
desc.ByteWidth = sizeof(PerObject);
desc.Usage = D3D11_USAGE_DYNAMIC;
desc.BindFlags = D3D11_BIND_CONSTANT_BUFFER;
desc.CPUAccessFlags = D3D11_CPU_ACCESS_WRITE;
device->CreateBuffer(&desc, nullptr, constant_buffer.GetAddressOf());

D3D11_MAPPED_SUBRESOURCE mapped;
context->Map(constant_buffer.Get(), 0, D3D11_MAP_WRITE_DISCARD, 0, &mapped);
std::memcpy(mapped.pData, &per_object, sizeof(per_object));
context->Unmap(constant_buffer.Get(), 0);
context->VSSetConstantBuffers(0, 1, constant_buffer.GetAddressOf());
```

| 点 | 説明 |
| --- | --- |
| `DYNAMIC` ＋ `WRITE_DISCARD` | 毎フレーム CPU から書き換える用途の設定 |
| 16 バイト境界 | 定数バッファは 16 バイトごとに区切られる。構造体のサイズ・並びを揃える |
| スロット番号 | `register(b0)` と `VSSetConstantBuffers(0, …)` の `0` が対応 |

## ドロー コール

**材料を揃えたら、最後に「描け」と命令します**。これが「ドロー コール」です。

```cpp
UINT stride = sizeof(Vertex);
UINT offset = 0;
context->IASetVertexBuffers(0, 1, vertex_buffer.GetAddressOf(), &stride, &offset);
context->IASetIndexBuffer(index_buffer.Get(), DXGI_FORMAT_R16_UINT, 0);
context->IASetInputLayout(input_layout.Get());
context->IASetPrimitiveTopology(D3D11_PRIMITIVE_TOPOLOGY_TRIANGLELIST);

context->VSSetShader(vertex_shader.Get(), nullptr, 0);
context->PSSetShader(pixel_shader.Get(), nullptr, 0);

context->DrawIndexed(6, 0, 0);
```

| 関数 | 意味 |
| --- | --- |
| `IASet…` | 入力アセンブラ（Input Assembler）に頂点・インデックス・レイアウト・形の種類を設定 |
| `PrimitiveTopology` | 三角形のリスト（3 個ずつ区切る）・ストリップ（隣と共有）・線・点など |
| `VSSet… / PSSet…` | 使うシェーダー・定数・テクスチャの設定 |
| `DrawIndexed(6, 0, 0)` | インデックス 6 個で描く（開始位置 0、頂点のずれ 0） |

<svg class="fig illust" viewBox="0 0 780 220" role="img" aria-label="ドロー コールの前後"><defs><marker id="rfa" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs>
<text x="20" y="24" class="fig-title">状態を設定する → ドロー コールで実行：設定は「次の描画」に効く</text>
<g font-size="12">
<rect x="30" y="50" width="170" height="40" rx="6" fill="#4c8bf5" fill-opacity="0.2" stroke="#4c8bf5"/><text x="115" y="75" text-anchor="middle">頂点バッファを設定</text>
<rect x="30" y="100" width="170" height="40" rx="6" fill="#4c8bf5" fill-opacity="0.2" stroke="#4c8bf5"/><text x="115" y="125" text-anchor="middle">シェーダーを設定</text>
<rect x="30" y="150" width="170" height="40" rx="6" fill="#4c8bf5" fill-opacity="0.2" stroke="#4c8bf5"/><text x="115" y="175" text-anchor="middle">定数・テクスチャを設定</text>
<rect x="290" y="95" width="140" height="50" rx="8" fill="#e5484d" fill-opacity="0.25" stroke="#e5484d" stroke-width="2"/><text x="360" y="125" text-anchor="middle" style="font-weight:700">DrawIndexed</text>
<rect x="520" y="95" width="210" height="50" rx="8" fill="#2ea043" fill-opacity="0.2" stroke="#2ea043"/><text x="625" y="125" text-anchor="middle">設定どおりに GPU が描く</text>
</g>
<line x1="200" y1="120" x2="288" y2="120" stroke="currentColor" stroke-width="2" marker-end="url(#rfa)"/>
<line x1="430" y1="120" x2="518" y2="120" stroke="currentColor" stroke-width="2" marker-end="url(#rfa)"/>
</svg>

DX11 は設定が「状態」として残ります。次のドロー コールにも、前の設定がそのまま効くので、変えたい所だけを設定し直します。ドロー コールの数が多いと CPU が忙しくなるので、まとめる工夫が重要です（[ドロー コール](../../rendering/draw-calls.md)）。

## CPU と GPU は並行して動く

**`DrawIndexed` を呼んでも、その場で描き終わるわけではありません**。命令は GPU 用のキューに積まれ、CPU はすぐ次の処理に進みます。GPU は少し遅れて、積まれた命令を順に実行します。

<svg class="fig illust motion" data-fig="cpu-gpu-parallel" viewBox="0 0 780 220" role="img" aria-label="CPU と GPU の並行動作">
<text x="20" y="24" class="fig-title">CPU が命令を積み、GPU が少し遅れて実行する（パイプライン処理）</text>
<text x="20" y="78" style="font-size:13px;font-weight:700">CPU</text>
<text x="20" y="148" style="font-size:13px;font-weight:700">GPU</text>
<g font-size="12">
<rect x="80" y="55" width="120" height="36" fill="#4c8bf5" fill-opacity="0.35" stroke="#4c8bf5"/><text x="140" y="78" text-anchor="middle">フレーム 1 の命令</text>
<rect x="210" y="55" width="120" height="36" fill="#4c8bf5" fill-opacity="0.35" stroke="#4c8bf5"/><text x="270" y="78" text-anchor="middle">フレーム 2 の命令</text>
<rect x="340" y="55" width="120" height="36" fill="#4c8bf5" fill-opacity="0.35" stroke="#4c8bf5"/><text x="400" y="78" text-anchor="middle">フレーム 3 の命令</text>
<rect x="470" y="55" width="120" height="36" fill="#4c8bf5" fill-opacity="0.35" stroke="#4c8bf5"/><text x="530" y="78" text-anchor="middle">フレーム 4 の命令</text>
<rect x="150" y="125" width="130" height="36" fill="#2ea043" fill-opacity="0.35" stroke="#2ea043"/><text x="215" y="148" text-anchor="middle">フレーム 1 を描く</text>
<rect x="290" y="125" width="130" height="36" fill="#2ea043" fill-opacity="0.35" stroke="#2ea043"/><text x="355" y="148" text-anchor="middle">フレーム 2 を描く</text>
<rect x="430" y="125" width="130" height="36" fill="#2ea043" fill-opacity="0.35" stroke="#2ea043"/><text x="495" y="148" text-anchor="middle">フレーム 3 を描く</text>
</g>
<line x1="80" y1="190" x2="740" y2="190" stroke="currentColor" stroke-opacity="0.4"/>
<text x="740" y="208" text-anchor="end" style="font-size:12px">時間 →</text>
<circle cx="0" cy="190" r="5" fill="#e5484d"><animate attributeName="cx" values="80;740" dur="5s" repeatCount="indefinite"/></circle>
</svg>

| 点 | 説明 |
| --- | --- |
| 並行して動く | CPU が次のフレームを準備している間に GPU は前のフレームを描く |
| 遅いほうに合わせる | どちらかが遅いともう一方が待つ（[何が重いのか](../../rendering/bottlenecks.md)） |
| 数フレーム先まで積む | 積める数に上限があり、多すぎると入力の遅延が増える |
| 結果の読み戻しは遅い | GPU の結果を CPU が読もうとすると、描き終わるまで待たされる（同期）。避ける |

## よくあるミス

??? failure "頂点バッファを毎フレーム作り直して遅い"
    **一度作って使い回す**。動かすのは行列で。

??? failure "入力レイアウトと HLSL の入力が合わず、描画が崩れる"
    セマンティクス名・フォーマット・オフセットを頂点の構造体と揃える。

??? failure "定数バッファのサイズが 16 バイトの倍数でなく、作成に失敗する"
    `ByteWidth` は 16 の倍数に。構造体をパディングで合わせる。

??? failure "三角形の頂点の順が逆で、何も表示されない"
    時計回りが表（左手系）。逆なら並びを入れ替えるか、カリングの設定を直す。

??? failure "描画前にシェーダー／バッファを設定し忘れる"
    前の描画の設定がそのまま残るので予期しない結果。ドロー コールごとに全部設定する習慣をつける。

## これだけ覚える

!!! abstract "まとめ"
    - [x] GPU は<strong>命令どおりに描くだけ</strong>。CPU が材料（頂点・インデックス・定数・シェーダー・ステート）を揃える
    - [x] 頂点バッファ ＝ 頂点のデータ。インデックス バッファ ＝ 三角形の組み方
    - [x] 入力レイアウトでバイト列の読み方を教える
    - [x] 定数バッファ ＝ 全頂点で共通の値（16 バイト境界）
    - [x] ドロー コールで実行。CPU と GPU は並行して動く

## 参考

- Microsoft, "Direct3D 11 Graphics Pipeline"（Microsoft Learn）
- Microsoft, "Input-Assembler Stage"（Microsoft Learn）
- Fabian Giesen, "A trip through the Graphics Pipeline 2011"

## 関連ページ

- [描画の流れ（入門）](index.md)
- [頂点の工程](vertex-stage.md)
- [モデルの基本](../model-basics.md)
- [ドロー コール](../../rendering/draw-calls.md)
