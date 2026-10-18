---
title: Pre-Integrated Skin Shading
tags:
  - 描画
---

# Pre-Integrated Skin Shading

**事前積分**（pre-integrated）による肌のシェーディングは、SSS の効果を、**ライティングの段階で、LUT を 1 回引くだけ**で近似する方法です。画面空間のぼかしが不要で、追加のレンダー ターゲットも要りません。モバイルや、画面に多くのキャラクターが映るゲームで使われます。Penner と Borshukov が "Pre-Integrated Skin Shading"（GPU Pro 2、2011）で提案しました。このページでは、「なぜ法線の向きと曲率だけで SSS が近似できるのか」から順に説明します。

!!! tip "ポイント"
    - SSS は、**光が当たる側から影の側へ、じんわり染み出す**現象。**N·L の変化が、緩やかになる**。
    - LUT の入力は<strong>N·L（光の向き）</strong>と<strong>曲率（表面の曲がり具合）</strong>。**出力は RGB の拡散光**。
    - **曲率が大きい（細い）部位ほど、光が回り込んで、影側が明るくなる**。
    - **法線マップの法線を、色ごとにぼかす**（赤は大きく、青は小さく）と、**肌の柔らかさ**が増す。
    - **安い**が、**影の縁の赤みや、薄い部位の透けは、別に処理**。

## 考え方

肌に光が当たると、光が当たった側で入った光が、内部で広がって、**影の側にも染み出します**。その結果、明暗の境（N·L が 0 の付近）が、通常のランバート反射のようにくっきり切れず、なだらかに暗くなります。さらに、このなだらかさは、**赤の方が大きい**ので、境が赤く染まります。

ここで注目するのは、この広がりが、**表面がどれだけ曲がっているか**によって変わることです。平らな面（曲率 0）では、光が当たる範囲も影になる範囲も広いので、広がった光が影の側へ染み出す量は、少なくなります（染み出す先も一様に当たっている）。逆に、**細く丸い面**（指や耳、鼻の頭のように曲率が大きい面）では、光が当たっている領域のすぐ隣が影の領域なので、光が影へ染み出す効果が大きく見えます。

つまり、SSS による影の側の明るさは、**N·L**（光に対する向き）と**曲率**（表面の曲がり具合）の 2 つで、おおむね決まります。この 2 つを入力にして、結果の拡散光を返す表（LUT）を、あらかじめ作っておけば、実行時は引くだけで済みます。

## LUT の作り方

LUT は、次のように計算します。曲率は、半径 r の球で表します（曲率 = 1/r）。球の表面の点 P を考え、光の方向と法線のなす角 θ（N·L = cos θ）を決めます。点 P での拡散光は、**球の全表面に当たった光が、拡散プロファイル R_d で P に広がってきた量の合計**です。

球上の各点 Q は、光に対する角度が違い、その点での直接光は、`max(0, cos(θ + x))`（x は P から Q までの角度）に比例します。P と Q の距離は `2r sin(x/2)` です。したがって、P での拡散光は、次の積分で表されます。

<div class="formula">D(θ, r) = ∫_{−π}^{π} max(0, cos(θ + x)) · R_d(2r sin(x/2)) dx　／　∫_{−π}^{π} R_d(2r sin(x/2)) dx</div>

分母は正規化で、プロファイルの合計を 1 にします。この積分を、**θ（または N·L）と、1/r の組み合わせごとに**、RGB の各チャンネルについて計算し、2 次元のテクスチャに書き込みます。横軸が N·L（−1〜1 を 0〜1 に変換）、縦軸が曲率です。各テクセルに、RGB の拡散光の値が入ります。この計算はオフラインで行い、1 つの LUT をすべての肌に共通で使います（プロファイルは肌の種類で共通とします）。

## 曲率の求め方

実行時に必要な「曲率」は、画素ごとに次のように求めます。**法線の変化量**と、**位置の変化量**の比です。

<div class="formula">曲率 = ‖Δn‖ / ‖Δp‖　（隣の画素との差を使う）</div>

法線が速く変わる場所（鼻の頭）は曲率が大きく、ほぼ変わらない場所（頬の平らな部分）は曲率が小さくなります。ピクセル シェーダーで、`ddx` と `ddy` を使って求めます。

```hlsl
float curvature = saturate(length(fwidth(normal)) / length(fwidth(world_pos)) * kCurvatureScale);
```

画素単位の計算は、ノイズが出やすいので、頂点ごとに曲率を計算して頂点属性に持たせたり、事前に曲率のテクスチャを焼いておいたりする方法もあります。

## 実行時の計算

LUT を引く部分は、次のようになります。

```hlsl
float3 SkinDiffuse(float3 n, float3 l, float curvature, float3 albedo, float3 light_color) {
  float n_dot_l = dot(n, l);
  float2 lut_uv = float2(n_dot_l * 0.5 + 0.5, curvature);
  float3 diffuse = skin_lut.SampleLevel(linear_clamp, lut_uv, 0).rgb;
  return diffuse * albedo * light_color;
}
```

