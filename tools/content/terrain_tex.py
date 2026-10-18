import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import pg  # noqa: E402

ANDERSSON = '''Andersson, "Terrain Rendering in Frostbite Using Procedural Shader Splatting", SIGGRAPH 2007, Advances in Real-Time Rendering in 3D Graphics and Games（Frostbite の地形の素材合成）'''
BLOOM = '''Bloom, "Terrain Texture Compositing by Blending in the Frame-Buffer", 2000（レイヤーごとに別パスで、フレーム バッファにブレンドする古典的な方法）'''
MISHKINIS = '''Mishkinis, "Advanced Terrain Texture Splatting", Gamasutra, 2013（高さを使ったテクスチャのブレンド）'''
GEISS = '''Geiss, "Generating Complex Procedural Terrains Using the GPU", GPU Gems 3, Chapter 1, 2007（トライプラナー テクスチャリングを使った地形）'''
GOLUS = '''Golus, "Normal Mapping for a Triplanar Shader", 2017（トライプラナーでの法線マップの合成）'''
BARRE = '''Barré-Brisebois, Hill, "Blending in Detail", 2012（法線マップを合成する方法の比較）'''
QUILEZ_BIPLANAR = '''Quilez, "Biplanar Mapping", iquilezles.org, 2020（3 回ではなく 2 回の読み込みで済ませるトライプラナー）'''
HEITZ = '''Heitz, Neyret, "High-Performance By-Example Noise using a Histogram-Preserving Blending Operator", High-Performance Graphics 2018'''
MIKKELSEN = '''Mikkelsen, "Practical Real-Time Hex-Tiling", Journal of Computer Graphics Techniques, Vol. 11, No. 2, 2022'''
QUILEZ_REPEAT = '''Quilez, "Texture Repetition", iquilezles.org, 2015（セルごとのランダムなずらしと、ブレンド）'''
COHEN = '''Cohen, Shade, Hiller, Deussen, "Wang Tiles for Image and Texture Generation", ACM Transactions on Graphics (SIGGRAPH 2003)'''
HECKBERT = '''Heckbert, "Fundamentals of Texture Mapping and Image Warping", Master's thesis, UC Berkeley, 1989（楕円の足跡を使うフィルタリングの基礎）'''
FELINE = '''McCormack, Perry, Farkas, Jouppi, "Feline: Fast Elliptical Lines for Anisotropic Texture Mapping", SIGGRAPH 1999'''
PERSSON = '''Persson, "Volume Decals", GPU Pro 2, 2011'''
BARRETT = '''Barrett, "Sparse Virtual Textures", Game Developers Conference 2008'''
WAVEREN = '''van Waveren, "id Tech 5 Challenges: From Texture Virtualization to Massive Parallelization", SIGGRAPH 2009, Beyond Programmable Shading'''
MITTRING = '''Mittring, "Advanced Virtual Texture Topics", SIGGRAPH 2008, Advances in Real-Time Rendering in 3D Graphics and Games'''
D3D11_FILTER = '''Microsoft Learn, "D3D11_SAMPLER_DESC"（`D3D11_FILTER_ANISOTROPIC` と `MaxAnisotropy`）'''

