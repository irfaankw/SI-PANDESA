from django import forms
from .models import UserProfile

class UserProfileForm(forms.ModelForm):
    class Meta:
        model  = UserProfile
        fields = [
            'avatar', 'nik', 'jenis_kelamin', 'tanggal_lahir',
            'no_hp', 'alamat', 'rt', 'rw', 'dusun', 'pekerjaan',
            'agama', 'foto_ktp',
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
    class Meta:
        model  = UserProfile
        fields = ['avatar']

class EmailOTPRequestForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': 'nama@email.com'})
    )

class EmailOTPVerifyForm(forms.Form):
    code = forms.CharField(max_length=6, min_length=6)

    def clean_code(self):
        code = self.cleaned_data['code']
        if not code.isdigit():
            raise forms.ValidationError('Kode harus 6 digit angka.')
        return code