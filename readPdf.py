import re
import datetime
from datetime import datetime
from bson.objectid import ObjectId

def removerAcentos(cadena):
    lista_cars = [['Á','A'], ['É','E'], ['Í','I'], ['Ó','O'], ['Ú','U'], ['á','a'], ['é','e'], ['í','i'], ['ó','o'], ['ú','u']]
    for cars in lista_cars:
        cadena = re.sub(cars[0], cars[1], cadena)
    return cadena

states1 = {
    "Aguascalientes":{
        "_id" : ObjectId("5ae5abb59060ed36e3ca7ba0"),
        "name" : "Aguascalientes"
    },
    "Baja California":{ 
        "_id" : ObjectId("5ae5abb79060ed36e3ca7ba1"),
        "name" : "Baja California"
    },
    "Baja California Sur":{
        "_id" : ObjectId("5ae5abb99060ed36e3ca7ba2"),
        "name" : "Baja California Sur"
    },
    "Campeche":{
        "_id" : ObjectId("5ae5abba9060ed36e3ca7ba3"),
        "name" : "Campeche"
    },
    "Coahuila de Zaragoza":{
        "_id" : ObjectId("5ae5abbb9060ed36e3ca7ba4"),
        "name" : "Coahuila de Zaragoza"
    },
    "Colima":{
        "_id" : ObjectId("5ae5abbe9060ed36e3ca7ba5"),
        "name" : "Colima"
    },
    "Chiapas":{
        "_id" : ObjectId("5ae5abbf9060ed36e3ca7ba6"),
        "name" : "Chiapas"
    },
    "CHIHUAHUA":{
        "_id" : ObjectId("5ae5abc69060ed36e3ca7ba7"),
        "name" : "Chihuahua"
    },
    "CIUDAD DE MÉXICO":{
        "_id" : ObjectId("5ae5abb39060ed36e3ca7b9f"),
        "name" : "Ciudad de México"
    },
    "DISTRITO FEDERAL":{
        "_id" : ObjectId("5ae5abb39060ed36e3ca7b9f"),
        "name" : "Ciudad de México"
    },
    "DURANGO":{ 
        "_id" : ObjectId("5ae5abce9060ed36e3ca7ba8"),
        "name" : "Durango"
    },
    "GUANAJUATO":{
        "_id" : ObjectId("5ae5abd49060ed36e3ca7ba9"),
        "name" : "Guanajuato"
    },
    "GUERRERO":{
        "_id" : ObjectId("5ae5abdc9060ed36e3ca7baa"),
        "name" : "Guerrero"
    },
    "HIDALGO":{
        "_id" : ObjectId("5ae5abdf9060ed36e3ca7bab"),
        "name" : "Hidalgo"
    },
    "JALISCO":{
        "_id" : ObjectId("5ae5abe49060ed36e3ca7bac"),
        "name" : "Jalisco"
    },
    "ESTADO DE MÉXICO":{
        "_id" : ObjectId("5ae5abe89060ed36e3ca7bad"),
        "name" : "Estado de México"
    },
    "México":{
        "_id" : ObjectId("5ae5abe89060ed36e3ca7bad"),
        "name" : "Estado de México"
    },
    "MICHOACÁN DE OCAMPO":{
        "_id" : ObjectId("5ae5abee9060ed36e3ca7bae"),
        "name" : "Michoacán de Ocampo"
    },
    "MICHOACÁN":{
        "_id" : ObjectId("5ae5abee9060ed36e3ca7bae"),
        "name" : "Michoacán de Ocampo"
    },
    "Morelos":{
        "_id" : ObjectId("5ae5abfb9060ed36e3ca7baf"),
        "name" : "Morelos"
    },
    "Nayarit":{
        "_id" : ObjectId("5ae5abfd9060ed36e3ca7bb0"),
        "name" : "Nayarit"
    },
    "Nuevo León":{
        "_id" : ObjectId("5ae5abfe9060ed36e3ca7bb1"),
        "name" : "Nuevo León"
    },
    "Oaxaca":{
        "_id" : ObjectId("5ae5ac039060ed36e3ca7bb2"),
        "name" : "Oaxaca"
    },
    "Puebla":{ 
        "_id" : ObjectId("5ae5ac099060ed36e3ca7bb3"),
        "name" : "Puebla"
    },
     "Querétaro":{
        "_id" : ObjectId("5ae5ac0e9060ed36e3ca7bb4"),
        "name" : "Querétaro"
    },
    "Quintana Roo":{ 
        "_id" : ObjectId("5ae5ac119060ed36e3ca7bb5"),
        "name" : "Quintana Roo"
    },
    "San Luis Potosí": {
        "_id": ObjectId("5ae5ac129060ed36e3ca7bb6"),
        "name": "San Luis Potosí"
    },
    "Sinaloa":{
        "_id": ObjectId("5ae5ac179060ed36e3ca7bb7"),
        "name": "Sinaloa"
    },
    "Sonora":{
        "_id": ObjectId("5ae5ac1a9060ed36e3ca7bb8"),
        "name": "Sonora"
    },
    "Tabasco":{
        "_id": ObjectId("5ae5ac219060ed36e3ca7bb9"),
        "name": "Tabasco"
    },
    "Tamaulipas": {
        "_id": ObjectId("5ae5ac249060ed36e3ca7bba"),
        "name": "Tamaulipas"
    },
    "Tlaxcala": {
        "_id": ObjectId("5ae5ac269060ed36e3ca7bbb"),
        "name": "Tlaxcala"
    },
    "VERACRUZ DE IGNACIO DE LA LLAVE": {
        "_id": ObjectId("5ae5ac279060ed36e3ca7bbc"),
        "name": "Veracruz de Ignacio de la Llave"
    },
    "VERACRUZ": {
        "_id": ObjectId("5ae5ac279060ed36e3ca7bbc"),
        "name": "Veracruz de Ignacio de la Llave"
    },
    "Yucatán": {
        "_id": ObjectId("5ae5ac2f9060ed36e3ca7bbd"),
        "name": "Yucatán"
    },
    "Zacatecas": {
        "_id": ObjectId("5ae5ac309060ed36e3ca7bbe"),
        "name": "Zacatecas"
    },
    "NE": {
        "_id": None,
        "name": "Nacido En El Extranjero"
    },
    "": {
        "_id": None,
        "name": ""
    }
}

