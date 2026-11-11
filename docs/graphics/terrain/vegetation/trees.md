---
title: Trees
tags:
  - 描画
---

# Trees

森を描くと木 1 本が数万ポリゴンで、それが数万本並びます。そのまま描けば画面に入る三角形は数十億になります。遠くの木は画面で数ピクセルなので、近くと同じ細かさで描くのは無駄です。

<strong>木は近くは詳細なメッシュ、遠くは簡易なメッシュやビルボードにして、距離で LOD を切り替えます</strong>。このページでは木の部品、LOD の段階、切り替えを隠すディザ、遠景のインポスター（数方向から撮った絵を板に貼る方法）、影の扱い木の作り方を説明します。

!!! tip "ポイント"
    - 近くは幹と枝のメッシュ、葉は板（カード）にアルファ テストで切り抜きます。葉を 1 枚ずつモデリングすると数十万ポリゴンになります。
    - 中距離は枝と葉を減らします。遠くはインポスター、最遠はビルボードです。
    - LOD の切り替えは 2 つを同時に描いて、ディザ（市松）でなめらかに入れ替えます。
    - インポスターは球面上の方向を正方形に展開する 8 面体マッピングで撮り、近い 3 方向を重心座標で混ぜます。
    - 影は描画の LOD とは別の粗い距離で決めてかまいません。

!!! info "このページを読む前に"
    - [Vegetation](index.md)（このセクション全体の地図と読む順番）

## 木の部品 {#parts}

木は役割の違う 3 つの部品でできています。

- 幹と太い枝: 円柱を曲げたメッシュです。不透明で木の皮のテクスチャを貼ります。
- 細い枝: メッシュか板です。アルファ テストで切り抜きます。
- 葉: 葉の房を描いた板（カード）です。アルファ テストで切り抜いて、透過を表すときは [Foliage Translucency](translucency.md) の処理を足します。

葉を 1 枚ずつ 3D モデルにすると、1 本で数十万ポリゴンになります。葉の房を 1 枚の板に描いて、枝の周りに並べるカードにすると、数千ポリゴンに収まります。たとえば、葉 10 万枚を 2 三角形ずつで作れば 20 万三角形です。房 1 枚に葉 30 枚分の絵を描いて、カードを 3000 枚並べると、6000 三角形で済みます。

幹と葉はマテリアルを分けます。幹は不透明で葉はアルファ テストです。アルファ テストの描画は Early-Z を妨げるので、不透明の物と別のパスで描きます。

## LOD の段階 {#lod}

木の LOD は次のような 5 段階が目安です。距離と三角形の数は一例です。

1. LOD 0（〜30 m）: 幹と枝の完全なメッシュに葉のカードを付けます。2 万〜5 万三角形です。
2. LOD 1（30〜80 m）: 細い枝を減らして、葉のカードを統合します。5000〜1 万三角形です。
3. LOD 2（80〜200 m）: 幹と主な枝だけにして、葉は大きなカードにします。1000〜3000 三角形です。
4. インポスター（200 m〜）: 数方向から撮った絵をカメラを向く板に貼ります。2 三角形です。
5. ビルボード（最遠）: 1 枚の絵を常にカメラへ向けます。2 三角形です。

500 m を超えると木は数ピクセルの緑のかたまりです。1 km を超えたら木を 1 本ずつ描くのをやめて、森の色の塊として地形のテクスチャに含める方法もあります。

三角形の数は距離で 4 桁（5 万と 2）違います。この差が森を描ける理由です。

## LOD の切り替えを隠す {#fade}

LOD が切り替わる瞬間に形が急に変わって、ポップが目立ちます。2 つの LOD を同時に描いて、市松（ディザ）で入れ替えると、ポップが目立たなくなります。LOD A のピクセルが少しずつ抜けて、LOD B のピクセルが少しずつ現れます。

まず、距離から `fade`（0〜1）を作る関数とベイヤー行列のしきい値です。

