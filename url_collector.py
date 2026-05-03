import urllib.request
import csv
import io


def collect_urls():

    # Step 1: Download the CSV
    url = "https://data.phishtank.com/data/online-valid.csv"
    print("[1] Downloading PhishTank data...")

    with urllib.request.urlopen(url) as response:
        raw_data = response.read().decode("utf-8")

    print("    Done downloading!")

    # Step 2: Parse the CSV
    print("[2] Reading the CSV file...")
    reader = csv.DictReader(io.StringIO(raw_data))

    # Step 3: Filter verified URLs only
    print("[3] Filtering verified entries...")
    verified_urls = []

    for row in reader:
        if row["verified"] == "yes":
            verified_urls.append(row["url"])

    print(f"    Found {len(verified_urls)} verified URLs")

    # Step 4: Remove duplicates
    print("[4] Removing duplicates...")
    unique_urls = list(set(verified_urls))
    print(f"    {len(unique_urls)} unique URLs remaining")

    return unique_urls


# Run it
if __name__ == "__main__":
    urls = collect_urls()

    print("\n── First 10 URLs ──")
    for u in urls[:10]:
        print(u)