states_nombre_completo = {
    '': {'_id': None, 'name': ''},
    'MEXICO': {'_id': ObjectId('5ae5abe89060ed36e3ca7bad'), 'name': 'Estado de México'},
    'AGUASCALIENTES': {'_id': ObjectId('5ae5abb59060ed36e3ca7ba0'), 'name': 'Aguascalientes'},
    'BAJA CALIFORNIA': {'_id': ObjectId('5ae5abb79060ed36e3ca7ba1'), 'name': 'Baja California'},
    'BAJA CALIFORNIA SUR': {'_id': ObjectId('5ae5abb99060ed36e3ca7ba2'), 'name': 'Baja California Sur'},
    'CAMPECHE': {'_id': ObjectId('5ae5abba9060ed36e3ca7ba3'), 'name': 'Campeche'},
    'CHIAPAS': {'_id': ObjectId('5ae5abbf9060ed36e3ca7ba6'), 'name': 'Chiapas'},
    'CHIHUAHUA': {'_id': ObjectId('5ae5abc69060ed36e3ca7ba7'), 'name': 'Chihuahua'},
    'CIUDAD DE MEXICO': {'_id': ObjectId('5ae5abb39060ed36e3ca7b9f'), 'name': 'Ciudad de México'},
    'COAHUILA': {'_id': ObjectId('5ae5abbb9060ed36e3ca7ba4'), 'name': 'Coahuila de Zaragoza'},
    'COAHUILA DE ZARAGOZA': {'_id': ObjectId('5ae5abbb9060ed36e3ca7ba4'), 'name': 'Coahuila de Zaragoza'},
    'COLIMA': {'_id': ObjectId('5ae5abbe9060ed36e3ca7ba5'), 'name': 'Colima'},
    'DISTRITO FEDERAL': {'_id': ObjectId('5ae5abb39060ed36e3ca7b9f'), 'name': 'Ciudad de México'},
    'DURANGO': {'_id': ObjectId('5ae5abce9060ed36e3ca7ba8'), 'name': 'Durango'},
    'ESTADO DE MEXICO': {'_id': ObjectId('5ae5abe89060ed36e3ca7bad'), 'name': 'Estado de México'},
    'GUANAJUATO': {'_id': ObjectId('5ae5abd49060ed36e3ca7ba9'), 'name': 'Guanajuato'},
    'GUERRERO': {'_id': ObjectId('5ae5abdc9060ed36e3ca7baa'), 'name': 'Guerrero'},
    'HIDALGO': {'_id': ObjectId('5ae5abdf9060ed36e3ca7bab'), 'name': 'Hidalgo'},
    'JALISCO': {'_id': ObjectId('5ae5abe49060ed36e3ca7bac'), 'name': 'Jalisco'},
    'MICHOACAN DE OCAMPO': {'_id': ObjectId('5ae5abee9060ed36e3ca7bae'), 'name': 'Michoacán de Ocampo'},
    'MICHOACAN': {'_id': ObjectId('5ae5abee9060ed36e3ca7bae'), 'name': 'Michoacán de Ocampo'},
    'MORELOS': {'_id': ObjectId('5ae5abfb9060ed36e3ca7baf'), 'name': 'Morelos'},
    'NAYARIT': {'_id': ObjectId('5ae5abfd9060ed36e3ca7bb0'), 'name': 'Nayarit'},
    'NE': {'_id': None, 'name': 'Nacido En El Extranjero'},
    'NUEVO LEON': {'_id': ObjectId('5ae5abfe9060ed36e3ca7bb1'), 'name': 'Nuevo León'},
    'OAXACA': {'_id': ObjectId('5ae5ac039060ed36e3ca7bb2'), 'name': 'Oaxaca'},
    'PUEBLA': {'_id': ObjectId('5ae5ac099060ed36e3ca7bb3'), 'name': 'Puebla'},
    'QUERETARO': {'_id': ObjectId('5ae5ac0e9060ed36e3ca7bb4'), 'name': 'Querétaro'},
    'QUINTANA ROO': {'_id': ObjectId('5ae5ac119060ed36e3ca7bb5'), 'name': 'Quintana Roo'},
    'SAN LUIS POTOSI': {'_id': ObjectId('5ae5ac129060ed36e3ca7bb6'), 'name': 'San Luis Potosí'},
    'SINALOA': {'_id': ObjectId('5ae5ac179060ed36e3ca7bb7'), 'name': 'Sinaloa'},
    'SONORA': {'_id': ObjectId('5ae5ac1a9060ed36e3ca7bb8'), 'name': 'Sonora'},
    'TABASCO': {'_id': ObjectId('5ae5ac219060ed36e3ca7bb9'), 'name': 'Tabasco'},
    'TAMAULIPAS': {'_id': ObjectId('5ae5ac249060ed36e3ca7bba'), 'name': 'Tamaulipas'},
    'TLAXCALA': {'_id': ObjectId('5ae5ac269060ed36e3ca7bbb'), 'name': 'Tlaxcala'},
    'VERACRUZ DE IGNACIO DE LA LLAVE': {'_id': ObjectId('5ae5ac279060ed36e3ca7bbc'), 'name': 'Veracruz de Ignacio de la Llave'},
    'VERACRUZ': {'_id': ObjectId('5ae5ac279060ed36e3ca7bbc'), 'name': 'Veracruz de Ignacio de la Llave'},
    'YUCATAN': {'_id': ObjectId('5ae5ac2f9060ed36e3ca7bbd'), 'name': 'Yucatán'},
    'ZACATECAS': {'_id': ObjectId('5ae5ac309060ed36e3ca7bbe'), 'name': 'Zacatecas'}
}