通常のランバートでは `saturate(n_dot_l)` を使いますが、ここでは負の N·L（影の側）まで LUT に含めます。LUT の値は、N·L が 0 を下回っても 0 にならず、赤の成分がゆっくり減衰します。これが、影の縁の赤みを作ります。

## 法線の扱い：色ごとにぼかす

さらに、事前積分の論文には、**法線の扱い**の工夫があります。肌の表面の細かい凹凸（毛穴、小じわ）は、法線マップで表されます。ところが、SSS で光が広がると、**細かい凹凸の陰影は、赤の光では弱く、青の光では強く**見えます（赤は広がるので、細部が平均されてなめらかになります）。

そこで、**法線を色ごとに別々にぼかします**。具体的には、ジオメトリの法線（なめらか）と、法線マップの法線（細かい）の 2 つを用意します。次に、チャンネルごとに、2 つの法線を混ぜる割合を変えます。青は、法線マップの法線を多めに使い（細部が強く出る）、赤は、ジオメトリの法線を多めに使います（細部が弱く出る）。そして、各チャンネルで別々の法線を使って、LUT を引きます。

```hlsl
float3 n_geom = normalize(input.normal);
float3 n_map = ApplyNormalMap(n_geom, normal_map_sample);
float3 n_r = normalize(lerp(n_geom, n_map, 0.3));
float3 n_g = normalize(lerp(n_geom, n_map, 0.7));
float3 n_b = n_map;
float3 diffuse;
diffuse.r = skin_lut.SampleLevel(linear_clamp, float2(dot(n_r, l) * 0.5 + 0.5, curvature), 0).r;
diffuse.g = skin_lut.SampleLevel(linear_clamp, float2(dot(n_g, l) * 0.5 + 0.5, curvature), 0).g;
diffuse.b = skin_lut.SampleLevel(linear_clamp, float2(dot(n_b, l) * 0.5 + 0.5, curvature), 0).b;
```

この小さな工夫で、毛穴の凹凸の陰影が、青ではくっきり、赤ではぼんやり見える、現実の肌の柔らかさに近づきます。

## 長所と限界

事前積分の長所は、軽いことです。画素ごとに LUT を引くだけで、別のパスも追加のレンダー ターゲットも不要です。SSS のぼかしにある、輪郭をまたぐにじみの問題もありません。ライトごとに、独立して計算できるので、複数のライトにも素直に使えます。

限界もあります。まず、LUT が引くのは、**N·L の変化のなだらかさ**だけです。影（シャドウ マップ）で隠れた領域の周りに染み出す効果や、**影の縁の赤み**は表せません。これは、影がライティングの前に決まっていて、周りの画素の情報を参照しないためです。次に、**薄い部位の透け**（耳に光を当てると赤く透ける）は、別の処理が必要です（[Thin Translucency](thin-translucency.md)）。そして、曲率の推定が粗いと、顔の表面でムラが出ることがあります。

そのため、現代のゲームでは、事前積分と画面空間のぼかしを**併用**することもよくあります。事前積分で N·L のなだらかさを担当し、画面空間のぼかしで、影の縁などの広い範囲の散乱を担当します。

## よくあるミス

??? failure "曲率をそのまま使って、顔の表面がまだら模様になる"
    画素ごとの `fwidth` はノイズが出る。**頂点ごとに曲率を計算して補間する**か、**曲率のテクスチャを焼く**。

??? failure "LUT のアドレスが端で折り返して、境が見える"
    LUT のサンプラーは **clamp**。LUT の端のテクセルを、半テクセル内側から使う。

??? failure "影の縁に、赤みが出ない"
    事前積分は、シャドウ マップの影の縁には効かない。**影の縁の赤み**は、**影の判定にぼかしを掛ける**か、画面空間の SSS を併用する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 入力は<strong>N·L</strong>と<strong>曲率</strong>。**LUT を 1 回引くだけで、SSS のなだらかさ**が出る
    - [x] LUT は、**球の表面で拡散プロファイルを積分**して、事前に作る
    - [x] **法線を色ごとにぼかす**と、肌の柔らかさが増す
    - [x] **軽い**が、**影の縁の赤みと薄い部位の透け**は別に処理する

## 参考

- Penner, Borshukov, "Pre-Integrated Skin Shading"（GPU Pro 2, 2011）
- Penner, "Pre-Integrated Skin Shading"（SIGGRAPH 2011 Advances in Real-Time Rendering in Games）
- d'Eon, Luebke, "Advanced Techniques for Realistic Real-Time Skin Rendering"（GPU Gems 3, 2007）

## 関連ページ

- [Skin Overview](index.md)
- [Subsurface Scattering](subsurface-theory.md)
- [Separable SSS](screen-space-sss.md)
- [Thin Translucency](thin-translucency.md)
