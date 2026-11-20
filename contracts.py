import argparse
import json
from datetime import date
from pathlib import Path


def parse_date(value):
    try:
        parsed = date.fromisoformat(value)
        if parsed.isoformat() != value:
            raise ValueError
        return parsed
    except ValueError:
        raise argparse.ArgumentTypeError("Укажите дату в формате ГГГГ-ММ-ДД") from None


def main():
    parser = argparse.ArgumentParser(description="Контроль исполнения договоров")
    parser.add_argument("--file", type=Path, default=Path("contracts.json"))
    commands = parser.add_subparsers(dest="command", required=True)

    new_contract = commands.add_parser("add-contract", help="Добавить договор")
    new_contract.add_argument("number")
    new_contract.add_argument("party")

    new_item = commands.add_parser("add-obligation", help="Добавить обязательство")
    new_item.add_argument("number")
    new_item.add_argument("item")
    new_item.add_argument("title")
    new_item.add_argument("owner")
    new_item.add_argument("due", type=parse_date)

    close = commands.add_parser("close", help="Отметить выполнение")
    close.add_argument("number")
    close.add_argument("item")

    report = commands.add_parser("report", help="Показать договоры и обязательства")
    report.add_argument("--as-of", type=parse_date, default=date.today())
    args = parser.parse_args()

    registry = {}
    if args.file.exists():
        try:
            registry = json.loads(args.file.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            parser.error("Не удалось прочитать файл реестра")

    if args.command == "report":
        if not registry:
            print("Реестр пуст.")
        for number, contract in sorted(registry.items()):
            print(f"{number} | {contract['party']}")
            for item, obligation in sorted(contract["obligations"].items()):
                if obligation["done"]:
                    status = "Выполнено"
                elif date.fromisoformat(obligation["due"]) < args.as_of:
                    status = "Просрочено"
                elif date.fromisoformat(obligation["due"]) == args.as_of:
                    status = "Срок сегодня"
                else:
                    status = "В работе"
                print(f"  {item} | {obligation['title']} | {obligation['owner']} | {obligation['due']} | {status}")
        return

    if args.command == "add-contract":
        if args.number in registry:
            parser.error("Договор с таким номером уже существует")
        registry[args.number] = {"party": args.party, "obligations": {}}
    else:
        if args.number not in registry:
            parser.error("Договор не найден")
        obligations = registry[args.number]["obligations"]
        if args.command == "add-obligation":
            if args.item in obligations:
                parser.error("Обязательство с таким номером уже существует")
            obligations[args.item] = {
                "title": args.title,
                "owner": args.owner,
                "due": args.due.isoformat(),
                "done": False,
            }
        else:
            if args.item not in obligations:
                parser.error("Обязательство не найдено")
            if obligations[args.item]["done"]:
                parser.error("Обязательство уже выполнено")
            obligations[args.item]["done"] = True

    temporary = args.file.with_name(args.file.name + ".tmp")
    try:
        temporary.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        temporary.replace(args.file)
    except OSError:
        parser.error("Не удалось сохранить реестр")
    print("Реестр сохранён.")


if __name__ == "__main__":
    main()