states_abreviaciones = {
    "AGS": {"_id": ObjectId("5ae5abb59060ed36e3ca7ba0"), "name": "Aguascalientes"},
    "BCN": {"_id": ObjectId("5ae5abb79060ed36e3ca7ba1"), "name": "Baja California"},
    "BC": {"_id": ObjectId("5ae5abb79060ed36e3ca7ba1"), "name": "Baja California"},
    "BCS": {"_id": ObjectId("5ae5abb99060ed36e3ca7ba2"), "name": "Baja California Sur"},
    "CAM": {"_id": ObjectId("5ae5abba9060ed36e3ca7ba3"), "name": "Campeche"},
    "COA": {"_id": ObjectId("5ae5abbb9060ed36e3ca7ba4"), "name": "Coahuila de Zaragoza"},
    "COAH": {"_id": ObjectId("5ae5abbb9060ed36e3ca7ba4"), "name": "Coahuila de Zaragoza"},
    "COL": {"_id": ObjectId("5ae5abbe9060ed36e3ca7ba5"), "name": "Colima"},
    "CHS": {"_id": ObjectId("5ae5abbf9060ed36e3ca7ba6"), "name": "Chiapas"},
    "CHIS": {"_id": ObjectId("5ae5abbf9060ed36e3ca7ba6"), "name": "Chiapas"},
    "CHI": {"_id": ObjectId("5ae5abc69060ed36e3ca7ba7"), "name": "Chihuahua"},
    "CHIH": {"_id": ObjectId("5ae5abc69060ed36e3ca7ba7"), "name": "Chihuahua"},
    "CDMX": {"_id": ObjectId("5ae5abb39060ed36e3ca7b9f"), "name": "Ciudad de México"},
    "DGO": {"_id": ObjectId("5ae5abce9060ed36e3ca7ba8"), "name": "Durango"},
    "GTO": {"_id": ObjectId("5ae5abd49060ed36e3ca7ba9"), "name": "Guanajuato"},
    "GRO": {"_id": ObjectId("5ae5abdc9060ed36e3ca7baa"), "name": "Guerrero"},
    "HGO": {"_id": ObjectId("5ae5abdf9060ed36e3ca7bab"), "name": "Hidalgo"},
    "JAL": {"_id": ObjectId("5ae5abe49060ed36e3ca7bac"), "name": "Jalisco"},
    "EM": {"_id": ObjectId("5ae5abe89060ed36e3ca7bad"), "name": "Estado de México"},
    "MEX": {"_id": ObjectId("5ae5abe89060ed36e3ca7bad"), "name": "Estado de México"},
    "MICH": {"_id": ObjectId("5ae5abee9060ed36e3ca7bae"), "name": "Michoacán de Ocampo"},
    "MOR": {"_id": ObjectId("5ae5abfb9060ed36e3ca7baf"), "name": "Morelos"},
    "NAY": {"_id": ObjectId("5ae5abfd9060ed36e3ca7bb0"), "name": "Nayarit"},
    "NL": {"_id": ObjectId("5ae5abfe9060ed36e3ca7bb1"), "name": "Nuevo León"},
    "OAX": {"_id": ObjectId("5ae5ac039060ed36e3ca7bb2"), "name": "Oaxaca"},
    "PUE": {"_id": ObjectId("5ae5ac099060ed36e3ca7bb3"), "name": "Puebla"},
    "QRO": {"_id": ObjectId("5ae5ac0e9060ed36e3ca7bb4"), "name": "Querétaro"},
    "QROO": {"_id": ObjectId("5ae5ac119060ed36e3ca7bb5"), "name": "Quintana Roo"},
    "QR": {"_id": ObjectId("5ae5ac119060ed36e3ca7bb5"), "name": "Quintana Roo"},
    "SLP": {"_id": ObjectId("5ae5ac129060ed36e3ca7bb6"), "name": "San Luis Potosí"},
    "SIN": {"_id": ObjectId("5ae5ac179060ed36e3ca7bb7"), "name": "Sinaloa"},
    "SON": {"_id": ObjectId("5ae5ac1a9060ed36e3ca7bb8"), "name": "Sonora"},
    "TAB": {"_id": ObjectId("5ae5ac219060ed36e3ca7bb9"), "name": "Tabasco"},
    "TAM": {"_id": ObjectId("5ae5ac249060ed36e3ca7bba"), "name": "Tamaulipas"},
    "TLA": {"_id": ObjectId("5ae5ac269060ed36e3ca7bbb"), "name": "Tlaxcala"},
    "TLAX": {"_id": ObjectId("5ae5ac269060ed36e3ca7bbb"), "name": "Tlaxcala"},
    "VER": {"_id": ObjectId("5ae5ac279060ed36e3ca7bbc"), "name": "Veracruz de Ignacio de la Llave"},
    "YUC": {"_id": ObjectId("5ae5ac2f9060ed36e3ca7bbd"), "name": "Yucatán"},
    "ZAC": {"_id": ObjectId("5ae5ac309060ed36e3ca7bbe"), "name": "Zacatecas"},
    "NE": {"_id": None, "name": "Nacido En El Extranjero"},
    "AS": {"_id": ObjectId("5ae5abb59060ed36e3ca7ba0"), "name": "Aguascalientes"},
    "BS": {"_id": ObjectId("5ae5abb99060ed36e3ca7ba2"), "name": "Baja California Sur"},
    "CC": {"_id": ObjectId("5ae5abba9060ed36e3ca7ba3"), "name": "Campeche"},
    "CL": {"_id": ObjectId("5ae5abbb9060ed36e3ca7ba4"), "name": "Coahuila de Zaragoza"},
    "CM": {"_id": ObjectId("5ae5abbe9060ed36e3ca7ba5"), "name": "Colima"},
    "CS": {"_id": ObjectId("5ae5abbf9060ed36e3ca7ba6"), "name": "Chiapas"},
    "CH": {"_id": ObjectId("5ae5abc69060ed36e3ca7ba7"), "name": "Chihuahua"},
    "DF": {"_id": ObjectId("5ae5abb39060ed36e3ca7b9f"), "name": "Ciudad de México"},
    "DG": {"_id": ObjectId("5ae5abce9060ed36e3ca7ba8"), "name": "Durango"},
    "GT": {"_id": ObjectId("5ae5abd49060ed36e3ca7ba9"), "name": "Guanajuato"},
    "GR": {"_id": ObjectId("5ae5abdc9060ed36e3ca7baa"), "name": "Guerrero"},
    "HG": {"_id": ObjectId("5ae5abdf9060ed36e3ca7bab"), "name": "Hidalgo"},
    "JC": {"_id": ObjectId("5ae5abe49060ed36e3ca7bac"), "name": "Jalisco"},
    "MC": {"_id": ObjectId("5ae5abe89060ed36e3ca7bad"), "name": "Estado de México"},
    "MN": {"_id": ObjectId("5ae5abee9060ed36e3ca7bae"), "name": "Michoacán de Ocampo"},
    "MS": {"_id": ObjectId("5ae5abfb9060ed36e3ca7baf"), "name": "Morelos"},
    "NT": {"_id": ObjectId("5ae5abfd9060ed36e3ca7bb0"), "name": "Nayarit"},
    "OC": {"_id": ObjectId("5ae5ac039060ed36e3ca7bb2"), "name": "Oaxaca"},
    "PL": {"_id": ObjectId("5ae5ac099060ed36e3ca7bb3"), "name": "Puebla"},
    "QT": {"_id": ObjectId("5ae5ac0e9060ed36e3ca7bb4"), "name": "Querétaro"},
    "SP": {"_id": ObjectId("5ae5ac129060ed36e3ca7bb6"), "name": "San Luis Potosí"},
    "SL": {"_id": ObjectId("5ae5ac179060ed36e3ca7bb7"), "name": "Sinaloa"},
    "SR": {"_id": ObjectId("5ae5ac1a9060ed36e3ca7bb8"), "name": "Sonora"},
    "TC": {"_id": ObjectId("5ae5ac219060ed36e3ca7bb9"), "name": "Tabasco"},
    "TS": {"_id": ObjectId("5ae5ac249060ed36e3ca7bba"), "name": "Tamaulipas"},
    "TL": {"_id": ObjectId("5ae5ac269060ed36e3ca7bbb"), "name": "Tlaxcala"},
    "VZ": {"_id": ObjectId("5ae5ac279060ed36e3ca7bbc"), "name": "Veracruz de Ignacio de la Llave"},
    "YN": {"_id": ObjectId("5ae5ac2f9060ed36e3ca7bbd"), "name": "Yucatán"},
    "ZS": {"_id": ObjectId("5ae5ac309060ed36e3ca7bbe"), "name": "Zacatecas"}
}

