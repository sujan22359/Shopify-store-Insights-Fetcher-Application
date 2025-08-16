import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


# ---------------- Helpers ----------------
def clean_html(raw_html: str) -> str:
    """Remove HTML tags and return plain text"""
    if not raw_html:
        return ""
    return BeautifulSoup(raw_html, "html.parser").get_text(" ", strip=True)


def _normalize_url(base_url: str) -> str:
    if not base_url.startswith(("http://", "https://")):
        return "http://" + base_url
    return base_url


def _abs(base_url: str, href: str | None) -> str:
    if not href:
        return ""
    return urljoin(base_url, href)


# ---------------- Networking ----------------
def fetch_page(base_url: str, path: str = ""):
    try:
        base_url = _normalize_url(base_url)
        full_url = urljoin(base_url, path)
        resp = requests.get(full_url, timeout=12)
        if resp.status_code == 200:
            return BeautifulSoup(resp.text, "html.parser")
        return None
    except Exception as e:
        print(f"[fetch_page] {path} -> {e}")
        return None


# ---------------- About ----------------
def extract_about(base_url: str):
    base_url = _normalize_url(base_url)
    for path in ["pages/about", "about", "pages/our-story"]:
        soup = fetch_page(base_url, path)
        if soup:
            paras = [clean_html(p.get_text(strip=True)) for p in soup.find_all("p")]
            txt = " ".join([p for p in paras if p])
            if txt:
                return txt
    return "No about info found"


# ---------------- Policies ----------------
def extract_policies(base_url: str):
    base_url = _normalize_url(base_url)
    out = {}
    policy_paths = {
        "privacy_policy": "policies/privacy-policy",
        "refund_policy": "policies/refund-policy",
        "shipping_policy": "policies/shipping-policy",
        "terms_of_service": "policies/terms-of-service",
    }
    for key, path in policy_paths.items():
        soup = fetch_page(base_url, path)
        if soup:
            txt = " ".join(
                [clean_html(p.get_text(strip=True)) for p in soup.find_all("p")]
            )
            out[key] = (txt[:300] + "...") if txt else "Not available"
        else:
            out[key] = "Not available"
    return out


# ---------------- Contact ----------------
def extract_contact(base_url: str):
    base_url = _normalize_url(base_url)
    soup = fetch_page(base_url, "pages/contact")
    details = {"emails": [], "phone_numbers": [], "address": ""}
    if soup:
        text = soup.get_text(" ", strip=True)
        parts = text.split()
        details["emails"] = [t for t in parts if "@" in t and "." in t]
        details["phone_numbers"] = [t for t in parts if t.replace("+", "").replace("-", "").isdigit()]
        details["address"] = clean_html(text[:200])
    return details


# ---------------- Socials ----------------
def extract_socials(base_url: str):
    base_url = _normalize_url(base_url)
    soup = fetch_page(base_url)
    socials = {"facebook": "", "instagram": "", "twitter": "", "youtube": "", "tiktok": ""}
    if soup:
        for a in soup.find_all("a", href=True):
            href = a["href"]
            h = href.lower()
            if "facebook.com" in h and not socials["facebook"]:
                socials["facebook"] = href
            elif "instagram.com" in h and not socials["instagram"]:
                socials["instagram"] = href
            elif ("twitter.com" in h or "x.com" in h) and not socials["twitter"]:
                socials["twitter"] = href
            elif "youtube.com" in h and not socials["youtube"]:
                socials["youtube"] = href
            elif "tiktok.com" in h and not socials["tiktok"]:
                socials["tiktok"] = href
    return socials


# ---------------- FAQs ----------------
def extract_faqs(base_url: str):
    base_url = _normalize_url(base_url)
    faqs = []
    for path in ["pages/faq", "faq", "pages/faqs"]:
        soup = fetch_page(base_url, path)
        if not soup:
            continue
        questions = soup.find_all(["h2", "h3", "strong", "dt"])
        answers = []
        for q in questions:
            nxt = q.find_next_sibling()
            if nxt:
                answers.append(clean_html(nxt.get_text(" ", strip=True)))
        for i, q in enumerate(questions):
            qq = clean_html(q.get_text(" ", strip=True))
            aa = answers[i] if i < len(answers) else ""
            if qq:
                faqs.append({"question": qq, "answer": aa})
        if faqs:
            break
    return faqs


