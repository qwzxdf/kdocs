---
title: Denoising
tags:
  - 描画
---

# Denoising

粗い面の反射を 1 画素 1 本のレイで求めると、画面は砂嵐になります。レイの向きが乱数で決まるので、隣の画素がまるで違う方向を見るからです。そこで、「前のフレームの結果を借りる」（時間）と「周りの画素と平均する」（空間）の 2 つで、ノイズを消します。ただし、反射は拡散の間接光と違って見る角度で像の位置が動きます。このため画素が前のフレームでどこにあったかを調べる再投影が、反射では難しくなります。このページではデノイザーの標準形である SVGF と PICA PICA の反射パイプラインを読み、コメント付きの完成形で時間蓄積、反射の再投影、空間再構成、à-trous フィルターの順に説明します。

!!! tip "ポイント"
    - 時間蓄積は深度・法線・メッシュ ID の整合性を調べて、合わない履歴を捨てる。α = 0.2 の指数移動平均で、定常の等価サンプル数は 9 になる。
    - 空間フィルターは輝度の分散で導く。ノイズの多い所は強く少ない所は弱くかける。
    - 反射の再投影には 2 つの候補がある。反射面の動きベクトルとヒット点の再投影で、新しい色の統計から重みを決めて混ぜる。
    - 1/4 レイ/画素の反射を近傍のヒットを BRDF で重み付けして全解像度に配ると、16 レイ/画素に近い分散の低下が得られる。
    - ぼかしを強くするほどノイズは減るが、段差が鈍る。分散で導く重みはその取引を画素ごとに調整する。

!!! info "このページを読む前に"
    - [Ray-Traced Reflections](index.md)（このセクション全体の地図と、読む順番）
    - [Ray Generation](ray-generation.md)（反射レイの作り方）

## 読んだ資料 {#sources}

- Schied ほか, "Spatiotemporal Variance-Guided Filtering: Real-Time Reconstruction for Path-Traced Global Illumination", HPG 2017。本文の 11 ページと結論までを全部読みました。図と補足のビデオは見ていません。
- Barré-Brisebois ほか, "Hybrid Rendering for Real-Time Ray Tracing", Ray Tracing Gems 第 25 章。反射の節（25.2.2）と前後の節を読みました。性能の図 25-31 は図なので読めず数字は引いていません。

NVIDIA の NRD（ReBLUR、ReLAX）などほかのデノイザーは読んでいません。このページは名前に触れる程度です。

## 反射のノイズは拡散の間接光と性質が違う {#why-hard}

拡散の間接光は低周波です。なめらかに変わる光なので広くぼかしても見た目が崩れません。反射は高周波で映る物の細かい形が見えます。広くぼかすと鏡面の反射が失われます。

もう 1 つの違いが視点依存です。拡散の間接光はカメラが動いても画面上の同じ点を追えます。反射像は鏡の奥の「虚像」として存在するので、カメラが動くと床の点とそこに映る像が、別々の速さで画面を動きます。床の点の位置で履歴を読むと反射像がずれてぼやけます。

<svg class="fig flow" viewBox="0 0 700 226" role="img" aria-label="反射の再投影"><defs><marker id="dn-a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#94a3b8"/></marker></defs><text x="10" y="18" text-anchor="start" font-size="12" fill="currentColor">真横から見た図: カメラが右へ動くと、床の点と、そこに映る像が別々に動く</text><line x1="40" y1="150" x2="620" y2="150" stroke="#94a3b8" stroke-width="4"/><text x="630" y="154" text-anchor="start" font-size="10" fill="currentColor">床(鏡)</text><circle cx="150" cy="60" r="6" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="150" y="46" text-anchor="middle" font-size="10" fill="currentColor">カメラ(前)</text><circle cx="250" cy="60" r="6" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="250" y="46" text-anchor="middle" font-size="10" fill="currentColor">カメラ(今)</text><rect x="480" y="95" width="28" height="55" fill="rgba(148,163,184,0.18)" stroke="#94a3b8"/><text x="494" y="88" text-anchor="middle" font-size="10" fill="currentColor">映る物</text><line x1="150" y1="60" x2="310" y2="150" stroke="#4c8bf5" stroke-width="1.5"/><line x1="310" y1="150" x2="480" y2="110" stroke="#4c8bf5" stroke-width="1.5" stroke-dasharray="4 3"/><line x1="250" y1="60" x2="370" y2="150" stroke="#e5aa28" stroke-width="1.5"/><line x1="370" y1="150" x2="480" y2="124" stroke="#e5aa28" stroke-width="1.5" stroke-dasharray="4 3"/><circle cx="310" cy="150" r="4" fill="#4c8bf5"/><text x="310" y="172" text-anchor="middle" font-size="10" fill="currentColor">前の床の点</text><circle cx="370" cy="150" r="4" fill="#e5aa28"/><text x="370" y="172" text-anchor="middle" font-size="10" fill="currentColor">今の床の点</text><text x="40" y="198" text-anchor="start" font-size="10" fill="currentColor">床の点(面の動きベクトル)は 60 だけ動くが、映る物の見かけの位置は、それとは別の量で動く</text><text x="40" y="214" text-anchor="start" font-size="10" fill="currentColor">→ 面の位置で履歴を読むと、像がずれてぼける。ヒット点(映る物)を再投影すると、平らな鏡では合う</text></svg>

## パイプラインの全体 {#pipeline}

PICA PICA の反射は G バッファからレイを出します。反射は半分の解像度、つまり 1/4 レイ/画素で追跡します。多段の再構成とフィルターで全解像度に戻し、空間と時間の一貫性で欠けた情報を埋めます。以前は SSR と併用したが、結局レイトレースだけに統一したと書かれています。

1. 素材の重点サンプリングで反射レイを作る（法線分布だけを重点サンプリングする）。
2. 低食い違いの Halton 列と Cranley-Patterson 回転で、画素ごとにずらした乱数を作る。
3. 地平線の下に向かったレイは別のレイに取り替える。
4. 当たった点で影を取りライティングして、半分の解像度に保存する。
5. 空間の再構成で全解像度に配る（16 レイ/画素に近い分散の低下）。
6. 双方向（バイラテラル）フィルターで、残るノイズを消す。分散で核の大きさを調整する。
7. 時間蓄積と TAA で仕上げる。

SVGF はこの 6〜7 を一般化したものです。1 サンプル/画素の入力から、時間蓄積で等価サンプル数を増やし、輝度の分散を推定しその分散で à-trous ウェーブレット フィルターを導きます。

## 時間蓄積 {#temporal}

### 指数移動平均と整合性 {#ema}

SVGF は色に対する TAA の近傍クランプではなく、ジオメトリに基づく時間フィルターを使います。ノイズの多い入力に色ベースの時間フィルターを使うとアーティファクトが出るためです。前のフレームの結果を `C' = α × C + (1 − α) × C'_prev` で混ぜます。α を大きくすると新しい値に素早く追従しますが、ノイズが残ります。論文は α = 0.2 が最良だったと書いています。

