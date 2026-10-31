---
title: Light Shaft Meshes
tags:
  - 描画
---

# Light Shaft Meshes

<strong>窓から差し込む光など位置が決まっている光の筋は、半透明のメッシュ（光の柱）で作る</strong>と、最も軽く済みます。このページではメッシュによる光の柱を説明します。

!!! tip "ポイント"
    - 加算ブレンドの細長いメッシュを置く。
    - 縁と端をフェードさせる。
    - カメラに近づくと、フェードで消す。
    - 動かない光に最適。

!!! info "このページを読む前に"
    - [God Rays](index.md)（このセクション全体の地図と、読む順番）

## メッシュで光の柱を作る
<strong>固定された光の柱（窓から差す光、洞窟の天井の穴）</strong>は 半透明メッシュで作れます。

| 工夫 | 内容 |
| --- | --- |
| 形 | 光が通る形の錐台や箱のメッシュ |
| 加算ブレンド | 背景に足して光らせる |
| フレネル風の縁 | 視線と面の角度で縁を薄く（輪郭を消す） |
| 深度フェード | 床・壁との交差部を薄く（ハードな線を消す） |
| ノイズ・流れ | テクスチャを流して、ほこりの揺らぎ |
| カメラが近づくと薄く | 近すぎるとフェードアウト |

```hlsl
float edge_fade = pow(saturate(abs(dot(normal, view_dir))), 2.0);
float depth_fade = saturate((scene_depth - pixel_depth) / fade_distance);
float near_fade = saturate((pixel_depth - near_fade_start) / near_fade_range);
float dust = dust_texture.Sample(linear_wrap, uv + time * 0.02).r;
float alpha = edge_fade * depth_fade * near_fade * (0.7 + 0.3 * dust) * intensity;
return float4(light_color * alpha, 0);
```

### 作り方のコツ

メッシュの光の柱はアーティストが作るので、見た目の自由度が最も高い方式です。作るときのコツを挙げます。

形は窓の形をそのまま光の方向に押し出した錐台が基本です。太陽は平行光なので実際には窓と同じ大きさの柱になるはずですが、少し広げる（先細りでなく先広がりにする）と、光の拡散を表せます。柱を何本かの平面で構成する場合は、カメラに向かって回転するビルボードにすると、どの角度から見ても板に見えません。

強さは柱の中心を明るく縁を暗くします。上に書いたフレネル風の縁（`pow(dot(normal, view_dir), 2)`）がそれです。さらに、柱の長さ方向にも光源側を明るく、遠い側を暗くするグラデーションを付けると、光が拡散して弱まる様子が出ます。

ほこりの粒はノイズ テクスチャをゆっくり流す（UV を時間でずらす）だけで、揺らぎとして見えます。粒の動きに速度の違う 2 枚を重ねると、より自然になります。

メッシュ方式の弱点は動的な光に対応しにくいことです。太陽が動けば柱の向きも動かす必要があり、窓の前に人が立てば本来は影が出るはずですが、メッシュは対応しません。昼夜サイクルのあるゲームでは、時刻に合わせて柱の向きと色を動かす仕組みが必要になります。

## 光の筋をメッシュで描く

<strong>計算で光の筋を作る</strong>代わりに、半透明の板（メッシュ）を光の通り道に置き光の筋に見える、テクスチャを貼る方法です。アーティストが完全に制御でき、軽いので特定の場所（窓、洞窟の入口、森の木漏れ日）の演出に使われます。

## 作り方

| 要素 | 内容 |
| --- | --- |
| メッシュ | 光の筋の方向（太陽の方向）に沿って細長い、板（または円錐、箱）を置く |
| テクスチャ | 縦方向に薄れるグラデーション。横方向に縁がなめらか。縞（細かい筋）を描いてもよい |
| ブレンド | 加算ブレンド（光の、足し算）。重なる所が明るくなる |
| ライト | ない（自己発光）。太陽の色をマテリアルの色で与える |

```text
窓から、差し込む、光の筋（横から見た図）:

   窓
   │ ╲    ← 板（光の筋）。窓から、床に向かって、広がる
   │  ╲
   │   ╲
   └────╲──── 床
```

