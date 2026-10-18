import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import pg  # noqa: E402

# ---------------------------------------------------------------- 2d.md
pg.Add("../rendering/2d.md", '''
## スプライト バッチを、実装する

スプライトを、1 枚ずつ描かず、<strong>1 つの動的な頂点バッファに、溜めて、1 回で描く</strong>仕組みです。

```cpp
struct SpriteVertex {
  DirectX::XMFLOAT2 position;     // 画面上の位置（ピクセル）
  DirectX::XMFLOAT2 uv;           // アトラス上の位置（0〜1）
  uint32_t color;                 // RGBA8
};

class SpriteBatch {
 public:
  void Begin() { vertices_.clear(); }

  // 1 枚のスプライトを、4 頂点の四角形として溜める（まだ描かない）。
  void Draw(float x, float y, float w, float h, float u0, float v0, float u1, float v1, uint32_t color) {
    vertices_.push_back({{x, y}, {u0, v0}, color});               // 左上
    vertices_.push_back({{x + w, y}, {u1, v0}, color});           // 右上
    vertices_.push_back({{x + w, y + h}, {u1, v1}, color});       // 右下
    vertices_.push_back({{x, y + h}, {u0, v1}, color});           // 左下
  }

  // 溜めた分を、1 回で描く。インデックスは、起動時に作った固定のもの（0,1,2, 0,2,3 の繰り返し）。
  void End(ID3D11DeviceContext* context) {
    if (vertices_.empty()) return;
    D3D11_MAPPED_SUBRESOURCE mapped;
    context->Map(vertex_buffer_.Get(), 0, D3D11_MAP_WRITE_DISCARD, 0, &mapped);
    std::memcpy(mapped.pData, vertices_.data(), vertices_.size() * sizeof(SpriteVertex));
    context->Unmap(vertex_buffer_.Get(), 0);
    context->DrawIndexed(static_cast<UINT>(vertices_.size() / 4 * 6), 0, 0);   // 全スプライトを 1 回で
  }

 private:
  std::vector<SpriteVertex> vertices_;
  Microsoft::WRL::ComPtr<ID3D11Buffer> vertex_buffer_;     // DYNAMIC。最大スプライト数 × 4 頂点
};
```

インデックス バッファは、四角形ごとの規則的な並びなので、起動時に最大数ぶんを、1 回だけ作ります（[Index Buffer](../directx/dx11/index-buffer.md)）。頂点バッファは、`WRITE_DISCARD` で、毎フレーム書き直します（[Map, Unmap and UpdateSubresource](../directx/dx11/map-update.md)）。

### ソート：描画順とバッチを両立する

アルファ ブレンドの、2D は、<strong>奥から手前</strong>の順に描く必要があります。同時に、同じアトラス（テクスチャ）を、続けて描けば、バッチが、切れません。

```cpp
// レイヤー（奥行き）を第 1 キー、テクスチャを第 2 キーにして、並べ替える。
std::sort(sprites.begin(), sprites.end(), [](const Sprite& a, const Sprite& b) {
  if (a.layer != b.layer) return a.layer < b.layer;          // 奥のレイヤーから
  return a.texture_id < b.texture_id;                        // 同じレイヤーの中では、同じアトラスを連続させる
});
// テクスチャが変わるたびに、いったん End してバッチを区切り、次のテクスチャで再開する。
```

アトラスに、できるだけ、全スプライトを入れておくと、テクスチャの切り替え（バッチの区切り）が、ほとんど、なくなります。

## アトラスの、作り方と、にじみ

複数の画像を、1 枚の、アトラスに詰めると、バッチが切れません。ただし、<strong>隣の画像の、端の色が、にじむ</strong>問題が起きます。

| 問題 | 原因 | 対策 |
| --- | --- | --- |
| 画像の縁に、隣の画像の線が出る | バイリニア補間が、縁で、隣のテクセルを混ぜる | 各画像の周りに、<strong>1〜2 ピクセルの余白</strong>を取り、縁の色を、外側へ、引き伸ばして、埋める（エクストルード） |
| 遠くで縮小すると、にじむ | ミップが、隣の画像と混ざる | ミップを使うなら、余白を、ミップの段数に合わせて、増やす。2D は、ミップを使わないことが多い |
| ドット絵が、ぼやける | バイリニア補間 | `POINT` サンプラーで読む（[Sampler State](../directx/dx11/sampler-state.md)） |

ドット絵の、ゲームでは、サンプラーを `MIN_MAG_MIP_POINT` にし、表示の倍率を、<strong>整数倍</strong>（2 倍、3 倍）にそろえると、ぼやけず、くっきり見えます。

## タイルマップを、チャンクにする

広いマップを、タイル 1 枚ずつ、描くと、ドロー コールが、爆発します。<strong>16×16 タイルほどの、かたまり（チャンク）ごとに、1 つの頂点バッファ</strong>を作り、変更があったときだけ、作り直します。

```cpp
constexpr int kChunkSize = 16;

struct Chunk {
  std::vector<SpriteVertex> vertices;       // このチャンクの全タイルの頂点（作り直すまで、使い回す）
  bool dirty = true;                        // タイルが変わったら true
};

void RebuildChunk(Chunk& chunk, const TileMap& map, int cx, int cy) {
  chunk.vertices.clear();
  for (int y = 0; y < kChunkSize; ++y) {
    for (int x = 0; x < kChunkSize; ++x) {
      int tile = map.Get(cx * kChunkSize + x, cy * kChunkSize + y);
      if (tile == kEmpty) continue;                          // 空のタイルは、頂点を作らない
      AddTileQuad(chunk.vertices, x, y, tile);               // アトラスの、タイルの UV で、四角形を足す
    }
  }
  chunk.dirty = false;
}

// 描画: カメラの範囲に入るチャンクだけを描く。
for (int cy = first_y; cy <= last_y; ++cy) {
  for (int cx = first_x; cx <= last_x; ++cx) {
    Chunk& chunk = chunks[cy][cx];
    if (chunk.dirty) RebuildChunk(chunk, map, cx, cy);
    Submit(chunk);
  }
}
```

画面に入るチャンクは、数枚〜数十枚なので、1 画面で、数十回のドロー コール（さらに、1 つのバッファにまとめれば 1 回）で済みます。透明な、空のタイルの頂点を作らないので、<strong>オーバードローも減ります</strong>。
''', before="## よくあるミス")