履歴は無条件には使えません。前のフレームの同じ画素を動きベクトルで求め深度、オブジェクト空間の法線、メッシュ ID の 3 つを比べて、同じ面かを調べます。双線形の 2 × 2 のタップは 1 つずつ調べます。合わないタップは捨て重みを整合したタップに均等に配り直します。全部が合わなければ 3 × 3 で探し直して、薄い葉のような形を拾います。それでも見つからなければ遮蔽が解けた画素なので、履歴を捨てます。

C++ で計算すると固定 α = 0.2 の定常状態の等価サンプル数は `(2 − α) / α` ＝ 9 です。α = 0.1 なら 19 です。α を小さくするほど溜まるサンプルは増えますが、遅れや再サンプルのぼけも増えます。

```hlsl
// 反射のデノイズ ①: 時間方向の蓄積と、分散の推定（SVGF の 4.1 と 4.2、Schied ほか 2017）。
// 入力は 1 サンプル/画素の反射の色。G バッファ（深度・法線・メッシュ ID・動きベクトル）は
// ラスタライズで作ったノイズのないもの。出力は、積分した色と、輝度の 1 次・2 次モーメント。

Texture2D<float4> g_color : register(t0);         // 今のフレームの反射の色（アルベドを割った、照明だけ）
Texture2D<float4> g_history_color : register(t1); // 前フレームの積分した色。a = 蓄積したフレーム数
Texture2D<float2> g_history_moments : register(t2); // 前フレームの輝度のモーメント（x = 1 次、y = 2 次）
Texture2D<float> g_depth : register(t3);          // 今のフレームの線形深度 [m]
Texture2D<float> g_prev_depth : register(t4);     // 前フレームの線形深度 [m]
Texture2D<float4> g_normal : register(t5);        // 今のフレームのワールド法線（xyz）
Texture2D<float4> g_prev_normal : register(t6);   // 前フレームのワールド法線
Texture2D<uint> g_mesh_id : register(t7);         // 今のフレームのメッシュ番号
Texture2D<uint> g_prev_mesh_id : register(t8);    // 前フレームのメッシュ番号
Texture2D<float2> g_motion : register(t9);        // 動きベクトル（UV の差。前の位置 = 今の UV - 動き）
RWTexture2D<float4> g_out_color : register(u0);   // rgb = 積分した色、a = 蓄積フレーム数
RWTexture2D<float2> g_out_moments : register(u1); // 積分したモーメント
RWTexture2D<float> g_out_variance : register(u2); // 輝度の分散 σ²

cbuffer TemporalCB : register(b0) {
  int2 g_size;               // 画面の大きさ [px]
  float g_alpha;             // 新しい色の重み。論文は 0.2 が最良と書く
  float g_depth_tolerance;   // 深度の許容差（相対）。一例: 0.02
  float g_normal_tolerance;  // 法線の cos のしきい値。一例: 0.9（約 26 度）
  float g_max_history;       // 蓄積フレーム数の上限（一例: 32）
  float2 g_pad;
};

float Luminance(float3 c) {
  return dot(c, float3(0.2126, 0.7152, 0.0722));
}

// 前フレームの画素 p が、今の画素と同じ面か調べる（論文: 深度・法線・メッシュ ID の整合性）。
bool IsConsistent(int2 p, int2 prev_p, float depth, float3 normal, uint id) {
  if (any(prev_p < 0) || any(prev_p >= g_size)) return false;     // 画面の外
  if (g_prev_mesh_id.Load(int3(prev_p, 0)) != id) return false;   // 別のメッシュ
  float prev_depth = g_prev_depth.Load(int3(prev_p, 0));
  if (abs(prev_depth - depth) > g_depth_tolerance * depth) return false;   // 深度が離れている
  float3 prev_n = g_prev_normal.Load(int3(prev_p, 0)).xyz;
  if (dot(prev_n, normal) < g_normal_tolerance) return false;     // 法線の向きが違う
  return true;
}

[numthreads(8, 8, 1)]
void main(uint3 id : SV_DispatchThreadID) {
  int2 p = int2(id.xy);
  if (any(p >= g_size)) return;

  float4 current = g_color.Load(int3(p, 0));
  float lum = Luminance(current.rgb);                             // この画素の輝度
  float2 moments_now = float2(lum, lum * lum);                    // 1 サンプルのモーメント

  float depth = g_depth.Load(int3(p, 0));
  float3 normal = g_normal.Load(int3(p, 0)).xyz;
  uint mesh = g_mesh_id.Load(int3(p, 0));

  // 前フレームでの位置（小数）。画素の中心は +0.5 なので、座標を画素単位にして、
  // 双線形の 4 タップ（2 x 2）の左上を求める。
  float2 uv = (p + 0.5) / g_size;
  float2 prev_pos = (uv - g_motion.Load(int3(p, 0))) * g_size - 0.5;
  int2 base = int2(floor(prev_pos));
  float2 f = prev_pos - base;                                     // 双線形の小数部

  // 4 タップそれぞれに、整合性を調べる。合わないタップは捨てて、重みを残りに配り直す。
  float4 sum_color = 0;
  float2 sum_moments = 0;
  float sum_w = 0;
  [unroll] for (int j = 0; j < 2; ++j) {
    [unroll] for (int i = 0; i < 2; ++i) {
      int2 q = base + int2(i, j);
      float w = (i == 0 ? 1.0 - f.x : f.x) * (j == 0 ? 1.0 - f.y : f.y);   // 双線形の重み
      if (IsConsistent(p, q, depth, normal, mesh)) {
        sum_color += g_history_color.Load(int3(q, 0)) * w;
        sum_moments += g_history_moments.Load(int3(q, 0)) * w;
        sum_w += w;
      }
    }
  }

  float4 history = 0;
  float2 moments_hist = 0;
  float count = 0;                                                // 蓄積したフレーム数
  if (sum_w > 1e-3) {                                             // 1 つでも整合すれば履歴を使う
    history = sum_color / sum_w;                                  // 重みを正規化（捨てた分を配り直す）
    moments_hist = sum_moments / sum_w;
    count = min(history.a + 1.0, g_max_history);
  }
  // 論文は、全部が不整合なら 3 x 3 で探し直し、それでも無ければ「遮蔽が解けた」として履歴を捨てる。
  // ここでは 3 x 3 の探し直しは省略した（足していない処理）。

  // 指数移動平均。履歴が無い間は alpha = 1（今の値だけ）、溜まると alpha = max(g_alpha, 1/count)。
  // 1/count の下限を使うと、最初の数フレームは均等な平均になり、早く収束する（Yang ほか 2009 の考え方）。
  float alpha = (count > 0.0) ? max(g_alpha, 1.0 / count) : 1.0;
  float3 color = lerp(history.rgb, current.rgb, alpha);
  float2 moments = lerp(moments_hist, moments_now, alpha);

  // 分散 = E[x^2] - E[x]^2。負にならないよう 0 で打ち切る。
  float variance = max(moments.y - moments.x * moments.x, 0.0);

  // 論文: 履歴が 4 フレーム未満のときは、時間方向の分散が信頼できないので、空間の分散に切り替える。
  // その空間の分散（7 x 7 のバイラテラル）は、別パスで上書きする（ここでは目印だけ残す）。
  g_out_color[p] = float4(color, count);
  g_out_moments[p] = moments;
  g_out_variance[p] = variance;
}
```

