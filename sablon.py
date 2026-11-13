import os
import sys
from datetime import date

import mysql.connector

os.system("")  # mengaktifkan warna ANSI di terminal Windows
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

MIN_ORDER = 12          # minimal order per pesanan
WARNA_DASAR = 4          # 4 warna pertama sudah termasuk di harga dasar
BIAYA_PER_WARNA = 2000   # biaya tambahan per warna mulai warna ke-5 (jumlah warna unlimited)
FINISHING = {1: "Doff", 2: "Glossy", 3: "Kasar"}

# ------------------------------------------------------------
# WARNA (kode ANSI)
# ------------------------------------------------------------
RESET = "\033[0m"
BOLD, DIM = 1, 2
MERAH, HIJAU, KUNING, BIRU, UNGU, CYAN, PUTIH, ABU = 91, 92, 93, 94, 95, 96, 97, 90

# tema tabel: (warna garis, gaya header)
TEMA = {
    "biru": (CYAN, (BOLD, PUTIH, 44)),
    "ungu": (UNGU, (BOLD, PUTIH, 45)),
    "hijau": (HIJAU, (BOLD, 30, 42)),
    "merah": (MERAH, (BOLD, PUTIH, 41)),
    "kuning": (KUNING, (BOLD, 30, 43)),
}

# gaya kolom yang sering dipakai
G_NO = (BOLD, CYAN)
G_TEKS = (PUTIH,)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           
G_NAMA = (BOLD, PUTIH)
G_ANGKA = (CYAN,)
G_UANG = (BOLD, HIJAU)
G_LABEL = (UNGU,)
G_TGL = (ABU,)

def clr(teks, *kode):
    """Bungkus teks dengan warna ANSI."""
    kode = [k for k in kode if k is not None]
    if not kode:
        return teks
    return f"\033[{';'.join(str(k) for k in kode)}m{teks}{RESET}"


def sukses(teks):
    print(clr(f"✔ {teks}", BOLD, HIJAU))


def gagal(teks):
    print(clr(f"✘ {teks}", BOLD, MERAH))


def info(teks):
    print(clr(f"! {teks}", BOLD, KUNING))


def tanya(teks):
    return input(clr(teks, BOLD, CYAN) + " ")


def ya(teks):
    return tanya(teks).strip().lower() == "y"


def koneksi():
    return mysql.connector.connect(
        host="localhost", user="root", password="", database="sablon_db"
    )


def rp(n):
    return "Rp" + f"{int(n):,}".replace(",", ".")


def plus(n):
    """Format tambahan harga: FREE kalau 0, selain itu +Rp..."""
    return "FREE" if int(n) == 0 else "+" + rp(n)


# ------------------------------------------------------------
# KOMPONEN TAMPILAN
# ------------------------------------------------------------
def tabel(judul, kolom, baris, total=None, tema="biru"):
    """Cetak tabel berwarna.
    kolom : list (header, rata, gaya)  -> rata 'l' (kiri) atau 'r' (kanan)
    baris : list tuple data
    total : baris penutup (opsional)
    """
    warna_garis, gaya_head = TEMA[tema]
    data = [[str(c) for c in b] for b in baris]
    tot = [str(c) for c in total] if total else None

    lebar = [len(k[0]) for k in kolom]
    for b in data + ([tot] if tot else []):
        for i, c in enumerate(b):
            lebar[i] = max(lebar[i], len(c))

    kosong = not data
    teks_kosong = "(belum ada data)"
    if kosong:
        dalam = sum(w + 2 for w in lebar) + (len(lebar) - 1)
        if dalam < len(teks_kosong) + 2:
            lebar[-1] += len(teks_kosong) + 2 - dalam
    dalam = sum(w + 2 for w in lebar) + (len(lebar) - 1)

    def g(teks):
        return clr(teks, warna_garis)

    def sel(teks, i):
        rata = kolom[i][1]
        return teks.rjust(lebar[i]) if rata == "r" else teks.ljust(lebar[i])

    def cetak_baris(cells, gaya_fn):
        isi = [clr(" " + sel(c, i) + " ", *gaya_fn(i)) for i, c in enumerate(cells)]
        print(g("│") + g("│").join(isi) + g("│"))

    garis_atas = "╭" + "┬".join("─" * (w + 2) for w in lebar) + "╮"
    garis_tengah = (
        "├" + ("┴" if kosong else "┼").join("─" * (w + 2) for w in lebar) + "┤"
    )
    garis_bawah = "╰" + ("─" * dalam if kosong else "┴".join("─" * (w + 2) for w in lebar)) + "╯"

    print()
    print(clr(judul.center(dalam + 2), BOLD, KUNING))
    print(g(garis_atas))
    cetak_baris([k[0] for k in kolom], lambda i: gaya_head)
    print(g(garis_tengah))
    if kosong:
        print(g("│") + clr(" " + teks_kosong.ljust(dalam - 2) + " ", DIM, ABU) + g("│"))
    else:
        for b in data:
            cetak_baris(b, lambda i: kolom[i][2])
    if tot:
        print(g(garis_tengah.replace("┴", "┼") if kosong else garis_tengah))
        cetak_baris(tot, lambda i: (BOLD, KUNING))
    print(g(garis_bawah))


