"""
Crawl tuong/skin Lien Quan Mobile tu https://lienquan.garena.vn/hoc-vien/tuong-skin/
Yeu cau: pip install requests beautifulsoup4
Chay: python scrape_lienquan.py
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import re

BASE_URL = "https://lienquan.garena.vn"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
ROLE_MAP = {"28": "Đấu sĩ", "29": "Pháp sư", "30": "Trợ thủ", "31": "Đỡ đòn", "32": "Sát thủ", "33": "Xạ thủ"}


def get_heroes_and_roles():
    """Lay danh sach tuong + role tu trang danh sach."""
    resp = requests.get(f"{BASE_URL}/hoc-vien/tuong-skin/", headers=HEADERS, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    heroes = []
    for item in soup.find_all("a", class_="st-heroes__item"):
        href = item.get("href", "")
        match = re.search(r"/d/([^/]+)/?$", href)
        if not match:
            continue
        slug = match.group(1)
        name = item.get_text(strip=True) or slug
        type_ids = re.findall(r"\d+", item.get("data-type", "[]"))
        roles = [ROLE_MAP[tid] for tid in type_ids if tid in ROLE_MAP]
        heroes.append({"name": name, "slug": slug, "roles": roles})

    return heroes


def get_hero_detail(slug):
    """Lay anh + danh sach skin tu trang chi tiet tuong."""
    url = f"{BASE_URL}/hoc-vien/tuong-skin/d/{slug}/"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        # Anh dai dien
        og = soup.find("meta", property="og:image")
        hero_image = og["content"] if og and og.get("content") else None

        # Danh sach skin
        skins = []
        for detail in soup.find_all(class_="hero__skins--detail"):
            h3 = detail.find("h3")
            if not h3:
                continue
            skin_name = h3.get_text(strip=True)
            picture = detail.find("picture")
            skin_image = ""
            if picture and picture.find("img"):
                skin_image = picture.find("img").get("src", "")
            label_img = h3.find("img")
            skin_label = label_img.get("src", "") if label_img else ""
            skins.append({"name": skin_name, "image": skin_image, "label": skin_label})

        # Ky nang
        skills = []
        skill_list = soup.find("ul", class_="hero__skills--list")
        skill_details = soup.find_all(class_="hero__skills--detail")
        if skill_list:
            for i, li in enumerate(skill_list.find_all("li")):
                a = li.find("a")
                skill_name = a.get("title", "") if a else ""
                skill_icon = ""
                img = li.find("img")
                if img:
                    skill_icon = img.get("src", "")
                skill_desc = ""
                if i < len(skill_details):
                    article = skill_details[i].find("article")
                    if article:
                        skill_desc = article.get_text(strip=True)
                skills.append({"name": skill_name, "icon": skill_icon, "desc": skill_desc})

        return {"image": hero_image, "skins": skins, "skills": skills}
    except Exception as e:
        print(f"  [ERROR] {slug}: {e}")
        return {"image": None, "skins": [], "skills": []}


def main():
    print("=" * 50)
    print("  CRAWL TUONG/SKIN LIEN QUAN MOBILE")
    print("=" * 50)

    # Lay danh sach tuong + roles
    print("\nDang lay danh sach tuong...")
    heroes = get_heroes_and_roles()
    print(f"  Tim thay {len(heroes)} tuong\n")

    results = []
    total_skins = 0

    for i, hero in enumerate(heroes, 1):
        slug = hero["slug"]
        print(f"[{i:3d}/{len(heroes)}] {hero['name']}...", end=" ")

        detail = get_hero_detail(slug)
        total_skins += len(detail["skins"])
        results.append({
            "name": hero["name"],
            "slug": slug,
            "detail_url": f"{BASE_URL}/hoc-vien/tuong-skin/d/{slug}/",
            "image_url": detail["image"],
            "roles": hero["roles"],
            "skills": detail["skills"],
            "skins": detail["skins"],
        })
        print(f"OK ({len(detail['skins'])} skins)")
        time.sleep(0.2)

    # Luu JSON
    with open("lienquan_heroes.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n{'=' * 50}")
    print(f"  HOAN TAT! {len(results)} tuong, {total_skins} skin")
    print(f"{'=' * 50}")


if __name__ == "__main__":
    main()
