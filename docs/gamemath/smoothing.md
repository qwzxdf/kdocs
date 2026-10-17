---
title: スムージングとフィルタ
tags:
  - ゲーム数学
---

# スムージングとフィルタ

ゲームの値は**そのまま使うとガタガタ**になることがよくあります。カメラが急に動く、スティック入力がぶれる、FPS の表示が読めないほど変わる、HP バーが一瞬で減る、といった問題です。**値をなめらかにする**ための数学が、<strong>スムージング（平滑化）</strong>です。このページでは、**指数減衰・SmoothDamp・ばね・PID・移動平均・入力の補正**を説明します。

!!! tip "ポイント"
    - 基本は<strong>目標へ少しずつ近づく</strong>。<strong>`dt` に依存しない式</strong>（<strong>`1 - exp(-rate × dt)`</strong>）で書く。
    - <strong>SmoothDamp</strong>（臨界減衰ばね）は、<strong>速度も連続</strong>で<strong>カメラの追従に最適</strong>。
    - <strong>ばね（減衰つき）</strong>は、<strong>行き過ぎて戻る</strong>弾む動きを作れる。
    - <strong>PID</strong>は<strong>目標値に合わせ続ける</strong>制御（乗り物・照準・姿勢）。
    - <strong>移動平均・指数移動平均</strong>は、<strong>ノイズ・ばらつきを減らす</strong>（FPS の表示・入力）。
    - スティックの入力には<strong>デッドゾーンと、カーブ</strong>を入れる。

## 指数減衰（Damp）

**現在値から目標までの差を、毎フレーム一定の割合で縮める**方法です。

```cpp
float Damp(float current, float target, float rate, float delta_time) {
  return std::lerp(current, target, 1.0f - std::exp(-rate * delta_time));
}
```

| 点 | 説明 |
| --- | --- |
| **`rate` が大きいほど速い** | `rate = 10` で、0.1 秒に約 63%、0.3 秒で約 95% 近づく |
| **dt に依存しない** | 60 FPS でも 144 FPS でも、同じ時間後には、同じ位置 |
| **目標が動いても自然** | 常に「今の目標」へ向かう（追従に強い） |
| **終わりがない** | 目標に漸近するだけで到達しない。十分近ければスナップ |

詳しくは[補間](interpolation.md)にもあります。

### 半減期で指定する

「何秒で差が半分になるか」で指定すると**直感的に調整**できます。

```cpp
float DampHalfLife(float current, float target, float half_life, float delta_time) {
  float t = 1.0f - std::pow(0.5f, delta_time / half_life);
  return std::lerp(current, target, t);
}
```

`half_life = 0.1` なら、0.1 秒ごとに差が半分になります。

### ベクトル・色にも

`Vector3::Lerp` を使って、**位置・色・拡大率**に同じ式が使えます。**角度**は最短の差で補間します（[三角関数](trigonometry.md)）。

## SmoothDamp（臨界減衰ばね）

指数減衰は**目標が動かない時**は良いのですが、**速度が不連続**（動き出しが急）になります。**SmoothDamp** は、<strong>ばね（臨界減衰）</strong>として動くため、**速度も滑らかに連続**します。Unity の `Mathf.SmoothDamp` と同じ考え方です。

```cpp
float SmoothDamp(float current, float target, float* velocity, float smooth_time, float delta_time, float max_speed = std::numeric_limits<float>::infinity()) {
  float omega = 2.0f / std::max(0.0001f, smooth_time);
  float x = omega * delta_time;
  float exp = 1.0f / (1.0f + x + 0.48f * x * x + 0.235f * x * x * x);
  float change = current - target;
  float max_change = max_speed * smooth_time;
  change = std::clamp(change, -max_change, max_change);
  float adjusted_target = current - change;
  float temp = (*velocity + omega * change) * delta_time;
  *velocity = (*velocity - omega * temp) * exp;
  float output = adjusted_target + (change + temp) * exp;
  if ((target - current > 0.0f) == (output > target)) {
    output = target;
    *velocity = (output - target) / delta_time;
  }
  return output;
}
```

| 点 | 説明 |
| --- | --- |
| **`smooth_time`** | 目標へ達するおおよその時間（小さいほど速い） |
| **`velocity`** | 状態（呼び出しをまたいで持つ） |
| **行き過ぎない** | 臨界減衰なので目標を超えない |
| **使いどころ** | **カメラの追従**・UI のスクロール・キャラへ向かう視点 |

!!! note "式は、そのまま写す"
    この実装は**近似が入った、よく知られた形**です。自分で書き換えず、ライブラリや公開されたコードを、そのまま使うのが安全です。

