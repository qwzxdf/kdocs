---
title: AO Comparison
tags:
  - 描画
---

# AO Comparison

これまでの各方式を<strong>原理・必要な入力・コスト・弱点</strong>で並べて比べます。どの方式を選ぶかは対象プラットフォーム・必要な品質・使える入力・開発の手間で決まります。このページでは比較表と選び方の目安、実装の骨組みをまとめます。

!!! tip "ポイント"
    - 方式の違いは <strong>積分の近似法</strong>（サンプル・地平線・式）と <strong>コサイン重みの扱い</strong>、メモリ アクセスの工夫。
    - 精度の高さ：RTAO ＞ GTAO ＞ HBAO ＞ SSAO 系。
    - 実装の簡単さ：半球 SSAO ＞ Alchemy・SAO ＞ HBAO ＞ GTAO。
    - 新規に実装するなら：GTAO（品質・速さ・機能のバランス）またはHBAO+ ライブラリ。
    - どれもブラーと時間蓄積が必要。

!!! info "このページを読む前に"
    - [Ambient Occlusion (AO)](index.md)（このセクション全体の地図と、読む順番）
    - [MVP 変換（モデル・ビュー・プロジェクション）](../../3d/transforms-mvp.md)（座標変換（ワールド・ビュー・射影）の流れ）

## 総合比較表

| 項目 | Crytek SSAO | 半球 SSAO | Alchemy | SAO | HBAO | HBAO+ | GTAO |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 年 | 2007 | 2008頃〜 | 2011 | 2012 | 2008 | 2013頃〜 | 2016 |
| 近似法 | サンプル（球） | サンプル（半球） | 式の近似 | 式の近似（Alchemy） | 地平線 | 地平線（簡略） | 地平線（正確） |
| コサイン重み | なし | 雑（一様半球） | あり（v·n） | あり（v·n） | なし（立体角） | なし | 正確 |
| 入力 | 深度 | 深度＋法線 | 深度＋法線 | 深度のみ（法線を復元） | 深度＋法線 | 深度（＋法線） | 深度＋法線 |
| 平らな面の灰色化 | あり | なし | なし | なし | なし | なし | なし |
| ノイズ | 大 | 中〜大 | 中 | 中 | 小〜中 | 小 | 小（時間蓄積前提） |
| 半径とコスト | 比例 | 比例 | 大きいと遅い | 一定 | 比例 | 比例（キャッシュ効率） | 比例 |
| キャッシュ対策 | なし | なし | なし | 深度ミップ | なし | デインターリーブ | 深度ミップ（実装による） |
| バウンス・ベント法線 | なし | なし | なし | なし | なし | なし | あり |
| 実装の手間 | 小 | 小 | 小〜中 | 中 | 中 | ライブラリ | 中〜大 |

## 原理による分類

方式は「遮蔽の有無 V をどうやって求めるか」で 4 つに分けられます。

1 つ目は<strong>サンプルを数える</strong>方式（Crytek SSAO・半球 SSAO）です。近くのランダムな点が面の奥にあるかを調べその割合を 0/1 で数えます。単純ですが少ないサンプルでは量子化ノイズが出ます。2 つ目は式を足す方式（Alchemy・SAO）で、近くの面の点ごとに連続的な式を足します。0/1 の判定がないので滑らかです。3 つ目は地平線を積分する方式（HBAO・HBAO+・GTAO）で、方向ごとに遮蔽が始まる角度を探し、角度で積分します。少ない方向数で精度が出ます。4 つ目は世界を調べる方式（RTAO・DFAO・VXAO）で、シーン全体のデータから V を求めます。画面外の遮蔽も扱えますがデータ構造の用意が必要です。

## 数字で確かめる {#measure}

比較表の主張のうち数字で確かめられるものを計算しました（Python、乱数のシミュレーション）。

### 平らな面の灰色化

Crytek SSAO が平らな面で灰色になるのは、球のサンプルの約半分が面の下に入るからです。平面の上の 1 点を中心に半径 1 の球の中に 100 万個の点をランダムに置いて、平面より下にある割合を測ると、50.1 % でした。AO が約 0.5 になる計算で、何もない平らな面が半分暗くなります。法線の向きに半球を作る方式（半球 SSAO）では、0 % でした。

