---
title: ASSAO and CACAO
tags:
  - 描画
---

# ASSAO and CACAO

SSAO は取りの数を増やすほどきれいになりますが、そのぶん重くなります。1080p の画面で High 設定なら 1 画素あたり 24 回の深度読み込みで、1 フレームに約 4,980 万回です。ASSAO（Adaptive SSAO）は、Intel が 2016 年に公開した SSAO の実装で、この読み込みを軽くするために画面を 2×2 に分けて処理し、辺を見るぼかしで戻し AO が大きく変わる所にだけ取りを足します。実装が MIT ライセンスで読めるので、このページは `ASSAO.hlsl`（1184 行）を全部読んで、品質ごとに何を足しているか遮蔽量の式はどうなっているか辺をどう守っているかを、HLSL と数字で整理します。CACAO（FidelityFX）は ASSAO を基にした実装と言われますが、このページでは読んでいません。

!!! tip "ポイント"
    - ASSAO は深度を線形化して、2×2 の位置ごとに 4 枚の半解像度のテクスチャ（デインターリーブ）にする。1 枚は 960×540。遠い取りほど粗いミップから読む。
    - 品質は 5 段階（プリセット 0〜4）。Low は 3 取り Medium は 5 取り High は 12 取りで、取りごとに対称の 2 点を読む。1080p で深度の読み込みは 12.4 M、20.7 M、49.8 M 回。Highest（適応）は最大 32 取り（132.7 M 回）。
    - 遮蔽量は `max(0, N·D̂ − しきい値) × falloff`。しきい値（`EffectHorizonAngleThreshold`、0.05〜0.5）が地面に近い平らな面の誤った暗さを抑える。
    - 対称の 2 点を読むと同じ取りの数でノイズが大きく減る。このページの実験では 12 取りで標準偏差が 0.051 から 0.011 になった。
    - 辺を見るぼかしは辺を越えて混ぜない。深度の段差の例でただのぼかしは 0.95 → 0.80 → 0.65 → 0.50 と滲んだが、辺を見るぼかしは 0.95 → 0.50 の段差のままだった。

!!! info "このページを読む前に"
    - [SSAO（半球）](ssao-hemisphere.md)（深度から AO を作る基本）
    - [AO Filtering](filtering/index.md)（バイラテラル ブラー）

## 読んだ資料とこのページの範囲 {#sources}

- Intel の ASSAO（GameTechDev/ASSAO）の `ASSAO.hlsl`、全 1184 行を全部読みました。MIT ライセンスです。同じリポジトリの README はこのコードがもう更新されず[XeGTAO](xegtao.md) に置き換えられたと書いています。C++ 側（定数の既定値、パスの組み立て）は読んでいないので、定数のうち HLSL に書かれていないもの（`SSAO_ADAPTIVE_TAP_BASE_COUNT`、`SSAO_MAX_TAPS` など）の値はこのページでは示しません。
- AMD の FidelityFX CACAO は読んでいません。旧版は「ASSAO を FidelityFX に移植して発展させた」と書いていましたが、このページでは確かめていないので、CACAO のパラメーターや品質設定の数字は書きません。
- 論文はありません。数字は `ASSAO.hlsl` の値とこのページの C++ の実験です。

HLSL は `ASSAO.hlsl` の要点を書き直したもので、`fxc`（`ps_5_0`）でコンパイルして確かめました。「足した」と書いた式はこのページが決めたもので、ASSAO の実装ではありません。

## 全体の流れ {#overview}

ASSAO は次の順に処理します。

<svg class="fig flow" viewBox="0 0 660 194" role="img" aria-label="ASSAO の流れ(青: 必ず、黄: 品質で変わる)"><defs><marker id="ar" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#94a3b8"/></marker></defs><text x="10" y="18" text-anchor="start" font-size="12" fill="currentColor">ASSAO の流れ(青: 必ず、黄: 品質で変わる)</text><rect x="10" y="34" width="150" height="50" rx="6" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="85.0" y="49.0" text-anchor="middle" font-size="11" fill="currentColor">深度を線形化</text><text x="85.0" y="63.0" text-anchor="middle" font-size="11" fill="currentColor">デインターリーブ</text><text x="85.0" y="77.0" text-anchor="middle" font-size="11" fill="currentColor">4 枚の半解像度</text><rect x="190" y="34" width="150" height="50" rx="6" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="265.0" y="56.0" text-anchor="middle" font-size="11" fill="currentColor">ミップ</text><text x="265.0" y="70.0" text-anchor="middle" font-size="11" fill="currentColor">(品質 2 以上)</text><rect x="370" y="34" width="150" height="50" rx="6" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="445.0" y="63.0" text-anchor="middle" font-size="11" fill="currentColor">深度から法線</text><rect x="550" y="34" width="150" height="50" rx="6" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="625.0" y="56.0" text-anchor="middle" font-size="11" fill="currentColor">4 パスで AO</text><text x="625.0" y="70.0" text-anchor="middle" font-size="11" fill="currentColor">3 / 5 / 12 取り</text><rect x="10" y="114" width="150" height="50" rx="6" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="85.0" y="136.0" text-anchor="middle" font-size="11" fill="currentColor">重要度で追加</text><text x="85.0" y="150.0" text-anchor="middle" font-size="11" fill="currentColor">(品質 3)</text><rect x="190" y="114" width="150" height="50" rx="6" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="265.0" y="143.0" text-anchor="middle" font-size="11" fill="currentColor">辺を見るぼかし</text><rect x="370" y="114" width="150" height="50" rx="6" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="445.0" y="143.0" text-anchor="middle" font-size="11" fill="currentColor">全解像度に戻す</text><line x1="160" y1="59.0" x2="190" y2="59.0" stroke="#94a3b8" stroke-width="1.5" marker-end="url(#ar)"/><line x1="340" y1="59.0" x2="370" y2="59.0" stroke="#94a3b8" stroke-width="1.5" marker-end="url(#ar)"/><line x1="520" y1="59.0" x2="550" y2="59.0" stroke="#94a3b8" stroke-width="1.5" marker-end="url(#ar)"/><line x1="625.0" y1="84" x2="85.0" y2="114" stroke="#94a3b8" stroke-width="1.5" marker-end="url(#ar)"/><line x1="160" y1="139.0" x2="190" y2="139.0" stroke="#94a3b8" stroke-width="1.5" marker-end="url(#ar)"/><line x1="340" y1="139.0" x2="370" y2="139.0" stroke="#94a3b8" stroke-width="1.5" marker-end="url(#ar)"/></svg>