states = {**states_abreviaciones, **states_nombre_completo}
states1 = {removerAcentos(key).upper(): value for key, value in states1.items()}

def corregirBasura(estado0):
    estado = removerAcentos(estado0).upper()
    lista_estados = list(states_nombre_completo.keys())
    res = ''
    for s in lista_estados[:]:
        if estado.find(s) != -1:
            res = s
    if res == '':
        res = estado0
    return res

def fixState(estado):
    estado = corregirBasura(estado)
    estado = states.get(estado, states.get(''))
    return estado

def parsero(enter):
    if "/" in enter:
        enter = enter.replace(' ', '')
        enter = enter.split('/')
        y = datetime(int(enter[2]), int(enter[1]), int(enter[0]))
    else:
        y = enter
    return y

def extract_total_weeks(full_text):
    """Extrae el total de semanas cotizadas del encabezado - VERSIÓN DEFINITIVA"""
    try:
        print("=== EXTRAYENDO TOTAL DE SEMANAS (TSC) ===")
        
        # Extraer las primeras líneas donde está el encabezado
        lines = full_text.split('\n')
        
        # MÉTODO 1: Buscar el patrón exacto del encabezado
        # El formato es siempre: número grande en el encabezado después de "Total de semanas cotizadas"
        print("\n--- MÉTODO 1: Buscar patrón del encabezado ---")
        
        for i, line in enumerate(lines[:40]):  # Solo buscar en las primeras 40 líneas
            if "Total de semanas cotizadas" in line:
                print(f"Encontrado 'Total de semanas cotizadas' en línea {i}: {line}")
                
                # Buscar en las siguientes líneas el número
                for j in range(i+1, min(len(lines), i+8)):
                    next_line = lines[j].strip()
                    print(f"  Revisando línea {j}: '{next_line}'")
                    
                    # Buscar línea que solo contenga un número
                    if re.match(r'^\s*(\d{1,4})\s*$', next_line):
                        total = int(next_line)
                        # Validar que sea un total válido (no fecha)
                        if 1 <= total <= 5000 and total != 2025 and total != 2024:
                            print(f"✓ Total encontrado: {total}")
                            return total
        
        # MÉTODO 2: Buscar en la cadena original del pie de página que siempre contiene el total
        print("\n--- MÉTODO 2: Buscar en cadena original ---")
        
        # Buscar el patrón de la cadena original que siempre tiene el formato:
        # "Número total de semanas cotizadas:XX"
        cadena_pattern = re.search(r'Número total de semanas cotizadas:(\d{1,4})', full_text)
        if cadena_pattern:
            total = int(cadena_pattern.group(1))
            print(f"✓ Total encontrado en cadena original: {total}")
            return total
        
        # MÉTODO 3: Buscar el patrón específico en el NSS/CURP/Total
        print("\n--- MÉTODO 3: Buscar patrón NSS/CURP/Total ---")
        
        # Buscar después de encontrar NSS y CURP
        nss_found = -1
        curp_found = -1
        
        for i, line in enumerate(lines[:30]):
            if "NSS:" in line:
                nss_found = i
                print(f"NSS encontrado en línea {i}")
            elif "CURP:" in line and nss_found != -1:
                curp_found = i
                print(f"CURP encontrado en línea {i}")
                
                # Buscar el número en las siguientes líneas
                for j in range(i+1, min(len(lines), i+6)):
                    check_line = lines[j].strip()
                    if re.match(r'^\s*(\d{1,4})\s*$', check_line):
                        total = int(check_line)
                        if 1 <= total <= 5000:
                            print(f"✓ Total encontrado después de CURP: {total}")
                            return total
                break
        
        # MÉTODO 4: Buscar números aislados en el encabezado excluyendo fechas
        print("\n--- MÉTODO 4: Búsqueda de números aislados ---")
        
        for i, line in enumerate(lines[:25]):
            line_clean = line.strip()
            if re.match(r'^\s*(\d{1,4})\s*$', line_clean):
                total = int(line_clean)
                print(f"Candidato en línea {i}: {total}")
                
                # Verificar que no sea fecha
                context_valid = True
                for k in range(max(0, i-2), min(len(lines), i+3)):
                    context_line = lines[k].lower()
                    if any(word in context_line for word in ['fecha', 'dd', 'mm', 'yyyy', '/', '2024', '2025']):
                        context_valid = False
                        break
                
                if context_valid and 1 <= total <= 5000:
                    # Verificar que esté en el contexto correcto (después de datos personales)
                    found_personal_data = False
                    for k in range(max(0, i-10), i):
                        if any(word in lines[k] for word in ['NSS:', 'CURP:', 'Total de semanas']):
                            found_personal_data = True
                            break
                    
                    if found_personal_data:
                        print(f"✓ Total encontrado por contexto: {total}")
                        return total
        
        print("⚠️ No se encontró el total de semanas")
        return 0
        
    except Exception as e:
        print(f"Error extrayendo total de semanas: {e}")
        return 0

def extract_weeks_detail(full_text):
    """Extrae el detalle de semanas de la tabla específica"""
    try:
        print("=== EXTRAYENDO DETALLE DE SEMANAS ===")
        
        lines = full_text.split('\n')
        
        # Buscar en la sección de la tabla
        in_detail_section = False
        
        for i, line in enumerate(lines):
            if "Tu detalle de semanas cotizadas" in line:
                in_detail_section = True
                print(f"Inicio de sección detalle en línea {i}")
                continue
            elif "Tu historia laboral" in line:
                print(f"Fin de sección detalle en línea {i}")
                break
            elif in_detail_section:
                # Buscar línea con exactamente 3 números
                line_clean = line.strip()
                if re.match(r'^\s*\d+\s+\d+\s+\d+\s*$', line_clean):
                    numbers = re.findall(r'\d+', line_clean)
                    if len(numbers) == 3:
                        try:
                            cotizadas = int(numbers[0])
                            descontadas = int(numbers[1]) 
                            reintegradas = int(numbers[2])
                            
                            print(f"Candidato línea {i}: '{line_clean}' -> {cotizadas}, {descontadas}, {reintegradas}")
                            
                            # Validar que tiene sentido
                            if (cotizadas >= descontadas >= reintegradas >= 0 and 
                                cotizadas <= 10000 and 
                                not (cotizadas <= 31 and descontadas <= 12 and reintegradas >= 2020)):
                                
                                print(f"✓ Detalle encontrado: {cotizadas}, {descontadas}, {reintegradas}")
                                return [cotizadas, descontadas, reintegradas]
                                
                        except ValueError:
                            continue
        
        print("⚠️ No se encontró el detalle de semanas")
        return [0, 0, 0]
        
    except Exception as e:
        print(f"Error extrayendo detalle de semanas: {e}")
        return [0, 0, 0]

