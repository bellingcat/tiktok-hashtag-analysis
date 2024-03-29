from tiktok_hashtag_analysis.base import TikTokDownloader, load_hashtags_from_file


def test_scrape(tmp_path, hashtags):
    downloader = TikTokDownloader(hashtags=hashtags[:1], data_dir=tmp_path)
    downloader.run(
        limit=10, download=True, plot=True, table=True, number=5, headed=True
    )


def test_scrape_headless(tmp_path, hashtags):
    downloader = TikTokDownloader(hashtags=hashtags[:1], data_dir=tmp_path)
    downloader.run(
        limit=10, download=True, plot=True, table=True, number=5, headed=False
    )


def test_load_hashtags_from_file(tmp_path, hashtags):
    file = tmp_path / "hashtags.txt"
    with open(file, "w", encoding="utf-8") as f:
        f.write("\n".join(hashtags))

    loaded_hashtags = load_hashtags_from_file(file=file)
    assert loaded_hashtags == hashtags
