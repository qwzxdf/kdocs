import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import pg  # noqa: E402

# ---------------------------------------------------------------- texture-streaming.md
pg.Add("../rendering/texture-streaming.md", '''
## 圧縮後の、大きさを計算する

BC 圧縮は、4×4 ピクセルの<strong>ブロック</strong>ごとに、決まったバイト数で保存します。大きさは、計算で出せます。

| 形式 | 1 ブロック（4×4 = 16 ピクセル）のバイト数 | 1 ピクセルあたり |
| --- | --- | --- |
| BC1、BC4 | 8 バイト | 4 ビット（0.5 バイト） |
| BC3、BC5、BC6H、BC7 | 16 バイト | 8 ビット（1 バイト） |
| RGBA8（無圧縮） | — | 32 ビット（4 バイト） |

```cpp
// 圧縮テクスチャの、1 つのミップの大きさ（バイト）。幅・高さは、4 ピクセル単位に、切り上げる。
size_t BlockCompressedSize(uint32_t width, uint32_t height, size_t bytes_per_block) {
  const size_t blocks_x = std::max<size_t>(1, (width + 3) / 4);
  const size_t blocks_y = std::max<size_t>(1, (height + 3) / 4);
  return blocks_x * blocks_y * bytes_per_block;
}

// 全ミップの合計（1×1 まで）。ミップを足すと、元の約 1.33 倍。
size_t TotalMipSize(uint32_t width, uint32_t height, size_t bytes_per_block) {
  size_t total = 0;
  for (;;) {
    total += BlockCompressedSize(width, height, bytes_per_block);
    if (width == 1 && height == 1) break;
    width = std::max(1u, width / 2);
    height = std::max(1u, height / 2);
  }
  return total;
}
// 例: 4096×4096 の BC7（16 バイト/ブロック）→ 約 21 MB。RGBA8 の無圧縮（約 85 MB）の 1/4。
```

## 必要なミップを、決める

ストリーミングの核心は、「<strong>この物体に、どのミップが必要か</strong>」を、決めることです。画面上で、1 ピクセルが、テクスチャの、何テクセルに当たるかで決まります。

```cpp
// 物体の、画面上の大きさから、必要なミップを求める。
// texture_size: テクスチャの 1 辺（テクセル）。uv_density: 物体の 1 メートルあたりの UV の長さ。
float RequiredMip(float texture_size, float uv_density, float distance, float screen_height_px, float fov_y) {
  // 距離 distance での、1 ピクセルが覆う、ワールドの長さ。
  const float meters_per_pixel = 2.0f * distance * std::tan(fov_y * 0.5f) / screen_height_px;
  // 1 ピクセルが、テクスチャの何テクセルに当たるか。
  const float texels_per_pixel = meters_per_pixel * uv_density * texture_size;
  return std::max(0.0f, std::log2(texels_per_pixel));        // 1 テクセル/ピクセルなら、ミップ 0。2 倍で、ミップ 1。
}
```

たとえば、1080p、縦の視野 60°、距離 10 m では、1 ピクセルが約 0.011 m です。1 m に 1 周する、4096 のテクスチャなら、1 ピクセル ≒ 45 テクセルで、ミップは `log2(45) ≈ 5.5`、つまり、<strong>ミップ 5（128×128）以下で足りる</strong>ことになります。

## 予算内で、ミップを割り当てる

必要なミップが決まったら、VRAM の予算内で、<strong>見た目への効きが大きい物から</strong>、高いミップを割り当てます。

```cpp
struct StreamedTexture {
  float required_mip;          // 今、画面で必要なミップ（小さいほど細かい）
  int resident_mip;            // 今、VRAM に置いてあるミップ
  int lowest_mip;              // 常駐させる、最も粗いミップ（読み込みが、間に合わない時の代わり）
  size_t SizeAtMip(int mip) const;   // そのミップ以下を、全部置くときの、大きさ
};

// 毎フレーム（または、数フレームに 1 回）: 予算に収まるよう、各テクスチャの、目標のミップを決める。
void UpdateStreaming(std::vector<StreamedTexture>& textures, size_t budget_bytes) {
  // ① まず、全テクスチャを、最低限のミップ（小さい）にする。
  size_t used = 0;
  for (auto& t : textures) {
    t.target_mip = t.lowest_mip;
    used += t.SizeAtMip(t.target_mip);
  }
  // ② 必要なミップに、近づける。画面で大きい（required_mip が小さい）物から、1 段ずつ、細かくする。
  bool changed = true;
  while (changed) {
    changed = false;
    for (auto& t : SortedByPriority(textures)) {            // 優先: 画面で、大きく映る物から
      const int wanted = static_cast<int>(std::floor(t.required_mip));
      if (t.target_mip <= wanted) continue;                 // すでに、必要な細かさ
      const size_t extra = t.SizeAtMip(t.target_mip - 1) - t.SizeAtMip(t.target_mip);
      if (used + extra > budget_bytes) continue;            // 予算オーバーなら、細かくしない
      --t.target_mip;
      used += extra;
      changed = true;
    }
  }
  // ③ target_mip と resident_mip を比べて、足りない分は、非同期に読み込み、余った分は、解放する。
}
```

予算内で、足りなければ、<strong>遠くや、小さい物の、ミップを下げます</strong>。画面に大きく映る物は、細かいミップが、確保されます。読み込みは、別スレッドで、ディスクから行い、完了したら、`resident_mip` を、更新します。

## ストリーミングの、実装上の、注意

| 注意 | 内容 |
| --- | --- |
| ポップイン | 読み込みが間に合わず、ぼやけた画像から、急に細かい画像に、切り替わる。ミップ バイアスを、徐々に変えて、なじませる |
| ヒステリシス | 境目で、上げ下げを、繰り返すと、読み込みが、止まらない。下げるのは、少し遅らせる |
| 最低ミップの常駐 | 小さいミップ（たとえば 64×64 以下）は、常に VRAM に置いて、読み込みが間に合わないときの、保険にする |
| ミップ チェーンの、ファイル配置 | 小さいミップを、ファイルの先頭に置くと、先に読める。細かいミップだけを、後から、追加で読める |
| 先読み | カメラの移動方向や、場面の切り替えを予測して、事前に、読み込む |

D3D12 には、ミップ単位で、メモリを、確保・解放できる、<strong>予約リソース</strong>（Reserved Resource、タイルド リソース）の機能があり、GPU が、一部のミップだけを、メモリに、持てます。仮想テクスチャの土台でもあります（[Texture Upload](../directx/dx12/texture-upload.md)）。
''', before="## よくあるミス")

