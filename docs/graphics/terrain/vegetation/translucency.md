---
title: Foliage Translucency
tags:
  - 描画
---

# Foliage Translucency

**葉は、ソートできないほど多いので、通常の半透明は使えません**。**アルファ テスト・Alpha to Coverage・ハッシュド アルファ**で**対処**します。このページでは、**葉の半透明の問題と対策**を説明します。

!!! tip "ポイント"
    - **半透明ブレンドは、ソートが必要で、葉には不向き**。
    - **アルファ テストで、切り抜く**。
    - **遠くで細る問題は、アルファの補正で対処**。
    - **A2C やハッシュドで、縁をなめらかに**。

## 半透明の問題
**草と葉はアルファ テスト（切り抜き）で描きます**。**半透明ブレンドは、ソートが要るので不向き**です。

半透明の問題と対策です。ジャギーには、A2C と MSAA、または TAA で滑らかにします。遠くで草が痩せる問題は、ミップでアルファが薄まるためで、ミップごとにアルファを補正します（[Alpha Testing](../../translucency/alpha-test/index.md)）。裏面が暗い、または明るい問題は、両面描画で裏面の法線を反転し、葉の透過光を足します。

## 半透明が、使えない理由

草や木の葉は、**輪郭が、細かい**ので、**テクスチャの、アルファ（透明度）**で、形を切り抜きます。ここで、**半透明のブレンド**を使うと、次の問題が起きます。

| 問題 | 内容 |
| --- | --- |
| ソートが要る | 半透明は、**奥から手前の順**に描かないと、正しく、混ざらない。数百万本を、ソートできない |
| 深度を書かない | 半透明は、深度バッファに、書かない。**隣の草との、前後関係**が、おかしくなる |
| 重い | 画素ごとの、ブレンドは、メモリ帯域を使う。草は、画面全体に、重なる |

そこで、**アルファ テスト（切り抜き）**を使います。**アルファが、しきい値より小さい画素は、捨てる**だけで、深度も、書けて、ソートも要りません。

```hlsl
float alpha = g_albedo.Sample(g_linear_wrap, input.uv).a;
clip(alpha - 0.5);                // アルファが 0.5 未満の画素は、捨てる
```

## アルファ テストの、問題

### ① 縁が、ギザギザになる

アルファ テストは、**画素ごとに、残すか捨てるかを決める**ので、縁が、**ジャギー**になります。**MSAA の、効果も、出ません**（シェーダー内の、`clip` は、1 画素ごとの結果で、サブサンプルごとには、決まらない）。

| 対策 | 内容 |
| --- | --- |
| Alpha to Coverage | アルファの値を、**MSAA の、カバレッジ（サブサンプルの、何個を、描くか）に変換**する。縁が、なめらか（[Alpha to Coverage](../../translucency/alpha-test/alpha-to-coverage.md)） |
| TAA | 時間方向に、平均する。ジャギーが、ならされる（[TAA](../../postprocess/antialiasing/taa.md)） |
| ハッシュ アルファ | 画素ごとに、**ランダムな**しきい値で、判定する。**時間方向に、平均すると**、半透明に、見える（[Hashed Alpha](../../translucency/alpha-test/hashed-alpha.md)、Wyman と McGuire、2017） |

### ② 遠くで、葉が、痩せて見える

テクスチャの**ミップマップ**で、アルファを、**平均して縮める**と、**遠くのミップで、アルファの値が、小さくなります**。しきい値（0.5）を、下回る画素が、増えて、**葉が、スカスカになります**。

| 距離 | ミップ | アルファの平均 | 0.5 以上の画素の割合 |
| --- | --- | --- | --- |
| 近い | 0 | 元のまま | 元の割合（たとえば、60%） |
| 中くらい | 2 | ぼける | 40% |
| 遠い | 4 | さらに、ぼける | 10% |

葉の、**見た目の面積が、距離で、小さくなる**のです。

**対策：ミップごとに、アルファを、補正**します（Castaño、2010）。

| 手順 | 内容 |
| --- | --- |
| ① ミップ 0 で、**しきい値以上の画素の割合**（カバレッジ）を求める | たとえば、60% |
| ② 各ミップで、**カバレッジが、同じ 60%** になるように、アルファに、**スケール**を掛ける | ミップ 4 で、元の 60% を、保つ |
| ③ スケールを、ミップごとに、保存する | ミップ作成の、前処理で、行う |

