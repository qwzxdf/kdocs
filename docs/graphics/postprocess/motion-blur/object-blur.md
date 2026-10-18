---
title: Object Motion Blur
tags:
  - 描画
---

# Object Motion Blur

<strong>動く物体（走るキャラクター・飛ぶ弾・回るプロペラ）</strong>は、**カメラが静止していても、動きに沿ってぶれます**。**オブジェクト モーション ブラー**は、**物体ごとの速度**を**速度バッファに書き込み**、**その速度に沿って、物体と周りをぼかす**ものです。**カメラ ブラーに比べて、重く、破綻しやすい**ので**実装の工夫**が**必要**です。このページでは、**物体の速度の出し方・回転する物体・スキニング・輪郭のにじみ・描画順・対象の絞り込み**を説明します。

!!! tip "ポイント"
    - オブジェクト ブラー ＝ <strong>動く物体の速度</strong>に<strong>沿って、その物体（と周りの背景）をぼかす</strong>。
    - 速度は<strong>描画時に前フレームの行列で計算して、速度バッファへ</strong>（[Velocity Buffer](velocity-buffer.md)）。
    - <strong>回転する物体</strong>（プロペラ・タイヤ）は<strong>頂点ごとに速度が違う</strong>ので、<strong>頂点シェーダーで正しく計算</strong>。
    - <strong>キャラクター</strong>は<strong>前フレームの骨の姿勢</strong>が必要。
    - <strong>速い物体の輪郭の外側にも、尾が伸びる</strong>ように<strong>周りの速度を考慮</strong>（[Tile Max Velocity](tile-max.md)）。
    - <strong>対象を絞る</strong>（<strong>重要な物体・プレイヤー周辺</strong>）と<strong>コストが下がる</strong>。

## 物体の速度

**物体の各頂点について、前フレームの位置と今の位置を計算**し、**その差をピクセル シェーダーで速度として出力**します（[Velocity Buffer](velocity-buffer.md)）。

動きの種類ごとの速度の特徴です。並進（移動）は、物体全体でほぼ一様です。回転（プロペラ・タイヤ）は、中心から遠い点ほど速く、頂点ごとに違います。変形（スキニング）は、骨ごとに違い、手足の先が速くなります。

**物体全体で 1 つの速度**だと、**回転や変形が表現できません**。**頂点ごとの前フレームの位置から、画素ごとの速度**を**補間**します。

<!-- fig:object-blur-rotation:begin -->

