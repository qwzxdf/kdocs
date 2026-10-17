---
title: Alpha to Coverage
tags:
  - 描画
---

# Alpha to Coverage

**Alpha to Coverage（A2C）は、MSAA のサンプル マスクを、アルファ値に応じて決める手法**です。**縁がなめらかになり、ソートも不要**なので、**葉や草に最適**です。このページでは、**A2C の仕組みと使い方**を説明します。

!!! tip "ポイント"
    - **アルファ値を、MSAA の「カバレッジ（何サンプル覆うか）」に変換**する。
    - **ソート不要・縁がなめらか**。
    - **MSAA が必要**（4x なら、5 段階の濃さ）。
    - **遠くで細る問題は、アルファの補正で対処**する。

## Alpha to Coverage
**MSAA を使っているとき**、**アルファの値を、そのまま「カバレッジ（どのサンプルを塗るか）」に変換**する機能です。**アルファ 0.5 なら、4 サンプルのうち 2 つを塗る**ことで、**縁が滑らかな段階**になります。

```cpp
D3D11_BLEND_DESC desc = {};
desc.AlphaToCoverageEnable = TRUE;
desc.RenderTarget[0].RenderTargetWriteMask = D3D11_COLOR_WRITE_ENABLE_ALL;
device->CreateBlendState(&desc, &alpha_to_coverage_state);
```

| 点 | 説明 |
| --- | --- |
| **`AlphaToCoverageEnable`** | **ピクセル シェーダーの出力アルファを、カバレッジ マスクに変換** |
| **MSAA が必要** | **MSAA の描画先**（`SampleDesc.Count` が 2 以上）でのみ**有効** |
| **ブレンドは不要** | **アルファ ブレンドとは別の機構**。**深度も書ける** |
| **効果** | **縁が、MSAA のサンプル数ぶんの段階で滑らかに** |

**4x MSAA では 5 段階**（0/4〜4/4）の**透明度**しか**表せません**。**ディザリングのようなパターン**が**見える**ことがあります。

## よくあるミス

??? failure "A2C を設定したのに、効果が出ない"
    **MSAA を有効**にし、**ブレンド ステートで A2C を ON**にする。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **アルファを MSAA のカバレッジに変換**
    - [x] **葉や草に最適**

## 参考

- McGuire & Bavoil, "Weighted Blended Order-Independent Transparency"（JCGT 2013）
- Everitt, "Interactive Order-Independent Transparency"（NVIDIA 2001）
- Wyman & McGuire, "Hashed Alpha Testing"（I3D 2017）

## 関連ページ

- [アルファ テスト](index.md)
- [ハッシュド アルファ](hashed-alpha.md)
- [比較](comparison.md)