履歴の重みには `max(α, 1 / count)` の下限を使いました。count は蓄積したフレーム数で、最初の数フレームは均等な平均になり早く収束します（Yang ほか 2009 の考え方）。論文の SVGF は固定 α です。この処理は私が足しました。3 × 3 の探し直しも実装していません。

### 反射の再投影：2 つの候補 {#reflect-reproject}

反射像を追うには 2 つの方法があります。PICA PICA の章はどちらも使い統計で選びます。

1. 反射面の動きベクトル（他の技術と共有できる）を使う。粗くて曲がった面には向くがつるつるの平らな面では失敗する。
2. ヒット点を前のフレームに再投影する。床の反射のように平らな面の反射像は正しく追えるが、曲面では失敗する。

そこで、新しい画像の各画素で平均色と標準偏差を求め距離の尺度で重みを付けます。論文の 2 行は `dist = (rgb − rgb_mean) / rgb_deviation` と `w = exp2(−10 × luma(dist))` です。履歴の色が新しい色の分布から離れるほど w は 0 に近づきます。最後に、Karis の方法で局所の統計で履歴を棄却または切り詰めます。偏りは出るがゴーストをよく消し、リアルタイムには十分だと書かれています。

## 空間の再構成：1/4 レイ/画素を全解像度にする {#spatial}

半分の解像度のヒットを全解像度の画素に配ります。画素ごとに近傍のヒットを集め重みを `localBrdf(pixel.hit) / pixel.hitPdf` にします。局所 BRDF はその画素の面が、そのヒットの向きにどれだけ光を返すかを表します。元のレイの確率 pdf で割るのは、重点サンプリングで選ばれやすかったぶんを戻すためです。章はこの処理で実際に 16 レイ/画素を撃つのに近い分散の低下が得られ偏りはあるが実用上よく働く、と書いています。

```hlsl
// 反射のデノイズ ③: 反射に特有の 2 つの処理（Ray Tracing Gems 第 25 章、PICA PICA）。
//   A. 空間の再構成: 1/4 レイ/画素のヒットを、近傍から集めて、全解像度の画素に配る。
//   B. 時間の再投影: 「反射面の動きベクトル」と「ヒット点の再投影」を、統計で選んで混ぜる。

// ---------------- A. 空間の再構成 ----------------

Texture2D<float4> g_hit_radiance : register(t0);   // 半分の解像度のヒット。rgb = 当たった点の光、a = ヒット距離
Texture2D<float4> g_hit_dir_pdf : register(t1);    // 半分の解像度のヒット。xyz = 反射レイの向き、w = サンプルの確率 pdf
Texture2D<float4> g_normal_rough : register(t2);   // 全解像度。xyz = 法線、w = 粗さ
Texture2D<float> g_depth : register(t3);           // 全解像度の線形深度 [m]
Texture2D<float4> g_position : register(t4);       // 全解像度のワールド位置（xyz）
RWTexture2D<float4> g_reconstructed : register(u0); // 全解像度に再構成した反射

cbuffer ReconCB : register(b0) {
  int2 g_full_size;          // 全解像度 [px]
  int2 g_half_size;          // 半分の解像度 [px]
  float3 g_camera_pos;       // カメラ位置 [m]
  int g_radius;              // 近傍の半径（半分の解像度の画素。一例: 2 = 5 x 5）
  float g_depth_sigma;       // 深度の許容 [m]。一例: 0.1
  float3 g_pad;
};

static const float kPi = 3.14159265;

// 画素の「局所 BRDF」× cos。ヒットの向きに対して、この画素の面がどれだけ光を返すか。
// GGX の法線分布 D と、可視性 V（高さ相関の近似）、フレネル F（F0 = 0.04）を使う。
float LocalBrdf(float3 n, float3 v, float3 l, float roughness) {
  float n_dot_l = saturate(dot(n, l));
  float n_dot_v = max(dot(n, v), 1e-4);
  if (n_dot_l <= 0.0) return 0.0;                        // 面の裏側に向かうヒットは、寄与なし
  float3 h = normalize(v + l);                           // ハーフベクトル
  float n_dot_h = saturate(dot(n, h));
  float v_dot_h = saturate(dot(v, h));
  float a = max(roughness * roughness, 1e-3);            // GGX の a。0 割りを避けて下限を置く（足した処理）
  float a2 = a * a;
  float d_term = n_dot_h * n_dot_h * (a2 - 1.0) + 1.0;
  float D = a2 / (kPi * d_term * d_term);                // 法線分布
  float gv = n_dot_l * (n_dot_v * (1.0 - a) + a);
  float gl = n_dot_v * (n_dot_l * (1.0 - a) + a);
  float V = 0.5 / max(gv + gl, 1e-5);                    // 可視性
  float F = 0.04 + (1.0 - 0.04) * pow(1.0 - v_dot_h, 5.0);   // シュリックのフレネル
  return D * V * F * n_dot_l;                            // cos まで含めた、反射率
}

[numthreads(8, 8, 1)]
void ReconstructCS(uint3 id : SV_DispatchThreadID) {
  int2 p = int2(id.xy);
  if (any(p >= g_full_size)) return;

  float4 nr = g_normal_rough.Load(int3(p, 0));
  float3 n = normalize(nr.xyz);
  float roughness = nr.w;
  float3 pos = g_position.Load(int3(p, 0)).xyz;
  float depth = g_depth.Load(int3(p, 0));
  float3 v = normalize(g_camera_pos - pos);              // 画素から視点へ

  int2 center_half = p >> 1;                            // 対応する半分の解像度の画素

  // 近傍のヒットを集める（論文の疑似コード）:
  //   weight = localBrdf(pixel.hit) / pixel.hitPdf
  //   result += color(pixel.hit) * weight;  weightSum += weight
  float3 result = 0;
  float weight_sum = 0;
  for (int j = -g_radius; j <= g_radius; ++j) {
    for (int i = -g_radius; i <= g_radius; ++i) {
      int2 q = clamp(center_half + int2(i, j), int2(0, 0), g_half_size - 1);
      float4 hit = g_hit_radiance.Load(int3(q, 0));
      float4 dir_pdf = g_hit_dir_pdf.Load(int3(q, 0));

      // 近傍のヒットが、別の面の画素から出たレイでないか調べる。全解像度の深度で比べる。
      float q_depth = g_depth.Load(int3(min(q * 2, g_full_size - 1), 0));
      float depth_w = exp(-abs(q_depth - depth) / g_depth_sigma);   // 深度が離れるほど捨てる。足した処理

      // この画素から見て、そのヒットの向きが、BRDF 的にどれだけ「ありそう」か。
      // 元のレイの確率 pdf で割る = 重点サンプリングの補正（そのレイが選ばれやすかったぶんを戻す）。
      float w = LocalBrdf(n, v, dir_pdf.xyz, roughness) / max(dir_pdf.w, 1e-4) * depth_w;

      result += hit.rgb * w;
      weight_sum += w;
    }
  }
  // 論文は「偏りがあるが実用上よく働く」と書いている。weight_sum が 0 なら黒（反射なし）。
  g_reconstructed[p] = float4(weight_sum > 1e-6 ? result / weight_sum : 0.0, 1.0);
}
```

