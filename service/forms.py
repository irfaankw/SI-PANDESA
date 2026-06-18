from django import forms
from .models import DomicileLetterRequest

class MoveLetterForm(forms.Form):
    keperluan = forms.CharField(
        max_length=255,
        error_messages={
            'required': 'Alasan kepindahan wajib diisi.',
            'max_length': 'Alasan terlalu panjang (maks. 255 karakter).',
        }
    )
    jumlah_anggota = forms.IntegerField(
        min_value=0,
        initial=0,
        error_messages={
            'required': 'Jumlah anggota wajib diisi (isi 0 jika pindah sendiri).',
            'invalid':  'Jumlah anggota harus berupa angka.',
            'min_value': 'Jumlah anggota tidak boleh negatif.',
        }
    )
    alamat_tujuan = forms.CharField(
        max_length=255,
        error_messages={'required': 'Nama jalan dan RT/RW wajib diisi.'}
    )
    kelurahan = forms.CharField(
        max_length=100,
        error_messages={'required': 'Kelurahan/Desa wajib diisi.'}
    )
    kecamatan = forms.CharField(
        max_length=100,
        error_messages={'required': 'Kecamatan wajib diisi.'}
    )
    kota_kabupaten = forms.CharField(
        max_length=100,
        error_messages={'required': 'Kota/Kabupaten wajib diisi.'}
    )
    provinsi = forms.CharField(
        max_length=100,
        error_messages={'required': 'Provinsi wajib diisi.'}
    )
    file_kk = forms.FileField(
        error_messages={'required': 'Kartu Keluarga wajib diunggah.'}
    )
    file_ktp = forms.FileField(
        error_messages={'required': 'KTP-el Pemohon wajib diunggah.'}
    )
    file_pengantar = forms.FileField(
        error_messages={'required': 'Surat Pengantar RT/RW wajib diunggah.'}
    )

    def clean_file_kk(self):
        return self._validate_file(self.cleaned_data.get('file_kk'))

    def clean_file_ktp(self):
        return self._validate_file(self.cleaned_data.get('file_ktp'))

    def clean_file_pengantar(self):
        return self._validate_file(self.cleaned_data.get('file_pengantar'))

    def _validate_file(self, f):
        if not f:
            return f
        allowed_types = ['application/pdf', 'image/jpeg', 'image/png']
        max_size = 5 * 1024 * 1024
        content_type = getattr(f, 'content_type', '')

        if content_type and content_type not in allowed_types:
            raise forms.ValidationError('Format tidak didukung. Gunakan PDF, JPG, atau PNG.')
        if f.size > max_size:
            raise forms.ValidationError('Ukuran file melebihi batas maksimal 5 MB.')
        return f

class DomicileLetterForm(forms.Form):
    keperluan = forms.CharField(
        max_length=255,
        error_messages={
            'required': 'Keperluan/tujuan surat wajib diisi.',
            'max_length': 'Maksimal 255 karakter.',
        }
    )
    tujuan_instansi = forms.CharField(
        max_length=255,
        error_messages={
            'required': 'Instansi/pihak tujuan surat wajib diisi.',
            'max_length': 'Maksimal 255 karakter.',
        }
    )
    status_tempat_tinggal = forms.ChoiceField(
        choices=DomicileLetterRequest.STATUS_TEMPAT_TINGGAL_CHOICES,
        error_messages={'required': 'Status tempat tinggal wajib dipilih.'}
    )
    TAHUN_CHOICES = [(i, f"{i} Tahun") for i in range(10)] + [(10, "10+ Tahun")]
    lama_tinggal_tahun = forms.TypedChoiceField(
        choices=TAHUN_CHOICES, coerce=int,
        error_messages={'required': 'Lama tinggal (tahun) wajib dipilih.'}
    )
    BULAN_CHOICES = [(i, f"{i} Bulan") for i in range(12)]
    lama_tinggal_bulan = forms.TypedChoiceField(
        choices=BULAN_CHOICES, coerce=int,
        required=False,
        empty_value=0,
        error_messages={'required': 'Lama tinggal (bulan) wajib dipilih.'}
    )
    file_kk = forms.FileField(error_messages={'required': 'Kartu Keluarga wajib diunggah.'})
    file_ktp = forms.FileField(error_messages={'required': 'KTP-el Pemohon wajib diunggah.'})
    file_pengantar = forms.FileField(error_messages={'required': 'Surat Pengantar RT/RW wajib diunggah.'})

    def clean(self):
        cleaned_data = super().clean()
        tahun = cleaned_data.get('lama_tinggal_tahun')
        if tahun is not None and tahun >= 10:
            cleaned_data['lama_tinggal_bulan'] = 0
        return cleaned_data

    def clean_file_kk(self):
        return self._validate_file(self.cleaned_data.get('file_kk'))

    def clean_file_ktp(self):
        return self._validate_file(self.cleaned_data.get('file_ktp'))

    def clean_file_pengantar(self):
        return self._validate_file(self.cleaned_data.get('file_pengantar'))

    def _validate_file(self, f):
        if not f:
            return f
        allowed_types = ['application/pdf', 'image/jpeg', 'image/png']
        max_size = 5 * 1024 * 1024
        content_type = getattr(f, 'content_type', '')
        
        if content_type and content_type not in allowed_types:
            raise forms.ValidationError('Format tidak didukung. Gunakan PDF, JPG, atau PNG.')
        if f.size > max_size:
            raise forms.ValidationError('Ukuran file melebihi batas maksimal 5 MB.')
        return f
    