## シェーダー

```hlsl
float4 main(PSInput input) : SV_Target {
  // 縞のテクスチャ（縦方向に細かい筋）。
  float stripes = g_shaft_tex.Sample(g_linear_wrap, input.uv * float2(4.0, 1.0)).r;

  // 長さ方向（窓 → 床）に薄れる。0（窓）で 1、1（床）で 0。
  float along = 1.0 - input.uv.y;

  // 横方向（板の幅）に縁をなめらかに。中心で 1、縁で 0。
  float across = 1.0 - abs(input.uv.x * 2.0 - 1.0);
  across = smoothstep(0.0, 0.5, across);

  float intensity = stripes * along * across * g_intensity;
  return float4(g_sun_color * intensity, 1.0);                    // 加算ブレンドで、描く
}
```

<strong>3 つの要素</strong>（縞、長さ方向の減衰、横方向の縁）を 掛け合わせて、光の筋の形を作ります。縞のテクスチャで細かい筋（空気中の、ほこりが作る不均一さ）を与えます。

### ゆらぎ

光の筋がゆらゆら動くと 生きた、空気に見えます。縞の UV を時間でずらす強さをゆっくり脈打たせる。

```hlsl
float flicker = 0.85 + 0.15 * sin(g_time * 0.7 + input.world_position.x * 0.3);   // ゆっくり、脈打つ
float2 scroll = float2(g_time * 0.02, 0.0);
float stripes = g_shaft_tex.Sample(g_linear_wrap, input.uv * float2(4.0, 1.0) + scroll).r;
```

## 近くで見たとき

<strong>板</strong>は 平らな面なのでカメラが近づくと板の縁が見え不自然になります。

| 問題 | 対策 |
| --- | --- |
| 板の縁が見える | 視線に平行な向き（板を真横から見る）で縁が薄くなるよう、法線と視線の内積でフェード |
| 板に近づきすぎる | カメラに近いほどフェード アウト（ソフト パーティクルと同じ。[Soft Particles](../../translucency/blending-sorting/soft-particles.md)） |
| 床や壁との交差線 | 深度の差で、フェード（[Soft Particles](../../translucency/blending-sorting/soft-particles.md)） |

```hlsl
// 板が視線と、ほぼ平行（縁が見える角度）のとき、薄くする。
float facing = abs(dot(normalize(input.world_normal), normalize(g_camera_position - input.world_position)));
intensity *= smoothstep(0.0, 0.4, facing);
```

## 長所と短所

| | 内容 |
| --- | --- |
| 長所 | 軽い（半透明の板を数枚、描くだけ） |
| 長所 | アーティストの完全な、制御（形、色、動き） |
| 長所 | カメラ・太陽の位置に依存しない（常に同じ形で見える） |
| 短所 | 影や遮蔽物と連動しない（動く物が光を遮っても筋が変わらない） |
| 短所 | 太陽が動く（時間帯）と、板の向きを合わせる必要がある（手動） |
| 短所 | 近くで見ると板だと、分かる |
| 短所 | 配置が手作業（レベルデザイナーが置く） |

## 使いどころ

| 場面 | 判断 |
| --- | --- |
| 固定の演出（教会の窓、洞窟の穴） | 適している（光の筋が変わらない） |
| 動く太陽で屋外全体 | 不向き（[Volume-Based God Rays](volume.md) など） |
| モバイル、低スペック | 有効（計算がほぼ、不要） |

## よくあるミス

??? failure "メッシュの縁が硬く、板に見える"
    <strong>縁をフェード</strong>させる。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 加算メッシュで、手軽に光の柱

## 参考

- Mitchell, "Volumetric Light Scattering as a Post-Process", GPU Gems 3, Chapter 13, 2007（放射状ブラーによる、光の筋）
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（参加媒質、雲、霧の章）
- Microsoft Learn, "D3D11_RENDER_TARGET_BLEND_DESC"（加算ブレンド）

## 関連ページ

- [God Rays](index.md)
- [Blend State](../../translucency/blending-sorting/blend-state.md)
