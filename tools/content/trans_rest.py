import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import pg  # noqa: E402

PORTER = '''Porter, Duff, "Compositing Digital Images", SIGGRAPH 1984（アルファ合成の原典）'''
SMITH = '''Smith, "Image Compositing Fundamentals", Microsoft Technical Memo 4, 1995（乗算済みアルファ）'''
LORACH = '''Lorach, "Soft Particles", NVIDIA White Paper, 2007'''
D3D11_BLEND = '''Microsoft Learn, "D3D11_RENDER_TARGET_BLEND_DESC"（`SrcBlend`、`DestBlend`、`BlendOp`）'''
RTR = '''Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（透明、屈折、フレネルの章）'''
CARPENTER = '''Carpenter, "The A-buffer, an Antialiased Hidden Surface Method", SIGGRAPH 1984'''
EVERITT = '''Everitt, "Interactive Order-Independent Transparency", NVIDIA White Paper, 2001（デプス ピーリング）'''
BAVOIL = '''Bavoil, Myers, "Order Independent Transparency with Dual Depth Peeling", NVIDIA White Paper, 2008'''
YANG = '''Yang, Hensley, Grün, Thibieroz, "Real-Time Concurrent Linked List Construction on the GPU", Computer Graphics Forum (Eurographics Symposium on Rendering 2010)'''
MCGUIRE = '''McGuire, Bavoil, "Weighted Blended Order-Independent Transparency", Journal of Computer Graphics Techniques, Vol. 2, No. 2, 2013'''
ENDERTON = '''Enderton, Sintorn, Shirley, Luebke, "Stochastic Transparency", Symposium on Interactive 3D Graphics and Games 2010'''
SALVI = '''Salvi, Montgomery, Lefohn, "Adaptive Transparency", High-Performance Graphics 2011'''
SALVI14 = '''Salvi, Vaidyanathan, "Multi-Layer Alpha Blending", Symposium on Interactive 3D Graphics and Games 2014'''
MUNSTERMANN = '''Münstermann, Krumpen, Klein, Peters, "Moment-Based Order-Independent Transparency", High-Performance Graphics 2018'''
WYMAN16 = '''Wyman, "Exploring and Expanding the Continuum of OIT Algorithms", High-Performance Graphics 2016'''
SOUSA = '''Sousa, "Generic Refraction Simulation", GPU Gems 2, Chapter 19, 2005'''
WYMAN05 = '''Wyman, "An Approximate Image-Space Approach for Interactive Refraction", ACM Transactions on Graphics (SIGGRAPH 2005)'''
SCHLICK = '''Schlick, "An Inexpensive BRDF Model for Physically-based Rendering", Computer Graphics Forum, Vol. 13, No. 3, 1994'''
WALTER = '''Walter, Marschner, Li, Torrance, "Microfacet Models for Refraction through Rough Surfaces", Eurographics Symposium on Rendering 2007（粗い面での屈折）'''
D3D11_UAV = '''Microsoft Learn, "RWStructuredBuffer / RWByteAddressBuffer"（HLSL のバッファ）と "InterlockedExchange"'''

# ================================================================ blending-sorting
pg.Dedup("translucency/blending-sorting/blend-state.md")
pg.Add("translucency/blending-sorting/blend-state.md", '''
## ブレンドの式

半透明の描画は、**これから描く色（ソース）**と、**すでに画面に、ある色（デスティネーション）**を、**式**で、混ぜます。DirectX 11 の、ブレンド ステートは、この式の、**部品**を、指定します。

```text
結果 = ソース × SrcBlend  [演算 BlendOp]  デスティネーション × DestBlend
```

| 部品 | 意味 | よく使う値 |
| --- | --- | --- |
| `SrcBlend` | ソース（これから描く色）に、掛ける係数 | `SRC_ALPHA`、`ONE` |
| `DestBlend` | デスティネーション（画面の色）に、掛ける係数 | `INV_SRC_ALPHA`、`ONE` |
| `BlendOp` | 2 つを、どう組み合わせるか | `ADD`（足す）、`MAX`、`MIN` |

## 代表的なブレンド

### ① 通常の、アルファ ブレンド

```text
結果 = ソース × α  +  デスティネーション × (1 − α)
```

ガラス、煙、フェードする物の、**標準**です。

```cpp
D3D11_RENDER_TARGET_BLEND_DESC& rt = blend.RenderTarget[0];
rt.BlendEnable = TRUE;
rt.SrcBlend = D3D11_BLEND_SRC_ALPHA;
rt.DestBlend = D3D11_BLEND_INV_SRC_ALPHA;
rt.BlendOp = D3D11_BLEND_OP_ADD;
rt.SrcBlendAlpha = D3D11_BLEND_ONE;                // アルファ チャンネルの合成
rt.DestBlendAlpha = D3D11_BLEND_INV_SRC_ALPHA;
rt.BlendOpAlpha = D3D11_BLEND_OP_ADD;
rt.RenderTargetWriteMask = D3D11_COLOR_WRITE_ENABLE_ALL;
```

### ② 加算ブレンド

```text
結果 = ソース × α  +  デスティネーション × 1
```

火、光、魔法の、輝きなど、**明るさを、足していく**表現です。**順序に、依存しない**（足し算は、順序を、入れ替えても同じ）ので、**ソートが不要**です。

```cpp
rt.SrcBlend = D3D11_BLEND_SRC_ALPHA;
rt.DestBlend = D3D11_BLEND_ONE;                    // 画面の色を、そのまま残して、足す
rt.BlendOp = D3D11_BLEND_OP_ADD;
```

加算ブレンドは、**重なるほど、明るく**なり、**白に近づきます**。HDR で、**明るさの上限が、無い**場合は、**ブルームで、光る**表現に、つながります（[Bloom](../../postprocess/bloom/index.md)）。

### ③ 乗算ブレンド

```text
結果 = ソース × デスティネーション
```

**色付きガラス**、**影**、**汚れ**のように、**背景の色を、暗くする**表現です。

```cpp
rt.SrcBlend = D3D11_BLEND_ZERO;
rt.DestBlend = D3D11_BLEND_SRC_COLOR;              // 画面の色 × ソースの色
```

乗算も、**順序に依存しません**（掛け算は、順序を入れ替えても、同じ）。

### ④ 乗算済みアルファ

```text
結果 = ソース（すでに α が掛かっている）  +  デスティネーション × (1 − α)
```

アルファ ブレンドの、**ソースに、あらかじめ、アルファを、掛けておく**形です（[Premultiplied Alpha](premultiplied.md)）。

```cpp
rt.SrcBlend = D3D11_BLEND_ONE;                     // ソースには、掛けない（掛け済み）
rt.DestBlend = D3D11_BLEND_INV_SRC_ALPHA;
```

## 比較

| ブレンド | SrcBlend | DestBlend | 向く表現 | 順序依存 |
| --- | --- | --- | --- | --- |
| アルファ | SRC_ALPHA | INV_SRC_ALPHA | ガラス、フェード | **依存する** |
| 乗算済みアルファ | ONE | INV_SRC_ALPHA | 煙 + 光を、1 つのレイヤーで | 依存する |
| 加算 | SRC_ALPHA（または ONE） | ONE | 火、光、魔法 | **しない** |
| 乗算 | ZERO | SRC_COLOR | 色ガラス、影 | しない |
| 最大値（MAX） | ONE | ONE（`BlendOp = MAX`） | 重なっても、強い方だけ残す（[Trampled Grass](../../terrain/vegetation/trample.md)） | しない |

## 深度の設定との組み合わせ

半透明は、**深度テストは、行い、深度の書き込みは、しない**のが、基本です。

```cpp
D3D11_DEPTH_STENCIL_DESC ds = {};
ds.DepthEnable = TRUE;                                  // 不透明な物の後ろは、隠す
ds.DepthWriteMask = D3D11_DEPTH_WRITE_MASK_ZERO;        // 半透明は、深度を書かない
ds.DepthFunc = D3D11_COMPARISON_LESS_EQUAL;
device->CreateDepthStencilState(&ds, &transparent_depth_state);
```

| 設定 | 理由 |
| --- | --- |
| テスト：有効 | 不透明な物の、**後ろ**にある、半透明は、描かない |
| 書き込み：無効 | 半透明が、深度を書くと、**その後ろの、半透明が、隠れて**しまう |

## 描画の順番

半透明は、**不透明の後**に、描きます。

```text
① 不透明を描く（深度を書く）
② 半透明を描く（深度テストのみ、書き込みなし）、ソートして、奥から手前へ
③ ポストプロセス
```

半透明の中の、順序は、**ソート**で決めます（[Sorting](sorting.md)）。

## 複数の、レンダー ターゲットと、ブレンド

レンダー ターゲットごとに、**別のブレンド**を、指定できます（`IndependentBlendEnable = TRUE`）。OIT の、実装（[WBOIT](../oit/wboit.md)）で、**2 つのターゲット**に、別々の、ブレンドを、使います。

```cpp
blend.IndependentBlendEnable = TRUE;
blend.RenderTarget[0] = accum_blend;         // 加算（WBOIT の、積算）
blend.RenderTarget[1] = reveal_blend;        // 乗算風（WBOIT の、透過度）
```

''', before="## よくあるミス")
pg.Refs("translucency/blending-sorting/blend-state.md", [PORTER, SMITH, D3D11_BLEND, RTR])