最初に非線形の深度をビュー空間の深度に線形化し、2×2 の位置ごとに 4 枚の半解像度のテクスチャに振り分けます（デインターリーブ）。品質 2 以上では粗いミップも作ります。次に、深度から法線を作ります（法線バッファがあればそれを使う設定もあります）。それから 4 枚の半解像度に対して、品質ごとの取りの数で AO を計算します。最高品質では最初に少ない取りで AO を出し、変化の大きい所だけに追加の取りを足します。最後に、辺を見るぼかしをかけ 4 枚から全解像度に戻します。

## 深度の準備とデインターリーブ {#prepare}

```hlsl
// ================= ① 深度の線形化 =================

// ASSAO.hlsl の ScreenSpaceToViewSpaceDepth。標準の Z（near → 0、far → 1）の投影行列に対する式。
float LinearizeDepth(float d) {
  return g_depth_unpack.x / (g_depth_unpack.y - d);
}

// 画面の位置 (0〜1) とビュー空間の深度から、ビュー空間の位置へ。
float3 ViewPosition(float2 uv, float view_z) {
  return float3((g_ndc_to_view_mul * uv + g_ndc_to_view_add) * view_z, view_z);
}
```

`LinearizeDepth` は `ASSAO.hlsl` の `ScreenSpaceToViewSpaceDepth` と同じ式です。`g_depth_unpack.x = near·far/(far−near)`、`.y = far/(far−near)` を渡すと非線形の深度からビュー空間の深度が出ます。`ViewPosition` は画面の位置とビュー空間の深度から、ビュー空間の位置を出します。

デインターリーブは全解像度の深度を 2×2 の位置ごとに分けて、4 枚の半解像度にします。`PSPrepareDepths` は 2×2 の 4 画素を `Load` して、4 つの出力に 1 つずつ書きます。品質 0 で画素を市松に間引く設定のときは、4 枚のうち 2 枚（左上と右下）だけを作る経路（`PSPrepareDepthsHalf`）もあります（ソースのコメントによる。呼び出し側の C++ は読んでいません）。

ここで旧版の説明と食い違う点があります。旧版は「同じ組の画素は同じサンプル パターンを使うので、キャッシュが効く」と書いていましたが、`ASSAO.hlsl` の取りの回転はパスの中の画素の位置から `(y × 2 + x) mod 5` で選ぶ 5 通りの行列です。隣り合う画素は違う回転を使うので、「同じパターンだからキャッシュに乗る」とは読めませんでした。このファイルが示すのは解像度が半分になること（1 パスの画素数が 4 分の 1）と、粗いミップから読むことで遠い取りのテクスチャ上の範囲が縮むことです。キャッシュの効果はこのコードだけでは確かめられません。

1080p で 4 枚の半解像度は 960 × 540 = 518,400 テクセルずつです。品質 2 以上ではミップを 3 段（合計で 4 レベル）作ります。ミップを作るときは単純な平均ではなく、周りの 4 画素の「賢い平均」を使います。最も手前の深度を基準に半径内の画素を重みづけ（`saturate(dist² × (−1/R²) + 1)`）して平均します。

## 辺と法線 {#edges}

```hlsl
// ================= ② 辺の検出 =================

// 左・右・上・下の辺の強さ。1 = 辺なし、0 = 辺。
// 斜めの面でも辺と誤らないよう、反対側の隣との和（斜面で打ち消し合う）の小さいほうを取る。
float4 CalculateEdges(float center, float l, float r, float t, float b) {
  float4 e = float4(l, r, t, b) - center;
  float4 slope_adjusted = e + e.yxwz;                              // 例: 左の差 + 右の差。直線の斜面なら 0 に近い
  e = min(abs(e), abs(slope_adjusted));
  return saturate(1.3 - e / (center * 0.040));                     // 中心の深度の 4 % の差で辺。1.3 は ASSAO の値
}

// 辺 4 本を 2 ビットずつ 8 ビットに詰める（0, 1/3, 2/3, 1 の 4 段階）。
float PackEdges(float4 edges) {
  edges = round(saturate(edges) * 3.05);
  return dot(edges, float4(64.0, 16.0, 4.0, 1.0) / 255.0);
}

float4 UnpackEdges(float packed) {
  uint v = (uint)(packed * 255.5);
  float4 e = float4((v >> 6) & 3, (v >> 4) & 3, (v >> 2) & 3, v & 3) / 3.0;
  return saturate(e + g_inv_sharpness);                            // 鋭さを下げるときは辺を少し甘くする
}

// ================= ③ 深度から法線 =================

// 4 つの四分円（左上・上右・右下・下左）の外積を、辺がない所だけ足して正規化する。
float3 CalculateNormal(float4 edges_lrtb, float3 c, float3 pl, float3 pr, float3 pt, float3 pb) {
  float4 accept = float4(edges_lrtb.x * edges_lrtb.z, edges_lrtb.z * edges_lrtb.y, edges_lrtb.y * edges_lrtb.w, edges_lrtb.w * edges_lrtb.x);
  pl = normalize(pl - c); pr = normalize(pr - c); pt = normalize(pt - c); pb = normalize(pb - c);
  float3 n = float3(0, 0, -0.0005);                                // 全部の辺が切れても 0 割りにならない種
  n += accept.x * cross(pl, pt);
  n += accept.y * cross(pt, pr);
  n += accept.z * cross(pr, pb);
  n += accept.w * cross(pb, pl);
  return normalize(n);
}
```

`CalculateEdges` は左右上下の辺の強さを返します（1 = 辺なし、0 = 辺）。深度の差を中心の深度の 4 %（0.040）で割り 1.3 から引いて `saturate` します。斜めの面は左右の差が打ち消し合うので、「反対側との和」も作り絶対値の小さいほうを取ります。これで傾いた面を辺と誤らなくなります。

C++ で深度が 5 m から 10 m に段差で変わる場所の辺を計算しました。段差の手前の画素では右の辺が 0.000 で左が 1.000、段差の向こうの画素では逆でした。段差のある所だけがきちんと辺になります。

