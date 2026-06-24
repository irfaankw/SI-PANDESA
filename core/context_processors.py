def user_role(request):
    """
    Inject variabel peran user secara global ke semua template.

    Tiga role yang dikenali:
    - Warga biasa  : is_staff=False, bukan anggota group apapun
    - Staff Desa   : is_staff=True  + group 'Staff Desa'
    - Nakes        : is_staff=True  + group 'Nakes'

    Satu akun bisa merangkap dua group sekaligus jika diperlukan
    (misal: staff desa yang juga bertugas di poskesdes).

    Optimasi: values_list() satu query, hasil langsung dicek pakai 'in'
    — lebih efisien daripada dua kali .filter().exists()
    """
    is_nakes      = False
    is_staff_desa = False

    if request.user.is_authenticated and request.user.is_staff:
        # Satu query untuk ambil semua nama group user ini
        groups = set(request.user.groups.values_list('name', flat=True))
        is_nakes      = 'Nakes'       in groups
        is_staff_desa = 'Staff Desa'  in groups

    return {
        'is_nakes'      : is_nakes,
        'is_staff_desa' : is_staff_desa,
    }