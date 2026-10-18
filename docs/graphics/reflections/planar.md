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

<svg class="fig illust motion" data-fig="planar-mirror" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-planar-mirror" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">平面反射: カメラを鏡に対して反転して、もう 1 回シーンを描く</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">断面。床が鏡。本物のカメラが見る「床に映った像」は、鏡の下に置いた仮想カメラから見た景色と同じ</text>
<rect x="30" y="96" width="900" height="330" fill="#ffffff" stroke="#2563eb" stroke-width="1.8" rx="6"/>
<text x="30" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb">① 断面(灰色の線 = 鏡の床)</text>
<line x1="120.0" y1="250.0" x2="900.0" y2="250.0" stroke="#475569" stroke-width="5"/>
<line x1="345.0" y1="250.0" x2="345.0" y2="160.0" stroke="#94a3b8" stroke-width="6"/>
<circle cx="345.0" cy="160.0" r="8" fill="#e5aa28"/>
<line x1="450.0" y1="250.0" x2="450.0" y2="190.0" stroke="#94a3b8" stroke-width="6"/>
<circle cx="450.0" cy="190.0" r="8" fill="#e5aa28"/>
<circle cx="150.0" cy="124.0" r="9" fill="#1f2937"/>
<text x="150.0" y="110.0" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#1f2937">カメラ</text>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0463;0.0465;1.0000" values="0;0;1;1"/></g>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0603;0.0605;1.0000" values="0;0;1;1"/><line x1="150.0" y1="124.0" x2="263.75" y2="250.0" stroke="#e5484d" stroke-width="3"/>
<line x1="263.75" y1="250.0" x2="345.0" y2="160.0" stroke="#e5484d" stroke-width="3"/>
<circle cx="263.75" cy="250.0" r="6" fill="#e5484d"/>
<text x="263.75" y="272.0" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#e5484d">光が鏡で曲がる点 x = 4.79</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.2463;0.2465;1.0000" values="0;0;1;1"/><line x1="150.0" y1="124.0" x2="353.23" y2="250.0" stroke="#e5484d" stroke-width="3"/>
<line x1="353.23" y1="250.0" x2="450.0" y2="190.0" stroke="#e5484d" stroke-width="3"/>
<circle cx="353.23" cy="250.0" r="6" fill="#e5484d"/>
<text x="353.2258064516129" y="272.0" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#e5484d">光が鏡で曲がる点 x = 7.77</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.4649;0.4651;1.0000" values="0;0;1;1"/><circle cx="150.0" cy="376.0" r="9" fill="#94a3b8" stroke="#1f2937" stroke-width="2" stroke-dasharray="3 3"/>
<text x="150.0" y="398.0" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#64748b">仮想カメラ(鏡の下に反転)</text>
<circle cx="345.0" cy="340.0" r="8" fill="#fde68a" stroke="#f59e0b" stroke-width="2"/>
<line x1="150.0" y1="376.0" x2="345.0" y2="340.0" stroke="#2ea043" stroke-width="3" stroke-dasharray="7 5"/>
<text x="357.0" y="345.0" text-anchor="start" style="font-size:12px;font-weight:700;fill:#92400e">像</text>
<circle cx="450.0" cy="310.0" r="8" fill="#fde68a" stroke="#f59e0b" stroke-width="2"/>
<line x1="150.0" y1="376.0" x2="450.0" y2="310.0" stroke="#2ea043" stroke-width="3" stroke-dasharray="7 5"/>
<text x="462.0" y="315.0" text-anchor="start" style="font-size:12px;font-weight:700;fill:#92400e">像</text>
</g>
<text x="40" y="452" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">鏡で曲がる点(2 つの物体):</text>
<text x="270" y="452" text-anchor="start" style="font-size:14px;font-weight:700;fill:#e5484d" opacity="0">x = 4.79 と 7.77<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.2510;0.2512;1.0000" values="0;0;1;1"/></text>
<text x="470" y="452" text-anchor="start" style="font-size:14px;font-weight:700;fill:#2ea043" opacity="0">仮想カメラの直線と交わる点: 同じ値 (一致)<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.5114;0.5116;1.0000" values="0;0;1;1"/></text>
<rect x="30" y="470" width="900" height="48" fill="#ffffff" stroke="#7c3aed" stroke-width="1.8" rx="6"/>
<text x="44" y="500" text-anchor="start" style="font-size:14px;font-weight:700;fill:#7c3aed" opacity="0">描画回数: 反射なし 120 → 平面反射 240(シーンを 2 回描く)/ SSR は 120 + 画面全体 1 回<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.6045;0.6047;1.0000" values="0;0;1;1"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">床の鏡に映る像は、鏡の下にある「もう 1 つの世界」を見ているのと同じ<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0463;0.0465;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">本物のカメラから見ると、光は鏡で曲がって物体へ届く<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0463;0.0465;0.4649;0.4651;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">鏡の下に、カメラを反転して置くと、同じ線が、まっすぐ物体の像へ伸びる<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.4649;0.4651;0.6045;0.6047;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">反転したカメラで、もう 1 回シーンを描く(描画 2 倍)。完全に正確だが、鏡が平面のときだけ<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.6045;0.6047;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:planar-mirror:end -->