def extract_movements_for_employer(full_text, employer_name, registro_patronal):
    """Extrae movimientos específicos para un empleador dado"""
    movimientos = []
    
    try:
        print(f"  Extrayendo movimientos para {employer_name}")
        
        # Encontrar la sección de este empleador
        # Buscar desde el nombre del empleador hasta el siguiente empleador o fin del documento
        employer_pattern = re.escape(employer_name)
        start_match = re.search(f"Nombre del patrón\\s+{employer_pattern}", full_text)
        
        if not start_match:
            print(f"  No se encontró sección para {employer_name}")
            return movimientos
            
        start_pos = start_match.end()
        
        # Encontrar el final de la sección (siguiente empleador o fin)
        next_employer_match = re.search(r"Nombre del patrón\s+", full_text[start_pos:])
        if next_employer_match:
            end_pos = start_pos + next_employer_match.start()
            employer_section = full_text[start_pos:end_pos]
        else:
            # Si no hay siguiente empleador, tomar hasta el final de los movimientos
            important_section = re.search(r"Importante", full_text[start_pos:])
            if important_section:
                end_pos = start_pos + important_section.start()
                employer_section = full_text[start_pos:end_pos]
            else:
                employer_section = full_text[start_pos:]
        
        print(f"  Sección del empleador encontrada: {len(employer_section)} caracteres")
        
        # Extraer movimientos usando regex
        movement_pattern = r'(MODIFICACION DE SALARIO|REINGRESO|BAJA|ALTA)\s+(\d{2}/\d{2}/\d{4})\s+\$\s*([\d,.]+)'
        movement_matches = re.finditer(movement_pattern, employer_section)
        
        for match in movement_matches:
            try:
                tipo = match.group(1).strip()
                fecha_str = match.group(2).strip()
                salario_str = match.group(3).strip()
                
                # Convertir fecha
                try:
                    fecha_movimiento = parsero(fecha_str)
                except:
                    fecha_movimiento = fecha_str
                
                # Convertir salario
                try:
                    scb = float(salario_str.replace(',', ''))
                except:
                    scb = 0.0
                
                movimiento = {
                    'tipo_movimiento': tipo,
                    'fecha_movimiento': fecha_movimiento,
                    'scb': scb
                }
                
                movimientos.append(movimiento)
                
            except Exception as e:
                print(f"  Error procesando movimiento: {e}")
                continue
        
        print(f"  ✓ {len(movimientos)} movimientos extraídos para {employer_name}")
        return movimientos
        
    except Exception as e:
        print(f"  Error extrayendo movimientos para {employer_name}: {e}")
        return movimientos

def extract_employers_from_text(full_text):
    """Extrae empleadores usando detección de patrones individuales para manejar interrupciones"""
    employers = []
    
    try:
        print("=== EXTRAYENDO EMPLEADORES ===")
        
        # Paso 1: Encontrar todas las ocurrencias de "Nombre del patrón"
        patron_names = []
        name_pattern = r'Nombre del patrón\s+([^\n\r]+?)(?=\s+Registro Patronal|\n|\r)'
        name_matches = re.finditer(name_pattern, full_text, re.DOTALL)
        for match in name_matches:
            patron_names.append(match.group(1).strip())
        
        print(f"Nombres de patrones encontrados: {patron_names}")
        
        # Paso 2: Encontrar todos los registros patronales
        registros = []
        registro_pattern = r'Registro Patronal\s+([A-Z0-9*]+)'
        registro_matches = re.finditer(registro_pattern, full_text)
        for match in registro_matches:
            registros.append(match.group(1).strip())
        
        print(f"Registros patronales encontrados: {registros}")
        
        # Paso 3: Encontrar estados
        estados = []
        estado_pattern = r'Entidad federativa\s+([A-ZÁÉÍÓÚÑ][^\n\r]+?)(?=\s+(?:Contacto:|Fecha de alta)|\n|\r)'
        estado_matches = re.finditer(estado_pattern, full_text, re.DOTALL)
        for match in estado_matches:
            estados.append(match.group(1).strip())
        
        print(f"Estados encontrados: {estados}")
        
        # Paso 4: Encontrar fechas de alta, baja y salarios
        fecha_salario_pattern = r'Fecha de alta\s+(\d{2}/\d{2}/\d{4})\s+Fecha de baja\s+(\d{2}/\d{2}/\d{4}|Vigente)\s+Salario Base de Cotización[^$]*\$\s*([\d,.]+)'
        fecha_salario_matches = list(re.finditer(fecha_salario_pattern, full_text, re.DOTALL))
        
        print(f"Fechas y salarios encontrados: {len(fecha_salario_matches)}")
        
        # Combinar la información
        min_items = min(len(patron_names), len(registros), len(estados), len(fecha_salario_matches))
        print(f"Número mínimo de elementos para combinar: {min_items}")
        
        for i in range(min_items):
            try:
                fecha_alta = fecha_salario_matches[i].group(1).strip()
                fecha_baja = fecha_salario_matches[i].group(2).strip() 
                salario_str = fecha_salario_matches[i].group(3).strip()
                
                print(f"Procesando empleador {i+1}: {patron_names[i]}")
                
                # Procesar salario
                try:
                    salario = float(salario_str.replace(',', ''))
                except:
                    salario = 0.0
                
                # Procesar fechas
                try:
                    fa = parsero(fecha_alta)
                except:
                    fa = fecha_alta
                
                if fecha_baja == "Vigente":
                    fb = "Vigente"
                else:
                    try:
                        fb = parsero(fecha_baja)
                    except:
                        fb = fecha_baja
                
                # Extraer movimientos para este empleador
                movimientos = extract_movements_for_employer(full_text, patron_names[i], registros[i])
                
                employer = {
                    'p': patron_names[i],
                    'rp': registros[i],
                    'state': fixState(estados[i]),
                    'fa': fa,
                    'fb': fb,
                    'sbc': salario,
                    'movimientos': movimientos
                }
                
                employers.append(employer)
                print(f"✓ Empleador agregado: {patron_names[i]} con {len(movimientos)} movimientos")
                
            except Exception as e:
                print(f"Error procesando empleador {i+1}: {e}")
                continue
        
        print(f"Total empleadores extraídos: {len(employers)}")
        return employers
        
    except Exception as e:
        print(f"Error en extract_employers_from_text: {e}")
        return []
    