# ---------------------------------------------------------------- weights
pg.Dedup("terrain/texturing/weights.md")
pg.Add("terrain/texturing/weights.md", '''
## スプラット マップのデータ

スプラット（splat）は、「ばら撒く」という意味です。地形に使うテクスチャ（草・土・岩・雪）の<strong>混ぜ具合を、画素ごとに記録した画像</strong>が、スプラット マップです。

| 形式 | 内容 |
| --- | --- |
| `R8G8B8A8_UNORM` | 1 枚で 4 層分。R が草、G が土、B が岩、A が雪、のように割り当てる |
| 2 枚 | 8 層まで。多い地形では、4 層ごとに 1 枚を足す |
| 重みの合計 | 4 つの重みの合計は、1 になるのが前提。画像として塗ると、ずれるので、シェーダーで正規化する |

重みの 4 つ目は、「1 − (残りの 3 つ)」で求められます。3 つだけ記録して、残りは計算することで、`R8G8B8` 1 枚（A に別の情報）にもできます。ただし、**8 ビット同士の足し算は、誤差が積もる**ので、4 つ記録して、読んだあとに正規化するのが安全です。

```hlsl
float4 LoadWeights(float2 uv) {
  float4 w = splat_map.Sample(linear_clamp, uv);
  // 塗った結果、合計が 1 からずれることがある。1 に直す。
  return w / max(dot(w, 1.0), 1e-4);
}
```

### テクスチャ配列で、層をまとめる

層ごとに別のテクスチャにすると、シェーダーのスロット数が足りなくなります。同じ大きさ・同じ形式のテクスチャは、**テクスチャ配列（`Texture2DArray`）** にまとめます。1 つのスロットに、最大で 2,048 枚まで入ります。

```cpp
// 4 層の、アルベド（色）を配列にする。
D3D11_TEXTURE2D_DESC desc = {};
desc.Width = 1024;
desc.Height = 1024;
desc.MipLevels = 0;                 // 全ミップ（必須。遠くのタイルのちらつきを防ぐ）
desc.ArraySize = 4;                 // 層の数
desc.Format = DXGI_FORMAT_BC7_UNORM_SRGB;   // 色: BC7（sRGB）。高さは、A に入れる
desc.SampleDesc.Count = 1;
desc.Usage = D3D11_USAGE_DEFAULT;
desc.BindFlags = D3D11_BIND_SHADER_RESOURCE;
// 各スライスと各ミップに、初期データを渡す（DDS から読み込むのが普通）。
```

```hlsl
Texture2DArray<float4> g_albedo_height : register(t1);   // RGB = 色, A = 高さ
Texture2DArray<float4> g_normal        : register(t2);
SamplerState g_linear_wrap : register(s1);
```

## 毎画素の、コストを下げる

スプラットは、層が増えると、重くなります。4 層で、テクスチャ読み込みが、**層の数 × 種類の数**（色・法線・粗さ）になります。

| 工夫 | 内容 |
| --- | --- |
| 重みが 0 の層は、読まない | `if (w.x > 0.01)` で、読み込みを飛ばす。ブロックごとに、同じ層だけが出るので、分岐が揃う（ダイナミック ブランチの効率がよい） |
| 1 画素に使う層を、上位 N 個に絞る | スプラット マップに、「層の番号」と「重み」を、画素ごとに 2〜4 組だけ記録する。層が 32 個でも、1 画素の読み込みは、4 層分で済む |
| 遠くは、層を減らす | 距離で、法線マップの層を、読まなくする（遠くでは見えない） |
| タイルごとに、シェーダーを選ぶ | そのタイルに現れる層だけを、読むシェーダーを使う（Frostbite の方式、下記） |

### 層の番号と重みを、別々の画像に記録する

```text
index map (R8G8B8A8_UINT, 点サンプリング) : 画素ごとに 4 つの層の番号
weight map (R8G8B8A8_UNORM, 線形補間)     : 画素ごとに 4 つの重み
```

層の番号は、補間してはいけません（番号 2 と 5 の中間の 3 や 4 は、別の層です）。点サンプリングで読み、重みだけを、線形補間します。境目では、番号が変わるので、**隣の 4 画素の番号を、すべて調べて、重みを混ぜる**実装が必要です。ここまで来ると、仮想テクスチャ（[Virtual Texturing](virtual-texture.md)）の方が、素直になります。

## 自動で重みを決める

高さと傾きから、ルールで重みを計算できます。エディターで塗る前の、下地として使えます。

```hlsl
// 傾き: 法線の y が 1 に近いほど、平ら。
float Slope(float3 normal) { return 1.0 - saturate(normal.y); }

float4 ComputeWeights(float3 world_pos, float3 normal, float noise) {
  float slope = Slope(normal);
  // ノイズで、しきい値を揺らす。境目が、直線にならない。
  float jitter = (noise - 0.5) * 0.1;

  float rock = smoothstep(0.35, 0.55, slope + jitter);                   // 急な所は岩
  float snow = smoothstep(snow_line, snow_line + 20.0, world_pos.y + jitter * 50.0)
             * (1.0 - rock);                                              // 高い所は雪（岩を除く）
  float sand = (1.0 - smoothstep(water_level, water_level + 2.0, world_pos.y))
             * (1.0 - rock);                                              // 水際は砂
  float grass = max(1.0 - rock - snow - sand, 0.0);                       // 残りは草

  float4 w = float4(grass, sand, rock, snow);
  return w / max(dot(w, 1.0), 1e-4);
}
```

| 条件 | 変化の付け方 |
| --- | --- |
| 傾き | `smoothstep` で、2 つのしきい値の間を、なめらかに。しきい値が近いと、境目が鋭い |
| 高さ | 雪線のように、高さで切り替える。ノイズで揺らして、等高線に見えないようにする |
| 水からの距離 | 浜辺の砂。水位との差を使う |
| 曲率（凸凹） | 尾根には岩、谷には土、のように、地形の凹凸（ラプラシアン）を使う |
| 湿度・日当たり | 北向きの斜面に苔、など。別のマップを使う |

!!! tip "ルールは、重みマップに焼いてしまうのが基本"
    毎フレーム、ピクセル シェーダーで計算すると、ルールの数だけ重くなります。**ツールで一度計算して、スプラット マップに書き出し**、実行時は、マップを読むだけにします。ルールの結果に、手で塗った上書きを足せる、という利点もあります。

```text
最終の重み = ルールの重み × (1 − 手描きマスク) + 手描きの重み × 手描きマスク
```

## Frostbite の、手続き的なスプラット

Andersson（2007）は、Frostbite の地形で、<strong>「どの層が必要かを、ブロックごとに決めて、そのブロックだけに、必要な層を読むシェーダーを使う」</strong>方式を報告しています。

| 項目 | 内容 |
| --- | --- |
| 素材の定義 | 層ごとに、「どの高さ・傾き・ペイントのとき、この層が現れるか」というルールを持つ |
| ブロック分け | 地形を、小さなタイルに分ける |
| シェーダー | タイルに現れる層の組み合わせごとに、必要な層だけを、読んで混ぜるシェーダーを作る |
| 効果 | 数十種類の素材があっても、**1 タイルでは、数層だけを読む**。重みが 0 の層に、時間を使わない |

全ピクセルで、全層を読む方式（4 層、8 層まで）では、層が増えるほど遅くなりますが、**ブロック単位で、必要なものだけを読む**と、層の総数と、描画のコストが、切り離されます。素材のルールを、アーティストが作れるように、ツールの側に、組み合わせ用の仕組みが必要になります。

## 昔の方法：レイヤーごとのパス

古い GPU では、1 回のパスで読めるテクスチャの数が、4 枚ほどしかありませんでした。そこで、**層ごとに、地形を描き直して、フレーム バッファにアルファ ブレンドで重ねる**方法（Bloom、2000）が使われました。

```text
パス 1: 草を、不透明で描く
パス 2: 土を、スプラット マップの G を、アルファにして、重ねる
パス 3: 岩を、B をアルファにして、重ねる
```

層の数だけ、ジオメトリを描き直すので、頂点の処理が増えます。1 パスで、配列から読む方式の方が、いまは、はるかに効率的です。

''', before="## よくあるミス")
pg.Refs("terrain/texturing/weights.md", [ANDERSSON, BLOOM, MISHKINIS, "Microsoft Learn, \"Texture2DArray\"（HLSL のテクスチャ配列）"])