# ---------------- Products via Shopify JSON ----------------
def _fetch_products_json(base_url: str):
    base_url = _normalize_url(base_url)
    try:
        url = urljoin(base_url, "products.json")
        resp = requests.get(url, params={"limit": 250}, timeout=15)
        if resp.status_code != 200:
            return []
        js = resp.json()
        items = js.get("products", [])
        out = []
        for p in items:
            title = clean_html(p.get("title") or "")
            handle = p.get("handle") or ""
            product_url = _abs(base_url, f"/products/{handle}") if handle else ""
            image_url = ""
            if p.get("images"):
                image_url = p["images"][0].get("src") or ""
                image_url = _abs(base_url, image_url) if image_url else ""
            price = ""
            if p.get("variants"):
                try:
                    prices = [float(v.get("price") or 0) for v in p["variants"] if v.get("price")]
                    if prices:
                        price = f"{min(prices):.2f}"
                except Exception:
                    pass
            out.append({
                "title": title,
                "product_url": product_url,
                "image_url": image_url,
                "price": price
            })
        return out
    except Exception as e:
        print(f"[products.json] {e}")
        return []


# ---------------- Products via HTML ----------------
def _fetch_products_html(base_url: str):
    base_url = _normalize_url(base_url)
    products = []
    soup = fetch_page(base_url, "collections/all")
    if not soup:
        return products
    cards = soup.select("a[href*='/products/']")
    seen = set()
    for a in cards:
        href = a.get("href")
        if not href or "/products/" not in href:
            continue
        pu = _abs(base_url, href)
        if pu in seen:
            continue
        seen.add(pu)
        title = ""
        img_url = ""
        if a.get("title"):
            title = clean_html(a["title"])
        if not title and a.text:
            title = clean_html(a.get_text(" ", strip=True))
        img = a.find("img") or a.find_next("img")
        if img and (img.get("data-src") or img.get("src")):
            img_url = img.get("data-src") or img.get("src")
            img_url = _abs(base_url, img_url)
        products.append({
            "title": title,
            "product_url": pu,
            "image_url": img_url,
            "price": ""
        })
    return products


def extract_products(base_url: str):
    items = _fetch_products_json(base_url)
    if not items:
        items = _fetch_products_html(base_url)
    return items


# ---------------- Hero products ----------------
def extract_hero_products(base_url: str):
    base_url = _normalize_url(base_url)
    products = []
    soup = fetch_page(base_url)
    if not soup:
        return products
    cards = soup.select("a[href*='/products/']")
    seen = set()
    for a in cards:
        href = a.get("href")
        if not href or "/products/" not in href:
            continue
        pu = _abs(base_url, href)
        if pu in seen:
            continue
        seen.add(pu)
        title = ""
        if a.get("title"):
            title = clean_html(a["title"])
        if not title and a.text:
            title = clean_html(a.get_text(" ", strip=True))
        img_url = ""
        img = a.find("img") or a.find_next("img")
        if img and (img.get("data-src") or img.get("src")):
            img_url = img.get("data-src") or img.get("src")
            img_url = _abs(base_url, img_url)
        products.append({
            "title": title,
            "product_url": pu,
            "image_url": img_url
        })
        if len(products) >= 20:
            break
    return products


# ---------------- Important links ----------------
def extract_links(base_url: str):
    base_url = _normalize_url(base_url)
    soup = fetch_page(base_url)
    links = []
    if soup:
        for a in soup.find_all("a", href=True):
            links.append(_abs(base_url, a["href"]))
    wanted = []
    for u in links:
        lo = u.lower()
        if any(k in lo for k in ["order", "contact", "blog", "faq", "about", "shipping", "refund"]):
            wanted.append(u)
    dedup = []
    seen = set()
    for u in wanted:
        if u not in seen:
            dedup.append(u)
            seen.add(u)
    return dedup[:30]