```hlsl
// 切り替えの範囲 [start, end] で、0 から 1 へ上がる。start より近ければ 0、end より遠ければ 1
float LodFade(float distance_to_camera, float start, float end) {
  return saturate((distance_to_camera - start) / (end - start));
}

// 4×4 のベイヤー行列から、画素ごとのしきい値（0..1）を作る
float BayerThreshold(float2 screen_pos) {
  static const float kBayer[16] = {
     0,  8,  2, 10,
    12,  4, 14,  6,
     3, 11,  1,  9,
    15,  7, 13,  5};
  uint2 p = uint2(screen_pos) & 3;                 // 画面上の 4×4 の周期
  return (kBayer[p.y * 4 + p.x] + 0.5) / 16.0;
}
```

次に、2 つの LOD の描画での使い方です。

```hlsl
// LOD A（近い方）: fade が大きいほど、多くのピクセルを捨てる
void ClipLodA(float4 screen_pos, float fade) {
  clip(BayerThreshold(screen_pos.xy) - fade);      // しきい値 < fade の画素を捨てる
}

// LOD B（遠い方）: 逆。fade が小さいうちは、ほとんど捨てる
void ClipLodB(float4 screen_pos, float fade) {
  clip(fade - BayerThreshold(screen_pos.xy));      // しきい値 > fade の画素を捨てる
}
```

LOD A と B のしきい値の関係が裏表になっているので、ある画素は必ずどちらか一方が描きます。隙間も二重の描画もありません。

代償は切り替えの範囲で 2 つの LOD を同時に描くことです。頂点とピクセルの両方のコストが一時的に増えます。範囲は見た目のポップが目立たない程度に狭くします（[Dithered Transparency](../../translucency/alpha-test/dither.md) 参照）。TAA を使っていれば市松がフレームごとに平均されて、さらに目立たなくなります。

## インポスター {#imposter}

<strong>インポスター（imposter）</strong>は、3D の木を事前に複数の方向から撮影した絵を板に貼って、木の代わりに描く手法です。板は 2 三角形で木 1 本のコストがほぼ一定になります。

<svg class="fig flow" viewBox="0 0 720 270" role="img" aria-label="木を球面上の複数の方向から撮影してアトラスに並べ、実行時はカメラに近い 3 方向を混ぜる"><defs><marker id="trA" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">インポスター: 撮って、並べて、混ぜる</text>
<rect x="20" y="50" width="170" height="130" rx="10" fill="rgba(148,163,184,0.15)" stroke="#94a3b8"/><circle cx="105" cy="115" r="50" fill="none" stroke="#94a3b8" stroke-dasharray="4 4"/><path d="M105,150 L105,100 M105,100 L90,86 M105,100 L120,84 M105,120 L92,108 M105,120 L118,106" stroke="#4c8bf5" stroke-width="3" fill="none"/>
<g fill="#e5aa28"><circle cx="105" cy="62" r="5"/><circle cx="148" cy="80" r="5"/><circle cx="165" cy="115" r="5"/><circle cx="148" cy="150" r="5"/><circle cx="62" cy="150" r="5"/><circle cx="45" cy="115" r="5"/><circle cx="62" cy="80" r="5"/></g>
<text x="105" y="200" text-anchor="middle" style="font-size:12px">① 木を周りの方向から撮る</text>
<line x1="196" y1="115" x2="240" y2="115" stroke="currentColor" stroke-width="2" marker-end="url(#trA)"/>
<g stroke="#4c8bf5" stroke-width="1.5" fill="rgba(76,139,245,0.15)"><rect x="250" y="55" width="40" height="40"/><rect x="290" y="55" width="40" height="40"/><rect x="330" y="55" width="40" height="40"/><rect x="250" y="95" width="40" height="40"/><rect x="290" y="95" width="40" height="40" fill="rgba(229,170,40,0.35)"/><rect x="330" y="95" width="40" height="40" fill="rgba(229,170,40,0.35)"/><rect x="250" y="135" width="40" height="40"/><rect x="290" y="135" width="40" height="40" fill="rgba(229,170,40,0.35)"/><rect x="330" y="135" width="40" height="40"/></g>
<text x="310" y="200" text-anchor="middle" style="font-size:12px">② アトラスに並べる</text>
<line x1="380" y1="115" x2="424" y2="115" stroke="currentColor" stroke-width="2" marker-end="url(#trA)"/>
<rect x="434" y="50" width="150" height="130" rx="10" fill="rgba(148,163,184,0.15)" stroke="#94a3b8"/><text x="509" y="100" text-anchor="middle" style="font-size:12px">カメラの向きに近い</text><text x="509" y="118" text-anchor="middle" style="font-size:12px">3 枚（黄）を、重心座標の</text><text x="509" y="136" text-anchor="middle" style="font-size:12px">重みで混ぜる</text>
<text x="509" y="200" text-anchor="middle" style="font-size:12px">③ 実行時に混ぜて板に貼る</text>
<rect x="20" y="222" width="680" height="38" rx="9" fill="rgba(148,163,184,0.18)" stroke="#94a3b8" stroke-width="1.5"/><text x="360" y="246" text-anchor="middle" style="font-size:12px">64 方向（8×8）、1 枚 256×256 なら、アトラスは 2048×2048。色と法線・深度で 2 枚</text></svg>

