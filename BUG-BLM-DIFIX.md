nomor antrian hangus kalau sudah diluar dari batas kerja puskesmas.✅
layanan kesehatan mirip dgn mobile JKN.✅

-------------PENYESUAIAN FITUR-------------
user blm login masih bisa akses layanan
ai belum terpasang
kalau user search di url query "/service" atau "/layanan" itu error. seharusnya redirect..

urls.py (config):
    path('services/', include([
        # Path: /services/mail/ (Layanan Surat)
        path('mail/', include('service.urls', namespace='service')),
        
        # Path: /services/health/ (Layanan Kesehatan)
        # Catatan: Kita ganti 'kesehatan' jadi 'health' di URL agar konsisten Inggris
        path('health/', include('health.urls', namespace='health')),
        
        # Kedepannya kamu tinggal tambah di sini:
        # path('complaint/', include('complaint.urls', namespace='complaint')),
    ])),

navba_mobile routingnya blm disesuaikan.
buat file template sidebar profile user (lebih modular)