pg.Dedup("translucency/blending-sorting/premultiplied.md")
pg.Add("translucency/blending-sorting/premultiplied.md", '''
## ストレート アルファと、乗算済みアルファ

画像の色と、アルファの、持ち方に、**2 通り**あります。

| 形式 | 保存する値 | 例（赤、アルファ 0.5） |
| --- | --- | --- |
| **ストレート**（非乗算） | 色（アルファを、掛けていない）と、アルファ | `(1.0, 0.0, 0.0, 0.5)` |
| **乗算済み**（Premultiplied） | **色 × アルファ**と、アルファ | `(0.5, 0.0, 0.0, 0.5)` |

乗算済みは、**色の値に、アルファが、すでに掛かっている**形です（Smith、1995）。

## ブレンド式の違い

| 形式 | ブレンドの式 |
| --- | --- |
| ストレート | `結果 = C × α + D × (1 − α)` |
| 乗算済み | `結果 = C' + D × (1 − α)`（`C' = C × α`） |

**乗算済みは、ソースの色に、アルファを、掛ける計算を、省けます**。さらに、**複数の層を、重ねる、合成が、結合法則を、満たします**（**層を、先に、まとめて**、あとで、背景に重ねても、同じ結果になる）。

## なぜ、乗算済みが、よいのか

### ① 縁に、**白や黒の、縁取り**（フリンジ）が、出ない

画像を、**縮小・拡大**（バイリニア補間）するとき、**隣り合う画素の色が、混ざります**。**透明な画素の色**（本当は、見えない色）が、**縁の、不透明な画素と、混ざって**、**縁に、変な色が、にじみます**。

```text
画素 A: 赤、不透明      (1, 0, 0, 1.0)
画素 B: 透明（色は、黒） (0, 0, 0, 0.0)    ← 見えないが、色は、黒として保存されている

ストレートで、50% ずつ補間:  (0.5, 0, 0, 0.5)   ← 色が、暗い赤に（本来は、赤のまま、半透明であるべき）
乗算済みで、50% ずつ補間:    (0.5, 0, 0, 0.5)   ← 乗算済みなら、色 × アルファ が (0.5, 0, 0) で、正しい
```

ストレートでは、補間の結果が、`(0.5, 0, 0)`、アルファが 0.5 で、ブレンドの時に、**さらに、アルファを、掛けて**、`(0.25, 0, 0)` と、**暗く**なります。**縁が、暗くなる**（黒い縁取り）のは、これが原因です。

| 縁の問題 | 原因 |
| --- | --- |
| **黒い縁取り** | 透明な画素の色が、黒（ストレートで、補間が、色と、アルファを、別々に、混ぜる） |
| **白い縁取り** | 透明な画素の色が、白 |

### ② 加算と、アルファ ブレンドを、**1 つの式**で

乗算済みでは、**アルファを、0 にして、色だけを、持たせる**と、**加算ブレンド**に、なります。

```text
結果 = C' + D × (1 − α)
α = 0 のとき:  結果 = C' + D        ← 加算ブレンド
α = 1 のとき:  結果 = C'            ← 不透明
```

**1 つの、ブレンド ステート**で、**煙（アルファ ブレンド）と、火（加算）**を、**同じ、パーティクル システム**で、描けます。**アルファだけを、下げる**（火が、燃え尽きて、暗い煙に、変わる）、といった表現が、**ソート順を、変えずに**、できます。

### ③ ミップマップと、フィルタリング

**ミップマップを、作るとき**も、**ストレートのまま、平均すると、縁が、おかしくなります**。乗算済みで、ミップを作ると、**正しい、結果**になります。

## 乗算済みの、画像を、作る

| 方法 | 内容 |
| --- | --- |
| 画像を、**書き出すとき**に、掛ける | テクスチャを、作るツール（Photoshop、ツール）で、乗算済みに、変換 |
| **読み込み時**に、掛ける | エンジンが、ロード時に、`rgb *= a` を行う（**ミップを作る前**に） |
| **シェーダー**で、掛ける | `color.rgb *= color.a` |

```hlsl
// ストレートの画像を、乗算済みとして、出力する。
float4 c = g_tex.Sample(g_linear_wrap, input.uv);
c.rgb *= c.a;                                    // 乗算済みにする
return c;                                         // ブレンド: SrcBlend = ONE, DestBlend = INV_SRC_ALPHA
```

!!! warning "ミップを作る前に、乗算する"
    画像の、ミップを作るときは、**乗算済みの状態で、縮小**します。ストレートで、ミップを作ってから、シェーダーで、`rgb *= a` しても、**縁の、フリンジは、消えません**（ミップの中で、すでに、色が混ざっている）。**画像ファイルを、作る段階**で、乗算済みに、しておくのが、確実です。

## パーティクルでの、使い方

火と煙を、**1 つの、パーティクル システム**で、描くとき、乗算済みアルファが、**便利**です。

```hlsl
// 火から煙へ、時間とともに、変化する、パーティクル。
float life = particle.age / particle.lifetime;           // 0（生まれた）〜 1（消える）
float3 color = lerp(fire_color, smoke_color, life);       // 色: 火 → 煙
float fire_amount = saturate(1.0 - life * 2.0);           // 前半は、火（光る）
float alpha = lerp(0.0, 0.6, saturate(life * 2.0));       // アルファ: 火のとき 0（加算）、煙のとき、不透明に
// 乗算済み: 色 × アルファ（煙の部分）+ 火の部分は、アルファ 0 で、色だけを足す
float3 premul = smoke_color * alpha + fire_color * fire_amount * 4.0;   // 4.0 は、火の、明るさ（HDR）
return float4(premul, alpha);
```

## ブレンド ステート

```cpp
// 乗算済みアルファ。
D3D11_RENDER_TARGET_BLEND_DESC& rt = blend.RenderTarget[0];
rt.BlendEnable = TRUE;
rt.SrcBlend = D3D11_BLEND_ONE;                    // ソースに、アルファを、掛けない（掛け済み）
rt.DestBlend = D3D11_BLEND_INV_SRC_ALPHA;
rt.BlendOp = D3D11_BLEND_OP_ADD;
rt.SrcBlendAlpha = D3D11_BLEND_ONE;
rt.DestBlendAlpha = D3D11_BLEND_INV_SRC_ALPHA;
rt.BlendOpAlpha = D3D11_BLEND_OP_ADD;
```

## UI（画面の絵）との関係

ユーザー インターフェース（UI）の、画像も、**乗算済み**にする、ライブラリが、多いです（フォント、アイコンの縁が、きれいになる）。**ストレートか、乗算済みか**を、**ライブラリごとに**、確認します。

| 症状 | 原因 |
| --- | --- |
| UI の絵の縁に、黒い線 | ストレートの画像を、乗算済みの、ブレンドで、描いた（または、その逆） |
| UI の絵が、全体に、暗い | 乗算済みの画像を、ストレートの、ブレンドで、描いた（アルファが、二重に、掛かる） |

''', before="## よくあるミス")
pg.Refs("translucency/blending-sorting/premultiplied.md", [SMITH, PORTER, D3D11_BLEND, RTR])