# ---------------------------------------------------------------- particles.md
pg.Add("../rendering/particles.md", '''
## 半透明が、どれだけ重いか：数字で見る

1920×1080 は、約 207 万ピクセルです。画面全体を、覆う半透明を、10 枚重ねると、どれだけのピクセルを、ブレンドするでしょうか。

```text
ブレンドするピクセル数 ＝ 207 万 × 10 枚 ＝ 約 2,070 万ピクセル / フレーム

1 ピクセルのブレンド（RGBA16F のレンダー ターゲット）:
  読む 8 バイト + 書く 8 バイト ＝ 16 バイト
帯域 ＝ 2,070 万 × 16 バイト ≒ 330 MB / フレーム
60 FPS なら ≒ 20 GB/s
```

20 GB/s は、GPU の帯域の、数%〜十数%に、当たります（GPU による）。<strong>1 つの煙の演出だけで</strong>、これだけ使います。半分の解像度で描けば、ピクセル数が 1/4 になり、帯域も、約 5 GB/s に、減ります。

## 縮小バッファに描いて、合成する

煙のような、ぼんやりした物は、半分の解像度で描いて、最後に、フル解像度へ重ねます。

```cpp
// ① 半分の解像度の、レンダー ターゲットと、縮小した深度（深度テスト用）を用意する。
SetViewport(width / 2, height / 2);
context->OMSetRenderTargets(1, half_rtv.GetAddressOf(), half_depth_dsv.Get());
Clear(half_rtv, {0, 0, 0, 0});                                    // 透明な黒で、クリア

// ② 半透明のパーティクルを、ここに描く（プリマルチプライド アルファ）。
DrawParticles();

// ③ フル解像度のシーンに、重ねて合成する。
SetViewport(width, height);
context->OMSetRenderTargets(1, scene_rtv.GetAddressOf(), nullptr);
context->PSSetShaderResources(0, 1, half_srv.GetAddressOf());
DrawFullscreenTriangle();                                         // 合成シェーダー（下）
```

```hlsl
// ③ の合成シェーダー: 縮小バッファ（rgb は色、a は、後ろを、どれだけ隠すか）を、バイリニアで、拡大して重ねる。
Texture2D g_particles : register(t0);
SamplerState g_linear : register(s0);

float4 PSComposite(float4 pos : SV_Position, float2 uv : TEXCOORD0) : SV_Target {
  float4 p = g_particles.Sample(g_linear, uv);                    // プリマルチプライド（色に、アルファが掛け済み）
  return p;                                                       // ブレンド: ONE, INV_SRC_ALPHA で、シーンに重ねる
}
```

縮小して描くと、物体の縁で、煙が、にじみます（低解像度の深度が、縁を、またぐため）。縁が気になるときは、<strong>深度を考慮した拡大</strong>（フル解像度の深度と、近い縮小の深度を、比べて、似た位置の値だけを、混ぜる）にします（[Upsampling](../graphics/ao/filtering/upsample.md) と同じ考え方）。

## GPU パーティクルを、実装する

粒子が数万を超えるなら、<strong>計算シェーダーで、粒子を更新し、そのまま描く</strong>のが、効率的です。

```hlsl
struct Particle {
  float3 position;
  float life;                // 残りの寿命（秒）。0 以下で、死ぬ
  float3 velocity;
  float size;
};

RWStructuredBuffer<Particle> g_particles : register(u0);
AppendStructuredBuffer<uint> g_alive_list : register(u1);        // 今フレーム、生きている粒子の番号

cbuffer UpdateCB : register(b0) {
  float g_dt;
  float3 g_gravity;
  uint g_particle_count;
};

[numthreads(64, 1, 1)]
void UpdateCS(uint3 id : SV_DispatchThreadID) {
  if (id.x >= g_particle_count) return;
  Particle p = g_particles[id.x];
  if (p.life <= 0.0) return;                                       // 死んでいる粒子は、飛ばす

  p.velocity += g_gravity * g_dt;
  p.position += p.velocity * g_dt;
  p.life -= g_dt;
  g_particles[id.x] = p;
  if (p.life > 0.0) g_alive_list.Append(id.x);                     // 生きている粒子の番号を、追加
}
```

```cpp
// 更新: 生きている粒子のリスト（Append バッファ）を、毎フレーム空にして、作り直す。
UINT zero = 0;
context->CSSetUnorderedAccessViews(1, 1, alive_uav.GetAddressOf(), &zero);   // カウンターを 0 に
context->Dispatch((max_particles + 63) / 64, 1, 1);

// 描画: 生きている粒子の数を、間接描画の引数へコピーして、CPU に戻さず、描く。
context->CopyStructureCount(draw_args_buffer.Get(), sizeof(UINT), alive_uav.Get());   // InstanceCount の位置へ
context->DrawInstancedIndirect(draw_args_buffer.Get(), 0);        // 4 頂点（四角形）× 生きている数
```

頂点シェーダーは、`SV_InstanceID` で、`g_alive_list` から粒子の番号を引き、`SV_VertexID` で、四角形の 4 隅を作って、カメラの方を向けます（ビルボード）。<strong>CPU は、粒子の生成の指示を送るだけで、更新も、描画の数の決定も、GPU が行います</strong>（[Structured and Raw Buffers](../directx/dx11/structured-buffer.md)、[Instanced Drawing](../directx/dx11/instancing-draw.md)）。
''', before="## よくあるミス")

