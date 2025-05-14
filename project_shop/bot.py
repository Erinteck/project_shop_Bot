from telethon import TelegramClient, events, Button
from product_list import get_product_list
from config import Config
import database
import asyncio

client = TelegramClient("CAPITANSHOP_FF_bot_botsession", api_id=Config.APP_ID, api_hash=Config.API_HASH).start(bot_token=Config.BOT_TOKEN)

ADMINS = [7795693943]
pending_product_input = {}

@client.on(events.NewMessage(pattern="/start"))
async def start(event):
    user_id = event.sender_id
    await database.save_user(user_id)
    await show_main_menu(event)

async def show_main_menu(event):
    user_id = event.sender_id
    buttons = [
        [Button.inline("🛍 فروشگاه", data="store")],
        [Button.inline("📞 پشتیبان تلگرام", data="telegram_support")],
        [Button.inline("💬 پشتیبان واتساپ", data="whatsapp_support")],
        [Button.inline("📦 لیست محصولات", data="product_list")]
    ]
    if user_id in ADMINS:
        buttons.append([Button.inline("⚙️ مدیریت محصولات", data="manage_products")])
        buttons.append([Button.inline("👤 مدیریت کاربران", data="manage_users")])
    await event.respond("خوش آمدید! لطفاً یکی از گزینه‌ها را انتخاب کنید.", buttons=buttons)

@client.on(events.CallbackQuery)
async def handle_callback(event):
    user_id = event.sender_id
    data = event.data.decode()

    if data == "store":
        await database.save_user_action(user_id, "clicked_store")
        await event.respond("🔗 لینک فروشگاه: https://t.me/mehdicapitanshop")

    elif data == "telegram_support":
        await event.answer("در حال اتصال به پشتیبانی تلگرام...")
        await event.respond("🔗 [پشتیبان تلگرام](https://t.me/MEHDI_CAPITAN_FF)")

    elif data == "whatsapp_support":
        await database.save_user_action(user_id, "clicked_whatsapp_support")
        await event.respond("در حال اتصال به پشتیبانی واتساپ...")
        await client.send_message(user_id, "برای تماس با پشتیبان واتساپ، لطفاً از این لینک استفاده کنید: https://wa.me/09055169948")

    elif data == "product_list":
        await database.save_user_action(user_id, "clicked_product_list")
        products = await get_product_list()
        if not products:
            await event.respond("هیچ محصولی یافت نشد.")
            return
        buttons = [[Button.inline(f"{p['name']} - {p['price']} تومان", data=f"buy_{p['id']}")] for p in products]
        await event.respond("📋 لیست محصولات:", buttons=buttons)

    elif data.startswith("buy_"):
        product_id = data.split("_")[1]
        products = await get_product_list()
        selected_product = next((p for p in products if int(p["id"]) == int(product_id)), None)

        if selected_product is None:
            await event.respond("محصول مورد نظر یافت نشد.")
            return

        await database.save_user_action(user_id, f"requested_buy_{selected_product['id']}")

        caption = (
            f"🛍 <b>{selected_product['name']}</b>\n\n"
            f"📄 {selected_product['description']}\n"
            f"💰 قیمت: {selected_product['price']} تومان"
        )

        buttons = [[Button.url("🗨  خرید و صحبت با پشتیبان  ", url="https://t.me/MEHDI_CAPITAN_FF")]]
        
        try:
            await client.send_file(
                user_id,
                file=selected_product['image_url'],
                caption=caption,
                buttons=buttons,
                parse_mode="html"
            )
        except Exception as e:
            print(f"❌ خطا در ارسال محصول به کاربر {user_id}: {e}")
            await event.respond("ارسال اطلاعات محصول با مشکل مواجه شد.")

    elif data == "manage_products" and user_id in ADMINS:
        await event.respond("📦 مدیریت محصولات", buttons=[
            [Button.inline("➕ اضافه کردن محصول", data="add_product")],
            [Button.inline("🗑 حذف محصول", data="delete_product")],
            [Button.inline("🔙 بازگشت", data="back_to_main")]
        ])
        
        # نمایش لیست محصولات موجود
        products = await get_product_list()
        if products:
            product_list = "\n".join([f"شناسه: {p['id']} - {p['name']} - {p['price']} تومان" for p in products])
            await event.respond(f"📋 لیست محصولات موجود:\n{product_list}")
        else:
            await event.respond("هیچ محصولی یافت نشد.")

    elif data == "manage_users" and user_id in ADMINS:
        users = await database.get_all_users()
        text = '\n\n' + ("\n".join(['- ' + str(user) for user in users]) if users else "هیچ کاربری یافت نشد.")
        await event.respond("👤 مدیریت کاربران" + text, buttons=[ 
            [Button.inline("🔙 بازگشت", data="back_to_main")]
        ])

    elif data == "add_product" and user_id in ADMINS:
        pending_product_input[user_id] = "waiting_for_image"
        await event.respond("🖼 لطفاً تصویر محصول را ارسال کنید.")

    elif data == "delete_product" and user_id in ADMINS:
        pending_product_input[user_id] = "waiting_for_product_id_to_delete"
        await event.respond("🔻 لطفاً شناسه محصولی که می‌خواهید حذف کنید را ارسال کنید:")

    elif data == "back_to_main":
        await show_main_menu(event)

