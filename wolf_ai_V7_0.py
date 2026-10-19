# -*- coding: utf-8 -*-
"""
WOLF AI V7 - Web/Konsol Asistanı (V7.0)
- Sade menü: 6 ana başlık, istersen doğrudan yazarak kullan ("not süt al", "hava İstanbul")
- Yeni: yazı asistanı, hava durumu, harcama takibi, günlük, her yerde ara, veri yedeği, cevap tarzı
- Sohbet hafızası, web araması & Wolf Yorumu, görsel oluşturma, ödev yardımcısı
"""
import base64, datetime, hashlib, hmac, secrets, html as html_lib, json, math, os, random, re, ssl, subprocess, sys, time
from urllib.parse import quote, quote_plus, urlparse, parse_qs
from urllib.request import Request, urlopen

try:
    from getpass import getpass
except ImportError:
    getpass = input

MAKS_HAK = 3
RESIM_API = "https://image.pollinations.ai/prompt/"
# .exe olarak çalışırken dosyalar exe'nin yanına, normalde scriptin yanına kaydedilir
BASE_DIR = (os.path.dirname(sys.executable) if getattr(sys, "frozen", False)
            else os.path.dirname(os.path.abspath(__file__)))
HAFIZA_DOSYASI = os.path.join(BASE_DIR, "wolf_memory.json")
KULLANICI_DOSYASI = os.path.join(BASE_DIR, "wolf_users.json")

YESIL = "\033[92m"; KIRMIZI = "\033[91m"; SARI = "\033[93m"
MAVI = "\033[94m"; MOR = "\033[95m"; CYAN = "\033[96m"; RESET = "\033[0m"

YARDIM_METNI = (
    "🐺 Neler yapabilirim?\n"
    "• Sohbet: Her konuda yapay zeka ile konuşurum\n"
    "• ara <konu>: Web'de arar ve yorumlarım\n"
    "• resim <tanım>: Yapay zeka ile görsel üretirim\n"
    "• çevir <metin>  veya  çevir ingilizce: <metin>: Çeviri yaparım\n"
    "• Ana menüde doğrudan yaz: not <metin>, görev <metin>, hava <şehir>, bul <kelime>\n"
    "• Ana menü: 1 Sohbet, 2 Ödev ve yazı, 3 Günlük işler, 4 Araçlar, 5 Eğlence, 6 Ben\n"
    "• saat, tarih, şaka gibi hızlı komutlar\n"
    "• Sohbet geçmişini hatırlarım"
)

SAKALAR = [
    "Bilgisayar neden doktora gitmiş? Çünkü virüs kapmış. 😂",
    "Programcı neden kahve içer? Çünkü Java lazım! ☕",
    "Python neden yılan? Çünkü öyle denk gelmiş. 🐍",
    "Bilgisayarın en sevdiği yemek nedir? RAMen! 🍜",
]


# ------------------------------------------------------------------- LOGO
LOGO_ASCII = r"""
      /\                  /\
     /  \________________/  \
    / /|                  |\ \
   / / |   \\        //   | \ \
  |  | |    @@      @@    | |  |
  |  \_|     \\    //     |_/  |
   \    \        /\        /    /
    \    \      /  \      /    /
     \    \____/ /\ \____/    /
      \        \ \/ /        /
       \________\__/________/
"""

LOGO_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 600" width="512" height="600">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#0f172a"/><stop offset="1" stop-color="#1e293b"/>
    </linearGradient>
    <linearGradient id="fur" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#f1f5f9"/><stop offset="1" stop-color="#94a3b8"/>
    </linearGradient>
    <radialGradient id="eye" cx="0.5" cy="0.5" r="0.5">
      <stop offset="0" stop-color="#fde047"/><stop offset="1" stop-color="#f59e0b"/>
    </radialGradient>
  </defs>
  <rect width="512" height="600" rx="48" fill="#020617"/>
  <circle cx="256" cy="256" r="230" fill="url(#bg)" stroke="#38bdf8" stroke-width="8"/>
  <circle cx="256" cy="256" r="212" fill="none" stroke="#38bdf8" stroke-opacity="0.35" stroke-width="2"/>
  <!-- kurt başı -->
  <path d="M256 436 L212 404 L160 336 L126 236 L136 96 L214 168 L256 158 L298 168 L376 96 L386 236 L352 336 L300 404 Z"
        fill="url(#fur)" stroke="#e2e8f0" stroke-width="4" stroke-linejoin="round"/>
  <!-- iç kulaklar -->
  <path d="M148 140 L196 182 L150 214 Z" fill="#334155"/>
  <path d="M364 140 L316 182 L362 214 Z" fill="#334155"/>
  <!-- alın deseni -->
  <path d="M256 172 L222 180 L240 238 L256 222 L272 238 L290 180 Z" fill="#64748b"/>
  <!-- yanak çizgileri -->
  <path d="M138 262 L196 300 L176 332 Z" fill="#cbd5e1"/>
  <path d="M374 262 L316 300 L336 332 Z" fill="#cbd5e1"/>
  <!-- gözler -->
  <path d="M184 252 L240 268 L204 288 Z" fill="url(#eye)" stroke="#0f172a" stroke-width="3" stroke-linejoin="round"/>
  <path d="M328 252 L272 268 L308 288 Z" fill="url(#eye)" stroke="#0f172a" stroke-width="3" stroke-linejoin="round"/>
  <circle cx="214" cy="268" r="6" fill="#0f172a"/>
  <circle cx="298" cy="268" r="6" fill="#0f172a"/>
  <!-- burun ve ağız -->
  <path d="M256 300 L256 372" stroke="#475569" stroke-width="4"/>
  <path d="M226 372 L286 372 L256 404 Z" fill="#0f172a"/>
  <path d="M256 404 L256 424" stroke="#475569" stroke-width="4"/>
  <!-- yazı -->
  <text x="256" y="548" text-anchor="middle" font-family="Segoe UI, Arial, sans-serif"
        font-size="60" font-weight="800" letter-spacing="8" fill="#f8fafc">WOLF <tspan fill="#38bdf8">AI</tspan></text>
  <text x="256" y="582" text-anchor="middle" font-family="Segoe UI, Arial, sans-serif"
        font-size="18" letter-spacing="6" fill="#94a3b8">V7</text>
</svg>
"""


def logo_goster():
    """Renkli ASCII kurt logosunu ekrana basar."""
    print(CYAN + LOGO_ASCII + RESET)
    print((MOR + "W O L F   A I   V 7" + RESET).center(64 + len(MOR) + len(RESET)))


def logo_svg_kaydet():
    """Vektörel logoyu wolf_logo/wolf_logo.svg olarak kaydeder. Dosya yolunu döner."""
    klasor = os.path.join(BASE_DIR, "wolf_logo")
    os.makedirs(klasor, exist_ok=True)
    yol = os.path.join(klasor, "wolf_logo.svg")
    with open(yol, "w", encoding="utf-8") as f:
        f.write(LOGO_SVG)
    return yol


def logo_png_kaydet(svg_yolu):
    """cairosvg kuruluysa SVG'yi PNG'ye çevirir; değilse None döner."""
    try:
        import cairosvg
        png = svg_yolu[:-4] + ".png"
        cairosvg.svg2png(url=svg_yolu, write_to=png, output_width=1024)
        return png
    except Exception:
        return None


def logo_olustur():
    baslik("🐺 WOLF AI V7 - LOGO")
    logo_goster()
    print("\n1 - 🖼️  Hazır Wolf logosunu kaydet (SVG, çevrimdışı)")
    print("2 - 🎨 Yapay zeka ile yeni logo tasarla")
    print("0 - Geri")
    sec = input("\nSeçiminiz: ").strip()
    if sec == "1":
        yol = logo_svg_kaydet()
        print(f"{YESIL}✓ Logo kaydedildi: {yol}{RESET}")
        png = logo_png_kaydet(yol)
        if png:
            print(f"{YESIL}✓ PNG sürümü: {png}{RESET}")
        else:
            print(f"{SARI}PNG için: pip install cairosvg  (SVG dosyası tarayıcıda açılır){RESET}")
        try:
            if os.name == "nt":
                os.startfile(png or yol)
        except OSError:
            pass
    elif sec == "2":
        stil = input("Logo stili/rengi (boş = mavi minimalist): ").strip() or "mavi minimalist"
        prompt = (f"professional vector logo of a wolf head, {stil} style, flat design, "
                  "clean shapes, centered, plain background, text 'WOLF AI'")
        print("Logo hazırlanıyor...")
        yol, hata = resim_uret(prompt)
        if yol:
            print(f"{YESIL}✓ Kaydedildi: {yol}{RESET}")
        else:
            print(f"{KIRMIZI}✗ {hata}{RESET}")
            svg = logo_svg_kaydet()
            print(f"{SARI}↳ Yedek olarak hazır Wolf logosu kaydedildi: {svg}{RESET}")


def tr_lower(s):
    """Türkçe uyumlu küçük harfe çevirme (I -> ı, İ -> i)."""
    return s.replace("İ", "i").replace("I", "ı").lower()


def baslik(metin):
    print("\n" + "=" * 64)
    print(metin.center(64))
    print("=" * 64)


def bekle():
    input("\nDevam etmek için Enter'a bas...")


# ------------------------------------------------------------ hesap sistemi
HASH_TURU = 200_000
_AKTIF_KULLANICI = None
_SON_KILITLI = False


def kullanicilari_yukle():
    try:
        with open(KULLANICI_DOSYASI, "r", encoding="utf-8") as f:
            veri = json.load(f)
        return veri if isinstance(veri, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def kullanicilari_kaydet(veri):
    gecici = KULLANICI_DOSYASI + ".tmp"
    with open(gecici, "w", encoding="utf-8") as f:
        json.dump(veri, f, ensure_ascii=False, indent=2)
    os.replace(gecici, KULLANICI_DOSYASI)


def sifre_hashle(sifre, tuz=None):
    tuz = tuz or secrets.token_bytes(16)
    h = hashlib.pbkdf2_hmac("sha256", sifre.encode("utf-8"), tuz, HASH_TURU)
    return tuz.hex(), h.hex()


def kullanici_kaydet(ad, sifre):
    """Yeni hesap açar (e-posta gerekmez). (gorunen_ad, mesaj) döner; başarısızsa gorunen_ad None."""
    ad = (ad or "").strip()
    if not re.fullmatch(r"[A-Za-z0-9_çğıöşüÇĞİÖŞÜ]{3,20}", ad):
        return None, "Kullanıcı adı 3-20 karakter olmalı (harf, rakam veya _)."
    if len(sifre) < 6:
        return None, "Şifre en az 6 karakter olmalı."
    if len(sifre) > 128:
        return None, "Şifre en fazla 128 karakter olabilir."
    veri = kullanicilari_yukle()
    anahtar = tr_lower(ad)
    if anahtar in veri:
        return None, "Bu kullanıcı adı zaten alınmış."
    tuz, h = sifre_hashle(sifre)
    veri[anahtar] = {"ad": ad, "tuz": tuz, "hash": h,
                     "olusturma": datetime.datetime.now().isoformat(timespec="seconds")}
    try:
        kullanicilari_kaydet(veri)
    except OSError as e:
        return None, f"Hesap kaydedilemedi: {e}"
    return ad, "Hesap oluşturuldu."


def kullanici_dogrula(ad, sifre):
    """Doğruysa kullanıcının görünen adını, değilse None döner."""
    global _SON_KILITLI
    _SON_KILITLI = False
    kayit = kullanicilari_yukle().get(tr_lower((ad or "").strip()))
    tuz = bytes.fromhex(kayit["tuz"]) if kayit else b"\x00" * 16
    _, h = sifre_hashle(sifre or "", tuz)
    if kayit and hmac.compare_digest(h, kayit["hash"]):
        if kayit.get("kilitli"):
            _SON_KILITLI = True      # şifre doğru ama hesap kilitli
            return None
        return kayit["ad"]
    return None


def aktif_kullanici_ayarla(ad):
    global _AKTIF_KULLANICI
    _AKTIF_KULLANICI = ad


def hafiza_dosya_yolu():
    """Her kullanıcının sohbet hafızası ayrı dosyada tutulur."""
    if not _AKTIF_KULLANICI:
        return HAFIZA_DOSYASI
    guvenli = re.sub(r"[^\w]", "_", tr_lower(_AKTIF_KULLANICI))
    return os.path.join(BASE_DIR, f"wolf_memory_{guvenli}.json")


# ------------------------------------------------------- GELİŞTİRİCİ PANELİ
# Gizli kod burada düz metin olarak durmaz; sadece tuzlu hash'i saklanır.
DEV_TUZ = "22fd5d5a379b86b11442146b86e6c8c5"
DEV_HASH = "d5ff0c1484a2a6d01df74c1df2ef5bdabbe9f65d4b6ff76e711539d93c349079"


DEV_DOSYASI = os.path.join(BASE_DIR, "wolf_dev.json")


def _dev_kayit():
    """Değiştirilmiş geliştirici kodu varsa (tuz, hash) döner; yoksa kaynaktaki varsayılan."""
    try:
        with open(DEV_DOSYASI, "r", encoding="utf-8") as f:
            v = json.load(f)
        if isinstance(v, dict) and v.get("tuz") and v.get("hash"):
            return v["tuz"], v["hash"]
    except (OSError, json.JSONDecodeError):
        pass
    return DEV_TUZ, DEV_HASH


def gelistirici_kodu_dogru(kod):
    kod = (kod or "").strip().upper()
    tuz, hedef = _dev_kayit()
    try:
        h = hashlib.pbkdf2_hmac("sha256", kod.encode("utf-8"), bytes.fromhex(tuz), HASH_TURU)
    except ValueError:
        return False
    return hmac.compare_digest(h.hex(), hedef)


def _dev_json():
    try:
        with open(DEV_DOSYASI, "r", encoding="utf-8") as f:
            v = json.load(f)
        return v if isinstance(v, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def _dev_json_yaz(veri):
    try:
        gecici = DEV_DOSYASI + ".tmp"
        with open(gecici, "w", encoding="utf-8") as f:
            json.dump(veri, f)
        os.replace(gecici, DEV_DOSYASI)
        return True
    except OSError as e:
        print(f"{KIRMIZI}✗ Kaydedilemedi: {e}{RESET}")
        return False


def gelistirici_kodu_degistir():
    """Yeni geliştirici kodu belirler (özel şifre kaydını korur). Başarılıysa True döner."""
    yeni = getpass("Yeni geliştirici kodu (en az 8 karakter): ").strip().upper()
    if len(yeni) < 8 or len(yeni) > 64:
        print(f"{KIRMIZI}✗ Kod 8-64 karakter olmalı.{RESET}")
        return False
    if getpass("Yeni kodu tekrar yaz: ").strip().upper() != yeni:
        print(f"{KIRMIZI}✗ Kodlar eşleşmedi.{RESET}")
        return False
    tuz = secrets.token_bytes(16)
    h = hashlib.pbkdf2_hmac("sha256", yeni.encode("utf-8"), tuz, HASH_TURU)
    veri = _dev_json()
    veri["tuz"], veri["hash"] = tuz.hex(), h.hex()
    if _dev_json_yaz(veri):
        print(f"{YESIL}✓ Geliştirici kodu değiştirildi. (Kod büyük harfe çevrilerek saklanır.){RESET}")
        return True
    return False


def ozel_sifre_belirle():
    """Kodu unutursan kullanılacak 'özel şifre'yi (kurtarma şifresi) belirler. Sadece hash'i saklanır."""
    print("Özel şifre, geliştirici kodunu unutursan 'unuttum' yazınca sorulur. Kodundan FARKLI ve tahmin edilmesi zor olsun.")
    yeni = getpass("Yeni özel şifre (en az 8 karakter): ")
    if not 8 <= len(yeni) <= 64:
        print(f"{KIRMIZI}✗ Özel şifre 8-64 karakter olmalı.{RESET}")
        return False
    if gelistirici_kodu_dogru(yeni):
        print(f"{KIRMIZI}✗ Özel şifre geliştirici kodunla aynı olamaz.{RESET}")
        return False
    if getpass("Özel şifreyi tekrar yaz: ") != yeni:
        print(f"{KIRMIZI}✗ Şifreler eşleşmedi.{RESET}")
        return False
    tuz = secrets.token_bytes(16)
    h = hashlib.pbkdf2_hmac("sha256", yeni.encode("utf-8"), tuz, HASH_TURU)
    veri = _dev_json()
    veri["kurtarma_tuz"], veri["kurtarma_hash"] = tuz.hex(), h.hex()
    if _dev_json_yaz(veri):
        print(f"{YESIL}✓ Özel şifre kaydedildi. Bunu güvenli bir yere not et; kendisi geri okunamaz.{RESET}")
        return True
    return False


def kodu_kurtar():
    """Özel şifreyi doğrularsa yeni geliştirici kodu belirletir. Başarılıysa True döner."""
    veri = _dev_json()
    try:
        tuz = bytes.fromhex(veri.get("kurtarma_tuz", ""))
    except ValueError:
        tuz = b""
    if not tuz or not veri.get("kurtarma_hash"):
        print(f"{SARI}Özel şifre daha önce belirlenmemiş. Panelden 'o' komutuyla belirleyebilirsin.{RESET}")
        return False
    for hak in range(MAKS_HAK, 0, -1):
        h = hashlib.pbkdf2_hmac("sha256", getpass("Özel şifre: ").encode("utf-8"), tuz, HASH_TURU)
        if hmac.compare_digest(h.hex(), veri["kurtarma_hash"]):
            panel_log("gelistirici", "Kurtarma", "özel şifre doğrulandı")
            print(f"{YESIL}✓ Doğrulandı. Şimdi yeni geliştirici kodunu belirle.{RESET}")
            if gelistirici_kodu_degistir():
                panel_log("gelistirici", "Kurtarma", "geliştirici kodu kurtarma ile değiştirildi")
                return True
            return False
        print(f"{KIRMIZI}✗ Özel şifre hatalı. Kalan hak: {hak - 1}{RESET}")
    panel_log("gelistirici", "Kurtarma", "başarısız kurtarma denemesi")
    return False


YARDIMCI_DOSYASI = os.path.join(BASE_DIR, "wolf_yardimcilar.json")
PANEL_LOG = os.path.join(BASE_DIR, "wolf_panel_log.txt")
DUYURU_DOSYASI = os.path.join(BASE_DIR, "wolf_duyuru.txt")
YEDEK_KLASORU = os.path.join(BASE_DIR, "wolf_yedekler")
GELISTIRICI_KOMUTLARI = {"r", "x", "i", "d", "s", "k", "y", "g", "b", "a", "n", "e", "u", "h", "q", "v", "o",
                         "c", "m", "z", "p"}
