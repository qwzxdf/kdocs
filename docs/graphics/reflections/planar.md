---
title: Planar Reflections
tags:
  - 描画
---

# Planar Reflections

**平面反射**（Planar Reflection）は、<strong>鏡や水面のような「平らな反射面」</strong>で、**反射面の向こう側にカメラを置いて**、**シーンをもう一度描き直し**、その画像を反射として貼る方式です。**反射が完全に正確**（本物の鏡と同じ）で、**画面外の物も裏側も映ります**。その代わりに**シーンの描画がほぼ倍**になります。**水面・鏡・磨かれた床**など、**平面の反射が主役**の場面で、今も使われます。

!!! tip "ポイント"
    - <strong>反射面を軸にカメラを鏡映</strong>する。<strong>その視点からシーンを描いて、テクスチャに保存</strong>。
    - 反射面を描くとき、<strong>画面座標でそのテクスチャを引く</strong>。
    - 鏡映すると<strong>三角形の巻き方向が反転する</strong>。<strong>カリングの設定を反転</strong>。
    - <strong>反射面より下の物は描いてはいけない</strong>。<strong>斜めの近クリップ面</strong>（oblique clipping）で切る。
    - <strong>粗い面の反射</strong>は、<strong>ぼかす</strong>（距離に応じて）。
    - <strong>反射面が平らであることが前提</strong>。曲面・でこぼこには使えない。

## 仕組み

反射を、「**鏡の向こう側にある、もう 1 つの世界を覗き込んでいる**」と見なします。**カメラを反射面を挟んで反対側に置いた**（鏡映した）位置から、シーンを描けば、**鏡に映る景色**が得られます。

<svg class="fig illust" viewBox="0 0 798 300" role="img" aria-label="平面反射のカメラ鏡映">
<text x="20" y="24" class="fig-title">反射面を軸に、カメラを鏡映する。鏡映カメラから描いた画像が、反射として貼られる</text>
<line x1="60" y1="160" x2="720" y2="160" stroke="currentColor" stroke-width="5"/><text x="620" y="152" style="font-size:12px;font-weight:700">反射面（水面など）</text>
<circle cx="180" cy="80" r="9" fill="#4c8bf5"/><text x="150" y="62" style="font-size:12px">カメラ</text>
<circle cx="180" cy="240" r="9" fill="rgba(76,139,245,0.4)" stroke="#4c8bf5" stroke-dasharray="3 2"/><text x="120" y="268" style="font-size:12px">鏡映カメラ</text>
<line x1="180" y1="89" x2="180" y2="231" stroke="currentColor" stroke-dasharray="4 4"/>
<polygon points="400,160 440,100 480,160" fill="rgba(46,160,67,0.4)" stroke="currentColor" stroke-width="2"/><text x="415" y="92" style="font-size:12px">物体</text>
<polygon points="400,160 440,220 480,160" fill="rgba(46,160,67,0.15)" stroke="currentColor" stroke-dasharray="5 3"/><text x="418" y="240" style="font-size:12px">鏡像（反射）</text>
<line x1="180" y1="80" x2="395" y2="165" stroke="#e5484d" stroke-width="2.5"/>
<line x1="395" y1="165" x2="440" y2="215" stroke="#e5484d" stroke-width="2.5" stroke-dasharray="5 3"/>
<line x1="180" y1="240" x2="440" y2="215" stroke="#e5484d" stroke-width="1.5" stroke-dasharray="2 3"/>
<text x="520" y="200" style="font-size:12px">カメラから見た反射 ＝ 鏡映カメラから見た景色</text>
</svg>

## 手順

| 手順 | 内容 |
| --- | --- |
| **① 鏡映カメラを作る** | 反射面（平面）に対して、カメラの位置と向きを**鏡映** |
| **② 近クリップ面を反射面に合わせる** | **反射面より下**（鏡の裏側）にある物を**描かない**ため |
| **③ 反射用のテクスチャに描く** | 鏡映カメラから、<strong>シーン（不透明物）</strong>を描く。解像度は**画面と同じか、半分** |
| **④ 反射面を描く** | <strong>画面上の位置（スクリーン座標）</strong>で、反射テクスチャを引く。**フレネル・屈折・波の歪み**と合成 |

