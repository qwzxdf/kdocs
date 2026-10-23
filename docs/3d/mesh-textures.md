---
title: メッシュとテクスチャ
tags:
  - 3Dゲーム
---

# メッシュとテクスチャ

このページは、**3D モデルを DirectX 11 で描く**ための、データの作り方をまとめます。「メッシュ」は、3D モデルの形そのもの（三角形の集まり）、「テクスチャ」は、表面に貼る画像のことです。まだ、これらの言葉に慣れていなければ、先に [3D モデルの基礎](model-basics.md) を読んでください（頂点・三角形・UV・バッファをゼロから説明しています）。

!!! tip "ポイント"
    - <strong>メッシュ（＝3D モデルの形）</strong>は、<strong>三角形の集まり</strong>。GPU に渡すときは、頂点バッファ（＝頂点のリストを置く、GPU 側の置き場）と、インデックスバッファ（＝「どの頂点で三角形を作るか」の番号リストの置き場）に分ける。
    - 頂点には位置・法線・UV などを持たせる。入力レイアウトは、「頂点の中身がどう並んでいるか」を GPU に教える説明書。
    - UVは、「テクスチャ画像のどこを使うか」を表す座標（DX は左上が (0, 0)）。
    - サンプラーは、テクスチャを読むときのルール（拡大したときの補間、はみ出したときの扱い）。ミップマップは、縮小した画像のセットで、遠くのちらつきを抑える。
    - バッファは、一度作って使い回す。毎フレーム作らない。
    - 頂点が 65536 個以下なら、インデックスは 16 ビットで足りる（メモリが半分）。

## 頂点

頂点は**位置**だけでなく、陰影やテクスチャに必要な値を持ちます。

```cpp
struct Vertex {
  DirectX::SimpleMath::Vector3 position;
  DirectX::SimpleMath::Vector3 normal;
  DirectX::SimpleMath::Vector2 uv;
};
```

| 属性 | 型 | 用途 |
| --- | --- | --- |
| 位置（position） | `Vector3` | 頂点の座標（ローカル） |
| 法線（normal） | `Vector3` | 陰影（[法線とライティング](lighting-normals.md)） |
| UV（texcoord） | `Vector2` | テクスチャの座標 |
| 接線（tangent） | `Vector3` / `Vector4` | 法線マップ |
| 色（color） | `Vector4` / `uint32_t` | 頂点カラー |
| ボーン番号・重み | `uint8_t[4]` / `float[4]` | スキニング（[スキニング](skinning-animation.md)） |

## インデックスバッファ

四角形は、**2 つの三角形**です。頂点を共有して、インデックスで三角形を組みます（時計回りが表になる順に並べます）。

<svg class="fig" viewBox="0 0 520 190" role="img" aria-label="四角形を 2 つの三角形で表す"><polygon points="60,40 190,40 190,150 60,150" fill="none" stroke="currentColor" stroke-width="2"/><line x1="60" y1="150" x2="190" y2="40" stroke="currentColor" stroke-width="2" stroke-dasharray="5 4"/><text x="30" y="35">v3</text><text x="196" y="35">v2</text><text x="30" y="165">v0</text><text x="196" y="165">v1</text><text x="250" y="60" class="fig-title">頂点：v0 v1 v2 v3（4 個）</text><text x="250" y="90" class="fig-title">インデックス：0 2 1、0 3 2（6 個）</text><text x="250" y="130">インデックスなしなら、6 頂点が必要</text></svg>

| 方式 | 頂点数（四角形） | メモリ |
| --- | --- | --- |
| インデックスなし | 6 | 多い |
| インデックスあり | 4 + インデックス 6 | 少ない（共有の多いメッシュで大きく節約） |

| インデックス型 | 範囲 | 用途 |
| --- | --- | --- |
| `uint16_t` | 〜 65535 頂点 | 小さなメッシュ。メモリが半分 |
| `uint32_t` | 約 43 億 | 大きなメッシュ |

!!! note "巻き順（CW が表）"
    三角形の頂点の並びは、時計回りが表です（左手系。[深度とカリング](depth-culling.md)）。

