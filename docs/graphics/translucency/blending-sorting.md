---
title: ブレンドとソート
tags:
  - 描画
---

# ブレンドとソート

半透明の基本は、<strong>「今から描く色（ソース）」と「すでに画面にある色（デスティネーション）」を、アルファで混ぜる</strong>ことです。このページでは、**ブレンドの式・DirectX 11 のブレンド ステート・加算ブレンドと乗算ブレンドの使い分け・ソートの方法と限界・乗算済みアルファ**を説明します。

!!! tip "ポイント"
    - <strong>通常のアルファ ブレンド</strong>：<strong>結果 ＝ ソース × α ＋ デスティネーション × (1 − α)</strong>。
    - <strong>深度テストは ON、深度書き込みは OFF</strong>（半透明どうしが、互いを隠さないように）。
    - <strong>奥から手前</strong>の順に描く（<strong>Back-to-Front</strong>）。<strong>順序を逆にすると、色が変わる</strong>。
    - <strong>加算ブレンド</strong>は<strong>順序に依存しない</strong>（光・炎・魔法）。<strong>乗算ブレンド</strong>も順序に依存しない（影・色ガラス）。
    - <strong>ソートの単位はオブジェクト</strong>。<strong>三角形単位で並べない限り、交差・自己重なりで破綻</strong>。
    - <strong>乗算済みアルファ</strong>にすると、<strong>ブレンドの式が統一され、縁のにじみも減る</strong>。

## アルファ ブレンドの式

**ソース色 `C_s`**（今描く）、**ソース アルファ `α_s`**、**デスティネーション色 `C_d`**（すでにある）とします。

<div class="formula">C_out = C_s · α_s + C_d · (1 − α_s)</div>

| 記号 | 意味 |
| --- | --- |
| **C_s** | **今描こうとしている色** |
| **α_s** | **今の不透明度**（0 で完全に透明、1 で不透明） |
| **C_d** | **画面（レンダー ターゲット）にある色** |

**α が 0.5 なら、半分ずつ混ざり**ます。<strong>この式は「後から描いた物ほど、手前にある」</strong>ことを前提にしています。

### 順序で結果が変わる

**赤（α = 0.5）と青（α = 0.5）を、白い背景に重ねる**場合を考えます。

| 順序 | 結果 |
| --- | --- |
| **赤 → 青**（青が手前） | **青っぽい紫** |
| **青 → 赤**（赤が手前） | **赤っぽい紫** |

**どちらが手前か**が、**見た目を決める**ので、**奥の物から先に描く**必要があります。

## DirectX 11 のブレンド ステート

```cpp
D3D11_BLEND_DESC blend_desc = {};
blend_desc.RenderTarget[0].BlendEnable = TRUE;
blend_desc.RenderTarget[0].SrcBlend = D3D11_BLEND_SRC_ALPHA;
blend_desc.RenderTarget[0].DestBlend = D3D11_BLEND_INV_SRC_ALPHA;
blend_desc.RenderTarget[0].BlendOp = D3D11_BLEND_OP_ADD;
blend_desc.RenderTarget[0].SrcBlendAlpha = D3D11_BLEND_ONE;
blend_desc.RenderTarget[0].DestBlendAlpha = D3D11_BLEND_INV_SRC_ALPHA;
blend_desc.RenderTarget[0].BlendOpAlpha = D3D11_BLEND_OP_ADD;
blend_desc.RenderTarget[0].RenderTargetWriteMask = D3D11_COLOR_WRITE_ENABLE_ALL;
device->CreateBlendState(&blend_desc, &alpha_blend_state);

D3D11_DEPTH_STENCIL_DESC depth_desc = {};
depth_desc.DepthEnable = TRUE;
depth_desc.DepthWriteMask = D3D11_DEPTH_WRITE_MASK_ZERO;
depth_desc.DepthFunc = D3D11_COMPARISON_LESS;
device->CreateDepthStencilState(&depth_desc, &transparent_depth_state);
```

| 項目 | 設定 | 意味 |
| --- | --- | --- |
| **`SrcBlend`** | `SRC_ALPHA` | **ソースの色に、ソースのアルファを掛ける** |
| **`DestBlend`** | `INV_SRC_ALPHA` | **デスティネーションに、(1 − ソースのアルファ) を掛ける** |
| **`BlendOp`** | `ADD` | **足す** |
| **`DepthWriteMask`** | `ZERO` | **深度を書かない**（半透明が、後の半透明を隠さない） |
| **`DepthFunc`** | `LESS` | **深度テストは行う**（不透明の後ろにある物は描かない） |

