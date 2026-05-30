SERVICES_BY_CATEGORY = {
    "Peluquería": [
        "Alisado",
        "Secado",
        "Corte de cabello",
        "Tinte",
    ],
    "Hidratación": [
        "Hidratación capilar",
    ],
    "Manicura": [
        "Manicure semipermanente",
        "Manicure tradicional",
        "Pedicure semipermanente",
        "Pedicure tradicional",
    ],
    "Cejas": [
        "Depilación con cera",
        "Depilación con hilo",
        "Tinte con henna",
    ],
}

STYLIST_NAMES = {
    "Peluquería": [
        "María García",
        "Carmen Rodríguez",
        "Laura Martínez",
        "Ana López",
        "Isabel González",
        "Patricia Hernández",
        "Rosa Pérez",
        "Claudia Sánchez",
        "Juana Ramírez",
        "Daniela Flores",
        "Andrea Torres",
        "Sofía Díaz",
        "Valeria Cruz",
        "Paula Castillo",
        "Carolina Ortiz",
        "Gabriela Mora",
        "Natalia Reyes",
        "Fernanda Ríos",
        "Alejandra Vega",
        "Mariana Paredes",
    ],
    "Hidratación": [
        "Lucía Herrera",
        "Adriana Navarro",
        "Beatriz Campos",
    ],
    "Manicura": [
        "Sandra Ruiz",
        "Mónica Jiménez",
        "Patricia Vargas",
        "Lorena Mendoza",
        "Diana Castro",
        "Rocío Molina",
        "Elena Guerrero",
        "Viviana Aguilar",
        "Silvia Benítez",
        "Julia Rojas",
        "Cecilia Guerrero",
        "Angélica Rivera",
        "Liliana Medina",
        "Norma Fuentes",
        "Teresa León",
        "Blanca Córdova",
        "Esperanza Robles",
        "Miriam Delgado",
        "Karina Salazar",
        "Susana Ochoa",
    ],
    "Cejas": [
        "Gloria Ponce",
        "Alicia Esquivel",
        "Martha Acosta",
        "Pilar Valle",
        "Concepción Arellano",
    ],
}


def generar_estilistas():
    estilistas = {}
    idx = 0
    for categoria, nombres in STYLIST_NAMES.items():
        for nombre in nombres:
            idx += 1
            estilistas[idx] = {
                "id": idx,
                "nombre": nombre,
                "categoria": categoria,
                "ocupado": False,
                "cliente_actual": None,
                "servicio_actual": None,
            }
    return estilistas


def todos_los_servicios():
    result = []
    for categoria, servicios in SERVICES_BY_CATEGORY.items():
        for servicio in servicios:
            result.append((categoria, servicio))
    return result