## DX11 でバッファを作る

### 頂点バッファ

```cpp
std::vector<Vertex> vertices = {
    {{-0.5f, 0.0f, 0.5f}, {0, 1, 0}, {0, 0}},
    {{0.5f, 0.0f, 0.5f}, {0, 1, 0}, {1, 0}},
    {{0.5f, 0.0f, -0.5f}, {0, 1, 0}, {1, 1}},
    {{-0.5f, 0.0f, -0.5f}, {0, 1, 0}, {0, 1}},
};

D3D11_BUFFER_DESC vb_desc = {};
vb_desc.ByteWidth = static_cast<UINT>(sizeof(Vertex) * vertices.size());
vb_desc.Usage = D3D11_USAGE_IMMUTABLE;
vb_desc.BindFlags = D3D11_BIND_VERTEX_BUFFER;

D3D11_SUBRESOURCE_DATA vb_data = {};
vb_data.pSysMem = vertices.data();

Microsoft::WRL::ComPtr<ID3D11Buffer> vertex_buffer;
device->CreateBuffer(&vb_desc, &vb_data, &vertex_buffer);
```

### インデックスバッファ

```cpp
std::vector<uint16_t> indices = {0, 2, 1, 0, 3, 2};

D3D11_BUFFER_DESC ib_desc = {};
ib_desc.ByteWidth = static_cast<UINT>(sizeof(uint16_t) * indices.size());
ib_desc.Usage = D3D11_USAGE_IMMUTABLE;
ib_desc.BindFlags = D3D11_BIND_INDEX_BUFFER;

D3D11_SUBRESOURCE_DATA ib_data = {};
ib_data.pSysMem = indices.data();

Microsoft::WRL::ComPtr<ID3D11Buffer> index_buffer;
device->CreateBuffer(&ib_desc, &ib_data, &index_buffer);
```

### Usage の選び方

| `Usage` | 更新 | 用途 |
| --- | --- | --- |
| **`IMMUTABLE`** | できない（作成時のみ） | 変わらないメッシュ。最速 |
| `DEFAULT` | `UpdateSubresource` | たまに更新 |
| `DYNAMIC` | `Map`（`WRITE_DISCARD`）で、毎フレーム | パーティクル、動的なメッシュ。`CPUAccessFlags = WRITE` が必要 |

## 入力レイアウト

**頂点バッファの中身の並び**を、GPU に教えるのが入力レイアウトです。頂点シェーダーの入力（セマンティクス）と対応させます。

```cpp
D3D11_INPUT_ELEMENT_DESC layout[] = {
    {"POSITION", 0, DXGI_FORMAT_R32G32B32_FLOAT, 0, offsetof(Vertex, position),
     D3D11_INPUT_PER_VERTEX_DATA, 0},
    {"NORMAL", 0, DXGI_FORMAT_R32G32B32_FLOAT, 0, offsetof(Vertex, normal),
     D3D11_INPUT_PER_VERTEX_DATA, 0},
    {"TEXCOORD", 0, DXGI_FORMAT_R32G32_FLOAT, 0, offsetof(Vertex, uv),
     D3D11_INPUT_PER_VERTEX_DATA, 0},
};

Microsoft::WRL::ComPtr<ID3D11InputLayout> input_layout;
device->CreateInputLayout(layout, _countof(layout), vs_bytecode->GetBufferPointer(),
                          vs_bytecode->GetBufferSize(), &input_layout);
```

| 項目 | 説明 |
| --- | --- |
| セマンティクス名・番号 | HLSL の `POSITION`・`NORMAL`・`TEXCOORD0` と、同じ名前 |
| フォーマット | `R32G32B32_FLOAT` ＝ `float` 3 つ。`Vector3` に対応 |
| オフセット | 構造体の中の位置。`offsetof` が確実 |
| スロット | 頂点バッファの番号（複数の頂点バッファを使うとき） |
| `PER_VERTEX_DATA` / `PER_INSTANCE_DATA` | 頂点ごとか、インスタンスごとか（インスタンシング） |

## 描画する

