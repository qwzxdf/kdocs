---
title: 確率的 SSR
tags:
  - 描画
---

# 確率的 SSR

[SSR の基礎](ssr-basics.md)と [Hi-Z SSR](ssr-hiz.md)は、**反射方向 R の、1 本のレイ**を追いました。これは**完全な鏡**の反射です。**粗い面**の反射は、**R の周りのさまざまな方向の景色を、BRDF の重みで平均**したものでした。**確率的 SSR**（Stochastic SSR）は、**BRDF の分布に従って、画素ごとにランダムな方向のレイ**を 1 本だけ飛ばし、**近くの画素のレイの結果を再利用し、時間方向にも平均**して、**ぼけた反射を物理的に正しく**得ます。2015 年に Frostbite の Stachowiak が発表した方式が、現在の SSR の標準的な作り方です。

!!! tip "ポイント"
    - 粗い反射 ＝ <strong>BRDF（GGX）の山の中の様々な方向の景色の平均</strong>。<strong>モンテカルロ法</strong>で近似する。
    - <strong>重要度サンプリング</strong>：<strong>GGX の分布に従って</strong>方向を選ぶ（<strong>可視法線サンプリング、VNDF</strong>）。
    - <strong>1 画素 1 本</strong>（半分の解像度でも可）のレイ。<strong>ノイズだらけ</strong>。
    - <strong>空間再利用</strong>：<strong>近くの画素のレイの当たり点</strong>を、自分の反射の<strong>サンプルとして再利用</strong>（重みで補正）。
    - <strong>時間蓄積</strong>と<strong>バイラテラル フィルタ</strong>で、ノイズを消す。
    - 結果は<strong>BRDF の積分（スケール・バイアス）を掛けて</strong>合成する。

## 発想：粗い反射をモンテカルロ法で

鏡面の出射光は、次の積分でした（[反射](index.md)）。

<div class="formula">L_o = ∫ f_spec(ω_i, ω_o) · L_i(ω_i) · (n·ω_i) dω_i</div>

**ω_i を、BRDF の山の形に従ってランダムに選ぶ**（**重要度サンプリング**）と、**サンプルの平均**が積分の近似になります。**1 画素あたり 1 本**のレイを、**画素ごとに異なる方向**に飛ばして、**近くの画素と平均**すれば、**ぼけた反射**が出ます。

<svg class="fig illust" viewBox="0 0 780 280" role="img" aria-label="粗さと確率的レイ">
<text x="20" y="24" class="fig-title">粗さに応じて、反射方向の周りの「山」から、ランダムな方向を選ぶ</text>
<line x1="60" y1="220" x2="360" y2="220" stroke="currentColor" stroke-width="4"/>
<circle cx="210" cy="220" r="6" fill="currentColor"/>
<line x1="210" y1="220" x2="210" y2="80" stroke="#2ea043" stroke-width="2" stroke-dasharray="4 3"/><text x="218" y="92" style="font-size:12px;fill:#2ea043">法線 n</text>
<line x1="210" y1="220" x2="320" y2="100" stroke="#e5484d" stroke-width="3"/><text x="324" y="96" style="font-size:12px;fill:#e5484d;font-weight:700">反射方向 R</text>
<g stroke="#4c8bf5" stroke-width="1.8"><line x1="210" y1="220" x2="300" y2="86"/><line x1="210" y1="220" x2="340" y2="115"/><line x1="210" y1="220" x2="335" y2="135"/><line x1="210" y1="220" x2="310" y2="112"/><line x1="210" y1="220" x2="290" y2="104"/></g>
<text x="60" y="250" style="font-size:12px">粗いほど、R の周りに、レイが広く散らばる（青）</text>
<rect x="430" y="60" width="330" height="170" rx="10" fill="rgba(150,150,150,0.12)" stroke="currentColor"/>
<text x="446" y="88" style="font-weight:700">粗さ（ラフネス）</text>
<text x="446" y="114" style="font-size:12px">小さい：R の近くだけ（くっきり反射）</text>
<text x="446" y="136" style="font-size:12px">大きい：広い範囲（ぼけた反射）</text>
<text x="446" y="170" style="font-weight:700">サンプルの選び方</text>
<text x="446" y="194" style="font-size:12px">GGX の分布に従い、「法線 h」をランダムに選ぶ</text>
<text x="446" y="214" style="font-size:12px">→ R = reflect(−V, h)</text>
</svg>

## GGX 分布と重要度サンプリング

**GGX**（Trowbridge-Reitz）は、<strong>微小な面の向き（ハーフベクトル h）の分布 D(h)</strong> を表す、**標準的な式**です。

