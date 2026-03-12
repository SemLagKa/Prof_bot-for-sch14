import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from recommender import recommend_professions_top5, pretty_format
from config import TOKEN
from data_loader import load_all_data

from recommender import recommend_professions_top5, pretty_format
from books import search_books_google_smart, shorten_link

bot = Bot(token=TOKEN)
dp = Dispatcher()

data = load_all_data()


# --- FSM ---
class Form(StatesGroup):
    user_id = State()
    interests = State()


# --- Команда /start ---
@dp.message(Command("start"))
async def start(message: types.Message, state: FSMContext):
    await message.answer(
        "Привет! Я бот‑профориентатор.\n\n"
        "Сначала введи *свой ID* (например: `9A_5`).",
        parse_mode="Markdown"
    )
    await state.set_state(Form.user_id)


# --- Шаг 1: ввод ID ---
@dp.message(Form.user_id)
async def process_id(message: types.Message, state: FSMContext):
    user_id = message.text.strip()

    if user_id not in data["df_clustered"]["ID"].values:
        await message.answer("❌ Такого ID нет в базе. Попробуй снова.")
        return

    await state.update_data(user_id=user_id)

    await message.answer(
        "Отлично! Теперь введи свои интересы через запятую.\n\n"
        "Например:\n"
        "`программирование, роботы`",
        parse_mode="Markdown"
    )
    await state.set_state(Form.interests)


# --- Шаг 2: ввод интересов ---
@dp.message(Form.interests)
async def process_interests(message: types.Message, state: FSMContext):
    interests = [i.strip().lower() for i in message.text.split(",")]

    user_data = await state.get_data()
    user_id = user_data["user_id"]

    recs = recommend_professions_top5(
        student_id=user_id,
        df_clustered=data["df_clustered"],
        interests=interests,
        career_islands=data["career_islands"],
        cluster_to_islands=data["cluster_to_islands"],
        interest_to_islands=data["interest_to_islands"],
        interest_keywords=data["interest_keywords"],
        index_to_islands=data["index_to_islands"],
        profession_to_topics=data["profession_to_topics"],
        interest_island_weights=data["interest_island_weights"]
    )

    books = search_books_google_smart(interests, max_results=5)

    text = pretty_format(recs)

    if books:
        text += "\n📚 *Подборка книг по твоим интересам:*\n\n"
        for b in books[:5]:
            title = b["title"]
            authors = ", ".join(b["authors"]) if b["authors"] else "Автор не указан"
            preview = shorten_link(b.get("preview", ""))

            text += f"• *{title}*\n"
            text += f"  Автор(ы): {authors}\n"
            if preview:
                text += f"  [Открыть книгу]({preview})\n"
            text += "\n"

        await message.answer(text, parse_mode="Markdown")
        await state.clear()

@dp.message(Form.interests)
async def process_interests(message: types.Message, state: FSMContext):
    interests = [i.strip().lower() for i in message.text.split(",")]

    user_data = await state.get_data()
    user_id = user_data["user_id"]

    recs = recommend_professions_top5(
        student_id=user_id,
        df_clustered=data["df_clustered"],
        interests=interests,
        career_islands=data["career_islands"],
        cluster_to_islands=data["cluster_to_islands"],
        interest_to_islands=data["interest_to_islands"],
        interest_keywords=data["interest_keywords"],
        index_to_islands=data["index_to_islands"],
        profession_to_topics=data["profession_to_topics"],
        interest_island_weights=data["interest_island_weights"]
    )

    # --- КНИГИ ПО ИНТЕРЕСАМ ---
    books = search_books_google_smart(interests, max_results=5)

    text = pretty_format(recs)

    # --- ДОБАВЛЯЕМ КНИГИ ---
    if books:
        text += "\n📚 *Подборка книг по твоим интересам:*\n\n"
        for b in books[:5]:
            title = b["title"]
            authors = ", ".join(b["authors"]) if b["authors"] else "Автор не указан"
            preview = shorten_link(b.get("preview", ""))

            text += f"• *{title}*\n"
            text += f"  Автор(ы): {authors}\n"
            if preview:
                text += f"  [Открыть книгу]({preview})\n"
            text += "\n"

    await message.answer(text, parse_mode="Markdown")
    await state.clear()


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