## 減衰つきばね

**ばね（フックの法則）に減衰を足した**ものを毎フレーム解く方法です。**減衰の強さで動きが変わります**。

```cpp
void Spring(float* position, float* velocity, float target, float stiffness, float damping, float dt) {
  float force = -stiffness * (*position - target) - damping * (*velocity);
  *velocity += force * dt;
  *position += *velocity * dt;
}
```

| 減衰 | 動き |
| --- | --- |
| <strong>減衰が弱い（不足減衰）</strong> | **行き過ぎて、揺れながら収束**（弾む動き） |
| <strong>ちょうど（臨界減衰）</strong> | 行き過ぎずに**最速で収束**。SmoothDamp はこれ |
| <strong>強い（過減衰）</strong> | ゆっくり、のろのろと収束 |

| 使いどころ | 説明 |
| --- | --- |
| **弾むカメラ・UI** | 少し行き過ぎて戻る |
| **ボタンの押し込み** | 反応を弾ませる |
| **髪・尻尾・アクセサリー** | 本体の動きに遅れて揺れる |

**`stiffness` と `damping` は、組み合わせで動きが変わる**ので、`damping = 2 × √stiffness`（質量 1）を出発点にして、調整します（臨界減衰）。**硬いばね**（`stiffness` 大）を大きな `dt` で解くと**発散**するので、**サブステップ**で刻みます（[運動](motion.md)）。

## PID 制御

<strong>目標と現在の値の差（誤差）</strong>から、**操作量**を決める制御の方法です。**3 つの項**を足します。

```text
操作量 = Kp × 誤差 + Ki × (誤差の積分) + Kd × (誤差の微分)
```

| 項 | 意味 | 効果 |
| --- | --- | --- |
| <strong>P（比例）</strong> | 今の誤差に比例 | 誤差が大きいほど、強く動かす。**これだけだと振動や定常誤差** |
| <strong>I（積分）</strong> | 誤差の積み重ね | 少しの誤差が続いたら、強める（**定常誤差をなくす**） |
| <strong>D（微分）</strong> | 誤差の変化の速さ | 変化が速いほど、ブレーキ（**振動を抑える**） |

```cpp
class PidController {
 public:
  PidController(float kp, float ki, float kd) : kp_(kp), ki_(ki), kd_(kd) {}

  float Update(float target, float current, float dt) {
    float error = target - current;
    integral_ += error * dt;
    float derivative = (error - previous_error_) / dt;
    previous_error_ = error;
    return kp_ * error + ki_ * integral_ + kd_ * derivative;
  }

 private:
  float kp_;
  float ki_;
  float kd_;
  float integral_ = 0.0f;
  float previous_error_ = 0.0f;
};
```

| 使いどころ | 説明 |
| --- | --- |
| **乗り物の姿勢・高さ維持** | ホバーの高さ・飛行機の傾き |
| **照準アシスト・追尾** | 目標へ向かう回転 |
| **物理で「目標の位置」へ動かす** | 力を加えて、位置を追わせる |
| **カメラの追従** | 自然な加速と減速 |

| 注意 | 説明 |
| --- | --- |
| **積分のワインドアップ** | 誤差が大きい間、積分項が膨らみ続ける。**上限を設ける** |
| **微分のノイズ** | 微分はノイズを増幅する。**目標の変化では、微分しない**（現在値の変化だけを使う） |
| **ゲインの調整** | P だけ → D を足して振動を止める → I で残りの誤差。**試して調整**する |

## 移動平均

**直近 N 個の値の平均**を取ります。**ノイズ・ばらつきを減らす**シンプルな方法です。

```cpp
class MovingAverage {
 public:
  explicit MovingAverage(size_t size) : values_(size, 0.0f) {}

  void Add(float v) {
    sum_ -= values_[index_];
    values_[index_] = v;
    sum_ += v;
    index_ = (index_ + 1) % values_.size();
    if (count_ < values_.size()) ++count_;
  }

  float Average() const { return count_ == 0 ? 0.0f : sum_ / static_cast<float>(count_); }

 private:
  std::vector<float> values_;
  float sum_ = 0.0f;
  size_t index_ = 0;
  size_t count_ = 0;
};
```

| 使いどころ | 説明 |
| --- | --- |
| **FPS・フレーム時間の表示** | 直近 60 フレームの平均（読みやすくする） |
| **マウスの動きの平滑化** | 数フレームの平均 |
| **センサー風の値** | ノイズ除去 |