<div class="formula">D(h) = α² / ( π · ( (n·h)² (α² − 1) + 1 )² )　、　α = roughness²</div>

| 記号 | 意味 |
| --- | --- |
| **α** | 粗さのパラメータ（`roughness²` が一般的） |
| **n·h** | 法線とハーフベクトルのコサイン。**1 に近いほど D が大きい**（山の頂上） |

### サンプルの方向を作る

**ランダムな h** を、**D(h) に比例する確率**で選べば、**効率のよい（分散の小さい）サンプル**になります。**反射方向 L は `reflect(−V, h)`** です。

| 手順 | 内容 |
| --- | --- |
| **① h をサンプル** | **GGX の分布**（または**可視法線**の分布）から、ランダムに h を選ぶ |
| **② 反射方向を作る** | `L = reflect(−V, h)` |
| **③ 地平線の下は捨てる** | `L·N < 0`（面の裏側）なら、**無効**（再サンプル、または寄与 0） |

### 可視法線サンプリング（VNDF）

素朴な GGX サンプリングは、**視線から見えない向き**（裏向きの微小面）も選んで**無駄**（無効なレイ）が多くなります。<strong>可視法線の分布（VNDF）</strong>は、**視線 V から見える向きだけ**を、確率的に選ぶので**無駄が少なく、ノイズが小さい**です（Heitz, 2018）。

```hlsl
float3 SampleGGXVNDF(float3 view_ts, float alpha, float2 u) {
  float3 vh = normalize(float3(alpha * view_ts.x, alpha * view_ts.y, view_ts.z));

  float len_sq = vh.x * vh.x + vh.y * vh.y;
  float3 t1 = len_sq > 0.0 ? float3(-vh.y, vh.x, 0.0) * rsqrt(len_sq) : float3(1, 0, 0);
  float3 t2 = cross(vh, t1);

  float r = sqrt(u.x);
  float phi = 6.2831853 * u.y;
  float p1 = r * cos(phi);
  float p2 = r * sin(phi);
  float s = 0.5 * (1.0 + vh.z);
  p2 = (1.0 - s) * sqrt(1.0 - p1 * p1) + s * p2;

  float3 nh = p1 * t1 + p2 * t2 + sqrt(max(0.0, 1.0 - p1 * p1 - p2 * p2)) * vh;
  return normalize(float3(alpha * nh.x, alpha * nh.y, max(0.0, nh.z)));
}
```

| 点 | 説明 |
| --- | --- |
| **`view_ts`** | **接空間**での視線ベクトル（法線を z 軸とする座標系） |
| **`u`** | 2 つの一様乱数（画素・フレームごとに変える） |
| **戻り値** | 接空間での**ハーフベクトル h** |
| **接空間 → ワールド** | TBN（法線から作る）で、ワールドの h に |

**確率密度**（レイの方向 L に対する）は、次のとおりです（重み付けに使う）。

<div class="formula">pdf(L) = D_V(h) / (4 · (V·h))　、　D_V(h) = G1(V) · max(0, V·h) · D(h) / (n·V)</div>

| 記号 | 意味 |
| --- | --- |
| <strong>G1(V)</strong> | 視線方向の**遮蔽関数**（Smith の G1）。見える割合 |
| <strong>4 (V·h)</strong> | `h` の分布から、**反射方向 L の分布**に変換する係数（ヤコビアン） |

## 全体の流れ

| パス | 内容 |
| --- | --- |
| **① レイ生成** | **1 画素 1 本**（半分の解像度のことも）。**粗さに応じた GGX VNDF** で、方向を選ぶ |
| **② Hi-Z トレース** | レイを進めて、<strong>当たり点（位置・距離）</strong>を求める（[Hi-Z SSR](ssr-hiz.md)） |
| **③ 色の取得** | 当たり点の色（前フレームの HDR、動きベクトルで再投影） |
| **④ 空間リゾルブ** | **近隣画素のレイ**を再利用して、各画素の反射を再構成（下記） |
| **⑤ 時間蓄積** | 過去フレームと混ぜる |
| **⑥ バイラテラル フィルタ** | 粗さ・深度・法線を考慮して、ノイズを消す |
| **⑦ 合成** | <strong>BRDF の積分（スケール・バイアス）</strong>を掛け、**フォールバックと混ぜる** |

## 空間リゾルブ：近隣のレイの再利用