class DeathLetterForm(forms.Form):
    # ── Data almarhum ─────────────────────────────────────────
    nama_almarhum = forms.CharField(
        max_length=255,
        error_messages={
            'required': 'Nama almarhum/almarhumah wajib diisi.',
            'max_length': 'Nama terlalu panjang (maks. 255 karakter).',
        }
    )
    nik_almarhum = forms.CharField(
        max_length=16, min_length=16,
        error_messages={
            'required': 'NIK almarhum/almarhumah wajib diisi.',
            'max_length': 'NIK harus 16 digit.',
            'min_length': 'NIK harus 16 digit.',
        }
    )
    JENIS_KELAMIN_CHOICES = [
        ('L', 'Laki-laki'),
        ('P', 'Perempuan'),
    ]
    jenis_kelamin = forms.ChoiceField(
        choices=JENIS_KELAMIN_CHOICES,
        error_messages={'required': 'Jenis kelamin wajib dipilih.'}
    )
    tempat_lahir = forms.CharField(
        max_length=100,
        error_messages={'required': 'Tempat lahir almarhum wajib diisi.'}
    )
    tanggal_lahir = forms.DateField(
        input_formats=['%Y-%m-%d'],
        error_messages={
            'required': 'Tanggal lahir almarhum wajib diisi.',
            'invalid':  'Format tanggal tidak valid.',
        }
    )
    tanggal_kematian = forms.DateField(
        input_formats=['%Y-%m-%d'],
        error_messages={
            'required': 'Tanggal kematian wajib diisi.',
            'invalid':  'Format tanggal tidak valid.',
        }
    )
    tempat_kematian = forms.CharField(
        max_length=255,
        error_messages={'required': 'Tempat kematian wajib diisi.'}
    )
    penyebab_kematian = forms.CharField(
        max_length=255, required=False,
    )
    hubungan_pelapor = forms.CharField(
        max_length=100,
        error_messages={'required': 'Hubungan pelapor dengan almarhum wajib diisi.'}
    )
    # ── Dokumen ───────────────────────────────────────────────
    file_kk = forms.FileField(
        error_messages={'required': 'Kartu Keluarga wajib diunggah.'}
    )
    file_ktp_almarhum = forms.FileField(
        error_messages={'required': 'KTP-el almarhum/almarhumah wajib diunggah.'}
    )
    file_surat_dokter = forms.FileField(
        required=False,
    )

    def clean_nik_almarhum(self):
        nik = self.cleaned_data.get('nik_almarhum', '')
        if not nik.isdigit():
            raise forms.ValidationError('NIK hanya boleh berisi angka.')
        return nik

    def clean_file_kk(self):
        return self._validate_file(self.cleaned_data.get('file_kk'))

    def clean_file_ktp_almarhum(self):
        return self._validate_file(self.cleaned_data.get('file_ktp_almarhum'))

    def clean_file_surat_dokter(self):
        return self._validate_file(self.cleaned_data.get('file_surat_dokter'))

    def _validate_file(self, f):
        if not f:
            return f
        allowed_types = ['application/pdf', 'image/jpeg', 'image/png']
        max_size = 5 * 1024 * 1024
        content_type = getattr(f, 'content_type', '')
        if content_type and content_type not in allowed_types:
            raise forms.ValidationError('Format tidak didukung. Gunakan PDF, JPG, atau PNG.')
        if f.size > max_size:
            raise forms.ValidationError('Ukuran file melebihi batas maksimal 5 MB.')
        return f
    
