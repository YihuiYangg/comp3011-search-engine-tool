"""Command-line shell for the COMP3011 search engine tool."""

from __future__ import annotations

import argparse
import cmd
import json
from pathlib import Path

from .search import SearchEngine


class SearchShell(cmd.Cmd):
    intro = "COMP3011 Search Tool. Type help or ? to list commands."
    prompt = "> "

    def __init__(self, engine: SearchEngine) -> None:
        super().__init__()
        self.engine = engine

    def do_build(self, arg: str) -> None:
        """build: crawl the website, build the index, and save it."""

        print(
            f"Building index from {self.engine.base_url} "
            f"with {self.engine.delay_seconds:g}s politeness delay..."
        )
        self.engine.build()
        self.engine.save()
        print(
            f"Indexed {self.engine.page_count} pages and "
            f"{len(self.engine.index)} unique terms."
        )
        print(f"Saved index to {self.engine.index_path}")

    def do_load(self, arg: str) -> None:
        """load: load the saved index from the file system."""

        try:
            self.engine.load()
        except FileNotFoundError as exc:
            print(exc)
            return
        print(
            f"Loaded index from {self.engine.index_path}: "
            f"{self.engine.page_count} pages, {len(self.engine.index)} unique terms."
        )

    def do_print(self, arg: str) -> None:
        """print WORD: print the inverted index posting list for WORD."""

        word = arg.strip()
        if not word:
            print("Usage: print <word>")
            return
        try:
            postings = self.engine.print_word(word)
        except ValueError as exc:
            print(exc)
            return

        if not postings:
            print(f"No index entry found for '{word.lower()}'.")
            return
        print(json.dumps(postings, indent=2, sort_keys=True))

    def do_find(self, arg: str) -> None:
        """find QUERY: list pages containing all query terms."""

        query = arg.strip()
        if not query:
            print("Usage: find <word or words>")
            return

        results = self.engine.find(query)
        if not results:
            print(f"No pages found for '{query}'.")
            return

        for rank, result in enumerate(results, start=1):
            print(f"{rank}. score={result['score']} {result['url']}")

    def do_exit(self, arg: str) -> bool:
        """exit: quit the shell."""

        print("Goodbye.")
        return True

    def do_quit(self, arg: str) -> bool:
        """quit: quit the shell."""

        return self.do_exit(arg)

    def emptyline(self) -> None:
        """Do nothing when the user presses Enter on an empty line."""

        return None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="COMP3011 Coursework 2 search tool")
    parser.add_argument("--base-url", default="https://quotes.toscrape.com/")
    parser.add_argument("--index-path", default="data/index.json")
    parser.add_argument(
        "--delay",
        type=float,
        default=6.0,
        help="politeness delay between HTTP requests in seconds; default is 6",
    )
    parser.add_argument("--max-pages", type=int, default=120)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    engine = SearchEngine(
        base_url=args.base_url,
        index_path=Path(args.index_path),
        delay_seconds=args.delay,
        max_pages=args.max_pages,
    )
    SearchShell(engine).cmdloop()


if __name__ == "__main__":
    main()