YARDIMCI_KOMUTLARI = {"r", "x", "i", "d", "a", "n", "h", "q", "c", "m", "z", "p"}


def panel_log(rol, kisi, olay):
    """Panelde yapılan her işlemi tarih/rol/kişi ile kayıt altına alır."""
    try:
        with open(PANEL_LOG, "a", encoding="utf-8") as f:
            f.write(f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S} | {rol} | {kisi} | {olay}\n")
    except OSError:
        pass


def rastgele_sifre(n=10):
    return "".join(secrets.choice("abcdefghjkmnpqrstuvwxyz23456789") for _ in range(n))


def yardimcilari_yukle():
    try:
        with open(YARDIMCI_DOSYASI, "r", encoding="utf-8") as f:
            v = json.load(f)
        return v if isinstance(v, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def yardimcilari_kaydet(v):
    gecici = YARDIMCI_DOSYASI + ".tmp"
    with open(gecici, "w", encoding="utf-8") as f:
        json.dump(v, f, ensure_ascii=False, indent=2)
    os.replace(gecici, YARDIMCI_DOSYASI)


def yardimci_dogrula(ad, kod):
    """Doğruysa yardımcının görünen adını, değilse None döner."""
    kayit = yardimcilari_yukle().get(tr_lower((ad or "").strip()))
    tuz = bytes.fromhex(kayit["tuz"]) if kayit else b"\x00" * 16
    _, h = sifre_hashle((kod or "").strip(), tuz)
    if kayit and hmac.compare_digest(h, kayit["hash"]):
        return kayit["ad"]
    return None


def kullanici_mesaj_sayisi(ad):
    """Sadece SAYI döner; sohbet içeriği panelde gösterilmez (kullanıcı gizliliği)."""
    guvenli = re.sub(r"[^\w]", "_", tr_lower(ad))
    try:
        with open(os.path.join(BASE_DIR, f"wolf_memory_{guvenli}.json"), "r", encoding="utf-8") as f:
            v = json.load(f)
        return sum(1 for m in v if isinstance(m, dict) and m.get("role") == "user")
    except (OSError, json.JSONDecodeError, TypeError):
        return 0


def istatistik_goster(veri):
    baslik("📊 İSTATİSTİKLER")
    toplam = len(veri)
    kilitli = sum(1 for k in veri.values() if k.get("kilitli"))
    sayilar = sorted(((kullanici_mesaj_sayisi(k.get("ad", a)), k.get("ad", a)) for a, k in veri.items()),
                     reverse=True)
    yeni = 0
    sinir = datetime.datetime.now() - datetime.timedelta(days=7)
    for k in veri.values():
        try:
            if datetime.datetime.fromisoformat(k.get("olusturma", "")) >= sinir:
                yeni += 1
        except ValueError:
            pass
    print(f"Toplam kullanıcı        : {toplam}")
    print(f"Kilitli hesap           : {kilitli}")
    print(f"Son 7 günde kayıt olan  : {yeni}")
    print(f"Yardımcı geliştirici    : {len(yardimcilari_yukle())}")
    print(f"Toplam kullanıcı sorusu : {sum(s for s, _ in sayilar)}")
    if sayilar:
        print("\nEn aktif kullanıcılar:")
        for s, ad in sayilar[:3]:
            print(f"  • {ad}: {s} soru")


def duyuru_ayarla(rol, kisi):
    try:
        with open(DUYURU_DOSYASI, "r", encoding="utf-8") as f:
            mevcut = f.read().strip()
    except OSError:
        mevcut = ""
    print(f"Mevcut duyuru: {mevcut or '(yok)'}")
    yeni = input("Yeni duyuru (boş = değiştirme, '-' = duyuruyu kaldır): ").strip()
    if not yeni:
        return
    try:
        with open(DUYURU_DOSYASI, "w", encoding="utf-8") as f:
            f.write("" if yeni == "-" else yeni[:300])
        panel_log(rol, kisi, "duyuru kaldırıldı" if yeni == "-" else "duyuru güncellendi")
        print(f"{YESIL}✓ Duyuru {'kaldırıldı' if yeni == '-' else 'kaydedildi'}.{RESET}")
    except OSError as e:
        print(f"{KIRMIZI}✗ Kaydedilemedi: {e}{RESET}")


def duyuru_goster():
    """Giriş yapan herkese geliştiricinin duyurusunu gösterir."""
    try:
        with open(DUYURU_DOSYASI, "r", encoding="utf-8") as f:
            metin = f.read().strip()
    except OSError:
        return
    if metin:
        print(f"\n{SARI}📢 DUYURU: {metin}{RESET}")


def yedek_al():
    import shutil
    temel = os.path.join(YEDEK_KLASORU, f"yedek_{datetime.datetime.now():%Y%m%d_%H%M%S}")
    hedef, sayac = temel, 1
    while os.path.exists(hedef):          # aynı saniyede alınan yedek eskisinin üstüne yazılmasın
        sayac += 1
        hedef = f"{temel}_{sayac}"
    os.makedirs(hedef)
    adet = 0
    for yol in (KULLANICI_DOSYASI, YARDIMCI_DOSYASI, DEV_DOSYASI, DUYURU_DOSYASI, MESAJ_DOSYASI):
        if os.path.exists(yol):
            shutil.copy2(yol, hedef)
            adet += 1
    return hedef, adet


def yardimcilari_yonet(kisi):
    while True:
        v = yardimcilari_yukle()
        sirali = sorted(v.items())
        baslik("👥 YARDIMCI GELİŞTİRİCİLER")
        if not sirali:
            print("Henüz yardımcı yok.")
        for n, (a, k) in enumerate(sirali, 1):
            print(f"{n:>3}  {k.get('ad', a):<22} {k.get('olusturma', '-')}")
        print("\ne - Yeni yardımcı ekle   r <numara> - Kodu yenile   s <numara> - Sil   0 - Geri")
        sec = tr_lower(input("\nSeçiminiz: ").strip())
        parca = sec.split()
        if sec in ("0", ""):
            return
        if sec == "e":
            ad = input("Yardımcı adı: ").strip()
            if not re.fullmatch(r"[A-Za-z0-9_çğıöşüÇĞİÖŞÜ]{3,20}", ad):
                print(f"{KIRMIZI}✗ Ad 3-20 karakter olmalı (harf, rakam veya _).{RESET}")
                continue
            if tr_lower(ad) in v:
                print(f"{KIRMIZI}✗ Bu yardımcı zaten var.{RESET}")
                continue
            kod = getpass("Yardımcı kodu (boş = otomatik üret): ").strip() or rastgele_sifre(8)
            if len(kod) < 6:
                print(f"{KIRMIZI}✗ Kod en az 6 karakter olmalı.{RESET}")
                continue
            tuz, h = sifre_hashle(kod)
            v[tr_lower(ad)] = {"ad": ad, "tuz": tuz, "hash": h,
                               "olusturma": datetime.datetime.now().isoformat(timespec="seconds")}
            yardimcilari_kaydet(v)
            panel_log("gelistirici", kisi, f"yardımcı eklendi: {ad}")
            print(f"{YESIL}✓ Yardımcı eklendi.{RESET}")
            print(f"{SARI}Ad: {ad}   Kod: {kod}{RESET}  (kodu ona ilet; sonra gösterilemez)")
            bekle()
        elif len(parca) == 2 and parca[0] in ("r", "s") and parca[1].isdigit() and 1 <= int(parca[1]) <= len(sirali):
            anahtar, k = sirali[int(parca[1]) - 1]
            if parca[0] == "r":
                kod = rastgele_sifre(8)
                k["tuz"], k["hash"] = sifre_hashle(kod)
                yardimcilari_kaydet(v)
                panel_log("gelistirici", kisi, f"yardımcı kodu yenilendi: {k['ad']}")
                print(f"{YESIL}✓ Yeni kod:{RESET} {SARI}{kod}{RESET}")
                bekle()
            elif input(f"{k['ad']} silinsin mi? (e/h): ").strip().lower() in ("e", "evet"):
                del v[anahtar]
                yardimcilari_kaydet(v)
                panel_log("gelistirici", kisi, f"yardımcı silindi: {k['ad']}")
                print(f"{YESIL}✓ Silindi.{RESET}")
        else:
            print("Geçersiz seçim.")


# --------------------------------------- PANEL V2: not, destek, giriş kaydı...
NOT_DOSYASI = os.path.join(BASE_DIR, "wolf_admin_notlar.json")
GIRIS_LOG = os.path.join(BASE_DIR, "wolf_giris_log.txt")
DESTEK_DOSYASI = os.path.join(BASE_DIR, "wolf_destek.json")
DISA_AKTAR_KLASORU = os.path.join(BASE_DIR, "wolf_disa_aktar")


def giris_logla(ad, durum):
    """Giriş denemesini kaydeder. Var olmayan adlar (yanlışlıkla yazılmış şifre olabilir) kaydedilmez."""
    var = tr_lower((ad or "").strip()) in kullanicilari_yukle()
    try:
        with open(GIRIS_LOG, "a", encoding="utf-8") as f:
            f.write(f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S} | {ad.strip() if var else '(bilinmeyen ad)'} | {durum}\n")
    except OSError:
        pass


def giris_kayitlari_goster():
    try:
        with open(GIRIS_LOG, "r", encoding="utf-8") as f:
            satirlar = f.read().strip().splitlines()
    except OSError:
        satirlar = []
    if not satirlar:
        print("Henüz giriş kaydı yok.")
        return
    sinir = datetime.datetime.now() - datetime.timedelta(hours=24)
    basarisiz = 0
    for s in satirlar:
        try:
            if "başarısız" in s and datetime.datetime.strptime(s[:19], "%Y-%m-%d %H:%M:%S") >= sinir:
                basarisiz += 1
        except ValueError:
            pass
    print(f"Son 24 saatte başarısız giriş: {basarisiz}\n\nSon girişler:")
    for s in satirlar[-15:]:
        print(("  " + (KIRMIZI if "başarısız" in s or "kilitli" in s else "") + s + RESET))


def not_yonet(rol, kisi, anahtar, ad):
    """Bir kullanıcı hakkında iç not (kullanıcı görmez). Geliştirici ve yardımcılar okuyup ekleyebilir."""
    notlar = _json_oku(NOT_DOSYASI, {})
    liste = notlar.get(anahtar, [])
    print(f"\n📝 {ad} hakkındaki notlar:")
    for x in liste[-10:]:
        print(f"  [{x.get('tarih', '')}] {x.get('kim', '')}: {x.get('metin', '')}")
    if not liste:
        print("  (not yok)")
    yeni = input("\nYeni not (boş = geri): ").strip()
    if yeni:
        liste.append({"kim": f"{'Geliştirici' if rol == 'gelistirici' else 'Yardımcı'} {kisi}",
                      "metin": yeni[:300], "tarih": datetime.datetime.now().strftime("%d.%m.%Y %H:%M")})
        notlar[anahtar] = liste
        if _json_yaz(NOT_DOSYASI, notlar):
            panel_log(rol, kisi, f"not eklendi: {ad}")
            print(f"{YESIL}✓ Not eklendi.{RESET}")


def kullanicilari_csv_aktar(veri):
    """Kullanıcı listesini CSV yapar. Şifre/hash İÇERMEZ."""
    import csv
    os.makedirs(DISA_AKTAR_KLASORU, exist_ok=True)
    yol = os.path.join(DISA_AKTAR_KLASORU, f"kullanicilar_{datetime.datetime.now():%Y%m%d_%H%M%S}.csv")
    with open(yol, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["kullanici_adi", "olusturma", "durum", "soru_sayisi"])
        for anahtar, k in sorted(veri.items()):
            ad = k.get("ad", anahtar)
            w.writerow([ad, k.get("olusturma", ""), "kilitli" if k.get("kilitli") else "aktif", kullanici_mesaj_sayisi(ad)])
    return yol


def kullanici_ekle_paneli(rol, kisi):
    ad = input("Yeni kullanıcı adı: ").strip()
    sifre = getpass("Şifre (boş = geçici şifre üret): ")
    uretildi = not sifre
    if uretildi:
        sifre = rastgele_sifre(10)
    gercek, mesaj = kullanici_kaydet(ad, sifre)
    if gercek:
        panel_log(rol, kisi, f"hesap oluşturuldu: {gercek}")
        print(f"{YESIL}✓ {mesaj}{RESET}")
        if uretildi:
            print(f"{SARI}Geçici şifre: {sifre}{RESET}  (kullanıcıya ilet; sonra gösterilemez)")
    else:
        print(f"{KIRMIZI}✗ {mesaj}{RESET}")


def yedekten_geri_yukle(rol, kisi):
    """Eski bir yedekten kullanıcı ve yardımcı dosyalarını geri yükler (önce mevcut durumu yedekler)."""
    import shutil
    try:
        yedekler = sorted(d for d in os.listdir(YEDEK_KLASORU) if os.path.isdir(os.path.join(YEDEK_KLASORU, d)))
    except OSError:
        yedekler = []
    if not yedekler:
        print("Henüz yedek yok. Önce 'b' ile yedek al.")
        return
    for n, d in enumerate(yedekler[-10:], 1):
        print(f"{n:>2}. {d}")
    sec = input("Geri yüklenecek yedek (numara, boş = vazgeç): ").strip()
    son = yedekler[-10:]
    if not sec.isdigit() or not 1 <= int(sec) <= len(son):
        return
    if input("Mevcut kullanıcılar bu yedekle DEĞİŞTİRİLECEK. Emin misin? (e/h): ").strip().lower() not in ("e", "evet"):
        return
    try:
        yedek_al()   # geri dönüş noktası
        kaynak = os.path.join(YEDEK_KLASORU, son[int(sec) - 1])
        for yol in (KULLANICI_DOSYASI, YARDIMCI_DOSYASI):
            kopya = os.path.join(kaynak, os.path.basename(yol))
            if os.path.exists(kopya):
                shutil.copy2(kopya, yol)
        panel_log(rol, kisi, f"yedekten geri yüklendi: {son[int(sec) - 1]}")
        print(f"{YESIL}✓ Geri yüklendi. (Önceki durum da yeni bir yedek olarak saklandı.){RESET}")
    except OSError as e:
        print(f"{KIRMIZI}✗ Geri yüklenemedi: {e}{RESET}")


# ---- destek talepleri
def destek_menu(kullanici):
    """Kullanıcı tarafı: geliştiriciye/yardımcıya yazı gönder, yanıtları gör."""
    while True:
        talepler = _json_oku(DESTEK_DOSYASI, [])
        benim = [t for t in talepler if tr_lower(t.get("kullanici", "")) == tr_lower(kullanici)]
        baslik("💬 DESTEK")
        print("1 - Yeni talep gönder")
        print(f"2 - Taleplerim ({len(benim)})")
        print("0 - Geri")
        sec = input("\nSeçiminiz: ").strip()
        if sec == "1":
            if sum(1 for t in benim if t.get("durum") == "açık") >= 5:
                print(f"{KIRMIZI}✗ En fazla 5 açık talebin olabilir. Önce yanıtları bekle.{RESET}")
                continue
            metin = input("Sorunun/isteğin: ").strip()
            if metin:
                yeni_id = max([t.get("id", 0) for t in talepler] + [0]) + 1
                talepler.append({"id": yeni_id, "kullanici": kullanici, "metin": metin[:500], "durum": "açık",
                                 "tarih": datetime.datetime.now().strftime("%d.%m.%Y %H:%M"), "yanitlar": []})
                if _json_yaz(DESTEK_DOSYASI, talepler):
                    print(f"{YESIL}✓ Talep #{yeni_id} gönderildi. Yanıtı 'Taleplerim'den görebilirsin.{RESET}")
        elif sec == "2":
            if not benim:
                print("Henüz talebin yok.")
            for t in benim:
                print(f"\n{SARI}#{t['id']} [{t.get('durum')}]{RESET} {t.get('tarih', '')}\n  Sen: {t.get('metin', '')}")
                for y in t.get("yanitlar", []):
                    print(f"  {YESIL}{y.get('kim', '')}:{RESET} {y.get('metin', '')}")
            bekle()
        elif sec in ("0", ""):
            return


def destek_yonet(rol, kisi):
    """Panel tarafı: talepleri listele, yanıtla, kapat/aç."""
    etiket = f"{'Geliştirici' if rol == 'gelistirici' else 'Yardımcı'} {kisi}"
    while True:
        talepler = _json_oku(DESTEK_DOSYASI, [])
        baslik("💬 DESTEK TALEPLERİ")
        if not talepler:
            print("Henüz talep yok.")
        for t in sorted(talepler, key=lambda x: (x.get("durum") != "açık", -x.get("id", 0)))[:20]:
            print(f"#{t['id']:<3} [{t.get('durum')}] {t.get('kullanici', '?'):<16} {_kisalt(t.get('metin', ''), 40)} "
                  f"({len(t.get('yanitlar', []))} yanıt)")
        print("\n<id> - Aç ve yanıtla   c <id> - Kapat/yeniden aç   0 - Geri")
        sec = tr_lower(input("\nSeçiminiz: ").strip()).split()
        if not sec or sec[0] == "0":
            return
        kapat = sec[0] == "c" and len(sec) == 2
        idtxt = sec[1] if kapat else sec[0]
        hedef = next((t for t in talepler if str(t.get("id")) == idtxt), None) if idtxt.isdigit() else None
        if not hedef:
            print("Geçersiz seçim.")
            continue
        if kapat:
            hedef["durum"] = "kapalı" if hedef.get("durum") == "açık" else "açık"
            _json_yaz(DESTEK_DOSYASI, talepler)
            panel_log(rol, kisi, f"talep #{hedef['id']} {hedef['durum']}")
            continue
        print(f"\n#{hedef['id']} - {hedef.get('kullanici')} ({hedef.get('tarih', '')}):\n  {hedef.get('metin', '')}")
        for y in hedef.get("yanitlar", []):
            print(f"  {YESIL}{y.get('kim', '')}:{RESET} {y.get('metin', '')}")
        yanit = input("\nYanıtın (boş = vazgeç): ").strip()
        if yanit:
            hedef.setdefault("yanitlar", []).append({"kim": etiket, "metin": yanit[:500]})
            if _json_yaz(DESTEK_DOSYASI, talepler):
                panel_log(rol, kisi, f"talep #{hedef['id']} yanıtlandı")
                print(f"{YESIL}✓ Yanıt gönderildi.{RESET}")


def panel_ac(rol, kisi):
    """Rol'e göre yetkileri sınırlanan ortak panel. rol: 'gelistirici' veya 'yardimci'."""
    gel = rol == "gelistirici"
    izinli = GELISTIRICI_KOMUTLARI if gel else YARDIMCI_KOMUTLARI
    filtre = ""
    while True:
        veri = kullanicilari_yukle()
        notlar = _json_oku(NOT_DOSYASI, {})
        sirali = sorted(veri.items())
        baslik("🛠️ GELİŞTİRİCİ PANELİ" if gel else "🧰 YARDIMCI GELİŞTİRİCİ PANELİ")
        print(f"Giriş yapan: {kisi}\n")
        if not sirali:
            print("Kayıtlı kullanıcı yok.")
        else:
            print(f"{'#':>3}  {'Kullanıcı adı':<22} {'Oluşturma':<20} Durum")
            for n, (anahtar, k) in enumerate(sirali, 1):
                if filtre and filtre not in tr_lower(k.get("ad", anahtar)):
                    continue
                durum = "🔒 kilitli" if k.get("kilitli") else "✓ aktif"
                ek = f"  hash {str(k.get('hash', ''))[:8]}…" if gel else ""
                nm = f" 📝{len(notlar[anahtar])}" if notlar.get(anahtar) else ""
                print(f"{n:>3}  {k.get('ad', anahtar):<22} {k.get('olusturma', '-'):<20} {durum}{ek}{nm}")
            if filtre:
                print(f"{SARI}Filtre: '{filtre}' (temizlemek için sadece 'a' yaz){RESET}")
            print(f"\n{SARI}Not: Şifreler tek yönlü hash olarak saklanır, geri okunamaz; "
                  f"gerekirse geçici şifre üretebilirsin.{RESET}")
        print("\nr <n> - Şifre sıfırla (boş = geçici şifre üret)   x <n> - Hesabı kilitle/aç")
        print("i - İstatistikler   d - Duyuru ayarla   a <kelime> - Kullanıcı ara")
        print("c <n> - Kullanıcı kartı   m <n> - Mesaj gönder" + ("  (m * = herkese)" if gel else "")
              + "   z - Sistem durumu   p - İşlemlerim")
        print("n <n> - Kullanıcı notları   h - Giriş kayıtları   q - Destek talepleri")
        if gel:
            print("s <n> - Hesabı sil   k - Geliştirici kodunu değiştir   y - Yardımcıları yönet")
            print("g - İşlem kaydı   b - Yedek al   v - Yedekten geri yükle")
            print("u - Kullanıcı ekle   e - Kullanıcıları CSV olarak aktar")
            print("o - Özel şifre (kod kurtarma) belirle/değiştir")
        print("0 - Çıkış")
        sec = input("\nSeçiminiz: ").strip()
        parca = tr_lower(sec).split()
        if not parca or parca[0] == "0":
            return
        komut = parca[0]
        if komut in GELISTIRICI_KOMUTLARI and komut not in izinli:
            print(f"{KIRMIZI}✗ Bu komut için yetkin yok.{RESET}")
            continue
        if komut == "i":
            istatistik_goster(veri); bekle()
        elif komut == "d":
            duyuru_ayarla(rol, kisi); bekle()
        elif komut == "k":
            gelistirici_kodu_degistir(); panel_log(rol, kisi, "geliştirici kodu değiştirildi"); bekle()
        elif komut == "y":
            yardimcilari_yonet(kisi)
        elif komut == "o":
            if ozel_sifre_belirle():
                panel_log(rol, kisi, "özel (kurtarma) şifre belirlendi")
            bekle()
        elif komut == "b":
            try:
                hedef, adet = yedek_al()
                panel_log(rol, kisi, f"yedek alındı ({adet} dosya)")
                print(f"{YESIL}✓ {adet} dosya yedeklendi: {hedef}{RESET}")
            except OSError as e:
                print(f"{KIRMIZI}✗ Yedek alınamadı: {e}{RESET}")
            bekle()
        elif komut == "g":
            try:
                with open(PANEL_LOG, "r", encoding="utf-8") as f:
                    satirlar = f.read().strip().splitlines()[-20:]
                print("\nSon işlemler:\n" + ("\n".join(satirlar) if satirlar else "(kayıt yok)"))
            except OSError:
                print("Henüz işlem kaydı yok.")
            bekle()
        elif komut == "a":
            filtre = tr_lower(" ".join(parca[1:]))
        elif komut == "h":
            giris_kayitlari_goster(); bekle()
        elif komut == "q":
            destek_yonet(rol, kisi)
        elif komut == "u":
            kullanici_ekle_paneli(rol, kisi); bekle()
        elif komut == "v":
            yedekten_geri_yukle(rol, kisi); bekle()
        elif komut == "e":
            try:
                yol = kullanicilari_csv_aktar(veri)
                panel_log(rol, kisi, "kullanıcı listesi CSV aktarıldı")
                print(f"{YESIL}✓ Aktarıldı (şifre içermez): {yol}{RESET}")
            except OSError as e:
                print(f"{KIRMIZI}✗ Aktarılamadı: {e}{RESET}")
            bekle()
        elif komut == "z":
            sistem_durumu(); bekle()
        elif komut == "p":
            islemlerim(rol, kisi); bekle()
        elif komut == "c" and len(parca) == 2 and parca[1].isdigit() and 1 <= int(parca[1]) <= len(sirali):
            kullanici_karti(*sirali[int(parca[1]) - 1]); bekle()
        elif komut == "m" and len(parca) == 2 and ((parca[1].isdigit() and 1 <= int(parca[1]) <= len(sirali))
                                                  or (gel and parca[1] == "*")):
            hedef_ad = "*" if parca[1] == "*" else sirali[int(parca[1]) - 1][1].get("ad", sirali[int(parca[1]) - 1][0])
            panelden_mesaj(rol, kisi, hedef_ad); bekle()
        elif komut == "n" and len(parca) == 2 and parca[1].isdigit() and 1 <= int(parca[1]) <= len(sirali):
            anahtar, k = sirali[int(parca[1]) - 1]
            not_yonet(rol, kisi, anahtar, k.get("ad", anahtar)); bekle()
        elif komut in ("r", "x", "s") and len(parca) == 2 and parca[1].isdigit() and 1 <= int(parca[1]) <= len(sirali):
            anahtar, k = sirali[int(parca[1]) - 1]
            ad = k.get("ad", anahtar)
            if komut == "r":
                yeni = getpass(f"{ad} için yeni şifre (boş = geçici şifre üret): ")
                uretildi = not yeni
                if uretildi:
                    yeni = rastgele_sifre(10)
                if not 6 <= len(yeni) <= 128:
                    print(f"{KIRMIZI}✗ Şifre 6-128 karakter olmalı.{RESET}")
                    continue
                k["tuz"], k["hash"] = sifre_hashle(yeni)
                kullanicilari_kaydet(veri)
                panel_log(rol, kisi, f"şifre sıfırlandı: {ad}")
                print(f"{YESIL}✓ Şifre sıfırlandı.{RESET}")
                if uretildi:
                    print(f"{SARI}Geçici şifre: {yeni}{RESET}  (kullanıcıya ilet; sonra gösterilemez)")
                    bekle()
            elif komut == "x":
                k["kilitli"] = not k.get("kilitli", False)
                kullanicilari_kaydet(veri)
                panel_log(rol, kisi, f"hesap {'kilitlendi' if k['kilitli'] else 'açıldı'}: {ad}")
                print(f"{YESIL}✓ {ad} hesabı {'kilitlendi' if k['kilitli'] else 'tekrar açıldı'}.{RESET}")
            else:
                if input(f"{ad} silinsin mi? (e/h): ").strip().lower() in ("e", "evet"):
                    del veri[anahtar]
                    kullanicilari_kaydet(veri)
                    panel_log(rol, kisi, f"hesap silindi: {ad}")
                    print(f"{YESIL}✓ Hesap silindi.{RESET}")
        else:
            print("Geçersiz seçim.")


def gelistirici_paneli():
    """Gizli geliştirici koduyla açılır (tam yetki)."""
    print("(Kodu unuttuysan 'unuttum' yaz.)")
    for hak in range(MAKS_HAK, 0, -1):
        girilen = getpass("Geliştirici kodu: ")
        if tr_lower(girilen.strip()) == "unuttum":
            if kodu_kurtar():
                break
            return
        if gelistirici_kodu_dogru(girilen):
            break
        print(f"{KIRMIZI}✗ Hatalı kod. Kalan hak: {hak - 1}{RESET}")
    else:
        return
    panel_log("gelistirici", "Geliştirici", "panele giriş")
    panel_ac("gelistirici", "Geliştirici")


def yardimci_paneli():
    """Yardımcı geliştirici adı + koduyla açılır (sınırlı yetki)."""
    for hak in range(MAKS_HAK, 0, -1):
        ad = input("Yardımcı adı: ").strip()
        gercek = yardimci_dogrula(ad, getpass("Yardımcı kodu: "))
        if gercek:
            break
        print(f"{KIRMIZI}✗ Ad veya kod hatalı. Kalan hak: {hak - 1}{RESET}")
    else:
        return
    panel_log("yardimci", gercek, "panele giriş")
    panel_ac("yardimci", gercek)


def giris_dongusu():
    hak = MAKS_HAK
    while hak:
        baslik("🐺 WOLF AI V7 - GİRİŞ")
        ad = input("Kullanıcı adı: ").strip()
        sifre = getpass("Şifre: ")
        gercek = kullanici_dogrula(ad, sifre)
        giris_logla(ad, "başarılı" if gercek else ("kilitli hesap" if _SON_KILITLI else "başarısız"))
        if gercek:
            print(f"\n{YESIL}✓ Giriş başarılı!{RESET}")
            aktif_kullanici_ayarla(gercek)
            return gercek
        if _SON_KILITLI:
            print(f"{KIRMIZI}🔒 Bu hesap kilitli. Geliştirici ile iletişime geç.{RESET}")
            return None
        hak -= 1
        print(f"{KIRMIZI}✗ Kullanıcı adı veya şifre yanlış. Kalan hak: {hak}{RESET}")
    print(f"{KIRMIZI}❌ Çok fazla hatalı deneme.{RESET}")
    return None


def kayit_ol_konsol():
    baslik("🐺 WOLF AI V7 - KAYIT OL")
    print("E-posta gerekmez. Kullanıcı adı: 3-20 karakter (harf, rakam, _). Şifre: en az 6 karakter.\n")
    ad = input("Kullanıcı adı: ").strip()
    sifre = getpass("Şifre: ")
    tekrar = getpass("Şifre (tekrar): ")
    if sifre != tekrar:
        print(f"{KIRMIZI}✗ Şifreler aynı değil.{RESET}")
        return None
    gercek, mesaj = kullanici_kaydet(ad, sifre)
    if not gercek:
        print(f"{KIRMIZI}✗ {mesaj}{RESET}")
        return None
    print(f"{YESIL}✓ {mesaj}{RESET}")
    aktif_kullanici_ayarla(gercek)
    return gercek


def giris_yap():
    while True:
        baslik("🐺 WOLF AI V7")
        print("1 - Giriş yap")
        print("2 - Kayıt ol")
        print("3 - Çıkış")
        if not kullanicilari_yukle():
            print(f"{SARI}Henüz hesap yok, önce 'Kayıt ol'u seç.{RESET}")
        sec = input("\nSeçiminiz: ").strip()
        if tr_lower(sec) == "dev":
            gelistirici_paneli(); continue
        if tr_lower(sec) == "yg":
            yardimci_paneli(); continue
        if sec == "1":
            return giris_dongusu()
        elif sec == "2":
            ad = kayit_ol_konsol()
            if ad:
                return ad
        elif sec == "3":
            return None
        else:
            print("Geçersiz seçim.")


def hafiza_yukle():
    try:
        with open(hafiza_dosya_yolu(), "r", encoding="utf-8") as f:
            veri = json.load(f)
        return veri if isinstance(veri, list) else []
    except (OSError, json.JSONDecodeError):
        return []


def hafiza_kaydet(gecmis):
    try:
        with open(hafiza_dosya_yolu(), "w", encoding="utf-8") as f:
            json.dump(gecmis[-30:], f, ensure_ascii=False, indent=2)
    except OSError:
        pass


def hafiza_ciftleri(gecmis):
    """Düz mesaj listesini (soru, cevap) çiftlerine ayırır. Her çift: {'u': soru, 'a': cevap veya None, 'idx': [indeksler]}."""
    ciftler = []
    for i, m in enumerate(gecmis):
        if not isinstance(m, dict):
            continue
        if m.get("role") == "user":
            ciftler.append({"u": str(m.get("content", "")), "a": None, "idx": [i]})
        elif ciftler and ciftler[-1]["a"] is None:
            ciftler[-1]["a"] = str(m.get("content", ""))
            ciftler[-1]["idx"].append(i)
    return ciftler


def _kisalt(metin, n=52):
    metin = re.sub(r"\s+", " ", metin or "").strip()
    return metin if len(metin) <= n else metin[:n - 1] + "…"


def hafiza_listesi():
    """Sohbet hafızasını numaralı liste olarak gösterir; arama, silme, temizleme ve dışa aktarma sunar."""
    while True:
        gecmis = hafiza_yukle()
        ciftler = hafiza_ciftleri(gecmis)
        baslik("🧠 WOLF AI V7 - SOHBET HAFIZASI")
        if not ciftler:
            print("Henüz kayıtlı sohbet yok. Biraz sohbet edince burada listelenir. 🐺")
            return
        print(f"Toplam {len(ciftler)} kayıt (en fazla son 30 mesaj saklanır)\n")
        for n, c in enumerate(ciftler, 1):
            print(f"{SARI}{n:>2}.{RESET} {_kisalt(c['u'])}")
        print("\n<numara> - Detay göster      a <kelime> - Hafızada ara")
        print("s <numara> - Kaydı sil        t - Tümünü temizle")
        print("d - Metin dosyasına aktar     0 - Geri")
        sec = input("\nSeçiminiz: ").strip()
        kucuk = tr_lower(sec)
        if kucuk in ("0", "", "geri"):
            return
        if sec.isdigit() and 1 <= int(sec) <= len(ciftler):
            c = ciftler[int(sec) - 1]
            print(f"\n{CYAN}Sen:{RESET} {c['u']}")
            print(f"{YESIL}🐺 Wolf:{RESET} {c['a'] if c['a'] else '(kayıtlı cevap yok)'}")
            bekle()
        elif kucuk.startswith("a "):
            kelime = tr_lower(sec[2:].strip())
            bulunan = [(n, c) for n, c in enumerate(ciftler, 1)
                       if kelime in tr_lower(c["u"]) or kelime in tr_lower(c["a"] or "")]
            print()
            if not bulunan:
                print("Eşleşen kayıt bulunamadı.")
            for n, c in bulunan:
                print(f"{SARI}{n:>2}.{RESET} {_kisalt(c['u'])}")
            bekle()
        elif kucuk.startswith("s ") and sec[2:].strip().isdigit():
            n = int(sec[2:].strip())
            if 1 <= n <= len(ciftler):
                sil = set(ciftler[n - 1]["idx"])
                hafiza_kaydet([m for i, m in enumerate(gecmis) if i not in sil])
                print(f"{YESIL}✓ {n}. kayıt silindi.{RESET}")
            else:
                print("Geçersiz numara.")
        elif kucuk == "t":
            if input("Tüm hafıza silinsin mi? (e/h): ").strip().lower() in ("e", "evet"):
                hafiza_kaydet([])
                print(f"{YESIL}✓ Hafıza temizlendi.{RESET}")
                return
        elif kucuk == "d":
            klasor = os.path.join(BASE_DIR, "wolf_hafiza_disa_aktar")
            os.makedirs(klasor, exist_ok=True)
            yol = os.path.join(klasor, f"hafiza_{datetime.datetime.now():%Y%m%d_%H%M%S}.txt")
            try:
                with open(yol, "w", encoding="utf-8") as f:
                    for n, c in enumerate(ciftler, 1):
                        f.write(f"[{n}] Sen: {c['u']}\n    Wolf: {c['a'] or '-'}\n\n")
                print(f"{YESIL}✓ Aktarıldı: {yol}{RESET}")
            except OSError as e:
                print(f"{KIRMIZI}✗ Dosya yazılamadı: {e}{RESET}")
        else:
            print("Geçersiz seçim.")


def temiz_metin(s):
    s = re.sub(r"<[^>]+>", " ", s or "")
    return re.sub(r"\s+", " ", html_lib.unescape(s)).strip()


def resim_uret(prompt, ac=True):
    """Görseli üretip kaydeder. (dosya_yolu, None) veya (None, hata_metni) döner.
    402/401/403 (ücretli/yetkisiz model) gelirse otomatik olarak sıradaki modele geçer.
    İstersen POLLINATIONS_API_KEY ortam değişkeniyle kendi anahtarını kullanabilirsin."""
    klasor = os.path.join(BASE_DIR, "wolf_resimler")
    os.makedirs(klasor, exist_ok=True)
    basliklar = dict(TARAYICI_BASLIKLARI)
    anahtar = os.environ.get("POLLINATIONS_API_KEY", "").strip()
    if anahtar:
        basliklar["Authorization"] = "Bearer " + anahtar
    # Sırayla denenecek (adres, model) çiftleri: ücretsiz olanlar önde
    secenekler = [(RESIM_API, ""), (RESIM_API, "turbo"), (RESIM_API, "flux"),
                  ("https://pollinations.ai/p/", "")]
    son_hata = None
    odeme_hatasi = 0
    for taban, model in secenekler:
        url = (taban + quote(prompt) +
               f"?width=1024&height=1024&nologo=true&seed={random.randint(1, 999999)}" +
               (f"&model={model}" if model else ""))
        for deneme in range(2):
            try:
                req = Request(url, headers=basliklar)
                with urlopen(req, timeout=90, context=ssl.create_default_context()) as r:
                    tur = r.headers.get("Content-Type", "")
                    veri = r.read()
                if not tur.startswith("image/") or len(veri) < 1000:
                    raise ValueError(f"Görsel yerine farklı bir cevap geldi ({tur or 'bilinmiyor'})")
                uzanti = "png" if "png" in tur else "webp" if "webp" in tur else "jpg"
                ad = re.sub(r"[^\w]+", "_", prompt, flags=re.U)[:30].strip("_") or "resim"
                yol = os.path.join(klasor, f"{ad}_{datetime.datetime.now():%Y%m%d_%H%M%S}.{uzanti}")
                with open(yol, "wb") as f:
                    f.write(veri)
                if ac:
                    try:
                        if os.name == "nt":
                            os.startfile(yol)
                    except OSError:
                        pass
                return yol, None
            except Exception as e:
                son_hata = e
                kod = getattr(e, "code", None)
                if kod in (401, 402, 403):   # tekrar denemek işe yaramaz, sıradaki modele geç
                    odeme_hatasi += 1
                    break
                time.sleep(2)
    if odeme_hatasi:
        return None, ("Görsel servisi (Pollinations) şu an ücretsiz kullanımı kısıtlamış (HTTP 402/401/403).\n"
                      "   Çözüm: https://auth.pollinations.ai adresinden ücretsiz anahtar alıp\n"
                      "   POLLINATIONS_API_KEY ortam değişkenine yaz (Windows: setx POLLINATIONS_API_KEY \"anahtar\").\n"
                      "   Ya da biraz sonra tekrar dene.")
    return None, (f"{son_hata}\n   Servis yoğun olabilir veya bağlantın engelleniyor olabilir "
                  "(VPN / DNS 1.1.1.1 dene). Biraz sonra tekrar dene.")


def resim_yap(prompt):
    if not prompt:
        return "Lütfen bir görsel tanımı yaz."
    print(f"\n{MOR}🎨 Görsel isteği alındı: '{prompt}'{RESET}")
    print(f"{CYAN}ℹ️ Görsel üretiliyor, 10-40 saniye sürebilir...{RESET}")
    yol, hata = resim_uret(prompt)
    if yol:
        return f"{YESIL}✓ Görsel oluşturuldu ve kaydedildi:{RESET} {yol}"
    return f"{KIRMIZI}⚠ Görsel üretilemedi: {hata}{RESET}"


def cozum_url(link):
    """DuckDuckGo yönlendirme adresini gerçek adrese çevirir."""
    link = html_lib.unescape(link)
    if link.startswith("//"):
        link = "https:" + link
    if "uddg=" in link:
        hedef = parse_qs(urlparse(link).query).get("uddg")
        if hedef:
            return hedef[0]
    return link


def _ddg_ayristir(sayfa, adet):
    # Her sonucu kendi bloğu içinde işle (snippet'siz sonuç karışmasın)
    baslangiclar = list(re.finditer(r'<a\b[^>]*class="[^"]*result__a[^"]*"[^>]*>', sayfa, re.I))
    sonuclar = []
    for i, m in enumerate(baslangiclar):
        son = baslangiclar[i + 1].start() if i + 1 < len(baslangiclar) else len(sayfa)
        etiket = m.group(0)
        href = re.search(r'href="([^"]+)"', etiket)
        if not href:
            continue
        govde = sayfa[m.end():son]
        kapanis = govde.find("</a>")
        baslik_metni = govde[:kapanis] if kapanis != -1 else ""
        snip = re.search(r'class="[^"]*result__snippet[^"]*"[^>]*>(.*?)</(?:a|div|td)>', govde, re.I | re.S)
        sonuclar.append({
            "title": temiz_metin(baslik_metni),
            "url": cozum_url(href.group(1)),
            "snippet": temiz_metin(snip.group(1)) if snip else "",
        })
        if len(sonuclar) >= adet:
            break
    return sonuclar, None


TARAYICI_BASLIKLARI = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
    "Connection": "close",
}