pg.Dedup("translucency/blending-sorting/soft-particles.md")
pg.Add("translucency/blending-sorting/soft-particles.md", '''
## 問題：パーティクルが、地面と、交差して、線が見える

煙や、霧のパーティクルは、**板（ビルボード）**で、描かれます。板が、**地面や壁に、突き刺さる**と、**板と地面の交差線**が、**ぱっきりと**見えます。煙が、**地面に、板が、刺さっている**ように見えて、**不自然**です。

```text
 煙の板
     ╲
      ╲   ← 板が、地面に刺さっている
 ━━━━━━╲━━━━━ 地面
        ╲
         ← 交差した所に、くっきり線が出る
```

## ソフト パーティクル

**ソフト パーティクル**（Lorach、2007）は、**パーティクルの、深度**と、**後ろにある、物の深度**の、**差が、小さい所**（交差に近い所）で、**パーティクルを、透明に、フェード**させる手法です。**交差線が、消え、板が、地面に、なめらかに、溶け込み**ます。

```text
アルファ = 元のアルファ × saturate( (シーン深度 − パーティクル深度) / フェード距離 )
```

| 深度の差 | アルファ |
| --- | --- |
| 0（交差している） | 0（透明） |
| フェード距離の半分 | 半分 |
| フェード距離以上 | 元のまま |

## 実装

深度バッファを、**シェーダー リソース**として、読みます。パーティクルの、描画では、深度の書き込みは、無効なので、**同じ深度バッファを、読み取り専用の、DSV と、SRV の、両方**で使えます（[Color by Water Depth](../../water/shading/depth-color.md)、深度の、読み方）。

```hlsl
Texture2D<float> g_scene_depth : register(t0);

float4 main(PSInput input) : SV_Target {
  float4 color = g_particle_tex.Sample(g_linear_clamp, input.uv) * input.color;

  // ① 後ろにある、物の深度（視点深度）を、読む
  float scene_ndc = g_scene_depth.Load(int3(input.position.xy, 0));
  float scene_depth = LinearizeDepth(scene_ndc);

  // ② このパーティクルの、深度（視点深度）
  float particle_depth = LinearizeDepth(input.position.z);

  // ③ 差に応じて、アルファを、フェードさせる
  float fade = saturate((scene_depth - particle_depth) / g_soft_distance);
  color.a *= fade;
  return color;
}
```

| パラメーター | 目安 | 効果 |
| --- | --- | --- |
| `g_soft_distance` | 0.5〜2 m | **フェードする、深度の範囲**。大きいほど、交差線の、近くから、ゆっくり、透明になる |

ほとんどの、煙や霧では、**パーティクルの、大きさの、半分くらい**の、フェード距離が、使われます。

### 線形の深度で、比べる

深度バッファの値は、**非線形**（近くで、精度が高く、遠くで、粗い）です。**差を取るとき**は、**必ず、線形の、視点深度に、直して**から、引きます。

```hlsl
// 線形の視点深度に直す（通常の射影行列）。
float LinearizeDepth(float d) {
  return near_plane * far_plane / (far_plane - d * (far_plane - near_plane));
}
```

非線形のまま、差を取ると、**遠くで、フェードが、効かなくなったり**、**近くで、効きすぎたり**します。

## 逆方向：パーティクルが、カメラに近すぎる

パーティクルが、**カメラに、近づきすぎる**と、**画面全体を、覆う**ほど、大きくなり、**ブレンドの、コストが、跳ね上がり**、見た目も、うるさいです。**カメラに近いほど、フェードアウト**させます。

```hlsl
float near_fade = saturate((particle_depth - near_fade_start) / near_fade_range);
color.a *= near_fade;
```

## 光る、パーティクルへの、応用

**加算ブレンド**の、パーティクル（火花、光）でも、ソフト パーティクルは、**有効**です。**フェード**を、**アルファではなく、色（明るさ）**に掛けます（加算では、アルファが、色を、決めるため）。

```hlsl
// 加算ブレンド: 色そのものに、フェードを掛ける。
color.rgb *= fade;
```

## 注意点

| 項目 | 内容 |
| --- | --- |
| 深度を、読む | **MSAA** を、使っているとき、深度は、**MSAA の深度**。`Load` で、**サンプルを、指定**して、読む（または、リゾルブした、深度を使う） |
| 同じバッファの、読み書き | 深度を、**読み取り専用**にする（書き込みを、無効にする）。同時に、SRV で読む |
| 水と、同じ原理 | 水面と、地形が、交差する線を、消す（[Shore Foam: Depth Difference](../../water/shore-foam/shore-depth.md)）。**水の、岸の、アルファ**も、同じ式 |
| 解像度 | パーティクルを、**低解像度**で、描くときは、**深度も、縮小して、読む**（縮小する深度は、**最も近い値**で、縮める） |

''', before="## よくあるミス")
pg.Refs("translucency/blending-sorting/soft-particles.md", [LORACH, RTR, D3D11_BLEND, "Microsoft Learn, \"Reading depth-stencil as shader resource\""])