`PackEdges` は 4 本の辺を 2 ビットずつ 8 ビットに詰めます。値は 0、1/3、2/3、1 の 4 段階です。C++ で量子化を確かめると、入力 0.25 は 0.333、0.5 は 0.667、0.75 は 0.667、0.9 は 1.000 になりました。粗いですがぼかしの重みには足ります。

`CalculateNormal` は 4 つの四分円（左上・上右・右下・下左）の外積を辺のない所だけ足して正規化します。辺をまたぐ四分円は寄与しないので、段差で法線が引っ張られません。

## 取りと遮蔽量 {#tap}

### 遮蔽量の式 {#obscurance}

```hlsl
// ================= ④ 1 つの取りの遮蔽量 =================

// hit_delta = 取りの位置 − 中心の位置（ビュー空間）。falloff_mul_sq = −1 / R²。
float CalculatePixelObscurance(float3 normal, float3 hit_delta, float falloff_mul_sq) {
  float len_sq = dot(hit_delta, hit_delta);
  float n_dot_d = dot(normal, hit_delta) / sqrt(len_sq);           // 法線と、取りへの向きの余弦
  float falloff = max(0.0, len_sq * falloff_mul_sq + 1.0);         // 距離の 2 乗で 1 → 0。半径の外は 0
  return max(0.0, n_dot_d - g_horizon_threshold) * falloff;
}
```

取りの位置と中心の位置の差 `hit_delta` から、遮蔽量を出します。`n_dot_d` は法線と取りへの向きの余弦です。値が大きいほど取りは法線の上側（つまり面の上に出っ張った遮蔽物）にあります。`EffectHorizonAngleThreshold` を引くのは面とほぼ平行な（浅い角度の）取りを無視するためです。ソースのコメントは斜面やジオメトリの分割が足りないことによる誤差を抑える値で、0.05〜0.5 だと書いています。`falloff` は距離の 2 乗で 1 から 0 に下がる重みで、半径の外では 0 です。

### 取りのペアとミップ {#pairs}

ASSAO の取りは 2 点セットです。`g_samplePatternMain` の 1 点に対して中心を挟んで反対側の点も読みます（コメントは "each tap has two symmetrical depth texture samples"）。実際の深度の読み込みは取りの数の 2 倍です。パターンは 32 点で各点に (x, y, 重み, log2 の長さ) があり、最初のいくつかが全体を粗く覆う「プログレッシブ」な並びです。

```hlsl
// ================= ⑤ 取りのペア =================

static const float4 kPattern[12] = {                               // ASSAO の 32 点の最初の 12 点: (x, y, 重み, log2 の長さ)
  float4( 0.78488064,  0.56661671, 1.50, -0.126083), float4( 0.26022232, -0.29575172, 1.50, -1.064030),
  float4( 0.10459357,  0.08372527, 1.11, -2.730563), float4(-0.68286800,  0.04963045, 1.09, -0.498827),
  float4(-0.13570161, -0.64190155, 1.25, -0.532765), float4(-0.26193795, -0.08205118, 0.67, -1.783245),
  float4(-0.61177456,  0.66664219, 0.71, -0.044234), float4( 0.43675563,  0.25119025, 0.61, -1.167283),
  float4( 0.07884444,  0.86618668, 0.64, -0.459002), float4(-0.12790935, -0.29869005, 0.60, -1.729424),
  float4(-0.04031125,  0.02413622, 0.60, -4.792042), float4( 0.16201244, -0.52851415, 0.79, -1.067055) };

// 1 つの取りの対（p と、鏡写しの −p）。両方を同じ式で足す。
void TapPair(int i, float2x2 rot_scale, float3 center_pos, float3 normal, float2 center_uv, float mip_offset,
             float falloff_mul_sq, bool haloing, inout float obscurance_sum, inout float weight_sum) {
  float4 s = kPattern[i];
  float2 offset = round(mul(rot_scale, s.xy));                     // 画素の中心へ丸める（遮蔽量の式が正確になる）
  float mip = max(s.w + mip_offset, 0.0);                          // 遠い取りほど粗いミップ（Scalable AO と同じ考え方）
  [unroll] for (int k = 0; k < 2; ++k) {
    float2 o = (k == 0) ? offset : -offset;                        // 2 つ目は鏡写しの向き
    float2 uv = center_uv + o * g_viewport_2x_pixel;
    float z = g_view_depth.SampleLevel(g_point_clamp, uv, mip);
    float3 hit = ViewPosition(uv, z);
    float3 delta = hit - center_pos;
    float ob = CalculatePixelObscurance(normal, delta, falloff_mul_sq);
    float w = s.z;                                                 // 重み（ディスクの中心付近の取りは重い）
    if (haloing) {                                                 // ハロー抑制: 中心より手前にある取りの重みを下げる
      float reduct = saturate(max(0.0, -delta.z) * (-1.0 / g_effect_radius) + 2.0);
      w *= 0.6 * reduct + 0.4;                                     // 0.6 は SSAO_HALOING_REDUCTION_AMOUNT
    }
    obscurance_sum += ob * w;
    weight_sum += w;
  }
}
```

回転とスケール `rot_scale` を掛けて、位置を画素の中心に丸めます（`round`）。丸めないと遮蔽量の式が不正確になって、アーティファクトが出るとソースのコメントにあります。ミップは `s.w + mip_offset` で取りが遠いほど粗くなります。`mip_offset` は `log2(pixLookupRadiusMod) − 4.3` で−4.3 はソースのコメントで "best noise/quality/performance tradeoff, found empirically" です。品質 0 と 1 ではミップを使いません。

ハロー抑制は品質 1 以上です。中心より手前にある取り（`delta.z` が負）の重みを下げます。物体の手前の輪郭に薄い暗い縁（ハロー）が出るのを抑えます。重みは `0.6 × reduct + 0.4` です（0.6 は `SSAO_HALOING_REDUCTION_AMOUNT`）。

### 取りの数とノイズ {#noise}

実際のパターンの最初の 12 点と実際の遮蔽量の式で、ノイズを数えました。床の上の点が高さ 0.5 m の壁から 0.15 m 離れているシーンです。半径 R = 1 m、画素の大きさ 3 cm、4000 通りの回転で AO の平均と標準偏差を出しました。