def sayfa_getir(url, veri=None, deneme=2):
    """Tarayıcı gibi istek atar; bağlantı kopsa tekrar dener."""
    son_hata = None
    for i in range(deneme):
        try:
            req = Request(url, data=veri, headers=TARAYICI_BASLIKLARI)
            with urlopen(req, timeout=15, context=ssl.create_default_context()) as r:
                return r.read().decode("utf-8", errors="ignore"), None
        except Exception as e:
            son_hata = e
            time.sleep(1.5)
    return None, son_hata


def bing_url(link):
    link = html_lib.unescape(link)
    if "bing.com/ck/a" in link:
        u = parse_qs(urlparse(link).query).get("u")
        if u and u[0].startswith("a1"):
            b = u[0][2:]
            b += "=" * (-len(b) % 4)
            try:
                return base64.urlsafe_b64decode(b).decode("utf-8")
            except Exception:
                pass
    return link


def _bing_ayristir(sayfa, adet):
    sonuclar = []
    for blok in re.findall(r'<li class="b_algo".*?</li>', sayfa, re.S):
        a = re.search(r'<h2[^>]*>\s*<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>', blok, re.S)
        if not a:
            continue
        p = re.search(r'<p[^>]*>(.*?)</p>', blok, re.S)
        sonuclar.append({
            "title": temiz_metin(a.group(2)),
            "url": bing_url(a.group(1)),
            "snippet": temiz_metin(p.group(1)) if p else "",
        })
        if len(sonuclar) >= adet:
            break
    return sonuclar


