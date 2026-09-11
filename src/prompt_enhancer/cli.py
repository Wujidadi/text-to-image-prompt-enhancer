import argparse
import sys

from . import DEFAULT_PRESET, Enhancer, PromptEnhancerError, __version__, list_presets, load_config
from .prompt import LANGUAGE_DIRECTIVES

PROG = "prompt-enhancer"


def die(message):
    print(f"{PROG}: {message}", file=sys.stderr)
    sys.exit(1)


def is_comment_line(line):
    stripped = line.lstrip()
    return (stripped == "#"
            or stripped.startswith("# ")
            or stripped.startswith("//"))


def read_prompt_file(path):
    try:
        with open(path, encoding="utf-8") as f:
            lines = f.read().splitlines()
    except OSError as e:
        die(f"cannot read prompt file: {e}")
    return "\n".join(l for l in lines if not is_comment_line(l))


def build_parser():
    parser = argparse.ArgumentParser(
        prog=PROG,
        description="Enhance a text-to-image / video prompt with an LLM. "
                    "The prompt is read from the argument, or from stdin "
                    "when omitted; the enhanced prompt is printed to stdout.")
    parser.add_argument("text", nargs="?", help="prompt text (default: stdin)")
    parser.add_argument("--file", "-f", metavar="<file>",
                        help="read the prompt from a UTF-8 file instead; lines "
                             'that are "#" alone or start with "# " or "//" '
                             "(after indentation) are comments and dropped")
    parser.add_argument("--preset", "-p", metavar="<name>",
                        help="enhancer preset: a name (subdirectories allowed) "
                             "searched under --preset-dir, the user directory "
                             "and the bundled presets, or a plain path; "
                             f"default {DEFAULT_PRESET} unless --instruction "
                             "alone is given")
    parser.add_argument("--instruction", "-i", metavar="<text>",
                        help="ad-hoc instruction; with --preset it is appended "
                             "to the preset, alone it enables custom mode")
    parser.add_argument("--language", "-l", choices=sorted(LANGUAGE_DIRECTIVES),
                        metavar="<lang>",
                        help="output language: en or zh (Simplified Chinese); "
                             "overrides the config file, default en")
    parser.add_argument("--provider", "-P", metavar="<name>",
                        help="provider profile from the config file "
                             "(default: default_provider, else ollama)")
    parser.add_argument("--type", metavar="<type>",
                        help="override the provider type "
                             "(ollama, openai, wavespeed, anthropic)")
    parser.add_argument("--model", "-m", metavar="<name>",
                        help="override the provider's model")
    parser.add_argument("--url", metavar="<url>",
                        help="override the provider's endpoint URL")
    parser.add_argument("--preset-dir", metavar="<dir>", action="append", default=[],
                        help="extra preset directory searched first (repeatable)")
    parser.add_argument("--config", metavar="<file>",
                        help="config file (default: $PROMPT_ENHANCER_CONFIG or "
                             "~/.config/prompt-enhancer/config.toml)")
    parser.add_argument("--show-system", action="store_true",
                        help="print the assembled system instruction to stderr")
    parser.add_argument("--quiet", "-q", action="store_true",
                        help="suppress the progress line on stderr")
    parser.add_argument("--list-presets", action="store_true",
                        help="list visible presets and exit")
    parser.add_argument("--list-providers", action="store_true",
                        help="list provider profiles and exit")
    parser.add_argument("--version", action="version", version=f"{PROG} {__version__}")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    if args.file is not None and args.text is not None:
        die("give the prompt as text or --file, not both")
    try:
        if args.list_presets:
            config = load_config(args.config)
            for preset in list_presets(list(args.preset_dir) + config.preset_dirs):
                flag = "  [fixed-language]" if preset.fixed_language else ""
                print(f"{preset.name}\t{preset.path}{flag}")
            return
        if args.list_providers:
            config = load_config(args.config)
            for name in sorted(config.providers):
                s = config.providers[name]
                mark = "*" if name == config.default_provider else " "
                print(f"{mark} {name}\t{s.get('type')}\t{s.get('model', '')}"
                      f"\t{s.get('url', '')}")
            return
        overrides = {k: v for k, v in
                     (("type", args.type), ("model", args.model), ("url", args.url))
                     if v is not None}
        enhancer = Enhancer.from_config(args.provider, overrides,
                                        language=args.language,
                                        preset_dirs=args.preset_dir,
                                        config_path=args.config)
        if args.file is not None:
            text = read_prompt_file(args.file)
        elif args.text is not None:
            text = args.text
        else:
            text = sys.stdin.read()
        text = text.strip()
        if not text:
            die("empty prompt")
        preset = args.preset
        if preset is None and not args.instruction:
            preset = DEFAULT_PRESET
        if args.show_system:
            system, _, _ = enhancer.prepare(preset, args.instruction, args.language)
            print(system, file=sys.stderr)
        if not args.quiet:
            source = f"preset {preset}" if preset else "custom instruction"
            print(f"{PROG}: enhancing ({enhancer.provider.describe()}, {source})...",
                  file=sys.stderr)
        print(enhancer.enhance(text, preset=preset, instruction=args.instruction,
                               language=args.language))
    except PromptEnhancerError as e:
        die(str(e))


if __name__ == "__main__":
    main()
