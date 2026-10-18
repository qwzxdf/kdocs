---
title: Persistent Foam
tags:
  - 描画
---

# Persistent Foam

**実際の泡は、できてから、ゆっくり消えます**。**前フレームの泡を残して、少しずつ薄めながら、新しい泡を足す**と、**自然に消える泡**になります。このページでは、**履歴を使った泡の保持**を説明します。

!!! tip "ポイント"
    - **泡のバッファを、前フレームから引き継ぐ**。
    - **毎フレーム、少しだけ薄める**。
    - **新しい泡は、最大値で足す**。
    - **水面の動きに合わせて、バッファをずらす**。

## 泡を残す（履歴）
**実際の泡はできてから、しばらく水面に残って、ゆっくり消えます**。**ヤコビアンの泡は、波が折れた瞬間にしか出ない**ので、**そのままだと一瞬光って消えて見えます**。

泡を残す方法は 3 つです。泡の履歴テクスチャは、前のフレームの泡を持ち、今のマスクと `max` を取り、毎フレーム少し減衰させます。水の流れに乗せる方法は、履歴を読む UV を流れの向きにずらして、泡が流れるようにします。カメラ追従は、履歴テクスチャをカメラ周りのワールド領域に対応させ、カメラが動いたらスクロールさせます。

```hlsl
float previous = foam_history.Sample(linear_clamp, history_uv).r;
float decayed = previous * exp(-decay_rate * delta_time);
float foam_now = max(decayed, crest_mask);
```

コードの要点です。`exp(−rate · dt)` で、フレームレートに依らない減衰になります。`max` で、新しい泡が出たらそこを新しい値にします。岸辺・波頂・航跡の複数のマスクをまとめて、1 枚の履歴に書くと扱いやすくなります。

## よくあるミス

??? failure "泡が、いつまでも消えない"
    **減衰率を上げる**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **前フレームの泡を、薄めて残す**

## 参考

- Tessendorf, "Simulating Ocean Water"（SIGGRAPH Course Notes 2001）
- Finch, "Effective Water Simulation from Physical Models"（GPU Gems 2004）
- Vlachos, "Water Flow in Portal 2"（SIGGRAPH 2010）

## 関連ページ

- [Shore Foam](index.md)
- [Foam Textures and Compositing](foam-texture.md)