深度の重みは私が足しました。別の面の画素から出たレイを混ぜないためです。ヒットの向きが面の裏側に向くレイは BRDF の cos が 0 なので、自動的に捨てられます。

```hlsl
// ---------------- B. 時間の再投影 ----------------

Texture2D<float4> g_history : register(t5);          // 前フレームのデノイズ後の反射
Texture2D<float2> g_motion : register(t6);           // 反射面の動きベクトル（UV の差）
Texture2D<float4> g_new : register(t7);              // 今のフレームの再構成した反射
Texture2D<float> g_hit_distance : register(t8);      // 全解像度のヒット距離 [m]
SamplerState g_linear_clamp : register(s0);
RWTexture2D<float4> g_out : register(u1);

cbuffer ReprojectCB : register(b1) {
  float4x4 g_prev_view_proj;   // 前フレームのワールド → クリップ
  float3 g_camera_pos_now;
  float g_blend;               // 履歴の最大の重み（一例: 0.9）
  float2 g_inv_size;
  float2 g_pad2;
};

float Luma(float3 c) {
  return dot(c, float3(0.2126, 0.7152, 0.0722));
}

[numthreads(8, 8, 1)]
void ReprojectCS(uint3 id : SV_DispatchThreadID) {
  int2 p = int2(id.xy);
  if (any(p >= g_full_size)) return;

  float2 uv = (p + 0.5) * g_inv_size;
  float3 pos = g_position.Load(int3(p, 0)).xyz;
  float3 view_dir = normalize(pos - g_camera_pos_now);
  float hit_dist = g_hit_distance.Load(int3(p, 0));

  // ---- 3 x 3 の統計（平均と標準偏差）。新しいフレームの再構成から ----
  float3 m1 = 0, m2 = 0;
  [unroll] for (int j = -1; j <= 1; ++j) {
    [unroll] for (int i = -1; i <= 1; ++i) {
      float3 c = g_new.Load(int3(clamp(p + int2(i, j), int2(0, 0), g_full_size - 1), 0)).rgb;
      m1 += c;
      m2 += c * c;
    }
  }
  float3 mean = m1 / 9.0;
  float3 dev = sqrt(max(m2 / 9.0 - mean * mean, 0.0)) + 1e-3;    // 標準偏差。0 割りを避ける下駄

  // ---- 候補 1: 反射面の動きベクトル ----
  float2 uv_motion = uv - g_motion.Load(int3(p, 0));
  float3 hist_motion = g_history.SampleLevel(g_linear_clamp, uv_motion, 0).rgb;

  // ---- 候補 2: ヒット点の再投影 ----
  // 反射像は、ヒット点（鏡の向こうの物）を見ている。そのヒット点を、前フレームの画面に投影する。
  float3 hit_world = pos + reflect(view_dir, normalize(g_normal_rough.Load(int3(p, 0)).xyz)) * hit_dist;
  float4 prev_clip = mul(float4(hit_world, 1.0), g_prev_view_proj);
  float2 uv_hit = prev_clip.xy / prev_clip.w * float2(0.5, -0.5) + 0.5;
  float3 hist_hit = g_history.SampleLevel(g_linear_clamp, uv_hit, 0).rgb;

  // ---- 統計で重みを決める（論文の 2 行）----
  //   dist = (rgb - rgb_mean) / rgb_deviation;   w = exp2(-10 * luma(dist));
  // 履歴の色が、新しい色の分布から遠いほど w は 0 に近づく。近いほうの候補を選ぶことになる。
  float w_motion = exp2(-10.0 * Luma(abs(hist_motion - mean) / dev));
  float w_hit = exp2(-10.0 * Luma(abs(hist_hit - mean) / dev));
  float w_sum = w_motion + w_hit;
  float3 history = (w_sum > 1e-4) ? (hist_motion * w_motion + hist_hit * w_hit) / w_sum : mean;

  // ---- 近傍の分布に合わせて履歴を切る（Karis の方法。論文: 偏るがゴーストをよく消す）----
  history = clamp(history, mean - 1.5 * dev, mean + 1.5 * dev);   // 1.5 は一例。足した処理

  // 履歴が分布に近い（w_sum が大きい）ほど、履歴を多く使う。
  float blend = g_blend * saturate(w_sum);
  float3 new_color = g_new.Load(int3(p, 0)).rgb;
  g_out[p] = float4(lerp(new_color, history, blend), 1.0);
}
```

統計で 2 つの候補の重みを決め新しい色の分布に合わせて履歴を切ります。切り詰めの幅 1.5 σ は一例です。

## 空間フィルター：分散で導く à-trous {#atrous}

### 分散の推定 {#variance}

SVGF は画素の輝度の分散を時間蓄積で推定します。1 サンプルの画素に分散は定義できません。そこで、輝度の 1 次モーメント μ1 と 2 次モーメント μ2 を色と同じ整合性の判定で時間蓄積し、`σ² = μ2' − μ1'²` で求めます。ノイズが多い所の分散は大きく、ほとんどノイズのない所（完全な影の中など）では小さくなります。この分散でノイズの多い所を強く、少ない所を弱くフィルターします。

遮蔽が解けた直後など履歴が 4 フレーム未満のときは、時間方向の分散が信頼できません。論文はこのとき 7 × 7 のバイラテラルフィルター（深度とワールド法線で重み付け）による空間の分散に切り替えます。上のコードではこの分岐を実装していません。

### à-trous ウェーブレット {#atrous-wavelet}

à-trous は「穴あき」の意味です。5 × 5 の核（B3 スプライン、`h = (1/16, 1/4, 3/8, 1/4, 1/16)` の積）を反復ごとに間隔 `step = 1, 2, 4, 8, 16` で当てます。非ゼロ要素の数は変わらずに届く範囲が広がります。