def web_ara(sorgu, adet=5):
    """Önce DuckDuckGo (POST, sonra GET), olmazsa Bing ile arar."""
    hatalar = []
    q = quote_plus(sorgu)

    sayfa, hata = sayfa_getir("https://html.duckduckgo.com/html/", ("q=" + q).encode())
    if sayfa is None:
        sayfa, hata = sayfa_getir("https://html.duckduckgo.com/html/?q=" + q)
    if sayfa is not None:
        sonuclar, _ = _ddg_ayristir(sayfa, adet)
        if sonuclar:
            return sonuclar, None
        hatalar.append("DuckDuckGo sonuç döndürmedi")
    else:
        hatalar.append(f"DuckDuckGo: {hata}")

    sayfa, hata = sayfa_getir("https://www.bing.com/search?setlang=tr&q=" + q)
    if sayfa is not None:
        sonuclar = _bing_ayristir(sayfa, adet)
        if sonuclar:
            return sonuclar, None
        hatalar.append("Bing sonuç döndürmedi")
    else:
        hatalar.append(f"Bing: {hata}")

    return [], ("Web bağlantısı kurulamadı. " + " | ".join(hatalar) +
                "\n   İpucu: VPN açmayı, DNS'i 1.1.1.1 / 8.8.8.8 yapmayı veya "
                "antivirüs/güvenlik duvarını kontrol etmeyi dene.")


def wolf_yorumu(sorgu, sonuclar):
    if not sonuclar:
        return "Bu aramada yeterli kaynak bulamadım."
    basliklar = " | ".join(x["title"] for x in sonuclar)
    kelimeler = re.findall(r"[a-zA-ZçğıöşüÇĞİÖŞÜ0-9]{5,}", tr_lower(sorgu + " " + basliklar))
    sayim = {}
    for k in kelimeler:
        sayim[k] = sayim.get(k, 0) + 1
    ortak = sorted(sayim.items(), key=lambda x: x[1], reverse=True)[:5]
    odak = ", ".join(k for k, v in ortak if v > 1) or "ana konu"
    return (
        f"🐺 Wolf'un yorumu: Kaynakların ortak odağı '{odak}'. "
        f"{len(sonuclar)} sonuç içindeki detaylar karşılaştırıldı."
    )


def web_arastir(sorgu):
    if not sorgu:
        print(f"{KIRMIZI}Lütfen aranacak bir şey yaz.{RESET}")
        return
    print(f"\n{SARI}🌐 Web araştırması: {sorgu}{RESET}")
    sonuclar, hata = web_ara(sorgu)
    if hata:
        print(f"{KIRMIZI}⚠ {hata}{RESET}")
        return
    if not sonuclar:
        print("Sonuç bulunamadı.")
        return
    for i, x in enumerate(sonuclar, 1):
        print(f"\n{i}. {MAVI}{x['title']}{RESET}")
        if x["snippet"]:
            print(f"   {x['snippet'][:350]}")
        print(f"   🔗 {x['url']}")
    print("\n" + "-" * 64)
    print(wolf_yorumu(sorgu, sonuclar))


def yerel_cevap(mesaj, kullanici):
    m = tr_lower(mesaj).strip()
    if m in ("çık", "cik", "exit", "quit"): return "ÇIKIŞ"
    if "neler yapabil" in m or m in ("yardım", "yardim", "komutlar", "help"): return YARDIM_METNI
    if "merhaba" in m or "selam" in m: return f"Merhaba {kullanici}! 🐺 Bugün ne üretiyoruz veya araştırıyoruz?"
    if "adın ne" in m or "kimsin" in m: return "Ben Wolf AI V7. Web araştırması yapabilen ve sohbet geçmişi tutan asistanım. 🐺"
    if "nasılsın" in m: return "Gayet iyiyim. CPU tarafı sakin, kurt tarafı hazır! 😄"
    if "şaka" in m: return random.choice(SAKALAR)
    if m == "logo" or "logo göster" in m:
        logo_goster(); return "Wolf AI logosu yukarıda! Kaydetmek için ana menüden L'yi seç. 🐺"
    if re.search(r"\bsaat\b", m): return "Şu anda saat " + datetime.datetime.now().strftime("%H:%M:%S") + "."
    if "tarih" in m: return "Bugünün tarihi " + datetime.datetime.now().strftime("%d/%m/%Y") + "."
    if "teşekkür" in m or "sağ ol" in m or "sağol" in m: return "Rica ederim! 🐺"
    return None


AI_API = "https://text.pollinations.ai/openai"
AI_SISTEM = ("Sen Wolf AI adında, Türkçe konuşan yardımsever bir asistansın. "
             "Kısa, net ve doğru cevap ver. Emin olmadığın şeyi uydurma.")


def ai_cevap(mesajlar, sistem=None):
    """Yapay zekadan cevap alır (ücretsiz, anahtarsız servis). (metin, hata) döner."""
    govde = json.dumps({
        "model": "openai",
        "messages": [{"role": "system", "content": sistem or AI_SISTEM}] + mesajlar,
    }).encode("utf-8")
    basliklar = dict(TARAYICI_BASLIKLARI)
    basliklar["Content-Type"] = "application/json"
    son_hata = None
    for _ in range(2):
        try:
            req = Request(AI_API, data=govde, headers=basliklar)
            with urlopen(req, timeout=60, context=ssl.create_default_context()) as r:
                veri = json.loads(r.read().decode("utf-8"))
            metin = (veri["choices"][0]["message"]["content"] or "").strip()
            if metin:
                return metin, None
            son_hata = "Boş cevap geldi"
        except Exception as e:
            son_hata = e
            time.sleep(1.5)
    # Yedek yol: düz GET isteği
    try:
        son = mesajlar[-1]["content"]
        url = "https://text.pollinations.ai/" + quote((sistem or AI_SISTEM) + "\n\nKullanıcı: " + son)
        sayfa, hata = sayfa_getir(url, deneme=1)
        if sayfa and sayfa.strip():
            return sayfa.strip(), None
        son_hata = hata or son_hata
    except Exception as e:
        son_hata = e
    return None, f"Yapay zeka servisine ulaşılamadı: {son_hata}"


def ai_mesajlari(gecmis, mesaj):
    """Son sohbet geçmişini + yeni mesajı API formatına çevirir."""
    liste = []
    for x in gecmis[-10:]:
        if isinstance(x, dict) and x.get("role") in ("user", "assistant") and isinstance(x.get("content"), str):
            liste.append({"role": x["role"], "content": ansi_temizle(x["content"])})
    liste.append({"role": "user", "content": mesaj})
    return liste


def ceviri(metin):
    """'ingilizce: merhaba' gibi hedef dil verilebilir; verilmezse otomatik çevirir."""
    m = re.match(r"^([A-Za-zÇĞİÖŞÜçğıöşü]+)\s*:\s*(.+)$", metin, re.S)
    if m:
        gorev = f"Aşağıdaki metni {m.group(1)} diline çevir."
        metin = m.group(2).strip()
    else:
        gorev = "Aşağıdaki metin Türkçeyse İngilizceye, başka bir dildeyse Türkçeye çevir."
    istek = f"{gorev} Sadece çeviriyi yaz, açıklama ekleme.\n\n{metin}"
    return ai_cevap([{"role": "user", "content": istek}])


def ai_sohbet(kullanici, ilk_mesaj=None):
    baslik("🐺 WOLF AI V7 - SOHBET")
    print("Yaz ve sor.  ara <konu>  ·  resim <tanım>  ·  çevir <metin>  ·  çık")
    gecmis = hafiza_yukle()
    while True:
        if ilk_mesaj:
            mesaj, ilk_mesaj = ilk_mesaj, None
            print(f"Sen: {mesaj}")
        else:
            mesaj = input("Sen: ").strip()
        if not mesaj:
            continue
        kucuk = tr_lower(mesaj)
        ilk = kucuk.split(maxsplit=1)[0]

        if ilk in ("resim", "ciz", "çiz"):
            prompt = mesaj.split(maxsplit=1)[1].strip() if len(mesaj.split(maxsplit=1)) > 1 else ""
            if not prompt:
                print("🐺 Wolf: Kullanım: resim <tanım>")
                continue
            sonuc = resim_yap(prompt)
            print(f"\n🐺 Wolf: {sonuc}")
            gecmis += [{"role": "user", "content": mesaj}, {"role": "assistant", "content": temiz_metin(sonuc)}]
            hafiza_kaydet(gecmis)
            continue

        if ilk == "ara":
            sorgu = mesaj.split(maxsplit=1)[1].strip() if len(mesaj.split(maxsplit=1)) > 1 else ""
            if not sorgu:
                print("🐺 Wolf: Kullanım: ara <soru>")
                continue
            web_arastir(sorgu)
            gecmis += [{"role": "user", "content": mesaj}]
            hafiza_kaydet(gecmis)
            continue

        if ilk in ("çevir", "cevir"):
            metin = mesaj.split(maxsplit=1)[1].strip() if len(mesaj.split(maxsplit=1)) > 1 else ""
            if not metin:
                print("🐺 Wolf: Kullanım: çevir <metin>  veya  çevir ingilizce: <metin>")
                continue
            print(f"{CYAN}⏳ Çevriliyor...{RESET}")
            sonuc, hata = ceviri(metin)
            print("\n🐺 Wolf:", sonuc if sonuc else f"{KIRMIZI}{hata}{RESET}")
            if sonuc:
                gecmis += [{"role": "user", "content": mesaj}, {"role": "assistant", "content": sonuc}]
                hafiza_kaydet(gecmis)
            continue

        if kucuk in ("hafıza", "hafiza", "geçmiş", "gecmis", "hafıza listesi"):
            hafiza_listesi()
            gecmis = hafiza_yukle()
            continue

        cevap = yerel_cevap(mesaj, kullanici)
        if cevap == "ÇIKIŞ":
            print("🐺 Görüşürüz!")
            break
        if cevap is None:
            print(f"{CYAN}⏳ Wolf düşünüyor...{RESET}")
            cevap, hata = ai_cevap(ai_mesajlari(gecmis, mesaj))
            if cevap is None:
                print(f"{KIRMIZI}⚠ {hata}{RESET}")
                cevap = ("Şu an yapay zekaya ulaşamadım. İnternet/VPN/DNS'i kontrol et. "
                         "Bu arada 'ara <konu>' ile web'de arama yapabilirsin.")
        print("\n🐺 Wolf:", cevap)
        gecmis += [{"role": "user", "content": mesaj}, {"role": "assistant", "content": cevap}]
        hafiza_kaydet(gecmis)


# ------------------------------------------------------ ÖDEV YARDIMCISI
ODEV_DERSLER = ["Matematik", "Fen Bilimleri", "Türkçe / Edebiyat", "Tarih", "Coğrafya",
                "İngilizce", "Fizik", "Kimya", "Biyoloji", "Diğer"]
ODEV_SISTEM = ("Sen Wolf AI Ödev Yardımcısı adında, Türkçe konuşan sabırlı ve cana yakın bir öğretmensin. "
               "Amacın öğrencinin konuyu GERÇEKTEN anlamasını sağlamak: sade dille, adım adım ve örnekle anlat. "
               "Soru çözerken yolu ve mantığı göster, sonucu da açıkça yaz. Yazı ödevlerinde hazır metin yerine "
               "plan, ipucu ve örnek cümleler ver ki öğrenci kendi cümleleriyle yazsın. "
               "Emin olmadığın şeyi uydurma, bilmiyorsan söyle.")
ODEV_KLASORU = os.path.join(BASE_DIR, "wolf_odev_notlari")


def _odev_dosya():
    guvenli = re.sub(r"[^\w]", "_", tr_lower(_AKTIF_KULLANICI or "misafir"))
    return os.path.join(ODEV_KLASORU, f"odev_{guvenli}.txt")


def _ders_sec():
    for n, d in enumerate(ODEV_DERSLER, 1):
        print(f"{n:>2} - {d}")
    s = input("Ders (numara, boş = Diğer): ").strip()
    return ODEV_DERSLER[int(s) - 1] if s.isdigit() and 1 <= int(s) <= len(ODEV_DERSLER) else "Diğer"


def _odev_sor(ders, konu, istek, mesajlar=None):
    """Öğretmen modunda AI'ya sorar, cevabı gösterir, istenirse not defterine kaydeder."""
    print(f"{CYAN}⏳ Wolf hazırlıyor...{RESET}")
    mesajlar = mesajlar or [{"role": "user", "content": f"Ders: {ders}\n{istek}"}]
    cevap, hata = ai_cevap(mesajlar, ODEV_SISTEM)
    if cevap is None:
        print(f"{KIRMIZI}⚠ {hata}{RESET}")
        return None
    print(f"\n🐺 Wolf:\n{cevap}\n")
    if input("Not defterine kaydedeyim mi? (e/h): ").strip().lower() in ("e", "evet"):
        try:
            os.makedirs(ODEV_KLASORU, exist_ok=True)
            with open(_odev_dosya(), "a", encoding="utf-8") as f:
                f.write(f"{'=' * 40}\n[{datetime.datetime.now():%d.%m.%Y %H:%M}] {ders} - {_kisalt(konu, 40)}\n{cevap}\n")
            print(f"{YESIL}✓ Not defterine eklendi.{RESET}")
        except OSError as e:
            print(f"{KIRMIZI}✗ Kaydedilemedi: {e}{RESET}")
    return cevap


