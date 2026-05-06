from pathlib import Path

from src.main import SearchShell


class FakeEngine:
    def __init__(self):
        self.base_url = "https://quotes.toscrape.com/"
        self.delay_seconds = 0
        self.index_path = Path("data/index.json")
        self.page_count = 2
        self.index = {"love": {"https://quotes.toscrape.com/": {"frequency": 1, "positions": [3]}}}
        self.built = False
        self.saved = False
        self.load_should_fail = False

    def build(self):
        self.built = True

    def save(self):
        self.saved = True

    def load(self):
        if self.load_should_fail:
            raise FileNotFoundError("Index file not found")

    def print_word(self, word):
        if word == "bad input":
            raise ValueError("Only one word can be printed")
        return self.index.get(word.lower(), {})

    def find(self, query):
        if query == "missing":
            return []
        return [{"url": "https://quotes.toscrape.com/", "score": 4}]


def test_build_command_calls_engine_and_save(capsys):
    engine = FakeEngine()
    shell = SearchShell(engine)

    shell.do_build("")

    output = capsys.readouterr().out
    assert engine.built is True
    assert engine.saved is True
    assert "Indexed 2 pages" in output
    assert "Saved index" in output


def test_load_command_success(capsys):
    shell = SearchShell(FakeEngine())

    shell.do_load("")

    output = capsys.readouterr().out
    assert "Loaded index" in output
    assert "2 pages" in output


def test_load_command_handles_missing_index(capsys):
    engine = FakeEngine()
    engine.load_should_fail = True
    shell = SearchShell(engine)

    shell.do_load("")

    output = capsys.readouterr().out
    assert "Index file not found" in output


def test_print_command_requires_word(capsys):
    shell = SearchShell(FakeEngine())

    shell.do_print("")

    assert "Usage: print <word>" in capsys.readouterr().out


def test_print_command_outputs_postings(capsys):
    shell = SearchShell(FakeEngine())

    shell.do_print("love")

    output = capsys.readouterr().out
    assert "frequency" in output
    assert "positions" in output
    assert "https://quotes.toscrape.com/" in output


def test_print_command_handles_missing_word(capsys):
    shell = SearchShell(FakeEngine())

    shell.do_print("unknown")

    assert "No index entry found" in capsys.readouterr().out


def test_print_command_handles_invalid_input(capsys):
    shell = SearchShell(FakeEngine())

    shell.do_print("bad input")

    assert "Only one word can be printed" in capsys.readouterr().out


def test_find_command_requires_query(capsys):
    shell = SearchShell(FakeEngine())

    shell.do_find("")

    assert "Usage: find <word or words>" in capsys.readouterr().out


def test_find_command_outputs_ranked_results(capsys):
    shell = SearchShell(FakeEngine())

    shell.do_find("love")

    output = capsys.readouterr().out
    assert "1. score=4" in output
    assert "https://quotes.toscrape.com/" in output


def test_find_command_handles_no_results(capsys):
    shell = SearchShell(FakeEngine())

    shell.do_find("missing")

    assert "No pages found" in capsys.readouterr().out


def test_exit_and_quit_commands(capsys):
    shell = SearchShell(FakeEngine())

    assert shell.do_exit("") is True
    assert "Goodbye." in capsys.readouterr().out
    assert shell.do_quit("") is True


def test_emptyline_does_nothing():
    shell = SearchShell(FakeEngine())

    assert shell.emptyline() is None