# def extract_basic_info(full_text):
#     """Extrae información básica del PDF"""
#     try:
#         print("=== EXTRAYENDO INFORMACIÓN BÁSICA ===")
        
#         nss_real = ''
#         curp_sc = ''
#         nombre = ''
        
#         # Buscar NSS
#         nss_match = re.search(r"NSS:\s*([0-9]{10,11})", full_text)
#         if nss_match:
#             nss_real = nss_match.group(1).strip()
#             print(f"NSS encontrado: {nss_real}")
        
#         # Buscar CURP
#         curp_match = re.search(r"CURP:\s*([A-Z0-9]{18})", full_text)
#         if curp_match:
#             curp_sc = curp_match.group(1).strip()
#             print(f"CURP encontrado: {curp_sc}")
        
#         # Buscar nombre: la línea después de "Estimado(a),"
#         lines = full_text.split('\n')
#         for i, line in enumerate(lines):
#             if "Estimado(a)," in line:
#                 if i+1 < len(lines):
#                     nombre = lines[i+1].strip()
#                     # Limpiar posibles residuos (solo letras y espacios)
#                     nombre = re.sub(r'[^A-ZÁÉÍÓÚÑ\s]', '', nombre)
#                     nombre = re.sub(r'\s+', ' ', nombre).strip()
#                     # Eliminar palabras sueltas como "DD" al final
#                     nombre = re.sub(r'\bDD\b$', '', nombre).strip()
#                     print(f"Nombre encontrado: '{nombre}'")
#                 break
        
#         return nss_real, curp_sc, nombre
        
#     except Exception as e:
#         print(f"Error extrayendo información básica: {e}")
#         return '', '', ''

def extract_basic_info(full_text):
    """Extrae información básica del PDF"""
    try:
        print("=== EXTRAYENDO INFORMACIÓN BÁSICA ===")
        
        nss_real = ''
        curp_sc = ''
        nombre = ''
        
        # Buscar NSS
        nss_match = re.search(r"NSS:\s*([0-9]{10,11})", full_text)
        if nss_match:
            nss_real = nss_match.group(1).strip()
            print(f"NSS encontrado: {nss_real}")
        
        # Buscar CURP
        curp_match = re.search(r"CURP:\s*([A-Z0-9]{18})", full_text)
        if curp_match:
            curp_sc = curp_match.group(1).strip()
            print(f"CURP encontrado: {curp_sc}")
        
        # Buscar nombre
        nombre_patterns = [
            r"NSS:\s*[0-9]+\s*([A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ\s]+?)(?=\s*CURP)",
            r"([A-ZÁÉÍÓÚÑ]{2,}\s+[A-ZÁÉÍÓÚÑ]{2,}\s+[A-ZÁÉÍÓÚÑ]{2,}(?:\s+[A-ZÁÉÍÓÚÑ]{2,})?)"
        ]
        
        for pattern in nombre_patterns:
            nombre_matches = re.finditer(pattern, full_text)
            for nombre_match in nombre_matches:
                potential_name = nombre_match.group(1).strip()
                
                # Limpiar nombre
                unwanted_texts = [
                    "DD MM YYYY", "Tu detalle de semanas cotizadas", "NSS:", "CURP:", 
                    "Total de semanas cotizadas", "Instituto Mexicano del Seguro Social"
                ]
                
                for unwanted in unwanted_texts:
                    potential_name = potential_name.replace(unwanted, "")
                
                potential_name = re.sub(r'\s+', ' ', potential_name).strip()
                
                potential_name = re.sub(r'\bDD\b.*$', '', potential_name).strip()
                # Verificar que el nombre tiene sentido
                if (len(potential_name) > 5 and 
                    len(potential_name) < 100 and
                    not re.search(r'\d', potential_name) and
                    len(potential_name.split()) >= 2):
                    
                    nombre = potential_name
                    print(f"Nombre encontrado: {nombre}")
                    break
            
            if nombre:
                break
        
        return nss_real, curp_sc, nombre
        
    except Exception as e:
        print(f"Error extrayendo información básica: {e}")
        return '', '', ''

def detect_pdf_format(full_text, tables):
    """
    Detecta si el PDF tiene campos de movimientos o no
    Retorna: 'simple' o 'with_movements'
    """
    try:
        print("=== DETECTANDO FORMATO DE PDF ===")
        
        # Detectores más específicos para movimientos reales
        strong_movement_indicators = [
            "Tipo de movimiento",
            "Fecha de movimiento"
        ]
        
        # Detectores de formato simple (sin movimientos detallados)
        simple_format_indicators = [
            "historial de registros afiliatorios",
            "Tu detalle de semanas cotizadas"
        ]
        
        # Primero verificar indicadores fuertes de movimientos
        has_strong_movements = any(indicator in full_text for indicator in strong_movement_indicators)
        print(f"Indicadores fuertes de movimiento: {has_strong_movements}")
        
        # Verificar indicadores de formato simple
        has_simple_indicators = any(indicator in full_text for indicator in simple_format_indicators)
        print(f"Indicadores de formato simple: {has_simple_indicators}")
        
        # Analizar número de tablas como indicador adicional (no definitivo)
        table_count = len(tables) if tables else 0
        print(f"Número de tablas: {table_count}")
        
        # Detectar por contenido de tablas más específico
        tables_have_movements = False
        if tables:
            for table in tables:
                if table and len(table) > 3:  # Buscar en tablas con contenido sustancial
                    table_text = str(table).lower()
                    if any(indicator.lower() in table_text for indicator in strong_movement_indicators):
                        tables_have_movements = True
                        break
        
        print(f"Tablas contienen movimientos: {tables_have_movements}")
        
        # Lógica de decisión mejorada - NO usar table_count como criterio fijo
        if has_strong_movements and tables_have_movements:
            # Ambos indicadores fuertes presentes
            format_type = 'with_movements'
        elif has_strong_movements and not has_simple_indicators:
            # Solo indicadores de movimiento, sin indicadores simples
            format_type = 'with_movements'
        elif has_simple_indicators and not has_strong_movements:
            # Solo indicadores simples, sin movimientos fuertes
            format_type = 'simple'
        elif has_simple_indicators and has_strong_movements:
            # Ambos presentes - verificar contenido de tablas para decidir
            format_type = 'with_movements' if tables_have_movements else 'simple'
        else:
            # Fallback: si no hay indicadores claros, usar formato simple por defecto
            format_type = 'simple'
        
        print(f"✓ Formato detectado: {format_type}")
        print(f"  - Criterios: movimientos_fuertes={has_strong_movements}, tablas={table_count}, simple_indicators={has_simple_indicators}")
        
        return format_type
        
    except Exception as e:
        print(f"Error detectando formato: {e}")
        return 'simple'  # Por defecto usar formato simple

