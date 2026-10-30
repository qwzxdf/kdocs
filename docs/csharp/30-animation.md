---
title: 第 30 章 アニメーション
tags:
  - C#連携
---

# 第 30 章 アニメーション

エディタの画面は、基本的に静かなほうが使いやすいので、派手なアニメーションはあまり要りません。それでも、パネルの開閉を滑らかにする、ボタンにマウスを乗せたらふわっと色が変わる、読み込み中に回転するマークを出す、といった控えめな動きは、使い心地を良くしてくれます。WPF はアニメーションが標準機能なので、少しの XAML で書けます。

!!! info "このページを読む前に"
    - [第 29 章 アプリの基本（起動・終了・ウィンドウ・コマンド）](29-app-basics.md)（前の章。ここまでの内容が前提になる）
    - [C# 連携](index.md)（このセクション全体の地図と、読む順番）


!!! abstract "この章で Editor に足すもの"
    | ファイル | 内容 |
    | --- | --- |
    | `Asset/AssetView.xaml`（変更） | アセットの読み込み中に、回転するマークを出す |

    ほかの例（フェードイン、マウスを乗せたときの拡大）は、仕組みを見るためのもので、Editor には入れません。エディタは、動きを控えめにしたいからです。

## アニメーションの考え方

WPF のアニメーションは、「プロパティの値を時間をかけて変化させる」仕組みです。パラパラ漫画のようにコマを描くのではなく、「`Opacity` を 0 から 1 まで 0.3 秒かけて変える」と指定します。補間の計算は WPF がやってくれます。

アニメーションにできるのは、依存関係プロパティだけです（第 10 章）。値の型ごとに、アニメーションの種類が用意されています。

| 型 | アニメーション | 例 |
| --- | --- | --- |
| `double` | `DoubleAnimation` | `Opacity`、`Width`、`Height`、回転角 |
| `Color` | `ColorAnimation` | `SolidColorBrush.Color` |
| `Thickness` | `ThicknessAnimation` | `Margin` |
| `Point` | `PointAnimation` | 位置 |

## 最小の例：フェードイン

```xml title="実験：フェードイン（Editor には入れない）"
<Border x:Name="Panel" Opacity="0">
    <Border.Triggers>
        <EventTrigger RoutedEvent="Loaded">
            <BeginStoryboard>
                <Storyboard>
                    <DoubleAnimation Storyboard.TargetProperty="Opacity"
                                     From="0" To="1" Duration="0:0:0.3" />
                </Storyboard>
            </BeginStoryboard>
        </EventTrigger>
    </Border.Triggers>
</Border>
```

読み方は、次のとおりです。

- `EventTrigger` が「`Loaded` イベントが起きたら」。
- `BeginStoryboard` が「ストーリーボードを再生する」。
- `Storyboard` は、アニメーションを束ねる入れ物。
- `DoubleAnimation` が、実際のアニメーション。`Storyboard.TargetProperty` で対象のプロパティを指定し、`From` から `To` まで、`Duration`（時:分:秒）で変化させる。

## スタイルのトリガーと組み合わせる

マウスが乗ったら大きくなる、のような動きは、トリガーの中に書きます。

```xml title="実験：マウスを乗せると大きくなる（Editor には入れない）"
<Style TargetType="Button">
    <Setter Property="RenderTransformOrigin" Value="0.5,0.5" />
    <Setter Property="RenderTransform">
        <Setter.Value>
            <ScaleTransform ScaleX="1" ScaleY="1" />
        </Setter.Value>
    </Setter>
    <Style.Triggers>
        <Trigger Property="IsMouseOver" Value="True">
            <Trigger.EnterActions>
                <BeginStoryboard>
                    <Storyboard>
                        <DoubleAnimation Storyboard.TargetProperty="RenderTransform.ScaleX" To="1.05" Duration="0:0:0.1" />
                        <DoubleAnimation Storyboard.TargetProperty="RenderTransform.ScaleY" To="1.05" Duration="0:0:0.1" />
                    </Storyboard>
                </BeginStoryboard>
            </Trigger.EnterActions>
            <Trigger.ExitActions>
                <BeginStoryboard>
                    <Storyboard>
                        <DoubleAnimation Storyboard.TargetProperty="RenderTransform.ScaleX" To="1" Duration="0:0:0.1" />
                        <DoubleAnimation Storyboard.TargetProperty="RenderTransform.ScaleY" To="1" Duration="0:0:0.1" />
                    </Storyboard>
                </BeginStoryboard>
            </Trigger.ExitActions>
        </Trigger>
    </Style.Triggers>
</Style>
```

`Trigger.EnterActions` が条件を満たしたとき、`ExitActions` が条件が外れたときに実行する動作です。`Setter` と違って、アニメーションは自動では元に戻らないので、`ExitActions` に戻す動きを書きます。

## 回転し続ける読み込みマーク

第 17 章で、アセットの読み込みに進行バーを付けました。バーだけだと、読み込みが始まった直後や、ファイルの一覧を作っている間は、動いているのかが分かりにくいので、回転するマークも出します。読み込みボタンの横に置いて、`IsBusy` の間だけ見せます。

```xml title="Asset/AssetView.xaml（変更：読み込みボタンの横に足す）"
<Path x:Name="Spinner" Visibility="{Binding IsBusy, Converter={StaticResource BoolToVisibility}}"
      Margin="8,0,0,0" Data="M 0,0 A 8,8 0 1 1 8,8" Stroke="White" StrokeThickness="2"
      RenderTransformOrigin="0.5,0.5">
    <Path.RenderTransform>
        <RotateTransform />
    </Path.RenderTransform>
    <Path.Triggers>
        <EventTrigger RoutedEvent="Loaded">
            <BeginStoryboard>
                <Storyboard>
                    <DoubleAnimation Storyboard.TargetProperty="RenderTransform.Angle"
                                     From="0" To="360" Duration="0:0:1" RepeatBehavior="Forever" />
                </Storyboard>
            </BeginStoryboard>
        </EventTrigger>
    </Path.Triggers>
</Path>
```

`RepeatBehavior="Forever"` で、止めるまで繰り返します。

`BoolToVisibility` は、`AssetView` の `UserControl.Resources` に、第 15 章と同じ `BooleanToVisibilityConverter` を置いて使います。非表示（`Collapsed`）の間も、アニメーションは裏で回り続けますが、描画されないので負担は軽く済みます。

## C# のコードから

トリガーを使わずに、ビューのコードビハインドから再生することもできます。

```csharp title="実験（Editor には入れない）"
var animation = new DoubleAnimation(0, 1, TimeSpan.FromMilliseconds(300));
Panel.BeginAnimation(UIElement.OpacityProperty, animation);
```

`BeginAnimation` の第 1 引数は、対象の依存関係プロパティです。

## 補間の仕方を変える（イージング）

アニメーションの速度の変化は、既定では一定の速さ（直線）です。滑らかな動きにしたいときは `EasingFunction` を付けます。

```xml title="実験（Editor には入れない）"
<DoubleAnimation To="1" Duration="0:0:0.3">
    <DoubleAnimation.EasingFunction>
        <CubicEase EasingMode="EaseOut" />
    </DoubleAnimation.EasingFunction>
</DoubleAnimation>
```

`EaseOut` は「最初は速く、終わりに向かって減速する」動きで、画面に何かが現れるときに自然に見えます。`EaseIn` は反対、`EaseInOut` は両方です。

## 使うときの注意

アニメーションを実行している間は、そのプロパティに別の値を設定しても反映されません。アニメーションの値が一番強いからです（第 10 章の優先順位）。コードから値を変えたいときは、`BeginAnimation(property, null)` でアニメーションを外すか、`FillBehavior="Stop"` にして、終わったら元の値に戻る形にします。

`Width` や `Height` のアニメーションは重くなります。毎フレーム、レイアウトのやり直しが起きるからです。可能なら、拡大縮小・移動・回転を行う `RenderTransform` で代用してください。レイアウトに影響しないので軽く済みます。ゲームで言えば、当たり判定のサイズを毎フレーム変えるのではなく、描画だけの変換行列を変えるようなものです。

`HwndHost` の上にアニメーションを重ねても、見えません。エンジンの描画面（第 37 章）は WPF の外にあるので、WPF の部品は、その上に描けないからです。

動きは、控えめにします。エディタは、作業の邪魔をしないことが大事です。

## この章のまとめ

- アニメーションは、依存関係プロパティを時間をかけて変える仕組み。`Storyboard` に入れて、トリガーやコードから再生する。
- 見た目の変化を滑らかにするなら `EasingFunction`。
- 重いレイアウト系のプロパティより、`RenderTransform` のほうが軽い。
- エディタでは、控えめに使う。

## 第 2 部のまとめ

第 2 部では、次のことを学びました。

| 章 | 学んだこと |
| --- | --- |
| 第 5 章 | C# の基本（型、クラス、プロパティ、null、コレクション、デリゲート） |
| 第 6 章 | XAML の読み方と書き方 |
| 第 7 章 | Visual Studio で XAML を書くコツ（ホット リロード、ライブ ビジュアル ツリー） |
| 第 8 章 | コントロールとコンテンツ モデル |
| 第 9 章 | レイアウトの仕組み |
| 第 10 章 | 依存関係プロパティ、添付プロパティ、ルーテッド イベント |
| 第 11 章 | スタイル、リソース、テンプレート、トリガー |
| 第 14 章 | データバインディングと MVVM |
| 第 15 章 | バインディングの掘り下げ（Mode、検証、デバッグ） |
| 第 16 章 | リストとデータ表示 |
| 第 17 章 | 非同期処理と UI スレッド |
| 第 12 章、第 18〜24 章 | Prism（DI、ViewModelLocator、リージョン、モジュール、イベント集約、ダイアログ） |
| 第 25 章 | Prism の掘り下げ |
| 第 26 章 | MVVM ライブラリの比較 |
| 第 27〜28 章 | UserControl、カスタム コントロール、Behaviors |
| 第 29〜30 章 | アプリの基本、アニメーション |

ここまでで、C#、WPF、Prism の基本はそろいました。エディタの画面の骨組みはできましたが、まだエンジンとはつながっていません。次の章から、C# と C++ をつなぎます。

[第 31 章 C# から C++ を呼ぶ：連携方式の比較](31-interop-overview.md) へ進みます。
