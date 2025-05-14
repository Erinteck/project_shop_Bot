import aiosqlite
import asyncio

# Database configuration
DB_NAME = 'products_Information.db'

async def get_db_connection():
    """Create and return a database connection."""
    try:
        conn = await aiosqlite.connect(DB_NAME)
        await conn.execute("PRAGMA foreign_keys = ON")
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None


async def create_product_table():
    """Create the products table if it doesn't exist."""
    conn = await get_db_connection()
    if conn:
        try:
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    price REAL,
                    image_url TEXT,
                    is_available BOOLEAN DEFAULT 1
                )
            ''')
            await conn.commit()
            print("Products table created or already exists.")
            return True
        except Exception as e:
            print(f"Error creating product table: {e}")
            return False
        finally:
            await conn.close()
    return None


async def update_product_table():
    """Update the products table with any missing columns."""
    conn = await get_db_connection()
    if conn:
        try:
            cursor = await conn.cursor()
            await cursor.execute("PRAGMA table_info(products);")
            columns = await cursor.fetchall()
            column_names = [column[1] for column in columns]

            # Track if any changes were made
            changes_made = False

            if 'description' not in column_names:
                print("Column 'description' not found. Adding it now.")
                await conn.execute("ALTER TABLE products ADD COLUMN description TEXT;")
                changes_made = True

            if 'price' not in column_names:
                print("Column 'price' not found. Adding it now.")
                await conn.execute("ALTER TABLE products ADD COLUMN price REAL;")
                changes_made = True

            if 'image_url' not in column_names:
                print("Column 'image_url' not found. Adding it now.")
                await conn.execute("ALTER TABLE products ADD COLUMN image_url TEXT;")
                changes_made = True

            if 'is_available' not in column_names:
                print("Column 'is_available' not found. Adding it now.")
                await conn.execute("ALTER TABLE products ADD COLUMN is_available BOOLEAN DEFAULT 1;")
                changes_made = True

            if changes_made:
                await conn.commit()
                print("Product table updated successfully.")
            else:
                print("Product table is already up to date.")

            return True
        except Exception as e:
            print(f"Error updating product table: {e}")
            return False
        finally:
            await conn.close()
    return None


async def create_users_table():
    """Create the users table if it doesn't exist."""
    conn = await get_db_connection()
    if conn:
        try:
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY
                )
            ''')
            await conn.commit()
            print("Users table created or already exists.")
            return True
        except Exception as e:
            print(f"Error creating users table: {e}")
            return False
        finally:
            await conn.close()
    return None


