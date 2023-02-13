import logging, argparse
from .file_methods import log_writer
from .run_downloader import * # Import everything from run_downloader.py
from .hashtag_frequencies import * # Import everything from hashtag_frequencies.py

logger = logging.getLogger()


def create_parser() -> argparse.ArgumentParser:
    """Create the parser and the arguments for the user input."""
    parser = argparse.ArgumentParser(description="Analyze hashtags within posts scraped from TikTok.")
    parser.add_argument("command", help="command to initialize", choices=['download', 'frequencies'])
    parser.add_argument("-t", type=str, nargs="*", help="List of hashtags to scrape (module: run_downloader)")
    parser.add_argument("-f", type=str, help="File name containing list of hashtags to scrape (module: run_downloader)")
    parser.add_argument("-p", action="store_true", help="Download post data (module: run_downloader)")
    parser.add_argument("-v", action="store_true", help="Download video files (module: run_downloader)")
    parser.add_argument("-ht", "--hashtag", type=str,
                        help="The hashtag of scraped posts to analyze (module: hashtag_frequencies)", )
    parser.add_argument("-n", "--number", type=int, help="The number of top n occurrences (module: hashtag_frequencies)")
    parser.add_argument("-plt", "--plot", help="Plot the occurrences (module: hashtag_frequencies)", action="store_true")
    parser.add_argument("-d", "--print", help="List top n hashtags (module: hashtag_frequencies)", action="store_true")
    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()
    if args.command == "download":
        if not (args.t or args.f):
            parser.error(
                "No hashtags were given, please use either the `-t` flag or the `-f` flag to specify one or more hashtags.")

        if not (args.p or args.v):
            parser.error(
                "No argument given, please specify either the `-p` flag to download post data or the `-v` flag to download video files, or both."
            )

        if args.t:
            hashtags = args.t
        elif args.f:
            file_name = args.f
            hashtags = get_hashtag_list(file_name)

        logger.info(f"Hashtags to scrape: {hashtags}")
        if not hashtags:
            raise ValueError(
                "No hashtags were specified: please use either the `-t` flag to specify a sspace-separated list of one or more hashtags as a command-line argument, or use the `-f` flag to specify a text file of newline-separated hashtags.")

        download_data_type = {"posts": args.p, "videos": args.v}

        scraped_summary_list = get_data(hashtags, download_data_type)
        if scraped_summary_list:
            log_writer(scraped_summary_list)
    elif args.command == "frequencies":
        img_folder = IMAGES
        check_file(img_folder, "dir")
        if args.n < 1:
            raise ValueError(
                f"Specified argument `n` (the number of hashtags to analyze) must be greater than zero, not: {args.n}.")
        input_file = data_file = os.path.join(
            FILES["data"], args.hashtag, FILES["posts"], FILES["data_file"]
        )
        if not check_existence(input_file, "file"):
            raise FileNotFoundError(
                f"File ({input_file}) for specified argument `hashtag` ({args.hashtag}) does not exist.")

        # base = os.path.splitext(input_file)[0]
        # path = f"./{base}_sorted_hashtags.csv"
        occs = get_occurrences(input_file, args.n)
        if args.plot:
            plot(occs, img_folder)
        else:
            print_occurrences(occs)

if __name__=="__main__":
    main()