<svg class="fig flow" viewBox="0 0 640 230" role="img" aria-label="AO の標準偏差(取りの数ごと、対称ペアなし/あり)"><defs><marker id="ar" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#94a3b8"/></marker></defs><text x="10" y="18" text-anchor="start" font-size="12" fill="currentColor">AO の標準偏差(取りの数ごと、対称ペアなし/あり)</text><line x1="60" y1="190" x2="600" y2="190" stroke="#94a3b8"/><line x1="60" y1="40" x2="60" y2="190" stroke="#94a3b8"/><text x="54" y="194.0" text-anchor="end" font-size="10" fill="currentColor">0</text><text x="54" y="119.0" text-anchor="end" font-size="10" fill="currentColor">0.05</text><text x="54" y="44.0" text-anchor="end" font-size="10" fill="currentColor">0.1</text><rect x="104.0" y="59.2" width="43.0" height="130.8" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="125.5" y="55.19999999999999" text-anchor="middle" font-size="10" fill="currentColor">0.0872</text><rect x="150.0" y="130.3" width="43.0" height="59.7" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="171.5" y="126.30000000000001" text-anchor="middle" font-size="10" fill="currentColor">0.0398</text><text x="150.0" y="206" text-anchor="middle" font-size="11" fill="currentColor">3 取り</text><rect x="284.0" y="97.9" width="43.0" height="92.1" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="305.5" y="93.9" text-anchor="middle" font-size="10" fill="currentColor">0.0614</text><rect x="330.0" y="155.5" width="43.0" height="34.5" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="351.5" y="151.5" text-anchor="middle" font-size="10" fill="currentColor">0.023</text><text x="330.0" y="206" text-anchor="middle" font-size="11" fill="currentColor">5 取り</text><rect x="464.0" y="113.5" width="43.0" height="76.5" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="485.5" y="109.50000000000001" text-anchor="middle" font-size="10" fill="currentColor">0.051</text><rect x="510.0" y="173.7" width="43.0" height="16.4" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="531.5" y="169.65" text-anchor="middle" font-size="10" fill="currentColor">0.0109</text><text x="510.0" y="206" text-anchor="middle" font-size="11" fill="currentColor">12 取り</text><rect x="450" y="34" width="12" height="10" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="466" y="43" text-anchor="start" font-size="11" fill="currentColor">ペアなし</text><rect x="450" y="50" width="12" height="10" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="466" y="59" text-anchor="start" font-size="11" fill="currentColor">ペアあり</text></svg>

参照値（12 取り × 2000 回の回転の平均）は 0.0953 です。取りが 3 つでペアなし（片側だけ）だと平均は 0.0706（参照値より小さい）、標準偏差は 0.0872（平均に対して 1.24 倍）でした。ペアありにすると標準偏差は 0.0398（0.55 倍）に下がります。5 取りではペアなしの 0.0614（0.71）に対して、ペアありは 0.0230（0.27）。12 取りではペアなしの 0.0510（0.53）に対して、ペアありは 0.0109（0.11）です。

**読み込み回数を揃えて見ると、ペアの価値が分かります。** ペアなしの 12 取り（12 回の読み込み）は標準偏差 0.0510 でしたが、ペアありの 3 取り（6 回）は 0.0398、5 取り（10 回）は 0.0230 とより少ない読み込みで下回りました。壁が片側にあるシーンでは対称の 2 点が、壁の側と壁でない側を必ず両方読むからです。ただし、この結果は一方向に偏ったシーンでの値で、どんなシーンでも同じ割合で減るわけではありません。

## 品質のプリセット {#quality}

`ASSAO.hlsl` の品質は 0〜4 で 4 は参照用（未使用）です。

- **0（Low）。** 3 取り（6 回の読み込み）。辺の処理もハロー抑制もミップもありません。辺の情報は「辺なし」として出力します。ぼかしは辺を見ない 9 画素のものを使います。
- **1（Medium）。** 5 取り（10 回）。深度による辺の検出、ハロー抑制、ディテール AO（`DetailAOStrength`）が入ります。
- **2（High）。** 12 取り（24 回）。ミップが入り法線による辺（隣の法線との内積に 0.5 を足して `saturate` した値を辺の強さにする。内積が −0.5 以下で辺、0.5 以上で辺なし）が足されます。
- **3（Highest、適応）。** 最大 32 取り。基本の取りだけで AO を出し、重要度マップに従って追加します。取りの数の既定値は C++ 側にあり読んでいません。
- **4。** 参照用。未使用です。

ミップの有効化は品質 2、ハロー抑制は品質 1、法線による辺は品質 2 で `SSAO_*_ENABLE_AT_QUALITY_PRESET` の定数で決まります。

## 適応的サンプル {#adaptive}

最高品質ではまず基本の取りだけで AO を出します。その結果から、AO が画素ごとに大きく変わる所を探して、そこにだけ取りを足します。

```hlsl
// ================= ⑧ 適応的サンプル（品質 3）=================

// 重要度マップ: AO が画素ごとに大きく変わる所ほど 1 に近づく。2x2 の AO（4 枚分の 16 値）の最大 − 最小。
// ASSAO.hlsl の PSGenerateImportanceMap と同じ式（pow(saturate(差 * 2), 0.8)）。
float ImportanceFromAo(float4 ao_a, float4 ao_b, float4 ao_c, float4 ao_d) {
  float4 mx4 = max(max(ao_a, ao_b), max(ao_c, ao_d));
  float4 mn4 = min(min(ao_a, ao_b), min(ao_c, ao_d));
  float mx = max(max(mx4.x, mx4.y), max(mx4.z, mx4.w));
  float mn = min(min(mn4.x, mn4.y), min(mn4.z, mn4.w));
  return pow(saturate((mx - mn) * 2.0), 0.8);
}

// 追加で足す取りの数と、最後の数個の重み（なめらかに足し始めるため）。
// base = 全画素が使う取りの数、flexible = 重要度に応じて足せる最大数、limit / avg_importance = 全体の予算の調整。
void AdditionalTaps(float importance, float avg_importance, float limit, int flexible, out int count, out float last_weight) {
  float limiter = saturate(limit / max(avg_importance, 1e-3));   // 重要な画素が多すぎるときは全体を絞る
  float f = flexible * importance * limiter + 0.5;               // 四捨五入のために 0.5 を足す
  count = (int)f;                                                // 追加する取りの数
  last_weight = saturate(frac(f) * (1.0 / 3.0));                 // 簡略: 最後の数個を 3 つに分けて足し込む重み（足した式）
}
```

