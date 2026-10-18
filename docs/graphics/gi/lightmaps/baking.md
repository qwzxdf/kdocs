---
title: Baking Workflow
tags:
  - 描画
---

# Baking Workflow

<strong>ベイクは、シーンの静的な光を、事前に計算して、テクスチャへ書き出す作業</strong>です。<strong>時間がかかるので、設定を段階的に上げながら、確認します</strong>。法線マップと併用するための「方向情報」も、一緒にベイクできます。このページでは、ベイクの流れと、方向情報を説明します。

!!! tip "ポイント"
    - 手順：UV2 を用意 → 静的なオブジェクトを指定 → ベイク → 確認 → 調整。
    - 最初は低品質で、全体を確認してから、品質を上げる。
    - 方向情報を一緒に焼くと、法線マップの凹凸が反映される。
    - ベイクは時間がかかるので、自動化・並列化する。

## ベイクの流れ
| 手順 | 内容 |
| --- | --- |
| ① UV2 の生成・パッキング | 全メッシュの UV2 を、ライトマップ アトラスに配置 |
| ② ベイク | 各テクセルのワールド位置・法線から、パス トレースで放射照度を計算 |
| ③ デノイズ | 少ないサンプルで速く計算し、デノイザでノイズを除去 |
| ④ 圧縮・出力 | <strong>BC6H（HDR）</strong>などに圧縮 |
| ⑤ 実行時に読み込む | シーンと一緒にライトマップをストリーミング |


最初に、全メッシュの UV2 を生成して、ライトマップ アトラスに配置します。次に、アトラスの各テクセルが、ワールドのどの位置のどの法線に対応するかを求め、そこからパス トレーシングで放射照度を計算します。サンプル数が少なければ短時間で終わりますが、ノイズが残ります。そこで、<strong>デノイザ</strong>（Intel Open Image Denoise、NVIDIA OptiX、AMD の Radeon Image Filter など）でノイズを除去します。少ないサンプルで速く計算し、後でデノイズする方法が、いまの標準です。最後に、BC6H のような HDR 向けの圧縮形式に圧縮して出力し、実行時にシーンと一緒にストリーミングします。

ベイクには数分から数時間かかります。GPU ベイク（GPU レイトレース）を使うと、CPU より大幅に短縮できます。

最初に、全メッシュの UV2 を生成して、ライトマップ アトラスに配置します。次に、アトラスの各テクセルが、ワールドのどの位置のどの法線に対応するかを求め、そこからパス トレーシングで放射照度を計算します。サンプル数が少なければ短時間で終わりますが、ノイズが残ります。そこで、<strong>デノイザ</strong>（Intel Open Image Denoise、NVIDIA OptiX、AMD の Radeon Image Filter など）でノイズを除去します。少ないサンプルで速く計算し、後でデノイズする方法が、いまの標準です。最後に、BC6H のような HDR 向けの圧縮形式に圧縮して出力し、実行時にシーンと一緒にストリーミングします。

ベイクには数分から数時間かかります。GPU ベイク（GPU レイトレース）を使うと、CPU より大幅に短縮できます。

<strong>ベイクには数分〜数時間</strong>かかります。<strong>GPU ベイク</strong>（GPU レイトレース）で、大幅に短縮できます。

## 方向情報（法線マップとの併用）

通常のライトマップが持つのは、「その点に届く光の総量」（スカラー、色は RGB）だけです。法線マップで細かい凹凸を付けても、ライトマップの明るさは法線に応じて変わらないので、間接光の陰影が平坦に見えてしまいます。たとえば、レンガの壁に法線マップで凹凸を付けても、レンガの出っ張りと引っ込みの間接光が同じ明るさになります。

これを解決するのが<strong>方向情報</strong>です。光の来る方向も一緒に保存しておき、法線マップの法線と組み合わせて、明るさを補正します。主な方式は 4 つあります。

<strong>スカラーのみ</strong>は、放射照度だけを保存します。最も軽いですが、法線マップは間接光に効きません。<strong>Directional ライトマップ</strong>は、主な光の方向をもう 1 枚のテクスチャに保存します。法線との内積で、明るさを補正します。<strong>SH ライトマップ</strong>は、L1 SH（4 係数）を保存して、法線で SH を評価します。そして、<strong>Radiosity Normal Mapping</strong>（Valve が『Half-Life 2』で使った方式）は、正三角形状に配した 3 つの基底方向のそれぞれについて放射照度を保存し、法線マップの法線で 3 つを補間します。