class BirthLetterForm(forms.Form):
    # ── Data bayi ─────────────────────────────────────────────
    nama_bayi = forms.CharField(
        max_length=255,
        error_messages={
            'required': 'Nama bayi wajib diisi.',
            'max_length': 'Nama terlalu panjang (maks. 255 karakter).',
        }
    )
    JENIS_KELAMIN_CHOICES = [
        ('L', 'Laki-laki'),
        ('P', 'Perempuan'),
    ]
    jenis_kelamin_bayi = forms.ChoiceField(
        choices=JENIS_KELAMIN_CHOICES,
        error_messages={'required': 'Jenis kelamin bayi wajib dipilih.'}
    )
    tanggal_lahir_bayi = forms.DateField(
        input_formats=['%Y-%m-%d'],
        error_messages={
            'required': 'Tanggal lahir bayi wajib diisi.',
            'invalid':  'Format tanggal tidak valid.',
        }
    )
    tempat_lahir_bayi = forms.CharField(
        max_length=255,
        error_messages={'required': 'Tempat lahir bayi wajib diisi.'}
    )
    ANAK_KE_CHOICES = [(i, f"Anak ke-{i}") for i in range(1, 16)]
    anak_ke = forms.TypedChoiceField(
        choices=ANAK_KE_CHOICES,
        coerce=int,
        initial=1,
        error_messages={'required': 'Urutan anak wajib dipilih.'}
    )

    # ── Data orang tua ────────────────────────────────────────
    nama_ayah = forms.CharField(
        max_length=255,
        error_messages={
            'required': 'Nama ayah wajib diisi.',
            'max_length': 'Nama terlalu panjang (maks. 255 karakter).',
        }
    )
    nik_ayah = forms.CharField(
        max_length=16, min_length=16,
        error_messages={
            'required': 'NIK ayah wajib diisi.',
            'max_length': 'NIK harus 16 digit.',
            'min_length': 'NIK harus 16 digit.',
        }
    )
    nama_ibu = forms.CharField(
        max_length=255,
        error_messages={
            'required': 'Nama ibu wajib diisi.',
            'max_length': 'Nama terlalu panjang (maks. 255 karakter).',
        }
    )
    nik_ibu = forms.CharField(
        max_length=16, min_length=16,
        error_messages={
            'required': 'NIK ibu wajib diisi.',
            'max_length': 'NIK harus 16 digit.',
            'min_length': 'NIK harus 16 digit.',
        }
    )

    # ── Dokumen ───────────────────────────────────────────────
    file_kk = forms.FileField(
        error_messages={'required': 'Kartu Keluarga wajib diunggah.'}
    )
    file_ktp_ayah = forms.FileField(
        error_messages={'required': 'KTP-el Ayah wajib diunggah.'}
    )
    file_ktp_ibu = forms.FileField(
        error_messages={'required': 'KTP-el Ibu wajib diunggah.'}
    )
    file_surat_rs = forms.FileField(
        required=False,
    )

    def clean_nik_ayah(self):
        nik = self.cleaned_data.get('nik_ayah', '')
        if not nik.isdigit():
            raise forms.ValidationError('NIK hanya boleh berisi angka.')
        return nik

    def clean_nik_ibu(self):
        nik = self.cleaned_data.get('nik_ibu', '')
        if not nik.isdigit():
            raise forms.ValidationError('NIK hanya boleh berisi angka.')
        return nik

    def clean_file_kk(self):
        return self._validate_file(self.cleaned_data.get('file_kk'))

    def clean_file_ktp_ayah(self):
        return self._validate_file(self.cleaned_data.get('file_ktp_ayah'))

    def clean_file_ktp_ibu(self):
        return self._validate_file(self.cleaned_data.get('file_ktp_ibu'))

    def clean_file_surat_rs(self):
        return self._validate_file(self.cleaned_data.get('file_surat_rs'))

    def _validate_file(self, f):
        if not f:
            return f
        allowed_types = ['application/pdf', 'image/jpeg', 'image/png']
        max_size = 5 * 1024 * 1024
        content_type = getattr(f, 'content_type', '')
        if content_type and content_type not in allowed_types:
            raise forms.ValidationError('Format tidak didukung. Gunakan PDF, JPG, atau PNG.')
        if f.size > max_size:
            raise forms.ValidationError('Ukuran file melebihi batas maksimal 5 MB.')
        return f