<svg class="fig illust motion" data-fig="object-blur-rotation" viewBox="0 0 780 400" role="img"><rect x="0" y="0" width="780" height="400" rx="14" fill="#ffffff"/>
<defs><marker id="arr-object-blur-rotation" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">回転する物体:中心は動かず、外側ほど速い ＝ ブレも長い</text>
<text x="200" y="70" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#64748b">速度ベクトル（画素ごと）</text>
<circle cx="200" cy="210" r="120" fill="#f1f5f9" stroke="#94a3b8" stroke-width="2"/>
<text x="580" y="70" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#64748b">結果のブレ</text>
<circle cx="580" cy="210" r="120" fill="#f1f5f9" stroke="#94a3b8" stroke-width="2"/>
<g opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0797;0.0800;1.0000" values="0;0;1;1"/><circle cx="230.0" cy="210.0" r="4" fill="#2ea043"/>
<line x1="230.0" y1="210.0" x2="230.0" y2="226.5" stroke="#2ea043" stroke-width="3"/>
<polygon points="230.0,226.5 225.0,217.5 235.0,217.5" fill="#2ea043"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0797;0.0800;1.0000" values="0;0;1;1"/><circle cx="185.0" cy="235.98" r="4" fill="#2ea043"/>
<line x1="185.0" y1="235.98" x2="170.71" y2="227.73" stroke="#2ea043" stroke-width="3"/>
<polygon points="170.71,227.73 181.0,227.9 176.0,236.56" fill="#2ea043"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0797;0.0800;1.0000" values="0;0;1;1"/><circle cx="185.0" cy="184.02" r="4" fill="#2ea043"/>
<line x1="185.0" y1="184.02" x2="199.29" y2="175.77" stroke="#2ea043" stroke-width="3"/>
<polygon points="199.29,175.77 194.0,184.6 189.0,175.94" fill="#2ea043"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1757;0.1760;1.0000" values="0;0;1;1"/><circle cx="265.78" cy="233.94" r="4" fill="#e5aa28"/>
<line x1="265.78" y1="233.94" x2="252.61" y2="270.12" stroke="#e5aa28" stroke-width="3"/>
<polygon points="252.61,270.12 250.99,259.95 260.39,263.37" fill="#e5aa28"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1757;0.1760;1.0000" values="0;0;1;1"/><circle cx="146.38" cy="255.0" r="4" fill="#e5aa28"/>
<line x1="146.38" y1="255.0" x2="121.63" y2="225.5" stroke="#e5aa28" stroke-width="3"/>
<polygon points="121.63,225.5 131.24,229.18 123.58,235.61" fill="#e5aa28"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1757;0.1760;1.0000" values="0;0;1;1"/><circle cx="187.84" cy="141.06" r="4" fill="#e5aa28"/>
<line x1="187.84" y1="141.06" x2="225.76" y2="134.38" stroke="#e5aa28" stroke-width="3"/>
<polygon points="225.76,134.38 217.76,140.86 216.03,131.02" fill="#e5aa28"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.2717;0.2720;1.0000" values="0;0;1;1"/><circle cx="284.26" cy="280.71" r="4" fill="#e5484d"/>
<line x1="284.26" y1="280.71" x2="245.38" y2="327.05" stroke="#e5484d" stroke-width="3"/>
<polygon points="245.38,327.05 247.33,316.94 254.99,323.37" fill="#e5484d"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.2717;0.2720;1.0000" values="0;0;1;1"/><circle cx="96.63" cy="247.62" r="4" fill="#e5484d"/>
<line x1="96.63" y1="247.62" x2="75.94" y2="190.77" stroke="#e5484d" stroke-width="3"/>
<polygon points="75.94,190.77 83.72,197.52 74.32,200.94" fill="#e5484d"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.2717;0.2720;1.0000" values="0;0;1;1"/><circle cx="219.1" cy="101.67" r="4" fill="#e5484d"/>
<line x1="219.1" y1="101.67" x2="278.68" y2="112.18" stroke="#e5484d" stroke-width="3"/>
<polygon points="278.68,112.18 268.95,115.54 270.69,105.69" fill="#e5484d"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.3997;0.4000;1.0000" values="0;0;1;1"/><line x1="580" y1="210" x2="698.83" y2="193.3" stroke="#1f2937" stroke-width="3" opacity="0.1"/>
<line x1="580" y1="210" x2="596.7" y2="328.83" stroke="#1f2937" stroke-width="3" opacity="0.1"/>
<line x1="580" y1="210" x2="461.17" y2="226.7" stroke="#1f2937" stroke-width="3" opacity="0.1"/>
<line x1="580" y1="210" x2="563.3" y2="91.17" stroke="#1f2937" stroke-width="3" opacity="0.1"/>
<line x1="580" y1="210" x2="699.43" y2="198.29" stroke="#1f2937" stroke-width="3" opacity="0.1"/>
<line x1="580" y1="210" x2="591.71" y2="329.43" stroke="#1f2937" stroke-width="3" opacity="0.1"/>
<line x1="580" y1="210" x2="460.57" y2="221.71" stroke="#1f2937" stroke-width="3" opacity="0.1"/>
<line x1="580" y1="210" x2="568.29" y2="90.57" stroke="#1f2937" stroke-width="3" opacity="0.1"/>
<line x1="580" y1="210" x2="699.81" y2="203.3" stroke="#1f2937" stroke-width="3" opacity="0.1"/>
<line x1="580" y1="210" x2="586.7" y2="329.81" stroke="#1f2937" stroke-width="3" opacity="0.1"/>
<line x1="580" y1="210" x2="460.19" y2="216.7" stroke="#1f2937" stroke-width="3" opacity="0.1"/>
<line x1="580" y1="210" x2="573.3" y2="90.19" stroke="#1f2937" stroke-width="3" opacity="0.1"/>
<line x1="580" y1="210" x2="699.99" y2="208.32" stroke="#1f2937" stroke-width="3" opacity="0.1"/>
<line x1="580" y1="210" x2="581.68" y2="329.99" stroke="#1f2937" stroke-width="3" opacity="0.1"/>
<line x1="580" y1="210" x2="460.01" y2="211.68" stroke="#1f2937" stroke-width="3" opacity="0.1"/>
<line x1="580" y1="210" x2="578.32" y2="90.01" stroke="#1f2937" stroke-width="3" opacity="0.1"/>
<line x1="580" y1="210" x2="699.95" y2="213.35" stroke="#1f2937" stroke-width="3" opacity="0.1"/>
<line x1="580" y1="210" x2="576.65" y2="329.95" stroke="#1f2937" stroke-width="3" opacity="0.1"/>
<line x1="580" y1="210" x2="460.05" y2="206.65" stroke="#1f2937" stroke-width="3" opacity="0.1"/>
<line x1="580" y1="210" x2="583.35" y2="90.05" stroke="#1f2937" stroke-width="3" opacity="0.1"/>
<line x1="580" y1="210" x2="699.71" y2="218.37" stroke="#1f2937" stroke-width="3" opacity="0.1"/>
<line x1="580" y1="210" x2="571.63" y2="329.71" stroke="#1f2937" stroke-width="3" opacity="0.1"/>
<line x1="580" y1="210" x2="460.29" y2="201.63" stroke="#1f2937" stroke-width="3" opacity="0.1"/>
<line x1="580" y1="210" x2="588.37" y2="90.29" stroke="#1f2937" stroke-width="3" opacity="0.1"/>
<line x1="580" y1="210" x2="699.25" y2="223.38" stroke="#1f2937" stroke-width="3" opacity="0.1"/>
<line x1="580" y1="210" x2="566.62" y2="329.25" stroke="#1f2937" stroke-width="3" opacity="0.1"/>
<line x1="580" y1="210" x2="460.75" y2="196.62" stroke="#1f2937" stroke-width="3" opacity="0.1"/>
<line x1="580" y1="210" x2="593.38" y2="90.75" stroke="#1f2937" stroke-width="3" opacity="0.1"/>
<line x1="580" y1="210" x2="698.59" y2="228.36" stroke="#1f2937" stroke-width="3" opacity="0.1"/>
<line x1="580" y1="210" x2="561.64" y2="328.59" stroke="#1f2937" stroke-width="3" opacity="0.1"/>
<line x1="580" y1="210" x2="461.41" y2="191.64" stroke="#1f2937" stroke-width="3" opacity="0.1"/>
<line x1="580" y1="210" x2="598.36" y2="91.41" stroke="#1f2937" stroke-width="3" opacity="0.1"/>
<line x1="580" y1="210" x2="697.71" y2="233.31" stroke="#1f2937" stroke-width="3" opacity="0.1"/>
<line x1="580" y1="210" x2="556.69" y2="327.71" stroke="#1f2937" stroke-width="3" opacity="0.1"/>
<line x1="580" y1="210" x2="462.29" y2="186.69" stroke="#1f2937" stroke-width="3" opacity="0.1"/>
<line x1="580" y1="210" x2="603.31" y2="92.29" stroke="#1f2937" stroke-width="3" opacity="0.1"/>
<line x1="580" y1="210" x2="696.64" y2="238.22" stroke="#1f2937" stroke-width="3" opacity="0.1"/>
<line x1="580" y1="210" x2="551.78" y2="326.64" stroke="#1f2937" stroke-width="3" opacity="0.1"/>
<line x1="580" y1="210" x2="463.36" y2="181.78" stroke="#1f2937" stroke-width="3" opacity="0.1"/>
<line x1="580" y1="210" x2="608.22" y2="93.36" stroke="#1f2937" stroke-width="3" opacity="0.1"/>
<line x1="580" y1="210" x2="695.35" y2="243.08" stroke="#1f2937" stroke-width="3" opacity="0.1"/>
<line x1="580" y1="210" x2="546.92" y2="325.35" stroke="#1f2937" stroke-width="3" opacity="0.1"/>
<line x1="580" y1="210" x2="464.65" y2="176.92" stroke="#1f2937" stroke-width="3" opacity="0.1"/>
<line x1="580" y1="210" x2="613.08" y2="94.65" stroke="#1f2937" stroke-width="3" opacity="0.1"/>
<line x1="580" y1="210" x2="693.87" y2="247.88" stroke="#1f2937" stroke-width="3" opacity="0.1"/>
<line x1="580" y1="210" x2="542.12" y2="323.87" stroke="#1f2937" stroke-width="3" opacity="0.1"/>
<line x1="580" y1="210" x2="466.13" y2="172.12" stroke="#1f2937" stroke-width="3" opacity="0.1"/>
<line x1="580" y1="210" x2="617.88" y2="96.13" stroke="#1f2937" stroke-width="3" opacity="0.1"/>
<line x1="580" y1="210" x2="692.18" y2="252.61" stroke="#1f2937" stroke-width="3" opacity="0.1"/>
<line x1="580" y1="210" x2="537.39" y2="322.18" stroke="#1f2937" stroke-width="3" opacity="0.1"/>
<line x1="580" y1="210" x2="467.82" y2="167.39" stroke="#1f2937" stroke-width="3" opacity="0.1"/>
<line x1="580" y1="210" x2="622.61" y2="97.82" stroke="#1f2937" stroke-width="3" opacity="0.1"/>
<line x1="580" y1="210" x2="690.3" y2="257.27" stroke="#1f2937" stroke-width="3" opacity="0.1"/>
<line x1="580" y1="210" x2="532.73" y2="320.3" stroke="#1f2937" stroke-width="3" opacity="0.1"/>
<line x1="580" y1="210" x2="469.7" y2="162.73" stroke="#1f2937" stroke-width="3" opacity="0.1"/>
<line x1="580" y1="210" x2="627.27" y2="99.7" stroke="#1f2937" stroke-width="3" opacity="0.1"/>
</g>
<g opacity="1"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.3997;0.4000;1.0000" values="1;1;0;0"/><line x1="580" y1="210" x2="700.0" y2="210.0" stroke="#1f2937" stroke-width="4"/>
<line x1="580" y1="210" x2="580.0" y2="330.0" stroke="#1f2937" stroke-width="4"/>
<line x1="580" y1="210" x2="460.0" y2="210.0" stroke="#1f2937" stroke-width="4"/>
<line x1="580" y1="210" x2="580.0" y2="90.0" stroke="#1f2937" stroke-width="4"/>
</g>
<circle cx="580" cy="210" r="14" fill="#1f2937"/>
<text x="40" y="372" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">ホイールが回っている<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0797;0.0800;1.0000" values="1;1;0;0"/></text>
<text x="40" y="372" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">速度 ＝ 角速度 × 中心からの距離。外側ほど矢印が長い<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0797;0.0800;0.3997;0.4000;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="372" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">→ 中心はくっきり、外縁ほど長くブレる（物体の速度バッファで表現）<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.3997;0.4000;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:object-blur-rotation:end -->