def kotak(judul, isi, warna_garis=UNGU, gaya_judul=(BOLD, KUNING)):
    """Kotak berbingkai ganda. isi = list baris, tiap baris = list (teks, gaya)."""
    lebar = max(
        [len(judul)] + [sum(len(t) for t, _ in b) for b in isi]
    )
    dalam = lebar + 4

    def g(teks):
        return clr(teks, warna_garis)

    print()
    print(g("╔" + "═" * dalam + "╗"))
    print(g("║") + clr(judul.center(dalam), *gaya_judul) + g("║"))
    print(g("╠" + "═" * dalam + "╣"))
    for b in isi:
        panjang = sum(len(t) for t, _ in b)
        konten = "".join(clr(t, *gaya) for t, gaya in b)
        print(g("║") + "  " + konten + " " * (lebar - panjang) + "  " + g("║"))
    print(g("╚" + "═" * dalam + "╝"))


def tampil_menu():
    kotak(
        "SISTEM REKAP SABLON",
        [
            [("1", (BOLD, CYAN)), ("  Tambah pesanan", (PUTIH,))],
            [("2", (BOLD, CYAN)), ("  Rekap per ukuran", (PUTIH,))],
            [("3", (BOLD, CYAN)), ("  Rekap per bahan", (PUTIH,))],
            [("4", (BOLD, CYAN)), ("  Riwayat pesanan", (PUTIH,))],
            [("5", (BOLD, CYAN)), ("  Hapus pesanan", (PUTIH,))],
            [("6", (BOLD, CYAN)), ("  Detail pesanan", (PUTIH,))],
            [("0", (BOLD, MERAH)), ("  Keluar", (MERAH,))],
        ],
    )


def input_int(teks, valid=None, minimum=1):
    while True:
        try:
            n = int(tanya(teks))
        except ValueError:
            gagal("Masukkan angka saja.")
            continue
        if valid is not None and n not in valid:
            gagal("Pilihan tidak tersedia.")
        elif valid is None and n < minimum:
            gagal(f"Minimal {minimum}.")
        else:
            return n


# ------------------------------------------------------------
# LOGIKA HARGA
# ------------------------------------------------------------
def cari_harga(cur, id_bahan, total_qty):
    """Harga dasar per pcs sesuai tier. None = call admin (atau tier tidak ditemukan)."""
    cur.execute(
        "SELECT harga FROM harga_bahan "
        "WHERE id_bahan=%s AND qty_min<=%s AND (qty_max IS NULL OR qty_max>=%s) "
        "ORDER BY qty_min DESC LIMIT 1",
        (id_bahan, total_qty, total_qty),
    )
    rows = cur.fetchall()
    return rows[0][0] if rows else None


def biaya_tambah_warna(cur, jml_warna):
    """Tambahan per kaos untuk warna di atas WARNA_DASAR: BIAYA_PER_WARNA per warna.
    Jumlah warna tidak dibatasi. 5 warna = 1x, 6 warna = 2x, 7 warna = 3x, dst.
    Return (id_tambahan, biaya) atau None kalau tidak ada tambahan.
    id_tambahan bernilai None kalau baris otomatis=1 belum ada di tabel tambahan."""
    ekstra = jml_warna - WARNA_DASAR
    if ekstra <= 0:
        return None
    cur.execute("SELECT id_tambahan FROM tambahan WHERE otomatis = 1 LIMIT 1")
    rows = cur.fetchall()
    id_t = rows[0][0] if rows else None
    return id_t, ekstra * BIAYA_PER_WARNA