class PovertyLetterForm(forms.Form):

    KEPERLUAN_CHOICES = [
        ('', '— Pilih keperluan —'),
        ('beasiswa',         'Pengajuan Beasiswa'),
        ('keringanan_biaya', 'Keringanan Biaya Pendidikan'),
        ('bantuan_sosial',   'Permohonan Bantuan Sosial'),
        ('keringanan_rs',    'Keringanan Biaya Rumah Sakit'),
        ('lainnya',          'Lainnya'),
    ]

    keperluan = forms.ChoiceField(
        choices=KEPERLUAN_CHOICES,
        error_messages={'required': 'Keperluan/tujuan surat wajib dipilih.'}
    )
    keperluan_lain = forms.CharField(
        max_length=255, required=False,
        error_messages={'max_length': 'Maksimal 255 karakter.'}
    )
    tujuan_instansi = forms.CharField(
        max_length=255,
        error_messages={
            'required': 'Instansi/pihak tujuan surat wajib diisi.',
            'max_length': 'Maksimal 255 karakter.',
        }
    )
    penghasilan = forms.IntegerField(
        min_value=0,
        initial=0,
        error_messages={
            'required': 'Penghasilan wajib diisi (isi 0 jika tidak berpenghasilan).',
            'invalid':  'Penghasilan harus berupa angka.',
            'min_value': 'Penghasilan tidak boleh negatif.',
        }
    )
    jumlah_tanggungan = forms.IntegerField(
        min_value=0,
        initial=0,
        error_messages={
            'required': 'Jumlah tanggungan wajib diisi.',
            'invalid':  'Jumlah tanggungan harus berupa angka.',
            'min_value': 'Jumlah tanggungan tidak boleh negatif.',
        }
    )
    file_kk = forms.FileField(
        error_messages={'required': 'Kartu Keluarga wajib diunggah.'}
    )
    file_ktp = forms.FileField(
        error_messages={'required': 'KTP-el Pemohon wajib diunggah.'}
    )
    file_pengantar = forms.FileField(
        error_messages={'required': 'Surat Pengantar RT/RW wajib diunggah.'}
    )
    file_pendukung = forms.FileField(
        required=False,
    )

    def clean_keperluan(self):
        value = self.cleaned_data.get('keperluan', '')
        if not value:
            raise forms.ValidationError('Keperluan/tujuan surat wajib dipilih.')
        return value

    def clean(self):
        cleaned_data = super().clean()
        keperluan = cleaned_data.get('keperluan')
        keperluan_lain = cleaned_data.get('keperluan_lain', '').strip()
        if keperluan == 'lainnya' and not keperluan_lain:
            self.add_error('keperluan_lain', 'Mohon jelaskan keperluan Anda.')
        return cleaned_data

    def clean_file_kk(self):
        return self._validate_file(self.cleaned_data.get('file_kk'))

    def clean_file_ktp(self):
        return self._validate_file(self.cleaned_data.get('file_ktp'))

    def clean_file_pengantar(self):
        return self._validate_file(self.cleaned_data.get('file_pengantar'))

    def clean_file_pendukung(self):
        return self._validate_file(self.cleaned_data.get('file_pendukung'))

    def _validate_file(self, f):
        if not f:
            return f
        allowed_types = ['application/pdf', 'image/jpeg', 'image/png']
        max_size = 5 * 1024 * 1024
        content_type = getattr(f, 'content_type', '')
        if content_type and content_type not in allowed_types:
            raise forms.ValidationError('Format tidak didukung. Gunakan PDF, JPG, atau PNG.')
        if f.size > max_size:
            raise forms.ValidationError('Ukuran file melebihi batas maksimal 5 MB.')
        return f
    