<svg class="fig flow" viewBox="0 0 720 214" role="img" aria-label="à-trous の核の広がり"><defs><marker id="dn-a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#94a3b8"/></marker></defs><text x="10" y="18" text-anchor="start" font-size="12" fill="currentColor">à-trous: 5 点の核を、間隔 step で当てる(非ゼロの数は一定、届く範囲だけ広がる)</text><text x="40" y="50" text-anchor="start" font-size="10" fill="currentColor">step = 1</text><circle cx="362" cy="46" r="4" fill="#4c8bf5"/><circle cx="371" cy="46" r="4" fill="#4c8bf5"/><circle cx="380" cy="46" r="4" fill="#4c8bf5"/><circle cx="389" cy="46" r="4" fill="#4c8bf5"/><circle cx="398" cy="46" r="4" fill="#4c8bf5"/><text x="640" y="50" text-anchor="start" font-size="10" fill="currentColor">幅 5 画素</text><text x="40" y="84" text-anchor="start" font-size="10" fill="currentColor">step = 2</text><circle cx="344" cy="80" r="4" fill="#4c8bf5"/><circle cx="362" cy="80" r="4" fill="#4c8bf5"/><circle cx="380" cy="80" r="4" fill="#4c8bf5"/><circle cx="398" cy="80" r="4" fill="#4c8bf5"/><circle cx="416" cy="80" r="4" fill="#4c8bf5"/><text x="640" y="84" text-anchor="start" font-size="10" fill="currentColor">幅 9 画素</text><text x="40" y="118" text-anchor="start" font-size="10" fill="currentColor">step = 4</text><circle cx="308" cy="114" r="4" fill="#4c8bf5"/><circle cx="344" cy="114" r="4" fill="#4c8bf5"/><circle cx="380" cy="114" r="4" fill="#4c8bf5"/><circle cx="416" cy="114" r="4" fill="#4c8bf5"/><circle cx="452" cy="114" r="4" fill="#4c8bf5"/><text x="640" y="118" text-anchor="start" font-size="10" fill="currentColor">幅 17 画素</text><text x="40" y="152" text-anchor="start" font-size="10" fill="currentColor">step = 8</text><circle cx="236" cy="148" r="4" fill="#4c8bf5"/><circle cx="308" cy="148" r="4" fill="#4c8bf5"/><circle cx="380" cy="148" r="4" fill="#4c8bf5"/><circle cx="452" cy="148" r="4" fill="#4c8bf5"/><circle cx="524" cy="148" r="4" fill="#4c8bf5"/><text x="640" y="152" text-anchor="start" font-size="10" fill="currentColor">幅 33 画素</text><text x="40" y="186" text-anchor="start" font-size="10" fill="currentColor">step = 16</text><circle cx="92" cy="182" r="4" fill="#4c8bf5"/><circle cx="236" cy="182" r="4" fill="#4c8bf5"/><circle cx="380" cy="182" r="4" fill="#4c8bf5"/><circle cx="524" cy="182" r="4" fill="#4c8bf5"/><circle cx="668" cy="182" r="4" fill="#4c8bf5"/><text x="640" y="186" text-anchor="start" font-size="10" fill="currentColor">幅 65 画素</text><line x1="380" y1="30" x2="380" y2="200" stroke="#e5aa28" stroke-dasharray="3 3"/></svg>

論文は 5 回の反復を使い有効な足跡を 65 × 65 画素と書いています。C++ で数えると最後の反復だけで 4 × 16 + 1 ＝ 65 画素に届き、全反復を合わせた半径は 62 画素です。

各画素の重みは `w = h × w_z × w_n × w_l` で 3 つの edge-stopping 関数の積です。

- 深度 `w_z = exp(−|z(p) − z(q)| / (σ_z |∇z・(p − q)| + ε))`。画素の位置の差に沿った平面からのずれを測る。σ_z は 1。
- 法線 `w_n = max(0, n(p)・n(q))^σ_n`。σ_n は 128 と大きく、向きの違いに急に反応する。
- 輝度 `w_l = exp(−|l(p) − l(q)| / (σ_l √G(Var) + ε))`。分散で正規化することであらゆるスケールに自動で適応する。分散を 3 × 3 のガウスで先にぼかすのは、低サンプルでの不安定を避けるためで、ぼかした分散は次の反復には渡さない。σ_l は 4。

反復のたびに分散もフィルターして更新します。分散が独立だと仮定して `Var' = Σ h² w² Var / (Σ h w)²` です。反復が進むと分散は下がるので、輝度の重みの効きが強くなりぼかしすぎを防ぎます。

```hlsl
// 反射のデノイズ ②: 分散で導く à-trous ウェーブレット フィルター（SVGF の 4.3 と 4.4）。
// 1 回の呼び出しが 1 反復。step = 1, 2, 4, 8, 16 と変えて 5 回呼ぶ。反復ごとに、
// 5 x 5 の核の間隔が 2 倍になり、非ゼロ要素の数（25）は変わらずに、届く範囲が広がる。

Texture2D<float4> g_color_in : register(t0);       // 前の反復の色（rgb）。a は使わない
Texture2D<float> g_variance_in : register(t1);     // 前の反復の分散
Texture2D<float> g_depth : register(t2);           // クリップ空間の深度 z（ラスタライズで作ったもの）
Texture2D<float4> g_normal : register(t3);         // ワールド法線
RWTexture2D<float4> g_color_out : register(u0);
RWTexture2D<float> g_variance_out : register(u1);

cbuffer AtrousCB : register(b0) {
  int2 g_size;
  int g_step;               // この反復の間隔（1, 2, 4, 8, 16）
  float g_sigma_z;          // 深度の許容。論文は 1
  float g_sigma_n;          // 法線の指数。論文は 128
  float g_sigma_l;          // 輝度の許容。論文は 4
  float2 g_pad;
};

// 5 点の核 h = (1/16, 1/4, 3/8, 1/4, 1/16)（B3 スプライン）。2 次元は積。
static const float kKernel[5] = {1.0 / 16.0, 1.0 / 4.0, 3.0 / 8.0, 1.0 / 4.0, 1.0 / 16.0};

float Luminance(float3 c) {
  return dot(c, float3(0.2126, 0.7152, 0.0722));
}

// 輝度の分散を 3 x 3 のガウスでぼかしたもの（論文: 輝度の重みの安定のため）。
// このぼかしは、重みの計算だけに使って、次の反復に渡す分散には使わない。
float BlurredVariance(int2 p) {
  static const float k3[3] = {1.0 / 4.0, 1.0 / 2.0, 1.0 / 4.0};   // ガウスの近似 (1 2 1)/4
  float sum = 0;
  [unroll] for (int j = -1; j <= 1; ++j) {
    [unroll] for (int i = -1; i <= 1; ++i) {
      int2 q = clamp(p + int2(i, j), int2(0, 0), g_size - 1);
      sum += g_variance_in.Load(int3(q, 0)) * k3[i + 1] * k3[j + 1];
    }
  }
  return sum;
}

[numthreads(8, 8, 1)]
void main(uint3 id : SV_DispatchThreadID) {
  int2 p = int2(id.xy);
  if (any(p >= g_size)) return;

  float4 center_color = g_color_in.Load(int3(p, 0));
  float center_lum = Luminance(center_color.rgb);
  float center_var = g_variance_in.Load(int3(p, 0));
  float center_z = g_depth.Load(int3(p, 0));
  float3 center_n = g_normal.Load(int3(p, 0)).xyz;

  // 深度の勾配（画面の x, y 方向）。隣の画素との差で近似する。論文は ∇z の内積で平面からのずれを測る。
  float z_dx = g_depth.Load(int3(min(p + int2(1, 0), g_size - 1), 0)) - center_z;
  float z_dy = g_depth.Load(int3(min(p + int2(0, 1), g_size - 1), 0)) - center_z;

  // 輝度の重みの分母: σ_l * sqrt(ぼかした分散) + ε。ノイズが大きい所ほど、輝度の違いを大目に見る。
  float lum_scale = g_sigma_l * sqrt(max(BlurredVariance(p), 0.0)) + 1e-4;

  float3 sum_color = 0;
  float sum_var = 0;
  float sum_w = 0;
  float sum_w2h2 = 0;                                             // 分散の伝播に使う Σ h²w²

  [unroll] for (int j = -2; j <= 2; ++j) {
    [unroll] for (int i = -2; i <= 2; ++i) {
      int2 q = p + int2(i, j) * g_step;                           // 間隔 step の 5 x 5
      if (any(q < 0) || any(q >= g_size)) continue;               // 画面の外は使わない

      float h = kKernel[i + 2] * kKernel[j + 2];                  // 核の重み

      // ---- 3 つの edge-stopping 関数 ----
      // 深度 w_z = exp(-|z(p) - z(q)| / (σ_z |∇z・(p - q)| + ε))。平面なら同じ面と見なす。
      float z = g_depth.Load(int3(q, 0));
      float plane_diff = abs(z_dx * i * g_step + z_dy * j * g_step);   // ∇z・(p - q) の大きさ
      float w_z = exp(-abs(center_z - z) / (g_sigma_z * plane_diff + 1e-5));

      // 法線 w_n = max(0, n(p)・n(q))^σ_n。向きが違うほど急に 0 に近づく。
      float3 n = g_normal.Load(int3(q, 0)).xyz;
      float w_n = pow(max(0.0, dot(center_n, n)), g_sigma_n);

      // 輝度 w_l = exp(-|l(p) - l(q)| / (σ_l sqrt(Var) + ε))。
      float lum = Luminance(g_color_in.Load(int3(q, 0)).rgb);
      float w_l = exp(-abs(center_lum - lum) / lum_scale);

      float w = h * w_z * w_n * w_l;                              // 論文の式 (1)(2): h(q) * w(p, q)
      sum_color += w * g_color_in.Load(int3(q, 0)).rgb;
      sum_var += w * w * g_variance_in.Load(int3(q, 0));          // 分散は、重みの 2 乗で伝わる
      sum_w += w;
    }
  }

  // 正規化。重みの合計が 0 に近いときは、元の値を残す（全部が別の面だったとき）。
  if (sum_w < 1e-6) {
    g_color_out[p] = center_color;
    g_variance_out[p] = center_var;
    return;
  }
  g_color_out[p] = float4(sum_color / sum_w, center_color.a);
  // 論文: Var(ĉ_{i+1}(p)) = Σ h² w² Var(ĉ_i(q)) / (Σ h w)²。
  // ここでは w に h を含めたので、sum_var は Σ w² Var、分母は (Σ w)² になる。
  g_variance_out[p] = sum_var / (sum_w * sum_w);
}
```