def odev_notlari():
    try:
        with open(_odev_dosya(), "r", encoding="utf-8") as f:
            girdiler = [e.strip() for e in f.read().split("=" * 40) if e.strip()]
    except OSError:
        girdiler = []
    if not girdiler:
        print("Not defterin boş. Bir cevaptan sonra 'e' diyerek not ekleyebilirsin. 📓")
        return
    while True:
        print()
        for n, g in enumerate(girdiler, 1):
            print(f"{SARI}{n:>2}.{RESET} {_kisalt(g.splitlines()[0], 60)}")
        sec = input("\nGörmek için numara (0 = geri): ").strip()
        if not sec.isdigit() or sec == "0":
            return
        if 1 <= int(sec) <= len(girdiler):
            print("\n" + girdiler[int(sec) - 1] + "\n")


def odev_yardimcisi(kullanici):
    while True:
        baslik("📚 WOLF AI V7 - ÖDEV YARDIMCISI")
        print(f"Merhaba {kullanici}! Ne üzerinde çalışalım?\n")
        print("1 - 📖 Konu anlat")
        print("2 - ✏️  Soru çöz (adım adım)")
        print("3 - 📝 Metin özetle")
        print("4 - ❓ Test hazırla (5 soru)")
        print("5 - 🖊️  Kompozisyon / yazı planı")
        print("6 - 🗓️  Çalışma programı")
        print("7 - 📓 Not defterim")
        print("0 - Geri")
        sec = input("\nSeçiminiz: ").strip()
        if sec == "0":
            return
        if sec == "1":
            ders = _ders_sec(); konu = input("Hangi konu? ").strip()
            if konu:
                _odev_sor(ders, konu, f"'{konu}' konusunu bir öğrenciye anlatır gibi anlat: kısa tanım, ana fikirler, "
                                      "bir örnek ve sonunda 2 mini tekrar sorusu ver.")
        elif sec == "2":
            ders = _ders_sec(); soru = input("Soruyu yaz: ").strip()
            if soru:
                _odev_sor(ders, soru, f"Şu soruyu adım adım çöz, her adımı neden yaptığını açıkla ve sonucu net yaz:\n{soru}")
        elif sec == "3":
            ders = _ders_sec(); metin = input("Özetlenecek metni yapıştır: ").strip()
            if metin:
                _odev_sor(ders, metin, "Aşağıdaki metni önce 3-4 cümlede özetle, sonra madde madde anahtar kavramları yaz:\n" + metin)
        elif sec == "4":
            ders = _ders_sec(); konu = input("Hangi konudan test? ").strip()
            if konu:
                istek = (f"'{konu}' konusundan 4 seçenekli (A-D) 5 test sorusu hazırla. "
                         "Cevapları ve açıklamaları HENÜZ verme, sadece soruları yaz.")
                ilk = {"role": "user", "content": f"Ders: {ders}\n{istek}"}
                cevap = _odev_sor(ders, "Test: " + konu, istek)
                if cevap and input("Cevap anahtarını göster? (e/h): ").strip().lower() in ("e", "evet"):
                    _odev_sor(ders, "Cevap anahtarı: " + konu, "", [
                        ilk, {"role": "assistant", "content": cevap},
                        {"role": "user", "content": "Şimdi her sorunun doğru cevabını ve kısa açıklamasını ver."}])
        elif sec == "5":
            ders = _ders_sec(); konu = input("Konu / başlık: ").strip()
            tur = input("Tür (kompozisyon, paragraf, rapor...): ").strip() or "kompozisyon"
            if konu:
                _odev_sor(ders, konu, f"'{konu}' konulu bir {tur} için: giriş-gelişme-sonuç planı, "
                                      "kullanabileceğim 5 anahtar fikir ve birkaç örnek açılış cümlesi ver. "
                                      "Metni tamamen yazma, kendi cümlelerimle yazmama yardım et.")
        elif sec == "6":
            ders = _ders_sec(); sinav = input("Sınav/ödev ne zaman? (örn. 10 gün sonra): ").strip()
            saat = input("Günde kaç saat çalışabilirsin? ").strip()
            if sinav:
                _odev_sor(ders, "Çalışma programı", f"{sinav} olan {ders} sınavı için, günde {saat or '1-2'} saat "
                                                     "çalışabilen bir öğrenciye gün gün çalışma programı hazırla; tekrar ve deneme günlerini de ekle.")
        elif sec == "7":
            odev_notlari()
        else:
            print("Geçersiz seçim.")
            continue
        bekle()


def ansi_temizle(s):
    return re.sub(r"\033\[[0-9;]*m", "", s)


def ses_motoru_hazirla():
    """pyttsx3 motorunu başlatır, varsa Türkçe ses seçer."""
    import pyttsx3
    motor = pyttsx3.init()
    motor.setProperty("rate", 170)
    turkce = False
    for v in motor.getProperty("voices"):
        bilgi = (str(v.id) + " " + str(v.name) + " " + str(getattr(v, "languages", ""))).lower()
        if "tr-tr" in bilgi or "turk" in bilgi or "türk" in bilgi or "tr_tr" in bilgi:
            motor.setProperty("voice", v.id)
            turkce = True
            break
    return motor, turkce


GEREKLI_PAKETLER = ["SpeechRecognition", "pyttsx3", "sounddevice", "numpy"]


def paketleri_hazirla():
    """Sesli sohbet paketlerini yükler; eksikse onayla, çalışan Python'a kurar."""
    def yukle():
        import speech_recognition as sr
        import pyttsx3  # noqa: F401
        import sounddevice as sd
        import numpy as np
        return sr, sd, np

    try:
        return yukle()
    except (ImportError, OSError) as e:
        print(f"{KIRMIZI}Eksik veya yüklenemeyen paket: {getattr(e, 'name', None) or e}{RESET}")
    print(f"Wolf şu Python ile çalışıyor:\n   {sys.executable}")
    komut = [sys.executable, "-m", "pip", "install", *GEREKLI_PAKETLER]
    if input("Gerekli paketler bu Python'a şimdi kurulsun mu? (e/h): ").strip().lower() not in ("e", "evet"):
        print("Elle kurmak için şunu çalıştır:")
        print(f"{SARI}   \"{sys.executable}\" -m pip install {' '.join(GEREKLI_PAKETLER)}{RESET}")
        return None
    try:
        subprocess.check_call(komut)
    except (subprocess.CalledProcessError, OSError) as err:
        print(f"{KIRMIZI}Kurulum başarısız: {err}{RESET}")
        return None
    try:
        return yukle()
    except (ImportError, OSError) as e:
        print(f"{KIRMIZI}Kurulumdan sonra da yüklenemedi: {e}{RESET}")
        print("Hata mesajının tamamını bana gönderirsen birlikte bakarız.")
        return None


SES_HIZI = 16000


def mikrofon_esik(sd, np):
    """1 sn ortam sesi ölçüp konuşma eşiğini belirler."""
    kayit = sd.rec(int(SES_HIZI * 1), samplerate=SES_HIZI, channels=1, dtype="int16")
    sd.wait()
    ortam = float(np.sqrt(np.mean(kayit.astype(np.float64) ** 2)))
    return max(ortam * 3, 300.0)


def mikrofondan_dinle(sr, sd, np, esik, bekleme=8, azami=15, sessizlik=1.2):
    """Konuşma başlayınca kaydeder, sessizlikte durur. PyAudio gerekmez."""
    blok = int(SES_HIZI * 0.1)
    parcalar, onceki = [], []
    basladi, sessiz, gecen = False, 0.0, 0.0
    with sd.InputStream(samplerate=SES_HIZI, channels=1, dtype="int16", blocksize=blok) as akis:
        while True:
            veri, _ = akis.read(blok)
            rms = float(np.sqrt(np.mean(veri.astype(np.float64) ** 2)))
            gecen += 0.1
            if rms > esik:
                if not basladi:
                    basladi = True
                    parcalar = list(onceki)
                sessiz = 0.0
            elif basladi:
                sessiz += 0.1
            if basladi:
                parcalar.append(veri.copy())
                if sessiz >= sessizlik or len(parcalar) * 0.1 >= azami:
                    break
            else:
                onceki.append(veri.copy())
                onceki = onceki[-3:]
                if gecen >= bekleme:
                    raise sr.WaitTimeoutError()
    return sr.AudioData(np.concatenate(parcalar).tobytes(), SES_HIZI, 2)


def sesli_sohbet(kullanici):
    baslik("🎙️ WOLF AI V7 - SESLİ SOHBET")
    paketler = paketleri_hazirla()
    if paketler is None:
        return
    sr, sd, np = paketler

    try:
        motor, turkce = ses_motoru_hazirla()
    except Exception as e:
        print(f"{KIRMIZI}Konuşma motoru başlatılamadı: {e}{RESET}")
        return
    if not turkce:
        print(f"{SARI}⚠ Türkçe ses bulunamadı, varsayılan ses kullanılacak.\n"
              f"  Windows: Ayarlar > Zaman ve dil > Konuşma > Ses ekle > Türkçe{RESET}")

    def konus(metin):
        temiz = ansi_temizle(metin)
        print(f"\n🐺 Wolf: {temiz}")
        try:
            motor.say(temiz)
            motor.runAndWait()
        except Exception:
            pass

    tanici = sr.Recognizer()

    print("Konuşarak sohbet et. Komutlar:")
    print("• 'ara <konu>'      → web araması")
    print("• 'resim <tanım>'   → görsel üret")
    print("• 'çık' veya 'görüşürüz' → sesli sohbeti bitirir\n")
    print("🎧 Ortam gürültüsü ölçülüyor (1 sn sessiz kal)...")
    try:
        esik = mikrofon_esik(sd, np)
    except Exception as e:
        print(f"{KIRMIZI}Mikrofon açılamadı: {e}{RESET}")
        print("Windows: Ayarlar > Gizlilik > Mikrofon izinlerini ve varsayılan mikrofonu kontrol et.")
        return
    konus(f"Merhaba {kullanici}, seni dinliyorum.")

    gecmis = hafiza_yukle()
    anlasilmayan = 0
    while True:
        print(f"\n{CYAN}🎤 Dinliyorum... (konuş){RESET}")
        try:
            ses = mikrofondan_dinle(sr, sd, np, esik)
            mesaj = tanici.recognize_google(ses, language="tr-TR").strip()
        except sr.WaitTimeoutError:
            continue
        except sr.UnknownValueError:
            anlasilmayan += 1
            if anlasilmayan >= 3:
                konus("Seni anlayamıyorum. Mikrofonu kontrol edebilir misin?")
                anlasilmayan = 0
            continue
        except sr.RequestError as e:
            print(f"{KIRMIZI}Ses tanıma servisine ulaşılamadı (internet gerekli): {e}{RESET}")
            return
        except KeyboardInterrupt:
            break
        anlasilmayan = 0
        if not mesaj:
            continue
        print(f"Sen: {mesaj}")
        kucuk = tr_lower(mesaj).strip(" .!?")
        parcalar = kucuk.split(maxsplit=1)
        ilk = parcalar[0] if parcalar else ""
        kalan = mesaj.split(maxsplit=1)[1].strip() if len(mesaj.split(maxsplit=1)) > 1 else ""

        if kucuk in ("çık", "cik", "kapat", "görüşürüz", "sohbeti bitir", "hoşça kal"):
            konus("Görüşürüz!")
            break

        if ilk in ("resim", "çiz", "ciz") and kalan:
            cevap = resim_yap(kalan)
            konus("Görsel hazır." if "✓" in cevap else "Görsel üretilemedi.")
            print(ansi_temizle(cevap))
            cevap = ansi_temizle(cevap)
        elif ilk in ("çevir", "cevir") and kalan:
            cevap, hata = ceviri(kalan)
            if cevap is None:
                cevap = "Çeviri yapılamadı."
            konus(cevap)
        elif ilk == "ara" and kalan:
            sonuclar, hata = web_ara(kalan, 3)
            if hata:
                cevap = "Web bağlantısı kurulamadı."
                konus(cevap)
            elif not sonuclar:
                cevap = "Sonuç bulamadım."
                konus(cevap)
            else:
                for i, x in enumerate(sonuclar, 1):
                    print(f"\n{i}. {MAVI}{x['title']}{RESET}\n   🔗 {x['url']}")
                cevap = ("İlk sonuçlar: " + ". ".join(x["title"] for x in sonuclar) + ". "
                         + wolf_yorumu(kalan, sonuclar))
                konus(cevap)
        else:
            cevap = yerel_cevap(mesaj, kullanici)
            if cevap in (None, "ÇIKIŞ"):
                cevap, hata = ai_cevap(ai_mesajlari(gecmis, mesaj))
                if cevap is None:
                    print(f"{KIRMIZI}⚠ {hata}{RESET}")
                    cevap = "Şu an yapay zekaya ulaşamadım."
            konus(cevap)

        gecmis += [{"role": "user", "content": mesaj}, {"role": "assistant", "content": cevap}]
        hafiza_kaydet(gecmis)


def hesap_makinesi():
    baslik("HESAP MAKİNESİ")
    try:
        a = float(input("Birinci sayı: "))
        op = input("İşlem (+ - * / % **): ").strip()
        b = float(input("İkinci sayı: "))
        if op == "+": r = a + b
        elif op == "-": r = a - b
        elif op == "*": r = a * b
        elif op == "/": r = a / b
        elif op == "%": r = a % b
        elif op == "**": r = a ** b
        else:
            print("Geçersiz işlem.")
            return
        print(f"{YESIL}Sonuç: {r}{RESET}")
    except ValueError:
        print(f"{KIRMIZI}Geçerli bir sayı gir.{RESET}")
    except ZeroDivisionError:
        print(f"{KIRMIZI}Sıfıra bölme hatası.{RESET}")
    except OverflowError:
        print(f"{KIRMIZI}Sonuç çok büyük, hesaplanamadı.{RESET}")


def gelismis_hesap():
    baslik("GELİŞMİŞ HESAP")
    try:
        s = float(input("Sayı: "))
    except ValueError:
        print(f"{KIRMIZI}Geçerli sayı gir.{RESET}")
        return
    print("1-Kare  2-Karekök  3-Mutlak  4-Yuvarla")
    sec = input("Seçim: ").strip()
    try:
        if sec == "1": r = s ** 2
        elif sec == "2":
            if s < 0:
                print(f"{KIRMIZI}Negatif sayının karekökü alınamaz.{RESET}")
                return
            r = math.sqrt(s)
        elif sec == "3": r = abs(s)
        elif sec == "4": r = round(s)
        else:
            print("Geçersiz seçim.")
            return
        print(f"{YESIL}Sonuç: {r}{RESET}")
    except (OverflowError, ValueError):
        print(f"{KIRMIZI}Bu sayı için işlem yapılamadı.{RESET}")


def tahmin_oyunu():
    baslik("SAYI TAHMİN OYUNU")
    gizli = random.randint(1, 100)
    deneme = 0
    while True:
        try:
            t = int(input("Tahminin: "))
        except ValueError:
            print("Tam sayı gir.")
            continue
        deneme += 1
        if t < gizli: print("Daha büyük!")
        elif t > gizli: print("Daha küçük!")
        else:
            print(f"🎉 Bildin! {deneme} denemede.")
            return


# ------------------------------------------------------- V6.0 YENİLİKLER
SURUM = "7.0"
YENILIKLER = [
    "━━ V7.0 ━━",
    "✨ Sade menü: 20+ madde yerine 6 ana başlık (Sohbet, Ödev ve yazı, Günlük işler, Araçlar, Eğlence, Ben)",
    "⌨️ Doğrudan yaz: 'not süt al', 'görev ödev yap', 'hava İstanbul', 'bul kelime' ya da herhangi bir soru",
    "📋 Menü başında günlük özet: açık görev, bekleyen alışkanlık, yeni mesaj",
    "✍️ Yazı asistanı: özetle, yazım düzelt, resmî dile çevir, e-posta yaz, fikir üret",
    "🌤️ Hava durumu (şehir adıyla)",
    "💰 Harcama takibi: aylık toplam ve kategori dağılımı",
    "📔 Günlük defteri: gün puanı ve ortalama",
    "🔍 Her yerde ara: not, görev, günlük, harcama ve alışkanlıkta tek aramada",
    "💾 Verilerimi yedekle (zip)  ·  🗣️ Wolf'un cevap tarzı: kısa / ayrıntılı / samimi",
    "🔑 V6 tek harfli kısayolları (T, O, A, G, M ...) gizli olarak hâlâ çalışır",
    "━━ V6.0 ━━",
    "📝 Notlarım: kişisel not defteri (ekle, ara, sil)  [O]",
    "🔥 Alışkanlık takibi: günlük işaretle, seri (streak) ve son 7 gün  [A]",
    "📅 Tarih hesaplayıcı: gün farkı, yaş, doğum günü sayacı, N gün sonrası  [D]",
    "🔑 Güvenli şifre üretici: uzunluk ve güç ölçümüyle (kaydedilmez)  [K]",
    "🎮 Oyun merkezi: adam asmaca, taş-kağıt-makas, zar/yazı-tura + skorlar  [G]",
    "📬 Mesaj kutusu: geliştirici/yardımcılardan gelen mesajlar  [M]",
    "💡 Menüde günün sözü",
    "🧰 YG paneli: c <n> kullanıcı kartı, m <n> mesaj gönder, z sistem durumu, p işlemlerim",
    "🛠️ Geliştirici paneli: m * ile herkese mesaj",
    "━━ V5.1 ━━",
    "✅ Görevlerim: yapılacaklar listesi (ekle, tamamla, sil)",
    "⏱️ Odak zamanlayıcı: Pomodoro ile çalışma süresi takibi",
    "📐 Birim çevirici: uzunluk, ağırlık, hacim, sıcaklık (çevrimdışı)",
    "🎨 Renk temaları: Ayarlar'dan renkli veya renksiz görünüm",
    "🔑 Profil: şifre değiştirme ve kişisel istatistikler",
    "🆕 Yenilikler ekranı (N)",
    "🔐 Geliştirici kodunu unutursan: 'unuttum' + özel şifre ile kurtarma",
    "💬 Destek: geliştiriciye talep gönder, yanıtı menüden gör (S)",
    "🛠️ Panel: kullanıcı arama, notlar, giriş kayıtları, destek yanıtlama, CSV, kullanıcı ekleme, yedekten geri yükleme",
]
VARSAYILAN_RENKLER = {"YESIL": "\033[92m", "KIRMIZI": "\033[91m", "SARI": "\033[93m",
                      "MAVI": "\033[94m", "MOR": "\033[95m", "CYAN": "\033[96m", "RESET": "\033[0m"}