pg.Dedup("translucency/blending-sorting/sorting.md")
pg.Add("translucency/blending-sorting/sorting.md", '''
## なぜ、ソートが、必要か

通常の、アルファ ブレンドは、**順序に、依存**します。**奥の物を、先に、手前の物を、後に**、描かないと、正しい色になりません。

```text
赤いガラス（手前）と、青いガラス（奥）を、通して、背景を見るとき:
  正しい順序:  背景 → 青（奥）→ 赤（手前）   → 赤が、手前に、見える
  逆の順序:    背景 → 赤（手前）→ 青（奥）   → 青が、手前に見える（間違い）
```

順序を、間違えると、**手前と奥が、入れ替わった**ような、見た目になります。**深度の書き込みを、しない**ので、**後から描いた物が、常に、手前に重なる**ためです。

## ソートの、基本

**カメラからの、距離の、遠い順**に、並べて、描きます（**画家のアルゴリズム**）。

```cpp
struct TransparentObject {
  float3 position;       // 代表点（中心）
  float sort_key;        // カメラからの距離（の 2 乗）
  // ...
};

// 毎フレーム、カメラからの距離を計算して、遠い順に、並べる。
for (auto& o : transparent_objects) {
  const float3 d = o.position - camera_position;
  o.sort_key = Dot(d, d);                              // 距離の 2 乗（sqrt は、順序に影響しないので、省く）
}
std::sort(transparent_objects.begin(), transparent_objects.end(),
          [](const auto& a, const auto& b) { return a.sort_key > b.sort_key; });   // 遠い順

for (const auto& o : transparent_objects) Draw(o);       // 遠い物から、描く
```

### 距離か、ビュー空間の、深度か

| キー | 内容 | 向く場面 |
| --- | --- | --- |
| カメラからの**距離** | 位置と、カメラの、直線距離 | 球状の、広がり（爆発、パーティクルの、群れ） |
| ビュー空間の **z 深度** | カメラの**前方向**に、沿った距離 | 平面的な、板（ビルボード、ガラス板） |

板の、パーティクルは、**画面に、平行な面**を持つので、**ビュー空間の z 深度**で、ソートするほうが、**見た目の、前後に、一致**します。

## ソートが、**破綻する**場面

### ① 物体の、内部で、ソートできない

**1 つのメッシュ**（ガラスの瓶、水槽）は、**三角形が、ばらばらの距離**に、あります。物体の、**中心の距離だけ**で、ソートすると、**1 つのメッシュの中の、三角形の順序**が、**描画の順（インデックスの順）**で、決まり、**手前と奥が、逆に重なる**ことがあります。

| 対策 | 内容 |
| --- | --- |
| 2 パスで描く | **裏面（奥側）を、先に**、描き、**表面（手前側）を、あとに**描く。凸な物（瓶、球）で、正しくなる |
| 深度の、事前描画 | 手前の面だけを、深度に書いて、**最前面の、1 層だけ**を、描く |
| メッシュを、分割 | 三角形を、ソートする。重い |

```cpp
// 凸な半透明の物: 裏面 → 表面の、順で、2 回描く。
context->RSSetState(rs_cull_front.Get());     // 表面をカリング（裏面だけ）
Draw(mesh);
context->RSSetState(rs_cull_back.Get());      // 裏面をカリング（表面だけ）
Draw(mesh);
```

### ② 物体同士が、交差している

**2 つの、大きな物体が、互いに、貫通**していると、**どちらが、手前**か、**場所によって違う**ので、**物体単位の、ソートが、成立しません**。

### ③ 大きな物体と、小さな物体

**大きな板**（地面に、広がる、水面）と、**小さなパーティクル**では、**中心の距離で、並べる**と、**小さな物が、大きな物の、手前にあるのに、先に描かれる**ことがあります。**大きな物は、別のパス**で、先に描きます（水は、不透明の後、半透明の前、など）。

### ④ 同じ距離

**距離が、ほぼ同じ**の物が、**フレームごとに、順序が、入れ替わる**と、**ちらつきます**。**安定した、タイブレーク**（物の ID など）を、加えます。

```cpp
// 距離が、同じなら、ID で順序を決める（フレームごとに、順序が揺れない）。
std::sort(objects.begin(), objects.end(), [](const auto& a, const auto& b) {
  if (a.sort_key != b.sort_key) return a.sort_key > b.sort_key;
  return a.id < b.id;
});
```

## パーティクルの、ソート

パーティクルは、**数千〜数万個**あり、毎フレーム、CPU で、ソートすると、重いです。

| 方法 | 内容 |
| --- | --- |
| **システム単位**でソート | パーティクル システム（炎、煙）を、**1 つの物体として**、ソートする。システムの中は、**描画の順序のまま**（生成順） |
| システムの中も、ソート | 煙のように、重なりが、多い、**見た目が、重要なもの**だけ、**パーティクルごとに**、ソートする |
| **GPU でソート** | 計算シェーダーで、**ビトニック ソート**などを、使う。数万個でも、**ミリ秒以下** |
| **ソートしない** | **加算ブレンド**（火花、光）は、**順序に、依存しない**。ソート不要 |

### GPU での、ソート

```text
① 計算シェーダーで、各パーティクルの、カメラからの距離を、計算する
② ビトニック ソート（または、基数ソート）で、距離の順に、並べ替える
③ 並べ替えた順序で、描く（インデックス バッファを、並べ替える）
```

ビトニック ソートは、**データ数が、2 の累乗**で、**並列に実行しやすい**ソートです。GPU での、ソートの、定番です（実装は、短いが、本書では、省略。ライブラリの、`FidelityFX Parallel Sort` などを使う方法もある）。

## ソートに、**頼らない**方法

| 方法 | 内容 |
| --- | --- |
| **加算・乗算ブレンド** | 順序に、依存しない |
| **OIT**（順序に、依存しない、透明） | ソートなしで、近似または、正確な、結果を得る（[OIT](../oit/index.md)） |
| **アルファ テスト系** | 深度に書き込み、ソートが、不要（[Alpha Testing](../alpha-test/index.md)） |

''', before="## よくあるミス")
pg.Refs("translucency/blending-sorting/sorting.md", [RTR, PORTER, CARPENTER, "Batcher, \"Sorting Networks and their Applications\", AFIPS Spring Joint Computer Conference, 1968（ビトニック ソートの原典）"])
pg.Refs("translucency/blending-sorting/index.md", [PORTER, SMITH, LORACH, RTR])

