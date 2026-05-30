"""
Auto cap nhat tuong/skin moi tu Lien Quan Mobile.
Chi tai ve nhung gi chua co, cap nhat JSON va rebuild trang web.

Cach dung:
  python auto_update.py              -> Chi them tuong moi (nhanh)
  python auto_update.py --check-skins -> Kiem tra skin moi cho tat ca tuong (cham hon)
  python auto_update.py --full       -> Crawl lai toan bo (giong scrape_lienquan.py)
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import os
import re
import sys
from datetime import datetime

BASE_URL = "https://lienquan.garena.vn"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
ROLE_MAP = {"28": "Đấu sĩ", "29": "Pháp sư", "30": "Trợ thủ", "31": "Đỡ đòn", "32": "Sát thủ", "33": "Xạ thủ"}
JSON_FILE = "lienquan_heroes.json"
MAX_RETRIES = 3
RETRY_DELAY = 2


def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")


def safe_get(url, retries=MAX_RETRIES):
    """Request voi tu dong retry khi loi."""
    for attempt in range(retries):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=15)
            resp.raise_for_status()
            return resp
        except requests.exceptions.RequestException as e:
            if attempt < retries - 1:
                log(f"  Loi ket noi, thu lai ({attempt + 1}/{retries}): {e}")
                time.sleep(RETRY_DELAY)
            else:
                log(f"  THAT BAI sau {retries} lan thu: {e}")
                return None
    return None


def get_online_heroes():
    """Lay danh sach tuong tu trang web."""
    resp = safe_get(f"{BASE_URL}/hoc-vien/tuong-skin/")
    if not resp:
        log("KHONG THE lay danh sach tuong tu web!")
        return []
    soup = BeautifulSoup(resp.text, "html.parser")
    heroes = []
    for item in soup.find_all("a", class_="st-heroes__item"):
        match = re.search(r"/d/([^/]+)/?$", item.get("href", ""))
        if not match:
            continue
        slug = match.group(1)
        name = item.get_text(strip=True) or slug
        type_ids = re.findall(r"\d+", item.get("data-type", "[]"))
        roles = [ROLE_MAP[tid] for tid in type_ids if tid in ROLE_MAP]
        heroes.append({"name": name, "slug": slug, "roles": roles})
    return heroes


def get_hero_detail(slug):
    """Lay anh + skin tu trang chi tiet."""
    url = f"{BASE_URL}/hoc-vien/tuong-skin/d/{slug}/"
    resp = safe_get(url)
    if not resp:
        return {"image": None, "skins": []}
    try:
        soup = BeautifulSoup(resp.text, "html.parser")
        og = soup.find("meta", property="og:image")
        hero_image = og["content"] if og and og.get("content") else None
        skins = []
        for detail in soup.find_all(class_="hero__skins--detail"):
            h3 = detail.find("h3")
            if not h3:
                continue
            skin_name = h3.get_text(strip=True)
            picture = detail.find("picture")
            skin_image = picture.find("img").get("src", "") if picture and picture.find("img") else ""
            label_img = h3.find("img")
            skin_label = label_img.get("src", "") if label_img else ""
            skins.append({"name": skin_name, "image": skin_image, "label": skin_label})
        return {"image": hero_image, "skins": skins}
    except Exception as e:
        log(f"  ERROR parse {slug}: {e}")
        return {"image": None, "skins": []}


def main():
    check_skins = "--check-skins" in sys.argv or "--full" in sys.argv
    full_crawl = "--full" in sys.argv

    log("=" * 50)
    log("AUTO UPDATE - LIEN QUAN MOBILE")
    if check_skins:
        log("Che do: Kiem tra skin moi cho tat ca tuong")
    else:
        log("Che do: Chi them tuong moi (dung --check-skins de kiem tra skin)")
    log("=" * 50)

    # Load du lieu hien tai
    existing = json.load(open(JSON_FILE, "r", encoding="utf-8")) if os.path.exists(JSON_FILE) else []
    existing_map = {h["slug"]: h for h in existing}
    log(f"Du lieu hien tai: {len(existing)} tuong, {sum(len(h.get('skins',[])) for h in existing)} skin")

    # Lay danh sach online
    log("Kiem tra tuong moi tren web...")
    online = get_online_heroes()
    if not online:
        log("Khong lay duoc danh sach tuong. Ket thuc.")
        return
    log(f"Tren web: {len(online)} tuong")

    updated = False
    new_hero_count = 0
    new_skin_count = 0

    # --- Xu ly tuong moi ---
    new_heroes = [h for h in online if h["slug"] not in existing_map]
    if new_heroes:
        log(f"\nTim thay {len(new_heroes)} tuong moi:")
        for i, hero_info in enumerate(new_heroes, 1):
            slug = hero_info["slug"]
            log(f"  [{i}/{len(new_heroes)}] + TUONG MOI: {hero_info['name']} ({slug})")
            detail = get_hero_detail(slug)
            existing.append({
                "name": hero_info["name"],
                "slug": slug,
                "detail_url": f"{BASE_URL}/hoc-vien/tuong-skin/d/{slug}/",
                "image_url": detail["image"],
                "roles": hero_info["roles"],
                "skins": detail["skins"],
            })
            existing_map[slug] = existing[-1]
            new_hero_count += 1
            new_skin_count += len(detail["skins"])
            updated = True
            time.sleep(0.5)
    else:
        log("Khong co tuong moi.")

    # --- Cap nhat roles cho tuong chua co ---
    for hero_info in online:
        hero = existing_map.get(hero_info["slug"])
        if hero and not hero.get("roles") and hero_info["roles"]:
            hero["roles"] = hero_info["roles"]
            updated = True

    # --- Kiem tra skin moi (chi khi co flag) ---
    if check_skins:
        log(f"\nKiem tra skin moi cho {len(online)} tuong...")
        for i, hero_info in enumerate(online, 1):
            slug = hero_info["slug"]
            hero = existing_map.get(slug)
            if not hero:
                continue  # Da xu ly o tren

            old_skin_names = {s["name"] for s in hero.get("skins", [])}
            old_count = len(old_skin_names)

            print(f"  [{i:3d}/{len(online)}] {hero['name']}...", end=" ", flush=True)
            detail = get_hero_detail(slug)

            new_skins = [s for s in detail["skins"] if s["name"] not in old_skin_names]
            if new_skins:
                print(f"+{len(new_skins)} skin moi!")
                log(f"    Skin moi: {[s['name'] for s in new_skins]}")
                hero["skins"] = detail["skins"]
                new_skin_count += len(new_skins)
                updated = True
            else:
                print(f"OK ({old_count} skin)")

            # Cap nhat anh dai dien neu chua co
            if not hero.get("image_url") and detail["image"]:
                hero["image_url"] = detail["image"]
                updated = True

            time.sleep(0.3)

    # --- Luu va rebuild ---
    if updated:
        log("\nLuu du lieu...")
        with open(JSON_FILE, "w", encoding="utf-8") as f:
            json.dump(existing, f, ensure_ascii=False, indent=2)
        log("Dang rebuild trang web...")
        os.system("python build_website.py")
    else:
        log("\nKhong co gi thay doi, bo qua rebuild.")

    total_skins = sum(len(h.get("skins", [])) for h in existing)
    log(f"\n{'=' * 50}")
    log(f"KET QUA: {len(existing)} tuong, {total_skins} skin")
    if new_hero_count or new_skin_count:
        log(f"  + {new_hero_count} tuong moi, + {new_skin_count} skin moi")
    else:
        log("  Khong co gi moi.")
    log("=" * 50)


if __name__ == "__main__":
    main()