# ---------------------------------------------------------------- height blend
pg.Dedup("terrain/texturing/height-blend.md")
pg.Add("terrain/texturing/height-blend.md", '''
## なぜ、線形ブレンドは不自然なのか

重みで、色を線形に混ぜると、境目は、「2 枚の写真が、半透明で重なった」ように見えます。実際の地面では、境目は、そうなりません。

| 現実の地面 | 線形ブレンド |
| --- | --- |
| 石の高い所は、石のまま。土は、石の隙間に溜まる | どこでも、石と土が、同じ割合で混ざる |
| 境目が、凹凸に沿って、ギザギザになる | 境目が、ぼんやりと、なだらかに混ざる |
| 草の根元に、土が見える | 草と土が、一面に、均等に混ざる |

ここで欲しいのは、**「重みが 0.5 でも、石の出っ張りは石、窪みは土」と、高さで勝敗を決める**ことです。各テクスチャに、<strong>高さ情報（出っ張り・窪み）</strong>を持たせて、<strong>重みに、高さを足した値が最も大きい層だけが、見える</strong>ようにします。

## 基本の式

層 i の重みを `w_i`、高さを `h_i` とします。

```text
v_i = w_i + h_i                    重みと高さの合計（その層の勢い）
m   = max(v_i) − depth             一番勢いのある層から、depth だけ引いた線
b_i = max(v_i − m, 0)              その線より上に出ている分だけが、見える
最終の重み = b_i / Σ b_j
```

| 値 | 意味 |
| --- | --- |
| `depth` | 境目の幅。0 に近いと、勝った層だけが残る（切り替え）。大きいと、線形ブレンドに近づく |
| `max(...)` | 一番高い層を、基準にする |
| `/ Σ b_j` | 重みの合計を、1 に戻す |

`depth` が小さいほど、境目が鋭く、凹凸に沿った形になります。`0.05〜0.2` の間で、見た目に合わせます。

## シェーダーでの書き方

```hlsl
// 4 層分の、高さを読む。高さは、アルベドのアルファ チャンネルに入れておくと、
// 色と同時に 1 回で読める。
float4 SampleHeights(float2 uv) {
  return float4(
      g_albedo_height.Sample(g_linear_wrap, float3(uv, 0)).a,
      g_albedo_height.Sample(g_linear_wrap, float3(uv, 1)).a,
      g_albedo_height.Sample(g_linear_wrap, float3(uv, 2)).a,
      g_albedo_height.Sample(g_linear_wrap, float3(uv, 3)).a);
}

float4 HeightBlendWeights(float4 weights, float4 heights, float depth) {
  float4 v = weights + heights;
  float m = max(max(v.x, v.y), max(v.z, v.w)) - depth;
  float4 b = max(v - m, 0.0);
  return b / max(dot(b, 1.0), 1e-4);
}

float4 main(PSInput input) : SV_Target {
  float4 w = LoadWeights(input.splat_uv);
  float4 h = SampleHeights(input.tile_uv);
  float4 fw = HeightBlendWeights(w, h, 0.15);

  float3 color = 0;
  [unroll] for (int i = 0; i < 4; ++i) {
    color += g_albedo_height.Sample(g_linear_wrap, float3(input.tile_uv, i)).rgb * fw[i];
  }
  return float4(color, 1.0);
}
```

最後のループで、`Sample` を、もう一度呼んでいます。コンパイラが、同じ読み込みを、まとめてくれることが多いですが、**高さの読み込みと、色の読み込みを、1 回にまとめた**ほうが確実です。

## よく起きる問題と対策

### ① 重みが 0 の層が、顔を出す

`v_i = w_i + h_i` なので、**重みが 0 でも、高さが高い層は、`v_i` が大きくなります**。`depth` を大きくすると、重みが 0 の層が、現れてしまいます。

| 対策 | 内容 |
| --- | --- |
| 高さに、重みを掛ける | `v_i = w_i + h_i * w_i`（`w_i = 0` なら、必ず 0） |
| 重みを、高さの影響範囲に収める | `v_i = w_i * (1 + k * h_i)` のような形 |
| 重みが 0 なら、除外する | `b_i *= step(0.001, w_i)` |

```hlsl
// 重みが 0 の層は、高さがどれだけ高くても、現れない形にする。
float4 HeightBlendWeights2(float4 weights, float4 heights, float depth) {
  float4 v = weights * (1.0 + heights);              // 重みが 0 なら 0
  float m = max(max(v.x, v.y), max(v.z, v.w)) - depth;
  float4 b = max(v - m, 0.0) * step(0.001, weights);
  return b / max(dot(b, 1.0), 1e-4);
}
```

### ② 境目の、画素が、ちらつく

スプラット マップの重みは、バイリニアで、補間されます。高さブレンドは、**重みの小さな変化を、急な変化に変える**ので、境目が、ギザギザに、ちらつきます。

- スプラット マップの解像度を上げる
- `depth` を、少し大きくして、境目に、幅を持たせる
- ノイズで、重みを揺らして、規則的なギザギザを、消す

### ③ 高さを、どこから取るか

| 方法 | 内容 |
| --- | --- |
| アルベドの A に入れる（BC7） | 色と同時に読める。**高さの精度は、8 ビット**。標準的 |
| 法線マップの A に入れる | 同上。法線マップが、BC5 で A が使えない場合は、別のテクスチャが必要 |
| 専用の高さマップ（`R8_UNORM`） | 精度は自由。読み込みが、1 回増える |
| ORM テクスチャに入れる | Occlusion・Roughness・Metallic に加えて、高さを、1 枚にまとめる |

高さの値は、0〜1 に正規化して、**平均が 0.5 になるよう**に、作ります。平均が偏っていると、層ごとに、勝ちやすさが違ってしまいます。

## 実装のバリエーション

| 方式 | 特徴 |
| --- | --- |
| 上の式（`weights + heights`） | 最も単純。多くの実装で、基本形になっている |
| `weights * heights` を、べき乗する | 重みが 0 の層が、出ない。境目が、ややなめらか |
| Mishkinis（2013）の方式 | 層ごとの高さに、コントラストを足して、ブレンドの鋭さを、素材ごとに調整できる |

層ごとに、`depth` や、高さのコントラストを変えると、<strong>「砂は、石の隙間に入り込む」「草は、土の上に乗る」</strong>のような、素材ごとの性格を、出せます。

''', before="## よくあるミス")
pg.Refs("terrain/texturing/height-blend.md", [MISHKINIS, ANDERSSON, "Unity Technologies, \"HDRP: Layered Lit Shader\" のドキュメント（高さブレンドの実装例）"])