# ================================================================ OIT
pg.Dedup("translucency/oit/depth-peeling.md")
pg.Add("translucency/oit/depth-peeling.md", '''
## 考え方：1 層ずつ、剥がす

**デプス ピーリング**（Everitt、2001）は、**最も手前の層から、順に、1 層ずつ**、**剥がす**ように、取り出していく方法です。

```text
視線 ──→  ┌────┐   ┌────┐   ┌────┐
          │ 層1 │   │ 層2 │   │ 層3 │     層 1 が、最も手前
          └────┘   └────┘   └────┘
```

1. 最初のパスで、**最も手前の層**（層 1）を、描く
2. 2 つ目のパスで、**層 1 より、奥の、最も手前**（層 2）を、描く
3. 3 つ目のパスで、**層 2 より、奥の、最も手前**（層 3）を、描く
4. …（層が、なくなるまで）
5. 取り出した層を、**奥から手前**の順に、**ブレンド**する

**各層は、画素ごとに、1 つの、フラグメント**です。**正確な順序**で、ブレンドできるので、**順序に依存しない透明が、正確に**、得られます。

## 仕組み：深度を、2 枚、使う

**前のパスの深度**を、テクスチャとして、**ピクセル シェーダーで、読み**、**それより、手前のフラグメントを、捨てます**。

```hlsl
Texture2D<float> g_prev_depth : register(t0);       // 前のパスで取り出した層の深度

struct PSOut { float4 color : SV_Target; };

PSOut main(PSInput input) {
  // 前の層の深度以下（手前）のフラグメントは、すでに取り出したので、捨てる。
  float prev = g_prev_depth.Load(int3(input.position.xy, 0));
  if (input.position.z <= prev + 1e-6) discard;

  PSOut o;
  o.color = ShadeFragment(input);                    // 通常の、ライティング
  return o;
}
```

| 設定 | 内容 |
| --- | --- |
| 深度テスト | `LESS`（最も手前の、1 つだけが、残る） |
| 深度の書き込み | 有効（そのパスでの、最も手前を、決めるため） |
| 前の深度 | **ping-pong**（2 枚の深度を、交互に、読み書き）。**書き込み先と、読み取り元は、別のテクスチャ** |
| 色 | 各パスの、色を、別の、レンダー ターゲットに、保存 |

```cpp
// 各層: 深度は 2 枚を交互に使う。色は、層ごとに別のテクスチャへ。
for (int layer = 0; layer < kMaxLayers; ++layer) {
  const int write = layer & 1, read = 1 - write;
  context->OMSetRenderTargets(1, layer_rtv[layer].GetAddressOf(), depth_dsv[write].Get());
  context->ClearDepthStencilView(depth_dsv[write].Get(), D3D11_CLEAR_DEPTH, 1.0f, 0);
  context->PSSetShaderResources(0, 1, depth_srv[read].GetAddressOf());
  DrawTransparentObjects();
}
// 最後に、層を奥（最後に取り出した層）から手前（最初）の順に、ブレンドする。
```

## 層の、数

必要な、パスの数は、**画素ごとの、最大の重なり（深度の複雑度）**です。

| 場面 | 重なり | パス |
| --- | --- | --- |
| 窓ガラス | 1〜2 | 2 |
| 葉の群れ | 5〜20 | 多い（重い） |
| 髪の毛 | 10〜50 | 非常に、多い |

**すべての層を、取り出す**には、**パスの数 × 半透明の描画コスト**が、かかります。実用では、**手前の、数層（3〜4 層）**だけを、正確に、残りは、近似、という使い方に、なります。

## デュアル デプス ピーリング

Bavoil と Myers（2008）の、**デュアル デプス ピーリング**は、**最も手前と、最も奥の、両方を、同時に、剥がす**方法です。**パスの数が、約半分**になります。

| 方式 | 1 パスで剥がす層 | 必要なパス（層が 8 のとき） |
| --- | --- | --- |
| 通常 | 手前から、1 層 | 8 |
| デュアル | 手前と奥から、各 1 層 | 4 |

**最小深度と、最大深度**を、同時に、追跡し、**ブレンドの、MIN / MAX 演算**を、使って、実現します（`BlendOp = MAX`、深度を、`-depth` で、2 つを、1 つのテクスチャに、格納する）。実装は、複雑ですが、**パスの、半減**が、得られます。

## 長所と短所

| | 内容 |
| --- | --- |
| 長所 | **正確**（順序が、完全に、正しい）。**ソート不要**。実装が、**概念的に**単純 |
| 短所 | **重い**。層の数 × 描画。**層が、足りないと、奥が、欠ける** |
| 短所 | **メモリ**：層ごとの、レンダー ターゲット（1 層 = 画面 1 枚） |
| 短所 | **半透明を、層の数だけ、何度も描く**（ジオメトリ、頂点シェーダーも、繰り返す） |

## 使いどころ

| 場面 | 判断 |
| --- | --- |
| 小さな、**重要な**半透明（ガラスの、造形物） | 使える |
| 重なりが、非常に多い（髪、葉、煙） | **重すぎる**。他の方式（[WBOIT](wboit.md)、[PPLL](ppll.md)） |
| オフラインの、正解画像の作成 | 最適（比較用の、リファレンス） |

''', before="## よくあるミス")
pg.Refs("translucency/oit/depth-peeling.md", [EVERITT, BAVOIL, CARPENTER, WYMAN16])

pg.Dedup("translucency/oit/ppll.md")
pg.Add("translucency/oit/ppll.md", '''
## 考え方：全部、リストに、溜める

**PPLL（Per-Pixel Linked List、画素ごとの、連結リスト）**は、**画面の各画素に、重なる、すべての、フラグメントを、リストとして、溜めて**、**最後に、画素ごとに、ソートして、ブレンド**する方法です（Yang ら、2010）。**デプス ピーリングのような、複数パスが、不要**で、**1 パスで、すべての層を、集められます**。

```text
画素 (x, y):  head ──→ [赤, 深度 0.3] ──→ [青, 深度 0.7] ──→ [緑, 深度 0.5] ──→ 終わり
                          リストの順序は、描かれた順（深度の順ではない）

最後に、画素ごとに、リストを取り出して、深度で並べ替え、奥から手前へブレンドする
```

## データ構造

| 要素 | 内容 |
| --- | --- |
| **ヘッド ポインタ バッファ**（画面と同じ大きさ） | 各画素の、リストの**先頭の、番号**。最初は `0xFFFFFFFF`（空） |
| **フラグメント バッファ**（大きな配列） | 全フラグメントを、**1 本の配列**に、書き込む。各要素は、`色`、`深度`、`次の要素の番号` |
| **カウンター** | 次に、使う、フラグメント バッファの、位置（アトミックに、増やす） |

```hlsl
struct FragmentNode {
  uint packed_color;      // RGBA8 に詰めた色
  float depth;            // 深度（並べ替え用）
  uint next;              // 同じ画素の、次のフラグメントの番号（0xFFFFFFFF なら、終わり）
};

RWStructuredBuffer<FragmentNode> g_fragments : register(u1);     // フラグメント バッファ
RWByteAddressBuffer g_head : register(u2);                       // ヘッド ポインタ（画素ごと）
RWByteAddressBuffer g_counter : register(u3);                    // 割り当て済みの、数
```

## 構築パス：フラグメントを、溜める

半透明の、ピクセル シェーダーで、**フラグメントを、書き込み**ます。**レンダー ターゲットには、描きません**（`discard` するか、書き込みマスクを、無効に）。

```hlsl
// 構築パス（半透明のオブジェクトを描くとき）。
[earlydepthstencil]                                              // 不透明の深度で、隠れたフラグメントを、事前に捨てる
void BuildPS(PSInput input) {
  float4 color = ShadeFragment(input);

  // ① フラグメント バッファの、空き位置を、アトミックに、確保する
  uint index;
  g_counter.InterlockedAdd(0, 1, index);
  if (index >= kMaxFragments) return;                             // 溢れたら、捨てる

  // ② この画素の、ヘッドを、新しいノードに、入れ替え、前のヘッドを、受け取る
  uint pixel = (uint)input.position.y * g_screen_width + (uint)input.position.x;
  uint prev_head;
  g_head.InterlockedExchange(pixel * 4, index, prev_head);

  // ③ 新しいノードを、書き込む（次 = 前のヘッド）
  FragmentNode node;
  node.packed_color = PackColor(color);
  node.depth = input.position.z;
  node.next = prev_head;
  g_fragments[index] = node;
}
```

| 命令 | 内容 |
| --- | --- |
| `InterlockedAdd` | カウンターを、アトミックに、増やして、**自分の、番号**を得る |
| `InterlockedExchange` | ヘッドを、自分の番号に、**入れ替え**、**前のヘッド**を受け取る。これで、**リストの、先頭に、追加**される |
| `[earlydepthstencil]` | 不透明な物で、隠れた、フラグメントは、シェーダー実行前に、捨てる |

## 解決パス：ソートして、ブレンド

**全画面の、ピクセル シェーダー**で、**画素ごとに、リストを、取り出し、ソートして、ブレンド**します。

```hlsl
float4 ResolvePS(float4 pos : SV_Position) : SV_Target {
  uint pixel = (uint)pos.y * g_screen_width + (uint)pos.x;
  uint node_index = g_head.Load(pixel * 4);

  // ① リストを、ローカル配列に、取り出す（最大 kMaxLayers 個）
  FragmentNode layers[kMaxLayers];
  int count = 0;
  while (node_index != 0xFFFFFFFF && count < kMaxLayers) {
    layers[count++] = g_fragments[node_index];
    node_index = layers[count - 1].next;
  }

  // ② 深度の大きい順（奥から手前）に、並べ替える（挿入ソート。層が、少ないので、これで十分）
  for (int i = 1; i < count; ++i) {
    FragmentNode key = layers[i];
    int j = i - 1;
    while (j >= 0 && layers[j].depth < key.depth) { layers[j + 1] = layers[j]; --j; }
    layers[j + 1] = key;
  }

  // ③ 背景（不透明の描画結果）から、奥から手前へ、順にブレンドする
  float3 color = g_opaque_color.Load(int3(pos.xy, 0)).rgb;
  for (int k = 0; k < count; ++k) {
    float4 c = UnpackColor(layers[k].packed_color);
    color = lerp(color, c.rgb, c.a);                              // 通常のアルファ ブレンド
  }
  return float4(color, 1.0);
}
```

## 長所と短所

| | 内容 |
| --- | --- |
| 長所 | **正確**（最大 `kMaxLayers` まで）。**1 パス**で、全層を、集められる |
| 長所 | **半透明の、ジオメトリを、1 回だけ、描く**（デプス ピーリングは、層の数だけ描く） |
| 短所 | **メモリ**が、大きい（フラグメント バッファ）。画面の、数倍〜数十倍の、フラグメントを、想定する |
| 短所 | **バッファが、溢れる**と、**フラグメントが、捨てられる**（画面が、欠ける）。上限の見積もりが、必要 |
| 短所 | **アトミック命令**が、**同じ画素に、集中**すると、競合して、遅い |
| 短所 | 解決パスの、画素ごとの、**ソートが、重い**（層が、多い画素） |
| 短所 | **画素ごとに、リストの長さが、バラバラ**で、**GPU の、スレッドが、待たされる**（ワープ内のばらつき） |

## 最適化

| 工夫 | 内容 |
| --- | --- |
| 色を、詰める | 色を `RGBA8`（4 バイト）にして、深度と合わせて、**8 バイト**に。**ノード全体で、12 バイト**（次の番号を含む） |
| 層の数の上限 | `kMaxLayers = 8〜16`。それ以上は、**近似**（奥の層を、まとめる） |
| 手前を残して、奥を、まとめる | 最も手前の、数層だけ、正確に。残りは、**WBOIT で、近似**（ハイブリッド、[Hybrid Approaches and Choosing](hybrid.md)） |
| 低解像度で、集める | 煙のような、ぼやけた物は、**画面の半分の解像度**で、集めて、**アップサンプル** |
| 画面を、タイルに分ける | タイルごとに、**フラグメントの、上限を、決める** |

## DirectX 11 での、リソース

PPLL には、**`RWByteAddressBuffer`** と **`RWStructuredBuffer`**（**UAV**）を、**ピクセル シェーダーから、書き込む**必要があります。DirectX 11 では、**ピクセル シェーダーでの、UAV の、使用**が、できます（`OMSetRenderTargetsAndUnorderedAccessViews`）。

```cpp
// レンダー ターゲット 0 個（描かない）+ UAV 3 つ（ヘッド、フラグメント、カウンター）を、ピクセル シェーダーへ設定する。
ID3D11UnorderedAccessView* uavs[3] = {fragment_uav.Get(), head_uav.Get(), counter_uav.Get()};
UINT initial_counts[3] = {0, 0, 0};
context->OMSetRenderTargetsAndUnorderedAccessViews(
    0, nullptr, depth_dsv_readonly.Get(),    // レンダー ターゲットなし。深度は、読み取り専用
    1, 3, uavs, initial_counts);             // UAV はスロット 1 から
// 毎フレームの最初に、ヘッド バッファを 0xFFFFFFFF で、カウンターを 0 で、クリアする。
const UINT clear_head[4] = {0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF};
context->ClearUnorderedAccessViewUint(head_uav.Get(), clear_head);
```

''', before="## よくあるミス")
pg.Refs("translucency/oit/ppll.md", [YANG, CARPENTER, SALVI, WYMAN16, D3D11_UAV])