# ---------------------------------------------------------------- postprocess.md
pg.Add("../rendering/postprocess.md", '''
## 帯域を、パスの数で、計算する

1920×1080 の画像 1 枚は、フォーマットで、大きさが変わります。1 パスは、「入力を読み、出力を書く」ので、2 枚ぶんです。

| フォーマット | 1 枚の大きさ | 1 パス（読み + 書き） | 60 FPS、10 パス |
| --- | --- | --- | --- |
| RGBA16F（8 バイト） | 約 16.6 MB | 約 33 MB | 約 20 GB/s |
| R11G11B10F（4 バイト） | 約 8.3 MB | 約 17 MB | 約 10 GB/s |
| RGBA8（4 バイト） | 約 8.3 MB | 約 17 MB | 約 10 GB/s |

フォーマットを、半分にすれば、帯域も、半分です。<strong>パスを 10 から 3 に</strong>減らせば、帯域は、さらに、約 3 分の 1 です。両方で、約 1/6 になります。

## 最終パスを、1 つにまとめる

トーン マッピング、カラー グレーディング（LUT）、ビネット、フィルム グレインを、<strong>1 つのパス</strong>で行います。入力を読むのは、1 回だけです。

```hlsl
Texture2D<float3> g_scene : register(t0);                     // HDR のシーン
Texture3D<float3> g_lut : register(t1);                       // カラー グレーディングの 3D LUT（32³）
Texture2D<float> g_bloom : register(t2);
SamplerState g_linear_clamp : register(s0);

cbuffer FinalCB : register(b0) {
  float g_exposure;
  float g_vignette_strength;
  float g_grain_strength;
  float g_time;
};

float3 TonemapAces(float3 x) {                                // ACES の近似（Narkowicz）
  return saturate((x * (2.51 * x + 0.03)) / (x * (2.43 * x + 0.59) + 0.14));
}

float4 PSFinal(float4 pos : SV_Position, float2 uv : TEXCOORD0) : SV_Target {
  float3 color = g_scene.Load(int3(pos.xy, 0));               // ① 読むのは、ここ 1 回
  color += g_bloom.Sample(g_linear_clamp, uv);                // ブルームを足す（HDR のうちに）
  color *= g_exposure;                                        // 露出
  color = TonemapAces(color);                                 // トーン マッピング（HDR → LDR）

  // カラー グレーディング: LUT を引く。LUT の端に、半テクセルの余白を足して、補間の誤差を避ける。
  float3 lut_uv = color * (31.0 / 32.0) + 0.5 / 32.0;
  color = g_lut.SampleLevel(g_linear_clamp, lut_uv, 0);

  // ビネット: 画面の端を暗く。
  float2 d = uv - 0.5;
  color *= 1.0 - g_vignette_strength * dot(d, d) * 2.0;

  // フィルム グレイン: 軽いノイズを足す（LDR のうちに）。
  float noise = frac(sin(dot(pos.xy + g_time, float2(12.9898, 78.233))) * 43758.5453) - 0.5;
  color += noise * g_grain_strength;

  return float4(color, 1.0);                                  // ② 書くのは、ここ 1 回
}
```

数行ずつ見ると、<strong>読み込み（①）が 1 回、書き込み（②）が 1 回</strong>です。個別のパスで行うと、4 回の読み書き（約 130 MB）になる所が、1 回（約 33 MB）に減ります。ALU の計算（ACES、LUT の補間、ビネット）は、安いので、<strong>計算を足して、パスを減らす</strong>ほうが、得です（[Tone Mapping and Exposure](../graphics/postprocess/tonemapping/index.md)、[3D LUT](../graphics/postprocess/color-grading/lut-3d.md)）。

## ガウスぼかしを、バイリニアで、半分の回数に

分離可能な、ガウスぼかしは、横 1 回 + 縦 1 回に分けて、サンプルを、N 回にできます。さらに、<strong>テクセルの間を、バイリニアで読む</strong>と、1 回の読み込みで、2 つのテクセルぶんが、得られ、回数が、ほぼ半分になります。

```hlsl
// 9 タップのガウス（横方向）を、5 回の読み込みで行う。重みとオフセットは、バイリニアで 2 点分を、1 回にまとめた値。
static const float kOffsets[3] = {0.0, 1.3846153846, 3.2307692308};
static const float kWeights[3] = {0.2270270270, 0.3162162162, 0.0702702703};

float3 BlurHorizontal(Texture2D<float3> src, SamplerState linear_clamp, float2 uv, float2 texel) {
  float3 color = src.SampleLevel(linear_clamp, uv, 0) * kWeights[0];
  for (int i = 1; i < 3; ++i) {
    float2 offset = float2(kOffsets[i] * texel.x, 0.0);
    color += src.SampleLevel(linear_clamp, uv + offset, 0) * kWeights[i];
    color += src.SampleLevel(linear_clamp, uv - offset, 0) * kWeights[i];
  }
  return color;
}
```

重みの合計は `0.2270 + 2 × (0.3162 + 0.0703) ≈ 1.0` です。9 タップが、5 回の読み込みで済みます（[Gaussian Blur](../graphics/postprocess/bloom/gaussian.md)）。さらに、<strong>縮小してから、ぼかす</strong>と、ピクセル数が 1/4 になり、同じ見た目で、数倍速くなります。
''', before="## よくあるミス")