# ---------------------------------------------------------------- triplanar
pg.Dedup("terrain/texturing/triplanar.md")
pg.Add("terrain/texturing/triplanar.md", '''
## なぜ、上から貼ると、伸びるのか

地形のテクスチャは、普通、**真上から（XZ 平面に）投影**して貼ります。UV は、ワールドの x と z を、そのまま使います。平らな場所では、これでよいのですが、**斜面が急になると、1 テクセルが、斜面の上で、縦に長く伸びます**。

| 斜面の角度 | テクスチャの伸び（1 / cos θ） |
| --- | --- |
| 0°（水平） | 1.0 倍 |
| 45° | 1.4 倍 |
| 60° | 2.0 倍 |
| 80° | 5.8 倍 |
| 90°（垂直） | 無限大（1 本の線になる） |

崖では、テクスチャが、縦の筋に、なってしまいます。

## トライプラナー（3 方向の投影）

X 軸・Y 軸・Z 軸の、**3 方向から、それぞれ投影した 3 枚を、法線の向きで混ぜる**のが、トライプラナー マッピングです。法線がどの軸に近いかで、重みを決めます。

| 法線が近い軸 | 使う投影 | UV |
| --- | --- | --- |
| X（右・左を向いた面） | YZ 平面に投影 | `world.zy` |
| Y（上・下を向いた面） | XZ 平面に投影 | `world.xz` |
| Z（前・後を向いた面） | XY 平面に投影 | `world.xy` |

```hlsl
// 法線の絶対値を、べき乗して、合計 1 に正規化する。
// sharpness が大きいほど、切り替えが、鋭い（混ざる幅が、せまい）。
float3 TriplanarWeights(float3 n, float sharpness) {
  float3 w = pow(abs(n), sharpness);
  return w / max(w.x + w.y + w.z, 1e-4);
}

float3 TriplanarColor(Texture2D tex, float3 world_pos, float3 n, float scale) {
  float3 w = TriplanarWeights(n, 4.0);
  float3 cx = tex.Sample(g_linear_wrap, world_pos.zy * scale).rgb;
  float3 cy = tex.Sample(g_linear_wrap, world_pos.xz * scale).rgb;
  float3 cz = tex.Sample(g_linear_wrap, world_pos.xy * scale).rgb;
  return cx * w.x + cy * w.y + cz * w.z;
}
```

`sharpness` が小さいと、3 枚が広い範囲で混ざって、模様がぼやけます。大きいと、切り替えが鋭くなって、境目に、線が出ます。**4〜8 が、よく使われる範囲**です。

## 法線マップを、正しく混ぜる

色は、そのまま混ぜられますが、**法線マップは、そのままでは、混ぜられません**。法線マップの向きは、投影した面（接線空間）のものなので、ワールドの向きに、直してから混ぜる必要があります。

次は、Golus が整理した、「whiteout ブレンド」を使った書き方です。ワールド法線（地形の滑らかな法線）に、法線マップの凹凸を、足し合わせます。

```hlsl
float3 TriplanarNormal(Texture2D normal_tex, float3 world_pos, float3 n, float scale) {
  // 3 方向の、接線空間の法線を読む（-1〜1 に戻す）。
  float3 tx = normal_tex.Sample(g_linear_wrap, world_pos.zy * scale).xyz * 2.0 - 1.0;
  float3 ty = normal_tex.Sample(g_linear_wrap, world_pos.xz * scale).xyz * 2.0 - 1.0;
  float3 tz = normal_tex.Sample(g_linear_wrap, world_pos.xy * scale).xyz * 2.0 - 1.0;

  // whiteout ブレンド: ワールド法線の成分を、XY に足し、Z は掛ける。
  tx = float3(tx.xy + n.zy, abs(tx.z) * n.x);
  ty = float3(ty.xy + n.xz, abs(ty.z) * n.y);
  tz = float3(tz.xy + n.xy, abs(tz.z) * n.z);

  // 軸を入れ替えて、ワールドの向きに直し、重みで混ぜる。
  float3 w = TriplanarWeights(n, 4.0);
  return normalize(tx.zyx * w.x + ty.xzy * w.y + tz.xyz * w.z);
}
```

| 法線の混ぜ方 | 内容 | 結果 |
| --- | --- | --- |
| 単純な平均 | 3 つの法線マップを、そのまま重みで平均 | 向きが、間違っているので、凹凸が逆になることがある |
| UDN ブレンド | ワールド法線の XY に、法線マップの XY を足す | 軽い。凹凸が、やや弱くなる |
| whiteout | 上のコード。XY を足し、Z を掛ける | 凹凸が、保たれる。実用的 |
| Reoriented Normal Mapping（RNM） | 回転で合成する。もっとも正確 | 少し重い（Barré-Brisebois と Hill の比較を参照） |

!!! warning "法線マップの、Y の向きを確認する"
    DirectX 系の法線マップは、緑（Y）が、下向きを正と数える形式（D3D 形式）と、上向きを正と数える形式（OpenGL 形式）があります。取り違えると、**凹凸が、逆に見えます**。アセットの形式に、シェーダーを合わせます。

## コスト

| 項目 | 内容 |
| --- | --- |
| テクスチャの読み込み | 1 層につき、3 倍（色・法線・粗さなら、9 回） |
| 帯域 | 同じテクスチャを 3 回読むので、キャッシュには乗りやすい |
| ALU | 重みの計算と、法線の混ぜ合わせ |

### 読み込みを、減らす方法

| 方法 | 内容 |
| --- | --- |
| 傾きで使い分ける | 平らな所は、1 方向（安い）。急な所だけ、3 方向。ピクセルごとに、分岐する |
| 層ごとに使い分ける | **岩の層だけ**、トライプラナーにする。草や土は、真上からの投影のまま |
| 2 方向だけ読む（バイプラナー） | 重みが最も大きい 2 方向だけを読む。Quilez が提案した方法 |
| 重みが小さい方向は、飛ばす | `if (w.x > 0.05)` で、読み込みを省く |

```hlsl
// 重みが、しきい値より小さい方向は、読み込まない。
float3 TriplanarColorFast(Texture2D tex, float3 world_pos, float3 n, float scale) {
  float3 w = TriplanarWeights(n, 4.0);
  float3 c = 0;
  if (w.x > 0.05) c += tex.Sample(g_linear_wrap, world_pos.zy * scale).rgb * w.x;
  if (w.y > 0.05) c += tex.Sample(g_linear_wrap, world_pos.xz * scale).rgb * w.y;
  if (w.z > 0.05) c += tex.Sample(g_linear_wrap, world_pos.xy * scale).rgb * w.z;
  return c / max(dot(w * step(0.05, w), 1.0), 1e-4);
}
```

分岐の中で `Sample` を呼ぶと、画素の微分が、不連続になって、ミップの選択が、乱れることがあります。分岐を使うなら、`SampleGrad` で、微分を、分岐の外で計算して渡します。

## 向き（符号）に、注意する

法線が、**負の向き**（`-X`、`-Y`、`-Z`）を向く面では、テクスチャが、**鏡に映したように**反転して見えます。UV を、そのまま使っているので、裏側から見たことになるためです。ほとんどの地形では、目立ちませんが、文字や、向きのある模様では、気になります。

| 対策 | 内容 |
| --- | --- |
| 符号で、UV を反転する | `uv.x *= sign(n.x)` のように、負の向きでは、反転させる |
| 気にしない | 岩・土のように、向きのない模様では、見た目の違いは、ほとんどない |

''', before="## よくあるミス")
pg.Refs("terrain/texturing/triplanar.md", [GEISS, GOLUS, BARRE, QUILEZ_BIPLANAR])

