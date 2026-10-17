---
title: Depth Peeling
tags:
  - 描画
---

# Depth Peeling

**Depth Peeling は、最も手前の層を描いて、その次の層、さらに次…と、1 枚ずつ剥ぎながら描く手法**です。**正確ですが、層の数だけ描画が必要**で、**重い**です。このページでは、**Depth Peeling の仕組みと限界**を説明します。

!!! tip "ポイント"
    - **1 パスごとに、1 層ずつ（手前から）取り出す**。
    - **層の数だけ、パスが必要**（4 層なら 4 パス）。
    - **正確だが、重い**。
    - **現在は、PPLL や WBOIT に置き換わっている**。

## Depth Peeling
<strong>「最も手前の層」を、深度テストで取り出し、次に「その次の層」を取り出し…と、層を剥がしていく</strong>方法です。

| 手順 | 内容 |
| --- | --- |
| **① 1 枚目** | **通常の深度テスト**で、**最も手前の半透明の層**を、**画像 1 に描く**。**深度 1 を保存** |
| **② 2 枚目** | **深度 1 より奥の最も手前**を、**画像 2 に描く**（**前の深度より手前のフラグメントは、捨てる**） |
| **③ N 枚目まで繰り返す** | **層の数だけ、描画を繰り返す** |
| **④ 合成** | **奥の層から手前へ**、**N 枚の画像を重ねる** |

```hlsl
float4 PSMain(VsOutput input) : SV_Target {
  float previous_depth = previous_depth_texture.Load(int3(input.position.xy, 0)).r;
  clip(input.position.z - previous_depth - kEpsilon);
  return Shade(input);
}
```

| 点 | 説明 |
| --- | --- |
| **`clip(z - previous_depth - ε)`** | **前の層と同じか手前**の**フラグメント**を**捨てる** |
| **層の数** | **4 層で、多くのシーンは足りる**が、**足りない画素は、欠ける** |
| **コスト** | **N 回の描画**（**シーン全体の半透明ジオメトリを、N 回流す**） |
| **派生** | **Dual Depth Peeling**（**手前と奥を、同時に剥がす**：パスが半分） |

## よくあるミス

??? failure "層が多いシーンで、Depth Peeling が遅すぎる"
    **PPLL や WBOIT**に切り替える。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **1 層ずつ剥いで、正確に描く**
    - [x] **重いので、現在は少数派**

## 参考

- McGuire & Bavoil, "Weighted Blended Order-Independent Transparency"（JCGT 2013）
- Everitt, "Interactive Order-Independent Transparency"（NVIDIA 2001）
- Wyman & McGuire, "Hashed Alpha Testing"（I3D 2017）

## 関連ページ

- [OIT](index.md)
- [PPLL](ppll.md)
- [WBOIT](wboit.md)