<svg class="fig flow" viewBox="0 0 720 250" role="img" aria-label="平らな面で面の下に入るサンプルの割合。球は 50 パーセント、半球は 0 パーセント"><text x="14" y="22" class="fig-title">平らな面で、面の下に入るサンプルの割合</text>
<line x1="60" y1="190" x2="690" y2="190" stroke="currentColor" stroke-width="1.5"/>
<g stroke-width="2"><rect x="150" y="50" width="120" height="140" fill="rgba(229,72,77,0.28)" stroke="#e5484d"/><rect x="400" y="189" width="120" height="1" fill="rgba(76,139,245,0.28)" stroke="#4c8bf5"/></g>
<g style="font-size:12px" text-anchor="middle"><text x="210" y="44">50.1 %</text><text x="460" y="183">0 %</text>
<text x="210" y="212">Crytek SSAO（球）</text><text x="460" y="212">半球 SSAO（法線の半球）</text></g>
<text x="360" y="238" text-anchor="middle" style="font-size:12px">球は、何もない平らな面でも約半分が暗くなる。法線を使う半球で解消する</text></svg>

### サンプル数と量子化ノイズ

0/1 で数える方式（Crytek SSAO、半球 SSAO）は `N` 個のサンプルで、AO が `N + 1` 段階の値しか取れません。遮蔽の割合が 0.5 なら二項分布の標準偏差は `√(0.25 / N)` です。`N = 4` で 0.25、8 で 0.177、16 で 0.125、32 で 0.088 です。16 サンプルでも AO が ±0.125 ばらつきます。ブラーと時間蓄積でならす必要があるのは、このためです。連続的な式を足す方式（Alchemy、SAO）や地平線を積分する方式（HBAO、GTAO）は 0/1 の判定がなく、量子化ノイズが出にくいです。

### 1 フレームの深度読み込み回数

フル HD（1920 × 1080、約 207 万画素）で 1 画素あたりのサンプル数を掛けた深度の読み込み回数です。半球 SSAO の 16 サンプルは、約 3300 万回です。Alchemy や SAO の 12 サンプルは、約 2500 万回です。HBAO の 8 方向 × 6 ステップ（48 回）と GTAO の 2 スライス × 両側 12 ステップ（48 回）は、約 1 億回です。SAO は深度ミップで読み込みがキャッシュに乗りやすく、実際の時間は読み込み回数の比より小さくなります。HBAO+ のデインターリーブも同じ目的です。

<svg class="fig flow" viewBox="0 0 720 240" role="img" aria-label="フル HD での 1 フレームの深度読み込み回数（百万回）"><text x="14" y="22" class="fig-title">1 フレームの深度読み込み（1920×1080、百万回）</text>
<line x1="60" y1="190" x2="690" y2="190" stroke="currentColor" stroke-width="1.5"/>
<g stroke-width="2" fill="rgba(76,139,245,0.28)" stroke="#4c8bf5"><rect x="110" y="123" width="90" height="67"/><rect x="250" y="140" width="90" height="50"/><rect x="390" y="40" width="90" height="150"/><rect x="530" y="40" width="90" height="150"/></g>
<g style="font-size:12px" text-anchor="middle"><text x="155" y="117">約 33</text><text x="295" y="134">約 25</text><text x="435" y="34">約 100</text><text x="575" y="34">約 100</text>
<text x="155" y="210">半球 SSAO（16）</text><text x="295" y="210">Alchemy / SAO（12）</text><text x="435" y="210">HBAO（8 方向×6）</text><text x="575" y="210">GTAO（2 スライス×24）</text></g>
<text x="360" y="232" text-anchor="middle" style="font-size:12px">読み込み回数の比。SAO の深度ミップや HBAO+ のデインターリーブは、キャッシュで実時間を縮める</text></svg>

### 深度の線形化の式