async def create_user_actions_table():
    """Create the user_actions table if it doesn't exist with a foreign key to users table."""
    conn = await get_db_connection()
    if conn:
        try:
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS user_actions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    action TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
                )
            ''')
            await conn.commit()
            print("User actions table created or already exists.")
            return True
        except Exception as e:
            print(f"Error creating user actions table: {e}")
            return False
        finally:
            await conn.close()
    return None

async def save_user(user_id):
    """Save a user to the database. If the user already exists, do nothing."""
    conn = await get_db_connection()
    if conn:
        try:
            await conn.execute(
                "INSERT OR IGNORE INTO users (user_id) VALUES (?)",
                (str(user_id),)
            )
            await conn.commit()
            return True
        except Exception as e:
            print(f"Error saving user: {e}")
            return False
        finally:
            await conn.close()
    return False

async def get_all_users():
    """Get a list of all user IDs from the database."""
    conn = await get_db_connection()
    if conn:
        try:
            cursor = await conn.cursor()
            await cursor.execute("SELECT user_id FROM users")
            rows = await cursor.fetchall()
            return [row[0] for row in rows]
        except Exception as e:
            print(f"Error getting all users: {e}")
            return []
        finally:
            await conn.close()
    return []

async def save_user_action(user_id, action):
    """Save a user action to the database. Requires the user to exist."""
    # First check if the user exists
    conn = await get_db_connection()
    if conn:
        try:
            # Check if user exists
            cursor = await conn.cursor()
            await cursor.execute("SELECT 1 FROM users WHERE user_id = ?", (user_id,))
            user_exists = await cursor.fetchone() is not None

            if not user_exists:
                # Create the user if they don't exist
                await conn.execute(
                    "INSERT OR IGNORE INTO users (user_id) VALUES (?)",
                    (user_id,)
                )

            # Now save the action
            await conn.execute(
                "INSERT INTO user_actions (user_id, action) VALUES (?, ?)",
                (user_id, action)
            )
            await conn.commit()
            return True
        except Exception as e:
            print(f"Error saving user action: {e}")
            return False
        finally:
            await conn.close()
    return False


async def add_product(name, description, price, image_url, is_available=True):
    """Add a new product to the database."""
    conn = await get_db_connection()
    if conn:
        try:
            await conn.execute(
                "INSERT INTO products (name, description, price, image_url, is_available) VALUES (?, ?, ?, ?, ?)",
                (name, description, price, image_url, is_available)
            )
            await conn.commit()
            print(f"Product '{name}' added successfully.")
            return True
        except Exception as e:
            print(f"Error adding product: {e}")
            return False
        finally:
            await conn.close()
    return False

async def edit_product(product_id, name=None, description=None, price=None, image_url=None, is_available=None):
    """Edit an existing product in the database."""
    # First check if the product exists
    exists = await product_exists(product_id)
    if not exists:
        print(f"Product with ID {product_id} does not exist.")
        return False

    conn = await get_db_connection()
    if conn:
        try:
            update_fields = []
            values = []

            if name is not None:
                update_fields.append("name = ?")
                values.append(name)
            if description is not None:
                update_fields.append("description = ?")
                values.append(description)
            if price is not None:
                update_fields.append("price = ?")
                values.append(price)
            if image_url is not None:
                update_fields.append("image_url = ?")
                values.append(image_url)
            if is_available is not None:
                update_fields.append("is_available = ?")
                values.append(is_available)

            if not update_fields:
                print("No fields to update.")
                return False

            query = f"UPDATE products SET {', '.join(update_fields)} WHERE id = ?"
            values.append(product_id)
            await conn.execute(query, tuple(values))
            await conn.commit()
            print(f"Product with ID {product_id} updated successfully.")
            return True
        except Exception as e:
            print(f"Error editing product: {e}")
            return False
        finally:
            await conn.close()
    return False

async def delete_product(product_id):
    """Delete a product from the database."""
    # First check if the product exists
    exists = await product_exists(product_id)
    if not exists:
        print(f"Product with ID {product_id} does not exist.")
        return False

    conn = await get_db_connection()
    if conn:
        try:
            await conn.execute("DELETE FROM products WHERE id = ?", (product_id,))
            await conn.commit()
            print(f"Product with ID {product_id} deleted successfully.")
            return True
        except Exception as e:
            print(f"Error deleting product: {e}")
            return False
        finally:
            await conn.close()
    return False


async def product_exists(product_id):
    """Check if a product with the given ID exists in the database."""
    conn = await get_db_connection()
    if conn:
        try:
            cursor = await conn.cursor()
            await cursor.execute("SELECT 1 FROM products WHERE id = ?", (product_id,))
            return await cursor.fetchone() is not None
        except Exception as e:
            print(f"Error checking product existence: {e}")
            return False
        finally:
            await conn.close()
    return False

async def get_all_products(limit=None):
    """Get all products from the database, optionally limited to a specific number."""
    conn = await get_db_connection()
    if conn:
        try:
            cursor = await conn.cursor()
            if limit:
                await cursor.execute("SELECT * FROM products LIMIT ?", (limit,))
            else:
                await cursor.execute("SELECT * FROM products")
            products = await cursor.fetchall()
            print(f"Retrieved {len(products)} products from database.")
            return products
        except Exception as e:
            print(f"Error fetching products: {e}")
            return []
        finally:
            await conn.close()
    return []

async def get_product_by_id(product_id):
    """Get a product by its ID from the database."""
    conn = await get_db_connection()
    if conn:
        try:
            cursor = await conn.cursor()
            await cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
            product = await cursor.fetchone()
            if product:
                print(f"Retrieved product with ID {product_id}.")
            else:
                print(f"No product found with ID {product_id}.")
            return product
        except Exception as e:
            print(f"Error fetching product by ID: {e}")
            return None
        finally:
            await conn.close()
    return None

async def get_products_by_availability(is_available=True):
    """Get products filtered by availability status."""
    conn = await get_db_connection()
    if conn:
        try:
            cursor = await conn.cursor()
            await cursor.execute("SELECT * FROM products WHERE is_available = ?", (int(is_available),))
            products = await cursor.fetchall()
            status = "available" if is_available else "unavailable"
            print(f"Retrieved {len(products)} {status} products from database.")
            return products
        except Exception as e:
            print(f"Error fetching available products: {e}")
            return []
        finally:
            await conn.close()
    return []

async def search_products_by_name(name_query):
    """Search for products by name using a partial match."""
    conn = await get_db_connection()
    if conn:
        try:
            cursor = await conn.cursor()
            like_query = f"%{name_query}%"
            await cursor.execute("SELECT * FROM products WHERE name LIKE ?", (like_query,))
            products = await cursor.fetchall()
            print(f"Found {len(products)} products matching '{name_query}'.")
            return products
        except Exception as e:
            print(f"Error searching products: {e}")
            return []
        finally:
            await conn.close()
    return []

async def get_product_count():
    """Get the total number of products in the database."""
    conn = await get_db_connection()
    if conn:
        try:
            cursor = await conn.cursor()
            await cursor.execute("SELECT COUNT(*) FROM products")
            result = await cursor.fetchone()
            count = result[0] if result else 0
            print(f"Total product count: {count}")
            return count
        except Exception as e:
            print(f"Error counting products: {e}")
            return 0
        finally:
            await conn.close()
    return 0




async def initialize_db():
    """Initialize all database tables."""
    print("Initializing database...")
    product_table = await create_product_table()
    product_columns = await update_product_table()
    users_table = await create_users_table()
    actions_table = await create_user_actions_table()

    if product_table and product_columns and users_table and actions_table:
        print("✅ All database tables initialized successfully.")
        return True
    else:
        print("⚠️ Some database tables may not have been initialized properly.")
        return False




if __name__ == "__main__":
    asyncio.run(initialize_db())
    print("✅ Database initialization complete.")