pg.Dedup("translucency/oit/wboit.md")
pg.Add("translucency/oit/wboit.md", '''
## 考え方：順序の、**近似**

**WBOIT**（Weighted Blended OIT、McGuire と Bavoil、2013）は、**ソートも、複数パスも、リストも、使わず**、**1 パスで、順序の影響を、近似**する方法です。

通常のアルファ ブレンドは、**順序に、依存**します。そこで、**各フラグメントに、重みを付けた、平均**を、取ります。**重みは、手前ほど、大きく**します。**順序に、依存しない**計算（足し算）だけで、**手前が、より、強く、見える**結果を、近似的に、作ります。

## 式

各フラグメント `i`（色 `Cᵢ`、アルファ `αᵢ`、深度 `zᵢ`）に、**重み `wᵢ`** を、付けます。

```text
累積色     = Σ  Cᵢ × αᵢ × wᵢ                ← 加算ブレンドで、足せる
累積重み   = Σ  αᵢ × wᵢ                      ← 加算ブレンドで、足せる
透過度     = Π  (1 − αᵢ)                      ← 乗算ブレンドで、掛けられる（reveal）

合成色     = 累積色 / 累積重み                 ← 重みつき平均の、色
最終       = 合成色 × (1 − 透過度) + 背景 × 透過度
```

| 値 | 意味 |
| --- | --- |
| 累積色 / 累積重み | **半透明全体の、平均的な色**（手前ほど、重みが大きい） |
| 透過度（reveal） | **すべての層を、通過して**、背景に届く光の割合。`Π(1 − α)` |
| 最終色 | 半透明全体の色を、`1 − 透過度` の割合で、背景に重ねる |

**足し算と、掛け算だけ**なので、**順序に、依存しません**。**加算ブレンド**と、**乗算ブレンド**の、組み合わせで、**1 パス**で、実現できます。

## 2 つの、レンダー ターゲット

| ターゲット | 形式 | 内容 | ブレンド |
| --- | --- | --- | --- |
| 0：累積（accum） | `R16G16B16A16_FLOAT` | `rgb` = 累積色、`a` = 累積重み | **加算**（`ONE`、`ONE`） |
| 1：透過度（reveal） | `R8_UNORM`（または `R16_FLOAT`） | `Π(1 − α)` | **乗算**（`ZERO`、`INV_SRC_COLOR`） |

```cpp
// WBOIT の、ブレンド ステート。2 つのレンダー ターゲットに、別のブレンドを使う。
D3D11_BLEND_DESC blend = {};
blend.IndependentBlendEnable = TRUE;

// ターゲット 0: 累積（加算）
D3D11_RENDER_TARGET_BLEND_DESC& accum = blend.RenderTarget[0];
accum.BlendEnable = TRUE;
accum.SrcBlend = D3D11_BLEND_ONE;       accum.DestBlend = D3D11_BLEND_ONE;
accum.BlendOp = D3D11_BLEND_OP_ADD;
accum.SrcBlendAlpha = D3D11_BLEND_ONE;  accum.DestBlendAlpha = D3D11_BLEND_ONE;
accum.BlendOpAlpha = D3D11_BLEND_OP_ADD;
accum.RenderTargetWriteMask = D3D11_COLOR_WRITE_ENABLE_ALL;

// ターゲット 1: 透過度（乗算）。出力した値 α が、(1 − α) として、掛けられる。
D3D11_RENDER_TARGET_BLEND_DESC& reveal = blend.RenderTarget[1];
reveal.BlendEnable = TRUE;
reveal.SrcBlend = D3D11_BLEND_ZERO;     reveal.DestBlend = D3D11_BLEND_INV_SRC_COLOR;
reveal.BlendOp = D3D11_BLEND_OP_ADD;
reveal.SrcBlendAlpha = D3D11_BLEND_ZERO; reveal.DestBlendAlpha = D3D11_BLEND_INV_SRC_ALPHA;
reveal.BlendOpAlpha = D3D11_BLEND_OP_ADD;
reveal.RenderTargetWriteMask = D3D11_COLOR_WRITE_ENABLE_RED;

device->CreateBlendState(&blend, &wboit_blend);
// ターゲット 0 は 0 で、ターゲット 1 は 1（reveal の初期値 = 透過度 1）で、クリアしておく。
```

## 半透明の、ピクセル シェーダー

```hlsl
struct WboitOut {
  float4 accum : SV_Target0;
  float reveal : SV_Target1;
};

WboitOut main(PSInput input) {
  float4 color = ShadeFragment(input);        // 通常のライティング。color.a は、アルファ
  float z = input.position.z;                  // 0（近い）〜 1（遠い）

  // 重み関数: 手前ほど大きく、アルファが大きいほど大きい。論文の候補の 1 つ。
  float weight = max(min(1.0, max(max(color.r, color.g), color.b) * color.a), color.a)
               * clamp(0.03 / (1e-5 + pow(z / 200.0, 4.0)), 1e-2, 3e3);

  WboitOut o;
  o.accum = float4(color.rgb * color.a, color.a) * weight;     // 累積色（α 乗算済み）と、累積重み（α）に、重みを掛ける
  o.reveal = color.a;                                            // 乗算ブレンドの、(1 − α) 用
  return o;
}
```

重みは、**深度 `z`**（遠いほど小さい）と、**色・アルファ**で決まります。論文には、**複数の候補**が、載っています。**場面の、深度の範囲**（近い面、遠い面）に、**合わせて**、**調整が必要**です。

## 合成パス

全画面の、ピクセル シェーダーで、**累積と、透過度から、最終色**を、作って、**背景に、重ねます**。

```hlsl
Texture2D<float4> g_accum : register(t0);
Texture2D<float> g_reveal : register(t1);

float4 main(float4 pos : SV_Position) : SV_Target {
  int3 p = int3(pos.xy, 0);
  float reveal = g_reveal.Load(p);                    // 透過度（1 = 何も描かれていない）
  if (reveal >= 1.0) discard;                         // 半透明が、何もない画素

  float4 accum = g_accum.Load(p);
  // 極端に大きい値（オーバーフロー）の対策
  if (isinf(accum.a)) accum.a = max(max(accum.r, accum.g), accum.b);
  float3 average_color = accum.rgb / max(accum.a, 1e-5);       // 重みつき平均の色

  // 出力: 色 = 平均色、アルファ = 1 − 透過度。通常のアルファ ブレンド（SRC_ALPHA, INV_SRC_ALPHA）で、背景に重ねる。
  return float4(average_color, 1.0 - reveal);
}
```

## 長所と短所

| | 内容 |
| --- | --- |
| 長所 | **1 パス**。**ソート不要**。**メモリ、帯域が、小さい**（2 枚のターゲット） |
| 長所 | 実装が、**簡単**。**ブレンド ステートだけ**で、実現 |
| 長所 | **多くの層**（煙、葉）が、重なっても、**コストが、変わらない** |
| 短所 | **近似**。**色が、正しくない**ことがある（特に、**色が、大きく違う、層**が重なるとき） |
| 短所 | **手前の、不透明に近い物が、奥の物より、うっすら**に、見えることがある |
| 短所 | **重み関数の調整**が、場面ごとに、必要 |
| 短所 | **アルファが、非常に、大きい**（不透明に近い）物の、**前後関係**は、**不正確** |

### どんな時に、うまくいく / 悪いか

| 状況 | 結果 |
| --- | --- |
| 煙・霧・パーティクル（同じような色が、重なる） | **よく合う** |
| ガラス（色が、違う、層が、重なる） | **前後が、混ざる**（赤が、手前、青が、奥のはずが、紫になる） |
| 髪の毛 | 近い色が、重なるので、**まずまず** |
| 不透明に近い、半透明（アルファ 0.9） | **悪い**（手前が、ちゃんと、手前に見えない） |

## 改良版

| 改良 | 内容 |
| --- | --- |
| **色の、補正** | 論文の後続で、**色の、ずれを、減らす**、工夫が、提案されている |
| **屈折** | WBOIT の、**画面のコピー**を、使い、背景の、屈折を、扱う |
| **ハイブリッド** | **手前の数層だけ、正確に**（PPLL、デプス ピーリング）、**残りを、WBOIT** で、近似（[Hybrid Approaches and Choosing](hybrid.md)） |

''', before="## よくあるミス")
pg.Refs("translucency/oit/wboit.md", [MCGUIRE, WYMAN16, D3D11_BLEND, MUNSTERMANN])