# ---------------------------------------------------------------- tiling
pg.Dedup("terrain/texturing/tiling.md")
pg.Add("terrain/texturing/tiling.md", '''
## 繰り返しが目立つ、理由

人間の目は、**同じ模様の繰り返し**を、とても敏感に見つけます。タイル状のテクスチャを、広い地面に貼ると、**遠くから見たとき、格子状の模様**が見えてしまいます。特に、明るさが少し違う大きな斑点（石、花の群れ）があると、そこが、目印になります。

| 見える現象 | 理由 |
| --- | --- |
| 格子状の模様 | テクスチャの周期ごとに、同じ目印が、並ぶ |
| 地平線に向かって、縞が見える | 遠くでは、周期が、画面上で、並んで見える |
| 同じ石が、何度も見える | 近くで、同じ形を、見つけられてしまう |

## 方法 1：スケールの違う 2 枚を重ねる

周期の違う 2 枚（たとえば、1 m と 23 m）を混ぜると、**2 つの周期の最小公倍数**が、見かけの周期になります。ほぼ繰り返しが、見えなくなります。

```hlsl
float3 near_color = albedo.Sample(g_linear_wrap, world_pos.xz * 0.5).rgb;     // 2 m ごとに繰り返し
float3 far_color  = albedo.Sample(g_linear_wrap, world_pos.xz * 0.043).rgb;   // 約 23 m ごと
// 2 枚を掛けて 2 倍にすると、平均の明るさが、保たれる。
float3 color = near_color * far_color * 2.0;
```

遠くのテクスチャは、**平均が 0.5 の、低周波のテクスチャ**（明るさの揺らぎだけ）にしておきます。絵柄が強いと、そちらが、新しい目印になります。

## 方法 2：セルごとに、ずらして混ぜる

テクスチャを、格子のセルに分けて、**セルごとにランダムなずらし**を与えます。隣のセルとの境目は、ブレンドでつなぎます。1 つのセルの中は、普通のタイルですが、セルごとに、違う部分を、見せることになります。

Quilez が紹介した、この方式の考え方を、手を加えて示します。

```hlsl
float2 Hash2(float2 p) {
  // 整数のセル座標から、0〜1 の乱数を 2 つ作る
  float3 q = frac(float3(p.xyx) * float3(0.1031, 0.1030, 0.0973));
  q += dot(q, q.yzx + 33.33);
  return frac((q.xx + q.yz) * q.zy);
}

float3 SampleNoTiling(Texture2D tex, float2 uv) {
  float2 cell = floor(uv);
  float2 f = frac(uv);

  // ミップの選択を、セルの境目で、乱さないために、微分は、最初に計算して使い回す。
  float2 dx = ddx(uv);
  float2 dy = ddy(uv);

  float3 sum = 0;
  float wsum = 0;
  [unroll] for (int j = 0; j <= 1; ++j) {
    [unroll] for (int i = 0; i <= 1; ++i) {
      float2 g = float2(i, j);
      float2 offset = Hash2(cell + g);                 // このセルの、ランダムなずらし
      float2 r = g - f + offset * 0.5;                 // 画素から、ずらした中心への向き
      float w = exp(-5.0 * dot(r, r));                 // 中心に近いほど、重みが大きい
      sum += tex.SampleGrad(g_linear_wrap, uv + offset, dx, dy).rgb * w;
      wsum += w;
    }
  }
  return sum / wsum;
}
```

| 注意点 | 内容 |
| --- | --- |
| 読み込み | 4 回（2×2 のセル）。通常の 4 倍 |
| `SampleGrad` | 必須。`Sample` を使うと、セルの境目で、ミップが、急に変わって、線が見える |
| コントラストの低下 | 4 つを混ぜると、平均化して、コントラストが落ちる。次の方法 3 で、補正できる |

## 方法 3：ヒストグラムを保って混ぜる（Heitz と Neyret）

方法 2 の欠点は、**混ぜると、コントラストが、落ちる**ことです。複数のテクスチャの平均を取ると、ばらつきが、小さくなるからです（統計的には、平均化で、分散が減る）。

Heitz と Neyret（2018）は、これを、次の流れで、直しました。

| 段階 | 内容 |
| --- | --- |
| ① 前処理 | テクスチャの色の分布を、**正規分布（ガウス分布）に変換**する。変換の表（ルックアップ テーブル）も、保存する |
| ② 実行時の混ぜ合わせ | ずらした 3 つの読み込みを、**分散が保たれる重み**で、混ぜる（ガウス分布の性質を使う） |
| ③ 実行時の戻し | 混ぜた結果に、①のテーブルを、逆に適用して、元の色の分布に戻す |

結果は、**もとのテクスチャと、同じ色の分布**を持ち、しかも繰り返しが見えないテクスチャです。コストは、3 回の読み込みと、テーブルの引き 1 回です。

実装では、**①の前処理（ツール）**が、必要になる点が、手間です。

## 方法 4：六角形のタイル（Hex-Tiling）

Mikkelsen（2022）の方法は、**平面を、正三角形（または六角形）に分けて、3 つの頂点のそれぞれに、ずらしを与えて、混ぜる**やり方です。正方形のセルより、**セルの境目が、少なく、目立ちにくい**特徴があります。

| 項目 | 内容 |
| --- | --- |
| 読み込み | 3 回（正三角形の 3 頂点） |
| 混ぜる範囲 | 3 つの重みの合計が 1 になるので、広い範囲でなめらか |
| 法線マップ | ずらしだけでなく、回転も与える場合は、法線の向きも、回す必要がある |
| 実装の例 | Mikkelsen の論文に、HLSL / GLSL のコードがある |

回転も与えると、**向きのある模様（木目、石の層）が、乱れて、不自然になる**ことがあります。地形の土や砂のように、向きのない模様では、回転も、有効です。

## 方法 5：遠くで、別の模様に切り替える

「近く」と「遠く」で、別々の目的の、テクスチャを持ちます。

| 距離 | 使うテクスチャ | 役割 |
| --- | --- | --- |
| 近い（〜 20 m） | 細かい、ディテール テクスチャ | 近づいたときの、細かい凹凸 |
| 中間 | 通常のテクスチャ | 色と模様 |
| 遠い（100 m〜） | 低周波の、大きなスケールの色むら | 繰り返しを、見えなくする |

距離に応じて、重みを `smoothstep` で切り替えます。ディテール テクスチャは、**平均が 0.5**（掛け算で明るさが変わらない）に、作っておきます。

## 方法 6：Wang タイル

事前に、**辺の模様が合うタイルを、複数枚用意**しておき、セルごとに、辺の模様が合うタイルを、ランダムに並べます（Cohen ら、2003）。タイルの数が増えると、繰り返しは、ほとんど見えなくなります。ただし、**タイルを作る作業（ツール）が、大変**で、実行時にも、タイルの選択の、インデックス テクスチャが必要です。地形では、方法 2〜4 の方が、手軽です。

## 選び方

| 状況 | おすすめ |
| --- | --- |
| まず、手軽にやりたい | 方法 1（2 枚を重ねる）と、方法 5（遠くの色むら） |
| 草・土・砂の、向きのない模様 | 方法 4（hex-tiling）、または方法 3 |
| コントラストを、保ちたい | 方法 3（ヒストグラムを保つ） |
| ツールを作れる、品質を最優先 | 方法 3 ＋ 方法 5 |

''', before="## よくあるミス")
pg.Refs("terrain/texturing/tiling.md", [HEITZ, MIKKELSEN, QUILEZ_REPEAT, COHEN])