class BusinessLetterForm(forms.Form):
 
    JENIS_USAHA_CHOICES = [
        ('', '— Pilih jenis usaha —'),
        ('perdagangan',  'Perdagangan / Toko'),
        ('pertanian',    'Pertanian / Perkebunan'),
        ('perikanan',    'Perikanan / Tambak'),
        ('jasa',         'Jasa / Servis'),
        ('kerajinan',    'Kerajinan / Industri Rumahan'),
        ('kuliner',      'Kuliner / Warung Makan'),
        ('peternakan',   'Peternakan'),
        ('lainnya',      'Lainnya'),
    ]
 
    KEPERLUAN_CHOICES = [
        ('', '— Pilih keperluan —'),
        ('permodalan',    'Pengajuan Modal / Pinjaman Usaha'),
        ('izin_usaha',    'Pengurusan Izin Usaha (SIUP/NIB)'),
        ('bantuan_pemda', 'Permohonan Bantuan Pemerintah'),
        ('kemitraan',     'Kemitraan / Kerja Sama Usaha'),
        ('lainnya',       'Lainnya'),
    ]
 
    # ── Data usaha ────────────────────────────────────────────
    nama_usaha = forms.CharField(
        max_length=255,
        error_messages={
            'required': 'Nama usaha wajib diisi.',
            'max_length': 'Nama usaha terlalu panjang (maks. 255 karakter).',
        }
    )
    jenis_usaha = forms.ChoiceField(
        choices=JENIS_USAHA_CHOICES,
        error_messages={'required': 'Jenis usaha wajib dipilih.'}
    )
    jenis_usaha_lain = forms.CharField(
        max_length=255, required=False,
        error_messages={'max_length': 'Maksimal 255 karakter.'}
    )
    alamat_usaha = forms.CharField(
        max_length=255,
        error_messages={'required': 'Alamat/lokasi usaha wajib diisi.'}
    )
    lama_usaha_tahun = forms.IntegerField(
        min_value=0,
        initial=0,
        error_messages={
            'required': 'Lama usaha wajib diisi.',
            'invalid':  'Lama usaha harus berupa angka.',
            'min_value': 'Lama usaha tidak boleh negatif.',
        }
    )
    omset_perbulan = forms.IntegerField(
        min_value=0,
        initial=0,
        error_messages={
            'required': 'Perkiraan omset wajib diisi (isi 0 jika belum diketahui).',
            'invalid':  'Omset harus berupa angka.',
            'min_value': 'Omset tidak boleh negatif.',
        }
    )
 
    # ── Keperluan surat ───────────────────────────────────────
    keperluan = forms.ChoiceField(
        choices=KEPERLUAN_CHOICES,
        error_messages={'required': 'Keperluan surat wajib dipilih.'}
    )
    keperluan_lain = forms.CharField(
        max_length=255, required=False,
        error_messages={'max_length': 'Maksimal 255 karakter.'}
    )
    tujuan_instansi = forms.CharField(
        max_length=255,
        error_messages={
            'required': 'Instansi tujuan wajib diisi.',
            'max_length': 'Maksimal 255 karakter.',
        }
    )
 
    # ── Dokumen ───────────────────────────────────────────────
    file_ktp = forms.FileField(
        error_messages={'required': 'KTP-el Pemohon wajib diunggah.'}
    )
    file_kk = forms.FileField(
        error_messages={'required': 'Kartu Keluarga wajib diunggah.'}
    )
    file_foto_usaha = forms.FileField(required=False)
 
    def clean_jenis_usaha(self):
        value = self.cleaned_data.get('jenis_usaha', '')
        if not value:
            raise forms.ValidationError('Jenis usaha wajib dipilih.')
        return value
 
    def clean_keperluan(self):
        value = self.cleaned_data.get('keperluan', '')
        if not value:
            raise forms.ValidationError('Keperluan surat wajib dipilih.')
        return value
 
    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('jenis_usaha') == 'lainnya' and not cleaned_data.get('jenis_usaha_lain', '').strip():
            self.add_error('jenis_usaha_lain', 'Mohon jelaskan jenis usaha Anda.')
        if cleaned_data.get('keperluan') == 'lainnya' and not cleaned_data.get('keperluan_lain', '').strip():
            self.add_error('keperluan_lain', 'Mohon jelaskan keperluan Anda.')
        return cleaned_data
 
    def clean_file_ktp(self):
        return self._validate_file(self.cleaned_data.get('file_ktp'))
 
    def clean_file_kk(self):
        return self._validate_file(self.cleaned_data.get('file_kk'))
 
    def clean_file_foto_usaha(self):
        return self._validate_file(self.cleaned_data.get('file_foto_usaha'))
 
    def _validate_file(self, f):
        if not f:
            return f
        allowed_types = ['application/pdf', 'image/jpeg', 'image/png']
        max_size = 5 * 1024 * 1024
        content_type = getattr(f, 'content_type', '')
        if content_type and content_type not in allowed_types:
            raise forms.ValidationError('Format tidak didukung. Gunakan PDF, JPG, atau PNG.')
        if f.size > max_size:
            raise forms.ValidationError('Ukuran file melebihi batas maksimal 5 MB.')
        return f
    