## 回転する物体

**プロペラやタイヤ**は、**回転軸から離れた点ほど、大きな速度**です。**頂点シェーダーで前フレームの回転を適用した位置を計算**すれば、**自動的に頂点ごとの速度**が**得られます**。

```hlsl
float4 current_position = mul(mul(float4(local_position, 1.0), world), view_projection);
float4 previous_position = mul(mul(float4(local_position, 1.0), previous_world), previous_view_projection);
```

<strong>注意：回転が大きい（1 フレームで 90° 以上）</strong>と、**前後の位置の差が実際の弧の動きを表さず、速度の向きが不正確**になります。**速い回転はブラーを円弧に沿わせる**特別な処理が**必要**です（**多くのゲームは、回転の大きい物体のブラーを弱める**）。

## スキニング

**キャラクター**は、<strong>骨の行列で頂点を動かす（スキニング）</strong>ので**前フレームの骨の姿勢**が**必要**です。

| 方式 | 内容 | コスト |
| --- | --- | --- |
| **前フレームのボーン行列で、もう一度スキニング** | **頂点シェーダーで今・前の 2 回** | **頂点処理が 2 倍** |
| **前フレームのスキニング済み頂点を保存** | **スキニング結果をバッファに保存し、次フレームに使う** | **メモリ ＋ 帯域** |
| **コンピュートでスキニング** | **スキニングを事前に行い、今・前を保存**（[スキニング](../../../3d/skinning-animation.md)） | **一括で効率的** |

