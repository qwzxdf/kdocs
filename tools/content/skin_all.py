import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import pg  # noqa: E402

pg.Add("skin-hair/hair/transparency.md", '''
## 実装：ハッシュド アルファ テストと、2 パス描画

### ハッシュド アルファ テスト（Wyman と McGuire、2017）

アルファ テストの閾値を、固定の 0.5 にすると、細い毛が、ぷつぷつ途切れます。閾値を、画素ごとに、ばらつかせ、時間で変えると、TAA が平均して、半透明に見えます。

```hlsl
// 画素ごとに、疑似乱数の閾値を決め、アルファがそれより小さければ捨てる（ワールド位置から決めるので、動いても貼りつく）。
float Hash(float2 p) { return frac(sin(dot(p, float2(127.1, 311.7))) * 43758.5453); }

float HashedThreshold(float3 object_pos, float3 object_dx, float3 object_dy) {
  float max_deriv = max(length(object_dx), length(object_dy));            // 画面上の 1 画素が、オブジェクト空間で覆う大きさ
  float pix_scale = 1.0 / max_deriv;
  float2 pix_scale_pair = float2(exp2(floor(log2(pix_scale))), exp2(ceil(log2(pix_scale))));
  float2 alpha = float2(Hash(floor(pix_scale_pair.x * object_pos.xy)), Hash(floor(pix_scale_pair.y * object_pos.xy)));
  float lerp_factor = frac(log2(pix_scale));
  return lerp(alpha.x, alpha.y, lerp_factor);                              // 2 つのスケールの閾値を補間
}
```

閾値の模様を、物体に貼りつけておくと、カメラが動いても、ちらつきません。スケールを、距離に応じて 2 の冪で切り替えるのは、遠くでも、近くでも、同じ粗さに見せるためです。

```hlsl
// ピクセル シェーダーの最後で、アルファと閾値を比べる。
float threshold = clamp(HashedThreshold(input.object_pos, ddx(input.object_pos), ddy(input.object_pos)), 1e-3, 1.0);
if (alpha < threshold) discard;
```

### 2 パス描画：まず、毛先を、深度に書き、次に、色を描く

```cpp
// パス 1: アルファ テスト（閾値 0.5 ほど）で、深度だけ書く。毛の芯の部分が、確実に、深度を作る。
context->OMSetDepthStencilState(depth_write_state.Get(), 0);
DrawHairDepthOnly();

// パス 2: 深度は、書かずに、比較だけ（EQUAL ではなく LESS_EQUAL）。色を、アルファ ブレンドで描く（奥から手前の順に並べ替えた、ストランド）。
context->OMSetDepthStencilState(depth_test_only_state.Get(), 0);
context->OMSetBlendState(alpha_blend_state.Get(), nullptr, 0xFFFFFFFF);
DrawHairColor();
```

パス 1 で、髪の「芯」を確定させると、パス 2 では、毛の周りの、柔らかい縁だけが、アルファ ブレンドされ、重なりの順序の乱れが、目立ちません。

''', before="## よくあるミス")

pg.Add("skin-hair/hair/geometry.md", '''
## 実装：ストランドを、カメラに向けて、帯にする

ストランドは、1 本の線（頂点の列）ですが、線のままでは、細すぎて描けません。頂点シェーダーで、カメラを向く、細い帯（ビルボード）に広げます。

### 頂点バッファ

```cpp
// 各ストランドの、頂点（位置と太さ）を、StructuredBuffer に入れる。
struct StrandVertex { DirectX::XMFLOAT3 position; float thickness; };
D3D11_BUFFER_DESC desc = {};
desc.ByteWidth = sizeof(StrandVertex) * vertex_count;
desc.StructureByteStride = sizeof(StrandVertex);
desc.BindFlags = D3D11_BIND_SHADER_RESOURCE | D3D11_BIND_UNORDERED_ACCESS;   // 物理シミュレーションが書き込む
desc.MiscFlags = D3D11_RESOURCE_MISC_BUFFER_STRUCTURED;
device->CreateBuffer(&desc, nullptr, &strand_vertices);
```

シミュレーション（髪の動き）を、計算シェーダーで行うなら、UAV で書き込み、描画では、SRV で読みます。

### 帯に広げる

```hlsl
// 頂点 ID から、どのセグメントの、どちら側の頂点かを決め、線の接線に直交する向きに、幅だけ広げる。
VSOut StrandVS(uint vertex_id : SV_VertexID) {
  uint segment = vertex_id / 2;
  float side = (vertex_id & 1) ? 1.0 : -1.0;
  StrandVertex v = g_strand[segment];
  StrandVertex next = g_strand[min(segment + 1, g_strand_vertex_count - 1)];
  float3 tangent = normalize(next.position - v.position);                  // 毛の向き
  float3 to_camera = normalize(g_camera_position - v.position);
  float3 side_dir = normalize(cross(tangent, to_camera));                  // カメラに向いた帯の、幅の向き
  float3 world = v.position + side_dir * side * v.thickness * 0.5;
  VSOut o;
  o.position = mul(float4(world, 1.0), g_view_proj);
  o.tangent = tangent;                                                       // シェーディング（Kajiya-Kay、Marschner）で使う
  return o;
}
```

`cross(接線, 視線)` で、帯の幅の向きが決まります。接線は、シェーディングで、必要なので、ピクセル シェーダーへ渡します（[Kajiya-Kay](kajiya-kay.md)、[Marschner](marschner.md)）。

### 太さの下限：細すぎる毛は、サブピクセルに消える

```hlsl
// 画面上で 1 画素より細くなる毛は、幅を 1 画素に保ち、かわりにアルファを下げて、ちらつきを防ぐ。
float pixel_world = length(clip_w) * g_pixel_size;                          // 1 画素が、その距離で覆う、ワールドの幅
float width = max(thickness, pixel_world);
float coverage = thickness / width;                                          // 太さが足りない分は、アルファで補う
```

幅を、画素より細くすると、ストランドが、ラスタライザーに拾われず、ちらちら消えます。幅を保ち、アルファで、実際の太さを表す方法が、定番です（TressFX など）。

''', before="## よくあるミス")