```cpp
UINT stride = sizeof(Vertex);
UINT offset = 0;
context->IASetInputLayout(input_layout.Get());
context->IASetVertexBuffers(0, 1, vertex_buffer.GetAddressOf(), &stride, &offset);
context->IASetIndexBuffer(index_buffer.Get(), DXGI_FORMAT_R16_UINT, 0);
context->IASetPrimitiveTopology(D3D11_PRIMITIVE_TOPOLOGY_TRIANGLELIST);

context->DrawIndexed(static_cast<UINT>(indices.size()), 0, 0);
```

| 項目 | 説明 |
| --- | --- |
| `stride` | 頂点 1 つのバイト数（`sizeof(Vertex)`） |
| `DXGI_FORMAT_R16_UINT` / `R32_UINT` | インデックスの型と**一致**させる |
| `TRIANGLELIST` | 3 つごとに、1 つの三角形（最も一般的） |
| `DrawIndexed(個数, 開始位置, 頂点のずれ)` | インデックスを使う描画 |

## UV とテクスチャ

**UV**はテクスチャ上の座標です。頂点ごとに持ち、三角形の内部は、補間されます。

<svg class="fig" viewBox="0 0 440 240" role="img" aria-label="UV 座標の向き"><defs><marker id="ah3" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="currentColor"/></marker></defs><rect x="60" y="30" width="160" height="160" fill="none" stroke="currentColor" stroke-width="2"/><text x="110" y="115">テクスチャ</text><line x1="60" y1="30" x2="260" y2="30" stroke="currentColor" stroke-width="2" marker-end="url(#ah3)"/><text x="262" y="35">U</text><line x1="60" y1="30" x2="60" y2="215" stroke="currentColor" stroke-width="2" marker-end="url(#ah3)"/><text x="48" y="232">V</text><text x="20" y="25">(0,0)</text><text x="225" y="22">(1,0)</text><text x="225" y="205">(1,1)</text><text x="14" y="205" style="display:none">.</text><text x="290" y="90">DirectX：左上が原点</text><text x="290" y="115">V は下向きに増える</text></svg>

| API | UV の原点 |
| --- | --- |
| DirectX | 左上 |
| OpenGL | 左下 |

OpenGL 系のモデル（`.obj`・`.gltf` など）を読むと上下が逆になることがあります。読み込み時に `v = 1 - v` で直します。

### テクスチャを読み込んで使う（DirectXTK）

```cpp
#include <DDSTextureLoader.h>
#include <WICTextureLoader.h>

Microsoft::WRL::ComPtr<ID3D11ShaderResourceView> srv;
DirectX::CreateWICTextureFromFile(device, context, L"assets/albedo.png", nullptr, &srv);
DirectX::CreateDDSTextureFromFile(device, L"assets/albedo.dds", nullptr, &srv);

context->PSSetShaderResources(0, 1, srv.GetAddressOf());
```

| ローダー | 用途 |
| --- | --- |
| `CreateWICTextureFromFile` | PNG・JPG など。ミップマップを自動生成する（`context` を渡したとき） |
| `CreateDDSTextureFromFile` | DDS（圧縮・ミップ済み）。本番はこれが速い |
| `DirectXTex` | 変換・圧縮・ミップ生成のツール・ライブラリ |

sRGB：色のテクスチャは、`DXGI_FORMAT_*_SRGB` として読むと、ガンマ補正が自動です（`WIC_LOADER_FORCE_SRGB`）。法線マップ・数値のテクスチャは、sRGB にしません。

## サンプラー

**テクスチャをどう読むか**を決めます。

```cpp
D3D11_SAMPLER_DESC sampler_desc = {};
sampler_desc.Filter = D3D11_FILTER_MIN_MAG_MIP_LINEAR;
sampler_desc.AddressU = D3D11_TEXTURE_ADDRESS_WRAP;
sampler_desc.AddressV = D3D11_TEXTURE_ADDRESS_WRAP;
sampler_desc.AddressW = D3D11_TEXTURE_ADDRESS_WRAP;
sampler_desc.MaxLOD = D3D11_FLOAT32_MAX;

Microsoft::WRL::ComPtr<ID3D11SamplerState> sampler;
device->CreateSamplerState(&sampler_desc, &sampler);
context->PSSetSamplers(0, 1, sampler.GetAddressOf());
```

