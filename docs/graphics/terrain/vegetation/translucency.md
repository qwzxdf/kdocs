---
title: Foliage Translucency
tags:
  - 描画
---

# Foliage Translucency

<strong>葉はソートできないほど多いので、通常の半透明は使えません</strong>。<strong>アルファ テスト・Alpha to Coverage・ハッシュド アルファ</strong>で対処します。このページでは葉の半透明の問題と対策を説明します。

!!! tip "ポイント"
    - 半透明ブレンドは、ソートが必要で葉には不向き。
    - アルファ テストで、切り抜く。
    - 遠くで細る問題は、アルファの補正で対処。
    - A2C やハッシュドで、縁をなめらかに。

## 半透明の問題
<strong>草と葉はアルファ テスト（切り抜き）で描きます</strong>。<strong>半透明ブレンドはソートが要るので不向き</strong>です。

半透明の問題と対策です。ジャギーには A2C と MSAA、または TAA で滑らかにします。遠くで草が痩せる問題はミップでアルファが薄まるためで、ミップごとにアルファを補正します（[Alpha Testing](../../translucency/alpha-test/index.md)）。裏面が暗いまたは明るい問題は、両面描画で裏面の法線を反転し、葉の透過光を足します。

## 半透明が使えない理由

草や木の葉は <strong>輪郭が細かい</strong>ので、<strong>テクスチャのアルファ（透明度）</strong>で、形を切り抜きます。ここで半透明のブレンドを使うと、次の問題が起きます。

| 問題 | 内容 |
| --- | --- |
| ソートが要る | 半透明は、奥から手前の順に描かないと正しく、混ざらない。数百万本をソートできない |
| 深度を書かない | 半透明は、深度バッファに書かない。隣の草との前後関係がおかしくなる |
| 重い | 画素ごとのブレンドは、メモリ帯域を使う。草は画面全体に重なる |

そこで、<strong>アルファ テスト（切り抜き）</strong>を使います。<strong>アルファがしきい値より小さい画素は、捨てる</strong>だけで深度も書けてソートも要りません。

```hlsl
float alpha = g_albedo.Sample(g_linear_wrap, input.uv).a;
clip(alpha - 0.5);                // アルファが 0.5 未満の画素は、捨てる
```

## アルファ テストの問題

### ① 縁がギザギザになる

アルファ テストは <strong>画素ごとに、残すか捨てるかを決める</strong>ので縁が、<strong>ジャギー</strong>になります。MSAA の効果も出ません（シェーダー内の `clip` は、1 画素ごとの結果でサブサンプルごとには、決まらない）。

| 対策 | 内容 |
| --- | --- |
| Alpha to Coverage | アルファの値を、MSAA のカバレッジ（サブサンプルの何個を、描くか）に変換する。縁がなめらか（[Alpha to Coverage](../../translucency/alpha-test/alpha-to-coverage.md)） |
| TAA | 時間方向に平均する。ジャギーがならされる（[TAA](../../postprocess/antialiasing/taa.md)） |
| ハッシュ アルファ | 画素ごとに、ランダムなしきい値で判定する。時間方向に平均すると半透明に、見える（[Hashed Alpha](../../translucency/alpha-test/hashed-alpha.md)、Wyman と McGuire、2017） |

### ② 遠くで葉が痩せて見える

テクスチャの<strong>ミップマップ</strong>で、アルファを <strong>平均して縮める</strong>と、遠くのミップでアルファの値が、小さくなります。しきい値（0.5）を下回る画素が増えて葉が、スカスカになります。

| 距離 | ミップ | アルファの平均 | 0.5 以上の画素の割合 |
| --- | --- | --- | --- |
| 近い | 0 | 元のまま | 元の割合（たとえば、60%） |
| 中くらい | 2 | ぼける | 40% |
| 遠い | 4 | さらに、ぼける | 10% |

葉の <strong>見た目の面積が距離で小さくなる</strong>のです。

<strong>対策：ミップごとにアルファを、補正</strong>します（Castaño、2010）。

| 手順 | 内容 |
| --- | --- |
| ① ミップ 0 でしきい値以上の画素の割合（カバレッジ）を求める | たとえば、60% |
| ② 各ミップでカバレッジが、同じ 60% になるようにアルファに、スケールを掛ける | ミップ 4 で、元の 60% を保つ |
| ③ スケールをミップごとに、保存する | ミップ作成の前処理で、行う |

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

ミップを作る <strong>ツールの段階</strong>で、行います。実行時のシェーダーでは普通に、ミップを読むだけです。

### ③ 距離でシェーダー側で補う

ツールで作り直せない既存のテクスチャには、<strong>シェーダーで距離に応じてしきい値を、下げる</strong>方法もあります。

```hlsl
// ミップが進むほど、しきい値を下げる（簡易な補正）。
float mip = g_albedo.CalculateLevelOfDetail(g_linear_wrap, input.uv);
float threshold = lerp(0.5, 0.25, saturate(mip / 4.0));
clip(alpha - threshold);
```

簡単ですが <strong>ミップごとのアルファの分布が、画像によって違う</strong>ので前処理の補正（②）より、精度が劣ります。

## 薄い植生（草）のアルファ

草は <strong>形をジオメトリ（細い三角形の帯）</strong>で、表現するなら <strong>アルファが要りません</strong>。三角形の縁がそのまま草の形になるので、アルファ テストの問題がなくなります。

| 方式 | アルファ | 縁 |
| --- | --- | --- |
| クロス板 ＋ 草の絵 | 要る（アルファで切り抜く） | アルファ テスト。ミップの補正が必要 |
| 1 本ずつの細い帯 | 要らない | ジオメトリの縁。MSAA でなめらか。ただし、遠くで細すぎて消える |

細い帯の <strong>遠くでの細さ</strong>（1 画素より細いと、消える）には <strong>幅の下限</strong>を設けます（[Grass Shape](grass-shape.md)）。

## 木の葉

木の葉は <strong>カード（板に葉の絵）</strong>で、表現します。アルファ テストで <strong>葉の形を、切り抜きます</strong>。

| 項目 | 内容 |
| --- | --- |
| 葉の描画 | アルファ テスト ＋ Alpha to Coverage |
| 影 | アルファ テストで影も、切り抜く（[Alpha-Tested Shadows](../../shadows/special-cases/alpha-test-shadows.md)） |
| 遠景（インポスター） | 木全体を、1 枚の絵（板）に。アルファ テスト、またはディザでフェード（[Trees](trees.md)） |
| LOD の切り替え | ディザ フェード（市松の、ディザ パターンで 2 つの LOD を、混ぜる） |

## よくあるミス

??? failure "遠くの木の葉が、スカスカに見える"
    <strong>ミップごとにアルファを補正</strong>する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 葉はアルファ テスト系で処理

## 参考

- Castaño, "Computing Alpha Mipmaps", 2010（ミップごとに、アルファを補正する）
- Wyman, McGuire, "Hashed Alpha Testing", Symposium on Interactive 3D Graphics and Games 2017
- Sousa, "Vegetation Procedural Animation and Shading in Crysis", GPU Gems 3, Chapter 16, 2007（幹・枝・葉の 3 層の揺れ、葉の透過）
- Microsoft Learn, "D3D11_BLEND_DESC"（`AlphaToCoverageEnable`）

## 関連ページ

- [Vegetation](index.md)
- [Alpha Testing](../../translucency/alpha-test/index.md)