重要度は 2×2 の AO（4 枚分の 16 値）の最大から最小を引いた差の 2 倍を `saturate` し、0.8 乗したものです（`PSGenerateImportanceMap` の式）。平らな壁では差が小さく隙間や角では差が大きくなります。重要度マップはさらに近傍の 4 点の平均で滑らかにされ（`cSmoothenImportance = 1`）、全画素の重要度の平均が `InterlockedAdd` で数えられます。`importanceLimiter = saturate(AdaptiveSampleCountLimit / 平均の重要度)` で重要な画素が多すぎる場面では全体の取りを絞ります。追加する取りの数は `SSAO_ADAPTIVE_TAP_FLEXIBLE_COUNT × 重要度 × limiter` で四捨五入のために 0.5 を足します。最後の数個は 3 段階（`blendRange = 3`）で重みを上げて足すので、取りの数が切り替わる所で縞が出ません。

`AdditionalTaps` はこの考え方を簡略化したもので、最後の数個の重みの付け方は ASSAO の実装とは違います（足した式）。

## ぼかしと戻し {#blur}

```hlsl
// ================= ⑥ 辺を見るぼかし =================

float2 SmartBlur(float2 uv) {
  float2 c = g_blur_input.SampleLevel(g_point_clamp, uv, 0);
  float2 l = g_blur_input.SampleLevel(g_point_clamp, uv, 0, int2(-1, 0));
  float2 r = g_blur_input.SampleLevel(g_point_clamp, uv, 0, int2(1, 0));
  float2 t = g_blur_input.SampleLevel(g_point_clamp, uv, 0, int2(0, -1));
  float2 b = g_blur_input.SampleLevel(g_point_clamp, uv, 0, int2(0, 1));
  float4 e = UnpackEdges(c.y);                                     // 自分から見た 4 方向の辺
  float sum_w = 0.5, sum = c.x * 0.5;                              // 中心の重み 0.5（ASSAO の通常のぼかし）
  sum += e.x * l.x; sum_w += e.x;                                  // 辺を越える向きは重み 0 に近づく
  sum += e.y * r.x; sum_w += e.y;
  sum += e.z * t.x; sum_w += e.z;
  sum += e.w * b.x; sum_w += e.w;
  return float2(sum / sum_w, c.y);
}

// ================= ⑦ 全解像度に戻す =================

// 全解像度の画素 (px, py) は、4 枚の半解像度のうち、位置の偶奇で決まる 1 枚の画素に対応する。
float ApplyAo(uint2 pix) {
  uint2 half_pix = pix / 2;
  int mx = pix.x % 2, my = pix.y % 2;
  int ic = mx + my * 2;                                            // 自分の枚
  float2 center = g_final.Load(int4(half_pix, ic, 0));
  float4 e = UnpackEdges(center.y);
  float ih = (1 - mx) + my * 2, iv = mx + (1 - my) * 2, id = (1 - mx) + (1 - my) * 2;   // 隣の 3 枚
  float ao_h = g_final.Load(int4(half_pix + int2(mx == 0 ? -1 : 0, 0), (int)ih, 0)).x;
  float ao_v = g_final.Load(int4(half_pix + int2(0, my == 0 ? -1 : 0), (int)iv, 0)).x;
  float ao_d = g_final.Load(int4(half_pix + int2(mx == 0 ? -1 : 0, my == 0 ? -1 : 0), (int)id, 0)).x;
  float4 w;                                                        // 辺があれば隣の寄与を下げる
  w.x = 1.0;
  w.y = (e.x + e.y) * 0.5;
  w.z = (e.z + e.w) * 0.5;
  w.w = (w.y + w.z) * 0.5;
  return dot(float4(center.x, ao_h, ao_v, ao_d), w) / dot(w, float4(1, 1, 1, 1));
}
```

`SmartBlur` は自分と上下左右の 5 点を辺の値を重みにして混ぜます。中心の重みは 0.5（広い版は 0.8）です。辺の値が 0 に近い向き（段差の向こう）は、重みが 0 に近づき混ざりません。C++ で深度が 5 m から 10 m に変わる段差で、AO が左 0.95、右 0.50 の理想的な場合を試しました。

