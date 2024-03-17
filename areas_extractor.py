
def load_areas(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        print(file)
        areas = [line.strip() for line in file if line.strip()]
    return areas

def extract_area(question, areas):
    for area in areas:
        if area in question:
            return area
    return None
    
def map_area_to_code(extracted_area):
    area_to_code={
        '東京':'Z011',
        '大阪':'Z023'
        
    }
    
    return area_to_code.get(extracted_area)