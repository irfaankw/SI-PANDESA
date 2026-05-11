from django import forms
from .models import UserProfile


# ─────────────────────────────────────────────────────────────
#  AUTH FORMS
# ─────────────────────────────────────────────────────────────

class LoginForm(forms.Form):
    email    = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': 'email@contoh.com'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Masukkan password'})
    )


class RegisterForm(forms.Form):
    nama_lengkap = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'Nama sesuai KTP'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': 'email@contoh.com'})
    )
    no_hp = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={'placeholder': '08xxxxxxxxxx'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Min. 8 karakter'})
    )

    def clean_password(self):
        password = self.cleaned_data.get('password', '')
        if len(password) < 8:
            raise forms.ValidationError('Password minimal 8 karakter.')
        return password

    def clean_no_hp(self):
        no_hp = self.cleaned_data.get('no_hp', '')
        if not no_hp.isdigit():
            raise forms.ValidationError('Nomor HP hanya boleh berisi angka.')
        return no_hp


# ─────────────────────────────────────────────────────────────
#  PROFILE FORM
# ─────────────────────────────────────────────────────────────

class UserProfileForm(forms.ModelForm):

    class Meta:
        model  = UserProfile
        fields = [
            'avatar',
            'nik',
            'jenis_kelamin',
            'tanggal_lahir',
            'no_hp',
            'alamat',
            'rt',
            'rw',
            'dusun',
            'pekerjaan',
            'agama',
            'foto_ktp',
        ]
        widgets = {
            'tanggal_lahir': forms.DateInput(attrs={'type': 'date'}),
            'nik':           forms.TextInput(attrs={'maxlength': '16', 'placeholder': '16 digit NIK'}),
            'no_hp':         forms.TextInput(attrs={'placeholder': '08xxxxxxxxxx'}),
            'alamat':        forms.TextInput(attrs={'placeholder': 'Nama jalan dan nomor'}),
            'rt':            forms.TextInput(attrs={'maxlength': '3', 'placeholder': '001'}),
            'rw':            forms.TextInput(attrs={'maxlength': '3', 'placeholder': '003'}),
            'dusun':         forms.TextInput(attrs={'placeholder': 'Nama dusun'}),
            'pekerjaan':     forms.TextInput(attrs={'placeholder': 'Petani, Pedagang, dll'}),
            'agama':         forms.TextInput(attrs={'placeholder': 'Islam, Kristen, dll'}),
        }

    def __init__(self, *args, **kwargs):
        # Jika sudah verified, kunci field sensitif
        self.is_verified = kwargs.pop('is_verified', False)
        super().__init__(*args, **kwargs)
        if self.is_verified:
            for field_name in ('nik', 'jenis_kelamin', 'tanggal_lahir', 'foto_ktp'):
                self.fields[field_name].disabled = True

    def clean_nik(self):
        nik = self.cleaned_data.get('nik', '')
        if nik and (not nik.isdigit() or len(nik) != 16):
            raise forms.ValidationError('NIK harus 16 digit angka.')
        return nik

class AvatarForm(forms.ModelForm):
    """Form khusus untuk upload avatar saja."""
    class Meta:
        model  = UserProfile
        fields = ['avatar']