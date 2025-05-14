from database import get_db_connection

async def get_product_list():
    products = []
    conn = await get_db_connection()
    if conn:
        try:
            cursor = await conn.cursor()
            await cursor.execute("SELECT * FROM products")
            rows = await cursor.fetchall()
            for row in rows:
                products.append({
                    "id": row[0],
                    "name": row[1],
                    "description": row[2],
                    "price": row[3],
                    "image_url": row[4],
                    "is_available": row[5]
                })
        except Exception as e:
            print(f"Error getting product list: {e}")
        finally:
            await conn.close()
    return products
