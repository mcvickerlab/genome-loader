from pathlib import Path
import sys
import argparse

def parse_writefasta(args):
    from genome_loader.write_h5 import write_genome_seq, write_encoded_genome

    if args.encode:
        write_encoded_genome(args.input, args.directory, h5_name=args.name,
                             chrom_list=args.chroms, encode_spec=args.spec)
    else:
        write_genome_seq(args.input, args.directory,
                         h5_name=args.name, chrom_list=args.chroms)


def parse_writefrag(args):
    from genome_loader.write_h5 import write_frag_depth
    offset_tn5 = not args.ignore_offset # Negate args.ignore_offset

    write_frag_depth(args.input, args.directory,
                     h5_name=args.name, chrom_list=args.chroms, 
                     chrom_lens=args.lens, offset_tn5=offset_tn5, 
                     count_method=args.method)


def parse_writecoverage(args):
    from genome_loader.write_h5 import write_allele_coverage
    write_allele_coverage(args.input, args.directory,
                          h5_name=args.name, chrom_list=args.chroms)


def validate_args(args):

    if args.output:
        args.directory = str(Path(args.output).parent)
        args.name = str(Path(args.output).name)

    elif not args.name:
        args.name = f"{Path(args.input).stem.split('.')[0]}.h5"

    # Validate file extension
    valid_suffixes = [".h5", ".hdf5", ".hdf", ".he5"]
    if "".join(Path(args.name).suffixes).lower() not in valid_suffixes:
        args.name = f"{Path(args.name).stem.split('.')[0]}.h5"

    # Validate writefasta
    if args.command == "writefasta":
        if args.spec:

            if not args.encode:
                return f"Encoding specification given without --encode flag!"

            if not (args.spec).isalpha():
                return f"Spec: '{args.spec}' contains non-characters!"

            if len(set(args.spec)) != len(args.spec):
                return f"Spec: '{args.spec}' can't contain duplicate characters!"

    # Validate writefrag
    if args.command == "writefrag":

        if args.lens:
            if not args.chroms:
                print("WARNING: Lengths ignored, provided w/o chroms")
            elif len(args.chroms) != len(args.lens):
                return f"Number of chroms({len(args.chroms)}) and lengths don't match({len(args.lens)})"

    return args


def parse_cmd():
    parent_parser = argparse.ArgumentParser(add_help=False)

    out_parser = parent_parser.add_mutually_exclusive_group(required=True)
    out_parser.add_argument("-o", "--output", help="Output h5 file and path")
    out_parser.add_argument("-d", "--directory", help="Output directory")

    parent_parser.add_argument("-n", "--name",
                               help="Output file if --directory given, ignored if using --output flag. Defaults to input name")

    parser = argparse.ArgumentParser()

    # Subparser options
    subparser = parser.add_subparsers(dest="command")

    # Parser for writing fasta to H5
    writefa_parser = subparser.add_parser(
        "writefasta", parents=[parent_parser])
    writefa_parser.add_argument("input", help="Fasta file to write to H5")

    writefa_parser.add_argument("-c", "--chroms", "--contigs",
                                nargs="*", help="Chromosomes to write. Writes all by default")
    writefa_parser.add_argument("-e", "--encode", "--onehot",
                                action="store_true", help="Write onehot-encoded genome")
    writefa_parser.add_argument("-s", "--spec", "--order", type=str,
                                help="Ordered string of non-repeating chars. Denotes encoded bases and order (ie: ACGT, Default: ACGTN)")

    # Parsers for writing BAM to H5
    frag_parser = subparser.add_parser("writefrag", parents=[parent_parser])
    frag_parser.add_argument("input", help="BAM file to write to H5")

    frag_parser.add_argument("-c", "--chroms", "--contigs", nargs="*",
                             help="Chromosomes to write. Writes all by default")
    frag_parser.add_argument("-l", "--lens", "--lengths", "--chromlens", type=int,
                             nargs="*", help="Lengths of provided chroms (Auto retrieved if not provided)")
    frag_parser.add_argument("--ignore_offset", action='store_true',
                             help="Don't offset tn5 cutsites")
    frag_parser.add_argument("-m", "--method", "--count_method", type=str,
                             choices=["cutsite", "midpoint", "fragment"], default="cutsite",
                             help="Counting method, Choose from 'cutsite', 'midpoint, 'fragment'")

    cover_parser = subparser.add_parser("writecoverage", parents=[parent_parser])
    cover_parser.add_argument("input", help="BAM file to write to H5")
    cover_parser.add_argument("-c", "--chroms", "--contigs", nargs="*",
                              help="Chromosomes to write. Writes all by default")

    args = parser.parse_args()

    # Validate arguments
    validate_out = validate_args(args)

    if isinstance(validate_out, str):
        parser.error(validate_out)
    else:
        args = validate_out

    return args


def run(args):
    command = args.command

    func_dict = {"writefasta": parse_writefasta,
                 "writefrag": parse_writefrag,
                 "writecoverage": parse_writecoverage}

    func_dict[command](args)


def main():
    root_dir = Path(__file__).parent
    sys.path.append(str(root_dir / "genome_loader"))

    args = parse_cmd()

    # print(args) # Show Input values
    # print()

    run(args)


if __name__ == '__main__':
    main()