def pilih_tambahan(cur):
    """Kasir memilih tambahan bahan/sablon. Return list (id, nama, harga)."""
    cur.execute(
        "SELECT id_tambahan, kelompok, nama, harga FROM tambahan "
        "WHERE otomatis = 0 ORDER BY id_tambahan"
    )
    daftar = cur.fetchall()
    tabel(
        "TAMBAHAN BAHAN & SABLON (per kaos)",
        [
            ("No", "r", G_NO),
            ("Kelompok", "l", G_LABEL),
            ("Tambahan", "l", G_NAMA),
            ("Harga", "r", G_UANG),
        ],
        [(i, k, n, plus(h)) for i, k, n, h in daftar],
        tema="kuning",
    )
    valid = {d[0]: d for d in daftar}
    while True:
        teks = tanya("Pilih tambahan (nomor dipisah koma, kosongkan jika tidak ada):").strip()
        if not teks:
            return []
        try:
            nomor = sorted({int(x) for x in teks.replace(" ", "").split(",") if x})
        except ValueError:
            gagal("Pakai angka dipisah koma, contoh: 1,8,12")
            continue
        tidak_ada = [n for n in nomor if n not in valid]
        if tidak_ada:
            gagal("Nomor tidak tersedia: " + ", ".join(str(n) for n in tidak_ada))
            continue
        return [(valid[n][0], valid[n][2], valid[n][3]) for n in nomor]


# ------------------------------------------------------------
# FITUR
# ------------------------------------------------------------
def pilih_pelanggan(cur):
    cur.execute("SELECT id_pelanggan, nama FROM pelanggan ORDER BY id_pelanggan")
    daftar = cur.fetchall()
    tabel(
        "DAFTAR PELANGGAN",
        [("No", "r", G_NO), ("Nama", "l", G_NAMA)],
        list(daftar) + [(0, "+ Pelanggan baru")],
        tema="ungu",
    )
    pilihan = input_int("Pilih pelanggan:", {i for i, _ in daftar} | {0}, minimum=0)
    if pilihan != 0:
        return pilihan
    nama = ""
    while not nama:
        nama = tanya("Atas nama:").strip()
    no_hp = tanya("No HP:").strip()
    cur.execute("INSERT INTO pelanggan (nama, no_hp) VALUES (%s, %s)", (nama, no_hp))
    return cur.lastrowid