class IntroLetterForm(forms.Form):

    KEPERLUAN_CHOICES = [
        ('', '— Pilih keperluan —'),
        ('pembuatan_ktp',  'Pembuatan / Perpanjangan KTP'),
        ('pembuatan_kk',   'Pembuatan / Perubahan Kartu Keluarga'),
        ('akta_kelahiran', 'Pengurusan Akta Kelahiran'),
        ('akta_kematian',  'Pengurusan Akta Kematian'),
        ('nikah',          'Pengurusan Pernikahan'),
        ('skck',           'Pembuatan SKCK'),
        ('beasiswa',       'Pengajuan Beasiswa'),
        ('perizinan',      'Pengurusan Perizinan / Legalitas'),
        ('lainnya',        'Lainnya'),
    ]

    keperluan = forms.ChoiceField(
        choices=KEPERLUAN_CHOICES,
        error_messages={'required': 'Keperluan/tujuan surat wajib dipilih.'}
    )
    keperluan_lain = forms.CharField(
        max_length=255, required=False,
        error_messages={'max_length': 'Maksimal 255 karakter.'}
    )
    tujuan_instansi = forms.CharField(
        max_length=255,
        error_messages={
            'required': 'Instansi/pihak tujuan surat wajib diisi.',
            'max_length': 'Maksimal 255 karakter.',
        }
    )
    keterangan_tambahan = forms.CharField(
        max_length=500, required=False,
        error_messages={'max_length': 'Maksimal 500 karakter.'}
    )
    file_ktp = forms.FileField(
        error_messages={'required': 'KTP-el Pemohon wajib diunggah.'}
    )
    file_kk = forms.FileField(
        error_messages={'required': 'Kartu Keluarga wajib diunggah.'}
    )
    file_pendukung = forms.FileField(required=False)

    def clean_keperluan(self):
        value = self.cleaned_data.get('keperluan', '')
        if not value:
            raise forms.ValidationError('Keperluan/tujuan surat wajib dipilih.')
        return value

    def clean(self):
        cleaned_data = super().clean()
        keperluan = cleaned_data.get('keperluan')
        keperluan_lain = cleaned_data.get('keperluan_lain', '').strip()
        if keperluan == 'lainnya' and not keperluan_lain:
            self.add_error('keperluan_lain', 'Mohon jelaskan keperluan Anda.')
        return cleaned_data

    def clean_file_ktp(self):
        return self._validate_file(self.cleaned_data.get('file_ktp'))

    def clean_file_kk(self):
        return self._validate_file(self.cleaned_data.get('file_kk'))

    def clean_file_pendukung(self):
        return self._validate_file(self.cleaned_data.get('file_pendukung'))

    def _validate_file(self, f):
        if not f:
            return f
        allowed_types = ['application/pdf', 'image/jpeg', 'image/png']
        max_size = 5 * 1024 * 1024
        content_type = getattr(f, 'content_type', '')
        if content_type and content_type not in allowed_types:
            raise forms.ValidationError('Format tidak didukung. Gunakan PDF, JPG, atau PNG.')
        if f.size > max_size:
            raise forms.ValidationError('Ukuran file melebihi batas maksimal 5 MB.')
        return f