**深度書き込みを ON のままにする**と、**手前の半透明が、奥の半透明の描画を妨げ**ます（**奥が、描かれなくなる**）。

### ブレンドの種類

| 種類 | `SrcBlend` / `DestBlend` | 式 | 用途 |
| --- | --- | --- | --- |
| <strong>通常（アルファ）</strong> | `SRC_ALPHA` / `INV_SRC_ALPHA` | `C_s·α + C_d·(1−α)` | ガラス・水・UI |
| **加算** | `SRC_ALPHA` / `ONE` | `C_s·α + C_d` | 炎・光・魔法・爆発 |
| <strong>加算（アルファなし）</strong> | `ONE` / `ONE` | `C_s + C_d` | 明るい光の粒 |
| **乗算** | `ZERO` / `SRC_COLOR` | `C_d · C_s` | 影・色付きガラス・暗くする |
| **乗算済みアルファ** | `ONE` / `INV_SRC_ALPHA` | `C_s + C_d·(1−α)` | 通常の、安定した方式 |

**加算と乗算は、順序に依存しない**（足し算・掛け算は、交換できる）ので、**ソートが不要**です。**炎・光の粒・影**は、**この性質を利用**して**ソートなしで描ける**ことが多いです。

## 乗算済みアルファ

**色にあらかじめアルファを掛けて保存**しておく方式です（**Premultiplied Alpha**）。

<div class="formula">C_s' = C_s · α_s　（保存する色）　、　C_out = C_s' + C_d · (1 − α_s)</div>

| 利点 | 内容 |
| --- | --- |
| **式が簡単** | **ソースに掛け算が不要**（`ONE`） |
| **加算と通常を、1 つのブレンドで表せる** | **α を 0 にすれば加算**（`C_s' + C_d`）になる |
| **縁のにじみが少ない** | **テクスチャの縁**で、**背景の色（黒や白）が混ざる**問題が**起きにくい** |
| **ミップ・フィルタが正しい** | **縮小・補間**しても、**透明な部分の色に引きずられない** |

**ストレート アルファ**（通常の画像）は、**完全に透明な画素の RGB が不定**で、**縮小・補間時に、縁に、白や黒の線（ハロー）が出ます**。**乗算済みアルファのテクスチャ**を使うと、**これが起きません**。

<!-- fig:alpha-sort-order:begin -->