pg.Dedup("translucency/oit/stochastic.md")
pg.Add("translucency/oit/stochastic.md", '''
## 考え方：確率で、描く

**確率的透明**（Stochastic Transparency、Enderton ら、2010）は、**半透明を、確率的な、アルファ テスト**に、置き換えます。**アルファが、0.3** なら、**30% の確率で、描き、70% の確率で、捨てます**。**深度を書き込み**、**ソートも不要**になります。**1 画素を、複数の、サンプルで、描く**（MSAA の、サンプルを使う）と、**サンプルごとに、違う結果**になり、**平均すると、半透明**に、見えます。

```text
アルファ 0.3 の、半透明の物:
  サンプル 1: 描く     （確率 30%）
  サンプル 2: 捨てる
  サンプル 3: 捨てる
  サンプル 4: 描く
  ↓ 平均（リゾルブ）
  半透明な色（約 30% の濃さ）
```

[Hashed Alpha](../alpha-test/hashed-alpha.md) と、**同じ、考え方**を、**複数のサンプル**に、拡張した、手法です。

## 基本の、実装

MSAA の、**カバレッジ**（どのサンプルを、描くか）を、**アルファから、作ります**。

```hlsl
// ピクセル シェーダーが、SV_Coverage を出力して、描くサンプルを、決める。
struct PSOut {
  float4 color : SV_Target;
  uint coverage : SV_Coverage;
};

PSOut main(PSInput input) {
  float4 c = ShadeFragment(input);

  // アルファに応じて、4 つのサンプルのうち、何個を描くか（ランダムに、選ぶ）
  uint mask = 0;
  [unroll] for (uint s = 0; s < 4; ++s) {
    // サンプルごとに、違う乱数（画素の位置と、サンプル番号から）
    float r = Hash(input.position.xy, s);
    if (c.a > r) mask |= (1u << s);
  }

  PSOut o;
  o.color = float4(c.rgb, 1.0);       // 色は、そのまま（アルファは、使わない）
  o.coverage = mask;
  return o;
}
```

| 項目 | 内容 |
| --- | --- |
| 深度テスト | **有効**。**深度の書き込みも、有効**（描いた、サンプルの深度が、残る） |
| ブレンド | **不要**（不透明として、描く） |
| `SV_Coverage` | **どのサンプルを、描くか**を、シェーダーが、決める |

## 正しい結果にならない、理由

この方法は、**サンプルごとに、深度を、書きます**。サンプルに、**最も手前の、描かれた、フラグメントの、色**だけが、残ります。**奥のフラグメントは、手前のフラグメントに、隠されて**、**消えます**。**手前の物が、描かれた、サンプルでは、奥の物は、見えません**。

結果、**手前と奥の、両方が、混ざった色**には、**ならず**、**サンプルごとに、どちらか 1 つ**が、見えます。**平均すると、確率的には、正しい**（手前が、アルファの確率で、見え、残りの確率で、奥が見える）ので、**期待値は、正しい**です。

**問題**は、**サンプル数が、少ない**ことです。4 サンプルでは、**ノイズが、非常に大きく**なります。

## ノイズを、減らす

Enderton らの、論文は、**ノイズを、減らす**、**工夫**を、いくつか、提案しています。

| 工夫 | 内容 |
| --- | --- |
| **サンプル数を、増やす** | 8x、16x、さらに、**サブピクセル**で、多くのサンプルを使う。**メモリと、帯域が、増える** |
| **層ごとの、層化** | アルファに応じた、**カバレッジの、パターンを、均等に、分ける**（ランダムでなく、**層化された**パターン）。ノイズが、減る |
| **ブルー ノイズ** | サンプルの、選択に、**ブルー ノイズ**を使う。粒が、均一で、目立たない |
| **TAA** | フレームをまたいで、**平均**する。ノイズが、**時間方向に、ならされる** |

## 論文の、**もう 1 つ**の、方法：色の、正しい復元

論文は、**確率的な、深度**だけでなく、**各サンプルの、深度の、順序**から、**色を、正しく、復元**する、拡張も、述べています。

| 段階 | 内容 |
| --- | --- |
| ① 不透明度の、推定 | 複数のサンプルの、深度を、比べて、**各フラグメントの、手前に、どれだけの、不透明度が、あるか**を、推定する |
| ② 色の、積算 | 手前の、不透明度で、重みを付けて、**色を、足す** |

実装は、複雑で、**メモリも、帯域も、必要**です。ゲームでは、あまり、使われず、**TAA と、組み合わせた、簡易版**（ハッシュ アルファ）が、使われます。

## 長所と短所

| | 内容 |
| --- | --- |
| 長所 | **ソート不要**。**深度を、書き込める**。**ライティングが、1 回**（半透明の色を、そのまま、描く） |
| 長所 | **大量の、重なり**（髪、煙）でも、**コストは、ほぼ、一定** |
| 長所 | **TAA と、相性が、良い**（ノイズを、時間方向に、平均できる） |
| 短所 | **ノイズ**（ざらつき）。TAA がないと、**目立つ** |
| 短所 | **MSAA の、サンプル数**に、品質が、依存する。メモリ、帯域が、大きい |
| 短所 | **不透明に近い**半透明は、**ノイズが、小さい**が、**透明に近い**（アルファ 0.1）では、**ノイズが、大きい** |

## 使いどころ

| 場面 | 判断 |
| --- | --- |
| **TAA を、使っている** + 半透明の**髪、葉、煙** | **よい選択**（ハッシュ アルファ、または、確率的透明） |
| TAA がない | ノイズが、目立つ。**WBOIT** などを検討（[WBOIT](wboit.md)） |
| ガラス（正確な、屈折、反射が、必要） | **向かない**（ノイズ、前後の、混ざり） |

''', before="## よくあるミス")
pg.Refs("translucency/oit/stochastic.md", [ENDERTON, WYMAN16, "Wyman, McGuire, \"Hashed Alpha Testing\", Symposium on Interactive 3D Graphics and Games 2017", "Microsoft Learn, \"SV_Coverage semantic\"（HLSL）"])

