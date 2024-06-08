import disnake
from disnake.ext import commands, tasks
import json
import datetime
import asyncio

class Prosecutor(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.prosecutors = self.load_prosecutors()
        self.previous_messages = []
        self.additional_message = None
        self.update_task.start()

    def load_prosecutors(self):
        try:
            with open("prosecutors.json", "r") as file:
                data = file.read()
                if data:
                    return json.loads(data)
                else:
                    return {
                        "San Andreas National Guard": [],
                        "Federal Investigation Bureau": [],
                        "Emergency Medical Services": [],
                        "Los Santos Police Department": [],
                        "Los Santos Sheriff County Department": []
                    }
        except FileNotFoundError:
            return {
                "San Andreas National Guard": [],
                "Federal Investigation Bureau": [],
                "Emergency Medical Services": [],
                "Los Santos Police Department": [],
                "Los Santos Sheriff County Department": []
            }
        except json.JSONDecodeError:
            print("Error decoding JSON. File might be corrupted.")
            return {
                "San Andreas National Guard": [],
                "Federal Investigation Bureau": [],
                "Emergency Medical Services": [],
                "Los Santos Police Department": [],
                "Los Santos Sheriff County Department": []
            }

    def save_prosecutors(self):
        with open("prosecutors.json", "w") as file:
            json.dump(self.prosecutors, file, indent=4)

    async def staff_proc(self, inter=None):
        role_groups = {
            'Генеральный прокурор': [1119326877820133500],
            'Зам. Генерального Прокурора': [1119326877794975924],
            'Старший Прокурор': [1124700387513991279],
            'Прокурор': [1119326877740441676],
            'Помощник прокурора': [1119326877740441675],
        }
        channel_id = 1122465213095092356  # Укажите ID канала
        channel = self.bot.get_channel(channel_id)
        server_id = 1119326877690110023
        guild = self.bot.get_guild(server_id)

        if channel is None or guild is None:
            if inter:
                await inter.response.send_message("Не удалось найти указанный канал или гильдию.", ephemeral=True)
            return

        def create_embed(title="", footer=False):
            embed = disnake.Embed(title=title, color=0x2F3136)
            if footer:
                embed.timestamp = datetime.datetime.now()
            return embed

        async def send_embeds():
            users_ids = [member.id for member in guild.members]
            checked_members = set()

            embeds = []
            for index, (group, roles) in enumerate(role_groups.items()):
                group_members = []

                for min_role in roles:
                    for i in range(len(users_ids)):
                        if users_ids[i] not in checked_members:
                            member = guild.get_member(users_ids[i])
                            if member is None:
                                continue
                            for mem_role in reversed(member.roles):
                                if min_role == mem_role.id and users_ids[i] not in checked_members:
                                    group_members.append(
                                        f"{len(group_members) + 1}. {mem_role.name} - {member.mention}")
                                    checked_members.add(users_ids[i])
                                    break

                if group_members:
                    group_value = "\n".join(group_members)  # Use newline to separate members
                    if len(group_value) > 1024:  # Check if group value exceeds Discord field limit
                        chunks = [group_value[i:i + 1024] for i in range(0, len(group_value), 1024)]
                        for chunk_index, chunk in enumerate(chunks):
                            current_embed = create_embed(
                                title="Состав Прокуратуры" if index == 0 and chunk_index == 0 else "")
                            current_embed.add_field(name=f"{group} (часть {chunk_index + 1})", value=chunk,
                                                    inline=False)
                            embeds.append(current_embed)
                    else:
                        current_embed = create_embed(title="Состав Прокуратуры" if index == 0 else "")
                        current_embed.add_field(name=group, value=group_value, inline=False)
                        embeds.append(current_embed)

            if embeds:
                embeds[-1].timestamp = datetime.datetime.now()  # Set timestamp only on the last embed
                embeds[-1].set_footer(text="Актуально на", icon_url=f'{guild.icon.url}')

            for embed in embeds:
                msg = await channel.send(embed=embed)
                self.previous_messages.append(msg)

        async def send_additional_embed():
            embed = create_embed(title="Курирующие прокуроры", footer=True)
            additional_members = []
            for department, members in self.prosecutors.items():
                for member_id in members:
                    member_name = guild.get_member(member_id)
                    if member_name:
                        additional_members.append(f"{department} - {member_name.mention}")
                    else:
                        additional_members.append(f"{department} - <@{member_id}>")
            if additional_members:
                embed.add_field(name='Курирующие прокуроры', value='\n'.join(additional_members), inline=False)
            self.additional_message = await channel.send(embed=embed)

        await self.delete_previous_messages()
        await send_embeds()
        await send_additional_embed()

    async def delete_previous_messages(self):
        for msg in self.previous_messages:
            try:
                await msg.delete()
            except disnake.NotFound:
                continue
        self.previous_messages = []

        if self.additional_message:
            try:
                await self.additional_message.delete()
            except disnake.NotFound:
                pass
            self.additional_message = None

    @commands.slash_command(description="Добавить курирующего прокурора")
    async def add_prosecutor(self, inter: disnake.ApplicationCommandInteraction, user: disnake.Member,
                             list_name: str):
        await inter.response.defer(ephemeral=True)
        if list_name in self.prosecutors:
            self.prosecutors[list_name].append(user.id)
            self.save_prosecutors()
            await inter.edit_original_response(content=f"Пользователь {user.mention} добавлен в список {list_name}.")
            await self.update_staff_proc(inter)
        else:
            await inter.edit_original_response(content="Неверное название списка.")

    @commands.slash_command(description="Список курирующих прокуроров")
    async def list_prosecutor(self, inter: disnake.ApplicationCommandInteraction,
                              list_name: str):
        await inter.response.defer(ephemeral=True)
        if list_name in self.prosecutors:
            if self.prosecutors[list_name]:
                embed = disnake.Embed(
                    title=f"Список пользователей в {list_name}",
                    description='\n'.join(f"<@{user_id}>" for user_id in self.prosecutors[list_name]),
                    color=0x00ff00
                )
                await inter.edit_original_response(embed=embed)
            else:
                await inter.edit_original_response(content=f"Список {list_name} пуст.")
        else:
            await inter.edit_original_response(content="Неверное название списка.")

    @commands.slash_command(description="Удалить курирующего прокурора")
    async def remove_prosecutor(self, inter: disnake.ApplicationCommandInteraction, user: disnake.Member,
                                list_name: str):
        await inter.response.defer(ephemeral=True)
        if list_name in self.prosecutors:
            if user.id in self.prosecutors[list_name]:
                self.prosecutors[list_name].remove(user.id)
                self.save_prosecutors()
                await inter.edit_original_response(content=f"Пользователь {user.mention} удален из списка {list_name}.")
                await self.update_staff_proc(inter)
            else:
                await inter.edit_original_response(content=f"Пользователь {user.mention} не найден в списке {list_name}.")
        else:
            await inter.edit_original_response(content="Неверное название списка.")

    @add_prosecutor.autocomplete("list_name")
    async def add_prosecutor_autocomplete(self, inter: disnake.ApplicationCommandInteraction, user_input: str):
        return [list_name for list_name in self.prosecutors.keys() if user_input.lower() in list_name.lower()]

    @list_prosecutor.autocomplete("list_name")
    async def list_prosecutor_autocomplete(self, inter: disnake.ApplicationCommandInteraction, user_input: str):
        return [list_name for list_name in self.prosecutors.keys() if user_input.lower() in list_name.lower()]

    @remove_prosecutor.autocomplete("list_name")
    async def remove_prosecutor_autocomplete(self, inter: disnake.ApplicationCommandInteraction, user_input: str):
        return [list_name for list_name in self.prosecutors.keys() if user_input.lower() in list_name.lower()]

    async def update_staff_proc(self, inter=None):
        await self.staff_proc(inter)

    @commands.slash_command(description="Обновить список прокуроров")
    async def staff_proc_command(self, inter: disnake.ApplicationCommandInteraction):
        await inter.response.defer(ephemeral=True)
        await self.staff_proc(inter)
        await inter.edit_original_response(content="Список прокуроров обновлен.")

    @tasks.loop(hours=1)
    async def update_task(self):
        await self.staff_proc()

    @update_task.before_loop
    async def before_update_task(self):
        await self.bot.wait_until_ready()

    def cog_unload(self):
        self.update_task.cancel()

def setup(bot):
    bot.add_cog(Prosecutor(bot))