## 鏡映の行列

**平面 `n·x + d = 0`**（n は単位法線）に関する、**鏡映行列**（行ベクトル規約）は、次のとおりです。

<div class="formula">M_reflect = I − 2 · [n; d] [n; 0]ᵀ　（4×4 の行列。具体的な成分は下）</div>

行列の成分は、次のとおりです。左上の 3×3 部分は `I − 2 n nᵀ`（成分で書くと `δ_ij − 2 n_i n_j`）です。4 行目（平行移動の部分）は `(−2 d n_x, −2 d n_y, −2 d n_z, 1)` です。

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

この対処は 2 つです。反射パスの間だけ、カリング設定を反転します（`FrontCounterClockwise` を逆にする、あるいは `CullMode` を `FRONT` にする）。法線は、鏡映行列で変換すれば（位置と同じ行列なので）、そのままで正しくなります。

## 斜めの近クリップ面（Oblique Clipping）

**反射面より下**（水面の下の地面・川底）は、**鏡映カメラから見ると反射面の手前**に来ます。**これを描くと反射に「水面の下の物」が映り込み**ます。**反射面より下は描かない**必要があります。

反射面より下を描かない方法は、2 つあります。1 つ目は<strong>ユーザー クリップ面</strong>で、`SV_ClipDistance` を使い、反射面の下のピクセルを切ります（頂点シェーダーで距離を出力）。簡単ですが、頂点シェーダーの変更が必要です。2 つ目は<strong>斜めの近クリップ面</strong>（Lengyel のテクニック）で、射影行列を書き換えて、近クリップ面を反射面に合わせます。シェーダーを変更しなくてよい代わりに、遠クリップ面や深度の精度が少し変わります。

**射影行列の書き換え**は、「近クリップ面の式を反射面にする」ものです（計算の詳細は参考の資料を参照）。**深度の精度がわずかに下がる**ので**反射パスだけ**で使います。

## 反射面を描くときの使い方

**スクリーン座標**で反射テクスチャを引きます。

```hlsl
float2 uv = clip_pos.xy / clip_pos.w * float2(0.5, -0.5) + 0.5;
float3 reflection = reflect_tex.Sample(linear_sampler, uv + distortion).rgb;
float fresnel = FresnelSchlick(saturate(dot(N, V)), 0.02);
float3 color = lerp(refraction_color, reflection, fresnel);
```

コードの要点です。`uv = clip.xy / clip.w` は、反射面のピクセルが画面のどこにあるかを示します。鏡映カメラの画像は、通常のカメラと同じ画面位置で対応します。`distortion` は、水面の波の法線で uv を少しずらし、揺らぎを出します。フレネルは、斜めから見るほど反射が強くなる効果です（水の `F0` は約 0.02 です）。

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
