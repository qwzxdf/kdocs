---
title: アップサンプル
tags:
  - 描画
---

# アップサンプル

**AO は、半解像度（または 1/4）で計算する**と**コストが大きく減ります**が、**フル解像度に戻すとき、単純な拡大では、エッジがにじみます**。**フル解像度の深度を見ながら、近い深度の低解像度サンプルだけを重く混ぜる「深度を考慮したアップサンプル」**が**必要**です。このページでは、**低解像度で計算する理由・深度を見るアップサンプル・実装**を説明します。

!!! tip "ポイント"
    - **低解像度で AO を計算**し、**コストを 1/4**。
    - **拡大時に、フル解像度の深度**と**低解像度の深度**を**比べ、近いものを重く**。
    - **単純なバイリニアは、エッジで AO がにじむ**。
    - **ジョイント バイラテラル アップサンプル**と呼ばれる。

## アップサンプル：低解像度から戻す
AO は<strong>低周波（なめらか）</strong>なので**半分や 1/4 の解像度**で計算して、**拡大**すると**コストを大きく減らせます**（[低解像度のエフェクト](../../../rendering/low-res-effects.md)）。しかし、**単純なバイリニア拡大**は、**境界でにじみます**。

### ジョイント バイラテラル アップサンプル

**拡大先（フル解像度）の深度**と**低解像度の深度**を**比べて**、**近い深度の低解像度の画素**を、重みを大きくして混ぜます。

| 手順 | 内容 |
| --- | --- |
| **① フル解像度の画素の深度** | 拡大先の各画素の深度 `z_full` |
| **② 周りの低解像度画素（2×2）の深度** | `z_low_i` |
| **③ 重みを計算** | `w_i = 双線形の重み × 1 / (ε + \|z_full − z_low_i\|)` |
| **④ 混ぜる** | `AO = Σ w_i · AO_low_i / Σ w_i` |

```hlsl
float UpsampleAO(float2 uv_full) {
  float z_full = LinearDepth(uv_full);
  float2 low_pos = uv_full * low_size - 0.5;
  float2 f = frac(low_pos);
  int2 base = int2(floor(low_pos));

  float sum = 0.0;
  float weight_sum = 0.0;
  [unroll] for (int y = 0; y < 2; ++y) {
    [unroll] for (int x = 0; x < 2; ++x) {
      int2 p = base + int2(x, y);
      float w = (x == 0 ? 1.0 - f.x : f.x) * (y == 0 ? 1.0 - f.y : f.y);
      w *= 1.0 / (0.001 + abs(z_full - low_depth_tex.Load(int3(p, 0)).r));
      sum += ao_low_tex.Load(int3(p, 0)).r * w;
      weight_sum += w;
    }
  }
  return sum / weight_sum;
}
```

| 点 | 説明 |
| --- | --- |
| **低解像度の深度を別途用意** | AO を計算したときの深度（縮小した深度）を保持しておく |
| <strong>「最も近い深度」を選ぶ方式</strong> | 深度が最も近い 1 画素だけを選ぶ（シャープだが階段状になりやすい） |
| **ハローの防止** | 境界で**低解像度の画素が別の面の AO を持つ**のを防ぐ |

## よくあるミス

??? failure "バイリニアで拡大して、物の輪郭に暗いにじみが出る"
    **深度を見るアップサンプル**にする。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **低解像度で計算 ＋ 深度を見て拡大**
    - [x] **エッジのにじみを防ぐ**

## 参考

- Mittring, "Finding Next Gen: CryEngine 2"（SIGGRAPH 2007）
- Jimenez et al., "Practical Real-Time Strategies for Accurate Indirect Occlusion"（SIGGRAPH 2016）

## 関連ページ

- [AO のフィルタ](index.md)
- [バイラテラル ブラー](bilateral-blur.md)
- [典型のパイプライン](pipeline.md)