### 数字で確かめる {#numbers}

輝度の重みの効果を 1 次元で確かめました。段差（0.2 → 1.0）に 1 サンプルのノイズ（標準偏差 0.3）をのせ、400 通りの乱数で試します。段差の幅は 400 通りの平均の形から測ります（10 % から 90 % に上がる幅）。

MSVC（`/std:c++latest /W4`）でコンパイルして実行しました。HLSL は `fxc`（cs_5_0）でコンパイルして確かめました。実行して絵は確かめていません。「足した処理」「一例」と書いた所は資料にない処理です。

```cpp
// 1 次元で、à-trous ウェーブレット フィルターの挙動を確かめる。
//  信号: 段差（0.2 → 1.0）。各画素は 1 サンプルのモンテカルロ（標準偏差 sigma_noise）でノイズがのる。
//  比べるもの: (a) フィルターなし (b) 輝度の edge-stopping なし (c) SVGF の輝度の重みあり
#include <algorithm>
#include <cmath>
#include <cstdio>
#include <random>
#include <vector>

namespace {
constexpr int kN = 512;                  // 画素数
constexpr int kEdge = 256;               // 段差の位置
constexpr double kLow = 0.2, kHigh = 1.0;
constexpr double kSigmaNoise = 0.3;      // 1 サンプルのノイズの標準偏差
constexpr double kSigmaL = 4.0;          // 論文の輝度の許容

const double kKernel[5] = {1.0 / 16, 1.0 / 4, 3.0 / 8, 1.0 / 4, 1.0 / 16};   // B3 スプライン

double Truth(int i) { return i < kEdge ? kLow : kHigh; }

// 1 反復。step は 1, 2, 4, 8, 16。use_lum が true なら、輝度の edge-stopping を使う。
// var は画素ごとの分散（反復ごとに、重みの 2 乗で伝播させる）。
void Atrous(const std::vector<double>& in, const std::vector<double>& var_in, int step, bool use_lum,
            std::vector<double>* out, std::vector<double>* var_out) {
  out->assign(kN, 0.0);
  var_out->assign(kN, 0.0);
  for (int p = 0; p < kN; ++p) {
    // 輝度の重みの分母。分散を 3 点 (1 2 1)/4 でぼかして使う（論文の 3x3 ガウスの 1 次元版）。
    double v = 0.0;
    const double g3[3] = {0.25, 0.5, 0.25};
    for (int d = -1; d <= 1; ++d) v += var_in[std::clamp(p + d, 0, kN - 1)] * g3[d + 1];
    const double scale = kSigmaL * std::sqrt(std::max(v, 0.0)) + 1e-4;

    double sum = 0, sum_w = 0, sum_w2v = 0;
    for (int k = -2; k <= 2; ++k) {
      const int q = p + k * step;
      if (q < 0 || q >= kN) continue;
      double w = kKernel[k + 2];
      if (use_lum) w *= std::exp(-std::fabs(in[p] - in[q]) / scale);
      sum += w * in[q];
      sum_w += w;
      sum_w2v += w * w * var_in[q];                        // 分散の伝播: Σ w² Var
    }
    (*out)[p] = sum / sum_w;
    (*var_out)[p] = sum_w2v / (sum_w * sum_w);
  }
}

struct Stats {
  double rmse_flat_low = 0, rmse_flat_high = 0;            // 平らな部分の誤差（ノイズの残り）
  double edge_width = 0;                                   // 段差が 10 % から 90 % に立ち上がる幅 [px]
};

Stats Measure(const std::vector<double>& v) {
  Stats s;
  double a = 0, b = 0;
  int na = 0, nb = 0;
  for (int i = 30; i < kEdge - 40; ++i) { a += (v[i] - kLow) * (v[i] - kLow); ++na; }       // 段差から離れた低い側
  for (int i = kEdge + 40; i < kN - 30; ++i) { b += (v[i] - kHigh) * (v[i] - kHigh); ++nb; }  // 高い側
  s.rmse_flat_low = std::sqrt(a / na);
  s.rmse_flat_high = std::sqrt(b / nb);
  const double lo = kLow + 0.1 * (kHigh - kLow), hi = kLow + 0.9 * (kHigh - kLow);
  int first = -1, last = -1;
  for (int i = kEdge - 40; i < kEdge + 40; ++i) {
    if (first < 0 && v[i] > lo) first = i;
    if (v[i] < hi) last = i;
  }
  s.edge_width = (first >= 0 && last >= first) ? last - first + 1 : 0;
  return s;
}
}  // namespace

int main() {
  std::mt19937_64 rng(11);
  std::normal_distribution<double> noise(0.0, kSigmaNoise);
  constexpr int kTrials = 400;           // ノイズの出方を 400 通り試して平均する（段差の幅は平均の形から測る）

  std::printf("== 入力（1 spp）==\n");
  {
    double a = 0, b = 0;
    int na = 0, nb = 0;
    for (int t = 0; t < kTrials; ++t) {
      for (int i = 30; i < kEdge - 40; ++i) { const double e = noise(rng); a += e * e; ++na; }
      for (int i = kEdge + 40; i < kN - 30; ++i) { const double e = noise(rng); b += e * e; ++nb; }
    }
    std::printf("平らな部分の誤差 RMSE: 低い側 %.3f, 高い側 %.3f\n", std::sqrt(a / na), std::sqrt(b / nb));
  }

  for (int mode = 0; mode < 2; ++mode) {
    const bool use_lum = (mode == 1);
    std::printf("\n== %s ==\n", use_lum ? "輝度の edge-stopping あり（SVGF）" : "輝度の edge-stopping なし（ただのぼかし）");
    std::printf("反復  step  低い側RMSE  高い側RMSE  段差の幅[px]\n");
    double mse_low[5] = {}, mse_high[5] = {};
    std::vector<std::vector<double>> mean_profile(5, std::vector<double>(kN, 0.0));
    for (int t = 0; t < kTrials; ++t) {
      std::vector<double> cur(kN), v(kN, kSigmaNoise * kSigmaNoise), next, vnext;
      for (int i = 0; i < kN; ++i) cur[i] = Truth(i) + noise(rng);     // 1 サンプル/画素
      for (int it = 0; it < 5; ++it) {
        Atrous(cur, v, 1 << it, use_lum, &next, &vnext);
        cur.swap(next);
        v.swap(vnext);
        const Stats s = Measure(cur);
        mse_low[it] += s.rmse_flat_low * s.rmse_flat_low;
        mse_high[it] += s.rmse_flat_high * s.rmse_flat_high;
        for (int i = 0; i < kN; ++i) mean_profile[it][i] += cur[i] / kTrials;
      }
    }
    for (int it = 0; it < 5; ++it) {
      const Stats prof = Measure(mean_profile[it]);                     // 平均の形から、段差の幅を測る
      std::printf("%3d   %3d   %8.3f   %8.3f   %8.0f\n", it + 1, 1 << it, std::sqrt(mse_low[it] / kTrials),
                  std::sqrt(mse_high[it] / kTrials), prof.edge_width);
    }
  }

  // 時間方向の指数移動平均（SVGF の α = 0.2）の、等価サンプル数。
  const double alpha = 0.2;
  std::printf("\nα = %.1f の定常の等価サンプル数: %.1f（(2 - α) / α）\n", alpha, (2.0 - alpha) / alpha);
  std::printf("à-trous の足跡: 1 反復あたり 4 x step + 1 画素、5 反復の最後は %d 画素、合計の半径 %d 画素\n",
              4 * 16 + 1, 2 * (1 + 2 + 4 + 8 + 16));
  return 0;
}
```