### フィルター

<svg class="fig" viewBox="0 0 600 190" role="img" aria-label="フィルターの違い">
<text x="20" y="22" class="fig-title">POINT（最近傍）：ドットがくっきり</text>
<g stroke="currentColor" stroke-width="1">
<rect x="30" y="40" width="30" height="30" fill="#2a4fa8"/><rect x="60" y="40" width="30" height="30" fill="#e5e5e5"/><rect x="90" y="40" width="30" height="30" fill="#2a4fa8"/><rect x="120" y="40" width="30" height="30" fill="#e5e5e5"/>
<rect x="30" y="70" width="30" height="30" fill="#e5e5e5"/><rect x="60" y="70" width="30" height="30" fill="#2a4fa8"/><rect x="90" y="70" width="30" height="30" fill="#e5e5e5"/><rect x="120" y="70" width="30" height="30" fill="#2a4fa8"/>
</g>
<text x="20" y="130">拡大しても、マスの色が、そのまま</text><text x="20" y="152">→ ピクセルアート向き</text>
<text x="320" y="22" class="fig-title">LINEAR（線形補間）：なめらか</text>
<defs><linearGradient id="lg1" x1="0" x2="1" y1="0" y2="1"><stop offset="0" stop-color="#2a4fa8"/><stop offset="0.5" stop-color="#9aa7c9"/><stop offset="1" stop-color="#2a4fa8"/></linearGradient></defs>
<rect x="330" y="40" width="120" height="60" fill="url(#lg1)" stroke="currentColor"/>
<text x="320" y="130">拡大すると、周りの色を混ぜて、なめらかに</text><text x="320" y="152">→ 標準。写真・テクスチャ向き</text>
</svg>

| フィルター | 説明 | 用途 |
| --- | --- | --- |
| `MIN_MAG_MIP_POINT` | 最近傍（補間なし）。ドット絵がくっきり | ピクセルアート、データのテクスチャ |
| `MIN_MAG_MIP_LINEAR` | 双線形 + ミップ間も補間（トライリニア） | 標準 |
| `ANISOTROPIC` | 異方性。斜めから見た面がくっきり | 床・道路など。`MaxAnisotropy` を設定 |

### アドレスモード

<svg class="fig" viewBox="0 0 600 190" role="img" aria-label="アドレスモード">
<text x="20" y="22" class="fig-title">WRAP（繰り返す）</text>
<rect x="30" y="40" width="40" height="40" fill="#2a4fa8" stroke="currentColor"/><rect x="70" y="40" width="40" height="40" fill="#2a4fa8" stroke="currentColor"/><rect x="110" y="40" width="40" height="40" fill="#2a4fa8" stroke="currentColor"/>
<text x="44" y="62" style="fill:#fff">絵</text><text x="84" y="62" style="fill:#fff">絵</text><text x="124" y="62" style="fill:#fff">絵</text>
<text x="20" y="110">0〜1 の外では、画像が、</text><text x="20" y="130">タイルのように並ぶ（床・壁）</text>
<text x="320" y="22" class="fig-title">CLAMP（端を伸ばす）</text>
<rect x="330" y="40" width="40" height="40" fill="#2a4fa8" stroke="currentColor"/><rect x="370" y="40" width="40" height="40" fill="#5f8ff0" stroke="currentColor"/><rect x="410" y="40" width="40" height="40" fill="#5f8ff0" stroke="currentColor"/>
<text x="344" y="62" style="fill:#fff">絵</text><text x="384" y="62" style="fill:#fff">端</text><text x="424" y="62" style="fill:#fff">端</text>
<text x="320" y="110">外では、端の色が、</text><text x="320" y="130">そのまま伸びる（空・UI）</text>
</svg>

UV が `0..1` の外に出たときの扱いです。