撮影する方向は球面上に均等に並べたい場面です。**8 面体マッピング**（正八面体への展開）を使うと球面を正方形に展開して、格子状に均等な方向を取れます（Brucks、2018）。方向のベクトルと正方形の座標は次の関数で相互に変換できます。

```hlsl
// 方向（単位ベクトル）→ 0..1 の正方形の座標（8 面体マッピング）
float2 OctEncode(float3 n) {
  n /= (abs(n.x) + abs(n.y) + abs(n.z));           // 正八面体の表面に投影する
  float2 uv = n.xz;                                // 上半分（y >= 0）はそのまま使う
  if (n.y < 0.0) {
    // 下半分は、外側へ折り返す
    float2 sign_xz = float2(n.x >= 0.0 ? 1.0 : -1.0, n.z >= 0.0 ? 1.0 : -1.0);
    uv = (1.0 - abs(n.zx)) * sign_xz;
  }
  return uv * 0.5 + 0.5;                           // -1..1 → 0..1
}

// 0..1 の正方形の座標 → 方向（撮影時に、各フレームの向きを決めるのに使う）
float3 OctDecode(float2 uv) {
  float2 f = uv * 2.0 - 1.0;
  float3 n = float3(f.x, 1.0 - abs(f.x) - abs(f.y), f.y);
  if (n.y < 0.0) {
    float2 sign_xz = float2(n.x >= 0.0 ? 1.0 : -1.0, n.z >= 0.0 ? 1.0 : -1.0);
    n.xz = (1.0 - abs(n.zx)) * sign_xz;
  }
  return normalize(n);
}
```

撮影側は格子 `N × N` の各セル `(i, j)` について、`OctDecode((i, j) / (N - 1))` の方向からカメラで木を撮って、アトラスの `(i, j)` の位置に貼ります。色（アルベド）と法線・深度を別のテクスチャに撮っておくと実行時にライティングを計算できます。色にライトを焼き込むと太陽が動いても陰影が変わりません。

実行時はカメラの方向に最も近いフレームを選びます。カメラがフレームの間を向いているとき 1 枚だけを選ぶとフレームが切り替わる瞬間にポップします。そこで、近い 3 フレームを選んで重心座標で混ぜます。

```hlsl
Texture2D<float4> g_imposter_albedo : register(t0);   // アトラス。N×N のフレーム
SamplerState g_linear_clamp : register(s0);
static const float kGridSize = 8.0;                   // N（1 辺のフレーム数）

float4 SampleFrame(float2 cell, float2 uv) {
  // セル (i, j) のフレームの中の uv（0..1）を、アトラス全体の uv に直す
  float2 atlas_uv = (cell + uv) / kGridSize;
  return g_imposter_albedo.SampleLevel(g_linear_clamp, atlas_uv, 0);
}

float4 ImposterPS(float2 uv : TEXCOORD0, float3 view_dir : TEXCOORD1) : SV_Target {
  // ① カメラ方向（木から見た向き）を、格子の座標にする
  float2 grid = OctEncode(normalize(view_dir)) * (kGridSize - 1.0);
  float2 cell = floor(grid);
  float2 f = frac(grid);

  // ② 格子のセルを 2 つの三角形に分けて、f が入る方の 3 頂点と重みを選ぶ
  float2 c_a, c_b, c_c;
  float3 w;
  if (f.x + f.y > 1.0) {                           // 右上の三角形: (1,1), (0,1), (1,0)
    c_a = cell + float2(1, 1);
    c_b = cell + float2(0, 1);
    c_c = cell + float2(1, 0);
    w = float3(f.x + f.y - 1.0, 1.0 - f.x, 1.0 - f.y);
  } else {                                         // 左下の三角形: (0,0), (1,0), (0,1)
    c_a = cell;
    c_b = cell + float2(1, 0);
    c_c = cell + float2(0, 1);
    w = float3(1.0 - f.x - f.y, f.x, f.y);
  }

  // ③ 3 フレームを読んで、重みで混ぜる
  float4 col = SampleFrame(c_a, uv) * w.x + SampleFrame(c_b, uv) * w.y + SampleFrame(c_c, uv) * w.z;
  clip(col.a - 0.5);                               // アルファ テストで木の輪郭を切り抜く
  return col;
}
```