<svg class="fig illust motion" data-fig="alpha-sort-order" viewBox="0 0 780 390" role="img"><rect x="0" y="0" width="780" height="390" rx="14" fill="#ffffff"/>
<defs><marker id="arr-alpha-sort-order" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
<mask id="as-mask-1-1" maskUnits="userSpaceOnUse" x="420" y="84" width="300" height="220"><rect x="420" y="84" width="300" height="220" fill="#ffffff"/>
<rect x="532" y="168" width="130" height="130" fill="#000000"/>
</mask>
<mask id="as-mask-1-2" maskUnits="userSpaceOnUse" x="420" y="84" width="300" height="220"><rect x="420" y="84" width="300" height="220" fill="#ffffff"/>
<rect x="532" y="168" width="130" height="130" fill="#000000"/>
<rect x="486" y="134" width="130" height="130" fill="#000000"/>
</mask>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">半透明は奥から手前の順に描く。順番を間違えると、透けなくなる</text>
<text x="40" y="66" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937">正しい順:奥 → 中 → 手前</text>
<rect x="40" y="84" width="300" height="220" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<circle cx="290" cy="116" r="20" fill="none" stroke="#cbd5e1" stroke-width="2"/>
<g opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;1.0000" values="0;0;1;1"/><rect x="60" y="100" width="130" height="130" fill="#e5484d" fill-opacity="0.55" stroke="#e5484d" stroke-width="1.5"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2779;0.2783;1.0000" values="0;0;1;1"/><rect x="106" y="134" width="130" height="130" fill="#2ea043" fill-opacity="0.55" stroke="#2ea043" stroke-width="1.5"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4692;0.4696;1.0000" values="0;0;1;1"/><rect x="152" y="168" width="130" height="130" fill="#2563eb" fill-opacity="0.55" stroke="#2563eb" stroke-width="1.5"/>
</g>
<text x="40" y="326" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">1 番目:奥（赤） を描く<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;0.2779;0.2783;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="326" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">2 番目:中（緑） を描く<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2779;0.2783;0.4692;0.4696;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="326" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">3 番目:手前（青） を描く<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4692;0.4696;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="420" y="66" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937">間違った順:手前 → 中 → 奥（深度を書く）</text>
<rect x="420" y="84" width="300" height="220" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<circle cx="670" cy="116" r="20" fill="none" stroke="#cbd5e1" stroke-width="2"/>
<g opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;1.0000" values="0;0;1;1"/><rect x="532" y="168" width="130" height="130" fill="#2563eb" fill-opacity="0.55" stroke="#2563eb" stroke-width="1.5"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2779;0.2783;1.0000" values="0;0;1;1"/><g mask="url(#as-mask-1-1)"><rect x="486" y="134" width="130" height="130" fill="#2ea043" fill-opacity="0.55" stroke="#2ea043" stroke-width="1.5"/>
</g>
</g>
<g opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4692;0.4696;1.0000" values="0;0;1;1"/><g mask="url(#as-mask-1-2)"><rect x="440" y="100" width="130" height="130" fill="#e5484d" fill-opacity="0.55" stroke="#e5484d" stroke-width="1.5"/>
</g>
</g>
<text x="420" y="326" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">1 番目:手前（青） を描く<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;0.2779;0.2783;1.0000" values="0;0;1;1;0;0"/></text>
<text x="420" y="326" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">2 番目:中（緑） を描く<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2779;0.2783;0.4692;0.4696;1.0000" values="0;0;1;1;0;0"/></text>
<text x="420" y="326" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">3 番目:奥（赤） を描く<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4692;0.4696;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="40" y="356" text-anchor="start" style="font-size:14px;font-weight:700;fill:#2ea043" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.6692;0.6696;1.0000" values="1;1;0;0"/></text>
<text x="40" y="356" text-anchor="start" style="font-size:14px;font-weight:700;fill:#2ea043" opacity="0">左:重なりに赤・緑・青が全部透けて見える。<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.6692;0.6696;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="420" y="356" text-anchor="start" style="font-size:14px;font-weight:700;fill:#e5484d" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.6692;0.6696;1.0000" values="1;1;0;0"/></text>
<text x="420" y="356" text-anchor="start" style="font-size:14px;font-weight:700;fill:#e5484d" opacity="0">右:手前が先に深度を書くので、奥の物が消えて透けない。<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.6692;0.6696;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:alpha-sort-order:end -->

## ソート

**奥から手前**の順に描くため、**半透明のオブジェクトを、カメラからの距離で並べ替えます**。

```cpp
struct TransparentDraw {
  float distance_squared;
  uint32_t draw_index;
};

std::vector<TransparentDraw> sorted;
for (uint32_t i = 0; i < transparent_draws.size(); ++i) {
  Vector3 to_object = transparent_draws[i].center - camera_position;
  sorted.push_back({to_object.LengthSquared(), i});
}
std::sort(sorted.begin(), sorted.end(),
          [](const TransparentDraw& a, const TransparentDraw& b) {
            return a.distance_squared > b.distance_squared;
          });
```

| 点 | 説明 |
| --- | --- |
| **`LengthSquared`** | **距離の比較だけ**なので、**平方根は不要** |
| <strong>降順（遠い順）</strong> | **一番遠い物から**描く |
| **距離の基準** | **オブジェクトの中心**（または、<strong>カメラの前方ベクトルへの射影（深度）</strong>）。**射影のほうが、横に並んだ物の順序が安定** |
| **ソートのキー** | **透明度の種類（加算など順序不要のもの）を分けて**、**通常のものだけソート** |

<strong>カメラの前方ベクトルへの射影（ビュー空間の z）</strong>で**並べる**と、**カメラが回転しても、順序が安定**します。

```cpp
float view_depth = Vector3::Dot(center - camera_position, camera_forward);
```

### ソートの限界

| 問題 | 内容 | 対策 |
| --- | --- | --- |
| **オブジェクトが交差** | **1 つの順序では、表せない**（互いに食い込む） | **分割する**・**OIT** |
| **自己重なり** | **1 つのメッシュの手前の面と奥の面**（ガラス瓶） | <strong>背面を先、前面を後に描く（2 パス）</strong> |
| **大きな物体** | **中心では、順序を決められない** | **分割する**・**OIT** |
| **パーティクル** | **数が多い**ので、**ソートが重い** | **GPU ソート・加算ブレンドで回避** |
| **ポップ** | **カメラが動くと、順序が突然入れ替わり、見た目が変わる** | **中心の取り方・OIT** |

### 自己重なり（2 パス）

**ガラスの瓶**のように、**閉じたメッシュ**は、**背面（奥の面）を先に描き、前面（手前の面）を後に描く**と、**正しい順序**に近づきます。

```cpp
context->RSSetState(cull_front_state);
DrawMesh();
context->RSSetState(cull_back_state);
DrawMesh();
```

| パス | カリング | 描く面 |
| --- | --- | --- |
| **1 回目** | **前面カリング** | <strong>奥の面（背面）</strong> |
| **2 回目** | **背面カリング** | <strong>手前の面（前面）</strong> |

## 深度の読み取り（ソフト パーティクル）

**パーティクルの板**が、**地面や壁と交差する所で、硬い線**が出ます。**シーンの深度を読んで、近いほど透明にする**と、**なじみます**（**ソフト パーティクル**）。

```hlsl
float scene_depth = LinearDepth(depth_texture.Load(int3(input.position.xy, 0)).r);
float particle_depth = LinearDepth(input.position.z);
float fade = saturate((scene_depth - particle_depth) / fade_distance);
color.a *= fade;
```

| 点 | 説明 |
| --- | --- |
| **`scene_depth`** | **不透明な物の深度**（深度バッファを SRV として読む） |
| **`particle_depth`** | **パーティクル自身の深度** |
| **`fade_distance`** | **この距離で、完全に不透明に** |
| **要件** | **深度バッファを、読み取りと深度テストで、同時に使えない**ので、**深度のコピー**（または読み取り専用 DSV）が要る |

## ブレンド順序の決め方（まとめ）

| 物 | ブレンド | ソート |
| --- | --- | --- |
| **ガラス・水面** | 通常 | **必要** |
| **炎・爆発・魔法** | 加算 | **不要** |
| **煙** | 通常（または乗算済み） | **必要** |
| <strong>影の板（ブロブ）</strong> | 乗算 | **不要** |
| **UI** | 通常 | **描画順を、レイヤーで決める** |

## よくあるミス

??? failure "半透明の深度書き込みを ON にして、奥の半透明が描かれない"
    **深度書き込みを OFF**（`DepthWriteMask = ZERO`）にする。

??? failure "半透明を、手前から奥の順に描いて、色が逆になる"
    **奥から手前**の順に**ソート**する。

??? failure "テクスチャの縁に、白や黒の縁取りが出る"
    **乗算済みアルファ**にする（または、**透明部分の RGB を、周囲の色で埋める**）。

??? failure "ガラス瓶の内側が、外側より手前に描かれる"
    **背面 → 前面の 2 パス**で描く。

??? failure "パーティクルが、地面との交差で、くっきり切れる"
    **ソフト パーティクル**（深度でフェード）。

## これだけ覚える

!!! abstract "まとめ"
    - [x] アルファ ブレンド ＝ <strong>C_s·α ＋ C_d·(1−α)</strong>。<strong>順序で結果が変わる</strong>
    - [x] <strong>深度テスト ON・深度書き込み OFF</strong>。<strong>奥から手前</strong>に描く
    - [x] <strong>加算・乗算ブレンド</strong>は<strong>順序に依存しない</strong>（ソート不要）
    - [x] ソートは<strong>オブジェクト単位</strong>。<strong>交差・自己重なりは破綻</strong>（OIT・分割で対処）
    - [x] <strong>乗算済みアルファ</strong>で<strong>縁のにじみを防ぐ</strong>。<strong>ソフト パーティクル</strong>で<strong>交差をなじませる</strong>

## 参考

- Microsoft, "Blend State"（Direct3D 11）
- Porter, Duff, "Compositing Digital Images"（SIGGRAPH 1984）

## 関連ページ

- [半透明](index.md)
- [アルファ テスト](alpha-test.md)
- [OIT](oit.md)
- [オーバードロー（最適化）](../../rendering/overdraw.md)
