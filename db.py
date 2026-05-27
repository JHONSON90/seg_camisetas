import os
from datetime import datetime

# def _get_st():
#     """Lazy-loads streamlit only when running inside a Streamlit server context."""
#     try:
#         import streamlit as st
#         return st
#     except Exception:
#         return None

# # We wrap gspread imports in try-except to avoid crash during installations
# try:
#     import gspread
#     from google.oauth2.service_account import Credentials
#     GS_AVAILABLE = True
# except ImportError:
#     GS_AVAILABLE = False

# DEFAULT_PRODUCTS = [
#     {
#         "id": "prod_1",
#         "name": "Camiseta Classic White",
#         "price": 20.0,
#         "description": "Camiseta de algodón pima 100% premium en color blanco clásico.",
#         "stock_by_store": {
#             "Tienda Principal": 45,
#             "Sucursal Norte": 20,
#             "Sucursal Sur": 15,
#             "Almacén Central": 120
#         }
#     },
#     {
#         "id": "prod_2",
#         "name": "Camiseta Obsidian Black",
#         "price": 28.0,
#         "description": "Camiseta de corte moderno color negro obsidiana mate de alta durabilidad.",
#         "stock_by_store": {
#             "Tienda Principal": 30,
#             "Sucursal Norte": 25,
#             "Sucursal Sur": 10,
#             "Almacén Central": 90
#         }
#     },
#     {
#         "id": "prod_3",
#         "name": "Camiseta Ocean Blue",
#         "price": 26.0,
#         "description": "Camiseta transpirable en azul océano con costuras reforzadas.",
#         "stock_by_store": {
#             "Tienda Principal": 15,
#             "Sucursal Norte": 12,
#             "Sucursal Sur": 8,
#             "Almacén Central": 60
#         }
#     },
#     {
#         "id": "prod_4",
#         "name": "Camiseta Crimson Red",
#         "price": 30.0,
#         "description": "Edición especial en color rojo carmesí con estampado minimalista.",
#         "stock_by_store": {
#             "Tienda Principal": 10,
#             "Sucursal Norte": 5,
#             "Sucursal Sur": 15,
#             "Almacén Central": 40
#         }
#     },
#     {
#         "id": "prod_5",
#         "name": "Camiseta Forest Green",
#         "price": 27.0,
#         "description": "Camiseta ecológica hecha de algodón orgánico y fibra de bambú color verde bosque.",
#         "stock_by_store": {
#             "Tienda Principal": 22,
#             "Sucursal Norte": 18,
#             "Sucursal Sur": 12,
#             "Almacén Central": 80
#         }
#     }
# ]

# DEFAULT_SALES = [
#     {
#         "id": "sale_1001",
#         "date": "2026-05-20",
#         "product_id": "prod_1",
#         "product_name": "Camiseta Classic White",
#         "quantity": 2,
#         "price": 20.0,
#         "total_amount": 40.0,
#         "amount_paid": 40.0,
#         "client_name": "Juan Pérez",
#         "client_contact": "juan.perez@email.com",
#         "store": "Tienda Principal"
#     },
#     {
#         "id": "sale_1002",
#         "date": "2026-05-22",
#         "product_id": "prod_2",
#         "product_name": "Camiseta Obsidian Black",
#         "quantity": 1,
#         "price": 28.0,
#         "total_amount": 28.0,
#         "amount_paid": 10.0,
#         "client_name": "María Gómez",
#         "client_contact": "+57 312 345 6789",
#         "store": "Sucursal Norte"
#     },
#     {
#         "id": "sale_1003",
#         "date": "2026-05-23",
#         "product_id": "prod_3",
#         "product_name": "Camiseta Ocean Blue",
#         "quantity": 3,
#         "price": 26.0,
#         "total_amount": 78.0,
#         "amount_paid": 40.0,
#         "client_name": "Carlos Rodríguez",
#         "client_contact": "+57 300 987 6543",
#         "store": "Sucursal Sur"
#     },
#     {
#         "id": "sale_1004",
#         "date": "2026-05-24",
#         "product_id": "prod_4",
#         "product_name": "Camiseta Crimson Red",
#         "quantity": 1,
#         "price": 30.0,
#         "total_amount": 30.0,
#         "amount_paid": 30.0,
#         "client_name": "Ana Martínez",
#         "client_contact": "ana.mtz@email.com",
#         "store": "Tienda Principal"
#     },
#     {
#         "id": "sale_1005",
#         "date": "2026-05-25",
#         "product_id": "prod_5",
#         "product_name": "Camiseta Forest Green",
#         "quantity": 2,
#         "price": 27.0,
#         "total_amount": 54.0,
#         "amount_paid": 0.0,
#         "client_name": "Luis Hernández",
#         "client_contact": "+57 315 555 4433",
#         "store": "Tienda Principal"
#     },
#     {
#         "id": "sale_1006",
#         "date": "2026-05-25",
#         "product_id": "prod_1",
#         "product_name": "Camiseta Classic White",
#         "quantity": 1,
#         "price": 20.0,
#         "total_amount": 20.0,
#         "amount_paid": 20.0,
#         "client_name": "Sofía Castro",
#         "client_contact": "sofia.castro@email.com",
#         "store": "Sucursal Norte"
#     }
# ]