板は頂点シェーダーでカメラの方を向けて作ります。木の中心を板の中心にして半径 `radius` の球を覆う大きさにします。

```hlsl
cbuffer ImposterConstants : register(b0) {
  float4x4 g_view_proj;
  float3 g_camera_pos;
  float g_radius;            // 木を囲む球の半径（メートル）。板の 1 辺の半分になる
  float3 g_tree_center;      // 木の中心（球の中心）のワールド位置
  float _pad;
};

struct ImposterVsOut {
  float4 pos : SV_Position;
  float2 uv : TEXCOORD0;
  float3 view_dir : TEXCOORD1;   // 木の中心から見たカメラの向き
};

ImposterVsOut ImposterVS(uint vertex_id : SV_VertexID) {
  // 2 三角形の板（ストリップ）の 4 頂点: (0,0) (1,0) (0,1) (1,1)
  float2 corner = float2(vertex_id & 1, vertex_id >> 1);
  float3 to_camera = normalize(g_camera_pos - g_tree_center);
  // カメラを向く板の基底。真上を向いたときに退化しないよう、上向きを切り替える
  float3 up_hint = abs(to_camera.y) > 0.99 ? float3(0, 0, 1) : float3(0, 1, 0);
  float3 right = normalize(cross(up_hint, to_camera));
  float3 up = cross(to_camera, right);

  float2 offset = (corner * 2.0 - 1.0) * g_radius;     // -radius .. +radius
  float3 world_pos = g_tree_center + right * offset.x + up * offset.y;

  ImposterVsOut o;
  o.pos = mul(float4(world_pos, 1.0), g_view_proj);
  o.uv = float2(corner.x, 1.0 - corner.y);             // v は下向き
  o.view_dir = to_camera;
  return o;
}
```

`DrawInstanced(4, 木の数, 0, 0)` を三角形ストリップで描けば、板が木の数だけ並びます。

重みの和は常に 1 です（右上: `f.x + f.y − 1 + 1 − f.x + 1 − f.y = 1`）。`f = (0, 0)` なら左下の頂点だけが 1 になって、そのフレームそのものが出ます。

この簡易版はフレームの間を単純に混ぜるので、3 フレームの絵の輪郭が少しずれて見えることがあります。深度を撮っておいてフレームごとにテクスチャ座標を視差でずらすとずれが減ります（足さずに省いています）。

数字を確かめます。64 フレーム（8 × 8）で 1 枚 256 × 256 ならアトラスは 2048 × 2048 です。RGBA8 なら 16 MiB です。色と法線・深度の 2 枚で 32 MiB になります。BC7 などで圧縮すれば 4 分の 1 です。木の種類ごとに 1 組なので、数種類の木なら数十 MiB に収まります。

インポスターは真上や真下から見ない地上のゲームなら横方向の 8 方向だけでも十分です。簡易版は縦の軸だけで回して撮影の枚数を減らします。

!!! note "確かめた範囲"
    HLSL は `fxc` でコンパイルして、エラーが出ないことを確かめました。8 面体マッピングの相互変換と重みの和が 1 であることを手で追いました。GPU での描画は確認していません。

## 影 {#shadows}

影は描画とは別の距離で LOD を決めてかまいません。粗くても影の形は気づかれにくいからです。