## 輪郭の外側に伸びる尾

**速い物体の輪郭の外側（背景）にもぼけた尾が伸びる**べきです。**物体の画素の速度**だけを**使う**と、**物体の縁でぼかしが急にぷつっと切れます**。

物体の輪郭に関する問題と対処です。物体の周りの背景がぼけない問題には、周りの画素のうち最も速い物体の速度を、その画素も使います（タイルの最大速度、近傍最大。[Tile Max Velocity](tile-max.md)）。ぼけた物体の縁がくっきりする問題には、深度と速度で重みを付けてサンプルを集めます（[Blur Pass Implementation](blur-pass.md)）。

## 描画順と透明物

**半透明の物体**は、**速度バッファに書き込めない**（**背景の速度が上書きされる**）ことが**多い**ので**扱いに注意**します。

| 対象 | 扱い |
| --- | --- |
| **不透明** | **速度を書く** |
| **半透明** | **速度を書かない**、または**別パス**で**後処理の前に近似** |
| **パーティクル** | **ストレッチ ビルボードなど、速度を表す形そのものに**。**ブラーの対象外**に |
| **UI** | **ブラーの対象外**（**ポストプロセスの後に描く**） |

## 対象を絞る

**すべての動く物をブラーする**と**重く、不自然**な場合があります。