pg.Add("skin-hair/skin/subsurface-theory.md", '''
## 拡散プロファイルを、数値で扱う

### 距離ごとの、光の広がり

皮膚に、細い光を当てたとき、入った点から、距離 `r` だけ離れた場所に、どれだけの光が出てくるかを、**拡散プロファイル** `R(r)` と呼びます。赤・緑・青で、広がり方が違います（赤が、最も遠くまで届く）。

```text
R(r) ≈ Σ w_i · G(r, v_i)      （ガウス関数 G の、重み付きの和で近似する）
```

d'Eon と Luebke（2007）は、皮膚の `R(r)` を、**6 つのガウス**の和で、よく近似できることを示しました。ガウスは、重ね合わせても、ガウスのままなので、画像のぼかしとして、実装できます。

```hlsl
// 分散 v のガウス関数（2D）。距離 r での重み。
float Gaussian(float v, float r) {
  return exp(-r * r / (2.0 * v)) / (2.0 * 3.14159265 * v);
}

// 赤・緑・青ごとに、重みと分散を持つ、6 ガウスの拡散プロファイル（d'Eon と Luebke の皮膚の値、単位: mm²）。
float3 DiffusionProfile(float r) {
  return float3(0.233, 0.455, 0.649) * Gaussian(0.0064, r)
       + float3(0.100, 0.336, 0.344) * Gaussian(0.0484, r)
       + float3(0.118, 0.198, 0.000) * Gaussian(0.1870, r)
       + float3(0.113, 0.007, 0.007) * Gaussian(0.5670, r)
       + float3(0.358, 0.004, 0.000) * Gaussian(1.9900, r)
       + float3(0.078, 0.000, 0.000) * Gaussian(7.4100, r);
}
```

分散が大きいガウスほど、遠くまで光が届きます。赤の成分だけが、大きなガウス（分散 1.99、7.41）に、重みを持つので、皮膚の「赤み」が、光の当たる場所から、にじみ出るように広がります。

### 正規化：エネルギーを保つ

```hlsl
// 重みの合計が 1（各色）になるよう、割る。そうしないと、ぼかしただけで、明るさが変わってしまう。
float3 total = float3(0.233 + 0.100 + 0.118 + 0.113 + 0.358 + 0.078,
                      0.455 + 0.336 + 0.198 + 0.007 + 0.004,
                      0.649 + 0.344 + 0.007);
float3 normalized_weight = weight / total;
```

拡散プロファイルは、広がる前後で、光の総量を変えない（吸収は別に扱う）ので、積分が 1 になるよう、正規化します。

### リアルタイムでの使い方

ガウスは、**水平方向の、ぼかしと、垂直方向の、ぼかし**に、分けられます（分離可能）。6 つのガウスを、画面空間の、ぼかしとして、順に適用し、足し合わせるのが、d'Eon と Luebke の、テクスチャ空間 SSS です。Jimenez ら（2015）は、1 つの、分離可能なカーネルで、プロファイル全体を近似し、1 回の、水平・垂直のぼかしで済ませました（[Screen-Space SSS](screen-space-sss.md)）。

''', before="## よくあるミス")
print("ok")