```hlsl
float3 basis0 = lightmap0.Sample(linear_sampler, uv).rgb;
float3 basis1 = lightmap1.Sample(linear_sampler, uv).rgb;
float3 basis2 = lightmap2.Sample(linear_sampler, uv).rgb;
float3 w = saturate(float3(dot(n_ts, kBasis0), dot(n_ts, kBasis1), dot(n_ts, kBasis2)));
w *= w;
w /= (w.x + w.y + w.z);
float3 irradiance = basis0 * w.x + basis1 * w.y + basis2 * w.z;
```

3 つの基底方向は、接空間で表されます（法線に近い方向を 3 方向から取り囲むように置く）。法線 n_ts と各基底方向の内積が大きいほど、その基底の放射照度が強く効きます。2 乗して正規化しているのは、重みを鋭くして、法線の向きに敏感にするためです。

方向情報を持たせると、法線マップの凹凸に応じた陰影が、間接光にも加わります。代償は、テクスチャが 3 枚に増えること（メモリと読み込み回数）です。モバイルなどでは、Directional（2 枚）や、スカラー 1 枚で妥協する選択もあります。

## ベイクとは

<strong>ベイク</strong>は、<strong>光の、シミュレーション</strong>を、制作時に、実行して、結果を、ライトマップ（テクスチャ）に、焼き込む作業です。実行時の、ゲームでは、重すぎて、できない、高品質な、光の計算（何度も、反射、ソフトな影）を、時間を、かけて、行えます。

## ベイクの、手順

```text
① 静的なオブジェクトに、ライトマップ UV（UV2）を、作る     （[Lightmap UVs (UV2)](uv2.md)）
② 静的なライトを、「ベイク」に、設定する
③ ベイカーを、実行（光の、シミュレーション。数分〜数時間）
④ 結果（ライトマップ、プローブ）を、保存して、ゲームに、組み込む
```

## 光の、シミュレーション：レイトレーシング

ライトマップの、<strong>各画素</strong>（<strong>面の上の、1 点</strong>）について、その点に、届く、光の総量を、レイトレーシングで、求めます。

```cpp
// ライトマップの 1 画素（面上の位置 p、法線 n）の、明るさを、パス トレーシングで、推定する（概略）。
float3 BakeTexel(const Scene& scene, const float3& p, const float3& n, int samples) {
  float3 sum = 0;
  for (int i = 0; i < samples; ++i) {                                // 数百〜数万サンプル
    float3 dir = CosineSampleHemisphere(n, Rand2());                  // 法線の側の、半球から、余弦重みで、方向を選ぶ
    sum += TracePath(scene, p + n * 1e-3f, dir, /*max_bounces*/ 4);   // その方向から、来る光（反射を、数回、追う）
  }
  return sum / samples;                                                // 拡散の、間接光（アルベドは、実行時に掛ける）
}
```

<strong>各画素</strong>から、<strong>余弦重みづけ</strong>（[Monte Carlo Integration](../theory/monte-carlo.md)）で、多数の、レイを、飛ばし、反射を、数回、追跡して、光を、集めます。サンプルが、多いほど、ノイズが、減ります（数千〜数万サンプル）。時間は、かかりますが、制作時なので、問題ありません。

## ベイクの、設定

| 設定 | 内容 | 大きくすると |
| --- | --- | --- |
| ライトマップの、解像度（画素密度） | 1 m あたりの画素数 | 細かい影。メモリ・ベイク時間が、増える |
| サンプル数 | 1 画素あたりの、レイの数 | ノイズが、減る。ベイクが、遅い |
| バウンス数 | 光が、何回、反射するか | 間接光が、明るく、自然。時間が、増える（効果は、2〜3 回で、頭打ち） |
| ノイズ除去（デノイズ） | ベイク後に、ノイズを、消す | 少ない、サンプルでも、なめらか |
| 間接光の、強さ | 間接光の、倍率 | 間接光が、強く（アーティストの、調整） |

### バウンス数の、効果