**1 画素 1 本**のレイでは、ノイズが大きすぎます。**近隣の画素（たとえば 4〜9 個）が、それぞれ飛ばしたレイの当たり点**を、**自分のサンプルとして再利用**します。

**近隣の画素 j のレイが、当たり点 H_j を持つ**とします。**自分（画素 i）から見た H_j への方向 L**は、`L = normalize(H_j − P_i)` です。**この L は自分の BRDF から見て、どれくらいありえる方向か**で、サンプルを**重み付け**します。

<div class="formula">L_o(i) ≈ Σ_j w_j · Color(H_j) / Σ_j w_j　、　w_j = f_spec,i(L_j) · (n_i·L_j) / pdf_j(L_j)</div>

| 項 | 意味 |
| --- | --- |
| <strong>f_spec,i(L_j)</strong> | **自分の BRDF**で方向 L_j の値 |
| <strong>pdf_j(L_j)</strong> | **そのレイを生成した画素 j の確率密度**（j の法線・粗さ・視線から求めた、その方向に飛ぶ確率） |
| **w_j** | <strong>「自分にとっての価値」÷「j がその方向を選ぶ確率」</strong>。**重要度の補正** |

つまり、**他の画素が選んだレイを、自分にとって妥当な方向として、「借りて」きて**、**確率の違いを重みで補正**しています。**1 画素 1 本のレイが、実質 4〜9 本分**になり、**ノイズが大きく減ります**。

```hlsl
float4 ResolveSpatial(int2 pixel) {
  float3 p = ViewPosition(pixel);
  float3 n = ViewNormal(pixel);
  float3 v = -normalize(p);
  float roughness = Roughness(pixel);

  float4 sum = 0;
  float weight_sum = 0;
  for (int i = 0; i < kNeighborCount; ++i) {
    int2 neighbor = pixel + kOffsets[i];
    float4 ray = ray_hit_tex.Load(int3(neighbor, 0));
    float3 hit_vs = ray.xyz;
    float neighbor_pdf = ray.w;

    float3 l = normalize(hit_vs - p);
    float weight = SpecularBRDF(n, v, l, roughness) * saturate(dot(n, l)) / max(neighbor_pdf, 1e-5);

    sum += float4(HitColor(neighbor), 1.0) * weight;
    weight_sum += weight;
  }
  return sum / max(weight_sum, 1e-5);
}
```

| 点 | 説明 |
| --- | --- |
| **`kOffsets`** | 近隣のオフセット（4〜9 個。**画素ごとにパターンを回す**） |
| **当たり点とその pdf を保存** | レイ生成パスで**当たり位置と確率密度**を書き出しておく |
| **`HitColor`** | 近隣の当たり点の色（前フレームから取得済み） |
| **有効性** | **深度・法線が近くない**近隣は除外（別の面） |
| **サンプルの偏り** | 大きな近隣の範囲（ぼけすぎ）を避けるため、**範囲は小さく** |

## 時間蓄積

**フレームごとにランダムな方向**を変えて、**過去のフレームと平均**します。

| 要素 | 内容 |
| --- | --- |
| **再投影** | **今の画素の位置**を前フレームの画面へ。**動きベクトル** |
| **反射の再投影** | **鏡面反射**は**映っている物の動き**に従う。**反射した当たり点**（仮想的な位置）を使って、再投影する |
| **履歴の検証** | 深度・法線・**粗さ**が近いか |
| **混合係数** | `α = 0.05〜0.2`（粗い面ほど、強く蓄積できる） |
| **近傍クランプ** | **周囲の画素の範囲**に履歴を制限して、ゴーストを防ぐ |

**粗い面**は**反射がぼけている**ので**少々のずれは目立たず**、**強く蓄積**できます。**鏡面に近い面**は、**くっきり**しているので**ずれ（ゴースト）が目立ち**、**慎重に**扱います。

### 反射の動き（仮想的な位置）

反射像は**表面の動きと映っている物の動きとカメラの動き**で**複雑に動き**ます。**表面の動きだけ**で再投影すると、**反射像が引きずられます**。

| 再投影の方法 | 結果 |
| --- | --- |
| **表面の動きベクトル** | 粗い反射には十分。鏡面に近いと**ゴースト** |
| **当たり点の動き**（レイの先の動き） | 鏡面反射では**映った物体の動き**に追従 |
| **仮想的な位置**（反射像が鏡の向こうに見える位置） | **鏡面反射に最適**。複雑 |

## フィルタとノイズ除去

リゾルブと時間蓄積のあとも、**ノイズが残る**ことがあります。**空間フィルタ**（バイラテラル）で、**さらに滑らか**にします。