どの方式でも深度バッファの値を視点深度（メートル）に直します。標準の深度（近い面が 0）と reverse-Z（近い面が 1）で、式が違います。`near = 0.1`、`far = 1000` で視点深度 0.5、5、50、500 m の点を深度バッファの値に変換して、式で戻すと両方とも元の値に一致しました（標準の深度の値は 0.800、0.980、0.998、0.9999、reverse-Z は 0.200、0.0199、0.0019、0.0001）。

```hlsl
Texture2D<float> g_depth : register(t0);
Texture2D<float4> g_normal : register(t1);            // xyz = 法線を 0..1 に詰めたもの
SamplerState g_point_clamp : register(s0);

cbuffer AoConstants : register(b0) {
  float4x4 g_proj;           // 射影行列
  float2 g_inv_focal;        // (1 / proj[0][0], 1 / proj[1][1])。ビュー空間の位置の復元用
  float g_near;              // 例: 0.1
  float g_far;               // 例: 1000
  float g_radius;            // AO の半径（ビュー空間、メートル）。例: 0.5
  float g_reverse_z;         // 1 = reverse-Z、0 = 標準
  float2 _pad;
};

// 深度バッファの値 → 視点深度（メートル）。射影行列に合わせる
float LinearizeDepth(float d) {
  return (g_reverse_z > 0.5) ? g_near * g_far / (g_near + d * (g_far - g_near))
                             : g_near * g_far / (g_far - d * (g_far - g_near));
}

// 画素の UV と視点深度から、ビュー空間の位置（左手系、+Z が前）を復元する
float3 ViewPosition(float2 uv, float view_z) {
  float2 ndc = float2(uv.x * 2.0 - 1.0, 1.0 - uv.y * 2.0);     // 画面は y が下向き
  return float3(ndc * g_inv_focal * view_z, view_z);
}

// 半球 SSAO の最小版（16 サンプル）。比較のための骨組みで、ノイズの回転とブラーは省いている
float4 HemisphereAoPS(float4 pos : SV_Position, float2 uv : TEXCOORD0) : SV_Target {
  float d = g_depth.SampleLevel(g_point_clamp, uv, 0);
  float view_z = LinearizeDepth(d);
  if (view_z > g_far * 0.999) return float4(1, 1, 1, 1);        // 空は遮蔽なし（足した処理）

  float3 p = ViewPosition(uv, view_z);
  float3 n = normalize(g_normal.SampleLevel(g_point_clamp, uv, 0).xyz * 2.0 - 1.0);

  float occluded = 0.0;
  const int kSamples = 16;
  [unroll] for (int i = 0; i < kSamples; ++i) {
    // 法線の半球の中の点（黄金角で散らす簡易な分布。足した処理）
    float t = (i + 0.5) / kSamples;
    float phi = i * 2.399963;
    float r = sqrt(t);
    float3 h = float3(r * cos(phi), r * sin(phi), sqrt(1.0 - t));
    // 法線を軸にした向きへ回す（Duff らの基底）
    float s = (n.z >= 0.0) ? 1.0 : -1.0;
    float a = -1.0 / (s + n.z), c = n.x * n.y * a;
    float3 tx = float3(1.0 + s * n.x * n.x * a, s * c, -s * n.x);
    float3 ty = float3(c, s + n.y * n.y * a, -n.y);
    float3 sample_pos = p + (tx * h.x + ty * h.y + n * h.z) * g_radius * lerp(0.2, 1.0, t);

    // サンプル点を画面へ投影して、そこの深度と比べる
    float4 clip = mul(float4(sample_pos, 1.0), g_proj);
    float2 suv = float2(clip.x / clip.w * 0.5 + 0.5, 0.5 - clip.y / clip.w * 0.5);
    float scene_z = LinearizeDepth(g_depth.SampleLevel(g_point_clamp, suv, 0));
    // サンプルが面の奥にあれば遮蔽。半径より離れた面は範囲チェックで除外（ハローを抑える）
    float range = smoothstep(0.0, 1.0, g_radius / max(abs(p.z - scene_z), 1e-4));
    occluded += (scene_z < sample_pos.z - 0.02) ? range : 0.0;
  }
  float ao = 1.0 - occluded / kSamples;
  return float4(ao, ao, ao, 1.0);
}
```

