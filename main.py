import urllib.parse
import webbrowser
from bs4 import BeautifulSoup
import requests

# Standard browser user-agent to prevent getting blocked by websites
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}

# Source configurations: base search URL and target HTML classes
SOURCES = [
    {
        "name": "Golden Audiobooks",
        "search_url": "https://goldenaudiobooks.com/?s=",
        "tag": "h2",
        "class": "entry-title",
    },
    {
        "name": "Find Audiobook",
        "search_url": "https://findaudiobook.com/?s=",
        "tag": "h2",
        "class": "entry-title post-title",
    },
    {
        "name": "Full Length Audiobooks",
        "search_url": "https://fulllengthaudiobooks.com/?s=",
        "tag": "h2",
        "class": "entry-title post-title",
    },
    {
        "name": "101 Audiobooks",
        "search_url": "https://101audiobooks.net/?s=",
        "tag": "h2",
        "class": "entry-title",
    },
]


def search_source(source: dict, query: str) -> list[dict]:
    """Scrapes audiobook titles and links from a single source."""
    encoded_query = urllib.parse.quote_plus(query)
    target_url = source["search_url"] + encoded_query
    results = []

    try:
        response = requests.get(target_url, headers=HEADERS, timeout=8)
        if response.status_code != 200:
            return results

        soup = BeautifulSoup(response.content, "html.parser")
        items = soup.find_all(source["tag"], class_=source["class"])

        for item in items:
            link_tag = item.find("a")
            if link_tag and link_tag.get("href"):
                title = link_tag.get_text(strip=True)
                url = link_tag["href"]
                results.append(
                    {"title": title, "url": url, "source": source["name"]}
                )

    except requests.RequestException:
        # Gracefully handle connection issues or timeouts per source
        pass

    return results


def search_all_audiobooks(query: str) -> list[dict]:
    """Aggregates results across all configured audiobook platforms."""
    all_results = []
    print(f"\n🔍 Searching for '{query}' across multiple sources...")

    for src in SOURCES:
        source_results = search_source(src, query)
        all_results.extend(source_results)

    return all_results


def main():
    query = input("Enter audiobook title to search: ").strip()
    if not query:
        print("Search query cannot be empty.")
        return

    results = search_all_audiobooks(query)

    if not results:
        print("No audiobooks found. Please try a different title or check your connection.")
        return

    print(f"\nFound {len(results)} results:\n")
    for idx, item in enumerate(results, start=1):
        print(f"[{idx}] {item['title']} ({item['source']})")

    while True:
        choice = input(
            f"\nSelect a number (1-{len(results)}) to open in browser (or 'q' to quit): "
        ).strip()
        if choice.lower() == "q":
            break

        if choice.isdigit() and 1 <= int(choice) <= len(results):
            selected = results[int(choice) - 1]
            print(f"Opening: {selected['url']}")
            webbrowser.open(selected["url"], new=2)
            break
        else:
            print("Invalid selection. Please enter a valid number.")


if __name__ == "__main__":
    main()