| 点 | 説明 |
| --- | --- |
| **遅れる** | 平均を取るぶん、変化に**遅れて**反応する |
| **リングバッファ** | 古い値を上書きして、メモリを一定にする |
| **和を保持** | 毎回足し直さず、**差分**で更新する（高速） |
| **浮動小数点の誤差** | 長時間使うと和の誤差が溜まる。たまに再計算する |

### 指数移動平均（EMA）

**過去の全部を重み付きで平均**したものです。**メモリが要らず、1 つの値だけ**持てば済みます。

```cpp
smoothed = std::lerp(smoothed, new_value, alpha);
```

**これは指数減衰と同じ形**です。`alpha` が小さいほど滑らかで、遅れます。**フレームレートに依存しない**ようにするには、`alpha = 1 - exp(-rate × dt)` にします。

## 入力の補正

**ゲームパッドのスティック**は、**中央に戻ってもわずかにずれた値**を返します。そのままだと**放しているのにキャラが少しずつ動く**（ドリフト）ことがあります。

### デッドゾーン

**中央付近の小さな値を、0 とみなします**。

```cpp
Vector2 ApplyDeadzone(Vector2 stick, float deadzone) {
  float length = stick.Length();
  if (length < deadzone) {
    return Vector2::Zero;
  }
  float scaled = (length - deadzone) / (1.0f - deadzone);
  return stick * (scaled / length);
}
```

| 方式 | 説明 |
| --- | --- |
| **軸ごとのデッドゾーン** | x・y それぞれで判定（斜めの動きが不自然になる） |
| **円形のデッドゾーン** | ベクトルの長さで判定（推奨） |
| **再スケール** | デッドゾーンの外を、0〜1 に引き伸ばす（急に動き出さない） |

### 入力のカーブ

**スティックの倒し量と動きの量の関係を曲げます**。

| カーブ | 効果 |
| --- | --- |
| **線形** | そのまま |
| <strong>2 乗（`x²`）</strong> | **小さな倒しで細かく操作**できる（狙い・微調整）。大きく倒すと速い |
| <strong>S 字（smoothstep）</strong> | 小さい所と大きい所の両端を、なだらかに |

```cpp
float ApplyCurve(float input, float exponent) {
  return std::copysign(std::pow(std::abs(input), exponent), input);
}
```

### 入力の遅れ・緩め

| 方法 | 説明 |
| --- | --- |
| **加速と減速** | 入力に対し、**目標の速度へ近づく**（Damp）。急停止・急発進がなめらか |
| **マウスの加速** | 速い動きをより大きく（精度と速さの両立） |
| **入力のバッファ** | 少し前の入力を数フレーム覚えて、受け付ける |

## 使い分け

| 目的 | おすすめ |
| --- | --- |
| **決まった時間の演出** | [イージング](easing.md) |
| <strong>動く目標への追従（カメラ）</strong> | **SmoothDamp**・指数減衰 |
| **弾む・揺れる** | **減衰つきばね** |
| **目標値を保ち続ける** | **PID** |
| **値のばらつきの除去** | **移動平均・EMA** |
| **スティックの入力** | **デッドゾーン ＋ カーブ** |

## よくあるミス

??? failure "`lerp(current, target, 0.1f)` を毎フレーム使って、フレームレートで速さが変わる"
    `1 - exp(-rate × dt)` にします。

??? failure "指数減衰が、いつまでも目標に着かない"
    十分近づいたら、目標へスナップします。

??? failure "PID の積分が膨らみ続ける"
    積分項に上限を設けます。

??? failure "硬いばねが大きな `dt` で発散する"
    サブステップにするか、SmoothDamp を使います。

??? failure "スティックで、軸ごとにデッドゾーンをかけて、斜めが不自然になる"
    ベクトルの長さで判定する、円形のデッドゾーンにします。

??? failure "移動平均で、反応が遅れすぎる"
    窓を小さくするか、EMA の `alpha` を大きくします。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 基本は<strong>指数減衰</strong>。<strong>`1 - exp(-rate × dt)`</strong>。目標が動いても自然
    - [x] <strong>SmoothDamp</strong>：速度も連続。<strong>カメラの追従</strong>
    - [x] <strong>減衰つきばね</strong>：弾む動き。<strong>臨界減衰 ＝ 行き過ぎない最速</strong>
    - [x] <strong>PID</strong>：目標値を保つ制御。<strong>積分に上限</strong>
    - [x] <strong>移動平均・EMA</strong>：ノイズ除去（遅れる）
    - [x] スティックは<strong>円形デッドゾーン ＋ カーブ</strong>

## 関連ページ

- [ゲーム数学](index.md)
- [補間（lerp）](interpolation.md)
- [イージング](easing.md)
- [運動と物理の数学](motion.md)