<svg class="fig flow" viewBox="0 0 640 230" role="img" aria-label="段差の前後の AO(左 0.95、右 0.50 が正解)"><defs><marker id="ar" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#94a3b8"/></marker></defs><text x="10" y="18" text-anchor="start" font-size="12" fill="currentColor">段差の前後の AO(左 0.95、右 0.50 が正解)</text><line x1="60" y1="190" x2="600" y2="190" stroke="#94a3b8"/><line x1="60" y1="40" x2="60" y2="190" stroke="#94a3b8"/><text x="54" y="194.0" text-anchor="end" font-size="10" fill="currentColor">0</text><text x="54" y="119.0" text-anchor="end" font-size="10" fill="currentColor">0.5</text><text x="54" y="44.0" text-anchor="end" font-size="10" fill="currentColor">1</text><rect x="68.0" y="47.5" width="21.7" height="142.5" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="78.83333333333333" y="43.5" text-anchor="middle" font-size="10" fill="currentColor">0.95</text><rect x="92.7" y="47.5" width="21.7" height="142.5" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="103.5" y="43.5" text-anchor="middle" font-size="10" fill="currentColor">0.95</text><rect x="117.3" y="47.5" width="21.7" height="142.5" fill="rgba(148,163,184,0.18)" stroke="#94a3b8"/><text x="128.16666666666669" y="43.5" text-anchor="middle" font-size="10" fill="currentColor">0.95</text><text x="105.0" y="206" text-anchor="middle" font-size="11" fill="currentColor">x=3</text><rect x="158.0" y="47.5" width="21.7" height="142.5" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="168.83333333333334" y="43.5" text-anchor="middle" font-size="10" fill="currentColor">0.95</text><rect x="182.7" y="47.5" width="21.7" height="142.5" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="193.5" y="43.5" text-anchor="middle" font-size="10" fill="currentColor">0.95</text><rect x="207.3" y="47.5" width="21.7" height="142.5" fill="rgba(148,163,184,0.18)" stroke="#94a3b8"/><text x="218.16666666666669" y="43.5" text-anchor="middle" font-size="10" fill="currentColor">0.95</text><text x="195.0" y="206" text-anchor="middle" font-size="11" fill="currentColor">x=4</text><rect x="248.0" y="47.5" width="21.7" height="142.5" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="258.8333333333333" y="43.5" text-anchor="middle" font-size="10" fill="currentColor">0.95</text><rect x="272.7" y="70.0" width="21.7" height="120.0" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="283.5" y="66.0" text-anchor="middle" font-size="10" fill="currentColor">0.8</text><rect x="297.3" y="47.5" width="21.7" height="142.5" fill="rgba(148,163,184,0.18)" stroke="#94a3b8"/><text x="308.16666666666663" y="43.5" text-anchor="middle" font-size="10" fill="currentColor">0.95</text><text x="285.0" y="206" text-anchor="middle" font-size="11" fill="currentColor">x=5</text><rect x="338.0" y="115.0" width="21.7" height="75.0" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="348.8333333333333" y="111.0" text-anchor="middle" font-size="10" fill="currentColor">0.5</text><rect x="362.7" y="92.5" width="21.7" height="97.5" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="373.5" y="88.5" text-anchor="middle" font-size="10" fill="currentColor">0.65</text><rect x="387.3" y="115.0" width="21.7" height="75.0" fill="rgba(148,163,184,0.18)" stroke="#94a3b8"/><text x="398.16666666666663" y="111.0" text-anchor="middle" font-size="10" fill="currentColor">0.5</text><text x="375.0" y="206" text-anchor="middle" font-size="11" fill="currentColor">x=6</text><rect x="428.0" y="115.0" width="21.7" height="75.0" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="438.8333333333333" y="111.0" text-anchor="middle" font-size="10" fill="currentColor">0.5</text><rect x="452.7" y="115.0" width="21.7" height="75.0" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="463.5" y="111.0" text-anchor="middle" font-size="10" fill="currentColor">0.5</text><rect x="477.3" y="115.0" width="21.7" height="75.0" fill="rgba(148,163,184,0.18)" stroke="#94a3b8"/><text x="488.16666666666663" y="111.0" text-anchor="middle" font-size="10" fill="currentColor">0.5</text><text x="465.0" y="206" text-anchor="middle" font-size="11" fill="currentColor">x=7</text><rect x="518.0" y="115.0" width="21.7" height="75.0" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="528.8333333333334" y="111.0" text-anchor="middle" font-size="10" fill="currentColor">0.5</text><rect x="542.7" y="115.0" width="21.7" height="75.0" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="553.5" y="111.0" text-anchor="middle" font-size="10" fill="currentColor">0.5</text><rect x="567.3" y="115.0" width="21.7" height="75.0" fill="rgba(148,163,184,0.18)" stroke="#94a3b8"/><text x="578.1666666666667" y="111.0" text-anchor="middle" font-size="10" fill="currentColor">0.5</text><text x="555.0" y="206" text-anchor="middle" font-size="11" fill="currentColor">x=8</text><rect x="450" y="34" width="12" height="10" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="466" y="43" text-anchor="start" font-size="11" fill="currentColor">元</text><rect x="450" y="50" width="12" height="10" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="466" y="59" text-anchor="start" font-size="11" fill="currentColor">ただのぼかし</text><rect x="450" y="66" width="12" height="10" fill="rgba(148,163,184,0.18)" stroke="#94a3b8"/><text x="466" y="75" text-anchor="start" font-size="11" fill="currentColor">辺を見るぼかし</text></svg>

ただのぼかし（3 点の平均）は段差の前後で 0.950、0.950、0.800、0.650、0.500、0.500 と滑らかに繋ぎます。辺を見るぼかしは 0.950、0.950、0.950、0.500、0.500、0.500 で段差のまま残ります。ただのぼかしの 0.800 と 0.650 は、手前の物に奥の暗さが滲んだ（またはその逆の）値です。

`ApplyAo` は 4 枚の半解像度から全解像度に戻します。全解像度の画素は位置の偶奇で決まる 1 枚の画素に対応し、隣の 3 枚からも辺の重みで混ぜます。辺があれば隣の寄与を下げます。辺の両側にある場合は重みが 0 になります。

## パラメーター {#params}

`ASSAO.hlsl` の定数バッファにある主な値は次の通りです。

- **`EffectRadius`。** ビュー空間の半径 [m]。AO を探す範囲です。シーンの縮尺に合わせます。
- **`EffectShadowStrength`。** 全体の強さ（0〜5）。
- **`EffectShadowPow`。** AO のコントラスト。大きいと暗い所が締まります。
- **`EffectShadowClamp`。** 遮蔽量の上限。
- **`EffectFadeOutMul`、`EffectFadeOutAdd`。** 距離で AO を消す範囲（例: 25、100 とソースのコメントにある）。
- **`EffectHorizonAngleThreshold`。** 浅い角度の取りを無視するしきい値（0.05〜0.5）。
- **`DetailAOStrength`。** 周りの 4 画素から足す細かい AO の強さ。
- **`DepthPrecisionOffsetMod`。** 16 ビットの深度の精度不足を避けるために中心を少し手前へ動かす係数。32 ビット浮動小数点なら小さな値で足ります。
- **`InvSharpness`。** ぼかしの辺の鋭さ。

## 他の手法との比較 {#compare}

ASSAO の README はこのコードがもう更新されず[XeGTAO](xegtao.md) に置き換えられたと書いています。XeGTAO は同じ GameTechDev が公開した GTAO の実装で、多くの用途でより良く速いと README にあります。ASSAO の利点は時間蓄積に頼らない（TAA がなくても安定する）ことです。品質の比較は [AO Comparison](comparison.md) を見てください。

## 数字を出した C++ {#experiment}

