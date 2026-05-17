def user_role(request):
    """
    Inject variabel `is_nakes` ke semua template context.
    True jika user adalah staff atau anggota grup 'Nakes'.
    """
    is_nakes = False
    if request.user.is_authenticated:
        is_nakes = (
            request.user.is_staff
            or request.user.groups.filter(name='Nakes').exists()
        )
    return {'is_nakes': is_nakes}