# DEFAULT_STORES = [
#     "Tienda Principal",
#     "Sucursal Norte",
#     "Sucursal Sur",
#     "Almacén Central"
# ]

from streamlit_gsheets import GSheetsConnection

def get_connection():
    conn = GSheetsConnection("gsheets", type=GSheetsConnection)
    return conn


def init_db(force=False):
    """Fallback compatibility function for database initialization."""
    if check_credentials_exist():
        return init_google_sheets(force=force)
    return False

def init_google_sheets(force=False):
    """Initializes the worksheets (Productos, Ventas, Tiendas) in the Google Sheet if they do not exist."""
    if not check_credentials_exist():
        return False
        
    try:
        sh = get_spreadsheet()
        
        # 1. Initialize "Productos" worksheet
        try:
            ws_prod = sh.worksheet("Productos")
            if force:
                sh.del_worksheet(ws_prod)
                raise gspread.exceptions.WorksheetNotFound()
        except gspread.exceptions.WorksheetNotFound:
            ws_prod = sh.add_worksheet(title="Productos", rows=100, cols=20)
            headers = ["id", "name", "price", "description", "Tienda Principal", "Sucursal Norte", "Sucursal Sur", "Almacén Central"]
            ws_prod.append_row(headers)
            # Add initial products
            for p in DEFAULT_PRODUCTS:
                ws_prod.append_row([
                    p["id"],
                    p["name"],
                    p["price"],
                    p["description"],
                    p["stock_by_store"]["Tienda Principal"],
                    p["stock_by_store"]["Sucursal Norte"],
                    p["stock_by_store"]["Sucursal Sur"],
                    p["stock_by_store"]["Almacén Central"]
                ])
                
        # 2. Initialize "Ventas" worksheet
        try:
            ws_sales = sh.worksheet("Ventas")
            if force:
                sh.del_worksheet(ws_sales)
                raise gspread.exceptions.WorksheetNotFound()
        except gspread.exceptions.WorksheetNotFound:
            ws_sales = sh.add_worksheet(title="Ventas", rows=1000, cols=20)
            headers = ["id", "date", "product_id", "product_name", "quantity", "price", "total_amount", "amount_paid", "client_name", "client_contact", "store"]
            ws_sales.append_row(headers)
            for s in DEFAULT_SALES:
                ws_sales.append_row([
                    s["id"],
                    s["date"],
                    s["product_id"],
                    s["product_name"],
                    s["quantity"],
                    s["price"],
                    s["total_amount"],
                    s["amount_paid"],
                    s["client_name"],
                    s["client_contact"],
                    s["store"]
                ])
                
        # 3. Initialize "Tiendas" worksheet
        try:
            ws_stores = sh.worksheet("Tiendas")
            if force:
                sh.del_worksheet(ws_stores)
                raise gspread.exceptions.WorksheetNotFound()
        except gspread.exceptions.WorksheetNotFound:
            ws_stores = sh.add_worksheet(title="Tiendas", rows=20, cols=5)
            headers = ["name"]
            ws_stores.append_row(headers)
            for store in DEFAULT_STORES:
                ws_stores.append_row([store])
                
        # Try to delete the default "Sheet1" if it exists and we created other sheets
        try:
            default_sheet = sh.worksheet("Sheet1")
            sh.del_worksheet(default_sheet)
        except:
            try:
                default_sheet = sh.worksheet("Hoja 1")
                sh.del_worksheet(default_sheet)
            except:
                pass
                
        return True
    except Exception as e:
        st = _get_st()
        if st:
            st.error(f"Error al inicializar las hojas en Google Sheets: {e}")
        return False

# Database API wrappers

