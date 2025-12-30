import argparse
from src.cli.commands import add, list_cmd, show, update, complete, calendar


def main():
    parser = argparse.ArgumentParser(prog="todo")
    sub = parser.add_subparsers(dest="cmd")

    # add
    p_add = sub.add_parser("add", help="Add a new todo")
    p_add.add_argument("title")
    p_add.add_argument("--deadline", required=True)
    p_add.add_argument("--location", required=True)
    p_add.add_argument("--priority", choices=["高","中","低"], default="中")
    p_add.add_argument("--json", action="store_true")

    # list
    p_list = sub.add_parser("list", help="List todos")
    p_list.add_argument("--month", required=False)
    p_list.add_argument("--json", action="store_true")

    # show
    p_show = sub.add_parser("show", help="Show todo detail")
    p_show.add_argument("id", type=int)

    # update
    p_update = sub.add_parser("update", help="Update todo")
    p_update.add_argument("id", type=int)
    p_update.add_argument("--title")
    p_update.add_argument("--deadline")
    p_update.add_argument("--location")
    p_update.add_argument("--priority", choices=["高","中","低"])

    # complete
    p_complete = sub.add_parser("complete", help="Complete todo")
    p_complete.add_argument("id", type=int)

    # calendar
    p_cal = sub.add_parser("calendar", help="Show calendar")
    p_cal.add_argument("--month", required=True)

    args = parser.parse_args()
    if args.cmd == "add":
        add.handle(args)
    elif args.cmd == "list":
        list_cmd.handle(args)
    elif args.cmd == "show":
        show.handle(args)
    elif args.cmd == "update":
        update.handle(args)
    elif args.cmd == "complete":
        complete.handle(args)
    elif args.cmd == "calendar":
        calendar.handle(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