| 工夫 | 内容 |
| --- | --- |
| **重要な動きだけ** | **プレイヤー・敵・乗り物・弾** |
| **遠い物体を除外** | **画面上で小さい物は、ブラーが見えない** |
| **速度の閾値以下は 0** | **ほぼ止まっている物にコストをかけない** |
| **マテリアルのフラグ** | **ブラーを掛けない物（武器・UI・遠景）を除外** |

## より良いやり方

| 工夫 | 内容 |
| --- | --- |
| **カメラ ブラー優先** | **まずカメラ。オブジェクトは必要なものだけ** |
| **回転の大きい物は弱める** | **プロペラなど、速度の向きが当てにならない物は、別途処理** |
| **前フレームの頂点位置を保存** | **スキニング・変形でも正確な速度** |
| **近傍最大の速度でぼかす** | **輪郭の外側にも尾が伸びる** |
| **TAA の速度バッファと共有** | **同じバッファを使う** |
| **速度の上限を設ける** | **速すぎる物で画面が崩れない** |

## よくあるミス

??? failure "物体のブラーが、輪郭でぷつっと切れる"
    <strong>近傍の最大速度（タイル）</strong>を使い、**サンプルの重み付け**をする。

??? failure "プロペラのブラーが、ぐちゃぐちゃになる"
    **回転が大きい物体は、速度の向きが不正確**。**ブラーを弱める・別処理**。

??? failure "キャラクターの手足にブラーが無い"
    **スキニングの前フレームの姿勢**が**無く、速度が 0**。**前フレームのボーンで再計算**。

??? failure "半透明の物体が、背景の速度を上書きして、ブラーがおかしい"
    **半透明は速度を書かない**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] オブジェクト ブラー ＝ <strong>動く物体の速度に沿ってぼかす</strong>
    - [x] <strong>頂点ごと</strong>に<strong>前フレームの位置から速度</strong>。<strong>回転・スキニングも</strong>
    - [x] <strong>輪郭の外にも尾が伸びる</strong>よう<strong>近傍の最大速度</strong>を使う
    - [x] <strong>半透明・パーティクル・UI は対象外</strong>が基本
    - [x] <strong>重要な物体だけ</strong>に絞って<strong>コストと破綻を減らす</strong>

## 参考

- McGuire et al., "A Reconstruction Filter for Plausible Motion Blur"（I3D 2012）
- Sousa, "Graphics Gems from CryENGINE 3"（SIGGRAPH 2013）
- Jimenez, "Next Generation Post Processing in Call of Duty: Advanced Warfare"（SIGGRAPH 2014）

## 関連ページ

- [Motion Blur](index.md)
- [Velocity Buffer](velocity-buffer.md)
- [Camera Motion Blur](camera-blur.md)
- [スキニングとアニメーション](../../../3d/skinning-animation.md)
