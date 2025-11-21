import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster, Fullscreen, LocateControl
import pandas as pd
import openai
from geopy.distance import geodesic

# --- 1. SAYFA AYARLARI ---
st.set_page_config(page_title="İSTANBUL MEGA REHBERİ", layout="wide", page_icon="💎")

# --- 2. CSS TASARIMI (CYBER-DARK & UX) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');

    .stApp { background-color: #050505; font-family: 'Inter', sans-serif; color: white; }

    /* KART TASARIMI */
    .place-card {
        background: rgba(30, 30, 30, 0.6);
        border: 1px solid #333;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
        transition: transform 0.2s;
    }
    .place-card:hover {
        border-color: #10b981;
        background: #111;
        transform: translateX(5px);
    }

    /* ETİKETLER */
    .tag {
        font-size: 10px;
        padding: 3px 8px;
        border-radius: 4px;
        font-weight: bold;
        text-transform: uppercase;
        margin-right: 5px;
        color: #000;
    }
    .tag-vegan { background-color: #10b981; } /* Yeşil */
    .tag-tarih { background-color: #3b82f6; } /* Mavi */
    .tag-doga { background-color: #f59e0b; } /* Turuncu */
    .tag-sanat { background-color: #a855f7; } /* Mor */

    .distance-badge {
        float: right;
        color: #fbbf24;
        font-family: monospace;
        font-size: 12px;
        font-weight: bold;
    }

    h1, h2, h3 { color: white !important; }

    /* BUTON */
    .action-btn {
        display: block;
        width: 100%;
        text-align: center;
        background: #333;
        color: white;
        padding: 8px;
        border-radius: 6px;
        text-decoration: none;
        font-size: 12px;
        margin-top: 10px;
        font-weight: bold;
    }
    .action-btn:hover { background: #10b981; color: black; }
</style>
""", unsafe_allow_html=True)

# --- 3. DEVASA VERİ SETİ (138 MEKAN) ---
data = [
    # === YENİ EKLENEN GLUTENSİZ MEKANLAR (Senin Son Listen) ===
    {"isim": "Glutensiz.com Market & Cafe", "kategori": "Glutensiz/Vegan", "lat": 40.9380, "lon": 29.1350,
     "bolge": "Maltepe", "aciklama": "Geniş glutensiz ürün yelpazesi ve kafe."},
    {"isim": "Guru Glutensiz", "kategori": "Glutensiz/Vegan", "lat": 40.9850, "lon": 29.0280, "bolge": "Moda",
     "aciklama": "Şerifali ve Ataşehir şubeleri de var, güvenilir glutensiz."},
    {"isim": "Art Cafe", "kategori": "Glutensiz/Vegan", "lat": 41.0790, "lon": 29.0180, "bolge": "Levent",
     "aciklama": "Glutensiz tatlılar konusunda uzman."},
    {"isim": "Blum Coffee House", "kategori": "Glutensiz/Vegan", "lat": 41.0425, "lon": 29.0010, "bolge": "Akaretler",
     "aciklama": "Şekersiz ve glutensiz tatlı alternatifleri."},
    {"isim": "Vi Coffee Healthy Living", "kategori": "Glutensiz/Vegan", "lat": 41.0485, "lon": 28.9960,
     "bolge": "Nişantaşı", "aciklama": "Raw ve glutensiz seçenekler."},
    {"isim": "Voi Coffee Company", "kategori": "Glutensiz/Vegan", "lat": 40.9660, "lon": 29.0650,
     "bolge": "Bağdat Cad.", "aciklama": "Fit tatlılar ve kahve çeşitleri."},
    {"isim": "Grandma", "kategori": "Glutensiz/Vegan", "lat": 41.0480, "lon": 28.9950, "bolge": "Nişantaşı",
     "aciklama": "Unsuz ve glutensiz kek seçenekleri."},
    {"isim": "Fiore Pizzeria Italian", "kategori": "Glutensiz/Vegan", "lat": 41.0350, "lon": 28.9890,
     "bolge": "Gümüşsuyu", "aciklama": "İtalyan usulü glutensiz pizza."},
    {"isim": "Nalia", "kategori": "Glutensiz/Vegan", "lat": 40.9950, "lon": 29.1100, "bolge": "Ataşehir",
     "aciklama": "Mısır unuyla yapılan Karadeniz yemekleri."},
    {"isim": "Glutensiz Cafe", "kategori": "Glutensiz/Vegan", "lat": 41.0600, "lon": 28.9870, "bolge": "Şişli",
     "aciklama": "Poğaça, simit, hamburger (Sipariş ağırlıklı)."},
    {"isim": "Nohut Falafel & Humus", "kategori": "Glutensiz/Vegan", "lat": 40.9875, "lon": 29.0230, "bolge": "Kadıköy",
     "aciklama": "Vegan ve glutensiz falafel tabakları."},
    {"isim": "Sofram Ev Yemekleri", "kategori": "Glutensiz/Vegan", "lat": 41.0300, "lon": 28.9800, "bolge": "Beyoğlu",
     "aciklama": "Ev yemeği seçenekleri."},
    {"isim": "Neyzade Restaurant", "kategori": "Glutensiz/Vegan", "lat": 41.0120, "lon": 28.9600, "bolge": "Sirkeci",
     "aciklama": "Geleneksel mutfakta glutensiz opsiyonlar."},
    {"isim": "Atelier Raw", "kategori": "Glutensiz/Vegan", "lat": 41.0550, "lon": 29.0100, "bolge": "Etiler",
     "aciklama": "Raw ve sağlıklı beslenme atölyesi."},
    {"isim": "PePo Cafe", "kategori": "Glutensiz/Vegan", "lat": 41.0320, "lon": 28.9750, "bolge": "Galata",
     "aciklama": "Glutensiz menü seçenekleri."},
    {"isim": "Massa Bistro", "kategori": "Glutensiz/Vegan", "lat": 41.0150, "lon": 28.9700, "bolge": "Sirkeci",
     "aciklama": "Glutensiz bistro menüsü."},
    {"isim": "L’avare", "kategori": "Glutensiz/Vegan", "lat": 41.0750, "lon": 29.0300, "bolge": "Bebek",
     "aciklama": "Sahne ve yemek, glutensiz opsiyonlu."},
    {"isim": "My Home Sultanahmet", "kategori": "Glutensiz/Vegan", "lat": 41.0040, "lon": 28.9760,
     "bolge": "Sultanahmet", "aciklama": "Turistik bölgede güvenilir seçenek."},
    {"isim": "Babylonie Garden", "kategori": "Glutensiz/Vegan", "lat": 41.0070, "lon": 28.9780, "bolge": "Sultanahmet",
     "aciklama": "Teras manzaralı glutensiz yemek."},
    {"isim": "Arch Bistro", "kategori": "Glutensiz/Vegan", "lat": 41.0050, "lon": 28.9720, "bolge": "Sultanahmet",
     "aciklama": "Tarihi dokuda özel menüler."},
    {"isim": "Şirvan Sofrası", "kategori": "Glutensiz/Vegan", "lat": 41.0060, "lon": 28.9740, "bolge": "Sultanahmet",
     "aciklama": "Anadolu mutfağı."},
    {"isim": "Sur Balık Sarayburnu", "kategori": "Glutensiz/Vegan", "lat": 41.0170, "lon": 28.9850,
     "bolge": "Sarayburnu", "aciklama": "Deniz ürünleri ve glutensiz seçenekler."},
    {"isim": "Ist Too", "kategori": "Glutensiz/Vegan", "lat": 41.0380, "lon": 29.0020, "bolge": "Beşiktaş",
     "aciklama": "Shangri-La içinde Asya/Akdeniz mutfağı."},
    {"isim": "Asitane", "kategori": "Glutensiz/Vegan", "lat": 41.0290, "lon": 28.9390, "bolge": "Edirnekapı",
     "aciklama": "Osmanlı saray mutfağı (Doğal glutensizler)."},

    # === ÖNCEKİ VEGAN/GLUTENSİZ LİSTESİ (Tekrarlar Çıkarıldı) ===
    {"isim": "Bi Nevi Deli", "kategori": "Glutensiz/Vegan", "lat": 41.0821, "lon": 29.0256, "bolge": "Etiler",
     "aciklama": "Bitkisel bazlı mutfak, sağlıklı kaseler."},
    {"isim": "Healin Foods", "kategori": "Glutensiz/Vegan", "lat": 41.0491, "lon": 28.9974, "bolge": "Nişantaşı",
     "aciklama": "Doğal, şekersiz ve temiz içerik."},
    {"isim": "Vegan İstanbul", "kategori": "Glutensiz/Vegan", "lat": 41.0325, "lon": 28.9825, "bolge": "Cihangir",
     "aciklama": "Ev yemeği tadında vegan lezzetler."},
    {"isim": "Vegan Dükkan Lokanta", "kategori": "Glutensiz/Vegan", "lat": 41.0310, "lon": 28.9830, "bolge": "Cihangir",
     "aciklama": "Türkiye'nin köklü vegan dükkanı."},
    {"isim": "Vegan Masa", "kategori": "Glutensiz/Vegan", "lat": 41.0422, "lon": 29.0085, "bolge": "Beşiktaş",
     "aciklama": "Taş fırın vegan lahmacun ve pide."},
    {"isim": "CicoCebali", "kategori": "Glutensiz/Vegan", "lat": 41.0350, "lon": 28.9800, "bolge": "Beyoğlu",
     "aciklama": "Yaratıcı vegan mezeler."},
    {"isim": "Avokado Bar", "kategori": "Glutensiz/Vegan", "lat": 41.0480, "lon": 29.0010, "bolge": "Nişantaşı",
     "aciklama": "Avokado temalı sağlıklı menüler."},
    {"isim": "İnkase", "kategori": "Glutensiz/Vegan", "lat": 40.9870, "lon": 29.0240, "bolge": "Fenerbahçe",
     "aciklama": "Kase konseptli taze yiyecekler."},
    {"isim": "Veganarsist", "kategori": "Glutensiz/Vegan", "lat": 40.9895, "lon": 29.0215, "bolge": "Kadıköy",
     "aciklama": "Vegan döner ve tantuni."},
    {"isim": "Vegan Food Cartel", "kategori": "Glutensiz/Vegan", "lat": 41.0440, "lon": 29.0050, "bolge": "Beşiktaş",
     "aciklama": "Fast food tarzı vegan lezzetler."},
    {"isim": "Govinda", "kategori": "Glutensiz/Vegan", "lat": 41.0660, "lon": 29.0000, "bolge": "Mecidiyeköy",
     "aciklama": "Saf vejetaryen Hint mutfağı."},
    {"isim": "Kase No 16", "kategori": "Glutensiz/Vegan", "lat": 41.0456, "lon": 29.0021, "bolge": "Teşvikiye",
     "aciklama": "Sağlıklı kase ve salata barı."},
    {"isim": "Falafel Zone", "kategori": "Glutensiz/Vegan", "lat": 41.0340, "lon": 28.9780, "bolge": "Taksim",
     "aciklama": "Şehrin en iyi falafellerinden biri."},
    {"isim": "Mr. Dumpling", "kategori": "Glutensiz/Vegan", "lat": 40.9910, "lon": 29.0230, "bolge": "Kadıköy",
     "aciklama": "Vegan mantı ve dumpling çeşitleri."},
    {"isim": "Cafe Amedros", "kategori": "Glutensiz/Vegan", "lat": 41.0090, "lon": 28.9780, "bolge": "Sultanahmet",
     "aciklama": "Turistik bölgede glutensiz seçenekler."},
    {"isim": "Ozi Pizza & Pasta", "kategori": "Glutensiz/Vegan", "lat": 40.9860, "lon": 29.0260, "bolge": "Kadıköy",
     "aciklama": "Tamamen glutensiz pizza ve makarnalar."},
    {"isim": "Vegan Community Kitchen", "kategori": "Glutensiz/Vegan", "lat": 41.0290, "lon": 28.9490, "bolge": "Balat",
     "aciklama": "Samimi ortam, günlük değişen menü."},
    {"isim": "Mahatma Café", "kategori": "Glutensiz/Vegan", "lat": 40.9920, "lon": 29.0245, "bolge": "Yeldeğirmeni",
     "aciklama": "Renkli tabaklar, meşhur vegan kahvaltı."},
    {"isim": "Kem Küm Egyptian", "kategori": "Glutensiz/Vegan", "lat": 40.9880, "lon": 29.0220, "bolge": "Kadıköy",
     "aciklama": "Mısır sokak lezzetleri, falafel."},
    {"isim": "Çiğköftem", "kategori": "Glutensiz/Vegan", "lat": 41.0100, "lon": 28.9600, "bolge": "Zincir",
     "aciklama": "Vegan sertifikalı çiğ köfte."},
    {"isim": "Rolla Gluten Free", "kategori": "Glutensiz/Vegan", "lat": 40.9890, "lon": 29.0210, "bolge": "Kadıköy",
     "aciklama": "%100 glutensiz mutfak."},
    {"isim": "Gabfoods", "kategori": "Glutensiz/Vegan", "lat": 41.0676, "lon": 29.0436, "bolge": "Arnavutköy",
     "aciklama": "Paleo, Keto ve Vegan dostu lüks kafe."},
    {"isim": "Glutensiz Ada", "kategori": "Glutensiz/Vegan", "lat": 40.9321, "lon": 29.1324, "bolge": "Maltepe",
     "aciklama": "Glutensiz fırın ve pastane."},
    {"isim": "Ethique Plant-Based", "kategori": "Glutensiz/Vegan", "lat": 40.9780, "lon": 29.0250, "bolge": "Moda",
     "aciklama": "Fransız usulü vegan pastane."},
    {"isim": "Limonita", "kategori": "Glutensiz/Vegan", "lat": 40.9885, "lon": 29.0235, "bolge": "Kadıköy",
     "aciklama": "Vegan kasap ve restoran."},

    # === TARİHİ, KÜLTÜREL, DOĞA & SANAT (FULL LİSTE) ===
    {"isim": "Ayasofya", "kategori": "Tarihi/Kültürel", "lat": 41.0086, "lon": 28.9802, "bolge": "Sultanahmet",
     "aciklama": "Dünya mirası başyapıt."},
    {"isim": "Topkapı Sarayı", "kategori": "Tarihi/Kültürel", "lat": 41.0115, "lon": 28.9833, "bolge": "Sultanahmet",
     "aciklama": "Osmanlı'nın yönetim merkezi."},
    {"isim": "Sultanahmet Camii", "kategori": "Tarihi/Kültürel", "lat": 41.0054, "lon": 28.9768, "bolge": "Sultanahmet",
     "aciklama": "Mavi çinili cami."},
    {"isim": "Yerebatan Sarnıcı", "kategori": "Tarihi/Kültürel", "lat": 41.0084, "lon": 28.9779, "bolge": "Sultanahmet",
     "aciklama": "Medusa ve sütunlar."},
    {"isim": "Kapalıçarşı", "kategori": "Tarihi/Kültürel", "lat": 41.0107, "lon": 28.9680, "bolge": "Beyazıt",
     "aciklama": "Tarihi büyük çarşı."},
    {"isim": "Mısır Çarşısı", "kategori": "Tarihi/Kültürel", "lat": 41.0167, "lon": 28.9711, "bolge": "Eminönü",
     "aciklama": "Baharat ve egzotik tatlar."},
    {"isim": "Galata Kulesi", "kategori": "Tarihi/Kültürel", "lat": 41.0256, "lon": 28.9741, "bolge": "Galata",
     "aciklama": "Panoramik manzara."},
    {"isim": "Dolmabahçe Sarayı", "kategori": "Tarihi/Kültürel", "lat": 41.0391, "lon": 29.0007, "bolge": "Beşiktaş",
     "aciklama": "Osmanlı'nın son dönemi."},
    {"isim": "Süleymaniye Camii", "kategori": "Tarihi/Kültürel", "lat": 41.0162, "lon": 28.9638, "bolge": "Vefa",
     "aciklama": "Mimar Sinan eseri."},
    {"isim": "Eyüp Sultan Camii", "kategori": "Tarihi/Kültürel", "lat": 41.0482, "lon": 28.9302, "bolge": "Eyüp",
     "aciklama": "Kutsal ziyaret noktası."},
    {"isim": "Kariye Müzesi", "kategori": "Tarihi/Kültürel", "lat": 41.0292, "lon": 28.9402, "bolge": "Edirnekapı",
     "aciklama": "Eşsiz mozaikler."},
    {"isim": "Rumeli Hisarı", "kategori": "Tarihi/Kültürel", "lat": 41.0836, "lon": 29.0578, "bolge": "Sarıyer",
     "aciklama": "Boğazın hisarı."},
    {"isim": "Anadolu Hisarı", "kategori": "Tarihi/Kültürel", "lat": 41.0816, "lon": 29.0664, "bolge": "Beykoz",
     "aciklama": "Anadolu yakası hisarı."},
    {"isim": "Kız Kulesi", "kategori": "Tarihi/Kültürel", "lat": 41.0211, "lon": 29.0041, "bolge": "Üsküdar",
     "aciklama": "Boğazın incisi."},
    {"isim": "Beylerbeyi Sarayı", "kategori": "Tarihi/Kültürel", "lat": 41.0426, "lon": 29.0395, "bolge": "Üsküdar",
     "aciklama": "Yazlık saray."},
    {"isim": "Yıldız Sarayı", "kategori": "Tarihi/Kültürel", "lat": 41.0497, "lon": 29.0108, "bolge": "Beşiktaş",
     "aciklama": "Köşkler kompleksi."},
    {"isim": "Zeyrek Çinili Hamam", "kategori": "Tarihi/Kültürel", "lat": 41.0190, "lon": 28.9550, "bolge": "Zeyrek",
     "aciklama": "Restore edilmiş hamam."},
    {"isim": "Nuruosmaniye Camii", "kategori": "Tarihi/Kültürel", "lat": 41.0100, "lon": 28.9720,
     "bolge": "Çemberlitaş", "aciklama": "Barok mimari."},
    {"isim": "Kamondo Merdivenleri", "kategori": "Tarihi/Kültürel", "lat": 41.0244, "lon": 28.9730, "bolge": "Galata",
     "aciklama": "Art Nouveau merdivenler."},
    {"isim": "Panorama 1453", "kategori": "Tarihi/Kültürel", "lat": 41.0180, "lon": 28.9200, "bolge": "Topkapı",
     "aciklama": "Fetih müzesi."},
    {"isim": "Miniatürk", "kategori": "Tarihi/Kültürel", "lat": 41.0603, "lon": 28.9486, "bolge": "Haliç",
     "aciklama": "Minyatür Türkiye."},
    {"isim": "Arkeoloji Müzesi", "kategori": "Tarihi/Kültürel", "lat": 41.0116, "lon": 28.9813, "bolge": "Sultanahmet",
     "aciklama": "İskender lahdi."},
    {"isim": "Aya İrini", "kategori": "Tarihi/Kültürel", "lat": 41.0090, "lon": 28.9810, "bolge": "Sultanahmet",
     "aciklama": "Tarihi kilise."},
    {"isim": "Sakıp Sabancı Müzesi", "kategori": "Sanat/Kültür", "lat": 41.1060, "lon": 29.0550, "bolge": "Emirgan",
     "aciklama": "Atlı Köşk."},
    {"isim": "Rahmi Koç Müzesi", "kategori": "Sanat/Kültür", "lat": 41.0415, "lon": 28.9490, "bolge": "Hasköy",
     "aciklama": "Endüstri tarihi."},
    {"isim": "Oyuncak Müzesi", "kategori": "Sanat/Kültür", "lat": 40.9760, "lon": 29.0720, "bolge": "Göztepe",
     "aciklama": "Nostaljik oyuncaklar."},
    {"isim": "Masumiyet Müzesi", "kategori": "Sanat/Kültür", "lat": 41.0300, "lon": 28.9780, "bolge": "Çukurcuma",
     "aciklama": "Orhan Pamuk eseri."},
    {"isim": "İstanbul Modern", "kategori": "Sanat/Kültür", "lat": 41.0260, "lon": 28.9820, "bolge": "Karaköy",
     "aciklama": "Modern sanat."},
    {"isim": "Pera Müzesi", "kategori": "Sanat/Kültür", "lat": 41.0318, "lon": 28.9750, "bolge": "Tepebaşı",
     "aciklama": "Kaplumbağa Terbiyecisi."},
    {"isim": "SALT Galata", "kategori": "Sanat/Kültür", "lat": 41.0238, "lon": 28.9735, "bolge": "Karaköy",
     "aciklama": "Kütüphane ve sanat."},
    {"isim": "Arter", "kategori": "Sanat/Kültür", "lat": 41.0390, "lon": 28.9830, "bolge": "Dolapdere",
     "aciklama": "Çağdaş sanat."},
    {"isim": "Denizcilik Müzesi", "kategori": "Sanat/Kültür", "lat": 41.0410, "lon": 29.0060, "bolge": "Beşiktaş",
     "aciklama": "Denizcilik tarihi."},
    {"isim": "AKM", "kategori": "Sanat/Kültür", "lat": 41.0360, "lon": 28.9880, "bolge": "Taksim",
     "aciklama": "Kültür merkezi."},
    {"isim": "Belgrad Ormanı", "kategori": "Doğa/Park", "lat": 41.1792, "lon": 28.9900, "bolge": "Sarıyer",
     "aciklama": "Doğa yürüyüşü."},
    {"isim": "Emirgan Korusu", "kategori": "Doğa/Park", "lat": 41.1047, "lon": 29.0539, "bolge": "Sarıyer",
     "aciklama": "Lale bahçeleri."},
    {"isim": "Gülhane Parkı", "kategori": "Doğa/Park", "lat": 41.0127, "lon": 28.9800, "bolge": "Sultanahmet",
     "aciklama": "Tarihi park."},
    {"isim": "Yıldız Parkı", "kategori": "Doğa/Park", "lat": 41.0450, "lon": 29.0150, "bolge": "Beşiktaş",
     "aciklama": "Şehir içi koru."},
    {"isim": "Polonezköy", "kategori": "Doğa/Park", "lat": 41.1100, "lon": 29.2100, "bolge": "Beykoz",
     "aciklama": "Tabiat parkı."},
    {"isim": "Adalar (Büyükada)", "kategori": "Doğa/Park", "lat": 40.8746, "lon": 29.1287, "bolge": "Adalar",
     "aciklama": "Prens Adaları."},
    {"isim": "Çamlıca Tepesi", "kategori": "Doğa/Park", "lat": 41.0280, "lon": 29.0670, "bolge": "Üsküdar",
     "aciklama": "Manzara noktası."},
    {"isim": "Atatürk Arboretumu", "kategori": "Doğa/Park", "lat": 41.1750, "lon": 28.9750, "bolge": "Bahçeköy",
     "aciklama": "Canlı ağaç müzesi."},
    {"isim": "Kuzguncuk", "kategori": "Doğa/Park", "lat": 41.0360, "lon": 29.0300, "bolge": "Üsküdar",
     "aciklama": "Tarihi mahalle."},
    {"isim": "Bebek Sahili", "kategori": "Doğa/Park", "lat": 41.0760, "lon": 29.0430, "bolge": "Bebek",
     "aciklama": "Sahil yürüyüşü."},
    {"isim": "Ortaköy Sahili", "kategori": "Doğa/Park", "lat": 41.0474, "lon": 29.0264, "bolge": "Ortaköy",
     "aciklama": "Boğaz manzarası."},
    {"isim": "Pierre Loti", "kategori": "Doğa/Park", "lat": 41.0530, "lon": 28.9330, "bolge": "Eyüp",
     "aciklama": "Haliç manzarası."},
    {"isim": "Ihlamur Kasrı", "kategori": "Doğa/Park", "lat": 41.0500, "lon": 29.0020, "bolge": "Beşiktaş",
     "aciklama": "Mesire yeri."}
]

df = pd.DataFrame(data)

# --- 4. UX & AI SIDEBAR ---
with st.sidebar:
    st.markdown("## 🦅 KONTROL MERKEZİ")

    # 4.1 ARAMA
    search = st.text_input("🔍 Mekan Ara", placeholder="Örn: Glutensiz, Galata...")

    # 4.2 KONUM SEÇ (MESAFE İÇİN)
    st.markdown("### 📍 KONUMUN")
    centers = {
        "Seçim Yok": None,
        "Taksim": (41.0369, 28.9850),
        "Beşiktaş": (41.0428, 29.0075),
        "Kadıköy": (40.9910, 29.0210),
        "Nişantaşı": (41.0520, 28.9930),
        "Sultanahmet": (41.0054, 28.9768),
        "Etiler": (41.0830, 29.0200),
        "Maltepe": (40.9250, 29.1300)
    }
    selected_center_name = st.selectbox("Neredesin?", list(centers.keys()))
    user_coords = centers[selected_center_name]

    max_km = 100
    if user_coords:
        max_km = st.slider("Maksimum Mesafe (km)", 1, 20, 5)

    # 4.3 FİLTRELER
    st.markdown("### 📂 FİLTRELE")
    cats = st.multiselect("Kategori", df['kategori'].unique(), default=df['kategori'].unique())

    # VERİ FİLTRELEME MANTIĞI
    filtered_df = df[df['kategori'].isin(cats)].copy()

    # Mesafe Hesabı
    if user_coords:
        filtered_df['mesafe'] = filtered_df.apply(
            lambda row: geodesic(user_coords, (row['lat'], row['lon'])).km, axis=1
        )
        filtered_df = filtered_df[filtered_df['mesafe'] <= max_km]
        filtered_df = filtered_df.sort_values(by="mesafe")

    # Arama Filtresi
    if search:
        filtered_df = filtered_df[
            filtered_df['isim'].str.contains(search, case=False) | filtered_df['aciklama'].str.contains(search,
                                                                                                        case=False)]

    st.markdown("---")

    # 4.4 AI CHATBOT
    st.markdown("### 🤖 REHBERİNE SOR")
    api_key = st.text_input("API Key (Opsiyonel)", type="password")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    prompt = st.chat_input("Örn: Nişantaşı'nda glutensiz tatlı?")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        if api_key:
            openai.api_key = api_key
            try:
                # Context'i sınırlı tutarak AI'a gönderiyoruz
                context = filtered_df[['isim', 'bolge', 'aciklama']].head(20).to_json()
                response = openai.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": f"Sen İstanbul rehberisin. Data: {context}. Kısa cevapla."},
                        {"role": "user", "content": prompt}
                    ]
                )
                bot_reply = response.choices[0].message.content
                st.session_state.messages.append({"role": "assistant", "content": bot_reply})
                st.rerun()
            except:
                st.error("API Hatası")
        else:
            st.warning("API Key gerekli.")

# --- 5. ANA EKRAN ---
st.markdown(f"### 📍 BULUNAN MEKAN: {len(filtered_df)}")

col_list, col_map = st.columns([4, 8], gap="medium")

# --- SOL LİSTE ---
with col_list:
    if filtered_df.empty:
        st.warning("Kriterlere uygun yer yok.")
    else:
        for idx, row in filtered_df.iterrows():
            map_url = f"https://www.google.com/maps/search/?api=1&query={row['lat']},{row['lon']}"

            # Etiket Rengi
            tag_class = "tag-vegan" if "Vegan" in row['kategori'] else "tag-tarih" if "Tarih" in row[
                'kategori'] else "tag-doga"

            # Mesafe Rozeti
            dist_badge = f"{row['mesafe']:.1f} km" if user_coords else ""

            st.markdown(f"""
            <div class="place-card">
                <div style="display:flex; justify-content:space-between;">
                    <div style="font-weight:bold; font-size:16px;">{row['isim']}</div>
                    <div class="distance-badge">{dist_badge}</div>
                </div>
                <div style="margin:5px 0;">
                    <span class="tag {tag_class}">{row['kategori']}</span>
                    <span style="font-size:12px; color:#aaa;">📍 {row['bolge']}</span>
                </div>
                <div style="font-size:13px; color:#ccc;">{row['aciklama']}</div>
                <a href="{map_url}" target="_blank" class="action-btn">YOL TARİFİ ➔</a>
            </div>
            """, unsafe_allow_html=True)

# --- SAĞ HARİTA ---
with col_map:
    # Merkez Belirle
    if user_coords:
        center = user_coords
        zoom = 13
    elif not filtered_df.empty:
        center = [filtered_df['lat'].mean(), filtered_df['lon'].mean()]
        zoom = 11
    else:
        center = [41.0082, 28.9784]
        zoom = 11

    m = folium.Map(location=center, zoom_start=zoom, tiles="CartoDB dark_matter")
    Fullscreen().add_to(m)
    LocateControl().add_to(m)

    # Kullanıcı Konumu (Varsa)
    if user_coords:
        folium.Marker(user_coords, icon=folium.Icon(color="red", icon="user"), popup="Konumum").add_to(m)
        folium.Circle(user_coords, radius=max_km * 1000, color="#10b981", fill=True, fill_opacity=0.1).add_to(m)

    marker_cluster = MarkerCluster().add_to(m)

    for idx, row in filtered_df.iterrows():
        # İkon
        if "Vegan" in row['kategori']:
            color, icon = "green", "leaf"
        elif "Tarihi" in row['kategori']:
            color, icon = "blue", "university"
        elif "Doğa" in row['kategori']:
            color, icon = "orange", "tree"
        else:
            color, icon = "purple", "palette"

        popup_html = f"<b>{row['isim']}</b><br>{row['aciklama']}"

        folium.Marker(
            [row['lat'], row['lon']],
            popup=folium.Popup(popup_html, max_width=200),
            tooltip=row['isim'],
            icon=folium.Icon(color=color, icon=icon, prefix="fa")
        ).add_to(marker_cluster)

    st_folium(m, width="100%", height=800)