pg.Dedup("translucency/oit/hybrid.md")
pg.Add("translucency/oit/hybrid.md", '''
## 方式の、一覧（比べる）

| 方式 | 正確さ | パス数 | メモリ | 速さ | 向く対象 |
| --- | --- | --- | --- | --- | --- |
| ソート + アルファ ブレンド | 物体単位で、正確。**物体内、交差は、不正確** | 1 | 小 | 速い | 少数の、ガラス、パーティクル |
| デプス ピーリング | **正確** | 層の数 | 中（層ごとに、ターゲット） | **遅い** | 重要な、少数の物 |
| PPLL | **正確**（上限まで） | 2（構築 + 解決） | **大**（バッファ） | 中 | 重なりが、多く、正確さが、必要 |
| WBOIT | **近似** | 2（描画 + 合成） | 小（2 枚） | **速い** | 煙、霧、パーティクル（色が、近い） |
| 確率的透明 | 期待値は、正しい | 1 | 中（MSAA） | 速い | TAA ありの、髪、葉 |
| アルファ テスト系 | 縁を、切り抜く | 1 | 小 | 速い | 葉、草、柵 |

## 選び方

```text
半透明の物が、少ない（数個）？
   └ Yes → ソート + アルファ ブレンド（物体内の、問題があれば、裏面 → 表面の 2 パス）
   └ No ↓
重なりが、多い（数十層）？
   ├ 縁を、切り抜く物（葉、草、髪）？ → アルファ テスト系（A2C、ハッシュ アルファ + TAA）
   ├ ぼんやりした、物（煙、霧、パーティクル）？ → WBOIT
   └ 正確さが、必要（ガラス、水中の物）？ → PPLL、または、少数層に、デプス ピーリング
```

## ハイブリッド

**1 つの方式だけ**で、すべてを、まかなうのは、**難しい**です。**物の種類で、使い分け**ます。

| 物 | 方式 |
| --- | --- |
| 窓ガラス、車の窓（重要で、数が少ない） | **ソート + アルファ ブレンド**（または、デプス ピーリング） |
| 煙、霧、魔法のパーティクル | **WBOIT**（別のレンダー ターゲットに、描いて、最後に、合成） |
| 木の葉、草 | **アルファ テスト**（A2C、ハッシュ） |
| 髪の毛 | **ハッシュ アルファ + TAA**、または、**PPLL** で、手前の数層（[Hair Transparency](../../skin-hair/hair/transparency.md)） |
| 水面 | 専用の、水のシェーダー（[Water](../../water/index.md)） |

### 描画の順番

```text
① 不透明（深度を書く）
② アルファ テスト系（葉、草、柵）
③ 水
④ ソートした、半透明（ガラス）
⑤ WBOIT の、パーティクル（別ターゲットに、描いて、合成）
⑥ ポストプロセス
```

**各方式の、結果を、順に、画面に、重ねる**ので、**方式の間の、前後関係**は、**描く順番**で、決まります。**ガラスの向こうの、煙**は、ガラスより先に、描く必要があります。**1 つの、場面に、混ざる**場合は、**全体の、順番を、設計**します。

## 手前だけ、正確に

**画面の、手前の、数層**は、**見た目の影響が、大きく**、**奥の層は、小さい**。この性質を、使った、ハイブリッドが、あります。

| 層 | 方式 |
| --- | --- |
| 手前の、数層（たとえば、4 層） | **正確**（PPLL や、デプス ピーリング） |
| 奥の、残り | **近似**（WBOIT で、まとめて、1 つの層に） |

Salvi らの、**適応的な透明度**（Adaptive Transparency、2011）や、**マルチレイヤー アルファ ブレンド**（2014）は、**少数の層で、近似する**考え方です。**メモリを、固定**できます（**PPLL のように、溢れない**）。

## 実装の、現実

| 項目 | 内容 |
| --- | --- |
| まず、**測る** | 半透明の、**オーバードロー**が、実際に、何層なのか。問題が、起きて**いない**なら、単純な方式で、十分 |
| まず、**単純な方式**から | ソート + アルファ ブレンドで、**問題が、出たら**、その部分だけ、他の方式に |
| **品質設定** | PPLL や、WBOIT の、**層の数、解像度**を、設定で、変えられるように、しておく |
| **対応環境** | PPLL は、**UAV をピクセル シェーダーで、書ける**必要がある（DX11 の、機能レベル 11_0 以上） |

''', before="## よくあるミス")
pg.Refs("translucency/oit/hybrid.md", [WYMAN16, SALVI, SALVI14, MCGUIRE, MUNSTERMANN])
pg.Refs("translucency/oit/index.md", [CARPENTER, EVERITT, YANG, MCGUIRE, ENDERTON, WYMAN16])
print("ok")