def get_products():
    conn = get_connection()
    
    try:
        df = conn.read(
            worksheet="Productos",
            parse_dates=False
        )
        
        products = []
        for _, r in df.iterrows():
            products.append({
                "id": str(r["id"]),
                "name": str(r["name"]),
                "price": float(r["price"]),
                "description": str(r["description"]),
                "stock_by_store": {
                    "Tienda Principal": int(r["Tienda Principal"]),
                    "Sucursal Norte": int(r["Sucursal Norte"]),
                    "Sucursal Sur": int(r["Sucursal Sur"]),
                    "Almacén Central": int(r["Almacén Central"])
                }
            })
        
        products = []
        for r in records:
            products.append({
                "id": str(r["id"]),
                "name": str(r["name"]),
                "price": float(r["price"]),
                "description": str(r["description"]),
                "stock_by_store": {
                    "Tienda Principal": int(r["Tienda Principal"]),
                    "Sucursal Norte": int(r["Sucursal Norte"]),
                    "Sucursal Sur": int(r["Sucursal Sur"]),
                    "Almacén Central": int(r["Almacén Central"])
                }
            })
        return products
    except Exception as e:
        st = _get_st()
        if st:
            st.warning(f"Error leyendo Google Sheets (Productos), usando datos locales demo: {e}")
        return DEFAULT_PRODUCTS

def get_product_by_id(product_id):
    products = get_products()
    for p in products:
        if p["id"] == product_id:
            return p
    return None

def get_sales():
    if not check_credentials_exist():
        return DEFAULT_SALES
        
    try:
        sh = get_spreadsheet()
        ws = sh.worksheet("Ventas")
        records = ws.get_all_records()
        
        sales = []
        for r in records:
            sales.append({
                "id": str(r["id"]),
                "date": str(r["date"]),
                "product_id": str(r["product_id"]),
                "product_name": str(r["product_name"]),
                "quantity": int(r["quantity"]),
                "price": float(r["price"]),
                "total_amount": float(r["total_amount"]),
                "amount_paid": float(r["amount_paid"]),
                "client_name": str(r["client_name"]),
                "client_contact": str(r["client_contact"]),
                "store": str(r["store"])
            })
        return sales
    except Exception as e:
        st = _get_st()
        if st:
            st.warning(f"Error leyendo Google Sheets (Ventas), usando datos locales demo: {e}")
        return DEFAULT_SALES

def get_stores():
    if not check_credentials_exist():
        return DEFAULT_STORES
        
    try:
        sh = get_spreadsheet()
        ws = sh.worksheet("Tiendas")
        records = ws.get_all_records()
        return [r["name"] for r in records if r.get("name")]
    except Exception as e:
        st = _get_st()
        if st:
            st.warning(f"Error leyendo Google Sheets (Tiendas), usando datos locales demo: {e}")
        return DEFAULT_STORES

def add_sale(client_name, client_contact, product_id, quantity, store, amount_paid, sale_date=None):
    """Registers a sale in Google Sheets and updates inventory."""
    if not check_credentials_exist():
        raise ValueError("Google Sheets no está configurado. No se pueden registrar ventas permanentes.")
        
    sh = get_spreadsheet()
    
    # 1. Update Stock in Productos Sheet
    ws_prod = sh.worksheet("Productos")
    id_cell = ws_prod.find(product_id, in_column=1)
    if not id_cell:
        raise ValueError("Producto no encontrado en Google Sheets.")
    row_idx = id_cell.row
    
    headers_prod = ws_prod.row_values(1)
    if store not in headers_prod:
        raise ValueError(f"Tienda '{store}' no existe en las columnas de Google Sheets.")
    store_col_idx = headers_prod.index(store) + 1
    
    current_stock = int(ws_prod.cell(row_idx, store_col_idx).value)
    if current_stock < quantity:
        raise ValueError(f"Stock insuficiente en {store}. Disponible: {current_stock}, Solicitado: {quantity}.")
        
    # Deduct stock
    new_stock = current_stock - quantity
    ws_prod.update_cell(row_idx, store_col_idx, new_stock)
    
    # 2. Append Sale in Ventas Sheet
    product = get_product_by_id(product_id)
    unit_price = product["price"]
    total_amount = unit_price * quantity
    
    # Format date
    if not sale_date:
        sale_date_str = datetime.now().strftime("%Y-%m-%d")
    elif isinstance(sale_date, datetime):
        sale_date_str = sale_date.strftime("%Y-%m-%d")
    else:
        sale_date_str = str(sale_date)
        
    # Generate new ID
    sales = get_sales()
    max_id_num = 1000
    for s in sales:
        try:
            id_num = int(s["id"].split("_")[1])
            if id_num > max_id_num:
                max_id_num = id_num
        except:
            pass
    new_id = f"sale_{max_id_num + 1}"
    
    ws_sales = sh.worksheet("Ventas")
    ws_sales.append_row([
        new_id,
        sale_date_str,
        product_id,
        product["name"],
        quantity,
        unit_price,
        total_amount,
        float(amount_paid),
        client_name,
        client_contact,
        store
    ])
    
    return True

