def format_teamfight_participation(participation: float) -> str:
    """
    Mengubah nilai teamfight_participation menjadi format persentase.
    
    :param participation: Nilai partisipasi teamfight (0.0 - 1.0)
    :return: String dengan format "X% teamfight"
    """
    if not (0.0 <= participation <= 1.0):
        raise ValueError("Nilai partisipation harus antara 0.0 hingga 1.0")
    
    percentage = round(participation * 100, 2)  # Konversi ke persen dengan 2 desimal
    return f"{percentage}% teamfight"