| モード | 動き | 用途 |
| --- | --- | --- |
| `WRAP` | 繰り返す | 床・壁のタイリング |
| `CLAMP` | 端の色を伸ばす | スカイボックス、UI |
| `MIRROR` | 折り返す | つなぎ目を目立たせない |
| `BORDER` | 指定色 | 影の範囲外など |

## ミップマップ

**テクスチャを半分・4 分の 1 ... と縮小した画像を、あらかじめ作っておく**仕組みです。遠くの面では小さい画像を使うのでちらつき（モアレ）が減り、キャッシュにも優しくなります。

<svg class="fig flow" viewBox="0 0 704 112" role="img" aria-label="ミップマップ：半分ずつ縮小した画像を用意する（メモリは約 1.33 倍）"><defs><marker id="fl37951" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">ミップマップ：半分ずつ縮小した画像を用意する（メモリは約 1.33 倍）</text><line x1="111.0" y1="64.0" x2="169.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl37951)"/><line x1="255.0" y1="64.0" x2="313.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl37951)"/><line x1="399.0" y1="64.0" x2="457.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl37951)"/><line x1="539.0" y1="64.0" x2="597.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl37951)"/><rect x="28.0" y="44.0" width="80" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="68.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">512×512</text><circle cx="30.0" cy="46.0" r="10" fill="#4c8bf5"/><text x="30.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">1</text><rect x="172.0" y="44.0" width="80" height="40" rx="9" fill="rgba(46,160,67,0.22)" stroke="#2ea043" stroke-width="2"/><text x="212.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">256×256</text><circle cx="174.0" cy="46.0" r="10" fill="#2ea043"/><text x="174.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">2</text><rect x="316.0" y="44.0" width="80" height="40" rx="9" fill="rgba(229,170,40,0.25)" stroke="#e5a828" stroke-width="2"/><text x="356.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">128×128</text><circle cx="318.0" cy="46.0" r="10" fill="#e5a828"/><text x="318.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">3</text><rect x="460.0" y="44.0" width="76" height="40" rx="9" fill="rgba(229,72,77,0.20)" stroke="#e5484d" stroke-width="2"/><text x="498.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">...</text><circle cx="462.0" cy="46.0" r="10" fill="#e5484d"/><text x="462.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">4</text><rect x="600.0" y="44.0" width="76" height="40" rx="9" fill="rgba(150,100,230,0.22)" stroke="#9664e6" stroke-width="2"/><text x="638.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">1×1</text><circle cx="602.0" cy="46.0" r="10" fill="#9664e6"/><text x="602.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">5</text></svg>

| 項目 | 説明 |
| --- | --- |
| 効果 | 遠くのちらつきが消える。速くなることが多い |
| コスト | メモリが約 33% 増える |
| 作り方 | ローダーの自動生成、`GenerateMips`、DDS に最初から入れる |
| 使わない場合 | UI・2D スプライト（等倍で表示するもの） |

## メッシュの読み込み

| 形式 | 特徴 |
| --- | --- |
| **`.obj`** | 単純なテキスト。アニメーションなし。学習・簡単な用途 |
| `.fbx` | 業界標準。アニメーション・ボーンあり。SDK が重い |
| `.gltf` / `.glb` | オープン形式。軽量。PBR・アニメーション対応。おすすめ |
| 独自形式 | 読み込みが速い。ツールで変換して、ゲーム用に最適化 |
| `.sdkmesh`（DirectXTK） | DX 向けのサンプル形式 |

!!! tip "ゲームの本番は、独自の軽い形式に変換する"
    開発中は `.gltf`・`.fbx`、リリース時はビルド時に独自の形式に変換して、そのままメモリに読む形にします。読み込みが速く、扱いも単純になります。

## 頂点の最適化

| 方法 | 効果 |
| --- | --- |
| 頂点の共有（インデックス） | メモリ・頂点処理を減らす |
| 頂点のフォーマットを小さく | 法線を `R10G10B10A2`、UV を `half` に |
| 頂点キャッシュの最適化 | 三角形の並びを、GPU のキャッシュに優しく並べ替え（`DirectXMesh` の `OptimizeFaces`） |
| インスタンシング | 同じメッシュを大量に描く（木・草・弾）。1 回の描画命令で |
| LOD | 遠くは頂点の少ないモデル |