@client.on(events.NewMessage)
async def handle_product_input(event):
    user_id = event.sender_id

    if user_id in pending_product_input:
        status_info = pending_product_input[user_id]

        if status_info == "waiting_for_image":
            if event.photo:
                image_path = await event.client.download_media(event.message.photo)
                pending_product_input[user_id] = {
                    "status": "waiting_for_title",
                    "image": image_path
                }
                await event.respond("📝 لطفاً عنوان محصول را وارد کنید.")
            else:
                await event.respond("❌ لطفاً یک تصویر ارسال کنید.")

        elif isinstance(status_info, dict) and status_info.get("status") == "waiting_for_title":
            title = event.raw_text.strip()
            if len(title) < 2:
                await event.respond("❌ عنوان محصول خیلی کوتاه است.")
            else:
                pending_product_input[user_id]["name"] = title
                pending_product_input[user_id]["status"] = "waiting_for_description"
                await event.respond("📄 لطفاً توضیحات محصول را وارد کنید.")

        elif isinstance(status_info, dict) and status_info.get("status") == "waiting_for_description":
            description = event.raw_text.strip()
            if len(description) < 5:
                await event.respond("❌ توضیحات خیلی کوتاه است.")
            else:
                pending_product_input[user_id]["description"] = description
                pending_product_input[user_id]["status"] = "waiting_for_price"
                await event.respond("💰 لطفاً قیمت محصول را وارد کنید (فقط عدد).")

        elif isinstance(status_info, dict) and status_info.get("status") == "waiting_for_price":
            if not event.raw_text.isdigit():
                await event.respond("❌ لطفاً فقط عدد وارد کنید.")
                return

            price = int(event.raw_text)
            data = pending_product_input[user_id]
            await database.add_product(
                name=data["name"],
                description=data["description"],
                price=price,
                image_url=data["image"],
                is_available=True
            )

            product_info = f"🛍 {data['name']}\n\n📄 {data['description']}\n💰 قیمت: {price} تومان"
            buttons = [[Button.url("🗨 صحبت با پشتیبان", url="https://t.me/MEHDI_CAPITAN_FF")]] 

            await event.respond(product_info, file=data["image"], buttons=buttons)

            all_users = await database.get_all_users()
            for uid in all_users:
                try:
                    await client.send_file(
                        uid,
                        file=data["image"],
                        caption=product_info,
                        buttons=buttons
                    )
                except Exception as e:
                    print(f"خطا در ارسال به کاربر {uid}: {e}")

            pending_product_input.pop(user_id)

        elif status_info == "waiting_for_product_id_to_delete":
            product_id = event.raw_text.strip()
            product = await database.get_product_by_id(product_id)
            if not product:
                await event.respond("❌ محصولی با این شناسه یافت نشد.")
                return

            await database.delete_product(product_id)
            await event.respond(f"✅ محصول با شناسه {product_id} حذف شد.")
            pending_product_input.pop(user_id)

        else:
            await event.respond("❌ اطلاعات وارد شده معتبر نیست. لطفاً از ابتدا شروع کنید.")

async def main():
    await database.initialize_db()
    print("✅ Database initialized.")

    await client.start()
    print("✅ Bot is running.")
    await client.run_until_disconnected()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        print("Bot stopped by user.")
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()