```text title="実行結果"
== 入力（1 spp）==
平らな部分の誤差 RMSE: 低い側 0.300, 高い側 0.301
```

```text title="実行結果（続き）"
== 輝度の edge-stopping なし（ただのぼかし） ==
反復  step  低い側RMSE  高い側RMSE  段差の幅[px]
  1     1      0.157      0.156          2
  2     2      0.105      0.104          6
  3     4      0.073      0.073         12
  4     8      0.052      0.051         24
  5    16      0.037      0.036         48
```

```text title="実行結果（続き）"
== 輝度の edge-stopping あり（SVGF） ==
反復  step  低い側RMSE  高い側RMSE  段差の幅[px]
  1     1      0.181      0.179          2
  2     2      0.124      0.122          4
  3     4      0.089      0.088          6
  4     8      0.066      0.065          6
  5    16      0.051      0.050          5
```

```text title="実行結果（続き）"
α = 0.2 の定常の等価サンプル数: 9.0（(2 - α) / α）
à-trous の足跡: 1 反復あたり 4 x step + 1 画素、5 反復の最後は 65 画素、合計の半径 62 画素
```

ただのぼかしはノイズの RMSE が 0.30 から 0.037 まで下がりますが、段差の幅が 2 画素から 48 画素に広がります。輝度の重みがあると RMSE は 0.051 と少し高いままですが、段差は 5 画素のまま保たれます。これが「ぼかしを強くするほど段差が鈍る」取引を分散で調整する効果です。

<svg class="fig flow" viewBox="0 0 700 234" role="img" aria-label="ノイズと段差の取引"><defs><marker id="dn-a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#94a3b8"/></marker></defs><text x="10" y="18" text-anchor="start" font-size="12" fill="currentColor">反復ごとの、ノイズ(RMSE、左)と段差の幅(px、右)。入力のノイズは 0.30</text><line x1="60" y1="170" x2="300" y2="170" stroke="#94a3b8"/><line x1="60" y1="40" x2="60" y2="170" stroke="#94a3b8"/><polyline points="80.0,68.0 130.0,101.8 180.0,122.6 230.0,136.2 280.0,145.9" fill="none" stroke="#94a3b8" stroke-width="2.5"/><circle cx="80.0" cy="68.0" r="3" fill="#94a3b8"/><circle cx="130.0" cy="101.8" r="3" fill="#94a3b8"/><circle cx="180.0" cy="122.6" r="3" fill="#94a3b8"/><circle cx="230.0" cy="136.2" r="3" fill="#94a3b8"/><circle cx="280.0" cy="145.9" r="3" fill="#94a3b8"/><polyline points="80.0,52.4 130.0,89.4 180.0,112.2 230.0,127.1 280.0,136.9" fill="none" stroke="#e5aa28" stroke-width="2.5"/><circle cx="80.0" cy="52.4" r="3" fill="#e5aa28"/><circle cx="130.0" cy="89.4" r="3" fill="#e5aa28"/><circle cx="180.0" cy="112.2" r="3" fill="#e5aa28"/><circle cx="230.0" cy="127.1" r="3" fill="#e5aa28"/><circle cx="280.0" cy="136.9" r="3" fill="#e5aa28"/><text x="80.0" y="184" text-anchor="middle" font-size="10" fill="currentColor">1</text><text x="130.0" y="184" text-anchor="middle" font-size="10" fill="currentColor">2</text><text x="180.0" y="184" text-anchor="middle" font-size="10" fill="currentColor">3</text><text x="230.0" y="184" text-anchor="middle" font-size="10" fill="currentColor">4</text><text x="280.0" y="184" text-anchor="middle" font-size="10" fill="currentColor">5</text><text x="180.0" y="200" text-anchor="middle" font-size="10" fill="currentColor">反復</text><text x="54" y="46" text-anchor="end" font-size="10" fill="currentColor">0.2</text><line x1="390" y1="170" x2="630" y2="170" stroke="#94a3b8"/><line x1="390" y1="40" x2="390" y2="170" stroke="#94a3b8"/><polyline points="410.0,164.8 460.0,154.4 510.0,138.8 560.0,107.6 610.0,45.2" fill="none" stroke="#94a3b8" stroke-width="2.5"/><circle cx="410.0" cy="164.8" r="3" fill="#94a3b8"/><circle cx="460.0" cy="154.4" r="3" fill="#94a3b8"/><circle cx="510.0" cy="138.8" r="3" fill="#94a3b8"/><circle cx="560.0" cy="107.6" r="3" fill="#94a3b8"/><circle cx="610.0" cy="45.2" r="3" fill="#94a3b8"/><polyline points="410.0,164.8 460.0,159.6 510.0,154.4 560.0,154.4 610.0,157.0" fill="none" stroke="#e5aa28" stroke-width="2.5"/><circle cx="410.0" cy="164.8" r="3" fill="#e5aa28"/><circle cx="460.0" cy="159.6" r="3" fill="#e5aa28"/><circle cx="510.0" cy="154.4" r="3" fill="#e5aa28"/><circle cx="560.0" cy="154.4" r="3" fill="#e5aa28"/><circle cx="610.0" cy="157.0" r="3" fill="#e5aa28"/><text x="410.0" y="184" text-anchor="middle" font-size="10" fill="currentColor">1</text><text x="460.0" y="184" text-anchor="middle" font-size="10" fill="currentColor">2</text><text x="510.0" y="184" text-anchor="middle" font-size="10" fill="currentColor">3</text><text x="560.0" y="184" text-anchor="middle" font-size="10" fill="currentColor">4</text><text x="610.0" y="184" text-anchor="middle" font-size="10" fill="currentColor">5</text><text x="510.0" y="200" text-anchor="middle" font-size="10" fill="currentColor">反復</text><text x="384" y="46" text-anchor="end" font-size="10" fill="currentColor">50</text><text x="60" y="222" text-anchor="start" font-size="10" fill="currentColor">灰: ただのぼかし(ノイズは減るが段差が 48 px に広がる)　黄: 輝度の重みあり(段差は 5 px)</text></svg>

