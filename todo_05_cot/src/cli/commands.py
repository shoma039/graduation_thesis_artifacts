from typing import Optional
from ..services import storage
from ..services import registration
from . import output
from ..lib.errors import ValidationError
from ..services import geocode


def add(title: str, deadline: Optional[str], place: Optional[str], priority: str = 'medium'):
    try:
        selected_place = None
        if place:
            # attempt disambiguation: fetch multiple candidates
            candidates = geocode.geocode_place(place, limit=5)
            if len(candidates) > 1:
                print(output.info('候補地が複数見つかりました。選択してください:'))
                for i, c in enumerate(candidates, start=1):
                    print(output.line(f"{i}. {c.get('display_name')} (lat={c.get('lat')}, lon={c.get('lon')}) tz={c.get('timezone') or '-'}"))
                try:
                    sel = int(input('番号を入力: ').strip())
                    if 1 <= sel <= len(candidates):
                        selected_place = candidates[sel-1]
                except Exception:
                    print(output.info('無効な入力、最初の候補を使用します'))
            elif len(candidates) == 1:
                selected_place = candidates[0]

        tid, loc = registration.register_task(title=title, deadline_text=deadline, place_query=place, priority=priority, place_candidate=selected_place)
        print(output.success(f"タスクを追加しました: id={tid} 場所={loc.get('display_name') if loc else '-'}"))
    except ValidationError as e:
        print(output.error(f"入力エラー: {e}"))
    except Exception as e:
        print(output.error(f"エラー: {e}"))


def list_tasks():
    rows = storage.list_tasks()
    if not rows:
        print(output.info('未完了のタスクはありません'))
        return
    for r in rows:
        print(output.line(f"{r['id']}: {r['title']} (優先度={r['priority']}) 期限={r.get('deadline') or '-'} 場所={r.get('display_name') or '-'}"))


def detail(task_id: int):
    r = storage.get_task(task_id)
    if not r:
        print(output.error('指定されたタスクが見つかりません'))
        return
    print(output.info('--- タスク詳細 ---'))
    print(output.line(f"id: {r['id']}"))
    print(output.line(f"title: {r['title']}"))
    print(output.line(f"priority: {r['priority']}"))
    print(output.line(f"deadline: {r.get('deadline')}"))
    print(output.line(f"place: {r.get('display_name')} ({r.get('lat')},{r.get('lon')}) tz={r.get('timezone')}"))


def complete(task_id: int):
    storage.mark_task_complete(task_id)
    print(output.success('タスクを完了（削除）しました'))


def update(task_id: int, title: Optional[str], deadline: Optional[str], place: Optional[str], priority: Optional[str] = None):
    try:
        place_candidate = None
        place_id = None
        if place:
            candidates = geocode.geocode_place(place, limit=5)
            if len(candidates) > 1:
                print(output.info('候補地が複数見つかりました。選択してください:'))
                for i, c in enumerate(candidates, start=1):
                    print(output.line(f"{i}. {c.get('display_name')} (lat={c.get('lat')}, lon={c.get('lon')}) tz={c.get('timezone') or '-'}"))
                try:
                    sel = int(input('番号を入力: ').strip())
                    if 1 <= sel <= len(candidates):
                        place_candidate = candidates[sel-1]
                except Exception:
                    print(output.info('無効な入力、最初の候補を使用します'))
            elif len(candidates) == 1:
                place_candidate = candidates[0]

        # If deadline provided and place_candidate has timezone, parse to iso
        deadline_iso = None
        if deadline:
            tz = place_candidate.get('timezone') if place_candidate else None
            from ..services import date_parser
            tzname = tz or 'UTC'
            parsed = date_parser.parse_natural_date_iso(deadline, tzname)
            if parsed is None:
                print(output.error('期限の解析に失敗しました'))
                return
            deadline_iso = parsed

        # ensure place saved if provided
        place_id = None
        if place_candidate:
            place_id = storage.insert_location(place_candidate.get('display_name'), place_candidate.get('lat'), place_candidate.get('lon'), place_candidate.get('timezone') or 'UTC')

        storage.update_task(task_id, title, priority, place_id, deadline_iso)
        print(output.success('タスクを更新しました'))
    except Exception as e:
        print(output.error(f'更新に失敗しました: {e}'))


def confirm_candidate(candidate_id: int):
    try:
        # set as confirmed
        storage.set_candidate_confirmed(candidate_id, 1)
        print(output.success('候補日を確定しました'))
    except Exception as e:
        print(output.error(f'確定に失敗しました: {e}'))


def schedule(task_id: Optional[int] = None):
    # if task_id is None, schedule for all tasks
    if task_id is None:
        tasks = storage.list_tasks()
        results = {}
        for t in tasks:
            res = __schedule_single(t['id'])
            results[t['id']] = res
        print(output.info(f"スケジュールを実行しました: {results}"))
        return
    res = __schedule_single(task_id)
    print(output.info(f"スケジュール結果: {res}"))


def __schedule_single(task_id: int):
    from ..services import scheduler
    return scheduler.generate_candidates_for_task(task_id, max_candidates=3)