```cpp
// ASSAO の数字を確かめる。ASSAO.hlsl の式（遮蔽量、辺の検出、パターン）をそのまま C++ に写して使う。
//   [1] 品質ごとの深度の読み込み回数（1080p）
//   [2] 取りの数と AO のノイズ（段差のある高さマップ。真値は 2 万点）
//   [3] 辺を見るぼかしと、ただのぼかしの比較（深度の段差）
//   [4] 辺の 2 ビット量子化
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdio>
#include <random>

constexpr double kPi = 3.14159265358979323846;

struct Tap { double x, y, w; };
// ASSAO の 32 点のパターン（x, y, 重み）。最初の 12 点（高品質まで使う分）。
static const Tap kTaps[12] = {
    {0.78488064, 0.56661671, 1.50}, {0.26022232, -0.29575172, 1.50}, {0.10459357, 0.08372527, 1.11}, {-0.68286800, 0.04963045, 1.09},
    {-0.13570161, -0.64190155, 1.25}, {-0.26193795, -0.08205118, 0.67}, {-0.61177456, 0.66664219, 0.71}, {0.43675563, 0.25119025, 0.61},
    {0.07884444, 0.86618668, 0.64}, {-0.12790935, -0.29869005, 0.60}, {-0.04031125, 0.02413622, 0.60}, {0.16201244, -0.52851415, 0.79}};

// ASSAO.hlsl の CalculatePixelObscurance。
static double Obscurance(double nx, double ny, double nz, double dx, double dy, double dz, double radius, double horizon) {
  double len_sq = dx * dx + dy * dy + dz * dz;
  double n_dot_d = (nx * dx + ny * dy + nz * dz) / std::sqrt(len_sq);
  double falloff = std::max(0.0, len_sq * (-1.0 / (radius * radius)) + 1.0);
  return std::max(0.0, n_dot_d - horizon) * falloff;
}

// 高さマップ: 真上から見た床 (y = 0) に、x >= wall_x で高さ H の段（壁）がある。画素の大きさは pix [m]。
static double Height(double x, double wall_x, double H) { return x >= wall_x ? H : 0.0; }

// 点 (x0, 0, 0)（床の上）の AO を、半径 R の円盤内の n 個の取り（ペアは数えない）で求める。
// 取りを回す角度 angle で、同じ位置でも違う結果になる。
static double Ao(double x0, double wall_x, double H, double R, double pix, int taps, double angle, bool pairs) {
  double sum = 0, wsum = 0, radius_px = 0.85 * R / pix;
  double c = std::cos(angle), s = std::sin(angle);
  for (int i = 0; i < taps; ++i) {
    double ox = (c * kTaps[i].x - s * kTaps[i].y) * radius_px, oy = (s * kTaps[i].x + c * kTaps[i].y) * radius_px;
    for (int k = 0; k < (pairs ? 2 : 1); ++k) {
      double px = std::round(k == 0 ? ox : -ox), py = std::round(k == 0 ? oy : -oy);   // 画素の中心へ丸める
      double hx = x0 + px * pix, hz = py * pix, hy = Height(hx, wall_x, H);
      sum += Obscurance(0, 1, 0, hx - x0, hy, hz, R, 0.05) * kTaps[i].w;
      wsum += kTaps[i].w;
    }
  }
  return sum / wsum;
}

// ASSAO.hlsl の CalculateEdges。
static std::array<double, 4> Edges(double c, double l, double r, double t, double b) {
  double e[4] = {l - c, r - c, t - c, b - c};
  double sa[4] = {e[0] + e[1], e[1] + e[0], e[2] + e[3], e[3] + e[2]};   // 反対側との和
  std::array<double, 4> out{};
  for (int i = 0; i < 4; ++i) {
    double v = std::min(std::fabs(e[i]), std::fabs(sa[i]));
    out[i] = std::clamp(1.3 - v / (c * 0.040), 0.0, 1.0);
  }
  return out;
}

int main() {
  // ---- [1] 読み込み回数 ----
  std::printf("[1] depth reads per pixel and per 1080p frame (taps are pairs: 2 reads each)\n");
  const double px = 1920.0 * 1080;
  struct Q { const char* name; int taps; };
  for (Q q : {Q{"Low (0)", 3}, Q{"Medium (1)", 5}, Q{"High (2)", 12}, Q{"Adaptive max (3, 32 taps)", 32}}) {
    std::printf("%-26s taps=%2d reads/pixel=%2d  frame=%.1f M\n", q.name, q.taps, q.taps * 2, px * q.taps * 2 / 1e6);
  }
  std::printf("deinterleaved depth: 4 slices of %d x %d = %.0f texels each\n", 1920 / 2, 1080 / 2, 1920.0 / 2 * 1080 / 2);

  // ---- [2] ノイズ ----
  std::printf("\n[2] AO noise vs taps: floor point 0.15 m from a 0.5 m high wall, R = 1 m, pixel = 3 cm; 4000 random rotations\n");
  const double R = 1.0, pix = 0.03, wall_x = 0.15, H = 0.5;
  std::mt19937 rng(3);
  std::uniform_real_distribution<double> uni(0, 2 * kPi);
  double truth = 0;                                                // 参照: 12 点を 2000 通りの角度で平均（誤差は十分小さい）
  for (int i = 0; i < 2000; ++i) truth += Ao(0, wall_x, H, R, pix, 12, uni(rng), true);
  truth /= 2000;
  std::printf("reference (12 taps x 2000 rotations) = %.4f\n", truth);
  std::printf("taps  pairs   mean     std      std/mean\n");
  for (int taps : {3, 5, 12}) {
    for (bool pairs : {false, true}) {
      double sum = 0, sq = 0;
      const int T = 4000;
      for (int t = 0; t < T; ++t) { double v = Ao(0, wall_x, H, R, pix, taps, uni(rng), pairs); sum += v; sq += v * v; }
      double m = sum / T, sd = std::sqrt(sq / T - m * m);
      std::printf("%3d   %-5s  %.4f   %.4f   %.2f\n", taps, pairs ? "yes" : "no", m, sd, sd / m);
    }
  }

  // ---- [3] 辺を見るぼかし ----
  std::printf("\n[3] blur across a depth step (5 m | 10 m): AO left = 0.95, right = 0.50 (exact)\n");
  const int N = 12;
  double z[N], ao[N];
  for (int i = 0; i < N; ++i) { z[i] = i < 6 ? 5.0 : 10.0; ao[i] = i < 6 ? 0.95 : 0.50; }
  std::printf("x:        ");
  for (int i = 3; i < 9; ++i) std::printf("%7d ", i);
  std::printf("\nraw AO:   ");
  for (int i = 3; i < 9; ++i) std::printf("%7.3f ", ao[i]);
  std::printf("\nnaive:    ");
  for (int i = 3; i < 9; ++i) std::printf("%7.3f ", (ao[i - 1] + ao[i] + ao[i + 1]) / 3.0);
  std::printf("\nedge-aware:");
  for (int i = 3; i < 9; ++i) {
    auto e = Edges(z[i], z[i - 1], z[i + 1], z[i], z[i]);          // 水平方向だけ（上下は同じ深度）
    double sum = ao[i] * 0.5, sw = 0.5;
    sum += e[0] * ao[i - 1]; sw += e[0];
    sum += e[1] * ao[i + 1]; sw += e[1];
    std::printf("%7.3f ", sum / sw);
  }
  std::printf("\nedges at x=5 (L,R): ");
  { auto e = Edges(z[5], z[4], z[6], z[5], z[5]); std::printf("%.3f %.3f\n", e[0], e[1]); }
  { auto e = Edges(z[6], z[5], z[7], z[6], z[6]); std::printf("edges at x=6 (L,R): %.3f %.3f\n", e[0], e[1]); }

  // ---- [4] 2 ビット量子化 ----
  std::printf("\n[4] 2-bit edge quantization: value -> round(v * 3.05) / 3\n");
  for (double v : {0.0, 0.1, 0.25, 0.4, 0.5, 0.6, 0.75, 0.9, 1.0})
    std::printf("v=%.2f -> %.3f\n", v, std::round(std::clamp(v, 0.0, 1.0) * 3.05) / 3.0);
  return 0;
}
```

