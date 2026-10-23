---
title: Character Shadows and Color
tags:
  - 描画
---

# Character Shadows and Color

<strong>キャラクターの影はゲームで最も目立ちます</strong>。顔に変な影が出たり髪や肌の影が汚くなると、絵が崩れます。キャラクター専用の影の設定（専用のバイアス・専用のライト・影の色と濃さの調整）で品質を上げます。このページではキャラクターの影の注意点・髪や肌の影・影の色と濃さの調整を説明します。

!!! tip "ポイント"
    - キャラクターは専用のバイアス・解像度にして、影を綺麗にする。
    - 顔の影は目立つので、法線オフセットや専用ライトで制御する。
    - 髪・肌は光が透ける（散乱）ので、影の色を少し暖かく・薄くする。
    - 影の色と濃さ：真っ黒でなく、環境光の色を残す。

## キャラクターの影
<strong>キャラクター</strong>は 画面の主役で影の品質が目立ちます。専用の工夫がよく使われます。

| 方法 | 内容 |
| --- | --- |
| 専用のシャドウ マップ | キャラクターだけを高解像度のシャドウ マップに描く（カスケードとは別）。顔・手の細部まで鋭く |
| カプセル シャドウ | 骨にカプセル（線分 ＋ 半径）を割り当て、解析的な柔らかい影。変形するキャラにも安い（[Distance Field Shadows](../sdf-shadows.md)） |
| コンタクト シャドウ | 足元・細部の接触を補う（[Contact Shadows](../contact-shadows.md)） |
| フェイク ライト | キャラクター用に専用のライト（リム ライト・影の向きを演出的に調整） |

### 髪・肌の影

髪は細いのでシャドウ マップではほぼ点になります。髪専用の深いシャドウ（Deep Opacity Maps）・近似的な、半透明の影が使われます（[Hair Shadows](../../skin-hair/hair/shadows.md) と [Skin and Hair](../../skin-hair/index.md) を参照）。

## 影の色・濃さの調整
影の色と濃さの調整です。影の色は真っ黒でなく環境光の色（空の青）に寄せます。間接光が影の中にも届くからです。影の濃さは 0〜1 の係数で調整し（`lerp(1, shadow, strength)`）、シーンの雰囲気に合わせます。AO と併用すればシャドウ マップが覆えない細かい隙間の暗さを補えます（[AO](../../ao/index.md)）。

```hlsl
float3 direct = sun_color * n_dot_l * shadow;
float3 ambient = sky_ambient * ao;
float3 lit = direct + ambient;
```

<strong>影の中も環境光で少し明るい</strong>ので影を完全な黒にしないことが、自然な見た目の基本です。

## キャラクターの影が特別な理由

キャラクターはゲームで <strong>最も、注目される物</strong>です。足元の接地、顔・体の自己影、動くことによる影のちらつきがすぐに、目に付きます。

| 課題 | 内容 |
| --- | --- |
| 接地感 | 足元の影が地面に、しっかり接していることでキャラクターが、地面の上に立っているように見える。接地が弱いと浮いて見える |
| 自己影 | 顔、首、服の折り目の細かい自己影。解像度が足りないとぼやけて汚く見える |
| ちらつき | キャラクターが動き、影の縁がちらちらする（テクセル スナップ、PCF で軽減） |
| 薄い物 | 髪、マント、細いアクセサリーの影が欠ける（ピーター パンニング） |

## キャラクターの専用のシャドウ マップ

<strong>シーン全体を覆うカスケード</strong>の、1 画素は数センチ〜数十センチです。キャラクターの顔（数十センチ）は、数画素にしか映りません。キャラクター専用のシャドウ マップを作ると、解像度が大幅に上がります。

```cpp
// キャラクターを囲む、小さな範囲（半径 2 m）に、シャドウ マップを割り当てる。
// 解像度 2048 で、1 画素 = 約 2 mm。顔や、服の、細かい影が、出る。
float radius = 2.0f;
Matrix character_view = Matrix::CreateLookAt(character_center - light_dir * radius, character_center, up);
Matrix character_proj = Matrix::CreateOrthographicOffCenter(-radius, radius, -radius, radius, 0.0f, 2.0f * radius);
```