- 近い木: 完全なメッシュで影を落とします。葉はアルファ テストで切り抜いて影にも反映します。
- 中くらいの木: 影用に簡略した LOD を使います。
- 遠い木: 影を落とさないかインポスターの板で近似します。

詳しい扱いは [Shadows](../../shadows/index.md) にあります。

## 木はどう作られるか {#generation}

木の 3D モデルは手で作る場合とルールから自動生成する場合があります。手で作る（DCC ツールで幹、枝、葉をモデリングする）と品質は高いですが、手間がかかります。専用のツールは樹種ごとのパラメーターから木を作って、パラメーターを変えて同じ種類の別の木をたくさん作れます。

自動生成の基礎は Prusinkiewicz と Lindenmayer の L システム（1990）と、Weber と Penn のパラメトリックな木（1995）です。この節はどちらの原典も読まずに一般的な説明として書いています。

L システムは枝分かれの規則を繰り返し適用して、枝を生やします。Weber と Penn の方法は 1 本の木を少数のパラメーターで記述します。

- 枝の分かれる数: 幹から何本の枝が出るかです。
- 枝の長さと太さの減り方: 先へ行くほど短く、細くなります。
- 枝の曲がりとねじれ: 枝がどのくらいまっすぐでないかです。
- 枝の角度: 幹からどの角度で分かれるかです。
- ランダムさ: 個体ごとのばらつきです。

パラメーターを変えると松、オーク、柳のような違う樹種が作れます。1 つの定義からランダムなバリエーションをいくつも作れるので、同じ木ばかりが並ぶ問題が軽くなります。

## よくあるミス {#mistakes}

??? failure "LOD の切り替わりで、木がポップする"
    原因は LOD A から B へ 1 フレームで入れ替えていることです。切り替えの距離の範囲を作って、2 つを同時に描きディザ フェードで入れ替えます。LOD A と B のしきい値の向きが逆になっていないと隙間や二重の描画が出ます。

??? failure "インポスターの木が、カメラを動かすとパタパタ入れ替わる"
    原因は近いフレーム 1 枚だけを選んでいることです。フレームが切り替わる瞬間に絵が急に変わります。近い 3 フレームを重心座標の重みで混ぜます。

??? failure "インポスターだけ陰影が周りと合わない"
    原因は撮影のときにライトの陰影を色に焼き込んでいることです。太陽の向きが変わってもインポスターだけが同じ陰影のままです。アルベドと法線を別々に撮って、実行時にライティングを計算します。

??? failure "森の木が全部同じ形で並んでいる"
    原因は 1 種類のモデルを同じ向きで並べていることです。数種類の木を用意して向き（`yaw`）と大きさを少しずつ変えます。生成ツールを使えば同じパラメーターから別の個体を作れます。

## これだけ覚える {#summary}

!!! abstract "まとめ"
    - [x] 近くは詳細なメッシュ、遠くはインポスターとビルボードにして、三角形を 4 桁減らします。
    - [x] LOD の切り替えは、2 つを同時に描いてディザ フェードで入れ替えます。
    - [x] インポスターは 8 面体マッピングで方向を並べて、近い 3 フレームを重心座標で混ぜます。
    - [x] 影の LOD は、描画の LOD より粗くてかまいません。

## 参考 {#references}

このページは次の資料を読まずに書きました。インポスターの式は 8 面体マッピングの一般的な定義と重心座標から、自分で書いたものです。HLSL は `fxc` でのコンパイルまで確かめています。

- Sousa, "Vegetation Procedural Animation and Shading in Crysis", GPU Gems 3, Chapter 16, 2007（幹・枝・葉の 3 層の揺れ、葉の透過）
- Weber, Penn, "Creation and Rendering of Realistic Trees", SIGGRAPH 1995
- Prusinkiewicz, Lindenmayer, "The Algorithmic Beauty of Plants", Springer, 1990（L システム）
- Décoret, Durand, Sillion, Dorsey, "Billboard Clouds for Extreme Model Simplification", ACM Transactions on Graphics (SIGGRAPH 2003)
- Brucks, "Octahedral Impostors", 2018（8 面体のマッピングを使ったインポスターの作り方）

## 関連ページ

- [Vegetation](index.md)
- [Dithered Transparency](../../translucency/alpha-test/dither.md)
