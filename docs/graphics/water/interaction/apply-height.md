---
title: Applying a Height Map to the Surface
tags:
  - 描画
---

# Applying a Height Map to the Surface

**シミュレーションした高さマップを、水面のメッシュの高さと法線に足す**と、**波紋が見えます**。**シミュレーションする範囲は、カメラの周りに限る**のが**普通**です。このページでは、**反映の方法と、シミュレーション領域**を説明します。

!!! tip "ポイント"
    - **高さマップを読んで、頂点の高さに足す**。
    - **傾きから、法線にも足す**。
    - **シミュレーション領域は、カメラの周りの四角**。
    - **領域が動く時は、マップをずらす**。

## 高さマップを水面に反映する
**シミュレーションの高さを、水面に反映**します。

| 反映先 | 内容 |
| --- | --- |
| **頂点の高さ** | **頂点シェーダーで高さマップを読み**、**波の高さに足す** |
| **法線** | **高さマップの勾配**から**法線**を作り、**波の法線に足す**（**細かい凹凸が見える**） |

```hlsl
float2 texel = 1.0 / sim_size;
float hl = ripple_map.Sample(linear_clamp, uv - float2(texel.x, 0)).r;
float hr = ripple_map.Sample(linear_clamp, uv + float2(texel.x, 0)).r;
float hd = ripple_map.Sample(linear_clamp, uv - float2(0, texel.y)).r;
float hu = ripple_map.Sample(linear_clamp, uv + float2(0, texel.y)).r;

float3 ripple_normal = normalize(float3((hl - hr) * normal_strength, 2.0 * texel_world, (hd - hu) * normal_strength));
```

| 点 | 説明 |
| --- | --- |
| **中心差分** | **左右・上下の差**が**勾配** |
| **`normal_strength`** | **大きいほど、凹凸がはっきり** |
| **合成** | **波の法線の XZ に波紋の XZ を足して正規化** |

## シミュレーション領域
**水面全体を高解像度でシミュレーションするのは、重すぎます**。**カメラ周りの狭い領域だけ**を**対象にします**。

| 工夫 | 内容 |
| --- | --- |
| **カメラ追従** | **領域の中心をカメラの近くに置く** |
| **ずれの処理** | **領域が動くとき、テクセル単位で動かして、高さを読み替える**（**波がずれない**ように**ワールド座標をテクセルに揃える**） |
| **解像度** | **512×512 を、20〜30 m 四方**など。**1 テクセル 5 cm 程度** |
| **端でフェード** | **領域の端で高さを 0 に近づける**（**切れ目が見えない**） |

## よくあるミス

??? failure "領域の端で、波紋が途切れる"
    **端でフェード**する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **高さと法線に、足し込む**
    - [x] **領域はカメラに追従**

## 参考

- Tessendorf, "Simulating Ocean Water"（SIGGRAPH Course Notes 2001）
- Finch, "Effective Water Simulation from Physical Models"（GPU Gems 2004）
- Vlachos, "Water Flow in Portal 2"（SIGGRAPH 2010）

## 関連ページ

- [Water Interaction](index.md)
- [Writing Object Contacts](contact.md)