```text title="実行結果"
[1] depth reads per pixel and per 1080p frame (taps are pairs: 2 reads each)
Low (0)                    taps= 3 reads/pixel= 6  frame=12.4 M
Medium (1)                 taps= 5 reads/pixel=10  frame=20.7 M
High (2)                   taps=12 reads/pixel=24  frame=49.8 M
Adaptive max (3, 32 taps)  taps=32 reads/pixel=64  frame=132.7 M
deinterleaved depth: 4 slices of 960 x 540 = 518400 texels each
```

```text title="実行結果（続き）"
[2] AO noise vs taps: floor point 0.15 m from a 0.5 m high wall, R = 1 m, pixel = 3 cm; 4000 random rotations
reference (12 taps x 2000 rotations) = 0.0953
taps  pairs   mean     std      std/mean
  3   no     0.0706   0.0872   1.24
  3   yes    0.0720   0.0398   0.55
  5   no     0.0860   0.0614   0.71
  5   yes    0.0861   0.0230   0.27
 12   no     0.0965   0.0510   0.53
 12   yes    0.0955   0.0109   0.11
```

```text title="実行結果（続き）"
[3] blur across a depth step (5 m | 10 m): AO left = 0.95, right = 0.50 (exact)
x:              3       4       5       6       7       8 
raw AO:     0.950   0.950   0.950   0.500   0.500   0.500 
naive:      0.950   0.950   0.800   0.650   0.500   0.500 
edge-aware:  0.950   0.950   0.950   0.500   0.500   0.500 
edges at x=5 (L,R): 1.000 0.000
edges at x=6 (L,R): 0.000 1.000
```

```text title="実行結果（続き）"
[4] 2-bit edge quantization: value -> round(v * 3.05) / 3
v=0.00 -> 0.000
v=0.10 -> 0.000
v=0.25 -> 0.333
v=0.40 -> 0.333
```

## よくあるミス {#mistakes}

??? failure "デインターリーブの格子模様が見える"
    ぼかしが足りないまたは戻しの重みが合っていない。ぼかしを 1 回増やすか品質を上げる。

??? failure "平らな床が、浅い角度で縞状に暗くなる"
    `EffectHorizonAngleThreshold` が小さすぎる。0.05 から 0.5 の範囲で上げる。

??? failure "物体の手前の輪郭に暗い縁（ハロー）が出る"
    ハロー抑制がない品質 0 を使っている、または手前の取りの重みを下げていない。品質 1 以上にする。

??? failure "段差をまたいで、手前の物に奥の暗さが滲む"
    ぼかしが辺を見ていない。辺を見るぼかし（品質 1 以上）を使う。

??? failure "法線を渡さず面の向きがずれる"
    法線のテクスチャが必要な設定で、深度から作った法線だとポリゴンの境目が出る。法線バッファがあれば渡す。

## これだけ覚える {#summary}

!!! abstract "まとめ"
    - [x] ASSAO は深度を 4 枚の半解像度に分けて AO を計算し、辺を見るぼかしで戻す。
    - [x] 取りは対称の 2 点セット。同じ読み込み回数でもノイズが大きく減る（偏ったシーンの例）。
    - [x] 遮蔽量は `max(0, N·D̂ − しきい値) × falloff`。しきい値が平らな面の誤った暗さを抑える。
    - [x] 辺（深度の段差）は 2 ビットで詰めぼかしと戻しの重みに使う。
    - [x] 最高品質は AO の変化が大きい所にだけ取りを足す。

## 参考 {#references}

- Filip Strugar (Intel), "ASSAO.hlsl", GameTechDev/ASSAO, 2016. MIT ライセンス。全 1184 行を読んだ。C++ 側は未読。
- GameTechDev, "ASSAO" README. このコードが XeGTAO に置き換えられたという記述を参照した。
- AMD, "FidelityFX CACAO". 読んでいない。
- Morgan McGuire, Michael Mara, David Luebke, "Scalable Ambient Obscurance", HPG 2012. 読んでいない。ミップの選び方の出典として ASSAO.hlsl のコメントが挙げている。
- このページの HLSL は ASSAO.hlsl の要点を書き直したもの。C++ の実験の取りのパターン、遮蔽量の式、辺の式は ASSAO.hlsl から写したもの。シーン（段差のある高さマップ）はこのページが決めた。

## 関連ページ {#related}

- [GTAO](gtao.md)
- [XeGTAO](xegtao.md)
- [SSAO（半球）](ssao-hemisphere.md)
- [AO Filtering](filtering/index.md)
- [AO Comparison](comparison.md)