TEMALAR = {
    "1": ("Varsayılan (camgöbeği)", {}),
    "2": ("Yeşil", {"CYAN": "\033[92m", "MOR": "\033[93m"}),
    "3": ("Mor", {"CYAN": "\033[95m", "MOR": "\033[94m"}),
    "4": ("Renksiz", {k: "" for k in VARSAYILAN_RENKLER}),
}


def kullanici_dosya(onek, uzanti="json"):
    """Aktif kullanıcıya özel dosya yolu (görevler, ayarlar, odak kaydı...)."""
    guvenli = re.sub(r"[^\w]", "_", tr_lower(_AKTIF_KULLANICI or "misafir"))
    return os.path.join(BASE_DIR, f"wolf_{onek}_{guvenli}.{uzanti}")


def _json_oku(yol, varsayilan):
    try:
        with open(yol, "r", encoding="utf-8") as f:
            v = json.load(f)
        return v if isinstance(v, type(varsayilan)) else varsayilan
    except (OSError, json.JSONDecodeError):
        return varsayilan


def _json_yaz(yol, veri):
    try:
        gecici = yol + ".tmp"
        with open(gecici, "w", encoding="utf-8") as f:
            json.dump(veri, f, ensure_ascii=False, indent=2)
        os.replace(gecici, yol)
        return True
    except OSError as e:
        print(f"{KIRMIZI}✗ Kaydedilemedi: {e}{RESET}")
        return False


def yenilikler():
    baslik(f"🆕 WOLF AI V7 - SÜRÜM {SURUM} YENİLİKLERİ")
    for madde in YENILIKLER:
        print("  " + madde)


# ---- renk teması
def tema_uygula(anahtar):
    g = globals()
    g.update(VARSAYILAN_RENKLER)
    g.update(TEMALAR.get(anahtar, TEMALAR["1"])[1])


def tema_yukle():
    tema_uygula(_json_oku(kullanici_dosya("ayar"), {}).get("tema", "1"))


def tema_sec():
    print("\nRenk temaları:")
    for k, (ad, _) in TEMALAR.items():
        print(f"{k} - {ad}")
    sec = input("Seçiminiz: ").strip()
    if sec in TEMALAR:
        ayar = _json_oku(kullanici_dosya("ayar"), {})
        ayar["tema"] = sec
        if _json_yaz(kullanici_dosya("ayar"), ayar):
            tema_uygula(sec)
            print(f"{YESIL}✓ Tema değişti: {TEMALAR[sec][0]}{RESET}")
    else:
        print("Geçersiz seçim.")


# ---- görevler
def gorevler():
    yol = kullanici_dosya("gorevler")
    while True:
        liste = _json_oku(yol, [])
        baslik("✅ GÖREVLERİM")
        if not liste:
            print("Henüz görev yok. 'e <görev>' ile ekle.")
        for n, g in enumerate(liste, 1):
            isaret = f"{YESIL}[x]{RESET}" if g.get("bitti") else "[ ]"
            print(f"{n:>3}. {isaret} {g.get('metin', '')}")
        print("\ne <görev> - Ekle   t <n> - Tamamla/geri al   s <n> - Sil   c - Tamamlananları temizle   0 - Geri")
        sec = input("\nSeçiminiz: ").strip()
        kucuk = tr_lower(sec)
        if kucuk in ("0", ""):
            return
        if kucuk.startswith("e ") and sec[2:].strip():
            liste.append({"metin": sec[2:].strip()[:120], "bitti": False,
                          "tarih": datetime.datetime.now().isoformat(timespec="minutes")})
            _json_yaz(yol, liste)
        elif kucuk[:2] in ("t ", "s ") and kucuk[2:].strip().isdigit() and 1 <= int(kucuk[2:].strip()) <= len(liste):
            i = int(kucuk[2:].strip()) - 1
            if kucuk[0] == "t":
                liste[i]["bitti"] = not liste[i].get("bitti")
            else:
                del liste[i]
            _json_yaz(yol, liste)
        elif kucuk == "c":
            _json_yaz(yol, [g for g in liste if not g.get("bitti")])
        else:
            print("Geçersiz seçim.")


# ---- odak zamanlayıcı
def odak_zamanlayici():
    baslik("⏱️ ODAK ZAMANLAYICI")
    yol = kullanici_dosya("odak")
    kayit = _json_oku(yol, {})
    print(f"Toplam odak süren: {kayit.get('toplam_dk', 0)} dk ({kayit.get('oturum', 0)} oturum)")
    try:
        dk = float(input("\nOdak süresi dakika (boş = 25): ").strip().replace(",", ".") or 25)
    except ValueError:
        print("Geçersiz süre.")
        return
    if not 0 < dk <= 180:
        print("Süre 0-180 dakika arasında olmalı.")
        return
    toplam = int(dk * 60)
    gecen = 0
    print("Başladı! Durdurmak için Ctrl+C.")
    try:
        for gecen in range(1, toplam + 1):
            time.sleep(1)
            kalan = toplam - gecen
            print(f"\r⏳ {kalan // 60:02d}:{kalan % 60:02d} kaldı   ", end="", flush=True)
        print(f"\n{YESIL}🎉 Süre doldu! Harika iş, 5 dakika mola ver.{RESET}\a")
    except KeyboardInterrupt:
        print(f"\n{SARI}Durduruldu.{RESET}")
    if gecen >= 60:
        kayit["toplam_dk"] = kayit.get("toplam_dk", 0) + gecen // 60
        kayit["oturum"] = kayit.get("oturum", 0) + 1
        _json_yaz(yol, kayit)
        print(f"Kaydedildi: +{gecen // 60} dk")


# ---- birim çevirici
BIRIMLER = {
    "uzunluk": {"mm": 0.001, "cm": 0.01, "m": 1, "km": 1000, "inç": 0.0254, "ayak": 0.3048, "mil": 1609.344},
    "ağırlık": {"mg": 1e-6, "g": 0.001, "kg": 1, "ton": 1000, "lb": 0.45359237, "oz": 0.0283495231},
    "hacim": {"ml": 0.001, "l": 1, "m3": 1000, "galon": 3.785411784},
    "sıcaklık": {"c": None, "f": None, "k": None},
}


def birim_hesapla(deger, kaynak, hedef):
    """(sonuç, hata) döner. kaynak/hedef birim adları küçük harfle verilir."""
    kaynak, hedef = tr_lower(kaynak), tr_lower(hedef)
    for tur, birimler in BIRIMLER.items():
        if kaynak in birimler and hedef in birimler:
            if tur == "sıcaklık":
                c = {"c": deger, "f": (deger - 32) * 5 / 9, "k": deger - 273.15}[kaynak]
                if c < -273.15:
                    return None, "Mutlak sıfırın altında sıcaklık olamaz."
                return {"c": c, "f": c * 9 / 5 + 32, "k": c + 273.15}[hedef], None
            return deger * birimler[kaynak] / birimler[hedef], None
    return None, "Bu iki birim aynı türden değil veya tanınmıyor."


def birim_cevirici():
    baslik("📐 BİRİM ÇEVİRİCİ")
    for tur, b in BIRIMLER.items():
        print(f"• {tur}: {', '.join(b)}")
    print("\nÖrnek:  10 km mil     |     100 c f     |     5 kg lb     (çıkmak için boş bırak)")
    while True:
        giris = input("\n> ").strip().replace(",", ".").split()
        if not giris:
            return
        try:
            sonuc, hata = birim_hesapla(float(giris[0]), giris[1], giris[2]) if len(giris) == 3 else (None, "Biçim: <sayı> <birim> <hedef birim>")
        except ValueError:
            sonuc, hata = None, "İlk değer bir sayı olmalı."
        print(f"{YESIL}= {sonuc:,.6g} {giris[2]}{RESET}" if hata is None else f"{KIRMIZI}✗ {hata}{RESET}")


# ---- profil (şifre değiştirme + istatistik) ve ayarlar
def sifre_degistir(kullanici):
    eski = getpass("Mevcut şifre: ")
    if not kullanici_dogrula(kullanici, eski):
        print(f"{KIRMIZI}✗ Mevcut şifre yanlış.{RESET}")
        return
    yeni = getpass("Yeni şifre (en az 6 karakter): ")
    if not 6 <= len(yeni) <= 128:
        print(f"{KIRMIZI}✗ Şifre 6-128 karakter olmalı.{RESET}")
        return
    if getpass("Yeni şifreyi tekrar yaz: ") != yeni:
        print(f"{KIRMIZI}✗ Şifreler eşleşmedi.{RESET}")
        return
    veri = kullanicilari_yukle()
    kayit = veri.get(tr_lower(kullanici))
    if not kayit:
        print(f"{KIRMIZI}✗ Hesap bulunamadı.{RESET}")
        return
    kayit["tuz"], kayit["hash"] = sifre_hashle(yeni)
    try:
        kullanicilari_kaydet(veri)
        print(f"{YESIL}✓ Şifren değiştirildi.{RESET}")
    except OSError as e:
        print(f"{KIRMIZI}✗ Kaydedilemedi: {e}{RESET}")


def profil(kullanici):
    baslik("PROFİL")
    kayit = kullanicilari_yukle().get(tr_lower(kullanici), {})
    odak = _json_oku(kullanici_dosya("odak"), {})
    gorev = _json_oku(kullanici_dosya("gorevler"), [])
    print("👤 Kullanıcı:", kullanici)
    print("🟢 Durum: Aktif")
    print(f"🤖 Sistem: Wolf AI V7 (sürüm {SURUM})")
    print("📅 Kayıt tarihi:", str(kayit.get("olusturma", "-")).replace("T", " "))
    print("💬 Sorduğun soru:", kullanici_mesaj_sayisi(kullanici))
    print(f"⏱️ Odak süresi: {odak.get('toplam_dk', 0)} dk")
    print(f"✅ Görevler: {sum(1 for g in gorev if g.get('bitti'))}/{len(gorev)} tamamlandı")
    print(f"📝 Not sayısı: {len(_json_oku(kullanici_dosya('notlar'), []))}   "
          f"🔥 Alışkanlık: {len(_json_oku(kullanici_dosya('aliskanlik'), []))}")
    skor = _json_oku(kullanici_dosya("skor"), {})
    if skor:
        print("🎮 Oyun galibiyetleri: " + ", ".join(f"{o} {s}" for o, s in sorted(skor.items())))
    print("🌐 Web: Aktif | 🎨 Görsel: Aktif (Pollinations) | 🧠 Hafıza: Aktif")
    if input("\nŞifreni değiştirmek ister misin? (e/h): ").strip().lower() in ("e", "evet"):
        sifre_degistir(kullanici)


# ---------------------------------------------------------------- V6.0 KULLANICI ÖZELLİKLERİ
MESAJ_DOSYASI = os.path.join(BASE_DIR, "wolf_mesajlar.json")

SOZLER = [
    "Küçük adımlar, büyük yolların başlangıcıdır.",
    "Bugün yapabileceğini yarına bırakma, ama kendine de nazik ol.",
    "Hata yapmak öğrenmenin bir parçasıdır.",
    "Disiplin, motivasyonun bittiği yerde başlar.",
    "Bir şeyi öğrenmenin en iyi yolu onu birine anlatmaktır.",
    "Odaklan, nefes al, devam et. 🐺",
    "Kurt sürüyle güçlüdür; yardım istemek zayıflık değildir.",
]


def gunun_sozu():
    return SOZLER[datetime.date.today().toordinal() % len(SOZLER)]


def simdi_metin():
    return datetime.datetime.now().strftime("%d.%m.%Y %H:%M")


# ---- mesaj kutusu
def mesaj_gonder(kime, kimden, metin):
    """kime: kullanıcı adı veya '*' (herkes). Başarılıysa True döner."""
    metin = (metin or "").strip()
    if not metin:
        return False
    mesajlar = _json_oku(MESAJ_DOSYASI, [])
    yeni_id = max([m.get("id", 0) for m in mesajlar] + [0]) + 1
    mesajlar.append({"id": yeni_id, "kime": "*" if kime == "*" else tr_lower(kime), "kimden": kimden,
                     "metin": metin[:500], "tarih": simdi_metin(), "okuyanlar": []})
    return _json_yaz(MESAJ_DOSYASI, mesajlar[-500:])


def okunmamis_sayisi(kullanici):
    k = tr_lower(kullanici)
    return sum(1 for m in _json_oku(MESAJ_DOSYASI, [])
               if m.get("kime") in (k, "*") and k not in m.get("okuyanlar", []))


def mesaj_kutusu(kullanici):
    k = tr_lower(kullanici)
    mesajlar = _json_oku(MESAJ_DOSYASI, [])
    benim = [m for m in mesajlar if m.get("kime") in (k, "*")]
    baslik("📬 MESAJ KUTUSU")
    if not benim:
        print("Henüz mesajın yok.")
        return
    degisti = False
    for m in reversed(benim[-15:]):
        yeni = k not in m.get("okuyanlar", [])
        renk = SARI if yeni else ""
        print(f"{renk}{'● ' if yeni else '  '}{m.get('tarih', '')} - {m.get('kimden', '?')}"
              f"{' (herkese)' if m.get('kime') == '*' else ''}{RESET}\n    {m.get('metin', '')}")
        if yeni:
            m.setdefault("okuyanlar", []).append(k)
            degisti = True
    if degisti:
        _json_yaz(MESAJ_DOSYASI, mesajlar)


# ---- notlar
def notlar_defteri():
    yol = kullanici_dosya("notlar")
    filtre = ""
    while True:
        liste = _json_oku(yol, [])
        baslik("📝 NOTLARIM")
        gosterilen = 0
        for n, x in enumerate(liste, 1):
            if filtre and filtre not in tr_lower(x.get("metin", "")):
                continue
            gosterilen += 1
            print(f"{n:>3}. {x.get('tarih', '')}  {x.get('metin', '')}")
        if not liste:
            print("Henüz not yok. 'e <not>' ile ekle.")
        elif not gosterilen:
            print("Aramayla eşleşen not yok.")
        if filtre:
            print(f"{SARI}Filtre: '{filtre}' (temizlemek için sadece 'a' yaz){RESET}")
        print("\ne <not> - Ekle   a <kelime> - Ara   s <n> - Sil   0 - Geri")
        sec = input("\nSeçiminiz: ").strip()
        kucuk = tr_lower(sec)
        if kucuk in ("0", ""):
            return
        if kucuk.startswith("e ") and sec[2:].strip():
            if len(liste) >= 300:
                print(f"{KIRMIZI}✗ En fazla 300 not tutulabilir.{RESET}")
                continue
            liste.append({"metin": sec[2:].strip()[:500], "tarih": simdi_metin()})
            _json_yaz(yol, liste)
        elif kucuk == "a" or kucuk.startswith("a "):
            filtre = tr_lower(sec[2:].strip()) if kucuk != "a" else ""
        elif kucuk.startswith("s ") and kucuk[2:].strip().isdigit() and 1 <= int(kucuk[2:].strip()) <= len(liste):
            del liste[int(kucuk[2:].strip()) - 1]
            _json_yaz(yol, liste)
        else:
            print("Geçersiz seçim.")


# ---- alışkanlık takibi
def _seri(gunler):
    """Bugünden (yoksa dünden) geriye doğru kesintisiz gün sayısı."""
    kume = set(gunler)
    d = datetime.date.today()
    if d.isoformat() not in kume:
        d -= datetime.timedelta(days=1)
    seri = 0
    while d.isoformat() in kume:
        seri += 1
        d -= datetime.timedelta(days=1)
    return seri


def aliskanlik_takibi():
    yol = kullanici_dosya("aliskanlik")
    bugun = datetime.date.today()
    while True:
        liste = _json_oku(yol, [])
        baslik("🔥 ALIŞKANLIKLARIM")
        if not liste:
            print("Henüz alışkanlık yok. 'e <ad>' ile ekle (ör: e Kitap oku).")
        for n, a in enumerate(liste, 1):
            gunler = set(a.get("gunler", []))
            son7 = "".join("■" if (bugun - datetime.timedelta(days=i)).isoformat() in gunler else "□"
                           for i in range(6, -1, -1))
            bugun_mu = f"{YESIL}✓{RESET}" if bugun.isoformat() in gunler else " "
            print(f"{n:>3}. [{bugun_mu}] {a.get('ad', ''):<24} {son7}  seri: {_seri(gunler)} gün  (toplam {len(gunler)})")
        print("\ne <ad> - Ekle   t <n> - Bugünü işaretle/geri al   s <n> - Sil   0 - Geri")
        sec = input("\nSeçiminiz: ").strip()
        kucuk = tr_lower(sec)
        if kucuk in ("0", ""):
            return
        if kucuk.startswith("e ") and sec[2:].strip():
            if len(liste) >= 20:
                print(f"{KIRMIZI}✗ En fazla 20 alışkanlık takip edilebilir.{RESET}")
                continue
            liste.append({"ad": sec[2:].strip()[:40], "gunler": []})
            _json_yaz(yol, liste)
        elif kucuk[:2] in ("t ", "s ") and kucuk[2:].strip().isdigit() and 1 <= int(kucuk[2:].strip()) <= len(liste):
            i = int(kucuk[2:].strip()) - 1
            if kucuk[0] == "t":
                gunler = set(liste[i].get("gunler", []))
                gunler.symmetric_difference_update({bugun.isoformat()})
                liste[i]["gunler"] = sorted(gunler)[-400:]
            else:
                del liste[i]
            _json_yaz(yol, liste)
        else:
            print("Geçersiz seçim.")


