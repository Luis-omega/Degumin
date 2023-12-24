from argparse import ArgumentParser
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from Degumin.Common.Error import DeguminError
from Degumin.Common.Loggers import get_logger
from Degumin.Parser.Parser import load_grammar

log = get_logger(__name__)


@dataclass
class CompileModulesArguments:
    symbol_paths: list[Path]
    modules: list[Path]
    output_path: Path


@dataclass
class FormatModulesArguments:
    modules: list[Path]
    just_check: bool
    # TODO: Join output_path and to_console
    output_path: Optional[Path]
    to_console: bool


@dataclass
class GenerateDocumentationArguments:
    symbol_paths: list[Path]
    modules: list[Path]


class ArgumentParserError(DeguminError):
    pass


def generate_argument_parser() -> ArgumentParser:
    parser = ArgumentParser(
        prog="Degumin",
        description="Degumin python compiler",
        epilog="End of help, have a nice day =)",
    )
    subparsers = parser.add_subparsers(
        help="Degumin offers this series of subcommands", dest="sub_parser_name"
    )
    # Format
    parser_format = subparsers.add_parser(
        "format", help="Format files or check if they are formatted"
    )
    parser_format_group = parser_format.add_mutually_exclusive_group()
    parser_format_group.add_argument(
        "-c",
        "--check",
        action="store_false",
        help="Check if files are formatted and report to console",
    )
    parser_format_group.add_argument(
        "-o",
        "--output",
        type=str,
        metavar="PATH",
        help="Output of the formatted code",
    )
    parser_format.add_argument(
        "f",
        nargs="+",
        type=str,
        metavar="PATH",
        help="The path of a folder or file",
    )

    # Compiler
    parser_compiler = subparsers.add_parser("compile", help="Compile files")
    parser_compiler.add_argument(
        "-o",
        "--output",
        type=str,
        default="./distribution",
        metavar="PATH",
        help="Output of the compiled code",
    )
    parser_compiler.add_argument(
        "-p",
        "--paths",
        metavar="PATH",
        nargs="*",
        type=str,
        help="Places to look for packages",
    )
    parser_compiler.add_argument(
        "modules",
        metavar="PATH",
        nargs="+",
        type=str,
        help="File, files,folder or folders to compile",
    )

    return parser


def parse_cli_arguments() -> (
    ArgumentParserError
    | CompileModulesArguments
    | FormatModulesArguments
    | GenerateDocumentationArguments
):
    parser = generate_argument_parser()
    parser_result = parser.parse_args()
    match parser_result.sub_parser_name:
        case "format":
            print("Formatting!")

        case "compile":
            print("Compiling!")
            if parser_result.paths is None:
                symbol_paths = []
            else:
                # TODO: Separete Folders from files
                symbol_paths = [Path(i) for i in parser_result.paths]

            if parser_result.modules is None:
                modules = []
            else:
                # TODO: Separete Folders from files
                modules = [Path(i) for i in parser_result.modules]

            return CompileModulesArguments(
                symbol_paths, modules, parser_result.output
            )

        case _:
            print("Unknow Arguments\nTerminating program\nHave a nice day!")
            exit()


def compile(args: CompileModulesArguments):
    parser = load_grammar()
    csts = [parser.parse(i) for i in args.modules]
    asts = [to_ast(i) for i in csts]
    resolutions = [
        symbol_resolution(i, args.symbol_paths, args.modules) for i in asts
    ]
    typedAsts = [infer(i, j) for i, j in zip(asts, resolutions)]
    cores = [core(i) for i in typedAsts]
    optimizeds = [optimize(i) for i in typedAsts]


def main() -> None:
    arguments = parse_cli_arguments()
    print(arguments)


if __name__ == "__main__":
    main()