# ---------------------------------------------------------------- anisotropic
pg.Dedup("terrain/texturing/anisotropic.md")
pg.Add("terrain/texturing/anisotropic.md", '''
## なぜ、斜めから見ると、ぼやけるのか

テクスチャの 1 画素（ピクセル）が、テクスチャの上では、**どんな形の領域に当たるか**を考えます。真上から見ると、画面の 1 画素は、テクスチャの小さな正方形に当たります。**斜めから見る地面では、画面の 1 画素が、テクスチャの上で、細長い楕円**に当たります。

```text
真上から               斜めから（遠い地面）
┌──┐                  ┌──────────────┐
│  │  正方形          └──────────────┘  → 横に細長い楕円
└──┘
```

標準のミップマップ（等方性フィルタ）は、**正方形の領域**しか、平均できません。そこで、細長い領域の、長い方に合わせて、ミップを選ぶと、**短い方向が、必要以上に、ぼける**のです。

| 選び方 | 結果 |
| --- | --- |
| 短い方に合わせる | 長い方向が、ちらつく（エイリアシング） |
| 長い方に合わせる（標準のミップ） | 短い方向が、ぼける |

## 異方性フィルタリングの考え方

異方性（anisotropic）フィルタリングは、**楕円の足跡**を、直接扱います。基礎は、Heckbert（1989）の整理です。

1. 画面の 1 画素が、テクスチャ上で作る楕円の、**長軸と短軸**を求める（画面の微分 `ddx`・`ddy` から）
2. **短軸に合わせた、細かいミップ**を選ぶ
3. 長軸の方向に、**複数のサンプルを並べて、平均する**

サンプルの数は、`長軸 ÷ 短軸` の比で決まり、最大で `MaxAnisotropy` 個になります。

| 比（長軸 ÷ 短軸） | 使うサンプル数 |
| --- | --- |
| 1（真上から） | 1 |
| 4 | 4 |
| 16 | 16（`MaxAnisotropy = 16` のとき） |
| 32（ほぼ水平） | 16（上限） |

実際のハードウェアは、楕円を、**複数のトライリニア サンプルの列**で、近似しています（Feline など、各社の実装は少しずつ違う）。サンプルの数が増えるので、**テクスチャの帯域と、時間が、増えます**。ただし、斜めの面だけが、増える形で、真上を向いた面では、増えません。

## DirectX 11 での設定

サンプラー ステートを作るときに、`Filter` を `D3D11_FILTER_ANISOTROPIC` にして、`MaxAnisotropy` を設定します。

```cpp
D3D11_SAMPLER_DESC desc = {};
desc.Filter = D3D11_FILTER_ANISOTROPIC;     // 異方性フィルタリング
desc.AddressU = D3D11_TEXTURE_ADDRESS_WRAP; // 地形は、繰り返すのでラップ
desc.AddressV = D3D11_TEXTURE_ADDRESS_WRAP;
desc.AddressW = D3D11_TEXTURE_ADDRESS_WRAP;
desc.MaxAnisotropy = 16;                    // 1〜16。大きいほど、品質が高く、重い
desc.MaxLOD = D3D11_FLOAT32_MAX;            // ミップを、すべて使う
desc.ComparisonFunc = D3D11_COMPARISON_NEVER;

Microsoft::WRL::ComPtr<ID3D11SamplerState> sampler;
device->CreateSamplerState(&desc, &sampler);
context->PSSetSamplers(0, 1, sampler.GetAddressOf());
```

| 設定 | 内容 |
| --- | --- |
| `Filter` | `D3D11_FILTER_ANISOTROPIC`（縮小・拡大・ミップの、すべてが、異方性） |
| `MaxAnisotropy` | 最大サンプル数。1 で、異方性なし。2、4、8、16 |
| ミップが、あること | 異方性フィルタは、ミップマップを、使う。ミップのないテクスチャでは、効かない |

## どのくらい効くか

| 設定 | 見た目 | コスト（斜めの面） |
| --- | --- | --- |
| トライリニア（異方性なし） | 遠くの地面が、ぼやける | 1 倍 |
| 2x | 少し改善 | 約 2 倍 |
| 4x | 中程度の斜めまで、くっきり | 約 4 倍 |
| 8x | 低い視点でも、ほぼ、くっきり | 約 8 倍 |
| 16x | ほぼ水平の面まで、くっきり | 約 16 倍 |

ただし、「斜めの面の、テクスチャ読み込みだけ」の倍率です。ゲーム全体のフレーム時間は、そこまで増えません（ほかの処理が、ほとんどのため）。**近年の GPU では、16x でも、コストは小さい**ことが多いです。

## 地形では、ほぼ必須

地形は、**視点が低く、地面が、ほぼ水平に見える**ことが多い対象です。遠くの地面は、画面の中で、ほぼ水平で、異方性の比が、非常に大きくなります。異方性フィルタリングがないと、**中景から遠景で、地面のテクスチャが、ぼけた絵の具のように見えます**。

### 注意点

| 項目 | 内容 |
| --- | --- |
| トライプラナーとの併用 | 3 方向の、それぞれに効く。コストは 3 倍になる（[Triplanar Mapping](triplanar.md)） |
| 法線マップ | 異方性は、法線マップにも効く。ぼけると、スペキュラーが、不自然になる |
| 頂点シェーダー | 頂点では、`SampleLevel` で、ミップを指定する（異方性は、画素の微分から決めるので、頂点では使えない） |
| 設定の入れ替え | ユーザー設定で、1x〜16x を、切り替えられるように、しておく |

''', before="## よくあるミス")
pg.Refs("terrain/texturing/anisotropic.md", [HECKBERT, FELINE, D3D11_FILTER, "Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, \"Real-Time Rendering\", 4th Edition, CRC Press, 2018（テクスチャのフィルタリングの章）"])

