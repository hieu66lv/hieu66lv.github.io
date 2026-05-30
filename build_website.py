"""
Tao file index.html hien thi tuong + trang phuc (skin) day du.
Chay: python build_website.py
Ket qua: index.html (mo truc tiep bang trinh duyet)
"""

import json

# Doc du lieu
with open("lienquan_heroes.json", "r", encoding="utf-8") as f:
    heroes = json.load(f)

heroes_json = json.dumps(heroes, ensure_ascii=False)

html_content = """<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Liên Quân Mobile - Tướng & Trang Phục</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;600;700;800;900&display=swap');

        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: 'Be Vietnam Pro', sans-serif;
            background: #0a0e1a;
            color: #fff;
            min-height: 100vh;
            font-weight: 600;
        }

        .header {
            background: linear-gradient(135deg, #1a1f3a 0%, #0d1025 100%);
            border-bottom: 2px solid #f5a623;
            padding: 20px 0;
            text-align: center;
            position: sticky;
            top: 0;
            z-index: 100;
        }

        .header h1 {
            font-size: 2.2rem;
            font-weight: 900;
            background: linear-gradient(90deg, #f5a623, #ff6b35);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 5px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .header p { color: #8892b0; font-size: 0.9rem; font-weight: 600; }

        .search-container {
            max-width: 500px;
            margin: 12px auto 0;
            position: relative;
        }

        .search-container input {
            width: 100%;
            padding: 12px 20px 12px 45px;
            border: 2px solid #2a3050;
            border-radius: 25px;
            background: #141828;
            color: #fff;
            font-size: 1rem;
            outline: none;
            transition: border-color 0.3s;
        }

        .search-container input:focus { border-color: #f5a623; }

        .search-icon {
            position: absolute;
            left: 16px;
            top: 50%;
            transform: translateY(-50%);
            font-size: 1.1rem;
        }

        .stats {
            text-align: center;
            padding: 12px;
            color: #8892b0;
            font-size: 0.9rem;
        }
        .stats span { color: #f5a623; font-weight: bold; }

        /* Role Filter */
        .filter-bar {
            display: flex;
            justify-content: center;
            flex-wrap: wrap;
            gap: 8px;
            padding: 0 20px 15px;
            max-width: 800px;
            margin: 0 auto;
        }

        .filter-btn {
            padding: 8px 18px;
            border: 1px solid #2a3050;
            border-radius: 20px;
            background: #141828;
            color: #8892b0;
            font-size: 0.85rem;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.2s;
            outline: none;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .filter-btn:hover {
            border-color: #f5a623;
            color: #f5a623;
        }

        .filter-btn.active {
            background: #f5a623;
            border-color: #f5a623;
            color: #0a0e1a;
            font-weight: 600;
        }

        /* New Skins */
        .new-skins-section {
            margin-bottom: 30px;
            padding-bottom: 25px;
            border-bottom: 1px solid #2a3050;
        }

        .new-skins-title {
            font-size: 1.2rem;
            font-weight: 800;
            color: #ff6b35;
            margin-bottom: 15px;
            text-transform: uppercase;
        }

        .new-skins-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 15px;
        }

        .new-skin-card {
            background: #1a1f3a;
            border-radius: 10px;
            overflow: hidden;
            border: 1px solid #f5a623;
            cursor: pointer;
            transition: all 0.3s;
        }

        .new-skin-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 5px 20px rgba(245, 166, 35, 0.3);
        }

        .new-skin-card .ns-image {
            width: 100%;
            aspect-ratio: 16/9;
            overflow: hidden;
            background: #0d1025;
        }

        .new-skin-card .ns-image img {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }

        .new-skin-card .ns-info {
            padding: 10px 12px;
        }

        .new-skin-card .ns-name {
            font-size: 0.95rem;
            font-weight: 700;
            color: #fff;
        }

        .new-skin-card .ns-hero {
            font-size: 0.8rem;
            color: #f5a623;
            margin-top: 3px;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 0 20px 40px;
        }

        /* Hero Grid */
        .heroes-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
            gap: 16px;
        }

        .hero-card {
            background: linear-gradient(145deg, #1a1f3a, #141828);
            border-radius: 12px;
            overflow: hidden;
            border: 1px solid #2a3050;
            transition: all 0.3s ease;
            cursor: pointer;
            display: block;
        }

        .hero-card:hover {
            transform: translateY(-4px);
            border-color: #f5a623;
            box-shadow: 0 8px 25px rgba(245, 166, 35, 0.2);
        }

        .hero-card .image-wrapper {
            width: 100%;
            aspect-ratio: 1;
            overflow: hidden;
            background: #0d1025;
        }

        .hero-card img {
            width: 100%;
            height: 100%;
            object-fit: cover;
            transition: transform 0.3s ease, opacity 0.3s ease;
            opacity: 0;
        }

        .hero-card img.loaded { opacity: 1; }
        .hero-card:hover img { transform: scale(1.08); }

        .hero-card .info {
            padding: 10px;
            text-align: center;
        }

        .hero-card .name {
            font-size: 0.95rem;
            font-weight: 700;
            color: #fff;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .hero-card .skin-count {
            font-size: 0.75rem;
            color: #8892b0;
            margin-top: 3px;
        }

        .hero-card .role-badge {
            font-size: 0.7rem;
            color: #f5a623;
            margin-top: 2px;
        }

        .hero-card .gold-price {
            font-size: 0.7rem;
            color: #ffd700;
            margin-top: 2px;
        }

        /* Modal */
        .modal-overlay {
            display: none;
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(0,0,0,0.85);
            z-index: 1000;
            overflow-y: auto;
            padding: 20px;
        }

        .modal-overlay.active { display: flex; justify-content: center; align-items: flex-start; }

        .modal {
            background: #141828;
            border-radius: 16px;
            max-width: 1100px;
            width: 100%;
            margin: 20px auto;
            border: 1px solid #2a3050;
            overflow: hidden;
        }

        .modal-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 20px 25px;
            background: #1a1f3a;
            border-bottom: 1px solid #2a3050;
        }

        .modal-header h2 {
            font-size: 1.6rem;
            font-weight: 800;
            color: #f5a623;
            text-transform: uppercase;
        }

        .modal-close {
            background: none;
            border: none;
            color: #8892b0;
            font-size: 2rem;
            cursor: pointer;
            padding: 0 10px;
            line-height: 1;
            transition: color 0.2s;
        }

        .modal-close:hover { color: #fff; }

        .modal-body { padding: 25px; }

        .modal-hero-info {
            display: flex;
            align-items: center;
            gap: 20px;
            margin-bottom: 25px;
        }

        .modal-hero-info img {
            width: 80px;
            height: 80px;
            border-radius: 50%;
            object-fit: cover;
            border: 3px solid #f5a623;
        }

        .modal-hero-info .details h3 {
            font-size: 1.3rem;
            color: #fff;
        }

        .modal-hero-info .details p {
            color: #8892b0;
            font-size: 0.9rem;
            margin-top: 4px;
        }

        .modal-hero-info .details a {
            color: #f5a623;
            text-decoration: none;
            font-size: 0.85rem;
        }

        .modal-hero-info .details a:hover { text-decoration: underline; }

        /* Skills */
        .skills-section { margin-top: 25px; margin-bottom: 10px; }

        .skills-title {
            font-size: 1.1rem;
            color: #e6e6e6;
            margin-bottom: 12px;
            padding-bottom: 10px;
            border-bottom: 1px solid #2a3050;
        }

        .skills-list { display: flex; flex-direction: column; gap: 12px; }

        .skill-item {
            display: flex;
            align-items: flex-start;
            gap: 12px;
            padding: 12px;
            background: #1a1f3a;
            border-radius: 10px;
            border: 1px solid #2a3050;
        }

        .skill-item img {
            width: 48px;
            height: 48px;
            border-radius: 8px;
            flex-shrink: 0;
            border: 2px solid #2a3050;
        }

        .skill-item .skill-info { flex: 1; }

        .skill-item .skill-name {
            font-size: 0.95rem;
            font-weight: 700;
            color: #f5a623;
            margin-bottom: 4px;
        }

        .skill-item .skill-desc {
            font-size: 0.85rem;
            color: #8892b0;
            line-height: 1.4;
            font-weight: 400;
        }

        .skins-title {
            font-size: 1.1rem;
            color: #e6e6e6;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 1px solid #2a3050;
        }

        /* Skin Grid */
        .skins-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 15px;
        }

        .skin-card {
            background: #1a1f3a;
            border-radius: 10px;
            overflow: hidden;
            border: 1px solid #2a3050;
            transition: all 0.3s ease;
        }

        .skin-card:hover {
            border-color: #f5a623;
            transform: translateY(-3px);
            box-shadow: 0 5px 15px rgba(245, 166, 35, 0.15);
        }

        .skin-card .skin-image {
            width: 100%;
            aspect-ratio: 16/9;
            overflow: hidden;
            background: #0d1025;
        }

        .skin-card .skin-image img {
            width: 100%;
            height: 100%;
            object-fit: cover;
            transition: transform 0.3s;
        }

        .skin-card:hover .skin-image img { transform: scale(1.05); }

        .skin-card .skin-info {
            padding: 10px 12px;
        }

        .skin-card .skin-name {
            font-size: 1.15rem;
            color: #fff;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .skin-card .skin-label {
            height: 26px;
            width: auto;
        }

        .skin-card .skin-price {
            font-size: 0.8rem;
            color: #ffd700;
            font-weight: 600;
            margin-top: 4px;
        }

        .skin-card .skin-image { cursor: pointer; }

        /* Lightbox */
        .lightbox {
            display: none;
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(0,0,0,0.95);
            z-index: 2000;
            justify-content: center;
            align-items: center;
            flex-direction: column;
            padding: 20px;
            cursor: zoom-out;
        }

        .lightbox.active { display: flex; }

        .lightbox img {
            max-width: 95%;
            max-height: 80vh;
            object-fit: contain;
            border-radius: 8px;
            box-shadow: 0 0 40px rgba(0,0,0,0.5);
        }

        .lightbox .lb-caption {
            color: #fff;
            font-size: 1.3rem;
            font-weight: 700;
            margin-top: 15px;
            text-align: center;
            max-width: 600px;
        }

        .lightbox .lb-close {
            position: absolute;
            top: 20px;
            right: 30px;
            background: none;
            border: none;
            color: #fff;
            font-size: 2.5rem;
            cursor: pointer;
            line-height: 1;
            opacity: 0.7;
            transition: opacity 0.2s;
        }

        .lightbox .lb-close:hover { opacity: 1; }

        .lightbox .lb-nav {
            position: absolute;
            top: 50%;
            transform: translateY(-50%);
            background: rgba(255,255,255,0.1);
            border: none;
            color: #fff;
            font-size: 2.5rem;
            cursor: pointer;
            padding: 15px 20px;
            border-radius: 8px;
            opacity: 0.6;
            transition: opacity 0.2s, background 0.2s;
        }

        .lightbox .lb-nav:hover { opacity: 1; background: rgba(255,255,255,0.2); }
        .lightbox .lb-prev { left: 20px; }
        .lightbox .lb-next { right: 20px; }

        .no-results {
            text-align: center;
            padding: 60px 20px;
            color: #8892b0;
            display: none;
            grid-column: 1 / -1;
        }
        .no-results.show { display: block; }

        .footer {
            text-align: center;
            padding: 30px;
            color: #555;
            font-size: 0.8rem;
            border-top: 1px solid #1a1f3a;
        }
        .footer a { color: #f5a623; text-decoration: none; }

        @media (max-width: 768px) {
            .header h1 { font-size: 1.4rem; }
            .heroes-grid {
                grid-template-columns: repeat(auto-fill, minmax(110px, 1fr));
                gap: 10px;
            }
            .hero-card .info { padding: 8px; }
            .hero-card .name { font-size: 0.8rem; }
            .skins-grid {
                grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
                gap: 10px;
            }
            .modal-hero-info { flex-direction: column; text-align: center; }
        }

        @media (max-width: 480px) {
            .heroes-grid { grid-template-columns: repeat(3, 1fr); gap: 8px; }
            .skins-grid { grid-template-columns: repeat(2, 1fr); }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>&#9876; Liên Quân Mobile - Tướng & Trang Phục</h1>
        <p>128 tướng &bull; 1184 trang phục</p>
        <div class="search-container">
            <span class="search-icon">&#128269;</span>
            <input type="text" id="searchInput" placeholder="Tìm tướng hoặc trang phục..." autocomplete="off">
        </div>
    </div>

    <div class="stats">
        Hiển thị <span id="visibleCount">0</span> / <span id="totalCount">0</span> tướng
    </div>

    <div class="filter-bar" id="filterBar">
        <button class="filter-btn active" data-role="all">Tất cả</button>
        <button class="filter-btn" data-role="Đấu sĩ">&#9876; Đấu sĩ</button>
        <button class="filter-btn" data-role="Đỡ đòn">&#128737; Đỡ đòn</button>
        <button class="filter-btn" data-role="Pháp sư">&#10024; Pháp sư</button>
        <button class="filter-btn" data-role="Sát thủ">&#128481; Sát thủ</button>
        <button class="filter-btn" data-role="Trợ thủ">&#128154; Trợ thủ</button>
        <button class="filter-btn" data-role="Xạ thủ">&#127993; Xạ thủ</button>
    </div>

    <div class="container">
        <!-- New Skins Section -->
        <div class="new-skins-section" id="newSkinsSection">
            <h2 class="new-skins-title">&#128293; SKIN MỚI NHẤT</h2>
            <div class="new-skins-grid" id="newSkinsGrid"></div>
        </div>

        <div class="heroes-grid" id="heroesGrid"></div>
        <div class="no-results" id="noResults">
            <p>Không tìm thấy tướng nào</p>
        </div>
    </div>

    <div class="footer">
        Dữ liệu từ <a href="https://lienquan.garena.vn/hoc-vien/tuong-skin/" target="_blank">lienquan.garena.vn</a>
    </div>

    <!-- Modal -->
    <div class="modal-overlay" id="modalOverlay">
        <div class="modal">
            <div class="modal-header">
                <h2 id="modalTitle">Tướng</h2>
                <button class="modal-close" id="modalClose">&times;</button>
            </div>
            <div class="modal-body" id="modalBody"></div>
        </div>
    </div>

    <!-- Lightbox -->
    <div class="lightbox" id="lightbox">
        <button class="lb-close" id="lbClose">&times;</button>
        <button class="lb-nav lb-prev" id="lbPrev">&#10094;</button>
        <button class="lb-nav lb-next" id="lbNext">&#10095;</button>
        <img id="lbImage" src="" alt="">
        <div class="lb-caption" id="lbCaption"></div>
    </div>

    <script>
        var heroesData = __HEROES_DATA__;

        document.getElementById('totalCount').textContent = heroesData.length;
        renderHeroes(heroesData);
        renderNewSkins();

        function renderNewSkins() {
            // Show last skin of each of the first 10 heroes (newest heroes = newest skins)
            var newSkins = [];
            for (var i = 0; i < heroesData.length && newSkins.length < 12; i++) {
                var hero = heroesData[i];
                if (hero.skins.length > 1) {
                    var lastSkin = hero.skins[hero.skins.length - 1];
                    if (lastSkin.image) {
                        newSkins.push({skin: lastSkin, hero: hero});
                    }
                }
            }
            var grid = document.getElementById('newSkinsGrid');
            newSkins.forEach(function(item) {
                var card = document.createElement('div');
                card.className = 'new-skin-card';
                card.addEventListener('click', function() {
                    openModal(item.hero);
                });
                var imgDiv = document.createElement('div');
                imgDiv.className = 'ns-image';
                var img = document.createElement('img');
                img.src = item.skin.image;
                img.alt = item.skin.name;
                img.loading = 'lazy';
                imgDiv.appendChild(img);
                card.appendChild(imgDiv);
                var info = document.createElement('div');
                info.className = 'ns-info';
                var name = document.createElement('div');
                name.className = 'ns-name';
                name.textContent = item.skin.name;
                var heroName = document.createElement('div');
                heroName.className = 'ns-hero';
                heroName.textContent = item.hero.name;
                info.appendChild(name);
                info.appendChild(heroName);
                card.appendChild(info);
                grid.appendChild(card);
            });
        }

        function renderHeroes(heroes) {
            var grid = document.getElementById('heroesGrid');
            grid.innerHTML = '';

            heroes.forEach(function(hero, index) {
                var card = document.createElement('div');
                card.className = 'hero-card';
                card.setAttribute('data-index', index);

                var imgSrc = hero.image_url;

                var wrapper = document.createElement('div');
                wrapper.className = 'image-wrapper';

                var img = document.createElement('img');
                img.src = imgSrc;
                img.alt = hero.name;
                img.loading = 'lazy';
                img.onload = function() { this.classList.add('loaded'); };
                wrapper.appendChild(img);

                var info = document.createElement('div');
                info.className = 'info';

                var name = document.createElement('div');
                name.className = 'name';
                name.title = hero.name;
                name.textContent = hero.name;

                var skinCount = document.createElement('div');
                skinCount.className = 'skin-count';
                skinCount.textContent = hero.skins.length + ' trang phục';

                var roleBadge = document.createElement('div');
                roleBadge.className = 'role-badge';
                roleBadge.textContent = (hero.roles || []).join(', ');

                var goldPrice = document.createElement('div');
                goldPrice.className = 'gold-price';
                var priceLabel = hero.price_label || '';
                if (priceLabel === 'Miễn phí') {
                    goldPrice.innerHTML = '&#9733; Miễn phí';
                    goldPrice.style.color = '#2ed573';
                } else if (priceLabel) {
                    goldPrice.innerHTML = '<span style="color:#ffd700">&#9679;</span> ' + priceLabel + ' v\u00E0ng';
                }

                info.appendChild(name);
                info.appendChild(roleBadge);
                info.appendChild(goldPrice);
                info.appendChild(skinCount);
                card.appendChild(wrapper);
                card.appendChild(info);

                card.addEventListener('click', function() {
                    openModal(hero);
                });

                grid.appendChild(card);
            });

            document.getElementById('visibleCount').textContent = heroes.length;
            var noResults = document.getElementById('noResults');
            if (heroes.length === 0) {
                noResults.classList.add('show');
            } else {
                noResults.classList.remove('show');
            }
        }

        function openModal(hero) {
            var overlay = document.getElementById('modalOverlay');
            var title = document.getElementById('modalTitle');
            var body = document.getElementById('modalBody');

            title.textContent = hero.name;

            var heroImg = hero.image_url;

            currentSkins = hero.skins;

            var container = document.createElement('div');

            // Hero info
            var heroInfo = document.createElement('div');
            heroInfo.className = 'modal-hero-info';
            var hImg = document.createElement('img');
            hImg.src = heroImg;
            hImg.alt = hero.name;
            heroInfo.appendChild(hImg);

            var details = document.createElement('div');
            details.className = 'details';
            var h3 = document.createElement('h3');
            h3.textContent = hero.name;
            var p = document.createElement('p');
            p.textContent = (hero.roles || []).join(', ') + ' • ' + hero.skins.length + ' trang phục';
            var goldInfo = document.createElement('p');
            goldInfo.style.color = '#ffd700';
            goldInfo.style.fontSize = '0.9rem';
            goldInfo.style.marginTop = '4px';
            var pl = hero.price_label || '';
            if (pl === 'Miễn phí') {
                goldInfo.innerHTML = '&#9733; Miễn phí';
                goldInfo.style.color = '#2ed573';
            } else if (pl) {
                goldInfo.innerHTML = '<span style="color:#ffd700">&#9679;</span> ' + pl + ' v\u00E0ng';
            }
            var link = document.createElement('a');
            link.href = hero.detail_url;
            link.target = '_blank';
            link.innerHTML = 'Xem trên Garena &#8599;';
            details.appendChild(h3);
            details.appendChild(p);
            details.appendChild(goldInfo);
            details.appendChild(link);
            heroInfo.appendChild(details);
            container.appendChild(heroInfo);

            // Skins title
            var skinsTitle = document.createElement('div');
            skinsTitle.className = 'skins-title';
            skinsTitle.textContent = 'Trang phục (' + hero.skins.length + ')';
            container.appendChild(skinsTitle);

            // Skins grid
            var skinsGrid = document.createElement('div');
            skinsGrid.className = 'skins-grid';

            hero.skins.forEach(function(skin, skinIdx) {
                var card = document.createElement('div');
                card.className = 'skin-card';
                card.style.cursor = 'pointer';
                card.addEventListener('click', (function(idx) {
                    return function() { openLightbox(idx); };
                })(skinIdx));

                if (skin.image) {
                    var imgDiv = document.createElement('div');
                    imgDiv.className = 'skin-image';
                    var sImg = document.createElement('img');
                    sImg.src = skin.image;
                    sImg.alt = skin.name;
                    sImg.loading = 'lazy';
                    imgDiv.appendChild(sImg);
                    card.appendChild(imgDiv);
                }

                var skinInfo = document.createElement('div');
                skinInfo.className = 'skin-info';
                var skinName = document.createElement('div');
                skinName.className = 'skin-name';

                if (skin.label) {
                    var labelImg = document.createElement('img');
                    labelImg.className = 'skin-label';
                    labelImg.src = skin.label;
                    skinName.appendChild(labelImg);
                }

                var nameSpan = document.createElement('span');
                nameSpan.textContent = skin.name;
                skinName.appendChild(nameSpan);

                skinInfo.appendChild(skinName);

                // Price
                if (skin.price_text) {
                    var skinPrice = document.createElement('div');
                    skinPrice.className = 'skin-price';
                    var pt = skin.price_text;
                    if (pt === 'Mặc định' || pt === 'Rank mùa') {
                        skinPrice.style.color = '#2ed573';
                        skinPrice.textContent = pt;
                    } else if (pt === 'Giới hạn' || pt === 'Giải đấu' || pt === 'Hợp tác') {
                        skinPrice.style.color = '#ff6b6b';
                        skinPrice.textContent = pt;
                    } else {
                        // Show voucher icon + number
                        var num = pt.replace(' QH', '');
                        skinPrice.innerHTML = '<svg width="14" height="14" viewBox="0 0 24 24" style="vertical-align:middle;margin-right:4px;"><polygon points="12,2 15,9 22,9 16.5,14 18.5,21 12,17 5.5,21 7.5,14 2,9 9,9" fill="#ffd700"/></svg>' + num;
                    }
                    skinInfo.appendChild(skinPrice);
                }

                card.appendChild(skinInfo);
                skinsGrid.appendChild(card);
            });

            container.appendChild(skinsGrid);

            // Skills (below skins)
            if (hero.skills && hero.skills.length > 0) {
                var skillsSection = document.createElement('div');
                skillsSection.className = 'skills-section';
                var skillsTitle = document.createElement('div');
                skillsTitle.className = 'skills-title';
                skillsTitle.textContent = 'Kỹ năng';
                skillsSection.appendChild(skillsTitle);

                var skillsList = document.createElement('div');
                skillsList.className = 'skills-list';
                hero.skills.forEach(function(skill) {
                    var item = document.createElement('div');
                    item.className = 'skill-item';
                    if (skill.icon) {
                        var icon = document.createElement('img');
                        icon.src = skill.icon;
                        icon.alt = skill.name;
                        item.appendChild(icon);
                    }
                    var info = document.createElement('div');
                    info.className = 'skill-info';
                    var name = document.createElement('div');
                    name.className = 'skill-name';
                    name.textContent = skill.name;
                    info.appendChild(name);
                    if (skill.desc) {
                        var desc = document.createElement('div');
                        desc.className = 'skill-desc';
                        desc.textContent = skill.desc;
                        info.appendChild(desc);
                    }
                    item.appendChild(info);
                    skillsList.appendChild(item);
                });
                skillsSection.appendChild(skillsList);
                container.appendChild(skillsSection);
            }

            body.innerHTML = '';
            body.appendChild(container);
            overlay.classList.add('active');
            document.body.style.overflow = 'hidden';
        }

        // Close modal
        document.getElementById('modalClose').addEventListener('click', closeModal);
        document.getElementById('modalOverlay').addEventListener('click', function(e) {
            if (e.target === this) closeModal();
        });
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') closeModal();
        });

        function closeModal() {
            document.getElementById('modalOverlay').classList.remove('active');
            document.body.style.overflow = '';
        }

        // Lightbox
        var currentSkins = [];
        var currentSkinIdx = 0;

        function openLightbox(idx) {
            currentSkinIdx = idx;
            var skin = currentSkins[idx];
            if (!skin || !skin.image) return;

            var lb = document.getElementById('lightbox');
            var lbImg = document.getElementById('lbImage');
            var lbCaption = document.getElementById('lbCaption');

            lbImg.src = skin.image;
            lbCaption.innerHTML = '';
            if (skin.label) {
                var lbLabelImg = document.createElement('img');
                lbLabelImg.src = skin.label;
                lbLabelImg.style.height = '26px';
                lbLabelImg.style.verticalAlign = 'middle';
                lbLabelImg.style.marginRight = '8px';
                lbCaption.appendChild(lbLabelImg);
            }
            var lbText = document.createElement('span');
            lbText.textContent = skin.name;
            lbCaption.appendChild(lbText);
            lb.classList.add('active');

            // Hide nav if only 1 skin
            document.getElementById('lbPrev').style.display = currentSkins.length > 1 ? '' : 'none';
            document.getElementById('lbNext').style.display = currentSkins.length > 1 ? '' : 'none';
        }

        function closeLightbox() {
            document.getElementById('lightbox').classList.remove('active');
        }

        function navigateLightbox(dir) {
            currentSkinIdx += dir;
            if (currentSkinIdx < 0) currentSkinIdx = currentSkins.length - 1;
            if (currentSkinIdx >= currentSkins.length) currentSkinIdx = 0;

            var skin = currentSkins[currentSkinIdx];
            document.getElementById('lbImage').src = skin.image || '';
            var cap = document.getElementById('lbCaption');
            cap.innerHTML = '';
            if (skin.label) {
                var navLabelImg = document.createElement('img');
                navLabelImg.src = skin.label;
                navLabelImg.style.height = '26px';
                navLabelImg.style.verticalAlign = 'middle';
                navLabelImg.style.marginRight = '8px';
                cap.appendChild(navLabelImg);
            }
            var navText = document.createElement('span');
            navText.textContent = skin.name;
            cap.appendChild(navText);
        }

        document.getElementById('lbClose').addEventListener('click', closeLightbox);
        document.getElementById('lbPrev').addEventListener('click', function(e) {
            e.stopPropagation();
            navigateLightbox(-1);
        });
        document.getElementById('lbNext').addEventListener('click', function(e) {
            e.stopPropagation();
            navigateLightbox(1);
        });
        document.getElementById('lightbox').addEventListener('click', function(e) {
            if (e.target === this) closeLightbox();
        });
        document.addEventListener('keydown', function(e) {
            var lb = document.getElementById('lightbox');
            if (!lb.classList.contains('active')) return;
            if (e.key === 'Escape') closeLightbox();
            if (e.key === 'ArrowLeft') navigateLightbox(-1);
            if (e.key === 'ArrowRight') navigateLightbox(1);
        });

        // Filter & Search
        var currentRole = 'all';

        function filterAndSearch() {
            var query = document.getElementById('searchInput').value.toLowerCase().trim();
            var section = document.getElementById('newSkinsSection');
            section.style.display = (query || currentRole !== 'all') ? 'none' : '';
            var filtered = heroesData.filter(function(hero) {
                // Role filter
                if (currentRole !== 'all') {
                    if (!hero.roles || hero.roles.indexOf(currentRole) === -1) return false;
                }
                // Search filter
                if (query) {
                    if (hero.name.toLowerCase().indexOf(query) !== -1) return true;
                    if (hero.slug.toLowerCase().indexOf(query) !== -1) return true;
                    for (var i = 0; i < hero.skins.length; i++) {
                        if (hero.skins[i].name.toLowerCase().indexOf(query) !== -1) return true;
                    }
                    return false;
                }
                return true;
            });
            renderHeroes(filtered);
        }

        // Role filter buttons
        document.getElementById('filterBar').addEventListener('click', function(e) {
            var btn = e.target.closest('.filter-btn');
            if (!btn) return;
            currentRole = btn.getAttribute('data-role');
            var btns = this.querySelectorAll('.filter-btn');
            for (var i = 0; i < btns.length; i++) btns[i].classList.remove('active');
            btn.classList.add('active');
            filterAndSearch();
        });

        document.getElementById('searchInput').addEventListener('input', filterAndSearch);
    </script>
</body>
</html>"""

# Thay placeholder bang du lieu thuc
html_content = html_content.replace("__HEROES_DATA__", heroes_json)

# Cap nhat so lieu trong header
total_skins = sum(len(h.get("skins", [])) for h in heroes)
html_content = html_content.replace(
    "128 tướng &bull; 1184 trang phục",
    f"{len(heroes)} tướng &bull; {total_skins} trang phục"
)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"Da tao index.html thanh cong!")
print(f"Tong tuong: {len(heroes)}")
print(f"Tong skin: {total_skins}")
print("Mo file index.html bang trinh duyet de xem.")
