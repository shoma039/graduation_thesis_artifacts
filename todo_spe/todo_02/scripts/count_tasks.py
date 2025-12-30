from pathlib import Path
p = Path('specs/001-todo-weather-scheduler/tasks.md')
text = p.read_text(encoding='utf-8')
lines = [l.strip() for l in text.splitlines() if l.strip().startswith('- [')]
completed = [l for l in lines if l.startswith('- [x]')]
open_tasks = [l for l in lines if l.startswith('- [ ]')]
print('total_checklist_items:', len(lines))
print('completed:', len(completed))
print('open:', len(open_tasks))

# Count per story
from collections import defaultdict
per_story = defaultdict(int)
for l in lines:
    # extract [USn] if present
    if '[US' in l:
        start = l.find('[US')
        end = l.find(']', start)
        tag = l[start:end+1]
    else:
        tag = 'NO_STORY'
    per_story[tag] += 1

print('per_story:')
for k,v in per_story.items():
    print(f'  {k}: {v}')