<!-- fig:planar-mirror:begin -->

<svg class="fig illust motion" data-fig="planar-mirror" viewBox="0 0 780 460" role="img"><rect x="0" y="0" width="780" height="460" rx="14" fill="#ffffff"/>
<defs><marker id="arr-planar-mirror" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">平面反射:鏡の裏側に、鏡映したカメラを置いて、もう一度描く</text>
<rect x="60" y="246" width="660" height="8" fill="#38bdf8"/>
<text x="700" y="238" text-anchor="end" style="font-size:12px;font-weight:700;fill:#0284c7">鏡（水面）</text>
<rect x="60" y="254" width="660" height="150" fill="#e0f2fe" fill-opacity="0.5"/>
<polygon points="498,210 542,210 520,160" fill="#b8794b" stroke="#7a4b2a" stroke-width="2"/>
<polygon points="498,290 542,290 520,340" fill="#b8794b" fill-opacity="0.35" stroke="#7a4b2a" stroke-width="1.5" stroke-dasharray="4 3"/>
<text x="550" y="330" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">鏡像の物体</text>
<circle cx="140" cy="110" r="11" fill="#2563eb" stroke="#ffffff" stroke-width="2"><animate attributeName="cx" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0593;0.2963;0.5556;0.7778;1.0000" values="140;140;300;420;140;140"/></circle>
<circle cx="140" cy="390" r="11" fill="#2563eb" fill-opacity="0.35" stroke="#2563eb" stroke-width="2" stroke-dasharray="4 3"><animate attributeName="cx" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0593;0.2963;0.5556;0.7778;1.0000" values="140;140;300;420;140;140"/></circle>
<text x="160" y="104" text-anchor="start" style="font-size:12px;font-weight:700;fill:#2563eb">カメラ</text>
<text x="160" y="396" text-anchor="start" style="font-size:12px;font-weight:700;fill:#2563eb">鏡映したカメラ</text>
<line x1="140" y1="110" x2="300" y2="250" stroke="#2563eb" stroke-width="2.5"><animate attributeName="x1" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0593;0.2963;0.5556;0.7778;1.0000" values="140;140;300;420;140;140"/><animate attributeName="x2" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0590;0.0593;0.2963;0.5556;0.7778;1.0000" values="300;300;393.33;446.67;486.67;393.33;393.33"/></line>
<line x1="300" y1="250" x2="520" y2="180" stroke="#2563eb" stroke-width="2.5"><animate attributeName="x1" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0590;0.0593;0.2963;0.5556;0.7778;1.0000" values="300;300;393.33;446.67;486.67;393.33;393.33"/></line>
<line x1="140" y1="390" x2="520" y2="330" stroke="#2563eb" stroke-width="1.5" stroke-dasharray="5 4"><animate attributeName="x1" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0593;0.2963;0.5556;0.7778;1.0000" values="140;140;300;420;140;140"/></line>
<text x="40" y="60" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">カメラを動かすと、鏡映カメラも、鏡の反対側で同じ動きをする<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;1.0000;1.0000" values="1;1;0"/></text>
<text x="40" y="440" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b" opacity="0">鏡映カメラで普通にシーンを描く → それがそのまま、鏡に映る絵。実線の経路 = 鏡映カメラの点線の経路（同じ点に当たる）。<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;1.0000;1.0000" values="1;1;0"/></text>
</svg>

<!-- fig:planar-mirror:end -->

## 鏡映の行列

**平面 `n·x + d = 0`**（n は単位法線）に関する、**鏡映行列**（行ベクトル規約）は、次のとおりです。

<div class="formula">M_reflect = I − 2 · [n; d] [n; 0]ᵀ　（4×4 の行列。具体的な成分は下）</div>

| 成分 | 値 |
| --- | --- |
| **左上 3×3** | `I − 2 n nᵀ`（成分 `δ_ij − 2 n_i n_j`） |
| <strong>4 行目（平行移動）</strong> | `(−2 d n_x, −2 d n_y, −2 d n_z, 1)` |