この骨組みは `fxc` でコンパイルして確かめました。GPU での動作は確認していません。方式を入れ替えるときは `HemisphereAoPS` の中身だけを変えて、深度の線形化と位置の復元は共通にします。

## 見た目の違い

実際の画面で、方式の違いが出る場面をいくつか挙げます。

平らな面では Crytek SSAO だけが灰色になります（球のサンプルの約半分が面の下に入るため）。物の下の接地ではどの方式も暗くなりますが、半径と強さの調整で見た目が大きく変わります。凹んだ角は GTAO や HBAO では滑らかに暗くなりサンプル方式ではノイズが出やすくなります。凸の角（外側の縁）は法線を使う方式なら正しく暗くならず法線を持たない Crytek SSAO だと暗い輪が出やすくなります。細い柱の周りはどの方式でもハローが出ます。これはスクリーン空間の限界です。斜め方向の遮蔽はコサイン重みの扱いで強さが変わり HBAO は強めに出ます。明るい色の部屋ではマルチ バウンス（GTAO）がないと隅が黒く沈みます。

## コストの目安

コストは<strong>画素数 × サンプル数</strong>に比例します。フル HD での 1 画素あたりの深度読み込み回数の目安は、次のとおりです（概算で実装と GPU で変わります）。

半球 SSAO（16 サンプル）は 16 回に法線の読み込みが加わりノイズ テクスチャとブラーが必要です。Alchemy や SAO（9〜13 サンプル）は 9〜13 回で、SAO はミップのおかげで読み込みが軽くなります。HBAO（8 方向 × 6 ステップ）は 48 回で、方向を減らせば軽くなります。HBAO+ は HBAO 相当ですが、キャッシュ効率が良くライブラリとして使えます。GTAO（1〜2 スライス × 両側 8〜12 ステップ）は 16〜48 回で、時間蓄積で実質的な精度を上げます。RTAO（1〜2 レイ）は読み込みでなくレイトレースの処理で、BVH の更新とデノイズが必要です。

実際の速さは、キャッシュ効率・ブラー・解像度で大きく変わります。実機で測るのが一番確実です（[Profiling Tools](../optimization/tools.md)）。

## 実用実装の比較（XeGTAO・ASSAO・CACAO） {#implementations}

上の表は論文ごとの手法を比べたものです。実際にゲームへ入れるときは公開されている実装から選ぶことが多いので、その比較も載せます。

| 項目 | [XeGTAO](xegtao.md) | [ASSAO / CACAO](assao-cacao.md) | HBAO+ |
| --- | --- | --- | --- |
| 元の方式 | GTAO | 適応的な SSAO | 地平線（HBAO の改良） |
| 品質 | 高い（レイトレース AO に近い） | 中〜高 | 高い |
| 軽さの工夫 | 深度ミップ、プリセット | デインターリーブ、適応サンプル | デインターリーブ |
| 時間蓄積 | 前提（TAA と組む） | 不要 | 不要 |
| ライセンス | MIT（ソースが読める） | MIT（FidelityFX） | NVIDIA のライブラリ |
| 向く場面 | 品質を最優先、TAA がある | TAA が無い軽さが大事 | NVIDIA 向けに手早く入れたい |

TAA を使っているなら XeGTAO、使っていない・低スペックの GPU も対象なら CACAO、と考えると選びやすいです。

## 選び方

状況ごとにおすすめを挙げます。

とにかく簡単に AO を入れたいなら <strong>半球 SSAO</strong>（[実装が簡単](ssao-hemisphere.md)）から始めます。品質・速さ・機能のバランスを求めるなら GTAO（コサイン重み・マルチ バウンス・スペキュラ遮蔽を備え、公開実装の XeGTAO があります）が第一候補です。特に PC でライブラリに任せたいなら HBAO+ です。広い範囲・大きな半径を安く扱いたいなら半径に依存しない SAO が向きます。モバイルではサンプル数を 4〜8 に減らした半球 SSAO か AO を事前に焼いておく方法を選びます。最高品質でレイトレ対応の環境なら RTAO とデノイザー（あるいは GTAO との併用）です。静的な広い屋外なら DFAO かベイクした AO、画面外の遮蔽が必須なら世界空間の方式（[RTAO・DFAO・VXAO](world-space/index.md)）を選びます。