| 工夫 | 内容 |
| --- | --- |
| **粗さに比例した、フィルタの大きさ** | **粗いほど、広くぼかす**（反射がもともとぼけているため） |
| **深度・法線の重み** | 境界をまたがない |
| **ホタル（極端に明るい点）の除去** | **色の上限**（輝度クランプ）、**外れ値の除去** |
| **解像度を下げて計算** | 粗い反射は半分・4 分の 1 でも十分 |

## BRDF の積分を掛ける

確率的 SSR の出力は、<strong>「その方向の景色の（重み付き）平均」</strong>です。**反射の最終的な明るさ**には、**BRDF の積分**（Split-Sum の第 2 項）を掛けます（[プローブ](probes.md)）。

```hlsl
float2 brdf = brdf_lut.Sample(linear_sampler, float2(n_dot_v, roughness)).rg;
float3 F0 = lerp(0.04, albedo, metallic);
float3 specular = ssr_color * (F0 * brdf.x + brdf.y);
```

**プローブ**で使うのと**同じ式**なので、**SSR とプローブを同じ調子で混ぜられます**（[フォールバック](ssr-fallback.md)）。

## コストと品質の調整

| 設定 | 品質への影響 | コスト |
| --- | --- | --- |
| **レイの解像度**（フル・半分・4 分の 1） | 下げるとにじむ | 大きく減る |
| **近隣の数**（リゾルブ） | 増やすとノイズが減る・ぼけが増える | 少し増える |
| **時間蓄積の強さ** | 強いと滑らかだが遅れる | ほぼ無し |
| **最大レイ長・Hi-Z 反復数** | 長いと遠くの映り込み | 増える |
| **粗さの上限** | これ以上の粗さは、SSR をやめる（プローブへ） | 大きく減る |

## 長所と短所

| 長所 | 短所 |
| --- | --- |
| **粗さに応じた、物理的に正しいぼけ** | **ノイズ**が大きく、**フィルタが必須** |
| **1 画素 1 本のレイで済む** | **ゴースト・遅れ**（時間蓄積） |
| **粗さの全域を 1 つの仕組みで**扱える | **実装が複雑**（レイ・リゾルブ・時間・フィルタ・合成） |
| **レイトレ反射とほぼ同じ構造**（デノイズなど） | 画面外・裏側が映らない限界は同じ |

## よくあるミス

??? failure "GGX のサンプリングで、裏向き（地平線の下）のレイを使って、暗い縞・ノイズ"
    `L·N < 0` を**無効**にします。**VNDF** で無駄を減らします。

??? failure "近隣のレイを再利用するとき、pdf で割らず、偏りが出る"
    **レイを生成した画素の pdf** で、重みを補正します。

??? failure "鏡面に近い面に、強い時間蓄積をして、ゴーストが出る"
    **粗さに応じて**蓄積の強さを変える。**反射の動き**で再投影する。

??? failure "ホタル（極端に明るい点）が、ノイズ除去後も残る"
    **輝度クランプ**、**外れ値の除去**を入れます。

??? failure "BRDF の積分（スケール・バイアス）を掛け忘れて、反射が明るすぎる・暗すぎる"
    Split-Sum の第 2 項を、掛けます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 確率的 SSR ＝ <strong>粗さに合わせた GGX（VNDF）で、画素ごとにランダムなレイを 1 本飛ばす</strong>
    - [x] <strong>近隣の画素のレイを再利用</strong>（<strong>重み ＝ BRDF ÷ そのレイの pdf</strong>）して、ノイズを減らす
    - [x] <strong>時間蓄積</strong>（粗いほど強く）と<strong>バイラテラル</strong>でさらに滑らかに
    - [x] <strong>BRDF の積分（スケール・バイアス）</strong>を掛けて、<strong>プローブと同じ調子</strong>で合成
    - [x] レイトレ反射と、<strong>ほぼ同じ構造</strong>（レイ生成 → 当たり → デノイズ）

## 参考

- Stachowiak, Uludag, "Stochastic Screen-Space Reflections"（SIGGRAPH 2015 Advances in Real-Time Rendering、Frostbite）
- Heitz, "Sampling the GGX Distribution of Visible Normals"（Journal of Computer Graphics Techniques, 2018）

## 関連ページ

- [反射](index.md)
- [Hi-Z SSR](ssr-hiz.md)
- [SSR のフォールバックと合成](ssr-fallback.md)
- [レイトレース反射](rt-reflections.md)
- [PBR](../../3d/pbr.md)
- [AO のフィルタ](../ao/filtering.md)
