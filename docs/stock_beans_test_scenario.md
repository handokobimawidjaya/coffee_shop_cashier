# Schema Uji Coba Stock Beans Coffee Shop

Dokumen ini dipakai untuk menguji alur stock biji kopi/beans masuk, beans dipakai sebagai bahan minuman kopi di POS, stok menipis, lalu notification low stock muncul.

## Tujuan Uji

Memastikan:

1. Stock beans bisa ditambahkan sebagai bahan baku.
2. Produk minuman kopi bisa memakai resep beans per gelas.
3. Saat minuman dijual di POS, stock beans otomatis berkurang.
4. Saat stock beans menyentuh threshold, notifikasi low stock muncul.
5. Laporan stock Excel menunjukkan status beans sebagai `KRITIS`.

## Data Uji

| Item | Nilai |
| --- | ---: |
| Produk bahan baku | Arabica Beans |
| UoM beans | gr |
| Stock awal beans | 250 gr |
| Low stock threshold | 50 gr |
| Produk minuman | Kopi Susu |
| Beans ingredient untuk Kopi Susu | Arabica Beans |
| Beans per cup | 15 gr |

## Rumus Stock

```text
Stock akhir beans = Stock awal beans - (Jumlah gelas terjual x Beans per cup)
```

Contoh:

```text
250 gr - (14 gelas x 15 gr) = 40 gr
```

Karena `40 gr <= 50 gr`, maka stock masuk kondisi kritis dan notifikasi low stock harus muncul.

## Persiapan Master Data

1. Buka menu `Inventory > Products > Products`.
2. Pastikan produk `Arabica Beans`:
   - Product Type: storable/stockable.
   - Product Category: `Beans`.
   - Unit of Measure: `g` atau `gram`.
   - `Alert on Low Stock`: aktif.
   - `Low Stock Threshold`: `50`.
3. Tambahkan stock awal `Arabica Beans` sebesar `250 gr`.
   - Bisa lewat Inventory Adjustment.
   - Bisa juga lewat Receipt/Penerimaan Barang dari supplier.
4. Buat atau buka produk minuman `Kopi Susu`.
5. Buka produk minuman `Kopi Susu`, lalu masuk ke tab `Inventory`.
6. Pada section `Coffee Shop Recipe`, pastikan:
   - `Available in POS`: aktif.
   - `Coffee Beans Ingredient`: `Arabica Beans`.
   - `Beans per Cup`: `15`.

## Skenario Uji A: Stock Beans Masuk

Langkah:

1. Masuk ke `Inventory`.
2. Tambahkan stock `Arabica Beans` sebesar `250 gr`.
3. Validate transaksi stock masuk.
4. Buka produk `Arabica Beans`.

Expected result:

| Field | Expected |
| --- | ---: |
| On Hand Quantity | 250 gr |
| Low Stock Threshold | 50 gr |
| Low Stock Alert Sent | Tidak aktif |
| Status di laporan stock | OK |

## Skenario Uji B: Jual 1 Gelas Kopi Susu

Langkah:

1. Buka POS.
2. Jual `Kopi Susu` sebanyak `1` gelas.
3. Lakukan pembayaran sampai order berstatus paid/done.
4. Buka produk `Arabica Beans`.

Expected result:

```text
250 gr - (1 x 15 gr) = 235 gr
```

| Field | Expected |
| --- | ---: |
| On Hand Quantity Arabica Beans | 235 gr |
| Low Stock Alert Sent | Tidak aktif |
| Notification | Belum muncul |

## Skenario Uji C: Jual Sampai Mendekati Threshold

Langkah:

1. Dari stock `235 gr`, jual `Kopi Susu` sebanyak `12` gelas lagi.
2. Lakukan pembayaran sampai order berstatus paid/done.
3. Buka produk `Arabica Beans`.

Expected result:

```text
235 gr - (12 x 15 gr) = 55 gr
```

| Field | Expected |
| --- | ---: |
| On Hand Quantity Arabica Beans | 55 gr |
| Low Stock Threshold | 50 gr |
| Low Stock Alert Sent | Tidak aktif |
| Notification | Belum muncul |
| Status di laporan stock | OK |

## Skenario Uji D: Jual Sampai Stock Kritis

Langkah:

1. Dari stock `55 gr`, jual `Kopi Susu` sebanyak `1` gelas lagi.
2. Lakukan pembayaran sampai order berstatus paid/done.
3. Buka produk `Arabica Beans`.
4. Cek dashboard Coffee Shop dan email notifikasi.

Expected result:

```text
55 gr - (1 x 15 gr) = 40 gr
```

| Field | Expected |
| --- | ---: |
| On Hand Quantity Arabica Beans | 40 gr |
| Low Stock Threshold | 50 gr |
| Low Stock Alert Sent | Aktif |
| Notification email | Terkirim |
| Dashboard Stok Kritis | Arabica Beans tampil |
| Status di laporan stock | KRITIS |

## Skenario Uji E: Export Laporan Stock Excel

Langkah:

1. Buka `Coffee Shop > Laporan > Laporan Stok`.
2. Pilih filter `Only Critical Stock (Below Threshold)`.
3. Klik `Export Excel`.
4. Buka file Excel hasil download.

Expected result:

Sheet `Stock` berisi `Arabica Beans` dengan:

| Kolom | Expected |
| --- | ---: |
| Qty | 40 |
| UoM | gr |
| Threshold | 50 |
| Status | KRITIS |

## Skenario Uji F: Restock Beans Setelah Kritis

Langkah:

1. Tambahkan stock masuk `Arabica Beans` sebesar `210 gr`.
2. Validate stock masuk.
3. Jalankan tombol `Cek Stok Rendah Sekarang` di dashboard Coffee Shop, atau tunggu cron low stock.
4. Buka produk `Arabica Beans`.

Expected result:

```text
40 gr + 210 gr = 250 gr
```

| Field | Expected |
| --- | ---: |
| On Hand Quantity Arabica Beans | 250 gr |
| Low Stock Alert Sent | Tidak aktif |
| Dashboard Stok Kritis | Arabica Beans tidak tampil |
| Status di laporan stock | OK |

## Catatan Penting

- Setelah update kode modul, restart server Odoo dulu sebelum klik Upgrade module.
- Untuk contoh ini, UoM beans harus gram. Jika memakai kilogram, angka `15` akan dibaca sebagai `15 kg`, bukan `15 gr`.
- Notification email memakai konfigurasi `Coffee Shop Alert Email`. Jika kosong, sistem memakai email company atau user sebagai fallback.