# ---- tarih hesaplayıcı
def _tarih_oku(metin):
    metin = tr_lower((metin or "").strip())
    if metin in ("bugün", "bugun", ""):
        return datetime.date.today()
    for bicim in ("%d.%m.%Y", "%d/%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.datetime.strptime(metin, bicim).date()
        except ValueError:
            pass
    return None


def _sonraki_dogum_gunu(dg, bugun):
    for yil in (bugun.year, bugun.year + 1):
        try:
            aday = dg.replace(year=yil)
        except ValueError:                       # 29 Şubat -> 28 Şubat
            aday = dg.replace(year=yil, day=28)
        if aday >= bugun:
            return aday
    return None


def yas_hesapla(dg, bugun):
    """(yıl, ay, gün) döner."""
    yil = bugun.year - dg.year
    ay = bugun.month - dg.month
    gun = bugun.day - dg.day
    if gun < 0:
        onceki_ay_sonu = bugun.replace(day=1) - datetime.timedelta(days=1)
        gun += onceki_ay_sonu.day
        ay -= 1
    if ay < 0:
        ay += 12
        yil -= 1
    return yil, ay, gun


def tarih_hesapla():
    baslik("📅 TARİH HESAPLAYICI")
    print("Tarih biçimi: GG.AA.YYYY  (ör: 23.04.2008)   'bugün' de yazabilirsin")
    print("1 - İki tarih arası kaç gün")
    print("2 - Yaş hesapla + doğum günüme kaç gün var")
    print("3 - Bugünden N gün sonrası / öncesi")
    print("0 - Geri")
    sec = input("\nSeçiminiz: ").strip()
    bugun = datetime.date.today()
    if sec == "1":
        a, b = _tarih_oku(input("Birinci tarih: ")), _tarih_oku(input("İkinci tarih: "))
        if not a or not b:
            print(f"{KIRMIZI}✗ Tarih okunamadı.{RESET}")
            return
        fark = abs((b - a).days)
        print(f"{YESIL}= {fark} gün ({fark // 7} hafta {fark % 7} gün){RESET}")
    elif sec == "2":
        dg = _tarih_oku(input("Doğum tarihin: "))
        if not dg or dg > bugun:
            print(f"{KIRMIZI}✗ Geçerli bir geçmiş tarih gir.{RESET}")
            return
        y, a, g = yas_hesapla(dg, bugun)
        print(f"{YESIL}Yaşın: {y} yıl, {a} ay, {g} gün  ({(bugun - dg).days} gün yaşadın){RESET}")
        sonraki = _sonraki_dogum_gunu(dg, bugun)
        kalan = (sonraki - bugun).days if sonraki else None
        print("🎂 Doğum günün bugün, kutlu olsun!" if kalan == 0 else f"🎂 Doğum gününe {kalan} gün var.")
    elif sec == "3":
        try:
            n = int(input("Gün sayısı (öncesi için negatif): ").strip())
            hedef = bugun + datetime.timedelta(days=n)
        except (ValueError, OverflowError):
            print(f"{KIRMIZI}✗ Geçerli bir sayı gir.{RESET}")
            return
        gunler = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
        print(f"{YESIL}= {hedef:%d.%m.%Y} {gunler[hedef.weekday()]}{RESET}")


# ---- şifre üretici
def sifre_uretici():
    baslik("🔑 ŞİFRE ÜRETİCİ")
    try:
        n = int(input("Uzunluk (8-64, boş = 16): ").strip() or 16)
    except ValueError:
        print(f"{KIRMIZI}✗ Geçerli bir sayı gir.{RESET}")
        return
    if not 8 <= n <= 64:
        print(f"{KIRMIZI}✗ Uzunluk 8-64 arasında olmalı.{RESET}")
        return
    sembol = input("Özel karakter (!?#...) olsun mu? (e/h, boş = e): ").strip().lower() not in ("h", "hayır", "hayir")
    gruplar = ["abcdefghjkmnpqrstuvwxyz", "ABCDEFGHJKMNPQRSTUVWXYZ", "23456789"]
    if sembol:
        gruplar.append("!?#$%&*+-=")
    alfabe = "".join(gruplar)
    # her gruptan en az bir karakter garanti edilir
    karakterler = [secrets.choice(g) for g in gruplar] + [secrets.choice(alfabe) for _ in range(n - len(gruplar))]
    for i in range(len(karakterler) - 1, 0, -1):          # güvenli karıştırma (Fisher-Yates)
        j = secrets.randbelow(i + 1)
        karakterler[i], karakterler[j] = karakterler[j], karakterler[i]
    sifre = "".join(karakterler)
    bit = n * math.log2(len(alfabe))
    guc = "çok güçlü" if bit >= 100 else "güçlü" if bit >= 70 else "orta" if bit >= 50 else "zayıf"
    print(f"\n{YESIL}{sifre}{RESET}")
    print(f"Güç: {guc} (~{bit:.0f} bit)   {SARI}Not: Wolf AI şifreyi kaydetmez, güvenli bir yere kendin not al.{RESET}")


# ---- oyun merkezi
def _skor_ekle(oyun):
    yol = kullanici_dosya("skor")
    skor = _json_oku(yol, {})
    skor[oyun] = skor.get(oyun, 0) + 1
    _json_yaz(yol, skor)


def adam_asmaca():
    baslik("🪢 ADAM ASMACA")
    kelime = random.choice(["bilgisayar", "program", "yazılım", "klavye", "internet", "algoritma", "değişken",
                            "fonksiyon", "kullanıcı", "şifreleme", "yapay", "kurt", "terminal", "veritabanı"])
    bulunan, yanlis, hak = set(), [], 6
    while hak > 0:
        maske = " ".join(h if h in bulunan else "_" for h in kelime)
        print(f"\n{maske}\nKalan hak: {hak}   Yanlışlar: {' '.join(yanlis) or '-'}")
        if all(h in bulunan for h in kelime):
            print(f"{YESIL}🎉 Kazandın!{RESET}")
            _skor_ekle("adam asmaca")
            return
        harf = tr_lower(input("Harf (0 = çık): ").strip())
        if harf == "0":
            return
        if len(harf) != 1 or not harf.isalpha():
            print("Tek bir harf gir.")
        elif harf in bulunan or harf in yanlis:
            print("Bu harfi zaten denedin.")
        elif harf in kelime:
            bulunan.add(harf)
        else:
            yanlis.append(harf)
            hak -= 1
    print(f"{KIRMIZI}💀 Kaybettin! Kelime: {kelime}{RESET}")


def tas_kagit_makas():
    baslik("✊ TAŞ - KAĞIT - MAKAS")
    secenek = {"t": "taş", "k": "kağıt", "m": "makas"}
    yener = {("t", "m"), ("k", "t"), ("m", "k")}
    puan = [0, 0]
    print("t = taş, k = kağıt, m = makas, 0 = bitir")
    while True:
        s = tr_lower(input("\nSeçimin: ").strip())
        if s == "0":
            break
        if s not in secenek:
            print("t, k veya m yaz.")
            continue
        wolf = random.choice(list(secenek))
        print(f"Wolf: {secenek[wolf]}")
        if s == wolf:
            print("Berabere.")
        elif (s, wolf) in yener:
            puan[0] += 1
            print(f"{YESIL}Bu turu kazandın!{RESET}")
        else:
            puan[1] += 1
            print(f"{KIRMIZI}Bu turu Wolf aldı.{RESET}")
        print(f"Skor -> Sen {puan[0]} : {puan[1]} Wolf")
    if puan[0] > puan[1]:
        print(f"{YESIL}🏆 Genel galibiyet senin!{RESET}")
        _skor_ekle("taş-kağıt-makas")


def zar_yazi_tura():
    baslik("🎲 ZAR / YAZI-TURA")
    print("1 - Yazı-tura   2 - Zar (kaç yüzlü, boş = 6)   0 - Geri")
    sec = input("\nSeçiminiz: ").strip()
    if sec == "1":
        print(f"{YESIL}{random.choice(['Yazı', 'Tura'])}{RESET}")
    elif sec == "2":
        try:
            yuz = int(input("Yüz sayısı (2-1000, boş = 6): ").strip() or 6)
            adet = int(input("Kaç zar (1-10, boş = 1): ").strip() or 1)
        except ValueError:
            print(f"{KIRMIZI}✗ Geçerli bir sayı gir.{RESET}")
            return
        if not (2 <= yuz <= 1000 and 1 <= adet <= 10):
            print(f"{KIRMIZI}✗ Değerler sınır dışında.{RESET}")
            return
        atislar = [random.randint(1, yuz) for _ in range(adet)]
        print(f"{YESIL}{' + '.join(map(str, atislar))} = {sum(atislar)}{RESET}")


def oyun_merkezi():
    while True:
        baslik("🎮 OYUN MERKEZİ")
        skor = _json_oku(kullanici_dosya("skor"), {})
        if skor:
            print("🏆 Galibiyetlerin: " + ", ".join(f"{o} {s}" for o, s in sorted(skor.items())) + "\n")
        print("1 - Sayı tahmin oyunu")
        print("2 - Adam asmaca")
        print("3 - Taş-kağıt-makas")
        print("4 - Zar / Yazı-tura")
        print("0 - Geri")
        sec = input("\nSeçiminiz: ").strip()
        if sec == "1": tahmin_oyunu(); bekle()
        elif sec == "2": adam_asmaca(); bekle()
        elif sec == "3": tas_kagit_makas(); bekle()
        elif sec == "4": zar_yazi_tura(); bekle()
        elif sec in ("0", ""): return
        else: print("Geçersiz seçim.")


# ---------------------------------------------------------------- V6.0 PANEL (GELİŞTİRİCİ / YG) ÖZELLİKLERİ
def panelden_mesaj(rol, kisi, hedef_ad):
    """Panelden bir kullanıcıya (veya geliştirici ise herkese '*') mesaj gönderir."""
    etiket = f"{'Geliştirici' if rol == 'gelistirici' else 'Yardımcı'} {kisi}"
    hedef_yazi = "tüm kullanıcılar" if hedef_ad == "*" else hedef_ad
    metin = input(f"{hedef_yazi} için mesaj (boş = vazgeç): ").strip()
    if not metin:
        return
    if mesaj_gonder(hedef_ad, etiket, metin):
        panel_log(rol, kisi, f"mesaj gönderildi: {'HERKES' if hedef_ad == '*' else hedef_ad}")
        print(f"{YESIL}✓ Mesaj gönderildi.{RESET}")


def kullanici_karti(anahtar, k):
    """Kullanıcı özeti. Gizlilik: yalnızca sayılar gösterilir, sohbet/not/görev içeriği gösterilmez."""
    ad = k.get("ad", anahtar)
    baslik(f"👤 KULLANICI KARTI - {ad}")
    son_giris, basarisiz = "-", 0
    try:
        with open(GIRIS_LOG, "r", encoding="utf-8") as f:
            for s in f.read().strip().splitlines():
                parca = [p.strip() for p in s.split(" | ")]
                if len(parca) == 3 and tr_lower(parca[1]) == tr_lower(ad):
                    if parca[2] == "başarılı":
                        son_giris = parca[0]
                    elif parca[2] == "başarısız":
                        basarisiz += 1
    except OSError:
        pass
    talepler = [t for t in _json_oku(DESTEK_DOSYASI, []) if tr_lower(t.get("kullanici", "")) == tr_lower(ad)]
    print(f"Durum              : {'🔒 kilitli' if k.get('kilitli') else '✓ aktif'}")
    print(f"Kayıt tarihi       : {str(k.get('olusturma', '-')).replace('T', ' ')}")
    print(f"Son başarılı giriş : {son_giris}")
    print(f"Başarısız giriş    : {basarisiz} (kayıtlı toplam)")
    print(f"Sorduğu soru       : {kullanici_mesaj_sayisi(ad)}")
    print(f"Destek talebi      : {len(talepler)} ({sum(1 for t in talepler if t.get('durum') == 'açık')} açık)")
    print(f"Okunmamış mesaj    : {okunmamis_sayisi(ad)}")
    print(f"Yönetici notu      : {len(_json_oku(NOT_DOSYASI, {}).get(anahtar, []))}")


def sistem_durumu():
    baslik("🩺 SİSTEM DURUMU")
    dosyalar = [("Kullanıcılar", KULLANICI_DOSYASI), ("Yardımcılar", YARDIMCI_DOSYASI),
                ("Destek talepleri", DESTEK_DOSYASI), ("Mesajlar", MESAJ_DOSYASI),
                ("Panel kaydı", PANEL_LOG), ("Giriş kaydı", GIRIS_LOG)]
    for etiket, yol in dosyalar:
        try:
            print(f"{etiket:<18}: {os.path.getsize(yol) / 1024:.1f} KB")
        except OSError:
            print(f"{etiket:<18}: (henüz yok)")
    talepler = _json_oku(DESTEK_DOSYASI, [])
    veri = kullanicilari_yukle()
    bugun_basarili = bugun_basarisiz = 0
    try:
        with open(GIRIS_LOG, "r", encoding="utf-8") as f:
            for s in f.read().strip().splitlines():
                if s.startswith(f"{datetime.date.today():%Y-%m-%d}"):
                    if "başarılı" in s:
                        bugun_basarili += 1
                    elif "başarısız" in s:
                        bugun_basarisiz += 1
    except OSError:
        pass
    try:
        yedekler = len([d for d in os.listdir(YEDEK_KLASORU) if os.path.isdir(os.path.join(YEDEK_KLASORU, d))])
    except OSError:
        yedekler = 0
    print(f"\nKullanıcı sayısı    : {len(veri)} ({sum(1 for k in veri.values() if k.get('kilitli'))} kilitli)")
    print(f"Açık destek talebi  : {sum(1 for t in talepler if t.get('durum') == 'açık')}")
    print(f"Bugün girişler      : {bugun_basarili} başarılı, {bugun_basarisiz} başarısız")
    print(f"Mevcut yedek sayısı : {yedekler}")
    print(f"Python              : {sys.version.split()[0]}   Wolf AI V7 (sürüm {SURUM})")


def islemlerim(rol, kisi):
    """Panel kaydından yalnızca bu kişinin son işlemlerini gösterir."""
    try:
        with open(PANEL_LOG, "r", encoding="utf-8") as f:
            satirlar = f.read().strip().splitlines()
    except OSError:
        satirlar = []
    benim = []
    for s in satirlar:
        parca = [p.strip() for p in s.split(" | ")]
        if len(parca) >= 4 and parca[1] == rol and tr_lower(parca[2]) == tr_lower(kisi):
            benim.append(s)
    print("\nSon işlemlerin:\n" + ("\n".join(benim[-15:]) if benim else "(kayıt yok)"))



# ---------------------------------------------------------------- V7.0 YENİ ÖZELLİKLER
AI_SISTEM_TEMEL = AI_SISTEM
AI_TONLARI = {
    "1": ("Kısa ve net", "Çok kısa ve net cevap ver (en fazla 3-4 cümle)."),
    "2": ("Ayrıntılı", "Konuyu ayrıntılı, adım adım ve örneklerle açıkla."),
    "3": ("Samimi ve eğlenceli", "Samimi, esprili ve cana yakın bir dille cevap ver."),
}


def ton_yukle():
    """Kullanıcının seçtiği cevap tarzını yapay zekanın sistem mesajına ekler."""
    global AI_SISTEM
    t = _json_oku(kullanici_dosya("ayar"), {}).get("ton", "1")
    AI_SISTEM = AI_SISTEM_TEMEL + " " + AI_TONLARI.get(t, AI_TONLARI["1"])[1]


def ton_sec():
    mevcut = _json_oku(kullanici_dosya("ayar"), {}).get("ton", "1")
    print("\nCevap tarzı:")
    for k, (ad, _) in AI_TONLARI.items():
        print(f"{k} - {ad}" + ("  ← seçili" if k == mevcut else ""))
    sec = input("Seçiminiz (boş = vazgeç): ").strip()
    if sec in AI_TONLARI:
        ayar = _json_oku(kullanici_dosya("ayar"), {})
        ayar["ton"] = sec
        if _json_yaz(kullanici_dosya("ayar"), ayar):
            ton_yukle()
            print(f"{YESIL}✓ Cevap tarzı: {AI_TONLARI[sec][0]}{RESET}")
    elif sec:
        print("Geçersiz seçim.")


def _sayi_oku(s):
    try:
        return float(str(s).replace(",", "."))
    except ValueError:
        return None


# ---- günlük özet (ana menüde tek satır)
def gunluk_ozet(kullanici):
    parcalar = []
    acik = sum(1 for g in _json_oku(kullanici_dosya("gorevler"), []) if not g.get("bitti"))
    if acik:
        parcalar.append(f"✅ {acik} açık görev")
    bugun = datetime.date.today().isoformat()
    aliskanlik = _json_oku(kullanici_dosya("aliskanlik"), [])
    bekleyen = sum(1 for a in aliskanlik if bugun not in a.get("gunler", []))
    if bekleyen:
        parcalar.append(f"🔥 {bekleyen} alışkanlık bekliyor")
    yeni = okunmamis_sayisi(kullanici)
    if yeni:
        parcalar.append(f"📬 {yeni} yeni mesaj")
    return ("Bugün: " + "   ".join(parcalar)) if parcalar else ""


# ---- hızlı ekleme (ana menüden: "not süt al", "görev ödev yap")
def hizli_not(metin):
    yol = kullanici_dosya("notlar")
    liste = _json_oku(yol, [])
    if len(liste) >= 300:
        print(f"{KIRMIZI}✗ En fazla 300 not tutulabilir.{RESET}")
        return
    liste.append({"metin": metin[:500], "tarih": simdi_metin()})
    if _json_yaz(yol, liste):
        print(f"{YESIL}✓ Nota eklendi.{RESET}")


def hizli_gorev(metin):
    yol = kullanici_dosya("gorevler")
    liste = _json_oku(yol, [])
    liste.append({"metin": metin[:120], "bitti": False,
                  "tarih": datetime.datetime.now().isoformat(timespec="minutes")})
    if _json_yaz(yol, liste):
        print(f"{YESIL}✓ Göreve eklendi.{RESET}")


# ---- yazı asistanı
YAZI_ISLEMLERI = {
    "1": ("Özetle", "Aşağıdaki metni Türkçe olarak kısa ve net şekilde özetle."),
    "2": ("Yazım ve dil bilgisi düzelt",
          "Aşağıdaki metnin yazım ve dil bilgisi hatalarını düzelt. Anlamı değiştirme. Sadece düzeltilmiş metni yaz."),
    "3": ("Resmî dile çevir", "Aşağıdaki metni anlamını bozmadan resmî ve kibar bir dille yeniden yaz."),
    "4": ("E-posta yaz", "Aşağıdaki bilgilere göre konu satırı olan kısa, kibar ve düzgün bir e-posta yaz."),
    "5": ("Fikir üret", "Aşağıdaki konu için 8 yaratıcı ve uygulanabilir fikir listele."),
    "6": ("Daha sade anlat", "Aşağıdaki metni 12 yaşındaki birinin anlayacağı sadelikte yeniden anlat."),
}


def yazi_asistani():
    while True:
        baslik("✍️ YAZI ASİSTANI")
        for k, (ad, _) in YAZI_ISLEMLERI.items():
            print(f"{k} - {ad}")
        print("0 - Geri")
        sec = input("\nSeçiminiz: ").strip()
        if sec in ("0", ""):
            return
        if sec not in YAZI_ISLEMLERI:
            print("Geçersiz seçim.")
            continue
        ad, gorev = YAZI_ISLEMLERI[sec]
        metin = input(f"{ad} - metin veya konu (tek satır, boş = vazgeç): ").strip()
        if not metin:
            continue
        print(f"{CYAN}⏳ Hazırlanıyor...{RESET}")
        sonuc, hata = ai_cevap([{"role": "user", "content": f"{gorev}\n\n{metin}"}])
        print("\n" + (sonuc if sonuc else f"{KIRMIZI}⚠ {hata}{RESET}"))
        bekle()


# ---- hava durumu
def hava_durumu(sehir=""):
    sehir = sehir.strip() or input("Hangi şehir? (ör: İstanbul): ").strip()
    if not sehir:
        return
    print(f"{CYAN}⏳ Hava durumu alınıyor...{RESET}")
    url = ("https://wttr.in/" + quote(sehir) +
           "?format=%l:+%c+%t+(hissedilen+%f),+nem+%h,+rüzgâr+%w&lang=tr")
    sayfa, hata = sayfa_getir(url, deneme=1)
    if sayfa and sayfa.strip() and "unknown location" not in sayfa.lower():
        print("\n🌤️ " + sayfa.strip())
    else:
        print(f"{KIRMIZI}⚠ Hava durumu alınamadı ({hata or 'şehir bulunamadı'}).{RESET}")


# ---- harcama takibi
def harcama_takibi():
    yol = kullanici_dosya("harcama")
    while True:
        liste = _json_oku(yol, [])
        ay = datetime.date.today().strftime("%Y-%m")
        buay = [(n, h) for n, h in enumerate(liste, 1) if str(h.get("tarih", "")).startswith(ay)]
        baslik("💰 HARCAMA TAKİBİ")
        if not buay:
            print("Bu ay harcama yok. Örnek: e 85 market")
        for n, h in buay[-15:]:
            print(f"{n:>3}. {h.get('tarih', '')}  {h.get('tutar', 0):>9.2f} ₺  {h.get('aciklama', '')}")
        toplam = sum(h.get("tutar", 0) for _, h in buay)
        kategoriler = {}
        for _, h in buay:
            k = h.get("kategori", "diğer")
            kategoriler[k] = kategoriler.get(k, 0) + h.get("tutar", 0)
        print(f"\nBu ay toplam: {YESIL}{toplam:.2f} ₺{RESET}")
        if kategoriler:
            print("Dağılım: " + ", ".join(f"{k} {v:.0f} ₺" for k, v in sorted(kategoriler.items(), key=lambda x: -x[1])[:6]))
        print("\ne <tutar> <açıklama> - Ekle   s <n> - Sil   0 - Geri")
        sec = input("\nSeçiminiz: ").strip()
        kucuk = tr_lower(sec)
        if kucuk in ("0", ""):
            return
        if kucuk.startswith("e "):
            parca = sec[2:].strip().split(maxsplit=1)
            tutar = _sayi_oku(parca[0]) if parca else None
            if tutar is None or tutar <= 0 or tutar > 100_000_000:
                print("Geçersiz tutar. Örnek: e 85,50 market")
                continue
            aciklama = parca[1].strip()[:60] if len(parca) > 1 else "harcama"
            liste.append({"tutar": round(tutar, 2), "aciklama": aciklama,
                          "kategori": tr_lower(aciklama.split()[0]) if aciklama.split() else "diğer",
                          "tarih": datetime.date.today().isoformat()})
            _json_yaz(yol, liste[-2000:])
        elif kucuk.startswith("s ") and kucuk[2:].strip().isdigit() and 1 <= int(kucuk[2:].strip()) <= len(liste):
            del liste[int(kucuk[2:].strip()) - 1]
            _json_yaz(yol, liste)
        else:
            print("Geçersiz seçim.")


# ---- günlük defteri
def gunluk_defteri():
    yol = kullanici_dosya("gunluk")
    while True:
        liste = _json_oku(yol, [])
        baslik("📔 GÜNLÜĞÜM")
        if not liste:
            print("Henüz kayıt yok. 'e <bugün neler oldu>' ile ekle.")
        for n, x in list(enumerate(liste, 1))[-8:]:
            yildiz = ("★" * x["ruh"] + "☆" * (5 - x["ruh"])) if isinstance(x.get("ruh"), int) else ""
            print(f"{n:>3}. {x.get('tarih', '')}  {yildiz}\n     {x.get('metin', '')}")
        puanlar = [x["ruh"] for x in liste[-7:] if isinstance(x.get("ruh"), int)]
        if puanlar:
            print(f"\nSon kayıtlarda gün puanı ortalaman: {sum(puanlar) / len(puanlar):.1f}/5")
        print("\ne <metin> - Bugüne yaz   s <n> - Sil   0 - Geri")
        sec = input("\nSeçiminiz: ").strip()
        kucuk = tr_lower(sec)
        if kucuk in ("0", ""):
            return
        if kucuk.startswith("e ") and sec[2:].strip():
            puan = input("Bugün nasıldı? 1-5 (boş = geç): ").strip()
            kayit = {"metin": sec[2:].strip()[:800], "tarih": simdi_metin()}
            if puan in ("1", "2", "3", "4", "5"):
                kayit["ruh"] = int(puan)
            liste.append(kayit)
            _json_yaz(yol, liste[-500:])
        elif kucuk.startswith("s ") and kucuk[2:].strip().isdigit() and 1 <= int(kucuk[2:].strip()) <= len(liste):
            del liste[int(kucuk[2:].strip()) - 1]
            _json_yaz(yol, liste)
        else:
            print("Geçersiz seçim.")


# ---- her yerde ara
def her_yerde_ara(sorgu=""):
    sorgu = tr_lower(sorgu.strip() or input("Notlarında, görevlerinde, günlüğünde ne arayayım? ").strip())
    if not sorgu:
        return
    kaynaklar = (("📝 Not", "notlar", "metin"), ("✅ Görev", "gorevler", "metin"),
                 ("📔 Günlük", "gunluk", "metin"), ("💰 Harcama", "harcama", "aciklama"),
                 ("🔥 Alışkanlık", "aliskanlik", "ad"))
    bulunan = 0
    baslik(f"🔍 '{sorgu}' sonuçları")
    for etiket, onek, alan in kaynaklar:
        for x in _json_oku(kullanici_dosya(onek), []):
            metin = str(x.get(alan, ""))
            if sorgu in tr_lower(metin):
                print(f"{etiket:<14} {metin[:90]}")
                bulunan += 1
    if not bulunan:
        print("Hiçbir yerde bulunamadı.")


# ---- verilerimi yedekle
def verilerimi_yedekle(kullanici):
    import zipfile
    dosyalar = [kullanici_dosya(o) for o in
                ("gorevler", "notlar", "aliskanlik", "odak", "skor", "ayar", "gunluk", "harcama")]
    dosyalar.append(hafiza_dosya_yolu())
    dosyalar = [d for d in dosyalar if os.path.exists(d)]
    if not dosyalar:
        print("Yedeklenecek veri henüz yok.")
        return
    try:
        os.makedirs(DISA_AKTAR_KLASORU, exist_ok=True)
        guvenli = re.sub(r"[^\w]", "_", tr_lower(kullanici))
        yol = os.path.join(DISA_AKTAR_KLASORU,
                           f"wolf_yedek_{guvenli}_{datetime.datetime.now():%Y%m%d_%H%M}.zip")
        with zipfile.ZipFile(yol, "w", zipfile.ZIP_DEFLATED) as z:
            for d in dosyalar:
                z.write(d, os.path.basename(d))
        print(f"{YESIL}✓ {len(dosyalar)} dosya yedeklendi: {yol}{RESET}")
    except OSError as e:
        print(f"{KIRMIZI}✗ Yedek alınamadı: {e}{RESET}")


# ---- ayarlar (sadeleşti)
def ayarlar(kullanici):
    while True:
        baslik("⚙️ AYARLAR")
        print("1 - 🎨 Renk teması")
        print("2 - 🗣️  Wolf'un cevap tarzı")
        print("3 - 💾 Verilerimi yedekle (zip)")
        print("4 - ℹ️  Sistem bilgisi")
        print("0 - Geri")
        sec = input("\nSeçiminiz: ").strip()
        if sec == "1":
            tema_sec()
        elif sec == "2":
            ton_sec()
        elif sec == "3":
            verilerimi_yedekle(kullanici)
        elif sec == "4":
            print(f"\nWolf AI V7 (sürüm {SURUM})")
            print("Web araması: DuckDuckGo / Bing   Görsel: Pollinations.ai -> wolf_resimler/")
            print("Sohbet hafızası:", hafiza_dosya_yolu())
        elif sec in ("0", ""):
            return
        else:
            print("Geçersiz seçim.")


# ---------------------------------------------------------------- V7.0 SADE MENÜ
def _alt_menu(baslik_metni, secenekler):
    """secenekler: [(etiket veya etiket-fonksiyonu, fonksiyon, işlemden sonra bekle?), ...]"""
    while True:
        baslik(baslik_metni)
        for n, (etiket, _, _) in enumerate(secenekler, 1):
            print(f"{n} - {etiket() if callable(etiket) else etiket}")
        print("0 - Geri")
        sec = input("\n> ").strip()
        if sec in ("0", ""):
            return
        if sec.isdigit() and 1 <= int(sec) <= len(secenekler):
            _, fonksiyon, bekle_mi = secenekler[int(sec) - 1]
            fonksiyon()
            if bekle_mi:
                bekle()
        else:
            print("Geçersiz seçim.")


def hesap_menusu():
    _alt_menu("🧮 HESAP VE DÖNÜŞTÜRME", [
        ("Hesap makinesi", hesap_makinesi, True),
        ("Gelişmiş hesap", gelismis_hesap, True),
        ("Birim çevirici", birim_cevirici, False),
        ("Tarih hesaplayıcı", tarih_hesapla, True),
    ])


def _web_ara_sor():
    q = input("Web'de ne arayayım? ").strip()
    if q:
        web_arastir(q)


def _resim_sor():
    p = input("Nasıl bir resim yapayım? ").strip()
    if p:
        print(resim_yap(p))


def serbest_komut(metin, kullanici):
    """Ana menüde sayı yerine yazılan komutları çalıştırır. İşlendiyse True döner."""
    parcalar = metin.split(maxsplit=1)
    ilk = tr_lower(parcalar[0])
    arg = parcalar[1].strip() if len(parcalar) > 1 else ""

    if ilk == "not":
        hizli_not(arg) if arg else notlar_defteri()
    elif ilk in ("görev", "gorev"):
        hizli_gorev(arg) if arg else gorevler()
    elif ilk == "ara":
        web_arastir(arg) if arg else _web_ara_sor()
        bekle()
    elif ilk in ("resim", "çiz", "ciz"):
        print(resim_yap(arg)) if arg else _resim_sor()
        bekle()
    elif ilk in ("çevir", "cevir"):
        if not arg:
            arg = input("Çevrilecek metin: ").strip()
        if arg:
            print(f"{CYAN}⏳ Çevriliyor...{RESET}")
            sonuc, hata = ceviri(arg)
            print("\n🐺 Wolf:", sonuc if sonuc else f"{KIRMIZI}{hata}{RESET}")
        bekle()
    elif ilk == "hava":
        hava_durumu(arg)
        bekle()
    elif ilk in ("harcama", "harcamalar"):
        harcama_takibi()
    elif ilk in ("günlük", "gunluk"):
        gunluk_defteri()
    elif ilk == "bul":
        her_yerde_ara(arg)
        bekle()
    elif ilk in ("yaz", "yazı", "yazi"):
        yazi_asistani()
    elif ilk in ("yedek", "yedekle"):
        verilerimi_yedekle(kullanici)
        bekle()
    else:
        acilir = (
            (("görevler", "görevlerim", "gorevler"), gorevler),
            (("notlar", "notlarım"), notlar_defteri),
            (("alışkanlık", "alışkanlıklar", "aliskanlik"), aliskanlik_takibi),
            (("odak", "pomodoro"), lambda: (odak_zamanlayici(), bekle())),
            (("hesap", "hesapla", "hesap makinesi"), hesap_menusu),
            (("birim",), birim_cevirici),
            (("tarih",), lambda: (tarih_hesapla(), bekle())),
            (("şifre", "sifre"), lambda: (sifre_uretici(), bekle())),
            (("oyun", "oyunlar"), oyun_merkezi),
            (("ödev", "odev"), lambda: odev_yardimcisi(kullanici)),
            (("sesli",), lambda: (sesli_sohbet(kullanici), bekle())),
            (("mesaj", "mesajlar"), lambda: (mesaj_kutusu(kullanici), bekle())),
            (("destek",), lambda: destek_menu(kullanici)),
            (("hafıza", "hafiza"), lambda: (hafiza_listesi(), bekle())),
            (("profil",), lambda: (profil(kullanici), bekle())),
            (("ayar", "ayarlar"), lambda: ayarlar(kullanici)),
            (("logo",), lambda: (logo_olustur(), bekle())),
            (("yenilik", "yenilikler"), lambda: (yenilikler(), bekle())),
        )
        tum = tr_lower(metin)
        for adlar, fonksiyon in acilir:
            if tum in adlar:
                fonksiyon()
                return True
        return False
    return True


def ana_menu(kullanici):
    tema_yukle()
    ton_yukle()
    duyuru_goster()

    def planlama():
        _alt_menu("🗂️ GÜNLÜK İŞLER", [
            ("✅ Görevler", gorevler, False),
            ("📝 Notlar", notlar_defteri, False),
            ("🔥 Alışkanlıklar", aliskanlik_takibi, False),
            ("📔 Günlük", gunluk_defteri, False),
            ("💰 Harcamalar", harcama_takibi, False),
            ("⏱️ Odak zamanlayıcı", odak_zamanlayici, True),
        ])

    def araclar():
        _alt_menu("🔧 ARAÇLAR", [
            ("🌐 Web'de ara + Wolf yorumu", _web_ara_sor, True),
            ("🎨 Görsel oluştur", _resim_sor, True),
            ("🎙️ Sesli sohbet", lambda: sesli_sohbet(kullanici), True),
            ("🌤️ Hava durumu", hava_durumu, True),
            ("🧮 Hesap ve dönüştürme", hesap_menusu, False),
            ("🔑 Şifre üretici", sifre_uretici, True),
            ("🔍 Her yerde ara (not, görev, günlük...)", her_yerde_ara, True),
        ])

    def odev_yazi():
        _alt_menu("📚 ÖDEV VE YAZI", [
            ("📚 Ödev yardımcısı", lambda: odev_yardimcisi(kullanici), False),
            ("✍️ Yazı asistanı (özetle, düzelt, e-posta...)", yazi_asistani, False),
        ])

    def ben():
        def mesaj_etiketi():
            yeni = okunmamis_sayisi(kullanici)
            return "📬 Mesajlar" + (f"  {SARI}({yeni} yeni){RESET}" if yeni else "")
        _alt_menu("👤 BEN", [
            ("🙋 Profil", lambda: profil(kullanici), True),
            (mesaj_etiketi, lambda: mesaj_kutusu(kullanici), True),
            ("💬 Destek", lambda: destek_menu(kullanici), False),
            ("🧠 Sohbet hafızası", hafiza_listesi, True),
            ("⚙️ Ayarlar", lambda: ayarlar(kullanici), False),
            ("🆕 Yenilikler", yenilikler, True),
            ("🐺 Logo", logo_olustur, True),
        ])

    # V6'dan alışkanlık kalan tek harfli kısayollar gizli olarak çalışmaya devam eder
    eski_kisayollar = {
        "t": gorevler, "p": lambda: (odak_zamanlayici(), bekle()), "b": birim_cevirici,
        "o": notlar_defteri, "a": aliskanlik_takibi, "d": lambda: (tarih_hesapla(), bekle()),
        "k": lambda: (sifre_uretici(), bekle()), "g": oyun_merkezi,
        "m": lambda: (mesaj_kutusu(kullanici), bekle()), "s": lambda: destek_menu(kullanici),
        "e": lambda: odev_yardimcisi(kullanici), "h": lambda: (hafiza_listesi(), bekle()),
        "l": lambda: (logo_olustur(), bekle()), "n": lambda: (yenilikler(), bekle()),
        "dev": gelistirici_paneli, "yg": yardimci_paneli,
    }

    while True:
        baslik("🐺 WOLF AI V7")
        print(f"{MOR}💡 {gunun_sozu()}{RESET}")
        ozet = gunluk_ozet(kullanici)
        if ozet:
            print(f"{CYAN}{ozet}{RESET}")
        print()
        print("1 - 💬 Sohbet        (soru sor, ara, resim, çeviri)")
        print("2 - 📚 Ödev ve yazı")
        print("3 - 🗂️  Günlük işler  (görev, not, alışkanlık, harcama...)")
        print("4 - 🔧 Araçlar")
        print("5 - 🎮 Eğlence")
        yeni = okunmamis_sayisi(kullanici)
        print("6 - 👤 Ben" + (f"          {SARI}({yeni} yeni mesaj){RESET}" if yeni else "            (profil, mesaj, ayar)"))
        print("0 - 🚪 Çıkış")
        print(f"\n{SARI}İpucu: sayı seç veya doğrudan yaz → 'not süt al', 'görev ödev yap', "
              f"'hava İstanbul', 'ara deprem'{RESET}")
        sec = input("\n> ").strip()
        kucuk = tr_lower(sec)
        if not sec:
            continue
        if sec == "1": ai_sohbet(kullanici)
        elif sec == "2": odev_yazi()
        elif sec == "3": planlama()
        elif sec == "4": araclar()
        elif sec == "5": oyun_merkezi()
        elif sec == "6": ben()
        elif sec == "0":
            print("🐺 Görüşürüz!")
            break
        elif kucuk in eski_kisayollar:
            eski_kisayollar[kucuk]()
        elif sec.isdigit():
            print("Geçersiz seçim.")
        elif not serbest_komut(sec, kullanici):
            # Menüde olmayan her şey doğrudan Wolf'a sorulmuş sayılır
            ai_sohbet(kullanici, ilk_mesaj=sec)


if __name__ == "__main__":
    try:
        logo_goster()
        print("Yerel + web destekli asistan".center(64))
        kullanici = giris_yap()
        if kullanici:
            ana_menu(kullanici)
    except (KeyboardInterrupt, EOFError):
        print("\n🐺 Görüşürüz!")