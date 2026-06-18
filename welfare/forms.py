# welfare/forms.py
from django import forms
from .models import UMKM, Produk

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
            'harga': forms.NumberInput(attrs={
                'placeholder': 'Contoh: 150000',
                'class': _INPUT,
            }),
            'harga_coret': forms.NumberInput(attrs={
                'placeholder': 'Kosongkan jika tidak ada diskon',
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