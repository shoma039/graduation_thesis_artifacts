import argparse
from . import commands as cli_commands


def main():
    parser = argparse.ArgumentParser(prog='todo')
    sub = parser.add_subparsers(dest='cmd')

    p_add = sub.add_parser('add')
    p_add.add_argument('title')
    p_add.add_argument('--priority', default='medium')
    p_add.add_argument('--place', default=None)
    p_add.add_argument('--deadline', default=None)
    p_add.set_defaults(func=lambda args: cli_commands.add(args.title, args.deadline, args.place, args.priority))

    p_list = sub.add_parser('list')
    p_list.set_defaults(func=lambda args: cli_commands.list_tasks())

    p_detail = sub.add_parser('detail')
    p_detail.add_argument('id', type=int)
    p_detail.set_defaults(func=lambda args: cli_commands.detail(args.id))

    p_complete = sub.add_parser('complete')
    p_complete.add_argument('id', type=int)
    p_complete.set_defaults(func=lambda args: cli_commands.complete(args.id))

    p_update = sub.add_parser('update')
    p_update.add_argument('id', type=int)
    p_update.add_argument('--title', default=None)
    p_update.add_argument('--priority', default=None)
    p_update.add_argument('--place', default=None)
    p_update.add_argument('--deadline', default=None)
    p_update.set_defaults(func=lambda args: cli_commands.update(args.id, args.title, args.deadline, args.place, args.priority))

    p_calendar = sub.add_parser('calendar')
    p_calendar.add_argument('--month', required=True, help='YYYY-MM')
    p_calendar.set_defaults(func=lambda args: __run_calendar(args.month))

    p_confirm = sub.add_parser('confirm')
    p_confirm.add_argument('candidate_id', type=int)
    p_confirm.set_defaults(func=lambda args: cli_commands.confirm_candidate(args.candidate_id))

    def __run_calendar(month):
        from . import calendar as cal
        cal.month_view(month)

    p_schedule = sub.add_parser('schedule')
    p_schedule.add_argument('--task-id', type=int, default=None)
    p_schedule.set_defaults(func=lambda args: cli_commands.schedule(args.task_id))

    args = parser.parse_args()
    if not hasattr(args, 'func'):
        parser.print_help()
        return
    args.func(args)


if __name__ == '__main__':
    main()
