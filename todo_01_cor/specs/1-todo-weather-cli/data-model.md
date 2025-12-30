# Data Model: Todo 天気連携CLI

## エンティティ: Task

- `id` (int): 一意の連番ID
- `title` (string): タスク名（必須, 非空）
- `completed` (bool): 完了フラグ
- `priority` (enum): `高` / `中` / `低`（default: `中`）
- `location` (object): {
  - `name` (string): ユーザーが入力した都市名/場所名
  - `latitude` (float): 緯度
  - `longitude` (float): 経度
  - `timezone` (string): IANA タイムゾーン名（例: `Asia/Tokyo`）
  }
- `due_date` (datetime with tz): 期限日時（ローカルのタイムゾーンに解釈）
- `candidate_dates` (array of objects): 候補日リスト（最大N件）
  - each candidate: {
    - `date` (date with tz): 候補日（時間情報はオプション）
    - `precipitation_probability` (float 0-100): 降水確率（%）
    - `temperature` (float): 予想気温（摂氏）
    - `reason` (string): 選定理由（例: "降水確率が最小"）
    }
- `created_at` (datetime UTC)
- `updated_at` (datetime UTC)

## バリデーションルール

- `title` は空であってはならない。
- `priority` は `高`/`中`/`低` のいずれか。
- `due_date` は `created_at` より未来であること（違反時は警告を出し拒否または確認を要求）。
- `location` は `name` が存在し、成功したジオコーディングで `latitude`/`longitude`/`timezone` が埋まること。

## ストレージ表現

- 単一JSONファイルで Task オブジェクトの配列を保持する。
- 変更時は `filelock` によるロックを取得し、読み込み→変更→上書きの順で操作する。

## 状態遷移

- `active` (デフォルト) → `completed`（ユーザー更新） → 自動削除（完了マークでストレージから削除）

## 候補日重複ポリシー

- 候補日を割り当てる際に、ほかの Task の `candidate_dates` と被らないかをチェックする。被っている場合は次善の候補を選定する。再割当できない場合、ユーザーに通知して手動調整を促す。
