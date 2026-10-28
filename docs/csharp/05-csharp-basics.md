---
title: 第 5 章 C++ を知っている人のための C# 入門
tags:
  - C#連携
---

# 第 5 章 C++ を知っている人のための C# 入門

ここから先は C# のコードがどんどん出てきます。この章では、エディタを作るのに必要な C# の文法を C++ と見比べながら一通り見ていきます。C# の全部を説明するわけではありません。この教材のコードが読めて、少し直せるようになれば十分です。

!!! info "このページを読む前に"
    - [第 4 章 Player：エンジンを動かす実行側](04-player.md)（前の章。ここまでの内容が前提になる）
    - [C# 連携](index.md)（このセクション全体の地図と、読む順番）


C++ を触ったことがあれば、C# の見た目はほとんど違和感がありません。`class` も `if` も `for` もそのまま書けます。ただ、中身の考え方が違う場所が 4 つあって、最初にここを押さえておくと混乱しません。

1. メモリを自分で解放しません。`new` したオブジェクトは、使われなくなったら GC（ガベージ コレクター）が勝手に片付けます。`delete` もデストラクターも、普段はまず書きません。
2. 型が「値型」と「参照型」に分かれます。`struct` は値型（コピーすると中身がコピーされる）、`class` は参照型（コピーすると同じものを指す）です。C++ では `struct` と `class` の違いはアクセス権の初期値くらいでしたが、C# では動きが変わります。
3. ポインターをほとんど使いません。参照型の変数は、最初から「指している」ものです。`*` や `->` は出てきません。
4. ヘッダー ファイルがありません。宣言と定義は同じ場所にあって、他のファイルのクラスは `using` と名前空間で使えます。

!!! abstract "この章での Editor"
    この章では、Editor にファイルを足しません。次の節で作る、捨ててよいコンソール アプリ（`CSharpPlayground`）で、C# の文法を試します。以降のコードは、すべてその実験用のものです。

## 実験用のプロジェクトを作る

エディタのプロジェクトに実験コードを書くと散らかるので、捨ててよいプロジェクトを別に作ります。

1. Visual Studio で「新しいプロジェクトの作成」を開き、C# の「コンソール アプリ」を選びます（.NET Framework と書いてあるほうではなく、普通の「コンソール アプリ」）。
2. 名前は `CSharpPlayground`。場所は `MiniEngine` とは別のフォルダーにします。フレームワークは .NET 8.0 です。
3. 「最上位レベルのステートメントを使用しない」にチェックを入れます。`Main` 関数が見えたほうが、C++ と対応させやすいからです。

できあがる `Program.cs` はこうなっています。

```csharp title="実験：CSharpPlayground の Program.cs（Editor には入れない）"
namespace CSharpPlayground;

internal class Program
{
    static void Main(string[] args)
    {
        Console.WriteLine("Hello, World!");
    }
}
```

C++ の `main` に当たるのが `Main` です。クラスの中に書く点が違いますが、`static` を付けると「オブジェクトを作らなくても呼べる関数」になる、という意味は C++ と同じです。`Console.WriteLine` は `std::println` のようなものだと思ってください。`internal` はあとで説明します。

`Ctrl + F5` で実行すると、黒い画面に文字が出ます。以降のコードは、この `Main` の中に書いて試せます。

## 型と変数

数値や文字の型は、C++ とだいたい同じ名前です。

```csharp title="実験（CSharpPlayground の Main に書いて試す。Editor には入れない）"
int hp = 100;
float speed = 2.5f;      // float には f を付ける
double pi = 3.14159265358979;
bool alive = true;
char letter = 'A';
string name = "Player";
```

大事な違いは、C# では型の大きさが決まっていることです。`int` はどの環境でも 32 ビット、`long` は 64 ビットです。C++ の Windows では `long` が 32 ビットなので、ここは混乱しやすいところです。C++ と数値をやり取りするときは、名前ではなく大きさで対応させます。

| C# | 大きさ | C++ で近いもの |
| --- | --- | --- |
| `byte` / `sbyte` | 8 ビット | `uint8_t` / `int8_t` |
| `short` / `ushort` | 16 ビット | `int16_t` / `uint16_t` |
| `int` / `uint` | 32 ビット | `int32_t` / `uint32_t` |
| `long` / `ulong` | 64 ビット | `int64_t` / `uint64_t` |
| `float` / `double` | 32 / 64 ビット | `float` / `double` |
| `nint` | ポインターと同じ大きさ | `intptr_t` |

`char` は 16 ビット（UTF-16 の 1 単位）で、C++ の `char` とは別物です。`string` も UTF-16 で、しかも変更できません（`ToUpper()` などは、元を書き換えずに新しい文字列を返します）。

`var` は C++ の `auto` と同じです。右辺から型が決まります。

```csharp title="実験（CSharpPlayground の Main に書いて試す。Editor には入れない）"
var count = 10;                  // int
var names = new List<string>();  // List<string>
```

型の変換は、情報が落ちる向きのときだけ、はっきり書く必要があります。

```csharp title="実験（CSharpPlayground の Main に書いて試す。Editor には入れない）"
long big = 10;
int small = (int)big;       // 小さい型へはキャストが要る
int i = (int)3.7f;          // 3（小数は切り捨て）
// int j = 3.7f;            // これはコンパイル エラー
```

C++ では `int x = 3.7;` が通ってしまいますが、C# は止めてくれます。

文字列に値を埋め込むときは `$"..."` を使います（補間文字列）。`std::format` に近い機能ですが、`{}` の中に変数名をそのまま書けます。

```csharp title="実験（CSharpPlayground の Main に書いて試す。Editor には入れない）"
string text = $"{name} の HP は {hp} です";
string line = $"速度 {speed:F1}";   // :F1 で小数 1 桁
int length = name.Length;           // () が付かない（プロパティなので）
```

## 値型と参照型

この章でいちばん大事なところです。

```csharp title="実験（CSharpPlayground の Main に書いて試す。Editor には入れない）"
struct PointStruct { public int X; public int Y; }
class  PointClass  { public int X; public int Y; }

var s1 = new PointStruct { X = 1, Y = 2 };
var s2 = s1;          // 中身がコピーされる
s2.X = 99;
Console.WriteLine(s1.X);   // 1  ← s1 は変わらない

var c1 = new PointClass { X = 1, Y = 2 };
var c2 = c1;          // 同じオブジェクトを指すだけ
c2.X = 99;
Console.WriteLine(c1.X);   // 99 ← c1 も変わる
```

`struct` は、`int` や `float` と同じ仲間の「値そのもの」です。代入するたびにコピーされます。`class` は、変数が「オブジェクトへの参照」を持っているだけなので、代入しても同じオブジェクトを指します。C++ で言えば、`class` の変数は `shared_ptr` に近い感覚です（参照カウントではなく GC が管理する点は違います）。

使い分けの目安はこうです。

- 位置や色のように小さくて、コピーしても困らないものは `struct`。C++ の構造体と並びを合わせれば、エンジンにもそのまま渡せます（第 32 章）。
- シーンの物やビューモデルのように、いろいろな場所から同じものを見たいときは `class`。
- 迷ったら `class` にしておきます。

`struct` は「コピーが取れる」性質のせいで、思わぬ落とし穴もあります。`List<Point>` から取り出した `struct` のフィールドを書き換えても、コピーを変えただけで元は変わりません（実際にはコンパイル エラーになります）。第 39 章で `Vector3` の一部だけを変えたいときにも出てきます。

## クラスとプロパティ

クラスの書き方は C++ とほぼ同じです。違うのは、変数と関数の中間のような「プロパティ」があることです。WPF のバインディングはこのプロパティを前提に動くので、慣れておく必要があります。

```csharp title="実験（CSharpPlayground の Main に書いて試す。Editor には入れない）"
public class Player
{
    private int _hp = 100;                  // フィールド（メンバー変数）

    public int Hp                           // プロパティ
    {
        get { return _hp; }
        set { _hp = Math.Clamp(value, 0, 100); }
    }

    public string Name { get; set; } = "Player";   // 自動実装プロパティ
    public bool IsDead => _hp <= 0;                // 読み取り専用

    public Player(string name) { Name = name; }

    public void Damage(int amount) { Hp -= amount; }
}
```

```csharp title="実験（CSharpPlayground の Main に書いて試す。Editor には入れない）"
var p = new Player("Alice");   // new で作る。delete は書かない
p.Damage(30);
Console.WriteLine(p.Hp);       // 70
p.Hp = 500;                    // set が動いて、100 に切り詰められる
```

外から見ると `p.Hp` はただの変数のように読み書きできますが、中では `get` と `set` という関数が動いています。値を入れるときに範囲を確かめたり、あとで「値が変わったことを画面に知らせる」処理を挟んだりできるのが便利なところです。

`set` の中で出てくる `value` は、代入された値です。特別な処理が要らないなら、`{ get; set; }` と書くだけで、裏のフィールドごと自動で作られます。`=>` は「式 1 つで済むメンバー」の書き方で、`IsDead` のように読み取り専用のプロパティによく使います。くわしくは、このあとの「`=>` で書くメンバー」の節で説明します。

フィールドは `_hp` のように先頭に `_` を付けるのが慣習です。理由は「名前の付け方」の節で説明します。

アクセス権は C++ と似ていますが、`internal` が加わります。

| C# | 見える範囲 |
| --- | --- |
| `public` | どこからでも |
| `private` | そのクラスの中だけ（何も書かないとこれ） |
| `protected` | そのクラスと派生クラス |
| `internal` | 同じプロジェクトの中だけ |

`internal` は C++ には直接対応するものがありません。「DLL の中では自由に使いたいけれど、外には見せたくない」ときに使います。

作ると同時にプロパティを設定する書き方（初期化子）もよく見ます。

```csharp title="実験（CSharpPlayground の Main に書いて試す。Editor には入れない）"
var p = new Player("Bob") { Hp = 50 };
```

### `=>` で書くメンバー

`=>` は「式形式メンバー」という省略記法で、`{}` で書いても、同じ意味になります。

```csharp title="実験（CSharpPlayground の Main に書いて試す。Editor には入れない）"
public void Write(string message) => Console.WriteLine(message);

public void Write(string message)
{
    Console.WriteLine(message);
}
```

上と下は、まったく同じ関数です。値を返す関数では、`{}` の側に `return` が必要になります。

```csharp title="実験（CSharpPlayground の Main に書いて試す。Editor には入れない）"
public int Add(int a, int b) => a + b;

public int Add(int a, int b)
{
    return a + b;
}
```

`=>` は、メソッドだけでなく、プロパティ（`get` だけのもの）やコンストラクターにも使えます。

```csharp title="実験（CSharpPlayground の Main に書いて試す。Editor には入れない）"
public string Name => _name;
public Foo(ILogger logger) => _logger = logger;
```

#### 「式が 1 つ」とは、何か

`=>` の右側に書けるのは、式 1 つだけです。式と文の違いは、こうです。式は、値として評価できるひとまとまりで、文は、何かを実行するものです。

- 式の例: `a + b`、`Console.WriteLine("x")`、`new Foo()`、`x > 0 ? 1 : 2`
- 文の例: `if`、`for`、`int x = 5;`、`return a + b;`

見分け方は、「`var y = ここ;` と書けるか」です。`var y = a + b;` は書けるので、式です。`var y = if (...)` は書けないので、文です。メソッド呼び出しは、戻り値が `void` でも、式として扱われるので、`=>` の右側に書けます。

複数の処理を並べたいときは、`{}` が要ります。`=>` にできるのは、式 1 つのときだけです。

C++ のラムダ `[](int a, int b) { return a + b; }` が、C# では `(a, b) => a + b` と書ける、という関係に近いです。

`=>` と `{}` のどちらで書くかは、好みの問題です。`.editorconfig` の `csharp_style_expression_bodied_methods` で統一もできますが、すべて `{}` で書いても問題ありません。

## 名前の付け方

C# には、C++ のような、クラスに属さない関数（自由関数）がなく、メソッドは必ずクラスの中に置きます。命名の規則はコンパイラが強制しないので、`snake_case` でも `camelCase` でも動きます。それでも、次の理由で、C# の標準の習慣に合わせるのが無難です。

- `CreateShell` や `RegisterTypes` のように、基底クラスの関数を上書きするときは、基底クラスの名前に合わせるので、`PascalCase` のままになる。
- .NET の標準ライブラリや Prism の関数も `PascalCase` なので、自分のコードだけ変えると、混ざって読みにくくなる。
- `.editorconfig` の `dotnet_naming_rule` で、メソッドなどの名前を統一して、守っていないと警告を出すこともできる。

大まかな決まりは、クラス、メソッド、プロパティは `PascalCase`（`MainWindow`、`CreateShell`）、ローカル変数と引数は `camelCase`（`logger`）、private なフィールドは `_camelCase`（`_logger`）です。エディタ側（C#）はこの習慣に従い、エンジン側（C++）は Google スタイルで書く、と割り切るのが分かりやすいです。

### private フィールドの先頭の `_` は、なぜ付けるのか

`_logger` の `_` は、言語の決まりではなく、慣習です。付ける理由は、3 つあります。

- コンストラクターの引数 `logger` と、フィールドを区別できる。`_` が無いと、`this.logger = logger;` と書くことになる。
- 名前を見るだけで、フィールドだと分かる。
- `_` と打つと、そのクラスの private なフィールドだけが、入力補完の候補に出る。

Microsoft の公式の規約では必須ではありませんが、.NET の内部のコードや、Visual Studio、Rider の既定の命名規則で、`_camelCase` が使われています。

フィールドの宣言に `readonly` が付いているのも、このあとよく見ます（`private readonly ILogger _logger;`）。`readonly` は「コンストラクターの中でしか代入できない」という印で、C++ の、コンストラクターの初期化子リストで 1 度だけ決めて、あとは変えない `const` メンバーに近いものです。ほかの場所で書き換えようとすると、コンパイル エラーになります。依存するオブジェクトを受け取って保存するだけのフィールドには、`readonly` を付けるのが習慣です。

Google の C++ スタイルでは、クラスのメンバー変数の末尾に `_` を付けます（`logger_`）。構造体（`struct`）のデータ メンバーには付けません。C++ で先頭に `_` を付けるのを避ける理由は、先頭が `_` の識別子が、処理系用に予約されている場合があるためです（先頭が `_` の次に大文字、または `_` が 2 つ続く名前は、使ってはいけません）。そのため、同じ「フィールドの印」でも、C++ は末尾、C# は先頭、と流儀が分かれています。このチュートリアルでも、エンジン側の C++ は `logger_`、エディタ側の C# は `_logger` と書き分けます。

## null と、`?` の記号たち

参照型の変数は `null`（何も指していない）になれます。`null` のオブジェクトのメンバーを呼ぶと `NullReferenceException` という例外が出ます。C++ でヌル ポインターを参照したときと同じ失敗ですが、C# ではクラッシュではなく例外として受け止められます。

最近の C# では、`null` になりうるかどうかを型に書いて、コンパイラーに見張ってもらえます。

```csharp title="実験（CSharpPlayground の Main に書いて試す。Editor には入れない）"
string name = "abc";      // null を入れないという約束
string? maybe = null;     // null かもしれない、という宣言

int length = maybe?.Length ?? 0;     // null なら 0
if (maybe is not null)
{
    Console.WriteLine(maybe.Length);
}
int? number = null;       // 値型にも ? を付けると「値なし」を表せる
```

`?.` は「左が null ならここで止めて、全体を null にする」、`??` は「左が null なら右の値を使う」です。`int?` は `std::optional<int>` に近いものです。`string?` のように書いたとき、`?` が付いていない `string` に `null` を入れようとすると、コンパイラーが警告を出します。この警告を無視しないのがコツです。

## コレクションと繰り返し

```csharp title="実験（CSharpPlayground の Main に書いて試す。Editor には入れない）"
var numbers = new List<int> { 3, 1, 2 };   // std::vector<int>
numbers.Add(5);
numbers.Sort();
Console.WriteLine(numbers.Count);          // size() ではなく Count

foreach (var n in numbers)                 // 範囲 for 文
{
    Console.WriteLine(n);
}

var scores = new Dictionary<string, int>  // std::unordered_map
{
    ["Alice"] = 90,
    ["Bob"] = 70,
};
if (scores.TryGetValue("Alice", out int score))
{
    Console.WriteLine(score);
}
```

| C# | C++ で近いもの |
| --- | --- |
| `List<T>` | `std::vector<T>` |
| `Dictionary<K, V>` | `std::unordered_map<K, V>` |
| `HashSet<T>` | `std::unordered_set<T>` |
| `T[]`（配列） | `T[N]` や `std::array`（大きさは実行時に決められる） |

`dict["Carol"]` のように存在しないキーで引くと例外になります。あるかどうか分からないときは、`TryGetValue` を使います。`out int score` は「関数が値を書き込んで返してくれる引数」で、C++ の `int&` に近い使い方です。呼ぶ側にも `out` と書くのが C# のルールです。

`<T>` はジェネリクスで、`template <typename T>` にあたります。ただし C# のジェネリクスは実行時に型が決まるので、テンプレートほど自由ではありません。

`foreach` の最中にコレクションを書き換えると例外になります。消したいときは `list.ToList()` でコピーしてから回します。

### LINQ

絞り込みや変換は LINQ で書くと短く済みます。

```csharp title="実験（CSharpPlayground の Main に書いて試す。Editor には入れない）"
var names = new List<string> { "Alice", "Bob", "Charlie" };
var longNames = names.Where(n => n.Length > 3).ToList();   // 4 文字より長いもの
var upper = names.Select(n => n.ToUpper());                // 全部大文字にしたもの
bool anyB = names.Any(n => n.StartsWith("B"));
```

`Where` は filter、`Select` は transform、`Any` は any_of です。`n => n.Length > 3` はラムダ式で、次の節で説明します。

## ラムダ式、デリゲート、イベント

C++ の `std::function` に当たるものが、C# ではデリゲートです。ほとんどの場合、標準で用意された `Action` と `Func` で足ります。

```csharp title="実験（CSharpPlayground の Main に書いて試す。Editor には入れない）"
Action<string> log = message => Console.WriteLine(message);   // 戻り値なし
Func<int, int, int> add = (a, b) => a + b;                    // 最後の型が戻り値
log("hello");
Console.WriteLine(add(2, 3));    // 5
```

`Action<T>` は `std::function<void(T)>`、`Func<A, B, R>` は `std::function<R(A, B)>` と考えてください。`=>` の右が関数の本体で、これがラムダ式です。C++ のラムダとの違いは、外の変数を自動で捕まえてくれること（`[&]` のような書き方が要らない）です。

関数を持ち回るだけでなく、「何かが起きたら呼んでほしい」を実現するのが `event` です。

```csharp title="実験（CSharpPlayground の Main に書いて試す。Editor には入れない）"
public class Player
{
    public event Action<int>? HpChanged;       // HP が変わったときの通知

    private int _hp;
    public int Hp
    {
        get => _hp;
        set
        {
            _hp = value;
            HpChanged?.Invoke(_hp);            // 登録者がいれば呼ぶ
        }
    }
}

var p = new Player();
p.HpChanged += hp => Console.WriteLine($"HP が {hp} になった");   // 登録
p.Hp = 50;                                                         // 表示される
```

`event` を付けると、クラスの外からできることは `+=`（登録）と `-=`（解除）だけになります。勝手に呼び出したり、別の人の登録を消したりできません。オブザーバー パターンを言語が支えている、と考えるとしっくりきます。

ここでひとつ注意があります。`+=` で登録したものは、`-=` で解除するまで残ります。登録された側のオブジェクトを GC が片付けられなくなるので、メモリが減らない原因になりがちです（第 50 章で詳しく扱います）。

WPF の画面は、ボタンの `Click` のようなイベントと、プロパティが変わったときの通知（第 12 章）でできています。この仕組みの土台がここです。

## 継承とインターフェース

```csharp title="実験（CSharpPlayground の Main に書いて試す。Editor には入れない）"
public interface IDamageable        // 約束だけを書く
{
    void Damage(int amount);
    bool IsDead { get; }
}

public abstract class Entity { public string Name { get; set; } = ""; }

public class Enemy : Entity, IDamageable   // 継承は 1 つ、インターフェースはいくつでも
{
    private int _hp = 10;
    public void Damage(int amount) { _hp -= amount; }
    public bool IsDead => _hp <= 0;
}
```

`interface` は、純粋仮想関数だけを持つクラスのようなものです。名前は `I` で始める習慣があります。クラスの継承は 1 つだけですが、インターフェースは好きなだけ実装できます。`public` を付けずに `: Entity, IDamageable` と並べるだけで済みます。

仮想関数は `virtual` を付けたものだけで、派生クラスでは `override` と書きます（C++ と違って、`virtual` を付けない関数はデフォルトでは上書きできません）。`dynamic_cast` の代わりには `is` と `as` を使います。

```csharp title="実験（CSharpPlayground の Main に書いて試す。Editor には入れない）"
if (obj is Enemy e) { e.Damage(1); }   // 型を調べて、合えば e に取り出す
var enemy = obj as Enemy;              // 合わなければ null
```

## 例外

```csharp title="実験（CSharpPlayground の Main に書いて試す。Editor には入れない）"
try
{
    var text = File.ReadAllText("settings.json");
    Console.WriteLine(text.Length);
}
catch (FileNotFoundException e)
{
    Console.WriteLine($"ファイルがありません: {e.Message}");
}
catch (Exception e)
{
    Console.WriteLine($"想定外のエラー: {e}");
}
finally
{
    Console.WriteLine("最後に必ず通る");
}
```

C++ との大きな違いは `finally` があることです。成功しても失敗しても必ず実行されるので、後片付けを書く場所に使います。C++ ならデストラクターでやっていたことです。

例外はどれも `Exception` から派生したクラスで、`Message` にメッセージ、`StackTrace` に呼び出し経路が入っています。ログに残すときは、`e.Message` だけでなく `e.ToString()`（スタック トレースと内側の例外まで入る）を書いておくと、あとで原因を追えます。

## using の 2 つの意味

`using` は 2 種類の使い方があって、最初は紛らわしく感じるかもしれません。

```csharp title="実験（CSharpPlayground の Main に書いて試す。Editor には入れない）"
using System.Collections.Generic;      // ① 名前空間を使えるようにする

using (var stream = File.OpenRead("a.bin"))   // ② 使い終わったら自動で閉じる
{
    // stream を使う
}                                      // ここで閉じられる

using var writer = new StreamWriter("log.txt");   // ③ ②の短い書き方
```

① は C++ の `using namespace` に近いものです。ただし最近のプロジェクトでは、`System` や `System.Collections.Generic` などよく使うものは最初から入っているので、ほとんど書かずに済みます。

②③ は、ファイルやネイティブのハンドルのように「確実に閉じたいもの」のための仕組みです。C++ なら、スコープを抜けるときにデストラクターが閉じてくれました（RAII）。C# の GC は片付けるタイミングが決まっていないので、同じことをしたいなら `IDisposable` という約束を実装して、`using` で包みます。エンジンのハンドルを扱う第 32 章で、実際に使います。

## 非同期（async / await）の入口

ファイルの読み込みのように時間のかかる処理を画面を止めずに行うための仕組みです。

```csharp title="実験（CSharpPlayground の Main に書いて試す。Editor には入れない）"
string text = await File.ReadAllTextAsync("big.txt");
Console.WriteLine(text.Length);
```

`await` は「結果が出るまでこの関数を一旦止めて、呼び出し元に処理を返す」という意味で、C++20 の `co_await` に近いものです。`await` を使う関数には `async` を付け、戻り値の型は `Task`（値を返すなら `Task<T>`）にします。

WPF では、画面を触れるスレッドは 1 本だけ（UI スレッド）です。そこで時間のかかる処理を同期的に実行すると画面が固まるので、`async` / `await` が標準的な解決策になります。詳しくは第 15 章と第 44 章で扱います。

## ほかによく見る書き方

```csharp title="実験（CSharpPlayground の Main に書いて試す。Editor には入れない）"
string label = hp switch               // switch 式（値を返す）
{
    <= 0 => "死亡",
    < 30 => "ピンチ",
    _    => "元気",
};

(int x, int y) = (3, 4);               // タプル（複数の値を、まとめて受け渡す。C++ の std::tuple や構造化束縛に近い）

public record SceneInfo(string Name, int ObjectCount);   // データを運ぶだけの型

void Log(string message, int level = 0) { }
Log("hello", level: 2);                // 名前付き引数と既定値

public static class StringExtensions
{
    public static bool IsBlank(this string s) => string.IsNullOrWhiteSpace(s);   // 拡張メソッド
}
```

`record` は、プロパティとコンストラクターが自動で作られて、中身が同じなら「等しい」と判定される型です。設定やログの 1 件分のように、データを持ち運ぶだけのものに向いています。`static class` は、インスタンスを作れず、`static` なメンバーだけを持つクラスです。C++ でクラスに属さない自由関数を名前空間にまとめるのに近く、C# は自由関数が無いので、これで代用します。拡張メソッドは `this` を付けた最初の引数の型にメソッドを後から足したように見せる機能で、LINQ の `Where` や `Select` はこの仕組みでできています。

## C++ との対応表

最後に、ここまでの対応をまとめます。迷ったらここに戻ってきてください。

| やりたいこと | C++ | C# |
| --- | --- | --- |
| メモリの解放 | `delete`、スマート ポインター | GC が自動で。ネイティブ資源は `IDisposable` と `using` |
| 参照渡し | `T&` | 参照型は元から参照。値型は `ref` / `out` / `in` |
| ポインター | `T*` | 基本使わない。境界では `nint` |
| 名前の取り込み | `#include` と `namespace` | `using` と `namespace` |
| テンプレート | `template` | ジェネリクス `<T>` |
| 継承 | 多重継承可 | クラスは 1 つ、インターフェースは複数 |
| 定数 | `constexpr` / `const` | `const`（コンパイル時）、`readonly`（実行時に 1 回） |
| 配列・可変長配列 | `std::array` / `std::vector` | `T[]` / `List<T>` |
| 列挙型 | `enum class` | `enum`（`Color.Red` のように型名を付ける） |

## 動かしてみたときの詰まりどころ

??? failure "`CS0103: 現在のコンテキストに '〜' という名前は存在しません`"
    名前のタイプミスか、`using` が足りないかのどちらかです。クラス名にカーソルを置いて `Ctrl + .` を押すと、必要な `using` を足す候補が出ます。

??? failure "null の警告（`CS8600`、`CS8602` など）が出る"
    `null` になるかもしれない値をそのまま使っています。`?.` や `is not null` で確かめてから使うか、そもそも `null` にならない作りにします。警告を放置すると、実行時に `NullReferenceException` になります。

??? failure "`foreach` の途中で `Collection was modified` の例外が出る"
    ループ中に回している対象の要素を足したり消したりしています。`ToList()` でコピーしてから回してください。

??? failure "`struct` を `List` から取り出して書き換えても反映されない"
    取り出した時点でコピーになっているからです。書き換えたいデータは `class` にします。

??? failure "文字列の大文字小文字を無視して比べたい"
    `==` は大文字と小文字を区別します。区別しないなら `string.Equals(a, b, StringComparison.OrdinalIgnoreCase)` を使います。

次の章では、ここで覚えた C# を使って、WPF の画面を作り始めます。

[第 6 章 WPF プロジェクトと XAML](06-wpf-xaml.md) へ進みます。
