from django import forms
from django.utils import timezone
from datetime import timedelta

from .models import ComplaintReport


class ComplaintForm(forms.Form):
    judul = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'placeholder': 'Judul singkat pengaduan Anda'}),
    )
    kategori = forms.ChoiceField(choices=ComplaintReport.KATEGORI_CHOICES)
    kategori_lain = forms.CharField(
        max_length=255, required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Sebutkan kategori lainnya'}),
    )
    lokasi = forms.CharField(
        max_length=255, required=False,
        widget=forms.TextInput(attrs={'placeholder': 'RT/RW, nama jalan, dll.'}),
    )
    deskripsi = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Jelaskan pengaduan atau aspirasi Anda secara detail...', 'rows': 5}),
    )
    bukti_foto = forms.FileField(required=False)
    setuju = forms.BooleanField(error_messages={'required': 'Anda harus menyetujui pernyataan ini.'})

    def clean(self):
        cleaned = super().clean()
        kategori      = cleaned.get('kategori')
        kategori_lain = cleaned.get('kategori_lain', '').strip()

        if kategori == 'lainnya' and not kategori_lain:
            self.add_error('kategori_lain', 'Harap sebutkan kategori lainnya.')

        return cleaned

    def check_rate_limit(self, user):
        """Return True kalau user sudah submit dalam 5 menit terakhir."""
        cutoff = timezone.now() - timedelta(minutes=5)
        return ComplaintReport.objects.filter(
            user=user,
            created_at__gte=cutoff,
        ).exists()