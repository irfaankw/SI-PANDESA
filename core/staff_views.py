from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django import forms as django_forms
from django.contrib.auth.models import User

from core.decorators import staff_desa_required
from .models import StafDesa, KategoriStaf

# ── Widget CSS helper ─────────────────────────────────────────────────────────
_INPUT = (
    "w-full px-4 py-3 border border-slate-200 rounded-xl "
    "focus:outline-none focus:ring-2 focus:ring-emerald-500 "
    "bg-white text-slate-800 text-sm"
)
_CHECKBOX = "h-4 w-4 rounded border-slate-300 text-emerald-600 focus:ring-emerald-500"


# ── Form ──────────────────────────────────────────────────────────────────────
class StafDesaForm(django_forms.ModelForm):

    class Meta:
        model  = StafDesa
        fields = [
            'nama', 'gelar_depan', 'gelar_belakang',
            'jabatan', 'kategori',
            'user',
            'telepon', 'email', 'alamat',
            'tahun_mulai', 'masih_aktif', 'tahun_selesai',
            'foto', 'bio',
            'urutan', 'aktif_tampil',
        ]
        widgets = {
            'nama'          : django_forms.TextInput(attrs={'class': _INPUT, 'placeholder': 'Nama lengkap (tanpa gelar)'}),
            'gelar_depan'   : django_forms.TextInput(attrs={'class': _INPUT, 'placeholder': 'Dr., H., dll.'}),
            'gelar_belakang': django_forms.TextInput(attrs={'class': _INPUT, 'placeholder': 'S.E., M.M., dll.'}),
            'jabatan'       : django_forms.TextInput(attrs={'class': _INPUT, 'placeholder': 'Kepala Desa, Sekretaris, dll.'}),
            'kategori'      : django_forms.Select(attrs={'class': _INPUT}),
            'user'          : django_forms.Select(attrs={'class': _INPUT}),
            'telepon'       : django_forms.TextInput(attrs={'class': _INPUT, 'placeholder': '08xx-xxxx-xxxx'}),
            'email'         : django_forms.EmailInput(attrs={'class': _INPUT, 'placeholder': 'email@contoh.com'}),
            'alamat'        : django_forms.TextInput(attrs={'class': _INPUT, 'placeholder': 'Dusun / RT-RW'}),
            'tahun_mulai'   : django_forms.NumberInput(attrs={'class': _INPUT, 'placeholder': '2020'}),
            'masih_aktif'   : django_forms.CheckboxInput(attrs={'class': _CHECKBOX}),
            'tahun_selesai' : django_forms.NumberInput(attrs={'class': _INPUT, 'placeholder': 'Kosongkan jika masih aktif'}),
            'bio'           : django_forms.Textarea(attrs={'class': _INPUT, 'rows': 4, 'placeholder': 'Narasi singkat tentang staf ini...'}),
            'urutan'        : django_forms.NumberInput(attrs={'class': _INPUT, 'placeholder': '0'}),
            'aktif_tampil'  : django_forms.CheckboxInput(attrs={'class': _CHECKBOX}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dropdown user: hanya user yang belum jadi StafDesa lain
        # (kecuali user yang sedang diedit — kalau edit, exclude semua kecuali dirinya sendiri)
        taken_qs = StafDesa.objects.filter(user__isnull=False)
        if self.instance.pk and self.instance.user_id:
            taken_qs = taken_qs.exclude(pk=self.instance.pk)
        taken_ids = taken_qs.values_list('user_id', flat=True)
        self.fields['user'].queryset = User.objects.exclude(pk__in=taken_ids).order_by('first_name', 'username')
        self.fields['user'].empty_label = '— Tidak dihubungkan ke akun —'
        self.fields['user'].required = False

        # foto tidak wajib saat edit
        self.fields['foto'].required = False

    def clean(self):
        cleaned = super().clean()
        masih_aktif  = cleaned.get('masih_aktif')
        tahun_selesai = cleaned.get('tahun_selesai')
        if not masih_aktif and not tahun_selesai:
            self.add_error('tahun_selesai', 'Isi tahun selesai jika sudah tidak aktif.')
        return cleaned


# ── Views ─────────────────────────────────────────────────────────────────────

@staff_desa_required
def staff_anggota_list(request):
    anggota_list = StafDesa.objects.select_related('user').order_by('urutan', 'nama')
    stats = {
        'total'       : anggota_list.count(),
        'aktif_tampil': anggota_list.filter(aktif_tampil=True).count(),
        'masih_aktif' : anggota_list.filter(masih_aktif=True).count(),
    }
    return render(request, 'core/staff_dashboard.html', {
        'anggota_list': anggota_list,
        'stats'       : stats,
    })


@staff_desa_required
def staff_anggota_tambah(request):
    form = StafDesaForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        staf = form.save()
        messages.success(request, f'Anggota "{staf.nama_lengkap}" berhasil ditambahkan.')
        return redirect('core_staff:dashboard')
    return render(request, 'core/staff_form.html', {
        'form' : form,
        'title': 'Tambah Anggota Desa',
        'is_edit': False,
    })


@staff_desa_required
def staff_anggota_edit(request, pk):
    staf = get_object_or_404(StafDesa, pk=pk)
    form = StafDesaForm(request.POST or None, request.FILES or None, instance=staf)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'Data "{staf.nama_lengkap}" berhasil diperbarui.')
        return redirect('core_staff:dashboard')
    return render(request, 'core/staff_form.html', {
        'form'   : form,
        'title'  : f'Edit — {staf.nama_lengkap}',
        'staf'   : staf,
        'is_edit': True,
    })


@staff_desa_required
def staff_anggota_hapus(request, pk):
    staf = get_object_or_404(StafDesa, pk=pk)
    if request.method == 'POST':
        nama = staf.nama_lengkap
        staf.delete()
        messages.success(request, f'Anggota "{nama}" berhasil dihapus.')
        return redirect('core_staff:dashboard')
    return render(request, 'core/staff_hapus.html', {'staf': staf})