def register_abono(sale_id, amount):
    """Registers an abono (payment) against a debtor sale in Google Sheets."""
    if not check_credentials_exist():
        raise ValueError("Google Sheets no está configurado. No se pueden registrar abonos permanentes.")
        
    sh = get_spreadsheet()
    ws_sales = sh.worksheet("Ventas")
    
    id_cell = ws_sales.find(sale_id, in_column=1)
    if not id_cell:
        raise ValueError("Venta no encontrada en Google Sheets.")
    row_idx = id_cell.row
    
    headers_sales = ws_sales.row_values(1)
    paid_col_idx = headers_sales.index("amount_paid") + 1
    total_col_idx = headers_sales.index("total_amount") + 1
    
    current_paid = float(ws_sales.cell(row_idx, paid_col_idx).value)
    total_amount = float(ws_sales.cell(row_idx, total_col_idx).value)
    max_allowed = total_amount - current_paid
    
    if amount <= 0:
        raise ValueError("El monto del abono debe ser mayor a cero.")
    if amount > max_allowed:
        raise ValueError(f"El abono de ${amount:.2f} excede la deuda de ${max_allowed:.2f}.")
        
    new_paid = round(current_paid + amount, 2)
    ws_sales.update_cell(row_idx, paid_col_idx, new_paid)
    return True

def transfer_stock(product_id, from_store, to_store, quantity):
    """Transfers stock of a product between store columns in Google Sheets."""
    if from_store == to_store:
        raise ValueError("Las tiendas de origen y destino deben ser diferentes.")
    if quantity <= 0:
        raise ValueError("La cantidad a transferir debe ser mayor a cero.")
        
    if not check_credentials_exist():
        raise ValueError("Google Sheets no está configurado. No se pueden registrar transferencias permanentes.")
        
    sh = get_spreadsheet()
    ws_prod = sh.worksheet("Productos")
    
    id_cell = ws_prod.find(product_id, in_column=1)
    if not id_cell:
        raise ValueError("Producto no encontrado en Google Sheets.")
    row_idx = id_cell.row
    
    headers_prod = ws_prod.row_values(1)
    from_col_idx = headers_prod.index(from_store) + 1
    to_col_idx = headers_prod.index(to_store) + 1
    
    from_stock = int(ws_prod.cell(row_idx, from_col_idx).value)
    if from_stock < quantity:
        raise ValueError(f"Stock insuficiente en {from_store}. Disponible: {from_stock}, Solicitado: {quantity}.")
        
    to_stock = int(ws_prod.cell(row_idx, to_col_idx).value)
    
    ws_prod.update_cell(row_idx, from_col_idx, from_stock - quantity)
    ws_prod.update_cell(row_idx, to_col_idx, to_stock + quantity)
    return True

def adjust_stock(product_id, store, quantity_change):
    """Directly adjusts stock level for a product in a store column in Google Sheets."""
    if not check_credentials_exist():
        raise ValueError("Google Sheets no está configurado. No se pueden registrar ajustes permanentes.")
        
    sh = get_spreadsheet()
    ws_prod = sh.worksheet("Productos")
    
    id_cell = ws_prod.find(product_id, in_column=1)
    if not id_cell:
        raise ValueError("Producto no encontrado en Google Sheets.")
    row_idx = id_cell.row
    
    headers_prod = ws_prod.row_values(1)
    col_idx = headers_prod.index(store) + 1
    
    current_stock = int(ws_prod.cell(row_idx, col_idx).value)
    new_stock = current_stock + quantity_change
    if new_stock < 0:
        raise ValueError(f"No se puede reducir el stock por debajo de 0. Stock actual en {store}: {current_stock}.")
        
    ws_prod.update_cell(row_idx, col_idx, new_stock)
    return True

def get_debtors():
    """Dynamically parses sales to calculate active debtors list."""
    sales = get_sales()
    debtors = []
    for s in sales:
        pending = s["total_amount"] - s["amount_paid"]
        if pending > 0.01:
            debtors.append({
                "sale_id": s["id"],
                "date": s["date"],
                "client_name": s["client_name"],
                "client_contact": s["client_contact"],
                "product_name": s["product_name"],
                "quantity": s["quantity"],
                "total_amount": s["total_amount"],
                "amount_paid": s["amount_paid"],
                "debt_pending": round(pending, 2),
                "store": s["store"]
            })
    return debtors