def tambah_pesanan(db):
    cur = db.cursor()
    try:
        # 1. bahan
        cur.execute("SELECT id_bahan, nama_bahan FROM bahan_kain ORDER BY id_bahan")
        bahan = cur.fetchall()
        tabel(
            "BAHAN KAIN",
            [("No", "r", G_NO), ("Bahan", "l", G_NAMA)],
            bahan,
            tema="biru",
        )
        id_bahan = input_int("Pilih bahan:", {b[0] for b in bahan})
        nama_bahan = next(b[1] for b in bahan if b[0] == id_bahan)

        # 2. jumlah per ukuran
        cur.execute(
            "SELECT id_ukuran, nama_ukuran, tambahan_harga FROM ukuran ORDER BY id_ukuran"
        )
        print(clr("\nJumlah per ukuran (isi 0 kalau tidak ada):", BOLD, PUTIH))
        item = []   # (id_ukuran, nama, jumlah, tambahan_ukuran)
        for id_u, nama_u, tambah_u in cur.fetchall():
            label = nama_u + (f" ({plus(tambah_u)})" if tambah_u else "")
            qty = input_int(f"  {label}:", minimum=0)
            if qty > 0:
                item.append((id_u, nama_u, qty, tambah_u))

        total_qty = sum(q for _, _, q, _ in item)
        if total_qty < MIN_ORDER:
            gagal(f"Total {total_qty} pcs. Minimal order {MIN_ORDER} pcs, pesanan dibatalkan.")
            return

        # 3. harga dasar sesuai tier
        harga_dasar = cari_harga(cur, id_bahan, total_qty)
        if harga_dasar is None:
            gagal(f"Harga untuk {total_qty} pcs belum diatur di tabel harga_bahan, pesanan dibatalkan.")
            return

        # 4. finishing dan warna
        tabel(
            "FINISHING",
            [("No", "r", G_NO), ("Finishing", "l", G_LABEL)],
            list(FINISHING.items()),
            tema="kuning",
        )
        finishing = FINISHING[input_int("Pilih finishing:", set(FINISHING))]
        jml_warna = input_int(
            f"Jumlah warna ({WARNA_DASAR} warna pertama gratis, "
            f"tiap warna berikutnya +{rp(BIAYA_PER_WARNA)}):",
            minimum=1,
        )

        # 5. tambahan
        tambahan = pilih_tambahan(cur)
        extra_warna = biaya_tambah_warna(cur, jml_warna)
        biaya_warna = extra_warna[1] if extra_warna else 0
        biaya_pesanan = sum(h for _, _, h in tambahan) + biaya_warna  # per kaos, semua ukuran

        # 6. rincian dan ringkasan
        rincian = [(f"Harga dasar {nama_bahan}", rp(harga_dasar))]
        if extra_warna:
            rincian.append((f"Tambah warna ({jml_warna} warna)", plus(biaya_warna)))
        for _, nama_t, h in tambahan:
            rincian.append((nama_t, plus(h)))
        tabel(
            "RINCIAN HARGA PER KAOS",
            [("Komponen", "l", G_NAMA), ("Per kaos", "r", G_UANG)],
            rincian,
            total=("Harga per kaos (belum tambahan ukuran)", rp(harga_dasar + biaya_pesanan)),
            tema="ungu",
        )

        baris_ringkasan = []
        total_bayar = 0
        for _, nama_u, q, tambah_u in item:
            harga_u = harga_dasar + biaya_pesanan + tambah_u
            total_bayar += q * harga_u
            baris_ringkasan.append(
                (nama_u, q, plus(tambah_u) if tambah_u else "-", rp(harga_u), rp(q * harga_u))
            )
        tabel(
            f"RINGKASAN PESANAN | {nama_bahan} | {finishing} | {jml_warna} warna",
            [
                ("Ukuran", "l", G_NAMA),
                ("Jumlah", "r", G_ANGKA),
                ("Tambah ukuran", "r", G_TEKS),
                ("Harga/pcs", "r", G_TEKS),
                ("Subtotal", "r", G_UANG),
            ],
            baris_ringkasan,
            total=("TOTAL", total_qty, "", "", rp(total_bayar)),
            tema="hijau",
        )
        if not ya("Simpan pesanan? (y/n):"):
            info("Dibatalkan.")
            return

        # 7. simpan
        id_pel = pilih_pelanggan(cur)
        cur.execute(
            "INSERT INTO pesanan (id_pelanggan, tanggal, finishing, jumlah_warna) "
            "VALUES (%s, %s, %s, %s)",
            (id_pel, date.today(), finishing, jml_warna),
        )
        id_pesanan = cur.lastrowid
        for id_u, _, q, tambah_u in item:
            cur.execute(
                "INSERT INTO detail_pesanan "
                "(id_pesanan, id_bahan, id_ukuran, jumlah, harga_satuan) "
                "VALUES (%s, %s, %s, %s, %s)",
                (id_pesanan, id_bahan, id_u, q, harga_dasar + biaya_pesanan + tambah_u),
            )
        simpan_tambahan = [(i, h) for i, _, h in tambahan]
        if extra_warna and extra_warna[0] is not None:
            simpan_tambahan.append(extra_warna)
        for id_t, h in simpan_tambahan:
            cur.execute(
                "INSERT INTO pesanan_tambahan (id_pesanan, id_tambahan, harga) "
                "VALUES (%s, %s, %s)",
                (id_pesanan, id_t, h),
            )
        db.commit()
        kotak(
            f"PESANAN #{id_pesanan} TERSIMPAN",
            [
                [("Total bayar : ", (PUTIH,)), (rp(total_bayar), (BOLD, HIJAU))],
                [("Jumlah kaos : ", (PUTIH,)), (f"{total_qty} pcs", (BOLD, CYAN))],
            ],
            warna_garis=HIJAU,
            gaya_judul=(BOLD, HIJAU),
        )
    except Exception as e:
        db.rollback()
        gagal(f"Gagal menyimpan pesanan: {e}")


def rekap_per_ukuran(db):
    cur = db.cursor()
    cur.execute("""
        SELECT u.nama_ukuran,
               COALESCE(SUM(d.jumlah), 0),
               COALESCE(SUM(d.jumlah * d.harga_satuan), 0)
        FROM ukuran u
        LEFT JOIN detail_pesanan d ON d.id_ukuran = u.id_ukuran
        GROUP BY u.id_ukuran, u.nama_ukuran
        ORDER BY u.id_ukuran
    """)
    baris = [(nama, int(qty), int(total)) for nama, qty, total in cur.fetchall()]
    total_qty = sum(b[1] for b in baris)
    total_rp = sum(b[2] for b in baris)
    tabel(
        "REKAP PER UKURAN",
        [("Ukuran", "l", G_NAMA), ("Jumlah (pcs)", "r", G_ANGKA), ("Total (Rp)", "r", G_UANG)],
        [(n, q, rp(t)) for n, q, t in baris],
        total=("TOTAL", total_qty, rp(total_rp)),
        tema="biru",
    )


