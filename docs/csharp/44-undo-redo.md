---
title: 第 44 章 Undo/Redo
tags:
  - C#連携
---

# 第 44 章 Undo/Redo

この章で、これまでの編集（作成、削除、親子づけ、名前、位置、回転、拡大、色）をすべて元に戻せて、やり直せるようにします。エディタにとって Undo は「あると便利な機能」ではなく、あって当たり前の土台です。あとから足そうとすると、すべての編集コードを書き直すことになります。第 42 章で `ISceneEditor` という窓口を作っておいたのは、この章のためでした。

!!! info "このページを読む前に"
    - [第 43 章 ピッキングとギズモ](43-picking-gizmo.md)（前の章。ここまでの内容が前提になる）
    - [C# 連携](index.md)（このセクション全体の地図と、読む順番）


## Undo の作り方は 2 通り

| 方式 | 内容 | 長所 | 短所 |
| --- | --- | --- | --- |
| スナップショット | 編集のたびに、シーン全体のコピーを保存する。Undo はそのコピーに戻す | 実装が簡単で、漏れがない | シーンが大きいと、メモリも時間も膨大。小さな変更でも全体をコピーする |
| コマンド（採用） | 編集を「やること」と「戻すこと」のペアとして記録する | 小さい。必要な分だけ記録できる。操作の名前も残せる | 編集の種類ごとにコマンドを書く。「戻すこと」の書き忘れがバグになる |

コマンド パターンを使います。1 つの編集が 1 つのコマンド（オブジェクト）で、`Do()`（実行）と `Undo()`（元に戻す）を持ちます。

```text
履歴： [ 位置を変更 ] [ 色を変更 ] [ 物を追加 ] ← 今ここ
         Undo すると、「物を追加」の Undo() が呼ばれて 1 つ前に戻る
         Redo すると、戻したコマンドの Do() がもう一度呼ばれる
```

作り始める前に難しいところを 4 つ知っておきます。

| 難しさ | 例 | 対処 |
| --- | --- | --- |
| 連続した操作 | ギズモのドラッグは、1 秒に 60 回の位置更新。そのまま積むと、Undo が 60 回必要になる | まとめる（トランザクションと合体） |
| 削除の復元 | 削除した物を戻すとき、子、色、並び順、ID を元通りにしたい | 削除の前にスナップショットを取る |
| 参照が壊れる | 削除して復元すると、別のオブジェクトになる。古いコマンドが古いオブジェクトを指したままになる | コマンドはオブジェクトでなく ID を持つ |
| 履歴の分岐 | Undo してから別の編集をすると、Redo の履歴は使えなくなる | 新しい編集で Redo の履歴を捨てる |

## コマンドと履歴

まず、コマンドのインターフェースです。

```csharp title="Services/Undo/IUndoCommand.cs"
namespace Editor.Services.Undo;

// 1 つの編集。Do で実行し、Undo で元に戻す。
public interface IUndoCommand
{
    string Name { get; }
    void Do();
    void Undo();

    // 直前のコマンドと「まとめられる」なら、next を自分に取り込んで true を返す
    // （next は、すでに実行済み）
    bool TryMerge(IUndoCommand next);
}
```

`TryMerge` は、スライダーを動かし続けたときのような連続した編集を 1 つにまとめるための口です。同じ物の同じプロパティへの編集なら、新しい値だけを自分に取り込んで、`true` を返します。

複数のコマンドを 1 つの Undo の単位にまとめる入れ物も作ります。

```csharp title="Services/Undo/MacroCommand.cs"
namespace Editor.Services.Undo;

// 複数のコマンドを 1 つの Undo の単位にまとめる。
public sealed class MacroCommand : IUndoCommand
{
    private readonly List<IUndoCommand> _commands = new();

    public MacroCommand(string name) => Name = name;

    public string Name { get; }
    public bool IsEmpty => _commands.Count == 0;

    // 追加と同時に実行する。直前のコマンドと合体できれば合体する（ドラッグの連続した更新が 1 つになる）。
    public void AddAndDo(IUndoCommand command)
    {
        command.Do();
        if (_commands.Count > 0 && _commands[^1].TryMerge(command)) return;
        _commands.Add(command);
    }

    public void Do()
    {
        foreach (var c in _commands) c.Do();                  // Redo のとき、順番に
    }

    public void Undo()
    {
        for (int i = _commands.Count - 1; i >= 0; --i) _commands[i].Undo();   // 逆順に戻す
    }

    public bool TryMerge(IUndoCommand next) => false;
}
```

C# の記法が 2 つ出てきました。`_commands[^1]` は「末尾から数えて 1 番目」、つまり最後の要素です（`^` はインデックスを末尾から数える演算子）。`public MacroCommand(string name) => Name = name;` は、本体が 1 文のコンストラクターを `=>` で書いたものです。

Undo を逆順にするのは大事なところです。「A をしてから B をした」を戻すなら、B を戻してから A を戻します。順番を守らないと、B が A の結果に依存していたときに壊れます。

履歴を管理するサービスのインターフェースは次のとおりです。

```csharp title="Services/Undo/IHistoryService.cs"
namespace Editor.Services.Undo;

public interface IHistoryService
{
    bool CanUndo { get; }
    bool CanRedo { get; }
    string? UndoName { get; }
    string? RedoName { get; }
    bool IsDirty { get; }                // 保存の後で、変更があるか

    void Execute(IUndoCommand command);  // 実行して、履歴に積む
    void Undo();
    void Redo();

    // 複数の操作を 1 つにまとめる（ギズモのドラッグなど）
    void BeginTransaction(string name);
    void CommitTransaction();

    void Clear();                        // シーンを開き直したとき
    void MarkSaved();                    // 保存したとき

    event Action? Changed;
}
```

実装は少し長いので、2 つに分けて見ます。まずフィールドとプロパティです。

```csharp title="Services/Undo/HistoryService.cs"
using System.Diagnostics;

namespace Editor.Services.Undo;

public sealed class HistoryService : IHistoryService
{
    private const int MaxHistory = 200;
    private static readonly long MergeWindowTicks = Stopwatch.Frequency * 7 / 10;   // 0.7 秒

    private readonly List<IUndoCommand> _done = new();
    private readonly Stack<IUndoCommand> _undone = new();
    private MacroCommand? _transaction;
    private long _lastExecuteTicks;

    private IUndoCommand? _savePoint;            // 保存した時点の、先頭のコマンド
    private bool _savePointBroken;               // 保存点が合体や削除で失われた

    public event Action? Changed;

    public bool CanUndo => _done.Count > 0;
    public bool CanRedo => _undone.Count > 0;
    public string? UndoName => CanUndo ? _done[^1].Name : null;
    public string? RedoName => CanRedo ? _undone.Peek().Name : null;
    public bool IsDirty => _savePointBroken || (_done.Count > 0 ? _done[^1] : null) != _savePoint;
```

履歴を 2 つの入れ物に分けています。実行済みの `_done` と、Undo して取っておいた `_undone` です。`Stack<T>` は後入れ先出しの入れ物（C++ の `std::stack`）で、`Push`、`Pop`、`Peek`（取り出さずに先頭を見る）があります。Undo は `_done` の末尾から `_undone` へ移し、Redo はその逆です。

未保存かどうか（`IsDirty`）は、保存した時点の先頭のコマンド（保存点）と、今の先頭が同じかで判定します。同じなら、保存してから何も変わっていません。Undo で保存時点まで戻れば、また「未保存なし」に戻れます。ただし、合体で保存点の中身が変わったり、古い履歴を捨てて保存点が消えたりしたら、もう戻れないので、`_savePointBroken` を立てます。

続いて、操作の部分です。

```csharp
    public void Execute(IUndoCommand command)
    {
        // トランザクション中は、まとめる入れ物に入れる（履歴にはまだ積まない）
        if (_transaction != null)
        {
            _transaction.AddAndDo(command);
            return;
        }

        command.Do();

        long now = Stopwatch.GetTimestamp();
        bool canMerge = _done.Count > 0 && now - _lastExecuteTicks < MergeWindowTicks && _done[^1].TryMerge(command);
        _lastExecuteTicks = now;

        if (canMerge)
        {
            if (ReferenceEquals(_done[^1], _savePoint)) _savePointBroken = true;    // 保存点の中身が変わった
        }
        else
        {
            _done.Add(command);
        }

        _undone.Clear();                         // 新しい編集で、Redo の履歴は捨てる
        TrimHistory();
        Changed?.Invoke();
    }

    public void Undo()
    {
        if (!CanUndo) return;
        var command = _done[^1];
        _done.RemoveAt(_done.Count - 1);
        command.Undo();
        _undone.Push(command);
        _lastExecuteTicks = 0;                   // Undo のあとは、直前のコマンドと合体させない
        Changed?.Invoke();
    }

    public void Redo()
    {
        if (!CanRedo) return;
        var command = _undone.Pop();
        command.Do();
        _done.Add(command);
        _lastExecuteTicks = 0;
        Changed?.Invoke();
    }

    public void BeginTransaction(string name)
    {
        if (_transaction != null) throw new InvalidOperationException("トランザクションの入れ子はできません");
        _transaction = new MacroCommand(name);
    }

    public void CommitTransaction()
    {
        var transaction = _transaction ?? throw new InvalidOperationException("トランザクションが始まっていません");
        _transaction = null;
        if (transaction.IsEmpty) return;         // 何も起きなかった（クリックしただけのドラッグ）
        _done.Add(transaction);                  // すでに実行済みなので、Do は呼ばない
        _undone.Clear();
        TrimHistory();
        Changed?.Invoke();
    }

    public void Clear()
    {
        _done.Clear();
        _undone.Clear();
        _transaction = null;
        _savePoint = null;
        _savePointBroken = false;
        Changed?.Invoke();
    }

    public void MarkSaved()
    {
        _savePoint = _done.Count > 0 ? _done[^1] : null;
        _savePointBroken = false;
        Changed?.Invoke();
    }

    private void TrimHistory()
    {
        while (_done.Count > MaxHistory)
        {
            if (ReferenceEquals(_done[0], _savePoint)) _savePointBroken = true;
            _done.RemoveAt(0);
        }
    }
}
```

`Execute` が中心です。トランザクション中なら、まとめる入れ物に渡すだけです。そうでなければ、コマンドを実行してから、直前のコマンドと合体できるかを調べます。合体の条件は、0.7 秒以内で、かつ `TryMerge` が `true` を返すこと（同じ物の同じプロパティ）です。スライダーを動かし続けている間の編集が 1 つのコマンドにまとまります。

新しい編集をしたら、`_undone.Clear()` で Redo の履歴を捨てます。Undo してから別の編集をしたあとに、古い Redo を許すと、履歴の整合性が取れなくなるからです。

`Undo` と `Redo` のあとで `_lastExecuteTicks = 0` にしているのは、Undo の直後の編集が Undo 前のコマンドに合体してしまうのを防ぐためです。`ReferenceEquals(a, b)` は、`==` の再定義に影響されない、同一オブジェクトかどうかの比較です。上限の `MaxHistory` で、古い履歴から捨てます。

## ドキュメントを復元しやすくする

Undo で物を復元するには、元の場所（兄弟の中の順番）に戻す必要があります。`SceneDocument` の `Create` と `Reparent` に、挿入位置の `index` を足します。

```csharp
public SceneObject Create(string name, SceneObject? parent = null, uint? id = null, int index = -1)
{
    // …（第 40 章と同じ）
    var siblings = parent?.Children ?? Roots;
    if (index < 0 || index > siblings.Count) siblings.Add(obj);
    else siblings.Insert(index, obj);
    Changed?.Invoke(new SceneChange(SceneChangeKind.Created, obj));
    return obj;
}

public void Reparent(SceneObject obj, SceneObject? newParent, int index = -1)
{
    // …（輪の検査は、第 40 章と同じ）
    (obj.Parent?.Children ?? Roots).Remove(obj);
    obj.Parent = newParent;
    var siblings = newParent?.Children ?? Roots;
    if (index < 0 || index > siblings.Count) siblings.Add(obj);
    else siblings.Insert(index, obj);
    Changed?.Invoke(new SceneChange(SceneChangeKind.Reparented, obj));
}

public int IndexOf(SceneObject obj) => (obj.Parent?.Children ?? Roots).IndexOf(obj);
```

`index` が省略（`-1`）なら末尾に追加し、指定されたらその位置に挿入します。

### スナップショット

削除する物の全部の情報を子を含めて保存します。

```csharp title="Services/Undo/Snapshots.cs"
using System.Numerics;
using Editor.Models;

namespace Editor.Services.Undo;

// 物 1 つ分（子を含む）の、保存された状態
public sealed record ObjectSnapshot(
    uint Id, string Name, Vector3 Position, Vector3 RotationDegrees, Vector3 Scale, Vector4 Color,
    IReadOnlyList<ObjectSnapshot> Children)
{
    public static ObjectSnapshot Take(SceneObject o) => new(
        o.Id, o.Name, o.Position, o.RotationDegrees, o.Scale, o.Color,
        o.Children.Select(Take).ToList());

    // 復元する。parent の下の index の位置に同じ ID で再作成する
    public SceneObject Restore(SceneDocument document, SceneObject? parent, int index)
    {
        var obj = document.Create(Name, parent, Id, index);
        obj.Position = Position;
        obj.RotationDegrees = RotationDegrees;
        obj.Scale = Scale;
        obj.Color = Color;
        document.NotifyChanged(SceneChangeKind.TransformChanged, obj);
        document.NotifyChanged(SceneChangeKind.ColorChanged, obj);
        foreach (var child in Children) child.Restore(document, obj, -1);
        return obj;
    }
}

// 削除のとき、親と並び順も一緒に覚える
public sealed record RemovedObject(ObjectSnapshot Snapshot, uint ParentId, int Index);
```

`record` は、値を運ぶだけの入れ物を短く書ける型です。コンストラクターとプロパティが自動で作られ、作ったあとは変わりません。履歴に安全に保存できます。`o.Children.Select(Take).ToList()` は、子を再帰的に `Take` します（メソッド名をそのまま渡せます）。

`Take`（保存）と `Restore`（復元）は対です。物に項目を足したら、両方に足すのを忘れないでください。`Restore` の中で `NotifyChanged` を呼んでいるのは、`Create` が既定の値でエンジンに作るので、復元した変換と色をエンジンにも送り直すためです。

## 具体的なコマンド

### 値の変更

```csharp title="Services/Undo/SetValueCommand.cs"
namespace Editor.Services.Undo;

// 物の 1 つのプロパティを変える。物は、ID で覚える（復元で別のオブジェクトになっても辿れる）。
public sealed class SetValueCommand<T> : IUndoCommand
{
    private readonly uint _id;
    private readonly string _property;
    private readonly Action<uint, T> _apply;
    private readonly T _oldValue;
    private T _newValue;

    public SetValueCommand(string name, uint id, string property, T oldValue, T newValue, Action<uint, T> apply)
    {
        Name = name;
        _id = id;
        _property = property;
        _oldValue = oldValue;
        _newValue = newValue;
        _apply = apply;
    }

    public string Name { get; }

    public void Do() => _apply(_id, _newValue);
    public void Undo() => _apply(_id, _oldValue);

    public bool TryMerge(IUndoCommand next)
    {
        if (next is SetValueCommand<T> other && other._id == _id && other._property == _property)
        {
            _newValue = other._newValue;       // 古い値は保ち、新しい値だけを更新する
            return true;
        }
        return false;
    }
}
```

`SetValueCommand<T>` はジェネリックなクラスで、`Vector3` にも `Vector4` にも `string` にも使い回せます。「どう設定するか」は `Action<uint, T> apply` として外から渡します。だから、このクラスは Undo の仕組みだけを担当して、シーンの中身を知りません。

合体のとき、`_oldValue` は最初のままで、`_newValue` だけを更新します。これで、ドラッグを何百回の更新に分けても、Undo すると、ドラッグを始める前の値に戻ります。

### 作成、削除、親子づけ

```csharp title="Services/Undo/StructureCommands.cs"
using Editor.Models;

namespace Editor.Services.Undo;

public sealed class CreateObjectCommand : IUndoCommand
{
    private readonly SceneDocument _document;
    private readonly string _objectName;
    private readonly uint _parentId;
    private readonly uint _id;
    private readonly Action<SceneObject>? _initialize;

    public CreateObjectCommand(SceneDocument document, string name, uint parentId, uint id, Action<SceneObject>? initialize)
    {
        _document = document;
        _objectName = name;
        _parentId = parentId;
        _id = id;
        _initialize = initialize;
    }

    public string Name => $"{_objectName} を作成";

    public void Do()
    {
        var parent = _parentId == 0 ? null : _document.Find(_parentId);
        var obj = _document.Create(_objectName, parent, _id);
        _initialize?.Invoke(obj);
    }

    public void Undo()
    {
        var obj = _document.Find(_id);
        if (obj != null) _document.Destroy(obj);
    }

    public bool TryMerge(IUndoCommand next) => false;
}

public sealed class DestroyObjectsCommand : IUndoCommand
{
    private readonly SceneDocument _document;
    private readonly List<RemovedObject> _removed = new();

    // 選択された物のうち、「親も選ばれている物」は除く（親が消えれば子も消えるので）
    public DestroyObjectsCommand(SceneDocument document, IEnumerable<SceneObject> targets)
    {
        _document = document;
        var set = targets.ToHashSet();
        foreach (var o in targets)
        {
            bool ancestorIncluded = false;
            for (var p = o.Parent; p != null; p = p.Parent) if (set.Contains(p)) { ancestorIncluded = true; break; }
            if (ancestorIncluded) continue;
            _removed.Add(new RemovedObject(ObjectSnapshot.Take(o), o.Parent?.Id ?? 0, document.IndexOf(o)));
        }
    }

    public string Name => _removed.Count == 1 ? $"{_removed[0].Snapshot.Name} を削除" : $"{_removed.Count} 個を削除";

    public void Do()
    {
        foreach (var r in _removed)
        {
            var obj = _document.Find(r.Snapshot.Id);
            if (obj != null) _document.Destroy(obj);
        }
    }

    public void Undo()
    {
        // 削除した順の逆に復元すると、並び順（Index）が元通りになる
        for (int i = _removed.Count - 1; i >= 0; --i)
        {
            var r = _removed[i];
            var parent = r.ParentId == 0 ? null : _document.Find(r.ParentId);
            r.Snapshot.Restore(_document, parent, r.Index);
        }
    }

    public bool TryMerge(IUndoCommand next) => false;
}

public sealed class ReparentCommand : IUndoCommand
{
    private readonly SceneDocument _document;
    private readonly uint _id;
    private readonly uint _oldParentId, _newParentId;
    private readonly int _oldIndex;

    public ReparentCommand(SceneDocument document, SceneObject obj, SceneObject? newParent)
    {
        _document = document;
        _id = obj.Id;
        _oldParentId = obj.Parent?.Id ?? 0;
        _oldIndex = document.IndexOf(obj);
        _newParentId = newParent?.Id ?? 0;
    }

    public string Name => "親を変更";

    public void Do() => Move(_newParentId, -1);
    public void Undo() => Move(_oldParentId, _oldIndex);

    private void Move(uint parentId, int index)
    {
        var obj = _document.Find(_id);
        if (obj == null) return;
        var parent = parentId == 0 ? null : _document.Find(parentId);
        _document.Reparent(obj, parent, index);
    }

    public bool TryMerge(IUndoCommand next) => false;
}
```

3 つのコマンドに共通する大事な約束が 2 つあります。

1つ目は、コマンドは `SceneObject` の参照を持たず、ID を覚えて、実行のたびに `_document.Find(_id)` で探すことです。削除して復元すると別のオブジェクトになりますが、同じ ID で復元するので、ID なら見つかります。

2つ目は、作成コマンドが最初に決めた ID を覚えて、Redo でも同じ ID を使うことです。Redo のたびに採番し直すと、あとの履歴（その物を指しているコマンド）が壊れます。

削除では、親と子が両方選ばれているとき、親だけを記録します。両方を記録すると、親を復元したときに子も戻り、さらに子自身も戻って、二重になるからです。復元を逆順にするのは、削除時の兄弟の中の位置（`Index`）を使うためで、後ろから戻すと位置がずれません。`ToHashSet()` は、集合に変えて `Contains` を速くします。

## 窓口を Undo 対応版に差し替える

`ISceneEditor` に、構造の操作を足します。

```csharp
SceneObject CreateObject(string name, SceneObject? parent, Vector3? position = null);
void DestroyObjects(IReadOnlyList<SceneObject> objects);
void Reparent(SceneObject obj, SceneObject? newParent);
```

第 42 章の `SceneEditor` は、値を直接変える実装でした。これを内側の実装として残し、履歴を記録する外側の実装を新しく作ります。内側は値の設定だけなので、小さなインターフェースに分けます。

```csharp
// 値を直接設定する（Undo なし）。内側の実装がこれを実装する。
public interface IRawSceneEditor
{
    void SetName(SceneObject obj, string name);
    void SetPosition(SceneObject obj, Vector3 value);
    void SetRotationDegrees(SceneObject obj, Vector3 value);
    void SetScale(SceneObject obj, Vector3 value);
    void SetColor(SceneObject obj, Vector4 value);
}
```

`SceneEditor` は `IRawSceneEditor` を実装する形に変えます（中身は第 42 章のまま）。外側が次のクラスです。

```csharp title="Services/UndoableSceneEditor.cs"
using System.Numerics;
using Editor.Models;
using Editor.Services.Undo;

namespace Editor.Services;

// 編集を Undo 可能なコマンドにして履歴に積む。実際の変更は、内側の IRawSceneEditor が行う。
public sealed class UndoableSceneEditor : ISceneEditor
{
    private readonly SceneDocument _document;
    private readonly IRawSceneEditor _inner;
    private readonly IHistoryService _history;

    public UndoableSceneEditor(SceneDocument document, IRawSceneEditor inner, IHistoryService history)
    {
        _document = document;
        _inner = inner;
        _history = history;
    }

    public void SetName(SceneObject obj, string name)
    {
        if (obj.Name == name) return;
        _history.Execute(new SetValueCommand<string>("名前を変更", obj.Id, "Name", obj.Name, name,
            (id, v) => { if (_document.Find(id) is { } o) _inner.SetName(o, v); }));
    }

    public void SetPosition(SceneObject obj, Vector3 value)
    {
        if (obj.Position == value) return;
        _history.Execute(new SetValueCommand<Vector3>("位置を変更", obj.Id, "Position", obj.Position, value,
            (id, v) => { if (_document.Find(id) is { } o) _inner.SetPosition(o, v); }));
    }

    public void SetRotationDegrees(SceneObject obj, Vector3 value)
    {
        if (obj.RotationDegrees == value) return;
        _history.Execute(new SetValueCommand<Vector3>("回転を変更", obj.Id, "Rotation", obj.RotationDegrees, value,
            (id, v) => { if (_document.Find(id) is { } o) _inner.SetRotationDegrees(o, v); }));
    }

    public void SetScale(SceneObject obj, Vector3 value)
    {
        if (obj.Scale == value) return;
        _history.Execute(new SetValueCommand<Vector3>("拡大を変更", obj.Id, "Scale", obj.Scale, value,
            (id, v) => { if (_document.Find(id) is { } o) _inner.SetScale(o, v); }));
    }

    public void SetColor(SceneObject obj, Vector4 value)
    {
        if (obj.Color == value) return;
        _history.Execute(new SetValueCommand<Vector4>("色を変更", obj.Id, "Color", obj.Color, value,
            (id, v) => { if (_document.Find(id) is { } o) _inner.SetColor(o, v); }));
    }

    public SceneObject CreateObject(string name, SceneObject? parent, Vector3? position = null)
    {
        uint id = _document.AllocateId();
        _history.Execute(new CreateObjectCommand(_document, name, parent?.Id ?? 0, id,
            o => { if (position is { } p) _inner.SetPosition(o, p); }));
        return _document.Find(id)!;
    }

    public void DestroyObjects(IReadOnlyList<SceneObject> objects)
    {
        if (objects.Count == 0) return;
        _history.Execute(new DestroyObjectsCommand(_document, objects));
    }

    public void Reparent(SceneObject obj, SceneObject? newParent)
    {
        if (obj.Parent == newParent) return;
        _history.Execute(new ReparentCommand(_document, obj, newParent));
    }
}
```

どのメソッドも「古い値と新しい値を持つコマンドを作って、履歴に渡す」だけです。コマンドの中で値を実際に変えるのは、内側の `_inner` で、窓口の `UndoableSceneEditor` ではありません。もし窓口を呼ぶと、Undo の中でさらに履歴が積まれて、壊れます。

登録は次のとおりです。

```csharp
containerRegistry.RegisterSingleton<IHistoryService, HistoryService>();
containerRegistry.RegisterSingleton<IRawSceneEditor, SceneEditor>();
containerRegistry.RegisterSingleton<ISceneEditor, UndoableSceneEditor>();
```

ここで見てほしいのは、`PropertyViewModel` を 1 行も変えずに、Undo に対応できたことです。`ISceneEditor` という窓口の後ろだけを差し替えたからです。

## 呼び出し側を窓口に切り替える

シーン ツリーの `SceneTreeViewModel` は、まだ `_document.Create` などを直接呼んでいます。これを窓口の呼び出しに変えます。

```csharp
private void AddEmpty()
{
    var obj = _editor.CreateObject($"Object {_document.AllocateId()}", null);
    _selection.Select(obj);
}

private void AddChild()
{
    var parent = _selection.Primary;
    if (parent == null) return;
    var obj = _editor.CreateObject($"Object {_document.AllocateId()}", parent, new Vector3(0, 1, 0));
    _selection.Select(obj);
}

private void Delete() => _editor.DestroyObjects(_selection.Selection.ToList());

public void Reparent(SceneObject dragged, SceneObject? newParent) => _editor.Reparent(dragged, newParent);
```

ギズモのドラッグは、開始から終了までをトランザクションにします。

```csharp
// GizmoController
public bool TryBeginDrag(float px, float py)
{
    // …（当たり判定）
    _history.BeginTransaction("移動");
    // …
}

public void EndDrag()
{
    _history.CommitTransaction();       // ドラッグ中の何百回もの SetPosition が、1 つの Undo になる
    _dragAxis = -1;
    // …
}
```

トランザクション中の `Execute` は `MacroCommand.AddAndDo` を通り、同じ ID、同じプロパティの連続した `SetValueCommand<Vector3>` は合体して、1 つになります。ドラッグ中の何百回もの更新は、1 つのコマンドに収まります。

## メニューとキー

`MainWindowViewModel` に、Undo と Redo のコマンドを足します。メニューの表示に操作の名前が出るようにします。

```csharp
public MainWindowViewModel(IHistoryService history /* ほか */)
{
    _history = history;
    UndoCommand = new DelegateCommand(_history.Undo, () => _history.CanUndo);
    RedoCommand = new DelegateCommand(_history.Redo, () => _history.CanRedo);

    _history.Changed += () =>
    {
        UndoCommand.RaiseCanExecuteChanged();
        RedoCommand.RaiseCanExecuteChanged();
        RaisePropertyChanged(nameof(UndoHeader));
        RaisePropertyChanged(nameof(RedoHeader));
    };
}

public DelegateCommand UndoCommand { get; }
public DelegateCommand RedoCommand { get; }
public string UndoHeader => _history.UndoName is { } n ? $"元に戻す: {n}(_U)" : "元に戻す(_U)";
public string RedoHeader => _history.RedoName is { } n ? $"やり直し: {n}(_R)" : "やり直し(_R)";
```

```xml title="MainWindow.xaml"
<Window.InputBindings>
    <KeyBinding Key="Z" Modifiers="Control" Command="{Binding UndoCommand}" />
    <KeyBinding Key="Y" Modifiers="Control" Command="{Binding RedoCommand}" />
    <KeyBinding Key="Z" Modifiers="Control+Shift" Command="{Binding RedoCommand}" />
</Window.InputBindings>
<!-- … -->
<MenuItem Header="{Binding UndoHeader}" Command="{Binding UndoCommand}" InputGestureText="Ctrl+Z" />
<MenuItem Header="{Binding RedoHeader}" Command="{Binding RedoCommand}" InputGestureText="Ctrl+Y" />
```

`Window.InputBindings` は、ウィンドウ全体で効くキー操作です。`Modifiers="Control+Shift"` のように修飾キーを組み合わせられます。`InputGestureText` はメニューに出すショートカットの表示だけで、機能は付きません。機能は `KeyBinding` の側です。

`TextBox` にフォーカスがあるときの `Ctrl+Z` は、`TextBox` 自身が持つ文字入力の Undo が優先されます。確定前の入力を取り消すだけなので、期待どおりの動きです。

最後に、ダーティ フラグ（未保存の印）をウィンドウのタイトルに出します。保存の本体は次の章です。

```csharp
public string Title => _history.IsDirty ? "MiniEngine Editor *" : "MiniEngine Editor";
// _history.Changed で RaisePropertyChanged(nameof(Title)) を呼ぶ
```

## 動かして確かめる

| 操作 | 期待する結果 |
| --- | --- |
| 「＋ 追加」→ `Ctrl+Z` | 物が消える。`Ctrl+Y` で復活（同じ名前、同じ場所） |
| 位置を変更 → `Ctrl+Z` | 元の位置に戻る。メニューに「元に戻す: 位置を変更」が出る |
| ギズモで長くドラッグ → `Ctrl+Z` | 1 回の Undo で、ドラッグ前の位置に戻る |
| 色のスライダーを動かす → `Ctrl+Z` | 1 回で、動かす前の色に戻る |
| 親を持つ物を削除 → `Ctrl+Z` | 子も含めて元通りに復活。並び順も同じ |
| Undo → 別の編集 | Redo ができなくなる（メニューが灰色） |
| 保存の後で編集 | タイトルに `*` が付く。Undo で保存時点に戻ると消える |

??? failure "Undo すると例外が出る（オブジェクトが見つからない）"
    コマンドが `SceneObject` の参照を持っています。ID を覚えて、実行時に `document.Find(id)` で探します。

??? failure "ドラッグが 1 回の Undo にならない"
    トランザクションを使っていないか、`TryMerge` の条件（同じ ID、同じプロパティ）が合っていません。

??? failure "Undo で復活した物の子が消えている"
    スナップショットの `Children` を再帰的に `Restore` していないか、`DestroyObjectsCommand` が子を二重に扱っています。

??? failure "Redo すると ID が変わる"
    `CreateObjectCommand` が `Do` のたびに新しい ID を採番しています。最初の ID を覚えて使い回します。

??? failure "Undo のあとにスライダーを動かすと、直前のコマンドと合体する"
    `Undo` と `Redo` で `_lastExecuteTicks = 0` にして、合体の対象から外します。

??? failure "Undo の途中で、また編集コマンドが積まれて履歴が壊れる"
    コマンドの中で、窓口の `ISceneEditor` ではなく、内側の `IRawSceneEditor` を呼んでいるか確認します。

## この章のまとめ

- 編集を `Do()` と `Undo()` を持つコマンドにする。
- 連続した操作は、トランザクションと合体（`TryMerge`）で 1 つにまとめる。
- コマンドは、オブジェクトの参照ではなく ID を覚える。削除はスナップショットで復元する。
- `ISceneEditor` という窓口を作っておいたので、呼び出し側を変えずに Undo に対応できた。

次の章では、シーンを JSON のファイルに保存して、読み込み直せるようにします。

[第 45 章 保存と読み込み](45-save-load.md) へ進みます。