<!-- fig:uv-sampling:begin -->

<svg class="fig illust motion" data-fig="uv-sampling" viewBox="0 0 780 440" role="img"><rect x="0" y="0" width="780" height="440" rx="14" fill="#ffffff"/>
<defs><marker id="arr-uv-sampling" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">UV 座標から、テクスチャの画素(テクセル)を選ぶ</text>
<rect x="230" y="90" width="40" height="40" fill="#dbeafe" stroke="#ffffff" stroke-width="1"/>
<rect x="270" y="90" width="40" height="40" fill="#94aae0" stroke="#ffffff" stroke-width="1"/>
<rect x="310" y="90" width="40" height="40" fill="#4d6ac3" stroke="#ffffff" stroke-width="1"/>
<rect x="350" y="90" width="40" height="40" fill="#c3d5f4" stroke="#ffffff" stroke-width="1"/>
<rect x="390" y="90" width="40" height="40" fill="#7c95d6" stroke="#ffffff" stroke-width="1"/>
<rect x="430" y="90" width="40" height="40" fill="#3655b9" stroke="#ffffff" stroke-width="1"/>
<rect x="470" y="90" width="40" height="40" fill="#acc0ea" stroke="#ffffff" stroke-width="1"/>
<rect x="510" y="90" width="40" height="40" fill="#6580cd" stroke="#ffffff" stroke-width="1"/>
<rect x="230" y="130" width="40" height="40" fill="#6580cd" stroke="#ffffff" stroke-width="1"/>
<rect x="270" y="130" width="40" height="40" fill="#dbeafe" stroke="#ffffff" stroke-width="1"/>
<rect x="310" y="130" width="40" height="40" fill="#94aae0" stroke="#ffffff" stroke-width="1"/>
<rect x="350" y="130" width="40" height="40" fill="#4d6ac3" stroke="#ffffff" stroke-width="1"/>
<rect x="390" y="130" width="40" height="40" fill="#c3d5f4" stroke="#ffffff" stroke-width="1"/>
<rect x="430" y="130" width="40" height="40" fill="#7c95d6" stroke="#ffffff" stroke-width="1"/>
<rect x="470" y="130" width="40" height="40" fill="#3655b9" stroke="#ffffff" stroke-width="1"/>
<rect x="510" y="130" width="40" height="40" fill="#acc0ea" stroke="#ffffff" stroke-width="1"/>
<rect x="230" y="170" width="40" height="40" fill="#acc0ea" stroke="#ffffff" stroke-width="1"/>
<rect x="270" y="170" width="40" height="40" fill="#6580cd" stroke="#ffffff" stroke-width="1"/>
<rect x="310" y="170" width="40" height="40" fill="#dbeafe" stroke="#ffffff" stroke-width="1"/>
<rect x="350" y="170" width="40" height="40" fill="#94aae0" stroke="#ffffff" stroke-width="1"/>
<rect x="390" y="170" width="40" height="40" fill="#4d6ac3" stroke="#ffffff" stroke-width="1"/>
<rect x="430" y="170" width="40" height="40" fill="#c3d5f4" stroke="#ffffff" stroke-width="1"/>
<rect x="470" y="170" width="40" height="40" fill="#7c95d6" stroke="#ffffff" stroke-width="1"/>
<rect x="510" y="170" width="40" height="40" fill="#3655b9" stroke="#ffffff" stroke-width="1"/>
<rect x="230" y="210" width="40" height="40" fill="#3655b9" stroke="#ffffff" stroke-width="1"/>
<rect x="270" y="210" width="40" height="40" fill="#acc0ea" stroke="#ffffff" stroke-width="1"/>
<rect x="310" y="210" width="40" height="40" fill="#6580cd" stroke="#ffffff" stroke-width="1"/>
<rect x="350" y="210" width="40" height="40" fill="#dbeafe" stroke="#ffffff" stroke-width="1"/>
<rect x="390" y="210" width="40" height="40" fill="#94aae0" stroke="#ffffff" stroke-width="1"/>
<rect x="430" y="210" width="40" height="40" fill="#4d6ac3" stroke="#ffffff" stroke-width="1"/>
<rect x="470" y="210" width="40" height="40" fill="#c3d5f4" stroke="#ffffff" stroke-width="1"/>
<rect x="510" y="210" width="40" height="40" fill="#7c95d6" stroke="#ffffff" stroke-width="1"/>
<rect x="230" y="250" width="40" height="40" fill="#7c95d6" stroke="#ffffff" stroke-width="1"/>
<rect x="270" y="250" width="40" height="40" fill="#3655b9" stroke="#ffffff" stroke-width="1"/>
<rect x="310" y="250" width="40" height="40" fill="#acc0ea" stroke="#ffffff" stroke-width="1"/>
<rect x="350" y="250" width="40" height="40" fill="#6580cd" stroke="#ffffff" stroke-width="1"/>
<rect x="390" y="250" width="40" height="40" fill="#dbeafe" stroke="#ffffff" stroke-width="1"/>
<rect x="430" y="250" width="40" height="40" fill="#94aae0" stroke="#ffffff" stroke-width="1"/>
<rect x="470" y="250" width="40" height="40" fill="#4d6ac3" stroke="#ffffff" stroke-width="1"/>
<rect x="510" y="250" width="40" height="40" fill="#c3d5f4" stroke="#ffffff" stroke-width="1"/>
<rect x="230" y="290" width="40" height="40" fill="#c3d5f4" stroke="#ffffff" stroke-width="1"/>
<rect x="270" y="290" width="40" height="40" fill="#7c95d6" stroke="#ffffff" stroke-width="1"/>
<rect x="310" y="290" width="40" height="40" fill="#3655b9" stroke="#ffffff" stroke-width="1"/>
<rect x="350" y="290" width="40" height="40" fill="#acc0ea" stroke="#ffffff" stroke-width="1"/>
<rect x="390" y="290" width="40" height="40" fill="#6580cd" stroke="#ffffff" stroke-width="1"/>
<rect x="430" y="290" width="40" height="40" fill="#dbeafe" stroke="#ffffff" stroke-width="1"/>
<rect x="470" y="290" width="40" height="40" fill="#94aae0" stroke="#ffffff" stroke-width="1"/>
<rect x="510" y="290" width="40" height="40" fill="#4d6ac3" stroke="#ffffff" stroke-width="1"/>
<rect x="230" y="330" width="40" height="40" fill="#4d6ac3" stroke="#ffffff" stroke-width="1"/>
<rect x="270" y="330" width="40" height="40" fill="#c3d5f4" stroke="#ffffff" stroke-width="1"/>
<rect x="310" y="330" width="40" height="40" fill="#7c95d6" stroke="#ffffff" stroke-width="1"/>
<rect x="350" y="330" width="40" height="40" fill="#3655b9" stroke="#ffffff" stroke-width="1"/>
<rect x="390" y="330" width="40" height="40" fill="#acc0ea" stroke="#ffffff" stroke-width="1"/>
<rect x="430" y="330" width="40" height="40" fill="#6580cd" stroke="#ffffff" stroke-width="1"/>
<rect x="470" y="330" width="40" height="40" fill="#dbeafe" stroke="#ffffff" stroke-width="1"/>
<rect x="510" y="330" width="40" height="40" fill="#94aae0" stroke="#ffffff" stroke-width="1"/>
<rect x="230" y="370" width="40" height="40" fill="#94aae0" stroke="#ffffff" stroke-width="1"/>
<rect x="270" y="370" width="40" height="40" fill="#4d6ac3" stroke="#ffffff" stroke-width="1"/>
<rect x="310" y="370" width="40" height="40" fill="#c3d5f4" stroke="#ffffff" stroke-width="1"/>
<rect x="350" y="370" width="40" height="40" fill="#7c95d6" stroke="#ffffff" stroke-width="1"/>
<rect x="390" y="370" width="40" height="40" fill="#3655b9" stroke="#ffffff" stroke-width="1"/>
<rect x="430" y="370" width="40" height="40" fill="#acc0ea" stroke="#ffffff" stroke-width="1"/>
<rect x="470" y="370" width="40" height="40" fill="#6580cd" stroke="#ffffff" stroke-width="1"/>
<rect x="510" y="370" width="40" height="40" fill="#dbeafe" stroke="#ffffff" stroke-width="1"/>
<text x="230" y="80" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">8×8 のテクスチャ。UV は (0,0) が左上、(1,1) が右下</text>
<rect x="310" y="290" width="40" height="40" fill="none" stroke="#e5aa28" stroke-width="5" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.0687;0.0690;0.3308;0.3310;1.0000" values="0;0;1;1;0;0"/></rect>
<circle cx="326.0" cy="314.0" r="7" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.0687;0.0690;0.3308;0.3310;1.0000" values="0;0;1;1;0;0"/></circle>
<rect x="390" y="130" width="40" height="40" fill="none" stroke="#e5aa28" stroke-width="5" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.3308;0.3310;0.5928;0.5931;1.0000" values="0;0;1;1;0;0"/></rect>
<circle cx="406.0" cy="154.0" r="7" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.3308;0.3310;0.5928;0.5931;1.0000" values="0;0;1;1;0;0"/></circle>
<rect x="510" y="370" width="40" height="40" fill="none" stroke="#e5aa28" stroke-width="5" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.5928;0.5931;1.0000" values="0;0;1;1"/></rect>
<circle cx="527.6" cy="387.6" r="7" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.5928;0.5931;1.0000" values="0;0;1;1"/></circle>
<text x="390" y="430" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">三角形の内側の点には、UV が補間されて届く<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.0687;0.0690;1.0000" values="1;1;0;0"/></text>
<text x="390" y="430" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">UV (0.30, 0.70) × 8 = (2.40, 5.60) → テクセル (2, 5)<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.0687;0.0690;0.3308;0.3310;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="430" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">UV (0.55, 0.20) × 8 = (4.40, 1.60) → テクセル (4, 1)<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.3308;0.3310;0.5928;0.5931;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="430" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">UV (0.93, 0.93) × 8 = (7.44, 7.44) → テクセル (7, 7)<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.5928;0.5931;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:uv-sampling:end -->