| 方式 | 内容 |
| --- | --- |
| キャラクター専用のシャドウ マップ | キャラクターごとに、小さな範囲を高解像度で。主役の数体だけ |
| カスケードの最初のカスケードを、キャラクターに | カメラの、すぐ近く（最も細かい）カスケードが、キャラクターを覆う |
| 接触の影（コンタクト シャドウ） | 画面空間で足元の、短い影を補う（[Contact Shadows](../contact-shadows.md)） |

## 接地感を出す

### ① 足元のブロブ影

キャラクターの <strong>足元に丸い暗いテクスチャ</strong>を、貼る（[Blob and Planar Projected Shadows](blob-planar.md)）。簡単で安定。シャドウ マップがぼやけても足元は、しっかり接地して見えます。

### ② コンタクト シャドウ

画面空間で キャラクターの、近くだけ、短い距離の影をレイマーチで求めます（[Contact Shadows](../contact-shadows.md)）。シャドウ マップの解像度では、出せない細かい接触の影が出ます。

### ③ アンビエント オクルージョン

足元は 地面と体の隙間で 環境光が、遮られて暗くなります。AO（[AO](../../ao/index.md)）で自然な暗さが、出ます。

| 方法 | 効果 |
| --- | --- |
| ブロブ影 | 足元の丸い暗がり。どんな環境でも安定して接地して見える |
| コンタクト シャドウ | 細かい、接触の影（足と地面の境目） |
| AO | 全体の暗がり（体と地面の隙間、脇の下） |

3 つを組み合わせるとシャドウ マップが、荒くても、接地感が保たれます。

## 影の色

影は <strong>真っ黒ではありません</strong>。影の中も環境光（空の光、周りの反射光）が当たります。

```hlsl
// 影の中でも、環境光が、残る。直接光だけが、影で、遮られる。
float3 direct = albedo * g_light_color * n_dot_l * shadow;       // 影で、遮られる
float3 ambient = albedo * g_ambient_color;                        // 影に、関係なく、残る
float3 color = direct + ambient;
```

| 問題 | 内容 |
| --- | --- |
| 影の中が真っ黒 | 環境光が無いまたは、弱すぎる。空の色（青みがかった）を足す |
| 影の色がグレー | 屋外では影は、青みがかる（空の青い光が当たるため）。環境光を青っぽく |
| 影の中のキャラクターが浮く | 周りの、影の色とキャラクターの影の中の色が、合っていない。同じ環境光で照らす |

## キャラクターの影のちらつき

| 原因 | 対策 |
| --- | --- |
| キャラクターの位置が動くことで、シャドウ マップの画素がずれる | テクセル スナップ（[Aliasing and Stabilization](../shadow-map-basics/aliasing-stabilize.md)）。キャラクターの中心を画素の整数倍に、丸める |
| アニメーションで細いパーツが、動く | PCF を広く（5×5）。TAA |
| 薄いパーツ（髪、マント）の影が欠ける | 影用の、厚みのあるメッシュ。両面を描く |

## 影を落とす側と受ける側の制御

| 設定 | 内容 |
| --- | --- |
| 影を落とさない | 小さな、アクセサリー、銃の細部、目の周り（眼球の影が顔に落ちると、不自然） |
| 影を受けない | 目、歯（光り方が不自然になるため）、顔の特定の部分（アーティストの、意図） |
| 自己影の調整 | 顔では、自己影を弱める（鼻の下、顎の影が強すぎると不自然）。バイアスの調整 |

アーティストが <strong>物ごとにフラグを、設定</strong>できる仕組み（影を落とす / 受ける）を、用意しておくと 調整が楽です。

## よくあるミス

??? failure "顔に、鼻や顎の汚い影が出る"
    <strong>顔の専用バイアス</strong>・専用ライト・影の濃さを下げる。

## これだけ覚える

!!! abstract "まとめ"
    - [x] キャラクターは、専用の影の設定を持つ
    - [x] 影の色と濃さを調整して真っ黒にしない

## 参考

- Valient, "Stable Rendering of Cascaded Shadow Maps", ShaderX6, 2008
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018
- McGuire, Mara, "Efficient GPU Screen-Space Ray Tracing", Journal of Computer Graphics Techniques, Vol. 3, No. 4, 2014
- Dimitrov, "Cascaded Shadow Maps", NVIDIA White Paper, 2007

## 関連ページ

- [Special Cases](index.md)
- [Shadow Bias](../bias/index.md)
- [Cel Shading](../../postprocess/stylized/cel-shading.md)