def rekap_per_bahan(db):
    cur = db.cursor()
    cur.execute("""
        SELECT b.nama_bahan,
               COALESCE(SUM(d.jumlah), 0),
               COALESCE(SUM(d.jumlah * d.harga_satuan), 0)
        FROM bahan_kain b
        LEFT JOIN detail_pesanan d ON d.id_bahan = b.id_bahan
        GROUP BY b.id_bahan, b.nama_bahan
        ORDER BY b.id_bahan
    """)
    baris = [(nama, int(qty), int(total)) for nama, qty, total in cur.fetchall()]
    total_qty = sum(b[1] for b in baris)
    total_rp = sum(b[2] for b in baris)
    tabel(
        "REKAP PER BAHAN",
        [("Bahan", "l", G_NAMA), ("Jumlah (pcs)", "r", G_ANGKA), ("Total (Rp)", "r", G_UANG)],
        [(n, q, rp(t)) for n, q, t in baris],
        total=("TOTAL", total_qty, rp(total_rp)),
        tema="ungu",
    )


KOLOM_RIWAYAT = [
    ("No", "r", G_NO),
    ("Tanggal", "l", G_TGL),
    ("Atas nama", "l", G_NAMA),
    ("Finishing", "l", G_LABEL),
    ("Warna", "r", (KUNING,)),
    ("Jumlah", "r", G_ANGKA),
    ("Total", "r", G_UANG),
]


def riwayat_pesanan(db, tema="biru", judul="RIWAYAT PESANAN"):
    cur = db.cursor()
    cur.execute("""
        SELECT p.id_pesanan, p.tanggal, pl.nama, p.finishing, p.jumlah_warna,
               SUM(d.jumlah), SUM(d.jumlah * d.harga_satuan)
        FROM pesanan p
        JOIN pelanggan pl ON pl.id_pelanggan = p.id_pelanggan
        JOIN detail_pesanan d ON d.id_pesanan = p.id_pesanan
        GROUP BY p.id_pesanan, p.tanggal, pl.nama, p.finishing, p.jumlah_warna
        ORDER BY p.id_pesanan DESC
    """)
    baris = [
        (id_p, tgl, nama, fin, jml_warna, int(qty), rp(total))
        for id_p, tgl, nama, fin, jml_warna, qty, total in cur.fetchall()
    ]
    tabel(judul, KOLOM_RIWAYAT, baris, tema=tema)


def detail_pesanan(db):
    riwayat_pesanan(db)
    cur = db.cursor()
    try:
        id_p = int(tanya("\nNomor pesanan yang dilihat (0 = batal):"))
    except ValueError:
        gagal("Masukkan angka saja.")
        return
    if id_p == 0:
        return

    cur.execute("""
        SELECT p.tanggal, pl.nama, pl.no_hp, p.finishing, p.jumlah_warna
        FROM pesanan p
        JOIN pelanggan pl ON pl.id_pelanggan = p.id_pelanggan
        WHERE p.id_pesanan = %s
    """, (id_p,))
    kepala = cur.fetchall()
    if not kepala:
        gagal("Pesanan tidak ditemukan.")
        return
    tgl, nama, no_hp, finishing, jml_warna = kepala[0]
    kotak(
        f"DETAIL PESANAN #{id_p}",
        [
            [("Atas nama : ", (PUTIH,)), (str(nama), (BOLD, PUTIH))],
            [("No HP     : ", (PUTIH,)), (str(no_hp or "-"), (PUTIH,))],
            [("Tanggal   : ", (PUTIH,)), (str(tgl), (ABU,))],
            [("Finishing : ", (PUTIH,)), (str(finishing), (UNGU,))],
            [("Warna     : ", (PUTIH,)), (f"{jml_warna} warna", (KUNING,))],
        ],
        warna_garis=CYAN,
    )

    cur.execute("""
        SELECT b.nama_bahan, u.nama_ukuran, d.jumlah, d.harga_satuan
        FROM detail_pesanan d
        JOIN bahan_kain b ON b.id_bahan = d.id_bahan
        JOIN ukuran u ON u.id_ukuran = d.id_ukuran
        WHERE d.id_pesanan = %s
        ORDER BY u.id_ukuran
    """, (id_p,))
    detail = cur.fetchall()
    total_qty = sum(int(r[2]) for r in detail)
    total_rp = sum(int(r[2]) * int(r[3]) for r in detail)
    tabel(
        "RINCIAN UKURAN",
        [
            ("Bahan", "l", G_NAMA),
            ("Ukuran", "l", G_TEKS),
            ("Jumlah", "r", G_ANGKA),
            ("Harga/pcs", "r", G_TEKS),
            ("Subtotal", "r", G_UANG),
        ],
        [(b, u, int(q), rp(h), rp(int(q) * int(h))) for b, u, q, h in detail],
        total=("TOTAL", "", total_qty, "", rp(total_rp)),
        tema="hijau",
    )

    cur.execute("""
        SELECT t.kelompok, t.nama, pt.harga
        FROM pesanan_tambahan pt
        JOIN tambahan t ON t.id_tambahan = pt.id_tambahan
        WHERE pt.id_pesanan = %s
        ORDER BY t.id_tambahan
    """, (id_p,))
    tambahan = cur.fetchall()
    if tambahan:
        tabel(
            "TAMBAHAN PADA PESANAN INI (per kaos)",
            [("Kelompok", "l", G_LABEL), ("Tambahan", "l", G_NAMA), ("Harga", "r", G_UANG)],
            [(k, n, plus(h)) for k, n, h in tambahan],
            tema="kuning",
        )
    else:
        info("Pesanan ini tanpa tambahan.")


