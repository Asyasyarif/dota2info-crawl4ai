import json
import jq

def build_filters(keys):
    """
    Mengubah list keys (misalnya: ["85", 100]) menjadi list filter jq.
    
    Args:
        keys (list): List key yang akan dikonversi.
        
    Returns:
        List filter jq dalam format string.
    """
    filters = []
    for key in keys:
        # Ubah key ke string, lalu buat filter dengan format .["key"]
        filters.append(f'.["{str(key)}"]')
    return filters

def query_json(file_path, jq_filter, first_result=False):
    """
    Fungsi utilitas untuk melakukan query pada file JSON menggunakan filter jq.
    
    Args:
        file_path (str): Lokasi file JSON.
        jq_filter (str): Filter jq untuk mengekstrak data.
        first_result (bool): Jika True, hanya mengembalikan hasil pertama.
        
    Returns:
        Hasil query.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        compiled = jq.compile(jq_filter)
        results = compiled.input(data).all()
        if first_result:
            return results[0] if results else None
        return results
    except Exception as e:
        raise Exception(f"Gagal melakukan query pada file JSON: {e}")

def search_json(file_path, keys):
    """
    Fungsi utilitas untuk melakukan pencarian dengan banyak key yang akan dikonversi 
    ke filter jq dan mengembalikan hasilnya dalam bentuk array.

    Args:
        file_path (str): Lokasi file JSON.
        keys (list): List key (sebagai string atau angka) yang akan dicari.

    Returns:
        List yang berisi hasil query untuk setiap key. Jika sebuah key tidak menghasilkan data,
        maka nilainya adalah None.
    """
    # Konversi keys menjadi filter jq
    jq_filters = build_filters(keys)

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        results = []
        for filter_jq in jq_filters:
            try:
                compiled = jq.compile(filter_jq)
                result = compiled.input(data).all()
                results.append(result if result else None)
            except Exception as inner_e:
                # Jika terjadi error pada salah satu filter, simpan pesan error
                results.append(f"Error pada filter {filter_jq}: {inner_e}")
        return results
    except Exception as e:
        raise Exception(f"Gagal melakukan pencarian pada file JSON: {e}")

def search_json_single(file_path, key):
    jq_filter = build_filters([key])[0]
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        try:
            compiled = jq.compile(jq_filter)
            result = compiled.input(data).all()
            return result[0] if result else None
        except Exception as inner_e:
            return f"Error pada filter {jq_filter}: {inner_e}"
    except Exception as e:
        raise Exception(f"Gagal melakukan pencarian single pada file JSON: {e}")

def find_hero_by_id(hero_id: int):
    file_path = 'sources/7.37e/heroes.json'
    keys = [hero_id]
    return search_json(file_path, keys)

def find_item_by_id_jq(item_id: int):
    file_path = 'sources/7.37e/items.json'
    jq_filter = f'.[] | select(.id == {item_id})'
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        compiled = jq.compile(jq_filter)
        result = compiled.input(data).all()
        return result[0] if result else None
    except Exception as e:
        raise Exception(f"Gagal mencari item dengan id {item_id}: {e}")

if __name__ == "__main__":

    file_path = 'sources/7.37e/heroes.json'
    keys = ["85", 100]

    try:
        search_results = search_json(file_path, keys)
        print("\nHasil pencarian dengan fungsi search_json:")
        for i, res in enumerate(search_results, start=1):
            print(f"Hasil untuk key {keys[i-1]}: {res}")
    except Exception as e:
        print(e)