## 実装の注意と限界 {#limits}

SVGF の速さは 1280 × 720 で平均 4.4 ms、1920 × 1080 で 10.2 ms（NVIDIA TITAN X Pascal）です。解像度に線形で約 2 億画素/秒です。コストの変動は平均の 15 % 以内で、変動は全部が分散推定（遮蔽が解けた画素が増えると空間の分散に切り替わる）から来ます。最悪のフレームは画面全体が遮蔽解除になる起動時などで、最良の約 50 % 増しです。時間の安定は従来の手法より約 10 倍よいと書かれています。

論文自身が挙げる限界は次のとおりです。

- 輝度の分散しか追わないので、色の反射が過度にぼける（色成分ごとの分散で直せるが、メモリと計算が増える）。
- 動きの速い物が光源に近いと影が物から離れて見える（時間蓄積が、照明の変化に気づかない）。
- 極端に暗い所（わずかな間接光だけ）で、ノイズが時間的に不安定になる。
- 確率的に雑音が入る反射はノイズと一緒にぼける。
- 動きの中で履歴の逆投影による細部のぼけが出る。
- 確率的な主光線（被写界深度や運動ぶれ）には使えない。G バッファのノイズのなさが前提。
- サブピクセルのジオメトリが極端にエイリアスしていると、edge-stopping が有効な近傍を見つけられない。

## ノイズを減らす入力側の工夫 {#input}

デノイザーに渡す前の段階でもノイズを減らせます。

- 重点サンプリング。PICA PICA は素材の法線分布だけを重点サンプリングします。
- 低食い違いの列（Halton）。SVGF も 16 個程度の Halton 列を巡回して使います。
- 反射はアルベドを割って照明だけにしてから、フィルターする。SVGF もアルベドを除いてから再構成し、あとで掛け直します。細かいテクスチャをぼかさずに済みます。
- 反射と拡散は別々にデノイズする。SVGF も直接光と間接光を別々に再構成します。

## 長所と短所

- 長所: 1 サンプル/画素の入力から、時間的に安定した結果が得られる。
- 長所: 分散で導くので場面に依存するパラメーターが要らない（σ_z、σ_n、σ_l は固定でよい）。
- 短所: ぼやけゴースト、細部の損失が引き換えに出る。
- 短所: G バッファが要る。反射の再投影にはヒット距離などの追加の入力が要る。

## よくあるミス

??? failure "動く反射が尾を引く（ゴースト）"
    履歴の棄却が足りない。整合性の判定（深度・法線・ID）を厳しくし、新しい色の分布で履歴を切り詰める。ヒット点の再投影と動きベクトルを統計で選ぶ。

??? failure "反射の細部が消える"
    空間フィルターが強すぎる。輝度の重みを入れ法線の σ_n を大きく保つ。粗さの小さい面はほとんどぼかさない。

??? failure "遮蔽が解けた所に色の付いたノイズが残る"
    履歴が無い間の分散を時間方向で推定している。履歴が 4 フレーム未満のときは空間の分散に切り替える。

??? failure "平らな床の反射がずれてぼやける"
    反射面の動きベクトルだけで再投影している。ヒット点の再投影を足し新しい色の統計で選ぶ。

??? failure "画面の端で、フィルターの結果が暗くなる"
    画面外の画素を重み 0 としながら、正規化していない。有効な重みの合計で割る。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 時間は整合性を調べて、合わない履歴を捨てる。
    - [x] 空間は輝度の分散で導く。ノイズの多い所を強く少ない所を弱く。
    - [x] 反射の再投影は動きベクトルとヒット点の 2 つを統計で選ぶ。
    - [x] 1/4 レイ/画素は、BRDF で重み付けして近傍から集める。
    - [x] ぼかしの強さと段差の鈍りは引き換え。分散で画素ごとに決める。

## 参考

- Christoph Schied, Anton Kaplanyan, Chris Wyman, Anjul Patney, Chakravarty R. Alla Chaitanya, John Burgess, Shiqiu Liu, Carsten Dachsbacher, Aaron Lefohn, Marco Salvi, "Spatiotemporal Variance-Guided Filtering: Real-Time Reconstruction for Path-Traced Global Illumination", Proceedings of HPG '17, 2017. DOI: 10.1145/3105762.3105770（本文を全部読んだ。図とビデオは見ていない）
- Colin Barré-Brisebois, Henrik Halén, Graham Wihlidal, Andrew Lauritzen, Jasper Bekkers, Tomasz Stachowiak, Johan Andersson, "Hybrid Rendering for Real-Time Ray Tracing", Ray Tracing Gems, Chapter 25, Apress, 2019. DOI: 10.1007/978-1-4842-4427-2_25（25.2.2 を中心に読んだ。性能の図は読めていない）
- Dammertz ほか, "Edge-Avoiding À-Trous Wavelet Transform for Fast Global Illumination Filtering", HPG 2010（読んでいない。SVGF が土台にしたと書かれている）
- NVIDIA, "Real-Time Denoisers (NRD)"（読んでいない）

## 関連ページ

- [Ray-Traced Reflections](index.md)
- [Hybrid Pipeline](hybrid.md)
- [Ray Generation](ray-generation.md)
- [AO Filtering](../../ao/filtering/index.md)