def hapus_pesanan(db):
    riwayat_pesanan(db, tema="merah", judul="PILIH PESANAN YANG AKAN DIHAPUS")
    cur = db.cursor()
    try:
        id_p = int(tanya("\nNomor pesanan yang dihapus (0 = batal):"))
    except ValueError:
        gagal("Masukkan angka saja.")
        return
    if id_p == 0:
        info("Dibatalkan.")
        return

    cur.execute("""
        SELECT p.tanggal, pl.nama,
               COALESCE(SUM(d.jumlah), 0),
               COALESCE(SUM(d.jumlah * d.harga_satuan), 0)
        FROM pesanan p
        JOIN pelanggan pl ON pl.id_pelanggan = p.id_pelanggan
        LEFT JOIN detail_pesanan d ON d.id_pesanan = p.id_pesanan
        WHERE p.id_pesanan = %s
        GROUP BY p.id_pesanan, p.tanggal, pl.nama
    """, (id_p,))
    rows = cur.fetchall()
    if not rows:
        gagal("Pesanan tidak ditemukan.")
        return

    tgl, nama, qty, total = rows[0]
    tabel(
        "PESANAN INI AKAN DIHAPUS PERMANEN",
        [
            ("No", "r", G_NO),
            ("Tanggal", "l", G_TGL),
            ("Atas nama", "l", G_NAMA),
            ("Jumlah", "r", G_ANGKA),
            ("Total", "r", G_UANG),
        ],
        [(id_p, tgl, nama, int(qty), rp(total))],
        tema="merah",
    )
    if not ya("Yakin hapus? Data tidak bisa dikembalikan (y/n):"):
        info("Dibatalkan.")
        return

    try:
        cur.execute("DELETE FROM pesanan_tambahan WHERE id_pesanan = %s", (id_p,))
        cur.execute("DELETE FROM detail_pesanan WHERE id_pesanan = %s", (id_p,))
        cur.execute("DELETE FROM pesanan WHERE id_pesanan = %s", (id_p,))
        db.commit()
        sukses(f"Pesanan #{id_p} berhasil dihapus.")
    except Exception as e:
        
        db.rollback()
        
        gagal(f"Gagal menghapus: {e}")
        




def main():
    
    try:
        
        db = koneksi()
        
    except mysql.connector.Error as e:
        
        gagal("Tidak bisa terhubung ke database. Pastikan MySQL XAMPP menyala.")
        
        print(e)
        
        return
        


    while True:
        tampil_menu()
        pilihan = tanya("Pilih menu:").strip()
        if pilihan == "1":
            tambah_pesanan(db)
        elif pilihan == "2":
            rekap_per_ukuran(db)
        elif pilihan == "3":
            rekap_per_bahan(db)
        elif pilihan == "4":
            riwayat_pesanan(db)
        elif pilihan == "5":
            hapus_pesanan(db)
        elif pilihan == "6":
            detail_pesanan(db)
        elif pilihan == "0":
            break
        else:
            gagal("Menu tidak valid.")
    db.close()
    print(clr("\nSampai jumpa!", BOLD, CYAN))

main()