# ---------------------------------------------------------------- taa-upscaling.md
pg.Add("../rendering/taa-upscaling.md", '''
## TAA の解決パスを、実装する

履歴を混ぜるパスを、シェーダーで見ます。要点は、<strong>履歴を、そのまま混ぜず、「今の周りの色の範囲」に、収めてから、混ぜる</strong>ことです。これでゴーストを、抑えます（[TAA](../graphics/postprocess/antialiasing/taa.md)）。

```hlsl
Texture2D<float3> g_current : register(t0);       // 今フレームの色（ジッター付き）
Texture2D<float3> g_history : register(t1);       // 前フレームの結果
Texture2D<float2> g_velocity : register(t2);      // 動きベクトル（UV 単位）
SamplerState g_linear_clamp : register(s0);

float3 RgbToYCoCg(float3 c) {                      // 色空間を変えると、クランプが、色味を保ちやすい
  return float3(0.25 * c.r + 0.5 * c.g + 0.25 * c.b, 0.5 * c.r - 0.5 * c.b, -0.25 * c.r + 0.5 * c.g - 0.25 * c.b);
}
float3 YCoCgToRgb(float3 c) {
  return float3(c.x + c.y - c.z, c.x + c.z, c.x - c.y - c.z);
}

float4 PSResolve(float4 pos : SV_Position, float2 uv : TEXCOORD0) : SV_Target {
  const int2 p = int2(pos.xy);

  // ① 今のピクセルと、周りの 3×3 の色から、「今フレームで、ありうる色の範囲」（平均と分散）を求める。
  float3 current = RgbToYCoCg(g_current.Load(int3(p, 0)));
  float3 m1 = 0, m2 = 0;
  [unroll] for (int y = -1; y <= 1; ++y) {
    [unroll] for (int x = -1; x <= 1; ++x) {
      float3 c = RgbToYCoCg(g_current.Load(int3(p + int2(x, y), 0)));
      m1 += c;
      m2 += c * c;
    }
  }
  float3 mean = m1 / 9.0;
  float3 sigma = sqrt(max(m2 / 9.0 - mean * mean, 0.0));
  float3 box_min = mean - 1.25 * sigma;               // 分散クリッピング（Salvi）。1.0〜1.5 が目安
  float3 box_max = mean + 1.25 * sigma;

  // ② 動きベクトルで、前フレームの同じ点を探して、履歴の色を読む。
  float2 velocity = g_velocity.Load(int3(p, 0));
  float3 history = RgbToYCoCg(g_history.SampleLevel(g_linear_clamp, uv - velocity, 0));

  // ③ 履歴を、範囲の中に、収める（範囲の外の履歴は、古い・間違った色なので、引き戻す）。
  history = clamp(history, box_min, box_max);

  // ④ 混ぜる。動きが大きいほど、履歴を、信用しない。
  float motion = length(velocity * float2(1920.0, 1080.0));     // 画素単位の、動きの大きさ
  float history_weight = lerp(0.95, 0.7, saturate(motion / 8.0));
  float3 result = lerp(current, history, history_weight);
  return float4(YCoCgToRgb(result), 1.0);
}
```

数行ずつ見ると、①で「今、ありうる色の範囲」を作り、②で履歴を読み、③で、その範囲に収め、④で、混ぜています。<strong>③のクランプが、ゴースト対策の、要</strong>です。動いた物の、後ろに、古い色が残っても、範囲の外なので、引き戻されます。範囲を、広げる（`1.25` を大きく）と、ゴーストが増え、狭めると、ちらつきが増えます。

## ジッターの、入れ方

```cpp
// Halton 数列（底 2 と 3）で、サブピクセルのずらしを作る。8 フレームで、1 周。
float Halton(int index, int base) {
  float result = 0.0f;
  float f = 1.0f;
  while (index > 0) {
    f /= base;
    result += f * (index % base);
    index /= base;
  }
  return result;
}

DirectX::XMFLOAT2 JitterOffset(int frame, int width, int height) {
  const int i = (frame % 8) + 1;
  // -0.5〜0.5 ピクセルを、NDC（-1〜1）の単位に直す（1 ピクセル = 2/width）。
  return {(Halton(i, 2) - 0.5f) * 2.0f / width, (Halton(i, 3) - 0.5f) * 2.0f / height};
}
// 射影行列の _31, _32 に、ずらしを入れる（符号の理由は、TAA のページ）。速度の計算では、ジッターを、引いて使う。
```

## 動的解像度の、制御

GPU 時間を測って、次のフレームの、解像度を決めます。

```cpp
// 目標の GPU 時間（たとえば 60 FPS なら 14 ms）に、近づけるよう、解像度の倍率を、少しずつ、動かす。
class DynamicResolution {
 public:
  float Update(float gpu_ms) {
    const float target_ms = 14.0f;
    const float error = (target_ms - gpu_ms) / target_ms;     // 速すぎれば正、遅すぎれば負
    scale_ += error * 0.1f;                                    // 少しずつ動かす（急に変えると、ちらつく）
    scale_ = std::clamp(scale_, 0.6f, 1.0f);                   // 60%〜100%
    return scale_;
  }

 private:
  float scale_ = 1.0f;
};
// 使い方: 解像度 = 出力解像度 × scale。ピクセル数は scale² に比例して減るので、scale 0.7 でも、約半分。
```

ピクセル数は、<strong>倍率の 2 乗</strong>で減ります（0.7 倍なら 0.49 倍）。そのため、少しの倍率の変化で、GPU 時間が、大きく変わります。UI は、出力解像度のまま描き、3D の結果だけを、拡大して重ねます。

## アップスケーラに、渡すもの

DLSS・FSR・XeSS などは、TAA と同じ入力を、必要とします。

| 入力 | 内容 |
| --- | --- |
| 低解像度の色 | ジッター付きで描いた、HDR の色（トーン マッピング前） |
| 深度 | 低解像度の深度（逆 Z が多い） |
| 動きベクトル | 低解像度、または出力解像度。ジッターを、含まない |
| ジッターの値 | そのフレームで、入れたずらし（ピクセル単位） |
| 露出 | 露出の値（明るさの変化を、正しく扱うため） |
| リセット フラグ | カットシーンの切り替えなど、履歴が使えないとき |

動きベクトルが、不正確（スキニングや、パーティクルが、出ていない）と、アップスケーラの結果にも、ゴーストが出ます。<strong>エンジン側で、正しい入力を、そろえることが、品質の、ほとんど全て</strong>です。
''', before="## よくあるミス")
print("ok")
