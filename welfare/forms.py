from django import forms
from .models import UMKM, Produk
from core.utils import parse_rupiah, format_rupiah

_INPUT = (
    "w-full px-4 py-3 border border-slate-200 rounded-xl "
    "focus:outline-none focus:ring-2 focus:ring-emerald-500 "
    "bg-white text-slate-800 text-sm transition-all duration-200"
)


class UMKMForm(forms.ModelForm):
    class Meta:
        model  = UMKM
        fields = ['nama_usaha', 'deskripsi', 'alamat_usaha']
        widgets = {
            'nama_usaha': forms.TextInput(attrs={
                'placeholder': 'Contoh: Warung Bu Sari',
                'class': _INPUT,
            }),
            'deskripsi': forms.Textarea(attrs={
                'placeholder': 'Jelaskan produk atau layanan usaha Anda...',
                'rows': 4,
                'class': _INPUT,
            }),
            'alamat_usaha': forms.TextInput(attrs={
                'placeholder': 'Contoh: Dusun Tengah, RT 001/RW 002',
                'class': _INPUT,
            }),
        }


class ProdukForm(forms.ModelForm):
    class Meta:
        model  = Produk
        fields = ['nama', 'deskripsi', 'harga', 'harga_coret', 'kategori', 'foto', 'tags']
        widgets = {
            'nama': forms.TextInput(attrs={
                'placeholder': 'Contoh: Batik Tulis Motif Padi',
                'class': _INPUT,
            }),
            'deskripsi': forms.Textarea(attrs={
                'placeholder': 'Deskripsi produk Anda...',
                'rows': 4,
                'class': _INPUT,
            }),
            'harga': forms.TextInput(attrs={
                'placeholder': 'Contoh: 150000 atau 150.000',
                'class': _INPUT,
            }),
            'harga_coret': forms.TextInput(attrs={
                'placeholder': 'Contoh: 200000 atau 200.000',
                'class': _INPUT,
            }),
            'kategori': forms.Select(attrs={
                'class': _INPUT,
            }),
            'tags': forms.TextInput(attrs={
                'placeholder': 'Contoh: organik, segar, lokal',
                'class': _INPUT,
            }),
            'foto': forms.ClearableFileInput(attrs={
                'class': 'hidden',
                'accept': 'image/*',
                'id': 'foto-input',
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Format harga saat edit (hanya saat load form, bukan saat submit)
        if self.instance.pk and not self.is_bound:
            if self.instance.harga:
                formatted = format_rupiah(self.instance.harga)
                self.fields['harga'].initial = formatted.replace("Rp ", "")
            
            if self.instance.harga_coret:
                formatted = format_rupiah(self.instance.harga_coret)
                self.fields['harga_coret'].initial = formatted.replace("Rp ", "")
    
    def clean_harga(self):
        """Validasi dan parse harga jual"""
        harga_raw = self.data.get('harga', '').strip()
        
        if not harga_raw:
            raise forms.ValidationError('Harga tidak boleh kosong')
        
        harga = parse_rupiah(harga_raw)
        
        if harga == 0:
            raise forms.ValidationError('Format harga tidak valid')
        
        if harga < 1000:
            raise forms.ValidationError('Harga minimal Rp 1.000')
        
        return harga

    def clean_harga_coret(self):
        """Validasi dan parse harga sebelum diskon"""
        harga_coret_raw = self.data.get('harga_coret', '').strip()
        
        # Field opsional - boleh kosong
        if not harga_coret_raw:
            return None
        
        harga_coret = parse_rupiah(harga_coret_raw)
        
        if harga_coret == 0:
            raise forms.ValidationError('Format harga diskon tidak valid')
        
        if harga_coret < 1000:
            raise forms.ValidationError('Harga diskon minimal Rp 1.000')
        
        return harga_coret
    
    def clean(self):
        """Validasi cross-field: harga_coret harus > harga"""
        cleaned_data = super().clean()
        
        harga = cleaned_data.get('harga')
        harga_coret = cleaned_data.get('harga_coret')
        
        # Jika ada keduanya, validasi
        if harga and harga_coret:
            if harga_coret <= harga:
                error_msg = (
                    f'Harga sebelum diskon harus lebih tinggi dari harga jual. '
                    f'Sekarang: Diskon {format_rupiah(harga_coret)} < Jual {format_rupiah(harga)}'
                )
                self.add_error('harga_coret', error_msg)
        
        return cleaned_data