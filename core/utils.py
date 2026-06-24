"""
core/utils.py - Rupiah formatting utilities
Simple dan straightforward
"""

def format_rupiah(nilai):
    """
    Convert integer ke rupiah string
    150000 → "Rp 150.000"
    """
    if not nilai:
        return "Rp 0"
    
    nilai = int(nilai)
    return f"Rp {nilai:,}".replace(",", ".")


def parse_rupiah(nilai):
    """
    Convert rupiah string ke integer
    "150.000" → 150000
    "Rp 150.000" → 150000
    "150000" → 150000
    
    Hanya ambil digit, hapus semua separator
    """
    # Jika sudah integer/float, return langsung
    if isinstance(nilai, (int, float)):
        return int(nilai)
    
    if not nilai:
        return 0
    
    # Convert ke string
    nilai = str(nilai).strip()
    
    # Hapus "Rp" prefix
    nilai = nilai.replace("Rp", "").strip()
    
    # Ambil hanya digit (remove titik, koma, space, dll)
    hanya_angka = ""
    for char in nilai:
        if char.isdigit():
            hanya_angka += char
    
    return int(hanya_angka) if hanya_angka else 0