## AO を使わない選択肢

AO が不要なまたは別の手段で済む場面もあります。静的なメッシュには AO をテクスチャに焼き込んでおけば、ランタイムのコストはゼロです。動かない背景にはこれが最適です。ライトマップやプローブは間接光そのものを事前計算するので、AO も含まれます（[GI](../gi/index.md)）。キャラクターの足元の丸い影（ブロブ影）は、簡易な接地用の AO として働きます。頂点カラーに AO を焼いてシェーダーで使う方法もあります。

現実的な構成は <strong>静的なものは焼き動くものとの接触だけをスクリーン空間 AO で補う</strong>併用です。

## 実装の骨組み

どの方式でもパスの構成はほぼ同じです。

最初に深度（と法線）を準備します。G-Buffer か深度プリパスから得て、必要なら線形深度とミップも作ります。次に、方式ごとに AO を計算します（フル解像度か半分の解像度）。続いてバイラテラル ブラーなどの空間フィルタを掛けます（[AO Filtering](filtering/index.md)）。任意で動きベクトルと深度を使った時間蓄積を行います。半分の解像度で計算したならジョイント バイラテラルでアップサンプルします。最後に、間接光（環境光）に乗算してライティングに適用し、スペキュラ遮蔽も足します。

## 実装チェックリスト

実装でつまずきやすい点を確認項目にまとめます。深度の線形化の式が射影行列（標準 Z か reverse-Z か）に合っているか。ビュー空間の向き（左手系・+Z が前）と y の符号（画面は下向き）が正しいか。深度・法線をポイント サンプリングで読んでいるか。深度が far の画素（空）で AO = 1 にしているか。適用先が間接光だけで直接光に掛けていないか。AO をリニア空間で掛けているか。半径をビュー空間（メートル）で指定しているか。

## よくあるミス

??? failure "どの方式を選ぶか迷い続けて、実装が進まない"
    まず<strong>半球 SSAO</strong>で動かして、不満が出たら GTAOに進みます。パスの構成は同じです。

??? failure "AO のコストを方式だけで比較する"
    キャッシュ・ブラー・解像度で実測値は大きく変わります。自分の環境で測ります。

??? failure "ベイクした AO とスクリーン空間 AO を両方フルで掛けて、二重に暗くなる"
    役割を分け（ベイクは細部、SSAO は接触）、強さを調整します。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 方式の違いは<strong>積分の近似法（サンプル・式・地平線）</strong>とコサイン重み、メモリ アクセス
    - [x] 精度はRTAO ＞ GTAO ＞ HBAO ＞ SSAO 系。簡単さは逆
    - [x] まず半球 SSAO、品質を上げるなら GTAO。ライブラリなら HBAO+
    - [x] 静的なものは焼き動くものとの接触はスクリーン空間 AO
    - [x] どれもブラー・時間蓄積・間接光への乗算が共通

## 参考

このページは、次の資料を読まずに書きました。数字は、Python のシミュレーションと式からの計算です。

- Mittring, "Finding Next Gen: CryEngine 2", SIGGRAPH 2007, Advances in Real-Time Rendering in 3D Graphics and Games
- Bavoil, Sainz, Dimitrov, "Image-Space Horizon-Based Ambient Occlusion", SIGGRAPH 2008 Talks
- McGuire, Osman, Bukowski, Hennessy, "The Alchemy Screen-Space Ambient Obscurance Algorithm", High-Performance Graphics 2011
- McGuire, Mara, Luebke, "Scalable Ambient Obscurance", High-Performance Graphics 2012
- Jimenez, Wu, Pesce, Jarabo, "Practical Real-Time Strategies for Accurate Indirect Occlusion", SIGGRAPH 2016, Physically Based Shading in Theory and Practice
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（Ambient Occlusion の章）

## 関連ページ

- [Ambient Occlusion (AO)](index.md)
- [AO Theory](theory/index.md)
- [GTAO](gtao.md)
- [AO Filtering](filtering/index.md)
- [AO Artifacts](artifacts/index.md)