def process_simple_format(pdf):
    """Procesa PDFs en formato simplificado (sin movimientos)"""
    try:
        print("\n=== PROCESANDO FORMATO SIMPLE ===")
        
        # Extraer todo el texto del PDF
        full_text = ""
        for page in pdf.pages:
            try:
                page_text = page.extract_text()
                if page_text:
                    full_text += page_text + "\n"
            except Exception as e:
                print(f"Error extrayendo página: {e}")
                continue
        
        print(f"Texto extraído: {len(full_text)} caracteres")
        
        # Extraer información básica
        nss_real, curp_sc, nombre = extract_basic_info(full_text)
        print(f"Nombre crudo extraído: '{nombre}'")
        
        # Extraer detalle de semanas
        detalle_semanas = extract_weeks_detail(full_text)
        
        # Extraer total de semanas (TSC)
        total_semanas = extract_total_weeks(full_text)
        
        print(f"=== RESUMEN FORMATO SIMPLE ===")
        print(f"NSS: {nss_real}")
        print(f"CURP: {curp_sc}")
        print(f"Nombre: {nombre}")
        print(f"TSC (Total): {total_semanas}")
        print(f"Detalle - Cotizadas: {detalle_semanas[0]}, Descontadas: {detalle_semanas[1]}, Reintegradas: {detalle_semanas[2]}")
        
        # Extraer empleadores
        employers = extract_employers_from_text(full_text)
        print(f"Empleadores: {len(employers)}")
        
        # Generar nombres alternativos
        nombres_field = nombre
        if nombre:
            partes = nombre.split()
            if len(partes) >= 3:
                nombres_field = f"{partes[-1]} {' '.join(partes[:-1])}"
        
        # Estructura final
        s_c = {
            "Nombre": nombre,
            "Nombres": nombres_field,
            "created_at": datetime.now(),
            "curp_sc": [curp_sc] if curp_sc else [],
            "detalle_semanas": {
                'semanas_cotizadas': detalle_semanas[0],
                'semanas_descontadas': detalle_semanas[1], 
                'semanas_reintegradas': detalle_semanas[2]
            },
            "device": "",
            "job_cotizations": employers,
            "nss_final": nss_real,
            "nss_real": [nss_real] if nss_real else [],
            "rw_data": {
                "browser-scraper": "Para continuar con su trámite le hemos enviado una liga de confirmación a su correo electrónico",
                "requests-scraper": "",
                "e-visor": "",
                "app-requests-scraper": ""
            },
            "source": "browser-web",
            "tsc": total_semanas
        }
        
        return s_c
        
    except Exception as e:
        print(f"Error en process_simple_format: {e}")
        import traceback
        traceback.print_exc()
        return None

def old_job_cotizations(tables):
    """Procesa trabajos con movimientos (formato antiguo)"""
    guardar_si=['Nombre del patrón','Esta constancia presenta el número de semanas que has cotizado durante tu vida laboral, registradas en el IMSS. Además, esta constancia','Importante']
    job_cotizations=[]
    movimientos=[]
    info={}
    movimientosIter = False

    iterObject = list(range(len(tables)))
    for i in iterObject:

        if 'Estimado(a)' in tables[i][0]:
            for _ in range(5):  # Remover 5 elementos
                if i < len(iterObject):
                    iterObject.pop(i)
            continue

        if any(string in tables[i][0] for string in guardar_si) and movimientosIter:
            movimientosIter = False
            info['movimientos']=movimientos
            job_cotizations.append(info)
            info={}
            movimientos=[]

        if movimientosIter and not 'Tipo de movimiento' in tables[i][0]:
            try:
                movimientos.append({
                    'tipo_movimiento':"REINGRESO" if tables[i][0]=="ALTA" else tables[i][0],
                    'fecha_movimiento':parsero(tables[i][1]),
                    'scb':float(tables[i][2].split(" ")[1])
                })
            except:
                pass

        if tables[i][0] == 'Nombre del patrón':
            try:
                info['p']=tables[i][1]
                info['rp']=tables[i+1][1]
                info['state']= fixState(tables[i+2][1])
                info['fa']=parsero(tables[i+3][1])
                info['fb']=parsero(tables[i+3][3])
                info['sbc']=float(tables[i+3][5].split(" ")[1])
                info['dependencia']='IMSS'
            except:
                pass

        elif tables[i][0]=='Tipo de movimiento' or movimientosIter:
            movimientosIter = True

    return job_cotizations

def job_cotizations_with_movements(tables):
    """Procesa trabajos con movimientos (formato nuevo)"""
    table_headers = ['Nombre del patrón','Esta constancia presenta el número de semanas que has cotizado durante tu vida laboral, registradas en el IMSS. Además, esta constancia','Importante']
    job_cotizations=[]
    iter_movimiento = False

    for i, table in enumerate(tables):
        if any(header in table[0] for header in table_headers):
            iter_movimiento = False
        if 'Nombre del patrón' in table[0]:
            try:
                job_cotizations.append({
                    'p': tables[i+0][1],
                    'rp': tables[i+1][1],
                    'state': fixState(tables[i+2][1]),
                    'fa': parsero(tables[i+3][1]),
                    'fb': parsero(tables[i+3][3]),
                    'sbc': float(tables[i+3][5].split(" ")[1]),
                    'movimientos': []
                })
            except:
                try:
                    job_cotizations.append({
                        'p': tables[i+0][1],
                        'rp': tables[i+1][1],
                        'state': '',
                        'fa': parsero(tables[i+2][1]),
                        'fb': parsero(tables[i+2][3]),
                        'sbc': float(tables[i+2][5].split(" ")[1]),
                        'movimientos': []
                    })
                except:
                    pass

            iter_movimiento = False
        if 'Tipo de movimiento' in table[0] and 'Tipo de movimiento' not in tables[i+1][0]:
            iter_movimiento = True
        else:
            if iter_movimiento and len(job_cotizations) > 0:
                if len(table) >= 3 and table[1] is not None:
                    try:
                        job_cotizations[-1]['movimientos'].append({
                            'tipo_movimiento': "REINGRESO" if table[0]=="ALTA" else table[0],
                            'fecha_movimiento':parsero(table[1]),
                            'scb':float(table[2].split(" ")[1])
                        })
                    except:
                        pass

    return job_cotizations

