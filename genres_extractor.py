
def load_genres(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        print(file)
        genres = [line.strip() for line in file if line.strip()]
    return genres

def extract_genre(question, genres):
    for genre in genres:
        if genre in question:
            return genre
    return None
    
def map_genre_to_code(extracted_genre):
    genre_to_code={
        '居酒屋':'G001',
        'ダイニングバー・バル':'G002',
        '創作料理':'G003',
        '和食':'G004',
        '洋食':'G005',
        'レストラン':'G006',
        'イタリアン':'G006',
        'フレンチ':'G006',
        'パスタ':'G006',
        'カフェ': 'G014',
        
    }
    
    return genre_to_code.get(extracted_genre)