```cpp
// ミップごとに、アルファを、補正して、カバレッジを保つ（前処理の例）。
float ComputeCoverage(const std::vector<float>& alpha, float threshold, float scale) {
  size_t covered = 0;
  for (float a : alpha) if (a * scale > threshold) ++covered;
  return float(covered) / float(alpha.size());
}

// 二分探索で、カバレッジが、目標（ミップ 0 の値）に、一致する scale を探す。
float FindAlphaScale(const std::vector<float>& mip_alpha, float threshold, float target_coverage) {
  float lo = 0.0f, hi = 8.0f;
  for (int i = 0; i < 20; ++i) {
    const float mid = 0.5f * (lo + hi);
    if (ComputeCoverage(mip_alpha, threshold, mid) < target_coverage) lo = mid; else hi = mid;
  }
  return 0.5f * (lo + hi);
}

// 全ミップに、適用する。
for (int level = 1; level < mip_count; ++level) {
  const float scale = FindAlphaScale(mips[level].alpha, 0.5f, coverage_at_mip0);
  for (float& a : mips[level].alpha) a = std::min(a * scale, 1.0f);
}
```

ミップを作る、**ツールの段階**で、行います。実行時の、シェーダーでは、普通に、ミップを読むだけです。

### ③ 距離で、シェーダー側で補う

ツールで、作り直せない、既存のテクスチャには、**シェーダーで、距離に応じて、しきい値を、下げる**方法も、あります。

```hlsl
// ミップが進むほど、しきい値を下げる（簡易な補正）。
float mip = g_albedo.CalculateLevelOfDetail(g_linear_wrap, input.uv);
float threshold = lerp(0.5, 0.25, saturate(mip / 4.0));
clip(alpha - threshold);
```

簡単ですが、**ミップごとの、アルファの分布が、画像によって違う**ので、前処理の補正（②）より、精度が劣ります。

## 薄い、植生（草）の、アルファ

草は、**形を、ジオメトリ（細い三角形の帯）**で、表現するなら、**アルファが、要りません**。三角形の縁が、そのまま、草の形になるので、アルファ テストの、問題がなくなります。

| 方式 | アルファ | 縁 |
| --- | --- | --- |
| クロス板 ＋ 草の絵 | **要る**（アルファで切り抜く） | アルファ テスト。ミップの補正が必要 |
| 1 本ずつの、細い帯 | 要らない | **ジオメトリの縁**。MSAA で、なめらか。ただし、遠くで、細すぎて、消える |

細い帯の、**遠くでの、細さ**（1 画素より細いと、消える）には、**幅の、下限**を設けます（[Grass Shape](grass-shape.md)）。

## 木の葉

木の葉は、**カード（板に、葉の絵）**で、表現します。アルファ テストで、**葉の形を、切り抜きます**。

| 項目 | 内容 |
| --- | --- |
| 葉の描画 | アルファ テスト ＋ Alpha to Coverage |
| 影 | アルファ テストで、**影も、切り抜く**（[Alpha-Tested Shadows](../../shadows/special-cases/alpha-test-shadows.md)） |
| 遠景（インポスター） | 木全体を、1 枚の絵（板）に。アルファ テスト、またはディザで、フェード（[Trees](trees.md)） |
| LOD の、切り替え | ディザ フェード（市松の、ディザ パターンで、2 つの LOD を、混ぜる） |

## よくあるミス

??? failure "遠くの木の葉が、スカスカに見える"
    **ミップごとにアルファを補正**する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **葉は、アルファ テスト系で処理**

## 参考

- Castaño, "Computing Alpha Mipmaps", 2010（ミップごとに、アルファを補正する）
- Wyman, McGuire, "Hashed Alpha Testing", Symposium on Interactive 3D Graphics and Games 2017
- Sousa, "Vegetation Procedural Animation and Shading in Crysis", GPU Gems 3, Chapter 16, 2007（幹・枝・葉の 3 層の揺れ、葉の透過）
- Microsoft Learn, "D3D11_BLEND_DESC"（`AlphaToCoverageEnable`）

## 関連ページ

- [Vegetation](index.md)
- [Alpha Testing](../../translucency/alpha-test/index.md)
