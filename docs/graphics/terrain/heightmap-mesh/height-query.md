---
title: Height at Arbitrary Positions
tags:
  - 描画
---

# Height at Arbitrary Positions

**キャラクターを地面に立たせるには、任意の位置の地面の高さが必要**です。**格子の 4 点から補間**して**求めます**。このページでは、**高さの取得方法**を説明します。

!!! tip "ポイント"
    - **位置を格子の座標に変換**し、**周囲の 4 点を取り出す**。
    - **双線形補間で、高さを求める**。
    - **CPU 側にも、高さマップを持つ**。
    - **格子の三角形の分割と、補間を合わせる**。

## 任意の位置の高さを取る
**キャラクターを地面に立たせる・草を置く・当たり判定**には、**CPU で任意の (x, z) の高さ**が**必要**です。**高さマップの 4 点を、双線形補間**します。

```cpp
float SampleHeight(const HeightMap& map, float world_x, float world_z) {
  float u = (world_x - map.origin_x) / map.cell_size;
  float v = (world_z - map.origin_z) / map.cell_size;
  int x0 = static_cast<int>(std::floor(u));
  int z0 = static_cast<int>(std::floor(v));
  float fx = u - x0;
  float fz = v - z0;

  float h00 = map.At(x0, z0);
  float h10 = map.At(x0 + 1, z0);
  float h01 = map.At(x0, z0 + 1);
  float h11 = map.At(x0 + 1, z0 + 1);

  float h0 = h00 + (h10 - h00) * fx;
  float h1 = h01 + (h11 - h01) * fx;
  return h0 + (h1 - h0) * fz;
}
```

| 点 | 説明 |
| --- | --- |
| **双線形補間** | **4 点を補間**して**滑らかな高さ** |
| **メッシュの三角形と一致させる** | **見た目のメッシュは三角形 2 枚**なので、**厳密には三角形に沿って補間する**と**ずれない**（**足が浮く・めり込む**を防ぐ） |
| **GPU と同じデータ** | **CPU 側にも同じ高さマップを保持** |
| **範囲外** | **`At` は端にクランプ** |

**対角線方向の三角形に沿った補間**は、**マス内の位置 (fx, fz) が `fx + fz < 1` かどうか**で**三角形を選び**、**その三角形上の平面の式**で**高さを出します**。

## よくあるミス

??? failure "キャラクターが、地面にめり込む・浮く"
    **描画と同じ補間方法**で**高さを求める**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **4 点を補間して、高さを求める**

## 参考

- Strugar, "Continuous Distance-Dependent Level of Detail for Rendering Heightmaps (CDLOD)"（JGT 2010）
- Losasso & Hoppe, "Geometry Clipmaps"（SIGGRAPH 2004）
- Musgrave et al., "The Synthesis and Rendering of Eroded Fractal Terrains"（SIGGRAPH 1989）

## 関連ページ

- [Heightmaps and Meshes](index.md)
- [Chunking](chunks.md)