```cpp
Matrix MakeReflectionMatrix(const Vector3& n, float d) {
  return Matrix(
      1 - 2 * n.x * n.x, -2 * n.x * n.y, -2 * n.x * n.z, 0,
      -2 * n.y * n.x, 1 - 2 * n.y * n.y, -2 * n.y * n.z, 0,
      -2 * n.z * n.x, -2 * n.z * n.y, 1 - 2 * n.z * n.z, 0,
      -2 * d * n.x, -2 * d * n.y, -2 * d * n.z, 1);
}
```

**水面が `y = 高さ`**の水平な平面（`n = (0, 1, 0)`、`d = −高さ`）の場合は<strong>ほぼ「y を水面に対して反転する」</strong>だけです。

```cpp
Matrix reflect_view = MakeReflectionMatrix(plane_normal, plane_d) * camera_view;
```

**ワールド行列を鏡映してから**、通常のビュー・プロジェクションを掛けます。

## 巻き方向の反転

**鏡映**は**左右（または上下）を反転する変換**なので**三角形の巻き方向が逆**になります（[座標系](../../gamemath/coordinate-systems.md)の鏡像変換と同じ）。そのまま描くと**表と裏が逆**になり、**カリングで見えるはずの面が消えます**。

| 対処 | 内容 |
| --- | --- |
| **カリング設定を反転** | 反射パスの間だけ、`FrontCounterClockwise` を逆にする（または `CullMode` を `FRONT` に） |
| **法線の扱い** | 鏡映行列で変換した法線は、**そのままで正しい**（位置と同じ行列） |

## 斜めの近クリップ面（Oblique Clipping）

**反射面より下**（水面の下の地面・川底）は、**鏡映カメラから見ると反射面の手前**に来ます。**これを描くと反射に「水面の下の物」が映り込み**ます。**反射面より下は描かない**必要があります。

| 方法 | 説明 |
| --- | --- |
| **ユーザー クリップ面** | `SV_ClipDistance` で、**反射面の下**のピクセルを切る（頂点シェーダーで距離を出力）。**簡単だが頂点シェーダーの変更が必要** |
| **斜めの近クリップ面** | **射影行列を書き換えて**、**近クリップ面を反射面に合わせる**（Lengyel のテクニック）。**シェーダーの変更なし**。ただし、**遠クリップ面や深度の精度が少し変わる** |

**射影行列の書き換え**は、「近クリップ面の式を反射面にする」ものです（計算の詳細は参考の資料を参照）。**深度の精度がわずかに下がる**ので**反射パスだけ**で使います。

## 反射面を描くときの使い方

**スクリーン座標**で反射テクスチャを引きます。

```hlsl
float2 uv = clip_pos.xy / clip_pos.w * float2(0.5, -0.5) + 0.5;
float3 reflection = reflect_tex.Sample(linear_sampler, uv + distortion).rgb;
float fresnel = FresnelSchlick(saturate(dot(N, V)), 0.02);
float3 color = lerp(refraction_color, reflection, fresnel);
```

| 点 | 説明 |
| --- | --- |
| **`uv = clip.xy / clip.w`** | 反射面のピクセルが**画面のどこにあるか**。**鏡映カメラの画像は、通常のカメラと同じ画面位置**で対応 |
| **`distortion`** | 水面の**波の法線**で、**uv を少しずらす**と揺らぎが出る |
| **フレネル** | 斜めから見るほど反射が強い（水の `F0` は約 0.02） |

!!! note "鏡映カメラの画面位置"
    反射テクスチャは、**鏡映カメラの視点**で描いたものです。**鏡映すると左右が反転する**ことを、行列（ビュー）が吸収しているので**通常のカメラと同じ画面位置**で引けば、正しい位置に映ります。**射影行列は通常のものと同じ**（斜めクリップを除く）です。

## 粗さとぼかし

平面反射は**完全な鏡**の反射です。<strong>粗い面（磨りガラス・濡れた石）</strong>では反射は**ぼけて**見えるべきです。

| 方法 | 内容 |
| --- | --- |
| **単純なぼかし** | 反射テクスチャ全体を**一定の大きさ**でぼかす（粗さに比例） |
| **距離に応じたぼかし** | **反射面から、映っている物までの距離**が遠いほど、**大きくぼかす**（現実の粗い鏡の振る舞い）。**反射パスで深度を一緒に保存**しておく |
| **ミップマップ** | 反射テクスチャのミップを作り、**粗さに応じて、ミップを選ぶ** |
| **コーン トレース風** | 距離に応じたミップ選択（SSR の考え方に近い。[SSR の基礎](ssr-basics/index.md)） |