# ---------------------------------------------------------------- decals
pg.Dedup("terrain/texturing/decals.md")
pg.Add("terrain/texturing/decals.md", '''
## 地形に貼る、2 つの方法

地形に、道や足跡を重ねる方法は、大きく 2 つに分かれます。

| 方法 | 内容 | 向くもの |
| --- | --- | --- |
| スプラット（地形の素材に塗る） | 重みのマップに、色を塗る。地形の素材の一部として、扱う | 道、小道、広い範囲の足跡の跡 |
| デカール（投影して重ねる） | 地形とは別の、貼り付けるテクスチャを、地形の形に沿って、投影する | 焼け跡、血痕、爆発の跡、魔法陣 |

スプラットは、**素材の重みを書き換える**ので、地形の材質（足音、ぬかるみ）まで、変えられます。デカールは、**地形のデータに触れず**、見た目だけを重ねます。後から消せるので、動的な跡に向きます。

## 道をつくる（スプライン）

道は、**制御点を結んだ曲線（スプライン）**で、定義します。曲線に沿って、3 つのことを行います。

| 作業 | 内容 |
| --- | --- |
| ① スプラットに、塗る | 曲線からの距離で、重みを決める。中心は 1、縁へ向かって、0 に減らす |
| ② 高さマップを、整える | 道の中央を、**地形の高さと、道の高さを混ぜて、平らにする**。道が、斜面を、横切るとき、地面が、凸凹だと、不自然になる |
| ③ 草を、避ける | 道の上には、草や木を、置かない（配置のマスクにも、道を書く） |

```cpp
// 道（スプライン）から、距離に応じた重みを、スプラット マップに塗る。
for (int y = 0; y < height; ++y) {
  for (int x = 0; x < width; ++x) {
    const float2 p = float2(x, y) * texel_size;
    const float d = DistanceToSpline(spline, p);        // 曲線までの最短距離
    const float w = 1.0f - SmoothStep(road_width * 0.4f, road_width * 0.5f, d);
    splat[y][x].road = std::max(splat[y][x].road, w);   // 重みを足し合わせる
  }
}
```

高さの整地は、次の式で、混ぜます。

```text
新しい高さ = lerp(元の高さ, 道の高さ, 整地の重み)
```

整地の重みを、道の幅より、少し広く取ると、**道の両側に、緩やかな、土手**ができて、自然に見えます。

## デカール：ボックスで、投影する

デカールは、**箱（ボリューム）の中に入った、地形の表面だけに、テクスチャを貼る**方式が、標準です（Persson、2011「Volume Decals」）。

```text
 ┌─────────┐  ← デカールの箱。位置・向き・大きさを、持つ
 │ ╲╱╲╱╲╱  │
 │──地形───│  ← 箱の中に入っている、地形の画素だけに、貼られる
 └─────────┘
```

### 手順

1. 箱を描く（立方体のメッシュを、デカールの位置・向き・大きさに変換して描く）
2. ピクセル シェーダーで、**その画素の、ワールド座標を、デプス バッファから復元する**
3. ワールド座標を、**箱のローカル座標に変換**する
4. ローカル座標が、箱の外（`[-0.5, 0.5]` の外）なら、捨てる。中なら、ローカルの XZ を、UV に使って、テクスチャを引く

```hlsl
Texture2D<float> g_depth : register(t0);          // シーンのデプス
Texture2D<float4> g_decal : register(t1);         // デカールのテクスチャ
cbuffer DecalCB : register(b1) {
  float4x4 inv_view_proj;      // クリップ空間 → ワールド
  float4x4 world_to_decal;     // ワールド → デカールのローカル（箱は -0.5〜0.5）
};

float4 main(float4 pos : SV_Position) : SV_Target {
  // ① 画素の、デプスから、ワールド座標を復元する
  float2 uv = pos.xy * inv_screen_size;
  float depth = g_depth.Load(int3(pos.xy, 0));
  float4 ndc = float4(uv * float2(2, -2) + float2(-1, 1), depth, 1);
  float4 world = mul(ndc, inv_view_proj);
  world.xyz /= world.w;

  // ② デカールのローカル座標へ
  float3 local = mul(float4(world.xyz, 1), world_to_decal).xyz;

  // ③ 箱の外なら、捨てる
  clip(0.5 - abs(local));

  // ④ XZ を UV にして、テクスチャを引く
  float2 decal_uv = local.xz + 0.5;
  float4 c = g_decal.Sample(g_linear_clamp, decal_uv);
  return c;   // アルファ ブレンドで、シーンに重ねる
}
```

箱は、**裏面（背面）を描き、デプス テストを無効**にします（カメラが、箱の中に入っても、描画が消えないように）。ブレンドは、`SrcAlpha / InvSrcAlpha` の、アルファ ブレンドです。

### 注意点

| 項目 | 内容 |
| --- | --- |
| 斜面で、引き伸ばされる | 箱の「上から」の投影なので、**急斜面では、デカールが伸びる**。急な場所には、貼らない。法線で、フェードさせる |
| 重ねる数 | デカール 1 枚につき、箱の面積ぶんの、画素処理が増える。数百枚以上は、重くなる |
| 法線・粗さへの影響 | デカールが、色だけでなく、法線・粗さも変える場合は、G バッファに、書き込む（ディファード）か、シェーダーで、直接ライティングに足す |
| 順序 | 重ねる順序が、見た目を、変える。優先度で、並べる |

法線で、デカールの強さを、落とす例です。

```hlsl
// 地形の、傾きが急な場所で、デカールを薄くする。
float3 n = DecodeNormal(g_gbuffer_normal.Load(int3(pos.xy, 0)));
float facing = saturate(dot(n, decal_up_world));
c.a *= smoothstep(0.3, 0.7, facing);
```

## 足跡など、動的な跡

足跡や、タイヤの跡のように、**ゲーム中に増える跡**は、スプラット マップに、直接書き込みます。

| 方法 | 内容 |
| --- | --- |
| 小さなブラシ | 足の位置に、足跡の形のブラシを、スプラット マップ（`RenderTarget`）へ描く |
| 時間で薄くする | 毎フレーム、少しだけ、全体を暗くして、古い跡を消す（[Trampled Grass](../vegetation/trample.md) も同じ仕組み） |
| 窓として持つ | カメラの周りの、**数十メートルだけ**を、跡のマップにする（円環バッファ、クリップマップと同じ発想） |

跡のテクスチャは、`R8_UNORM` 1 枚で十分です（0 = なし、1 = 深い跡）。

''', before="## よくあるミス")
pg.Refs("terrain/texturing/decals.md", [PERSSON, ANDERSSON, "Microsoft Learn, \"HLSL: clip\"（`clip` 関数）"])

