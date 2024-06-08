import disnake
from disnake.ext import commands
import json
import datetime
import os
import asyncio

POSITIONS = [
    "Ранг 1 | Стажер", "Ранг 2 | Юрист", "Ранг 3 | Пом. Прокурора", "Ранг 4 | Мл. агент USSS", "Ранг 5 | Менеджер",
    "Ранг 6 | Агент USSS", "Ранг 7 | Адвокат", "Ранг 8 | Ст. Менеджер", "Ранг 9 | Спецагент USSS",
    "Ранг 10 | Прокурор", "Ранг 11 | Старший прокурор", "Ранг 12 | Ст. Агент USSS", "Ранг 13 | Окружной судья",
    "Ранг 14 | Верховный судья", "Ранг 15 | Председатель Верх. суда", "Ранг 16 | Заместитель Главы Ведомства",
    "Ранг 17 | Глава Ведомства", "Ранг 18 | Вице губернатор", "Ранг 19 | Губернатор"
]

class FactionManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Функция для загрузки данных пользователя из JSON файла
    def load_user_data(self, user_id):
        file_path = f'data/{user_id}.json'
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return {"logs": []}

    # Функция для сохранения данных пользователя в JSON файл
    def save_user_data(self, user_id, data):
        os.makedirs('data', exist_ok=True)
        with open(f'data/{user_id}.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    # Логирование действий пользователя
    def log_user_action(self, user_id, action, details):
        user_data = self.load_user_data(user_id)
        log_entry = {
            "timestamp": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "action": action,
            "details": details
        }
        user_data["logs"].append(log_entry)
        self.save_user_data(user_id, user_data)

    # Функция для создания embed сообщений
    def create_embed(self, title, color, fields, inline_fields):
        embed = disnake.Embed(title=title, color=color)
        for name, value in fields.items():
            embed.add_field(name=name, value=value, inline=False)
        for name, value in inline_fields.items():
            embed.add_field(name=name, value=value, inline=True)
        embed.set_footer(text=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        return embed

    @commands.slash_command(description="Принять игрока во фракцию")
    async def invite(self, inter, member: disnake.Member, passport: str):
        inviter_details = f"{inter.author.mention} | {inter.author.display_name} | ||{inter.author.id}||"
        invitee_details = f"{member.mention} | {member.display_name} | ||{member.id}||"
        self.log_user_action(member.id, "Принят", {"Принял": inviter_details, "passport": passport, "Причина": "Набор/заявка"})
        self.log_user_action(inter.author.id, "Принял во фракцию", {"invitee": invitee_details, "passport": passport, "reason": "Набор/заявка"})

        fields = {
            "Принял": inviter_details,
            "Принят": invitee_details
        }
        inline_fields = {
            "Номер паспорта": passport,
            "Действие": "Принят на Ранг 1 | Стажер",
            "Причина": "Набор/заявка"
        }
        embed = self.create_embed("Кадровый аудит • Принятие", disnake.Color.blue(), fields, inline_fields)
        await inter.response.send_message(embed=embed)

    @commands.slash_command(description="Уволить игрока из фракции")
    async def uval(self, inter, member: disnake.Member, reason: str, passport: str):
        remover_details = f"{inter.author.mention} | {inter.author.display_name} | ||{inter.author.id}||"
        removed_details = f"{member.mention} | {member.display_name} | ||{member.id}||"
        self.log_user_action(member.id, "Уволен", {"remover": remover_details, "reason": reason, "passport": passport})
        self.log_user_action(inter.author.id, "Уволил из фракции", {"removed": removed_details, "reason": reason, "passport": passport})

        fields = {
            "Уволил": remover_details,
            "Уволен": removed_details,
        }
        inline_fields = {
            "Номер паспорта": passport,
        }
        embed = self.create_embed("Кадровый аудит • Увольнение", disnake.Color.red(), fields, inline_fields)
        embed.add_field(name='Причина', value=reason, inline=False)
        await inter.response.send_message(embed=embed)
        if inter.author.top_role > member.top_role:
            await member.kick(reason=reason)  # Кикаем пользователя с сервера

    @commands.slash_command(description="Назначить на должность")
    async def appoint(self, inter, member: disnake.Member, position: str, reason: str, passport: str):
        assigner_details = f"{inter.author.mention} | {inter.author.display_name} | ||{inter.author.id}||"
        assignee_details = f"{member.mention} | {member.display_name} | ||{member.id}||"
        self.log_user_action(member.id, "Назначен", {"assigner": assigner_details, "position": position, "reason": reason, "passport": passport})
        self.log_user_action(inter.author.id, "Назначил на должность", {"assignee": assignee_details, "position": position, "reason": reason, "passport": passport})

        fields = {
            "Назначил": assigner_details,
            "Назначен": assignee_details,
        }
        inline_fields = {
            "Номер паспорта": passport,
            "Должность": position,
        }
        embed = self.create_embed("Кадровый аудит • Назначение на должность", disnake.Color.purple(), fields, inline_fields)
        embed.add_field(name='Причина', value=reason, inline=False)

        await inter.response.send_message(embed=embed)

    @commands.slash_command(description="Уволить игрока из фракции (нет в Discord)")
    async def uval_nik(self, inter, name_surname: str, passport: str, reason: str):
        remover_details = f"{inter.author.mention} | {inter.author.display_name} | ||{inter.author.id}||"
        self.log_user_action(name_surname, "uval_nik", {"remover": remover_details, "name_surname": name_surname, "reason": reason, "passport": passport})
        self.log_user_action(inter.author.id, "Уволил из фракции", {"name_surname": name_surname, "reason": reason, "passport": passport})

        fields = {
            "Уволил": remover_details,
            "Уволен": name_surname,
        }
        inline_fields = {
            "Номер паспорта": passport,
        }
        embed = self.create_embed("Кадровый аудит • Увольнение (нет в Discord)", disnake.Color.red(), fields, inline_fields)
        embed.add_field(name='Причина', value=reason, inline=False)
        await inter.response.send_message(embed=embed)

    @commands.slash_command(description="Показать логи пользователя")
    async def logs(self, inter, member: disnake.Member):
        user_data = self.load_user_data(member.id)
        if not user_data["logs"]:
            await inter.response.send_message(f"Логи для пользователя {member.mention} не найдены.", ephemeral=True)
            return

        log_messages = [
            f"{log['timestamp']}: {log['action']} - {log['details']}" for log in user_data["logs"]
        ]

        # Функция для разбивки списка на части
        def chunks(lst, n):
            for i in range(0, len(lst), n):
                yield lst[i:i + n]

        # Максимальное количество логов на одной странице
        max_logs_per_page = 10
        log_pages = list(chunks(log_messages, max_logs_per_page))

        # Создание страницы с логами
        def create_embed(page, page_num, total_pages):
            log_text = "\n".join(page)
            embed = disnake.Embed(
                title=f"Логи пользователя {member.display_name} (Страница {page_num}/{total_pages})",
                description=log_text,
                color=disnake.Color.blue()
            )
            return embed

        # Отправка первой страницы
        current_page = 0
        total_pages = len(log_pages)
        embed = create_embed(log_pages[current_page], current_page + 1, total_pages)
        components = [
            disnake.ui.Button(label="⬅️", custom_id="prev_page", style=disnake.ButtonStyle.secondary),
            disnake.ui.Button(label="➡️", custom_id="next_page", style=disnake.ButtonStyle.secondary),
            disnake.ui.Button(label="Скачать полные логи", custom_id="download_logs", style=disnake.ButtonStyle.primary)
        ]

        await inter.response.send_message(embed=embed, components=components, ephemeral=True)
        message = await inter.original_message()

        # Обработчик для кнопок
        while True:
            try:
                button_inter = await self.bot.wait_for(
                    "interaction",
                    check=lambda i: i.data["custom_id"] in ["prev_page", "next_page", "download_logs"] and i.message.id == message.id,
                    timeout=60.0
                )

                if button_inter.data["custom_id"] == "next_page" and current_page < total_pages - 1:
                    current_page += 1
                    embed = create_embed(log_pages[current_page], current_page + 1, total_pages)
                    await button_inter.response.edit_message(embed=embed)

                elif button_inter.data["custom_id"] == "prev_page" and current_page > 0:
                    current_page -= 1
                    embed = create_embed(log_pages[current_page], current_page + 1, total_pages)
                    await button_inter.response.edit_message(embed=embed)

                elif button_inter.data["custom_id"] == "download_logs":
                    filename = f"user_logs_{member.id}.html"
                    self.create_html_file(user_data["logs"], filename)
                    await button_inter.response.send_message(
                        "Полные логи можно скачать ниже.", file=disnake.File(filename), ephemeral=True
                    )
                    os.remove(filename)
            except asyncio.TimeoutError:
                break

    @commands.slash_command(description="Показать все логи")
    async def all_logs(self, inter):
        all_logs = []
        for filename in os.listdir('data'):
            if filename.endswith('.json'):
                user_id = filename.split('.')[0]
                user_data = self.load_user_data(user_id)
                all_logs.extend(user_data["logs"])

        if not all_logs:
            await inter.response.send_message("Нет логов для отображения.", ephemeral=True)
            return

        all_logs.sort(key=lambda x: x['timestamp'])

        filename = 'all_user_logs.html'
        self.create_html_file(all_logs, filename)
        await inter.response.send_message("Полные логи можно скачать ниже.", file=disnake.File(filename), ephemeral=True)
        os.remove(filename)

    # Функция для создания HTML файла
    def create_html_file(self, logs, filename):
        html_content = "<html><head><title>User Logs</title></head><body>"
        html_content += "<h1>User Logs</h1><ul>"
        for log in logs:
            html_content += f"<li>{log['timestamp']}: {log['action']} - {log['details']}</li>"
        html_content += "</ul></body></html>"

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)

    @appoint.autocomplete("position")
    async def appoint_autocomplete(self, inter, position: str):
        return [pos for pos in POSITIONS if pos.lower().startswith(position.lower())]

def setup(bot):
    bot.add_cog(FactionManagement(bot))
