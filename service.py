from scraper import (
    extract_about,
    extract_policies,
    extract_contact,
    extract_socials,
    extract_faqs,
    extract_products,
    extract_hero_products,
    extract_links,
    fetch_page,
)
from urllib.parse import urlparse
import re

# ---------------- Fetch insights for a single brand ----------------
def fetch_brand_insights(base_url: str):
    """
    Fetch all insights for a Shopify brand.
    Includes: about, policies, contact, socials, FAQs, products (with images), hero products, and links.
    """
    return {
        "brand_name": base_url,
        "about": extract_about(base_url),
        "policies": extract_policies(base_url),
        "contact_details": extract_contact(base_url),
        "social_handles": extract_socials(base_url),
        "faqs": extract_faqs(base_url),
        "products": extract_products(base_url),            # ✅ includes image_url, product_url, price
        "hero_products": extract_hero_products(base_url),  # ✅ includes image_url, product_url
        "important_links": extract_links(base_url),
    }

# ---------------- Static competitor mapping ----------------
competitor_map = {
    "memy.co.in": [
        "hairoriginals.com",
        "thelabelelement.com"
    ],
    # Extend with more if needed
}

# ---------------- Dynamic competitor discovery ----------------
def discover_competitors(base_url: str, limit: int = 5):
    """
    Try to dynamically discover competitor Shopify stores by scanning outbound links.
    Only returns domains that look like Shopify stores.
    """
    discovered = []
    soup = fetch_page(base_url)
    if not soup:
        return discovered

    for a in soup.find_all("a", href=True):
        href = a["href"]
        # must be an absolute link
        if not href.startswith("http"):
            continue
        domain = urlparse(href).netloc.lower()

        # skip self
        if base_url in domain:
            continue

        # very naive Shopify detection
        if ("myshopify.com" in domain) or re.search(r"\.com$", domain):
            if domain not in discovered:
                discovered.append(domain)

        if len(discovered) >= limit:
            break

    return discovered

# ---------------- Competitor fetcher ----------------
def fetch_competitors(base_url: str):
    """
    Fetch insights for given store + competitors.
    First tries static competitor_map, falls back to dynamic discovery.
    """
    results = []

    # static
    if base_url in competitor_map:
        sites = [base_url] + competitor_map[base_url]
    else:
        # fallback: discover dynamically
        dynamic_sites = discover_competitors(base_url)
        sites = [base_url] + dynamic_sites

    for site in sites:
        try:
            results.append(fetch_brand_insights(site))
        except Exception as e:
            results.append({
                "brand_name": site,
                "error": str(e)
            })

    return results
