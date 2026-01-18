from typing import Dict

def extract_pdf_data_dummy(pdf_path: str, curp: str) -> Dict:
    return {
        "curp": curp,
        "name": "John Doe",
        "last_name": "Doe",
        "mother_last_name": "Doe",
        "birth_date": "1990-01-01",
        "birth_place": "New York",
        "gender": "Male",
        "civil_status": "Single",
        "curp_type": "1",
        "curp_type_description": "1",
        "curp_type_description": "1",
    }