def process_with_movements_format(pdf):
    """Procesa PDFs con formato que incluye movimientos"""
    try:
        print("\n=== PROCESANDO FORMATO CON MOVIMIENTOS ===")
        
        # Extraer tablas y texto
        tables = []
        full_text = ""
        
        for page in pdf.pages:
            try:
                # Extraer tablas
                page_tables = page.extract_tables(table_settings={})
                if page_tables:
                    for table in page_tables:
                        for row in table:
                            if row and not 'Instituto Mexicano del Seguro Social' in str(row[0]):
                                tables.append(row)
                
                # Extraer texto
                page_text = page.extract_text()
                if page_text:
                    full_text += page_text + "\n"
                    
            except Exception as e:
                print(f"Error extrayendo página: {e}")
                continue
        
        print(f"Tablas extraídas: {len(tables)}")
        print(f"Texto extraído: {len(full_text)} caracteres")
        
        # Extraer NSS y CURP del texto
        nss_real = ''
        curp_sc = ''
        
        if "nss" in full_text.lower():
            try:
                nss_match = re.search(r"NSS:\s*([0-9]{10,12})", full_text)
                if nss_match:
                    nss_real = nss_match.group(1).strip()
                    print(f"NSS encontrado: {nss_real}")
            except:
                pass
                
        if "curp" in full_text.lower():
            try:
                curp_match = re.search(r"CURP:\s*([A-Z0-9]{18})", full_text)
                if curp_match:
                    curp_sc = curp_match.group(1).strip()
                    print(f"CURP encontrado: {curp_sc}")
            except:
                pass
        
        # Procesar trabajos usando la extracción mejorada de texto (más confiable que tablas)
        jobs = extract_employers_from_text(full_text)
        print(f"Trabajos procesados: {len(jobs)}")
        
        # Extraer detalle de semanas de las tablas
        detalle_semanas = [0, 0, 0]
        try:
            # Buscar en las primeras tablas el detalle de semanas
            for i, row in enumerate(tables[:15]):  # Buscar en las primeras 15 filas
                if row and len(row) > 0:
                    for j, cell in enumerate(row):
                        if cell and 'IMSS' in str(cell):
                            try:
                                if i+1 < len(tables) and len(tables[i+1]) > j:
                                    detalle_semanas[0] = int(tables[i+1][j])
                            except:
                                pass
                        elif cell and 'Descontadas' in str(cell):
                            try:
                                if i+1 < len(tables) and len(tables[i+1]) > j:
                                    detalle_semanas[1] = int(tables[i+1][j])
                            except:
                                pass
                        elif cell and 'Reintegradas' in str(cell):
                            try:
                                if i+1 < len(tables) and len(tables[i+1]) > j:
                                    detalle_semanas[2] = int(tables[i+1][j])
                            except:
                                pass
        except Exception as e:
            print(f"Error extrayendo detalle de semanas: {e}")
        
        # Extraer nombre
        nombre = ''
        try:
            for i in range(len(tables)):
                if tables[i] and len(tables[i]) > 0:
                    if tables[i][0] and str(tables[i][0]) == 'Estimado(a),':
                        if i+1 < len(tables) and tables[i+1] and len(tables[i+1]) > 0:
                            nombre = str(tables[i+1][0])
                            break
        except Exception as e:
            print(f"Error extrayendo nombre: {e}")
        
        print(f"=== RESUMEN FORMATO CON MOVIMIENTOS ===")
        print(f"NSS: {nss_real}")
        print(f"CURP: {curp_sc}")
        print(f"Nombre: {nombre}")
        print(f"Detalle - Cotizadas: {detalle_semanas[0]}, Descontadas: {detalle_semanas[1]}, Reintegradas: {detalle_semanas[2]}")
        
        # Calcular TSC
        tsc = detalle_semanas[0] - detalle_semanas[1] + detalle_semanas[2]
        
        # Generar nombres alternativos
        nombres_field = nombre
        if nombre:
            partes = nombre.split()
            if len(partes) >= 3:
                nombres_field = f"{partes[-1]} {' '.join(partes[:-1])}"
        
        # Estructura final
        s_c = {
            "Nombre": nombre,
            "Nombres": nombres_field,
            "created_at": datetime.now(),
            "curp_sc": [curp_sc] if curp_sc else [],
            "detalle_semanas": {
                'semanas_cotizadas': detalle_semanas[0],
                'semanas_descontadas': detalle_semanas[1], 
                'semanas_reintegradas': detalle_semanas[2]
            },
            "device": "",
            "job_cotizations": jobs,
            "nss_final": nss_real,
            "nss_real": [nss_real] if nss_real else [],
            "rw_data": {
                "browser-scraper": "Para continuar con su trámite le hemos enviado una liga de confirmación a su correo electrónico",
                "requests-scraper": "",
                "e-visor": "",
                "app-requests-scraper": ""
            },
            "source": "browser-web",
            "tsc": tsc
        }
        
        return s_c
        
    except Exception as e:
        print(f"Error en process_with_movements_format: {e}")
        import traceback
        traceback.print_exc()
        return None

def leyendopdf(pdf):
    """Función principal que detecta el formato y procesa en consecuencia"""
    try:
        print("=== INICIANDO PROCESAMIENTO PDF UNIFICADO ===")
        
        # Extraer texto completo para detección
        full_text = ""
        tables = []
        
        try:
            for page in pdf.pages:
                # Extraer texto
                page_text = page.extract_text()
                if page_text:
                    full_text += page_text + "\n"
                
                # Extraer tablas básicas para detección
                try:
                    page_tables = page.extract_tables(table_settings={})
                    if page_tables:
                        tables.extend(page_tables)
                except:
                    pass
                    
        except Exception as e:
            print(f"Error en extracción inicial: {e}")
        
        # Detectar formato
        format_type = detect_pdf_format(full_text, tables)
        
        # Procesar según el formato detectado
        if format_type == 'simple':
            print("🔄 Usando procesamiento SIMPLE (sin movimientos)")
            result = process_simple_format(pdf)
        else:
            print("🔄 Usando procesamiento CON MOVIMIENTOS")
            result = process_with_movements_format(pdf)
        
        if result:
            print("\n=== PROCESAMIENTO EXITOSO ===")
            print(f"Formato: {format_type}")
            print(f"Nombre: {result.get('Nombre', 'N/A')}")
            print(f"CURP: {result.get('curp_sc', ['N/A'])[0] if result.get('curp_sc') else 'N/A'}")
            print(f"NSS: {result.get('nss_final', 'N/A')}")
            print(f"TSC: {result.get('tsc', 'N/A')}")
            print(f"Empleadores: {len(result.get('job_cotizations', []))}")
            print(f"Detalle - Cotizadas: {result.get('detalle_semanas', {}).get('semanas_cotizadas', 'N/A')}")
            print(f"Detalle - Descontadas: {result.get('detalle_semanas', {}).get('semanas_descontadas', 'N/A')}")
            print(f"Detalle - Reintegradas: {result.get('detalle_semanas', {}).get('semanas_reintegradas', 'N/A')}")
        
        return result
   
    except Exception as e:
        print(f"Error procesando PDF: {e}")
        import traceback
        traceback.print_exc()
        return None