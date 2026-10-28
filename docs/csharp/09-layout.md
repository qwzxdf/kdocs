---
title: 第 9 章 レイアウトの仕組み
tags:
  - C#連携
---

# 第 9 章 レイアウトの仕組み

「`Width` を指定したのに、思った大きさにならない」「`Grid` の中で部品がはみ出す」「`ScrollViewer` を付けたのにスクロールしない」。WPF のレイアウトで困るときは、たいてい、WPF がどうやって大きさを決めているかを知らないだけです。この章では、その仕組みをひととおり説明します。

!!! info "このページを読む前に"
    - [第 8 章 コントロールとコンテンツ モデル](08-controls.md)（前の章。ここまでの内容が前提になる）
    - [C# 連携](index.md)（このセクション全体の地図と、読む順番）


!!! abstract "この章での Editor"
    この章では、Editor にファイルを足しません。第 6 章で書いた `DockPanel` と `Grid` の枠が、なぜその大きさと並びになるかを読み解きます。コードは、仕組みを見るための例です。

## 大きさは親と子の相談で決まる

WPF では、部品が自分の大きさを一方的に決めるわけではありません。親と子が 2 段階でやり取りして決めます。

1. Measure（測る）：親が子に「これだけの空きがあるけど、あなたはどれだけ欲しい？」と聞きます。子は「このくらい欲しい」と答えます。
2. Arrange（置く）：親が全員の希望を見て、「あなたはここに、この大きさで置くよ」と最終決定を伝えます。

この仕組みのおかげで、ウィンドウの大きさが変わると、自動でレイアウトがやり直されます。

親が子に「どれだけ空いているか」を伝えるとき、パネルの種類によって伝え方が違います。これが、「`Width` を指定しても効かない」現象の元です。

| 親のパネル | 子に伝える空き |
| --- | --- |
| `Grid` | そのセル（行・列）の大きさ |
| `StackPanel`（縦） | 幅は親の幅いっぱい、高さは無制限 |
| `StackPanel`（横） | 高さは親の高さいっぱい、幅は無制限 |
| `DockPanel` | 張り付けた端の残り |
| `ScrollViewer` | スクロールする向きは無制限 |
| `Canvas` | 無制限（座標で置くので） |

縦の `StackPanel` の中に `ListBox` を置くと、高さが無制限と伝えられるので、`ListBox` は全項目が収まる高さまで伸び、スクロールバーが出ません。「スクロールしないリスト」の原因の 1 つです。この場合は、`StackPanel` ではなく `Grid`（行の高さが `*` のもの）か `DockPanel` を使います。

## 大きさに関するプロパティ

| プロパティ | 意味 |
| --- | --- |
| `Width` / `Height` | 固定の大きさ。指定しないと `Auto`（`NaN`） |
| `MinWidth` / `MaxWidth` / `MinHeight` / `MaxHeight` | 大きさの下限・上限 |
| `Margin` | 外側の余白 |
| `Padding` | 内側の余白 |
| `HorizontalAlignment` / `VerticalAlignment` | 親から与えられた空きの中での配置 |
| `ActualWidth` / `ActualHeight` | 実際にレイアウトされたあとの大きさ（読み取り専用） |

配置の `Stretch` は、与えられた空きいっぱいに広げる指定で、これが既定です。`Width` を指定すると、`Stretch` でも指定サイズになります。`HorizontalAlignment="Left"` などを指定すると、中身に必要な大きさになります。

固定の `Width` は最後の手段にしてください。ウィンドウ全体を広げたときに、部品が追従しなくなります。まず `Grid` の `*` や `Stretch`、`MinWidth` で表現できないかを考えます。

## Grid を使いこなす

### 行・列の単位

| 指定 | 意味 |
| --- | --- |
| `100` | 固定サイズ |
| `Auto` | 中身に必要な大きさ |
| `*` | 余った領域を比率で分ける。`2*` は `*` の 2 倍 |

`*` の行・列は「余り」を分け合うので、固定サイズや `Auto` の行・列が先に場所を取った残りを使います。

### 複数のセルにまたがる

```xml title="例（Editor には入れない）"
<TextBlock Grid.Row="0" Grid.Column="0" Grid.ColumnSpan="2" Text="見出し" />
<Button    Grid.Row="1" Grid.RowSpan="2" Content="縦長" />
```

### 複数の Grid で列の幅をそろえる

別々の `Grid` にある列の幅を同じにしたいときがあります。たとえば、プロパティ パネルの「位置」「回転」「拡大」を別々の `Grid` で作って、ラベル列の幅をそろえたい場合です。`SharedSizeGroup` を使います。

```xml title="例（Editor には入れない）"
<StackPanel Grid.IsSharedSizeScope="True">
    <Grid>
        <Grid.ColumnDefinitions>
            <ColumnDefinition SharedSizeGroup="Label" Width="Auto" />
            <ColumnDefinition Width="*" />
        </Grid.ColumnDefinitions>
        <TextBlock Text="位置" />
        <TextBox Grid.Column="1" />
    </Grid>
    <Grid>
        <Grid.ColumnDefinitions>
            <ColumnDefinition SharedSizeGroup="Label" Width="Auto" />
            <ColumnDefinition Width="*" />
        </Grid.ColumnDefinitions>
        <TextBlock Text="回転 (度)" />
        <TextBox Grid.Column="1" />
    </Grid>
</StackPanel>
```

`Grid.IsSharedSizeScope="True"` を付けた親の中で、同じグループ名の列は、一番広いものに幅がそろいます。

## 他の便利なパネル

| パネル | 使いどころ |
| --- | --- |
| `UniformGrid` | すべてのセルが同じ大きさの格子。ボタンを均等に並べるとき |
| `WrapPanel` | 横に並べて折り返す。タイル、タグの並び |
| `Viewbox` | 中身を空きに合わせて拡大・縮小する |
| `DockPanel` | 端に張り付けるレイアウト。`LastChildFill` の既定は `true` |
| `Border` | 背景・枠線・角丸・余白をまとめて付けられる |
| `ScrollViewer` | 中身が大きいときのスクロール |

## スクロールしないとき

`ScrollViewer` を付けてもスクロールしないときは、中身に伝わる空きが無制限になっていないことが多いです。

1. `ScrollViewer` 自体の大きさが固定されているか、`Grid` の `*` の行に入っているかを確かめる。`Auto` の行に置くと、中身の大きさ分まで広がってしまい、スクロールの必要がなくなります。
2. `ListBox` や `DataGrid` は、内側にもともとスクロールの仕組みを持っています。その外側に別の `ScrollViewer` を重ねると、内側の `ListBox` に無制限の高さが伝わって、内側がスクロールしなくなります。
3. 横にスクロールしたければ `HorizontalScrollBarVisibility="Auto"` を指定する。既定は横が `Disabled` です。

## 画面の拡大率（DPI）

WPF の長さの単位は、1 単位が 1/96 インチです。画面の拡大率が 100% なら、1 単位が 1 ピクセル、150% なら 1.5 ピクセルになります。見た目の大きさが環境で変わらないのは、この単位のおかげです。

ただし、画像やエンジンの描画面（第 36 章の `HwndHost`）のように、物理ピクセルが必要なものを扱うときは、変換が必要です。

```csharp title="例（Editor には入れない）"
var dpi = VisualTreeHelper.GetDpi(this);       // この部品がいる画面の DPI 情報
double scaleX = dpi.DpiScaleX;                  // 150% なら 1.5
double pixelWidth = ActualWidth * scaleX;
```

アプリ自体も、DPI の違う複数のモニターに対応させたい場合は、`app.manifest` で Per-Monitor DPI 対応を宣言します（第 36 章）。

## レイアウトがうまくいかないときの確かめ方

1. 実行中に Visual Studio の「ライブ ビジュアル ツリー」を開いて、問題の部品を選ぶ。
2. 「ライブ プロパティ エクスプローラー」で `ActualWidth`、`ActualHeight`、`Margin` を確かめる（第 7 章）。
3. 部品に `Background` を付けて、どこからどこまでが、その部品に与えられた領域なのかを色で見る。

デバッグ用に一時的に色を付ける方法は、地味ですが、確実に役立ちます。「余白だと思っていた所が実は別の部品の領域だった」といったことが、すぐ分かります。

## C++ で考えると

Dear ImGui のような即時モードの UI は、毎フレーム、自分で位置と大きさを指定して描きます。WPF は保持モードで、画面の部品が親子の木として残っています。大きさは、親が「使える大きさ」を子に伝え（Measure）、子の希望を聞いてから、親が最終の場所を決める（Arrange）、という 2 段階の相談で決まります。自分で座標を計算しなくてよい代わりに、「なぜこの大きさになったのか」を相談の流れで考える必要があります。

??? failure "`StackPanel` の中に `ListBox` を入れたら、スクロールバーが出ずに画面からはみ出す"
    縦向きの `StackPanel` は、子に「高さは好きなだけ使っていい」と伝えます。そのため `ListBox` は、全項目が収まる高さまで広がってしまい、スクロールする必要がなくなります。画面の残りの高さに合わせたいときは、`Grid` の `*` の行か、`DockPanel` に入れて、親から高さが与えられるようにします。

## この章のまとめ

- 大きさは、親が空きを伝え、子が希望を答え、親が最終決定する、という流れで決まる。
- 縦の `StackPanel` の中は高さが無制限。リストの中のスクロールが効かない原因の定番。
- 固定の `Width` / `Height` は最後の手段。`Grid` の `*` や配置で表現する。
- 困ったら、色を付けて領域を見る。ライブ ビジュアル ツリーで確かめる。

次の章では、依存関係プロパティ、添付プロパティ、ルーテッド イベントという、WPF 独特の仕組みを見ます。

[第 10 章 依存関係プロパティ、添付プロパティ、ルーテッド イベント](10-dependency-properties.md) へ進みます。
