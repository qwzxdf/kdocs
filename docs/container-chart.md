# コンテナの選び方

!!! tip "ポイント"
    <strong>迷ったら `std::vector`。</strong> ほかのコンテナは「vector だと困る理由」があるときだけ使います。

```mermaid
flowchart TD
    A[データをまとめて持ちたい] --> B{要素数はコンパイル時に決まる？}
    B -- はい --> ARR[std::array]
    B -- いいえ --> C{キーで検索したい？}
    C -- はい --> D{キーの順番が必要？}
    D -- いいえ --> UM[std::unordered_map / unordered_set]
    D -- はい --> M[std::map / set]
    C -- いいえ --> E{先頭への追加・削除が多い？}
    E -- はい --> DQ[std::deque]
    E -- いいえ --> F{取り出す順番が決まっている？}
    F -- 優先度順 --> PQ[std::priority_queue]
    F -- 先入れ先出し --> Q[std::queue]
    F -- 後入れ先出し --> ST[std::stack]
    F -- 特にない --> V[std::vector]
```

## ざっくり比較

| コンテナ | 速さ | 一言で | 追加 | 検索 | 削除 |
| --- | --- | --- | --- | --- | --- |
| [`vector`](stl/containers/vector.md) | <span class="perf perf-4">◎</span> | 伸びる配列。基本これ | 末尾 O(1) | O(n) | 末尾 O(1) |
| [`array`](stl/containers/array.md) | <span class="perf perf-4">◎</span> | 固定長の配列 | できない | O(n) | できない |
| [`unordered_map`](stl/containers/unordered_map.md) | <span class="perf perf-3">○</span> | ハッシュ表 | 平均 O(1) | 平均 O(1) | 平均 O(1) |
| [`map`](stl/containers/map.md) | <span class="perf perf-3">○</span> | 順序付きの表 | O(log n) | O(log n) | O(log n) |
| [`deque`](stl/containers/deque.md) | <span class="perf perf-3">○</span> | 両端に強い配列 | 両端 O(1) | O(n) | 両端 O(1) |
| [`priority_queue`](stl/containers/priority_queue.md) | <span class="perf perf-3">○</span> | 一番大きい物がすぐ取れる | O(log n) | 先頭のみ | 先頭 O(log n) |
| [`list`](stl/containers/list.md) | <span class="perf perf-1">×</span> | 連結リスト。ほぼ使わない | O(1) | O(n) | O(1) |

!!! warning "`std::list` はほぼ使わない"
    教科書では「途中の挿入・削除が O(1)」と習いますが、実際のゲームでは**キャッシュ効率が悪くて vector より遅い**ことがほとんどです。
