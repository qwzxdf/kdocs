---
title: 水面の裏側と、またぐ処理
tags:
  - 描画
---

# 水面の裏側と、またぐ処理

**水中から水面を見上げると、水面は、鏡のように反射する部分と、空が見える部分（スネルの窓）に分かれます**。**カメラが水面をまたぐ時の、見た目の切り替え**にも**注意**が必要です。このページでは、**水面の裏側の見え方と、またぐ処理**を説明します。

!!! tip "ポイント"
    - **水面の裏側は、全反射とスネルの窓**。
    - **水面を描く時、裏面も描く**（カリングを切る）。
    - **カメラが水面をまたぐ瞬間は、画面の半分が水中**になる。
    - **またぐ時は、水面の位置で、画面を上下に分ける**。

## 水面の裏側
**水中から水面を見上げる**と、**水面は「鏡」と「窓」の両方**になります。

<svg class="fig illust" viewBox="0 0 780 260" role="img" aria-label="水中から見上げる窓">
<text x="20" y="24" class="fig-title">水中から見上げる：臨界角の内側だけ空が見え、外側は全反射</text>
<rect x="40" y="110" width="700" height="130" fill="#4c8bf5" fill-opacity="0.2"/>
<line x1="40" y1="110" x2="740" y2="110" stroke="#4c8bf5" stroke-width="3"/>
<circle cx="390" cy="225" r="7" fill="#e5484d"/>
<text x="402" y="230" style="font-size:12px">カメラ</text>
<line x1="390" y1="225" x2="390" y2="110" stroke="currentColor" stroke-opacity="0.4" stroke-dasharray="4 4"/>
<line x1="390" y1="225" x2="505" y2="110" stroke="#2ea043" stroke-width="3"/>
<line x1="390" y1="225" x2="275" y2="110" stroke="#2ea043" stroke-width="3"/>
<line x1="505" y1="110" x2="610" y2="60" stroke="#2ea043" stroke-width="3"/>
<line x1="275" y1="110" x2="170" y2="60" stroke="#2ea043" stroke-width="3"/>
<text x="612" y="62" style="font-size:12px">空が見える</text>
<line x1="390" y1="225" x2="610" y2="110" stroke="#e5aa28" stroke-width="3"/>
<line x1="610" y1="110" x2="690" y2="215" stroke="#e5aa28" stroke-width="3"/>
<text x="600" y="172" style="font-size:12px">全反射</text>
<text x="400" y="170" style="font-size:12px">臨界角 約 49°</text>
</svg>

**水から空気へ出る光は、臨界角（約 49°）より浅い角度だと屈折せずに全反射**します。

<div class="formula">臨界角 θc = asin( n₂ / n₁ ) = asin( 1.0 / 1.33 ) ≈ 48.8°</div>

| 範囲 | 見え方 |
| --- | --- |
| <strong>真上に近い（円の内側）</strong> | **空が見える**（**窓**）。**空は円形に縮んで見える**（スネルの窓） |
| **円の外側** | **全反射**：**水中の景色が水面に鏡のように映る** |

```hlsl
float3 refracted = refract(-view_dir, -normal, 1.33 / 1.0);
bool total_internal_reflection = dot(refracted, refracted) < 0.001;

float3 color = total_internal_reflection
             ? SampleUnderwaterReflection(reflect(-view_dir, -normal))
             : SampleSky(refracted);
```

| 点 | 説明 |
| --- | --- |
| **`refract` の戻り値が 0** | **全反射**（屈折できない） |
| **法線を反転** | **水中側から見るので法線の向きを逆に** |
| **水面の下側のシェーディング** | **フレネルは水中側の屈折率で計算** |

## 水面をまたぐ処理
**水面ぎりぎりにカメラがあるとき、画面の上半分は水の外、下半分は水の中**になります。

| 工夫 | 内容 |
| --- | --- |
| **近い面を塞ぐ** | **カメラ前方の水面に細い帯**（水中のフォグ色）**を描き、境目の隙間をなくす** |
| **水位線の描画** | **ポストプロセスで水位の画面上の位置を求め、上下で別の処理** |
| **体積の判定** | **水のボリューム（メッシュ）を描き、前面・裏面で内外を決める** |
| **遷移** | **水に入る瞬間は、フェードで急変を隠す** |

## よくあるミス

??? failure "水に入る瞬間、画面がちらつく"
    **水面のメッシュは、裏面も描き**、**水中の判定をなめらかに**切り替える。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **裏面も描く**
    - [x] **またぐ瞬間の処理に注意**

## 参考

- Tessendorf, "Simulating Ocean Water"（SIGGRAPH Course Notes 2001）
- Finch, "Effective Water Simulation from Physical Models"（GPU Gems 2004）
- Vlachos, "Water Flow in Portal 2"（SIGGRAPH 2010）

## 関連ページ

- [水中の表現](index.md)
- [水中の霧](fog.md)
