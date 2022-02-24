"""Step parsers."""
from __future__ import annotations

import re as base_re
from typing import Any, Dict, cast

import parse as base_parse
from parse_type import cfparse as base_cfparse


class StepParser:
    """Parser of the individual step."""

    def __init__(self, name: str) -> None:
        self.name = name

    def parse_arguments(self, name):
        """Get step arguments from the given step name.

        :return: `dict` of step arguments
        """
        raise NotImplementedError()  # pragma: no cover

    def is_matching(self, name):
        """Match given name with the step name."""
        raise NotImplementedError()  # pragma: no cover


class re(StepParser):
    """Regex step parser."""

    def __init__(self, name: str, *args: Any, **kwargs: Any) -> None:
        """Compile regex."""
        super().__init__(name)
        self.regex = base_re.compile(self.name, *args, **kwargs)

    def parse_arguments(self, name: str) -> Dict[str, str]:
        """Get step arguments.

        :return: `dict` of step arguments
        """
        # TODO: This is a potential bug, as groupdict can return None (found with typing)
        return self.regex.match(name).groupdict()

    def is_matching(self, name: str) -> bool:
        """Match given name with the step name."""
        return bool(self.regex.match(name))


class parse(StepParser):
    """parse step parser."""

    def __init__(self, name: str, *args: Any, **kwargs: Any) -> None:
        """Compile parse expression."""
        super().__init__(name)
        self.parser = base_parse.compile(self.name, *args, **kwargs)

    def parse_arguments(self, name: str) -> Dict[str, Any]:
        """Get step arguments.

        :return: `dict` of step arguments
        """
        return cast(Dict[str, Any], self.parser.parse(name).named)

    def is_matching(self, name: str) -> bool:
        """Match given name with the step name."""
        try:
            return bool(self.parser.parse(name))
        except ValueError:
            return False


class cfparse(parse):
    """cfparse step parser."""

    def __init__(self, name: str, *args: Any, **kwargs: Any) -> None:
        """Compile parse expression."""
        super(parse, self).__init__(name)
        self.parser = base_cfparse.Parser(self.name, *args, **kwargs)


class string(StepParser):
    """Exact string step parser."""

    def __init__(self, name: str) -> None:
        """Stringify"""
        name = str(name)
        super().__init__(name)

    def parse_arguments(self, name: str) -> Dict:
        """No parameters are available for simple string step.

        :return: `dict` of step arguments
        """
        return {}

    def is_matching(self, name: str) -> bool:
        """Match given name with the step name."""
        return self.name == name


def get_parser(step_name: Any) -> Any:
    """Get parser by given name.

    :param step_name: name of the step to parse

    :return: step parser object
    :rtype: StepArgumentParser
    """

    support_parser_interface = hasattr(step_name, "is_matching") and hasattr(step_name, "parse_arguments")

    if support_parser_interface:
        return step_name
    else:
        return string(step_name)
