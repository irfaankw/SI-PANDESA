from django.db import models


class Tag(models.Model):
    nama = models.CharField(max_length=50, unique=True, verbose_name="Nama Tag")
    slug = models.SlugField(max_length=60, unique=True, blank=True)
    warna = models.CharField(
        max_length=30,
        default="green",
        verbose_name="Warna Badge",
        help_text="Pilihan: green, blue, yellow, red, purple, orange"
    )

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tag"
        ordering = ["nama"]

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.nama)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nama


class GaleriPhoto(models.Model):
    foto = models.ImageField(upload_to="galeri/%Y/%m/", verbose_name="Foto")
    judul = models.CharField(max_length=120, verbose_name="Judul Foto", blank=True)
    deskripsi = models.TextField(verbose_name="Deskripsi Singkat", blank=True)
    tags = models.ManyToManyField(Tag, blank=True, verbose_name="Tags")
    bulan_tahun = models.DateField(
        verbose_name="Bulan & Tahun",
        help_text="Isi tanggal 1, yang ditampilkan hanya bulan & tahunnya"
    )
    urutan = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="Urutan Tampil",
        help_text="Angka lebih kecil tampil lebih dulu"
    )
    ditampilkan = models.BooleanField(default=True, verbose_name="Tampilkan?")
    dibuat_pada = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Foto Galeri"
        verbose_name_plural = "Foto Galeri"
        ordering = ["urutan", "-bulan_tahun"]

    def __str__(self):
        return self.judul or f"Foto {self.pk}"

    def bulan_tahun_display(self):
        BULAN_ID = {
            1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr",
            5: "Mei", 6: "Jun", 7: "Jul", 8: "Agu",
            9: "Sep", 10: "Okt", 11: "Nov", 12: "Des",
        }
        return f"{BULAN_ID[self.bulan_tahun.month]} {self.bulan_tahun.year}"