# ---------------------------------------------------------------- virtual texture
pg.Dedup("terrain/texturing/virtual-texture.md")
pg.Add("terrain/texturing/virtual-texture.md", '''
## 解きたい問題

広い地形に、場所ごとに違う模様（手描きの道、建物の跡、境目の汚れ）を貼りたいとします。地形が 8 km 四方で、1 m を 4 画素にすると、32,000 × 32,000 画素です。1 画素 4 バイトなら、**4 GB** になります。さらに、近づくと、もっと細かい解像度が欲しくなります。

| 方法 | 問題 |
| --- | --- |
| 全部をメモリに載せる | VRAM が、足りない |
| 繰り返しのテクスチャ（タイル）を使う | 場所ごとの、固有の模様を、描けない |
| 低解像度で、全体を覆う | 近づくと、ぼやける |

仮想テクスチャ（Virtual Texture、VT）は、**巨大なテクスチャを、小さなタイル（ページ）に切って、いま見えている部分だけを、メモリに置く**方式です。CPU の、仮想メモリと、まったく同じ考え方です。

| CPU の仮想メモリ | 仮想テクスチャ |
| --- | --- |
| 仮想アドレス | テクスチャ座標（UV） |
| ページ（4 KB など） | タイル（128×128 画素など） |
| ページ テーブル | ページ テーブル（間接参照のテクスチャ） |
| 物理メモリ | 物理テクスチャ（タイルを置くキャッシュ） |
| ページ フォールト | 足りないタイルの要求 |

## 3 つの部品

### ① フィードバック パス

画面の各画素が、**どのタイルの、どのミップが必要か**を調べます。専用の、小さな解像度（画面の 1/8 など）の描画で、タイルの番号を書き出します。

```hlsl
// フィードバック: 画素ごとに、必要なタイルの番号を書き出す。
float4 FeedbackPS(PSInput input) : SV_Target {
  float2 uv = input.virtual_uv * virtual_size;          // 仮想テクスチャ上の画素座標
  // ミップ レベルを、画素の微分から求める
  float2 dx = ddx(uv);
  float2 dy = ddy(uv);
  float mip = max(0.0, 0.5 * log2(max(dot(dx, dx), dot(dy, dy))) + mip_bias);
  mip = min(floor(mip), max_mip);

  uint2 page = uint2(uv / (tile_size * exp2(mip)));     // このミップでの、タイル番号
  // R, G = タイルの X, Y、B = ミップ、A = 有効フラグ
  return float4(page.x & 255, page.y & 255, mip, 255) / 255.0;
}
```

書き出した画像は、**CPU に読み戻して**（ステージング テクスチャ経由）、重複を除き、「必要なタイルの一覧」を作ります。

```cpp
// 1〜2 フレーム前の結果を読む（GPU を待たせないため、遅延させる）。
context->CopyResource(staging_texture.Get(), feedback_texture.Get());
// 数フレーム後に、Map で読む
D3D11_MAPPED_SUBRESOURCE mapped;
context->Map(old_staging.Get(), 0, D3D11_MAP_READ, 0, &mapped);
// 画素を走査して、必要なタイルの集合を作る
context->Unmap(old_staging.Get(), 0);
```

### ② 物理テクスチャ（キャッシュ）

読み込んだタイルを、置く場所です。1 枚の大きなテクスチャを、**タイル大のスロット**に、分けて使います。

| 項目 | 内容 |
| --- | --- |
| 大きさ | 例：4096×4096 画素 ＝ 128×128 画素のタイル、**1,024 枚** |
| 入れ替え | 足りなくなったら、**最近使われていないタイル（LRU）**を、捨てて、新しいタイルを入れる |
| タイルの内容 | ディスクから読んで展開する、または、**その場で生成する**（スプラットを合成して作る、など） |

タイルを、物理テクスチャに書き込むときは、`UpdateSubresource` や、タイルを描いた小さなレンダー ターゲットから、`CopySubresourceRegion` します。

### ③ ページ テーブル（間接参照）

「仮想の UV」から、「物理テクスチャの、どの位置か」を引く表です。**テクスチャ自体で表現します**（1 画素 ＝ 1 タイル）。

```hlsl
Texture2D<float4> g_page_table : register(t0);   // 各画素が、1 つのタイル。RG = 物理スロットの位置、B = ミップ
Texture2D g_physical : register(t1);             // 物理テクスチャ（タイルのキャッシュ）

float4 SampleVirtual(float2 virtual_uv) {
  // ① ページ テーブルを、点サンプリングで引く（補間しない）
  uint2 table_pos = uint2(virtual_uv * page_table_size);
  float4 entry = g_page_table.Load(int3(table_pos, 0));

  // ② 物理テクスチャ上の、タイルの位置と、タイル内のオフセットを計算する
  float2 tile_pos = entry.xy * 255.0;                    // 物理スロット（タイル単位）
  float scale = exp2(entry.z * 255.0);                   // そのタイルのミップの大きさ
  float2 in_tile = frac(virtual_uv * page_table_size * scale);  // タイルの中の、0〜1 の位置

  // ③ 境界を、少し内側に寄せる（隣のタイルの色が、混ざるのを防ぐ）
  float2 padded = (in_tile * (tile_size - 2 * border) + border) / tile_size_with_border;
  float2 physical_uv = (tile_pos + padded) / physical_tile_count;
  return g_physical.SampleGrad(g_linear_clamp, physical_uv, ddx(virtual_uv * ...), ddy(virtual_uv * ...));
}
```

### 境界の問題（枠）

**バイリニアやトライリニア補間は、隣の画素を読みます。** タイルの端では、隣のタイルが、物理テクスチャの、全然違う場所にあるので、**別のタイルの色が混ざって、継ぎ目の線が見えます**。

対策は、各タイルに、**周りの画素を、数画素ぶん、一緒に持たせる（ボーダー）**ことです。たとえば、128×128 のタイルに、4 画素の枠を付けて、136×136 を、1 スロットとします。異方性フィルタリングを使うなら、枠も、大きく（4 画素以上）します。

## 動き全体の流れ

```text
毎フレーム:
  ① フィードバック パス  → 必要なタイルの一覧を、作る（数フレーム遅れて、CPU に届く）
  ② ストリーミング       → 足りないタイルを、ディスクから読む／その場で生成する
  ③ 物理テクスチャを更新 → タイルを、スロットに、書き込む
  ④ ページ テーブルを更新 → 仮想の位置と、物理スロットを、結びつける
  ⑤ 通常の描画           → SampleVirtual で、テクスチャを引く
```

タイルが、まだ届いていない間は、**粗いミップの、常駐しているタイルで、代用**します。そうすると、画面は、一瞬ぼやけますが、真っ黒や、抜けにはなりません。タイルが届くと、鮮明になります。

!!! note "最も粗いミップは、常に、メモリに置く"
    必ず読み込み済みの、**最も粗い階層**（たとえば、全体が 1 枚のタイルに収まるミップ）を、常駐させておきます。ページ テーブルは、タイルが、まだ無いとき、この常駐したタイルを指します。

## 論文と、実装の例

| 資料 | 内容 |
| --- | --- |
| Barrett、GDC 2008「Sparse Virtual Textures」 | 仮想テクスチャの、基本構成を、整理した発表。ページ テーブルに、アルゴリズムを、シェーダーで書く例 |
| van Waveren、SIGGRAPH 2009 | id Tech 5（RAGE）の実装。ページ テーブルの、更新方法や、圧縮、ストリーミング |
| Mittring、SIGGRAPH 2008 | CryEngine での、仮想テクスチャの、応用（地形、キャラクター） |

id Tech 5 は、**ゲーム全体の地形テクスチャを、固有の絵として**描いて、巨大な仮想テクスチャに入れました。アーティストは、場所ごとに、好きな絵を描けます。代わりに、ディスク容量が、大きくなります。

## ランタイム仮想テクスチャ（RVT）

近年の実装では、**ディスクから、タイルを読む代わりに、その場で、タイルを生成する**方式があります。タイルの中身は、<strong>地形のスプラットと、高さブレンド、デカールを、ブレンドした結果</strong>です。

| 項目 | 内容 |
| --- | --- |
| 生成 | 必要なタイルが、要求されたとき、そのタイルの範囲だけ、地形の素材を、ブレンドして、物理テクスチャに描く |
| 利点 | **画素ごとの、素材の合成（数層ぶんの読み込み）が、描画時に、1 回の読み込みで済む**。デカールも、タイルに焼き込める |
| 欠点 | タイルを作る間は、負荷が、かかる。キャッシュが、足りないと、毎フレーム、作り直しが起きる |
| 向く場面 | 素材の層が多い地形。デカールが多い場面。カメラが、ゆっくり動く場面 |

スプラット（[Splat Weights](weights.md)）の合成は、近景では、1 画素に、数十回のテクスチャ読み込みを、必要とします。RVT は、この処理を、**「タイルを作るときの、1 回だけ」**に、してしまいます。

## 他の方法との比較

| 方式 | 固有の模様 | メモリ | 実装の難しさ |
| --- | --- | --- | --- |
| タイルの繰り返し ＋ スプラット | 素材の組み合わせだけ | 少ない | 易しい |
| 巨大な 1 枚のテクスチャ | 自由 | 巨大 | 易しいが、メモリが足りない |
| 仮想テクスチャ | **自由** | キャッシュの分だけ | 難しい（ページ テーブル、フィードバック、境界、ストリーミング） |
| DirectX 11.2 の Tiled Resources | 自由（ハードウェア対応） | キャッシュの分だけ | やや難しい（ハードウェアが、ページ テーブルの役割を果たす） |

DirectX 11.2 以降の **Tiled Resources**（リザーブド リソース）は、ハードウェアが、**仮想テクスチャの、ページ テーブルを、担当します**。シェーダーの中で、`SampleVirtual` のような、間接参照を書く手間が、なくなります。ただし、対応する GPU と、Windows の組み合わせが、必要です。

''', before="## よくあるミス")
pg.Refs("terrain/texturing/virtual-texture.md", [BARRETT, WAVEREN, MITTRING, "Microsoft Learn, \"Tiled resources\"（Direct3D 11.2 の、ハードウェアによる仮想テクスチャ）"])

pg.Refs("terrain/texturing/index.md", [ANDERSSON, MISHKINIS, GEISS, HEITZ, WAVEREN])
print("ok")