| バウンス | 内容 | 見た目 |
| --- | --- | --- |
| 0 | 直接光のみ | 影が、真っ黒 |
| 1 | 1 回反射 | 日陰が、ほのかに、明るい。カラー ブリーディング |
| 2〜3 | 複数回の、反射 | 室内が、自然に、明るい。効果は、頭打ち |
| 4 以上 | 非常に、わずかな、変化 | ほぼ、変わらない（時間の、無駄） |

<strong>多くの、場面で、2〜3 バウンス</strong>で、<strong>十分</strong>です（[Visual Effect](../theory/visual-effect.md) の、等比級数）。

## ベイカーの、種類

| ベイカー | 内容 |
| --- | --- |
| エンジン内蔵（Unity の Progressive Lightmapper、Unreal の Lightmass） | エンジンに、組み込まれたベイカー。設定が、簡単 |
| 外部ツール（Blender の Cycles、V-Ray、Arnold など） | DCC ツールの、レンダラーで、ベイク。テクスチャとして、書き出し、エンジンへ |
| 自作（DXR など） | GPU レイトレーシングで、自分で、ベイカーを、作る。独自の、エンジンに、組み込みやすい |

自作の、エンジンで、<strong>簡単に、ベイクする</strong>には、<strong>GPU レイトレーシング</strong>（DXR）で、ライトマップの、各画素から、レイを、飛ばす方法が、現実的です（[Ray-Traced GI](../rt-gi/index.md)）。

## 保存する、形式

| 形式 | 内容 |
| --- | --- |
| HDR テクスチャ（`R16G16B16A16_FLOAT`、`BC6H`） | 明るさの、範囲が、広い（HDR）。BC6H で、圧縮（サイズが、1/4〜1/6） |
| RGBM / RGBE（8 ビットの、形式） | 8 ビット RGBA に、HDR を、詰める（スケールを、アルファに）。古い、環境向け |
| LDR（`R8G8B8A8`） | 明るさの範囲が、狭い。簡易 |

```text
BC6H（HDR の、圧縮形式）: 4×4 画素を、16 バイトに圧縮（1 画素 = 1 バイト）。DirectX 11 が、対応。
```

<strong>DirectX 11 の、BC6H</strong> は、<strong>HDR の、ライトマップを、圧縮</strong>するのに、最適です（RGB16F の、1/8 の、サイズ）。

## ベイクの、落とし穴

| 問題 | 内容 | 対策 |
| --- | --- | --- |
| 継ぎ目の、黒い線 | UV2 の、余白が、足りない、パディングが、ない | 余白を、広く（2〜4 画素）、ブリード（[Lightmap UVs (UV2)](uv2.md)） |
| ノイズ | サンプルが、少ない | サンプルを、増やす、デノイズ |
| 真っ黒な、面 | メッシュの、法線が、反転、面が、重なっている | 法線の、向きを、確認、UV2 の、重なりを、確認 |
| 光漏れ | 壁の、すき間（メッシュが、壁を、完全に、閉じていない） | メッシュを、閉じる、壁に、厚みを、持たせる |
| ベイクが、非常に、遅い | 解像度、サンプル、バウンスが、多すぎる | まず、低品質で、確認（プレビュー）。最終だけ、高品質 |

## よくあるミス

??? failure "ライトマップが、法線マップの凹凸と合わず、平らに見える"
    <strong>方向情報も一緒にベイク</strong>する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 低品質で確認 → 高品質でベイク
    - [x] 方向情報で、法線マップと併用

## 参考

- Goral, Torrance, Greenberg, Battaile, "Modeling the Interaction of Light Between Diffuse Surfaces", SIGGRAPH 1984（ラジオシティ）
- Cohen, Wallace, "Radiosity and Realistic Image Synthesis", Academic Press, 1993
- Iwanicki, Sloan, "Precomputed Lighting in Call of Duty: Infinite Warfare", SIGGRAPH 2017, Advances in Real-Time Rendering in Games
- Pharr, Jakob, Humphreys, "Physically Based Rendering: From Theory to Implementation", 4th Edition, MIT Press, 2023
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（大域照明、ライトマップ、プローブの章）

## 関連ページ

- [Lightmaps](index.md)
- [Lightmap UVs (UV2)](uv2.md)
- [Specular and Dynamic Objects](dynamic-objects.md)