# ---------------------------------------------------------------- shadows.md
pg.Add("../rendering/shadows.md", '''
## 影のコストを、数字で見積もる

影マップは、シーンを、もう一度描くので、コストの目安は、「影用の描画 ＝ 見える物の、頂点とドロー コール × 光源の数」です。

| 構成 | 描画の追加 |
| --- | --- |
| 太陽（CSM、4 枚） | カスケードごとに、シーンを再描画 → <strong>約 4 倍</strong>のドロー コール（カリングで、かなり減る） |
| 点光源 1 個（キューブ） | 6 面 → 約 6 倍 |
| スポットライト 1 個 | 1 枚 → 約 1 倍 |
| 影つきのライト 10 個（点光源） | 60 面 → <strong>非常に重い</strong> |

カスケードと光源ごとに、<strong>光の視錐台でカリング</strong>すると、実際に描く量は、大きく減ります（[カリング](culling.md)）。

## カスケードの分割と、ちらつきの防止

### 分割の位置：実用分割

カメラの手前を細かく、奥を粗く分けます。対数分割と線形分割の、中間（実用分割）が、よく使われます。

```cpp
// 各カスケードの境目（カメラからの距離）を、実用分割で求める。lambda: 0 で線形、1 で対数。0.5〜0.9 が実用的。
std::array<float, kCascadeCount + 1> SplitDistances(float near_z, float far_z, float lambda) {
  std::array<float, kCascadeCount + 1> d;
  for (int i = 0; i <= kCascadeCount; ++i) {
    const float p = static_cast<float>(i) / kCascadeCount;
    const float log_split = near_z * std::pow(far_z / near_z, p);       // 対数: 手前を細かく
    const float lin_split = near_z + (far_z - near_z) * p;              // 線形: 均等
    d[i] = lambda * log_split + (1.0f - lambda) * lin_split;
  }
  return d;
}
```

例えば、`near = 0.1`、`far = 200`、4 分割、`lambda = 0.8` なら、境目は、約 0.1、5、24、72、200 m と、手前ほど細かくなります（数値は目安）。

### テクセル スナップ：カメラが動いても、影がちらつかない

カスケードの範囲が、カメラの動きに合わせて、連続的に動くと、影マップの、テクセルの境目が、毎フレーム、ずれて、影の縁が、ちらつきます。<strong>範囲の中心を、1 テクセルの大きさの倍数に、そろえて</strong>動かします。

```cpp
// 光の空間で、カスケードの中心を、影マップの 1 テクセルの大きさの倍数に切り捨てる。
// radius: カスケードを囲む球の半径（回転しても、大きさが変わらないよう、球で囲む）。
const float world_units_per_texel = (2.0f * radius) / shadow_map_size;
center_light_space.x = std::floor(center_light_space.x / world_units_per_texel) * world_units_per_texel;
center_light_space.y = std::floor(center_light_space.y / world_units_per_texel) * world_units_per_texel;
```

範囲を、カメラの向きで回転する四角形ではなく、<strong>球</strong>で囲んでおくと、カメラを回しても、範囲の大きさが、変わらず、スナップが、有効になります（[Aliasing and Stabilization](../graphics/shadows/shadow-map-basics/aliasing-stabilize.md)）。

## 静的な影を、キャッシュする

動かない物（地形、建物）の影は、毎フレーム、描き直す必要がありません。<strong>静的な影マップを、1 度作って、使い回し</strong>、動く物だけを、毎フレーム、足します。

```cpp
// 静的な影マップ（建物・地形）は、光が動いたとき、または、静的な物が、変わったときだけ、描き直す。
if (light_moved || static_changed) {
  RenderShadow(static_shadow_map, static_casters);
}
// 毎フレーム: 静的な影マップを、動的な影マップにコピーして、動く物だけを、上から描く。
context->CopyResource(dynamic_shadow_map.Get(), static_shadow_map.Get());
RenderShadow(dynamic_shadow_map, dynamic_casters);
```

太陽が、ゆっくり動くゲームでは、静的な影を、数秒に 1 回だけ、更新するのが一般的です。コピーの帯域は、かかりますが、シーン全体の再描画（頂点とドロー コール）より、はるかに、安く済みます（遠いカスケードは、さらに、頻度を落とす）。
''', before="## よくあるミス")
print("ok")