## よくあるミス

??? failure "メッシュが表示されない"
    巻き順（CW が表）、`FrontCounterClockwise`、入力レイアウト、`stride`、インデックスの型（`R16_UINT` / `R32_UINT`）を確認します。

??? failure "テクスチャが、上下逆になる"
    UV の原点の違い（DX は左上）です。`v = 1 - v` で直します。

??? failure "入力レイアウトの作成が失敗する"
    頂点シェーダーの入力と、セマンティクス・フォーマットが一致していません。

??? failure "テクスチャが、ぼやける・ちらつく"
    ミップマップとフィルター（`MIN_MAG_MIP_LINEAR`、異方性）を確認します。

??? failure "色が、暗い・明るすぎる"
    sRGB の扱い（色は sRGB、法線マップなどは、sRGB にしない）を確認します。

??? failure "毎フレーム、バッファを作り直して遅い"
    一度作って、使い回す。動くなら `DYNAMIC` + `Map` で更新します。

## これだけ覚える

!!! abstract "まとめ"
    - [x] メッシュは頂点バッファ + インデックスバッファ。入力レイアウトでシェーダーとつなぐ
    - [x] 巻き順は CW が表。UV は DX が左上原点（OpenGL 系は `v = 1 - v`）
    - [x] 変わらないものは `IMMUTABLE`、毎フレーム変わるものは`DYNAMIC`
    - [x] サンプラーは、標準はトライリニア + WRAP。斜めの面は異方性。ミップマップで遠くのちらつきを消す
    - [x] 本番は、独自の軽い形式に変換。同じ物の大量描画はインスタンシング

## 関連ページ

- [3D ゲーム（目次）](index.md)
- [法線とライティング](lighting-normals.md)
- [深度とカリング](depth-culling.md)
- [スキニングとアニメーション](skinning-animation.md)
