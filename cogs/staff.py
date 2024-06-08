import disnake
from disnake.ext import commands
import datetime
import asyncio


class Staff(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def send_staff_embeds(self, ctx, role_groups, title, channel_id):
        await ctx.message.delete()  # Удалить сообщение с вызовом команды

        channel = self.bot.get_channel(channel_id)
        guild = self.bot.get_guild(ctx.guild.id)

        if channel is None or guild is None:
            await ctx.send("Не удалось найти указанный канал или гильдию.")
            return

        def create_embed(title="", footer=False):
            embed = disnake.Embed(title=title, color=0x2F3136)
            if footer:
                embed.timestamp = datetime.datetime.now()
            return embed

        async def send_embeds():
            messages = []
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
                                title=title if index == 0 and chunk_index == 0 else "")
                            current_embed.add_field(name=f"{group} (часть {chunk_index + 1})", value=chunk,
                                                    inline=False)
                            embeds.append(current_embed)
                    else:
                        current_embed = create_embed(title=title if index == 0 else "")
                        current_embed.add_field(name=group, value=group_value, inline=False)
                        embeds.append(current_embed)

            if embeds:
                embeds[-1].timestamp = datetime.datetime.now()  # Set timestamp only on the last embed
                embeds[-1].set_footer(text="Актуально на", icon_url=f'{ctx.guild.icon.url}')

            for embed in embeds:
                msg = await channel.send(embed=embed)
                messages.append(msg)

            return messages

        previous_messages = await send_embeds()

        try:
            while True:
                await asyncio.sleep(3600)  # Ожидание перед каждым обновлением (1 час)
                for msg in previous_messages:
                    try:
                        await msg.delete()
                    except disnake.NotFound:
                        continue

                previous_messages = await send_embeds()

        except asyncio.CancelledError:
            pass  # Просто выходим из цикла, если задача отменена

        for msg in previous_messages:
            try:
                await msg.delete()
            except disnake.NotFound:
                continue

    @commands.command()
    async def staff_ld(self, ctx):
        role_groups = {
            'Министр Финансов': [1119326877807554689],
            'Заместители Министра Финансов': [1119326877794975922],
            'Директор LD': [1139165924826562660],
            'Заместители Директора LD': [1139166159887937539],
            'Лицензеры': [1119945876589264916],
            'Стажеры LD': [1193944327483834538],
        }
        await self.send_staff_embeds(ctx, role_groups, "Состав Лицензеров", 1184217977747423404)

    @commands.command()
    async def staff_fsd(self, ctx):
        role_groups = {
            'Head of FSD': [1161056980941684747],
            'Head of FSD': [1161056980941684747],
            'Deputy Head of FSD': [1161058031774216334],
            'FSD USSS': [1161048435730956338],
        }
        await self.send_staff_embeds(ctx, role_groups, "Состав FSD", 1174418948045950976)

    @commands.command()
    async def staff_mk(self, ctx):
        role_groups = {
            'Министр Культуры': [1119924452965240832],
            'Заместители Министра Культуры': [1119924778434834472],
            'Менеджеры культуры': [1149708866179825845],
            'Стажеры культуры': [1144453558335459328],
        }
        await self.send_staff_embeds(ctx, role_groups, "Состав Министерства Культуры", 1119925067447545916)

    @commands.command()
    async def staff_mz(self, ctx):
        role_groups = {
            'Министр Здравоохранения': [1119326877807554688],
            'Заместители Министра Здравоохранения': [1119326877794975925],
            'Менеджеры здравоохранения': [1119634461198405753],
        }
        await self.send_staff_embeds(ctx, role_groups, "Состав Министерства Здравоохранения", 1119917254625214475)

    @commands.command()
    async def staff_ectf(self, ctx):
        role_groups = {
            'Head of ECTF': [1223205925037543464],
            'Deputy Head ECTF': [1223206228998623232],
            'ECTF USSS': [1223205550783987813],
        }
        await self.send_staff_embeds(ctx, role_groups, "Состав ECTF", 1151819402002583572)

    @commands.command()
    async def staff_usss(self, ctx):
        role_groups = {
            'Министр Безопасности': [1119326877820133501],
            'Заместители Министра Безопасности': [1119326877807554680],
            'Директор USSS': [1119326877820133497],
            'Заместители Директора USSS': [1119326877774000144],
            'ECTF': [1223205925037543464, 1223206228998623232],
            'RTPD': [1119326877774000141, 1122206265284767765],
            'FSD': [1161056980941684747, 1161058031774216334],
            'IOD': [1245808093950906468, 1245808195193143427],
        }
        await self.send_staff_embeds(ctx, role_groups, "Состав United States Secret Service", 1119326881540481078)

    @commands.command()
    async def staff_mb(self, ctx):
        role_groups = {
            'Министр Безопасности': [1119326877820133501],
            'Заместители Министра Безопасности': [1119326877807554680],
        }
        await self.send_staff_embeds(ctx, role_groups, "Состав Министерства Безопасности", 1119326880441573541)

    @commands.command()
    async def staff_advokat(self, ctx):
        role_groups = {
            'Глава Коллегии Адвокатов': [1119326877807554683],
            'Заместители Главы Коллегии Адвокатов': [1120369701411889152],
            'Адвокаты': [1119326877740441673],
            'Юристы': [1119326877740441672],
        }
        await self.send_staff_embeds(ctx, role_groups, "Состав Коллегии Адвокатов", 1119326881334964315)

    @commands.command()
    async def staff_sud(self, ctx):
        role_groups = {
            'Председатель Верховного Суда': [1119326877820133502],
            'Верховные судья': [1119326877757227065],
            'Председатель Окружного Суда': [1121421400540975134],
            'Окружные Судья': [1119326877757227063],
            'Судебные секретари': [1126805044705108049],
        }
        await self.send_staff_embeds(ctx, role_groups, "Состав Судейского Корпуса", 1125089050311786516)

    @commands.command()
    async def staff_rtpd(self, ctx):
        role_groups = {
            'Head RTPD': [1119326877774000141],
            'Deputy Head RTPD': [1122206265284767765],
            'RTPD USSS': [1120813079299620946],
        }
        await self.send_staff_embeds(ctx, role_groups, "Состав RTPD", 1139665269543927960)

    @commands.command()
    async def staff_iod(self, ctx):
        role_groups = {
            'Head of IOD': [1245808093950906468],
            'Deputy Head IOD': [1245808195193143427],
            'IOD USSS': [1151791015506747434],
        }
        await self.send_staff_embeds(ctx, role_groups, "Состав IOD", 1151798794673979455)

    @commands.command()
    async def staff_high(self, ctx):
        role_groups = {
            'Губернатор': [1119326877820133504],
            'Вице-Губернатор': [1119326877820133503],
            'Министерство Юстиции': [1119326877820133500, 1119326877794975924],
            'Министерство Финансов': [1119326877807554689, 1119326877794975922],
            'Министерство Безопасности': [1119326877820133501, 1119326877807554680],
            'Министерство Обороны': [1138884817228935311, 1138885355983085679],
            'Министерство Здравоохранения': [1119326877807554688, 1119326877794975925],
            'Министерство Культуры': [1119924452965240832, 1119924778434834472],
            'Судебная власть': [1119326877820133502, 1119326877757227065, 1121421400540975134, 1119326877757227063],
            'USSS': [1119326877820133497, 1119326877774000144, 1223205925037543464, 1223206228998623232,
                     1119326877774000141, 1122206265284767765, 1161056980941684747, 1161058031774216334,
                     1245808093950906468, 1245808195193143427],
            'Адвокатура': [1119326877807554683, 1120369701411889152],
            'Отдел лицензирования': [1139165924826562660, 1139166159887937539],
        }
        await self.send_staff_embeds(ctx, role_groups, "Старший состав Goverment", 1119326879724351616)


def setup(bot):
    bot.add_cog(Staff(bot))