## コストと工夫

**平面反射はシーンをもう 1 回描く**ので**描画コストがほぼ倍**になります。

| 工夫 | 内容 |
| --- | --- |
| **解像度を下げる** | 反射テクスチャを**半分の解像度**にする |
| **描く物を絞る** | **遠景・小さな物・影・ポストプロセス**を省く。**LOD を下げる** |
| **反射面が見えているときだけ描く** | **視錐台カリング**で反射面が画面に入っていないなら、描かない |
| **更新頻度を下げる** | 数フレームに 1 回だけ更新する（動きが遅い場合） |
| **キューブマップで代用** | **遠景はプローブ**（[プローブ](probes/index.md)） |
| **反射用の簡易シェーダー** | **ライティングを簡略化** |

## 複数の平面・傾いた面

| 状況 | 対応 |
| --- | --- |
| <strong>複数の反射面（高さが違う水面）</strong> | **面ごとに反射パスが必要**。数が増えると非常に重い |
| **傾いた鏡** | 鏡映行列と斜めクリップでそのまま対応できる |
| **曲面・でこぼこの面** | **平面反射は使えない**（SSR・プローブ・レイトレに任せる） |
| **反射の中の反射**（向かい合う鏡） | 再帰が必要。通常は、**1 回だけ**に制限 |

## 長所と短所

| 長所 | 短所 |
| --- | --- |
| **完全に正確**（画面外・裏側も映る） | **シーンをもう 1 回描く**ので重い |
| **ノイズがない**（確定的） | **平面のみ**。曲面・でこぼこに不向き |
| **実装がほぼ「描き直す」だけ** | **粗さのぼけ**を別途工夫する必要がある |
| **粗い物体でも高解像度で映る** | **複数の面でコストが増える** |

## 使いどころ

| 場面 | 方式 |
| --- | --- |
| <strong>水面（湖・海・水たまり）</strong> | 平面反射 ＋ 波の歪み（[水](../index.md)）。または SSR |
| <strong>鏡（部屋・車のミラー）</strong> | 平面反射（画像の質が重要） |
| **磨かれた床** | 平面反射、または SSR・プローブで安く |
| **広い範囲の濡れた路面** | SSR ＋ プローブ（平面反射は面が多く重い） |

## よくあるミス

??? failure "反射パスで、カリングの設定を反転せず、反射が消える・内側が見える"
    反射パスの間だけ、巻き方向（`FrontCounterClockwise`）を**反転**します。

??? failure "反射面より下の物が、反射に映り込む"
    **斜めの近クリップ面**か、**クリップ距離**で反射面より下を切ります。

??? failure "反射テクスチャを、画面と別の座標で引いてずれる"
    **クリップ座標 `/ w`** から、**スクリーン座標**を作って引きます。

??? failure "全てのフレームで、フル解像度・フル品質で反射を描いて、重い"
    **半分の解像度・LOD の削減・簡易シェーダー**で軽くします。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 平面反射 ＝ <strong>反射面でカメラを鏡映し、シーンを描き直して、反射テクスチャにする</strong>
    - [x] <strong>画面外・裏側も正確に映る</strong>。<strong>平面のみ</strong>。<strong>描画コストがほぼ倍</strong>
    - [x] <strong>巻き方向を反転</strong>。<strong>反射面より下は、斜めの近クリップ面で切る</strong>
    - [x] <strong>粗さ</strong>は、距離に応じたぼかし・ミップで
    - [x] <strong>解像度・LOD・更新頻度</strong>で軽くする

## 参考

- Lengyel, "Oblique View Frustum Depth Projection and Clipping"（Journal of Game Development, 2005）

## 関連ページ

- [Reflections](index.md)
- [リフレクション プローブ](probes/index.md)
- [SSR の基礎](ssr-basics/index.md)
- [座標系](../../gamemath/coordinate-systems.md)
- [描画の最適化（詳細）](../../rendering/index.md)
